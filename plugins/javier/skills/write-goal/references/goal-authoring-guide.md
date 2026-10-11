# Goal authoring guide

## Tool selection

| Mechanism | Choose when |
|---|---|
| Normal prompt | One small, concrete, linear action |
| `/plan` | The target, scope, or constraints are not settled |
| `/goal` | A verifiable outcome requires adaptive action-check-adjust cycles |
| Skill | A procedure or format should be reused across tasks |
| `AGENTS.md` | Guidance must apply automatically inside a repository |
| Scheduled task | Work starts or repeats by clock or calendar |
| `codex exec` | Work runs non-interactively in a script or CI pipeline |

A Goal is thread-scoped persistent state and a completion contract. It is not global memory, repository policy, or a scheduler. A Skill defines a reusable method; a Goal defines the specific result for the current thread.

## Required contract

Write one observable final state, then define:

- **Evidence:** current tests, benchmarks, artifacts, logs, sources, screenshots, or review criteria that prove the outcome.
- **Acceptance criteria:** binary or quantitative conditions. For metrics, name the dataset or benchmark, threshold, repetitions, and tolerance when relevant.
- **Constraints:** behavior, compatibility, quality, or data that must not regress.
- **Boundaries:** permitted files, repositories, tools, data, environments, and external systems.
- **Initial context:** issues, plans, documents, logs, or source files to inspect first.
- **Iteration policy:** how to test each material change, retain or discard it, and choose the next attempt from evidence.
- **Checkpoint cadence:** events such as after each meaningful change or benchmark run, not times such as every Monday.
- **Stops:** success, genuine blockage, and budget exhaustion must be separate outcomes.
- **Safety:** require minimum access, dry runs, rollback planning, and explicit approval before external or irreversible actions when applicable.
- **Observability:** record hypothesis, action, evidence, result, decision, and next action briefly.
- **Final output:** identify the report or artifact and the evidence it must contain.

## Stop conditions

Mark complete only when every acceptance criterion has current evidence. If blocked, report attempts, evidence, precise blocker, best state reached, remaining risk, and the input or permission needed. If budget is exhausted, stop substantive work and report progress; never reinterpret exhaustion as success.

## Anti-patterns

Repair or redirect:

- vague activities such as “improve,” “clean up,” or “investigate” without a final observable state;
- unrelated backlog items grouped into one Goal;
- no named verification surface;
- unrestricted scope such as “everything” or “all repositories”;
- rigid step lists that prevent adaptation to evidence;
- infinite continuation such as “never stop”;
- calendar recurrence inside a Goal;
- disabling tests, assertions, security controls, or approvals as a route to success;
- production, secrets, deployment, deletion, or destructive changes without explicit limits and approval stops;
- subjective criteria without a rubric or review surface;
- describing an approximation as an exact reproduction.

## Length heuristic

- Simple quantitative Goal: roughly 30–80 words.
- Normal engineering Goal: roughly 80–180 words.
- Research or high-risk Goal: roughly 150–300 words.

These are authoring heuristics, not platform limits. Prefer the shortest contract that makes completion auditable without inventing missing facts.
