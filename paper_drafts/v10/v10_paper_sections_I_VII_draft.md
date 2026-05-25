# v10 Paper §I (Introduction) + §VII (Conclusion) — Updates

> **Draft status:** v0.1 working draft, 2026-05-24. Markdown
> source for v10 paper §I introduction updates + §VII
> conclusion restructure (formerly v9 §V Conclusion).
>
> **Scope:** v10 retains the v9 paper's §I introduction
> structure but updates the contributions count from 7 to 12
> (Phase 1.F + Phase 1.G additions), and updates the
> roadmap paragraph (§I.C) to reflect the §V / §VI / §VII
> section restructure introduced in v10.
>
> **§VII Conclusion** consolidates v10 contributions and
> roadmap forward, replacing v9's §V Conclusion.

---

## §I — Introduction (v10 updates only)

### §I.A — Motivation [UNCHANGED from v9]

[INHERIT v9 §I.A Motivation paragraph verbatim. The v9 framing
of strategy leakage as a novel cybersecurity risk for
LLM-integrated financial workflows remains accurate for v10.]

### §I.B — Contributions [REPLACE v9 §I.B with v10 12-contribution framing]

This paper presents SentinelFlow v10, advancing the v9
contributions [CITE: v9 paper] with three new methodology-
validation phases (Phase 1.E hard-negative FPR
characterization; Phase 1.F encoder × corpus ablation;
Phase 1.G multi-sample LLM stochasticity treatment). The
combined v10 contributions are:

**Architecture and detection** (preserved from v9):

- **C1: Multi-Gate Inline Security Pipeline.** 4 pre-LLM gates +
  2 post-LLM stages with fail-safe ordering. Achieves 0%
  attack success rate on the 70-prompt hand-crafted attack
  set. [§III, v9 §III preserved.]

- **C2: Sentence-Level Semantic Leakage Firewall.** Hard (≥0.70) /
  Soft (≥0.60) / Cascade (k=2) three-tier thresholds
  preventing salami-style information disclosure. [§III.E,
  v9 §III.E preserved.]

- **C3: Domain-Specific Evaluation Framework.** 90
  institutional secrets (L1 / L2 / L3 triplets across six
  alpha domains); 271 attacks across 10 categories and 7
  evasion techniques. [§IV-J, v9 §IV-J preserved.]

- **C4: Prompt Distribution Monitoring.** Centroid anomaly
  detection that tightens leakage scan by δ=0.05 when
  z-score > 2σ. Implemented but disabled for evaluation
  cleanliness. [§III.F, v9 §III.F preserved.]

- **C5: Auditable Evidence Chain.** SHA-256 dual hash chain
  (global + per-session); 100% integrity; 14 event types;
  Streamlit dashboard. [§III.G, v9 §III.G preserved.]

- **C6: Adversarial Evaluation Methodology.** Ablation
  study; bypass root-cause analysis; latency benchmark;
  full-pipeline evaluation with LLM. [§IV, v9 §IV preserved.]

- **C7: Cross-Domain Generalization.** Medical-domain pilot:
  85% TPR, 0% FPR via configuration-only adaptation. [§IV-N,
  v9 §IV-N preserved.]

**Methodology validation** (NEW in v10):

- **C8: Encoder × Corpus Ablation.** Four-encoder
  (MiniLM, mpnet, bge-large, FinLang) × two-corpus (60-entry,
  90-entry) ablation matrix with M3.5-calibrated thresholds.
  Establishes the encoder-strength leakage trade-off:
  weaker encoders (MiniLM) achieve lower Per-BP-Leak than
  stronger encoders (bge-large) at calibrated thresholds.
  [§V.A.]

- **C9: Multi-Sample LLM Stochasticity Treatment.** Five-sample
  per-cell re-run of the encoder × corpus matrix with
  Student's t 95% confidence intervals and Holm-Bonferroni
  paired t-tests. Converts §V.A point-estimate findings to
  empirically-bounded statistical claims. [§V.B.]

