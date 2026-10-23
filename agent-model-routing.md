# Agent Model Routing

Use this policy for delegated agents, managed Codex continuations, and explicit
model-orchestration requests. It does not define any implementation workflow.

Javier's explicit model or reasoning instruction overrides these defaults.
Lifecycle and handoff rules live in
`{codex_home}/agent-orchestration.md`.

## Unversioned model names

When Javier says "Luna" or "Sol" without an explicit version, resolve that
family to its newest version available on the execution host at action time.
Check the current tool model list or host model catalog before selecting it;
do not assume a remembered identifier is still the newest. Preserve the
requested reasoning effort when supported. An explicit version requested by
Javier takes precedence. If availability cannot be established, report the
uncertainty instead of silently selecting an older version.

Agent profiles that require a concrete model identifier record the current
available default. Resolve unversioned requests using the rule above and
refresh the configured identifier when a newer available version is confirmed.

## Routing Table

| Assignment | Route | Topology |
| --- | --- | --- |
| Senior orchestration, including Goal orchestration | latest available Sol / `xhigh` | Root or authorized delegated orchestrator |
| Fully defined implementation writer | latest available Luna / `max` | Native `spawn_agent` subagent |
| Independent general code, contract, and correctness review | `gpt-6-astra` / `high` | Independent read-only reviewer |
| Goal engineering advisor/council | `gpt-6-astra` / `xhigh` | Read-only `goal_engineering_advisor` |
| Other read-only council specialists | `gpt-6-astra` / `xhigh` | Bounded, independent specialist lanes |
| Final review of materially cybersecurity-relevant changes | Daybreak Blue | Separate independent read-only security reviewer |
| CTO supervision explicitly requested by Javier | `gpt-6-astra` / `max` | Root CTO role only |

Javier's explicit model or reasoning instruction overrides these defaults.
Do not create agents or managed sessions solely because a route exists.
Do not silently substitute a model or reasoning level.

## Independent review sequence

Use Astra High for general review of correctness, Goal compliance,
contracts, architecture, maintainability, and operational behavior. Do not
route general reviews through Daybreak by default.

For a material cybersecurity surface, or an explicit cybersecurity-review
request, add a distinct final security pass using Daybreak Blue. Material
surfaces include authorization and tenant
isolation, sensitive records, secrets and credentials, payment state, webhooks,
untrusted input or file handling, privilege boundaries, and other
security-critical changes. Routine work without material cybersecurity
implications does not require Daybreak.

The Daybreak pass is last on the final candidate after the Astra review and
its fixes. If security findings change code, recheck affected changes with
the existing general reviewer, then have the same Daybreak security reviewer
inspect the final head again. Subsequent code changes invalidate that verdict.

When required native Daybreak security review is unsupported or rejected,
use the manual handoff in
`{codex_home}/references/external-daybreak-review.md`. Provide its full
ready-to-paste prompt in the originating chat with the actual originating
thread ID; do not start a session without Javier's authorization. Reuse the
chosen session for re-review. Always instruct the reviewer to send the full
report to the session requesting the review. A prompt is not a completed review.
A pending security review blocks only the security-dependent handoff, not
unrelated authorized work.

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

## Latest available Luna subagents

For a delegated fully defined implementation lane, use a native
subagent running the latest available Luna with `max` reasoning by default.
A simple edit does not require spawning an agent merely because this route exists.
Use one implementer by default. Add more Luna subagents only for
independent assignments with non-overlapping write and external-mutation
ownership. Reuse the same subagent for fixes and follow-through.

## Route Declaration

Before starting a delegated or managed lane, record its objective, topology,
the assigned route, exclusive ownership, and the policy condition that
selected the route. Requested or declared routing does not establish external
authority, permissions, or observed execution.
