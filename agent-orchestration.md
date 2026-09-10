# Agent Orchestration

This document governs agent topology, lifecycle, communication, waiting, reuse,
and handoffs. Model selection is governed by
`/Users/javierpiedra/.codex/agent-model-routing.md`.

Javier's explicit orchestration instructions override these defaults.

## Default Topology

Use one execution lane by default. Add lanes only when their work is genuinely
independent, ownership does not overlap, and delegation materially improves the
result or elapsed time.

Choose the role and lane form required by the model-routing policy:

- the root CTO role only when Javier explicitly requests CTO supervision;
- a native implementation writer for a fully defined implementation lane;
- a native independent reviewer when review semantics are required;
- a senior orchestrator for orchestration or judgment work; and
- an explicitly authorized special route when the assignment requires it.

Select model and reasoning identifiers from the model-routing policy rather than
duplicating them here.

Do not create parallel lanes for the same implementation, review, or decision.
Astra availability alone does not require a CTO or another supervisory layer
for a simple task.

## Assignment Contract

Before starting a lane, define:

- role, objective, and terminal deliverable;
- governing inputs and sources;
- exclusive write ownership;
- permitted and prohibited actions;
- required checks and acceptance criteria;
- dependencies, handoffs, and stop conditions; and
- approval boundaries that remain with Javier.

The assignment must be complete enough for the lane to work without tactical
approvals. Delegation never expands scope or authority.

If an orchestrator needs workers or a reviewer, the assignment must explicitly
authorize each named, bounded child role, including its objective, ownership,
permitted actions, evidence, and stop condition. General permission to
delegate does not authorize a child to fan out.

## Lifecycle

1. Create each role once.
2. Give it one complete assignment.
3. Wait for a blocker, dependency handoff, failed gate, or terminal result.
4. Reuse the same role for fixes, re-review, checks, and follow-through.
5. Close or replace it only after terminal completion or confirmed failure.

Use `followup_task` for native agents, including Luna Max implementers. Do not
create or continue a managed session for Luna work. Continue the same managed
session only when another route explicitly requires one. Do not create a
replacement merely because work is slow or a wait timed out.

For a requested CTO topology, use the smallest necessary chain: root CTO to a
senior orchestrator, then to explicitly named bounded writer or reviewer roles
when the assignment requires them. Confirm each handoff and exclusive mutable
ownership before reassignment. Reuse the same role for corrections and
follow-through; add no supervisor by default.

## Event-Driven Waiting

Wait for events; do not poll agents, CI, deployments, pull requests, or other
systems on a recurring interval.

The responsible implementation lane owns its checks and any blocking CI or
deployment watcher through a terminal result. Do not create a separate monitor
agent only to wait.

A mailbox timeout is not a failure and does not justify a status request,
replacement agent, or new orchestration cycle.

## Communication

Each writer or reviewer reports to its responsible orchestrator. An
orchestrator reports to the CTO when the objective is under requested CTO
supervision; otherwise it reports to the root. Report only when a real blocker
requires input, a dependency handoff is ready, a gate fails and requires a
decision, or the role reaches a terminal result. The root consolidates the user
result and tells Javier only meaningful blockers, approval gates, completed
milestones, and the terminal outcome.

Do not report acknowledgements, routine progress, unchanged waits, or every
test run.

## Ownership, Review, And Fan-Out

Never give two lanes overlapping write ownership.

Use one independent reviewer for a stable implementation. Send consolidated
findings to the existing implementer, then reuse the same reviewer after fixes.

Only the root may delegate by default. A child may fan out only when its
assignment explicitly authorizes named, bounded, non-overlapping child lanes,
such as a writer or reviewer. Hidden or open-ended agent trees are prohibited.

The CTO communicates direction to the responsible orchestrator. It does not
issue competing instructions directly to that orchestrator's writers or
reviewers.

## Root Responsibilities

The root orchestrator owns topology, exclusive ownership, dependency handoffs,
approval boundaries, and final consolidation. It must not duplicate work that
belongs to another lane or turn routine waiting into commentary or new work.

System, developer, security, and permission requirements remain higher
priority than this guide.
