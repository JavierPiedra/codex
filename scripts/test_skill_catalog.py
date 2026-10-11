"""The current catalog remains exact while the migration snapshot stays historical."""
import json
from pathlib import Path
import tempfile
import unittest

from check import ROOT, check


class SkillCatalog(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("scripts", "plugins/javier/skills", ".agents/plugins", "agents"):
            (self.root / name).mkdir(parents=True)
        for name in ("scripts/migration.json", "scripts/skill-catalog.json", "plugins/javier/plugin.json",
                     ".agents/plugins/marketplace.json"):
            (self.root / name).write_bytes((ROOT / name).read_bytes())
        self.catalog = json.loads((self.root / "scripts/skill-catalog.json").read_text())["skills"]
        for name in self.catalog:
            self.add_skill(name)

    def add_skill(self, name):
        skill = self.root / "plugins/javier/skills" / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Fixture\n---\n", encoding="utf-8")

    def test_catalog_accepts_exact_package_and_rejects_missing_or_unlisted_skills(self):
        self.assertEqual(check(self.root)["skills"], 32)
        self.add_skill("unlisted-fixture")
        with self.assertRaises(AssertionError):
            check(self.root)
        skill = self.root / "plugins/javier/skills/unlisted-fixture"
        (skill / "SKILL.md").unlink()
        skill.rmdir()
        skill = self.root / "plugins/javier/skills/exa-deep-search"
        (skill / "SKILL.md").unlink()
        skill.rmdir()
        with self.assertRaises(AssertionError):
            check(self.root)

    def test_catalog_cannot_drop_migrated_skills_or_admit_exclusions(self):
        for removed, added in (("btw", "fixture-replacement"), ("exa-deep-search", "pdf")):
            with self.subTest(removed=removed, added=added):
                catalog = [name for name in self.catalog if name != removed] + [added]
                (self.root / "scripts/skill-catalog.json").write_text(json.dumps({"skills": catalog}))
                source = self.root / "plugins/javier/skills" / removed
                source.rename(source.with_name(added))
                with self.assertRaises(AssertionError):
                    check(self.root)
                source.with_name(added).rename(source)

    def test_duplicate_catalog_and_missing_resources_still_fail(self):
        catalog_path = self.root / "scripts/skill-catalog.json"
        catalog_path.write_text(json.dumps({"skills": self.catalog + [self.catalog[0]]}))
        with self.assertRaises(AssertionError):
            check(self.root)
        catalog_path.write_text(json.dumps({"skills": self.catalog}))
        skill = self.root / "plugins/javier/skills/exa-deep-search/SKILL.md"
        skill.write_text(skill.read_text() + "[Missing helper](scripts/absent.py)\n")
        with self.assertRaises(AssertionError):
            check(self.root)


if __name__ == "__main__":
    unittest.main()
