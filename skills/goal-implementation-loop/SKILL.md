---
name: goal-implementation-loop
description: Run an explicitly requested Goal implementation through scoped issue tracking, branch preparation, Luna Max implementation, Daybreak review, verification, and pull-request handoff.
---

# Goal Implementation Loop

Use this skill only for an explicitly requested Goal implementation workflow.
It takes a validated Goal through implementation, review, checks, and the
requested handoff. Goal authoring, issue kickoff, and branch skills keep their
own narrower responsibilities.

Invoking it explicitly authorizes the required `write-goal` validation and,
when the request is mutating, the smallest necessary Linear issue structure,
an in-scope implementation commit, and closing references for issues the Goal
fully delivers. It does not authorize unrelated external mutations, a merge,
or a production action unless that action and target were already authorized.

## Goal and readiness

Apply `write-goal` first. It authors and validates the contract; this skill
activates and executes it. If Javier asks to see or authorize the Goal first,
return the validated contract and stop before activation, Linear, Git,
delegation, or implementation. Otherwise continue a matching active Goal or
create one with `create_goal`; do not replace a different unfinished Goal.

A clear bounded request receives the shortest valid Goal contract and does not
need renewed approval unless Javier requested that checkpoint. Ask only for a
missing decision that materially changes target, scope, authority, or safe
execution. Respect plan-only, review-only, read-only, no-PR, hold-PR, and
local-only boundaries.

Read the applicable `AGENTS.md` and only the repository rules needed for the
request. Confirm the target repository, allowed mutation scope, comparison base
and PR target when relevant, required checks and environment, existing issue,
branch and worktree context, and unresolved dependencies.

## Issue, branch, and worktree

Every mutating implementation needs a matching existing Linear issue or the
smallest useful issue structure before code changes. Reuse a matching issue;
use `prd-kickoff` for an approved PRD and `linear-issue-kickoff` otherwise.
Do not create issues for plan-only, review-only, or read-only work.

Use an existing branch/worktree only when the Goal or active context identifies
it and it matches the target. Otherwise use `create-branch`, which owns base
resolution, naming, temporary-worktree creation, dirty-tree safety, and
reporting. Do not create a second branch when kickoff already prepared the
correct one.

Before the first implementation commit, record the Goal's Linear closure set:
each standalone or leaf issue whose full acceptance criteria the Goal delivers.
Include an umbrella only when the Goal also completes it. Do not use a broad,
out-of-scope, planning, or review issue merely to obtain a closing reference.

## Roles and ownership

This workflow uses the following defaults unless Javier explicitly overrides
an assignment. These Goal-specific defaults supersede older generic routing
model defaults; retain the applicable lifecycle and authorization policies.

- The main session is the orchestrator: `gpt-6-sol` / `medium` by default.
- One `gpt-6-luna` / `max` writer owns implementation and in-scope fixes.
- One read-only engineering council uses `goal_engineering_advisor` with
  `gpt-6-astra` / `high`. Include it in the validated Goal and consult it using
  [the engineering protocol](references/engineering-advisor.md).
- One independent read-only Daybreak reviewer handles the stable implementation.
  Use the host-supported Daybreak route (including Daybreak Blue where exposed)
  and current reviewer routing, with
  medium reasoning by default or high for materially risky changes.

Record the requested assignments separately from the observed runtime. A skill
cannot change the model of an already-running main session. If its model or a
required route is unavailable or cannot be established, explain the limitation
and request the appropriate session/model selection instead of claiming a
switch or silently substituting a model. Use the external-review path below
when native Daybreak is unavailable.

Keep one exclusive writer for each branch, worktree, database, deployment,
provider, and shared integration surface. Additional Luna Max writers require
independent issues and non-overlapping files and external mutation targets.
The orchestrator directs the writer and reports its proposed approach and
progress to the engineering council. The council challenges drift, unproductive
repetition, and unnecessary complexity; it does not write code, direct competing
writers, or replace independent Daybreak review.