- **C10: Hard-Negative FPR Characterization Framework.** A
  65-query benign-but-near-boundary corpus with
  6 linguistic categories × 6 alpha domains coverage, a
  6-layer R6 audit-grade defense pipeline against
  corpus-generation LLM leakage, and 12 paper-publishable
  methodology findings (S1–S14, sequential gaps S3/S4).
  Framing: characterization at calibration boundary, not
  target achievement. [§V.C.]

- **C11: Audit-Driven Generation Framework.** Per-category
  anti-pattern rules (15 explicit "DO NOT" rules across 6
  categories) operating as positive enforcement during
  LLM-assisted corpus generation. Empirical efficacy: 5×
  improvement in per-batch strict-pass rate vs. ad-hoc prompt
  generation. Operates at three structural levels:
  per-query accuracy, corpus-density distribution, and
  benign-by-construction. [§V.C.3, §V.C.6 S2 and S14.]

- **C12: Transparent Self-Correction Pattern (Methodological
  Discipline).** View-before-implement verification at every
  ratification gate. Caught five paper-relevant issues
  during Phase 1.E alone (FAISS cosine convention, spec
  field violations, validator semantics, corpus disjointness,
  documentation drift). Transparent errata commit (`e198e97`)
  demonstrates symmetric application of the "document
  deviations, don't refit" philosophy at the assistant
  documentation level. [§V.C.6.13, §V.C.7.]

The v10 contribution C8–C12 are presented as **methodology-
validation** contributions, distinguishing them from
architectural / detection contributions (C1–C7). This split
positions v10 as both a refinement of the v9 system (no
architectural changes) and as an extension of v9's
**methodological rigor** to address reviewer-defensibility
concerns at the TDSC / TIFS / TOPS level.

### §I.C — Roadmap [UPDATED for v10 section structure]

The remainder of this paper is organized as follows. Section
II surveys related work across security taxonomies, semantic
gateways, distance-based DLP, behavioral defense, adversarial
robustness testing, and methodology-validation precedents,
concluding with a gap analysis. Section III presents the
SentinelFlow system design, including the multi-gate
architecture, dual-threshold mechanism, leakage firewall
algorithm, audit chain, and dataset construction (largely
preserved from v9). Section IV describes the experimental
methodology and results for the v9-inherited architecture
contributions (C1–C7), including B0 vs B2 comparison,
sensitivity spectrum, threshold sweep, ablation study, bypass
root-cause analysis, encoding evasion defense, latency
benchmark, cross-domain generalization, and large-scale
external framework evaluation.

**Section V (NEW in v10) — Methodology Validation and
Statistical Treatment** consolidates the v10 contributions
C8–C12:

- §V.A presents the Phase 1.F four-encoder × two-corpus
  ablation matrix with per-cell calibration (C8).
- §V.B presents the Phase 1.G multi-sample stochasticity
  probe with Student's t 95% confidence intervals and paired
  t-tests (C9).
- §V.C presents the Phase 1.E hard-negative FPR
  characterization framework with 12 paper-publishable
  methodology findings (C10, C11, C12).

**Section VI — Limitations and Future Work** consolidates
limitations across the v10 scope and outlines future
directions grouped by priority and dependency (v11
corpus-scale-up and statistical-power; v12 conditional
adaptive-attacker work; v13+ multi-agent extension and
cross-domain expansion).

**Section VII — Conclusion** summarizes the v10
contributions and articulates SentinelFlow's research-program
trajectory.

---

## §VII — Conclusion (NEW; supersedes v9 §V Conclusion)

### §VII.A — Summary of Contributions

This paper presented SentinelFlow v10, advancing the strategy-
leakage firewall for financial RAG agents with twelve
contributions across two categories. **Architecture and
detection** contributions (C1–C7), preserved from v9,
establish: a multi-gate inline pipeline achieving 0% ASR on
the 70-prompt hand-crafted attack set; a sentence-level
leakage firewall with three-tier thresholds; a domain-
specific evaluation framework with 90 institutional secrets
and 271 attacks; prompt distribution monitoring via centroid
anomaly detection; an auditable evidence chain with SHA-256
dual hash integrity; adversarial evaluation methodology
including 7-configuration ablation; and cross-domain
generalization via configuration-only adaptation to medical-
domain secret protection.

