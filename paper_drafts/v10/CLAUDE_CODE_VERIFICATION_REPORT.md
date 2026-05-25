# v10 Paper Drafts — Claude Code Verification Report

> **Generated:** 2026-05-25 (verification run during Phase 1.G G1
> background execution; 17 / 32 samples complete as of report
> generation — Phase 1.G G1 NOT interfered with).
>
> **Scope:** Verification audit of 5 markdown drafts in
> `paper_drafts/v10/` against the actual project codebase,
> Phase 1.E/F canonical RESULTS docs, validator outputs, v9
> paper text, and committed git revisions.
>
> **Method:** Read-only verification on codebase; targeted
> in-place edits applied to drafts where claims diverge from
> reality. No git operations. No LLM calls. No modifications
> to project code or Phase 1.G running process.

---

## Summary

| Metric | Value |
| --- | --- |
| Total verification tasks | 16 |
| `[CLAUDE_CODE_VERIFY]` markers resolved | **9 / 9** |
| Numerical claims verified | 51+ (8 cells × 8 cols + 4 encoder pins + ~20 finding numbers + commit refs + LOCs) |
| Critical discrepancies found | **4** (M3 60-disjoint, M6 consensus rate, M7 D/E ratio, FinLang model name) |
| Minor cosmetic discrepancies | **3** (C1/C2 title shortening, §V.C.6.14 cross-ref, repro_full_pipeline LOC rounding) |
| File path issues | **1** (`hard_negatives.jsonl` referenced; actual file is `hard_negatives_seeds_draft.jsonl` — rename deferred) |
| Updates applied to drafts | **11 in-place edits** (§V.A: 1; §V.C: 8; §VI: 1; §I/§VII: 1) |
| `[NEEDS_HUMAN_REVIEW]` items | **2** (corpus rename status; Bonferroni vs Holm-Bonferroni statistical-test choice) |

**Bottom line:** all 9 markers resolved with verified numerical values; 4 critical numerical errors corrected in §V.C; 1 wrong encoder model name corrected in §V.A; 1 sub-section cross-reference fixed in §VI; 1 v9 contribution-title alignment fixed in §I.

---

## Task-by-Task Results

### Task 1 — `[CLAUDE_CODE_VERIFY]` Markers (9 / 9 resolved)

| # | Location | Claim | Resolution | Status |
| --- | --- | --- | --- | --- |
| M1a | §V.C.3.2 line 265 (V5b N value) | N = ? | Verified V5b checks BOTH `secrets_v2.jsonl` (90) + `secrets.jsonl` (60) = **150 secrets**; multiplier 65 × 150 × 2 = 19,500 | PASS — updated |
| M1b | §V.C.6.10 line 553 (V5b N second occurrence) | N = ? + "~19,500" arithmetic | Same as M1a: 150 secrets, 19,500 comparisons | PASS — updated |
| M2a | §V.C.4 line 281 (validator LOC) | "~1800 LOC" | Verified `wc -l scripts/validate_hard_negatives.py = 1832` | PASS — updated to "1832 LOC" |
| M2b | §V.C.7 line 661 (validator LOC second occurrence) | LOC + CLI | Same: 1832 LOC; 4-mode CLI confirmed | PASS — updated |
| M3 | §V.C.6.5 line 454 (S7 60-only entries) | "6 entries present in 60-corpus but absent from 90-corpus" | **CRITICAL ERROR:** actual is `\|60 ∩ 90\| = 0`; ALL 60 entries are 60-only and ALL 90 are 90-only. The corpora are completely disjoint (legacy `S0001`-format IDs vs `v2_L<tier>_<domain>_NNN` IDs). | FAIL → corrected |
| M4 | §V.C.6.6 line 473 (mpnet mean) | 0.4725 | Verified against canonical `v1b_20260524T044018Z.json:cosine_stats_per_encoder.mpnet.mean = 0.4725` | PASS — marker removed |
| M5 | §V.C.6.6 line 482 (mpnet outliers ratio) | "9 of 14 mpnet outliers" | Verified: 14 total mpnet outliers; 9 Layer-3 only (excluding 4 Layer-5 + 1 multi-validator). Both numbers correct. | PASS — marker removed, framing clarified |
| M6 | §V.C.6.8 line 512 (S10 consensus rate) | "81.5% (53/65)" all-Step-2-in-band | **CRITICAL ERROR:** Actual is **78.5% (51/65)** (`any_secondary_fails_count = 14`; 65 − 14 = 51). The 53/65 = 81.5% is the V1a MiniLM-only pass rate, not Step-2 consensus. | FAIL → corrected |
| M7 | §V.C.6.9 line 531 (S11 D/E ratio) | "6 / 9 (67%) of mpnet outliers" | **CRITICAL ERROR:** Of 14 total mpnet outliers, D+E = 9 (Cat D=6, E=3). Ratio is **9/14 = 64%**, not 6/9 = 67%. Over-anchor rate is 2.1×, not 2.2×. | FAIL → corrected |

