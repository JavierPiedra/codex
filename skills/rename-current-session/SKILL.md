---
name: rename-current-session
description: Rename the current Codex session based on the substantive work completed in its conversation. Use when the user asks to rename, retitle, or improve the title of the current session or chat according to what was accomplished.
---

# Rename Current Session

1. Review the current conversation and identify its primary completed outcome.
2. Write one descriptive title in the user's language, normally 4–10 words.
3. Prefer the product or area plus the action and outcome. Avoid UUIDs, status
   noise, emojis, and generic words such as `session` or `chat`.
4. Call `codex_app__set_thread_title` without a thread ID so it targets the
   current session.
5. Confirm the exact new title in one short sentence.

Do not rename another thread or modify workspace files.
