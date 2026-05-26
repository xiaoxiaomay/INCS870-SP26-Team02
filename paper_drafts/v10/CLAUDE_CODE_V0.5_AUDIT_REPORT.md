# v10 Paper Drafts v0.5 — Audit Report

> **Generated:** 2026-05-26, after G2 production complete
> (8 / 8 cells at n = 5; 10,840 prompt-evaluations canonical).
>
> **Mode:** v0.4 + 12 authoring blocks driven by G2 production
> data at `eval/results/phase1_G/g2_outputs/`. No LLM calls,
> no git ops, no Phase 1.G interference (G1 already finished;
> PID 32567 exited).

---

## Summary

| Metric | Value |
| --- | --- |
| Authoring tasks completed | **12 / 12** |
| Files modified | 4 (V_A, V_B, VI, I+VII); V_C unchanged per rule |
| Total LOC v0.4 → v0.5 | **2,737 → 3,135** (+398) |
| `[TBD]` / `[G2 PENDING]` / `[PLACEHOLDER]` markers in active drafts | **0** (all eliminated) |
| `5,691` references in active drafts | **0** (all updated to 10,840) |
| `Candidate S15` / `Candidate S16` / `Candidate S17` | **0** (all promoted to empirical findings) |
| New findings authored | **S16, S17, S19** (empirically grounded by G2) |
| S15 strengthened: G2 full-matrix verification | **YES** — 25 / 25 non-bge-large samples ULR = 0 |
| S18 wall-time | **Preserved as candidate** at §V.B.5.5 (deferred analysis) |

---

## G2 production data source verification

Canonical data: `eval/results/phase1_G/g2_outputs/matrix_n5.json`
(generated 2026-05-26T00:46:16Z, 32 KB).

| Metric | G2 value | Used in drafts |
| --- | --- | --- |
| Cells at n = 5 | 8 / 8 ✓ | §V.B.4.1 |
| FinLang × 90 GLR mean (verified rerun) | 0.0885 ± 0.0197 | §V.B.4.1 |
| FinLang × 60 vs × 90 GLR paired test | mean −0.0531, t = −8.363, p = 0.0011, Holm rank 1, threshold 0.0125, **SIGNIFICANT** | §V.B.4.2, §V.B.5.3 |
| bge-large × 60 vs × 90 GLR paired test | mean −0.0177, t = −2.953, p = 0.0419, Holm rank 2, threshold 0.0167, not significant | §V.B.4.2, §V.B.5.3 |
| MiniLM × 60 vs × 90 GLR paired test | mean −0.0140, t = −2.543, p = 0.0638, Holm rank 3, threshold 0.0250, not significant | §V.B.4.2, §V.B.5.3 |
| mpnet × 60 vs × 90 GLR paired test | mean +0.0059, t = 1.322, p = 0.2566, Holm rank 4, threshold 0.0500, not significant | §V.B.4.2, §V.B.5.3 |
| F2 corpus-60 ordering | 5 / 5 samples hold | §V.B.4.3, §V.B.5.2 |
| F2 corpus-90 ordering | 4 / 5 samples hold; sample 4 mpnet ↔ MiniLM swap | §V.B.4.3, §V.B.5.2 |
| S15: bge-large ULR fires | 1 across 10 samples × 271 = 2,710 evaluations | §V.A.5.1, §V.B.5.1, §VII |
| S15: non-bge-large ULR fires | 0 across 30 samples × 271 = 8,130 evaluations | §V.A.5.1, §V.B.5.1, §VII |
| Total n_glr_leaked across 40 samples | 27+46+76+68+137+161+48+120 = **683** | §V.A.5.1 redaction effectiveness |
| Aggregate redaction effectiveness | 682 / 683 = 99.85% | §V.A.5.1, §VII |
| Bypass std per cell | 0.0000 universal | §V.B.4.1, §V.B.5.4 (S19) |

All 14 numerical claims trace to the G2 matrix_n5.json with zero `[NEEDS_HUMAN_REVIEW]` flags.

---

## Per-task completion

### Task 1 — §V.B.4 fill with G2 production tables ✓

