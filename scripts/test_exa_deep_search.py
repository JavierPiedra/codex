"""Offline Search API and credential contracts; no real secrets or network."""
import contextlib
from datetime import datetime, timedelta, timezone
from email.message import Message
from email.utils import format_datetime
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch
import urllib.error
import warnings

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "plugins/javier/skills/exa-deep-search/scripts/exa_deep_search.py"
spec = importlib.util.spec_from_file_location("exa_search_test", PATH)
exa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exa)
FAKE_KEY = "offline-fixture-only"


def success(mode="deep", **extra):
    payload = {"results": [{"title": "Fixture source", "url": "https://example.com/research",
                             "publishedDate": "2026-10-01", "highlights": ["Fixture evidence"]}],
               "requestId": "offline-request", "resolvedSearchType": mode, **extra}
    return io.BytesIO(json.dumps(payload).encode())


def failure(status, *, retry_after=None, body=None):
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError(exa.ENDPOINT, status, "fixture", headers,
                                  io.BytesIO(json.dumps(body or {"error": "Fixture error", "requestId": "offline-error"}).encode()))


class SearchContract(unittest.TestCase):
    def setUp(self):
        self.backend = Mock()
        self.backend.get_password.return_value = FAKE_KEY
        self.opener = Mock()
        for target, value in (("native_keyring", self.backend),
                              ("urllib.request.build_opener", self.opener)):
            mocked = patch.object(exa, target, return_value=value) if "." not in target else patch(target, return_value=value)
            mocked.start()
            self.addCleanup(mocked.stop)
        sleeper = patch.object(exa.time, "sleep")
        self.sleep = sleeper.start()
        self.addCleanup(sleeper.stop)

    def test_both_deep_modes_use_search_post_and_automatic_native_key(self):
        for mode in exa.MODES:
            with self.subTest(mode=mode), patch.dict(os.environ, {"EXA_API_KEY": "ignored-fixture"}):
                self.opener.open.return_value = success(mode, costDollars={"total": 0.015})
                result = exa.search("Fixture question", mode=mode, num_results=5,
                                    include_domains=["example.com"], additional_queries=["distinct fixture"])
                request = self.opener.open.call_args.args[0]
                self.assertEqual(request.full_url, "https://api.exa.ai/search")
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(request.get_header("X-api-key"), FAKE_KEY)
                self.assertNotIn(FAKE_KEY, request.data.decode())
                self.assertEqual(json.loads(request.data), {"query": "Fixture question", "type": mode,
                    "numResults": 5, "contents": {"highlights": True}, "includeDomains": ["example.com"],
                    "additionalQueries": ["distinct fixture"]})
                self.assertEqual(self.opener.open.call_args.kwargs, {"timeout": 60})
                self.assertEqual(result["costDollars"]["total"], 0.015)
                self.assertEqual(result["results"][0]["url"], "https://example.com/research")
                self.assertEqual(result["requestId"], "offline-request")
                self.assertEqual(result["attempts"], 1)
                self.assertNotIn(FAKE_KEY, json.dumps(result))
        self.backend.get_password.assert_called_with("codex.javier.exa-deep-search", "api-key")

    def test_synthesis_preserves_content_grounding_and_unknown_cost(self):
        output = {"content": "Fixture answer", "grounding": [{"field": "answer", "confidence": "high",
                    "citations": [{"url": "https://example.com/research", "title": "Fixture source"}]}]}
        self.opener.open.return_value = success("deep-reasoning", output=output)
        result = exa.search("Fixture", mode="deep-reasoning", synthesize=True)
        body = json.loads(self.opener.open.call_args.args[0].data)
        self.assertEqual(body["outputSchema"]["type"], "text")
        self.assertEqual(result["output"], output)
        self.assertIsNone(result["costDollars"])

    def test_transient_http_failures_retry_same_deep_request_with_bounds(self):
        self.opener.open.side_effect = [failure(429, retry_after="3"), failure(503), success()]
        result = exa.search("Fixture")
        self.assertEqual(result["attempts"], 3)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [3.0, 2.0])
        requests = [call.args[0] for call in self.opener.open.call_args_list]
        self.assertTrue(all(request is requests[0] for request in requests))
        self.opener.open.reset_mock()
        self.sleep.reset_mock()
        self.opener.open.side_effect = [failure(500), failure(502), failure(504)]
        with self.assertRaises(exa.ExaError) as caught:
            exa.search("Fixture")
        self.assertEqual(caught.exception.details["attempts"], 3)
        self.assertEqual(self.opener.open.call_count, 3)
        self.assertEqual(self.sleep.call_count, 2)

    def test_retry_after_above_bound_stops_and_http_dates_work(self):
        for header in ("31", "Infinity"):
            with self.subTest(header=header):
                self.opener.open.reset_mock()
                self.opener.open.side_effect = failure(429, retry_after=header)
                with self.assertRaises(exa.ExaError) as caught:
                    exa.search("Fixture")
                self.assertEqual(caught.exception.details["retryStopped"], "RETRY_DELAY_EXCEEDED")
                self.assertEqual(self.opener.open.call_count, 1)
        now = datetime.now(timezone.utc)
        self.assertGreater(exa.retry_delay(format_datetime(now + timedelta(seconds=10)), 1), 8)
        self.assertEqual(exa.retry_delay("invalid-fixture", 2), 2)
        self.sleep.assert_not_called()

    def test_nonretryable_http_errors_and_disabled_retries_stop_once(self):
        for status in (400, 401, 402, 403, 302, 429, 500, 503):
            with self.subTest(status=status):
                self.opener.open.reset_mock()
                self.opener.open.side_effect = failure(status)
                with self.assertRaises(exa.ExaError) as caught:
                    exa.search("Fixture", retries=0 if status in exa.RETRY_STATUSES else 2)
                self.assertEqual(caught.exception.details["httpStatus"], status)
                self.assertEqual(self.opener.open.call_count, 1)
        self.sleep.assert_not_called()

    def test_transport_and_malformed_responses_never_replay(self):
        for problem in (urllib.error.URLError(FAKE_KEY), TimeoutError(FAKE_KEY),
                        http.client.IncompleteRead(b"fixture partial")):
            with self.subTest(problem=type(problem)):
                self.opener.open.reset_mock()
                self.opener.open.side_effect = problem
                with self.assertRaises(exa.ExaError) as caught:
                    exa.search("Fixture")
                self.assertEqual(caught.exception.details["code"], "TRANSPORT_ERROR")
                self.assertNotIn(FAKE_KEY, str(caught.exception))
                self.assertEqual(self.opener.open.call_count, 1)
        self.opener.open.side_effect = None
        for response in (io.BytesIO(b"invalid-json"), success(results={}), success(results=[{}]),
                         success(output={})):
            self.opener.open.reset_mock()
            self.opener.open.return_value = response
            with self.assertRaises(exa.ExaError):
                exa.search("Fixture", synthesize=True)
            self.assertEqual(self.opener.open.call_count, 1)
        self.sleep.assert_not_called()

    def test_deprecated_mode_metadata_does_not_reject_or_change_requested_deep_mode(self):
        for legacy_value in (None, "", "neural", "auto"):
            with self.subTest(legacy_value=legacy_value):
                self.opener.open.reset_mock()
                self.opener.open.return_value = success(legacy_value, costDollars={"total": 0.012})
                result = exa.search("Fixture")
                self.assertEqual(result["mode"], "deep")
                self.assertEqual(result["costDollars"], {"total": 0.012})
                self.assertNotIn("resolvedSearchType", result)
                self.assertEqual(json.loads(self.opener.open.call_args.args[0].data)["type"], "deep")
                self.assertEqual(self.opener.open.call_count, 1)

    def test_empty_results_are_valid_and_cost_zero_is_preserved(self):
        self.opener.open.return_value = success(results=[], costDollars={"total": 0})
        result = exa.search("Fixture")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["costDollars"], {"total": 0})

    def test_invalid_requests_fail_before_credentials_and_network(self):
        for args in ({"mode": "auto"}, {"num_results": 101}, {"retries": 3},
                     {"additional_queries": ["fixture"] * 11}, {"include_domains": [""]}):
            with self.subTest(args=args), self.assertRaises(exa.ExaError):
                exa.search("Fixture", **args)
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_missing_or_invalid_store_never_uses_environment_key(self):
        with patch.dict(os.environ, {"EXA_API_KEY": "ignored-fixture"}):
            for stored in (None, "", "fixture\nkey"):
                self.backend.get_password.return_value = stored
                with self.assertRaises(exa.ExaError):
                    exa.search("Fixture")
        self.opener.open.assert_not_called()

    def test_cli_redacts_success_and_error_even_if_provider_echoes_key(self):
        self.opener.open.return_value = success(highlights=[FAKE_KEY], results=[{
            "url": "https://example.com", "title": FAKE_KEY, "highlights": [FAKE_KEY]}])
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(exa.main(["search", "Fixture"]), 0)
        self.assertNotIn(FAKE_KEY, out.getvalue() + err.getvalue())
        self.opener.open.side_effect = failure(401, body={"error": FAKE_KEY,
            "tag": FAKE_KEY, "requestId": FAKE_KEY, "costDollars": {"total": 0.01}})
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(exa.main(["search", "Fixture"]), 1)
        self.assertNotIn(FAKE_KEY, out.getvalue() + err.getvalue())
        self.assertEqual(json.loads(err.getvalue())["error"]["costDollars"], {"total": 0.01})

    def test_redirect_handler_refuses_secret_forwarding(self):
        request = exa.urllib.request.Request(exa.ENDPOINT, headers={"x-api-key": FAKE_KEY})
        for status in (301, 302, 303, 307, 308):
            self.assertIsNone(exa.NoRedirect().redirect_request(request, None, status, "fixture", {}, "https://other.example"))


