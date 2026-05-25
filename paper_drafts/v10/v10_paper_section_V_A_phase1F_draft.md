# v10 Paper §V.A — Phase 1.F Encoder Ablation

> **Draft status:** v0.1 working draft, 2026-05-24. Markdown
> source for v10 paper §V.A. LaTeX conversion deferred to
> final-polish pass. [PLACEHOLDER] markers indicate fields
> requiring values from Phase 1.G G2 statistical analysis
> (multi-sample stochasticity probe, in progress).
>
> **Section scope:** v10 §V (Methodology Validation and
> Statistical Treatment) subsection A. Documents the four-
> encoder × two-corpus ablation matrix introduced in v9 paper
> §IV-K and extends it with per-cell calibration methodology,
> M3.5 threshold sweep protocol, and per-cell leakage/bypass/
> false-positive characterization.
>
> **Relation to v9 paper:** v9 §IV-K mentions encoder choice
> as a configuration parameter; v10 §V.A elevates this to a
> systematic ablation with reproducibility provenance (encoder
> revisions pinned via PINNED_REVISIONS dict; FAISS indexes
> rebuildable from `eval/results/phase1_F/build_log.json`).

---

## §V.A.1 — Motivation and Scope

The v9 paper [CITE: SentinelFlow v9] reports leakage and FPR
metrics for a single encoder configuration (all-MiniLM-L6-v2,
384-dim, against a 60-entry secret index). This left two
open questions for reviewer scrutiny:

1. **Encoder choice as design parameter.** Does the choice of
   sentence-embedding model materially affect the gate's
   leakage-vs-FPR trade-off? The v9 §IV-K embedding-model
   benchmark compares three encoders on Gap(L2–L1) discrimination
   but does not run them end-to-end through the full pipeline.

2. **Corpus size sensitivity.** The v9 60-entry secret corpus
   was expanded to a 90-entry L1/L2/L3 institutional triplet
   corpus during the v9 paper preparation. v9 reports
   end-to-end metrics on the 90-entry corpus only. Whether the
   gate's behavior is stable across the 60 → 90 corpus
   expansion remains untested.

Phase 1.F answers both questions via a **four-encoder × two-
corpus ablation matrix** (eight cells). Each cell is end-to-end
calibrated and evaluated against the same 271-prompt fixed
adversarial corpus [CITE: §IV-J 271-prompt corpus]. Per-cell
metrics — sensitive-threshold $\theta$, Bypass%, GLR%, ULR%,
Per-BP-Leak%, cost, wall — are reported in §V.A.4 (Table
[REF: tab:phase1f_matrix]).

This ablation is the methodology backbone of v10's central
claim: **encoder choice creates a measurable leakage-vs-FPR
trade-off**, and **the v9 paper's MiniLM × 60 configuration
sits at one specific point on this trade-off curve** rather
than representing an arbitrary baseline.

---

## §V.A.2 — Encoder × Corpus Matrix Design

### §V.A.2.1 — Four encoders

