# v10 Paper §VI — Limitations and Future Work

> **Draft status:** v0.1 working draft, 2026-05-24. Markdown
> source for v10 paper §VI. LaTeX conversion deferred to
> final-polish pass.
>
> **Section scope:** v10 paper §VI consolidates limitations
> across the entire v10 contribution scope (encoder ablation,
> hard-negative characterization, stochasticity treatment,
> and end-to-end pipeline) and outlines future-work directions
> grouped by priority and dependency.
>
> **Framing principle:** v10 §VI is **reviewer-defensible
> transparent disclosure**, not apology. Every limitation is
> stated with its operational consequence (how it affects
> current claims) and its v11+ resolution path (how future
> work can lift the constraint). This positions v10 as a
> well-scoped contribution within an active research program,
> not as an incomplete first attempt.

---

## §VI.1 — Limitations Acknowledged

### §VI.1.1 — Corpus and evaluation-scope limitations

#### §VI.1.1.1 — Hard-negative corpus at 65 entries (v11 → 200)

The v10 hard-negative corpus (§V.C) contains **65 queries**
with full sub-cell coverage (36 / 36 cells) but at non-uniform
density. The PLAN.md document originally targeted 200
queries with [4, 7] per sub-cell uniformity.

**Operational consequence.** Statistical claims at the FPR
statistic level (e.g., "FPR is X% with 95% CI ± Y%") have
limited statistical power due to small sub-cell sizes. The
v10 paper §V.C therefore reports **mechanism-level findings
(S1–S14)** rather than population-level FPR effect sizes.

**v11 resolution path.** Scale to 200 entries via continued
audit-driven generation (replicating the per-sub-cell density
pattern that §V.C.6.12 demonstrates). The audit-driven
framework operates at corpus-structural level, so v11 scaling
should preserve all v10 mechanism-level findings while adding
statistical-power-level claims.

#### §VI.1.1.2 — V3 parametric numeric scope deferred

The §V.C.4 validator implements V3 (parametric numeric
content check) as a **reporting check**, not BLOCKING.
Several v10 hard-negative entries contain textbook-standard
numeric content ("130/30 long-short ratio", "2x leverage
cap", "14-day RSI", "70% concentration") that pass V2
(benign expected answers) but would require a dedicated V3
pass for parametric-leakage characterization.

**Operational consequence.** v10 hard-negative corpus may
contain queries whose expected answers could reveal
fund-specific numeric parameters if the LLM (defender)
treats the numeric content as a "this fund uses X%" target
rather than "the industry uses X%" pattern.

**v11 resolution path.** Implement V3 as BLOCKING in the v11
pipeline. Each query with numeric content is reviewed
against a parametric-leakage taxonomy: (i) industry-standard
constants pass; (ii) fund-specific parameters fail; (iii)
hypothetical / educational numbers pass with contextual
verification.

#### §VI.1.1.3 — Easy-benign vs hard-benign FPR comparison incomplete

The v10 paper compares hard-negative FPR (§V.C) against the
v9 easy-benign baselines (100-query baseline, 219-query
real-world). However, **per-encoder per-cell hard-negative
FPR measurements are deferred to v11**: the v10 paper
characterizes the **corpus** (§V.C), not the corpus
crossed with the eight encoder × corpus cells.

**Operational consequence.** The "encoder ablation on
hard-negatives" comparison is structurally possible (run
each of the 8 Phase 1.F cells against the 65-entry
hard-negative corpus) but is not in v10 scope.

**v11 resolution path.** Phase 1.E E2 / E3 / E4 deliverables
per PLAN.md §1.4 deliver this measurement after the
hard-negative corpus is scaled to 200 entries. Combined with
v11 V3 BLOCKING implementation, this produces a full
encoder × corpus × hard-FPR matrix.

### §VI.1.2 — Statistical-treatment limitations

#### §VI.1.2.1 — n = 5 is small-sample

The §V.B Phase 1.G stochasticity probe uses **n = 5 samples
per cell**. The Student's t critical value at 4 degrees of
freedom is 2.776 — relatively wide. A larger n (e.g., n = 10
or n = 20) would tighten 95% CIs proportionally to 1 / √n.

**Operational consequence.** Within-encoder corpus-delta
paired t-tests at the +0.37 pp scale (MiniLM × 60 vs × 90
GLR) may not achieve p < 0.05 even when a true effect
exists. §V.B reports the empirical outcomes; close-call
results that fail to reach significance at n = 5 are noted
as "within the stochastic band at n = 5; revisit at higher
n".

**v11 resolution path.** Scale to n = 10 with
Holm-Bonferroni-adjusted joint testing. Cost: $1.40 LLM
total Phase 1.G repeat. Wall: ~22 hours.

