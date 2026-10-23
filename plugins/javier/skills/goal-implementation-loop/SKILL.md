---
name: goal-implementation-loop
description: Run an explicitly requested Goal through scoped issue tracking, branch preparation, latest available Luna with max reasoning implementation, Astra general review, conditional final Daybreak Blue security review, verification, PR handoff, and cleanup.
---

# Goal Implementation Loop

Use this skill only for an explicitly requested Goal implementation workflow.
It takes a validated Goal through implementation, review, checks, and the
requested handoff. Goal authoring, issue kickoff, and branch skills keep their
own narrower responsibilities.

Invoking it explicitly authorizes the required `write-goal` validation and,
when the request is mutating, the smallest necessary Linear issue structure,
an in-scope implementation commit, and closing references for issues the Goal
fully delivers. Cleanup of disposable resources created for the Goal is part
of this workflow, subject to the ownership and authorization rules below. It
does not authorize unrelated external mutations, a merge, or a production
action unless that action and target were already authorized.

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

Use these role defaults unless Javier explicitly overrides them. The
model-routing and orchestration policies own availability and lifecycle;
do not choose weaker Goal-specific routes.

- Main orchestrator: latest available Sol / `xhigh`.
- One exclusive implementation writer: latest available Luna / `max`.
- Read-only Goal engineering council: `goal_engineering_advisor` with
  `gpt-6-astra` / `xhigh`. Include it in the validated Goal and use
  [the engineering protocol](references/engineering-advisor.md).
- Independent read-only general reviewer: `gpt-6-astra` / `high`.
- For a material cybersecurity surface or an explicit cybersecurity review:
  add a separate *final* read-only reviewer using latest available Sol / `xhigh`
  with verified Daybreak Blue access. Skip it only when cybersecurity review
  is not applicable.

Record the requested assignments separately from the observed runtime. A skill
cannot change the model of an already-running main session. If its model or a
required route is unavailable or cannot be established, explain the limitation
and request the appropriate session/model selection instead of claiming a
switch or silently substituting a model. Use the external-review path below
when a required native Daybreak security review is unavailable.

Keep one exclusive writer for each branch, worktree, database, deployment,
provider, and shared integration surface. Additional Luna writers using the same model and reasoning require
independent issues and non-overlapping files and external mutation targets.
The orchestrator directs the writer and reports its proposed approach and
progress to the engineering council. The council challenges drift, unproductive
repetition, and unnecessary complexity; it does not write code, direct competing
writers, or replace independent general or final cybersecurity review.

Give the writer its exact scope, governing sources, permitted mutations,
acceptance criteria, checks, dependencies, and stop conditions. Consult the
council before the first implementation assignment, at meaningful milestones,
before a material change of approach or retry after failure, and before closure.
Apply its concrete direction or document an evidence-backed reason to differ;
escalate only decisions that change the Goal, authority, or explicit limits.
Do not turn consultation into a per-tool approval or status-polling loop.

## Independent reviews and final cybersecurity handoff

Once implementation stabilizes, have the independent Astra High general reviewer
inspect the exact diff or head against the Goal, repository requirements,
correctness, contracts, operations, and unnecessary complexity. The reviewer
is read-only and distinct from the Luna writer. Consolidate actionable
findings, have the existing writer fix them, run affected checks, and reuse
the same reviewer to verify the changed head.

When the Goal changes a material cybersecurity surface (including authorization,
tenant isolation, sensitive data, secrets, credentials, payment state, webhooks,
or untrusted input), or Javier explicitly requests cybersecurity review, perform
a separate final security review with latest available Sol / `xhigh` and Daybreak Blue.
Focus on concrete exploitable security risks, trust boundaries, and missing
security verification. Conduct this last, after the general review is resolved,
against the exact final candidate. A model identifier alone does not establish
Daybreak mode; confirm it is enabled in the host.

If required native Daybreak review is unsupported, rejected, or cannot be
established, place the full ready-to-paste security review prompt **in the main
chat** using `{codex_home}/references/external-daybreak-review.md`. Javier
selects the new or existing Daybreak session; do not create one without
authorization, try model aliases, or replace it with a non-Daybreak reviewer.
The prompt must include the actual originating session/thread ID and request
return delivery of the verdict. Reuse Javier's designated reviewer session for
re-review. Distinguish designation from observed mode; an undelivered prompt
is not a completed review. Pending security evidence blocks security-dependent
handoff, but not independent authorized work.

If the security reviewer identifies actionable findings, return them to
the existing Luna writer, apply only in-scope fixes, rerun affected checks,
and have the same Astra reviewer recheck the affected general diff. Then
return the *final* head to the same Daybreak reviewer for the last pass.
Any later code change invalidates the final security verdict. Never create
a second writer to fix review findings. Stop when findings are resolved,
a material decision is needed, scope would be exceeded, or evidence is missing.

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

## Cleanup before completion

After the required work and handoff are complete, clean up temporary resources
created for this Goal before calling `update_goal` complete. Inspect their
ownership and current use; retain anything still needed for review, manual QA,
recovery, or an authorized delivery step.

- Stop unused development servers, background processes, containers, and
  isolated local environments created for the Goal. Remove disposable preview
  environments, temporary databases, and synthetic test data only within the
  existing authority for those exact targets.
- Close browser tabs opened for the Goal that no longer serve a purpose. Keep
  tabs Javier opened or is using and any result or handoff tab still needed.
- Archive unused Goal worktrees with the host's managed-worktree archive tool
  when available. Preserve commits, uncommitted changes, untracked files, and
  needed ignored files before removing a checkout; managed archives may omit
  ignored files. Use recoverable archival rather than forced deletion. Keep
  primary or shared checkouts and worktrees needed by pending work.
- Remove Goal-only scratch files and temporary credential files once unused.
  Preserve deliverables and required evidence outside resources being removed.

Leave shared, production, user-owned, or uncertain resources intact. Reuse
existing authorization for routine Goal-owned cleanup; ask only when removal
requires additional authority or Javier retained an explicit checkpoint.

Verify that each cleanup action succeeded. Include a short cleanup result in
the final outcome: what was removed, what was retained and why, and any failure
or pending action. A failed required cleanup remains unfinished work; do not
mark the Goal complete while it is unresolved. Retaining a resource for a
confirmed ongoing use is a completed cleanup decision.

## Authorization and outcomes

Before merge, deployment, destructive action, production change, permission
change, external data mutation, or another irreversible action, verify Javier
authorized that exact action and target. A prior authorization remains valid for
its stated scope and conditions. Ask only when a material precondition or
required evidence is missing, when a rollback/recovery condition was explicitly
required, or when Javier retained an action-time checkpoint. Do not invent a
generic rollback template or discard concrete authority because it did not
repeat one. Continue independent authorized work meanwhile.

Open a PR by default after implementation, applicable general and final
cybersecurity reviews, fixes, verification, and the closure audit unless Javier requested no PR, hold PR, or local-only
work. Follow repository PR rules.

Report one compact outcome with the Goal state, changed surface, closure set and
issue-to-commit evidence, branch/worktree, implementation owner, general-review and applicable final Daybreak security
verdicts, checks actually run, documentation status, PR URL or reason no PR was
opened, and cleanup result. Call `update_goal` complete only when the required
work, closure coverage, and resource cleanup are complete. Do not call an issue
closed until its closing commit has reached the default branch and that
integration result is verified. Never claim
unrun review, verification, deployment, or production observation as passed.

Unversioned "Luna" and "Sol" requests resolve to the newest available version
on the execution host under `{codex_home}/agent-model-routing.md`. Javier's explicit
version takes precedence.
