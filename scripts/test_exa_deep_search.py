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
import tempfile
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


def stream(events, *, terminate=True):
    content = ": keepalive\r\n\r\n" + "".join("event: message\ndata: " + json.dumps(event) + "\n\n" for event in events)
    if terminate:
        content += "data: [DONE]\n\n"
    response = io.BytesIO(content.encode())
    response.headers = {"Content-Type": "text/event-stream; charset=utf-8"}
    return response


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
                self.assertEqual(self.opener.open.call_args.kwargs, {"timeout": 120})
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

    def test_complete_request_forwards_every_current_deep_compatible_option(self):
        schema = {"type": "object", "properties": {"findings": {"type": "array", "items": {
            "type": "object", "properties": {"claim": {"type": "string"}}, "required": ["claim"]}}},
            "required": ["findings"], "additionalProperties": False}
        body = {"query": "Fixture research", "type": "deep-reasoning", "numResults": 10,
            "includeDomains": ["*.example.com", "example.org/research"], "excludeDomains": ["example.net"],
            "startPublishedDate": "2026-04-11T06:00:00.000Z", "endPublishedDate": "2026-10-12T05:59:59.999Z",
            "moderation": True, "additionalQueries": ["Fixture alternative"], "category": "publication",
            "userLocation": {"country": "MX", "latitude": 19.4, "longitude": -99.1},
            "objective": "Audit independently defined requirements", "userIdentifier": "opaque-fixture_1",
            "systemPrompt": "Prefer original evidence", "stream": False, "outputSchema": schema,
            "contents": {"text": {"maxCharacters": 10000, "includeHtmlTags": True, "verbosity": "full",
                "includeSections": ["body", "metadata"], "excludeSections": ["navigation", "footer"]},
                "highlights": {"query": "Fixture passages", "dynamic": True, "verbosity": "high"},
                "summary": {"query": "Fixture summary", "schema": {"type": "object", "properties": {
                    "summary": {"type": "string"}}}},
                "extras": {"links": 3, "imageLinks": 1, "richImageLinks": 2, "richLinks": 4, "codeBlocks": 5},
                "livecrawlTimeout": 90000, "maxAgeHours": 0, "subpages": 3, "subpageTarget": ["docs", "research"]}}
        output = {"content": {"findings": [{"claim": "Fixture claim"}]}, "grounding": []}
        self.opener.open.return_value = success(output=output, searchTime=123)
        original = json.dumps(body, sort_keys=True)
        result = exa.search(request=body, betas=[exa.BETAS[0]], timeout=300)
        request = self.opener.open.call_args.args[0]
        self.assertEqual(json.loads(request.data), body)
        self.assertEqual(json.dumps(body, sort_keys=True), original)
        self.assertEqual(request.get_header("Exa-beta"), exa.BETAS[0])
        self.assertEqual(self.opener.open.call_args.kwargs["timeout"], 300)
        self.assertEqual(result["output"], output)
        self.assertEqual(result["searchTime"], 123)
        self.assertEqual(result["mode"], "deep-reasoning")

    def test_user_example_is_supported_as_a_request_file_and_dry_run_is_offline(self):
        body = {"query": "Fixture research", "type": "deep-reasoning", "numResults": 10,
            "startPublishedDate": "2026-04-11T06:00:00.000Z", "endPublishedDate": "2026-10-12T05:59:59.999Z",
            "outputSchema": {"type": "text"}, "contents": {"highlights": True, "maxAgeHours": 0}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text(json.dumps(body), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(exa.main(["search", "--request-file", str(path), "--dry-run", "--retries", "0"]), 0)
            preview = json.loads(out.getvalue())
        self.assertEqual(preview["request"], body)
        self.assertFalse(preview["chargeable"])
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_active_variants_and_explicit_nulls_are_not_replaced_with_defaults(self):
        for contents in (None, {}, {"text": True, "highlights": False, "maxAgeHours": -1},
                         {"highlights": {"maxCharacters": 300}, "subpageTarget": "docs"}):
            with self.subTest(contents=contents):
                body = {"query": "Fixture", "contents": contents, "numResults": None,
                        "category": "custom topical hint", "userLocation": "MX", "stream": True}
                self.opener.open.return_value = success()
                exa.search(request=body)
                sent = json.loads(self.opener.open.call_args.args[0].data)
                self.assertEqual(sent, {**body, "type": "deep"})
        # stream without outputSchema is ordinary JSON transport for the same explicit deep mode.
        self.assertEqual(sent["type"], "deep")

    def test_invalid_options_and_documented_incompatibilities_stop_before_auth(self):
        cases = [
            {"type": None}, {"type": "auto"}, {"type": "deep-lite"}, {"apiKey": FAKE_KEY}, {"unknown": True},
            {"startPublishedDate": "2026-04-11"}, {"startPublishedDate": "2026-02-30T00:00:00Z"},
            {"startPublishedDate": "2026-10-11T00:00:00Z", "endPublishedDate": "2026-04-11T00:00:00Z"},
            {"category": "people", "excludeDomains": []}, {"category": "company", "startPublishedDate": "2026-01-01T00:00:00Z"},
            {"compliance": "hipaa"}, {"contents": {"snapshotAsOf": "2026-10-01"}},
            {"userLocation": {"latitude": 19.4}}, {"userLocation": {"latitude": 91, "longitude": 0}},
            {"userLocation": {"country": "Mexico"}}, {"userIdentifier": "email@example.com"},
            {"objective": "x" * 4097}, {"numResults": True}, {"moderation": "true"},
            {"contents": {"maxAgeHours": 721}}, {"contents": {"maxAgeHours": -2}},
            {"contents": {"livecrawlTimeout": 90001}}, {"contents": {"text": {"includeSections": ["invalid"]}}},
            {"contents": {"extras": {"links": 1001}}}, {"contents": {"subpages": 101}},
            {"userLocation": {"latitude": float("nan"), "longitude": 0}},
        ]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(exa.ExaError) as caught:
                exa.search(request={"query": "Fixture", **fields})
            self.assertNotIn(FAKE_KEY, json.dumps(caught.exception.details))
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_deprecated_parameters_are_rejected_instead_of_silently_ignored(self):
        cases = [{name: None} for name in ("startCrawlDate", "endCrawlDate", "includeText", "excludeText", "context")]
        cases += [{"contents": {name: None}} for name in ("context", "livecrawl", "crawledBeforeDate")]
        cases += [{"contents": {"highlights": {name: None}}} for name in ("numSentences", "highlightsPerUrl")]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(exa.ExaError):
                exa.search(request={"query": "Fixture", **fields})
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_highlight_beta_requires_explicit_opt_in_and_valid_combinations(self):
        for highlights, betas in (({"dynamic": True}, []), ({"dynamic": False}, []), ({"verbosity": "low"}, []),
                ({"dynamic": True, "maxCharacters": 10}, [exa.BETAS[0]]),
                ({"verbosity": "medium", "maxCharacters": 10}, [exa.BETAS[0]]), (True, ["unknown-beta"])):
            with self.subTest(highlights=highlights), self.assertRaises(exa.ExaError):
                exa.search(request={"query": "Fixture", "contents": {"highlights": highlights}}, betas=betas)
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_output_schema_limits_and_json_schema_validity_prevent_billable_errors(self):
        invalid = [{"type": "object", "properties": {f"p{i}": {"type": "string"} for i in range(11)}},
            {"type": "object", "properties": {"items": {"type": "array"}}},
            {"type": "object", "properties": {"value": {"type": "invalid-type"}}},
            {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object",
                "properties": {"nested": {"type": "object"}}}}}},
            {"type": "object", "properties": {"a": {"type": "object", "properties": {"b": {
                "type": "object", "properties": {"c": {"type": "object"}}}}}}}]
        for schema in invalid:
            with self.subTest(schema=schema), self.assertRaises(exa.ExaError):
                exa.search(request={"query": "Fixture", "outputSchema": schema})
        with self.assertRaises(exa.ExaError):
            exa.search(request={"query": "Fixture", "contents": {"summary": {"schema": {"type": "bad-type"}}}})
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_sse_completion_uses_authoritative_output_after_reset_and_preserves_sources_cost(self):
        sources = [{"url": "https://example.com/research", "extras": {"links": ["https://example.com/docs"]}}]
        final = {"content": {"claim": "Fixture answer"}, "grounding": [{"field": "claim", "confidence": "high",
                 "citations": [{"url": "https://example.com/research", "title": "Fixture source"}]}]}
        self.opener.open.return_value = stream([
            {"type": "text-delta", "delta": FAKE_KEY[:10]}, {"type": "text-delta", "delta": FAKE_KEY[10:]},
            {"type": "stream-reset", "streamReset": True},
            {"type": "grounding", "grounding": []}, {"type": "results", "results": sources, "requestId": "stream-fixture"},
            {"type": "done", "output": final, "searchTime": 456, "costDollars": {"total": 0.12}}])
        result = exa.search(request={"query": "Fixture", "type": "deep-reasoning", "stream": True,
            "outputSchema": {"type": "object", "properties": {"claim": {"type": "string"}}}})
        self.assertEqual(result["output"], final)
        self.assertEqual(result["results"], sources)
        self.assertEqual(result["costDollars"], {"total": 0.12})
        self.assertEqual(result["requestId"], "stream-fixture")
        self.assertEqual(result["searchTime"], 456)
        self.assertNotIn(FAKE_KEY, json.dumps(result))
        self.assertTrue(json.loads(self.opener.open.call_args.args[0].data)["stream"])

    def test_sse_errors_truncation_and_malformed_events_are_redacted_and_never_replayed(self):
        cases = [stream([{"type": "error", "error": {"message": FAKE_KEY}, "requestId": "failed-stream"}]),
                 stream([{"type": "text-delta", "delta": "Partial"}]),
                 stream([{"type": "text-delta", "delta": "Partial"}], terminate=False),
                 stream([{"type": "unknown-event"}]), stream([{"type": "done", "output": None, "searchTime": 10}])]
        for response in cases:
            with self.subTest(response=response):
                self.opener.open.reset_mock()
                self.opener.open.return_value = response
                with self.assertRaises(exa.ExaError) as caught:
                    exa.search(request={"query": "Fixture", "stream": True, "outputSchema": {"type": "text"}})
                self.assertEqual(self.opener.open.call_count, 1)
                self.assertNotIn(FAKE_KEY, json.dumps(caught.exception.details))
        self.sleep.assert_not_called()

    def test_request_files_reject_ambiguous_inputs_invalid_json_duplicates_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            for content in ('[]', 'invalid-json', '{"query":"first","query":"second"}',
                            '{"query":"Fixture","numResults":NaN}'):
                path.write_text(content, encoding="utf-8")
                with self.subTest(content=content), self.assertRaises(exa.ExaError):
                    exa.read_request_file(path)
            path.unlink()
            with self.assertRaises(exa.ExaError):
                exa.read_request_file(path)
        with self.assertRaises(exa.ExaError):
            exa.search("Ambiguous override", request={"query": "Fixture"})
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

    def test_missing_validation_dependency_and_bundled_schema_have_safe_offline_errors(self):
        with patch.object(exa, "Draft202012Validator", None), self.assertRaises(exa.ExaError) as caught:
            exa.search("Fixture", dry_run=True)
        self.assertEqual(caught.exception.details["code"], "MISSING_DEPENDENCY")
        with patch.object(exa, "REQUEST_SCHEMA", Path("missing-fixture.schema.json")), self.assertRaises(exa.ExaError) as caught:
            exa.search("Fixture", dry_run=True)
        self.assertEqual(caught.exception.details["code"], "MISSING_RESOURCE")
        self.backend.get_password.assert_not_called()
        self.opener.open.assert_not_called()

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
