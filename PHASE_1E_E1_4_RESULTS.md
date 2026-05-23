# Phase 1.E E1.4 — Outlier Disposition + S13 Finding: Results

> **Status:** PASS. The 23 outliers surfaced by E1.3's V1a + V1b +
> V5b validator pipeline are fully dispositioned: 0 drops, all 23
> retained per V1a Option B + V1b STRICT-with-paper-escalation
> precedents. One new paper finding (**S13 — Layer 5 paraphrase
> signature 100% false-positive rate**) emerged from the 4/4 Layer
> 5 candidate content review pattern. Total findings: **11**
> (S1–S13 with S3/S4 sequential gaps) + 2 PENDING V2.5 revision
> decisions. R6 audit log expanded from 4 → 23 entries (full
> forensic record of every validator-flagged outlier).
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §2.4 + §4.3 + §6 + §7.1 + §7.2 +
>   §10.1 (E1.4 references scattered; no single dedicated section).
> - `PHASE_1E_E1_3_RESULTS.md` (E1.3 close — 23 outliers handed off
>   for E1.4 disposition).
> - `eval/results/phase1_E/validation/outlier_inventory.md` (E1.3.6
>   per-outlier categorization).
> - `eval/results/phase1_E/validation/r6_audit.jsonl.preE14`
>   (pre-E1.4 snapshot, 4 entries; rollback target).
>
> **Outputs (authoritative artifacts):**
> - `scripts/validate_hard_negatives.py` (1700 LOC; +237 LOC over
>   E1.3 close for S13 entry + Layer 3 R6 audit builder).
> - `eval/results/phase1_E/validation/v1b_20260523T134252Z.json`
>   (**final E1.4 canonical artifact**; 13 documented_findings
>   keys = 11 S-findings + 2 PENDING).
> - `eval/results/phase1_E/validation/r6_audit.jsonl` (23 entries:
>   4 Layer 5 + 9 Layer 3 V1a below-band + 9 Layer 3 V1b mpnet
>   above-band + 1 Layer 3 multi-validator).
> - `eval/results/phase1_E/validation/r6_audit.jsonl.preE14`
>   (4-entry pre-E1.4 snapshot; permanent rollback artifact).
> - `PHASE_1E_E1_4_RESULTS.md` (this document).

---

## §1 — E1.4 Close Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| Outliers dispositioned | **23/23** (matches E1.3.6 inventory) |
| Drops | **0** |
| Retained — Layer 5 (content-reviewed) | **4** (HN_SEED_016, HN_GEN_051, HN_GEN_056, HN_GEN_059) |
| Retained — Layer 3 (S1/S8 batch ruling) | **19** (9 V1a below + 9 V1b mpnet + 1 multi-validator) |
| Content reviews performed this session | **2** (HN_SEED_016, HN_GEN_059) |
| Content reviews inherited from E1.3.2 (V1a Action 1a) | 2 (HN_GEN_051, HN_GEN_056) |
| Total Layer 5 candidate reviews | **4/4** → 0/4 paraphrase = **S13** |
| New paper findings | **1** (S13) |
| Total documented findings | **11** (S1, S2, S5, S6, S7, S8, S9, S10, S11, S12, **S13**) |
| PENDING V2.5 revision decisions | **2** (plan revision, schema revision) |
| Validator script LOC | 1463 → **1700** (+237) |
| R6 audit log entries | 4 → **23** (+19) |
| LLM cost | **$0** (entirely human content review + validator code edits) |
| Session wall | ~2.5 hours |

### §1.2 — Phase 1.E E1.4 milestone gate

PASS (6 / 6 acceptance criteria):

- ✓ All 4 Layer 5 candidates content-reviewed (V1a Action 1a +
  E1.4 reviews complete).
- ✓ All 19 standard outliers dispositioned with paper-finding
  references (S1, S8, S11 where applicable).
- ✓ R6 audit log forensic record complete (23 entries; 4 Layer 5
  + 19 Layer 3; Layer 2 = 0 per S12).
- ✓ S13 finding documented in validator `DOCUMENTED_FINDINGS`
  block + propagated to canonical V1b JSON artifact + all 4 Layer
  5 audit entries `findings_reference`.
- ✓ Atomic write discipline maintained (`r6_audit.jsonl.preE14`
  snapshot preserved; `.preV1a` permanent baseline untouched).
