# v10 Paper §V.B — Phase 1.G Multi-Sample Stochasticity Treatment

> **Draft status:** v0.1 working draft, 2026-05-24. Markdown
> source for v10 paper §V.B. LaTeX conversion deferred to
> final-polish pass.
>
> **[PLACEHOLDER] markers** indicate statistical values that
> will be populated after Phase 1.G G2 statistical analysis
> completes. Structure, methodology, framing, and findings
> framework are paper-grade as of v0.1; numerical content is
> deferred to G2.
>
> **Section scope:** v10 §V (Methodology Validation and
> Statistical Treatment) subsection B. Addresses the LLM
> stochasticity that affects Phase 1.F point-estimate metrics
> by re-running the eight cells with n = 5 samples each and
> converting GLR / Bypass / Per-BP-Leak to mean ± Student's
> t 95% confidence intervals.
>
> **Relation to §V.A:** §V.A reports Phase 1.F results as
> point estimates with a noted +0.36pp Cell-1 GLR drift. §V.B
> establishes the statistical bounds within which §V.A's
> inter-cell comparisons are statistically distinguishable
> from LLM stochasticity. The combined §V.A + §V.B story is
> v10's central methodology contribution: encoder ablation
> with empirically-bounded statistical claims.

---

## §V.B.1 — Motivation: Why Multi-Sample is Required

### §V.B.1.1 — The Cell-1 drift observation

Phase 1.F documented a discrepancy between the v9 paper's
published Cell-1 (MiniLM × 60) GLR of 1.85% and the v10
Phase 1.F Cell-1 GLR of 2.21% — a **+0.36 percentage-point
drift** despite byte-identical encoder pin, FAISS index, and
defender LLM model (gpt-4o-mini-2024-07-18). The Bypass% and
ULR% reproduce exactly (47.60% and 0.00% respectively); only
the GLR shifts.

The root cause is identified in [REF: Phase 1.F §7.1]: the
defender LLM is **non-deterministic at default temperature**
(temperature = 1.0). The same adversarial prompt produces
slightly different raw outputs across independent calls, and
in approximately 1 out of 271 cases the outputs differ in
whether they contain a secret token (raw-output leak). This
1 / 271 difference manifests as the +0.36pp GLR drift.

**Implication.** Every per-cell metric in §V.A.4 is a
*point estimate* of an underlying stochastic distribution.
Inter-cell differences smaller than the within-cell standard
deviation are **not statistically distinguishable** from LLM
stochasticity.

### §V.B.1.2 — Effect size vs stochastic band

Phase 1.F's headline findings (§V.A.5 F1, F2, F3) are
**effect-size claims**, not within-band claims:

- F1 (ULR = 0% across cells): the spread is **11.44 pp** (0%
  vs cell maximum GLR 11.44%). This is **~32×** larger than
  the observed ~0.36pp stochastic drift.
- F2 (encoder-strength leakage trade-off): the Per-BP-Leak%
  spread is **20.6 pp** (4.7% MiniLM × 60 vs 25.3% bge-large
  × 60). Approximately **~57×** larger than stochastic drift.
- F3 (FinLang paradox): the Bypass% spread between FinLang
  and MiniLM is **6.64 pp** (54.24% vs 47.60% on the 60-corpus).
  Approximately **~18×** larger than stochastic drift.

These effect sizes are large enough that they **should
survive** the stochasticity check — but this expectation
must be empirically verified, not assumed. §V.B provides the
verification.

### §V.B.1.3 — Within-encoder corpus deltas: the close-call cases

Smaller-effect comparisons in §V.A.4 are within the
stochastic band:

- MiniLM × 60 GLR (2.21%) vs MiniLM × 90 GLR (2.58%) =
  +0.37 pp delta. Approximately **equal to** the
  Cell-1 drift magnitude.
- mpnet × 60 Per-BP-Leak (19.0%) vs mpnet × 90 Per-BP-Leak
  (10.4%) = -8.6 pp delta. **Much larger** than stochastic
  band but a sign-flip exists for further investigation.
- FinLang × 60 GLR (3.32%) vs FinLang × 90 GLR (6.27%) =
  +2.95 pp delta. Likely outside stochastic band, but
  marginal.

