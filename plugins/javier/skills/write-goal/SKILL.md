---
name: write-goal
description: Draft, review, and repair verifiable Codex Goal contracts when Javier explicitly invokes `$javier:write-goal` or its required caller `$javier:goal-implementation-loop`. Authoring only; never start Goal mode or execute the described work.
---

# Write Goal

Produce the shortest contract that preserves the requested outcome, its evidence,
and material limits. Review its meaning before returning it; authoring is not
proof that the work can or has been completed.

## Invocation and ownership

- **Direct:** Javier invokes `$javier:write-goal` to author a Goal. Return it for
  review without activating it.
- **Caller:** `$javier:goal-implementation-loop` requires this skill first. Return
  the reviewed contract and unresolved material questions to that caller, which
  alone owns activation and execution. Its explicit selection settles the choice
  of Goal even for a small linear task.
- A request to inspect or edit this skill is about the skill itself, not an
  instruction to draft or activate a Goal.
- Keep `allow_implicit_invocation: false`. Do not call Goal tools or perform the
  work described in a draft.

## Authoring

1. Identify the caller and read only the applicable instructions and task
   references needed to establish the outcome, target, authority, and evidence.
   Reuse settled decisions and existing authorization.
2. For direct use, recommend a Goal when one coherent, verifiable objective
   should persist across turns and the next action is likely to depend on
   intermediate evidence. Prefer a normal prompt for one small linear action,
   or `/plan` when an unresolved decision prevents defining the outcome.
   Read the [authoring guide](references/goal-authoring-guide.md) when routing,
   evidence, or operating limits need clarification.
3. Ask a focused question before choosing between materially different targets,
   outcomes, authority, or effects. Do not invent those decisions to finish a
   draft. State only material assumptions; leave routine implementation choices
   to the executing workflow.
4. Draft an observable outcome with acceptance evidence and material boundaries.
   Identify the artifact, behavior, metric, or review rubric that distinguishes
   completion from a plausible approximation. Use the
   [template](assets/goal-template.md) when helpful; its layout is optional.
5. Add context, milestones, progress records, experiment rules, dependencies,
   or specific blocker handling only when needed for this task. Reference an
   existing plan or governing source instead of duplicating it. Preserve budgets
   and limits actually supplied; do not invent tokens, durations, or retry caps.
6. Review the contract semantically using the checks below. Repair unsupported
   requirements, ambiguous completion criteria, and missing boundaries before
   handing it back.
7. Measure the exact final copy-ready Goal with a deterministic tool before
   returning it, including to the loop caller. It must not exceed **4,000
   characters**, including the `/goal` prefix, spaces, and line breaks, but
   excluding Markdown fences and surrounding commentary. Count conservatively
   in UTF-16 code units (for example, JavaScript `text.length`); do not estimate
   from tokens or words. Recount after edits. If it exceeds the limit, remove
   repetition and move supporting detail to accessible references while keeping
   the outcome, acceptance evidence, and material boundaries in the Goal.
   Never truncate requirements just to fit.

Apart from the character ceiling, do not impose a target length, a fixed number
of questions, or a universal checkpoint/logging format. If direct use fits
another mechanism, give that recommendation and its reason without manufacturing
a Goal. For the loop caller, return the precise missing decision only when a
valid contract cannot be written.

## Semantic review

Check the contract against the request and authoritative context:

- Does it preserve every required result without adding adjacent work or
  silently narrowing success?
- Can each acceptance condition be assessed with appropriate evidence? Name
  known checks or review surfaces; do not invent commands, datasets, thresholds,
  or prerequisites that have not been established.
- Are target, scope, non-regression requirements, and action authority clear
  enough to proceed without guessing? Preserve existing authorization and any
  retained action-time checkpoint; a Goal grants no additional permissions.
- Can execution adapt its approach without changing the acceptance criteria?
  Missing evidence, spent effort, or an exhausted budget is not completion.
- Are genuine unresolved dependencies distinguished from ordinary uncertainty?
  Stop dependent actions when necessary and identify what would unlock them,
  while allowing independent authorized progress. Defer formal lifecycle
  transitions to the current Goal tool contract.

This is a reasoning check, not a keyword test or a guarantee of execution.
Do not require particular phrases to express evidence, constraints, or blockage.

## Output

Respond in Javier's language. When a Goal fits, return a copy-ready `/goal`
block plus only material assumptions, unresolved questions, or warnings.
Explain tool fit when it changes the recommendation; omit empty sections and
generic pass/warning scorecards.

For the loop caller, return the semantically validated contract with any
remaining material assumptions or warnings. Do not reproduce its issue, branch,
agent, review, or PR workflow here; preserve applicable obligations by reference
or as acceptance requirements without taking over execution.