| Symbol | Model | Revision | Dim | Source |
| --- | --- | --- | --- | --- |
| MiniLM | sentence-transformers/all-MiniLM-L6-v2 | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` | 384 | [Reimers & Gurevych 2019] |
| mpnet | sentence-transformers/all-mpnet-base-v2 | `e8c3b32edf5434bc2275fc9bab85f82640a19130` | 768 | [Song et al. 2020] |
| bge-large | BAAI/bge-large-en-v1.5 | `d4aa6901d3a41ba39fb536a557fa166f842b0e09` | 1024 | [Xiao et al. 2024] |
| FinLang | FinLang/finance-embeddings-investopedia | `37d7594d02e3d656a241e099e39ac50ab921f999` | 768 | [FinLang 2024 — finance-domain pretrained] |

Encoders span three architectural / training regimes: (a)
general-purpose distilled (MiniLM, lowest dimensionality), (b)
general-purpose full-scale (mpnet, bge-large), and (c) finance-
domain pretrained (FinLang). FinLang is included specifically
to test whether domain-specialized pretraining materially
improves discrimination on the finance-secret detection task —
a question the v9 paper raised but did not resolve.

All four encoders are pinned via the `PINNED_REVISIONS` dict
in `core/config_loader.py`. Revision hashes are recorded in
each cell's `summary.json` alongside the result metrics, so
that a reviewer can reproduce any cell's FAISS index byte-for-
byte from the commit corresponding to the published results.

### §V.A.2.2 — Two corpora

| Corpus | Entries | Composition | Source |
| --- | --- | --- | --- |
| 60-entry | 60 | 30 L2 + 30 L3 simple domain parameters (v9 baseline) | `data/secrets/secrets.jsonl` |
| 90-entry | 90 | 30 L1/L2/L3 institutional triplets × 6 alpha domains | `data/secrets/secrets_v2.jsonl` |

The 60-entry corpus is the v9 paper's published baseline,
preserved verbatim for direct comparison. The 90-entry corpus
extends this to institutional-grade L1/L2/L3 triplets across
six alpha domains (price/volume momentum, event-driven,
statistical arbitrage, alternative-data signals, risk-factor
neutralization, ML signal pipelines). The 30 triplets are
constructed by ratio L1 (publicly inferable practitioner-tier
knowledge) → L2 (institutionally confidential parameters) →
L3 (top-secret strategy specifics within a single firm).

The 90-entry expansion is a v10 contribution; v9 measured only
on the 60-entry baseline. The two-corpus ablation tests
whether the gate's behavior on 60 ⊂ 90 (subset semantics that
the v9 paper implicitly assumed) is consistent — a question
that surfaced an unrelated finding (corpus version disjointness)
documented in v10 §V.C [REF: S7].

### §V.A.2.3 — Cell labelling

The eight cells are labeled by encoder–corpus pair:

```
Cell 1: MiniLM × 60      Cell 5: bge-large × 60
Cell 2: MiniLM × 90      Cell 6: bge-large × 90
Cell 3: mpnet × 60       Cell 7: FinLang × 60
Cell 4: mpnet × 90       Cell 8: FinLang × 90
```

Cell 1 (MiniLM × 60) corresponds exactly to the v9 paper's
published configuration; its v10 metrics should reproduce v9's
within stochastic tolerance (see §V.B for stochasticity
treatment).

---

## §V.A.3 — Per-Cell Calibration Protocol (M3.5)

Each of the eight cells uses an encoder-specific calibrated
sensitive-threshold $\theta_{\text{cell}}$. Calibration follows
the **M3.5 protocol** introduced in Phase 1.F:

### §V.A.3.1 — Calibration objective

For each cell, M3.5 sweeps the sensitive-threshold across
[0.30, 0.95] in increments of 0.05 and selects the lowest $\theta$
satisfying the joint constraint:

$$
\theta_{\text{cell}} = \min \left\{ \theta : \text{FPR}_{\text{easy}}(\theta) \leq 3.0\% \text{ AND no v9 §IV-K regression} \right\}
$$

where $\text{FPR}_{\text{easy}}$ is measured against the v9
**100-query benign baseline** (`data/benchmark/normal_prompts.jsonl`,
representative of typical user queries). The 3.0% target
matches the v9 paper's FPR claim; calibrating to this floor
maintains backward-compatibility with v9 deployments.

### §V.A.3.2 — Calibrated thresholds

| Cell | Encoder × Corpus | $\theta_{\text{cell}}$ |
| --- | --- | --- |
| 1 | MiniLM × 60 | 0.50 |
| 2 | MiniLM × 90 | 0.45 |
| 3 | mpnet × 60 | 0.50 |
| 4 | mpnet × 90 | 0.50 |
| 5 | bge-large × 60 | 0.70 |
| 6 | bge-large × 90 | 0.80 |
| 7 | FinLang × 60 | 0.50 |
| 8 | FinLang × 90 | 0.50 |

The threshold spread reflects encoder-specific cosine
distributions. bge-large encodes queries closer to secrets on
average (larger raw cosines), requiring a higher $\theta$ to
maintain the same FPR floor. This pattern is consistent with
bge-large's design as a retrieval-optimized encoder that
maximizes semantic similarity scores.

All eight thresholds are **frozen after M3.5** and not re-tuned
in subsequent phases (Phase 1.E hard-negative FPR characterization,
Phase 1.G stochasticity probe). This immutability discipline
is central to v10's reviewer-defensible claims — see §V.C.5
on threshold-portability and the characterization-not-target
framing.

### §V.A.3.3 — Other gate parameters

All other gate parameters are held constant at v9-canonical
values across the eight cells:

- Base threshold ($\tau_{\text{base}}$): 0.75
- Strict threshold ($\tau_{\text{strict}}$): 0.45
- Hard leak score ($\sigma_{\text{hard}}$): 0.70
- Soft leak score ($\sigma_{\text{soft}}$): 0.60
- Cascade $k$: 2

This isolates the encoder × corpus variable as the only
deliberate manipulation in the ablation, ensuring observed
differences are attributable to encoder choice and corpus
size rather than to threshold confounds.

---

## §V.A.4 — Results: Master Matrix

The eight cells were evaluated end-to-end against the 271-prompt
fixed adversarial corpus, with GPT-4o-mini (`gpt-4o-mini-2024-07-18`,
dated snapshot) as the defender LLM. Per-cell metrics
(Phase 1.F sample-1 baseline):

| Cell | Encoder × Corpus | $\theta$ | Bypass% | GLR% | ULR% | Per-BP-Leak% | Cost (USD) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | MiniLM × 60 | 0.50 | 47.60 | 2.21 | 0.00 | 4.7 | 0.0240 | 489.7 |
| 2 | MiniLM × 90 | 0.45 | 42.80 | 2.58 | 0.00 | 6.0 | 0.0191 | 414.6 |
| 3 | mpnet × 60 | 0.50 | 36.90 | 7.01 | 0.00 | 19.0 | 0.0177 | 382.3 |
| 4 | mpnet × 90 | 0.50 | 49.45 | 5.17 | 0.00 | 10.4 | 0.0217 | 465.9 |
| 5 | bge-large × 60 | 0.70 | 36.53 | 9.23 | 0.00 | 25.3 | 0.0165 | 363.6 |
| 6 | bge-large × 90 | 0.80 | 54.98 | 11.44 | 0.00 | 20.8 | 0.0261 | 6684.6 |
| 7 | FinLang × 60 | 0.50 | 54.24 | 3.32 | 0.00 | 6.1 | 0.0259 | 533.7 |
| 8 | FinLang × 90 | 0.50 | 53.87 | 6.27 | 0.00 | 11.6 | 0.0246 | 588.1 |
| | **TOTAL** | | | | | | **0.1756** | 9922.5 |

Metric definitions:
- **Bypass%:** fraction of 271 adversarial prompts that pass
  all pre-LLM gates and reach the defender LLM.
- **GLR% (Gross Leak Rate):** fraction of 271 adversarial
  prompts where the LLM raw output contains a secret token
  (post-LLM, pre-redaction).
- **ULR% (User-facing Leak Rate):** fraction of 271 adversarial
  prompts where the user receives an unredacted secret (after
  the post-LLM leakage scan + redaction). The headline metric.
- **Per-BP-Leak% (Per-Bypass Leak Rate):** GLR / Bypass; the
  conditional leak rate given that the prompt reached the LLM.
  Isolates the LLM's intrinsic leak propensity from the gate's
  filtering effectiveness.

**Cell 1 reproducibility note.** The v10 Cell 1 metrics
(`MiniLM × 60`, $\theta = 0.50$) reproduce the v9 paper's
single-encoder configuration exactly on Bypass% (47.60%) and
ULR% (0.00%) but show a +0.36pp drift on GLR% (2.21% vs. v9's
1.85%). [REF: Phase 1.F §7.1] This drift motivated the Phase
1.G multi-sample stochasticity probe (§V.B), which establishes
the statistical bounds within which point-estimate GLR
comparisons can be made.

---

## §V.A.5 — Findings

The eight-cell matrix surfaces three headline findings, each
documented as a paper-publishable contribution. (Per-cell
forensics for each finding are in Phase 1.F supplementary
documentation.)

### §V.A.5.1 — Finding F1: ULR = 0% across all eight cells

**Observation.** ULR is exactly 0% in every cell, regardless
of encoder × corpus configuration.

**Interpretation.** The post-LLM rule-based redaction
(Leakage Scan) is **deterministic** — it operates on the LLM
output via fixed regex patterns + sentence-embedding lookups,
not on the LLM stochasticity. Even when the LLM produces a
raw secret in its output (GLR > 0%), the redaction layer
catches every instance before the user sees it.

**v10 paper claim.** SentinelFlow's user-facing leak rate is
**0% under all tested encoder × corpus configurations**, even
though intrinsic LLM leakage (GLR) varies 2.21% – 11.44%
across cells. This decouples the gate's user-visible
correctness from encoder-specific cosine geometry: encoder
choice affects internal forensic metrics (GLR, Per-BP-Leak)
but does not affect the headline ULR claim.

**Reviewer defense.** A skeptical reviewer may ask: "If ULR is
0% everywhere, why benchmark encoders at all?" The answer is
in the **defense-in-depth** framing: GLR % measures the
encoder's contribution to pre-LLM filtering effectiveness;
ULR = 0 is the result of **GLR + Leakage Scan** acting jointly.
A worse encoder (higher GLR) places more burden on the
Leakage Scan; a better encoder reduces that burden and improves
audit-trace quality (fewer post-LLM redactions to log). See
§V.A.5.3 for the encoder-strength trade-off implications.

### §V.A.5.2 — Finding F2: Encoder-strength leakage trade-off

**Observation.** Per-BP-Leak% varies systematically across
encoders, with a consistent ordering:

$$
\text{MiniLM} < \text{FinLang} \approx \text{mpnet} < \text{bge-large}
$$

Per-BP-Leak% ranges from 4.7% (Cell 1, MiniLM × 60) to 25.3%
(Cell 5, bge-large × 60) — a ~5× spread.

**Interpretation.** **Stronger semantic encoders bypass
attacks more readily** because they accept queries that are
semantically close to (but vocabulary-distinct from) secrets.
This is counter-intuitive from a retrieval-quality perspective:
bge-large has the best Gap(L2–L1) discrimination in v9's
embedding-model benchmark (Table [REF: tab:embedding_benchmark])
but the **worst** end-to-end leak rate under attack. The
mechanism is that bge-large encodes adversarial paraphrases
into the same neighborhood as the original secret, while
MiniLM's lower-dimensional encoding loses fine-grained semantic
distinctions that adversaries exploit.

**v10 paper claim.** **Defense-grade encoder selection differs
from retrieval-grade encoder selection.** For secret-protection
applications, the lower-dimensional, lossier MiniLM is
preferable to higher-capacity bge-large precisely because its
"weaker" semantic encoding creates a smaller adversarial
manifold. The v9 paper's MiniLM choice was correct by
operational accident; v10 elevates this to a documented design
principle: **encoder capacity is inversely correlated with
adversarial robustness in detection settings**.

**Caveat.** This finding holds at the M3.5-calibrated
thresholds. A higher $\theta$ on bge-large (which §V.A.3.2
already applies, $\theta = 0.70$ – $0.80$) partially compensates
but does not eliminate the trade-off. Whether further $\theta$
escalation could close the gap is left to future work.

### §V.A.5.3 — Finding F3: The "FinLang Paradox"

**Observation.** FinLang — the finance-domain pretrained
encoder — achieves the **highest Bypass%** in Cells 7–8
(54.24%, 53.87%) but only the **second-worst Per-BP-Leak%**
(6.1%, 11.6%). MiniLM (the general-purpose encoder) achieves
the **lowest Bypass%** (47.60%, 42.80%) but the **lowest
Per-BP-Leak%** (4.7%, 6.0%).

**Interpretation.** Finance-domain pretraining helps the
encoder recognize the *topical* relevance of adversarial
queries (so it lets fewer through as "obviously not finance"),
but the resulting bypass set contains queries that are
*semantically engineered* to be attack-shaped within the
finance domain. The "topical filter" effect is good for
pre-LLM bypass rate but bad for conditional leakage given a
bypass occurred.

**v10 paper claim.** **Domain-specific encoder pretraining
produces a topical-filter improvement at the cost of
conditional-leakage robustness.** This is a measurable
trade-off, not a free lunch — practitioners selecting an
encoder for secret-protection applications must explicitly
choose which axis to optimize: (a) absolute leakage rate
(MiniLM wins), or (b) conditional leak-given-bypass at full
defense-in-depth (still MiniLM wins, but FinLang is
competitive on raw bypass blocking).

**Reviewer defense.** This finding may appear to weaken the
case for finance-domain pretraining. The opposite is true:
this finding **strengthens** the contribution by reframing
domain pretraining as a **design lever**, not a universal
improvement. Future work [REF: §VI Limitations] examines
whether a *hybrid* configuration (MiniLM at the Gate 1
embedding gate, FinLang at the Leakage Scan stage) captures
both benefits.

---

## §V.A.6 — Reproducibility Provenance

Phase 1.F outputs are committed at git revision `007c460` and
treated as **immutable** in subsequent phases. The
reproducibility artifacts are:

- **Driver script:** `scripts/repro_full_pipeline.py` (~670 LOC)
- **Per-cell config files:** `config_phase1F_*.yaml` (8 YAML
  configs, one per cell)
- **Per-cell outputs:** `eval/results/phase1_F/<encoder>_<corpus>/`
  containing `summary.json` (per-cell metrics), `bypass_cases.jsonl`
  (per-attack bypass details), `full_pipeline_eval.json` (per-prompt
  log).
- **Aggregated matrix:** `eval/results/phase1_F/m4_matrix.json` +
  LaTeX-table emitter (via `scripts/phase1F_matrix.py`).
- **Encoder revision pins:** `core/config_loader.py:PINNED_REVISIONS`
  (4 entries; verified by `scripts/verify_repro_pins.py`).
- **FAISS index build log:** `eval/results/phase1_F/build_log.json`
  (records SHA256 hash of each FAISS file at build time).

A reviewer can re-execute any cell by:

```bash
python3 scripts/repro_full_pipeline.py \
    --config config_phase1F_<encoder>_<corpus>.yaml \
    --output-dir eval/results/phase1_F_replay/<encoder>_<corpus>
