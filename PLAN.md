# SentinelFlow v2 — Journal Submission Upgrade Plan

## 0. Document Status

This is the authoritative plan for upgrading SentinelFlow from
the course-project state (v9 journal draft, Team 02 final report)
into a competitive submission for IEEE TDSC or ACM TOPS within
6–9 months. When this document conflicts with v9 paper content,
this document wins. When this document conflicts with KICKOFF.md
on policy, KICKOFF.md wins (it is more recent and stricter).

## 1. Background and Motivation

The current v9 draft (`sentinelflow_journal_v9_final.tex`)
implements a single-agent inline AI security gateway with four
pre-LLM gates and two post-LLM stages, evaluated on 271 internal
prompts plus 1,079 supplementary prompts (779 garak + 300
HarmBench-format), achieving 2.58% true ASR on the internal set
and 0.74% across supplementary. Cross-domain generalization to
the medical domain is reported.

Three strategic gaps prevent this draft from being competitive at
TDSC/TOPS:

1. **Evaluation is largely internal.** The 779 garak probes are
   external but general-purpose (only 2.3% gate block on the
   financial domain); the 300 HarmBench-format and 271 internal
   prompts are author-created. No public, domain-relevant
   benchmark results are reported.

2. **Threat model is single-agent.** Recent work (AgentLeak,
   arXiv 2602.11510) shows that in multi-agent LLM systems,
   inter-agent message channels (C2) leak at 68.8% versus 27.2%
   on user-facing output (C1). Output-only firewalls miss 41.7%
   of violations. SentinelFlow currently inspects only C1.

3. **Several known weaknesses are deferred to "future work":**
   multi-turn salami evaluation, hard-negative FPR set, adaptive
   attacker robustness, and embedding model upgrade are all
   acknowledged but unaddressed.

## 2. Key Literature to Anchor Against

The following works MUST be read, cited, and where applicable
benchmarked against. Claude Code should treat this list as the
authoritative reading list when reasoning about related work.
arXiv IDs are given to prevent hallucinated citations; if any
arXiv ID below fails to resolve, flag it rather than invent one.

### 2.1 Multi-agent leakage and benchmarks
- AgentLeak: Full-Stack Benchmark for Privacy Leakage in
  Multi-Agent LLM Systems (arXiv:2602.11510).
  - 1,000 scenarios across healthcare/finance/legal/corporate
    (250 per vertical); 32-class attack taxonomy; three-tier
    detection pipeline.
  - Key finding: inter-agent C2 leak rate 68.8% vs C1 27.2%;
    output-only audits miss 41.7%.
  - Benchmark reference repo: `Privatris/AgentLeak` on GitHub.
- AgentDojo (NeurIPS 2024 D&B; arXiv:2406.13352).
  - 4 environments, banking suite directly relevant.
  - Indirect prompt injection in tool-using agents; verifiable
    via tool execution checks.
- AgentHarm (ICLR 2025; arXiv:2410.09024). Harm from malicious
  user direct queries (different threat model from AgentDojo).

### 2.2 Financial LLM safety benchmarks
- CNFinBench: Safety and Compliance Benchmark for Financial
  LLMs (arXiv:2512.09506).
  - Capability–Compliance–Safety triad, 15+ subtasks.
  - 17 attacker personas × 7 attack strategies for multi-turn
    adversarial dialogue.
  - Harmful Instruction Compliance Score (HICS), 0–100.
  - Note: primarily Chinese; SentinelFlow will need an English
    adaptation pipeline; this adaptation itself is a minor
    contribution and must be documented as such.
- FinanceBench (Islam et al., 2023). Public 10-K QA benchmark,
  150 questions. Use only for benign-baseline FPR sanity check.
- FinDER (arXiv:2504.15800). Already used in v9 as the public
  RAG corpus; preserved.

### 2.3 RAG and embedding attacks (threats outside the inline pipeline)
- PoisonedRAG (USENIX Security 2025). Five malicious documents
  achieve >90% manipulation on million-doc corpora.
