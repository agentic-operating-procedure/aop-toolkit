# AOP Toolkit

`aop-toolkit` is the single authority for the executable toolchain of the observe, model, compile, execute pipeline: the SOP parser, the variant miner, the decision-rule extractor, the AOP compiler, the linter, and the client SDK surface.

| Field | Value |
|---|---|
| Authority | The toolchain: parsing, mining, extraction, compilation, linting |
| Tier | Tooling |
| Landing wave | 4 |
| Version | 0.3.0 |
| Status | Stable |
| Licence | MIT |

## What this repository owns

- The SOP parser: reads a structured Standard Operating Procedure into a lightweight intent hypothesis, the claim about the work that observation will now test (NM-INT-3).
- The variant miner: groups observed cases into variants with frequencies, discriminating triggers, and provenance (NM-STR-1 to NM-STR-3).
- The decision-rule extractor: normalises observed decisions into rules with thresholds, and attaches observed provenance and the authority class from the governance manifest (NM-STR-4 to NM-STR-5).
- The compiler: assembles a conformant AOP document from the hypothesis, the mined structure, and the domain governance manifest, with a provenance block (NM-PRV-1 to NM-PRV-3).
- The linter: validates a compiled AOP against the `aop-spec` schema and clauses, and adds toolkit-level lints (identifier hygiene, permitted-set coverage of variant steps).
- The CLI (`python3 -m aop_toolkit`), which is also the client SDK surface for v0.1.0.

## What this repository does not own

- The schema being compiled to, or the conformance clauses. That is `aop-spec`.
- The graph being mined: the entity model, the stitching semantics, the case schema. That is `aop-context-graph`.
- The runtime that executes the compiled AOP. That is `aop-reference-harness`.
- The catalogue that publishes it. That is `aop-registry`.

## The governance boundary in the compiler

Observation says what humans decided. The owner says what the agent may decide. The compiler takes the structure (variants, rules, thresholds, exception patterns) from the case corpus, and takes the governance bounds (permitted set, prohibited set, risk axes, authority classes, skills, coordination, control, assurance) from the governance manifest. The miner never invents an authority class: where the manifest does not map a decision family, the rule lands as `prohibited` (NM-AUT-3).

## Reference toolchain walkthrough

```
fixtures/sop/rb-line-001.md                          the source SOP (v12)
fixtures/cases/fault-management-cases.jsonl          40 observed cases, stitched
fixtures/manifests/fault-management.json             the governance manifest

python3 scripts/generate_cases.py                    regenerate the corpus
python3 -m aop_toolkit parse-sop fixtures/sop/rb-line-001.md
python3 -m aop_toolkit mine fixtures/cases/fault-management-cases.jsonl --authority-map <json>
python3 -m aop_toolkit compile --sop ... --cases ... --manifest ... --version v0.1.0 --out aop.json
python3 -m aop_toolkit lint aop.json
```

The compiled fixture AOP carries a `process_alignment` block with declared gaps (NM-INT-4, NM-INT-5): the enterprise process catalog has no canonical network fault management entry yet, and the metrics catalog has no canonical MTTR or first-pass metric yet. The gaps are the work queue, not silence.

## Documentation

| Document | Scope |
|---|---|
| [The reference toolchain](./docs/aop-reference-toolchain-toolkit-scope.md) | Pipeline stage mapping, the mining heuristics and their limits, and the compile contract |
