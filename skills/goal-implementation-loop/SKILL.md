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

## Ownership and review

Keep one exclusive writer for each branch, worktree, database, deployment,
provider, and shared integration surface. Choose coordination topology and
model from the current routing and orchestration policies; this skill does not
hardcode a coordinator model.

- One `gpt-5.6-luna` / `max` implementer owns implementation writes by default.
- Additional Luna Max implementers require independent issues and non-overlapping
  files and external mutation targets.
- One read-only `gpt-daybreak-blue-latest` reviewer uses medium reasoning by
  default, or high reasoning for materially risky changes.

Give each implementer its exact scope, governing sources, permitted mutations,
acceptance criteria, checks, dependencies, and stop conditions. After the
implementation is stable, have Daybreak review the exact diff or head against
the Goal, repository rules, and relevant correctness, security, operations,
complexity, and contract risks. Send consolidated actionable findings to the
same implementer; apply in-scope fixes and rerun affected checks; have the same
reviewer recheck. Do not create a second writer to fix review findings.

Stop the fix loop when findings are resolved, require a material product
decision, exceed scope, lack required evidence, or cannot be verified.

## Optional adversarial engineering consultant

Enable this optional subagent when Javier requests it or the validated Goal
explicitly includes it. Otherwise run the existing loop without a consultant.
Use one read-only expert engineering consultant, selected through the current
routing and orchestration policies, and reuse it throughout the Goal. It advises
the orchestrator; it does not own implementation, replace Daybreak's independent
review, authorize mutations, or change the Goal contract.

Give it the validated Goal, acceptance criteria, exclusions, governing contract
sources, current plan, evidence, and any explicit time or resource limits. Its
mandate is to challenge the orchestrator's assumptions and proposed decisions,
not merely endorse progress reports. It must:

- Detect contract drift by comparing decisions, implementation evidence, and
  claimed progress against the Goal and governing contracts. Challenge weakened
  acceptance criteria, scope expansion, incompatible interfaces, and unsupported
  claims of completion.
- Assess engineering correctness, architecture, integration risks, and whether
  the proposed next step is the simplest durable way to satisfy the Goal.
- Critically assess elapsed time and resource use against demonstrated progress:
  repeated failed approaches, duplicate exploration or checks, unnecessary agent
  fan-out, excessive coordination, and work that does not advance acceptance.
  Use available time, token, tool, and cost evidence; identify unknowns rather
  than inventing measurements or budgets.
- Return concise, evidence-backed objections: the affected contract or objective,
  the consequence, and a concrete correction or cheaper sufficient next step.
  Recommend stopping an unproductive approach when further spending has no
  supported path to progress. Do not reduce required acceptance or verification
  merely to save resources, and do not manufacture objections.

The orchestrator reports to the same consultant at the initial execution plan,
meaningful milestones, before a material approach change or retry after failure,
and before claiming completion. Each report states acceptance progress and its
evidence, changes since the last report, blockers, available resource usage,
and the proposed next step with its expected result. Keep reports incremental;
do not send every tool result or create a second tracking system.

Resolve objections affecting the next dependent action before proceeding with
that action; continue independent authorized work meanwhile. The orchestrator
records the correction or an evidence-backed reason for rejecting the advice.
Escalate to Javier when resolution requires changing the contract, authority,
or an explicit resource limit. Advice is not an approval gate or permission to
stop a Goal contrary to its outcome rules. Include the consultant's material
findings and their disposition in the compact final outcome when enabled.

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
