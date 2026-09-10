---
name: gemini-code-review
description: Run a read-only Gemini CLI review of an exact local diff, commit, or pull-request head only when explicitly invoked as $gemini-code-review or /gemini-code-review.
---

# Gemini Code Review

This workflow is explicit-only. Generic code review, independent review, or
Gemini wording does not invoke it.

Review one immutable change set; Gemini reports findings and Codex verifies
them. Do not edit files, post comments, change issue status, merge, deploy, or
publish unless Javier separately authorizes that action.

## Preflight

1. Identify the exact repository, base SHA, head SHA, and files in scope.
2. Generate a read-only sanitized diff and file list. Exclude `.env*`,
   credentials, keys, tokens, customer exports, and unrelated generated files.
3. State which tests or CI evidence already exists. Do not claim Gemini ran
   checks unless it actually did so read-only.
4. Run `gemini --approval-mode plan --skip-trust --output-format json -p`.
   Never use Yolo, auto-edit, or a Gemini worktree.

## Prompt

Supply the exact base/head and sanitized diff. Require Gemini to review only
that scope, use no tools, files, network, or external contacts, and return only
actionable findings with severity `P1`, `P2`, or `P3`. Each finding must cite a
file and line/range from the supplied diff, explain the failure mode, and give a
minimal reproduction or missing test. Require `NO_FINDINGS` when no supported
finding exists; reject style nits without a concrete consequence.

Prompt boundary:

```text
You are an independent read-only code reviewer. Review only this exact sanitized diff. Do not edit files, use tools, contact services, or make unsupported findings. Return P1/P2/P3 findings with evidence, or NO_FINDINGS.
```

Afterwards verify every finding against the exact head and separate confirmed
defects from inferences. Authentication failure is a blocker: report the
error and stop without changing Gemini, account, or cloud configuration.
