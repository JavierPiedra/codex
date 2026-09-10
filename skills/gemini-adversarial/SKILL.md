---
name: gemini-adversarial
description: Run a read-only Gemini CLI challenge of a proposal, PRD, rollout, or technical plan only when explicitly invoked as $gemini-adversarial or /gemini-adversarial.
---

# Gemini Adversarial

This workflow is explicit-only. Generic requests for Gemini, dissent, or an
independent review do not invoke it.

Use Gemini as a bounded dissenting reviewer, never as an implementer or
decision-maker. Follow `$gemini-send` for consent, sanitization, and CLI mode.
Run one round by default; allow at most three only when Javier requests a
debate loop.

## Safety

- Use `gemini --approval-mode plan --skip-trust` and prohibit tools, edits,
  network actions, and file creation in the prompt.
- Exclude credentials, full `.env` files, customer data, private documents, and
  production logs.
- Do not create a council, task, branch, implementation, or authorization from
  Gemini's reply alone.

## Review

Give Gemini the proposal, constraints, and one decision under test. Choose one
relevant role such as skeptical maintainer, security critic, product
contrarian, or brand strategist. Require evidence-based claims labeled
`CONFIRMED`, `INFERENCE`, or `QUESTION`, using only supplied material.

Request exactly:

1. strongest hidden assumption;
2. up to five concrete objections tied to evidence;
3. smallest counter-proposal;
4. evidence that would falsify it; and
5. the one question a human owner must decide.

Independently verify material objections against the repository, contract, or
source evidence before recommending an action.

Prompt boundary:

```text
You are an adversarial reviewer. Challenge the proposal rather than seeking consensus. This is read-only: do not edit files, use tools, contact services, or treat your answer as authorization. Label every claim CONFIRMED, INFERENCE, or QUESTION using only the supplied material.
```
