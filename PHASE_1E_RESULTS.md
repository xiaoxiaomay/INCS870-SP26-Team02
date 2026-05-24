# Phase 1.E — Hard-Negative Corpus + Validator Pipeline: Master Results

> **Status:** Phase 1.E E1.1–E1.5 COMPLETE. E1.6 Part 1 (this
> document + corpus rename suggestion) completed in this session;
> E1.6 Part 2 (resolve 2 PENDING V2.5 decisions + batched commit
> + push) deferred to next session for fresh-state judgment.
>
> Phase 1.E delivers: a 65-entry hard-negative corpus (30 manual
> + 35 audit-driven LLM-generated), a 4-mode validator pipeline
> (V1a / V1b / V5b + R6 audit log) at 1773 LOC, **12 paper-
> publishable findings** (S1–S14 with S3/S4 sequential gaps), and
> **2 PENDING V2.5 plan/schema revision decisions** (deferred for
> next-session resolution). Total LLM cost across all 5 sub-phases:
> **$0.035** (E1.2 generation only). Cumulative wall: ~16–18
> hours across 5 sessions.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` (V2 plan; ratified 2026-05-11).
> - Sub-phase RESULTS docs (E1.1 through E1.5):
>   - `PHASE_1E_E1_1_RESULTS.md` (508 lines; 30 manual seeds)
>   - `PHASE_1E_E1_2_RESULTS.md` (504 lines; 35 LLM-generated + audit framework)
>   - `PHASE_1E_E1_3_RESULTS.md` (661 lines; V1a + V1b + V5b validators + 10 findings)
>   - `PHASE_1E_E1_4_RESULTS.md` (615 lines; 23 outlier disposition + S13)
>   - `PHASE_1E_E1_5_RESULTS.md` (413 lines; V2 benign check 65/65 PASS + S14)
>
> **Outputs (authoritative artifacts):**
> - `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries
>   × 22 fields; rename to `hard_negatives.jsonl` per V2 §5.1
>   deferred to Part 2).
> - `scripts/validate_hard_negatives.py` (1773 LOC; 4-mode CLI).
> - `eval/results/phase1_E/validation/` (9 validation artifacts).
> - This document (Phase 1.E master close-out).

---

## §1 — Executive Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| Sub-phases complete | **E1.1 + E1.2 + E1.3 + E1.4 + E1.5** (E1.6 Part 1 = this doc; Part 2 deferred) |
| Hard-neg corpus entries | **65** (30 manual seeds + 35 LLM-generated) |
| JSONL fields per entry | **22** (10 author-set + 12 validator-populated) |
| Validator script | `scripts/validate_hard_negatives.py` (**1773 LOC**, 4-mode CLI) |
| Validator stages run | V1a (MiniLM Step-1) + V1b (3-encoder Step-2) + V5b (exact-match) + V2 (manual benign) + R6 audit log |
| **Paper-publishable findings** | **12** (S1, S2, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14) |
| Sequential finding gaps | S3, S4 (early-rejected candidates during V1a investigation) |
| PENDING V2.5 revisions | **2** (plan revision; schema revision) — deferred to Part 2 |
| Total Phase 1.E LLM cost | **$0.035** (E1.2 generation only; E1.3+ all $0) |
| Cumulative wall (5 sessions) | ~16–18 hours human + ~35 seconds compute |
| Corpus mutations from validators | 0 drops (all 23 outliers retained per Option B + STRICT-with-paper-escalation precedents) |

### §1.2 — Phase 1.E milestone gate (master)

PASS (8 / 8 acceptance criteria):

- ✓ E1.1 manual-seed corpus delivered (30 entries, T1–T6 ruled).
- ✓ E1.2 audit-driven generation pipeline production-stable
  (35 entries, $0.035 LLM, anti-pattern audit framework).
- ✓ E1.3 V1a + V1b + V5b validators implemented + executed;
  R6 audit log seeded per V2 §7.2 spec.
- ✓ E1.4 23 outliers dispositioned (0 drops; Layer 5 content-
  reviewed; Layer 3 batch ruling).
- ✓ E1.5 V2 §4.1 BLOCKING manual benign check 65/65 PASS.
- ✓ JSONL schema honors V2 §5.2 + §5.3 dual-convention
  (Option C); 22 fields per entry.
- ✓ 12 paper-publishable findings ratified + embedded in canonical
  JSON artifact + propagated through R6 audit log cross-refs.
- ✓ Three-tier corpus snapshot discipline maintained
  (`.jsonl` + `.bak` rotator + `.preV1a` permanent baseline).

---

## §2 — Phase 1.E Scope