- ✓ Sequencing divergence + corpus scale decision documented
  transparently (§1.5 + §1.6 below).

### §1.5 — Sequencing Divergence Documentation

V2 §10.1 sequencing assumed:
- E1.1: manual seeds
- E1.2: prompt design
- E1.3: LLM generation
- **E1.4: human filter pass**
- E1.5: validator + finalize
- E1.6: status

Actual project sequencing:
- E1.1: manual seeds (30 entries, T1–T6 ruled)
- **E1.2: audit-driven prompt design + LLM generation merged** (35
  entries; absorbed V2's E1.2 + E1.3 phases)
- **E1.3: validator (V1a + V1b + V5b)** (absorbed what V2 called
  E1.5 "validator + finalize")
- **E1.4 (this sub-phase): human filter pass + outlier
  disposition** (combines V2's E1.4 human filter + V2's E1.5
  outlier resolution)
- E1.5 (upcoming): final manual spot-check + corpus filtering
- E1.6 (upcoming): Phase 1.E close + commit

**Rationale:** during E1.1 review, the anti-pattern audit framework
emerged as a natural mechanism that bundled V2's E1.2 (prompt
design) and E1.3 (LLM generation) into a single structured phase.
The 5× E1.1-vs-E1.2 below-band-failure-rate improvement (S2 finding)
is empirical evidence that the bundled approach worked: structured
audit + per-category scaffolding + LLM generation cohere as one
pipeline, not three separable steps.

The downstream effect rippled forward: V2's E1.5 validator step
became this project's E1.3, and V2's E1.4 human filter merged with
E1.5 outlier resolution into this project's E1.4.

**Reviewer-grade audit hygiene:** documented explicitly here rather
than silently renumbered. The substantive content matches V2's
intent (human filter + outlier disposition both performed); only
the sequencing labels diverged.

### §1.6 — Corpus Scale Decision

V2 target (§2.4): **200 hard-negative queries**, with §7.1 R9 floor
of **190**. V2 §2.4's rationale for 200: binomial 95% CI ±3.0pp on
5% FPR target; sub-cell breakdown feasibility (200/36 ≈ 5.6 per
sub-cell); cost discipline ($0.275 / $0.40 cap on 8-cell run).

Actual scale: **65 entries** (30 manual + 35 LLM-generated).

**Ruling:** 65-entry close for v10 paper. **200-entry expansion
deferred to v11 future work.**

**Rationale:**

