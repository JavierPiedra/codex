# Adaptable Goal template

Use only the clauses needed for the task; replace placeholders with established
requirements. Do not turn this layout into a validation grammar.
Measure the final substituted block using the character-count rule in
`SKILL.md`; it must fit within 4,000 characters before delivery.

```text
/goal [Observable result and target], following [relevant governing source].
Complete when [acceptance conditions], demonstrated by [appropriate evidence].
Respect [material scope, non-regression requirements, and existing authority].
[Add necessary context, dependencies, checkpoints, or supplied limits.]
Deliver [the requested artifact or evidence-based report].
```

## Example: investigation with incomplete evidence

Assume the requested deliverable is a read-only incident report using the
available logs, not a guaranteed diagnosis:

```text
/goal Produce a read-only incident report for the checkout failures in the agreed
time window. Use the supplied logs and deployment history to build a timeline
and distinguish confirmed causes, supported hypotheses, and unanswered questions.
Link each material conclusion to its evidence. If retention or access prevents
checking a claim, identify the missing source and the next input needed while
continuing the independent analysis. Finish with the report and its evidence
gaps; do not change services or customer data.
```

## Example: multi-part implementation

Assume an approved plan defines the replacement import format, repositories,
fixtures, data preservation, and local-only delivery:

```text
/goal Replace the old import format across the backend and frontend as specified
in the approved plan, migrating the data that must survive and removing the
obsolete paths. Demonstrate the plan's acceptance examples through the interface
and isolated persistence, including rejection of invalid inputs without partial
writes. Work in the plan's repositories and local test environments. Follow the
dependencies through verifiable milestones and retain decisions needed for the
next milestone. Report any unavailable fixture or unresolved contract without
claiming its requirement is complete. Deliver local changes and verification
evidence.
```

These examples do not authorize execution or prescribe budgets, new approvals,
extra reviewers, or a fixed number of iterations.
