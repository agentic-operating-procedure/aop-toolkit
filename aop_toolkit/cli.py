"""Command line interface for the reference toolchain.

Subcommands:
    parse-sop   Parse an SOP markdown file into an intent hypothesis (JSON).
    mine        Mine variants, rules, exceptions and rework loops from a case corpus (JSON).
    compile     Compile a full AOP document from an SOP, a case corpus and a governance manifest.
    lint        Lint an AOP document against the aop-spec schema and clauses.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import compile as compiler
from . import lint as linter
from . import mining
from .parser import parse_sop


def main(argv=None):
    parser = argparse.ArgumentParser(prog="aop_toolkit", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("parse-sop", help="parse an SOP into an intent hypothesis")
    p.add_argument("sop")
    p.add_argument("--out", default="-")

    p = sub.add_parser("mine", help="mine a case corpus")
    p.add_argument("cases", help="JSONL corpus of stitched cases")
    p.add_argument("--authority-map", help="JSON file mapping decision families to authority classes")
    p.add_argument("--out", default="-")

    p = sub.add_parser("compile", help="compile an AOP document")
    p.add_argument("--sop", required=True)
    p.add_argument("--cases", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("lint", help="lint a compiled AOP")
    p.add_argument("aop")
    p.add_argument("--spec-home", default=None, help="path to aop-spec (default: sibling checkout)")

    args = parser.parse_args(argv)

    if args.command == "parse-sop":
        hypothesis = parse_sop(open(args.sop).read())
        _emit(hypothesis, args.out)
        return 0

    if args.command == "mine":
        cases = mining.load_cases(args.cases)
        authority_map = json.load(open(args.authority_map)) if args.authority_map else {}
        result = {
            "variants": mining.mine_variants(cases),
            "decision_rules": mining.extract_decision_rules(cases, authority_map),
            "exception_edges": mining.mine_exceptions(cases),
            "rework_loops": mining.mine_rework_loops(cases),
        }
        _emit(result, args.out)
        return 0

    if args.command == "compile":
        sop = parse_sop(open(args.sop).read())
        cases = mining.load_cases(args.cases)
        manifest = json.load(open(args.manifest))
        doc = compiler.compile_aop(sop, cases, manifest, args.version)
        compiler.write_aop(doc, args.out)
        print("compiled %s %s to %s" % (doc["aop"], doc["version"], args.out), file=sys.stderr)
        return 0

    if args.command == "lint":
        ok, errors = linter.lint(args.aop, args.spec_home)
        if ok:
            print("LINT PASS: %s" % args.aop)
            return 0
        print("LINT FAIL: %s" % args.aop)
        for error in errors:
            print("  - %s" % error)
        return 1


def _emit(obj, out):
    text = json.dumps(obj, indent=2)
    if out == "-":
        print(text)
    else:
        with open(out, "w") as handle:
            handle.write(text + "\n")


if __name__ == "__main__":
    sys.exit(main())
