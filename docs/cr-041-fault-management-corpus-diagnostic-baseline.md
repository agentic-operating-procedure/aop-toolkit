# CR-041 Fault-Management Corpus Diagnostic Baseline

**Purpose:** Reproducible descriptive baseline only. This report does not adjudicate event classes, procedure branches, or correct source data.  
**Corpus:** `fixtures/cases/fault-management-cases.jsonl`  
**Corpus Git blob SHA:** `942587be2a79dba480208d490a9d7767911426f8`  
**Toolkit main commit inspected:** `a98b35d734046ba1f3180cd3d32983f5bfe330e9`  
**Validator source blob SHA:** `be8d123e3888812b4cc6b1de43e50f430b55bc92`  
**Diagnostic date:** 2026-11-26

## Method

The baseline was computed directly from all non-empty JSONL records in the pinned corpus. Step timestamps were flattened in their existing task/array order. ISO timestamps ending in `Z` were parsed as UTC. A step was counted before the case when its parsed instant was strictly earlier than `started_at`, and after the case when strictly later than `ended_at`. A case was non-monotonic when any adjacent timestamps in listed array order decreased. Elapsed duration was `(ended_at - started_at)` in minutes. Difference is `declared cycle_time - elapsed minutes`.

These are mechanical comparisons, not a decision that all steps must fall inside the case interval or that listed order must be chronological. The existing validator treats `cycle_time` as numeric minutes and compares it with elapsed boundary duration; that implementation interpretation is not independently inferred from the corpus.

## Aggregate findings

| Measure | Result |
|---|---:|
| JSONL cases | 40 |
| Total steps | 204 |
| Cases with at least one step before start | 35 |
| Cases with at least one step after end | 36 |
| Cases with at least one step outside boundaries | 40 |
| Cases with non-monotonic listed timestamps | 36 |
| Cases where declared cycle_time differs from elapsed boundary duration | 40 |
| Cases with negative elapsed boundary duration (end before start) | 20 |
| Timestamp strings all end in Z | Yes |

## Reconciliation with CR-041

CR-041 reports 35/40 cases with an event earlier than start, 36/40 later than end, 36/40 non-monotonic, and 40/40 duration mismatches. This pinned rerun reproduces all four counts exactly. The earlier AO-WE-001 summary that 40/40 cases have at least one out-of-bound event is the union of the before-start and after-end case sets; it is not contradictory to the two separate CR-041 counts. The prior concern about an aggregate-count discrepancy is therefore resolved for these measures and this corpus blob.

## Case-level diagnostic table

