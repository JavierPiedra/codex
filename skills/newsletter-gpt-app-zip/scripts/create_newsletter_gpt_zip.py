#!/usr/bin/env python3
"""Create a zip archive from repo files not ignored by .gitignore."""

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

DEFAULT_REPO_ROOT = Path(
    "/Users/javierpiedra/Desktop/goodancestor/newsletter-gpt"
)
DEFAULT_OUTPUT_NAME = "newsletter_gpt_app.zip"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Zip tracked and untracked files that are not ignored by "
            ".gitignore"
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(DEFAULT_REPO_ROOT),
        help="Repository root path",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_NAME,
        help="Output zip path (relative to repo root or absolute path)",
    )
    return parser.parse_args()


def list_non_ignored_files(repo_root: Path):
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "-c",
                "-o",
                "--exclude-standard",
                "-z",
            ],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError:
        raise RuntimeError("git is not installed or not available in PATH")
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git ls-files failed: {stderr}")

    raw_entries = [item for item in result.stdout.split(b"\0") if item]
    return sorted(
        item.decode("utf-8", errors="surrogateescape")
        for item in raw_entries
    )


def resolve_output_path(repo_root: Path, output_arg: str):
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    return output_path.resolve()


def create_archive(repo_root: Path, output_path: Path):
    files = list_non_ignored_files(repo_root)

    output_rel = None
    try:
        output_rel = output_path.relative_to(repo_root).as_posix()
    except ValueError:
        output_rel = None

    tmp_output = output_path.with_name(f".{output_path.name}.tmp")
    if tmp_output.exists():
        tmp_output.unlink()

    written = 0
    with zipfile.ZipFile(
        tmp_output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for rel_path in files:
            if output_rel and rel_path == output_rel:
                continue
            source_path = (repo_root / rel_path).resolve()
            if not source_path.exists():
                continue
            archive.write(source_path, arcname=rel_path)
            written += 1

    os.replace(tmp_output, output_path)
    size_bytes = output_path.stat().st_size
    print(f"Archive: {output_path}")
    print(f"Files: {written}")
    print(f"Size bytes: {size_bytes}")


def main():
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    if not repo_root.exists():
        print(f"Repository root does not exist: {repo_root}", file=sys.stderr)
        return 1

    output_path = resolve_output_path(repo_root, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        create_archive(repo_root, output_path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
