---
name: prd-council-review
description: Run a requested, read-only multi-perspective council on a PRD and any linked execution spec, selecting only the roles needed for the decision and returning a loop-ready, detailed, or JSON review.
---

# PRD Council Review

Use this skill for an explicitly requested PRD council. Ordinary PRD review,
readiness checking, or implementation planning can remain a single-agent task;
those requests do not automatically require a council. Never edit files unless
Javier explicitly asks for edits.

## Inputs and evidence

Accept a PRD path, pasted content, optional linked execution spec, optional repo
root, focus area, and output mode (`loop` by default, `detail`, or `json`). Ask
one concise question when the PRD source cannot be inferred. Keep the review
repo-agnostic and enforce only explicit user requirements and rules found in
the applicable repository guidance.

When the PRD is in a repository, inspect the nearest `AGENTS.md` files and
relevant README, contribution, planning, execution, task, workflow, and
progress docs. Read the PRD and only documents it explicitly links or the repo
guidance makes necessary. If none exists, record `repo_guidance: none_found`
and continue.

Keep evidence separate from interpretation, recommendation, missing decisions,
and unknowns. Do not invent lifecycle rules, commands, contracts, or tests.

## Select and run the council

Choose the smallest set of roles whose perspectives can change the decision.
There is no fixed council size or mandatory role list. Possible lenses include
contract/engineering, security/data/risk, product/UX/operations,
QA/guidance/maintainability, accessibility, legal, finance, support, or
rollout. Explain relevance briefly in the internal evidence; omit ceremonial
roles. Use the model and reasoning required by the current routing policy, or
the user's explicit choice. Do not rely on an outdated model baseline.

An optional HR profile-planning subagent is available only when Javier
explicitly requests HR planning. Keep HR read-only. Ask it to propose profiles
before council spawn, each containing:

- role and bounded decision scope;
- evidence inputs it will receive;
- model identifier and reasoning grounded in the current routing policy;
- expected output; and
- why the profile is necessary.

The HR profile-planning subagent cannot recruit, delegate, or choose the final council. The parent selects the
roles and starts the council. Pause for profile approval only when Javier
explicitly requests that checkpoint; otherwise continue after inspecting the
profiles.

Spawn one independent read-only subagent per selected role. Give each the same
PRD/spec evidence packet, repo guidance, focus, and gate definitions, without
other roles' opinions. Ask for compact gate statuses, evidence-grounded
findings, missing decisions, tradeoffs, confidence, and suggested fix order.
Do not simulate a missing perspective in the main agent when the requested
council cannot run; report the concrete blocker.

Reuse the same role agents for a later answer round when answers or new evidence
arrive; do not replace them without a reason. Preserve genuine disagreement.

## Review gates

Evaluate each gate explicitly, using `not_applicable` only when it truly does
not apply and `blocked` only when required evidence or human input prevents a
safe review:

- `repo_guidance_gate`: required structure, linked docs, commands, topology, and
  stop conditions follow discovered guidance.
- `problem_gate`: problem, impact, goals, and non-goals are implementable
  without product reinterpretation.
- `contract_gate`: interfaces, persisted artifacts, migrations, and lifecycle
  states are explicit where applicable.
- `execution_gate`: when the requested review concerns implementation readiness
  or a required/provided execution spec, tasks are atomic, file-scoped,
  dependency-safe, and have exact verification and stop conditions. Otherwise
  use `not_applicable` for a compact product PRD that intentionally excludes
  file-level execution bookkeeping.
- `verification_gate`: success is objectively testable.
- `risk_gate`: relevant security, privacy, rollout, rollback, observability,
  support, and operational risks are addressed.
- `drift_gate`: relevant prompt/runtime decisions, adjacent-path audits,
  negative checks, or explicit deferrals are present.

Use severities `blocker`, `major`, `minor`, and `nit`. A blocker must be fixed
before implementation; a major finding can cause scope, behavior, or validation
failure; minor and nit findings do not block by themselves. Each finding names
the exact section and smallest useful fix.

Set `LOOP_STATUS` to `pass` only when no blockers exist and all required gates
pass; `fail` when the PRD/spec can be fixed without new human input; and
`blocked` when a human decision or unavailable required evidence is needed.
Use `NEXT_ACTION: proceed`, `fix_prd`, `create_execution_spec`, `ask_human`, or
`inspect_repo` accordingly. Do not mark pass while implementation would need
to guess product policy, contracts, tests, rollout, rollback, or stop
conditions.

## Output

Read only the reference for the requested output mode:

- [loop-output.md](./references/loop-output.md) for the default stable loop block;
- [detail-output.md](./references/detail-output.md) for loop plus concise notes;
- [json-output.md](./references/json-output.md) for machine-readable output.

Synthesize the result from all independent council reports and the evidence you
read. Limit loop findings to the five highest-impact actionable findings. Keep
patch suggestions optional and do not edit files unless Javier explicitly asks.