**These close-call cases are precisely what §V.B's paired
t-tests resolve.** §V.B answers the question: *is the
within-encoder corpus-size effect statistically
significant, or is it within the LLM stochastic band?*

---

## §V.B.2 — Methodology: n = 5 Multi-Sample Protocol

### §V.B.2.1 — Sample-count rationale

Phase 1.G re-runs the eight cells from §V.A with n = 5
samples each. The sample count is selected based on the
required Student's t critical-value width:

| n | t_{0.025, n-1} | CI width factor (× σ/√n) | Cost (USD) |
| --- | --- | --- | --- |
| 3 | 4.30 | 4.30 × σ/√3 ≈ 2.48σ | $0.35 |
| **5** | **2.78** | **2.78 × σ/√5 ≈ 1.24σ** | **$0.70** |
| 10 | 2.26 | 2.26 × σ/√10 ≈ 0.71σ | $1.58 |

At n = 5, the 95% confidence interval has half-width
1.24σ. Assuming the empirical GLR standard deviation is on
the order of 0.1 percentage points (extrapolating from the
Cell-1 drift magnitude as a single-sample point estimate),
the per-cell 95% CI is approximately **±0.12 pp** at n = 5
versus **±0.25 pp** at n = 3.

This resolution is sufficient to distinguish the Cell-1
v9-to-v10 drift (+0.36 pp) from within-cell stochasticity,
but tight enough that within-encoder corpus deltas at the
+0.37 pp scale (MiniLM corpus delta) sit at the boundary
between "statistically distinguishable" and "within
stochastic band". §V.B.4 reports the precise outcomes.

### §V.B.2.2 — Pinned components

To ensure that observed variance is LLM stochasticity rather
than configuration drift, Phase 1.G fixes every
non-stochastic component identically to Phase 1.F:

- **Defender LLM:** `gpt-4o-mini-2024-07-18` (dated snapshot,
  PINNED_OPENAI_MODEL constant in `core/config_loader.py`).
- **Temperature:** 1.0 (default, OpenAI API).
- **Encoder revisions:** `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`
  (MiniLM) and corresponding pinned revisions for mpnet,
  bge-large, FinLang (PINNED_REVISIONS dict).
- **FAISS indexes:** SHA256-verified byte-identical to
  Phase 1.F build (`eval/results/phase1_F/build_log.json`).
- **Attack corpus:** 271-prompt
  `data/attack_prompts_expanded.jsonl` (identical to Phase
  1.F M4 input).
- **All gate parameters:** $\theta_{\text{cell}}$ per
  §V.A.3.2; base 0.75; strict 0.45; hard 0.70 leak score;
  soft 0.60 leak score; cascade k = 2.

The only deliberate variable is the LLM call number per
prompt: **sample 1 = Phase 1.F output (committed at 007c460),
samples 2–5 = Phase 1.G new outputs**.

### §V.B.2.3 — Sample independence: no random seed

The OpenAI API does not provide a deterministic seed
parameter (the `seed` parameter is best-effort and not
guaranteed reproducible). Phase 1.G makes no attempt to
control random seed — natural LLM stochasticity is the
**measurand**, not a confound to eliminate.

A reviewer asking *"are your n = 5 samples truly
independent?"* is answered by: yes, each sample is an
independent OpenAI API call at temperature 1.0 with no seed
control; differences across samples reflect the LLM's
intrinsic stochasticity.

A reviewer asking *"can the results be reproduced?"* is
answered by: the *methodology* is reproducible (any researcher
can run n = 5 samples following the same protocol); the
*specific numerical values* are reproducible up to natural
stochastic variance (which is precisely what §V.B reports).

### §V.B.2.4 — Statistical framework

For each of the eight cells × {Bypass%, GLR%, Per-BP-Leak%}
metric pairs (24 cell-metric combinations), §V.B reports:

1. **Mean** $\bar{x}$ across n = 5 samples.
2. **Sample standard deviation** $s$ with Bessel's correction
   (denominator n - 1).