V2 plan §1–§10 ratified the Phase 1.E target as a **hard-negative
corpus** that exercises the v9 cosine-band defender against
benign-but-superficially-similar queries — establishing the False
Positive Rate (FPR) envelope distinct from attack-corpus True
Positive Rate (TPR).

### §2.1 — Scale ruling (per E1.4 §1.6)

V2 §2.4 target: **200 queries** with §7.1 R9 floor of 190.

**Actual scale: 65 entries.** Per E1.4 Q2 ruling, **65-entry close
for v10 paper**; 200-entry expansion deferred to v11 future work.

Rationale: all 12 findings are corpus-scale-independent mechanistic
observations (cross-domain spillover, encoder calibration,
vocabulary overlap, false-positive analysis); 2-month timeline
tight; Phase 1.F's matching scale; v10 demonstrates methodology,
v11 validates statistical robustness.

### §2.2 — Sequencing divergence (per E1.4 §1.5)

V2 §10.1 envisioned: E1.3 = LLM generation, E1.4 = human filter,
E1.5 = validator + finalize.

Actual sequencing: E1.2 absorbed V2's E1.2 + E1.3 (audit-driven
generation merged into single phase); E1.3 absorbed V2's E1.5
(validator pipeline); E1.4 combined V2's E1.4 (human filter
for paraphrase candidates) + V2's E1.5 (outlier resolution);
E1.5 covered V2's E1.4 row of §4.1 (manual benign check).

Documented explicitly per reviewer-grade audit hygiene.

---

## §3 — Sub-Phase Summaries

### §3.1 — E1.1 (Manual Seeds, 2026-05-12 to 2026-05-20)

30 manual-seed hard-negatives authored across 6 linguistic
categories (A–F) × 6 alpha domains (price_volume_momentum,
event_driven, statistical_arbitrage, alternative_data,
factor_neutral, ml_signals). T1–T6 design-tension rulings closed
in Round 2; all 30 entries `manually_reviewed: true` with
`anchor_tier: "L1"` per T4 ruling. HN_SEED_006 PivotalPath
de-dup applied. $0 LLM, ~3.5 hours wall.

Full details: `PHASE_1E_E1_1_RESULTS.md`.

### §3.2 — E1.2 (Audit-Driven Generation, 2026-05-12 to 2026-05-21)

35 LLM-generated hard-negatives (HN_GEN_031–065) appended via
`scripts/generate_hard_negatives.py` (~617 LOC). Model:
`gpt-5-mini-2025-08-07` (pinned in
`core/config_loader.py:PINNED_OPENAI_GENERATION_MODEL_E1_2`).

**Anti-pattern audit framework** (1035-line `PHASE_1E_ANTI_PATTERN_AUDIT.md`)
ratified 20/20 decision points. Per-category anti-pattern rules
injected into generation prompts; 0 cross-category drift hard
failures across 35 entries.

Generation pipeline reliability metrics:
- 7 batches × 5 queries = 35 generated
- 0/35 rejects on Round 1
- 3 borderline cases resolved per audit framework
- Cost variance ±6% across batches; wall 4.3–5.4s per batch
- 5 defects observed pre-stabilization; 0 defects post-fix (reasoning_effort="minimal" + max_completion_tokens=8000)
- **Total E1.2 LLM cost: ~$0.035** (within $0.10/step cap, 35% utilization)

Sub-cell coverage: all 36/36 sub-cells covered (6 cat × 6 alpha-
domain); 7 sub-cells "rich" (n=5–6) from audit-driven batches;
29 sub-cells degenerate (n=1) from manual-seed coverage. Sub-cell
distribution becomes a paper finding (S14) at E1.5.

Full details: `PHASE_1E_E1_2_RESULTS.md`.

### §3.3 — E1.3 (V1a + V1b + V5b Validators, 2026-05-21 to 2026-05-22)

7 sub-steps (E1.3.1 through E1.3.7) implementing the V2 §4.1
BLOCKING validator matrix:

- **E1.3.1** — Infrastructure verification (`--check-only`); 4-mode CLI established
- **E1.3.2** — V1a MiniLM per-category band; 53/65 PASS (81.5%); 12 outliers; TOP_K=10 + Option C dual-field schema
- **E1.3.3** — V1a band-distribution markdown report (`v1a_band_report.md`, 390 lines)
- **E1.3.4** — V1b 3-encoder cosine band; no per-encoder BLOCKING escalation (max 21.5% fail rate); mpnet substantial-deviation +0.18 triggers V2 §4.4 V2.5 plan revision
- **E1.3.5** — V5b exact-string match + R6 audit log; 0/65 hits; 4 Layer 5 paraphrase signatures
- **E1.3.6** — Outlier inventory (`outlier_inventory.md`, 306 lines); 23 unique outliers (35.4%)
- **E1.3.7** — RESULTS doc (`PHASE_1E_E1_3_RESULTS.md`, 661 lines)

