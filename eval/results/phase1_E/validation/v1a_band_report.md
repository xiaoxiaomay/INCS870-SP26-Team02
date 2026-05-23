# Phase 1.E E1.3.2 — V1a MiniLM Cosine Band Report

> **Status:** E1.3.2 closed 2026-05-22. V1a per-encoder MiniLM
> cosine band validator implemented; 65 hard-negative entries
> populated with measurement fields; 12 outliers retained as
> paper observation per Option B ruling. Four paper-publishable
> findings (S1 / S2 / S5 / S6) plus one pending V2.5 plan-revision
> decision documented in the canonical JSON artifact.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §2.5 (per-encoder bands), §4.1 (V1a
>   BLOCKING status), §5.2 (schema), §5.3 (`target_secret_id`
>   dual-convention).
> - `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries,
>   30 manual seeds + 35 LLM-generated, all `manually_reviewed`).
> - `data/secrets/secrets_v2.jsonl` (90 secrets, 30 L1 + 30 L2 +
>   30 L3; canonical reference per V2 §2.5).
> - `data/index/secrets_v2.faiss` + `secrets_v2_meta.pkl` (MiniLM
>   FAISS IndexFlatIP, pinned revision matches `PINNED_REVISIONS`).
>
> **Canonical artifact:**
> `eval/results/phase1_E/validation/v1a_20260522T013349Z.json`.

---

## §1 — Executive Summary

V1a anchors hard-negative-vs-secret semantic proximity on MiniLM
(pinned revision `c9745ed1d9f2…`) against the 90-entry
`secrets_v2` canonical corpus. All 65 entries were embedded,
FAISS top-K=10 retrieved, post-filtered to L1/L2 tier per V2 §5.3,
and top-1 measurement populated into `closest_secret_id_minilm_90`
+ `closest_cosine_minilm_90`. The `target_secret_id` field is
preserved as author-intent (30/65 populated, manual seeds only)
per V2 §5.2 + §5.3 dual-convention (Option C ratification).
Global BLOCKING [0.40, 0.65]: **53/65 PASS (81.5%)**, 12 outliers
retained per Option B ruling — not "easy negatives" per V2 §2.5
prediction but cross-domain spillover (S1). All four paper
findings (S1 / S2 / S5 / S6) emerged from the investigation cycle.

---

## §2 — Per-Category × Per-Band Distribution

Bands are per V2 §2.2 (per-linguistic-category MiniLM expected
band). `compute_expected_minilm_band(cosine, category)` partitions:
`{< low → "low", [low, high] → "mid", > high → "high"}`.

| Cat | Label | Per-cat band | low | mid | high | n |
| --- | --- | --- | --- | --- | --- | --- |
| A | Industry-Typical Knowledge | [0.45, 0.60] | 3 | 12 | 0 | 15 |
| B | Aggregated Statistics | [0.40, 0.55] | 3 | 7 | 0 | 10 |
| C | Hypothetical Scenarios | [0.45, 0.65] | 6 | 4 | 0 | 10 |
| D | Educational / Conceptual | [0.40, 0.55] | 1 | 3 | **6** | 10 |
| E | Comparison / Benchmarking | [0.50, 0.65] | 2 | 7 | **1** | 10 |
| F | Negation / Past-Tense | [0.45, 0.60] | 6 | 4 | 0 | 10 |
| **Σ** | — | — | **21** | **37** | **7** | **65** |

**Per-category "high" entries** (above per-category cap; relevant
for Finding #3 deferred-to-V1b investigation):
- **D (6 entries):** HN_SEED_016, HN_SEED_017, HN_SEED_018,
  HN_GEN_051, HN_GEN_053, HN_GEN_054. One (`HN_GEN_051`) is
  outside global blocking band as well; five are inside.
- **E (1 entry):** HN_GEN_056. Outside global blocking band as
  well.

Note: D was predicted band-tightest per V2 §2.2 ([0.40, 0.55]
range, the narrowest of the six categories); the empirical 6/10
above-band rate aligns with that prediction but cannot be
disambiguated from systematic MiniLM-specific over-anchoring
until V1b cross-encoder check at E1.3.4.

---

## §3 — Per-Tier Breakdown (Two-Way Reporting per V2 §5.2 + §5.3)

### §3.1 — Author-intent (manual seeds, `target_secret_id`)

| Tier | Count |
| --- | --- |
| L1 | 30 |
| L2 | 0 |
| L3 | 0 (excluded per V2 §5.3) |

All 30 manual seeds anchor to L1 secrets per T4 ruling (E1.1).
LLM-generated entries (n=35) carry `target_secret_id: null` —
author-intent does not apply.

### §3.2 — MiniLM measurement (all 65 entries, `closest_secret_id_minilm_90`)

| Tier | All 65 | Manual seed (n=30) | LLM-generated (n=35) |
| --- | --- | --- | --- |
| L1 | **21** | 12 | 9 |
| L2 | **44** | 18 | 26 |
| L3 | 0 (filtered) | 0 | 0 |

Net: 68% of corpus closest-L1/L2 measurement lands on L2.
LLM-generated cohort is more L2-skewed (74%) than the
manual-seed cohort (60%) — author-intent's L1 anchoring is
echoed measurement-side only 40% of the time on manual seeds
(see §5.4 finding S6).

### §3.3 — Author vs measurement alignment (manual seeds, n=30)

| Comparison | Match | Rate |
| --- | --- | --- |
| Identical secret_id (author `target_secret_id` == MiniLM `closest_secret_id_minilm_90`) | 5/30 | **17%** |
| Same alpha domain | 20/30 | **67%** |
| Same tier (author L1 vs MiniLM L1) | 12/30 | **40%** |

(See §5.4 for the S6 finding interpretation.)

---

## §4 — Outliers Detailed Inventory (n=12; cosine outside [0.40, 0.65])

All 12 outliers retained per Option B ruling. None are paraphrases
of their measured-closest secret (Action 1a content review for the
2 above-band cases; Action 1b pattern analysis for the 10
below-band cases).

### §4.1 — Below-band outliers (n=10; cosine < 0.40)

| `_id` | cos | cat | src | hn_domain | sec_domain | sec_tier | same-domain? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HN_SEED_004 | 0.368 | A | SEED | alternative_data | alternative_data | L1 | **Y** |
| HN_SEED_006 | 0.384 | B | SEED | event_driven | statistical_arbitrage | L2 | N |
| HN_SEED_007 | **0.315** | B | SEED | statistical_arbitrage | event_driven | L2 | N |
| HN_SEED_010 | 0.399 | B | SEED | ml_signals | factor_neutral | L2 | N |
| HN_SEED_013 | 0.399 | C | SEED | alternative_data | factor_neutral | L2 | N |
| HN_SEED_019 | 0.396 | D | SEED | alternative_data | statistical_arbitrage | L1 | N |
| HN_SEED_025 | 0.398 | E | SEED | ml_signals | ml_signals | L1 | **Y** |
| HN_SEED_028 | 0.382 | F | SEED | alternative_data | event_driven | L1 | N |
| HN_GEN_039 | 0.339 | C | GEN | event_driven | statistical_arbitrage | L2 | N |
| HN_GEN_062 | 0.382 | F | GEN | statistical_arbitrage | factor_neutral | L2 | N |

**Same-domain rate within below-band failures: 2/10 (20%).**
Cross-domain mapping dominates — see §5.1 (S1 finding).

### §4.2 — Above-band outliers (n=2; cosine > 0.65)

| `_id` | cos | cat | src | hn_domain | sec_domain | sec_tier | same-domain? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HN_GEN_051 | 0.678 | D | GEN | factor_neutral | factor_neutral | L2 | **Y** |
| HN_GEN_056 | 0.678 | E | GEN | alternative_data | alternative_data | L2 | **Y** |

Both above-band entries are same-domain matches. Action 1a manual
content review confirmed neither is a paraphrase of its measured
secret — both share lexical vocabulary (LLM-generated queries
naturally converge on category-domain vocabulary) but the
question/answer semantics diverge (mechanism-asking vs
system-describing, comparison-axis vs combined-source strategy).
V1b cross-encoder validation (E1.3.4) will determine whether
this above-band concentration is MiniLM-specific or systematic.

### §4.3 — Aggregate by source (E1.1 manual vs E1.2 LLM-generated)

| Source | Below-band | Above-band | Total | Total n | Fail rate |
| --- | --- | --- | --- | --- | --- |
| HN_SEED (E1.1 manual) | 8 | 0 | 8 | 30 | **26.7%** |
| HN_GEN (E1.2 LLM-gen) | 2 | 2 | 4 | 35 | **11.4%** (below-band: 5.7%) |
| Total | 10 | 2 | 12 | 65 | 18.5% |

(See §5.2 — S2 finding.)

---

## §5 — Documented Findings (paper-grade observations)

The four findings below are embedded verbatim in the canonical
JSON artifact's `documented_findings` block. They emerged from
the V1a investigation cycle and are ratified for v10 paper
inclusion.

### §5.1 — S1: Cross-Domain Spillover (new failure mode)

Hard-negative corpus geometry interacts with secret corpus
coverage in a previously unmodeled way. When a hard-negative's
authored linguistic domain has insufficient vocabulary-aligned
secrets, FAISS top-1 lookup crosses domain boundaries, resulting
in cosine values below the expected per-encoder band. This
"cross-domain spillover" is structurally distinct from V2 §2.5's
anticipated "easy negative" failure mode and represents a
corpus-coverage finding (`secrets_v2` has ~5 entries per
domain × level), not a query-quality failure.

**Evidence:** 80% (8/10) of below-band hard-negatives map via
MiniLM top-1 to a v2 secret in a *different* alpha domain than
the hard-neg's authored domain. Cross-domain mapping is the
dominant mechanism for cosine < 0.40 in this corpus.

### §5.2 — S2: Audit-Framework Efficacy

Audit-driven hard-negative generation produces tighter MiniLM
band centrality than manual seed authoring. Manual E1.1 seeds
show **26.7% (8/30)** below-band failure rate; LLM-generated
E1.2 entries show **5.7% (2/35)**, a **5× improvement**
attributable to the per-category anti-pattern audit and prompt
scaffolding. This is empirical evidence that the audit framework
has measurable corpus-quality impact, not just theoretical
separation. Per V2 §2.2 specification, the LLM-generated cohort
more reliably lands within expected per-category bands.

### §5.3 — S5: Length Non-Signal

Query length is not a band-failure discriminator. Below-band
queries (mean **134 chars**) show no meaningful length difference
from corpus baseline (mean **138 chars**). Failures correlate
with domain-secret coverage gaps, not query verbosity.

### §5.4 — S6: Author-Intent vs Encoder-Measurement Divergence

**Type:** author-intent vs encoder-measurement alignment.

**Summary:** Author-intent `target_secret_id` (manual seeds,
n=30) vs MiniLM-measured `closest_secret_id_minilm_90` show
divergence at three semantic layers: **17% exact-secret match,
67% same-alpha-domain, 40% same-tier alignment**.

**Interpretation:** Manual seed authors operate at domain-level
semantic intuition (67% domain alignment) but cannot reliably
target the exact most-similar secret (17% exact match). This
mechanistically explains the S2 finding (audit-driven generation
5× lower below-band fail rate): authors lack the semantic-
precision intuition that LLM-with-domain-vocabulary-injection
provides.

**Paper implication:** Provides "author-intuition vs
encoder-measurement" axis for methodology rigor. Reviewer-grade
evidence that the audit framework operates at semantic-precision
level beyond human authorial intuition.

**Emerged from:** V2 §5.2 + §5.3 dual-field schema (Option C
ratification 2026-05-22) — both `target_secret_id` (author
intent) and `closest_secret_id_minilm_90` (validator measurement)
preserved in same record, enabling direct comparison.

---

## §6 — PENDING Decisions

### §6.1 — PENDING_V2_5_PLAN_REVISION

V2.5 plan-revision consideration for the **S1 cross-domain
spillover failure mode**. The V2 §2.5 rejection table prescribes
remediation only for "easy negative" (cosine < 0.40) under the
assumption that low cosine = query too off-manifold. S1 surfaces
a structurally distinct cause: insufficient same-domain secret
coverage. Awaiting V1b (multi-encoder) + V5b (exact-match) results
before deciding plan-revision vs paper-only documentation. To be
resolved at E1.3.7 results write-up or E1.6 Phase 1.E close.

### §6.2 — PENDING_V2_5_SCHEMA_REVISION (forward reference to E1.3.4)

V2 §5.2 schema describes `closest_secret_id (4 × 2)` implying
4 encoders × 2 corpora. Pre-flight check for E1.3.4 surfaced
that the 60-entry (`secrets.jsonl`) and 90-entry (`secrets_v2.jsonl`)
corpora are **disjoint** (zero overlap), with the 60-entry
corpus being a legacy pre-v2 reference (`S0001`-format IDs) and
the 90-entry being the v2 canonical (`v2_L<n>_<domain>_<NNN>`).
The 60-entry tier distribution (L1=0, L2=10, L3=50) makes the
V2 §5.3 L1+L2 filter degenerate against it. E1.3.4 implements
4 encoders × **90-entry only**; 60-entry comparison is deferred
to a v10 §VI reproducibility appendix or future V1c sub-step.
Plan-revision consideration pending. *(See E1.3.4 forward
reference in §8 below.)*

---

## §7 — Methodology Note: V2 §5.2 + §5.3 Dual-Field Schema (Option C)

The Phase 1.E E1.3.2 implementation adheres strictly to the V2
§5.2 + §5.3 dual-convention as ratified in Option C
(2026-05-22). The schema preserves two distinct semantic axes
on each hard-negative record:

| Field | Semantics | Populated by |
| --- | --- | --- |
| `target_secret_id` | **Author intent** — the secret the seed author intuited as most semantically near. Per V2 §5.3: "picked by the author at seed time or by `closest_secret_id["minilm_90"]` for LLM-generated." | Author at E1.1 seeding (manual seeds); `null` for LLM-generated. **Validator does NOT mutate this field.** |
| `closest_secret_id_<encoder>_<corpus>` | **Validator measurement** — FAISS top-1 result for the given encoder × corpus combination after L1/L2 filter (V2 §5.3). One field per encoder × corpus. | Validator (`scripts/validate_hard_negatives.py --run-v1a`); read-only after write. |
| `closest_cosine_<encoder>_<corpus>` | **Raw cosine value** — companion field for audit-trail reproducibility. Band classification is re-derivable from raw cosine + per-category bands without re-running FAISS. | Validator. |
| `expected_minilm_band` | **Per-category band classification** — derived from MiniLM cosine + V2 §2.2 per-category bands. One of `{"low", "mid", "high"}`. MiniLM-specific (V2 §2.2 defines bands only for the anchor encoder). | Validator. |

This split was ratified after the Option A/B/C three-way debate
(2026-05-22). Option A (don't-overwrite-only) preserved author
intent but lacked the measurement field. Option B (overwrite-all)
matched the original Q4 ratification but silently overwrote 30
author-set values, violating V2 §5.3. **Option C** introduces the
measurement-side `closest_*` fields as a separate axis, honoring
both V2 §5.2 (schema) and V2 §5.3 (dual-convention) without
information loss.

This is also the schema convention that **enabled the S6 finding**
(see §5.4): without both axes simultaneously preserved on the
same record, the author-intent-vs-encoder-measurement comparison
would not have been computable.

---

## §8 — Forward References to E1.3.4 (V1b Multi-Encoder)

The S7 corpus-disjointness finding (referenced in §6.2) emerged
during E1.3.4 pre-flight verification on 2026-05-22 immediately
after E1.3.2 close. It is documented here as a forward-reference
because:

1. It does NOT affect the V1a measurement values (V1a is MiniLM
   × 90-entry only — corpus-disjointness has no impact on V1a).
2. It DOES affect the V2 §5.2 "4×2" schema interpretation —
   E1.3.4 scope was revised to 4 encoders × 90-entry only,
   deferring 60-entry to a v10 §VI reproducibility appendix.
3. It will be appended to `DOCUMENTED_FINDINGS` in the V1b
   output JSON (anticipated `v1b_*.json` artifact, 2026-05-22+).

**Update (post-E1.3.4 close, 2026-05-22):** V1b multi-encoder
execution completed; four additional findings emerged during
cross-encoder analysis and are documented in
`v1b_<timestamp>.json` + the validator's `DOCUMENTED_FINDINGS`
block. They are forward-pointers from this V1a report:

- **S8 — mpnet expected-band prediction-miss.** Observed mean
  cosine 0.4725 exceeds V2 §2.5 predicted midpoint 0.295 by
  +0.18, unambiguously triggering V2 §4.4's substantial-
  deviation threshold. Per Q1 STRICT-with-paper-escalation
  ruling, the prediction-miss is documented as v10 contribution
  (no post-hoc re-anchor); V2.5 plan revision triggered.
- **S9 — bge_large band permissiveness (null result).** All
  65/65 entries pass bge_large's [0.45, 0.90] window with
  observed mean 0.7034. Informative null result; V2.5 may
  consider tightening to ~[0.60, 0.80] OR documenting bge_large
  as the most permissive encoder-family member.
- **S10 — encoder-family consensus is structurally weak.** Only
  9/65 (13.8%) entries have all 4 encoders pick the same
  closest secret; 11/65 (16.9%) have all 4 encoders pick
  completely different secrets. Reviewer-clarifying methodology
  note distinguishing "semantic-band consistency" (what V1b
  checks) from "secret-id consensus" (what V1b does NOT check).
- **S11 — Cat D + Cat E dominate cross-encoder above-band
  outliers.** Multi-encoder confirms V2 §2.2 prediction that
  D is band-tightest; pattern is structural to linguistic-
  category × secret-corpus geometry, not MiniLM artifact.

`PENDING_V2_5_PLAN_REVISION` was updated to reference S1 + S8 + S9
as constituent items pending E1.3.7 / E1.6 ruling.

The full S7-S11 entry texts + both PENDING blocks are
authored in the E1.3.4 validator extension (see
`scripts/validate_hard_negatives.py:DOCUMENTED_FINDINGS` block
post-V1b update).

---

## §9 — Reproducibility Provenance

### §9.1 — Pinned components

| Component | Pin | Source |
| --- | --- | --- |
| MiniLM encoder | `sentence-transformers/all-MiniLM-L6-v2 @ c9745ed1d9f207416be6d2e6f8de32d1f16199bf` | `core/config_loader.py:PINNED_REVISIONS` |
| FAISS index | `data/index/secrets_v2.faiss` (138285 bytes, IndexFlatIP, dim=384) | Phase 1.F M2 build (2026-05-09; `eval/results/phase1_F/build_log.json` `index_md5=a03fa690...`) |
| Secrets corpus | `data/secrets/secrets_v2.jsonl` (90 entries, 30 L1 + 30 L2 + 30 L3) | Phase 1.D close |
| Hard-neg corpus | `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries) | Phase 1.E E1.2 close |

### §9.2 — Validator script

- `scripts/validate_hard_negatives.py` (527 LOC)
- `TOP_K = 10` (post-filter buffer for L1/L2 tier filter)
- Atomic write with `.bak` rotation; `.preV1a` permanent baseline
  preserved as user-side snapshot of pre-V1a clean state.

### §9.3 — Run artifacts

- `eval/results/phase1_E/validation/v1a_20260522T010429Z.json` —
  historical (TOP_K=5, target_secret_id overwrite path).
- `eval/results/phase1_E/validation/v1a_20260522T012840Z.json` —
  TOP_K=10 + Option C dual-field (canonical until S6 added).
- **`eval/results/phase1_E/validation/v1a_20260522T013349Z.json`
  — CANONICAL FINAL** (TOP_K=10, Option C, 5 documented_findings).

### §9.4 — Cost and wall time

- LLM cost: **$0** (local FAISS + sentence-transformers only).
- Wall time: ~7 seconds per V1a run (encoding 65 queries +
  FAISS search + atomic write).

---

*End of `v1a_band_report.md`. E1.3.2 milestone PASS; E1.3.3
markdown report close-out. Standing by for E1.3.4 V1b
multi-encoder implementation.*