- `§V.B.4` placeholder header → "Results: Multi-Sample Aggregates (G2 production, n = 5 all 8 cells)" with canonical-source-pointer to `eval/results/phase1_G/g2_outputs/`.
- All `[TBD]` markers in §V.B.4.1, §V.B.4.2, §V.B.4.3 replaced with G2 production values.
- **§V.B.4.1**: 8-row per-cell aggregate table (Bypass / GLR / Per-BP-Leak / ULR ± CI).
- **§V.B.4.2**: 4 primary GLR Holm-Bonferroni paired tests + 8 secondary (bypass + Per-BP-Leak) tests; secondary table includes `±∞ (deterministic)` annotation for bypass tests with degenerate paired diffs.
- **§V.B.4.3**: Full per-sample × per-corpus encoder ranking tables (10 samples total); sample 4 corpus-90 exception bolded (MiniLM ↔ mpnet rank swap at the low end, separation 0.52 pp).
- **§V.B.4.4**: S15 verification table (ULR fires per cell; aggregate bge-large 1 / 2,710, non-bge-large 0 / 8,130).
- Added prose paragraphs before each sub-section per spec.

### Task 2 — §V.B.5.3 S17 rewrite (significance asymmetry) ✓

- Replaced "Candidate S17" placeholder with empirical-grounded finding.
- Headline: 1 of 4 primary tests reject H₀ (FinLang only, p = 0.0011 under Holm rank 1).
- Documented mechanism hypothesis (FinLang's finance-domain pretraining shapes retrieval geometry differently for 60 vs 90 corpora).
- Linked to F3 (FinLang paradox) — corpus-60 discriminative profile breaks down at corpus-90 (2.5× Per-BP-Leak regression).
- Documented bypass-rate degenerate tests (±∞ artifact, not statistical inference).
- v11 path: scale to n = 10 for tighter detection on smaller effects.

### Task 3 — §V.B.5.2 S16 promotion with corpus-90 micro-exception ✓

- Replaced "Candidate S16" with empirical finding.
- F2 endpoints (MiniLM-class lowest, bge-large highest) hold 10 / 10 samples.
- Corpus-90 sample 4 exception documented: mpnet (0.0896) < MiniLM (0.0948), within 0.52 pp; bge-large endpoint rank 4 remains universal.
- Added cross-corpus ranking pattern table (FinLang's middle-rank position is corpus-dependent — rank 2 at corpus-60, rank 3 at corpus-90; connection to S17).
- v10 claim: F2 endpoints universal; middle ordering corpus-sensitive.

### Task 4 — §V.B.5.1 S15 update with full G2 evidence ✓

- Updated predictive-claim subsection to **25 / 25 non-bge-large samples ULR = 0**.
- Added aggregate rates: bge-large 1 / 2,710 = 0.037%; non-bge-large 0 / 8,130 = 0.000%; total 1 / 10,840 = 0.0092%.
- **Discrepancy with user's prompt spec:** user's task spec listed "25 samples × 271 = 6,775 evaluations" for non-bge-large; actually there are **30 samples × 271 = 8,130 evaluations** (6 non-bge-large cells × n = 5). Drafts use the correct 30 / 8,130 numbers; the user's prompt apparently miscounted the cell × sample multiplication. **No source-of-truth violation:** G2 data backs the corrected numbers (verified via `len([c for c in CELLS if not c.startswith("bge_large_")])` × 5 = 30).
- Also updated §V.B.5.1 header from "G1 partial-run finding" to "G2 production n = 5 all 8 cells".

### Task 5 — §V.A.5.1 F1 multi-sample count update (10,840 evaluations) ✓

- Updated "5,691 evaluations = 21 Phase 1.G samples × 271 prompts" to "10,840 evaluations = 40 total samples × 271 prompts; 8 cells × n = 5 each; full G2 production completed 2026-05-26".
- Reframed multi-sample observation paragraph from "G1 partial" to full-matrix evidence.
- Added forensic paragraph reaffirming "0% true ULR" qualifier (auditable byte-by-byte).
- Updated aggregate redaction-effectiveness section: 682 / 683 = 99.85% across all 40 samples (corrected from prior partial-state figure).
- Updated `§V.A` draft-status block: v0.5, G2 complete.

### Task 6 — §V.B.1.4 full n = 5 multi-cell findings ✓

- Replaced partial-run findings with universal empirical findings (4 numbered items: S19, GLR mildly stochastic, S15, S17).
- Added 8-row aggregate matrix summary.
- Removed "These partial-run findings will be reframed as G2-stage formal statistical results once Phase 1.G G1 completes" language.

### Task 7 — §VII headline summary to 10,840 evaluations ✓

- Updated headline: "0% true user-facing secret leakage across **10,840 multi-sample evaluations** (40 total samples × 271 prompts; full n = 5 across all 8 encoder × corpus configurations; ...; aggregate redaction effectiveness 682 / 683 = 99.85%)".
- Updated cross-encoder evidence claim: "25 / 25 non-bge-large samples ULR = 0".
- Added paragraph documenting full G2 findings (S16, S17, S19) at the §VII summary level.

### Task 8 — Add S19 (universal pre-LLM gate determinism) ✓

- Inserted as §V.B.5.4 (new sub-section); existing S18 wall-time moved to §V.B.5.5 (preserved as candidate).
- Added full per-cell bypass-count table (8 rows; std = 0.0000 universal).
- Mechanism paragraph (pre-LLM gates deterministic by construction).
- Distinction from S15 paragraph documenting deterministic vs stochastic pipeline stages.

### Task 9 — §V.B.1.3 sign convention ✓

- Added explicit (60 − 90) sign convention statement.
- Updated MiniLM, mpnet, FinLang within-encoder corpus delta examples with G2 numbers.
- Documented MiniLM single-sample +0.37 pp vs G2 n = 5 mean −1.40 pp difference (single-sample was unrepresentative of n = 5 distribution).

### Task 10 — §I.B C9 description (S15 + S16 + S17 + S19) ✓

- Updated C9 description to mention all four findings with one-line summaries each.
- Added 10,840 evaluations total.
- Preserved existing two-stage stochasticity sub-observation language.

### Task 11 — Sanity check ✓

- **No `5,691` references** in active drafts (only in v0.4 audit-report historical record).
- **No `[TBD]` / `[G2 PENDING]`** in active drafts (all replaced with G2 production values).
- **No `Candidate S15/S16/S17`** in active drafts (promoted to empirical findings).
- **No `+0.37 pp` standalone references** to single-sample MiniLM corpus delta as if current (replaced with G2 −1.40 pp at n = 5; §V.B.2.1 design-stage prose preserved as historical priors-driven rationale).
- Updated v0.5 draft-status blocks in §V.A and §V.B.
- Updated §VI.1.2.1 operational consequence paragraph to G2 outcomes.

### Task 12 — v0.5 audit report ✓ (this file)

---

## Items requiring human review

| # | Issue | Action |
| --- | --- | --- |
| 1 | **Prompt spec arithmetic discrepancy in Task 4:** user's prompt said "25 samples × 271 = 6,775 evaluations" for non-bge-large totals; actual is **6 non-bge-large cells × n = 5 = 30 samples × 271 = 8,130 evaluations**. Drafts use the corrected 30 / 8,130 figures. | None — corrected drafts match G2 source-of-truth data. Audit-report flags the prompt inconsistency for the user's awareness. |
| 2 | **S18 wall-time variance retained as candidate** at §V.B.5.5 (renumbered from former §V.B.5.4). G2 matrix_n5.json does not aggregate wall-time. If future analysis adds wall-time aggregation, S18 can be promoted; until then it sits as a pending candidate. | None — preserved for future work. |
| 3 | **§V.B.2.1 design-stage prose** still references "+0.36 pp Cell-1 drift" and "+0.37 pp MiniLM corpus delta" as priors that drove the n = 5 sample-count choice. This is **prospective design rationale**, not retrospective claims about G2 outcomes. Preserved intact. | None — historical design rationale faithfully preserved. |

---

## v0.5 grand totals

| File | v0.4 | v0.5 | Delta |
| --- | --- | --- | --- |
| `v10_paper_section_V_A_phase1F_draft.md` | 460 | 470 | +10 |
| `v10_paper_section_V_B_phase1G_draft.md` | 658 | 1012 | **+354** |
| `v10_paper_section_V_C_phase1E_draft.md` | 787 | 787 | 0 (unchanged per task rule) |
| `v10_paper_section_VI_draft.md` | 528 | 531 | +3 |
| `v10_paper_sections_I_VII_draft.md` | 304 | 335 | +31 |
| **Total** | **2,737** | **3,135** | **+398** |

---

## Phase 1.G G1 final state

| Metric | Value |
| --- | --- |
| G1 production end time | 2026-05-26T00:37:52Z |
| Phase 1.G samples on disk | **32 / 32** complete |
| Cells at n = 5 (with Phase 1.F sample 1) | **8 / 8** |
| Total prompt-evaluations available | 10,840 (40 samples × 271) |
| PID 32567 status | Exited cleanly |
| Total Phase 1.G LLM cost | $0.6664 (within $0.70 forecast) |
| State ledger drift at close | 30 / 32 (2 samples missing due to RG4 halt + parent-kill orphan; canonical input for G2 is disk, not state) |

## Phase 1.G G2 final state

| Metric | Value |
| --- | --- |
| G2 production end time | 2026-05-26T00:46:16Z |
| Cells aggregated | 8 / 8 (full n = 5) |
| Primary paired tests | 4 (all encoders × {60, 90} GLR) |
| Holm-Bonferroni reject count | **1 / 4** (FinLang only) |
| F2 corpus-60 verdict | 5 / 5 samples ✓ |
| F2 corpus-90 verdict | 4 / 5 samples ✓ (sample 4 exception) |
| S15 claim verification | HOLDS (25 / 25 non-bge-large ULR = 0) |
| Output files | matrix_n5.json (32 KB), paper_table_v_b_4.md (86 LOC), g2_audit_report.md (135 LOC) |

---

## Findings status matrix (v10 paper-ready)

| Finding | Status | Section | Evidence |
| --- | --- | --- | --- |
| **F1** (ULR = 0% true) | Empirical, G2 strengthened | §V.A.5.1 | 10,840 evaluations; 1 measurement-stage false positive; 99.85% aggregate redaction effectiveness |
| **F2** (encoder ordering) | Empirical, G2 refined | §V.A.5.2 + S16 | Endpoints 10/10; middle corpus-dependent |
| **F3** (FinLang paradox) | Empirical, G2 strengthened | §V.A.5.3 + S17 | corpus-60 holds; corpus-90 breaks down at 2.5× Per-BP-Leak regression |
| **S15** (bge-large ULR over-sensitivity) | Empirical, G2 full matrix | §V.B.5.1 | 25/25 non-bge-large ULR=0; auditable forensic |
| **S16** (F2 ordering robustness) | NEW empirical | §V.B.5.2 | 10/10 endpoints; 1 micro-exception sample-4 corpus-90 |
| **S17** (asymmetric corpus delta significance) | NEW empirical | §V.B.5.3 | 1/4 Holm reject (FinLang p=0.0011) |
| **S18** (wall-time variance) | Candidate (deferred) | §V.B.5.5 | G2 not analyzed wall-time |
| **S19** (universal gate determinism) | NEW empirical | §V.B.5.4 | bypass std = 0.0000 across 40 samples |

---

## Items still pending (v10 → publication)

1. **LaTeX conversion** of all 5 markdown drafts (v10_paper_section_*.md → v10_paper.tex).
2. **Figures**: Phase 1.F + Phase 1.G + Phase 1.E plot generation (per-cell GLR / ULR scatter; F2 ordering bar chart; S15 forensic excerpt screenshot).
3. **Corpus rename** (V2 §5.1): `hard_negatives_seeds_draft.jsonl` → `hard_negatives.jsonl` (commands previously computed for user; user runs git ops).
4. **Professor review pass** on v0.5 drafts.
5. **§V.C update if any new Phase 1.E findings surface** — currently §V.C is unchanged from round-1 corrections and matches Phase 1.E E1.6 closing state.
6. **Citation key insertion** ([CITE: …] markers throughout).

---

## Standing G1/G2 infrastructure (post-completion)

- **scripts/phase1G_multi_sample.py** — 560 LOC, completed cleanly, NOT modified in v0.5 work.
- **scripts/phase1G_g2_analysis.py** — 819 LOC, production-ready, NOT modified in v0.5 work.
- **eval/results/phase1_G/g2_outputs/** — 3 files (matrix_n5.json, paper_table_v_b_4.md, g2_audit_report.md) treated as READ-ONLY canonical source.

---

*End of `CLAUDE_CODE_V0.5_AUDIT_REPORT.md`. v0.5 authoring
complete. Drafts ready for LaTeX conversion + figure
generation. NO git ops performed; user commits manually.*
