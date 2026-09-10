# PPM ledger schema

Use one `ppm-ledger.json` file in the projectless PPM directory. This file is internal
coordination state and must not be copied into managed repositories.

## Top-level shape

```json
{
  "schema_version": 2,
  "program": {
    "name": "Program name",
    "ppm_thread_id": "thread-id",
    "mode": "audit-only",
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601"
  },
  "sessions": {},
  "dependencies": [],
  "approvals": [],
  "javier_inbox": [],
  "events": []
}
```

## Session record

Key `sessions` by canonical thread ID.

```json
{
  "thread_id": "thread-id",
  "title": "Live thread title",
  "link": "codex://threads/thread-id",
  "original_objective": "Stable objective from the original assignment",
  "current_objective": "Latest explicit objective after any reuse or superseding instruction",
  "terminal_conditions": ["Evidence-based condition"],
  "current_lane": "Current bounded task",
  "current_action": "What the thread is doing now",
  "interrupting_lane": null,
  "interruption_debt": [],
  "managed_by": null,
  "role": "manager|executor|reviewer|independent",
  "status": "active",
  "product_status": "active|idle|notLoaded|unknown",
  "critical_path": true,
  "execution_contract": {
    "root_model": null,
    "root_reasoning": null,
    "governing_rules": [],
    "skills": [],
    "internal_delegation_allowed": false,
    "delegation_rules": [],
    "review_rules": [],
    "preserve_on_reactivation": true
  },
  "scope": {
    "repos": [],
    "branches": [],
    "worktrees": [],
    "files": [],
    "services": [],
    "environments": []
  },
  "write_ownership": [],
  "permissions": [],
  "prohibitions": [],
  "depends_on": [],
  "dependency_phase": null,
  "blocks": [],
  "blocker": null,
  "next_gate": "Concrete next gate",
  "pending_user_input": null,
  "superseded_by": null,
  "absorbed_by": null,
  "ledger_drift": null,
  "last_live_read": {
    "read_at": "ISO-8601",
    "latest_turn_id": null,
    "evidence_boundary": "Latest live event or source-of-truth state checked"
  },
  "last_evidence": {
    "summary": "Minimal evidence summary",
    "sha": null,
    "pr": null,
    "deployment": null,
    "verified_at": "ISO-8601"
  },
  "ownership_released": false,
  "updated_at": "ISO-8601"
}
```

## Dependency record

```json
{
  "upstream_thread_id": "thread-a",
  "downstream_thread_id": "thread-b",
  "reason": "Why the downstream work actually depends on the upstream",
  "blocked_phase": "implementation|publication|merge|migration-apply|deployment|qa|handoff",
  "release_condition": "Exact terminal evidence required",
  "status": "waiting",
  "released_at": null,
  "handoff_event_id": null
}
```

## Approval record

```json
{
  "approval_id": "approval-id",
  "source": "Javier",
  "scope": "Exact authorized scope",
  "allowed_actions": [],
  "environment": "staging",
  "prohibited_actions": [],
  "conditions": [],
  "granted_at": "ISO-8601",
  "expires_at": null,
  "consumed": false
}
```

An approval may be reusable when Javier explicitly grants standing authority. Do not
mark it consumed merely because one action occurred unless the authorization was
one-time.

## Javier inbox record

```json
{
  "inbox_id": "decision-id",
  "thread_id": "thread-id",
  "question": "One concrete decision",
  "why_needed": "Short consequence",
  "blocking": true,
  "created_at": "ISO-8601",
  "resolved_at": null,
  "resolution": null
}
```

Keep one logical inbox item per decision. Merge duplicate requests from multiple
threads when one answer resolves all of them.

## Event record and deduplication

```json
{
  "event_id": "PPM-YYYYMMDD-scope-n",
  "source_thread_id": "thread-id",
  "type": "blocker|terminal|handoff|approval|state-change",
  "content_hash": "stable-normalized-hash",
  "summary": "Short factual event",
  "received_at": "ISO-8601",
  "processed_at": "ISO-8601"
}
```

Treat `source_thread_id` and `source_host_id` envelopes containing the same
coordination ID or normalized payload as one event.

## State transitions

Allow these normal transitions:

```text
active -> waiting_dependency
active -> needs_javier
active -> blocked_external
active -> paused_coordination
active -> terminal
waiting_dependency -> active
needs_javier -> active
blocked_external -> active
paused_coordination -> active
terminal -> historical
```

Do not move to `terminal` from thread idleness alone. Require verified terminal
conditions, cleanup, and ownership release.

## Compact reporting projection

Generate the default dashboard only from:

- title and link;
- status;
- current lane;
- one blocker or dependency;
- critical path;
- unresolved Javier inbox items.

Keep all other ledger fields hidden until requested.

For an updated or deep status analysis, reconstruct every nonterminal or questioned
thread live first and project:

- original objective;
- current objective;
- current action;
- blocker;
- dependency reason and blocked phase;
- manager/executor/reviewer relationship;
- ledger drift, supersession, or canonical absorption.

`product_status` is display/runtime state only and must never be used as work status.