class CredentialContract(unittest.TestCase):
    def setUp(self):
        self.store = {}
        self.backend = Mock()
        self.backend.get_password.side_effect = lambda service, account: self.store.get((service, account))
        self.backend.set_password.side_effect = lambda service, account, key: self.store.__setitem__((service, account), key)
        self.backend.delete_password.side_effect = lambda service, account: self.store.pop((service, account))
        backend_patch = patch.object(exa, "native_keyring", return_value=self.backend)
        backend_patch.start()
        self.addCleanup(backend_patch.stop)
        network_patch = patch.object(exa.urllib.request, "build_opener", side_effect=AssertionError("No network permitted"))
        network_patch.start()
        self.addCleanup(network_patch.stop)

    def test_setup_persists_across_loads_update_replaces_and_remove_is_idempotent(self):
        output = io.StringIO()
        with patch.object(exa.sys.stdin, "isatty", return_value=True), \
                patch.object(exa.getpass, "getpass", return_value=FAKE_KEY), contextlib.redirect_stdout(output):
            self.assertEqual(exa.main(["setup"]), 0)
        self.assertEqual(exa.load_api_key(), FAKE_KEY)
        self.assertNotIn(FAKE_KEY, output.getvalue())
        with patch.object(exa, "prompt_api_key", return_value="replacement-fixture"):
            exa.manage_credential("update")
        self.assertEqual(exa.load_api_key(), "replacement-fixture")
        self.assertEqual(set(self.store), {("codex.javier.exa-deep-search", "api-key")})
        self.assertTrue(exa.manage_credential("remove")["removed"])
        self.assertFalse(exa.manage_credential("remove")["removed"])
        with self.assertRaises(exa.ExaError):
            exa.load_api_key()

    def test_setup_does_not_overwrite_and_update_requires_existing_entry(self):
        with patch.object(exa, "prompt_api_key") as prompt:
            with self.assertRaises(exa.ExaError):
                exa.manage_credential("update")
            self.store[(exa.KEYRING_SERVICE, exa.KEYRING_ACCOUNT)] = FAKE_KEY
            with self.assertRaises(exa.ExaError):
                exa.manage_credential("setup")
            prompt.assert_not_called()
        self.backend.set_password.assert_not_called()

    def test_invalid_stored_key_can_be_updated_or_removed(self):
        self.store[(exa.KEYRING_SERVICE, exa.KEYRING_ACCOUNT)] = "invalid\nfixture"
        with patch.object(exa, "prompt_api_key", return_value=FAKE_KEY):
            exa.manage_credential("update")
        self.assertEqual(exa.load_api_key(), FAKE_KEY)
        self.store[(exa.KEYRING_SERVICE, exa.KEYRING_ACCOUNT)] = "invalid\nfixture"
        self.assertTrue(exa.manage_credential("remove")["removed"])

    def test_hidden_input_failure_prevents_storage(self):
        def insecure_prompt(*args):
            warnings.warn("fixture echo would follow", exa.getpass.GetPassWarning)
            self.fail("Visible input must never execute")
        with patch.object(exa.sys.stdin, "isatty", return_value=True), \
                patch.object(exa.getpass, "getpass", side_effect=insecure_prompt):
            with self.assertRaises(exa.ExaError) as caught:
                exa.manage_credential("setup")
        self.assertEqual(caught.exception.details["code"], "HIDDEN_INPUT_UNAVAILABLE")
        self.backend.set_password.assert_not_called()
        with patch.object(exa.sys.stdin, "isatty", return_value=False), patch.object(exa.getpass, "getpass") as prompt:
            with self.assertRaises(exa.ExaError):
                exa.prompt_api_key()
            prompt.assert_not_called()

    def test_store_failures_are_safe_errors_and_writes_are_verified(self):
        for operation in ("get_password", "set_password", "delete_password"):
            with self.subTest(operation=operation):
                self.store[(exa.KEYRING_SERVICE, exa.KEYRING_ACCOUNT)] = FAKE_KEY
                method = getattr(self.backend, operation)
                previous = method.side_effect
                method.side_effect = RuntimeError(FAKE_KEY)
                command = "remove" if operation == "delete_password" else "update"
                with patch.object(exa, "prompt_api_key", return_value=FAKE_KEY), self.assertRaises(exa.ExaError) as caught:
                    exa.manage_credential(command)
                self.assertNotIn(FAKE_KEY, str(caught.exception))
                method.side_effect = previous
        self.backend.set_password.side_effect = None
        with patch.object(exa, "prompt_api_key", return_value="different-fixture"), self.assertRaises(exa.ExaError) as caught:
            exa.manage_credential("update")
        self.assertEqual(caught.exception.details["code"], "CREDENTIAL_WRITE_FAILED")


