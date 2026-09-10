#!/usr/bin/env python3
"""Read Codex transcript metadata without exposing transcript contents."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show configured model metadata from a Codex session transcript."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--latest", action="store_true", help="show the last turn")
    mode.add_argument("--history", action="store_true", help="show all distinct turns")
    parser.add_argument("--session", help="Codex thread/session UUID")
    return parser.parse_args()


def transcript_files(session_id: str, sessions_root: Path) -> list[Path]:
    matches: list[Path] = []
    for path in sessions_root.rglob(f"*{session_id}*.jsonl"):
        try:
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    payload = record.get("payload", {})
                    if (
                        record.get("type") == "session_meta"
                        and payload.get("session_id") == session_id
                    ):
                        matches.append(path)
                        break
        except OSError:
            continue
    return matches


def turn_contexts(paths: list[Path]) -> list[dict[str, str]]:
    contexts: list[dict[str, str]] = []
    for path in paths:
        try:
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if record.get("type") != "turn_context":
                        continue
                    payload = record.get("payload", {})
                    settings = payload.get("collaboration_mode", {}).get("settings", {})
                    model = payload.get("model") or settings.get("model")
                    effort = settings.get("reasoning_effort") or "unknown"
                    turn_id = payload.get("turn_id") or "unknown"
                    if not model:
                        continue
                    contexts.append(
                        {
                            "timestamp": record.get("timestamp", "unknown"),
                            "turn_id": turn_id,
                            "model": model,
                            "reasoning_effort": effort,
                            "source": str(path),
                        }
                    )
        except OSError:
            continue
    contexts.sort(key=lambda item: item["timestamp"])
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for context in contexts:
        key = (context["turn_id"], context["model"], context["reasoning_effort"])
        if key not in seen:
            seen.add(key)
            unique.append(context)
    return unique


def main() -> int:
    args = parse_args()
    session_id = args.session or os.environ.get("CODEX_THREAD_ID")
    if not session_id:
        print("BLOCKED: no session ID was supplied and CODEX_THREAD_ID is unavailable.")
        return 2

    codex_root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    paths = transcript_files(session_id, codex_root / "sessions")
    if not paths:
        print(f"BLOCKED: no local transcript has session_meta for {session_id}.")
        return 2

    contexts = turn_contexts(paths)
    if not contexts:
        print(f"BLOCKED: no turn_context with model metadata exists for {session_id} yet.")
        return 2

    if args.latest:
        context = contexts[-1]
        print(f"Session: {session_id}")
        print(f"Model: {context['model']}")
        print(f"Reasoning: {context['reasoning_effort']}")
        print(f"Turn: {context['turn_id']}")
        print(f"Logged: {context['timestamp']}")
        print(f"Source: {context['source']}")
        return 0

    print(f"Session: {session_id}")
    print("Model history:")
    for index, context in enumerate(contexts, start=1):
        print(
            f"{index}. {context['timestamp']} | {context['model']} | "
            f"{context['reasoning_effort']} | {context['turn_id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
