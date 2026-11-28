"""Deterministic corpus validation (CR-041 3.1).

Checks the timing and integrity invariants of a stitched case corpus:

  CV-1  every step timestamp lies inside the declared run interval
        (started_at <= timestamp <= ended_at);
  CV-2  step timestamps are monotonically non-decreasing in array order
        (procedural order and event order coincide in the reference corpus;
        a corpus needing a separate event order declares so per case);
  CV-3  outcome.cycle_time equals ended_at - started_at, in whole minutes;
  CV-4  started_at <= ended_at.

A violation fails with an actionable diagnostic naming the case, the step and
the invariant. Invalid corpora must not reach compilation.

Usage:
    python3 -m aop_toolkit.validate_corpus <cases.jsonl> [--max-report 12]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys


def parse_ts(text: str) -> datetime.datetime:
    # Minute precision (17 chars incl. Z) or second precision (19 chars).
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError("unrecognised timestamp format: %r" % text)


def validate_corpus(path: str, max_report: int = 12) -> tuple[int, list[str]]:
    diags: list[str] = []
    cases = 0
    with open(path) as handle:
        for line in handle:
            if not line.strip():
                continue
            cases += 1
            c = json.loads(line)
            cid = c.get("case_id", "?")
            try:
                start = parse_ts(c["started_at"])
                end = parse_ts(c["ended_at"])
            except (KeyError, ValueError) as exc:
                diags.append(f"{cid}: unparseable case boundary: {exc}")
                continue
            if end < start:
                diags.append(f"{cid}: CV-4 ended_at {c['ended_at']} precedes started_at {c['started_at']}")
            prev = start
            for t in c.get("tasks", []):
                for s in t.get("steps", []):
                    try:
                        ts = parse_ts(s["timestamp"])
                    except (KeyError, ValueError) as exc:
                        diags.append(f"{cid}: step {s.get('action')}: unparseable timestamp: {exc}")
                        continue
                    if ts < start:
                        diags.append(f"{cid}: CV-1 step '{s.get('action')}' at {s['timestamp']} precedes started_at {c['started_at']}")
                    if ts > end:
                        diags.append(f"{cid}: CV-1 step '{s.get('action')}' at {s['timestamp']} is later than ended_at {c['ended_at']}")
                    if ts < prev:
                        diags.append(f"{cid}: CV-2 step '{s.get('action')}' at {s['timestamp']} breaks monotonic order (previous {prev.isoformat()})")
                    prev = max(prev, ts)
            declared = c.get("outcome", {}).get("cycle_time")
            actual = (end - start).total_seconds() / 60
            if declared is not None and declared != actual:
                diags.append(f"{cid}: CV-3 declared cycle_time {declared} != ended-started {actual:g} minutes")
    return cases, diags


def main(argv=None):
    ap = argparse.ArgumentParser(prog="aop_toolkit.validate_corpus", description=__doc__)
    ap.add_argument("cases")
    ap.add_argument("--max-report", type=int, default=12)
    args = ap.parse_args(argv)

    cases, diags = validate_corpus(args.cases, args.max_report)
    if diags:
        print(f"CORPUS INVALID: {cases} cases, {len(diags)} violation(s):")
        for d in diags[: args.max_report]:
            print("  -", d)
        if len(diags) > args.max_report:
            print(f"  ... and {len(diags) - args.max_report} more")
        return 1
    print(f"CORPUS VALID: {cases} cases satisfy CV-1 to CV-4.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
