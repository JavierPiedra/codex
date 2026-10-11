#!/usr/bin/env python3
"""Calculate date bounds, decimal hours, and totals for Good Ancestor invoices."""

from __future__ import annotations

import argparse
import calendar
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


MONTH_ALIASES = {
    name.lower(): index
    for index, name in enumerate(calendar.month_name)
    if name
}
MONTH_ALIASES.update(
    {
        name.lower(): index
        for index, name in enumerate(calendar.month_abbr)
        if name
    }
)

CODEX_HOURS = Decimal("5.00")
RESEARCH_LEARN_HOURS = Decimal("10.00")


@dataclass(frozen=True)
class Entry:
    name: str
    raw: str
    hours: Decimal


def money_round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_month_year(value: str) -> tuple[int, int]:
    cleaned = value.strip()
    iso_match = re.fullmatch(r"(\d{4})-(\d{1,2})", cleaned)
    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        if 1 <= month <= 12:
            return year, month
        raise ValueError(f"Invalid month in {value!r}")

    parts = re.split(r"[\s,]+", cleaned)
    if len(parts) != 2:
        raise ValueError("Use a target month like 'January 2026' or '2026-01'.")

    first, second = parts[0].lower(), parts[1]
    if first in MONTH_ALIASES and second.isdigit():
        return int(second), MONTH_ALIASES[first]

    if second.lower() in MONTH_ALIASES and first.isdigit():
        return int(first), MONTH_ALIASES[second.lower()]

    raise ValueError("Use a target month like 'January 2026' or '2026-01'.")


def month_bounds(value: str) -> tuple[date, date]:
    year, month = parse_month_year(value)
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def parse_hours(value: str) -> Decimal:
    raw = value.strip()
    hhmm_match = re.fullmatch(r"(\d+):([0-5]\d)", raw)
    if hhmm_match:
        hours = Decimal(hhmm_match.group(1))
        minutes = Decimal(hhmm_match.group(2))
        return money_round(hours + (minutes / Decimal(60)))

    decimal_match = re.fullmatch(r"\d+(?:\.\d+)?", raw)
    if decimal_match:
        return money_round(Decimal(raw))

    raise ValueError(f"Invalid hour value {value!r}; use HH:MM or decimal hours.")


def parse_entry(value: str) -> Entry:
    if "=" not in value:
        raise ValueError(f"Invalid entry {value!r}; use Name=HH:MM or Name=decimal.")
    name, raw_hours = value.split("=", 1)
    name = name.strip()
    raw_hours = raw_hours.strip()
    if not name:
        raise ValueError(f"Invalid entry {value!r}; name is empty.")
    return Entry(name=name, raw=raw_hours, hours=parse_hours(raw_hours))


def format_decimal(value: Decimal) -> str:
    return f"{money_round(value):.2f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize timer hours and total Good Ancestor invoice hours."
    )
    parser.add_argument("target_month", help="Target month, e.g. 'January 2026' or '2026-01'.")
    parser.add_argument(
        "--timer",
        action="append",
        default=[],
        metavar="NAME=HOURS",
        help="Clockify timer entry. HOURS may be HH:MM or decimal. Repeat as needed.",
    )
    parser.add_argument(
        "--project",
        action="append",
        default=[],
        metavar="NAME=HOURS",
        help="WakaTime project entry. HOURS may be HH:MM or decimal. Repeat as needed.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    start, end = month_bounds(args.target_month)
    timers = [parse_entry(value) for value in args.timer]
    projects = [parse_entry(value) for value in args.project]
    total = money_round(
        sum(
            (entry.hours for entry in timers + projects),
            CODEX_HOURS + RESEARCH_LEARN_HOURS,
        )
    )

    if args.json:
        print(
            json.dumps(
                {
                    "starting": start.isoformat(),
                    "end": end.isoformat(),
                    "timer": [
                        {"name": entry.name, "raw": entry.raw, "hours": format_decimal(entry.hours)}
                        for entry in timers
                    ],
                    "projects": [
                        {"name": entry.name, "raw": entry.raw, "hours": format_decimal(entry.hours)}
                        for entry in projects
                    ],
                    "codex": format_decimal(CODEX_HOURS),
                    "research_learn": format_decimal(RESEARCH_LEARN_HOURS),
                    "total": format_decimal(total),
                },
                indent=2,
            )
        )
        return 0

    print(f"Starting: {start.isoformat()}")
    print(f"End: {end.isoformat()}")
    print(f"TOTAL {format_decimal(total)}")
    if timers:
        print()
        print("Timer")
        for entry in timers:
            print(f"{entry.name}: {format_decimal(entry.hours)}")
    print()
    print(f"Codex: {format_decimal(CODEX_HOURS)}")
    print(f"Research/Learn: {format_decimal(RESEARCH_LEARN_HOURS)}")
    if projects:
        print()
        for entry in projects:
            print(f"{entry.name} - {format_decimal(entry.hours)}")
            print("{Branch List}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
