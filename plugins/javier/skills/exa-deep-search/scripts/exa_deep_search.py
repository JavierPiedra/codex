#!/usr/bin/env python3
"""Exa Search API deep modes with native, persistent credential storage."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import getpass
import http.client
import json
import math
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import warnings

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError:
    Draft202012Validator = None


ENDPOINT = "https://api.exa.ai/search"
KEYRING_SERVICE = "codex.javier.exa-deep-search"
KEYRING_ACCOUNT = "api-key"
MODES = ("deep", "deep-reasoning")
BETAS = ("dynamic-highlights-2026-08-28",)
REQUEST_SCHEMA = Path(__file__).resolve().parent.parent / "references/search-request.schema.json"
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


def normalize_response(payload, mode: str, attempt: int, output_schema: dict | None) -> dict:
    details = {"attempts": attempt, "costNote": COST_NOTE}
    if isinstance(payload, dict):
        details.update({name: payload[name] for name in ("requestId", "costDollars") if name in payload})
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ExaError("INVALID_RESPONSE", "Exa returned no valid results array; completion may have been billed.", **details)
    for result in payload["results"]:
        if not isinstance(result, dict) or not isinstance(result.get("url"), str) or not result["url"].startswith(("https://", "http://")):
            raise ExaError("INVALID_RESPONSE", "Exa returned a result without a source URL.", **details)
    output = payload.get("output")
    if output_schema:
        content_type = str if output_schema["type"] == "text" else dict
        if (not isinstance(output, dict) or not isinstance(output.get("content"), content_type) or
                not isinstance(output.get("grounding"), list)):
            raise ExaError("INVALID_RESPONSE", "Exa returned no valid synthesized content and grounding.", **details)
    return {"mode": mode, "attempts": attempt,
            "requestId": payload.get("requestId"), "results": payload["results"],
            "output": output, "searchTime": payload.get("searchTime"),
            "costDollars": payload.get("costDollars"), "costNote": COST_NOTE}


def validate_output_schema(schema: dict) -> None:
    if schema["type"] == "text":
        return
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError:
        raise ExaError("INVALID_REQUEST", "outputSchema must be a valid JSON Schema.") from None

    # Count properties in nested objects and array items as the Deep guide specifies.
    def inspect(node, depth=0):
        if not isinstance(node, dict):
            return 0
        properties = node.get("properties", {})
        if depth > 2 and (node.get("type") == "object" or properties):
            raise ExaError("INVALID_REQUEST", "outputSchema supports at most two object levels below its root.")
        if node.get("type") == "array" and "items" not in node:
            raise ExaError("INVALID_REQUEST", "Every outputSchema array must define items.")
        count = len(properties)
        for child in properties.values():
            count += inspect(child, depth + 1)
        for name in ("items", "additionalProperties", "contains"):
            count += inspect(node.get(name), depth + 1)
        for name in ("not", "if", "then", "else"):
            count += inspect(node.get(name), depth)
        for name in ("allOf", "anyOf", "oneOf", "prefixItems"):
            count += sum(inspect(child, depth) for child in node.get(name, []))
        for name in ("$defs", "definitions", "patternProperties", "dependentSchemas"):
            count += sum(inspect(child, depth) for child in node.get(name, {}).values())
        return count

    if inspect(schema) > 10:
        raise ExaError("INVALID_REQUEST", "outputSchema supports at most ten properties across nested objects and array items.")


def prepare_request(query: str | None = None, *, request: dict | None = None,
                    mode: str | None = None, num_results: int | None = None,
                    synthesize: bool = False, include_domains: list[str] | None = None,
                    additional_queries: list[str] | None = None, betas: list[str] | None = None) -> dict:
    if Draft202012Validator is None or "date-time" not in FormatChecker.checkers:
        raise ExaError("MISSING_DEPENDENCY", "Run the source setup with --with-runtime to install JSON Schema/date validation, then use its recorded Python.")
    if request is not None and (query is not None or mode is not None or num_results is not None or
                                synthesize or include_domains is not None or additional_queries is not None):
        raise ExaError("INVALID_REQUEST", "Use a complete request file or query/options, without mixing API inputs.")
    body = copy.deepcopy(request) if request is not None else {"query": query}
    if not isinstance(body, dict):
        raise ExaError("INVALID_REQUEST", "The Search API request must be a JSON object.")
    try:
        json.dumps(body, allow_nan=False)
    except (TypeError, ValueError):
        raise ExaError("INVALID_REQUEST", "Request values must be finite JSON values.") from None
    if request is None:
        if mode is not None:
            body["type"] = mode
        if num_results is not None:
            body["numResults"] = num_results
        if synthesize:
            body["outputSchema"] = {"type": "text", "description": "Answer the query with grounded findings and state evidence gaps."}
        if include_domains:
            body["includeDomains"] = include_domains
        if additional_queries:
            body["additionalQueries"] = additional_queries
    body.setdefault("type", "deep")
    body.setdefault("numResults", 10)
    body.setdefault("contents", {"highlights": True})
    if not isinstance(betas, (list, type(None))) or any(beta not in BETAS for beta in betas or []):
        raise ExaError("INVALID_REQUEST", "Only the documented Dynamic Highlights beta is supported.")
    try:
        schema = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise ExaError("MISSING_RESOURCE", "Reinstall the complete skill; its bundled request schema is missing or invalid.") from None
    error = next(Draft202012Validator(schema, format_checker=FormatChecker(formats=["date", "date-time"])).iter_errors(body), None)
    if error:
        # Validator messages can include arbitrary request values. Report only the field path.
        path = ".".join(str(part) for part in error.absolute_path) or "request"
        raise ExaError("INVALID_REQUEST", "Invalid or unknown API option; check the request reference and its bounds.", field=path)
    contents = body.get("contents") or {}
    if body.get("compliance") is not None:
        raise ExaError("UNSUPPORTED_OPTION", "HIPAA Search supports instant/fast, not deep or deep-reasoning; no mode switch was made.")
    if contents.get("snapshotAsOf") is not None:
        raise ExaError("UNSUPPORTED_OPTION", "Snapshot Search does not support deep or deep-reasoning; no mode switch was made.")
    if body.get("category") in ("company", "people") and any(
            body.get(name) is not None for name in ("startPublishedDate", "endPublishedDate", "excludeDomains")):
        raise ExaError("INVALID_REQUEST", "company/people do not support publication dates or excludeDomains.")
    if body.get("startPublishedDate") and body.get("endPublishedDate"):
        start, end = (datetime.fromisoformat(body[name].upper().replace("Z", "+00:00"))
                      for name in ("startPublishedDate", "endPublishedDate"))
        if start > end:
            raise ExaError("INVALID_REQUEST", "startPublishedDate must not be later than endPublishedDate.")
    location = body.get("userLocation")
    country = location.get("country") if isinstance(location, dict) else location
    if country is not None and (len(country) != 2 or not country.isascii() or not country.isalpha()):
        raise ExaError("INVALID_REQUEST", "userLocation country must be a two-letter ISO country code.")
    highlights = contents.get("highlights")
    if isinstance(highlights, dict):
        beta_fields = any(highlights.get(name) is not None for name in ("dynamic", "verbosity"))
        if beta_fields and BETAS[0] not in (betas or []):
            raise ExaError("BETA_REQUIRED", "Dynamic Highlights and highlight verbosity require --beta " + BETAS[0] + ".")
        if (highlights.get("dynamic") is True or highlights.get("verbosity") is not None) and highlights.get("maxCharacters") is not None:
            raise ExaError("INVALID_REQUEST", "Dynamic Highlights/verbosity cannot be combined with maxCharacters.")
    if body.get("outputSchema"):
        validate_output_schema(body["outputSchema"])
    summary_schema = (contents.get("summary") or {}).get("schema")
    if summary_schema is not None:
        try:
            Draft202012Validator.check_schema(summary_schema)
        except SchemaError:
            raise ExaError("INVALID_REQUEST", "contents.summary.schema must be a valid JSON Schema.") from None
    return body


def read_request_file(path: Path) -> dict:
    def reject_constant(value):
        raise ValueError()

    def unique_object(pairs):
        obj = {}
        for name, value in pairs:
            if name in obj:
                raise ValueError()
            obj[name] = value
        return obj

    try:
        body = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant,
                          object_pairs_hook=unique_object)
    except (OSError, ValueError, UnicodeError):
        raise ExaError("INVALID_REQUEST_FILE", "Cannot read valid UTF-8 JSON with unique keys and finite values; no API call was made.") from None
    if not isinstance(body, dict):
        raise ExaError("INVALID_REQUEST_FILE", "The request file must contain a JSON object.")
    return body


def read_stream(response, attempt: int) -> dict:
    """Consume typed SSE events; final output is authoritative after stream resets."""
    payload, lines = {}, []

    def failure(code, message, **details):
        return ExaError(code, message, attempts=attempt, costNote=COST_NOTE,
                        **{name: payload[name] for name in ("requestId", "costDollars") if name in payload}, **details)

    def event(data):
        if data == "[DONE]":
            raise failure("INCOMPLETE_STREAM", "Stream ended without a done event; completion and cost are uncertain.")
        chunk = json.loads(data)
        if not isinstance(chunk, dict):
            raise ValueError()
        payload.update({name: chunk[name] for name in ("requestId", "costDollars") if name in chunk})
        kind = chunk.get("type")
        if kind == "error":
            raise failure("STREAM_ERROR", "Exa reported a streaming error; the request was not replayed.", apiError=chunk.get("error"))
        if kind == "results" and isinstance(chunk.get("results"), list):
            payload["results"] = chunk["results"]
        elif kind == "done" and "output" in chunk and type(chunk.get("searchTime")) in (int, float):
            payload.update({name: chunk[name] for name in ("output", "searchTime", "costDollars") if name in chunk})
            return True
        elif kind == "text-delta" and isinstance(chunk.get("delta"), str):
            pass
        elif kind == "grounding" and isinstance(chunk.get("grounding"), list):
            pass
        elif kind == "stream-reset" and chunk.get("streamReset") is True:
            pass
        else:
            raise ValueError()
        return False

    try:
        for raw in response:
            line = raw.decode("utf-8").rstrip("\r\n")
            if not line:
                if lines and event("\n".join(lines)):
                    return payload
                lines = []
            elif line.startswith("data:"):
                lines.append(line[5:].removeprefix(" "))
            elif not line.startswith((":", "event:", "id:", "retry:")):
                raise ValueError()
        if lines and event("\n".join(lines)):
            return payload
    except (ValueError, UnicodeError):
        raise failure("INVALID_RESPONSE", "Exa returned malformed streaming events; completion may have been billed.") from None
    except (OSError, http.client.HTTPException):
        raise failure("TRANSPORT_ERROR", "Stream transport failed; completion and cost are uncertain. The request was not replayed.") from None
    raise failure("INCOMPLETE_STREAM", "Stream ended without a done event; completion and cost are uncertain.")


def search(query: str | None = None, *, request: dict | None = None,
           mode: str | None = None, num_results: int | None = None,
           synthesize: bool = False, include_domains: list[str] | None = None,
           additional_queries: list[str] | None = None, retries: int = 2,
           betas: list[str] | None = None, timeout: int = 120, dry_run: bool = False) -> dict:
    if type(retries) is not int or not 0 <= retries <= 2 or type(timeout) is not int or not 1 <= timeout <= 300:
        raise ExaError("INVALID_REQUEST", "Provide 0–2 retries and a 1–300 second transport timeout.")
    body = prepare_request(query, request=request, mode=mode, num_results=num_results, synthesize=synthesize,
                           include_domains=include_domains, additional_queries=additional_queries, betas=betas)
    if dry_run:
        return {"endpoint": ENDPOINT, "request": body, "betas": betas or [],
                "retries": retries, "timeoutSeconds": timeout, "chargeable": False}
    key = load_api_key()
    headers = {"x-api-key": key, "Content-Type": "application/json", "Accept": "text/event-stream, application/json"}
    if betas:
        headers["Exa-Beta"] = ",".join(dict.fromkeys(betas))
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    for attempt in range(1, retries + 2):
        try:
            with opener.open(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "") if hasattr(response, "headers") else ""
                payload = read_stream(response, attempt) if content_type.startswith("text/event-stream") else json.load(response)
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
            raise ExaError("INVALID_RESPONSE", "Exa returned invalid JSON or streaming events; completion may have been billed.", attempts=attempt) from None
        except ExaError as exc:
            exc.details = redact(exc.details, key)
            raise exc from None
        return normalize_response(redact(payload, key), body["type"], attempt, body.get("outputSchema"))
    raise AssertionError("Attempt bound exhausted")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("setup", "update", "remove"):
        commands.add_parser(name, help=f"{name.capitalize()} the saved native-store credential; no API call.")
    research = commands.add_parser("search", help="Make a chargeable Exa Search API request.")
    research.add_argument("query", nargs="?")
    research.add_argument("--request-file", type=Path, help="Complete Search API JSON body using camelCase wire names.")
    research.add_argument("--mode", choices=MODES)
    research.add_argument("--num-results", type=int, choices=range(1, 101), metavar="1–100")
    research.add_argument("--synthesize", action="store_true", help="Request generated text and field-level grounding.")
    research.add_argument("--include-domain", action="append")
    research.add_argument("--additional-query", action="append")
    research.add_argument("--beta", choices=BETAS, action="append", help="Explicit opt-in for documented beta content fields.")
    research.add_argument("--dry-run", action="store_true", help="Validate and print the request offline; no credential read or API call.")
    research.add_argument("--timeout", type=int, choices=range(1, 301), default=120, metavar="1–300",
                          help="Per-socket transport timeout in seconds (default 120); no automatic replay after timeout.")
    research.add_argument("--retries", type=int, choices=range(3), default=2,
                          help="Retry selected HTTP failures at most 0–2 times (default 2); retries may add cost.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "search":
            body = None
            if args.request_file:
                body = read_request_file(args.request_file)
            result = search(args.query, mode=args.mode, num_results=args.num_results,
                            synthesize=args.synthesize, include_domains=args.include_domain,
                            additional_queries=args.additional_query, retries=args.retries, request=body,
                            betas=args.beta, timeout=args.timeout, dry_run=args.dry_run)
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