#### §VI.1.2.2 — Defender-LLM-only stochasticity

§V.B measures stochasticity introduced by the **defender
LLM only** (the LLM consuming attack prompts during the
SentinelFlow pipeline at temperature 1.0). It does **not**
measure:

- Encoder stochasticity (deterministic by construction).
- FAISS retrieval stochasticity (deterministic by FAISS).
- LLM-generation stochasticity for hard-negative corpus
  construction (Phase 1.E E1.2; this is a separate stochasticity
  source, separately characterized in §V.C.3).

**Operational consequence.** Phase 1.G's stochasticity
bounds apply specifically to defender-LLM-induced metric
variance. Other stochasticity sources are implicitly assumed
negligible (deterministic) but are not directly bounded.

**v11 resolution path.** If new stochastic components are
introduced (e.g., a stochastic embedding encoder or a
sample-based retrieval method), extend the §V.B n = 5
multi-sample protocol to each new component independently.

#### §VI.1.2.3 — Single defender-LLM model

Phase 1.G uses **only** `gpt-4o-mini-2024-07-18` as the
defender LLM, pinned for full reproducibility within v10.

**Operational consequence.** Cross-model robustness (e.g.,
how do v10's encoder ordering findings hold under GPT-4o
default, Claude Sonnet, Llama-3-70B as defender?) is
**unknown** at v10 publication. The encoder-ordering
finding F2 may be defender-LLM-specific.

**v11 resolution path.** Replicate §V.B's n = 5 protocol
across at least 3 defender LLMs (GPT-4o-mini, GPT-4o,
Claude Sonnet). Quantify cross-defender robustness as a
new v11 contribution. Cost estimate: $2-3 LLM per defender
× 3 defenders ≈ $6-9 total.

### §VI.1.3 — Architectural-scope limitations

#### §VI.1.3.1 — Adaptive attacker evaluation deferred

The v10 paper evaluates SentinelFlow against the **271-prompt
fixed adversarial corpus** (§IV-J), which represents
**non-adaptive attackers** — adversaries who craft attacks
without seeing SentinelFlow's responses or adapting based on
its block / pass decisions.

**Operational consequence.** Real-world attackers may
iterate attacks against an observed defense. A determined
adversary with API-access to a target SentinelFlow
deployment could potentially refine attacks until one
bypasses the gate. v10's "0% ULR" claim is therefore an
**upper bound on non-adaptive attacker success** — adaptive
attackers may achieve non-zero success.

**v11 resolution path.** PLAN.md line 150 lists "Hardening
— adaptive attacker evaluation, PoisonedRAG" as an
unscheduled future-work item. If reviewer feedback from v10
mandates this, a dedicated Phase 1.I (or later) would
implement adaptive attacker evaluation via:

- **Best-of-n attack:** LLM-generated attack pool of N
  variants; report success rate as a function of N.
- **Reinforcement-learning attacker:** RL agent that
  iteratively learns SentinelFlow's decision boundary;
  measure rate of boundary-crossing convergence.
- **PoisonedRAG-style attacks:** retrieval-corpus poisoning
  targeting the SentinelFlow defender RAG.

The v10 §V.A.5 F1 (ULR = 0%) result via post-LLM redaction
is **structurally robust** to many adaptive-attacker classes
(adaptive bypass increases GLR but not ULR), but this
robustness should be empirically validated, not assumed.

#### §VI.1.3.2 — Multi-agent extension unscheduled

SentinelFlow's current architecture protects a **single-agent**
RAG: one defender LLM, one retrieval index, one user
session. Multi-agent extensions (e.g., agent-to-agent
information flow, compositional leakage across agent
boundaries, inter-agent trust constraints) are **out of
scope** for v10.

**Operational consequence.** Deployment patterns where a
SentinelFlow-protected agent forwards outputs to a second
agent (or chains agents in a workflow) may leak across the
boundary, even if each individual agent's ULR is 0%.

**v11 resolution path.** Detailed future-work discussion is
deferred to §VI.2.3 below. The v10 paper Conclusion (§VII)
mentions this as a v11 direction.

#### §VI.1.3.3 — Single defender RAG model

v10 evaluates SentinelFlow protecting a single RAG instance
with one secret corpus (60 or 90 entries). Production
deployments may have multiple secret corpora across business
units, with cross-corpus access controls.