- ALGEN (early 2025). 1,000 alignment samples sufficient to
  partially invert black-box embedding models, recovering
  50–70% of original input words.
- OWASP LLM Top 10 (2025): LLM07 System Prompt Leakage, LLM08
  Vector and Embedding Weaknesses are new/elevated entries
  directly relevant to SentinelFlow's threat surface.

### 2.4 Adaptive attacks and benchmark robustness
- "Indirect Prompt Injections: Are Firewalls All You Need, or
  Stronger Benchmarks?" (arXiv:2510.05244).
  - Critical finding: existing agentic security benchmarks
    saturate easily under three-stage cascade attacks
    (standard injection + second-order + adaptive). Any
    single-attack-type evaluation is suspect.
- Mandatory Access Control for Agent Systems
  (arXiv:2601.11893). Formal critique of IsolateGPT, CaMeL,
  SecAlign, AgentArmor, Progent under multi-round and MAS
  conditions.

### 2.5 Industry deployments to position against (Section II
addition)
- JPMorgan LLM Suite (200K+ users, 2024–2025): no consumer-LLM
  policy, in-house gateway.
- Goldman Sachs GS AI Assistant (10K pilot → firmwide 2025):
  model-agnostic routing across GPT-4o/Gemini/Claude.
- Morgan Stanley AI@MS Assistant + AskResearchGPT (16K
  advisors, 100K+ documents).
- Hedge funds: D.E. Shaw LLM Gateway (PII strip + query
  logging across 24 external models) — closest industrial
  analog to SentinelFlow; Point72 Azure V-Net deployment;
  Balyasny in-house gateway; Bridgewater AIA Labs; Man Group
  Alpha Assistant (draft-not-execute). Citadel Seattle AI lab
  cancellation due to PM IP-leakage concerns is the strongest
  motivating story for Section I.

### 2.6 Defense-side products to compare against
- Lakera Guard (real-time, <50ms latency, SOC2/GDPR/NIST).
- NVIDIA NeMo Guardrails (open source, Colang DSL).
- Microsoft Prompt Shields (Azure AI Content Safety).
- CalypsoAI Moderator (enterprise DLP + audit trail).
- Arthur AI Shield, Protect AI, HiddenLayer, LLM Guard.

### 2.7 Auxiliary motivation
- Profit Mirage (arXiv:2510.07920). LLM financial agents
  collapse 50%+ in performance past training cutoff due to
  data contamination — useful as supporting framing for "why
  strategy leakage matters beyond IP", though not a direct
  benchmark target.
- Bayesian RAG (PMC 2025). Possible inspiration for a
  future uncertainty-aware grounding module; not in scope
  for this submission.

## 3. High-Level Goals (in priority order)

1. **Evaluation upgrade** — replace internal-only evaluation
   with at minimum two public benchmarks (CNFinBench Safety
   subset + AgentLeak finance subset, single-agent C1 channel
   first), plus a multi-turn salami evaluator and a
   hard-negative FPR set.
2. **Multi-agent extension** — extend SentinelFlow to inspect
   inter-agent (C2), tool-input (C3), tool-output (C4), shared-
   memory (C6/C7) channels, validated on three concrete
   scenarios (A, B, C below).
3. **Threat model formalization** — Information Flow Graph
   (IFG) abstraction with formal adversary, attack surface, and
   security goal.
4. **Hardening** — adaptive attacker evaluation, PoisonedRAG
   experiment, embedding model upgrade.

## 4. Phase Order Decision (Important — Do Not Reorder)

Phase 1 (Evaluation) MUST complete before Phase 2 (Multi-Agent
Extension) because:
- Phase 2 needs Phase 1's single-agent benchmark scores as the
  ablation reference. Without it, Phase 2 results are
  uninterpretable.
- CNFinBench attack templates and AgentLeak taxonomy are reused
  in Phase 2 as the attack corpus for inter-agent scenarios.
  Doing Phase 2 first means rebuilding evaluation infra mid-
  flight.
