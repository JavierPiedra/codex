---
name: create-branch
description: Create a repo-conforming Git branch in a fresh temporary worktree by default while preserving existing checkouts and local changes. Use when Javier explicitly asks to create, prepare, switch to, check out, or propose a branch.
---

# Create Branch

Use this skill for branch preparation. A request to propose or normalize a
branch name is read-only: return the candidate and create nothing.

## Resolve and inspect

1. Read the current request, the nearest applicable `AGENTS.md`, and only the
   branch guidance for the target repository.
2. Resolve the base branch from the request or unambiguous repository guidance.
   Ask one focused question when the base or final name remains materially
   ambiguous.
3. Inspect `git status -sb`, current branches, remotes, and worktrees. Preserve
   unrelated changes; never stash, reset, discard, move, overwrite, or commit
   them.
4. Derive the name from repository guidance. Preserve a supplied tracker issue
   identifier and normalize the descriptive slug. For Awra, let the shared
   Awra branch skill own its naming convention and slug normalization.

## Create

Unless Javier explicitly selects an existing destination checkout or worktree,
fetch the requested remote base (or use an explicitly supplied fixed SHA as the
base), verify the exact starting SHA, and create the branch in a fresh
temporary worktree. A fixed base SHA selects the starting point; by itself it
does not select a destination or override the fresh-worktree default. Do not
alter an existing checkout to prepare it. An explicitly selected destination
checkout or worktree may be used after checking that it matches the target
repository and scope.

Confirm the new branch is not checked out elsewhere and report the repository,
remote base and SHA, worktree path, final branch name, and resulting status.
Keep the worktree through handoff unless Javier requests cleanup.

Pushing is a separate remote action. Before any history rewrite, check whether
the branch exists on `origin`; never rewrite pushed history without Javier's
explicit approval after that check.