| Argument | Weight |
| --- | --- |
| All 10 (now 11) findings (S1–S13) corpus-scale-independent at 65 — they are mechanistic observations (cross-domain spillover, encoder calibration, vocabulary overlap), not statistical power claims | High |
| 2-month timeline tight; remaining work (Phase 1.G adaptive attacker + paper rewrite §V/§VI/§VII) needs reserve | High |
| Phase 1.F's matching scale (60/90 secret corpora) keeps v10 paper internally consistent | Medium |
| v11 future-work scope: "scale to 200 + validate findings hold under larger sample" — natural follow-on contribution | Medium |
| 65 = paper-grade methodology demonstration (the audit framework, V1a/V1b/V5b validator design, and per-finding mechanism explanations don't require 200 to be reviewer-defensible) | High |

**Reviewer framing:** scope sequencing, not scope shrinkage. v10
demonstrates the methodology; v11 validates statistical robustness.

---

## §2 — Scope and Acceptance Criteria

E1.4 disposes the 23 outliers surfaced by E1.3's validator
pipeline. Per E1.4 Q3 batch ruling (consistent with V1a Option B
and V1b STRICT-with-paper-escalation precedents from E1.3.2 and
E1.3.4):

- **Default disposition for V1a below-band outliers (S1):**
  retained_with_paper_finding_reference. Cross-domain spillover is
  a corpus-coverage finding, not a query-quality failure;
  regenerating won't help.
- **Default disposition for V1b mpnet-only above-band outliers
  (S8):** retained_with_paper_finding_reference. Dropping = post-
  hoc survivorship bias against mpnet's documented +0.18
  prediction-miss.
- **Layer 5 paraphrase candidates:** content-review required per
  V2 §7.2 Layer 4 spec; disposition determined by manual review
  (paraphrase → drop, non-paraphrase → retain).

V2 §7.2 Layer 4 scope ruling (Q6, this session): **practical
interpretation** — review the 4 Layer 5 candidates flagged by V1b
≥2-encoder above-band heuristic, plus the 2 V1a Action 1a content
reviews already performed (6 entries total). Defense-in-depth via
Layers 1 (prompt template), 2 (V5b exact-match, 0 hits per S12),
3 (V1b 4-encoder cross-validation) provides layered assurance;
blanket review of all 35 HN_GEN entries without specific suspicion
signal is process-for-process's-sake, not reviewer-required.

---

## §3 — E1.4 Work Performed

### §3.1 — Layer 5 Content Reviews

Two priority-queue Layer 5 candidates were content-reviewed this
session via Action-1a-style methodology (side-by-side semantic
comparison of hard-neg query + rationale against each encoder's
top-1 secret text). Both ruled `retained_non_paraphrase`.

**HN_SEED_016** (Cat D × price_volume_momentum, manual seed):

| Side | Content |
| --- | --- |
| Query | *"How is the standard 14-day RSI computed, and what does an extreme reading typically indicate about price momentum?"* |
| Rationale | *"Textbook RSI definition (14-day is Wilder's original, not proprietary); benign educational; will likely cluster very close to v2_L1_pvm_001 about RSI."* (author's E1.1 rationale **predicted** the clustering as design-intentional) |
| Convergent secret (4/4 encoders) | `v2_L1_price_volume_momentum_001` — "RSI Momentum Basics" (L1 practitioner-tier educational; *"RSI below 30 is commonly interpreted as an oversold signal..."*) |
| Cosines | minilm 0.586 (in-band), **mpnet 0.668 (above)**, bge_large 0.733 (in-band), **finlang 0.665 (above)** |
| Paraphrase verdict | **NO** — query asks computation method + general interpretation; secret states one specific practitioner rule (RSI<30→oversold) without computation explanation |
| Disposition | `retained_non_paraphrase` |

The secret is L1 practitioner-tier (not L2/L3 proprietary). Author
seed-time rationale explicitly predicted this clustering. The
vocabulary overlap is structural to two pieces of textbook RSI
content sharing common vocabulary, not semantic leakage.

**HN_GEN_059** (Cat E × alternative_data, LLM-generated):

| Side | Content |
| --- | --- |
| Query | *"In signal longevity and refresh needs, how do aggregated credit-card panels and satellite-derived physical-activity indicators compare for retail trend models?"* |
| Rationale | *"Compares signal persistence and refresh cadence across two alt-data signals; safe, high-level research query."* |
| Convergent secret (4/4 encoders) | `v2_L2_alternative_data_001` — "Satellite + Transaction Data Signals" (L2 confidential; *"We combine satellite-derived retail foot traffic data with credit card transaction signals..."*) |
| Cosines | minilm 0.558 (in-band), **mpnet 0.650 (above)**, bge_large 0.823 (in-band), **finlang 0.656 (above)** |
| Sibling precedent | HN_GEN_056 (V1a Action 1a 2026-05-21, same secret, ruled `retained_non_paraphrase` via comparison-axis vs combined-strategy semantic divergence) |
| Paraphrase verdict | **NO** — same mechanism as HN_GEN_056: query asks comparative methodology (longevity + refresh cadence); secret describes combined-source strategy for one fund |
| Disposition | `retained_non_paraphrase` |

The convergent secret is L2 confidential, but the query asks an
*operational comparison axis* (longevity / refresh) — not the
secret's proprietary content (alpha decay, entry timing, brick-
and-mortar focus). Vocabulary overlap reflects S11 mechanism in
the alternative_data domain.

### §3.2 — Batch Retain Ruling for 19 Standard Outliers

Per Q3 ratification, the 19 standard outliers were batch-
dispositioned `retained_with_paper_finding_reference` with primary
findings tagged per failure mode:

| Failure mode | Count | Primary findings | Entries |
| --- | --- | --- | --- |
| V1a below-band only (cross-domain spillover) | **9** | S1 | HN_SEED_004, HN_SEED_006, HN_SEED_007, HN_SEED_010, HN_SEED_019, HN_SEED_025, HN_SEED_028, HN_GEN_039, HN_GEN_062 |
| V1b mpnet above-band only (single-encoder; S8 mechanism) | **9** | S8 (+ S11 for Cat D/E entries) | HN_SEED_003, HN_SEED_017 *(D)*, HN_SEED_021 *(E)*, HN_GEN_033, HN_GEN_034, HN_GEN_043, HN_GEN_053 *(D)*, HN_GEN_054 *(D)*, HN_GEN_055 *(D)* |
| Multi-validator opposite-direction (V1a below + mpnet above) | **1** | S1 + S8 | HN_SEED_013 |
| **Total** | **19** | | |

Of the 9 V1b mpnet entries, 5 are in Categories D or E and
additionally reference S11 (cross-encoder vocabulary-overlap
mechanism). HN_SEED_013 is a unique multi-validator case
(opposite-direction failure across V1a and V1b) — neither a
paraphrase signature nor a single-mechanism failure; the
disposition_evidence explicitly cites both S1 (corpus-coverage on
MiniLM) and S8 (vocabulary-overlap on mpnet).

### §3.3 — Layer 4 Scope Decision (Q6)

V2 §7.2 Layer 4 verbatim: *"Author reads every generated query
during E1.4 filter pass; queries that 'feel like' they paraphrase
a secret are dropped even if they pass cosine filters."*

**Strict reading:** review all 35 HN_GEN entries.
**Practical reading (this session's ruling):** review the 4 Layer
5 candidates (V1b ≥2-encoder above-band heuristic) + the 2 V1a
Action 1a reviews already performed = **6 entries content-
reviewed**, 29 HN_GEN entries not individually content-reviewed.

**Reviewer-grade defense for the practical reading:**

| Layer | What it provides | Result |
| --- | --- | --- |
| Layer 1 (V2 §7.2) | Prompt template constraint — no literal secrets in generation context | Held; not violated during E1.2 |
| Layer 2 (V5b, S12) | Exact-string match check against 150 secrets | 0 hits across 19,500 comparisons |
| Layer 3 (V1a + V1b) | 4-encoder cosine band check | 23 outliers surfaced; all explained by S1/S8/S11 mechanisms |
| Layer 5 (heuristic) | V1b ≥2-encoder above-band flag → manual review | 4/4 candidates content-reviewed; all non-paraphrase (S13) |
| Layer 4 (human filter) | Author reading | **Practical scope: 6 entries reviewed (4 Layer 5 + 2 Action 1a)** |
| Layer 6 (regenerate-clean validation) | Re-validation after any regeneration | N/A this session (0 regenerations) |

The defense-in-depth design holds. Reviewing 29 unflagged HN_GEN
entries (no V1a/V1b/V5b/Layer-5 suspicion signal) would be process
without information — paper-grade methodology rigor is satisfied
by the flagged-entry review + the layered checks above.

---

## §4 — NEW FINDING: S13 — Layer 5 Paraphrase Signature 100% False-Positive Rate

### §4.1 — Pattern observation

V1b's ≥2-encoder above-band heuristic flagged **4 candidates**
across the 65-entry corpus:
- HN_GEN_051 (Cat D × factor_neutral; 3 encoders above-band)
- HN_GEN_056 (Cat E × alternative_data; 3 encoders above-band)
- HN_SEED_016 (Cat D × price_volume_momentum; 2 encoders above-band)
- HN_GEN_059 (Cat E × alternative_data; 2 encoders above-band)

Manual content review (V1a Action 1a + E1.4 content review):
**0/4 confirmed paraphrases, 4/4 ruled retained_non_paraphrase**.
Layer 5 false-positive rate: **100%**.

### §4.2 — Mechanism explanation

All 4 candidates exhibit the S11 vocabulary-overlap mechanism in
Categories D + E:
- Cat D (Educational/Conceptual): uses concept-name vocabulary
  that lexically aligns with secret titles + bodies (e.g.,
  "factor neutrality" ↔ "Multi-Factor Neutralization Framework";
  "RSI" ↔ "RSI Momentum Basics").
- Cat E (Comparison/Benchmarking): uses comparison-axis vocabulary
  that names two strategy/data types present in the secret corpus
  (e.g., "satellite vs credit-card" ↔ secret describing combined
  satellite + transaction strategy).

The high cosine values reflect **lexical-vocabulary convergence**
on shared finance-domain terminology, not **semantic content
leakage** of proprietary parameters or operational specifics.

### §4.3 — Paper implication

Reviewer-grade methodological clarity: **Layer 5 alone is not a
reliable paraphrase predictor in finance hard-negative corpora
where shared vocabulary between query and secret is structural
(Categories D/E by design).**

Defense-in-depth holds via layered validation:
- Layer 2 (V5b exact-match) provides primary leakage assurance
  (0 hits, S12).
- Layer 5 serves as **forensic catchment with manual review gate**,
  not as an auto-drop signal.

The V2 §7.2 R6 6-layer design correctly anticipates this via the
*"audit log reviewed before E2"* clause — V2 never claimed Layer 5
was auto-drop; it always required Layer 4 (human filter) gate.
S13 quantifies that requirement: in this corpus, **100% of Layer 5
flags would have been false-positive drops** if auto-dropped.

### §4.4 — Defense-in-depth narrative intact

S13 strengthens (not weakens) the R6 mitigation chain:
- Layer 2 + Layer 5 + Layer 4 work as designed (Layer 5 surfaces
  candidates; Layer 4 dispositions them).
- The 100% false-positive rate is **expected** given Categories
  D + E vocabulary-overlap mechanism (S11); it is not a flaw in
  Layer 5 design but a corpus-property observation.
- Future scaling (v11 to 200 entries) should track whether the
  false-positive rate remains 100% or drops as additional Layer 5
  candidates surface — this is itself a v11 research question.

---

## §5 — Final Disposition Matrix (23 outliers)

All 23 outliers retained; 0 drops. Audit IDs assigned per source
layer (Layer 5 first; then Layer 3 alphabetical by hard_neg_id).

| Audit ID | Hard-Neg | Cat | Source Layer | Disposition | Findings Ref |
| --- | --- | --- | --- | --- | --- |
| R6_AUDIT_001 | HN_SEED_016 | D | Layer 5 | retained_non_paraphrase | S11, S12, S13 |
| R6_AUDIT_002 | HN_GEN_051 | D | Layer 5 | retained_non_paraphrase | S11, S12, S13 |
| R6_AUDIT_003 | HN_GEN_056 | E | Layer 5 | retained_non_paraphrase | S11, S12, S13 |
| R6_AUDIT_004 | HN_GEN_059 | E | Layer 5 | retained_non_paraphrase | S11, S12, S13 |
| R6_AUDIT_005 | HN_GEN_033 | A | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8 |
| R6_AUDIT_006 | HN_GEN_034 | A | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8 |
| R6_AUDIT_007 | HN_GEN_039 | C | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_008 | HN_GEN_043 | A | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8 |
| R6_AUDIT_009 | HN_GEN_053 | D | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8, S11 |
| R6_AUDIT_010 | HN_GEN_054 | D | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8, S11 |
| R6_AUDIT_011 | HN_GEN_055 | D | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8, S11 |
| R6_AUDIT_012 | HN_GEN_062 | F | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_013 | HN_SEED_003 | A | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8 |
| R6_AUDIT_014 | HN_SEED_004 | A | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_015 | HN_SEED_006 | B | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_016 | HN_SEED_007 | B | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_017 | HN_SEED_010 | B | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_018 | HN_SEED_013 | C | Layer 3 multi-validator | retained_with_paper_finding_reference | S1, S8 |
| R6_AUDIT_019 | HN_SEED_017 | D | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8, S11 |
| R6_AUDIT_020 | HN_SEED_019 | D | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_021 | HN_SEED_021 | E | Layer 3 V1b mpnet | retained_with_paper_finding_reference | S8, S11 |
| R6_AUDIT_022 | HN_SEED_025 | E | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |
| R6_AUDIT_023 | HN_SEED_028 | F | Layer 3 V1a below | retained_with_paper_finding_reference | S1 |

Aggregate counts:

| Dimension | Count |
| --- | --- |
| Total dispositioned | 23 |
| `retained_non_paraphrase` (Layer 5) | 4 |
| `retained_with_paper_finding_reference` (Layer 3) | 19 |
| Drops | **0** |
| References S1 | 11 entries (9 V1a below + HN_SEED_013 + Layer-5 entries indirectly via §4) |
| References S8 | 11 entries (9 V1b mpnet + HN_SEED_013 + Layer-5 entries indirectly via §4) |
| References S11 | 9 entries (4 Layer 5 + 5 Cat D/E mpnet-only) |
| References S12 | 4 entries (all Layer 5) |
| References S13 | 4 entries (all Layer 5) |

---

## §6 — R6 Audit Log Final State

**Path:** `eval/results/phase1_E/validation/r6_audit.jsonl`
**Entries:** 23 (was 4 at E1.3.5 close; +19 during E1.4).
**Per source_layer:**

| Source layer | Count |
| --- | --- |
| `Layer_5_V1b_paraphrase_signature` | 4 |
| `Layer_3_V1a_below_band` | 9 |
| `Layer_3_V1b_mpnet_above_band` | 9 |
| `Layer_3_multi_validator` | 1 |
| `Layer_2_V5b` | 0 (null result per S12) |
| `Layer_4_manual_drop` | 0 (no entries dropped this session) |

**Snapshot:** `r6_audit.jsonl.preE14` (4680 bytes, pre-E1.4 state,
4 Layer 5 entries with provisional dispositions) preserved as
rollback artifact.

**Methodology note:** the R6 audit log is a **forensic record of
every validator-flagged entry**, not a drop list. Every entry
includes:
- `audit_id` (R6_AUDIT_NNN)
- `source_layer` (which validator + which failure mode)
- `hard_neg_id` + `category` + `domain`
- `match_type` (cosine_below_global_blocking_band / cosine_above_step2_window_single_encoder / multi_encoder_above_band / multi_validator_distinct_mechanisms)
- `matched_secret_ids` + `matched_secret_corpus`
- `evidence` (cosines per 4 encoders, closest secret IDs per encoder, above-band thresholds)
- `disposition` + `disposition_evidence` (prose explaining the ruling)
- `findings_reference` (cross-link to paper-publishable findings)
- `timestamp_utc`

This forensic record is the audit-grade trail demanded by V2 §7.2
Layer 5 + E1.6 close gate.

---

## §7 — Documented Findings Status (11 S-findings + 2 PENDING)

The canonical `DOCUMENTED_FINDINGS` block in
`scripts/validate_hard_negatives.py` (and embedded in
`v1b_20260523T134252Z.json:documented_findings`) contains:

| ID | Title | Emerged from |
| --- | --- | --- |
| **S1** | Cross-domain spillover (new failure mode) | E1.3.2 V1a investigation |
| **S2** | Audit-framework efficacy (5× E1.1 vs E1.2) | E1.3.2 V1a investigation |
| **S5** | Query length is not a band discriminator | E1.3.2 V1a investigation |
| **S6** | Author-intent vs encoder-measurement divergence (17%/67%/40%) | E1.3.2 Option C schema enabled |
| **S7** | Corpus-version disjointness (60 ⊥ 90) | E1.3.4 V1b pre-flight |
| **S8** | mpnet expected-band prediction-miss +0.18 | E1.3.4 V1b run |
| **S9** | bge_large band permissiveness (0/65 outliers) | E1.3.4 V1b run |
| **S10** | Encoder-family consensus structurally weak (13.8% exact) | E1.3.4 V1b run |
| **S11** | Cat D + Cat E cross-encoder above-band concentration | E1.3.4 V1b run |
| **S12** | V5b zero corpus contamination (Layer 1 held) | E1.3.5 V5b run |
| **S13** | Layer 5 paraphrase signature 100% false-positive rate | **E1.4 content review (this session)** |

S3 / S4 are sequential gaps (early-rejected candidates during the
V1a investigation cycle, preserved as honest record-keeping).

S13 is the only new finding from E1.4 — it emerged from the 4/4
Layer 5 candidate review pattern after HN_SEED_016 + HN_GEN_059
joined HN_GEN_051 + HN_GEN_056 in the `retained_non_paraphrase`
category.

---

## §8 — PENDING Decisions (deferred to E1.6 Phase 1.E close)

Both PENDING blocks remain unresolved post-E1.4. E1.4 did not
trigger their resolution because:

- **PENDING_V2_5_PLAN_REVISION** (references S1, S8, S9) — V2.5
  plan revision for encoder windows. E1.4 added no new
  observational data about encoder band calibration; the
  underlying S1/S8/S9 findings are unchanged. **Decision criterion
  for E1.6:** confirm Q1 STRICT-with-paper-escalation ruling
  (documented-prediction-miss, no post-hoc re-anchor) as final
  v10 paper framing.

- **PENDING_V2_5_SCHEMA_REVISION** (references S7) — V2 §5.2
  schema 4×2 vs 4×1. E1.4 did not implement 60-entry comparison;
  the schema-vs-reality gap is unchanged. **Decision criterion
  for E1.6:** ratify Option (a) restrict to 4×1 (90-entry) for v10,
  defer 60-entry-legacy-reference field semantics to v11.

Both PENDING blocks are paper-relevant but neither is gating for
E1.5 manual spot-check or commit. Final resolution at E1.6 close.

---

## §9 — Process Discipline Events

| # | Event | Outcome |
| --- | --- | --- |
| 1 | r6_audit.jsonl atomic snapshot pre-E1.4 (`r6_audit.jsonl.preE14`, 4680 bytes) | Step 1 of action sequence; rollback target preserved |
| 2 | Content review preparation: pulled query + rationale + 4 encoder × top-1 secret for HN_SEED_016 + HN_GEN_059 | Independent dual-review (user + Claude Code) prior to disposition |
| 3 | S13 emergence: 4/4 Layer 5 false-positive pattern identified by user (Claude Code provisional reading agreed; user formalized the finding) | New paper finding added to DOCUMENTED_FINDINGS; no Claude Code unilateral addition |
| 4 | Idempotent V5b re-run: validator code updated; re-ran V5b to refresh canonical JSON with 13 documented_findings keys + 23 R6 audit entries | Atomic write + .bak rotation honored; no data loss |
| 5 | View-before-implement: read E1.3 RESULTS markdown format before writing E1.4 RESULTS (this document) | Format consistency between sub-phase RESULTS docs |

No stop-and-disclose alarms triggered this session. All operations
executed within ratification scope.

---

## §10 — Reproducibility Provenance

### §10.1 — Canonical artifacts (post-E1.4)

| Path | Size | Role |
| --- | --- | --- |
| `scripts/validate_hard_negatives.py` | **1700 LOC** | Validator + 13-key DOCUMENTED_FINDINGS |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | 65 entries × 21 fields | Post-V5b canonical corpus (unchanged data since E1.3.5) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` | rotates per run | Atomic-write rollback target |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` | 34207 bytes (frozen 2026-05-21) | Permanent pre-V1a baseline |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | **4680 → 29555 bytes (23 entries)** | R6 audit log (FINAL) |
| `eval/results/phase1_E/validation/r6_audit.jsonl.preE14` | 4680 bytes | Pre-E1.4 snapshot (rollback target) |
| `eval/results/phase1_E/validation/v1b_20260523T134252Z.json` | (post-S13) | **V1b + V5b + S13 canonical (FINAL E1.4 artifact)** |
| `eval/results/phase1_E/validation/v1b_20260523T045118Z.json` | 24992 bytes | Historical (pre-S13) |
| `PHASE_1E_E1_3_RESULTS.md` | 661 lines | E1.3 close (historical) |
| `PHASE_1E_E1_4_RESULTS.md` (this) | E1.4 close | E1.4 close |

### §10.2 — Cost and wall

| Stage | LLM cost | Wall |
| --- | --- | --- |
| Content review prep (HN_SEED_016 + HN_GEN_059) | $0 | ~15 min |
| User content review (independent verification) | $0 | ~10 min |
| Step 3 r6_audit.jsonl update + Step 3.5 S13 addition | $0 | ~20 min |
| Steps 4-5 outlier categorization + r6_audit expansion | $0 | ~30 min |
| Step 6 RESULTS doc writing (this document) | $0 | ~50 min |
| **Total E1.4 session** | **$0** | **~2 hours** |

Within all per-step ($0.005) and per-phase ($0.40) cost caps.

---

## §11 — Commit-Prep Summary

Per project no-commit discipline, no commit initiated by validator.
User runs git operations manually.

### §11.1 — Files modified or added since `09b3cc2` (E1.3 close)

```
M  scripts/validate_hard_negatives.py                          (1463 → 1700 LOC; +S13 + Layer 3 R6 audit builder)
M  data/benchmark/hard_negatives_seeds_draft.jsonl             (idempotent re-run; same 65 entries × 21 fields)
M  data/benchmark/hard_negatives_seeds_draft.jsonl.bak         (rotates per run)
M  eval/results/phase1_E/validation/r6_audit.jsonl             (4 → 23 entries)
?? eval/results/phase1_E/validation/r6_audit.jsonl.preE14      (4-entry pre-E1.4 snapshot; user choice on commit)
?? eval/results/phase1_E/validation/v1b_20260523T134252Z.json  (FINAL E1.4 canonical; 13 documented_findings)
?? PHASE_1E_E1_4_RESULTS.md                                    (E1.4 close-out, this document)
```

### §11.2 — `.gitignore` consideration

`r6_audit.jsonl.preE14` parallels `hard_negatives_seeds_draft.jsonl.preV1a` from E1.3 — both are permanent snapshots of pre-mutation state. User's choice on whether to commit `.preE14`:

- **Commit (recommended):** preserves the pre-E1.4 R6 audit state as
  a permanent reproducibility checkpoint (4 Layer 5 entries with
  `requires_content_review_at_E1_4` dispositions visible in git
  history).
- **Gitignore:** treat `.preE14` as operational-only (consistent with
  `*.jsonl.bak` recommendation from E1.3 §13.2).

### §11.3 — Suggested commit message

```
phase1E: E1.4 close - outlier disposition + S13 Layer 5 finding

23 outliers dispositioned (0 drops, all retained per V1a Option B
+ V1b STRICT-with-paper-escalation precedents):
- 4 Layer 5 (all retained_non_paraphrase per content review)
- 9 V1a below-band (S1 cross-domain spillover reference)
- 9 V1b mpnet above-band (S8 prediction-miss reference, + S11 if
  Cat D/E)
- 1 multi-validator HN_SEED_013 (S1 + S8 references)

New finding S13 (Layer 5 100% false-positive rate) emerged from
4/4 paraphrase candidate review pattern. Total findings: 11
(S1-S13 with S3/S4 sequential gaps) + 2 PENDING V2.5 decisions.

Sequencing divergence acknowledged (V2 E1.4 spec scattered across
5 sections; actual sequencing diverged due to E1.2 audit-driven
generation absorbing V2's E1.2 + E1.3 phases).

Corpus scale ruling: 65-entry close for v10 paper (200-entry
target deferred to v11 future work).
```

---

## §12 — Next Phase Roadmap

### §12.1 — E1.5 — Manual spot-check + corpus filtering

V2 §4.1 V2 (benign check) is manual per V2 spec. E1.5 performs
human review of every hard-neg query for benign-in-expected-
answer-sense semantics. Estimated wall: ~1–2 hours.

Entry criteria: all 23 outliers dispositioned (this E1.4 close);
0 drops in queue.

### §12.2 — E1.6 — Phase 1.E close + commit + push

Per V2 §5.1: rename `hard_negatives_seeds_draft.jsonl` →
`hard_negatives.jsonl`. Resolve both PENDING_V2_5_* decisions.
Write `PHASE_1E_RESULTS.md` (Phase 1.E master close-out).

User manual commit + push. Estimated wall: ~30–45 minutes.

### §12.3 — v11 future work (deferred from §1.6)

- Scale to 200-entry corpus + re-validate findings (S1–S13 should
  hold at larger sample; statistical power claims become defensible).
- Implement 60-entry-legacy-reference field semantics OR formal
  restriction to 4×1 schema (PENDING_V2_5_SCHEMA_REVISION
  resolution).
- Layer 5 false-positive rate tracking at scale (does S13 hold at
  200, or do new paraphrase signatures emerge?).

### §12.4 — Phase 1.G — Adaptive attacker

Reviewer-mandatory sub-project per Phase 1.F audit feedback.
Independent of E1.5 / E1.6; can begin once Phase 1.E closes.

### §12.5 — Paper rewrite

§V (Methodology) + §VI (Reproducibility) + §VII (Limitations + Future Work) integration. All 11 findings + 2 PENDING decisions need paper placement.

---

*End of `PHASE_1E_E1_4_RESULTS.md`. E1.4 sub-phase PASS; 23
outliers dispositioned with 0 drops; S13 finding documented;
sequencing + scale decisions explicit. Standing by for user
manual commit + E1.5 manual spot-check kickoff.*
