# Phase 1.E — Hard-Negative FPR Set: Implementation Plan (V2)

> **V2 revision** of `PHASE_1E_PLAN.md` (V1, dated 2026-05-11
> morning). V2 incorporates the user's three Tension rulings,
> three required revisions, and per-item ratifications of all
> 10 §14 approval gates (locked 2026-05-11 afternoon).
>
> - **Tension #1 ruling:** Hard-FPR <5% is **aspirational, not
>   gating**. v10 paper frames this section as *FPR envelope
>   characterization at the calibration boundary*, not as
>   *target achievement*. (See §9 paper-framing addendum.)
> - **Tension #2 ruling:** Corpus size confirmed at **200
>   queries** (6 linguistic × 6 alpha-domain = 36 sub-cells).
> - **Tension #3 ruling:** 2-axis structure confirmed. Sub-cell
>   sizes may be **non-uniform** in the 4–7 range; total target
>   200 ±5% (so [190, 210] hard cap). Quality > strict per-cell
>   equality. Awkward sub-cells (e.g., Category B × ml_signals)
>   may be smaller; actual distribution is reported in
>   `PHASE_1E_RESULTS.md`.
> - **Revision R1 (§2.5):** Multi-encoder validation is now a
>   **two-step rule** — MiniLM primary anchor + per-encoder
>   secondary sanity check with explicit tolerance.
> - **Revision R2 (§7):** New **R6 risk** — corpus-generation
>   LLM leakage; mitigation written into the generation prompt
>   template + validator dedup check.
> - **Revision R3 (§2.3):** Sub-cell non-uniformity rule
>   explicitly written.
> - **§14:** All 10 approval-gate items **APPROVED** with
>   ratification notes.
> - **§15 (new):** V1→V2 changelog.
>
> **V2 supersedes V1.** V1 is retained at `PHASE_1E_PLAN.md`
> for diff reference (matches the Phase 1.F V1/V2 convention).
>
> **Authoritative inputs preserved (unchanged from V1):**
> - `PLAN.md` §5 Deliverable E (DoD ratified)
> - `KICKOFF.md` (strict git policy, cost discipline)
> - `PHASE_1F_RESULTS.md` §3.1–§3.2 (M3.5 calibration protocol)
> - `PHASE_1F_RESULTS.md` §5.5 (asymmetric encoder shift)
> - 8 calibrated `config_phase1F_*.yaml` files
> - `eval/results/phase1_F/calibration/*.json`
>
> **Three deferrals in force (unchanged):**
> 1. LEAK_CASES_FORENSICS 5 follow-up Qs → v10 rewrite
> 2. `sentinelflow_journal_v9_final.tex` → Phase 3
> 3. PHASE_1F_RESULTS.md §11.1 follow-ups → out of 1.E scope

---

## §0 — Document Status and Approval Gate (V2 update)

**V1 status:** PRE-EXECUTION; awaiting user ratification.
**V2 status:** RATIFIED. All 10 §14 approval items APPROVED
2026-05-11 afternoon. Tension rulings #1–#3 locked. Revisions
R1–R3 applied. Ready for E1.1 start upon per-command "start
E1.1" sentence.

V2 acceptance does NOT auto-start E1.1; user issues an explicit
session sentence. Until then, no work-unit execution.

If during E1 execution any sub-step surfaces an unanticipated
issue requiring planning revision, V2 → V2.5 (diffed); V2.5
re-submitted for incremental approval. No silent plan drift.

---

## §1 — Background and Goal (unchanged from V1)

### §1.1 — Why hard-negatives matter

The v9 paper reports FPR on a 100-query benign baseline
(`data/benchmark/normal_prompts.jsonl`) and a 219-query real-
world benign corpus (`data/eval/real_world_normal_prompts.json`).
Both are *easy* benign distributions — queries clearly
off-manifold from any secret. Across all 8 Phase-1.F cells,
both yielded FPR ≤ target 3.0% after M3.5 calibration.

**This under-tests the gate's discriminative boundary.**
Reviewers at TDSC / TOPS expect a hard-negative corpus:
benign queries deliberately *near* the decision boundary,
vocabulary-overlapping with sensitive content, structurally
similar to attacks, but provably benign.

### §1.2 — What 1.E is NOT (unchanged)

- Not a re-calibration of `sensitive_threshold` (M3.5 did
  that; 1.E operates *at* M3.5-fixed thresholds).