**10 findings emerged from E1.3** (S1, S2, S5, S6, S7, S8, S9, S10, S11, S12).

Validator LOC trajectory: 394 (V1a-only) → 527 → 921 → 1106 →
1395 → 1463 (V5b). $0 LLM. Cumulative wall ~7.5 hours across 2
sessions.

Full details: `PHASE_1E_E1_3_RESULTS.md`.

### §3.4 — E1.4 (Outlier Disposition + S13, 2026-05-23)

23 outliers from E1.3.6 dispositioned in single ~2.5-hour
session. Per V1a Option B + V1b STRICT-with-paper-escalation
precedents:

- 4 Layer 5 candidates: all `retained_non_paraphrase` (2 from
  V1a Action 1a 2026-05-21; 2 from E1.4 content review)
- 9 V1a below-band outliers: `retained_with_paper_finding_reference`
  with S1 reference (cross-domain spillover)
- 9 V1b mpnet above-band outliers: `retained_with_paper_finding_reference`
  with S8 reference (+ S11 for Cat D/E)
- 1 multi-validator outlier (HN_SEED_013): S1 + S8 references
- **0 drops; 23 retained**

R6 audit log expanded from 4 → 23 entries.

**1 new finding emerged from E1.4: S13** (Layer 5 paraphrase signature 100% false-positive rate).

Validator LOC: 1463 → 1700 (+S13 + Layer 3 R6 audit builder).

Full details: `PHASE_1E_E1_4_RESULTS.md`.

### §3.5 — E1.5 (V2 Benign Check + S14, 2026-05-23)

V2 §4.1 BLOCKING manual benign-in-expected-answer-sense check
applied to all 65 entries (full review per Q1, not sampling).
6-criterion checklist (E1.5 Q2 ratified): industry-standard
knowledge / aggregated statistics / hypothetical-educational
PASS vs fund-specific parameter / operational specifics /
malformed FAIL.

**Result: 65/65 PASS (100%), 0 FAIL, 0 BORDERLINE.** Per-source
HN_SEED 30/30, HN_GEN 35/35. Per-category all 100%.

**1 new finding emerged from E1.5: S14** (sub-cell distribution
audit-driven concentration), unifying corpus-structural pattern
+ V2 100% PASS into triple-layered defense-in-depth narrative.

JSONL schema extended: `v2_benign_check` field added (V2 §5.2
extension; 22 fields per entry).

Validator LOC: 1700 → 1773.

Full details: `PHASE_1E_E1_5_RESULTS.md`.

---

## §4 — Findings Catalog (12 paper-publishable)

Full prose for each finding embedded in `scripts/validate_hard_negatives.py:DOCUMENTED_FINDINGS`
+ propagated to every canonical V1b artifact's `documented_findings`
block. Summary catalog with source attribution:

### §4.1 — V1a-derived (E1.3.2 investigation)

| ID | Title | Type |
| --- | --- | --- |
| **S1** | Cross-domain spillover (new failure mode) | Structural finding |
| **S2** | Audit-framework efficacy (5× E1.1 vs E1.2 below-band fail rate) | Corpus-quality finding |
| **S5** | Query length is not a band discriminator | Null-finding |
| **S6** | Author-intent vs encoder-measurement divergence (17%/67%/40%) | Methodology finding (Option C schema enabled) |

### §4.2 — V1b-derived (E1.3.4)

| ID | Title | Type |
| --- | --- | --- |
| **S7** | Corpus-version disjointness (60 ⊥ 90) | Schema-vs-reality (pre-flight catch) |
| **S8** | mpnet expected-band prediction-miss +0.18 | Calibration deviation, V2.5 trigger |
| **S9** | bge_large band permissiveness (0/65 outliers) | Informative null result |
| **S10** | Encoder-family consensus structurally weak (13.8% exact agreement) | Reviewer-clarifying methodology |
| **S11** | Cat D + Cat E cross-encoder above-band concentration | Linguistic-category × encoder structural pattern |

### §4.3 — V5b-derived (E1.3.5)

| ID | Title | Type |
| --- | --- | --- |
| **S12** | V5b zero corpus contamination (Layer 1 prompt template held) | Audit-grade null result |

### §4.4 — E1.4-derived

| ID | Title | Type |
| --- | --- | --- |
| **S13** | Layer 5 paraphrase signature 100% false-positive rate | R6 Layer 5 methodology clarification |

### §4.5 — E1.5-derived

