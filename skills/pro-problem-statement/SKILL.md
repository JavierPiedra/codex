---
name: pro-problem-statement
description: Turn product and engineering discussion into a project-grounded problem statement for Pro. Use for rough issue notes, draft refinement, or a high-signal PRD prompt that separates fixed decisions, material questions, side effects, and scope.
---

# Pro Problem Statement

Turn messy discussion into a problem statement that lets Pro produce a PRD
without avoidable back-and-forth. Read the project's applicable guidance and
the user-provided artifacts before writing. Prefer active progress docs,
planning guidance, product or vision docs, and the exact notes, drafts, issues,
workflows, policies, schemas, configs, and screens named by the user. If a
referenced artifact is missing, say so and continue from available evidence.

By default write or update the Markdown document in the project where this
skill is invoked, using its existing planning convention or a sensible
`problem-statement-<initiative-slug>.md` name.

## Mode boundaries

In Plan Mode, investigate read-only, classify facts and decisions, resolve
material owner questions, and present only the plan and decision map. Do not
write a file or paste the full statement.

Treat `hazme preguntas primero`, `questions first`, or equivalent as the same
read-only question-first mode. `Draft subject to approval` means produce a
complete, reviewable draft in the normal write-capable mode and mark it as
pending approval; it is not a request to suppress the draft or add another
permission gate for an ordinary project file. If the user explicitly requests
chat-only output, return the draft there instead of writing it.

Never convert an unresolved owner decision into a requirement, assumption, or
question for Pro. Ask one focused question when the answer changes product
behavior, architecture, data handling, security, ownership, rollout, or scope.

## Build the statement

1. Extract every substantive point as a fixed requirement, quality bar, owner
   decision still required, question delegated to Pro, side effect to validate,
   assumption, or non-goal. Preserve decisions already made.
2. Frame the actual user or product pain: latency, confusion, quality loss,
   coordination cost, or user-visible friction. Do not call an expected guard or
   invariant the problem.
3. Inspect project reality around affected surfaces: current routes, services,
   statuses, readiness, drafts, handoffs, access rules, state transitions,
   safeguards, and documentation. If an existing state drives downstream
   behavior, name its current meaning before proposing another one.
4. Ask Pro only lifecycle, contract, state-model, quality-preservation, and
   user-visible design questions explicitly delegated by the owner. Remove
   low-level implementation forks that Pro does not need to decide.
5. Define overloaded terms inline, distinguish current behavior from desired
   behavior, and name stale sources or contract drift precisely.
6. Put hard requirements in `Desired Direction` and fence out declared
   non-goals. Do not force a particular architecture or project vocabulary.

Use [problem-statement-template.md](./references/problem-statement-template.md)
for the document shape. Keep the scope tight and include only evidence and
questions that can change the PRD. Review the result once for reopened owner
decisions, vague goals, missing workflow or stakeholder effects, and
unsupported claims.

## Quality and adaptation

- Lead with the pain and observable consequence, then give the evidence.
- Separate verified facts, decisions, assumptions, Pro questions, and unknowns.
- Prefer the smallest conceptual model that satisfies the goal.
- If related issues belong to one initiative, unify them and state the boundary.
- Use project-specific planning docs, issue metadata, state models, and operating
  contracts when present; otherwise derive only the minimum reliable context.
- The requested planning document may be written in its normal project
  destination; keep application/source edits and unrelated mutations read-only
  unless separately authorized.

When the user asks for the document, confirm material decisions are resolved or
explicitly delegated, state the destination path, write the statement, and
report its status. When refining an existing draft, rewrite it in place after
identifying low-level, vague, or reopened sections.