- Not per-tier joint calibration (deferred to PHASE_1F_RESULTS
  §11.1 #1).
- Not a regression on Phase 1.F GLR/ULR (different corpus,
  different metric).
- Not a new encoder ablation (same 4 encoders × 2 corpora).

### §1.3 — PLAN.md Deliverable E DoD (unchanged)

> Path: `sentinelflow/evaluations/internal/hard_negatives/`
> - ~100 L1-boundary queries, vocabulary-overlapping with L2/L3
>   secrets but containing no proprietary parametric content.
> - Distribute coverage across all 6 alpha domains in the
>   existing 90-secret corpus.
> - DoD:
>   - 96+ queries, balanced across domains.
>   - FPR-on-hard-negatives reported separately from the
>     existing 100-query benign baseline.
>   - Each query annotated with target secret it borders.

V2 complies with each DoD line. The 200-query target exceeds
the 96-minimum; the linguistic × domain matrix complements (does
not replace) the 6-alpha-domain coverage requirement (§2.3).
Per-query target-secret annotation is in the JSONL schema (§5.2).

### §1.4 — Milestone topology (unchanged)

| Milestone | Deliverable | Wall | LLM cost |
| --- | --- | --- | --- |
| **E1** | Corpus design + generation + validation | ~3–4 d | ≤ $0.10 |
| **E2** | 8 calibrated cells on hard-neg corpus | ~0.5 d | ≤ $0.20 |
| **E3** | Hard-vs-easy FPR comparison + threshold robustness | ~0.5 d | $0 |
| **E4** | `PHASE_1E_RESULTS.md` writeup | ~2–3 d | $0 |

**Phase 1.E hard cost cap: $0.40** (matches Phase 1.F). Realistic
$0.20–0.30; rest is buffer.

---

## §2 — Hard-Negative Taxonomy Design

### §2.1 — Definition (unchanged)

A **hard negative** for SentinelFlow is a query satisfying ALL of:

1. **Benign:** answering reveals no proprietary parametric
   content.
2. **Near-boundary:** encoded vector ∈ [0.40, 0.65] cosine vs.
   closest secret on MiniLM-L6-v2 baseline (V2 R1: + per-encoder
   sanity bands; see §2.5).
3. **Topically-related:** finance / quant vocabulary overlap.
4. **Borderline-realistic:** a real analyst could plausibly
   send this; no contrived adversarial phrasing.

Failure of any property → not a hard-negative → filter (§4).

### §2.2 — Six linguistic sub-categories (unchanged from V1)

Per V1 §2.2; user ratified taxonomy in §14 item (1). Summary:

| Cat | Label | Target size | MiniLM band | Risk |
| --- | --- | --- | --- | --- |
| A | Industry-Typical Knowledge | ~40 | [0.45, 0.60] | Low |
| B | Aggregated Statistics | ~40 | [0.40, 0.55] | Low-Med |
| C | Hypothetical Scenarios | ~30 | [0.45, 0.65] | Med |
| D | Educational / Conceptual | ~40 | [0.40, 0.55] | Low |
| E | Comparison / Benchmarking | ~30 | [0.50, 0.65] | Low-Med |
| F | Negation / Past-Tense / Conditional | ~20 | [0.45, 0.60] | High |

Full per-category definitions, example seeds, why-reviewer-
accepts, expected band, and risk analysis: V1 §2.2.1–§2.2.6
(unchanged in V2; load V1 if needed).

### §2.3 — Cross-cutting axis: 6 alpha domains (V2 revised: R3)

The PLAN.md DoD-mandated finance-domain coverage axis: 6 alpha
domains × ~33 queries per domain. The 6 categories × 6 domains
= **36 sub-cells**.

**V2 Revision R3 — Sub-cell non-uniformity rule (per Tension #3
ruling):**

- **Nominal target:** ~5–6 queries per sub-cell (200 / 36 ≈ 5.56).
- **Allowed range:** **4 to 7 queries per sub-cell**. Quality
  takes priority over strict numerical balance.
- **Total corpus cap:** 200 ± 5% = **[190, 210] queries (hard
  bound)**. Going below 190 triggers re-generation; going above
  210 triggers selective drop.
- **Awkward sub-cell allowance:** some (category × domain)
  combinations are intrinsically harder to populate with
  realistic queries. Examples:
  - **Category B × `ml_signals`** ("aggregated peer statistics
    about ML signals") — peer aggregation data on proprietary
    ML signals is rarely publicly published; queries here are
    plausible but the seed pool is thin.
  - **Category F × `alternative_data`** ("negation/past-tense
    about alternative data") — alt-data is a relatively new
    field, so past-tense framing is unnatural.
  These sub-cells may carry only 3–4 queries; surplus from
  high-fluency sub-cells (e.g., A × `price_volume_momentum`,
  D × `factor_neutral`) absorbs the deficit.
- **Reporting requirement:** the actual 6×6 sub-cell count
  matrix is reported in `PHASE_1E_RESULTS.md` §4 alongside the
  hard-FPR results. Variance from the nominal (5–6) is explained
  per sub-cell.

**Distribution table (nominal, with V2 tolerance):**

| Category | Nominal per-domain | Tolerance | Total target |
| --- | --- | --- | --- |
| A (40) | 6–7 | 4–8 | 36–44 |
| B (40) | 6–7 | 4–8 | 36–44 |
| C (30) | 5 | 3–7 | 24–36 |
| D (40) | 6–7 | 4–8 | 36–44 |
| E (30) | 5 | 3–7 | 24–36 |
| F (20) | 3–4 | 2–5 | 15–25 |
| **TOTAL** | **~33 per domain** | **[28, 38] per domain** | **[190, 210]** |

**Decision rule on per-domain coverage:** every alpha domain
must have ≥ 28 total queries (across the 6 linguistic categories);
no domain may have > 38. If validation surfaces an imbalance
outside this range, E1.4 regenerates targeted sub-cells.

### §2.4 — Total target size: 200 queries (unchanged; Tension #2 ratified)

Per Tension #2 ruling, 200 is confirmed. The rationale chain:

| Sizing rationale | Value |
| --- | --- |
| PLAN.md DoD floor | ≥96 |
| User's session-start proposal | ~200 |
| Statistical power: 200 → binomial 95% CI ±3.0pp on 5% FPR | ✓ |
| Statistical power: 100 → binomial 95% CI ±4.3pp on 5% FPR | weaker |
| Sub-cell breakdown feasibility: 200 / 36 = 5.6 | ✓ supports paper sub-cell table |
| 8-cell run cost worst case (all-bypass, 200 queries × 8 cells) | $0.275 / $0.40 cap |

Reporting in `PHASE_1E_RESULTS.md` will explicitly justify
200 as: (a) doubles the DoD floor for stat power; (b) enables
sub-cell breakdown for paper depth; (c) stays within the $0.40
budget.

### §2.5 — Multi-encoder validation: 2-step rule (V2 revised: R1)

Phase 1.F M3 surfaced the asymmetric encoder shift: short
queries (attacks / hard-negs) shift in encoder-specific ways.
V1's "anchor on MiniLM; report others" was under-specified —
V2 fixes this with an explicit two-step rule.

**Step 1 — Primary anchor (MiniLM, BLOCKING):**

Each query must satisfy:

```
0.40 ≤ cos_minilm_v90(query, closest_secret) ≤ 0.65
```

where the closest secret is determined via FAISS top-1 against
`data/index/secrets_v2__minilm.faiss` (the 90-entry corpus,
canonical reference; the 60-entry index is reported but not
filter-binding).

Failure → drop or refine.

**Step 2 — Per-encoder secondary sanity check (BLOCKING for
the encoder family claim):**

For each of {mpnet, bge_large, FinLang}, the query's cosine to
its closest secret on the **secrets_v2 (90-entry)** index must
fall inside the encoder's **expected band ± 0.10 tolerance**.

The expected bands are derived from Phase 1.F observations and
v1 §4.4 predictions:

| Encoder | Expected band | Tolerance | Acceptance window |
| --- | --- | --- | --- |
| MiniLM | [0.40, 0.65] | n/a (anchor) | [0.40, 0.65] |
| mpnet | [0.17, 0.42] | ±0.10 | **[0.07, 0.52]** |
| bge-large | [0.55, 0.80] | ±0.10 | **[0.45, 0.90]** |
| FinLang | [0.30, 0.55] | ±0.10 | **[0.20, 0.65]** |

**Acceptance rule:** query is accepted iff **MiniLM ∈ Step 1
band AND every other encoder's cosine ∈ its Step 2 window**.

**Rejection causes and remediation:**

| Failure mode | Likely cause | Remediation |
| --- | --- | --- |
| MiniLM cosine < 0.40 | Query too easy (off-manifold on MiniLM) | Refine: increase domain vocabulary overlap; or move to easy-benign corpora (not 1.E) |
| MiniLM cosine > 0.65 | Query too attack-shaped on MiniLM | Refine: soften phrasing; remove imperative tone |
| mpnet > 0.52 (above expected high + 0.10) | Query has unusual mpnet-side affinity to secret (rare; may indicate a paraphrase-class secret match) | Drop and regenerate; flag pattern for §7 risk audit |
| mpnet < 0.07 (below expected low - 0.10) | Query is genuinely off-manifold on mpnet (= easy negative on mpnet despite being hard on MiniLM) | Drop and regenerate; not a hard-neg across encoder family |
| bge-large > 0.90 | Query is dangerously close to secret on bge-large; would behave like an attack with this encoder | Drop and regenerate; this is the user's "0.95 on bge-large" example — methodologically must drop |
| bge-large < 0.45 | Query is too distant on bge-large | Drop and regenerate; not hard-neg across encoder family |
| FinLang > 0.65 | Query has unexpected finance-domain pull toward secret on FinLang | Drop and regenerate |
| FinLang < 0.20 | Query is off-manifold on FinLang | Drop and regenerate; consistent with FinLang paradox (§5.2 of Phase 1.F) but breaks the cross-encoder hard-neg claim |

**Methodological honesty note:** the tolerance ±0.10 is a
proposed value derived from Phase 1.F's encoder-shift
magnitudes (M3 mpnet shift ~0.23; M3.5 bge-large band shift
~0.15–0.30). If E1.5 validation reveals a substantial fraction
(>30%) of MiniLM-passing queries failing the Step 2 secondary
check, the tolerance is **NOT loosened to admit more queries**.
Instead, this finding is itself reported as a v10 contribution
("encoder-family hard-negative consistency is a non-trivial
constraint"). Loosening tolerance ex-post to fit the data would
be a methodological violation.

**Validator implementation (§4.2 update):** the validator
(`scripts/validate_hard_negatives.py`) implements both Step 1
and Step 2; outputs per-query pass/fail with the failing
encoder and direction (above/below) recorded for forensic
review.

**Per-corpus scope (60 vs 90):** Step 1 and Step 2 are
evaluated against the **90-entry corpus** primarily; the
60-entry index is **also evaluated** and recorded but only
warns (does not block) if it disagrees with the 90-entry
decision. This matches Phase 1.F's canonical-corpus convention.

**No filter on attack-corpus cosine:** unlike V4 (attack-phrase
n-gram check) in §4, the 2-step rule does NOT compare
hard-neg cosines to the attack corpus; that check happens in
V4 (string/n-gram) and V5 (exact dedup), not at the cosine
level. The 2-step rule's scope is **closeness to secret
manifold across encoder family**.

---

## §3 — Generation Strategy (unchanged from V1)

§3.1 (options compared), §3.2 (hybrid pipeline), §3.3 (cost
estimate ≤ $0.10), §3.4 (workload ~18 h human) unchanged from
V1. Key recap:

- **Chosen: Hybrid** (manual seeds + LLM extend + human filter).
- **LLM:** GPT-4o (`gpt-4o-2024-08-06`, dated snapshot for
  reproducibility), consistent with KICKOFF.md attacker-role
  convention.
- **Generation cost cap:** ≤ $0.10. Realistic ~$0.05–0.08.
- **Cap on LLM-only step:** the generation step is the ONLY
  LLM use in E1; validation (E1.5) and E2 are separately
  budgeted.

**V2 addition (links to R2):** the generation prompt template
(§3.2.2) is constrained per R2 to never include actual secret
content. See R6 risk + mitigation in §7.

---

## §4 — Validation Pipeline (V2 revision: R1 integration)

### §4.1 — Per-query properties (V2 revised to integrate R1)

| # | Property | Verification method | Status in V2 |
| --- | --- | --- | --- |
| V1 | MiniLM cosine ∈ [0.40, 0.65] (Step 1 of §2.5) | FAISS top-1 vs secrets_v2 90-entry | **BLOCKING** |
| **V1b (NEW)** | **Per-encoder cosine ∈ Step 2 window (mpnet/bge-large/FinLang)** | FAISS top-1 vs secrets_v2 90-entry × 3 encoders | **BLOCKING (V2 added per R1)** |
| V2 | Benign in expected-answer sense | Human review during E1.4 | BLOCKING (manual) |
| V3 | No parametric numeric content | Regex (digits in numeric-trigger contexts) + human review | BLOCKING |
| V4 | No attack-corpus phrase overlap | Cross-check vs 8 attack n-grams | BLOCKING |
| V5 | Distinct from existing benign corpora | Exact string + Jaccard ≥ 0.7 vs 100-corpus + 219-corpus | BLOCKING |
| **V5b (NEW)** | **No exact-match against any secret (R2 leakage check)** | Exact-string check against `secrets_v2.jsonl` and `secrets.jsonl` | **BLOCKING (V2 added per R2)** |
| V6 | Encoder-asymmetric cosines reported (4 encoders × 2 corpora = 8 entries) | Computed during V1 + V1b | Reported (not blocking — V1b is the blocking secondary) |
| V7 | Target-secret-ID annotation present | Schema check | BLOCKING |
| V8 | Sub-cell balance ([4, 7] per sub-cell, [190, 210] total) | Aggregate count | BLOCKING |

**V2 changes:**

- **V1b:** explicit Step-2 secondary check per R1 (was implicit
  in V1's "report others"). Now blocking.
- **V5b:** exact-match-vs-secret check per R2 (new). This is
  the corpus-generation-LLM leakage defense.
- **V6:** demoted from "reported" to "reported, not blocking"
  semantics (now that V1b is the blocking secondary check).

### §4.2 — `scripts/validate_hard_negatives.py` (V2 design update)

**V2 LOC estimate:** ~280 LOC (V1 was ~250; +30 LOC for the
explicit Step-2 windows table + V5b exact-match check).

```python
# scripts/validate_hard_negatives.py (V2)
#
# Single-purpose validator. Reads JSONL → for each entry, runs
# V1, V1b, V3, V4, V5, V5b, V6, V7, V8 → writes report.
# V2 (benign check) is manual.
#
# V2-specific additions:
#   - V1b: per-encoder secondary band check (§2.5 R1).
#   - V5b: exact-string match check against secrets corpora (§7 R6).
#
# Reuses:
#   - core/config_loader.py:get_pinned_revision
#   - core/embedding (4 encoders with pinned revisions)
#   - 4 × {60, 90} FAISS indexes (8 total; built in Phase 1.F M2)
#
# Adds nothing to PINNED_REVISIONS. No driver changes.
#
# Outputs:
#   - eval/results/phase1_E/validation/<run_id>.json
#       Per-query: V1 cosine, V1b per-encoder pass/fail with
#       (failing_encoder, direction, observed_value),
#       V3 regex hits, V4 n-gram hits, V5/V5b dedup hits,
#       V6 cosines (all 4×2), V7 schema-ok, V8 sub-cell counts.
#
# CLI (V2):
#   python scripts/validate_hard_negatives.py \
#       --input data/benchmark/hard_negatives.jsonl \
#       --secrets data/secrets/secrets_v2.jsonl \
#       --secrets-fallback data/secrets/secrets.jsonl \
#       --encoders minilm mpnet bge_large finlang \
#       --step2-tolerance 0.10 \
#       --out eval/results/phase1_E/validation/run_<timestamp>.json
```

### §4.3 — Validation outcomes (V2: extended with V1b + V5b)

| Outcome | Action |
| --- | --- |
| V1 fails (MiniLM cosine outside [0.40, 0.65]) | Refine or drop per direction (§2.5 table) |
| **V1b fails (Step 2 encoder outside window)** | **Drop and regenerate; do NOT loosen tolerance** |
| V2 fails (not benign) | Drop and regenerate |
| V3 fails (parametric numeric) | Refine: replace number with "typical" / "appropriate" |
| V4 fails (attack-phrase overlap) | Drop and regenerate |
| V5 fails (duplicate of existing benign) | Drop |
| **V5b fails (exact match vs a secret)** | **Drop immediately; flag R6 audit log entry** |
| V6 — reported, not gating | No filter |
| V7 missing | Author re-tags with `target_secret_id` |
| V8 sub-cell imbalance | Rebalance via E1.4 regeneration of under-filled sub-cells |

### §4.4 — Encoder-asymmetric band: predicted vs observed (V2 reference)

The Step 2 expected bands (§2.5) are predictions from Phase 1.F
observations. After E1.5, the validation report includes:

- Observed mean cosine per encoder.
- Observed [P10, P90] per encoder.
- Step 2 pass rate per encoder.
- Cross-encoder failure correlation (do queries that fail
  Step 2 on mpnet also fail on bge-large?).

If E1.5 observed bands deviate **substantially** (> 0.10 from
predicted), V2.5 plan revision is triggered (re-anchor expected
bands, document in V2 → V2.5 changelog). No silent tolerance
relaxation.

---

## §5 — Corpus Storage + Schema (unchanged from V1)

### §5.1 — File path

Final corpus: **`data/benchmark/hard_negatives.jsonl`** (unchanged).
Intermediate: `hard_negatives_seeds.jsonl`, `hard_negatives_raw.jsonl`.

### §5.2 — JSONL schema (unchanged from V1)

Per V1 §5.2. Fields: `_id`, `query`, `category`, `domain`,
`target_secret_id`, `rationale`, `expected_band_minilm`,
`measured_cosine` (4×2 = 8 entries), `closest_secret_id` (4×2),
`manually_reviewed`, `generated_via`, `regex_check_passed`,
`ngram_check_passed`, `dedup_check_passed`.

**V2 minor addition** — add two boolean validator-output fields:

```json
{
  ...
  "step1_passed": true,
  "step2_passed_per_encoder": {
    "mpnet": true,
    "bge_large": true,
    "finlang": true
  },
  "exact_match_against_secret": false  // V5b
}
```

These are populated by the validator during E1.5; manual
authors leave them absent / null at seed time.

### §5.3 — `target_secret_id` semantics (unchanged from V1)

Per V1 §5.3: target_secret_id is the **L1 or L2** secret most
semantically near the query, picked by the author at seed time
or by `closest_secret_id["minilm_90"]` for LLM-generated. NOT
L3, because hard-negs border practitioner-tier (L1) content,
not top-secret (L3).

---

## §6 — Integration with Existing Infrastructure (unchanged from V1)

§6.1 (what we reuse), §6.2 (what we build, ~450 LOC total),
§6.3 (driver invocation) unchanged from V1.

**V2 LOC adjustment** — validator goes from ~250 to ~280 LOC.
Total new code: ~480 LOC across 2 scripts (validate, aggregator).

---

## §7 — Risk Assessment (V2 revision: R2 — add R6)

### §7.1 — Highest-risk environments (V2: extended)

| ID | Risk | Likelihood | Severity | Mitigation |
| --- | --- | --- | --- | --- |
| R1 | Hard-FPR substantially > 5% on multiple cells | Med-High | Med (paper framing, not blocker) | §8.3 reframing + §9 V2 paper-framing addendum |
| R2 | Hard-FPR very close to 3% (corpus not actually hard) | Med | High (corpus design failure) | §8.4 corpus-validity diagnostic |
| R3 | Generated hard-negs attack-shaped on some encoder | Med | Med | §2.5 R1 Step 2 secondary check (V2 NEW) |
| R4 | Category F overlaps social-engineering attack vector | Med-Low | Med | §2.2.6 narrower definition + V4 attack-phrase filter |
| R5 | LLM generation produces low-quality / clustered queries | Med | Med | Hybrid pipeline §3.2 + V1b Step 2 acts as quality floor |
| **R6** (V2 NEW) | **Corpus-generation LLM (GPT-4o) may infer secret content if generation prompt includes secrets** | **Low (mitigated by design)** | **High (audit-grade)** | **§7.2 R6 detailed mitigation below** |
| R7 | `target_secret_id` ambiguous (multiple secrets equally close) | Low | Low | Deterministic top-1; record `top_3_secret_ids` |
| R8 | Cell wall-stall recurs (Phase 1.F Cell-6 pattern) | Low-Med | Low (E2 cost is small; can re-run) | Mitigations A+B from Phase 1.F |
| R9 | Validator over-filters → corpus shrinks below 190 | Low | High (PLAN.md floor) | E1.4 regeneration step; 210+ candidate buffer |

(R1–R5 and R7–R9 were V1's risks, renumbered. R6 is new in V2.)

### §7.2 — R6: Corpus-generation LLM leakage risk (V2 NEW per Revision R2)

**Risk statement.** The hybrid generation pipeline (§3.2) uses
GPT-4o (`gpt-4o-2024-08-06`) to extend hard-negative seeds. If
the generation prompt template includes actual secret content
(e.g., paste in `secrets_v2.jsonl` entries as few-shot
context), the generation LLM has direct exposure to proprietary
parametric content. The LLM might then:

1. **Emit verbatim secret text** in a generated hard-neg
   candidate (most easily caught at V5b exact-match check).
2. **Emit paraphrases of secret text** that exceed cosine
   tolerance on some encoder (caught at V1b Step 2 or V1 Step 1).
3. **Train on the secret content** (zero risk on a stateless
   API call, but worth disclosing per audit-grade conservatism).
4. **Reveal cross-secret patterns** the project team had not
   surfaced through any other path.

**Mitigation (multi-layer, V2 contract):**

**Layer 1 — Prompt template constraint.** The generation prompt
template (§3.2.2) MUST NOT contain:

- Any literal entry from `data/secrets/secrets.jsonl` or
  `data/secrets/secrets_v2.jsonl`.
- Any literal entry from `data/secrets/secrets_full.jsonl`
  (Phase 0 superset).
- Any secret `_id` (e.g., `v2_L3_price_volume_momentum_001`,
  `S0001`, etc.) as in-context reference.
- Specific numeric parameters (RSI thresholds, position
  sizes, ADTV multipliers, etc.) that appear in any secret
  entry.

**Layer 1 enforcement:** the generation prompt template is
hand-written and reviewed by author before E1.3 execution. The
template uses ONLY:

- Linguistic category definitions (§2.2).
- Generic financial vocabulary (e.g., "momentum", "long-short",
  "factor", "alpha" — vocabulary that is publicly textbook-
  standard, not parametric).
- The 30 manually-authored seeds (§3.2.1) — which themselves
  must comply with V3 (no parametric content) before being
  used as few-shot examples.

**Layer 2 — Validator V5b exact-match check.** The validator
performs an exact-string match between every generated query
and every entry in `secrets.jsonl` + `secrets_v2.jsonl`. Any
exact match → drop the generated query immediately and log to
audit trail.

**Layer 3 — V1 + V1b cosine-tolerance check.** A generated
query that paraphrases a secret will likely score MiniLM cosine
> 0.65 (Step 1 failure) or shift outside Step 2 windows on
multiple encoders simultaneously. These cases are caught at
validation.

**Layer 4 — Manual review filter (V2 benign check).** Author
reads every generated query during E1.4 filter pass; queries
that "feel like" they paraphrase a secret are dropped even if
they pass cosine filters.

**Layer 5 — Audit log.** A separate forensic log file
(`eval/results/phase1_E/validation/r6_audit.jsonl`) records:

- Every V5b exact-match failure.
- Every V1b Step 2 failure with > 1 encoder failing simultaneously
  (paraphrase signature).
- Every author manual-drop reason tagged with "suspected secret
  paraphrase".

Audit log is reviewed before E2 start. If any V5b match was
found, V2.5 plan revision is triggered (root-cause analysis on
what leaked through Layer 1).

**Layer 6 — Validation regenerates queries don't accidentally
exact-match any secret entry.** This is the key validator
output: V5b exact-string match → 0 hits target. Plus cosine to
nearest secret must be in target band (§2.5) — NOT exact-match
1.0 (cosine 1.0 = identical vector = identical text after
encoding, which V5b catches at the string level).

**Why R6 is low likelihood:** the project's six layers above are
defense-in-depth. The probability of a leakage surviving all 6
layers is bounded by the joint probability of Layer 1 failure
(author error in prompt template) AND Layer 2 failure (validator
bug) AND Layer 3 failure (cosine-tolerance miscalibration) AND
Layer 4 failure (human reviewer miss). Estimated joint
probability: < 0.5% per generated query. With 200 queries → 1
incident expected per ~100 1.E-equivalent generations.

**Why R6 is high severity (despite low likelihood):** any
leakage would be an **audit-grade** finding — meaning it would
need to be disclosed in the v10 paper's Methodology + Limitations
sections, even if it had no effect on the published numbers.
This is the kind of audit risk the v9 audit-phase critique
explicitly cared about (paper-code gaps + provenance gaps).

### §7.3 — Sixth paper-code inconsistency risk (unchanged from V1)

Per V1 §8.2. 1.E cannot surface a v9 hard-neg-FPR claim
inconsistency (v9 doesn't report hard-neg FPR). But might
surface:

- Gate 0b verb×obj over-block on innocuous pairs.
- Base-tier 0.75 over-block on hard-negs (vs Phase 1.F
  100-corpus baseline).
- Cascade k=2 false-trigger on benign.

**Stop-and-report protocol** (per `feedback_stop_and_report`):
any new paper-code inconsistency → stop, report, do not
auto-continue.

### §7.4 — If hard-FPR > 5% (unchanged structural framing; see §9 V2 paper-framing addendum)

Per V1 §8.3, the <5% target is reframed as aspirational in V2
(Tension #1 ruling). Operational guidance:

- **Watchpoint α** (§12): if any cell's hard-FPR > 30%, stop
  and report.
- **Paper framing** (§9): always report honestly per
  characterization framing (V2 addendum below).

### §7.5 — If hard-FPR < 1% on > 4 cells (unchanged from V1 §8.4)

Diagnostic protocol unchanged. Watchpoint γ fires per §12.

---

## §8 — Milestone E2-E4 Sub-Plan (renumbered from V1 §7)

§7 from V1 (was "E2-E4 Sub-Plan") is renumbered to §8 in V2
because §7 is now Risk Assessment (per user's natural section
numbering). All content unchanged.

### §8.1 — E2: Run 8 calibrated cells (unchanged from V1 §7.1)
### §8.2 — E3: Hard-vs-easy FPR comparison (unchanged from V1 §7.2)
### §8.3 — E4: Writeup (unchanged from V1 §7.3)
### §8.4 — Cost/wall summary (unchanged from V1 §7.4)

Per-milestone cost / gate / wall details: identical to V1.
Loading V1 §7.1–§7.4 for full detail.

---

## §9 — v10 Paper Section Integration (V2 revision: framing addendum)

### §9.1 — Section placement options (unchanged from V1)

**Option (a)** — extend §IV-K alongside Phase 1.F as a column
addition. Compact.
**Option (b)** — new §IV-L stand-alone section. Higher
prominence; matches reviewer expectations.

**Recommendation: Option (b).** Final decision deferred to v10
paper rewrite (Phase 2).

### §9.2 — Draft outline for §IV-L (unchanged from V1)

§IV-L.1 Hard-Negative Corpus Design
§IV-L.2 Per-Encoder Hard-FPR Results
§IV-L.3 Findings
§IV-L.4 Limitations

(Full outline: V1 §9.2.)

### §9.3 — V2 paper-framing addendum (NEW per Tension #1 ruling)

**Framing principle (locked):** the v10 paper Section §IV-L
frames hard-negative FPR as a **characterization metric**, not
a **target metric**.

**What "characterization" means in this context:**

- Hard-neg FPR is a measurement of *where the gate's
  discriminative boundary actually lies* under near-boundary
  benign input, evaluated at the M3.5-calibrated thresholds
  that were fixed before Phase 1.E started.
- It is NOT a metric the project optimizes against (e.g., "we
  tuned the gate until hard-FPR fell below 5%"). The
  thresholds were locked in M3.5; 1.E measures the consequence.
- The reported number is the gate's *FPR envelope at the
  calibration boundary* — describing the gate's actual
  behavior on the hardest tested benign distribution.

**Why this framing is reviewer-defensible:**

- Reviewers at TDSC / TOPS are trained to be skeptical of
  papers that claim "we achieved X% FPR on hard negatives" when
  the hard-negative corpus was constructed AFTER the threshold
  was tuned. The implicit risk: the corpus was selected to be
  "hard enough to be plausible but not hard enough to break
  our number."
- Characterization framing inverts this: the corpus is
  constructed independently (per the taxonomy + validation
  pipeline in §2–§4, locked before any 1.E numbers are
  measured), and the resulting FPR is the gate's honest
  envelope. The number could be 2% or 35% — both are
  defensible characterizations as long as the corpus
  construction was principled.

**Concrete paper prose (drop-in template, finalized in E4):**

> *Insert in §IV-L motivation paragraph.*
>
> The v9 paper establishes FPR ≤ 3.0% on a 100-query benign
> baseline tuned to be representative of typical user queries.
> This evaluation does not constrain the gate's behavior on
> near-boundary benign queries — queries with vocabulary
> overlap to sensitive content but no proprietary parametric
> exposure. We construct a 200-query hard-negative corpus
> (§IV-L.1) targeting MiniLM cosine [0.40, 0.65] vs. the closest
> secret, validated for cross-encoder consistency on mpnet,
> bge-large-en-v1.5, and FinLang-investopedia (§IV-L.1.2).
> Hard-FPR is reported as the **gate's FPR envelope at the
> calibration boundary**: an honest measurement of the
> threshold's discriminative power, evaluated at the
> M3.5-calibrated `sensitive_threshold` per cell (Section IV-K
> threshold-portability discussion). We do NOT re-tune
> thresholds against the hard-negative corpus; doing so would
> conflate corpus difficulty with gate fitness. The reported
> hard-FPR is therefore a *post-calibration discriminative-
> power signal*, not a *target-achievement metric*.

**What this means operationally:**

- E4 paper-section prose uses the word "envelope" and
  "characterization", not "achieve" or "target".
- The §IV-L.4 Limitations section explicitly disclaims the
  <5% framing: "PLAN.md §9 Success Criterion #6 (hard-FPR <5%)
  was an aspirational planning target; the measured FPR is
  reported regardless of whether it falls below this number."
- The §IV-L.3 Findings section comments on **what the FPR
  envelope reveals** (e.g., per-encoder asymmetry, per-category
  discriminative variance), not on **whether the envelope is
  small enough**.

**Reviewer-anticipated rebuttals this framing prepares for:**

- "Did you tune thresholds against hard-negatives?" → No,
  thresholds are M3.5-locked. (§IV-K + §IV-L threshold
  immutability disclosure.)
- "Why not target <5% explicitly?" → Hard-neg FPR is by design
  in the worst-case benign band; a hard cap would either
  collapse to easy-neg territory or require ex-post threshold
  tuning. (§IV-L.4 Limitations.)
- "Is your corpus representative?" → Generation pipeline §IV-
  L.1.1 is described in full; corpus is released for
  independent re-construction.

This framing also positions Phase 1.E as a v10 methodology
contribution (not just a number) — the "characterization at
calibration boundary" framework is reusable beyond SentinelFlow.

---

## §10 — Sequencing (renumbered from V1 §10)

### §10.1 — E1 work units (unchanged from V1)

Per V1 §10.1. 6 work units (E1.1 manual seeds, E1.2 prompt
design, E1.3 LLM generation, E1.4 human filter, E1.5 validator
+ finalize, E1.6 status). Each ≤ 4 h. Total ~18 h human / 3–4
days wall / ≤ $0.10 LLM.

### §10.2 — E1.1 detailed sub-plan (unchanged from V1)

Per V1 §10.2. E1.1 produces `hard_negatives_seeds.jsonl` with
30 manual seeds (5 per category × 6 categories, with rotating
domain coverage). $0, 4 h wall.

**V2 note:** the V1 spec for E1.1 already complies with the R2
mitigation Layer 1 constraint (manual seeds don't paste
secrets). No procedural change for E1.1.

---

## §11 — Audit Phase + Phase 1.F Lessons Applied (V2 revision: §11.2 rulings)

### §11.1 — Direct lessons from Phase 1.F (unchanged from V1)

Lessons 1–10 unchanged from V1 §11.1.

- L1 — Asymmetric encoder shift → §2.5 R1 (V2 strengthened to
  explicit Step 2 windows).
- L2 — Per-encoder calibration → §6 (reuse 8 calibrated configs).
- L3 — Cost discipline → §7.4 / §8.4 ($0.40 cap).
- L4 — Per-cell immediate reporting → §8.1.
- L5 — Two-corpus discipline → three-corpus (100/219/200) in §9.
- L6 — GLR/ULR separation → §6.3.
- L7 — Watchpoint discipline → §12.
- L8 — Three-layer verifier reuse → §6.1.
- L9 — Append-only status log → `PHASE_1E_STATUS.md`.
- L10 — Senior-level honesty framing → §7.4 + §9.3 V2 framing
  addendum.

### §11.2 — Tensions with PLAN.md / KICKOFF.md (V2: rulings locked)

**Tension #1 (PLAN.md §9 SC#6 hard-FPR <5% target).**
- **V1 status:** flagged as tension; proposed P1/P2/P3 framing
  options.
- **V2 RULING (2026-05-11 afternoon):** hard-FPR <5% is
  **aspirational, not gating**. v10 paper Section §IV-L frames
  this as **FPR envelope characterization at the calibration
  boundary**, not as target achievement. The paper-prose
  template in §9.3 implements this framing. The Limitations
  section explicitly disclaims the <5% framing. Watchpoint α
  remains (>30% triggers stop-and-report) but values in the
  5–30% band are reported as-is without paper-side
  apology. **RESOLVED.**

**Tension #2 (Corpus size 200 vs PLAN.md "~100").**
- **V1 status:** proposed 200; user confirmation needed.
- **V2 RULING (2026-05-11 afternoon):** **200 confirmed.** The
  6×6=36 sub-cell structure × ~5.5 queries per cell enables
  paper sub-cell breakdown reporting (a contribution beyond
  the DoD minimum). Statistical power on hard-FPR ±3.0pp at
  the binomial 95% CI on 5% baseline. Cost stays in $0.40
  cap. `PHASE_1E_RESULTS.md` writeup will explicitly justify
  200 vs the PLAN.md "~100" baseline as: (a) doubled stat
  power; (b) sub-cell paper depth; (c) within budget.
  **RESOLVED.**

**Tension #3 (Linguistic × Domain 2-axis structure).**
- **V1 status:** proposed both axes; user confirmation needed.
- **V2 RULING (2026-05-11 afternoon):** **2-axis confirmed.**
  6 linguistic × 6 domain = 36 sub-cells. **Sub-cell sizes are
  non-uniform** (allowed range 4–7 queries per cell). Total
  corpus 200 ±5% ([190, 210] hard bound). Quality > strict
  numerical equality. Awkward (linguistic × domain)
  combinations (e.g., B×ml_signals, F×alternative_data) may
  carry 3–4 queries; surplus from high-fluency cells absorbs
  the deficit. Actual sub-cell distribution + variance
  explanation reported in `PHASE_1E_RESULTS.md` §4.
  **RESOLVED.**

**Tension #4 (KICKOFF.md "no LLM API call this step" rule).**
- **V1 status:** applies to plan turn only.
- **V2 status:** **RESOLVED.** This (V2 plan-turn) again
  uses $0 LLM. E1.3 generation uses ~$0.05–0.08 LLM per §3.3
  separately budgeted. R6 mitigation (V2 NEW) further constrains
  the LLM-use scope.

**Tension #5 (KICKOFF.md attacker-LLM convention GPT-4o).**
- **V1 status:** generation uses GPT-4o per convention.
- **V2 status:** **RESOLVED.** No tension. Reaffirmed: GPT-4o
  (`gpt-4o-2024-08-06`, dated snapshot pinned) is the only LLM
  in E1.

**Tension #6 (PLAN.md sequencing: F → E → D → A → B → C).**
- **V1 status:** no tension; E is up next after F.
- **V2 status:** **RESOLVED.** No change.

**Tension #7 (KICKOFF.md git policy strict).**
- **V1 status:** no commits/pushes; file edits only.
- **V2 status:** **RESOLVED.** Same in V2; no change.

### §11.3 — Lessons NOT directly applicable (unchanged from V1)

Phase 1.F lessons that don't bind on 1.E: ROC plotting
deferral (Phase 3); bge-large 3-prompt floor (per-tier
calibration follow-up, not 1.E); single-sample stochasticity
(largely irrelevant on benign queries where we measure FPR at
gate). Per V1 §11.3.

---

## §12 — Watchpoints + Cost/Wall Discipline (V2: extended)

Watchpoints unchanged from V1 §12, plus one V2 addition (η).

| Watchpoint | Condition | Where it fires | Action |
| --- | --- | --- | --- |
| **α** | Any cell's hard-FPR > 30% | E2 per-cell completion | Stop; report; do not auto-continue |
| **β** | E2 per-cell wall > 1800s (30 min) | E2 per-cell completion | Stop; diagnose (likely Cell-6-style); apply Mitigations A+B |
| **γ** | Hard-FPR < 1% on > 4 of 8 cells | E3 aggregation | Stop; corpus likely too easy; refresh |
| **δ** | New paper-code inconsistency surfaced | E2 or E3 | Stop; report; do not proceed to E4 |
| **ε** | Per-cell LLM cost > $0.05 | E2 per-cell completion | Stop; investigate |
| **ζ** | E1 LLM generation cost > $0.10 | E1.3 completion | Stop; reduce scope or refine prompt |
| **η** (V2 NEW) | **V5b exact-match leakage detected (R6 layer 2 fires)** | **E1.5 validation** | **Stop; root-cause Layer 1 prompt failure; V2.5 plan revision before continuing** |

**Cost cap reminder:** $0.40 hard cap. Per-cell cap $0.10.
Buffer $0.10.

**Wall cap reminder:** ~8 days end-to-end. Active work ~38 h.

---

## §13 — Out of Scope (unchanged from V1)

Per V1 §13. Out-of-scope items:

- Per-tier joint calibration (PHASE_1F §11.1 #1, separate phase).
- bge-large 3-prompt floor (per-tier follow-up).
- Multi-sample LLM stochasticity (PHASE_1F §11.1 #2, Phase 1.G).
- OpenAI text-embedding-3 ablation (PHASE_1F §11.1 #3, Phase 1.H).
- v10 paper rewrite (PLAN.md Phase 2).
- v9_final.tex LaTeX edits (Phase 3).
- LEAK_CASES_FORENSICS Qs (v10 rewrite).
- New encoders, new corpora, salami / multi-turn evals,
  adaptive attacker evals.

---

## §14 — Plan Status / Approval (V2: all APPROVED)

**Plan version:** V2 (this document).
**Plan status:** RATIFIED — all 10 §14 items APPROVED by user
2026-05-11 afternoon. Tensions #1–#3 resolved per §11.2.
**Plan cost:** $0 LLM, $0 dependencies, no git operations.
**Plan output files:** this document.

**User per-item ratifications (10 items, all APPROVED):**

| # | Item | V1 ref | V2 ratification | Note |
| --- | --- | --- | --- | --- |
| 1 | Taxonomy 6 categories (A–F) | §2.2 | **APPROVED** | Includes V1 §2.2.6 Category F narrowed-definition retained |
| 2 | 2-axis Linguistic × Domain structure | §2.3 | **APPROVED** | Tension #3 ruled — non-uniform sub-cell sizes [4,7] range; total [190,210]; awkward cells smaller; report variance |
| 3 | Corpus size 200 | §2.4 | **APPROVED** | Tension #2 ruled — 200 confirmed; rationale in PHASE_1E_RESULTS §4 |
| 4 | Cosine band MiniLM-anchored + Step 2 per-encoder secondary | §2.5 | **APPROVED** | Revision R1 applied — explicit 2-step rule; per-encoder windows tabulated; tolerance ±0.10 (not loosened ex-post) |
| 5 | Generation strategy hybrid (manual seed + LLM extend + human review) | §3 | **APPROVED** | Revision R2 applied — R6 corpus-gen LLM leakage mitigation (6-layer defense); ≤ $0.10 LLM cap |
| 6 | Validation pipeline (V1–V8 + V2 NEW V1b + V5b) | §4 | **APPROVED** | Per V2 §4.1 updated table |
| 7 | E2-E4 milestone breakdown | §8 | **APPROVED** | Unchanged from V1 §7 (renumbered to §8 in V2) |
| 8 | Storage schema (JSONL + per-encoder cosines + V2 added validator fields) | §5 | **APPROVED** | V2 minor schema addition: step1/step2/exact_match fields |
| 9 | v10 paper integration plan (Option (b) §IV-L; characterization framing) | §9 | **APPROVED** | Revision R1 framing — V2 paper-framing addendum (§9.3); locked as characterization not target |
| 10 | SC#6 hard-FPR <5% target — aspirational only | §7.4 / §9.3 | **APPROVED** | Tension #1 ruled — aspirational, not gating; Limitations explicitly disclaims; Watchpoint α retained at >30% |

**Next step:** user issues per-command "start E1.1" sentence.
No work begins until that sentence.

**If V2 surfaces a tension during user re-read:** flag to user
before starting E1.1; V2 → V2.5 diffed revision; re-ratify
the affected item(s). Otherwise V2 is the operational plan
for 1.E.

---

## §15 — V1 → V2 Changelog (NEW)

This section tracks the specific changes from V1 to V2,
matching the Phase 1.F V2 changelog convention. Future plan
diffs (V2 → V2.5, V2 → V3 if any) append here.

### §15.1 — Tension rulings (3 locked)

| Tension | V1 status | V2 ruling | Sections modified |
| --- | --- | --- | --- |
| #1 hard-FPR <5% | Open; P1/P2/P3 options | **Aspirational only; characterization framing** | §7.4, §9.3 (NEW addendum), §11.2 #1, §14 item (10) |
| #2 Corpus size 200 | Proposed; user confirmation needed | **Confirmed 200; rationale explicit** | §2.4, §11.2 #2, §14 item (3) |
| #3 2-axis structure | Proposed; user confirmation needed | **Confirmed 2-axis; non-uniform [4,7]; total [190,210]** | §2.3 (R3 rule added), §11.2 #3, §14 item (2) |

### §15.2 — Required revisions (3 applied)

| Revision | Scope | V2 implementation |
| --- | --- | --- |
| R1 | Multi-encoder validation 2-step rule | §2.5 rewritten with explicit Step 1 + Step 2; per-encoder windows + tolerance ±0.10 table; V4.1 V1b added as blocking check |
| R2 | Corpus-gen LLM leakage risk | §7.2 NEW with 6-layer mitigation; V4.1 V5b added as blocking exact-match check; Watchpoint η added (§12) |
| R3 | Sub-cell non-uniformity rule | §2.3 expanded with explicit [4,7] range + [190,210] total + awkward-cell allowance + reporting requirement |

### §15.3 — Approval gates (all 10 ratified)

V2 §14 captures all 10 items as APPROVED with per-item
ratification notes. Items #2, #3, #4, #5, #9, #10 explicitly
referenced the tension rulings and revisions; items #1, #6,
#7, #8 unchanged from V1 substance.

### §15.4 — Section renumbering

| V1 section | V2 section | Reason |
| --- | --- | --- |
| §7 (E2-E4 Sub-Plan) | §8 | V2 inserts Risk Assessment as §7 to match user's natural section numbering from task brief |
| §8 (Risk Assessment) | §7 | (renumbered, content expanded with R6 R-table row + §7.2 NEW) |
| §9 (Paper Integration) | §9 (unchanged number) | §9.3 addendum added |
| §10–§14 | §10–§14 (unchanged) | Content per V1; §11.2 updated with rulings; §14 marked APPROVED |
| (none) | §15 (NEW) | This changelog |

### §15.5 — LOC / cost adjustments

- Validator script: V1 ~250 LOC → V2 ~280 LOC (+30 for Step 2
  table + V5b exact-match check + audit log emission).
- Total new code: V1 ~450 → V2 ~480 LOC.
- Total budget unchanged: $0.40 Phase 1.E cap.
- Wall budget unchanged: ~38 h active / ~8 days wall.

### §15.6 — Operational impact of V2 vs V1

V2 strengthens 1.E in three ways without growing scope:

1. **Cross-encoder rigor (R1):** what was "anchor + report" in
   V1 becomes "anchor + per-encoder secondary block" in V2.
   This catches the user's "0.50 on MiniLM but 0.95 on bge-
   large" case at validation, not later at E3 forensics.
2. **Audit-grade R6 mitigation (R2):** corpus-gen LLM leakage
   gets a 6-layer defense before the paper-level claim is
   made. Reviewer-defensible at TDSC/TOPS.
3. **Tension-rulings locked (3):** ambiguity at the
   methodology / paper-framing level is resolved before E1
   starts, eliminating mid-execution plan churn.

V2 does NOT change scope (still 200 queries, 4 encoders, 8
cells, $0.40 budget). It tightens the methodology around the
same scope.

---

*End of `PHASE_1E_PLAN_V2.md`.*
