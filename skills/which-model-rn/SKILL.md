---
name: which-model-rn
description: Show the configured model and reasoning effort for the most recent turn of the current Codex session, or of one explicitly supplied session ID. Use only when Javier explicitly invokes `$which-model-rn`; never invoke it implicitly while discussing models or logs.
---

# Which Model Now

Report only the last recorded `turn_context` for the requested Codex session.

## Input

- With no ID, use `CODEX_THREAD_ID` from the current session environment.
- With one UUID supplied after the invocation, use that session ID.
- Do not guess a session from recent files. If the current ID is unavailable or no transcript has a matching `session_meta`, report that exact blocker.

## Procedure

Run:

```bash
python3 /Users/javierpiedra/.codex/skills/which-model-rn/scripts/which_model.py --latest [--session <UUID>]
```

Return the script output unchanged. It identifies the configured model, reasoning effort, turn ID, logged time, and source transcript. Do not inspect message text or modify any file.
