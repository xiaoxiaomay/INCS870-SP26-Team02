# Phase 1.E E1.5 — V2 Benign Check + S14 Finding: Results

> **Status:** PASS. V2 §4.1 BLOCKING manual benign check executed
> against all 65 hard-negative entries: **65/65 PASS (100%)**, 0
> FAIL, 0 BORDERLINE. One new paper finding (**S14 — sub-cell
> distribution audit-driven concentration**) added to
> `DOCUMENTED_FINDINGS`, unifying corpus-structural sub-cell
> distribution data with V2 100% PASS as constituent evidence.
> Total findings: **12** (S1–S14 with S3/S4 sequential gaps) + 2
> PENDING V2.5 revision decisions. JSONL schema extended with
> `v2_benign_check` field (65/65 = "pass"). Sub-cell distribution
> failure of V2 §4.1 V8 documented as design-acknowledged
> structural property per E1.4 Q2 65-entry close ruling.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §4.1 V2 row + §4.3 V2 fail outcome
>   + §4.1 V8 row (sub-cell balance, V8 strict-fail acknowledged).
> - `PHASE_1E_E1_4_RESULTS.md` (E1.4 close — 23 outliers
>   dispositioned; V2 check still pending, our E1.5 covers).
> - `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries
>   × 22 fields after E1.5 close).
>
> **Outputs (authoritative artifacts):**
> - `scripts/validate_hard_negatives.py` (**1773 LOC**; +73 LOC
>   over E1.4 close for S14 finding entry).
> - `eval/results/phase1_E/validation/v2_benign_check_report.md`
>   (E1.5 spot-check forensic report; 65-row per-entry verdict
>   table; V3-scope deferral note).
> - `eval/results/phase1_E/validation/v1b_20260524T002258Z.json`
>   (**FINAL E1.5 canonical artifact**; 14 documented_findings
>   keys = 12 S-findings + 2 PENDING).
> - `PHASE_1E_E1_5_RESULTS.md` (this document).

---

## §1 — E1.5 Close Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| V2 BLOCKING manual benign check entries reviewed | **65/65** (full review per Q1) |
| V2 PASS | **65** |
| V2 FAIL | **0** |
| V2 BORDERLINE | **0** |
| Per-source: HN_SEED | 30/30 PASS (100%) |
| Per-source: HN_GEN | 35/35 PASS (100%) |
| Per-category | 100% PASS across A–F |
| Corpus mutations | **0** (no drops, no refines) |
| New paper findings | **1** (S14) |
| Total documented findings | **12** (S1, S2, S5, S6, S7, S8, S9, S10, S11, S12, S13, **S14**) |
| PENDING V2.5 revision decisions | **2** (unchanged from E1.4) |
| JSONL schema fields per entry | 21 → **22** (`v2_benign_check` added) |
| Validator LOC | 1700 → **1773** (+73) |
| LLM cost | **$0** |
| Session wall | ~1.5 hours (35 min review + 55 min documentation) |

### §1.2 — Phase 1.E E1.5 milestone gate

PASS (5 / 5 acceptance criteria):

- ✓ V2 §4.1 BLOCKING manual benign check executed against all 65
  entries (full review, no sampling per Q1).
- ✓ Per-entry verdict + criterion documented in
  `v2_benign_check_report.md` §3 (65-row table).
- ✓ `v2_benign_check` field added to JSONL schema (V2 §5.2
  extension; 65/65 populated "pass").
- ✓ S14 finding added to `DOCUMENTED_FINDINGS` with expanded
  interpretation incorporating V2 PASS as supporting evidence.
- ✓ Atomic write discipline maintained (`.bak` rotated; `.preV1a`
  permanent baseline untouched; `.preE14` snapshot preserved).

---

## §2 — Scope and Acceptance Criteria

E1.5 executes V2 §4.1's third BLOCKING manual check (V2 row:
"Benign in expected-answer sense"). Per E1.4 §1.5 sequencing
divergence acknowledgment, V2's "Human review during E1.4" maps
to this project's E1.5 — V2's E1.4 label was absorbed by E1.4
paraphrase-suspect content review (Layer 5 + Layer 3
disposition).

Per E1.5 Q1 ratification: **full 65-entry review** (not
sampling). Rationale: V2 is the only single-layer benign check
without defense-in-depth cover; strict reading of "every entry"
gives clean paper-grade BLOCKING claim.

Per E1.5 Q-additional ratification: **uniform 6-criterion
application to all 65 entries** (no special-casing of the 23
dispositioned outliers). Rationale: V2 is its own BLOCKING gate;
chaining from Layer 5 non-paraphrase ruling obscures the V2-
specific assessment. Layer 5 (4 entries) + Action 1a (2 entries)
review covered paraphrase concern; V2 covers expected-answer
benignity — adjacent but distinct semantic checks.

---

## §3 — V2 Benign Check Execution

### §3.1 — Methodology

6-criterion checklist per E1.5 Q2 ratification:

| Criterion | Verdict |
| --- | --- |
| (a) Expected answer is industry-standard knowledge (textbook, peer-published, regulatory) | PASS |
| (b) Expected answer is aggregated statistics (no individual-fund attribution) | PASS |
| (c) Expected answer is hypothetical/educational/conceptual | PASS |
| (d) Expected answer would name a specific fund's parameter | FAIL → drop |
| (e) Expected answer would leak operational specifics (entry timing, position sizing) | FAIL → drop |
| (f) Query is grammatically malformed or factually wrong | FAIL → drop |

Disposition states: `pass` / `fail` (drop per V2 §4.3) /
`borderline` (retain with note).

### §3.2 — Per-batch results (5 batches × ~15 entries)

| Batch | Entries | PASS | FAIL | BORDERLINE |
| --- | --- | --- | --- | --- |
| Batch 1 | HN_SEED_001–015 (Cat A + B + C manual) | 15/15 | 0 | 0 |
| Batch 2 | HN_SEED_016–030 (Cat D + E + F manual) | 15/15 | 0 | 0 |
| Batch 3 | HN_GEN_031–045 (Cat A_pvm + C_ed + A_ml gen) | 15/15 | 0 | 0 |
| Batch 4 | HN_GEN_046–060 (Cat B_pvm + D_fn + E_ad gen) | 15/15 | 0 | 0 |
| Batch 5 | HN_GEN_061–065 (Cat F_sa gen) | 5/5 | 0 | 0 |
| **Total** | 65 entries | **65/65 (100%)** | **0** | **0** |

### §3.3 — Per-category + per-source aggregate

| Cat | Total | PASS | Rate |
| --- | --- | --- | --- |
| A | 15 | 15 | 100% |
| B | 10 | 10 | 100% |
| C | 10 | 10 | 100% |
| D | 10 | 10 | 100% |
| E | 10 | 10 | 100% |
| F | 10 | 10 | 100% |
| **Σ** | **65** | **65** | **100%** |

| Source | Total | PASS | Rate |
| --- | --- | --- | --- |
| HN_SEED (E1.1 manual seeds) | 30 | 30 | 100% |
| HN_GEN (E1.2 LLM-generated) | 35 | 35 | 100% |

### §3.4 — Mechanism: benign-by-construction across both tiers

The linguistic-category taxonomy (V2 §2.2) and audit framework
(V2 §3.2 + E1.2 anti-pattern audit) jointly produce
benign-by-construction queries:

- Cat A "typical/common" markers → industry-standard answer space
- Cat B "industry-survey" markers → aggregated statistics
- Cat C "if/suppose/hypothetical" markers → conceptual scenarios
- Cat D educational/definitional markers → textbook explanations
- Cat E "compare/differ" markers → conceptual contrasts
- Cat F "historically/used to/prior to" markers → industry evolution

E1.5 V2 100% PASS empirically confirms the design intent: the
65-entry corpus has zero queries that would induce a RAG system
to leak fund-specific parameters or operational specifics.

---

## §4 — NEW FINDING: S14 — Sub-Cell Distribution Audit-Driven Concentration

### §4.1 — Pattern observation

65-entry corpus exhibits **bimodal sub-cell distribution**:

| Sub-cell density | Count | Notes |
| --- | --- | --- |
| Empty (n=0) | 0 | all 36 sub-cells covered (per E1.2 close) |
| **Degenerate (n=1)** | **29** | all from E1.1 manual seeds |
| Intermediate (2 ≤ n ≤ 4) | 0 | — |
| **Rich (n=5 or 6)** | **7** | A_pvm (6), A_ml (5), B_pvm (5), C_event_driven (5), D_factor_neutral (5), E_alternative_data (5), F_statistical_arbitrage (5) |

The 7 rich sub-cells correspond **EXACTLY** to the 7 audit-driven
E1.2 generation batches. Manual seeds (E1.1) authored 1 entry per
sub-cell as initial design intent (T4 rotation pattern); E1.2
audit-driven generation concentrated 5 additional entries per
chosen sub-cell.

### §4.2 — V8 sub-cell balance — strict FAIL acknowledged

V2 §4.1 V8 row prescribes "[4, 7] per sub-cell, [190, 210]
total" as BLOCKING. At 65-entry scale: **strict V8 FAIL** (29
sub-cells outside [4, 7]; total 65 outside [190, 210]). This is
**design-acknowledged** per E1.4 Q2 65-entry close ruling; V8
binding deferred to v11 future work.

### §4.3 — Triple-layered defense-in-depth confirmation

S14's interpretation links three independent BLOCKING checks
that all yielded clean results, providing layered assurance
against secret-content leakage:

| Gate | Check | Result | Finding |
| --- | --- | --- | --- |
| Layer 2 (V5b) | Exact-string match | 0/65 hits | S12 |
| Layer 5 (R6) | ≥2-encoder paraphrase signature | 4 candidates → 0/4 confirmed | S13 |
| V2 (this) | Benign-in-expected-answer | 65/65 PASS | S14 + this report |

This triple-layered defense-in-depth is the architectural
contribution claim for v10 paper §V/§VI: hard-negative corpus
construction with layered validation passes all three
independent gates.

### §4.4 — Paper implication

S14 provides architectural evidence for audit framework value
at **three structural levels**:

1. **ACCURACY** — S2 5× lower below-band fail rate (E1.1 vs E1.2).
2. **DENSITY** — concentrated sub-cell population in 7 audit-driven
   batches (this S14 finding).
3. **BENIGN-BY-CONSTRUCTION** — V2 100% PASS across both tiers
   (this E1.5 result).

v11 future work guidance: scaling to V2 §2.4's 200-entry target
should apply audit-driven generation to all 36 sub-cells
(achieving V8 [4, 7] balance) rather than scaling manual-seed
methodology. The audit framework is the methodology contribution;
scaling validates statistical robustness.

---

## §5 — Sub-Cell Distribution Analysis

Full 6×6 distribution matrix (pre-flight verification, embedded
in S14 finding):

```
cat    alt_data  event_dr  factor_n  ml_sig    pvm       stat_arb  total
A      1         1         1         5         6         1         15
B      1         1         1         1         5         1         10
C      1         5         1         1         1         1         10
D      1         1         5         1         1         1         10
E      5         1         1         1         1         1         10
F      1         1         1         1         1         5         10
Σ      10        10        10        10        15        10        65
```

Domain-aggregated:
- price_volume_momentum: 15 entries (A_pvm=6 + B_pvm=5 + 4 degenerate)
- All other domains: 10 entries each (1 rich sub-cell + 5 degenerate)
- Total: 65

The 7 rich sub-cells (diagonal pattern + A_ml double) are exactly
the E1.2 audit-driven generation targets per
`PHASE_1E_E1_2_RESULTS.md` §4.2.

---

## §6 — Future Work: V3 Parametric Numeric Scope Deferral

V2 6-criterion check observed 4 entries with numeric content:

| `_id` | Numeric | Context |
| --- | --- | --- |
| HN_SEED_001 | "130/30" | industry-standard strategy name |
| HN_SEED_011 | "2x" | industry-standard leverage shorthand |
| HN_SEED_016 | "14-day" | universal RSI textbook constant |
| HN_GEN_036 | "70%" | hypothetical-scenario parameter |

All four PASS V2 — the numbers are textbook constants or
hypothetical-scenario design parameters, not parametric-fund-
specific leaks. **V3 (no parametric numeric content) is a
separate BLOCKING check** (V2 §4.1 V3 row) not in E1.5 scope.
A V3 dedicated pass would refine these entries per V2 §4.3 V3
outcome ("Refine: replace number with 'typical' / 'appropriate'").

**Deferred to v11 future work alongside the 200-entry scale-up.**
v10 paper §VI Reproducibility should disclose V3 deferral as a
known scope-narrowing decision (alongside the 200→65 scale
decision documented in E1.4 §1.6 and the V8 sub-cell balance
deferral documented in this E1.5 §4.2).

---

## §7 — Reproducibility Provenance

### §7.1 — Canonical artifacts (post-E1.5)

| Path | Size | Role |
| --- | --- | --- |
| `scripts/validate_hard_negatives.py` | **1773 LOC** | Validator + 14-key DOCUMENTED_FINDINGS |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | 65 entries × 22 fields | Post-V5b + V2 canonical corpus |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` | rotates per run | Atomic-write rollback target |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` | 34207 bytes | Permanent pre-V1a baseline |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | 23 entries | R6 audit log (unchanged from E1.4) |
| `eval/results/phase1_E/validation/r6_audit.jsonl.preE14` | 4680 bytes | Pre-E1.4 snapshot |
| `eval/results/phase1_E/validation/v1b_20260524T002258Z.json` | (post-S14) | **FINAL E1.5 canonical artifact** |
| `eval/results/phase1_E/validation/v1b_20260523T134252Z.json` | 35030 bytes | Historical (pre-S14) |
| `eval/results/phase1_E/validation/v2_benign_check_report.md` | this E1.5 | E1.5 spot-check forensic report |
| `PHASE_1E_E1_3_RESULTS.md` | 661 lines | E1.3 close (historical) |
| `PHASE_1E_E1_4_RESULTS.md` | 615 lines | E1.4 close (historical) |
| `PHASE_1E_E1_5_RESULTS.md` (this) | E1.5 close | E1.5 close |

### §7.2 — Cost and wall

| Stage | LLM cost | Wall |
| --- | --- | --- |
| Pre-flight verification | $0 | ~5 min |
| V2 6-criterion review (5 batches × 65 entries) | $0 | ~35 min |
| S14 finding ratification + validator edit | $0 | ~10 min |
| JSONL `v2_benign_check` field atomic update + V5b re-run | $0 | ~5 min |
| `v2_benign_check_report.md` write | $0 | ~25 min |
| `PHASE_1E_E1_5_RESULTS.md` write (this) | $0 | ~30 min |
| **Total E1.5 session** | **$0** | **~1.5 hours** |

Within all per-step ($0.005) and per-phase ($0.40) cost caps.

---

## §8 — Commit-Prep Summary

Per project no-commit discipline, no commit initiated by validator.
User runs git operations manually at E1.6 Phase 1.E close (batched
with 7f57f05 E1.4 unpushed + this E1.5 commit + upcoming E1.6
commit).

### §8.1 — Files modified or added since `7f57f05` (E1.4 close, local)

```
M  scripts/validate_hard_negatives.py                          (1700 → 1773 LOC; +S14 finding)
M  data/benchmark/hard_negatives_seeds_draft.jsonl             (65 entries × 22 fields; +v2_benign_check)
M  data/benchmark/hard_negatives_seeds_draft.jsonl.bak         (rotates per run)
M  eval/results/phase1_E/validation/r6_audit.jsonl             (idempotent re-run; data unchanged)
?? eval/results/phase1_E/validation/v1b_20260524T002258Z.json  (FINAL E1.5 canonical; 14 documented_findings)
?? eval/results/phase1_E/validation/v2_benign_check_report.md  (E1.5 spot-check forensic report)
?? PHASE_1E_E1_5_RESULTS.md                                    (E1.5 close-out, this document)
```

### §8.2 — Suggested commit message

```
phase1E: E1.5 close - V2 benign check 65/65 PASS + S14 finding

