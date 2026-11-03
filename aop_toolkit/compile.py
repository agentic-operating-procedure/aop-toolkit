"""AOP compiler: assemble a conformant AOP document from the SOP hypothesis,
the mined variants and rules, and the domain governance manifest.

The manifest carries everything observation cannot decide: permitted and
prohibited actions, the risk-axis assessment, the authority classes per
decision family, skills, coordination, control and assurance obligations.
Observation supplies the structure and its provenance; the owner supplies
the governance bounds. That division is the compile step.
"""

from __future__ import annotations

import json

from . import mining


def compile_aop(sop_hypothesis: dict, cases: list[dict], manifest: dict, version: str) -> dict:
    variants_mined = mining.mine_variants(cases)
    rules = mining.extract_decision_rules(cases, manifest["authority_map"])
    exceptions_mined = mining.mine_exceptions(cases)
    loops_mined = mining.mine_rework_loops(cases)

    variants = []
    for index, v in enumerate(variants_mined, start=1):
        # Reference implementation: every mined rule is evaluated on every
        # variant path; the guardrail re-checks authority at run time.
        variant_rules = []
        for r in rules:
            rule = {
                "if": r["if"],
                "then": r["then"],
                "authority": r["authority"],
                "provenance": {
                    "observed_cases": r["observed_cases"],
                    "path_frequency": v["frequency"],
                },
            }
            if r.get("applies_to"):
                rule["applies_to"] = r["applies_to"]
            variant_rules.append(rule)
        if not variant_rules:
            # No decision fired on this path in observation. Close authority
            # coverage with the manifest's default authority class (NM-AUT-3).
            variant_rules.append({
                "if": "true",
                "then": "proceed under the variant plan",
                "authority": manifest.get("default_authority_class", "prohibited"),
                "provenance": {
                    "observed_cases": v["observed_cases"],
                    "path_frequency": v["frequency"],
                },
            })
        variants.append({
            "id": "VAR-%03d" % index,
            "name": v["trigger"],
            "frequency": v["frequency"],
            "trigger": v["trigger"],
            "steps": v["actions"],
            "decision_rules": variant_rules,
            "provenance": {
                "observed_cases": v["observed_cases"],
                "path_frequency": v["frequency"],
            },
        })

    doc = {
        "aop": manifest["aop"],
        "version": version,
        "lifecycle": {
            "specification_status": "draft",
            "release_status": "not-released",
            "operational_applicability": "not-effective",
        },
        "intent": {
            "objective": sop_hypothesis["objective"],
            "outcome_condition": sop_hypothesis["outcome_condition"],
            "scope_boundary": {
                "in_scope": sop_hypothesis["in_scope"],
                "out_of_scope": sop_hypothesis["out_of_scope"],
            },
            "intent_hypothesis": _hypothesis_statement(sop_hypothesis),
        },
        "context": manifest["context"],
        "constraints": {
            "permitted_actions": manifest["permitted_actions"],
            "prohibited_actions": manifest["prohibited_actions"],
            "fail_closed": True,
        },
        "authority": {
            "default_authority_class": manifest.get("default_authority_class", "prohibited"),
            "risk_axes": manifest["risk_axes"],
            "decision_rights_ladder": manifest["decision_rights_ladder"],
        },
        "capabilities": {"skills": manifest["skills"]},
        "coordination": manifest["coordination"],
        "control": manifest["control"],
        "assurance": manifest["assurance"],
        "structure": {
            "variants": variants,
            "exception_edges": [
                {k: v for k, v in edge.items() if k != "observed_count" and v is not None}
                for edge in exceptions_mined
            ],
            "rework_loops": [
                {k: v for k, v in loop.items() if k != "observed_max_repeats"}
                for loop in loops_mined
            ],
        },
        "provenance": {
            "source": manifest["source"],
            "derived_from": {
                "observed_cases": len(cases),
                "variants": len(variants),
                "last_recalibrated": manifest["compiled_at"],
            },
            "source_sop": manifest.get("source_sop"),
        },
        "governance": {"audit": "case-record"},
    }
    if manifest.get("process_alignment"):
        doc["process_alignment"] = manifest["process_alignment"]
    return doc


def _hypothesis_statement(sop: dict) -> str:
    claims = []
    for rule in sop.get("claimed_decision_rules", []):
        if rule.get("if"):
            claims.append("claims that %s then %s" % (rule["if"], rule["then"]))
    if sop.get("escalation_prose"):
        claims.append("states in prose: %s" % sop["escalation_prose"])
    if not claims:
        claims.append("claims a linear corridor of %d steps" % len(sop.get("claimed_steps", [])))
    return "The source procedure %s. Observation tests these claims." % "; ".join(claims)


def write_aop(doc: dict, path: str) -> None:
    with open(path, "w") as handle:
        json.dump(doc, handle, indent=2, sort_keys=False)
