---
name: write-goal
description: Draft, review, repair, and validate Codex Goals as evidence-based completion contracts. Use only when the user explicitly invokes `$write-goal` or `$goal-implementation-loop`, which declares this skill as a required dependency. Never activate it from model judgment alone, and never use it to execute work or start Goal mode.
---

# Write Goal

Produce a reviewable, validated Goal contract. This skill never calls Goal
tools or executes the underlying work.

## Invocation Boundary

This skill has two authorized callers:

- **Direct:** Javier explicitly invokes `$write-goal`. Return the contract for
  review; do not start Goal mode or begin the underlying work.
- **Goal implementation loop:** Javier explicitly invokes
  `$goal-implementation-loop`, whose public contract requires this skill as its
  first step. Return the validated contract to that workflow. The caller alone
  decides whether to request authorization or start Goal mode.

Do not activate this skill merely because the model considers it relevant.
Keep `allow_implicit_invocation: false`.

## Workflow

1. Read [references/goal-authoring-guide.md](references/goal-authoring-guide.md).
2. Identify whether the caller is direct or `$goal-implementation-loop`.
3. For direct use, classify the request as one of:
   - normal prompt
   - `/plan`
   - `/goal`
   - Skill
   - `AGENTS.md`
   - scheduled task
   - `codex exec`
4. Recommend `/goal` in direct use only when all are true:
   - the desired outcome is observable and verifiable;
   - multiple action-check-adjust cycles are likely;
   - the next action depends on intermediate evidence; and
   - one coherent objective belongs to the current thread.
5. When called by `$goal-implementation-loop`, treat Javier's explicit skill
   selection as the `/goal` decision. Author the shortest valid Goal even for a
   small bounded request. Do not redirect it to a normal prompt merely because
   the work is linear.
6. Extract or infer the objective, evidence, acceptance criteria, constraints,
   boundaries, initial context, iteration policy, checkpoint cadence, success
   stop, blocked stop, budget stop, safety limits, observability, assumptions,
   and final output.
7. Ask at most one focused question only when a missing fact materially changes
   the tool choice or completion criteria. Otherwise state a reasonable
   assumption and continue.
8. Draft the Goal using [assets/goal-template.md](assets/goal-template.md). Scale
   its length to the risk and complexity; omit irrelevant sections without
   omitting required semantics.
9. Validate the draft semantically and, when the draft is available as plain
   text, run:

   ```bash
   python3 scripts/validate_goal.py < goal.txt
   ```

10. Repair validation errors before returning the draft. Surface warnings that
    require user judgment.

## Redirections

For direct use:

- Redirect calendar recurrence to a scheduled task.
- Redirect an undefined finish line or unresolved target architecture to
  `/plan`.
- Redirect one small, linear action to a normal prompt.
- Redirect a reusable procedure to a Skill.
- Redirect standing repository guidance to `AGENTS.md`.
- Redirect CI or scripted non-interactive work to `codex exec`.

When called by `$goal-implementation-loop`, do not apply the small-action
redirection. Stop and return the precise missing decision only when no valid,
thread-scoped Goal can be authored.

## Validation Requirements

Require:

- one principal observable outcome;
- named tests, benchmarks, artifacts, logs, sources, or review surfaces;
- acceptance criteria that can be marked `pass`, `fail`, or `blocked`;
- explicit non-regression constraints and work boundaries;
- an event-based checkpoint cadence, never calendar scheduling;
- distinct success, blocked, and budget exits;
- safety limits for external, destructive, production, credentialed, or
  irreversible actions; and
- a short iteration record and an evidence-based final report.

Reject success based only on plausibility, effort, token use, or elapsed time.
Treat budget exhaustion as a stop condition, not completion.

## Output

For direct use, return in Javier's language:

1. `Tool fit`: recommendation and concise rationale.
2. `Assumptions`: only material assumptions.
3. `Missing critical input`: omit when empty.
4. A copy-ready `/goal` block.
5. `Validation`: pass/warning status for outcome, evidence, constraints,
   boundaries, iteration, stop conditions, safety, and observability.
6. `Warnings`: risks or suggested scope cuts; omit when empty.

For `$goal-implementation-loop`, return the validated Goal contract,
assumptions, and unresolved warnings to the caller without starting Goal mode or
performing mutations.

Keep the answer compact. Do not claim that a well-written Goal grants
permissions, bypasses sandboxing, or makes unsafe work safe.