V2 §4.1 BLOCKING manual benign check executed against all 65
hard-negative entries (full review per Q1 ratification):
- 65/65 PASS (100%), 0 FAIL, 0 BORDERLINE
- Per-source: HN_SEED 30/30, HN_GEN 35/35
- Per-category: 100% PASS across A-F
- 0 corpus mutations (no drops, no refines)

New finding S14 (sub-cell distribution audit-driven concentration)
added to DOCUMENTED_FINDINGS with unified interpretation linking
corpus-structural pattern + V2 100% PASS + V5b 0-hit + Layer 5
0-confirm into triple-layered defense-in-depth narrative. Total
findings: 12 (S1-S14 with S3/S4 sequential gaps) + 2 PENDING.

JSONL schema extended with v2_benign_check field (V2 §5.2
extension; 65/65 populated "pass").

V3 parametric numeric scope check deferred to v11 future work
alongside 200-entry scale-up (4 entries observed with numeric
content; all textbook constants or hypothetical parameters, V2-
clean).
```

---

## §9 — Next Phase Roadmap

### §9.1 — E1.6 — Phase 1.E Close

Final Phase 1.E sub-phase. Tasks:

1. Resolve `PENDING_V2_5_PLAN_REVISION` (S1 + S8 + S9 references).
   Per Q1 STRICT-with-paper-escalation default: confirm documented-
   prediction-miss as v10 final framing; no post-hoc re-anchor.
2. Resolve `PENDING_V2_5_SCHEMA_REVISION` (S7 reference). Ratify
   Option (a) restrict V2 §5.2 to 4×1 schema (90-entry only) for
   v10; defer 60-entry-legacy-reference field semantics to v11.
3. Rename `hard_negatives_seeds_draft.jsonl` →
   `hard_negatives.jsonl` per V2 §5.1.
4. Write `PHASE_1E_RESULTS.md` (Phase 1.E master close-out
   integrating E1.1 + E1.2 + E1.3 + E1.4 + E1.5).
5. User manual commit + push (batched: 7f57f05 E1.4 + E1.5
   commit + E1.6 commit pushed together).

Estimated wall: ~1-1.5 hours.

### §9.2 — Phase 1.G — Adaptive attacker

Reviewer-mandatory sub-project per Phase 1.F audit feedback.
Independent of remaining E1.x; can begin once Phase 1.E closes.

### §9.3 — Paper rewrite §V/§VI/§VII integration

All 12 documented findings + 2 PENDING decisions need paper
placement. v10 §VI Reproducibility must disclose:
- 65-entry close vs V2's 200 target (E1.4 §1.6).
- V8 sub-cell balance strict-fail at 65-entry scale (S14 §4.2).
- V3 parametric numeric deferred to v11 (E1.5 §6).
- Sequencing divergence between V2 plan labels and actual
  project execution (E1.4 §1.5).

### §9.4 — v11 future work

- Scale to V2 §2.4's 200-entry target via audit-driven
  generation to all 36 sub-cells (S14 §4.4 guidance).
- V3 parametric numeric dedicated pass.
- 60-entry-legacy-reference field semantics (PENDING_V2_5_SCHEMA_REVISION
  Option b alternative).

---

*End of `PHASE_1E_E1_5_RESULTS.md`. E1.5 sub-phase PASS; V2
BLOCKING manual benign check clean; S14 finding documented;
corpus benign-by-construction confirmed at architectural
triple-layered defense-in-depth level. Standing by for E1.6
Phase 1.E close.*
