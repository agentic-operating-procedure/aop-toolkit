#!/usr/bin/env python3
"""Validate declared fault-management case cycle_time against case boundaries.

Contract: aop-context-graph case schema documentation defines cycle time as
ended_at minus started_at. This validator checks that declared values match
that elapsed duration; it does not validate step ordering or event boundaries.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_time(value, field, case_id):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        raise ValueError(f"{case_id}: {field} is not a valid ISO-8601 timestamp: {value!r}")
    if parsed.tzinfo is None:
        raise ValueError(f"{case_id}: {field} must include a timezone")
    return parsed


def validate_case(case):
    case_id = case.get("case_id", "<missing-case-id>")
    problems = []
    try:
        start = parse_time(case.get("started_at"), "started_at", case_id)
        end = parse_time(case.get("ended_at"), "ended_at", case_id)
    except ValueError as exc:
        return [str(exc)]
    elapsed = (end - start).total_seconds() / 60
    if elapsed < 0:
        problems.append(f"{case_id}: ended_at precedes started_at")
        return problems
    declared = case.get("outcome", {}).get("cycle_time")
    if not isinstance(declared, (int, float)) or isinstance(declared, bool):
        problems.append(f"{case_id}: outcome.cycle_time must be a numeric minute duration")
    elif declared != elapsed:
        problems.append(
            f"{case_id}: outcome.cycle_time={declared} does not equal "
            f"elapsed boundary duration {elapsed} minutes"
        )
    return problems


def validate_file(path):
    problems = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        problems.extend(validate_case(case))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", nargs="?", default="fixtures/cases/fault-management-cases.jsonl")
    args = parser.parse_args()
    problems = validate_file(args.corpus)
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print(f"Cycle-time validation passed: {args.corpus}")


if __name__ == "__main__":
    main()