3. **Student's t 95% confidence interval**:
   $\bar{x} \pm t_{0.025, 4} \cdot s / \sqrt{5}$
   where $t_{0.025, 4} = 2.776$.

For **within-encoder corpus delta** tests (4 paired tests:
MiniLM × 60 vs × 90; mpnet × 60 vs × 90; bge-large × 60 vs
× 90; FinLang × 60 vs × 90), §V.B reports paired t-test
results with Holm-Bonferroni adjustment for the 4-test
multiplicity (more powerful than Bonferroni for low
correlated tests):

$$
H_0: \mu_{60} = \mu_{90}, \quad H_a: \mu_{60} \neq \mu_{90}
$$

with paired-test statistic computed on the matched
sample-id pairs (i.e., $\bar{d}_{60-90, i}$ across i = 1, ..., 5
samples).

The choice of Holm-Bonferroni over plain Bonferroni or
bootstrap CI is documented as a methodological judgment: at
n = 5, bootstrap CIs are fragile (limited resampling space);
Holm-Bonferroni preserves family-wise error control while
allowing more power than plain Bonferroni when paired tests
are loosely correlated.

[FOOTNOTE: The original `PHASE_1G_PLAN.md` D5 ratification
(2026-05-24) specified plain Bonferroni; a V2.5 errata revision
(2026-05-25) narrowed this to Holm-Bonferroni for the rationale
above. See `PHASE_1G_PLAN.md` §3.4 (revised) and §15 changelog
for the plan-side documentation; the methodology applied at
G2 statistical analysis is the Holm step-down algorithm
described above.]

---

## §V.B.3 — Cross-Encoder Ordering Robustness

A separate question §V.B answers is whether the §V.A.5 F2
encoder-strength leakage ordering — MiniLM < FinLang ≈
mpnet < bge-large on Per-BP-Leak% — **holds across all n
samples** or whether the relative order flips between samples
within the stochastic band.

The methodology is straightforward: for each sample 1, 2, 3,
4, 5, compute the encoder-Per-BP-Leak ranking; check that
the MiniLM-rank is consistently the lowest and the bge-large
rank is consistently the highest. **Cross-sample rank
flipping** would weaken F2's claim that the encoder ordering
is robust.

The same check applies to F1 (ULR = 0%): if any cell × any
sample produces non-zero ULR, F1's "0% across all cells"
claim is refuted at the per-sample level (though the
aggregate-mean ULR may remain 0%).

---

## §V.B.4 — Results: Multi-Sample Aggregates [PLACEHOLDER]

> **[G2 PENDING]** This section is structured to be filled
> with concrete numerical results once Phase 1.G G2
> (statistical analysis) completes. The structure is
> paper-ready; numerical content follows the same shape as
> the §V.A.4 master matrix table extended with mean / std /
> CI columns.

### §V.B.4.1 — Per-cell aggregate metrics (n = 5)

| Cell | $\bar{\text{Bypass}}$ ± CI | $\bar{\text{GLR}}$ ± CI | $\bar{\text{Per-BP-Leak}}$ ± CI | $\bar{\text{ULR}}$ ± CI |
| --- | --- | --- | --- | --- |
| 1 (MiniLM × 60) | [TBD] ± [TBD] | [TBD] ± [TBD] | [TBD] ± [TBD] | [TBD] ± [TBD] |
| 2 (MiniLM × 90) | [TBD] | [TBD] | [TBD] | [TBD] |
| 3 (mpnet × 60) | [TBD] | [TBD] | [TBD] | [TBD] |
| 4 (mpnet × 90) | [TBD] | [TBD] | [TBD] | [TBD] |
| 5 (bge-large × 60) | [TBD] | [TBD] | [TBD] | [TBD] |
| 6 (bge-large × 90) | [TBD] | [TBD] | [TBD] | [TBD] |
| 7 (FinLang × 60) | [TBD] | [TBD] | [TBD] | [TBD] |
| 8 (FinLang × 90) | [TBD] | [TBD] | [TBD] | [TBD] |

[FOOTNOTE: All confidence intervals are Student's t 95% CI;
n = 5 samples per cell. Phase 1.F's sample-1 baseline is
included as one of the five samples per cell, ensuring
upward compatibility with §V.A.4 numbers.]

