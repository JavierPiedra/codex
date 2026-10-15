# Agent Model Routing

Use this policy for delegated agents, managed Codex continuations, and explicit
model-orchestration requests. It does not define any implementation workflow.

Javier's explicit model or reasoning instruction overrides these defaults.
Lifecycle and handoff rules live in
`{codex_home}/agent-orchestration.md`.

## Routing Table

| Assignment | Route | Topology |
| --- | --- | --- |
| Senior orchestration, including Goal orchestration | `gpt-6.1-sol` / `xhigh` | Root or authorized delegated orchestrator |
| Fully defined implementation writer | `gpt-6-luna` / `max` | Native `spawn_agent` subagent |
| Independent general code, contract, and correctness review | `gpt-6-astra` / `high` | Independent read-only reviewer |
| Goal engineering advisor/council | `gpt-6-astra` / `xhigh` | Read-only `goal_engineering_advisor` |
| Other read-only council specialists | `gpt-6-astra` / `xhigh` | Bounded, independent specialist lanes |
| Final review of materially cybersecurity-relevant changes | `gpt-6-sol` / `xhigh` with Daybreak Blue | Separate independent read-only security reviewer |
| CTO supervision explicitly requested by Javier | `gpt-6-astra` / `max` | Root CTO role only |

Javier's explicit model or reasoning instruction overrides these defaults.
Do not create agents or managed sessions solely because a route exists.
A declared route does not establish the host's selected model, effort, or
Daybreak status. Do not silently substitute a model or reasoning level.

## Independent review sequence

Use Astra High for general review of correctness, Goal compliance,
contracts, architecture, maintainability, and operational behavior. Do not
route general reviews through Daybreak by default.

For a material cybersecurity surface, or an explicit cybersecurity-review
request, add a distinct final security pass using `gpt-6-sol` with Daybreak
Blue and `xhigh`. Material surfaces include authorization and tenant
isolation, sensitive records, secrets and credentials, payment state, webhooks,
untrusted input or file handling, privilege boundaries, and other
security-critical changes. Routine work without material cybersecurity
implications does not require Daybreak.

The Daybreak pass is last on the final candidate after the Astra review and
its fixes. If security findings change code, recheck affected changes with
the existing general reviewer, then have the same Daybreak security reviewer
inspect the final head again. Subsequent code changes invalidate that verdict.

Daybreak Blue is an access mode, not a separate model identifier. In Codex,
verify the host exposes and enables Daybreak Blue for `gpt-6-sol`; for
compatible Responses API calls set `model = gpt-6-sol` and
`access_programs.cyber = daybreak_blue`. Do not select deprecated Daybreak
model aliases or assume a model name enables the access program.

When required native Daybreak security review is unsupported, rejected, or
unobservable, use the manual handoff in
`{codex_home}/references/external-daybreak-review.md`. Provide its full
ready-to-paste prompt in the originating chat with the actual originating
thread ID; do not start a session without Javier's authorization. Reuse the
chosen session for re-review. A prompt is not a completed review. Missing
Daybreak evidence blocks only the security-dependent handoff, not unrelated
authorized work.

The CTO route applies only when Javier explicitly requests CTO supervision.
Astra availability alone does not add a supervisor to routine work.
If a required route is unavailable, state the limitation, continue independent
authorized work, and block only dependent actions.

## Fully Defined Assignment

An assignment is fully defined only when it states:

- the exact objective and terminal deliverable;
- governing inputs and sources;
- scope, ownership, and permitted mutations;
- required checks and acceptance criteria; and
- unresolved decisions, dependencies, and approval boundaries.

Implementation complexity alone does not justify changing the default route.

Select a model and reasoning route only after delegation is warranted by the
orchestration policy, explicitly requested by Javier, or required by an
applicable workflow. A routine simple edit does not acquire an agent solely
because this table names an implementation route.

For `create_thread`, omit `model` and `thinking` overrides unless Javier
selected a host-supported value under that host's contract. Do not claim a
model or runtime switch from a policy entry.

## Luna Max Subagents

For a delegated fully defined implementation lane, use a native
`gpt-6-luna` subagent with `max` reasoning by default. A simple edit does not
require spawning an agent merely because this route exists.
Use one Luna Max implementer by default. Add Luna Max subagents only for
independent assignments with non-overlapping write and external-mutation
ownership. Reuse the same subagent for fixes and follow-through.

## Route Declaration

Before starting a delegated or managed lane, record its objective, topology,
exact model and reasoning, exclusive ownership, and the policy condition that
selected the route. Requested or declared routing does not establish external
authority, permissions, or observed execution.