Give the writer its exact scope, governing sources, permitted mutations,
acceptance criteria, checks, dependencies, and stop conditions. Consult the
council before the first implementation assignment, at meaningful milestones,
before a material change of approach or retry after failure, and before closure.
Apply its concrete direction or document an evidence-backed reason to differ;
escalate only decisions that change the Goal, authority, or explicit limits.
Do not turn consultation into a per-tool approval or status-polling loop.

## Daybreak review and manual handoff

After implementation stabilizes, review the exact diff or head against the Goal,
repository rules, and relevant correctness, security, operations, complexity,
and contract risks. Confirm native Daybreak availability from the host before
spawning. A model name alone does not establish Daybreak mode.

If native spawning is unsupported, rejected, or Daybreak mode cannot be
established, produce a ready-to-paste reviewer prompt **inside the main chat**
using [the external-review handoff](references/external-daybreak-review.md).
Javier can paste it into a new or existing Daybreak session. Do not repeatedly
try alternate model identifiers, create a substitute reviewer, or require a
native subagent when the external review can satisfy the same review contract.

The prompt must identify the originating session by its actual thread ID and
require the reviewer to send the verdict back to that session. Record the
external reviewer session once known and reuse it for re-review. Distinguish
Javier's designation of the Daybreak session from independently observed runtime
metadata; missing native spawn capability is not a failure of an otherwise
valid review performed in the designated session. Missing review evidence still
blocks review-dependent handoff or completion. Continue independent authorized
work while waiting; a generated prompt is not a completed review.

Send consolidated actionable findings to the same writer, apply in-scope fixes,
rerun affected checks, and have the same reviewer recheck the resulting head.
The external path follows this same loop. Do not create a second writer to fix
review findings. Stop the fix loop when findings are resolved, require a material
product decision, exceed scope, lack required evidence, or cannot be verified.

## Commit closure

Every mutating run must finish with at least one in-scope implementation commit.
Across the complete comparison range, every issue in the closure set must occur
in a commit message with the repository-approved closing word. If no narrower
convention exists, use one footer per issue:

- `Fixes ISSUE-ID` for a fully resolved bug;
- `Completes ISSUE-ID` for fully delivered non-bug scope.

`Part of`, `Related to`, a bare issue ID, a branch name, or a PR-only reference
does not close an issue. Never close an issue whose acceptance criteria remain
unmet. A documentation or housekeeping commit may close only the exact process
scope it implements.

Before handoff or Goal completion, inspect the full range and produce:
`ISSUE-ID -> commit SHA -> exact closing line`. Confirm at least one
implementation commit. If a squash or other merge strategy could discard the
closing lines, verify the message that will reach the default branch. Check
push state before any rewrite and never rewrite published history without
Javier's explicit approval. Do not create an empty closure-only commit unless
explicitly authorized.

## Verification and documentation

Run objective checks appropriate to the changed surface and repository rules:
focused tests plus relevant lint, formatting, typecheck, build, codegen,
schema, migration, browser, API, or manual checks. State exact commands and
results; distinguish pre-existing failures and unrun checks.

Update canonical documentation only when the change affects durable behavior,
public contracts, architecture, setup, operations, or recorded decisions and
the existing source would otherwise become inaccurate. If no authorized source
is evident, ask instead of inventing one.

## Authorization and outcomes

Before merge, deployment, destructive action, production change, permission
change, external data mutation, or another irreversible action, verify Javier
authorized that exact action and target. A prior authorization remains valid for
its stated scope and conditions. Ask only when a material precondition or
required evidence is missing, when a rollback/recovery condition was explicitly
required, or when Javier retained an action-time checkpoint. Do not invent a
generic rollback template or discard concrete authority because it did not
repeat one. Continue independent authorized work meanwhile.

Open a PR by default after implementation, Daybreak review, fixes, verification,
and the closure audit unless Javier requested no PR, hold PR, or local-only
work. Follow repository PR rules.

Report one compact outcome with the Goal state, changed surface, closure set and
issue-to-commit evidence, branch/worktree, implementation owner, Daybreak
result, checks actually run, documentation status, and PR URL or reason no PR
was opened. Call `update_goal` complete only when the required work and closure
coverage are complete. Do not call an issue closed until its closing commit has
reached the default branch and that integration result is verified. Never claim
unrun review, verification, deployment, or production observation as passed.
