#!/usr/bin/env python3
"""Apply shared guidance without replacing host configuration or authentication."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv


SOURCE = Path(__file__).resolve().parent.parent


def effective_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()


def global_files(source: Path = SOURCE) -> list[Path]:
    return [source / name for name in
            ("AGENTS.md", "agent-model-routing.md", "agent-orchestration.md")] + [
        *sorted((source / "agents").glob("*.toml")),
        source / "references/external-daybreak-review.md",
    ]


def runtime_python(home: Path) -> Path:
    return home / "javier-runtime" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(content)
        temporary = Path(temp.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def apply_guidance(home: Path, *, source: Path = SOURCE, dry_run: bool = False,
                   awra_guidance_root: Path | None = None,
                   awra_voice_root: Path | None = None) -> dict:
    home = home.resolve()
    if (home / "AGENTS.override.md").exists():
        raise ValueError("AGENTS.override.md would override the shared guidance; resolve it before setup.")
    paths_file = home / "javier-paths.toml"
    paths = tomllib.loads(paths_file.read_text(encoding="utf-8")) if paths_file.exists() else {}
    if any(not isinstance(value, str) for value in paths.values()):
        raise ValueError("javier-paths.toml must contain string path values.")
    for name, value in (("awra_guidance_root", awra_guidance_root),
                        ("awra_voice_root", awra_voice_root)):
        if value is not None:
            value = value.expanduser().resolve()
            if not value.is_dir():
                raise ValueError(f"{name} is not an accessible directory: {value}")
            paths[name] = str(value)
    paths["python"] = str(runtime_python(home))
    changes = [(p.relative_to(source), p.read_bytes()) for p in global_files(source)]
    paths_content = "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
                            for key, value in sorted(paths.items()))
    changes.append((Path("javier-paths.toml"), paths_content.encode()))
    changes = [(rel, data) for rel, data in changes
               if not (home / rel).exists() or (home / rel).read_bytes() != data]
    backup = home / "javier-setup-backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backed_up = False
    if not dry_run:
        for rel, data in changes:
            target = home / rel
            if target.exists():
                saved = backup / rel
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, saved)
                backed_up = True
            atomic_write(target, data)
    return {"codex_home": str(home), "dry_run": dry_run,
            "changed": [str(rel) for rel, _ in changes],
            "backup": str(backup) if backed_up else None,
            "runtime_python": paths["python"]}


def install_runtime(home: Path) -> None:
    executable = runtime_python(home)
    if not executable.exists():
        venv.EnvBuilder(with_pip=True).create(home / "javier-runtime")
    subprocess.run([str(executable), "-m", "pip", "install", "-r",
                    str(SOURCE / "plugins/javier/requirements.txt")], check=True)


def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()
            and "__pycache__" not in p.parts and not p.name.endswith(".pyc")}


def retire_local_skills(home: Path, *, installed_plugin: Path,
                        source: Path = SOURCE, dry_run: bool = False) -> list[str]:
    """Archive only unchanged former copies, after both-host validation."""
    manifest = json.loads((source / "scripts/migration.json").read_text(encoding="utf-8"))
    if file_hashes(installed_plugin) != file_hashes(source / "plugins/javier"):
        raise ValueError("Installed plugin differs from this source; validate the same version before retirement.")
    candidates = []
    for root in (home / "skills",):
        for name, expected in manifest["legacy_files"].items():
            path = root / name
            if not path.exists():
                continue
            if path.is_symlink():
                raise ValueError(f"Refusing to archive a symlinked skill: {path}")
            actual = file_hashes(path)
            if actual != expected:
                raise ValueError(f"Local changes in {path}; preserve and reconcile them before retirement.")
            candidates.append(path)
    if not dry_run:
        backup = home / "javier-setup-backups" / datetime.now(timezone.utc).strftime("retired-%Y%m%dT%H%M%S%fZ")
        for path in candidates:
            destination = backup / "codex-skills" / path.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(destination))
    return [str(path) for path in candidates]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=effective_home())
    parser.add_argument("--awra-guidance-root", type=Path)
    parser.add_argument("--awra-voice-root", type=Path)
    parser.add_argument("--with-runtime", action="store_true", help="Install the shared Python environment.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--retire-local-skills", action="store_true",
                        help="After validating the plugin on BOTH hosts, archive its unchanged former local copies.")
    parser.add_argument("--installed-plugin", type=Path,
                        help="Installed plugin directory, required when retiring former local skills.")
    args = parser.parse_args()
    home = args.codex_home.expanduser().resolve()
    if args.retire_local_skills:
        if args.installed_plugin is None:
            parser.error("--retire-local-skills requires --installed-plugin")
        result = {"retired": retire_local_skills(home, installed_plugin=args.installed_plugin,
                                               dry_run=args.dry_run), "dry_run": args.dry_run}
    else:
        apply_guidance(home, dry_run=True,
                       awra_guidance_root=args.awra_guidance_root,
                       awra_voice_root=args.awra_voice_root)
        if args.with_runtime and not args.dry_run:
            install_runtime(home)
        result = apply_guidance(home, dry_run=args.dry_run,
                                awra_guidance_root=args.awra_guidance_root,
                                awra_voice_root=args.awra_voice_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
