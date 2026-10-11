"""Host-safe migration and helper checks, using synthetic data only."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parent.parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


setup = module("shared_setup", ROOT / "scripts/setup.py")
waka = module("waka", ROOT / "plugins/javier/skills/invoice-goodancestor/scripts/wakatime_client_hours.py")
models = module("models", ROOT / "plugins/javier/skills/which-model-rn/scripts/which_model.py")
whatsapp = module("whatsapp", ROOT / "plugins/javier/skills/whatsapp-group-review/scripts/export_whatsapp_group.py")


class Portability(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "José Piedra" / ".codex"
        self.home.mkdir(parents=True)

    def test_guidance_preserves_host_configuration_and_is_idempotent(self):
        for name in ("config.toml", "auth.json"):
            (self.home / name).write_bytes(b"host-local fixture")
        (self.home / "AGENTS.md").write_bytes(b"previous guidance")
        awra = self.home / "Guía Awra"
        awra.mkdir()
        first = setup.apply_guidance(self.home, awra_guidance_root=awra)
        self.assertEqual((Path(first["backup"]) / "AGENTS.md").read_bytes(), b"previous guidance")
        self.assertEqual(setup.apply_guidance(self.home)["changed"], [])
        for name in ("config.toml", "auth.json"):
            self.assertEqual((self.home / name).read_bytes(), b"host-local fixture")
        recorded = tomllib.loads((self.home / "javier-paths.toml").read_text(encoding="utf-8"))
        self.assertEqual(Path(recorded["awra_guidance_root"]), awra.resolve())

    def test_override_and_invalid_external_path_fail_before_writes(self):
        (self.home / "AGENTS.override.md").write_bytes(b"override")
        with self.assertRaises(ValueError):
            setup.apply_guidance(self.home)
        self.assertFalse((self.home / "AGENTS.md").exists())
        (self.home / "AGENTS.override.md").unlink()
        with self.assertRaises(ValueError):
            setup.apply_guidance(self.home, awra_voice_root=self.home / "absent")
        self.assertFalse((self.home / "javier-paths.toml").exists())

    def test_guidance_refuses_to_dirty_a_git_checkout(self):
        subprocess.run(["git", "init", str(self.home)], capture_output=True, check=True)
        (self.home / "AGENTS.md").write_bytes(b"tracked older guidance")
        subprocess.run(["git", "-C", str(self.home), "add", "AGENTS.md"],
                       capture_output=True, check=True)
        with self.assertRaisesRegex(ValueError, "AGENTS.md"):
            setup.apply_guidance(self.home)
        self.assertEqual((self.home / "AGENTS.md").read_bytes(), b"tracked older guidance")
        self.assertFalse((self.home / "javier-paths.toml").exists())

    def test_guidance_accepts_matching_tracked_files(self):
        subprocess.run(["git", "init", str(self.home)], capture_output=True, check=True)
        shutil.copyfile(ROOT / "AGENTS.md", self.home / "AGENTS.md")
        subprocess.run(["git", "-C", str(self.home), "add", "AGENTS.md"],
                       capture_output=True, check=True)
        result = setup.apply_guidance(self.home)
        self.assertNotIn("AGENTS.md", result["changed"])
        self.assertTrue((self.home / "javier-paths.toml").exists())

    def retirement_fixture(self):
        source = self.home / "source"
        installed = self.home / "installed"
        (source / "plugins/javier").mkdir(parents=True)
        (source / "plugins/javier/plugin.json").write_bytes(b"package fixture")
        shutil.copytree(source / "plugins/javier", installed)
        originals = {}
        for name in ("one", "two"):
            skill = self.home / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_bytes(b"original fixture")
            originals[name] = setup.file_hashes(skill)
        (source / "scripts").mkdir()
        (source / "scripts/migration.json").write_text(json.dumps({"legacy_files": originals}), encoding="utf-8")
        return source, installed

    def test_retirement_refuses_modified_copy_before_moving_any(self):
        source, installed = self.retirement_fixture()
        (self.home / "skills/two/SKILL.md").write_bytes(b"local edit")
        with self.assertRaises(ValueError):
            setup.retire_local_skills(self.home, source=source, installed_plugin=installed)
        self.assertTrue((self.home / "skills/one").exists())

    def test_retirement_verifies_installed_package_and_archives_unchanged_skills(self):
        source, installed = self.retirement_fixture()
        (installed / "plugin.json").write_bytes(b"different version")
        with self.assertRaises(ValueError):
            setup.retire_local_skills(self.home, source=source, installed_plugin=installed)
        shutil.copyfile(source / "plugins/javier/plugin.json", installed / "plugin.json")
        dry = setup.retire_local_skills(self.home, source=source, installed_plugin=installed, dry_run=True)
        self.assertEqual(len(dry), 2)
        self.assertTrue((self.home / "skills/one").exists())
        self.assertEqual(len(setup.retire_local_skills(self.home, source=source, installed_plugin=installed)), 2)
        self.assertFalse((self.home / "skills/one").exists())
        self.assertEqual(len(list((self.home / "javier-setup-backups").rglob("SKILL.md"))), 2)

    def test_native_credentials_use_os_backend_and_keep_service_account_identity(self):
        for platform, module_name, class_name in (("darwin", "keyring.backends.macOS", "Keyring"),
                                                   ("win32", "keyring.backends.Windows", "WinVaultKeyring")):
            backend = Mock()
            backend.get_password.return_value = "fixture-only"
            fake = types.ModuleType(module_name)
            setattr(fake, class_name, lambda: backend)
            with patch.dict(sys.modules, {module_name: fake}), patch.object(waka.sys, "platform", platform), \
                    patch.object(waka.getpass, "getuser", return_value="fixture-account"):
                self.assertEqual(waka.load_api_key(), "fixture-only")
                backend.get_password.assert_called_once_with("codex.invoice-goodancestor.wakatime", "fixture-account")
                backend.get_password.return_value = None
                with self.assertRaises(RuntimeError):
                    waka.load_api_key()

    def test_client_hours_sum_seconds_before_rounding(self):
        result = waka.aggregate_projects({"data": [
            {"projects": [{"name": "Project", "total_seconds": 1810}]},
            {"projects": [{"name": "Project", "total_seconds": 1810}]}]})
        self.assertEqual(result[0]["hours"], "1.01")

    def test_goal_validation_accepts_file_with_spaces_and_rejects_unbounded_goal(self):
        path = self.home / "Goal draft.txt"
        command = [sys.executable, str(ROOT / "plugins/javier/skills/write-goal/scripts/validate_goal.py"), "--file", str(path)]
        path.write_text("/goal Produce an artifact with tests, preserve existing data; if blocked report evidence; stop after 3 attempts.", encoding="utf-8")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        path.write_text("/goal keep trying forever", encoding="utf-8")
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)

    def test_invoice_cli_runs_with_unicode_paths_and_leap_year_dates(self):
        result = subprocess.run([sys.executable, str(ROOT / "plugins/javier/skills/invoice-goodancestor/scripts/invoice_math.py"),
                                 "2024-02", "--timer", "Revisión=1:30", "--project", "Work=2.25", "--json"],
                                capture_output=True, text=True, encoding="utf-8", check=True)
        value = json.loads(result.stdout)
        self.assertEqual((value["end"], value["total"]), ("2024-02-29", "18.75"))

    def test_model_reader_selects_explicit_session_and_exposes_metadata_only(self):
        path = self.home / "rollout-fixture-id.jsonl"
        records = [{"type": "session_meta", "payload": {"session_id": "fixture-id"}},
                   {"type": "response_item", "payload": {"message": "private fixture content"}},
                   {"type": "turn_context", "timestamp": "2026-10-11T00:00:00Z", "payload": {
                       "turn_id": "turn", "model": "fixture-model", "collaboration_mode": {
                           "settings": {"reasoning_effort": "high"}}}}]
        path.write_text("\n".join(json.dumps(row) for row in records), encoding="utf-8")
        self.assertEqual(models.transcript_files("other", self.home), [])
        found = models.transcript_files("fixture-id", self.home)
        result = models.turn_contexts(found)
        self.assertEqual(result[0]["reasoning_effort"], "high")
        self.assertNotIn("private fixture content", json.dumps(result))

    def test_whatsapp_database_is_readonly_and_windows_stops_before_reading(self):
        path = self.home / "Synthetic Chat.sqlite"
        with contextlib.closing(sqlite3.connect(path)) as conn:
            with conn:
                conn.execute("CREATE TABLE ZWACHATSESSION (Z_PK INTEGER, ZPARTNERNAME TEXT)")
                conn.execute("INSERT INTO ZWACHATSESSION VALUES (1, 'Fixture group')")
        with contextlib.closing(whatsapp.open_readonly(path)) as conn:
            self.assertEqual(whatsapp.resolve_group(conn, "Fixture group")["chat_pk"], 1)
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM ZWACHATSESSION")
        output = io.StringIO()
        with patch.object(whatsapp.sys, "platform", "win32"), patch.object(sys, "argv", ["export_whatsapp_group.py"]), \
                patch.object(whatsapp, "open_readonly") as read, contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                whatsapp.main()
            self.assertEqual(result.exception.code, 1)
            read.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["code"], "UNSUPPORTED_PLATFORM")


if __name__ == "__main__":
    unittest.main()
