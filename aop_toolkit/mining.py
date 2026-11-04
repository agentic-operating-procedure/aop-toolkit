"""Variant mining and decision-rule extraction from observed cases.

Input is a JSONL corpus of stitched cases in the substrate case-record shape
(aop-context-graph/schema/case-record.schema.json). Mining produces a variant
inventory with observed frequencies and provenance, and decision rules with
their observed thresholds. This is the model-to-compile half of the pipeline.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict


def load_cases(path: str) -> list[dict]:
    cases = []
    with open(path) as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def case_actions(case: dict) -> list[str]:
    actions = []
    for task in case.get("tasks", []):
        for step in task.get("steps", []):
            actions.append(step["action"])
    return actions


def case_context(case: dict) -> dict:
    return case.get("context", {})


def case_decisions(case: dict) -> list[dict]:
    out = []
    for task in case.get("tasks", []):
        for step in task.get("steps", []):
            for decision in step.get("decisions", []):
                out.append({
                    "condition": decision["branch_condition"],
                    "evidence": decision.get("evidence", ""),
                    "case_id": case["case_id"],
                })
    return out


def mine_variants(cases: list[dict], min_frequency: float = 0.05) -> list[dict]:
    """Group cases by their ordered action signature; emit variants with
    frequencies, discriminating triggers, and provenance."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for case in cases:
        groups[tuple(case_actions(case))].append(case)
    total = len(cases)
    variants = []
    for signature, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        frequency = len(members) / total
        if frequency < min_frequency and len(groups) > 1:
            continue
        trigger = _discriminating_trigger(members, cases)
        variants.append({
            "actions": list(signature),
            "frequency": round(frequency, 4),
            "trigger": trigger,
            "case_ids": [m["case_id"] for m in members],
            "observed_cases": len(members),
        })
    return variants


def _discriminating_trigger(members: list[dict], all_cases: list[dict]) -> str:
    """Find the context attribute value that best separates this variant's
    cases from the rest. A reference heuristic: highest purity single
    attribute equality."""
    member_ids = {m["case_id"] for m in members}
    other = [c for c in all_cases if c["case_id"] not in member_ids]
    if not other:
        return "all observed cases"
    best = None
    keys = set()
    for case in all_cases:
        keys.update(case_context(case).keys())
    for key in sorted(keys):
        values = Counter(case_context(m).get(key) for m in members)
        if not values:
            continue
        value, count = values.most_common(1)[0]
        purity = count / len(members)
        present_in_other = sum(1 for c in other if case_context(c).get(key) == value)
        if present_in_other == 0 and purity >= 0.6:
            score = purity
            if best is None or score > best[0]:
                best = (score, "%s == %r" % (key, value))
    return best[1] if best else "residual pattern across %d cases" % len(members)


THRESHOLD_RE = re.compile(r"([a-z_]+)\s*(>=|<=|>|<|==|!=)\s*([0-9]+(?:\.[0-9]+)?)")


def extract_decision_rules(cases: list[dict], authority_map: dict[str, str]) -> list[dict]:
    """Group observed decisions into rules; attach observed provenance and the
    authority class from the manifest.

    Each distinct observed condition becomes its own rule: merging two
    thresholds of one variable into a majority rule would silently drop the
    minority path and could let a beyond-threshold action execute under the
    below-threshold rule. The condition's variable family is used only to
    look up the authority class. Authority comes from the domain manifest,
    never from the miner: observation says what humans decided, the owner
    says what the agent may decide.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        for decision in case_decisions(case):
            # The observed condition is kept verbatim: truncating a compound
            # condition to its first numeric comparison would drop the rest of
            # the guard (for example, "degradation > 30 AND outage" losing the
            # outage half) and could widen authority by accident.
            key = decision["condition"].strip()
            m = THRESHOLD_RE.search(key)
            family = m.group(1) if m else (key.split()[0] if key.split() else key)
            groups[key].append({**decision, "family": family})

    rules = []
    for condition, decisions in sorted(groups.items()):
        family = decisions[0]["family"]
        # Authority is resolved from the manifest by exact condition first,
        # then by the condition's variable family, and only then fails closed
        # to prohibited. A manifest entry may carry an applies_to action scope.
        binding = authority_map.get(condition, authority_map.get(family, "prohibited"))
        rule = {
            "if": condition,
            "then": _consequence_for(family, authority_map),
            "authority": binding.get("authority") if isinstance(binding, dict) else binding,
            "observed_cases": len({d["case_id"] for d in decisions}),
            "decision_count": len(decisions),
        }
        if isinstance(binding, dict) and binding.get("applies_to"):
            rule["applies_to"] = binding["applies_to"]
        rules.append(rule)
    return rules


def _consequence_for(family: str, authority_map: dict[str, str]) -> str:
    return "escalate to %s" % family.replace("_", "-") if authority_map.get(family) in ("approval-required", "prohibited") else "apply rule: %s" % family.replace("_", "-")


def mine_exceptions(cases: list[dict]) -> list[dict]:
    """Exception and escalation patterns: conditions, target roles, observed bounds."""
    conditions: Counter = Counter()
    targets: dict[str, str] = {}
    for case in cases:
        for task in case.get("tasks", []):
            for step in task.get("steps", []):
                for exc in step.get("exceptions", []):
                    conditions[exc["condition"]] += 1
                    esc = exc.get("escalation") or {}
                    if esc.get("target_role"):
                        targets[exc["condition"]] = esc["target_role"]
    edges = []
    for condition, count in conditions.most_common():
        behaviour = "escalate" if condition in targets else "validated-path"
        edges.append({
            "condition": condition,
            "behaviour": behaviour,
            "target_role": targets.get(condition),
            "observed_count": count,
        })
    return edges


def mine_rework_loops(cases: list[dict]) -> list[dict]:
    """Where an action repeats within a case, that is a rework loop: the
    return condition is the repeat, the bound is the observed maximum."""
    max_repeats: dict[str, int] = Counter()
    for case in cases:
        counts = Counter(case_actions(case))
        for action, count in counts.items():
            if count > 1:
                max_repeats[action] = max(max_repeats[action], count)
    loops = []
    for action, bound in sorted(max_repeats.items()):
        loops.append({
            "return_condition": "%s repeated after failure" % action,
            "iteration_bound": bound,
            "bound_exceeded_behaviour": "escalate",
            "observed_max_repeats": bound,
        })
    return loops
