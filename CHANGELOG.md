# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning is semantic: the major version changes when the compile contract changes, the minor version when substantive toolchain content is added, and the patch version for corrections that do not change meaning.

## [Unreleased]

## [0.1.0] - 2026-11-04

### Reference toolchain

- Published the SOP parser: structured SOP markdown to intent hypothesis, carrying the claimed rules and escalation prose that observation tests (NM-INT-3).
- Published the variant miner: action-signature grouping with frequencies, discriminating-trigger heuristic, and provenance (NM-STR-1 to NM-STR-3).
- Published the decision-rule extractor: threshold normalisation with observed spread, provenance, and authority classes from the governance manifest, failing closed to prohibited for unmapped families (NM-AUT-3).
- Published the compiler: manifest-carried governance bounds, mined structure, provenance block, fallback rule for paths without fired decisions, and DEA catalog process alignment passed through with the reference-or-gap rule (NM-INT-4, NM-INT-5).
- Published the linter: schema and semantic validation reusing the shared `aop-spec` reference validator, plus toolkit lints for identifier hygiene and permitted-set coverage.
- Published the CLI and the fixture chain: source SOP, 40-case observed corpus, governance manifest, and the compiled fixture AOP that lints clean.

[Unreleased]: https://github.com/agentic-operating-procedure/aop-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/agentic-operating-procedure/aop-toolkit/releases/tag/v0.1.0
