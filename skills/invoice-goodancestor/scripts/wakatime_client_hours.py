#!/usr/bin/env python3
"""Read client-filtered WakaTime project and branch hours."""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP


DEFAULT_CLIENT = "018ef80e-a87c-46fe-a05b-b800113925e0"
KEYCHAIN_SERVICE = "codex.invoice-goodancestor.wakatime"


def round_hours(seconds: Decimal) -> Decimal:
    return (seconds / Decimal("3600")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def keychain_account() -> str:
    return getpass.getuser()


def store_api_key() -> None:
    api_key = getpass.getpass("WakaTime API key: ").strip()
    if not api_key:
        raise ValueError("API key cannot be empty.")
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
            api_key,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    print(f"Stored WakaTime API key in Keychain service {KEYCHAIN_SERVICE!r}.")


def load_api_key() -> str:
    result = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-a",
            keychain_account(),
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    api_key = result.stdout.strip()
    if result.returncode != 0 or not api_key:
        raise RuntimeError(
            "WakaTime API key is missing. Run this script with --store-key first."
        )
    return api_key


def fetch_summary(
    start: str, end: str, client: str, api_key: str, project: str | None = None
) -> dict:
    params = {
        "start": start,
        "end": end,
        "cache": "true",
        "paywalled": "true",
        "clients": client,
    }
    if project:
        params["project"] = project
    query = urllib.parse.urlencode(params)
    url = f"https://wakatime.com/api/v1/users/current/summaries?{query}"
    authorization = base64.b64encode(api_key.encode("ascii")).decode("ascii")
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {authorization}",
            "Accept": "application/json",
            "User-Agent": "codex-invoice-goodancestor/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WakaTime API returned HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"WakaTime API request failed: {exc.reason}") from exc


def summary_days(payload: dict) -> list[dict]:
    days = payload.get("data")
    if not isinstance(days, list):
        raise ValueError("WakaTime response does not contain a data array.")
    return days


def aggregate_projects(payload: dict) -> list[dict]:
    project_seconds: defaultdict[str, Decimal] = defaultdict(Decimal)
    for day in summary_days(payload):
        for project in day.get("projects", []):
            project_name = project.get("name")
            if not project_name:
                continue
            project_seconds[project_name] += Decimal(str(project.get("total_seconds", 0)))

    projects = []
    for project_name, seconds in project_seconds.items():
        if seconds <= 0:
            continue
        projects.append(
            {
                "name": project_name,
                "hours": f"{round_hours(seconds):.2f}",
                "total_seconds": f"{seconds:f}",
                "branches": [],
            }
        )

    return sorted(
        projects,
        key=lambda project: (-Decimal(project["total_seconds"]), project["name"].lower()),
    )


def aggregate_branches(payload: dict) -> list[dict]:
    branch_seconds: defaultdict[str, Decimal] = defaultdict(Decimal)
    for day in summary_days(payload):
        for branch in day.get("branches", []):
            branch_name = branch.get("name") or "Unknown"
            branch_seconds[branch_name] += Decimal(str(branch.get("total_seconds", 0)))

    return [
        {
            "name": branch_name,
            "hours": f"{round_hours(seconds):.2f}",
            "total_seconds": f"{seconds:f}",
        }
        for branch_name, seconds in sorted(
            branch_seconds.items(), key=lambda item: (-item[1], item[0].lower())
        )
        if seconds > 0
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read Good Ancestor project and branch hours from WakaTime."
    )
    parser.add_argument("--start", help="Inclusive start date in YYYY-MM-DD format.")
    parser.add_argument("--end", help="Inclusive end date in YYYY-MM-DD format.")
    parser.add_argument("--client", default=DEFAULT_CLIENT, help="WakaTime client ID.")
    parser.add_argument(
        "--store-key",
        action="store_true",
        help="Prompt for and store the WakaTime API key in macOS Keychain.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.store_key:
        store_api_key()
        return 0
    if not args.start or not args.end:
        raise ValueError("--start and --end are required unless --store-key is used.")

    api_key = load_api_key()
    payload = fetch_summary(args.start, args.end, args.client, api_key)
    projects = aggregate_projects(payload)
    if not projects:
        raise RuntimeError("WakaTime returned no projects for this client and date range.")
    for project in projects:
        branch_payload = fetch_summary(
            args.start, args.end, args.client, api_key, project["name"]
        )
        project["branches"] = aggregate_branches(branch_payload)
    print(
        json.dumps(
            {
                "start": args.start,
                "end": args.end,
                "client": args.client,
                "projects": projects,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
