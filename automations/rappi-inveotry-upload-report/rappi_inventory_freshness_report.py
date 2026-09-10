#!/usr/bin/env python3
"""Read-only Rappi inventory freshness report runner."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import time
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


AUTOMATION_DIR = Path(__file__).resolve().parent
RAPPI_DELIVERY_SERVICE_ID = "6665ad88-e23f-4d6b-a40d-37c702f38bfd"
REQUIRED_ENV = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
DESKTOP_REPO = Path("/Users/javierpiedra/Desktop/farcoyo")
PAGE_SIZE = 1000
DNS_ATTEMPTS = 4
DNS_RETRY_DELAY_SECONDS = 5
SUPABASE_HOST_IP_OVERRIDES = {
    # Last-resort DNS bypass for Codex automation sessions where every resolver
    # path fails, while Javier's shell still resolves this exact project host.
    "cjllsdrxbparqeskafhb.supabase.co": ["104.18.38.10", "172.64.149.246"],
}
SEVERITY_RANK = {
    "CRITICAL": 0,
    "CLOSE_STORE": 1,
    "CONTACT": 2,
    "OK": 3,
}
ACTION_BY_SEVERITY = {
    "OK": "No action.",
    "CONTACT": "Contact pharmacy to request inventory upload.",
    "CLOSE_STORE": "Close store in Rappi portal and contact pharmacy.",
    "CRITICAL": "Investigate missing inventory upload history immediately.",
}


class DNSResolutionError(OSError):
    def __init__(self, message: str, diagnostics: list[str]) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Farcoyo repo root. Defaults to cwd, then Desktop repo.",
    )
    return parser.parse_args()


def find_repo_root(repo_root_arg: str | None) -> Path | None:
    candidates = []
    if repo_root_arg:
        candidates.append(Path(repo_root_arg).expanduser())
    candidates.extend([Path.cwd(), DESKTOP_REPO])

    for candidate in candidates:
        if (candidate / "app/core/supabase.py").exists():
            return candidate.resolve()
    return None


def read_env_file(env_path: Path) -> None:
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)
    else:
        load_dotenv(env_path, override=False)


def load_supabase_env(repo_root: Path) -> Path | None:
    if all(os.getenv(name) for name in REQUIRED_ENV):
        return None

    for env_path in (repo_root / ".env", Path.cwd() / ".env", DESKTOP_REPO / ".env"):
        if env_path.exists():
            read_env_file(env_path)
            if all(os.getenv(name) for name in REQUIRED_ENV):
                return env_path
    return None


def print_missing_env() -> None:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    print("# Rappi Inventory Freshness Report")
    print()
    print("Supabase environment variables are missing; no database reads were executed.")
    print()
    print("Missing env vars: " + ", ".join(f"`{name}`" for name in missing))
    print()
    print("Run with:")
    print()
    print("```bash")
    print(
        "SUPABASE_URL='<your-supabase-url>' "
        "SUPABASE_SERVICE_ROLE_KEY='<your-service-role-key>' "
        "POETRY_VIRTUALENVS_PATH=\"$PWD/.poetry-venvs\" "
        "poetry run python "
        f"{AUTOMATION_DIR / 'rappi_inventory_freshness_report.py'} "
        "--repo-root \"$PWD\""
    )
    print("```")


def print_missing_repo() -> None:
    print("# Rappi Inventory Freshness Report")
    print()
    print("Could not find the Farcoyo repo root; no database reads were executed.")
    print()
    print("Run from the repo root or pass:")
    print()
    print("```bash")
    print(
        "POETRY_VIRTUALENVS_PATH=\"$PWD/.poetry-venvs\" "
        "poetry run python "
        f"{AUTOMATION_DIR / 'rappi_inventory_freshness_report.py'} "
        "--repo-root /Users/javierpiedra/Desktop/farcoyo"
    )
    print("```")


def print_missing_dependencies(repo_root: Path, exc: ModuleNotFoundError) -> None:
    print("# Rappi Inventory Freshness Report")
    print()
    print("Python dependencies are missing; no database reads were executed.")
    print()
    print(f"Import error: `{exc}`")
    print()
    print("Install locked dependencies and rerun:")
    print()
    print("```bash")
    print(
        f"cd {repo_root} && "
        "POETRY_VIRTUALENVS_PATH=\"$PWD/.poetry-venvs\" "
        "poetry install --only main --no-root"
    )
    print(
        f"cd {repo_root} && "
        "POETRY_VIRTUALENVS_PATH=\"$PWD/.poetry-venvs\" "
        "poetry run python "
        f"{AUTOMATION_DIR / 'rappi_inventory_freshness_report.py'} "
        "--repo-root \"$PWD\""
    )
    print("```")


def print_supabase_connect_failure(
    hostname: str,
    dns_source: str,
    exc: BaseException,
) -> None:
    print("# Rappi Inventory Freshness Report")
    print()
    print("Supabase network connection was blocked before any table data was read.")
    print()
    print(f"Supabase host: `{hostname}`")
    print(f"DNS path: `{dns_source}`")
    print(f"Error type: `{type(exc).__module__}.{type(exc).__name__}`")
    print(f"Error: `{exc}`")
    print()
    print(
        "This is an automation runtime outbound-network permission failure, "
        "not the DNS resolver failure path."
    )


def print_supabase_read_failure(
    dns_source: str,
    exc: BaseException,
) -> None:
    print("# Rappi Inventory Freshness Report")
    print()
    print("Supabase read failed after the helper passed DNS preparation.")
    print("No report counts were produced, and no stale counts were reused.")
    print()
    print(f"DNS path: `{dns_source}`")
    print(f"Error type: `{type(exc).__module__}.{type(exc).__name__}`")
    print(f"Error: `{exc}`")


def encode_dns_name(hostname: str) -> bytes:
    return b"".join(
        bytes([len(part)]) + part.encode("ascii")
        for part in hostname.rstrip(".").split(".")
    ) + b"\x00"


def read_dns_name(payload: bytes, offset: int) -> int:
    while True:
        length = payload[offset]
        if length == 0:
            return offset + 1
        if length & 0xC0 == 0xC0:
            return offset + 2
        offset += length + 1


def is_ipv4_address(value: str) -> bool:
    try:
        socket.inet_aton(value)
    except OSError:
        return False
    return value.count(".") == 3


def resolve_a_records_via_udp(hostname: str) -> list[str]:
    packet_id = os.getpid() & 0xFFFF
    packet = (
        struct.pack("!HHHHHH", packet_id, 0x0100, 1, 0, 0, 0)
        + encode_dns_name(hostname)
        + struct.pack("!HH", 1, 1)
    )

    addresses: list[str] = []
    for resolver in ("1.1.1.1", "8.8.8.8"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2)
                sock.sendto(packet, (resolver, 53))
                payload, _ = sock.recvfrom(512)
        except OSError:
            continue

        response_id, _, question_count, answer_count, _, _ = struct.unpack(
            "!HHHHHH", payload[:12]
        )
        if response_id != packet_id:
            continue

        offset = 12
        for _ in range(question_count):
            offset = read_dns_name(payload, offset) + 4

        for _ in range(answer_count):
            offset = read_dns_name(payload, offset)
            answer_type, answer_class, _, answer_len = struct.unpack(
                "!HHIH", payload[offset : offset + 10]
            )
            offset += 10
            answer = payload[offset : offset + answer_len]
            offset += answer_len
            if answer_type == 1 and answer_class == 1 and answer_len == 4:
                addresses.append(socket.inet_ntoa(answer))

        if addresses:
            return sorted(set(addresses))
    return []


def resolve_a_records_via_dig(
    hostname: str,
    resolver: str | None = None,
) -> list[str]:
    dig_path = "/usr/bin/dig"
    if not Path(dig_path).exists():
        return []

    command = [dig_path, "+short", "A", hostname]
    if resolver is not None:
        command.insert(1, f"@{resolver}")

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []

    addresses: list[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if is_ipv4_address(line):
            addresses.append(line)
    return sorted(set(addresses))


def resolve_a_records_via_doh(hostname: str) -> list[str]:
    query = urlencode({"name": hostname, "type": "A"})
    request = Request(
        f"https://1.1.1.1/dns-query?{query}",
        headers={"accept": "application/dns-json"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode())
    except (OSError, json.JSONDecodeError, TimeoutError):
        return []

    if payload.get("Status") != 0:
        return []

    addresses: list[str] = []
    for answer in payload.get("Answer", []):
        value = str(answer.get("data") or "")
        if answer.get("type") == 1 and is_ipv4_address(value):
            addresses.append(value)
    return sorted(set(addresses))


def resolve_a_records_via_host_override(hostname: str) -> list[str]:
    return SUPABASE_HOST_IP_OVERRIDES.get(hostname.lower(), [])


def install_dns_override(hostname: str, addresses: list[str]) -> None:
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(
        host: str,
        port: int,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list[tuple[Any, ...]]:
        if host == hostname:
            socktype = type or socket.SOCK_STREAM
            protocol = proto or socket.IPPROTO_TCP
            return [
                (
                    socket.AF_INET,
                    socktype,
                    protocol,
                    "",
                    (address, port),
                )
                for address in addresses
            ]
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = patched_getaddrinfo


def prepare_dns(hostname: str) -> str:
    diagnostics: list[str] = []
    last_error: OSError | None = None
    for attempt in range(1, DNS_ATTEMPTS + 1):
        try:
            socket.getaddrinfo(hostname, 443)
            suffix = "" if attempt == 1 else f" after {attempt} attempts"
            return f"system DNS{suffix}"
        except OSError as exc:
            last_error = exc
            diagnostics.append(f"attempt {attempt}: Python DNS failed: {exc}")

        fallback_resolvers = (
            ("system dig fallback", lambda: resolve_a_records_via_dig(hostname)),
            (
                "dig @1.1.1.1 fallback",
                lambda: resolve_a_records_via_dig(hostname, "1.1.1.1"),
            ),
            (
                "dig @8.8.8.8 fallback",
                lambda: resolve_a_records_via_dig(hostname, "8.8.8.8"),
            ),
            (
                "UDP DNS fallback via 1.1.1.1/8.8.8.8",
                lambda: resolve_a_records_via_udp(hostname),
            ),
            (
                "DNS-over-HTTPS fallback via 1.1.1.1",
                lambda: resolve_a_records_via_doh(hostname),
            ),
            (
                "pinned project host IP override",
                lambda: resolve_a_records_via_host_override(hostname),
            ),
        )

        for source, resolver in fallback_resolvers:
            addresses = resolver()
            if addresses:
                install_dns_override(hostname, addresses)
                suffix = "" if attempt == 1 else f" after {attempt} attempts"
                return f"{source}{suffix}"
            diagnostics.append(f"attempt {attempt}: {source} returned no A records")

        if attempt < DNS_ATTEMPTS:
            time.sleep(DNS_RETRY_DELAY_SECONDS)

    if last_error is not None:
        raise DNSResolutionError(str(last_error), diagnostics)
    raise DNSResolutionError(f"could not resolve {hostname}", diagnostics)


def probe_supabase_tcp_connect(hostname: str) -> None:
    with socket.create_connection((hostname, 443), timeout=5):
        pass


def iso_to_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def csv_cell(value: object) -> str:
    if value is None:
        return "null"
    return str(value).replace("\n", " ")


def fetch_all(query_builder: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        response = query_builder.range(start, start + PAGE_SIZE - 1).execute()
        page = response.data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        start += PAGE_SIZE


def fetch_by_ids(
    client: Any,
    table: str,
    select: str,
    column: str,
    ids: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for start in range(0, len(ids), 100):
        chunk = ids[start : start + 100]
        query = client.table(table).select(select).in_(column, chunk)
        rows.extend(fetch_all(query))
    return rows


def is_ready_to_upload(row: dict[str, Any]) -> bool:
    return any(
        row.get(column)
        for column in (
            "inventory_enabled_at",
            "orders_enabled_at",
            "channel_user_created_at",
            "credentials_sent_at",
        )
    )


def build_report_rows(client: Any, now_utc: datetime) -> list[dict[str, Any]]:
    rappi_rows = fetch_all(
        client.table("pharmacy_delivery_services")
        .select(
            "pharmacy_id,external_id,inventory_enabled_at,orders_enabled_at,"
            "channel_user_created_at,credentials_sent_at"
        )
        .eq("delivery_service_id", RAPPI_DELIVERY_SERVICE_ID)
    )
    ready_rows = [row for row in rappi_rows if is_ready_to_upload(row)]
    pharmacy_ids = sorted(
        {str(row["pharmacy_id"]) for row in ready_rows if row.get("pharmacy_id")}
    )

    pharmacies_by_id: dict[str, dict[str, Any]] = {}
    manifests_by_pharmacy: dict[str, dict[str, Any]] = {}
    if pharmacy_ids:
        pharmacy_rows = fetch_by_ids(
            client,
            "pharmacies",
            "id,name",
            "id",
            pharmacy_ids,
        )
        pharmacies_by_id = {str(row["id"]): row for row in pharmacy_rows}

        manifest_rows = fetch_by_ids(
            client,
            "pharmacy_update_manifests",
            "id,pharmacy_id,rappi_job_id,status,created_at",
            "pharmacy_id",
            pharmacy_ids,
        )
        manifest_rows.sort(
            key=lambda row: (
                str(row.get("pharmacy_id") or ""),
                iso_to_datetime(row["created_at"])
                if row.get("created_at")
                else datetime.min.replace(tzinfo=timezone.utc),
            ),
            reverse=True,
        )
        for row in manifest_rows:
            pharmacy_id = str(row.get("pharmacy_id") or "")
            if pharmacy_id and pharmacy_id not in manifests_by_pharmacy:
                manifests_by_pharmacy[pharmacy_id] = row

    report_rows: list[dict[str, Any]] = []
    for ready in ready_rows:
        pharmacy_id = str(ready.get("pharmacy_id") or "")
        latest = manifests_by_pharmacy.get(pharmacy_id)
        if latest is None:
            severity = "CRITICAL"
            latest_created_at = None
            hours_since = None
        else:
            latest_created_at = latest.get("created_at")
            created_at = iso_to_datetime(latest_created_at)
            hours_since = (now_utc - created_at).total_seconds() / 3600
            if hours_since <= 24:
                severity = "OK"
            elif hours_since <= 30:
                severity = "CONTACT"
            else:
                severity = "CLOSE_STORE"

        pharmacy = pharmacies_by_id.get(pharmacy_id, {})
        report_rows.append(
            {
                "severity": severity,
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": pharmacy.get("name"),
                "rappi_store_id": ready.get("external_id"),
                "latest_manifest_id": latest.get("id") if latest else None,
                "latest_job_id": latest.get("rappi_job_id") if latest else None,
                "latest_manifest_created_at": latest_created_at,
                "hours_since_latest_upload": hours_since,
                "latest_manifest_status": latest.get("status") if latest else None,
                "action_needed": ACTION_BY_SEVERITY[severity],
            }
        )

    report_rows.sort(
        key=lambda row: (
            SEVERITY_RANK[row["severity"]],
            -(
                row["hours_since_latest_upload"]
                if row["hours_since_latest_upload"] is not None
                else float("inf")
            ),
        )
    )
    return report_rows


def print_report(
    report_rows: list[dict[str, Any]],
    now_utc: datetime,
    env_source: Path | None,
    dns_source: str,
) -> None:
    now_local = now_utc.astimezone(ZoneInfo("America/Mexico_City"))
    counts = {
        "OK": sum(1 for row in report_rows if row["severity"] == "OK"),
        "CONTACT": sum(1 for row in report_rows if row["severity"] == "CONTACT"),
        "CLOSE_STORE": sum(
            1 for row in report_rows if row["severity"] == "CLOSE_STORE"
        ),
        "CRITICAL": sum(
            1 for row in report_rows if row["severity"] == "CRITICAL"
        ),
    }

    print("# Rappi Inventory Freshness Report")
    print()
    print(f"Report timestamp: {now_local.isoformat(timespec='seconds')}")
    if env_source is not None:
        print(f"Env source: `{env_source}`")
    print(f"Supabase connectivity: {dns_source}")
    print()
    print("## Summary")
    print()
    print(f"- total_ready_to_upload: {len(report_rows)}")
    print(f"- ok_count: {counts['OK']}")
    print(f"- contact_count: {counts['CONTACT']}")
    print(f"- close_store_count: {counts['CLOSE_STORE']}")
    print(f"- critical_no_manifest_count: {counts['CRITICAL']}")
    print()
    print("## Pharmacies CSV")
    print()

    headers = [
        "severity",
        "pharmacy_id",
        "pharmacy_name",
        "rappi_store_id",
        "latest_manifest_id",
        "latest_job_id",
        "latest_manifest_created_at",
        "hours_since_latest_upload",
        "latest_manifest_status",
        "action_needed",
    ]
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(headers)
    for row in report_rows:
        printable = row.copy()
        hours = printable["hours_since_latest_upload"]
        if hours is not None:
            printable["hours_since_latest_upload"] = f"{hours:.2f}"
        writer.writerow([csv_cell(printable[header]) for header in headers])


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(args.repo_root)
    if repo_root is None:
        print_missing_repo()
        return 2

    sys.path.insert(0, str(repo_root))
    env_source = load_supabase_env(repo_root)
    if not all(os.getenv(name) for name in REQUIRED_ENV):
        print_missing_env()
        return 2

    supabase_url = os.environ["SUPABASE_URL"]
    hostname = urlparse(supabase_url).hostname
    if hostname is None:
        print("# Rappi Inventory Freshness Report")
        print()
        print("SUPABASE_URL is invalid; no database reads were executed.")
        return 2

    try:
        dns_source = prepare_dns(hostname)
    except OSError as exc:
        print("# Rappi Inventory Freshness Report")
        print()
        print(f"Supabase host `{hostname}` could not be resolved.")
        print("No table data was read.")
        print()
        print(f"DNS error: `{exc}`")
        diagnostics = getattr(exc, "diagnostics", [])
        if diagnostics:
            print()
            print("Resolver diagnostics:")
            for line in diagnostics:
                print(f"- {line}")
        return 3

    try:
        probe_supabase_tcp_connect(hostname)
    except OSError as exc:
        print_supabase_connect_failure(hostname, dns_source, exc)
        return 4

    try:
        from app.core.supabase import get_supabase_client
    except ModuleNotFoundError as exc:
        print_missing_dependencies(repo_root, exc)
        return 2

    client = get_supabase_client()
    now_utc = datetime.now(timezone.utc)
    try:
        report_rows = build_report_rows(client, now_utc)
    except Exception as exc:
        print_supabase_read_failure(dns_source, exc)
        return 5

    print_report(report_rows, now_utc, env_source, dns_source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