### §V.B.4.2 — Within-encoder corpus delta paired t-tests

| Test | Mean delta | t-stat | p-value | Holm-adjusted | Significant @ 0.05 |
| --- | --- | --- | --- | --- | --- |
| MiniLM × 60 vs × 90 (GLR) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| mpnet × 60 vs × 90 (GLR) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| bge-large × 60 vs × 90 (GLR) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| FinLang × 60 vs × 90 (GLR) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### §V.B.4.3 — Cross-encoder ordering robustness

| Sample | MiniLM rank | FinLang rank | mpnet rank | bge-large rank | Order matches F2? |
| --- | --- | --- | --- | --- | --- |
| 1 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 2 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 3 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 4 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| 5 | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Aggregate | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

---

## §V.B.5 — Findings [PLACEHOLDER FOR S15+]

> **[G3 PENDING]** Phase 1.G G3 (paper claim integration) will
> surface any new findings (candidate S15+) arising from
> Phase 1.G n = 5 data. Expected finding categories:

### §V.B.5.1 — Candidate S15: §V.A.5 F1 (ULR = 0) at n = 5 aggregate

**Expected outcome.** ULR mean across n = 5 samples is 0.00%
for all eight cells, with standard deviation 0.00pp (no
sample produces non-zero ULR). This **strengthens** F1 from
single-sample point estimate to multi-sample empirical
confirmation.

**If observed differently:** [PLACEHOLDER] If any cell × any
sample produces non-zero ULR, F1 is refuted at the per-sample
level and Phase 1.G surfaces a new candidate finding about
ULR stochasticity — itself paper-grade.

### §V.B.5.2 — Candidate S16: §V.A.5 F2 (encoder ordering) robustness

**Expected outcome.** Cross-encoder ordering (MiniLM <
FinLang ≈ mpnet < bge-large on Per-BP-Leak%) holds in 5 / 5
samples for both 60- and 90-corpus configurations. This
**confirms** F2 as effect-size-dominated.

**If observed differently:** Mid-rank flips (FinLang vs
mpnet) are possible within the stochastic band; bottom or
top rank changes (MiniLM no longer lowest, or bge-large no
longer highest) would weaken F2.

### §V.B.5.3 — Candidate S17: Within-encoder corpus delta significance

**Expected outcome — MiniLM 60 vs 90 GLR.** With observed
delta +0.37 pp (single-sample) and expected within-cell std
~0.1 pp, the paired t-test should detect significance with
moderate p-value (~0.05 region). This is the precise
close-call case §V.B is designed to resolve.

**If observed as significant:** §V.A's claim that "60 → 90
corpus expansion affects MiniLM Cell GLR" is upheld at p <
0.05.

**If observed as not significant:** §V.A should soften this
claim — the corpus-size effect on MiniLM is within the
stochastic band, and §V.A.5 F1's strict "by cell" framing
should pivot to "by encoder family".

### §V.B.5.4 — Candidate S18: Wall-time variance characterization

**Expected outcome.** Wall-time across n = 5 samples shows
non-trivial variance (~20-30% within cell), with Cell 6
(bge-large × 90) showing the largest absolute variance
(1.86h to ~2.4h range). This is consistent with system-load
effects, not algorithm-stochasticity, and is reported as a
**reproducibility note** rather than a paper finding.

---

## §V.B.6 — Sample-Level Stochasticity Audit

Phase 1.G preserves per-sample outputs for forensic review:

```
eval/results/phase1_G/
  minilm_60entry/
    sample_1/  (= Phase 1.F 007c460 reference)
    sample_2/  (= Phase 1.G new)
    sample_3/  (= Phase 1.G new)
    sample_4/  (= Phase 1.G new)
    sample_5/  (= Phase 1.G new)
  ...
```

A reviewer can inspect any individual sample's
`bypass_cases.jsonl` to verify which 271-prompts produced
GLR or Bypass differences between samples. This is the
**audit layer** complementing the §V.B.4 aggregate
statistics: a skeptical reviewer can confirm sample-to-sample
differences are not aggregation artifacts.

---

