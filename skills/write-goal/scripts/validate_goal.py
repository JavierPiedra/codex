#!/usr/bin/env python3
"""Detect mechanical anti-patterns in a drafted Codex Goal."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    message: str


EVIDENCE_TERMS = (
    "test", "prueba", "benchmark", "build", "artifact", "artefacto",
    "log", "metric", "métrica", "source", "fuente", "screenshot", "captura",
)
RECURRENCE_PATTERNS = (
    r"\bevery\s+(day|week|hour|monday|month)\b",
    r"\b(daily|weekly|hourly|monthly)\b",
    r"\bcada\s+(día|semana|hora|lunes|mes)\b",
)
UNBOUNDED_PATTERNS = (
    r"\bnever stop\b", r"\bkeep trying forever\b",
    r"\bno pares nunca\b", r"\bcontinúa para siempre\b",
)
VAGUE_PATTERNS = (
    r"^/?goal\s+(improve|enhance|clean up|make better)\b",
    r"^/?goal\s+(mejora|optimiza|limpia|haz mejor)\b",
)


def validate_goal(text: str) -> list[Finding]:
    normalized = " ".join(text.lower().split())
    findings: list[Finding] = []

    if not normalized.startswith("/goal "):
        findings.append(Finding(Severity.WARNING, "missing-command", "Start the draft with `/goal`."))

    if not any(term in normalized for term in EVIDENCE_TERMS):
        findings.append(Finding(Severity.ERROR, "missing-evidence", "Name a test, benchmark, metric, artifact, log, source, or review surface."))

    if not re.search(r"\b(if blocked|if .*block|si .*bloque|si no (?:hay|quedan))\b", normalized):
        findings.append(Finding(Severity.ERROR, "missing-blocked-stop", "Define when to stop as blocked and what to report."))

    if not re.search(r"\b(without|while preserving|preserve|preserva|sin cambiar|manteniendo)\b", normalized):
        findings.append(Finding(Severity.WARNING, "missing-constraint", "Add a non-regression constraint."))

    if not re.search(r"\b(budget|attempts?|iterations?|presupuesto|intentos?|iteraciones?|tokens?|hours?|horas?)\b", normalized):
        findings.append(Finding(Severity.WARNING, "missing-budget-stop", "Add a budget or attempt stop when useful."))

    for pattern in RECURRENCE_PATTERNS:
        if re.search(pattern, normalized):
            findings.append(Finding(Severity.ERROR, "calendar-recurrence", "Use a scheduled task for calendar recurrence."))
            break

    for pattern in UNBOUNDED_PATTERNS:
        if re.search(pattern, normalized):
            findings.append(Finding(Severity.ERROR, "unbounded-loop", "Replace infinite continuation with success, blocked, and budget exits."))
            break

    for pattern in VAGUE_PATTERNS:
        if re.search(pattern, normalized):
            findings.append(Finding(Severity.ERROR, "vague-outcome", "Replace the activity with an observable final state."))
            break

    risky_terms = ("production", "producción", "deploy", "desplieg", "delete", "elimina", "drop table")
    safety_terms = ("approval", "aprobación", "pause", "pausa", "dry run", "rollback")
    if any(term in normalized for term in risky_terms) and not any(term in normalized for term in safety_terms):
        findings.append(Finding(Severity.ERROR, "unsafe-side-effect", "Add approval, pause, dry-run, or rollback requirements for risky actions."))

    return findings


def main() -> int:
    text = sys.stdin.read().strip()
    if not text:
        print("error: expected Goal text on stdin", file=sys.stderr)
        return 2

    findings = validate_goal(text)
    for finding in findings:
        print(f"{finding.severity.value}: {finding.code}: {finding.message}")

    return 1 if any(finding.severity is Severity.ERROR for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