**Operational consequence.** v10's "FPR characterization at
the calibration boundary" framework applies per-corpus, not
across-corpus. The cross-corpus FPR (e.g., "does a hard-neg
for corpus A trigger blocks in deployment using corpus B?")
is not characterized.

**v11 resolution path.** Extend §V.C corpus design to
**cross-corpus hard-negatives** explicitly: queries that
border secrets in corpus A but are intended for corpus B
deployment. Measure cross-corpus FPR as a new dimension.

### §VI.1.4 — Methodology-process limitations

#### §VI.1.4.1 — Sequencing divergence between V2 plan and actual execution

The Phase 1.E V2 plan specified sequencing E1.1 → E1.2 →
E1.3 → E1.4 → E1.5 → E1.6 with specific scope per sub-phase.
Actual execution sometimes diverged from V2 plan scope
(e.g., E1.4 originally specified as "human filter" was
repurposed mid-execution as "outlier disposition" when
E1.3.5 validator-flagging discoveries surfaced).

**Operational consequence.** The sub-phase RESULTS docs
preserve the actual execution timeline; the master
PHASE_1E_RESULTS.md aggregates with sequencing-divergence
acknowledgment. This is engineering-process honesty, not
methodology weakness.

**v11 resolution path.** v11 plan can explicitly schedule
sub-phases by **discovery dependency** rather than
**document-order**, reducing the risk of mid-execution
re-scoping. Lessons-learned format: document V2 → V2.5 → V3
plan evolution in a single changelog.

#### §VI.1.4.2 — Phase 1.E errata correction (Phase 1.G mischaracterization)

During Phase 1.E E1.6 close, the v10 plan documents briefly
mischaracterized Phase 1.G as "adaptive attacker evaluation,
reviewer-mandatory per Phase 1.F audit feedback." This was
an unsupported claim by the documentation author and was
caught during Phase 1.G design ratification via
view-before-implement discipline.

The errata commit (`e198e97`) corrects this transparently
without rewriting the underlying commits.

**Operational consequence.** Documentation history is
preserved with both the original error and the correction
visible in git history. This is the **transparent
self-correction pattern** documented as engineering rigor
evidence in v10 §V.C.6.13 RESOLVED decisions.

**v11 resolution path.** Continue view-before-implement
discipline across all plan ratification gates. Pre-flight
verification before any phase kickoff catches drift
deterministically.

#### §VI.1.4.3 — Documentation overhead

The Phase 1.E documentation tree includes 6 RESULTS docs +
1 master + 1 errata + multiple supplementary reports
(`r6_audit.jsonl`, `v2_benign_check_report.md`, etc.). This
documentation density is **higher than typical** for a
methodology section.

**Operational consequence.** Reviewer time investment to
verify v10 §V.C claims is non-trivial (potentially 2-4
hours of focused doc review for full audit). For a TDSC /
TIFS reviewer, this is acceptable; for a less-rigorous
review venue, this density may be over-investment.

**v11 resolution path.** Consolidate documentation tree at
v11 close: single PHASE_1E_v11_FINAL.md replacing 6
sub-phase RESULTS docs. Preserve audit trail via git
history rather than redundant markdown files.

---

## §VI.2 — Future Work

### §VI.2.1 — Near-term (v11 cycle)

The following directions are **scheduled** for v11 and have
explicit resolution paths above:

| Direction | Section | Effort | Cost |
| --- | --- | --- | --- |
| Hard-neg corpus scale to 200 | §VI.1.1.1 | 1-2 weeks | <$0.40 LLM |
| V3 parametric BLOCKING | §VI.1.1.2 | 1 week | $0 |
| n = 10 stochasticity | §VI.1.2.1 | 2 days | $1.40 |
| Cross-defender robustness | §VI.1.2.3 | 1 week | $6-9 |
| Cross-corpus hard-negs | §VI.1.3.3 | 1-2 weeks | <$0.40 |
| Per-cell hard-FPR matrix | §VI.1.1.3 | 1 week | <$0.20 |

Cumulative v11 cost: ~$8-12 LLM, ~6-8 weeks wall.

### §VI.2.2 — Medium-term (v12 cycle): adaptive attacker

If reviewer feedback from v10 publication mandates adaptive
attacker evaluation, v12 implements:

#### §VI.2.2.1 — Best-of-n attack methodology

For each adversarial prompt template, generate N variants
via LLM paraphrase / mutation. Report SentinelFlow's success
rate as a function of N. The expected curve: success rate
decreases (improves) as N increases, with diminishing
returns. Establish a **practical N-threshold** below which
adaptive attackers are deemed "non-trivial to construct".

#### §VI.2.2.2 — Reinforcement-learning attacker

Train an RL agent (PPO-style) against a SentinelFlow target.
Reward signal: SentinelFlow's bypass decision (1 for bypass,
0 for block). After T episodes, measure attacker's converged
bypass rate. Report **convergence wall time** as the
attacker-effort metric.

#### §VI.2.2.3 — PoisonedRAG defenses