### Task 2 — Phase 1.F Master Matrix (§V.A.4) — 8 / 8 cells PASS

Verified every cell against `eval/results/phase1_F/m4_matrix.json`:

| Cell | Encoder × Corpus | θ | Bypass% | GLR% | ULR% | Per-BP% | Cost | Wall | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | MiniLM × 60 | 0.50 ✓ | 47.60 ✓ | 2.21 ✓ | 0.00 ✓ | 4.7 ✓ | 0.0240 ✓ | 489.7 ✓ | PASS |
| 2 | MiniLM × 90 | 0.45 ✓ | 42.80 ✓ | 2.58 ✓ | 0.00 ✓ | 6.0 ✓ | 0.0191 ✓ | 414.6 ✓ | PASS |
| 3 | mpnet × 60 | 0.50 ✓ | 36.90 ✓ | 7.01 ✓ | 0.00 ✓ | 19.0 ✓ | 0.0177 ✓ | 382.3 ✓ | PASS |
| 4 | mpnet × 90 | 0.50 ✓ | 49.45 ✓ | 5.17 ✓ | 0.00 ✓ | 10.4 ✓ | 0.0217 ✓ | 465.9 ✓ | PASS |
| 5 | bge-large × 60 | 0.70 ✓ | 36.53 ✓ | 9.23 ✓ | 0.00 ✓ | 25.3 ✓ | 0.0165 ✓ | 363.6 ✓ | PASS |
| 6 | bge-large × 90 | 0.80 ✓ | 54.98 ✓ | 11.44 ✓ | 0.00 ✓ | 20.8 ✓ | 0.0261 ✓ | 6684.6 ✓ | PASS |
| 7 | FinLang × 60 | 0.50 ✓ | 54.24 ✓ | 3.32 ✓ | 0.00 ✓ | 6.1 ✓ | 0.0259 ✓ | 533.7 ✓ | PASS |
| 8 | FinLang × 90 | 0.50 ✓ | 53.87 ✓ | 6.27 ✓ | 0.00 ✓ | 11.6 ✓ | 0.0246 ✓ | 588.1 ✓ | PASS |

Total cost $0.1756 ✓. Total wall 9922.5s ✓.

### Task 3 — M3.5 Calibrated Thresholds (§V.A.3.2) — 8 / 8 PASS

All 8 sensitive_threshold values match m4_matrix.json (covered in Task 2 θ column).

### Task 4 — Other Gate Parameters (§V.A.3.3) — VERIFIED

Verified via Phase 1.F §3.3 (canonical source): base = 0.75, strict = 0.45, hard = 0.70 leak score, soft = 0.60 leak score, cascade k = 2. These are config-yaml settings (not module constants), held constant at v9-canonical values across all 8 cells.

### Task 5 — Encoder Revision Pins (§V.A.2.1) — UPDATED

Resolved from `core/config_loader.py:PINNED_REVISIONS`:

| Encoder | Pin | Status in §V.A.2.1 |
| --- | --- | --- |
| MiniLM | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` | already correct ✓ |
| mpnet | `e8c3b32edf5434bc2275fc9bab85f82640a19130` | replaced `[REF: PINNED_REVISIONS]` ✓ |
| bge-large | `d4aa6901d3a41ba39fb536a557fa166f842b0e09` | replaced `[REF: PINNED_REVISIONS]` ✓ |
| FinLang | `37d7594d02e3d656a241e099e39ac50ab921f999` | replaced `[REF: PINNED_REVISIONS]` ✓ |

**ALSO CORRECTED:** Draft listed FinLang model as `FinLang/investopedia-embedding-model`; actual `PINNED_REVISIONS` key is `FinLang/finance-embeddings-investopedia`. Corrected.

### Task 6 — Defender + Generation LLM Models — VERIFIED

- Defender LLM: `gpt-4o-mini-2024-07-18` (matches `PINNED_OPENAI_MODEL`) ✓
- Generation LLM: `gpt-5-mini-2025-08-07` (matches `PINNED_OPENAI_GENERATION_MODEL_E1_2`) ✓

### Task 7 — Hard-Negative Corpus Size — VERIFIED

Read `data/benchmark/hard_negatives_seeds_draft.jsonl` (rename to `hard_negatives.jsonl` per V2 §5.1 has NOT been executed yet):
- 65 entries × 22 fields each ✓
- 36 / 36 sub-cells covered ✓
- 7 sub-cells with n ≥ 5 (rich) ✓ (one is n=6, six are n=5)
- 29 sub-cells with n = 1 (degenerate) ✓
- 0 sub-cells with n = 0 (empty) ✓

### Task 8 — Findings against `PHASE_1E_RESULTS.md` — VERIFIED

`PHASE_1E_RESULTS.md` master close-out and canonical `v1b_20260524T044018Z.json:documented_findings` confirm:
- 14 documented_findings keys = 12 S-findings + 2 RESOLVED V2.5 decisions ✓
- S-numbering: S1, S2, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14 with S3/S4 sequential gaps ✓ (matches draft)
- Each finding's prose direction matches the validator's embedded text (S1 cross-domain spillover, S2 audit-efficacy 5×, etc.) ✓
- RESOLVED_V2_5_PLAN_REVISION (refs S1+S8+S9) and RESOLVED_V2_5_SCHEMA_REVISION (refs S7), both Option B document-only ✓

### Task 9 — §V.B Phase 1.G Methodology Consistency — MOSTLY VERIFIED

Cross-referenced `PHASE_1G_PLAN.md` against §V.B claims:

- n = 5 samples per cell (§V.B.2.1) ✓
- t_{0.025, 4} = 2.776 (§V.B.2.4) ✓
- $0.70 LLM budget (§V.B.7) ✓
- Sample 1 = Phase 1.F (committed at 007c460) (§V.B.2.2) ✓
- **Holm-Bonferroni** adjustment for 4 paired tests (§V.B.2.4) — **`[NEEDS_HUMAN_REVIEW]`**: `PHASE_1G_PLAN.md` §3.4 specifies plain "Bonferroni correction (α' = 0.0125)". Draft uses "Holm-Bonferroni" with rationale "more powerful than Bonferroni for low correlated tests." Both are valid; the discrepancy is a design choice. Recommend ratifying which to use before G2 execution.

### Task 10 — Phase 1.E Errata Commit Reference — VERIFIED

`e198e97` is the actual commit hash for the Phase 1.E errata. `git log` output confirms:
```
e198e97 phase1E: errata - correct Phase 1.G scope (multi-sample stochasticity per V2 plan)
```

§V.C.7 reference to `e198e97` is correct ✓

### Task 11 — Phase 1.F Commit Reference — VERIFIED

`007c460` is the actual commit hash for Phase 1.F M3–M5 close:
```
007c460 phase1F: M3-M5 complete - per-encoder calibration + 8-cell ablation matrix + results writeup
```

§V.A.6 + §V.B.2.2 references are correct ✓

### Task 12 — Contribution Count (C1–C12) — MOSTLY VERIFIED + 1 MINOR FIX

v9 paper's contributions (verified verbatim from `sentinelflow_journal_v9_final.tex` lines 97–115):
- C1: **Multi-Gate Inline Security Pipeline** — draft was "Multi-Gate Inline Pipeline" (missing "Security") → FIXED
- C2: **Sentence-Level Semantic Leakage Firewall** — draft was "Sentence-Level Leakage Firewall" (missing "Semantic") → FIXED
- C3: Domain-Specific Evaluation Framework ✓
- C4: Prompt Distribution Monitoring ✓
- C5: Auditable Evidence Chain ✓
- C6: Adversarial Evaluation Methodology ✓
- C7: Cross-Domain Generalization ✓

v10 §I.B and §VII both count "twelve" contributions ✓. §VI roadmap says "12 contributions C1–C12" ✓.

### Task 13 — File Path References — 11 / 12 PASS, 1 path issue

| File | Exists? | Notes |
| --- | --- | --- |
| `scripts/repro_full_pipeline.py` (673 LOC; draft says ~670) | ✓ exists | LOC ~670 is acceptable rounding |
| `scripts/validate_hard_negatives.py` (1832 LOC) | ✓ exists | LOC corrected from ~1800 |
| `scripts/phase1G_multi_sample.py` (490 LOC) | ✓ exists | Matches draft |
| `core/config_loader.py` | ✓ exists | |
| `eval/results/phase1_F/m4_matrix.json` | ✓ exists | |
| `eval/results/phase1_F/build_log.json` | ✓ exists | |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | ✓ exists | |
| `eval/results/phase1_E/validation/v1b_*.json` (canonical: `v1b_20260524T044018Z.json`) | ✓ exists | |
| `eval/results/phase1_E/validation/outlier_inventory.md` | ✓ exists | |
| `eval/results/phase1_E/validation/v2_benign_check_report.md` | ✓ exists | |
| **`data/benchmark/hard_negatives.jsonl`** | **✗ does not exist** | **`[NEEDS_HUMAN_REVIEW]`**: actual file is `data/benchmark/hard_negatives_seeds_draft.jsonl`. The V2 §5.1 rename was deferred at Phase 1.E close (per `PHASE_1E_E1_6_RESULTS.md` §4.3). Validator code constants still reference draft path. §V.C.7 reproducibility section updated to flag this in-place. |
| `eval/results/phase1_G/run_state.json` + `run_log.jsonl` | ✓ exist | G1 currently running |

### Task 14 — V2 Plan Section References — VERIFIED

All V2 plan section references in the drafts are correct:
- V2 §2.5 — Multi-encoder validation 2-step rule ✓ (matches `PHASE_1E_PLAN_V2.md` §2.5 starting line 228)
- V2 §4.1 — Per-query properties / BLOCKING checks ✓ (line 336)
- V2 §4.2 — Validator design ✓ (line 362)
- V2 §5.1 — Final corpus file path ✓ (line 437)
- V2 §5.2 — JSONL schema ✓ (line 442)
- V2 §7 R6 — Risk assessment / R6 ✓ (§7.2 is the actual R6 sub-section, line 506; draft uses "V2 §7 R6" shorthand which is acceptable)

### Task 15 — v9 Paper Claims (C1–C7 + Headline Numbers) — VERIFIED

C1–C7 substantive content matches v9 (titles minor-corrected per Task 12). Headline numbers from v9 abstract:
- 2.58% true end-to-end leakage on 271 internal attacks ✓ (matches v9 line 67)
- 3% FPR on benign analyst queries ✓ (v9 abstract + §IV.6 contributions)
- 28.75 ms P50 latency ✓ (v9 line 67 + §IV.G)
- 100% audit chain integrity ✓ (v9 abstract + §IV.H)
- 85% TPR, 0% FPR via configuration-only adaptation (medical pilot) ✓ (v9 §IV-N line 1063)

### Task 16 — Internal Cross-References — 1 FIX APPLIED

| Reference | Status |
| --- | --- |
| §V.A.5 F1, F2, F3 defined | ✓ exists (§V.A.5.1, §V.A.5.2, §V.A.5.3) |
| §V.B references §V.A.5 F1/F2/F3 | ✓ targets exist |
| §V.C.6 references §V.C.6.13 RESOLVED | ✓ exists (§V.C.6.13) |
| §VI references **§V.C.6.14** for S14 | **FIXED:** corrected to **§V.C.6.12** (S14 is at §V.C.6.12 per draft's S3/S4-gap numbering) — applied via `replace_all` to all `§V.C.6.14` instances in §VI |
| §I.C section roadmap | ✓ section names match (§II / §III / §IV preserved; §V / §VI / §VII as v10 additions) |

---

## Discrepancies Found

### Critical (paper-claim-affecting)

| # | Location | Issue | Correction Applied |
| --- | --- | --- | --- |
| 1 | §V.C.6.5 (S7) | "6 entries 60-only" — wrong by 10× | Corrected to "all 60 entries; corpora are completely disjoint" — strengthens S7 finding |
| 2 | §V.C.6.8 (S10) | 53/65 (81.5%) — wrong; this is the V1a pass rate, not Step-2 consensus | Corrected to 51/65 (78.5%) Step-2 consensus |
| 3 | §V.C.6.9 (S11) | "6/9 (67%)" of mpnet outliers in D/E — wrong | Corrected to "9/14 (64%)" of mpnet outliers in D/E; over-anchor 2.1× (not 2.2×) |
| 4 | §V.A.2.1 | Wrong FinLang model name (`investopedia-embedding-model`) | Corrected to `FinLang/finance-embeddings-investopedia` (matches PINNED_REVISIONS key) |

### Minor (cosmetic / linkage)

| # | Location | Issue | Correction Applied |
| --- | --- | --- | --- |
| 1 | §I.B C1 title | "Multi-Gate Inline Pipeline" missing "Security" | Restored "Multi-Gate Inline Security Pipeline" to match v9 verbatim |
| 2 | §I.B C2 title | "Sentence-Level Leakage Firewall" missing "Semantic" | Restored "Sentence-Level Semantic Leakage Firewall" |
| 3 | §VI references §V.C.6.14 for S14 (4 occurrences) | S14 is actually at §V.C.6.12 per S3/S4-gap numbering | Replaced all 4 occurrences with §V.C.6.12 |
| 4 | §V.A.6 says `repro_full_pipeline.py` ~670 LOC | Actual: 673 LOC | Acceptable rounding; not changed |

---

## Updates Applied to Drafts

### `v10_paper_section_V_A_phase1F_draft.md`
- Line 67-69: replaced 3 × `[REF: PINNED_REVISIONS]` with actual mpnet/bge-large/FinLang revision hashes
- Line 69: corrected FinLang model name to `FinLang/finance-embeddings-investopedia`

### `v10_paper_section_V_C_phase1E_draft.md`
- Line 265 (M1a): V5b N=150, 19,500 comparisons inline-stated
- Line 281 (M2a): validator LOC corrected to "1832 LOC"
- Line 454 (M3): S7 wording changed from "6 entries 60-only" to "completely disjoint, all 60 entries 60-only"
- Line 473 (M4): mpnet mean 0.4725 verified, marker removed
- Line 482 (M5): mpnet outlier count clarified as 14 total / 9 Layer-3-only
- Line 512 (M6): consensus rate corrected from 53/65 (81.5%) to 51/65 (78.5%)
- Line 531 (M7): D/E ratio corrected from 6/9 (67%) to 9/14 (64%); over-anchor 2.2× → 2.1×
- Line 553 (M1b): V5b N=150 second occurrence corrected
- Line 661 (M2b): validator LOC second occurrence corrected
- §V.C.7 final-corpus path: added `[NEEDS_HUMAN_REVIEW]` note that `hard_negatives.jsonl` rename is deferred; actual file is `hard_negatives_seeds_draft.jsonl`
- §V.C.7 reproducer command updated to reflect actual mode-based CLI (vs V2-design CLI)

### `v10_paper_section_VI_draft.md`
- All 4 instances of `§V.C.6.14` (referring to S14) replaced with `§V.C.6.12`

### `v10_paper_sections_I_VII_draft.md`
- C1 title: added "Security" → "Multi-Gate Inline Security Pipeline"
- C2 title: added "Semantic" → "Sentence-Level Semantic Leakage Firewall"

### `v10_paper_section_V_B_phase1G_draft.md`
- **No edits applied.** All [PLACEHOLDER] / [TBD] markers preserved per task rule 5.
- Bonferroni vs Holm-Bonferroni discrepancy with `PHASE_1G_PLAN.md` flagged as `[NEEDS_HUMAN_REVIEW]` (see Task 9).

---

## Items Requiring Human Review

### `[NEEDS_HUMAN_REVIEW]` #1: Corpus rename deferred

`PHASE_1E_E1_6_RESULTS.md` §4.3 documents a deferred V2 §5.1 rename (`hard_negatives_seeds_draft.jsonl` → `hard_negatives.jsonl`). The rename was not executed at Phase 1.E close per Claude Code's `不 git ops` discipline. §V.C.7 draft has been updated to flag this in-place. **Action item:** decide whether to execute the rename before paper submission (LaTeX section should reference the final name) or to retain the draft-name throughout v10 with explicit acknowledgment of the deferral.

### ~~`[NEEDS_HUMAN_REVIEW]` #2: Bonferroni vs Holm-Bonferroni~~ **RESOLVED 2026-05-25**

**Original gap:** `PHASE_1G_PLAN.md` §3.4 specified plain Bonferroni (α' = 0.0125); §V.B.2.4 draft specified Holm-Bonferroni.

**Resolution:** User ratified Holm-Bonferroni (Decision (β), 2026-05-25). `PHASE_1G_PLAN.md` §3.4 revised to specify Holm step-down algorithm with rank-by-rank thresholds {α/4 = 0.0125; α/3 = 0.0167; α/2 = 0.0250; α/1 = 0.0500}. New §15 Changelog documents V2 → V2.5 plan revision per "document deviations, don't refit" philosophy. Related Documents section moved from §15 → §16. §V.B.2.4 footnote added pointing to plan §15 changelog. Plan and paper now aligned. Impact on G1 production: none (G1 = sample collection; correction applied at G2).

---

## Phase 1.G G1 Status Check (Read-Only)

Read from `eval/results/phase1_G/run_state.json` at report time:

| Metric | Value |
| --- | --- |
| Completed samples | **17 / 32** |
| Cumulative cost | **$0.3443 / $1.00** (34% of phase cap) |
| Latest sample | `bge_large_60entry/sample_2` (2026-05-24T20:37:28Z) |
| Status | Running normally; no `stop_and_disclose` event logged |

**Trajectory:** ~17h elapsed from kickoff (assumed ~9:30 AM Sunday); about half-way through the expected ~11h wall but Cell 6 (bge-large × 90) dominates remaining wall (~7.4h cumulative on that cell across 4 samples). On track for completion by late Monday morning if uninterrupted.

No interference with G1 process during this verification round.

---

## Audit Trail

**Files read during verification (read-only):**
- All 5 draft files in `paper_drafts/v10/`
- `scripts/validate_hard_negatives.py` (1832 LOC; V5b implementation)
- `scripts/phase1G_multi_sample.py` (490 LOC)
- `scripts/repro_full_pipeline.py` (673 LOC)
- `core/config_loader.py` (PINNED_REVISIONS + PINNED_OPENAI_MODEL)
- `eval/results/phase1_F/m4_matrix.json` (8-cell aggregate)
- `eval/results/phase1_E/validation/v1b_20260524T044018Z.json` (V1b canonical)
- `data/benchmark/hard_negatives_seeds_draft.jsonl` (65 entries × 22 fields)
- `data/secrets/secrets.jsonl` (60 entries) + `secrets_v2.jsonl` (90 entries)
- `sentinelflow_journal_v9_final.tex` (contributions C1–C7 + abstract)
- `PHASE_1E_PLAN_V2.md`, `PHASE_1G_PLAN.md`, `PHASE_1E_RESULTS.md` references
- `PHASE_1F_RESULTS.md` § headers
- Git history via `git log --oneline`
- `eval/results/phase1_G/run_state.json` (read-only G1 status check)

**No project files written.** Only 4 markdown drafts in `paper_drafts/v10/` were edited.

**No git operations performed.**

**No LLM calls made.**

**No interference with Phase 1.G G1 background process.**

---

*End of `CLAUDE_CODE_VERIFICATION_REPORT.md`. 2026-05-25
verification audit complete; 4 critical numerical corrections
applied; 3 minor corrections applied; 2 items flagged for human
review. All 5 drafts now faithful to project codebase + canonical
results within the verification scope of this task.*
