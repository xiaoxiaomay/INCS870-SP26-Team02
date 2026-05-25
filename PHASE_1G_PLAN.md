# Phase 1.G — Multi-sample LLM Stochasticity Probe: Plan

> **Status:** DESIGN RATIFIED 2026-05-24. All 7 design dimensions
> (D1–D7) + G1–G4 sub-phase sequencing approved by user. No
> implementation work in this design session; deliverable is
> this plan document only. Phase 1.G operationalizes the
> stochasticity-probe scope per V2 plan §13 + `PHASE_1F_RESULTS.md`
> §11.1 #2 (authoritative).
>
> **Scope:** Re-run Phase 1.F M4's 8-cell ablation matrix with
> **n=5 samples per cell** (Phase 1.F 007c460 as sample-1; 4
> additional samples this phase) using **GPT-4o-mini-2024-07-18**
> pinned. Convert point-estimate GLR/Bypass/Per-BP-Leak numbers
> to mean ± std + Student's t 95% CI. Apply paired t-tests on 4
> within-encoder corpus deltas. Verify cross-encoder ordering
> robustness across all n samples.
>
> **Budget:** $0.70 LLM (4 additional × $0.1756 per Phase 1.F
> single-run), ~14 hours wall (G1 ~11h + G2-G4 ~3h analysis), $0
> code/implementation cost.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §13 (Phase 1.G referenced).
> - `PHASE_1F_RESULTS.md` §3.3 (8-cell ablation design), §4.1
>   (master matrix), §7.1 (Cell-1 +0.36pp drift), §11.1 #2
>   (Phase 1.G specification).
> - `core/config_loader.py:PINNED_OPENAI_MODEL` =
>   `"gpt-4o-mini-2024-07-18"`.
> - Phase 1.F 007c460 committed outputs (immutable; treated as
>   sample-1 of n=5).
>
> **Outputs (this design session):**
> - `PHASE_1G_PLAN.md` (this document).

---

## §1 — Executive Summary

### §1.1 — Phase 1.G scope

**Multi-sample LLM stochasticity probe.** Phase 1.F's M4 ablation
matrix (8 cells = 4 encoders × 2 corpora) produces point-estimate
GLR / Bypass% / Per-BP-Leak% numbers at n=1 per cell. §7.1
documents stochastic drift of ±0.4pp (Cell-1: +0.36pp GLR drift
between Part B replay and M4 run). The drift exceeds Watchpoint A
tolerance (±0.3pp) and brings within-encoder corpus comparisons
(e.g., MiniLM × 60 GLR 2.21% vs MiniLM × 90 GLR 2.58% = 0.37pp
delta) *within* the stochastic band — meaning v10 §V cannot
honestly claim per-cell statistical significance from point
estimates alone.

