---
name: session-tldr
description: Summarize the active Codex session's purpose, substantive results, and remaining work. Use when the user asks for a session TL;DR, recap, or handoff-ready summary.
---

# Session TL;DR

Help the user recover the session's context: why it exists, what it
accomplished, and what remains.

Summarize the active session only. Do not resume work, change files, update
external systems, or infer completion from a plan.

## Workflow

1. Recover the session's objective and explicitly agreed scope changes from
   the full available history, not just the latest exchanges.
2. Identify results against that objective: functional requirements achieved,
   questions answered, decisions reached, and deliverables produced.
   Include documentation when it was part of the work.
3. Identify what remains incomplete, unverified, or blocked within the agreed
   scope, and whether the user needs to act.
4. Use completed tool results as evidence. Perform read-only verification
   only when an essential claim cannot be resolved from the session.
   State when missing history prevents a reliable summary.

## Output

- Match the user's language.
- Start with `TL;DR` and answer in this order:
  1. Purpose: one sentence explaining the problem or intended outcome.
  2. Results: a few concise points explaining what was achieved and what
     behavior or deliverable changed.
  3. Remaining: material gaps, blockers, or required decisions. Omit when
     there are none.
- Use plain language while preserving necessary technical terms.
- Aim for 100–180 words; use fewer for simple sessions. Add detail only when
  needed to preserve a material result or limitation.

## Selection rules

- Organize around the objective and results, not chronology or repositories.
- Include recent debugging, CI repairs, and coordination only when they
  materially affect the outcome or explain a remaining blocker.
- Explain functionality through concrete behavior. PR counts, changed files,
  and passing tests alone do not explain what was delivered.
- Include relevant non-code deliverables, such as API documentation.
  Do not imply they exist without session evidence.
- Distinguish implemented, tested, reviewed, merged, deployed, and observed
  states where the distinction affects the conclusion. Keep verification
  limits next to the result they qualify.
- Summarize checks collectively. Include exact commands, counts, hashes,
  agent names, and ancestry details only when needed to explain a material
  issue or explicitly requested.
- Link the primary deliverable when useful; avoid an artifact inventory.
- Do not describe excluded or unauthorized actions as unfinished obligations.
  Mention merge or deployment state when needed to explain availability.
- Never infer completion from plans, PR creation, or passing checks alone.
- Omit secrets, verification codes, routine tool calls, and process narration.