Extend SentinelFlow's audit chain to detect retrieval-corpus
poisoning. Specifically: detect when newly-added secret
entries cause significant pre-gate bypass rate increase on
the existing 271-prompt corpus. Flag as a corpus-poisoning
event.

### §VI.2.3 — Long-term (v13+): multi-agent extension

The multi-agent extension warrants substantial discussion
because the architectural complexity is qualitatively
different from single-agent SentinelFlow:

#### §VI.2.3.1 — Trust boundary structure

A multi-agent deployment has multiple **trust boundaries**:

- **User → Agent A:** the standard SentinelFlow scope.
- **Agent A → Agent B:** new trust boundary requiring its
  own filtering layer.
- **Agent B → User:** standard, but receives Agent A
  outputs as input.

Each boundary is a potential leakage point. A query that
SentinelFlow allows at User → Agent A may pass an
intermediate signal to Agent B that, in turn, leaks at
Agent B → User.

#### §VI.2.3.2 — Compositional leakage detection

The v10 SentinelFlow firewall detects single-message
leakage: does this specific prompt + LLM response leak a
secret? Multi-agent settings require **compositional
leakage detection**: does the sequence of agent messages,
when aggregated, leak a secret?

A natural framework: per-edge hash chains (extending v10's
SHA-256 audit chain) tracking which secret tokens flow
through each agent boundary. Detection: secret token
presence at any User-facing endpoint flags a leak.

#### §VI.2.3.3 — Inter-agent C2 channels

A sophisticated adversary may use the multi-agent topology
itself as a **covert channel**: send a benign-looking
query to Agent A that, via Agent B's response, ultimately
leaks a secret without any single agent's output containing
it. Multi-agent SentinelFlow must detect such
**information-flow patterns**, not just per-message content.

#### §VI.2.3.4 — Information flow graph (IFG)

A natural model: represent the multi-agent system as an
information flow graph (IFG) with agents as nodes and
message flows as edges. SentinelFlow extensions track:

- **Per-edge information content:** what secrets does each
  edge carry?
- **Path-level aggregation:** does any path from a secret
  source to a User sink carry a leak?
- **Trust-zone partitioning:** which agents may share which
  secrets?

This is genuine v13+ research, requiring multiple new
theoretical contributions beyond v10's scope.

### §VI.2.4 — Cross-domain extension

The v10 paper's medical-domain pilot (§IV-K v9 paper
content; cross-domain generalization C7) demonstrates that
SentinelFlow can be retargeted via **configuration-only
adaptation**. v11+ should systematically extend to:

- **Legal:** litigation-strategy protection.
- **Pharmaceutical:** clinical trial parameter protection.
- **Semiconductor:** process recipe protection.
- **Financial cross-jurisdictional:** regulatory-zone-specific
  secret protection (e.g., GDPR-relevant secrets vs SEC-relevant
  secrets).

The v10 hard-negative characterization framework (§V.C) is
**naturally domain-agnostic**: the 6-category linguistic
taxonomy applies to any domain, and the audit-driven
generation framework can be re-instantiated with new
per-category anti-pattern rules per domain.

### §VI.2.5 — Production deployment

v10 evaluates SentinelFlow as a **standalone Python pipeline**.
Production deployments require:

- **HTTP proxy / sidecar architecture:** v10 §V.A discusses
  this as a future engineering direction.
- **Multi-tenant isolation:** each tenant's secrets
  isolated by FAISS index; cross-tenant FPR bounded.
- **Latency SLA monitoring:** v9 reports 28.75 ms P50; v11+
  should monitor P95, P99 under sustained load.
- **Audit chain durability:** SHA-256 chain integrity under
  power loss / restart scenarios.

These are engineering-quality concerns, not research
contributions, but are necessary for v10's
research-grade results to translate to production deployments.

---

## §VI.3 — Roadmap Summary

| Cycle | Scope | Effort | LLM Cost | Status |
| --- | --- | --- | --- | --- |
| **v10 (current)** | 12 contributions C1–C12 (architectural C1–C7, methodology-validation C8–C12) | 8 weeks | $0.88 | In submission |
| **v11** | Corpus scale 200, n = 10, V3, cross-corpus, per-cell hard-FPR | 8 weeks | $8-12 | Planned |
| **v12** | Adaptive attacker (if reviewer-mandated) | 4 weeks | $20-30 | Conditional |
| **v13+** | Multi-agent extension | 12+ weeks | $30-50 | Research direction |

---

*End of `v10_paper_section_VI_draft.md` v0.1. Next iterations:
tighten reviewer-defensibility tone in §VI.1; add
cross-references to specific §V subsections where each
limitation arises; consider whether §VI.2.3 multi-agent
discussion should be a top-level subsection rather than
nested under Future Work.*
