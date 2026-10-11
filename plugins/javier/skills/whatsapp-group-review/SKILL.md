---
name: whatsapp-group-review
description: Review local WhatsApp Desktop group chats on macOS in read-only mode and extract pending tasks, blockers, decisions, rules, and durable knowledge candidates. Use when Javier asks to review, audit, summarize, or extract action items from a local WhatsApp group chat, especially the Conexión Farcoyo - Rappi group.
---

# WhatsApp Group Review

When running a bundled helper, resolve its path from this installed skill
directory and use the `python` path in `{codex_home}/javier-paths.toml`.
Quote executable and file paths for the active shell.

Use this skill to review a local WhatsApp Desktop group chat in read-only mode.

## Defaults

This data source is available only on macOS. On native Windows, report that
the Windows source has not been defined and do not search for, infer, or
substitute another WhatsApp database. Javier chose to retain the macOS reader
while defining the Windows source separately.

- Group: `Conexión Farcoyo - Rappi`
- Database: `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite`
- Range: last 7 days unless Javier specifies another range
- Time zone: `America/Mexico_City`

## Rules

- Keep the workflow read-only.
- Use SQLite `mode=ro` only.
- Never modify WhatsApp files.
- Never export attachments unless Javier explicitly asks.
- Do not store chat content in this skill.
- Do not write memory from the chat. Only list memory candidates in the response.
- If multiple groups match, stop and ask Javier which group to use.
- Extract and review messages chronologically.
- Treat newer messages as more authoritative than older messages.
- Mark a task as pending only when there is no later evidence that it was completed, cancelled, or replaced.

## Export

Run the bundled exporter only when Javier asks to review a chat:

```text
<shared-python> <installed-skill>/scripts/export_whatsapp_group.py
```

Common options:

```text
<shared-python> <installed-skill>/scripts/export_whatsapp_group.py --group "Conexión Farcoyo - Rappi" --days 7
```

If the script returns `{"status":"ERROR","code":"MULTIPLE_GROUPS",...}`, ask Javier which listed `chat_pk` or group name to use before continuing.

## Review

Read the exported JSON and infer the current state from the messages:

- Prefer direct assignments, explicit requests, commitments, due dates, and unanswered questions for `pendientes`.
- Remove a pending item if later messages show it was done, cancelled, superseded, or no longer needed.
- Use `bloqueos` for external dependencies, missing access, missing data, operational stops, or unresolved decisions blocking work.
- Use `decisiones / reglas` for durable operating rules, policy changes, process decisions, or repeated corrections.
- Use `conocimiento candidato` for facts that may be worth saving later, but do not save them unless Javier explicitly asks.

Return this shape:

```yaml
estado: OK

grupo:
- name:
- chat_pk:
- range reviewed:
- message count:

pendientes:
- task:
  owner:
  evidence timestamp:
  why still pending:
  next action:

bloqueos:
- blocker:
  owner:
  evidence timestamp:

decisiones / reglas:
- rule:
  evidence timestamp:

conocimiento candidato:
- fact:
  why it matters:

errores exactos:
- none
```

For failures, return `estado: ERROR`, include any group metadata available, leave unavailable sections empty, and put exact script errors under `errores exactos`.
