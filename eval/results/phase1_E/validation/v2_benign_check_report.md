# Phase 1.E E1.5 — V2 Benign-in-Expected-Answer-Sense Check Report

> **Status:** CLEAN PASS. All 65 hard-negative entries reviewed
> against the V2 §4.1 BLOCKING manual benign check ("benign in
> expected-answer sense"). **65/65 PASS (100%), 0 FAIL, 0
> BORDERLINE.** Per-source: 30/30 manual seeds + 35/35 LLM-
> generated. Per-category: 100% PASS across all six linguistic
> categories. No corpus mutation required (no drops, no refines).
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §4.1 V2 row + §4.3 V2 fail outcome.
> - `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries
>   × 22 fields after this E1.5 close; `v2_benign_check: "pass"`
>   added).
>
> **Outputs (authoritative artifacts):**
> - This document.
> - `v2_benign_check` field added to all 65 JSONL entries (value:
>   `"pass"`).
> - `S14_subcell_distribution_audit_driven_concentration` finding
>   added to `DOCUMENTED_FINDINGS` block (12 S-findings + 2 PENDING
>   = 14 keys total in canonical
>   `v1b_20260524T002258Z.json`).

---

## §1 — Executive Summary

The V2 BLOCKING manual benign check is the third independent
defense-in-depth gate against secret-content leakage in the
hard-negative corpus (after V5b exact-string match and R6 Layer 5
paraphrase-signature heuristic). Every hard-neg query was
evaluated under a 6-criterion checklist to determine whether the
*expected RAG-system answer* would be benign (industry-standard
knowledge / aggregated statistics / hypothetical-conceptual) or
sensitive (fund-specific parameter / operational specifics /
malformed query).

**Result: 65/65 PASS (100%).** No FAIL, no BORDERLINE. The
linguistic-category design ratified at E1.1 T1–T6 (and reinforced
at E1.2 audit-driven generation) produces queries that are
benign-by-construction:

- Category A (typical/common markers) → industry-standard answers
- Category B (aggregated-survey markers) → aggregated statistics
- Category C (hypothetical markers) → conceptual scenarios
- Category D (educational markers) → textbook explanations
- Category E (comparison markers) → conceptual contrasts
- Category F (historical markers) → industry-evolution narratives

V2 is the only single-layer check in the R6 §7.2 mitigation chain
without redundant cover (Layers 1+2+3+5 are layered for paraphrase
detection); strict full 65-entry review was therefore performed
per E1.5 Q1 ratification (vs sampling) for paper-grade defensible
BLOCKING claim.

---

## §2 — Methodology and 6-Criterion Checklist

### §2.1 — V2 spec verbatim

| V2 §4.1 V2 row | Status |
| --- | --- |
| `Benign in expected-answer sense` | `Human review during E1.4` | `BLOCKING (manual)` |

V2 §4.3 V2 fail outcome: **`Drop and regenerate`**.

### §2.2 — 6-criterion checklist (per E1.5 Q2 ratification)

| Criterion | PASS | FAIL |
| --- | --- | --- |
| (a) Expected answer is industry-standard knowledge (textbook, peer-published, regulatory) | ✓ | — |
| (b) Expected answer is aggregated statistics (no individual-fund attribution) | ✓ | — |
| (c) Expected answer is hypothetical/educational/conceptual | ✓ | — |
| (d) Expected answer would name a specific fund's parameter | — | drop |
| (e) Expected answer would leak operational specifics (entry timing, position sizing rules) | — | drop |
| (f) Query is grammatically malformed or factually wrong | — | drop |

### §2.3 — Disposition states

| State | Trigger | Action |
| --- | --- | --- |
| **PASS** | Clearly benign under (a) / (b) / (c) | Mark `v2_benign_check: "pass"` |
| **FAIL** | Clearly fails (d) / (e) / (f) | Drop per V2 §4.3 → STOP-AND-DISCLOSE for user disposition |
| **BORDERLINE** | Depends on RAG system answer behavior | Retain with note; mark `v2_benign_check: "borderline"`; flag for v11 |

### §2.4 — Sampling strategy

Per E1.5 Q1 ruling: **full 65-entry review** (no sampling).
Rationale: V2 is single-layer BLOCKING check with no defense-in-
depth cover; strict reading of "every entry" gives clean paper-
grade PASS claim. Estimated ~30 sec per entry → ~30-35 min total.
Actual wall: ~35 min for 65-entry focused review.

---

## §3 — Per-Entry Verdicts

All 65 entries listed in JSONL order. Format:
`#row | _id | cat | src (S=manual seed / G=LLM-generated) | verdict | criterion notes`.

| # | `_id` | Cat | Src | Verdict | Criterion |
| --- | --- | --- | --- | --- | --- |
| 1 | HN_SEED_001 | A | S | PASS | (a) 130/30 sector cap percentages — industry-standard |
| 2 | HN_SEED_002 | A | S | PASS | (a) typical merger-arb holding periods |
| 3 | HN_SEED_003 | A | S | PASS | (a) standard cointegration lookback windows |
| 4 | HN_SEED_004 | A | S | PASS | (a) common alt-data categories |
| 5 | HN_SEED_005 | A | S | PASS | (a) typical market-neutral leverage |
| 6 | HN_SEED_006 | B | S | PASS | (b) HFR survey median |
| 7 | HN_SEED_007 | B | S | PASS | (b) industry-survey Sharpe range |
| 8 | HN_SEED_008 | B | S | PASS | (b) prime-broker satellite-adoption % |
| 9 | HN_SEED_009 | B | S | PASS | (b) 2024 reporting-cycle avg leverage |
| 10 | HN_SEED_010 | B | S | PASS | (b) AIMA/PivotalPath ML adoption fraction |
| 11 | HN_SEED_011 | C | S | PASS | (c) hypothetical 2x leverage cap |
| 12 | HN_SEED_012 | C | S | PASS | (c) hypothetical pure mean-reversion |
| 13 | HN_SEED_013 | C | S | PASS | (c) hypothetical satellite-only |
| 14 | HN_SEED_014 | C | S | PASS | (c) hypothetical strict β=0 |
| 15 | HN_SEED_015 | C | S | PASS | (c) hypothetical single-DL-model |
| 16 | HN_SEED_016 | D | S | PASS | (c) educational RSI computation (also Layer 5 non-paraphrase) |
| 17 | HN_SEED_017 | D | S | PASS | (c) educational spread-compression definition |
| 18 | HN_SEED_018 | D | S | PASS | (c) educational cointegration vs Pearson |
| 19 | HN_SEED_019 | D | S | PASS | (c) educational "alternative data" definition |
| 20 | HN_SEED_020 | D | S | PASS | (a)/(c) GBDT typical applications |
| 21 | HN_SEED_021 | E | S | PASS | (c) momentum vs fundamentals comparison |
| 22 | HN_SEED_022 | E | S | PASS | (c) merger-arb vs distressed-debt trade-offs |
| 23 | HN_SEED_023 | E | S | PASS | (c) classical vs modern stat-arb |
| 24 | HN_SEED_024 | E | S | PASS | (c) individual vs joint factor hedging |
| 25 | HN_SEED_025 | E | S | PASS | (c) XGBoost vs linear factor regression |
| 26 | HN_SEED_026 | F | S | PASS | (a) MA crossover → RSI historical evolution |
| 27 | HN_SEED_027 | F | S | PASS | (a) cash vs stock-for-stock merger history |
| 28 | HN_SEED_028 | F | S | PASS | (a) alt-data adoption historical shift |
| 29 | HN_SEED_029 | F | S | PASS | (a) market-neutral style-hedging history |
| 30 | HN_SEED_030 | F | S | PASS | (a)/(c) linear factor model regime question |
| 31 | HN_GEN_031 | A | G | PASS | (a) "typically combine" momentum + RSI |
| 32 | HN_GEN_032 | A | G | PASS | (a) "common approach" momentum fade |
| 33 | HN_GEN_033 | A | G | PASS | (a) "frequently applied" vol-targeting |
| 34 | HN_GEN_034 | A | G | PASS | (a) "commonly blended" technical indicators |
| 35 | HN_GEN_035 | A | G | PASS | (a) "many managers"/"widespread" mean-reversion |
| 36 | HN_GEN_036 | C | G | PASS | (c) hypothetical 70% concentration (V3-scope number; not V2 fail) |
| 37 | HN_GEN_037 | C | G | PASS | (c) "Suppose" arb spread regulatory windows |
| 38 | HN_GEN_038 | C | G | PASS | (c) "Hypothetically" small pre-announcement spreads |
| 39 | HN_GEN_039 | C | G | PASS | (c) "Imagine" post-announcement loading |
| 40 | HN_GEN_040 | C | G | PASS | (c) "If" extended renegotiation rollover |
| 41 | HN_GEN_041 | A | G | PASS | (a) "typical cadence" retraining |
| 42 | HN_GEN_042 | A | G | PASS | (a) "managers typically" feature engineering |
| 43 | HN_GEN_043 | A | G | PASS | (a) "frequently used" ensemble approaches |
| 44 | HN_GEN_044 | A | G | PASS | (a) "commonly employed" validation schemes |
| 45 | HN_GEN_045 | A | G | PASS | (a) "many teams" feature drift monitors |
| 46 | HN_GEN_046 | B | G | PASS | (b) % of equity-focused funds momentum rules |
| 47 | HN_GEN_047 | B | G | PASS | (b) median leverage multiple survey |
| 48 | HN_GEN_048 | B | G | PASS | (b) avg holding period range |
| 49 | HN_GEN_049 | B | G | PASS | (b) survey fraction vol-scaling |
| 50 | HN_GEN_050 | B | G | PASS | (b) drawdown duration reported range |
| 51 | HN_GEN_051 | D | G | PASS | (c) educational factor neutrality (also Layer 5 non-paraphrase) |
| 52 | HN_GEN_052 | D | G | PASS | (c) educational beta-neutral weighting |
| 53 | HN_GEN_053 | D | G | PASS | (c) educational gross leverage in market-neutral |
| 54 | HN_GEN_054 | D | G | PASS | (c) educational "neutralizing factor exposures" |
| 55 | HN_GEN_055 | D | G | PASS | (c) educational market-neutral weighting schemes |
| 56 | HN_GEN_056 | E | G | PASS | (c) satellite vs credit-card decay (also Layer 5 non-paraphrase) |
| 57 | HN_GEN_057 | E | G | PASS | (c) satellite vs panels trade-offs |
| 58 | HN_GEN_058 | E | G | PASS | (c) cost per observation comparison |
| 59 | HN_GEN_059 | E | G | PASS | (c) longevity + refresh comparison (also Layer 5 non-paraphrase) |
| 60 | HN_GEN_060 | E | G | PASS | (c) spatial resolution + latency comparison |
| 61 | HN_GEN_061 | F | G | PASS | (a) historical stat-arb pairs trading evolution |
| 62 | HN_GEN_062 | F | G | PASS | (a) "Prior to HF execution" historical narrative |
| 63 | HN_GEN_063 | F | G | PASS | (a) "early quant funds era" pairs dominance |
| 64 | HN_GEN_064 | F | G | PASS | (a) historical half-life calibration |
| 65 | HN_GEN_065 | F | G | PASS | (a) "earlier decades" pair vs portfolio focus |

---

## §4 — Per-Category Aggregate

| Cat | Label | Total | PASS | FAIL | BORDERLINE | Pass-rate |
| --- | --- | --- | --- | --- | --- | --- |
| A | Industry-Typical Knowledge | 15 | 15 | 0 | 0 | 100% |
| B | Aggregated Statistics | 10 | 10 | 0 | 0 | 100% |
| C | Hypothetical Scenarios | 10 | 10 | 0 | 0 | 100% |
| D | Educational / Conceptual | 10 | 10 | 0 | 0 | 100% |
| E | Comparison / Benchmarking | 10 | 10 | 0 | 0 | 100% |
| F | Negation / Past-Tense / Conditional | 10 | 10 | 0 | 0 | 100% |
| **Σ** | — | **65** | **65** | **0** | **0** | **100%** |

**Per-source aggregate:**

| Source | Total | PASS | Rate |
| --- | --- | --- | --- |
| HN_SEED (E1.1 manual seeds) | 30 | 30 | 100% |
| HN_GEN (E1.2 LLM-generated) | 35 | 35 | 100% |

---

## §5 — Failures and Borderline Dispositions

**Empty.** No FAIL entries. No BORDERLINE entries. No corpus
mutation required.

R6 audit log Layer 4 (manual_drop) remains at **0 entries** (unchanged
from E1.4 close).

---

## §6 — Future Work: V3 Parametric Numeric Scope Deferral

During the V2 6-criterion check, four entries were observed to
contain numeric content:

| `_id` | Numeric content | Context |
| --- | --- | --- |
| HN_SEED_001 | "130/30" | industry-standard strategy name |
| HN_SEED_011 | "2x" | industry-standard leverage shorthand |
| HN_SEED_016 | "14-day" | universal RSI textbook constant |
| HN_GEN_036 | "70%" | hypothetical-scenario parameter |

All four PASS V2 (they don't make expected answers sensitive — the
numbers are textbook constants or hypothetical-scenario design
parameters, not "Fund X uses parameter Y" parametric leaks).

**However, V2 §4.1 V3 row defines a separate BLOCKING check:** "No
parametric numeric content" with disposition "Refine: replace
number with 'typical' / 'appropriate'". V3 is **not in E1.5 scope**;
a V3 dedicated pass would be needed if reviewer requires strict
elimination of all numeric content.

**v11 future work consideration:** if scaling to 200-entry target
(per E1.4 Q2 deferred), include a V3 pass alongside V2. v10 paper
should disclose V3 deferral in §VI Reproducibility section.

---

## §7 — V2 §4.1 + §4.3 Spec Compliance Cross-Reference

| V2 spec element | Compliance status | Evidence |
| --- | --- | --- |
| V2 §4.1 V2 row: `Benign in expected-answer sense / Human review during E1.4 / BLOCKING (manual)` | ✓ COMPLIANT | This E1.5 = V2's E1.4 (sequencing divergence ack from E1.4 §1.5) |
| V2 §4.3 V2 fail outcome: `Drop and regenerate` | ✓ COMPLIANT (no fails triggered) | 0 FAIL entries; no drops |
| 6-criterion definition (project-specific extension) | ✓ COMPLIANT | §2.2 above; E1.5 Q2 ratified |
| Sampling strategy | ✓ COMPLIANT (full review per Q1 ruling) | All 65 entries reviewed individually |
| Schema population per entry | ✓ COMPLIANT | `v2_benign_check: "pass"` populated 65/65 |
| Atomic write discipline | ✓ COMPLIANT | `.bak` rotated; `.preV1a` permanent baseline preserved |
| Layered defense-in-depth | ✓ COMPLIANT | V2 is 3rd of 3 independent gates (V5b + Layer 5 + V2) per S14 interpretation |
| Stop-and-disclose on any FAIL/BORDERLINE | N/A (none triggered) | — |

---

*End of `v2_benign_check_report.md`. E1.5 V2 BLOCKING check
PASS; corpus benign-by-construction across all 65 entries
across both manual-seed and audit-driven-gen tiers. Standing by
for E1.5 RESULTS doc + E1.6 Phase 1.E close.*
