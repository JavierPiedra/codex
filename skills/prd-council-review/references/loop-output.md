# Loop output

In default `loop` mode, return exactly this block and no extra prose:

```text
LOOP_STATUS: <pass | fail | blocked>
VERDICT: <ready | ready_with_minor_fixes | needs_revision | blocked>
NEXT_ACTION: <proceed | fix_prd | create_execution_spec | ask_human | inspect_repo>
BLOCKER_COUNT: <number>
MAJOR_COUNT: <number>
MINOR_COUNT: <number>
CONFIDENCE: <high | medium | low>
GATES:
- repo_guidance_gate: <pass | fail | blocked | not_applicable>
- problem_gate: <pass | fail | blocked | not_applicable>
- contract_gate: <pass | fail | blocked | not_applicable>
- execution_gate: <pass | fail | blocked | not_applicable>
- verification_gate: <pass | fail | blocked | not_applicable>
- risk_gate: <pass | fail | blocked | not_applicable>
- drift_gate: <pass | fail | blocked | not_applicable>
EVIDENCE_READ:
- prd: <path | pasted_content>
- execution_spec: <path | missing | not_applicable>
- repo_guidance: <comma-separated paths | none_found>
- related_docs: <comma-separated paths | none_found>
TOP_FINDINGS:
1. [<severity>] <short title>
   location: <file path and section>
   gate: <gate name>
   fix: <smallest required fix>
2. [<severity>] <short title>
   location: <file path and section>
   gate: <gate name>
   fix: <smallest required fix>
MISSING_DECISIONS:
- <decision needed, or `none`>
SUGGESTED_FIX_ORDER:
1. <first smallest useful fix>
2. <second smallest useful fix>
3. <third smallest useful fix>
STOP_REASON:
<why the loop should stop or continue>
```

Keep at most five highest-impact findings, omit council tables and long
rationale, and use stable labels exactly. Use `none` when findings, decisions,
or suggested fixes are absent.
