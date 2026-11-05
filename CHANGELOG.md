# Changelog

All notable changes to this repository are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning is semantic: the major version changes when the compile contract changes, the minor version when substantive toolchain content is added, and the patch version for corrections that do not change meaning.

## [Unreleased]

## [v0.3.0] - 2026-11-05

### Added (Wave H3: CR-021)

- The build attestation: every compiled AOP carries the compiler version, builder identity, and the input digests (SOP, corpus, manifest) per NM-VER-7.


## [0.2.0] - 2026-11-05

### Added (CR-009 block 1)

- Ratification stamping from the manifest (NM-AUT-7): only manifest-ratified rules grant authority; below-support and low-confidence rules are capped (NM-STR-18, NM-PRV-6).
- Rare-but-critical variants exempt from frequency pruning (NM-STR-19).
- Stitching confidence propagation into variant provenance.
- Policy-conflict flagging where the SOP's claimed authority differs from the manifest's.
- Support-floor warnings at compile time.


## [0.2.0] - 2026-11-05

### Added (CR-009 block 1)

- Ratification stamping from the manifest (NM-AUT-7): only manifest-ratified rules grant authority; below-support and low-confidence rules are capped (NM-STR-18, NM-PRV-6).
- Rare-but-critical variants exempt from frequency pruning (NM-STR-19).
- Stitching confidence propagation into variant provenance.
- Policy-conflict flagging where the SOP's claimed authority differs from the manifest's.
- Support-floor warnings at compile time.


## [0.1.1] - 2026-11-04

### Fixed

- The decision-rule extractor keeps observed conditions verbatim. Truncating a compound condition (for example, degradation above threshold AND active outage) to its first numeric comparison dropped the rest of the guard and could let the rule fall through to prohibited with a truncated condition. Found by the 5G exemplar chain; the fault management chain was re-run unchanged.


## [0.1.0] - 2026-11-04

### Reference toolchain

- Published the SOP parser: structured SOP markdown to intent hypothesis, carrying the claimed rules and escalation prose that observation tests (NM-INT-3).
- Published the variant miner: action-signature grouping with frequencies, discriminating-trigger heuristic, and provenance (NM-STR-1 to NM-STR-3).
- Published the decision-rule extractor: threshold normalisation with observed spread, provenance, and authority classes from the governance manifest, failing closed to prohibited for unmapped families (NM-AUT-3).
- Published the compiler: manifest-carried governance bounds, mined structure, provenance block, fallback rule for paths without fired decisions, and DEA catalog process alignment passed through with the reference-or-gap rule (NM-INT-4, NM-INT-5).
- Published the linter: schema and semantic validation reusing the shared `aop-spec` reference validator, plus toolkit lints for identifier hygiene and permitted-set coverage.
- Published the CLI and the fixture chain: source SOP, 40-case observed corpus, governance manifest, and the compiled fixture AOP that lints clean.

[Unreleased]: https://github.com/agentic-operating-procedure/aop-toolkit/compare/v0.3.0...HEAD
[v0.3.0]: https://github.com/agentic-operating-procedure/aop-toolkit/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/agentic-operating-procedure/aop-toolkit/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/agentic-operating-procedure/aop-toolkit/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/agentic-operating-procedure/aop-toolkit/releases/tag/v0.1.0
