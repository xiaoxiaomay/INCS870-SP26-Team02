# Phase 1.E E1.3 — V1a + V1b + V5b Validator Pipeline: Results

> **Status:** PASS. The V2 §4 validator pipeline is implemented and
> run end-to-end against the 65-entry hard-negative corpus. Three
> validator stages (V1a MiniLM Step-1 + V1b 3-encoder Step-2 + V5b
> exact-string match) executed; R6 audit log seeded per V2 §7.2;
> 10 paper-publishable findings (S1, S2, S5, S6, S7, S8, S9, S10,
> S11, S12) plus 2 PENDING V2.5 plan/schema revision decisions
> embedded in canonical JSON artifact. Drop/refine decisions
> deferred to E1.4 regeneration phase per V1a Option B precedent.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §2.5 (encoder windows), §4 (validator
>   pipeline), §5 (schema), §7.2 (R6 mitigation layers).
> - `PHASE_1E_E1_2_RESULTS.md` (E1.2 close — 65-entry corpus +
>   dual-tier seed authoring).
> - `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries,
>   30 manual + 35 LLM-generated; all V1a/V1b/V5b fields populated).
> - `data/secrets/secrets_v2.jsonl` (90 secrets, 30 L1 + 30 L2 +
>   30 L3) + `data/secrets/secrets.jsonl` (60 legacy secrets).
> - `data/index/*.faiss` + `*_meta.pkl` (4 encoders × 2 corpora =
>   8 cells; Phase 1.F M2 build_log provenance).
> - `core/config_loader.py:PINNED_REVISIONS` (4 encoder pins
>   verified against M2 build_log).
>
> **Outputs (authoritative artifacts):**
> - `scripts/validate_hard_negatives.py` (1463 LOC; 4-mode CLI:
>   `--check-only` / `--run-v1a` / `--run-v1b` / `--run-v5b`).
> - `eval/results/phase1_E/validation/v1a_20260522T013349Z.json`
>   (V1a canonical; historical).
> - `eval/results/phase1_E/validation/v1b_20260523T045118Z.json`
>   (V1b + V5b merged canonical; **final E1.3 artifact**; 12
>   documented_findings keys; full per-encoder + agreement + R6
>   summary).
> - `eval/results/phase1_E/validation/r6_audit.jsonl`
>   (R6 audit log; 4 Layer 5 paraphrase signature entries).
> - `eval/results/phase1_E/validation/v1a_band_report.md`
>   (E1.3.3 markdown, 390 lines).
> - `eval/results/phase1_E/validation/outlier_inventory.md`
>   (E1.3.6 markdown, 306 lines).

---

## §1 — E1.3 Close Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| Sub-steps closed | **E1.3.1 → E1.3.6** (E1.3.7 = this document) |
| Validators implemented | V1a MiniLM + V1b 3 secondary encoders + V5b exact-match |
| Hard-neg entries processed | 65 (30 manual + 35 LLM-generated) |
| Secret-corpus inference | 4 encoders × 90-entry corpus + 60-entry legacy (V5b only) |
| V1a BLOCKING pass rate | **53/65 (81.5%)** |
| V1b per-encoder BLOCKING pass rate | minilm 53/65, mpnet 51/65, bge_large **65/65**, finlang 61/65 |
| V5b exact-string match hits | **0/65** (null result, S12) |
| Unique outliers across V1a + V1b + V5b | **23/65 (35.4%)** |
| R6 audit log entries | 4 (all Layer 5; 0 Layer 2 V5b; Layer 4 deferred to E1.4) |
| Documented paper findings | **10** (S1 / S2 / S5 / S6 / S7 / S8 / S9 / S10 / S11 / S12) |
| PENDING V2.5 revision decisions | **2** (plan revision; schema revision) |
| LLM cost | **$0** (entirely local FAISS + sentence-transformers) |
| Cumulative wall (E1.3.1–E1.3.6, 2 sessions) | ~7.5 hours (3.5 + 4.0) |

### §1.2 — Phase 1.E E1.3 milestone gate

PASS (7 / 7 acceptance criteria):

- ✓ Validator script implements V2 §4.1 V1a + V1b + V5b checks.
- ✓ JSONL schema honors V2 §5.2 + §5.3 dual-convention (Option C).
- ✓ All 4 encoder pins verified against Phase 1.F M2 build_log.
- ✓ R6 audit log file populated per V2 §7.2 Layer 5 spec
  (4 paraphrase signatures captured).
- ✓ 65 entries × all V1a/V1b/V5b measurement fields populated.
- ✓ Process-discipline events transparently surfaced (5
  stop-and-disclose / view-before-implement catches).
- ✓ No corpus mutation beyond field additions (entry IDs +
  authored query/rationale preserved across all stages).

---

## §2 — Scope and Acceptance Criteria

E1.3 implements the V2 §4 validator pipeline against the
E1.2-close 65-entry hard-negative corpus. Per V2 §4.1, three
BLOCKING checks are required at E1.3 scope (V2/V3/V4/V7/V8 are
manual or out-of-scope for E1.3):

- **V1a** — Per-category MiniLM cosine band check against
  `secrets_v2` 90-entry corpus, post-filter to L1+L2 tier (V2
  §5.3). Anchor encoder, Step-1 of V2 §2.5 two-step rule.
- **V1b** — Per-encoder cosine band check on 3 secondary encoders
  (mpnet, bge_large, finlang) using V2 §2.5 Step-2 windows.
  BLOCKING per V2 §4.1; STRICT-with-paper-escalation interpretation
  ratified for E1.3 scope (drops deferred to E1.4).
- **V5b** — Exact-string match check between hard-neg
  query/rationale and full secret texts from both corpora
  (60 + 90 = 150 secrets). Layer 2 of V2 §7.2 R6 mitigation chain.
  STRICT character-equality semantics.

Plus R6 audit log seeding per V2 §7.2 Layer 5 (V1b ≥2-encoder
above-band paraphrase signatures).

Three-layer verification discipline applied per project
convention (L1 static syntax checks, L2 runtime per-cell
verification, L3 cross-artifact consistency).

---

## §3 — Validator Architecture

### §3.1 — `scripts/validate_hard_negatives.py` (1463 LOC)

Single-file validator with 4-mode CLI:

```
python3 scripts/validate_hard_negatives.py {--check-only | --run-v1a | --run-v1b | --run-v5b}
```

| Mode | Phase | Side effects | Wall |
| --- | --- | --- | --- |
| `--check-only` | E1.3.1 | None (infrastructure verify) | ~5s |
| `--run-v1a` | E1.3.2 | JSONL atomic write + `v1a_<ts>.json` | ~7s |
| `--run-v1b` | E1.3.4 | JSONL atomic write + `v1b_<ts>.json` | ~22s |
| `--run-v5b` | E1.3.5 | JSONL atomic write + R6 log + merged `v1b_<ts>.json` | ~1s (after V1b cached) |

### §3.2 — Module structure

| Component | Detail |
| --- | --- |
| `ENCODER_NAMES` | 4 encoder short→full name map |
| `FAISS_INDEX_PATHS` | 4 paths; **MiniLM hard-coded as unsuffixed `secrets_v2.faiss`** per Phase 1.F M2 historical artifact (commented in source for reproducibility chain integrity) |
| `FAISS_META_PATHS` | 4 paths (parallel to index paths) |
| `CATEGORY_BANDS` | V2 §2.2 per-linguistic-category MiniLM bands (A–F, six 2-tuple windows) |
| `GLOBAL_BLOCKING_BAND` | (0.40, 0.65) — V2 §4.1 V1a global band |
| `STEP2_WINDOWS` | V2 §2.5 per-encoder Step-2 windows for V1b (mpnet/bge_large/finlang) |
| `EXPECTED_BAND_MIDPOINT` | Per-encoder predicted midpoints for V2 §4.4 substantial-deviation check |
| `SECRET_TIER_ALLOWED` | `{"L1", "L2"}` per V2 §5.3 |
| `TOP_K` | 10 (bumped from 5 during E1.3.2 after HN_SEED_009 fallback null surfaced) |
| `DOCUMENTED_FINDINGS` | 12-key dict embedded into every per-run JSON report; 10 S-findings + 2 PENDING |
| `load_encoder_components()` | Generic loader, returns (model, index, meta) for any of 4 encoders |

### §3.3 — Schema convention (Option C dual-field, V2 §5.2 + §5.3)

Per-entry fields after full V1a + V1b + V5b execution:

| Field | Semantics | Populated by |
| --- | --- | --- |
| `target_secret_id` | **Author intent** (manual seeds only; null for LLM-generated) | E1.1 author; validator does NOT mutate |
| `closest_secret_id_<enc>_90` (4 fields) | **Validator measurement** — FAISS top-1 post-L1/L2-filter per encoder | V1a + V1b |
| `closest_cosine_<enc>_90` (4 fields) | **Raw cosine** for audit-trail reproducibility | V1a + V1b |
| `expected_minilm_band` | `{low, mid, high}` per V2 §2.2 per-category band | V1a |
| `v1b_blocking_pass` | dict `{mpnet, bge_large, finlang}` per V2 §2.5 windows | V1b |
| `cross_encoder_agreement` | dict `{exact_secret_id, same_domain, same_tier, all_blocking_pass}` | V1b |
| `exact_match_against_secret` | bool per V2 §5.2; True if any V5b hit on query or rationale | V5b |

### §3.4 — Atomic write discipline

Every mutating run executes:
1. `shutil.copy2(JSONL → JSONL.bak)` before write
2. `write_jsonl(JSONL, persisted)` (full overwrite)
3. Re-read + count verification
4. If verify fails: restore from `.bak`, exit nonzero

User additionally created `.preV1a` permanent baseline (34207
bytes; pre-V1a clean state) preserved across all subsequent
runs as a 3-tier corpus snapshot.

---

## §4 — E1.3.1 + E1.3.2 — V1a Infrastructure and Per-Category Band

### §4.1 — Infrastructure (E1.3.1)

Pre-flight verification (`--check-only`) confirmed:
- 65 hard-neg entries; 65/65 `anchor_tier=L1` per T4 ruling.
- 90 secrets in `secrets_v2.jsonl`; tier distribution {L1: 30,
  L2: 30, L3: 30}; post-L1/L2 filter = **60 candidate secrets**.
- MiniLM FAISS index (`data/index/secrets_v2.faiss`) loaded;
  `IndexFlatIP` on `normalize_embeddings=True` vectors → inner
  product IS cosine directly.
- MiniLM pin `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` matches
  Phase 1.F M2 `build_log.json:cells[0].encoder_revision`.

### §4.2 — V1a results (E1.3.2)

| Metric | Value |
| --- | --- |
| BLOCKING band | global [0.40, 0.65] per V2 §4.1 |
| BLOCKING pass | **53/65 (81.5%)** |
| BLOCKING fail outliers | 12 (10 below + 2 above) |
| `expected_minilm_band` populated | 65/65 |
| `target_secret_id` populated | 30/65 (manual seeds only; V2 §5.3 honored) |
| `closest_secret_id_minilm_90` populated | 65/65 (validator measurement) |
| Per-category band distribution | A: 3/12/0, B: 3/7/0, C: 6/4/0, D: 1/3/6, E: 2/7/1, F: 6/4/0 |
| Tier breakdown (measurement) | L1: 21, L2: 44 (L3: 0 filtered) |
| Canonical artifact | `v1a_20260522T013349Z.json` |

### §4.3 — V1a investigation cycle

Three stop-and-disclose events during E1.3.2 surfaced four
paper-publishable findings:

- **18.5% BLOCKING fail rate** investigation → S1 (cross-domain
  spillover) + S2 (E1.1 vs E1.2 asymmetry) + S5 (length
  non-signal).
- **HN_SEED_009 fallback null** (all top-5 L3) → TOP_K=5 → 10
  fix; HN_SEED_009 then mapped to v2_L2_event_driven_005
  (cross-domain pattern itself, S1 consistent).
- **target_secret_id silent overwrite** caught → Option C dual-
  field schema ratified → S6 (author vs measurement divergence)
  emerged from the new schema's two-axis comparison.

Full details in `eval/results/phase1_E/validation/v1a_band_report.md` (E1.3.3).

---

## §5 — E1.3.3 — V1a Band-Distribution Markdown Report

`eval/results/phase1_E/validation/v1a_band_report.md` (390 lines)
documents V1a results in reviewer-grade prose with §1–§9
structure:

| § | Section | Key content |
| --- | --- | --- |
| §1 | Executive Summary | One-paragraph overview |
| §2 | Per-Category × Per-Band Matrix | 6×3 table + per-cat "high" entry enumeration |
| §3 | Per-Tier Breakdown (Two-Way) | Author-intent vs measurement, split by SEED vs GEN |
| §4 | Outliers Detailed Inventory | 12 entries with hn-domain ↔ sec-domain same-flag |
| §5 | Documented Findings | S1 / S2 / S5 / S6 prose |
| §6 | PENDING Decisions | V2.5 plan revision forward-pointer |
| §7 | Methodology Note (Option C) | A/B/C decision rationale + S6 emergence |
| §8 | Forward References | Originally S7 only; updated post-E1.3.4 to include S8–S11 |
| §9 | Reproducibility Provenance | Pins + run artifacts + cost/wall |

Every number cross-checked against canonical V1a JSON. No data
fabrication. Per-category "high" entries documented for V1b
cross-reference: D (6 entries) + E (1 entry).

---

## §6 — E1.3.4 — V1b Multi-Encoder Cosine Band

### §6.1 — Pre-flight (Q5 sub-decision: 60-entry deferred)

V2 §5.2 schema implied `closest_secret_id (4 × 2)` = 4 encoders
× 2 corpora. Pre-flight verification surfaced **S7**: the
60-entry (`secrets.jsonl`) and 90-entry (`secrets_v2.jsonl`)
corpora are completely disjoint (|60 ∩ 90| = 0); 60-entry tier
distribution {L1: 0, L2: 10, L3: 50} makes V2 §5.3's L1+L2
filter degenerate against it (10-candidate search space, all L2).
**E1.3.4 scope was revised to 4 encoders × 90-entry only.**
60-entry comparison deferred to v10 §VI reproducibility appendix
or future V1c sub-step.

### §6.2 — V1b results

Per-encoder BLOCKING (no escalation; all rates < 30%):

| Encoder | Window (V2 §2.5) | Pass | Fail | Fail rate |
| --- | --- | --- | --- | --- |
| minilm | [0.40, 0.65] | 53/65 | 12 | 18.5% (= V1a, consistency ✓) |
| mpnet | [0.07, 0.52] | 51/65 | 14 | 21.5% |
| bge_large | [0.45, 0.90] | **65/65** | **0** | **0.0%** |
| finlang | [0.20, 0.65] | 61/65 | 4 | 6.2% |
| any-of-3-secondary fails | — | 51/65 | 14 | 21.5% (below 30% escalation) |

Cross-encoder agreement (V2 §4.4 cross-encoder failure
correlation):

| Metric | Count | Rate |
| --- | --- | --- |
| exact_secret_id (all 4 pick same secret) | 9/65 | **13.8%** |
| same_domain (all 4 same alpha domain) | 34/65 | 52.3% |
| same_tier (all 4 same L1 vs L2) | 26/65 | 40.0% |
| all_blocking_pass (all 4 in window) | 42/65 | 64.6% |

Per-encoder cosine stats (V2 §4.4 reporting):

| Encoder | Observed mean | P10 | P90 | Predicted midpoint | Δ |
| --- | --- | --- | --- | --- | --- |
| minilm | 0.4934 | 0.3967 | 0.5996 | 0.5250 | −0.0316 |
| **mpnet** | **0.4725** | 0.3889 | 0.5769 | 0.2950 | **+0.1775** ← DEVIATION |
| bge_large | 0.7034 | 0.6408 | 0.7909 | 0.6750 | +0.0284 |
| finlang | 0.4753 | 0.3612 | 0.5905 | 0.4250 | +0.0503 |

**mpnet substantial-deviation +0.1775 unambiguously triggers
V2 §4.4 V2.5 plan revision (Δ > 0.10 threshold).** Per Q1
STRICT-with-paper-escalation ruling, no post-hoc re-anchor;
deviation documented as v10 paper finding S8.

### §6.3 — V1b findings emerged

5 paper findings (4 candidates + 1 pre-flight catch):

- **S7** — 60-entry vs 90-entry corpus disjointness (pre-flight).
- **S8** — mpnet prediction-miss +0.18 (V2.5 plan revision trigger).
- **S9** — bge_large band permissiveness (0/65 outliers; informative null).
- **S10** — encoder-family consensus structurally weak (13.8% exact agreement).
- **S11** — Cat D + Cat E above-band concentration confirmed across 3 of 4 encoders.

---

## §7 — E1.3.5 — V5b Exact-Match + R6 Audit Log

### §7.1 — V5b results

| Metric | Value |
| --- | --- |
| Comparison semantics | STRICT character-equality (Python `==`) |
| Fields compared per hard-neg | `query` AND `rationale` (both populated 65/65) |
| Secrets corpus | **150 total** (60 legacy + 90 v2 canonical) — V2 §4.1 both-corpora spec |
| Total pairwise comparisons | 65 × 2 × 150 = **~19,500** |
| V5b string-match hits | **0** |
| `exact_match_against_secret` = True | 0/65 |
| Wall | 0.01s (hashmap-set lookup) |

**Null result confirms Layer 1 prompt template (V2 §7.2) held.**
No verbatim secret content emitted by GPT-5-mini generation or
paraphrased into manual seed rationale.

### §7.2 — R6 audit log

`eval/results/phase1_E/validation/r6_audit.jsonl` (4 entries):

| `audit_id` | Layer | hard-neg | cat | above-band encoders | disposition |
| --- | --- | --- | --- | --- | --- |
| R6_AUDIT_001 | Layer 5 | HN_SEED_016 | D | mpnet, finlang | requires_content_review_at_E1_4 |
| R6_AUDIT_002 | Layer 5 | HN_GEN_051 | D | minilm, mpnet, finlang | **retained_non_paraphrase** (Action 1a) |
| R6_AUDIT_003 | Layer 5 | HN_GEN_056 | E | minilm, mpnet, finlang | **retained_non_paraphrase** (Action 1a) |
| R6_AUDIT_004 | Layer 5 | HN_GEN_059 | E | mpnet, finlang | requires_content_review_at_E1_4 |

All 4 entries reference findings_reference: `[S11, S12]`.

Layer counts: Layer_2_V5b = 0, Layer_5_V1b_paraphrase_signature
= 4, Layer_4_manual_drop = 0 (deferred to E1.4).

### §7.3 — V5b finding emerged

**S12** — V5b zero corpus contamination (null result audit-grade).

---

## §8 — E1.3.6 — Outlier Inventory

`eval/results/phase1_E/validation/outlier_inventory.md` (306 lines)
consolidates 23 unique outliers across V1a + V1b + V5b.

### §8.1 — Headline numbers (cross-validator)

| Metric | Value |
| --- | --- |
| Unique outliers (V1a ∪ V1b ∪ V5b) | **23/65 (35.4%)** |
| (matches `1 − all_blocking_pass` from S10) | 1 − 0.646 = 0.354 ✓ |
| SEED outliers | 12/30 = 40.0% |
| GEN outliers | 11/35 = 31.4% |

**SEED vs GEN gap narrows in the union (40.0% vs 31.4%) compared
to V1a-alone (S2's 26.7% vs 5.7% below-band).** Reason: V1b's
above-band Cat D/E failures are disproportionately LLM-generated
(S11 vocabulary-overlap mechanism), pulling the GEN flag rate up.

### §8.2 — Per-category concentration

| Cat | Outliers | Corpus | Rate |
| --- | --- | --- | --- |
| A | 5 | 15 | 33.3% |
| B | 3 | 10 | 30.0% |
| C | 2 | 10 | 20.0% |
| **D** | **7** | **10** | **70.0%** |
| **E** | **4** | **10** | **40.0%** |
| F | 2 | 10 | 20.0% |

**D + E account for 11/23 = 48% of outliers despite being only
20/65 = 31% of corpus** — S11 mechanism is structurally dominant.

### §8.3 — Overlap analysis

| Overlap | Entries |
| --- | --- |
| V1a ∩ V1b mpnet | HN_SEED_013, HN_GEN_051, HN_GEN_056 (n=3) |
| V1a ∩ V1b finlang | HN_GEN_051, HN_GEN_056 (n=2) |
| V1b mpnet ∩ V1b finlang | HN_SEED_016, HN_GEN_051, HN_GEN_056, HN_GEN_059 (n=4) |
| V1a ∩ V1b mpnet ∩ V1b finlang | HN_GEN_051, HN_GEN_056 (n=2) |
| Any-V1 ∩ V5b | — (V5b is null) |

Distribution: 18 entries flagged by 1 stage, 3 by 2 stages, 2
by 3 stages, 0 by all 4.

### §8.4 — Disposition matrix

| Disposition | Count | E1.4 action |
| --- | --- | --- |
| `retained_non_paraphrase` (Action 1a content-reviewed) | 2 | No regeneration; record audit |
| `requires_content_review_at_E1_4` (Layer 5, not yet reviewed) | 2 | Priority queue — Action-1a-style review |
| `defer_to_E1_4` (V1a below-band cross-domain spillover) | 10 | Refine vs drop per V2 §2.5 |
| `defer_to_E1_4` (V1b mpnet-only above-band) | 9 | Honest reporting per S8; no per-corpus drop indicated |
| **Total** | **23** | |

---

## §9 — Documented Findings (10 paper-publishable)

Full prose for each finding is embedded in the canonical JSON
artifact `v1b_20260523T045118Z.json:documented_findings` (also
re-emitted across V1a + V1b + V5b run JSONs). Summary catalog:

| ID | Title | Type | Emerged from |
| --- | --- | --- | --- |
| **S1** | Cross-domain spillover (new failure mode) | structural finding | V1a below-band cluster investigation (E1.3.2) |
| **S2** | Audit-framework efficacy (5× E1.1 vs E1.2) | corpus-quality finding | V1a fail-rate by source (E1.3.2) |
| **S5** | Query length is not a band discriminator | null-finding | V1a length-vs-failure stats (E1.3.2) |
| **S6** | Author-intent vs encoder-measurement divergence (17% / 67% / 40%) | methodology finding | Option C dual-field schema enabled comparison (E1.3.2) |
| **S7** | Corpus-version disjointness (60 ⊥ 90) | schema-vs-reality finding | E1.3.4 pre-flight verification |
| **S8** | mpnet expected-band prediction-miss +0.18 | calibration deviation, V2.5 trigger | V1b cosine stats vs V2 §2.5 predictions (E1.3.4) |
| **S9** | bge_large band permissiveness (0/65 outliers) | informative null result | V1b per-encoder BLOCKING (E1.3.4) |
| **S10** | Encoder-family consensus structurally weak (13.8% exact) | reviewer-clarifying methodology | V1b cross-encoder agreement matrix (E1.3.4) |
| **S11** | Cat D + Cat E cross-encoder above-band concentration | linguistic-category × encoder structural pattern | V1b per-encoder outlier categories (E1.3.4) |
| **S12** | V5b zero corpus contamination | audit-grade null result | V5b run (E1.3.5) |

**S3 / S4** do not exist — sequential gaps from
early-rejected candidates during the V1a investigation cycle.
Number gaps are honest record-keeping (vs renumbering, which
would obscure the investigation history).

Cross-references between findings:
- S2 ↔ S6: audit-framework efficacy (S2) mechanistically
  explained by author-vs-measurement divergence (S6).
- S11 ↔ S8: Cat D/E concentration (S11) amplified on mpnet by
  the +0.18 prediction-miss (S8).
- S9 ↔ S10: bge_large's 0 outliers (S9) contributes to weak
  cross-encoder consensus (S10) — it doesn't constrain agreement.
- S7 ↔ S12: corpus disjointness (S7) narrowed V5b scope to the
  90-entry corpus but did not affect V5b null-result claim (S12).

---

## §10 — PENDING Decisions

Both deferred to E1.3.7 (this document) → E1.6 Phase 1.E close.

### §10.1 — `PENDING_V2_5_PLAN_REVISION` (references S1 + S8 + S9)

Decision: should V2 §2.5 encoder windows be revised post-hoc
based on E1.3 observations, OR kept as Phase 1.F-derived
predictions with documented deviations?

Per Q1 STRICT-with-paper-escalation ruling, the **default is
documented-prediction-miss (no post-hoc re-anchor)** to avoid
survivorship bias. mpnet's +0.18 deviation (S8), bge_large's
0% fail rate (S9), and S1's cross-domain spillover mechanism
are all paper-grade observations that would be obscured by
ex-post window adjustment.

Final ruling deferred to E1.6 Phase 1.E close after E1.4
regeneration data is available.

### §10.2 — `PENDING_V2_5_SCHEMA_REVISION` (references S7)

Decision: should V2 §5.2 schema `closest_secret_id (4 × 2)` be
revised given the corpus-disjointness finding (S7)?

Two options:
- **(a)** Restrict schema to 4 × 1 (encoders × 90-entry only) for
  E1 validation scope. Consistent with E1.3.4 actual implementation.
- **(b)** Introduce explicit 60-entry-legacy-reference field
  semantics distinct from V1b BLOCKING measurement (e.g.,
  `legacy_60_ref_<encoder>` fields populated as informational).

Final ruling deferred to E1.6 Phase 1.E close.

---

## §11 — Process Discipline Events

E1.3 surfaced 5 process events documented transparently:

### §11.1 — View-before-implement catches (4 events)

| # | Event | Phase | Outcome |
| --- | --- | --- | --- |
| 1 | FAISS cosine convention pre-spec ("1 − L2/2" hint vs actual IndexFlatIP direct cosine) | E1.3.1 pre-impl | Verified against `build_phase1F_indexes.py` before writing V1a |
| 2 | `target_secret_id` Option B Q4-ratification overwriting V2 §5.3 author-intent | E1.3.2 post-impl | `.bak` restore + Option C three-way debate → schema fix |
| 3 | V1b STRICT vs LOOSE Q1 ambiguity (user's brief recommendation conflicted with V2 §4.3 spec) | E1.3.4 pre-impl | Pushback led to STRICT-with-paper-escalation hybrid ruling |
| 4 | 60-entry corpus disjointness (V2 §5.2 schema assumed subset relationship; actual is parallel canonical sources) | E1.3.4 pre-flight | Q5 re-ruling to Option (b) deferred 60-entry; S7 finding emerged |

### §11.2 — Stop-and-disclose events (1 event)

| # | Event | Phase | Outcome |
| --- | --- | --- | --- |
| 5 | V5b refactor tail-print bug — `print(f"... {report['wall_seconds']}")` referenced deleted variable after V5b's report-dict was refactored away | E1.3.5 V5b merge refactor | Crashed first re-run with `NameError`; merged v1b artifact had already been written before crash → deleted intermediate file, fixed reference to `v5b_section['v5b_wall_seconds']`, re-ran cleanly. No data loss. |

All 5 events resolved without scope creep; each surfaced a
paper-grade finding or schema correction.

---

## §12 — Reproducibility Provenance

### §12.1 — Pinned components

| Component | Pin | Source |
| --- | --- | --- |
| MiniLM | `sentence-transformers/all-MiniLM-L6-v2 @ c9745ed1d9f207416be6d2e6f8de32d1f16199bf` | `PINNED_REVISIONS` |
| mpnet | `sentence-transformers/all-mpnet-base-v2 @ e8c3b32edf5434bc2275fc9bab85f82640a19130` | `PINNED_REVISIONS` |
| bge-large | `BAAI/bge-large-en-v1.5 @ d4aa6901d3a41ba39fb536a557fa166f842b0e09` | `PINNED_REVISIONS` |
| FinLang | `FinLang/finance-embeddings-investopedia @ 37d7594d02e3d656a241e099e39ac50ab921f999` | `PINNED_REVISIONS` |

All 4 pins verified byte-identical against
`eval/results/phase1_F/build_log.json:cells[*].encoder_revision`.

### §12.2 — FAISS indexes (all `IndexFlatIP` on normalized vectors → cosine direct)

| Cell | Path | dim | ntotal |
| --- | --- | --- | --- |
| minilm × 90 | `data/index/secrets_v2.faiss` (unsuffixed; historical naming) | 384 | 90 |
| mpnet × 90 | `data/index/secrets_v2__mpnet.faiss` | 768 | 90 |
| bge_large × 90 | `data/index/secrets_v2__bge_large.faiss` | 1024 | 90 |
| finlang × 90 | `data/index/secrets_v2__finlang.faiss` | 768 | 90 |

All 4 meta pickles verified byte-identical secret set (same 90
`_id`s in same order across encoders).

### §12.3 — Canonical artifacts

| Path | Size | Role |
| --- | --- | --- |
| `scripts/validate_hard_negatives.py` | 1463 LOC | Validator (4-mode CLI) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | 65 entries × 21 fields each | Post-V5b canonical corpus |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` | rotates per run | Atomic-write rollback target |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` | 34207 bytes (frozen 2026-05-21) | Permanent pre-V1a baseline |
| `eval/results/phase1_E/validation/v1a_20260522T013349Z.json` | 6691 bytes | V1a canonical (historical) |
| `eval/results/phase1_E/validation/v1b_20260523T045118Z.json` | 24992 bytes | **V1b + V5b merged canonical (FINAL)** |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | 4680 bytes | R6 audit log (4 Layer 5 entries) |
| `eval/results/phase1_E/validation/v1a_band_report.md` | 18199 bytes | E1.3.3 markdown |
| `eval/results/phase1_E/validation/outlier_inventory.md` | 15924 bytes | E1.3.6 markdown |
| `PHASE_1E_E1_3_RESULTS.md` (this document) | E1.3.7 | E1.3 close-out |

### §12.4 — Cost and wall

| Stage | LLM cost | Wall |
| --- | --- | --- |
| E1.3.1 check-only | $0 | ~5s |
| E1.3.2 V1a | $0 | ~7s |
| E1.3.3 markdown | $0 | ~30 min authoring |
| E1.3.4 V1b | $0 | ~22s + ~15 min for findings ratification |
| E1.3.5 V5b + R6 | $0 | ~1s |
| E1.3.6 outlier inventory | $0 | ~30 min authoring |
| E1.3.7 results doc (this) | $0 | ~1.5 hours authoring |
| **Total E1.3** | **$0** | **~7.5 hours human + ~35s compute** |

Within all per-step ($0.005) and per-phase ($0.40) cost caps.

---

## §13 — Commit-Prep Summary

Per project convention, no commit is initiated by the validator.
The following enumeration is informational; user runs git
operations manually.

### §13.1 — Files modified or added since `61f087c`

```
M  data/benchmark/hard_negatives_seeds_draft.jsonl     (V1a + V1b + V5b fields added; 65 entries)
?? data/benchmark/hard_negatives_seeds_draft.jsonl.bak (operational; rotates per run)
?? data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a (permanent pre-V1a baseline)
?? scripts/validate_hard_negatives.py                  (1463 LOC; 4-mode validator)
?? eval/results/phase1_E/                              (validation output dir)
   ├── validation/v1a_20260522T010429Z.json            (historical, TOP_K=5)
   ├── validation/v1a_20260522T012840Z.json            (historical, TOP_K=10 Option C)
   ├── validation/v1a_20260522T013349Z.json            (V1a canonical)
   ├── validation/v1a_band_report.md                   (E1.3.3 markdown)
   ├── validation/v1b_20260523T030118Z.json            (historical, pre-S8/S9/S10/S11)
   ├── validation/v1b_20260523T031304Z.json            (historical, pre-V5b merge)
   ├── validation/v1b_20260523T045118Z.json            (V1b + V5b merged canonical)
   ├── validation/r6_audit.jsonl                       (R6 audit log)
   └── validation/outlier_inventory.md                 (E1.3.6 markdown)
?? PHASE_1E_E1_3_RESULTS.md                            (E1.3.7 close-out; this doc)
```

### §13.2 — `.gitignore` suggestion

`.gitignore` currently has no `.bak` pattern. **Recommend
adding:**

```
# Validator atomic-write artifacts (rotates per run; never committed)
*.jsonl.bak
```

Note: `.preV1a` should likely be committed (it's a stable baseline
snapshot, not an operational rotator); leaving that decision to
the user.

### §13.3 — Suggested commit message

```
phase1E: E1.3 close - V1a + V1b + V5b validator pipeline + 10 paper findings

- V1a MiniLM per-category band (12 outliers, 81.5% pass)
- V1b 3 secondary encoders (mpnet 21.5%, bge_large 0%, finlang 6.2%)
- V5b exact-string match (0 hits across 19500 comparisons; S12)
- R6 audit log (4 Layer 5 paraphrase signatures, V2 §7.2 spec)
- 10 documented paper findings: S1/S2/S5/S6/S7/S8/S9/S10/S11/S12
- 2 PENDING V2.5 revision decisions (plan + schema)
- Schema honors V2 §5.2 + §5.3 Option C dual-field
- $0 LLM cost across all E1.3.1-7 sub-steps
```

### §13.4 — Files NOT to commit

- `.bak` operational rotator (per §13.2)
- `__pycache__/` (already gitignored)

---

## §14 — Next Phase Roadmap

### §14.1 — E1.4 — Regeneration of below-band outliers + Layer 5 review

Inputs from E1.3:
- 19 entries marked `defer_to_E1_4` (V1a below-band cross-domain
  spillover + V1b mpnet-only above-band)
- 2 entries marked `requires_content_review_at_E1_4` (HN_SEED_016,
  HN_GEN_059)
- 2 entries marked `retained_non_paraphrase` (HN_GEN_051,
  HN_GEN_056)

E1.4 scope (informational; not in this session):
- Decide per-entry: drop / refine / retain
- Action-1a-style content review for the 2 Layer 5 unreviewed
- Re-generate dropped entries per V1a + V1b + V5b BLOCKING
  semantics
- Re-run validator on regenerated corpus

### §14.2 — E1.5 — Manual spot-check + corpus filtering

V2 §4.1 V2 (benign check) is manual per V2 spec. E1.5 performs
human review of every hard-neg query for benign-in-expected-
answer-sense semantics.

### §14.3 — E1.6 — Phase 1.E close

- Final corpus rename: `hard_negatives_seeds_draft.jsonl` →
  `hard_negatives.jsonl` per V2 §5.1
- V2.5 PENDING decisions ratified (both PENDING blocks resolved
  here or earlier at E1.3.7)
- `PHASE_1E_RESULTS.md` (Phase 1.E master close-out)
- Commit + push (user manual)

### §14.4 — Phase 2 — `eval/run_full_pipeline_eval.py` integration

E2 consumes the closed 1.E hard-neg corpus and runs the 8-cell
ablation matrix evaluation; this is the eventual paper §IV
output.

---

*End of `PHASE_1E_E1_3_RESULTS.md`. E1.3 sub-phase PASS;
deliverables complete; deferred items handed off cleanly to
E1.4 + E1.6. Standing by for user manual commit + E1.4 kickoff.*
