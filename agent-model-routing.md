# Agent Model Routing

Use this policy for delegated agents, managed Codex continuations, and explicit
model-orchestration requests. It does not define any implementation workflow.

Javier's explicit model or reasoning instruction overrides these defaults.
Lifecycle and handoff rules live in
`/Users/javierpiedra/.codex/agent-orchestration.md`.

## Routing Table

| Assignment | Route | Topology |
| --- | --- | --- |
| CTO supervision explicitly requested by Javier | `gpt-6-astra` / `ultra` | Root CTO role only |
| Fully defined implementation lane | `gpt-5.6-luna` / `max` | Native `spawn_agent` subagent |
| Senior orchestration or unresolved judgment | `gpt-5.6-sol` / `medium` | Native or managed lane |
| Independent code or security review | `gpt-daybreak-blue-latest` / `medium` or `high` | Native independent read-only lane |
| Explicit Terra assignment | `gpt-5.6-terra` / `max` | Native lane |
| Authorized unusually difficult decision | `gpt-5.6-sol` / `high` | Native lane |

The CTO route uses `gpt-6-astra` with `ultra` only when Javier explicitly
requests CTO supervision and the host supports that exact route. A route names
the requested assignment; it does not prove that the runtime selected or
observed it. Do not silently substitute a model or reasoning level. Terra is
not a Luna fallback. `ultra` is a root-session mode and must not be assigned to
a child.

Astra availability alone does not activate CTO or add a supervisory layer to a
simple task. The exact model and reasoning identifiers above are route entries,
not a capability ranking. If a requested route is unavailable or cannot be
observed, report that limitation and continue any independent authorized work;
block only a dependent action that is incompatible without the route.

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
`gpt-5.6-luna` subagent with `max` reasoning by default. A simple edit does not
require spawning an agent merely because this route exists.
Use one Luna Max implementer by default. Add Luna Max subagents only for
independent assignments with non-overlapping write and external-mutation
ownership. Reuse the same subagent for fixes and follow-through.

## Route Declaration

Before starting a delegated or managed lane, record its objective, topology,
exact model and reasoning, exclusive ownership, and the policy condition that
selected the route. Requested or declared routing does not establish external
authority, permissions, or observed execution.