- Phase 1 results will reveal which attack patterns currently
  bypass SentinelFlow most often, which directly informs Phase
  2 design priorities (e.g., if multi-turn social engineering
  is the main bypass, Scenario A's customer-facing pipeline
  should emphasize session-level cross-agent tracking).

Within Phase 1, deliverables A/B/C/D/E/F are mostly parallel,
but the recommended sequence is: F (embedding ablation, smallest)
→ E (hard-negative FPR, smallest) → D (salami) → A (CNFinBench,
largest) → B (AgentLeak finance C1) → C (AgentDojo banking).
This order front-loads small wins that strengthen v9's existing
results before tackling the larger benchmark integrations.

## 5. Phase Breakdown

### Phase 1 — Evaluation Upgrade (Months 1–2, Priority P0)

#### Deliverable A: CNFinBench Safety Subset Integration
- Path: `sentinelflow/evaluations/benchmarks/cnfinbench/`
- Adapter from CNFinBench format to SentinelFlow input.
- Multi-turn runner: attacker LLM (GPT-4o) drives 5–10 turn
  dialogues against SentinelFlow's defender (GPT-4o-mini).
- 17 personas × 7 strategies; record gate decisions every turn.
- HICS scorer per session.
- Definition of Done (DoD):
  - At least 50 distinct (persona, strategy) cells evaluated.
  - HICS heatmap CSV produced.
  - At least 30 "broken" sessions logged for case-study use.
  - README under the cnfinbench/ directory documents licensing,
    English-adaptation methodology, and known divergences from
    upstream CNFinBench.

#### Deliverable B: AgentLeak Finance Subset (Single-Agent C1)
- Path: `sentinelflow/evaluations/benchmarks/agentleak/`
- Run all 250 finance scenarios in single-agent mode (flatten
  the multi-agent task into one prompt). C1 channel only.
- Phase 1 baseline; Phase 2 will rerun the same scenarios in
  true multi-agent mode for direct comparison.
- DoD:
  - 250 scenarios executed end-to-end.
  - Per-scenario leakage flag and ground-truth sensitive entity
    annotations preserved.
  - Comparison table v9-internal (271 prompts) vs AgentLeak
    finance C1 (250 scenarios) — flag any discrepancy
    >5 percentage points and explain.

#### Deliverable C: AgentDojo Banking Suite
- Path: `sentinelflow/evaluations/benchmarks/agentdojo/`
- Wrap AgentDojo banking tools so SentinelFlow can intercept
  tool input (C3) and tool output (C4) channels.
- Run the full banking task suite under both benign and
  injection conditions.
- DoD:
  - Utility (task completion under benign) and Security
    (fraction of tasks completed despite injection) both
    reported.
  - Tool-output channel inspector implemented as a Phase-2
    dependency; smoke test runs in <5 minutes.

#### Deliverable D: Multi-Turn Salami Attack Evaluator
- Path: `sentinelflow/evaluations/internal/salami/`
- Generator: given an L3 secret, GPT-4o decomposes it into
  N benign-looking sub-questions covering all parameters.
- Runner: feeds the sequence to SentinelFlow turn-by-turn,
  records per-turn cumulative leakage and cascade trigger turn.
- DoD:
  - ≥100 generated sequences, average ≥7 turns each.
  - Cumulative-leakage-by-turn curve plotted.
  - Cascade trigger statistics: median turn, blocking rate,
    false-resolve rate.
  - Output a plain-English "this addresses the v9 future-work
    item" paragraph for paper insertion.

#### Deliverable E: Hard-Negative FPR Set
- Path: `sentinelflow/evaluations/internal/hard_negatives/`
- ~100 L1-boundary queries, vocabulary-overlapping with L2/L3
  secrets but containing no proprietary parametric content.
- Distribute coverage across all 6 alpha domains in the
  existing 90-secret corpus.
- DoD:
  - 96+ queries, balanced across domains.
  - FPR-on-hard-negatives reported separately from the
    existing 100-query benign baseline.
  - Each query annotated with target secret it borders.

