---
name: create-linear-issues
description: Create the smallest useful Linear issue structure from Javier's approved scope and stop after verified issue creation. Use when Linear issues are the complete deliverable; use linear-issue-kickoff instead when branch or worktree handoff is requested.
---

# Create Linear Issues

## Purpose

Create well-scoped Linear issues without starting implementation or preparing a
branch. Preserve the approved scope and make each issue independently useful.

## Before Creation

- Read the nearest applicable `AGENTS.md` and relevant Linear rules.
- Use only Javier's active approved scope. Do not add adjacent cleanup or future
  work.
- Confirm the exact Linear project in the current conversation before creating
  anything. If it is missing or ambiguous, ask one focused question.
- Confirm the team only when the project does not determine it.
- Resolve Javier's exact Linear member record for assignment. If it cannot be
  resolved unambiguously, stop before creation instead of leaving an issue
  unassigned.
- Resolve the labels available in the destination project. If no existing label
  applies and Javier has not explicitly approved a new label, stop before
  creation instead of leaving an issue unlabeled.
- Treat invocation as authorization to create the described issues after the
  project is confirmed. It does not authorize updating unrelated existing
  issues.

## Issue Structure

- Create one top-level issue for one independently actionable slice.
- For two or more real implementation slices, create either separate top-level
  issues or one umbrella with the fewest useful child issues.
- Never create an empty umbrella or an umbrella with one child.
- Express dependencies through Linear relationships. Do not hide them only in
  prose.
- Identify the first dependency-free issue when ordering matters.

## Issue Format

Use a concrete, outcome-oriented title. Avoid vague verbs such as `improve`,
`enhance`, `cleanup`, or `update` unless the object and resulting behavior are
explicit.

Use only the sections the issue needs, in this order:

```markdown
## Purpose
<Why this issue exists and the user or production consequence.>

## Scope
- <Concrete behavior or artifact included.>

## Acceptance criteria
- [ ] <Observable result.>
- [ ] <Required failure, authorization, migration, or isolation behavior.>

## Checks
- <Test, query, manual verification, or deployment evidence required.>

## Dependencies
- Blocked by <issue title and identifier>, or `None`.
```

Formatting rules:

- Keep the purpose to one short paragraph.
- Write acceptance criteria as observable outcomes, not implementation tasks.
- Include out-of-scope text only when it prevents a likely misunderstanding.
- Include implementation notes only when a verified constraint would otherwise
  be lost.
- Do not repeat project, status, owner, labels, priority, or relationships in
  the description when Linear fields already represent them.
- Never invent issue identifiers, estimates, alternative assignees, priorities,
  cycles, due dates, unapproved labels, or dependencies.

## Creation Rules

- Use the Linear tool directly. Do not use Browser, Chrome, or Computer Use
  unless Javier explicitly authorizes that interface.
- Set `To Do` only while creating an issue unless Javier explicitly requests a
  different creation status.
- Assign every new issue to Javier by default. Use another assignee only when
  Javier explicitly names that person. Never create an unassigned issue and do
  not change an existing issue's assignee without explicit instruction.
- Set priority, cycle, estimate, or due date only when explicitly requested.
- Give every new issue at least one label. Use the smallest relevant set already
  available in the destination project.
- Create and apply a missing label only after Javier explicitly approves that
  label. Do not create an unlabeled issue or change labels on an existing issue
  without explicit instruction.
- Do not change any existing issue status.
- After creation, re-fetch every created issue and verify its project, title,
  description, assignee, status, labels, parent/child structure, and
  dependencies.
- If the Linear tool is unavailable or verification disagrees with the intended
  result, stop and report the blocker. Do not fall back to another interface.

## Result

Return:

- confirmed Linear project;
- each issue identifier, title, URL, assignee, status, and labels;
- parent/child and blocking relationships;
- the first dependency-free issue, when relevant;
- any field that could not be verified.

Do not implement, create a branch or worktree, commit, open a pull request, add
comments, or change existing issue status. Return control after verified issue
creation.
