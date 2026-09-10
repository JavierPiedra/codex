---
name: make-explicit
description: Run only when Javier explicitly invokes `$make-explicit` or `/make-explicit`. Review and rewrite a selected response annotation, explicitly supplied text, or—by default—the immediately preceding assistant message for explicitness, clarity, precise language, and correct Spanish or English grammar. Default to English only when the target language is not established. Never trigger from ordinary requests to clarify, edit, rewrite, proofread, or correct grammar.
---

# Make Explicit

Rewrite supplied text so a careful reader can derive one reasonable meaning
without silently choosing unresolved product, technical, or operational policy.

## Select The Target

Use the first applicable target:

1. Text selected in a response annotation.
2. Text explicitly quoted or pasted with the invocation.
3. The immediately preceding assistant message in full.

When several response annotations are supplied, process each selection in
annotation order. Preserve any annotation linkage required by active runtime
instructions.

Do not inspect files, browse, run tools, or verify external facts. Work only
from the target text and context already supplied by the user.

## Select The Language

- Rewrite Spanish text in Spanish and English text in English.
- For mixed text, preserve the dominant language unless the user requests a
  target language.
- Default to English only when neither the target nor the request establishes
  a language.
- Preserve established product terms, identifiers, paths, code, and quoted
  literals in their original language and form.

## Review The Text

Check whether the text explicitly identifies every applicable element:

- actor;
- action;
- object or target;
- preconditions;
- ordering and priority;
- allowed and prohibited behavior;
- exceptions;
- failure behavior;
- observable result;
- unresolved decisions.

Also correct:

- ambiguous pronouns or referents;
- vague verbs and abstract nouns;
- inconsistent terminology;
- unnecessary qualifiers and repetition;
- spelling, agreement, syntax, punctuation, and idiom.

Do not add detail merely to make the text longer. Add only what is already
established by the target or supplied context.

## Preserve Semantic Integrity

- Preserve the original intent, scope, constraints, decisions, uncertainty,
  tone, and level of formality.
- Never invent facts, requirements, priorities, examples, exceptions, or
  approvals.
- Never resolve a material ambiguity on the user's behalf.
- When two interpretations remain possible, state the unresolved ambiguity
  before the rewrite and phrase the rewrite so it does not conceal it.
- Preserve code blocks, commands, URLs, paths, field names, identifiers, and
  quoted literals verbatim unless the user explicitly asks to edit them.
- Do not turn a recommendation into a decision or a tentative statement into a
  confirmed fact.

## Rewrite

Prefer concrete sentences that name the actor, action, condition, and
consequence. Use one term for one concept. Make precedence and failure behavior
explicit when they affect interpretation.

Return:

1. `Open ambiguities` only when material ambiguity remains, with one concise
   bullet per unresolved decision.
2. `Rewritten text` containing the complete replacement text.

If the user requests only the replacement, return only the rewritten text.
If the original is already explicit and correct, make only necessary edits.

## Final Check

Before responding, verify that the rewrite:

- has one reasonable interpretation wherever the source provides enough
  information;
- exposes rather than hides unresolved decisions;
- preserves every established constraint;
- contains no new facts or decisions;
- uses correct grammar in the selected language;
- can replace the original text without additional explanation.
