"""AOP linter: lint an AOP document against the schema and the conformance clauses.

The lint re-uses the shared reference validator from aop-spec (the single
authority for the schema and the semantic checks) and adds toolkit-level
lints that the validator does not carry: identifier hygiene and variant
coverage of the SOP's claimed steps.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

DEFAULT_SPEC_HOME = os.environ.get("AOP_SPEC_HOME", str(Path(__file__).resolve().parent.parent.parent / "aop-spec"))


def _load_validator(spec_home: str):
    validator_path = Path(spec_home) / "validation" / "validate.py"
    if not validator_path.exists():
        raise FileNotFoundError("reference validator not found under %s (set AOP_SPEC_HOME)" % spec_home)
    spec = importlib.util.spec_from_file_location("aop_spec_validate", validator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lint(aop_path: str, spec_home: str = None) -> tuple[bool, list[str]]:
    """Return (conformant, diagnostics). Exits non-zero through the CLI on failure."""
    spec_home = spec_home or DEFAULT_SPEC_HOME
    validator = _load_validator(spec_home)
    doc = json.loads(Path(aop_path).read_text())

    diag = validator.Diagnostics()
    schema = json.loads((Path(spec_home) / "schema" / "aop-document.schema.json").read_text())
    validator.validate(doc, schema, schema, "", diag)
    if diag.ok():
        validator.normative_checks(doc, diag)

    # Toolkit lints beyond the validator.
    variant_ids = [v["id"] for v in doc.get("structure", {}).get("variants", [])]
    if len(variant_ids) != len(set(variant_ids)):
        diag.add("$", "lint: duplicate variant identifiers")

    for variant in doc.get("structure", {}).get("variants", []):
        for step in variant.get("steps", []):
            permitted = doc.get("constraints", {}).get("permitted_actions", [])
            prohibited = doc.get("constraints", {}).get("prohibited_actions", [])
            if step in prohibited:
                diag.add("$", "lint: variant %s step %r is a prohibited action" % (variant["id"], step))
            if permitted and step not in permitted:
                diag.add("$", "lint: variant %s step %r is not in the permitted set (NM-CON-1)" % (variant["id"], step))

    return diag.ok(), diag.errors
