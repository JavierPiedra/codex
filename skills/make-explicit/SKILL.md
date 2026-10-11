---
name: make-explicit
description: Run only when Javier explicitly invokes `$make-explicit` or `/make-explicit`. Rewrite selected response annotations, supplied text, or the immediately preceding assistant message for clarity, precise language, and explicit reasons, effects, and decisions. Never trigger from ordinary requests to clarify, edit, rewrite, proofread, or correct grammar.
---

# Make Explicit

Rewrite the text so the reader understands what is happening, why a change
is proposed, what it would do, and exactly what is needed from them.

## Target And Language

Use the first applicable target: response annotation selections, text supplied
with the invocation, or the immediately preceding assistant message in full.
Process multiple annotations in their order and preserve required linkage.

Use the requested language; otherwise preserve the target's dominant language.
Default to English only when neither the target nor request establishes one.

## Rewrite For An Informed Decision

For each problem, proposed action, or decision, explain from the available
context:

- What happens today and what specific problem or unmet condition it causes.
- Who would change what, in which system or source of truth, and why that
  would address the problem.
- The material effects and scope, distinguishing units such as products and
  offers. Explain consequences of approving or deferring when established.
- What decision or input is needed and from whom.

Keep each reason beside its action. Distinguish technical necessity, external
requirements, and the author's preferred approach; do not present a preference
as indispensable. Labels such as "blocked", "preflight passed", or "the Goal
requires it" do not explain the underlying problem or purpose. Explain what
the evidence establishes; technical references support that explanation.

Use concrete, consistent language and correct grammar. Include conditions,
ordering, exceptions, and failure behavior only when they affect interpretation.
Use the shortest structure that conveys the necessary explanation; the reader
should not have to assemble it from scattered statements.

## Preserve Integrity

- Use only the target and supplied context. Do not inspect files, browse,
  run tools, execute proposed actions, or change Goal status.
- Preserve intent, scope, constraints, decisions, existing approvals and pending
  requests, uncertainty, tone, and formality. Do not invent facts, requirements,
  examples, permissions, next checks, schedules, or promised continuations.
- Distinguish observed facts, hypotheses, and unknowns. A recommendation is not
  a decision; preparation is not execution. Missing explanation is an
  information gap, not proof of an operational blocker.
- Resolve unclear wording when the context establishes its meaning. Otherwise
  identify missing information where it matters. Never choose between materially
  different interpretations on the user's behalf.
- Preserve established terms, code, commands, URLs, paths, identifiers, and
  quoted literals unless the user explicitly requests changing them.

## Close Blocked Goal Turns

When rewriting a blocked or incomplete Goal closing, make it self-contained.
Cover all applicable elements below, even if they fit in one paragraph:

1. **Result:** What was achieved and what remains unfinished. Distinguish
   prepared, tested, reviewed, published, merged, deployed, and observed states
   when relevant, and explain the practical limits of the evidence.
2. **Blocker:** The specific unmet condition, why it prevents the next action,
   and the evidence or stated rule establishing it. Separate an external
   party's pending action from a decision awaiting the user. Keep independently
   actionable work distinct from blocked work.
3. **Next action:** Who would do what, to which target, for what purpose and
   with what material effects. Explain dependencies only where they exist.
4. **Required input:** The concrete decision, information, access, or permission
   still needed. For permission, explain the established authority boundary
   requiring it and make the action reviewable. Preserve prior approvals;
   an unanswered request remains pending rather than becoming a new question
   each turn. If the user has nothing to do, say so and identify the next
   responsible actor or observable event.

Number independent decisions when useful. End with the actual next action,
unresolved request, or external event being awaited. Name the action and target;
a generic "may I continue?" or a numbered reference alone is insufficient.

## Return The Text

Return the complete replacement directly, without editorial headings such as
"Open ambiguities" or "Rewritten text", unless requested. Keep necessary
uncertainty within the rewritten text. If a material ambiguity prevents a
faithful rewrite, ask one focused question explaining how the answer changes
the action, scope, or consequences. Rewrite independent portions only when
useful and do not present a partial rewrite as complete.

Make only necessary edits when the original is already clear. Before returning
it, check: does it stand on its own, let the reader understand and answer the
actual decision, and preserve everything established without invention?