| ID | Title | Type |
| --- | --- | --- |
| **S14** | Sub-cell distribution audit-driven concentration + triple-layered defense-in-depth | Corpus-structural audit-framework efficacy |

### §4.6 — Sequential gaps note

**S3 / S4 do not exist** — sequential gaps from early-rejected
candidates during V1a investigation cycle. Preserved as honest
record-keeping (vs renumbering, which would obscure the
investigation history).

### §4.7 — Cross-finding linkages

| Linkage | Description |
| --- | --- |
| S2 ↔ S6 | Audit-framework efficacy (S2) mechanistically explained by author-vs-measurement divergence (S6) |
| S2 ↔ S14 | Audit-framework efficacy at accuracy level (S2) + density level (S14) |
| S8 ↔ S11 | Cat D/E concentration (S11) amplified on mpnet by +0.18 prediction-miss (S8) |
| S9 ↔ S10 | bge_large 0 outliers (S9) contributes to weak cross-encoder consensus (S10) |
| S7 ↔ S12 | Corpus disjointness (S7) narrowed V5b scope to 90-entry but did not affect V5b null-result claim (S12) |
| S12 + S13 + S14 | Triple-layered defense-in-depth: V5b (S12) + Layer 5 (S13) + V2 (S14) — three independent gates against secret-content leakage |

---

## §5 — RESOLVED V2.5 Decisions (E1.6 Part 2 — 2026-05-24)

Both PENDING blocks RESOLVED at E1.6 Part 2 with **unified
Option B (document-only)** philosophy: V2 plan/schema preserved
as-is; findings stand as v10 paper observations rather than
post-hoc V2 revisions. Full RESOLVED entry texts embedded in
canonical `v1b_20260524T044018Z.json:documented_findings`.

### §5.1 — `RESOLVED_V2_5_PLAN_REVISION` (references S1 + S8 + S9)

**Decision:** Document-only (Option B). V2 §2.5 windows preserved
as-is. S1/S8/S9 stand as paper findings about Phase 1.F
prediction calibration.

**Rationale:** Survivorship bias prevention — post-hoc window
adjustment based on observed data would invite reviewer critique
of methodology integrity. Consistency: aligns with V1a Option B
precedent (retain outliers as observations) + V1b STRICT-with-
paper-escalation precedent (escalate as finding, not patch). v10
paper §VI presents honest prediction-miss reporting rather than
refit-to-data.

**Options considered:**
- (A) Numeric re-anchor — Rejected: survivorship bias risk
- (B) Document-only — **ADOPTED**: reviewer-grade epistemic honesty
- (C) Hybrid selective — Rejected: inconsistent treatment risk

**Paper implication:** v10 §VI can claim *"Phase 1.F-derived
encoder bands predicted hard-negative cosines. Observed values
deviated for mpnet (+0.18 per S8) and showed null result for
bge_large (S9). We documented these as honest reporting of
prediction calibration rather than post-hoc window refit. Cross-
domain spillover (S1) is documented as previously unanticipated
failure mode."*

**v11 future work:** Recalibrate encoder bands with full 200-
entry corpus + cross-domain spillover anticipation. v11 V2.5
plan would incorporate observed-distribution data as starting
point, not post-hoc adjustment.

### §5.2 — `RESOLVED_V2_5_SCHEMA_REVISION` (references S7)

**Decision:** Document-only (Option B). V2 §5.2 4×2 schema
preserved as-is. S7 stands as paper finding about spec design
flaw caught at implementation.

**Rationale:** V2 plan history sanctity — V2 plan documented at
specific point in time (2026-05-11 V2 ratification). View-before-
implement discipline caught spec design assumption flaw (60-entry
vs 90-entry disjointness vs implicit subset semantics).
Retroactively revising V2 plan would obscure the discovery
timeline. Consistency with Option B on plan revision.

**Options considered:**
- (A) Formal revision — Rejected: V2 plan history retrofit risk
- (B) Document-only — **ADOPTED**: view-before-implement evidence preserved

**Paper implication:** v10 §VI can claim *"Our view-before-
implement discipline caught a V2 plan design assumption flaw
(S7): 60-entry and 90-entry corpora are disjoint, not subset/
superset as implicit in §5.2 closest_secret_id (4×2) schema. We
documented this as a methodology finding rather than retroactively
revising the V2 plan, preserving discovery timeline as evidence
of engineering rigor."*

**v11 future work:** Clean v11 schema design incorporating S7
lessons: 4×1 (4 encoders × 90-entry primary corpus) with 60-entry
as separate legacy reference if backward-compatibility required.
v11 plan won't carry V2 design flaw.

### §5.3 — Resolution rationale: unified Option B philosophy

