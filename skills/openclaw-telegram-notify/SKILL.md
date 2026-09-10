---
name: openclaw-telegram-notify
description: Send a concise Telegram message to Javier through the local OpenClaw CLI when he explicitly requests it or an active PPM subscription authorizes a blocker, failed gate, milestone, or terminal alert.
---

# OpenClaw Telegram Notify

Send through Javier's configured Telegram bot to chat `434830632`.

## Authorization

An individual message requires Javier's explicit request. A PPM may send
standing notifications only after Javier explicitly opts in or subscribes to
that channel; record the scope and duration when supplied, then reuse the
subscription until Javier revokes or it expires. Do not infer subscription
from a generic monitoring request, a managed session, or a previous unrelated
message. Read-only or audit-only work excludes sending unless Javier
explicitly authorizes a notification for that audit; an unrelated standing
subscription does not expand the audit's scope.

## Deterministic delivery

Use the notifier for a normal alert:

```bash
/Users/javierpiedra/.codex/skills/openclaw-telegram-notify/scripts/notify-javier.sh \
  --message "<concise message>" \
  --json
```

Run the notifier outside the restricted Codex sandbox from the first attempt.
It writes OpenClaw state under `~/.openclaw/state` and connects to the local
gateway at `127.0.0.1:18789`; use the approved escalated execution path for
that local write and connection.

Treat delivery as proven only when JSON contains `payload.ok: true` and a
`messageId`. Do not expose bot tokens or inspect secret configuration. For a
PPM blocker, include the short UUID, live title and `codex://threads/<uuid>`
link, blocked objective, exact action needed, safe work that can continue, and
one stable blocker ID. Do not send routine progress, acknowledgements,
unchanged waits, or duplicate events.

Read [telegram-options.md](./references/telegram-options.md) only for files,
media, buttons, polls, replies, silent messages, model-generated responses, or
delivery diagnostics. Prefer direct `message send` for deterministic alerts;
use `openclaw agent` only when Javier asks OpenClaw to reason or generate the
delivered text.

## Safety and failure

- Do not turn a Telegram button callback into production approval unless the
  governing workflow authenticates and accepts that channel.
- Verify attached paths and contents. Never attach credentials, environment
  files, cookies, tokens, payment data, or raw sensitive logs.
- Do not create polling loops. React to an authorized event.
- If delivery fails, report the failure in Codex and do not claim notification.
