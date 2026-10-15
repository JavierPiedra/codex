---
name: review-fix-loop
description: Review, fix, and objectively verify an implemented branch or pull request when Javier explicitly requests this standalone workflow. It does not create Linear kickoff work, persistent manual-QA tracking, or merge and deployment actions.
---

# Review Fix Loop

## Purpose And Mode

Use this skill only on demand after implementation exists.

Default mode is review, fix, and verify. If Javier says review-only or no edits,
return findings without changing files or commits.

## Readiness

Identify the active goal, comparison base, changed surface, allowed mutation
scope, and applicable repository rules. Ask one focused question only when a
missing value materially changes the review or permitted fixes.

Stop when product intent is unclear, required evidence or credentials are
missing, a fix would exceed scope, or an irreversible action would be required.

## Ownership And Routing

Use `agent-model-routing.md` and `agent-orchestration.md`.

- Use one independent read-only `gpt-6-astra` / `high` general reviewer,
  as defined by `agent-model-routing.md`.
- Keep one separate exclusive implementation writer. The reviewer never edits.
- Send findings to the existing writer, and reuse the same reviewer after fixes.
- For material cybersecurity changes or an explicit security-review request,
  use a *separate* final `gpt-6-sol` / `xhigh` reviewer with Daybreak Blue.
- If a required reviewer is unavailable, report the dependent review as blocked
  rather than silently substituting a different model or mode.

## Review And Fix

Review the exact diff against the active goal and applicable correctness,
complexity, security, operations, and contract risks. Return only findings tied
to concrete evidence, preferably with file and line references.

For each pass:

1. Consolidate actionable findings by root cause.
2. Have the implementation writer apply the smallest in-scope fixes.
3. Rerun checks affected by those fixes.
4. Have the same reviewer inspect the updated exact diff or head.

For security-relevant work, perform the Daybreak Blue security review last
on the final head. After security-driven fixes, repeat affected general review
before returning to the same security reviewer for the final verdict. Do not
claim a security pass for a head that changed after it was reviewed. If native
Daybreak is unavailable, use the external security-review handoff in
`{codex_home}/references/external-daybreak-review.md` without creating a
new session on Javier's behalf.

Stop when no actionable findings remain, a decision is required, or further
work would expand scope. Do not add optional cleanup after the goal is met.

## Verification

Success requires objective evidence appropriate to the changed surface, such as
focused tests, repository-required lint or formatting, typecheck/build/codegen,
schema or migration checks, or direct browser/API verification.

If a material behavior cannot be verified, report it as not verified and name
the missing environment or evidence.

## Boundaries And Result

Do not create Linear kickoff work or persistent manual-QA tracking. Do not
merge, deploy, alter production data, or change permissions.

Return the review result, fixes, checks actually run, commits if created, and
unresolved blockers. Never report unrun checks as passed.