Both RESOLVED decisions adopt **Option B (document-only)** based
on the same underlying epistemic principle: **the V2 plan + its
observed deviations together constitute the v10 paper evidence,
not refitted V2.5 specs**.

This philosophy emerged organically from precedents established
during Phase 1.E:

- **V1a Option B** (E1.3.2): retain 12 outliers as observations
  rather than drop.
- **V1b STRICT-with-paper-escalation** (E1.3.4): report
  prediction-miss as finding, not patch.
- **E1.4 RETAIN-all batch ruling** (E1.4 Q3): 23 outliers all
  retained with paper-finding references.
- **E1.5 V2 100% PASS confirmation** (S14): no need for V2.5
  schema revision since corpus passes uniformly.

The unified Option B philosophy is the v10 paper's reviewer-grade
methodology contribution: honest engineering with documented
deviations rather than retroactive refit.

Findings cross-reference: both RESOLVED blocks now have
`constituent_findings` arrays linking back to the V1a/V1b
observations they were originally generated from. v10 paper §VI
should treat S1/S7/S8/S9 as the source findings and RESOLVED
blocks as the methodology-decision documentation.

---

## §6 — Methodology Innovations

The Phase 1.E sub-phases established several methodology
patterns that constitute the v10 paper's claimed contributions:

| Innovation | Where introduced | Description |
| --- | --- | --- |
| **Audit-driven generation framework** | E1.2 | Anti-pattern audit (1035 lines) + per-category prompt scaffolding; 5× lower below-band fail rate than manual seeds (S2) |
| **Layered defense-in-depth validators** | E1.3.4 + E1.3.5 + E1.5 | V1a/V1b/V5b + R6 audit log + V2; triple-layered against secret-content leakage (S12 + S13 + S14) |
| **View-before-implement discipline** | E1.3.1 onward | Pre-implementation V2-spec verbatim read + ratification cycles; caught FAISS convention error, S7 corpus disjointness pre-flight, Option C schema fix |
| **Stop-and-disclose protocol** | E1.3.2 onward | Pause on any unexpected behavior + surface for user ratification; caught V5b refactor bug, push-instruction conflict |
| **Cross-session memory infrastructure** | E1.3.2 close onward | Per-sub-phase memory files + MEMORY.md index; enables clean session resumption |
| **Dual-field schema (Option C)** | E1.3.2 ratification | V2 §5.2 + §5.3 dual-convention: `target_secret_id` (author intent) + `closest_secret_id_<enc>_<corp>` (validator measurement) coexist; enabled S6 finding |
| **R6 audit log forensic record** | E1.3.5 onward | Every validator-flagged outlier captured with disposition + findings_reference; 23 entries (4 Layer 5 + 19 Layer 3) at E1.4 close |

---

## §7 — Corpus Quality Assurance

### §7.1 — Validator pass/fail aggregate

| Validator | Result | Outliers | Mechanism |
| --- | --- | --- | --- |
| **V1a** (MiniLM Step-1) | 53/65 PASS (81.5%) | 10 below + 2 above | S1 cross-domain spillover (below); S11 Cat D/E vocabulary (above) |
| **V1b mpnet** | 51/65 PASS (78.5%) | 14 above-band | S8 prediction-miss + S11 Cat D/E |
| **V1b bge_large** | 65/65 PASS (100%) | **0** | S9 band-permissiveness null result |
| **V1b finlang** | 61/65 PASS (93.8%) | 4 above-band | S11 Cat D/E |
| **V5b** (exact-match) | 65/65 PASS (100%) | 0 hits | S12 Layer 1 prompt template held |
| **R6 Layer 5** (paraphrase signature) | 4 candidates flagged | 4 content-reviewed | S13 100% false-positive rate |
| **V2** (manual benign) | 65/65 PASS (100%) | 0 fails | S14 triple-layered defense-in-depth |

### §7.2 — Cross-encoder agreement (V1b §4.4)

| Metric | Count | Rate |
| --- | --- | --- |
| exact_secret_id (all 4 encoders pick same) | 9/65 | 13.8% |
| same_domain | 34/65 | 52.3% |
| same_tier (L1 vs L2) | 26/65 | 40.0% |
| all_blocking_pass (all 4 in window) | 42/65 | 64.6% |

Implication: encoder family is NOT consensus-picking; V1b
validates semantic-band consistency, not secret-id agreement
(S10 reviewer-clarifying observation).

### §7.3 — R6 audit log final state

`eval/results/phase1_E/validation/r6_audit.jsonl` — **23 entries**:

