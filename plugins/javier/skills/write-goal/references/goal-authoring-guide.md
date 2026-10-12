# Goal authoring guide

## Choosing the mechanism

A Goal is a persistent objective for one thread. It is useful when the finish
line is verifiable and reaching it may take adaptive action/check cycles.

| Mechanism | Use when |
|---|---|
| Normal prompt | One small, concrete, linear action or a single answer |
| `/plan` | A material target, outcome, or constraint still needs deciding |
| `/goal` | One durable objective needs evidence-based continuation |
| Skill | The requested deliverable is a reusable procedure |
| `AGENTS.md` | Guidance should apply across repository tasks |
| Scheduled task | The agent should start or repeat by clock or calendar |
| `codex exec` | Execution belongs in a script or CI |

A task about a scheduled business process is not necessarily a request to
schedule the agent. Likewise, uncertainty about implementation does not prevent
a Goal when the outcome and verification are clear. A research Goal may aim to
resolve uncertainty through a report; it need not presuppose the answer.

The implementation-loop caller has already selected Goal mode. Do not redirect
its small tasks to normal prompts.

## Sufficient evidence

Keep the outcome, target, verification, and material limits clear. These are
semantic requirements, not mandatory headings.

- For behavior, describe the relevant action, expected result, and forbidden
  effects. Include negative cases where they protect a concrete requirement.
- For a metric, use the agreed benchmark, conditions, threshold, and tolerance.
  Do not invent a numeric target to make vague improvement appear measurable.
- For an artifact or subjective result, name its audience, required content,
  observable use, or agreed rubric. A command or binary test is not always the
  appropriate evidence.
- For research, distinguish confirmed findings, approximations, unsupported
  claims, and unavailable evidence. An uncertainty report can be complete when
  that is the requested deliverable; it cannot replace promised exact proof.
- Reference accessible, authoritative context. Embed the necessary information
  when a reference will not be available to the executing thread.

Tests and review must cover the acceptance requirement they support. Compilation,
a generated report, or green CI alone does not prove a broader runtime outcome.

## Add operating detail when it changes execution

| Detail | Include when |
|---|---|
| Initial references | They contain necessary requirements or prior decisions |
| Plan and milestones | Dependencies or complexity make progress hard to track |
| Persistent notes | Continuations or handoffs need recoverable decisions and evidence |
| Experiment policy | Trials need a defined comparison and retention criterion |
| Blocker condition | Missing access, inputs, review, or a decision prevents dependent work |
| Budget | Javier or an applicable instruction supplied a concrete limit |
| Approval or recovery step | The actual action and its existing authority require it |

Use meaningful events for checkpoints, not calendar recurrence. Reuse existing
progress artifacts when they fit; do not require a new file per Goal or a log
entry per tool call. Do not copy another harness's agent topology or restart
policy into a Goal.

Scope should protect the requested boundaries without prescribing a solution
that cannot reach the outcome. A materially broader target requires a decision,
not silent expansion.

## Authority and lifecycle

The authoring skill specifies the work and how to assess it. The executing
workflow and current tools control Goal activation, continuation, and status.

Do not encode a fixed blocked-state turn count or claim that prose limits are
native runtime controls. A missing permission stops the dependent action; it
need not stop unrelated authorized work or immediately change the Goal state.
Report the impediment and required input without redefining success.

Retain budgets that were requested, and distinguish exhaustion from completion.
Do not introduce a default budget or reapproval of actions already authorized.
Recovery, rollback, and compatibility are task decisions, not automatic additions.

## Evidence behind this guidance

Consult these when revising the skill or checking a platform claim, not on
every invocation. Reviewed for this rewrite on 2026-10-12; live tool contracts
take precedence over historical documentation.

- [OpenAI: Using Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)
  describes persistent objectives and evidence-based completion.
- [OpenAI: Codex best practices](https://developers.openai.com/codex/learn/best-practices)
  separates task context from durable instructions and conditional planning.
- [Anthropic: Harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps)
  reports model-dependent changes to useful scaffolding; it is not a Codex benchmark.
- [OpenAI: Skill evaluations](https://developers.openai.com/blog/eval-skills)
  describes evaluating observable behavior, rather than trusting a plausible draft.

These sources do not establish an optimal Goal length or prove this skill's
effectiveness on every model.
