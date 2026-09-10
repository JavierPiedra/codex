# JSON output

When JSON is requested, output only valid JSON with this shape:

```json
{
  "loop_status": "pass | fail | blocked",
  "verdict": "ready | ready_with_minor_fixes | needs_revision | blocked",
  "next_action": "proceed | fix_prd | create_execution_spec | ask_human | inspect_repo",
  "counts": {"blocker": 0, "major": 0, "minor": 0, "nit": 0},
  "confidence": "high | medium | low",
  "gates": {
    "repo_guidance_gate": "pass | fail | blocked | not_applicable",
    "problem_gate": "pass | fail | blocked | not_applicable",
    "contract_gate": "pass | fail | blocked | not_applicable",
    "execution_gate": "pass | fail | blocked | not_applicable",
    "verification_gate": "pass | fail | blocked | not_applicable",
    "risk_gate": "pass | fail | blocked | not_applicable",
    "drift_gate": "pass | fail | blocked | not_applicable"
  },
  "evidence_read": {
    "prd": "",
    "execution_spec": "",
    "repo_guidance": [],
    "related_docs": []
  },
  "top_findings": [{
    "severity": "blocker | major | minor | nit",
    "title": "",
    "location": "",
    "gate": "",
    "problem": "",
    "fix": ""
  }],
  "missing_decisions": [],
  "suggested_fix_order": [],
  "stop_reason": ""
}
```

Use actual enum values, arrays, numbers, and strings; do not emit the pipe
notation from the schema as a value.
