"""The eight upload gates. Publishing checks this file; prompts do not restate it."""

from __future__ import annotations

REQUIRED_GATES = (
    "quote",
    "reach",
    "impact",
    "bch",
    "domain",
    "experience",
    "prior_issues",
    "counter",
)
MIN_EVIDENCE = 40


def gates_ok(finding: dict) -> bool:
    gates = finding.get("gates")
    evidence = finding.get("gate_evidence")
    if not isinstance(gates, dict) or not isinstance(evidence, dict):
        return False
    if set(gates) != set(REQUIRED_GATES) or set(evidence) != set(REQUIRED_GATES):
        return False
    for name in REQUIRED_GATES:
        if gates.get(name) is not True:
            return False
        text = evidence.get(name)
        if not isinstance(text, str) or len(text.strip()) < MIN_EVIDENCE:
            return False
    prior = evidence["prior_issues"].casefold()
    if "no matching issue" not in prior and "#" not in evidence["prior_issues"]:
        return False
    domain = evidence["domain"].casefold()
    if "perspective:" not in domain and "perspective " not in domain:
        return False
    if "seedsigner" not in evidence["experience"].casefold():
        return False
    return True
