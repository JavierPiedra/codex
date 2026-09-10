---
name: btw
description: Send an additive, non-interrupting steering note to active delegated work. Use only when Javier explicitly invokes "$btw".
---

# By the way

Treat the user's text as an additive steering note, not a task replacement.

1. Preserve the active task and execution path.
2. If a relevant delegated agent is active, send the note with `send_message`.
3. Do not use `interrupt_agent`, `followup_task`, or a tool call that triggers a new agent turn.
4. If no relevant delegated agent is active, acknowledge the note briefly and apply it only at the next natural decision point.
5. Do not create a plan, edit files, or perform provider actions solely because of the note.

Keep the message concise, prefix it with `Non-interrupting steering note:`, and preserve the user's meaning. Do not claim the note has changed work until the receiving agent confirms or reaches a decision point.
