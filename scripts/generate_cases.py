#!/usr/bin/env python3
"""Generate the reference observed-case corpus for the fault management fixture.

Produces a JSONL file of stitched cases in the substrate case-record shape,
covering the dominant path, the inventory rework path, escalation cases, and
a loopback-failure exception case. Deterministic: the same invocation always
produces the same corpus.

Usage: python3 scripts/generate_cases.py [--out fixtures/cases/fault-management-cases.jsonl] [--n 40]
"""

import argparse
import json
import random

random.seed(20261104)


def make_case(index, profile):
    case_id = "FM-2026-11-%04d" % index
    started = "2026-11-02T%02d:%02dZ" % (8 + index % 8, index % 60)
    steps = []
    decisions = []

    def step(action, app, minute, actor="operations-agent", handoff=False):
        entry = {"action": action, "application": app,
                 "actor_role": actor, "timestamp": started.replace("T", "T")} if False else {
                 "action": action, "application": app, "actor_role": actor,
                 "timestamp": "2026-11-02T%02d:%02dZ" % (8 + (index % 8), minute % 60)}
        if handoff:
            entry["handoff"] = True
        return entry

    steps.append(step("correlate-alarms", "network-monitoring-platform", 5))
    if profile == "rework":
        steps.append(step("reconcile-inventory", "inventory-system", 12))
    steps.append(step("loopback-test", "line-test-system", 20))
    if profile == "loopback-failure":
        steps.append(step("loopback-test", "line-test-system", 30))
        steps.append(step("loopback-test", "line-test-system", 40))
        steps[-1]["exceptions"] = [{
            "condition": "three failed loopbacks",
            "class": "technical", "severity": "high",
            "escalation": {"target_role": "on-call-engineer", "reason": "loopback threshold exceeded"},
        }]
        decisions.append({"branch_condition": "loopback_failures >= 3", "evidence": "third failed loopback"})
        outcome = "not_achieved"
        cycle = 95 + index % 20
        first_pass = False
        dispatch = None
    elif profile == "high-mttr":
        decisions.append({"branch_condition": "mttr_estimate > 120", "evidence": "estimate %d min" % (130 + index % 60)})
        steps.append(step("dispatch-field-crew", "dispatch-system", 45, actor="shift-supervisor", handoff=True))
        outcome = "achieved"
        cycle = 140 + index % 30
        first_pass = True
        dispatch = "shift-supervisor"
    elif profile == "priority-outage":
        decisions.append({"branch_condition": "customer_tier == 'priority' and outage == true", "evidence": "priority customer with active outage"})
        steps.append(step("dispatch-field-crew", "dispatch-system", 45, actor="shift-supervisor", handoff=True))
        outcome = "achieved"
        cycle = 90 + index % 25
        first_pass = True
        dispatch = "shift-supervisor"
    else:  # dominant
        mttr = 60 + index % 50
        decisions.append({"branch_condition": "mttr_estimate <= 120", "evidence": "estimate %d min" % mttr})
        steps.append(step("dispatch-field-crew", "dispatch-system", 45, actor="operations-agent"))
        outcome = "achieved"
        cycle = mttr + 15
        first_pass = True
        dispatch = "operations-agent"
    if profile != "loopback-failure":
        steps.append(step("notify-planning", "planning-system", 55))
        if profile == "rework":
            steps.append(step("loopback-test", "line-test-system", 35))
            steps.append(step("resolve-fault", "network-monitoring-platform", 42))
        else:
            steps.append(step("resolve-fault", "network-monitoring-platform", 50))
    # The recorded decisions attach to the step that acted on them (the
    # dispatch, or the last step for cases that never dispatched).
    if decisions:
        target = next((s for s in steps if s["action"] == "dispatch-field-crew"), steps[-1])
        target["decisions"] = decisions

    context = {"segment_isolated": True}
    if profile == "rework":
        context["inventory_mismatch"] = True
        context["segment_isolated"] = False
    if profile == "dominant":
        context["mttr_estimate"] = mttr
    if profile == "high-mttr":
        context["mttr_estimate"] = 130 + index % 60
    if profile == "priority-outage":
        context["customer_tier"] = "priority"
        context["outage"] = True
    context["loopback_failures"] = 3 if profile == "loopback-failure" else 0

    return {
        "case_id": case_id,
        "procedure": "fault-management",
        "started_at": started,
        "ended_at": "2026-11-02T%02d:%02dZ" % (8 + index % 8, (index % 60 + cycle % 60) % 60),
        "process_ref": None,
        "tasks": [{"name": "diagnose-and-restore", "steps": steps}],
        "actor_roles": sorted({s["actor_role"] for s in steps}),
        "outcome": {"result": outcome, "cycle_time": cycle, "first_pass": first_pass},
        "provenance": {
            "stitching_version": "stitch-1.2.0",
            "capture_surface_declaration_version": "csd-2026-10",
            "process_catalog_version": "v1-alpha",
            "correlation_key": "fault-ticket:" + case_id,
        },
        "context": context,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fixtures/cases/fault-management-cases.jsonl")
    ap.add_argument("--n", type=int, default=40)
    args = ap.parse_args()

    profiles = (["dominant"] * 6 + ["rework"] * 1 + ["high-mttr"] * 1 + ["priority-outage"] * 1 + ["loopback-failure"] * 1)
    with open(args.out, "w") as handle:
        for i in range(1, args.n + 1):
            profile = profiles[i % len(profiles)]
            case = make_case(i, profile)
            if case.get("process_ref") is None:
                del case["process_ref"]
            handle.write(json.dumps(case) + "\n")
    print("wrote %d cases to %s" % (args.n, args.out))


if __name__ == "__main__":
    main()
