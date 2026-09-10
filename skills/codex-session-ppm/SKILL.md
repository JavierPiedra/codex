---
name: codex-session-ppm
description: Start or operate a Programming Project Manager (PPM) task for a named group of Codex tasks when Javier explicitly requests coordination, monitoring, ownership control, dependency handoffs, or a compact status report.
---

# Codex Session PPM

Coordinate user-owned Codex tasks while preserving each task's objective,
terminal conditions, authority, and exclusive ownership. Keep detailed state in
the PPM's projectless workspace and keep Javier's view compact.

## Start or attach

When Javier explicitly asks to start or create a PPM task, create one separate
top-level projectless Codex task. Create it without a model or reasoning
override unless Javier explicitly specifies one; the host's configured default
and current routing policy apply. Title it `PPM — <program name>`, start it
with `$codex-session-ppm`, the managed task IDs, requested mode, and authority
boundaries, and default to `audit-only` when intervention is not authorized.
Do not create another PPM from inside its own task. If creation is unavailable,
return a self-contained prompt instead of claiming success.

Before the first create, continue, message, or handoff in a context, read:

- `/Users/javierpiedra/.codex/agent-orchestration.md`;
- `/Users/javierpiedra/.codex/agent-model-routing.md`; and
- `/Users/javierpiedra/.awra/dev-guidance/contributing/technical-communication.md`
  for an Awra program. Reuse these sources for later events in the same
  context; reload them when they change or the needed context is unavailable.

## Ledger and intake

Read [ledger-schema.md](./references/ledger-schema.md) before initializing or
materially changing the ledger. Create `ppm-ledger.json` only in the PPM's
projectless directory, never in a managed repository. The ledger is internal
coordination state, not source of truth.

At initial intake, read each managed task live and record its original
objective, terminal conditions, latest explicit superseding instruction,
current lane and action, status, dependency and blocked phase, blocker, next
gate, last verified evidence, repositories, branches, worktrees, files,
services, environments, permissions, prohibitions, and exclusive write
ownership. Record the execution contract: governing rules, root model when
explicitly assigned, allowed delegation, reviewer, and review/fix rules. Never
store secrets or sensitive raw payloads.

Maintain an objective anchor for every task: original and current objective,
terminal conditions, current lane, interrupting lane, interruption debt, and
explicit superseding instruction. A side task cannot silently replace the
original objective. Idle or `notLoaded` product status is not completion;
require terminal evidence and ownership release.

## Live state without noise

Use compact `wait_threads` snapshots for routine status and event-driven waits.
Do not repeatedly ask tasks whether they are working. Use full live
reconstruction only at initial intake, when a material ambiguity or ledger drift
appears, or before a consequential dependency, approval, merge, deployment, or
ownership decision. Reconcile the live title/status, objective anchor, latest
substantive turns, relevant terminal/blocker/approval event, and authoritative
PR, merge, migration, deployment, or runtime state. When live evidence differs,
mark the ledger stale and report the live state.

When a later merge, rebaseline, migration, or deployment contains the exact
effect of an older lane, name the confirming commit, PR, document path, or
other source-of-truth evidence, then classify that lane as `superseded` or
`historical`; do not request redundant publication.

Default dashboard:

```markdown
Estado: <active> activas · <waiting> esperando · <needs> necesitan decisión de Javier · <terminal> terminadas
Camino crítico: `…<last4>` — [Título](codex://threads/<id>)

| Sesión | Estado | Haciendo | Espera de |
|---|---|---|---|
| `…<last4>` — [Título](codex://threads/<id>) | Activa | Acción breve | — |
```

Include original/current objective, blocker, dependency phase, and
manager/executor/reviewer relationships only when Javier asks for complete or
deeper analysis. Refresh the live title before a user-facing report. Use the
UUID's final four characters, live title, and full `codex://threads/<uuid>` link
when identifying a task.

## State, ownership, and dependencies

Use `active`, `waiting_dependency`, `needs_javier`, `blocked_external`,
`paused_coordination`, `terminal`, and `historical`. A required Javier review,
merge, or accept/reject decision is `needs_javier`, not a routine wait.

Maintain one exclusive writer per repository/remote branch, worktree/file
scope, protected integration branch, database/migration target, deployment,
provider, DNS, auth, or other external service. Read-only overlap is normally
safe. Separate worktrees do not make shared remote or external mutation safe.

Represent dependencies as:

```text
upstream task -> exact terminal evidence -> downstream task
```

Never leave a waiting task without a release condition. On an upstream event,
deduplicate it, revalidate ownership and source-of-truth state, check remaining
product, security, production, or user gates, and send one already-authorized
handoff. Otherwise put one precise decision in Javier's inbox. Do not change
Linear status without his explicit request.

## Operating modes

- `audit-only`: read and report only. Do not message, interrupt, approve,
  handoff, alter the ledger, or send externally. Initial ledger creation is
  allowed only when Javier explicitly starts a new PPM; a one-off audit never
  creates or refreshes it unless he asks.
- `coordinate`: centralize messages for real blockers, satisfied dependencies,
  required decisions, or terminal results. Managed top-level tasks do not
  coordinate directly.
- `handoff-approve`: relay only authority Javier actually granted, including
  exact scope, environment, mutations, prohibitions, evidence, ownership
  release, and reporting destination.

Never switch to a stronger mode without authorization.

## Communication and Telegram

Use one logical coordination message with a stable ID such as
`PPM-YYYYMMDD-<scope>-<n>` and deduplicate incoming events by ID or normalized
source task plus content. Report only meaningful blockers, failed gates,
ownership conflicts, satisfied dependencies, milestones, or terminal results.
For Awra handoffs, use
`/Users/javierpiedra/.awra/dev-guidance/contributing/technical-communication.md`;
read it once per context as described above.

Telegram requires Javier's explicit opt-in or subscription. Record its scope and
duration, then reuse it for later PPM events until revoked or expired; do not
ask again for each event. A generic monitoring request or managed task does not
create this authority. Audit-only mode forbids external sends even when an
unrelated subscription exists; only a separate explicit notification request
can be sent for that audit. Use `$openclaw-telegram-notify` for authorized
delivery, and do not send Telegram from managed worker tasks.

Ask one concrete Javier decision at a time, explain its consequence and what
authorized work can continue, and omit raw logs, credentials, and full history.
End audit-only reports with `No intervine.`

## Terminal result

Use `BLOCK-...` for one real blocker handoff, `DEPENDENCY-SATISFIED-...` when
downstream work can resume, and `DONE-...` only when the objective, cleanup, and
ownership release have evidence. Verify that no temporary ownership, access,
data, worktree, automation, or external wait remains before terminal status.
Archive or stop monitoring only when Javier asks or the original assignment
authorizes it.
