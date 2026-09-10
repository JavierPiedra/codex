---
name: linear-issue-kickoff
description: Turn an agreed implementation plan into the smallest useful Linear issue structure and optional branch/worktree handoff. Use when Javier asks to create Linear issues for scoped work; do not use it to implement, review, commit, or open a pull request.
---

# Linear Issue Kickoff

## Purpose

Create a lightweight implementation kickoff without a PRD. This skill owns
Linear issue creation and, when implementation is in scope, branch/worktree
preparation. It stops at a concrete execution handoff.

## Readiness

- Use only Javier's active approved scope.
- Read the nearest applicable `AGENTS.md` and only relevant Linear or branch
  rules.
- Confirm the Linear project in the current conversation before creating
  anything. If it is missing or ambiguous, ask one focused question.
- Resolve Javier's exact Linear member record. If it cannot be resolved
  unambiguously, stop before creation instead of leaving an issue unassigned.
- Resolve the labels available in the destination project. If no existing label
  applies and Javier has not explicitly approved a new label, stop before
  creation instead of leaving an issue unlabeled.
- Confirm whether a branch/worktree handoff is part of this invocation.

Invoking this skill authorizes the described issue creation after the project is
confirmed. It does not authorize unrelated issue updates or implementation.

## Create The Smallest Issue Structure

- One independently actionable slice becomes one top-level issue.
- Two or more real implementation slices may use one umbrella with the fewest
  useful child issues.
- Do not create an empty or single-child umbrella.
- Encode only current scope, observable acceptance criteria, dependencies, and
  relevant checks.
- Give every new issue at least one label. Use the smallest relevant set already
  available in the destination project. Create and apply a missing label only
  after Javier explicitly approves that label.
- Assign every new issue to Javier by default. Use another assignee only when
  Javier explicitly names that person. Never create an unassigned issue and do
  not change an existing issue's assignee without explicit instruction.
- Set `To Do` only while creating an issue unless Javier requests another
  creation status. Do not change existing issue statuses, priorities, cycles,
  or due dates without explicit instruction.

Use the Linear tool directly. Do not fall back to Browser, Chrome, or Computer
Use unless Javier explicitly authorizes that interface. If the Linear tool is
unavailable, stop as blocked.

After creation, re-fetch every created issue and verify its assignee, project,
status, labels, parent/child structure, and dependencies. Treat an unassigned
or unlabeled result as a failed creation gate.

Do not add Linear comments. Do not create a label unless Javier explicitly
approves it.

## Optional Branch Handoff

When implementation is in scope, use `create-branch` after issue creation. Let
that skill own base resolution, naming, temporary-worktree creation, dirty-tree
safety, and reporting.

Use one branch/worktree for the direct issue or umbrella unless independent
repositories require separate ownership. Do not hardcode `staging` or a branch
format outside repository guidance.

## Result

Return:

- confirmed Linear project;
- issue identifiers, titles, URLs, assignees, labels, creation status, and
  dependencies;
- branch, worktree, and exact base SHA when created;
- the first dependency-free issue or the blocker preventing handoff.

Do not implement issues, commit code, run a review loop, or open a PR. Return
control to the caller after the kickoff handoff.
