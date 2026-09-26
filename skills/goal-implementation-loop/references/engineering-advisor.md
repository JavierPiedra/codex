# Engineering advisor consultation protocol

Read this reference for the engineering council included by default in a
`goal-implementation-loop` Goal, unless Javier explicitly excludes it.

## Assignment and continuity

Use `goal_engineering_advisor` with `gpt-6-astra` / `high`, its read-only
boundary, and disabled delegation. The profile at
`~/.codex/agents/goal_engineering_advisor.toml` owns its technical and adversarial
mandate; preserve its advisory authority and read-only boundary in the
assignment. Follow the applicable agent lifecycle policies and reuse the same subagent throughout the Goal.
If the profile is unavailable, report that limitation instead of silently
substituting another role or model; continue independent authorized work.

Provide the validated Goal, authoritative user decisions and approved amendments,
acceptance criteria, exclusions, governing contracts, current execution plan,
relevant evidence, and any explicit time or resource limits. Supply source
pointers sufficient for targeted inspection. The orchestrator retains planning,
assignment, and delivery responsibility. The consultant advises the orchestrator;
Daybreak retains its independent review role.

## Progress reports

Report what the orchestrator intends to do and obtain the council's direction
before assigning the first implementation. Consult at meaningful milestones,
before a material approach change or retry after failure, and before claiming
completion. Send an
incremental report containing:

- Acceptance progress and supporting evidence, distinguishing reported results
  from inspected or observed facts.
- Changes since the last consultation, blockers, and outstanding objections.
- Available elapsed-time, attempt, tool, agent, token, or cost evidence; identify
  unknown usage and do not invent budgets or measurements.
- The proposed next step, its expected observable result, and how it advances
  the accepted Goal or reduces consequential uncertainty.

Keep reports proportional to the decision. Do not forward every tool result,
request unchanged status, poll the consultant, or create another tracking system.
Resume the same subagent with the next substantive update.

## Objections and decisions

Resolve objections affecting the next dependent action before proceeding with
that action; continue independent authorized work meanwhile. Record the smallest
justified correction or an evidence-backed reason for rejecting the advice.
Maintain whether each material objection is resolved, rejected with justification,
or open. Consensus is not required; rejection cannot authorize a contract
violation. Revisit settled points only when new evidence warrants it.

Escalate to Javier when resolution requires changing the contract, authority,
or an explicit resource limit. A change of execution plan that preserves the
contract does not itself require escalation. The consultant has no veto and
cannot authorize mutations, weaken required verification, or declare the Goal
abandoned. A recommendation to stop an approach remains subject to the Goal's
existing authorization and outcome rules.

Before closure, provide acceptance, review, and verification evidence and resolve
material objections affecting completion. Include material consultant findings
and their disposition in the existing compact final outcome. Do not add separate
approval gates or prolong satisfied work for additional polish.
