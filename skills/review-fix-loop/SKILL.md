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

- Use one read-only reviewer selected by `agent-model-routing.md`, with medium
  reasoning by default and high reasoning when complexity or material risk
  warrants it.
- Keep one separate exclusive implementation writer. The reviewer never edits.
- Send findings to the existing writer, and reuse the same reviewer after fixes.
- If the required reviewer is unavailable, report the workflow as blocked
  rather than substituting an undeclared model.

## Review And Fix

Review the exact diff against the active goal and applicable correctness,
complexity, security, operations, and contract risks. Return only findings tied
to concrete evidence, preferably with file and line references.

For each pass:

1. Consolidate actionable findings by root cause.
2. Have the implementation writer apply the smallest in-scope fixes.
3. Rerun checks affected by those fixes.
4. Have the same reviewer inspect the updated exact diff or head.

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
