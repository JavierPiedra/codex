---
name: manual-qa-linear-kickoff
description: >-
  Create and execute persistent manual-QA tracking with a repo-local evidence
  document and Linear issues when Javier explicitly requests this workflow. Do
  not use it for ordinary smoke checks, application fixes, commits, or direct
  post-deploy verification.
---

# Manual QA Linear Kickoff

## Purpose And Authorization

Use this skill only when Javier explicitly requests persistent manual-QA
tracking.

That request authorizes the scoped QA document and Linear issue creation after
the repository, Linear project, and test target are clear. It does not authorize
application fixes, commits, deployments, production-data changes, or other
environment mutations.

Default to the current local branch/worktree. Ask one focused question when the
target, expected behavior, credentials, repository, or Linear project is
materially ambiguous.

## Build The QA Plan

Inspect the active goal, exact diff or commits, existing automated checks, and
relevant user-visible or integration behavior. Create only manual cases that add
evidence automated checks do not already provide.

Each case must identify the requirement, preconditions, steps, expected result,
and evidence to capture. Cover only applicable happy paths, failure paths,
permissions, persistence, background behavior, and regressions.

## Track Evidence

Create or update the repository's QA artifact. When no stronger convention
exists, use:

```text
docs/manual-qa/<YYYY-MM-DD>-<short-scope>.md
```

Use one table for requirement coverage and execution:

```markdown
| ID | Status | Requirement | Test | Expected | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
```

Use only `Not started`, `In progress`, `Pass`, `Fail`, or `Blocked`.
Record fixes and rechecks in evidence or notes rather than adding workflow
statuses.

Update a case when it starts and immediately after its result so an interrupted
run remains resumable.

## Linear Tracking

Use `linear-issue-kickoff` for issue creation only.

- Create one direct QA issue by default.
- Use an umbrella only when two or more independent QA tracks already justify
  separate child issues.
- Create failure issues only for observed, independently actionable failures
  when persistent Linear tracking adds value.
- Do not create speculative fix or verification issues.
- Do not request a branch/worktree unless Javier separately authorizes
  implementation work.

## Execute And Report

Run each case against the approved target and capture concrete evidence. For a
failure, record reproduction steps, expected behavior, actual behavior, and the
affected surface.

Return failures to the owning implementation workflow. Do not edit application
code, create commits, or reassign write ownership. Recheck only after the owning
writer provides a fix and the active request still authorizes QA.

Finish with the QA document, Linear issue URLs, pass/fail/blocked counts,
evidence gaps, and unresolved failures. Never mark an unexecuted or indirect
check as passed.