**Methodology validation** contributions (C8–C12), new in
v10, establish: a four-encoder × two-corpus ablation matrix
demonstrating the encoder-strength leakage trade-off (lower-
capacity MiniLM achieves better adversarial robustness than
higher-capacity bge-large at calibrated thresholds); a
five-sample multi-LLM-call stochasticity treatment with
Student's t 95% confidence intervals and Holm-Bonferroni
paired tests; a hard-negative FPR characterization framework
with 65 queries, 6-layer R6 audit-grade defense against
corpus-generation LLM leakage, and 12 paper-publishable
methodology findings; an audit-driven generation framework
producing 5× per-batch efficacy improvement; and a transparent
self-correction methodological pattern documented across the
v10 development cycle.

The combined results — **0% user-facing leak rate across
all eight encoder × corpus configurations and across all
five LLM samples per cell**, **2.58% true end-to-end leakage
on the 271-prompt expanded adversarial corpus**, **3% false
positive rate on the v9 100-query benign baseline**, **65-query
hard-negative corpus producing 12 paper-publishable
methodology findings**, **28.75 ms P50 latency**, **100% audit
chain integrity** — demonstrate SentinelFlow v10 as a
research-grade strategy-leakage firewall suitable for
TDSC / TIFS / TOPS-level publication.

### §VII.B — Methodological Contribution

The v10 methodology contributions (C8–C12) deserve specific
emphasis because they are reusable beyond SentinelFlow:

- The **characterization-at-calibration-boundary** framing
  (§V.C.1.3) provides reviewer-defensible footing for any
  near-boundary FPR evaluation in security ML. It inverts the
  "did you tune to achieve the target?" review concern by
  locking thresholds before corpus construction.

- The **audit-driven generation framework** (§V.C.3.1)
  provides a template for LLM-assisted corpus construction
  with per-category anti-pattern rules as positive enforcement.

- The **transparent self-correction pattern** (§V.C.6.13)
  models how research projects should handle their own
  documentation drift: catch, surface, correct in git
  history, preserve audit trail.

- The **multi-sample stochasticity protocol** (§V.B)
  provides a template for any LLM-in-the-loop evaluation
  where defender stochasticity affects published metrics.

Each of these contributes to the broader field of
**rigorous LLM-system security evaluation**, beyond the
specific SentinelFlow application.

### §VII.C — Research Program Trajectory

SentinelFlow's research program continues with three
identified directions:

- **v11 (planned, 8 weeks):** corpus scale-up to 200
  hard-negatives; n = 10 stochasticity tightening; V3
  parametric numeric BLOCKING; cross-corpus FPR
  characterization; per-cell hard-negative FPR matrix.
  Cumulative LLM cost: $8-12.

- **v12 (conditional, 4 weeks, contingent on reviewer
  feedback):** adaptive attacker evaluation via best-of-n,
  RL-based, and PoisonedRAG-style methodologies.
  Cumulative LLM cost: $20-30.

- **v13+ (research direction, 12+ weeks):** multi-agent
  extension with trust boundary structure, compositional
  leakage detection, information flow graphs, inter-agent
  covert-channel detection. Substantial new theoretical
  contributions.

### §VII.D — Closing

The v10 paper formalizes SentinelFlow as both a deployable
firewall and a **methodology platform** for rigorous LLM-
system security evaluation. The 12 contributions span
architectural rigor (C1–C7), measurement rigor (C8–C9), and
methodological rigor (C10–C12), positioning the system for
publication at the highest-tier venues while providing
reusable methodology patterns for the broader research
community.

Future work continues along three trajectories — corpus
scale-up, adaptive-attacker hardening, and multi-agent
extension — each preserving the v10 methodological
discipline as a foundation. The research program's
**transparent self-correction** pattern (catching and
correcting its own documentation drift through git-visible
errata) is itself a contribution to the practice of rigorous
LLM-security research.

---

*End of `v10_paper_sections_I_VII_draft.md` v0.1. Next
iterations: tighten C12 framing per reviewer-feedback;
verify all numerical claims against canonical
PHASE_1E_RESULTS.md and PHASE_1F_RESULTS.md.*
