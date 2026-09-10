---
name: feature-council
description: Run a read-only, repository-grounded council for a proposed feature before implementation. Use when Javier asks for feature-council or a multi-perspective feature decision requiring focused exploration, material questions, and a decision memo or requested PRD/task brief.
---

# Feature Council

Evaluate whether and how to add a feature before implementation. Keep source
repositories and external systems read-only: no patches, branches, commits,
PRs, database changes, or external mutations. The only planning-artifact
exception is a deep-research prompt written under `/tmp`.

Follow active `AGENTS.md`, repository guidance, memory routing, and current
model/orchestration rules. Never invent files, APIs, models, routes, user data,
market facts, or evidence. Extend existing patterns when the evidence supports
it and use the shortest unambiguous output.

## Workflow

### Establish the decision

State the proposed feature, affected users, desired outcome, repositories,
known constraints, and decision Javier needs to make. Ask one focused question
only when a wrong assumption would change the feature, repository, or decision.

### Explore repositories when evidence is missing

Assess the available context for each repository before delegating exploration.
Reuse supplied context and existing evidence when sufficient for the decision.
Explore only material evidence gaps or uncertain freshness; state remaining
unknowns explicitly. Do not repeat repository scans solely to run this skill.

When exploration is needed, read the repository's applicable guidance first.
Use one independent read-only explorer per repository needing investigation,
with model and reasoning selected from current routing. Give each explorer
exclusive responsibility for that repository, the shared feature target, and
the specific gaps to resolve. Inspect relevant docs, architecture, routes,
models, services, UI flows, tests, adjacent stale paths, and Git provenance
only as needed to resolve those gaps.

Each explorer reports the relevant findings, source citations, branch/commit
and evidence date when available, and unresolved gaps or contradictions.
The main agent verifies only ambiguous or conflicting claims instead of
repeating full repository scans.

### Build evidence and choose roles

Consolidate a neutral evidence packet that separates facts, inferences, user
decisions, and unknowns. Select the smallest useful council, normally two to
six roles, with each role capable of changing the decision. Candidates include
engineering, product, UX, accessibility, security, data, operations, legal,
regulatory, finance, marketing, growth, support, and rollout. Omit ceremonial
roles and record why each chosen role matters.

Prefer suitable existing custom-agent profiles. The recurring specialists
`council_engineering`, `council_product`, and `council_ux` are available options,
not mandatory attendees. Reuse other suitable profiles, including
`delivery_simplifier`, according to their current definitions. Inspect those
definitions when their remit is not already sufficiently available; preserve
their boundaries instead of duplicating or silently broadening them.

Invoke `council_hr` only when Javier explicitly requests HR. Missing expertise
alone must never trigger it. Give HR the decision and available profile context
and return its proposed roles and profiles for Javier's review, then stop.
Do not install profiles or launch the proposed council as part of that HR
proposal. Continue only after Javier authorizes the next step.

Choose each council agent's model and reasoning from current routing unless the
invocation supplies them. Keep ownership read-only and non-overlapping.

### Run one council round

Spawn one independent read-only agent per selected role. Give all roles the
same evidence packet and feature target without other roles' opinions. Require
each to return a preliminary position, supporting and conflicting evidence,
user value and operational consequences, material tradeoffs and risks,
questions that could change the recommendation with suggested answers, material
uncertainties it will not assume, confidence, and what would change its view.
Keep contributions focused on the assigned decision and role. Do not manufacture
objections, questions, or uncertainty to satisfy the response structure.
Surface genuine disagreement. If the requested council cannot run, report the
blocker rather than simulating missing perspectives.

### Resolve material questions

Merge duplicate questions and ask only questions that change product,
technical, UX, security, data, legal, rollout, or market direction. Use batches
of one to three and pause for answers. For a complex question, state the
scenario, decision, what each option permits and requires, failure behavior,
tradeoffs, and the council recommendation. Treat silence as no answer.

After answers arrive, send the exact answers and new evidence to the same role
agents and ask them to update their position, risks, confidence, and smallest
valuable version. Identify which answer changed each view and what
disagreement remains.

### Research only when it can change the decision

Use deep research only when current external evidence could change scope,
safety, legality, market need, or roadmap commitment. State the decision it
must unblock and whether it is needed before scoping, roadmap commitment, or
build. Write a self-contained prompt to
`/tmp/feature-council-deep-research-<feature-slug>.md` with repository/product
evidence, unknowns and hypotheses, detailed research questions, applicable
primary-source and recency requirements, counterevidence, citations,
confidence labels, and decision criteria. Report the path and purpose. Perform
research only when Javier explicitly requests it and suitable tools exist.

## Synthesize and recommend

Separate verified facts, interpretations, recommendations, risks, accepted
assumptions, and unresolved questions. Choose exactly one recommendation:
`Build`, `Reframe`, `Defer`, or `Do not build`. Explain dissent and the smallest
valuable version for `Build` or `Reframe`; state what evidence would reopen
`Defer` or `Do not build`.

Default to a decision memo covering the problem and repository signal, Javier's
answers, selected roles and revised positions, disagreement, research verdict,
recommendation, smallest valuable version, risks, evidence gaps, and next gate.
Produce a full PRD or minor-version task brief only when Javier requests it,
material questions are answered, and the recommendation supports it. Follow
repository guidance for that deliverable and keep source repositories read-only
until implementation or document edits are separately authorized.

When requested, a full PRD includes problem, why now, goals and metrics,
confidence/evidence, users and stories, scope/non-goals, functional and
non-functional requirements, dependencies/assumptions, milestones, risks, and
open questions. A minor-version brief includes objective/value, scope and
non-goals, Linear implementation tasks, acceptance criteria, validation plan,
and risks.