| Source layer | Count | Disposition |
| --- | --- | --- |
| Layer_5_V1b_paraphrase_signature | 4 | retained_non_paraphrase (S11 + S12 + S13) |
| Layer_3_V1a_below_band | 9 | retained_with_paper_finding_reference (S1) |
| Layer_3_V1b_mpnet_above_band | 9 | retained_with_paper_finding_reference (S8 + S11 if Cat D/E) |
| Layer_3_multi_validator | 1 | retained_with_paper_finding_reference (S1 + S8) |
| Layer_2_V5b | 0 | — (S12 null) |
| Layer_4_manual_drop | 0 | — (no V2 fails to drop) |

**0 drops. All 23 retained per V1a Option B + V1b STRICT-with-
paper-escalation + V2 PASS precedents.**

---

## §8 — Reproducibility Provenance

### §8.1 — Pinned components

| Component | Pin | Source |
| --- | --- | --- |
| MiniLM | `sentence-transformers/all-MiniLM-L6-v2 @ c9745ed1d9f2…` | `PINNED_REVISIONS` |
| mpnet | `sentence-transformers/all-mpnet-base-v2 @ e8c3b32edf54…` | `PINNED_REVISIONS` |
| bge-large | `BAAI/bge-large-en-v1.5 @ d4aa6901d3a4…` | `PINNED_REVISIONS` |
| FinLang | `FinLang/finance-embeddings-investopedia @ 37d7594d02e3…` | `PINNED_REVISIONS` |
| Generation LLM | `gpt-5-mini-2025-08-07` | `PINNED_OPENAI_GENERATION_MODEL_E1_2` |

All 4 encoder pins verified byte-identical against Phase 1.F M2 `build_log.json:cells[*].encoder_revision`.

### §8.2 — FAISS indexes

8 cells × `IndexFlatIP` on `normalize_embeddings=True` vectors → inner product IS cosine directly. MiniLM uses unsuffixed naming (`secrets_v2.faiss`) per Phase 1.F M2 historical artifact; other 3 encoders use `secrets_v2__{enc}.faiss` pattern.

### §8.3 — 3-tier JSONL backup discipline

| Tier | Path | Role |
| --- | --- | --- |
| Active | `hard_negatives_seeds_draft.jsonl` | Current canonical (65 × 22 fields) |
| Rotator | `hard_negatives_seeds_draft.jsonl.bak` | Atomic-write rollback target (rotates per run) |
| Permanent baseline | `hard_negatives_seeds_draft.jsonl.preV1a` | Pre-V1a clean state (34207 bytes, frozen 2026-05-21) |

V2 §5.1 final-rename target: `data/benchmark/hard_negatives.jsonl` (deferred to Part 2).

### §8.4 — Canonical validation artifacts

| Artifact | Role |
| --- | --- |
| `eval/results/phase1_E/validation/v1a_20260522T013349Z.json` | V1a canonical (historical, pre-Option-C-merge) |
| `eval/results/phase1_E/validation/v1b_20260524T002258Z.json` | **FINAL canonical** (V1a + V1b + V5b + S14; 14 documented_findings) |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | R6 audit log (23 entries) |
| `eval/results/phase1_E/validation/r6_audit.jsonl.preE14` | Pre-E1.4 R6 snapshot |
| `eval/results/phase1_E/validation/v1a_band_report.md` | E1.3.3 markdown (390 lines) |
| `eval/results/phase1_E/validation/outlier_inventory.md` | E1.3.6 markdown (306 lines) |
| `eval/results/phase1_E/validation/v2_benign_check_report.md` | E1.5 markdown (250 lines) |

### §8.5 — Cost summary

| Sub-phase | LLM cost | Wall (human) |
| --- | --- | --- |
| E1.1 | $0 | ~3.5h |
| E1.2 | $0.035 | ~5h |
| E1.3 | $0 | ~7.5h (2 sessions) |
| E1.4 | $0 | ~2.5h |
| E1.5 | $0 | ~1.5h |
| E1.6 Part 1 (this session) | $0 | ~1.5h target |
| **Total Phase 1.E** | **$0.035** | **~16-18h across 5+ sessions** |

Well within $0.10/step and $0.40/phase caps (8.75% phase utilization).

---

## §9 — Process Discipline Events

### §9.1 — View-before-implement catches (5 events across E1.3–E1.5)