| Case | Start | End | Steps | Before | After | Listed timestamps non-monotonic | Elapsed min | Declared cycle_time | Difference min |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| FM-2026-11-0001 | 09:01Z | 09:17Z | 5 | 0 | 4 | Yes | 16 | 76 | 60 |
| FM-2026-11-0002 | 10:02Z | 10:19Z | 5 | 0 | 4 | Yes | 17 | 77 | 60 |
| FM-2026-11-0003 | 11:03Z | 11:21Z | 5 | 0 | 3 | Yes | 18 | 78 | 60 |
| FM-2026-11-0004 | 12:04Z | 12:23Z | 5 | 0 | 3 | Yes | 19 | 79 | 60 |
| FM-2026-11-0005 | 13:05Z | 13:25Z | 5 | 0 | 3 | Yes | 20 | 80 | 60 |
| FM-2026-11-0006 | 14:06Z | 14:27Z | 7 | 1 | 4 | Yes | 21 | 81 | 60 |
| FM-2026-11-0007 | 15:07Z | 15:34Z | 5 | 1 | 3 | Yes | 27 | 147 | 120 |
| FM-2026-11-0008 | 08:08Z | 08:46Z | 5 | 1 | 2 | Yes | 38 | 98 | 60 |
| FM-2026-11-0009 | 09:09Z | 09:53Z | 4 | 1 | 0 | No | 44 | 104 | 60 |
| FM-2026-11-0010 | 10:10Z | 10:35Z | 5 | 1 | 3 | Yes | 25 | 85 | 60 |
| FM-2026-11-0011 | 11:11Z | 11:37Z | 5 | 1 | 3 | Yes | 26 | 86 | 60 |
| FM-2026-11-0012 | 12:12Z | 12:39Z | 5 | 1 | 3 | Yes | 27 | 87 | 60 |
| FM-2026-11-0013 | 13:13Z | 13:41Z | 5 | 1 | 3 | Yes | 28 | 88 | 60 |
| FM-2026-11-0014 | 14:14Z | 14:43Z | 5 | 1 | 3 | Yes | 29 | 89 | 60 |
| FM-2026-11-0015 | 15:15Z | 15:45Z | 5 | 1 | 2 | Yes | 30 | 90 | 60 |
| FM-2026-11-0016 | 08:16Z | 08:47Z | 7 | 2 | 1 | Yes | 31 | 91 | 60 |
| FM-2026-11-0017 | 09:17Z | 09:54Z | 5 | 1 | 1 | Yes | 37 | 157 | 120 |
| FM-2026-11-0018 | 10:18Z | 10:06Z | 5 | 1 | 4 | Yes | -12 | 108 | 120 |
| FM-2026-11-0019 | 11:19Z | 11:13Z | 4 | 1 | 3 | No | -6 | 114 | 120 |
| FM-2026-11-0020 | 12:20Z | 12:55Z | 5 | 1 | 0 | Yes | 35 | 95 | 60 |
| FM-2026-11-0021 | 13:21Z | 13:57Z | 5 | 2 | 0 | Yes | 36 | 96 | 60 |
| FM-2026-11-0022 | 14:22Z | 14:59Z | 5 | 2 | 0 | Yes | 37 | 97 | 60 |
| FM-2026-11-0023 | 15:23Z | 15:01Z | 5 | 2 | 5 | Yes | -22 | 98 | 120 |
| FM-2026-11-0024 | 08:24Z | 08:03Z | 5 | 2 | 5 | Yes | -21 | 99 | 120 |
| FM-2026-11-0025 | 09:25Z | 09:05Z | 5 | 2 | 4 | Yes | -20 | 100 | 120 |
| FM-2026-11-0026 | 10:26Z | 10:07Z | 7 | 3 | 6 | Yes | -19 | 101 | 120 |
| FM-2026-11-0027 | 11:27Z | 11:14Z | 5 | 2 | 4 | Yes | -13 | 167 | 180 |
| FM-2026-11-0028 | 12:28Z | 12:01Z | 5 | 2 | 5 | Yes | -27 | 93 | 120 |
| FM-2026-11-0029 | 13:29Z | 13:13Z | 4 | 2 | 3 | No | -16 | 104 | 120 |
| FM-2026-11-0030 | 14:30Z | 14:15Z | 5 | 2 | 4 | Yes | -15 | 105 | 120 |
| FM-2026-11-0031 | 15:31Z | 15:17Z | 5 | 2 | 4 | Yes | -14 | 106 | 120 |
| FM-2026-11-0032 | 08:32Z | 08:19Z | 5 | 2 | 4 | Yes | -13 | 107 | 120 |
| FM-2026-11-0033 | 09:33Z | 09:21Z | 5 | 2 | 3 | Yes | -12 | 108 | 120 |
| FM-2026-11-0034 | 10:34Z | 10:23Z | 5 | 2 | 3 | Yes | -11 | 109 | 120 |
| FM-2026-11-0035 | 11:35Z | 11:25Z | 5 | 2 | 3 | Yes | -10 | 110 | 120 |
| FM-2026-11-0036 | 12:36Z | 12:27Z | 7 | 4 | 4 | Yes | -9 | 111 | 120 |
| FM-2026-11-0037 | 13:37Z | 13:04Z | 5 | 2 | 5 | Yes | -33 | 147 | 180 |
| FM-2026-11-0038 | 14:38Z | 14:21Z | 5 | 2 | 3 | Yes | -17 | 103 | 120 |
| FM-2026-11-0039 | 15:39Z | 15:33Z | 4 | 3 | 1 | No | -6 | 114 | 120 |
| FM-2026-11-0040 | 08:40Z | 08:35Z | 5 | 2 | 3 | Yes | -5 | 115 | 120 |

## Important limitations and unresolved decisions

1. A timestamp before start or after end may be a legitimate pre-run observation, delayed capture, post-run evidence, handoff, or a defect. The corpus does not encode enough temporal-field identity to decide which without source/domain adjudication.
2. Non-monotonic array order is not automatically invalid until array order's normative meaning is established. It does show that array position cannot safely be assumed to be event chronology for this corpus.
3. The negative elapsed durations (20 cases) are intrinsically incompatible with a positive elapsed-cycle interpretation, but their intended correction must be sourced, not guessed.
4. The 40 declared values are not equal to direct elapsed boundary duration. The existing validator interprets the declared unit as minutes. The source procedure/metric owner must confirm whether this is the intended metric or whether the field is misnamed/misdefined.
5. All inspected timestamp strings use UTC `Z`; this does not establish the source systems' original timezone or capture semantics.
6. No case records have been modified, reordered, clipped, or regenerated.

## Reproduction

From the toolkit repository root:

```sh
python3 scripts/validate_case_cycle_time.py fixtures/cases/fault-management-cases.jsonl
python3 -m unittest discover -s tests -p 'test_*.py'
```

The first command is expected to fail while the source corpus remains unreconciled. The second validates the validator/generator regression tests; it does not prove the corpus itself is valid.

## Next decisions

- Domain owner classifies timestamp semantics and legitimate pre/post-run event types.
- Domain owner confirms whether `cycle_time` is elapsed end-to-end duration or another measure.
- Toolkit owner expands validation only after the Context Graph semantic disposition; no automated fixture rewrite is authorized by this baseline.