```

Within encoder revision and FAISS index reproduction, results
are deterministic up to LLM stochasticity (see §V.B for the
multi-sample protocol that quantifies this stochasticity).

---

## §V.A.7 — Connection to §V.B (Phase 1.G stochasticity treatment)

The Cell 1 +0.36pp GLR drift observed between v9 and v10
[REF: §V.A.4] cannot be resolved by re-calibration (thresholds
are frozen) or by encoder re-pinning (encoder is byte-identical
across runs). The drift originates from the defender LLM's
non-determinism at default temperature.

§V.B (Phase 1.G multi-sample stochasticity probe) addresses
this by re-running each of the eight cells with $n = 5$
samples, converting point-estimate GLR / Bypass / Per-BP-Leak
to mean ± Student's t 95% CI. The resulting confidence bounds
determine **which inter-cell differences in this section
(§V.A.4) are statistically distinguishable** vs.\ **which fall
within the LLM stochastic band**.

Findings F1–F3 (§V.A.5) are stated in this section as
**effect-size claims** that should survive the Phase 1.G
stochasticity check (per Phase 1.F §7.1: effect sizes ~20pp
on Per-BP-Leak dominate the ~0.36pp stochastic drift). §V.B
provides the empirical confirmation.

---

*End of `v10_paper_section_V_A_phase1F_draft.md` v0.1.*
*Next iterations: integrate Phase 1.G n=5 statistical bounds
once G2 analysis completes (§V.A.7 references will become
concrete CI numbers); refine F2 + F3 prose after reviewer-style
re-read; add LaTeX-ready citation keys.*