| # | Event | Phase | Outcome |
| --- | --- | --- | --- |
| 1 | FAISS cosine convention pre-spec ("1 − L2/2" hint vs actual IndexFlatIP direct cosine) | E1.3.1 | Verified against `build_phase1F_indexes.py` before writing V1a |
| 2 | `target_secret_id` Option B Q4-ratification overwriting V2 §5.3 author-intent | E1.3.2 | `.bak` restore + Option A/B/C three-way debate → Option C dual-field schema fix; S6 finding emerged |
| 3 | V1b STRICT vs LOOSE Q1 ambiguity (user's brief conflicted with V2 §4.3 spec) | E1.3.4 | Pushback led to STRICT-with-paper-escalation hybrid ruling |
| 4 | 60-entry corpus disjointness (V2 §5.2 schema assumed subset; actual is parallel canonical) | E1.3.4 | Q5 re-ruling Option (b) deferred 60-entry; S7 finding emerged |
| 5 | E1.5 push-instruction conflict (pre-action vs 约束) | E1.5 | Defaulted to standing 不 push norm; user ruled defer to Part 2 batched push; lesson logged to `feedback_git_discipline.md` |

### §9.2 — Stop-and-disclose events (1 substantive)

| # | Event | Phase | Outcome |
| --- | --- | --- | --- |
| 1 | V5b refactor tail-print bug (`NameError` after report-dict deletion) | E1.3.5 V5b merge refactor | Crashed first re-run; intermediate merged file pre-crash detected; deleted + fixed + re-ran cleanly. **No data loss.** |

### §9.3 — Sequencing divergence acknowledgments (E1.4 §1.5 + this doc §2.2)

V2 plan original sequencing labels (E1.3 = LLM gen / E1.4 = human filter / E1.5 = validator) diverged from actual project sequencing due to audit-driven generation merging V2's E1.2 + E1.3 phases in E1.2. Downstream ripple shifted E1.3 = validator, E1.4 = paraphrase-suspect content review, E1.5 = V2 benign check. Documented explicitly for reviewer-grade audit hygiene.

---

## §10 — V3 + Future Work

### §10.1 — V3 parametric numeric (deferred to v11)

E1.5 §6 observation: 4 entries have numeric content (HN_SEED_001 "130/30", HN_SEED_011 "2x", HN_SEED_016 "14-day", HN_GEN_036 "70%"). All textbook constants or hypothetical-scenario parameters; PASS V2. V3 (no parametric numeric) is separate BLOCKING check not in E1.5 scope. Deferred to v11 alongside 200-entry scale-up. v10 paper §VI should disclose V3 deferral as a known scope-narrowing decision.

### §10.2 — Corpus scale 65 → 200 (deferred to v11)

Per E1.4 §1.6 ruling. v11 should apply audit-driven generation to all 36 sub-cells (achieving V8 [4, 7] balance per V2 §4.1 V8 spec) rather than scaling manual-seed methodology. S14 §4.4 paper-implication.

### §10.3 — V8 sub-cell balance (deferred to v11)

Strict V8 FAIL at 65-entry scale: 29 degenerate sub-cells + total below [190, 210]. Design-acknowledged per Q2 65-entry close ruling. Resolution in v11 alongside scale-up.

### §10.4 — Multi-agent extension (Future Work paper §VIII)

v10 paper Future Work may include reviewer-suggested multi-agent extensions to the validator pipeline. Not in Phase 1.E scope.

### §10.5 — Adaptive attacker (Phase 1.G)

Reviewer-mandatory sub-project per Phase 1.F audit feedback. Independent of remaining E1.x; can begin once Phase 1.E fully closes (post-Part 2).

---

## §11 — Phase 1.E → Paper §VI Mapping

### §11.1 — Methodology section structure for v10 paper

Phase 1.E findings + methodology innovations map into v10 paper sections as follows (proposed; subject to paper-rewrite session review):

| Paper section | Phase 1.E sources |
| --- | --- |
| §V Methodology — Corpus Construction | E1.1 (manual seeds) + E1.2 (audit-driven generation framework) + V2 §2.2 taxonomy + V2 §2.4 size rationale |
| §V Methodology — Validation Pipeline | E1.3 (V1a + V1b + V5b architecture) + V2 §4 spec + R6 6-layer mitigation chain |
| §VI Reproducibility | E1.3 pinned components + FAISS conventions + 3-tier backup + 65-entry close + V3 deferral + sequencing divergence |
| §VI Findings | S1–S14 (12 findings) — each finding gets 1–2 paragraphs |
| §VII Limitations / Future Work | V8 sub-cell balance deferral + 200-entry v11 + V3 v11 + multi-agent + Phase 1.G integration |

### §11.2 — Finding-to-section traceability

| Finding | Primary paper placement |
| --- | --- |
| S1, S5, S6 | §VI Findings (V1a-derived) |
| S2 | §V Methodology — Corpus Construction (efficacy claim) |
| S7 | §VI Reproducibility (corpus-version disjointness disclosure) |
| S8, S9 | §VI Findings (V1b calibration) — or §VII if absorbed into V2.5 plan revision |
| S10 | §V Methodology — Validation Pipeline (cross-encoder consensus clarification) |
| S11 | §VI Findings (linguistic-category × encoder structural pattern) |
| S12, S13, S14 | §V Methodology — triple-layered defense-in-depth narrative |

Final paper placement determined at paper-rewrite session.

---

## §12 — Next Phase Roadmap

### §12.1 — E1.6 Part 2 (next session)

Tasks:
1. **Resolve `PENDING_V2_5_PLAN_REVISION`** — confirm Q1 STRICT-with-paper-escalation default (no post-hoc re-anchor).
2. **Resolve `PENDING_V2_5_SCHEMA_REVISION`** — ratify Option (a) restrict V2 §5.2 to 4×1 (90-entry only) for v10.
3. **Corpus rename per V2 §5.1** — `git mv hard_negatives_seeds_draft.jsonl hard_negatives.jsonl` + update validator code constants (sequence in this doc's §13).
4. **Update DOCUMENTED_FINDINGS** with RESOLVED_* entries (or remove PENDING blocks if cleanly closed).
5. **Write `PHASE_1E_E1_6_RESULTS.md`** Part 2 close-out.
6. **Update this master document's §5** post-resolution.
7. **User batched commit + push** (`7f57f05` E1.4 + `e8bc030` E1.5 + Part 1 commit + Part 2 commit pushed together as Phase 1.E logical close).

Estimated wall: ~1.5–2 hours.

### §12.2 — Phase 1.G (after Phase 1.E full close)

Adaptive attacker sub-project. Reviewer-mandatory per Phase 1.F audit feedback. Independent of paper rewrite; can run in parallel. Estimated 3–5 days wall.

### §12.3 — Paper rewrite (§V + §VI + §VII + integration)

All 12 findings + 2 (resolved or pending) V2.5 decisions need paper placement. Estimated 15–20 hours focused writing.

### §12.4 — Realistic timeline to v10 submission-ready

~3 weeks from E1.6 Part 2 close:
- Week 1: Phase 1.G adaptive attacker
- Week 2: Paper §V + §VI + §VII drafts
- Week 3: Integration + review + final polish

---

## §13 — Part 1 Commit-Prep

### §13.1 — Files in this Part 1 commit

```
?? PHASE_1E_RESULTS.md   (master close-out aggregating E1.1-E1.5; this document)
```

This is the only new artifact from Part 1. Corpus rename + validator code updates DEFERRED to Part 2 alongside PENDING resolution + batched push.

### §13.2 — Suggested Part 1 commit message

```
phase1E: Part 1 of close - master RESULTS doc aggregating E1.1-E1.5

PHASE_1E_RESULTS.md authored as master Phase 1.E close-out:
- 12 paper-publishable findings (S1-S14 with S3/S4 gaps)
- 2 PENDING V2.5 decisions (DEFERRED to Part 2)
- Corpus: 65 entries × 22 fields, paper-grade methodology
- Total Phase 1.E LLM cost: $0.035 (E1.2 generation only)
- Cumulative wall: ~16-18 hours across 5 sub-phases

Part 2 (next session) resolves PENDING decisions, renames corpus
per V2 §5.1, and batches push (7f57f05 E1.4 + e8bc030 E1.5 +
this Part 1 + Part 2 commits pushed together at Phase 1.E
logical close).
```

### §13.3 — Files DEFERRED to Part 2

| File | Part 2 action |
| --- | --- |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | `git mv → hard_negatives.jsonl` per V2 §5.1 |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` | `git mv → hard_negatives.jsonl.preV1a` (preserve baseline) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` | Delete (operational rotator) |
| `scripts/validate_hard_negatives.py` | Update `HARD_NEG_PATH` + docstring (3 refs) |
| `scripts/generate_hard_negatives.py` | Update `DEFAULT_SEEDS_PATH` + docstring + CLI help (3 refs) |
| `scripts/validate_hard_negatives.py:DOCUMENTED_FINDINGS` | Add `RESOLVED_*` entries (or remove PENDING) post-decision |
| `eval/results/phase1_E/validation/v1b_*.json` | Idempotent refresh post-DOCUMENTED_FINDINGS update |
| `PHASE_1E_E1_6_RESULTS.md` | NEW Part 2 close-out doc |
| This document `PHASE_1E_RESULTS.md` | Update §5 post-PENDING-resolution |

---

*End of `PHASE_1E_RESULTS.md` Part 1. Phase 1.E E1.1–E1.5 master
close-out complete; PENDING V2.5 decisions + corpus rename +
Phase 1.E batched commit/push deferred to next-session Part 2.*
