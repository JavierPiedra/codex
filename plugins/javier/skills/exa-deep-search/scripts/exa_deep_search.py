#!/usr/bin/env python3
"""Exa Search API deep modes with native, persistent credential storage."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import getpass
import http.client
import json
import math
import sys
import time
import urllib.error
import urllib.request
import warnings


ENDPOINT = "https://api.exa.ai/search"
KEYRING_SERVICE = "codex.javier.exa-deep-search"
KEYRING_ACCOUNT = "api-key"
MODES = ("deep", "deep-reasoning")
RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRY_DELAY = 30
COST_NOTE = (
    "costDollars is Exa's estimated USD cost for this response, not final billing "
    "or an aggregate of retry attempts. Missing cost is unknown, not zero."
)


class ExaError(RuntimeError):
    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.details = {"code": code, "message": message, **details}


def native_keyring():
    """Select only the shipped native OS backend, never configured alternatives."""
    try:
        if sys.platform == "darwin":
            from keyring.backends.macOS import Keyring
            backend = Keyring()
        elif sys.platform == "win32":
            from keyring.backends.Windows import WinVaultKeyring
            backend = WinVaultKeyring()
        else:
            raise ExaError("UNSUPPORTED_PLATFORM", "Use native macOS Keychain or Windows Credential Locker.")
        if backend.priority <= 0:
            raise RuntimeError()
        return backend
    except ExaError:
        raise
    except Exception:
        raise ExaError(
            "CREDENTIAL_STORE_UNAVAILABLE",
            "Native credential storage is unavailable. Run the shared source setup "
            "with --with-runtime, use its recorded Python, and check OS credential-store access. "
            "No plaintext fallback is used.",
        ) from None


def read_credential(backend) -> str | None:
    try:
        key = backend.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except Exception:
        raise ExaError("CREDENTIAL_STORE_UNAVAILABLE",
                       "Cannot read the native credential store; check OS access and the shared runtime.") from None
    return key


def load_api_key() -> str:
    key = read_credential(native_keyring())
    if key is None:
        raise ExaError("MISSING_API_KEY", "Run setup in a local interactive terminal before searching.")
    if not isinstance(key, str) or not key or not all(33 <= ord(char) <= 126 for char in key):
        raise ExaError("INVALID_STORED_KEY", "Stored credential is invalid; run update with a valid API key.")
    return key


def prompt_api_key() -> str:
    if not sys.stdin.isatty():
        raise ExaError("HIDDEN_INPUT_UNAVAILABLE", "Run this command yourself in a local interactive terminal.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            key = getpass.getpass("Exa API key (hidden): ").strip()
    except (getpass.GetPassWarning, EOFError, OSError):
        raise ExaError("HIDDEN_INPUT_UNAVAILABLE", "Hidden input is unavailable; use a local interactive terminal.") from None
    if not key or not all(33 <= ord(char) <= 126 for char in key):
        raise ExaError("INVALID_API_KEY", "Enter a nonempty API key without whitespace or control characters.")
    return key


def manage_credential(command: str) -> dict:
    backend = native_keyring()
    existing = read_credential(backend)
    if command == "remove":
        if existing is not None:
            try:
                backend.delete_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
                if backend.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT) is not None:
                    raise RuntimeError()
            except Exception:
                raise ExaError("CREDENTIAL_REMOVE_FAILED", "Cannot confirm removal; check native credential-store access.") from None
        return {"action": command, "removed": existing is not None}
    if command == "setup" and existing is not None:
        raise ExaError("KEY_ALREADY_EXISTS", "A key is already stored; use update to replace it.")
    if command == "update" and existing is None:
        raise ExaError("MISSING_API_KEY", "No saved key exists; use setup first.")
    key = prompt_api_key()
    try:
        backend.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, key)
        if backend.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT) != key:
            raise RuntimeError()
    except Exception:
        raise ExaError("CREDENTIAL_WRITE_FAILED",
                       "Cannot confirm storage; check native credential-store access. No plaintext fallback is used.") from None
    return {"action": command, "stored": True, "service": KEYRING_SERVICE, "account": KEYRING_ACCOUNT}


def redact(value, key: str):
    """Do not print a credential even if a provider response echoes it."""
    if isinstance(value, str):
        return value.replace(key, "[REDACTED]")
    if isinstance(value, list):
        return [redact(item, key) for item in value]
    if isinstance(value, dict):
        return {redact(name, key): redact(item, key) for name, item in value.items()}
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def retry_delay(header: str | None, attempt: int) -> float:
    if header is None:
        return float(2 ** (attempt - 1))
    try:
        delay = float(header)
    except ValueError:
        try:
            date = parsedate_to_datetime(header)
            delay = (date - datetime.now(timezone.utc)).total_seconds()
        except (ValueError, TypeError, OverflowError):
            return float(2 ** (attempt - 1))
    if not math.isfinite(delay) or delay > MAX_RETRY_DELAY:
        raise ExaError("RETRY_DELAY_EXCEEDED", "Retry-After exceeds the 30-second bound; try again later.")
    return max(0.0, delay)


def api_error(response, key: str, attempt: int) -> ExaError:
    messages = {
        400: "Invalid Search API request; correct its parameters.",
        401: "Exa rejected the API key; run update with a valid key.",
        402: "Exa credits or spending budget are exhausted; check the Exa account.",
        403: "Exa denied access; check the key's feature access and returned error.",
        429: "Exa rate limit reached; retry later.",
    }
    try:
        payload = redact(json.loads(response.read(65536)), key)
    except (ValueError, OSError, http.client.HTTPException):
        payload = {}
    finally:
        response.close()
    details = {"httpStatus": response.code, "attempts": attempt, "costNote": COST_NOTE}
    if isinstance(payload, dict):
        for name in ("requestId", "tag", "error", "costDollars"):
            if name in payload:
                details["apiError" if name == "error" else name] = payload[name]
    return ExaError("HTTP_ERROR", messages.get(response.code, "Exa Search API request failed."), **details)


def normalize_response(payload, mode: str, attempt: int, synthesize: bool) -> dict:
    details = {"attempts": attempt, "costNote": COST_NOTE}
    if isinstance(payload, dict):
        details.update({name: payload[name] for name in ("requestId", "costDollars") if name in payload})
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ExaError("INVALID_RESPONSE", "Exa returned no valid results array; completion may have been billed.", **details)
    for result in payload["results"]:
        if not isinstance(result, dict) or not isinstance(result.get("url"), str) or not result["url"].startswith(("https://", "http://")):
            raise ExaError("INVALID_RESPONSE", "Exa returned a result without a source URL.", **details)
    output = payload.get("output")
    if synthesize and (not isinstance(output, dict) or not isinstance(output.get("content"), str) or
                       not isinstance(output.get("grounding"), list)):
        raise ExaError("INVALID_RESPONSE", "Exa returned no valid synthesized text and grounding.", **details)
    return {"mode": mode, "attempts": attempt,
            "requestId": payload.get("requestId"), "results": payload["results"],
            "output": output, "costDollars": payload.get("costDollars"), "costNote": COST_NOTE}


def search(query: str, *, mode: str = "deep", num_results: int = 10,
           synthesize: bool = False, include_domains: list[str] | None = None,
           additional_queries: list[str] | None = None, retries: int = 2) -> dict:
    if not query.strip() or mode not in MODES or not 1 <= num_results <= 100 or not 0 <= retries <= 2:
        raise ExaError("INVALID_REQUEST", "Provide a query, a deep mode, 1–100 results, and 0–2 retries.")
    if additional_queries and (len(additional_queries) > 10 or any(not item.strip() for item in additional_queries)):
        raise ExaError("INVALID_REQUEST", "Provide at most 10 nonempty additional queries.")
    if include_domains and (len(include_domains) > 1200 or any(not item.strip() for item in include_domains)):
        raise ExaError("INVALID_REQUEST", "Provide at most 1200 nonempty domain filters.")
    body = {"query": query, "type": mode, "numResults": num_results, "contents": {"highlights": True}}
    if synthesize:
        body["outputSchema"] = {"type": "text", "description": "Answer the query with grounded findings and state evidence gaps."}
    if include_domains:
        body["includeDomains"] = include_domains
    if additional_queries:
        body["additionalQueries"] = additional_queries
    key = load_api_key()
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"x-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    opener = urllib.request.build_opener(NoRedirect())
    for attempt in range(1, retries + 2):
        try:
            with opener.open(request, timeout=60) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as response:
            header = response.headers.get("Retry-After") if response.headers else None
            failure = api_error(response, key, attempt)
            if response.code not in RETRY_STATUSES or attempt > retries:
                raise failure from None
            try:
                delay = retry_delay(header, attempt)
            except ExaError as exc:
                failure.details["retryStopped"] = exc.details["code"]
                failure.details["retryMessage"] = exc.details["message"]
                raise failure from None
            time.sleep(delay)
            continue
        except (urllib.error.URLError, OSError, http.client.HTTPException):
            raise ExaError("TRANSPORT_ERROR", "Search transport failed or timed out. Completion and cost are uncertain; "
                           "the request was not replayed.", attempts=attempt) from None
        except (ValueError, UnicodeError):
            raise ExaError("INVALID_RESPONSE", "Exa returned invalid JSON; completion may have been billed.", attempts=attempt) from None
        return normalize_response(redact(payload, key), mode, attempt, synthesize)
    raise AssertionError("Attempt bound exhausted")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("setup", "update", "remove"):
        commands.add_parser(name, help=f"{name.capitalize()} the saved native-store credential; no API call.")
    research = commands.add_parser("search", help="Make a chargeable Exa Search API request.")
    research.add_argument("query")
    research.add_argument("--mode", choices=MODES, default="deep")
    research.add_argument("--num-results", type=int, choices=range(1, 101), default=10, metavar="1–100")
    research.add_argument("--synthesize", action="store_true", help="Request generated text and field-level grounding.")
    research.add_argument("--include-domain", action="append", default=[])
    research.add_argument("--additional-query", action="append", default=[])
    research.add_argument("--retries", type=int, choices=range(3), default=2,
                          help="Retry selected HTTP failures at most 0–2 times (default 2); retries may add cost.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "search":
            result = search(args.query, mode=args.mode, num_results=args.num_results,
                            synthesize=args.synthesize, include_domains=args.include_domain,
                            additional_queries=args.additional_query, retries=args.retries)
        else:
            result = manage_credential(args.command)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except ExaError as exc:
        print(json.dumps({"error": exc.details}, ensure_ascii=False), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(json.dumps({"error": {"code": "INTERRUPTED", "message": "Stopped; any in-flight Search API completion and cost are uncertain."}}), file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
