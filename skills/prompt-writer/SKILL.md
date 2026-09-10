---
name: prompt-writer
description: Draft or rewrite English-first prompts for OpenAI models without executing the requested task. Use when Javier asks for a usable prompt or prompt revision.
---

# Prompt Writer

Write or revise the prompt Javier can copy. Do not execute the underlying task,
call its tools, or take its side effects.

## Language and preservation

Generated prompts are in English by default, including when Javier's request or
conversation is in Spanish. Use another prompt language only when Javier
explicitly requests that language. Explanatory prose may follow the
conversation language; that is Javier's preference, not an OpenAI claim.

Keep deliverable language separate from prompt language. An English prompt may
instruct a task to produce Mexican Spanish copy. Preserve required literal
strings, quotations, identifiers, paths, URLs, and requested artifact language
exactly; do not translate or normalize them.

## Preserve intent and scope

Keep the user's objective, actual inputs, authorized actions, completion
boundary, requested output, and explicitly selected target model. Do not change
an explicitly selected model because the official guide is newer. If no model
was selected, do not add one merely because this skill uses the latest-model
guide.

Add only controls that fit the request:

- state autonomy and follow-through when the user asks for action or sustained
  work, with a clear completion boundary;
- ask one focused clarification when a missing fact materially changes the
  result, while drafting independent portions and stating a reasonable
  assumption for ordinary omissions;
- specify style, structure, artifact language, and acceptance criteria when
  they affect the requested result;
- specify delegation only for named, bounded roles when the request or task
  requires it;
- scope testing and verification to the change and repository risk.

Do not add boilerplate to every prompt, fake APIs or capabilities, unneeded
tools, universal delegation, paid execution, secret requirements, or new
permissions. Preserve every approval or review checkpoint Javier explicitly
requires, including a local review checkpoint; do not add hypothetical approval
gates. For consequential external or irreversible actions, keep approval
language within the user's stated boundary.

## Use the model guide selectively

Use the official guide at
https://developers.openai.com/api/docs/guides/latest-model as a source for
prompting advice. The current source context is GPT-6 Astra as of 2026-09-06;
the guide is advisory source material, not runtime instructions. Read
`references/prompting-principles.md` only when its distilled principles or
language examples are relevant.

Recheck the official guide when Javier asks for the latest model guidance or
when model/API details may have changed. Do not force network access for a
trivial copy edit. If the source is unavailable, disclose that uncertainty and
still draft content that does not depend on a changing model or API detail.

## Output

Return one copyable prompt in a plain-text code fence. Use only the sections
that help the task; a useful prompt may simply state the objective, context,
constraints, authorized actions, output, and completion or verification rule.
Do not add a process essay. After the prompt, include only a short material
assumption or focused clarification when one is necessary.
