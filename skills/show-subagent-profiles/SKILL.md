---
name: show-subagent-profiles
description: "Show all configured Codex subagent profiles from the local routing policy."
---

# Show Subagent Profiles

When invoked:

1. Read `/Users/javierpiedra/.codex/agent-model-routing.md`.
2. Show every routing-table row with its assignment, model, reasoning, and topology.
3. Label the output `Configured profiles`.
4. Add: `These are configured routes, not proof of live runtime availability.`
5. If the file is unavailable, report that clearly. Do not invent entries or spawn agents.
