---
name: which-model-analysis
description: Show the complete chronological configured-model history for the current Codex session, or of one explicitly supplied session ID. Use only when Javier explicitly invokes `$javier:which-model-analysis`; never invoke it implicitly while discussing models or logs.
---

# Which Model Analysis

When running a bundled helper, resolve its path from this installed skill
directory and use the `python` path in `{codex_home}/javier-paths.toml`.
Quote executable and file paths for the active shell.

Report every distinct recorded `turn_context` for the requested Codex session, in chronological order.

## Input

- With no ID, use `CODEX_THREAD_ID` from the current session environment.
- With one UUID supplied after the invocation, use that session ID.
- Do not guess a session from recent files. If the current ID is unavailable or no transcript has a matching `session_meta`, report that exact blocker.

## Procedure

Run:

```text
<shared-python> <installed-skill>/../which-model-rn/scripts/which_model.py --history [--session <UUID>]
```

Return the script output unchanged. It reports configured model, reasoning effort, turn ID, and logged time without reading or exposing message text. Do not modify any file.
