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
import sys

from . import mining


def compile_aop(sop_hypothesis: dict, cases: list[dict], manifest: dict, version: str) -> dict:
    ratifications = manifest.get("rule_ratifications", {})
    support_floor = manifest.get("minimum_support")
    confidence_floor = manifest.get("confidence_floor", 0.0)
    variants_mined = mining.mine_variants(cases, critical_actions=manifest.get("critical_variants"))
    rules = mining.extract_decision_rules(cases, manifest["authority_map"])
    exceptions_mined = mining.mine_exceptions(cases)
    loops_mined = mining.mine_rework_loops(cases)

    variants = []
    for index, v in enumerate(variants_mined, start=1):
        # NM-PRV-6: the variant inherits the lowest stitching confidence among
        # its cases (absent confidence means key-stitched, treated as 1.0).
        stitching_confidence = min(
            (c.get("stitching_confidence", 1.0) for c in cases if c["case_id"] in v["case_ids"]),
            default=1.0,
        )
        below_support = support_floor is not None and v["observed_cases"] < support_floor
        if below_support:
            print("compile: variant %s below the support floor (%d < %s); its rules cannot be ratified"
                  % (v["trigger"][:40], v["observed_cases"], support_floor), file=sys.stderr)
        # Reference implementation: every mined rule is evaluated on every
        # variant path; the guardrail re-checks authority at run time.
        variant_rules = []
        for r in rules:
            # NM-AUT-7: ratification comes from the manifest by exact
            # condition. A rule below the support floor or below the
            # confidence floor cannot be ratified, whatever the manifest says.
            requested = bool(ratifications.get(r["if"]))
            if requested and not below_support and stitching_confidence >= confidence_floor:
                status = "ratified"
            elif requested and stitching_confidence < confidence_floor:
                status = "reviewed"  # capped: low-confidence corpus cannot carry ratification (NM-PRV-6)
            else:
                status = "observed"
            rule = {
                "if": r["if"],
                "then": r["then"],
                "authority": r["authority"],
                "status": status,
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
                "status": "ratified" if (ratifications.get("true") and not below_support and stitching_confidence >= confidence_floor) else "observed",
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
        variants[-1]["provenance"]["stitching_confidence"] = round(stitching_confidence, 3)

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
    if manifest.get("accountable_owner"):
        doc["governance"]["accountable_owner"] = manifest["accountable_owner"]
    if manifest.get("prepared_by"):
        doc["governance"]["prepared_by"] = manifest["prepared_by"]
    if manifest.get("ratified_by"):
        doc["governance"]["ratified_by"] = manifest["ratified_by"]

    # Policy-conflict flagging: where the SOP claimed an authority hint and
    # the manifest assigns a different class for the same decision family,
    # the conflict is recorded, and the involved rules stay unratified until
    # the owner resolves it.
    conflicts = []
    claimed = {c.get("if", "").strip(): c.get("authority_hint") for c in sop_hypothesis.get("claimed_decision_rules", []) if c.get("if")}
    for condition, hint in claimed.items():
        for r in rules:
            if r["if"].strip() == condition.strip() and hint and hint != r["authority"]:
                conflicts.append({"condition": condition, "sop_claimed": hint, "manifest_assigned": r["authority"]})
    if conflicts:
        doc["provenance"]["policy_conflicts"] = conflicts
        print("compile: %d policy conflict(s) between the SOP claims and the manifest" % len(conflicts), file=sys.stderr)
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
