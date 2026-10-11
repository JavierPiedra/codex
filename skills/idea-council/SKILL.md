---
name: idea-council
description: Run a read-only council of at least two specialist perspectives to discuss an idea, document, strategy, or way of working. Use when Javier asks for idea-council or a multi-agent discussion whose purpose is exploration, comparison, or judgment rather than feature implementation planning.
---

# Idea Council

Help Javier understand an idea, improve its framing, or compare possible
directions through distinct expert perspectives. A useful discussion may end
with a recommendation, alternatives, or a sharper open question; do not force
a product decision, roadmap, PRD, vote, or consensus.

## Scope and evidence

Keep source documents, repositories, and external systems read-only. Discuss
and produce the requested text in chat. Editing documents, saving artifacts,
creating tasks, installing profiles, or executing recommendations requires a
separate instruction covering that action.

Frame the topic, the question Javier wants to explore, relevant constraints,
and the desired outcome. Ask only when an unresolved assumption materially
changes the discussion. Reuse the available context; investigate only evidence
gaps or freshness that could change a contribution. Repository exploration is
conditional, not a mandatory phase.

Prepare a common evidence packet separating sourced facts, Javier's decisions,
interpretations, proposals, and unknowns. Preserve source pointers and dates
when they matter. State contradictions without merging them into certainty.

Follow applicable AGENTS.md and current orchestration rules. Before the first
agent operation, read:

- `/Users/javierpiedra/.codex/agent-model-routing.md`
- `/Users/javierpiedra/.codex/agent-orchestration.md`

## Model selection

For HR and every council or supporting subagent, use the strongest currently
available model for complex reasoning, with reasoning effort at least
`high`. Reassess availability at each invocation using the host's supported
models, capability descriptions, and Javier's latest applicable designation
of the best model. Do not hardcode model identifiers in this skill or infer
a capability ranking from version numbers or the routing table alone.

This skill's explicit best-model requirement overrides lower-capability
default routes. Pass the selected model and effort explicitly when supported;
verify that profile settings and inherited defaults do not select a weaker
model or effort below `high`. If a profile cannot accept that route, use its
unchanged role instructions in an eligible read-only assignment when supported.
Declare the selected route, and distinguish requested selection from runtime
metadata actually observed. If the required route or delegation is unavailable,
report the limitation instead of silently downgrading or simulating a council.
If the best-model designation remains materially ambiguous, resolve it with
Javier before delegation.

## Choose perspectives; HR is optional

Use at least two specialists with distinct contributions. Start with the
smallest useful council; add a role only when it covers a material judgment
that the others cannot. Choose expertise for the topic, without mandatory
engineering, product, or UX attendance. Prefer suitable existing profiles and
respect their actual remit and boundaries.

Invoke `council_hr` initially only when Javier explicitly requests HR.
Missing expertise alone does not activate it. Give HR the discussion target,
evidence packet, available profile definitions, and these requirements:

- Propose at least two specialist profiles and explain each one's distinct
  contribution, responsibilities, evidence needs, and boundaries.
- Prefer suitable existing profiles; describe missing profiles without
  installing them or broadening existing roles silently.
- Return the proposed roster for Javier's review, then stop; do not launch
  specialists or perform their substantive analysis.

HR does not count toward the minimum two specialists. After HR, pause for
Javier's approval of the roster before launching the council; reuse any
applicable approval already given. Without HR, the coordinator chooses the
perspectives directly within the requested discussion scope.

## Discuss and contrast

Launch one independent read-only subagent per selected perspective. Give each
the same evidence packet and question, a bounded contribution, and no other
specialist's initial opinion. Do not authorize child delegation.

Ask each specialist for its substantive reading, useful alternatives,
supporting and conflicting evidence, relevant consequences and tradeoffs,
and uncertainties or questions that could change its view. Scale the response
to the topic. Do not manufacture objections or questions to fill a template,
and do not treat expert interpretation as verified fact.

The coordinator identifies agreements, differences, and which disagreements
would change the recommendation. Use a focused follow-up with the same
specialists when genuine disagreement, new evidence, or Javier's answers
would materially improve the discussion. Share the relevant competing
arguments and exact answers; request a revised position and its reason.
Do not require a debate round when the first contributions are sufficient.

Merge duplicate questions and ask only those that change the conclusion or
next exploration. Batch one to three when useful, explain the practical
tradeoff, and keep dependent conclusions pending until required answers arrive.
Silence does not supply a factual answer or approval.

## Synthesize

Return a concise account of:

- The question discussed and the useful perspectives.
- What the evidence supports and what remains interpretation or proposal.
- Agreements and substantive disagreement, including any changed positions.
- A recommendation or viable alternatives, with their reasons and limits.
- Unresolved questions or the evidence that would make further discussion useful.

Adapt the format to Javier's request. Preserve minority arguments that affect
the conclusion; do not count votes or invent consensus. A discussion can remain
open without declaring failure or forcing a build/no-build verdict. State any
missing perspective or evidence plainly, and leave implementation or document
edits to a separately authorized task.
