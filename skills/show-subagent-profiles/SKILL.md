---
name: show-subagent-profiles
description: "Show the actual Codex subagent profiles installed in the local agents directory."
---

# Show Subagent Profiles

When invoked:

1. List the `.toml` files directly under `/Users/javierpiedra/.codex/agents/`.
2. Read each listed profile file. Treat these files as the source of truth; do not read `/Users/javierpiedra/.codex/agent-model-routing.md`.
3. Show every profile with its `name`, `description`, `model`, `model_reasoning_effort`, `sandbox_mode`, and `[agents].enabled` value.
4. For an optional field absent from a profile, report `inherited` instead of inventing a value.
5. Label the output `Configured profiles`.
6. Add: `These are installed profile definitions, not proof of live runtime availability.`
7. If the agents directory is unavailable or contains no `.toml` files, report that clearly. Do not invent entries or spawn agents.
