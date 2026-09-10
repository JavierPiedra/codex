---
name: goal-ready-prd
description: Turn an approved product or engineering goal into a decision-complete PRD or smaller Linear-ready issue for later implementation. Use when Javier needs durable requirements, acceptance criteria, unresolved decisions, or an implementation handoff; do not perform implementation or execution bookkeeping.
---

# Goal Ready PRD

Turn an approved goal into a durable product contract that an implementation
workflow can execute without reconstructing decisions from chat. This skill
authors requirements; it does not create issues, branches, commits, pull
requests, or deployments.

## Read only what applies

Read the applicable `AGENTS.md` and the repository guidance needed for the goal.
Read current code or other evidence only when it is needed to avoid inventing a
requirement. For an Awra repository, read the canonical PRD contract at
`/Users/javierpiedra/.awra/dev-guidance/skills/prd/SKILL.md` and any conditional
Awra guide it names. Do not load complete implementation, kickoff, review, or
branch skills before drafting; link to the later handoff instead.

Before proposing delegated work, read the current
`/Users/javierpiedra/.codex/agent-model-routing.md` and
`/Users/javierpiedra/.codex/agent-orchestration.md`.

## Establish the contract

1. Restate the approved goal, target users or operators, affected products and
   repositories, source discussion or incident, environments, and the current
   authority boundary.
2. Inspect the smallest relevant set of entry points, current behavior, tests,
   schemas, APIs, provider contracts, configuration, UI surfaces, and durable
   docs. Record facts and evidence separately from inferences and unknowns.
3. Classify each material point as a fixed requirement, quality bar, owner
   decision, question delegated to Pro, assumption, side effect to validate, or
   non-goal. Do not reopen decisions Javier already made.
4. Ask only questions whose answers change product behavior, architecture,
   data handling, security, ownership, rollout, rollback, or acceptance. Keep
   an unresolved material question explicit; never fill it with a guessed
   policy.

For deletion, remediation, prompt, schema, or runtime work, search the relevant
code and docs for adjacent fallback, repair, retry, normalization, backfill,
placeholder, synthetic, best-effort, or schema-repair paths. Treat unavailable
evidence as an unknown with a concrete stop condition.

## Choose the smallest artifact

- Use one Linear-ready issue when the scope is small and implementation will not
  need a durable product contract. Create or update it only when the invoking
  task explicitly requests that operation.
- Use one durable PRD when behavior, scope, interfaces, or product decisions
  need an independent source of truth. This is the default for a goal that
  needs this skill.
- Add a technical specification only when the actual implementation complexity
  needs detail that does not belong in the product contract.
- Add child PRDs or multiple specifications only for independently executable
  workstreams, repositories, shared contracts, migrations, or coordinated
  rollout. Do not split a small goal into a package for organizational reasons.

For an Awra PRD, follow its canonical rule to omit repository paths, branches,
SHAs, inspection dates, commands, and agent bookkeeping from the product
contract. Keep execution evidence in the systems that own it. The same rule
does not automatically govern other repositories: follow their PRD conventions
and keep execution bookkeeping separate unless that convention or the request
requires it.

## Write the artifact

Write to the repository-authorized destination Javier supplied or that the
current project convention makes unambiguous, in a mode that permits writes.
Ask only when the artifact location is materially unresolved. A single PRD can be one Markdown file. A genuinely complex goal may use
a directory containing a master PRD, only the necessary child PRDs, and one
technical specification per child. Do not require a manifest, checksums, or an
execution spec for a small goal.

Use this compact PRD shape and include only applicable sections:

```md
# PRD: <title>

## Problem and Impact

## Goals and Success Criteria

## Non-Goals

## Scenarios and Requirements

## Confirmed Constraints and Interfaces

## Open Decisions
```

State observable behavior and acceptance criteria. Use requirement identifiers
only when several requirements need stable traceability. Include `Open
Decisions` only for unresolved choices that materially block implementation and
write each actual question. Omit unavailable, irrelevant, and empty fields;
do not insert invented identifiers or placeholder metadata.

For a requested Linear-ready issue, keep one measurable implementation scope:

```md
## <Imperative title>

### Context
<why the work exists>

### Scope
- <required change or explicit exclusion>

### Success Criteria
- <observable completion condition>

### Constraints / Interfaces
- <confirmed constraint, when applicable>

### Verification
- <observable acceptance check>
```

Keep issue fields such as owner, priority, labels, dependencies, identifier,
and status in the destination project. Keep branch commands, worktree setup,
agent prompts, and execution logs out of the issue and PRD.

## Plan mode and handoff

In Plan Mode, investigate read-only, resolve the artifact destination, present
the decision map, and ask the smallest remaining material questions. Do not
write files or mutate Linear, Git, providers, data, or environments.

Outside Plan Mode, write the approved artifact after its destination is known.
Then check that every requirement is testable, every material decision is
settled or explicitly listed, interfaces and lifecycle behavior are clear when
applicable, non-goals are explicit, and the document does not invent current
implementation facts. Report the durable path, status, unresolved decisions,
and the next authorized handoff. Do not paste the full document into chat.

When handing off to `goal-implementation-loop`, identify the artifact path,
confirmed repositories and environment boundaries, proposed issue scope, tests,
rollout and rollback decisions, and any blocker. The later workflow owns issue
creation, branch preparation, implementation, review, verification, and PR
actions.

Stop without claiming readiness when product intent, artifact location,
required source evidence, existing-data treatment, migration or compatibility
policy, rollback, privileged ownership, or objective acceptance remains
materially unresolved.
