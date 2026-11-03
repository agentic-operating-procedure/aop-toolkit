# AOP Reference Toolchain (Toolkit Scope)

Informative. This document describes the reference implementation: which pipeline stage each module implements, the mining heuristics and their limits, and the contract the compiler honours. The normative requirements come from `aop-spec`; the graph semantics come from `aop-context-graph`.

## 1. Pipeline stage mapping

| Pipeline stage (`aop-architecture`) | Module | Input | Output |
|---|---|---|---|
| Observe (substrate side) | not implemented here | declared capture surfaces | stitched cases (`aop-context-graph` shape) |
| Model: read the hypothesis | `parser.py` | SOP markdown in the reference convention | intent hypothesis (objective, scope, claimed rules, escalation prose) |
| Model: read the observation | `mining.py: load_cases` | case corpus JSONL | case objects |
| Compile: variant mining | `mining.py: mine_variants` | cases | variants with frequencies, triggers, provenance |
| Compile: rule extraction | `mining.py: extract_decision_rules` | cases + authority map | rules with thresholds and provenance |
| Compile: exception patterns | `mining.py: mine_exceptions` | cases | exception edges with target roles |
| Compile: rework loops | `mining.py: mine_rework_loops` | cases | loops with observed bounds |
| Compile: assembly | `compile.py: compile_aop` | hypothesis + cases + manifest | AOP document against the `aop-spec` schema |
| Lint | `lint.py` | AOP document | conformance verdict with diagnostics |

## 2. The mining heuristics and their limits

The reference miner is deliberately simple, and its limits are stated so nobody mistakes them for semantics:

- **Variants are action-signature groups.** Two cases with the same ordered action sequence are the same variant, whatever their context. Context that differentiates work with the same shape (for example, who authorised the dispatch) is invisible to this miner. The trigger heuristic therefore reports a residual pattern for the dominant variant when no context attribute separates it purely.
- **Triggers come from the highest-purity separating context attribute.** The heuristic looks for a single attribute value present in every case of the variant and no case outside it. It is a reference heuristic, not the method `aop-evaluation` will measure.
- **Thresholds are majority-voted from observed decision strings.** Where humans decided with different thresholds, the most frequent observed value wins and the spread is retained in `observed_thresholds`. A wide spread is itself signal: it usually means two populations were mined as one.
- **Authority never comes from observation.** The authority class per decision family is read from the governance manifest. Unmapped families land as `prohibited`, which is the fail-closed direction.
- **Rework loops are observed repeats.** The bound is the observed maximum. The compile cannot see loops that observation did not survive to repeat.

A production miner replaces the heuristics, not the contract: the output shape, the provenance obligations, and the governance boundary stay as they are here.

## 3. The compile contract

The compiler honours these obligations regardless of the miner:

- TK-1: The output validates against the `aop-spec` schema. A compile that cannot produce a conformant document fails (ARC-P3).
- TK-2: Every variant carries decision rules. Where no rule fired on a path, the compiler closes coverage with a fallback rule carrying the manifest's default authority class (NM-AUT-3).
- TK-3: Every rule carries observed provenance: the case count and the path frequency (NM-PRV-3).
- TK-4: Governance bounds come only from the manifest; observation contributes none of them.
- TK-5: The output carries the provenance block: the graph source reference, the observed case count, the variant count, the recalibration date, and the source SOP where one exists (NM-PRV-1, NM-PRV-2).
- TK-6: The output is a new version, never an edit (NM-VER-2).

## 4. Relationship to the DEA catalogs

The manifest may carry a `process_alignment` block (NM-INT-4 to NM-INT-5): a reference to the OpenDEA Business Process Catalog entry for the procedure, or an explicit gap, plus metric bindings to the OpenDEA metrics catalog by `dea:metric-*` reference or declared gap. The compiler copies that block through; it does not resolve or invent identifiers. Gap declarations flow through the substrate's gap work queue (CG-PA-5 to CG-PA-6).