**Phase 1.G addresses this** by adding **4 additional samples per
cell** (n=5 total when Phase 1.F's sample is included), enabling:

- Per-cell statistics: mean ± std + Student's t 95% CI.
- Within-encoder paired t-test for the 4 corpus-delta claims
  (MiniLM × 60 vs ×90, mpnet × 60 vs ×90, bge-large × 60 vs ×90,
  FinLang × 60 vs ×90).
- Cross-encoder ordering robustness verification across all n=5
  samples (MiniLM < mpnet < bge-large on per-BP leak).

### §1.2 — Headline budget

| Metric | Value |
| --- | --- |
| Sample count per cell (n) | **5** (D1 ruling) |
| Phase 1.F sample-1 contribution | from commit 007c460 (immutable) |
| Additional samples per cell | **4** (this phase) |
| Cells in scope | **8** (full ablation, D3 ruling) |
| LLM model pin (defender) | `gpt-4o-mini-2024-07-18` (D4 ruling) |
| LLM cost | **$0.70** ($0.1756 × 4 additional runs) |
| Phase 1.G phase cap | **$1.00** (70% utilization, D7 ruling) |
| Per-cell cost cap | **$0.15** (D7 ruling) |
| Total wall (G1 + G2 + G3 + G4) | **~14 hours** (G1 ~11h + G2-G4 ~3h) |
| Statistical framework | Mean ± std + Student's t 95% CI + paired t-test (D5 ruling) |

### §1.3 — Key deliverables

- Per-sample GLR/Bypass/Per-BP-Leak data for 32 additional cell-
  runs (8 cells × 4 samples).
- `eval/results/phase1_G/matrix_n5.json` (per-cell aggregated
  statistics).
- `PHASE_1G_RESULTS.md` (close-out doc; mirror Phase 1.F format).
- v10 §V draft claim update with mean ± CI notation.
- Validation or refutation of §7.1's "within stochastic band"
  claim using n=5 data.
- Memory persistence (`project_phase1g_close.md` +
  `MEMORY.md` index).

---

## §2 — Scope and Boundaries

### §2.1 — In scope (this phase)

| Item | Source |
| --- | --- |
| Multi-sample re-run of Phase 1.F M4's 8 cells with n=4 additional samples each | V2 §13 + §11.1 #2 |
| Statistical aggregation (mean / std / Student's t 95% CI) | D5 ruling |
| Paired t-test on 4 within-encoder corpus deltas | D5 ruling |
| Cross-encoder ordering robustness across n samples | §7.1 implicit |
| Phase 1.F sample-1 reuse (immutable; not re-run) | D6 ruling |
| `eval/results/phase1_G/` output directory (preserves Phase 1.F immutable) | D6 ruling |
| v10 §V claim integration with mean ± CI notation | G3 sub-phase |

### §2.2 — Out of scope (deferred to v11 or later)

| Item | Disposition |
| --- | --- |
| Adaptive attacker evaluation | Unscheduled "Hardening" per `PLAN.md` line 150; no reviewer mandate documented; may become Phase 1.I if reviewer feedback emerges from v10 draft |
| Higher-n protocols (n=10, n=20) | Deferred to v11; n=5 sufficient for paper-grade claims at current budget |
| Cross-model stochasticity comparison (e.g., GPT-4o vs gpt-4o-mini drift profiles) | Deferred; outside V2 §13 + §11.1 #2 scope |
| New encoders (e.g., text-embedding-3, OpenAI proprietary) | Phase 1.H per V2 §13 line 901; separate phase |
| New corpora / multi-turn evals / salami evals | V2 §13 line 905; out of E1.x scope |
| Bayesian posterior framework (D5 option d) | Deferred; Student's t-CI sufficient at n=5 |

### §2.3 — Acceptance criteria

PASS gate (5 / 5):

- ✓ All 8 cells × 4 additional samples = 32 cell-runs complete.
- ✓ Per-cell statistical aggregation present in
  `matrix_n5.json` (mean / std / t-CI for GLR / Bypass / Per-BP-
  Leak).
- ✓ 4 within-encoder paired t-tests computed; p-values reported.
- ✓ Cross-encoder ordering verified for all metrics across all
  n=5 samples.
- ✓ Phase 1.G LLM cost ≤ $1.00 phase cap; per-cell ≤ $0.15.

---

## §3 — Methodology

### §3.1 — Multi-sample protocol

For each of the 8 cells defined in Phase 1.F §3.3:

```
sample_i (i ∈ {2, 3, 4, 5}) execution:
  1. Load encoder + FAISS index per Phase 1.F M2 build_log (cached;
     no re-build needed).
  2. Apply M3.5-calibrated sensitive_threshold per cell (see §4 below).
  3. Process 271-prompt fixed adversarial corpus
     (data/eval/full_adversarial_corpus.jsonl) end-to-end:
        Gates → LLM call (gpt-4o-mini-2024-07-18) → leakage scan → redaction.
  4. Record per-sample metrics: GLR%, Bypass%, ULR%, Per-BP-Leak%,
     wall_seconds, cost_usd, sample_timestamp.
  5. Atomic write to eval/results/phase1_G/<cell_id>/sample_<i>.json.
```

Phase 1.F 007c460 outputs are treated as `sample_1`; references
in `matrix_n5.json` cite 007c460 commit hash for provenance.

### §3.2 — Random seed handling (per D2 ruling)

**No seed parameter.** OpenAI's `seed` is best-effort and not
guaranteed reproducible across calls. We measure natural
stochasticity at default temperature; reproducibility is at the
aggregate-statistic level (mean ± CI), not per-sample.

### §3.3 — LLM model pin (per D4 ruling)

`gpt-4o-mini-2024-07-18` — exact same as Phase 1.F (canonical via
`core/config_loader.py:PINNED_OPENAI_MODEL`). No revision change;
Phase 1.G is by definition a multi-sample re-run, not a cross-
model comparison.

### §3.4 — Statistical framework (per D5 ruling)

**Per-cell aggregation:**
- Mean: `μ = (1/n) Σ x_i`
- Standard deviation: `σ = sqrt((1/(n-1)) Σ (x_i - μ)²)` (sample std)
- Student's t 95% CI: `μ ± t_{α/2, n-1} × σ/√n`
  - At n=5, t_{0.025, 4} = **2.776**
  - CI half-width: 2.776 × σ/√5 ≈ 1.241 × σ
- Three metrics: GLR%, Bypass%, Per-BP-Leak%
- One verification metric: ULR% (expected 0% across all samples;
  deterministic per Phase 1.F §7.1)

**Within-encoder paired t-test (4 tests):**
- H₀: no difference between 60-entry and 90-entry corpora for the
  given encoder.
- Tests: MiniLM ×60 vs ×90; mpnet ×60 vs ×90; bge-large ×60 vs
  ×90; FinLang ×60 vs ×90.
- Paired (same encoder, same prompts, paired by sample number).
- Two-sided, α = 0.05.
- Report: t-statistic, df = n-1 = 4, p-value, mean delta, 95% CI
  on delta.
- **Holm-Bonferroni correction** over k = 4 paired tests
  (V2.5 errata revision; see §15 changelog).
  Algorithm:
  1. Compute the 4 unadjusted two-sided p-values from the paired
     t-tests above.
  2. Sort ascending: p_(1) ≤ p_(2) ≤ p_(3) ≤ p_(4).
  3. For each i ∈ {1, 2, 3, 4}, compare p_(i) to the adjusted
     threshold α / (k − i + 1):
     | Rank i | Threshold | Value at α = 0.05, k = 4 |
     | --- | --- | --- |
     | 1 (smallest p) | α / 4 | **0.0125** |
     | 2 | α / 3 | **0.0167** |
     | 3 | α / 2 | **0.0250** |
     | 4 (largest p) | α / 1 | **0.0500** |
  4. Reject H₀ at rank i iff *every* preceding rank j ≤ i was
     also rejected (sequential / step-down rule). The first
     non-rejection at rank i halts further rejections at
     ranks i+1 … k.
- Report both unadjusted p-values and Holm-rejection decisions.
- Family-wise error rate (FWER) ≤ α = 0.05 across the 4-test
  family.
- Rationale (vs plain Bonferroni α' = 0.0125 uniform): Holm
  preserves FWER control while delivering more statistical power
  when some effects are real, particularly relevant for the
  MiniLM 60 vs 90 GLR close-call comparison (+0.37 pp single-
  sample delta, on the boundary of the stochastic band). See
  §15 changelog for the V2 → V2.5 plan revision.

**Cross-encoder ordering robustness:**
- Phase 1.F §5.1 claim: MiniLM < mpnet < bge-large on per-BP-leak
  rate (point estimates 5.3 < 14.7 < 23.1).
- Robustness check: does the ordering hold sample-by-sample
  across n=5? Report fraction of samples where ordering preserved
  (target: 5/5 = 100% if effect size dominates stochasticity).
- Per Phase 1.F §7.1: effect size ~18pp >> stochastic drift ~0.4pp,
  so ordering is expected to hold; confirm empirically.

---

## §4 — Per-Cell Properties (Verification Table)

The 8 cells are identical to Phase 1.F M4 §3.3. Reproduced for
self-contained reference; **calibrated thresholds verbatim from
Phase 1.F**:

| Cell | Encoder × Corpus | Dim | Sens. θ | Per-cell cost cap | Phase 1.F sample-1 (GLR%) |
| --- | --- | --- | --- | --- | --- |
| 1 | MiniLM × 60 | 384 | 0.50 | $0.15 | 2.21 |
| 2 | MiniLM × 90 | 384 | 0.45 | $0.15 | 2.58 |
| 3 | mpnet × 60 | 768 | 0.50 | $0.15 | 7.01 |
| 4 | mpnet × 90 | 768 | 0.50 | $0.15 | 5.17 |
| 5 | bge-large × 60 | 1024 | 0.70 | $0.15 | 9.23 |
| 6 | bge-large × 90 | 1024 | 0.80 | $0.15 | 11.44 |
| 7 | FinLang × 60 | 768 | 0.50 | $0.15 | 3.32 |
| 8 | FinLang × 90 | 768 | 0.50 | $0.15 | 6.27 |

Other gate parameters held constant at v9-canonical (Phase 1.F
§3.3 verbatim):
- `threshold` (base) = 0.75
- `sensitive_threshold` (strict) = 0.45
- `hard` leak score = 0.70
- `soft` leak score = 0.60
- `cascade k` = 2
- 271-prompt adversarial corpus at
  `data/eval/full_adversarial_corpus.jsonl`.

Per-cell cost cap of $0.15 is **safety margin** above the worst-
case observed Phase 1.F per-cell cost ($0.0261 for Cell 6); with
4 additional samples expected per-cell cost is ~$0.10, leaving
~33% headroom for retries or API variance.

### §4.1 — Per-cell BLOCKING properties (acceptance gates)

| # | Property | Verification | Status |
| --- | --- | --- | --- |
| G1 | All 4 additional samples per cell completed | File existence: `sample_2.json` … `sample_5.json` per cell directory | **BLOCKING** |
| G2 | Per-cell wall ≤ 8h (Cell 6 expected ~7.4h cumulative across 4 samples) | Aggregate wall per cell | Warn if exceeded |
| G3 | Per-cell cost ≤ $0.15 | `cost_usd` sum per cell ≤ cap | **BLOCKING; stop-and-disclose on exceed** |
| G4 | ULR = 0% across all samples | `ulr_percent` per sample equals 0.0 | **BLOCKING; rule-based redaction must be deterministic** |
| G5 | Bypass% matches Phase 1.F single-sample (within sampling variance, no algorithmic drift) | Compare distribution to Phase 1.F sample-1 | Warn if >±2pp drift on any sample |

---

## §5 — Schema

### §5.1 — Per-sample output (`eval/results/phase1_G/cell_<N>/sample_<i>.json`)

```json
{
  "schema_version": "phase1G_per_sample_v1",
  "cell_id": 1,
  "cell_label": "MiniLM × 60",
  "encoder_short": "minilm",
  "corpus_label": "60entry",
  "sample_id": 2,
  "sample_of_n": 5,
  "model_pin": "gpt-4o-mini-2024-07-18",
  "phase_1f_sample_1_commit": "007c460",
  "sensitive_threshold": 0.50,
  "gate_params": {
    "base_threshold": 0.75,
    "strict_threshold": 0.45,
    "hard_leak_score": 0.70,
    "soft_leak_score": 0.60,
    "cascade_k": 2
  },
  "metrics": {
    "bypass_percent": null,
    "glr_percent": null,
    "ulr_percent": 0.0,
    "per_bp_leak_percent": null,
    "raw_counts": {
      "total_prompts": 271,
      "bypassed_to_llm": null,
      "post_llm_leaks": null,
      "user_facing_leaks": null
    }
  },
  "cost_usd": null,
  "wall_seconds": null,
  "sample_timestamp_utc": null
}
```

### §5.2 — Per-cell aggregated output (`eval/results/phase1_G/matrix_n5.json`)

```json
{
  "schema_version": "phase1G_matrix_v1",
  "n_samples": 5,
  "phase_1f_sample_1_commit": "007c460",
  "model_pin": "gpt-4o-mini-2024-07-18",
  "generated_at": "2026-MM-DDTHH:MM:SSZ",
  "cells": [
    {
      "cell_id": 1,
      "cell_label": "MiniLM × 60",
      "samples_summary": {
        "glr_percent": {
          "values": [2.21, "...", "...", "...", "..."],
          "mean": null,
          "std": null,
          "ci_95_lower": null,
          "ci_95_upper": null,
          "ci_half_width": null
        },
        "bypass_percent": { "...": "same structure" },
        "per_bp_leak_percent": { "...": "same structure" },
        "ulr_percent": { "values": [0.0, 0.0, 0.0, 0.0, 0.0], "all_zero": true }
      },
      "cumulative_cost_usd": null,
      "cumulative_wall_seconds": null
    }
  ],
  "within_encoder_paired_tests": [
    {
      "encoder": "minilm",
      "test_label": "MiniLM × 60 vs × 90 (GLR)",
      "delta_mean": null,
      "delta_std": null,
      "t_statistic": null,
      "df": 4,
      "p_value": null,
      "p_value_bonferroni": null,
      "ci_95_on_delta": [null, null],
      "verdict": null
    }
  ],
  "cross_encoder_ordering_check": {
    "claim": "MiniLM < mpnet < bge-large on per-BP-leak rate",
    "samples_with_ordering_preserved": null,
    "samples_total": 5,
    "robustness_rate": null
  },
  "cost_summary": {
    "phase_1g_additional_cost_usd": null,
    "phase_1f_baseline_cost_usd": 0.1756,
    "total_phase_1f_plus_1g": null,
    "phase_cap_usd": 1.00,
    "per_cell_cap_usd": 0.15
  }
}
```

### §5.3 — Schema population timeline

| Field group | Populated during |
| --- | --- |
| Per-sample `metrics` (raw counts + percentages) | G1 sub-phase (LLM evaluation) |
| Per-sample `cost_usd` / `wall_seconds` / `sample_timestamp_utc` | G1 sub-phase |
| Per-cell `samples_summary` aggregates (mean / std / CI) | G2 sub-phase (local compute) |
| `within_encoder_paired_tests` | G2 sub-phase |
| `cross_encoder_ordering_check` | G2 sub-phase |
| `cost_summary` | G1 (incremental) + G2 (final) |

---

## §6 — Sequencing

### §6.1 — G1 — Multi-sample re-run

| Step | Detail |
| --- | --- |
| G1.1 — Driver script | Adapt `scripts/phase1F_matrix.py` (or `scripts/repro_full_pipeline.py`) into multi-sample wrapper. Per-cell loop: 4 additional samples per cell. Atomic write each `sample_<i>.json`. |
| G1.2 — Per-cell cost monitoring | Track `cumulative_cost_usd` per cell; STOP-AND-DISCLOSE if any cell exceeds $0.15 cap. |
| G1.3 — Per-sample checkpoint | After each full pass through 8 cells (≈ 2.75h wall + Cell 6 ~1.86h = ~4.6h actual), checkpoint progress; allow multi-session split if needed. Estimated 4 checkpoints (one per additional sample). |
| G1.4 — ULR verification | Confirm `ulr_percent = 0.0` on every sample. Any non-zero ULR triggers STOP-AND-DISCLOSE (would indicate redaction-stage drift, not just LLM stochasticity). |
| G1.5 — Wall budget | ~11 hours total LLM-bound; can be split across sessions. |
| G1.6 — Cost budget | ~$0.70 LLM total. Per-cell cap $0.15 enforced. |

### §6.2 — G2 — Statistical analysis

| Step | Detail |
| --- | --- |
| G2.1 — Per-cell aggregation | Compute mean / std / Student's t 95% CI for GLR / Bypass / Per-BP-Leak. Write to `matrix_n5.json:cells[*].samples_summary`. |
| G2.2 — Within-encoder paired t-tests | 4 tests (MiniLM, mpnet, bge-large, FinLang × 60-vs-90). Report t-statistic, df=4, p-value, Bonferroni-adjusted p (α'=0.0125), 95% CI on delta. |
| G2.3 — Cross-encoder ordering check | For each sample (1–5), verify MiniLM < mpnet < bge-large per-BP-leak ordering. Report robustness rate. |
| G2.4 — Honest reporting | If §7.1 claim "within-encoder corpus comparisons within stochastic band" is **refuted** by n=5 data (e.g., MiniLM × 60 vs × 90 GLR delta is statistically significant), surface as new finding for v10 §V. |
| G2.5 — Wall | ~45 min local Python compute. |
| G2.6 — Cost | $0 (local). |

### §6.3 — G3 — Paper claim integration

| Step | Detail |
| --- | --- |
| G3.1 — v10 §V draft update | Replace point-estimate GLR/Bypass/Per-BP-Leak in v10 §V text with mean ± CI notation. |
| G3.2 — §7.1 claim validation | Confirm or refute "within stochastic band" claim using n=5 paired t-test results. Document either way. |
| G3.3 — Cross-encoder ordering claim | Strengthen v10 §V (§5.1 in Phase 1.F docs) ordering claim with empirical robustness rate. |
| G3.4 — New findings surface | If unexpected patterns emerge (e.g., Cell 6 bge-large × 90 has unusually high stochastic variance), draft candidate S15+ findings for user ratification. |
| G3.5 — Update `PHASE_1E_RESULTS.md` §11 paper-mapping if needed | Reflect Phase 1.G integration into paper §VII Limitations. |
| G3.6 — Wall | ~1 h authoring. |
| G3.7 — Cost | $0. |

### §6.4 — G4 — Phase 1.G close

| Step | Detail |
| --- | --- |
| G4.1 — `PHASE_1G_RESULTS.md` write-up | Mirror Phase 1.F RESULTS format. Sections: §1 close summary, §2 scope, §3 methodology, §4 results (per-cell aggregates), §5 statistical tests, §6 cross-encoder ordering, §7 limitations + future work, §8 paper §V draft update, §9 reproducibility provenance, §10 cost analysis. |
| G4.2 — Memory persistence | `project_phase1g_close.md` + `MEMORY.md` index update. |
| G4.3 — Commit-prep | Suggest commit message + files to stage for user manual commit + push. |
| G4.4 — Wall | ~1 h. |
| G4.5 — Cost | $0. |

### §6.5 — Multi-session execution plan

Phase 1.G can be split across 2 sessions:
- **Session A (long compute):** G1 sample-runs (~11 h LLM wall, ~$0.70 LLM). Can be background-executed overnight if user prefers.
- **Session B (analysis + close):** G2 + G3 + G4 (~3 h, $0).

Alternatively single session ~14h if user prefers continuous run.

---

## §7 — Risk Assessment

### §7.1 — Highest-risk scenarios

| ID | Risk | Likelihood | Severity | Mitigation |
| --- | --- | --- | --- | --- |
| RG1 | Cost runaway (LLM API token usage exceeds estimate) | Low | Medium | Per-cell $0.15 cap enforced; STOP-AND-DISCLOSE on exceed |
| RG2 | LLM API failures / rate limits during 4-sample-pass | Medium | Low | Retry policy: 3 retries with exponential backoff per call; if cell-level failure persists, save partial progress and resume next session |
| RG3 | Cell 6 wall outlier dominates (1.86h × 4 = 7.4h) | Certain (deterministic from Phase 1.F) | Low | Accept; budget already accounts for it; possible parallel execution of cells in future v11 |
| RG4 | Stochastic ULR > 0% (would invalidate Phase 1.F §4.2 deterministic claim) | Very low | High | STOP-AND-DISCLOSE; rule-based redaction expected deterministic; non-zero ULR would surface a Phase 1.F regression |
| RG5 | n=5 statistical power insufficient for paper claims | Medium | Low | t-CI honest reporting; if CIs too wide for §V claim support, escalate to n=10 in v11 (not this phase) |
| RG6 | §7.1 "within stochastic band" claim refuted by data | Medium | Low (positive finding) | Document as paper-grade observation; potentially S15 candidate |
| RG7 | Phase 1.F sample-1 (007c460) corrupted or unreproducible | Very low | High | Sample-1 is committed JSON; immutable. If discrepancy found, revert to re-running n=5 fresh (cost: $0.88 instead of $0.70). |
| RG8 | Cross-encoder ordering not preserved on any sample | Low | Medium | Surface as paper finding (would refute §5.1 ordering claim); honest reporting per established Phase 1.E unified Option B philosophy |

### §7.2 — Stop-and-disclose triggers

Immediate user notification + halt G1 execution if:

1. Any cell exceeds $0.15 cost cap (RG1).
2. Any sample produces ULR > 0% (RG4).
3. Cumulative Phase 1.G cost exceeds $0.90 (90% of phase cap; pre-emptive halt).
4. LLM API persistent failure across >3 retries on same cell (RG2).
5. Phase 1.F sample-1 reproducibility check fails (RG7).
6. Any new observation surfaces that contradicts V2 plan or Phase
   1.F documented findings.

### §7.3 — V2.5 plan-revision triggers (analog to Phase 1.E precedent)

Per Phase 1.E E1.6 RESOLVED Option B philosophy: document
deviations rather than retroactively refit. Phase 1.G plan-revision
candidates would arise if:

- Within-encoder paired t-test refutes "stochastic band" claim → v10 §V claim revised honestly (not plan revision).
- Cross-encoder ordering breaks on some samples → v10 §V claim revised.
- Cost overrun → would trigger v11 budget revision, not v10.

No PENDING blocks are pre-loaded for Phase 1.G; emerging issues
follow Phase 1.E S13/S14 precedent (surface during G2 analysis,
ratify in G3, finalize in G4).

---

## §8 — Cost Budget

### §8.1 — LLM cost forecast

| Component | Cost | Source |
| --- | --- | --- |
| Phase 1.F single-run baseline (sample 1) | $0.1756 | already incurred (007c460) |
| Phase 1.G additional samples (4 × 8 cells) | $0.7024 | this phase |
| Total Phase 1.F + 1.G (n=5) | **$0.8780** | combined |
| Phase 1.G phase cap | **$1.00** | 70% utilization at forecast |
| Per-cell cost cap | **$0.15** | safety margin over $0.10 expected |

Per-sample-pass cost estimate (across 8 cells): $0.1756. Multi-sample
re-run costs scale linearly (no API rate-card discount).

### §8.2 — Wall time forecast

| Component | Wall |
| --- | --- |
| Single sample-pass (8 cells, Cell 6 dominates) | ~2.75 hours |
| Cell 6 alone per pass | ~1.86 hours |
| 4 additional sample-passes (G1) | ~11 hours |
| G2 statistical analysis | ~45 min |
| G3 paper claim integration | ~1 hour |
| G4 close-out (RESULTS doc + memory + commit-prep) | ~1 hour |
| **Total Phase 1.G** | **~14 hours** |

V2 §11.1 #2 estimated "~6 hr wall" but did not itemize G2-G4
analysis; revised total ~14 hours reflects full sub-phase scope.

### §8.3 — Cost-tracking artifact

Per-cell cost tracked in `eval/results/phase1_G/cell_<N>/sample_<i>.json:cost_usd`.
Aggregated `cost_summary` in `matrix_n5.json`. Cost overrun
monitoring during G1 driven by Python script reading running
totals after each cell + sample completion.

---

## §9 — Reproducibility Provenance

### §9.1 — Pinned components

| Component | Pin | Source |
| --- | --- | --- |
| Defender LLM | `gpt-4o-mini-2024-07-18` | `core/config_loader.py:PINNED_OPENAI_MODEL` |
| Phase 1.F sample-1 outputs | Commit `007c460` (immutable; cited in `matrix_n5.json` provenance) | `eval/results/phase1_F/m4_matrix.json` |
| Encoder FAISS indexes | `eval/results/phase1_F/build_log.json` (M2 cached / built; 4 encoders × 2 corpora = 8 cells) | Phase 1.F M2 |
| Defender gate params | base=0.75, strict=0.45, hard=0.70 leak, soft=0.60 leak, cascade k=2 | Phase 1.F §3.3 + v9-canonical |
| Per-cell calibrated `sensitive_threshold` | Phase 1.F M3.5 calibration outputs (per-cell column in §4 table above) | Phase 1.F M3.5 |
| Adversarial corpus | `data/eval/full_adversarial_corpus.jsonl` (271 prompts, fixed) | Phase 1.F §3.3 |

### §9.2 — Provenance cross-reference

Phase 1.G artifacts cite:
- Phase 1.F M4 results: `eval/results/phase1_F/m4_matrix.json`
- Phase 1.F build log: `eval/results/phase1_F/build_log.json`
- Phase 1.F commit hash: `007c460` (committed 2026-05-10)
- V2 plan reference: `PHASE_1E_PLAN_V2.md` §13 (line 900)
- Phase 1.G specification: `PHASE_1F_RESULTS.md` §11.1 #2 (lines 986-995)

---

## §10 — Sub-phase Timeline (revised for n=5)

| Sub-phase | Wall | Cost | Deliverables |
| --- | --- | --- | --- |
| G1 — Multi-sample re-run | ~11 h | ~$0.70 LLM | 32 per-sample JSON files; per-cell incremental cost tracking |
| G2 — Statistical analysis | ~45 min | $0 | `matrix_n5.json` with aggregates + paired t-tests + ordering check |
| G3 — Paper claim integration | ~1 h | $0 | Updated v10 §V draft; validate/refute §7.1 claim; surface S15+ candidates |
| G4 — Phase 1.G close | ~1 h | $0 | `PHASE_1G_RESULTS.md`; memory persistence; commit-prep |
| **TOTAL** | **~14 h** | **~$0.70 LLM** | |

### §10.1 — Multi-session execution split

| Session | Sub-phases | Wall | LLM cost |
| --- | --- | --- | --- |
| Session A | G1 only (can run background overnight) | ~11 h | ~$0.70 |
| Session B | G2 + G3 + G4 | ~3 h | $0 |

Alternative single-session: ~14 h continuous (likely impractical
for single user-presence session).

---

## §11 — Success Criteria

PASS gate (Phase 1.G OFFICIAL CLOSE):

| # | Criterion | Verification |
| --- | --- | --- |
| 1 | All 8 cells × 4 additional samples completed | 32 `sample_<i>.json` files exist; ULR=0% verified per sample |
| 2 | Per-cell statistics computed | `matrix_n5.json:cells[*].samples_summary` populated with mean/std/CI |
| 3 | 4 within-encoder paired t-tests reported | `matrix_n5.json:within_encoder_paired_tests` (4 entries with t/p/CI) |
| 4 | Cross-encoder ordering verified | `matrix_n5.json:cross_encoder_ordering_check` populated with robustness rate |
| 5 | §7.1 "stochastic band" claim resolved | Either confirmed or refuted with statistical evidence |
| 6 | v10 §V draft updated with mean ± CI notation | Text changes ready for paper-rewrite session |
| 7 | `PHASE_1G_RESULTS.md` written | Mirrors Phase 1.F RESULTS format; reviewer-grade |
| 8 | Phase 1.G LLM cost ≤ $1.00 phase cap | `cost_summary:phase_1g_additional_cost_usd` ≤ 1.00 |
| 9 | Memory persistence + MEMORY.md index update | `project_phase1g_close.md` written |
| 10 | Commit-prep ready for user manual execution | Suggested commit message + file list in §8 of `PHASE_1G_RESULTS.md` |

---

## §12 — Findings Framework (forward-looking)

### §12.1 — DOCUMENTED_FINDINGS namespace

Phase 1.G findings extend the same S-numbered namespace as Phase
1.E (S1–S14 at Phase 1.E close + 2 RESOLVED V2.5 decisions).
Continuation: **S15, S16, …** for Phase 1.G discoveries.

Anticipated finding candidates (to be ratified during G2/G3 if
data supports):

| Candidate | Expected source |
| --- | --- |
| **S15** — Cross-encoder ordering robustness | G2 ordering check (e.g., "ordering preserved 5/5 samples" or "preserved on 4/5 samples") |
| **S16** — Within-encoder stochastic-band validation | G2 paired t-test (e.g., "MiniLM × 60 vs × 90 GLR delta p=0.X, statistically [significant/not significant]") |
| **S17+** — Unexpected statistical patterns | If data reveals e.g. Cell 6 anomalous variance |

### §12.2 — PENDING decisions framework

No PENDING blocks pre-loaded for Phase 1.G. Phase 1.E pattern
(introduce PENDING_V2_5_* blocks for deferred-decision items)
will be applied symmetrically if any unresolved questions emerge
during G2/G3 analysis. Resolution at Phase 1.G close or earlier.

### §12.3 — Cross-phase finding integration

Phase 1.G findings will be propagated to:
- `scripts/validate_hard_negatives.py:DOCUMENTED_FINDINGS` (if
  cross-phase relevance, e.g., S15 ordering robustness ties to
  Phase 1.E S11 Cat D/E cross-encoder analysis).
- v10 paper §V (per Phase 1.E §11 paper-mapping).
- Master `PHASE_1E_RESULTS.md` if §11 mapping needs update post-G3.

---

## §13 — v11 Future Work Boundaries

Items explicitly OUT of Phase 1.G scope, deferred to v11 or later:

| Item | Rationale |
| --- | --- |
| Higher-n protocols (n=10, n=20) | n=5 sufficient for paper-grade Student's t-CI claims at $0.70 budget. Higher n improves CI tightness but doubles+ cost; v11 if reviewer requests. |
| Cross-model stochasticity comparison (GPT-4o vs gpt-4o-mini drift profiles) | Outside V2 §13 + §11.1 #2 scope. Could be Phase 1.J research direction. |
| Bayesian posterior framework | Student's t-CI at n=5 is adequate for v10 paper-grade claims; Bayesian framework adds complexity without proportional clarity gain. v11 if reviewer requests. |
| Per-prompt variance analysis | n=5 enables per-cell aggregate stats only; per-prompt-id variance would require recording prompt-level outcomes per sample. Could be added in v11 if reviewer requests granular forensics. |
| Adaptive attacker integration with multi-sample defender | Adaptive attacker (per `PLAN.md` line 150) is unscheduled; possible Phase 1.I if reviewer feedback emerges post-v10 draft. Phase 1.G's n=5 defender data would feed in if so. |
| Phase 1.H OpenAI text-embedding-3 integration | Separate phase per V2 §13 line 901 + Phase 1.F §11.1 #3. |

---

## §14 — Plan Status / Approval

**Plan version:** V1 (this document).
**Plan status:** **DESIGN RATIFIED 2026-05-24** — all 7 design
dimensions (D1–D7) + G1–G4 sub-phase sequencing approved by user
2026-05-24. Implementation deferred to subsequent session(s) per
multi-session execution plan §10.1.
**Plan cost:** $0 LLM, $0 dependencies, 0 git operations.
**Plan output:** this document.

| Design Item | Ruling | Rationale |
| --- | --- | --- |
| D1 — Sample count n | **5** | §7.1 explicit example; n=3 t-CI too wide to distinguish Cell-1 +0.36pp drift from noise; n=5 t-CI gives ±0.28pp resolution at σ=0.1; cost delta $0.35 trivial for paper-grade claims |
| D2 — Random seed | **No seed (natural stochasticity)** | Stochasticity IS the measurand; OpenAI seed is best-effort, not guaranteed reproducible |
| D3 — Cells in scope | **All 8 cells** | V2 §11.1 #2 spec |
| D4 — LLM model pin | **`gpt-4o-mini-2024-07-18` same as Phase 1.F** | Cross-phase comparability; new model would render stochasticity vs model-shift confounded |
| D5 — Statistical framework | **Mean ± std + Student's t 95% CI + paired t-test** | §11.1 #2 "mean ± std with confidence bounds"; t-CI honest at n=5; paired t-test directly addresses §7.1 within-encoder claim |
| D6 — Output schema | **Phase 1.F immutable + Phase 1.G extension treating Phase 1.F as sample-1** | Preserves 007c460 immutability; Phase 1.G is strict additive extension |
| D7 — Cost budget | **$0.70 LLM forecast / $1.00 phase cap / $0.15 per-cell cap** | $0.70 = 4 × $0.1756; phase cap 70% utilization; per-cell cap = 5.7× worst-cell-observed for retry safety margin |

---

## §15 — Changelog (V2 → V2.5)

### V2.5 (2026-05-25): §3.4 multiplicity correction revised

**Change.** §3.4 paired t-test multiplicity correction
changed from plain Bonferroni (α' = 0.0125 for all tests)
to **Holm-Bonferroni** (sequential step-down adjustment).

**Rationale.** At n = 5 samples per cell, plain Bonferroni's
uniform α' = 0.0125 is overly conservative for paired tests
with low-to-moderate correlation. Holm-Bonferroni preserves
family-wise error control at α = 0.05 while allowing more
statistical power when some effects are real. Particularly
relevant for the MiniLM 60-vs-90 GLR comparison (+0.37 pp
single-sample delta, close to the stochastic band) where
plain Bonferroni's conservatism risks Type II error
(failure to reject when an effect truly exists).

**Impact on G1 production.** None. G1 production runs the
multi-sample protocol (sample collection); multiplicity
correction is applied in G2 (statistical analysis), which
has not started.

**Impact on §V.B paper draft.** None — `paper_drafts/v10/
v10_paper_section_V_B_phase1G_draft.md` §V.B.2.4 already
specifies Holm-Bonferroni; this V2.5 revision aligns the
plan with the paper draft.

**Discipline note.** This revision follows the Phase 1.E
"document deviations, don't refit" philosophy: where the
plan and paper diverge, the V2 plan is revised transparently
(this changelog) rather than silently refit. The change is
applied as an *errata* — the original ratification (D5,
2026-05-24) was Bonferroni; the V2.5 revision (2026-05-25)
moves to Holm-Bonferroni with the rationale above. Both
revisions are visible in the document history.

**Authority for change.** User ratification 2026-05-25
(Decision (β)). No new design dimension introduced; only the
multiplicity-correction algorithm narrowed from "Bonferroni
family" to the Holm step-down variant.

---

## §16 — Related Documents

- **Predecessor V2 plan:** `PHASE_1E_PLAN_V2.md` (ratified 2026-05-11).
- **Phase 1.F authoritative:** `PHASE_1F_RESULTS.md` §3.3 (8-cell design), §4.1 (master matrix), §7.1 (Cell-1 drift), §11.1 #2 (Phase 1.G spec).
- **Top-level plan reference:** `PLAN.md` (overall project roadmap).
- **Phase 1.E close-out (master):** `PHASE_1E_RESULTS.md` (Phase 1.E full logical close; informs §11 paper-mapping integration with Phase 1.G).
- **Phase 1.E errata note:** `PHASE_1E_RESULTS.md` §14 + `PHASE_1E_E1_6_RESULTS.md` §11 (correcting Phase 1.G scope to stochasticity probe per V2 + Phase 1.F authoritative).
- **v10 paper §V.B draft:** `paper_drafts/v10/v10_paper_section_V_B_phase1G_draft.md` §V.B.2.4 (Holm-Bonferroni statistical framework; aligned with §3.4 + §15 V2.5 revision).

---

*End of `PHASE_1G_PLAN.md`. Design ratified 2026-05-24; D1–D7
+ G1–G4 approved. Implementation in subsequent session(s) per
§10.1 multi-session execution plan. Standing by for user manual
commit of this plan doc + Session A kickoff for G1 multi-sample
re-run.*
