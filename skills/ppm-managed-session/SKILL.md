---
name: ppm-managed-session
description: Register the current Codex session with an existing Programming Project Manager (PPM) and report only meaningful blockers, dependency handoffs, failed gates, milestones, or terminal results. Use when Javier or a PPM explicitly says the session is managed.
---

# PPM Managed Session

Become a worker managed by one existing PPM thread. This skill does not make the
current session a coordinator and does not authorize work beyond the current
assignment.

## Register once

Obtain the full PPM thread UUID from the invocation or assignment. If
it is missing or ambiguous, ask for that value; never infer it from another
session ID. Record in the current Goal or working plan:

- PPM thread UUID and the current objective and terminal conditions;
- owned repositories, branches, worktrees, files, environments, and external
  resources;
- exact permissions, prohibitions, and current dependency or release condition.

Send one registration event through the available Codex thread messaging or
handoff tool. Use a stable ID and tell the PPM to process it once:

```text
PPM-REGISTER-<current-thread-last4>-<goal-or-date>-1 — Procesa este ID exactamente una vez.

Sesión gestionada: <UUID completo>
Objetivo: <una oración>
Condición terminal: <una oración>
Propiedad exclusiva: <alcance exacto, o sólo lectura>
Permitido: <alcance autorizado exacto>
Prohibido: <alcance protegido exacto>
Dependencia actual: <condición de liberación, o ninguna>
```

Do not resend registration when nothing material changed. Keep the registration
active until the PPM or Javier releases or replaces it, or the goal reaches a
terminal result.

## Continue inside the assignment

Continue authorized work autonomously. Do not ask the PPM for tactical approval
that Javier already granted. Keep one writer per branch, worktree, database,
deployment, provider, or other shared resource. If an ownership collision
appears, stop only the conflicting mutation and continue safe independent work.

Do not contact other managed sessions directly. Route cross-session dependencies
through the PPM. Do not change Linear statuses unless Javier explicitly asks.
Do not broaden staging authority into production authority, and never include
secrets, tokens, credentials, payment data, cookies, or raw sensitive payloads
in a handoff.

## Report meaningful events only

Send an event to the PPM only for a real blocker or failed gate, ownership
collision, satisfied dependency, merge or deployment milestone, or terminal
result. Routine execution, unchanged waits, normal CI output, and status
narration do not need a message.

A real blocker needs a decision, approval, credential, access change, external
action, or dependency outside this session's authority. Diagnose or fix a
problem that remains within the assignment before calling it a blocker.

For Awra work, read
`/Users/javierpiedra/.awra/dev-guidance/contributing/technical-communication.md`
once before the first registration or material handoff in this context. Reload
it only when it changes or the needed context is unavailable. Use its claim,
evidence, status, specificity, and concise reporting rules; do not duplicate
that policy here. Write in Spanish unless the assignment requires another
language. Lead with consequence, give the concrete evidence, and end with one
exact action outside this session's authority.

Use one stable event ID. A blocker handoff has this shape:

```text
BLOCK-<YYYYMMDD>-<scope>-1 — Procesa este ID exactamente una vez.

Estado: BLOQUEADA — <specific result that cannot continue>
Consecuencia: <phase stopped>
Hecho comprobado: <concrete evidence>
Necesita: <one exact decision, approval, access, or external action>
Puede continuar: <independent authorized work, or nada>
Propiedad: <retained or released, with exact scope>
```

Use `DEPENDENCY-SATISFIED-...` for a released downstream scope and `DONE-...`
only when the objective, cleanup, and ownership release are evidenced. If PPM
delivery fails, retry once only when the first result proves no delivery;
otherwise preserve the event locally and report the failed handoff in this
session.

## Boundaries

- Report to the PPM, never directly to Javier, Telegram, or another managed
  session.
- Do not send Telegram. The PPM owns notification authorization and delivery.
- Do not archive, merge, deploy, publish, or mutate a provider or production
  environment unless the active assignment separately authorizes it.
- A final chat response or idle state is not terminal evidence.
