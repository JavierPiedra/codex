---
name: prd-kickoff
description: Prepare an approved PRD or PRD suite in any repository for implementation by creating or reusing its Linear issue structure and branch/worktree handoff. Use when Javier or a calling workflow starts implementation from approved PRD sources. Stop before implementation.
---

# PRD Kickoff

## Purpose

Translate an approved PRD or PRD suite into the smallest useful Linear issue
structure and a repository-conforming branch/worktree handoff. This skill is
global and repository-aware; it must not assume a project, PRD path, section
number, branch format, or target branch.

Invoking this skill directly, or through an explicitly invoked
`goal-implementation-loop`, authorizes the described issue and branch
preparation after the Linear project and repository context are confirmed. It
does not authorize implementation or unrelated issue updates.

## Readiness

Read only the sources needed for the active kickoff:

1. The nearest applicable `AGENTS.md` and repository contribution rules.
2. Every approved PRD and execution spec in scope.
3. Repository kickoff, progress, or execution-packet documentation only when
   repository rules identify it as authoritative.

Before creating anything:

- confirm the PRD scope is approved for implementation;
- confirm the Linear project in the current conversation;
- resolve Javier's exact Linear member record for assignment;
- resolve the labels available in the destination project;
- inspect referenced or existing Linear issues to avoid duplicates;
- inspect any branch/worktree named by the caller; and
- ask one focused question only when the PRD scope, Linear project, repository,
  base, or ownership remains materially ambiguous.

If required source material is missing or conflicting, stop instead of
inventing a project-specific procedure.

## Build The Issue Structure

- Use the PRD's explicit tasks, acceptance criteria, dependencies, and ownership
  when present, regardless of heading names or section numbers.
- When the PRD does not prescribe issue boundaries, derive the fewest
  independently actionable issues that cover its observable deliverables.
- Use one top-level issue for one implementation slice. Use an umbrella only
  when two or more genuine child slices need shared tracking; never create an
  empty or single-child umbrella.
- Reuse an existing issue when it already represents the same PRD scope. Do not
  create duplicate tracking merely because this skill was invoked again.
- Preserve only dependencies required by the PRD or by actual execution order.
  Do not invent cross-lane dependencies.
- Encode current scope, observable acceptance criteria, relevant checks, and
  explicit ownership without copying the entire PRD into Linear.
- Give every new issue at least one label. Use the smallest relevant set already
  available in the destination project. Create and apply a missing label only
  after Javier explicitly approves that label. If no valid label applies, stop
  before issue creation.
- Assign every new issue to Javier by default. Use another assignee only when
  Javier explicitly names that person. Never create an unassigned issue. If
  Javier's member record cannot be resolved unambiguously, stop before
  creation.
- Set `To Do` only while creating an issue unless Javier requests another
  creation status. Do not change existing statuses, assignees, priorities,
  cycles, or due dates without explicit instruction.
- Do not add comments or update PRD task status unless Javier explicitly asks.
- Do not create a label unless Javier explicitly approves it.

Use the Linear tool directly. Do not fall back to Browser, Chrome, or Computer
Use unless Javier explicitly authorizes that interface. If the Linear tool is
unavailable, stop as blocked.

After creation, re-fetch every created issue and verify its assignee, project,
status, labels, parent/child structure, and dependencies. Treat an unassigned
or unlabeled result as a failed creation gate.

## Branch And Worktree Handoff

Reuse a branch/worktree supplied by the caller only after verifying that it
matches the repository and approved PRD scope. Respect an explicit no-branch
instruction. Otherwise use `create-branch` after issue creation and let that
skill own base resolution, repository naming, temporary-worktree creation,
dirty-tree safety, and reporting.

Use one branch/worktree for the direct issue or umbrella unless independent
repositories require separate ownership. Do not hardcode `staging`, `main`, or
any branch format.

Reuse repository kickoff or execution-packet templates only when repository
rules require them. Do not generate project-specific artifacts or fixed-path
files unless an authoritative repository procedure requires them.

## Ownership Boundary

This skill does not implement tasks, create commits, run reviewers, change PRD
status, open a PR, merge, deploy, or mutate production. Those actions belong to
the calling implementation workflow and its approval boundaries.

## Result

Return:

- repository and approved PRD sources;
- confirmed Linear project;
- reused and created issue identifiers, titles, URLs, assignees, labels,
  creation status, ownership, and dependencies;
- reused or created branch, worktree, and exact base SHA;
- repository-required handoff artifacts; and
- the first dependency-free issue or the blocker preventing handoff.

Then return control to the caller.
