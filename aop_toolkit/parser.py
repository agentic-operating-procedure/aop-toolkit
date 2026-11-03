"""SOP parser: parse a structured Standard Operating Procedure into an intent hypothesis.

The SOP is a hypothesis the observation will test (NM-INT-3). The parser reads
the declared structure: objective, scope, steps, decision rules, exceptions and
escalations. It does not interpret; it extracts the claim.
"""

from __future__ import annotations

import re


def parse_sop(text: str) -> dict:
    """Parse an SOP in the reference markdown convention into an intent hypothesis."""
    lines = text.splitlines()
    heading = {}
    current = None
    for line in lines:
        m = re.match(r"^##\s+(.+)$", line.strip())
        if m:
            current = m.group(1).strip().lower()
            heading[current] = []
        elif current is not None and line.strip():
            heading[current].append(line.strip())

    def bullets(section):
        return [re.sub(r"^[-*]\s+", "", item) for item in heading.get(section, [])]

    def paragraph(section):
        items = heading.get(section, [])
        return " ".join(items) if items and not all(i.startswith(("-", "*")) for i in items) else (" ".join(items) if items else "")

    steps = bullets("steps") or bullets("procedure steps")
    decision_rules = []
    for raw in bullets("decision rules") or bullets("decisions"):
        # Convention: "if <condition> then <action>" possibly ending with an authority hint in brackets.
        m = re.match(r"(?i)if\s+(.+?)\s+then\s+(.+?)(?:\s*\[(autonomous|approval-required|prohibited)\])?$", raw)
        if m:
            decision_rules.append({
                "if": m.group(1).strip(),
                "then": m.group(2).strip(),
                "authority_hint": m.group(3),
            })
        else:
            decision_rules.append({"if": None, "then": raw, "authority_hint": None})

    exceptions = []
    for raw in bullets("exceptions"):
        m = re.match(r"(?i)(.+?)\s*->\s*(escalate|recover|validated-path)(?:\s+to\s+(.+))?$", raw)
        if m:
            exceptions.append({"condition": m.group(1).strip(), "behaviour": m.group(2).strip(), "target_role": (m.group(3) or "").strip() or None})
        else:
            exceptions.append({"condition": raw, "behaviour": "escalate", "target_role": None})

    return {
        "name": _first_heading_title(lines),
        "objective": paragraph("objective"),
        "outcome_condition": paragraph("outcome"),
        "in_scope": bullets("in scope"),
        "out_of_scope": bullets("out of scope"),
        "claimed_steps": steps,
        "claimed_decision_rules": decision_rules,
        "claimed_exceptions": exceptions,
        "escalation_prose": paragraph("escalation"),
    }


def _first_heading_title(lines: list[str]) -> str:
    for line in lines:
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return "unnamed procedure"