#### Deliverable F: Embedding Model Ablation
- Rerun core experiments with three encoders:
  - all-MiniLM-L6-v2 (current baseline; preserve v9 numbers).
  - all-mpnet-base-v2 (paper's own Table XX shows +24% Gap).
  - One finance-finetuned model (suggest BAAI/bge-large-en-v1.5
    or a FinBERT-style encoder; final choice in
    AUDIT_AND_PROPOSAL.md).
- DoD:
  - For each model: TPR, FPR, true leakage rate, P50/P95
    latency on CPU and (if feasible) GPU.
  - Recommendation written for which model the v10 paper
    should adopt as primary.

### Phase 2 — Multi-Agent Extension (Months 3–5, Priority P1)

#### Deliverable G: Information Flow Graph Module
- Path: `sentinelflow/multiagent/`
- Files: `ifg.py`, `channels.py`, `inspector.py`,
  `agent_wrapper.py`, `orchestrator.py`, `policies/`.
- Channel taxonomy: C1 (agent→user), C2 (agent→agent),
  C3 (agent→tool), C4 (tool→agent), C5 (agent→log; passive),
  C6 (agent→memory write), C7 (memory→agent read).
- Each agent has: role, sensitivity_max (L0/L1/L2/L3 ceiling),
  identity, permission set.
- DoD:
  - Unit tests for each channel inspector.
  - Existing single-agent flow continues to pass all v9 tests
    unchanged.
  - Integration with LangGraph as the orchestration layer
    (rationale: built-in checkpointing, easier audit).

#### Deliverable H: Three Concrete Multi-Agent Scenarios

##### Scenario A — Customer-Facing Pipeline
- Agents: CustomerAgent (sensitivity_max=L0),
  ResearchAgent (sensitivity_max=L3), SalesAgent
  (sensitivity_max=L1).
- Three attacks:
  - A1 Pivot leakage: social-engineered query escalates
    through CustomerAgent → ResearchAgent → SalesAgent →
    CustomerAgent.
  - A2 Cross-agent salami: 5+ turns split across
    different downstream agents.
  - A3 Identity confusion: external user impersonates
    internal compliance role.
- Critical inspection point: C2 must redact L3 content when
  passing to a SalesAgent whose sensitivity_max is L1.

##### Scenario B — Cross-Agent Privilege Escalation
- Reproduces arXiv:2601.11893 attack: anonymous intermediate
  agent invokes high-privilege tools without proper checks.
- Defense: identity propagation (originating user identity
  travels with every message), delegation chain hash in
  message metadata.
- Maps to OWASP Agentic ASI05 (Privilege Compromise).

##### Scenario C — Tool I/O Channel Inspection
- ResearchAgent has tool access (DB queries, external APIs).
- Two attacks:
  - C-attack-1: indirect injection embedded in tool output.
  - C-attack-2: secret exfiltration via tool input
    (e.g., "send this analysis to attacker@…").
- Reuses Deliverable C's AgentDojo wrapper.

DoD across A/B/C:
- Each scenario implemented with reproducible attack scripts.
- Per-channel leakage rates reported (C1, C2, C3, C4 separately)
  on AgentLeak finance subset rerun in true multi-agent mode.
- Direct comparison to Phase 1 single-agent baseline.

#### Deliverable I: Cross-Agent Salami Tracker + Per-Edge Hash Chain
- Salami accumulator extended to (originating_user,
  strategy_domain) keys, aggregating signals across agents.
- Hash chain extended to per-edge chains plus a Merkle-style
  root chain over edge-chain heads every N messages.
- DoD:
  - Existing 100% audit integrity preserved (regression test
    suite).
  - New tamper-detection unit tests cover edge-chain
    falsification, root-chain replay, and out-of-order
    message injection.

#### Deliverable J: Multi-Agent Re-evaluation
- Rerun Deliverable B's 250 AgentLeak finance scenarios in true
  multi-agent mode with channels C1/C2/C3/C5 each instrumented.
- DoD:
  - Per-channel leak rate table in the format AgentLeak's
    paper uses (so direct comparison is possible).
  - At least one channel's leak rate must drop substantially
    versus the AgentLeak paper's reported 68.8% baseline; if
    no channel improves, that itself is a finding to report
    honestly.

### Phase 3 — Hardening and Submission Prep (Month 6+, Priority P2)

#### Deliverable K: Adaptive Attack Evaluation
- White-box attacker with full knowledge of amplifier list,
  dual thresholds (0.50 / 0.75), cascade k=2.
- Generate ≥100 adaptive attacks via GPT-4o with explicit
  evasion instructions.
- Report static-vs-adaptive ASR gap; honest discussion if
  gap is large (it likely will be).
- Directly addresses the critique in arXiv:2510.05244.

#### Deliverable L: PoisonedRAG-Style Corpus Injection
- Inject 5–20 crafted chunks into the 18,516-chunk public
  corpus targeting specific high-value queries.
- Goal: explicitly demonstrate SentinelFlow has no current
  defense against corpus poisoning, scope this out, and
  motivate future-work direction (retrieval validation /
  source attestation).
- This is a "negative result" deliverable — done well it
  strengthens the paper's honesty.

#### Deliverable M: Threat Model Formalization (Writing)
- New Section III-X in the paper: IFG formal definition,
  adversary capabilities, attack surface, security goal.
- This is writing, not coding; produced after Phase 2
  results stabilize.

#### Deliverable N: Paper Rewrite to v10
- Incorporate all Phase 1–3 results.
- Restructure Literature Review with the new sources from
  Section 2 of this PLAN.
- Add Industry Deployments paragraph in Section II.
- Update Limitations and Discussion.

## 6. Non-Goals (Explicitly Out of Scope)

- Zero-knowledge audit chain (zk-MCP); deferred to v3 paper.
- Differential privacy on query embeddings; future work
  mention only.
- Production-grade streaming optimization beyond current
  P50 latency.
- Cross-domain pilots beyond medical (already in v9).
- Re-architecting the existing single-agent pipeline. The
  multi-agent extension is additive, not replacing.

## 7. Constraints and Conventions

- Defender LLM: GPT-4o-mini (preserve fair comparison with v9).
- Attacker LLM (red-team generator): GPT-4o.
- Embedding (Phase 1 ablation): see Deliverable F.
- Audit chain integrity: must remain 100% across all changes.
- All randomized experiments use seeded RNG.
  Reproducibility scripts checked into repo, invoked via
  `make reproduce-<deliverable>` or equivalent.
- Each new benchmark integration includes a `LICENSE_NOTES.md`
  documenting upstream license and citation.
- Each new module ships with at least a smoke test runnable
  in <5 minutes on a small subset.

## 8. Repository Layout (Target State)

sentinelflow/
├── core/                       # existing pipeline (unmodified)
├── multiagent/                 # NEW (Phase 2)
│   ├── ifg.py
│   ├── channels.py
│   ├── inspector.py
│   ├── agent_wrapper.py
│   ├── orchestrator.py
│   └── policies/
│       ├── role_policy.yaml
│       └── flow_policy.yaml
└── evaluations/
├── benchmarks/             # NEW (Phase 1)
│   ├── cnfinbench/
│   ├── agentleak/
│   └── agentdojo/
├── internal/
│   ├── salami/             # NEW (Phase 1)
│   └── hard_negatives/     # NEW (Phase 1)
└── threats/                # NEW (Phase 3)
├── adaptive/
└── poisoned_rag/


## 9. Success Criteria for v10 Paper Submission

The paper is ready to submit to TDSC/TOPS when ALL of the
following hold:

1. Reported leakage rates on at least two external public
   benchmarks (CNFinBench Safety subset + AgentLeak finance),
   in addition to the existing internal corpus.
2. Multi-agent evaluation reports per-channel leakage rates
   (C1, C2, C3, C5) on at least 100 multi-agent scenarios.
3. Multi-turn salami evaluation: ≥100 generated sequences,
   cumulative-by-turn curve, cascade trigger statistics.
4. Adaptive attack ASR reported alongside static ASR.
5. Threat model section includes formal IFG definition with
   adversary capabilities, attack surface, security goal.
6. Hard-negative FPR reported separately and within
   operational target (<5%).
7. All experiments reproducible from a single make target.
8. v9 results re-run with the chosen Phase-1-F embedding
   model; results table updated.
9. Industry deployment paragraph added to Section II citing
   ≥5 named institutions (per Section 2.5 above).

## 10. Working Norms with Claude Code

- Claude Code MUST read this PLAN.md and KICKOFF.md before
  proposing any work.
- Claude Code MUST output an implementation plan
  (AUDIT_AND_PROPOSAL.md) before writing any code; the user
  reviews and approves before any code is written.
- Claude Code MUST NOT modify `sentinelflow_journal_v9_final.tex`
  without explicit instruction; paper edits are a separate
  phase.
- Claude Code MUST NOT add new dependencies without
  justification recorded in AUDIT_AND_PROPOSAL.md or a
  follow-up doc.
- Each new benchmark integration MUST include a smoke test
  that runs in <5 minutes on a small subset.
- All commits MUST follow `<area>: <imperative summary>`
  style (e.g., `cnfinbench: add multi-turn runner`).

### 10.1 Git Policy (STRICT — Authoritative)

The user controls all git history changes. Claude Code modifies
files only; the user reviews via `git status` / `git diff` and
decides what to commit and when.

#### Allowed (read-only inspection)

- `git status`, `git log`, `git diff`, `git show`, `git branch
  --list`, `git remote -v` — all read-only inspection commands.

#### Allowed (staging only, no history change)

- `git add <file>` to stage modifications. Staging does not
  change history; the user will commit.
- Reading files, modifying files, creating files (these are not
  git operations themselves; only the resulting state is what
  the user reviews).

#### FORBIDDEN — never run without per-command, in-session
authorization

The following all change git history or upload to remote, and
must never be executed by Claude Code under any circumstances
without an explicit authorization sentence in the current chat
session (e.g., "yes, commit this now"):

- `git commit` in any form, including `--amend`, `--no-edit`,
  `-m "..."`, etc. **The user does ALL commits manually.**
- `git merge`, `git rebase`, `git cherry-pick` (history change)
- `git reset --hard`, `git reset --soft <commit>` (loses work
  or rewrites history)
- `git stash drop`, `git stash clear`
- `git push` in any form (push, --force, --force-with-lease,
  --tags, to any remote)
- `git remote add`, `git remote set-url`, `git remote rm`,
  `git remote rename`
- Any direct edit of `.git/config`, `.git/hooks/`, or any
  file inside `.git/`
- `gh pr create`, `gh pr merge`, `gh repo create`, `gh repo
  fork`, or any GitHub CLI command that writes
- `git svn dcommit`, `git p4 submit`, or any VCS bridge that
  uploads
- Any shell command that uploads to a remote git endpoint
  (e.g., `curl` POST to git-receive-pack)

#### Standing authorization does NOT apply

A standing authorization in PLAN.md, KICKOFF.md, prior
sessions, or implied by phrases like "please finalize",
"proceed", or "all set" does NOT count as commit/push
authorization. Authorization must be PER-COMMAND, EXPLICIT,
and IN THE CURRENT SESSION.

#### Suggested workflow

When Claude Code completes a logical unit of work:
1. Modify files (and optionally `git add` to stage)
2. Report to user: "Done. Modified files: [list]. Suggest
   commit message: '...'. Stopping for your manual commit."
3. Stop and wait. Do not commit.
4. The user runs `git status` / `git diff`, decides whether
   to amend, then commits manually.

If Claude Code accidentally runs any forbidden command (e.g.,
through a tool wrapper that auto-commits), it MUST immediately
report this in chat with full details (commit hash, files
affected, message used) before doing anything else.