# Telegram delivery options

Use `/Users/javierpiedra/.codex/skills/openclaw-telegram-notify/scripts/notify-javier.sh`
for direct delivery. It fixes the channel and Javier's chat ID while passing
the remaining `openclaw message send` flags through unchanged. The shortened
`scripts/notify-javier.sh` form below refers to that absolute script.

## Text and delivery controls

```bash
scripts/notify-javier.sh --message "Texto" --json
scripts/notify-javier.sh --message "Aviso sin sonido" --silent --json
scripts/notify-javier.sh --message "Respuesta" --reply-to <message-id> --json
scripts/notify-javier.sh --message "Mensaje fijado" --pin --json
scripts/notify-javier.sh --message "Validar payload" --dry-run --json
```

`--silent` is supported by Telegram. Use `--reply-to` to preserve context.
Pin only when Javier asks or the alert must remain visible.

## Files and media

```bash
scripts/notify-javier.sh --message "Adjunto evidencia" --media /absolute/path/report.pdf --json
scripts/notify-javier.sh --message "Imagen sin compresión" --media /absolute/path/diagram.png --force-document --json
```

Use an absolute path. `--force-document` avoids Telegram compression for
images, GIFs, and videos. Inspect the attachment first and never send secrets.

## Buttons

Use a presentation with URL buttons for safe navigation:

```bash
scripts/notify-javier.sh \
  --message "La sesión requiere tu decisión" \
  --presentation '{"title":"Bloqueo de Codex","tone":"warning","blocks":[{"type":"text","text":"Falta una aprobación."},{"type":"buttons","buttons":[{"label":"Abrir sesión","url":"codex://threads/<uuid>"}]}]}' \
  --json
```

Telegram renders supported presentation buttons as an inline keyboard and
falls back to readable text otherwise. Callback or command buttons return
input to OpenClaw, not directly to the Codex PPM. Do not use them as
authoritative production approval without a separately designed,
authenticated handoff.

## Polls

Polls use `openclaw message poll`, not the wrapper:

```bash
openclaw message poll \
  --channel telegram \
  --target 434830632 \
  --poll-question "¿Qué opción prefieres?" \
  --poll-option "Opción A" \
  --poll-option "Opción B" \
  --poll-public
```

Telegram supports anonymous/public polls, multiple selections, silent
delivery, forum topics, and durations from 5 to 600 seconds. Polls are for
lightweight choices, not protected production authorization.

## Model-generated delivery

`message send` sends supplied content directly and does not invoke a model. To
ask an OpenClaw agent to generate and deliver a response with a specific
configured model:

```bash
openclaw agent \
  --session-key agent:main:codex-ppm-alerts \
  --message "Resume este bloqueo para Javier en menos de 70 palabras: <facts>" \
  --model <provider/model> \
  --thinking low \
  --deliver \
  --reply-channel telegram \
  --reply-to 434830632 \
  --json
```

Use only model identifiers already configured in OpenClaw. Prefer direct
deterministic messages for blocker alerts.

## Delivery diagnostics

Run the notifier outside the restricted Codex sandbox from the first attempt.
It writes OpenClaw state under `~/.openclaw/state` and connects to the local
gateway at `127.0.0.1:18789`; use the approved escalated execution path for
that local write and connection. Treat delivery as proven only when the JSON
contains `payload.ok: true` and a `messageId`.

If a restricted attempt produces `EPERM`, `attempt to write a readonly
database`, or WebSocket close `1006`, classify that result as a local sandbox
failure and retry the same deduplicated message once outside the sandbox. If
the outside attempt fails, run the gateway health diagnostic outside the
sandbox before classifying the failure as a gateway or Telegram channel
outage. Do not change permissions or restart services based only on restricted
diagnostics.

## Other Telegram actions

OpenClaw also exposes message editing, deletion, reactions, pin/unpin,
recent-message reads, stickers, and forum-topic actions. Use
`openclaw message <action> --help` immediately before an uncommon action
because flags and channel capabilities can change.

Official references:

- https://docs.openclaw.ai/cli/message
- https://docs.openclaw.ai/plugins/message-presentation
- https://docs.openclaw.ai/channels/telegram
- https://docs.openclaw.ai/cli/agent
