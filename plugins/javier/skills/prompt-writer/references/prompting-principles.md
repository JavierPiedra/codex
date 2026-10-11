# Prompting principles

Source: [OpenAI latest-model guide](https://developers.openai.com/api/docs/guides/latest-model), retrieved 2026-09-06 for GPT-6 Astra. This is a compact reference, not a copy of the guide and not runtime policy.

- State the intended follow-through and completion boundary when the task asks
  for sustained work. Ask only when missing input could materially change the
  result; use reasonable assumptions for ordinary omissions.
- Make priority, scope, output, and style explicit when they matter. Astra can
  be detailed and highly responsive to instruction files, so remove conflicting
  or irrelevant prompt rules.
- Mention delegation when a workflow needs it, with named bounded roles. Do
  not require delegation for every task.
- Match verification to the change and risk. Do not expand a small edit into a
  broad test campaign without a reason.

## Language acceptance examples

1. Request: “Escribe un prompt para mejorar el texto de checkout en español
   mexicano.” No prompt language is specified. Output an English prompt that
   preserves Mexican Spanish as the checkout copy language.
2. Request: “Dame el prompt en español para revisar este flujo.” The explicit
   language request overrides the default; output the prompt in Spanish.
3. Request includes the literal identifier `PUBLIC_PRODUCT_LISTING_CHANGED@1`
   or the quote `AWR-502`. Keep each exact string in the generated prompt,
   even when the surrounding prompt is translated.
