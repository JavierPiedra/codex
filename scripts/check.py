#!/usr/bin/env python3
"""Validate the package contract and its resolvable local resources."""
import ast
import json
from pathlib import Path
import re
import tomllib

import yaml

ROOT = Path(__file__).resolve().parent.parent


def check(root=ROOT):
    plugin = root / "plugins/javier"
    manifest = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
    migration = json.loads((root / "scripts/migration.json").read_text(encoding="utf-8"))
    catalog = json.loads((root / "scripts/skill-catalog.json").read_text(encoding="utf-8"))["skills"]
    market = json.loads((root / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "javier" and re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert market["plugins"][0]["source"]["path"] == "./plugins/javier"
    dirs = {p.name for p in (plugin / "skills").iterdir() if p.is_dir()}
    assert len(catalog) == len(set(catalog)), "Duplicate catalog entries"
    assert dirs == set(catalog), "Plugin directories differ from the current catalog"
    assert len(migration["selected"]) == len(set(migration["selected"])), "Duplicate migrated skill entries"
    assert set(migration["selected"]).issubset(dirs), "Missing migrated skill"
    assert not dirs.intersection(migration["excluded"])
    for name in sorted(dirs):
        path = plugin / "skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        assert len(parts) == 3, path
        header = yaml.safe_load(parts[1])
        assert header["name"] == name and isinstance(header["description"], str), path
    for path in plugin.rglob("*.yaml"):
        yaml.safe_load(path.read_text(encoding="utf-8"))
    for path in (root / "agents").glob("*.toml"):
        tomllib.loads(path.read_text(encoding="utf-8"))
    for path in plugin.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in plugin.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if ":" in target or target.startswith(("#", "{", "<")):
                continue
            assert (path.parent / target.split("#")[0]).exists(), (path, target)
        assert not re.search(r"/Users/[^\s`]+|~/.codex/", text), path
        for name in dirs:
            assert not re.search(r"\$" + re.escape(name) + r"(?![-\w])", text), (path, name)
    return {"plugin": manifest["name"], "version": manifest["version"], "skills": len(dirs)}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