class NativeBackendContract(unittest.TestCase):
    def test_native_backend_selection_ignores_configured_plaintext_backend(self):
        for platform, module_name, class_name in (("darwin", "keyring.backends.macOS", "Keyring"),
                                                  ("win32", "keyring.backends.Windows", "WinVaultKeyring")):
            backend = Mock(priority=5)
            fake = types.ModuleType(module_name)
            setattr(fake, class_name, lambda: backend)
            with patch.dict(sys.modules, {module_name: fake}), patch.object(exa.sys, "platform", platform), \
                    patch.dict(os.environ, {"PYTHON_KEYRING_BACKEND": "keyrings.alt.file.PlaintextKeyring"}):
                self.assertIs(exa.native_keyring(), backend)
        with patch.object(exa.sys, "platform", "linux"), self.assertRaises(exa.ExaError) as caught:
            exa.native_keyring()
        self.assertEqual(caught.exception.details["code"], "UNSUPPORTED_PLATFORM")

    def test_unavailable_native_backend_has_no_configured_fallback(self):
        fake = types.ModuleType("keyring.backends.macOS")
        fake.Keyring = Mock(side_effect=RuntimeError(FAKE_KEY))
        with patch.dict(sys.modules, {"keyring.backends.macOS": fake}), patch.object(exa.sys, "platform", "darwin"), \
                self.assertRaises(exa.ExaError) as caught:
            exa.native_keyring()
        self.assertEqual(caught.exception.details["code"], "CREDENTIAL_STORE_UNAVAILABLE")
        self.assertNotIn(FAKE_KEY, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