## §V.B.7 — Reproducibility Provenance

Phase 1.G outputs are committed at git revision [TBD post-G4]
and treated as **immutable** in subsequent work. The
reproducibility artifacts are:

- **Driver script:** `scripts/phase1G_multi_sample.py` (~490 LOC,
  subprocess-based orchestrator with resumability and
  cost-cap enforcement).
- **State ledger:** `eval/results/phase1_G/run_state.json`
  (atomic-write, JSON, tracks completed samples + cumulative
  cost).
- **Run log:** `eval/results/phase1_G/run_log.jsonl`
  (append-only event log: sample_start, sample_complete,
  stop_and_disclose, subprocess_failure, driver_complete).
- **Per-sample outputs:** 32 sample directories (8 cells ×
  4 additional samples beyond Phase 1.F sample-1).
- **Aggregate matrix:** `eval/results/phase1_G/matrix_n5.json`
  (per-cell mean, std, CI; paired t-test results;
  cross-encoder ordering).

A reviewer can re-execute Phase 1.G end-to-end by:

```bash
python3 scripts/phase1G_multi_sample.py
```

The driver auto-detects existing samples (Phase 1.F's
sample-1 + any prior Phase 1.G runs), so partial restarts
resume from the last completed sample without re-spending
LLM cost on already-completed work.

Cost: **$0.70 LLM** ($0.18 × 4 additional repeats × 8 cells).
Total Phase 1.F + Phase 1.G LLM cost: **$0.88** ($0.18 +
$0.70).

---

## §V.B.8 — Limitations

### §V.B.8.1 — n = 5 is small-sample

The Student's t critical value at 4 degrees of freedom is
2.776, which produces relatively wide confidence intervals
even for low-variance metrics. A larger n (e.g., n = 10 or
n = 20) would tighten the CIs proportionally to 1 / √n.

v11 future work: scale to n = 10 with Bonferroni-adjusted
joint testing across all encoders × all metrics.

### §V.B.8.2 — Defender-LLM-only stochasticity

Phase 1.G measures stochasticity introduced by the **defender
LLM only** (the LLM consuming attack prompts during the
SentinelFlow pipeline). It does **not** measure:

- Encoder stochasticity (encoders are deterministic on
  identical input with byte-identical weights).
- Index stochasticity (FAISS is deterministic).
- LLM-generation stochasticity for hard-negative corpus
  (Phase 1.E E1.2; the GPT-5-mini calls used for hard-neg
  construction are separately characterized in §V.C.3.1).

If future work introduces a stochastic component beyond the
defender LLM, the §V.B framework extends naturally with new
n = 5 multi-sample protocols for the new component.

### §V.B.8.3 — Single defender-LLM model

Phase 1.G uses **only** `gpt-4o-mini-2024-07-18` as the
defender LLM. Cross-model robustness (e.g., GPT-4o, Claude,
Llama-3) is **out of scope** for v10 and is deferred to
future work. The §V.B framework can be replicated for any
defender LLM by replacing the PINNED_OPENAI_MODEL constant
and re-running.

---

## §V.B.9 — Connection to §V.A and §V.C

§V.B provides the **statistical bounding layer** for §V.A's
encoder ablation findings:

- F1 (ULR = 0%): expected to hold at n = 5 aggregate; §V.B.5.1.
- F2 (encoder ordering): expected to hold across all 5
  samples; §V.B.5.2.
- F3 (FinLang paradox): expected to hold at effect-size
  level; tested against stochastic band per §V.B.4.3.

§V.B does **not** apply to §V.C's hard-negative
characterization findings (S1–S14). The §V.C findings are
**mechanism-level observations**, not effect-size measurements
requiring statistical confidence intervals (see §V.C.9).

The combined §V.A + §V.B + §V.C narrative is v10's central
methodology claim: **encoder ablation with
empirically-bounded statistical claims, hard-negative
characterization with mechanism-level findings**.

---

*End of `v10_paper_section_V_B_phase1G_draft.md` v0.1.
Numerical content (§V.B.4 master matrix, §V.B.5 findings) to
be filled after Phase 1.G G2 (statistical analysis) completes.*
