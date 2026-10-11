---
name: show-task-progress
description: Show or refresh the Codex task-progress widget. Use when the user asks to show task progress, display progress, or invoke $javier:show-task-progress.
---

# Show Task Progress

Call `update_plan` to show the current task progress in the Codex UI.

- Reuse the existing plan when one exists; otherwise create 2–4 concrete steps.
- Mark completed work accurately and keep only one step `in_progress`.
- Do not modify files or external systems.

If `update_plan` is unavailable on this host, report that limitation and
show the current steps in chat. Do not claim a widget was displayed.
