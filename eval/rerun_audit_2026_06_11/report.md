# Phase 0' — Rerun-Scope & API-Cost Inventory (READ-ONLY, NO EXECUTION)

**This document is a pure inventory.** No reruns were performed, no API calls were
made, and no experiment / config / pipeline file was modified. All token figures
are local-tokenizer (`tiktoken o200k_base`) estimates or recalibrations from
already-logged empirical usage; all dollar figures are estimates for Peter to
price-check.

Scope = the experiments in frozen positioning doc `sentinelflow_positioning_frozen_v5.md`
§9 item 2 ("重跑受影响结果", = checklist A–E) and §9 item 3 ("L2 产业机制体检", = F),
that are affected by the corpus_v2 restructure.

---

## 0. Pricing assumptions (Peter to verify — pin date assumed 2026-06-05)

| model | role | input $/1M | output $/1M | source of assumption |
|-------|------|-----------:|------------:|----------------------|
| `gpt-4o-mini-2024-07-18` | defender (B0/B2), attack rewrite, LLM-self-check | 0.15 | 0.60 | `config.yaml:21` pinned; `run_full_pipeline_eval.py:150` uses 0.15 input |
| `gpt-4o-2024-08-06` | L1 independent judge | 2.50 | 10.00 | `run_l1_judge.py:64` "list pricing pinned 2026-06-05"; back-checks the logged L1 cost exactly |

**Empirical anchors (already-logged actuals, used for extrapolation):**
- **L1 judge**: `l1_judge_summary.json` — 432 judgments (144-set × 3 arms) = 219,659 input + 24,005 output tok = **$0.789197**. → per-judgment ≈ **508 in / 56 out tok, $0.001827**.
- **B0/B2 defender**: `path_a_isolation_failure/summary.json` — 144 bypass cases (gpt-4o-mini) = **cumulative $0.044935** (cost_cap was $0.12).
- **8-cell n=5 leakage (Phase 1.G)**: `PHASE_1G_PLAN.md` forecast **~$0.70** (gpt-4o-mini, 8 cells × 5 samples).
- Local token sizes: attack `query` mean **29 tok** (n=271, max 57); corpus_v2 `secret_text` mean **54 tok**, `anchor_text` mean **29 tok** (n=90).

---

## 1. Divergences from the task checklist (reported honestly)

1. **A — "70 手工 + 201 改写": CONFIRMED CORRECT.** 271 = 70 originals (ids in `data/benchmark/attack_prompts.jsonl`) + 201 generated (carry `based_on_original_id`). (Note: a `_V2` id-suffix marks only 66 rows — that is a different sub-marker, NOT the manual/generated split.)
2. **All 271 attacks target the OLD secret ids** (`target_secret` ∈ 25 distinct `S00xx`). None point at corpus_v2 ids → 100% require retargeting. (Matches "目前指向旧 secret id".)
3. **L2 / FPR-LLM / retrieval-utility have NO existing script.** `eval/` contains no `l2_*`, no retrieval-utility, no benign-FPR-LLM module. FPR today is `run_statistical_eval.py` = **gate-level deterministic, 0 API** (`:236` "Estimated LLM API calls: 0"). So E and the offline parts of D/F are real but **F's LLM-self-check and D's per-cell leakage and any new code are net-new implementation, not just reruns**.
4. **L1 judge model = `gpt-4o-2024-08-06`** (full 4o, not mini). Checklist "GPT-4o judge" — consistent.
5. **8-cell = 4 encoders × 2 corpora** (`PHASE_1G_PLAN.md:42`; encoders minilm/mpnet/bge_large/finlang per `phase1_F/build_log.json`).

---

## 2. Per-experiment inventory

Columns: deps (file-level) · outputs · API? · est. API calls · est. tokens (prompt / completion) · cost range · offline part · blocking deps · risk + stop-gate.

### A. Attack-corpus regeneration (271 set + 70-set + isolation 144-set)
- **Deps**: `data/attack_prompts_expanded.jsonl` (271), `data/benchmark/attack_prompts.jsonl` (70), `eval/corpus_v2/*` (90 new secrets), old→new secret id map (does NOT exist — must be authored).
- **Outputs**: retargeted attack jsonl(s) pointing at corpus_v2 ids; regenerated isolation 144-set (derived by running pre-gates, not authored).
- **API?**: PARTIAL. Mechanical retarget (swap `target_secret` + literal params) = 0 API. Generated-variant re-rewrite = LLM.
- **Est. API calls**: 0 (if all-mechanical) … up to **201** (re-rewrite every generated variant). The exact mechanical-vs-rewrite split is **NOT mechanically derivable** — it needs per-prompt human triage (does the new corpus_v2 target carry an analogous parameter the attack can be value-swapped onto?). **Sub-task, flagged.**
- **Est. tokens** (if 201 re-rewritten, gpt-4o-mini): ~201 × (≈400 in / ≈120 out) = **~80k in / ~24k out**.
- **Cost range**: **$0.00 (all-mechanical) – $0.05** (all-rewritten). Small.
- **Offline part**: id/param swap; isolation-144 derivation (running deterministic pre-gates).
- **Blocking deps**: corpus_v2 (frozen ✓); old→new id map (TODO).
- **Risk + stop-gate**: 70 hand-authored attacks likely need **manual** re-authoring (0 API but human time) to stay faithful to each new secret; auto-rewriting them risks semantic drift. **Stop-gate: freeze the old→new id map + mechanical/rewrite triage list and get Peter sign-off BEFORE any rewrite call.**

### B. B0/B2 main comparison (271 × two arms × defender)
- **Deps**: retargeted attack set (from A), `config.yaml` (pinned `gpt-4o-mini-2024-07-18`), corpus_v2 FAISS index (rebuild needed — offline), `core/` gate code.
- **Outputs**: `eval/results/<new>/bypass_cases.jsonl`, per-prompt B0/B2 outputs, summary.
- **API?**: YES (defender generation). Leakage scan + all pre-gates = **offline/deterministic**.
- **Est. API calls**: B0 = all **271** (no-defense baseline answers every prompt); B2 = only bypass cases reaching the LLM (prior block rate gave 271→144 ≈ 53%; new corpus rate TBD) ≈ **~140–160**. Total ≈ **~410–430 calls**.
- **Est. tokens** (gpt-4o-mini): B0 271×(~200 in/~200 out) + B2 ~150×(~400 in/~200 out) ≈ **~115k in / ~85k out**.
- **Cost range**: **$0.05 – $0.12**. (Anchor: path_a 144-set = $0.045; this is 271 B0 + ~150 B2.)
- **Offline part**: index rebuild, pre-gates (regex+embedding), leakage scan, FPR-at-gate.
- **Blocking deps**: **A** (attacks must be retargeted first).
- **Risk + stop-gate**: B0 is an unguarded model emitting proprietary content — keep outputs out of any synced location. **Stop-gate: per-step cost-cap $0.10 (standing rule); if a single arm exceeds it, halt.**

### C. L1 independent judge (3 arms × new attack set)
- **Deps**: B0/B2 per-prompt outputs (from B), `run_l1_judge.py`, judge cache dir.
- **Outputs**: `per_prompt_judge.jsonl`, `l1_judge_summary.json`, crosstab, monotonicity.
- **API?**: YES (`gpt-4o-2024-08-06`). Caching present → unchanged (arm,attack,secret,response) reuse free; new secrets ⇒ new responses ⇒ mostly cold.
- **Est. API calls**: **3 × set size**. 144-set → **432** (= prior run). Full 271-set → **813**.
- **Est. tokens**: at 508 in / 56 out per judgment → 432 → ~219k in / 24k out; 813 → **~413k in / ~46k out**.
- **Cost range**: **$0.79 (144-set, = logged actual)** … **~$1.49 (271-set × 3)**.
- **Offline part**: substring/verbatim GT recomputation (deterministic, already in script).
- **Blocking deps**: **B** (needs the arm outputs), transitively **A**.
- **Risk + stop-gate**: **This is the single largest cost line and BY ITSELF exceeds the standing $0.40 total cap.** **Stop-gate: do NOT launch C without explicit Peter budget authorization; default to the 144-set (isolation-failure) scope, not full 271×3, unless Peter widens it.**

### D. 8-cell encoder×corpus + retrieval-utility (§3.4)
- **Deps**: corpus_v2, 4 encoders (minilm/mpnet/bge_large/finlang — HF download), `phase1_F`/`phase1_G` harness; **retrieval-utility needs a query→relevant-secret relevance set (does NOT exist — must be defined)**.
- **Outputs**: refreshed 8-cell matrix + per-encoder nDCG@k/recall@k.
- **API?**: embedding/index/retrieval/retrieval-utility = **OFFLINE** (HF only). Per-cell **leakage** measurement = LLM **iff** it regenerates defender outputs per cell (Phase 1.G did, gpt-4o-mini).
- **Est. API calls**: 0 for the retrieval/utility half. Per-cell leakage: anchor Phase 1.G n=5 = ~$0.70; single-sample 8-cell ≈ **~$0.14** (gpt-4o-mini) but scales with new bypass count.
- **Est. tokens**: embedding-only (no LLM) for the §3.4 deliverable; leakage half ~ Phase 1.G envelope.
- **Cost range**: **$0.00 (retrieval-utility only)** … **~$0.70 (with per-cell leakage at n=5)**.
- **Offline part**: **all of the §3.4 retrieval-utility deliverable**; only optional per-cell leakage re-measure costs API.
- **Blocking deps**: corpus_v2 (✓). Independent of A–C (parallelizable).
- **Risk + stop-gate**: **retrieval-utility relevance labels are not yet defined** — needs a labeling decision (use attack `target_secret`? a held-out query set?) before the metric is computable. **Stop-gate: ratify the relevance-label definition with Peter before D.**

### E. FPR retest (100 benign + 65 hard-neg + 90 anchor + 37 decoy)
- **Deps**: `data/benchmark/normal_prompts.jsonl` (100), `data/benchmark/hard_negatives.jsonl` (65), corpus_v2 anchors(90)/decoys(37), `run_statistical_eval.py`, rebuilt gate index.
- **Outputs**: FPR/TPR summary (mean±std, McNemar).
- **API?**: **NO.** Current FPR = gate-level deterministic (`run_statistical_eval.py:236` "0 API").
- **Est. API calls**: **0.**
- **Est. tokens**: 0.
- **Cost range**: **$0.00.**
- **Offline part**: **all of it.**
- **Blocking deps**: gate index rebuild (offline); independent of A–C.
- **Risk + stop-gate**: ONLY if the FPR definition is changed to include LLM response-level adjudication does this gain cost (then 292 prompts × defender + optional judge ≈ +$0.05–0.6). **Stop-gate: confirm FPR stays gate-level; if response-level is wanted, re-estimate before running.**

### F. L2 industry-mechanism taxonomy (§3.3; 6 classes)
- **Deps**: leakage response set (from B), corpus_v2 secrets, `config.yaml` (`model_path: meta-llama/Prompt-Guard-86M` for guardrail), **no existing L2 script (net-new)**.
- **Outputs**: per-class decision table (EDM / SIT / similarity / guardrail / doc-classifier / LLM-self-check).
- **API?**: PARTIAL. EDM / SIT / similarity = **offline** (literal/regex/embedding). guardrail (Prompt-Guard-86M, local) + doc-classifier (local) = **offline**. **LLM-self-check = API.**
- **Est. API calls (LLM-self-check)**: 1 self-check per response in the test set → ~**150–271** (gpt-4o-mini), or larger if 90 secrets × multiple probe responses.
- **Est. tokens**: ~271 × (≈400 in / ≈100 out) ≈ **~110k in / ~27k out**.
- **Cost range**: **$0.03 – $0.30** (gpt-4o-mini; higher if a 4o-grade self-check is chosen).
- **Offline part**: 4–5 of the 6 mechanism classes.
- **Blocking deps**: **B** (needs responses to classify); transitively **A**.
- **Risk + stop-gate**: net-new code + a pre-registered branch decision (`§3.3`: if LLM-self-check recall is high, the narrative branch switches). **Stop-gate: implement + dry-run the self-check on a ~10-item slice, confirm token/call shape against this estimate, then get Peter sign-off before the full run.**

---

## 3. Cost roll-up (estimates; Peter to price-check)

| item | API model | cost range |
|------|-----------|-----------:|
| A attack regen | gpt-4o-mini | $0.00 – $0.05 |
| B B0/B2 main | gpt-4o-mini | $0.05 – $0.12 |
| C L1 judge | gpt-4o-2024-08-06 | $0.79 – $1.49 |
| D 8-cell (+leakage) | gpt-4o-mini | $0.00 – $0.70 |
| E FPR | — | $0.00 |
| F L2 (LLM-self-check) | gpt-4o-mini | $0.03 – $0.30 |

See `dependency_graph.md` for the minimal-viable vs full rerun sets and their totals.

## 4. ⚠️ Cost-cap risk (standing rule) — TOP stop-gate

The standing budget discipline is **per-step $0.10 / total $0.40 hard cap.** Every
realistic rerun set **breaks the $0.40 total cap**, driven almost entirely by **C
(L1 judge), which alone is $0.79–$1.49.** No execution should begin until Peter
**explicitly authorizes a budget above $0.40** (or descopes C, e.g. judge only the
arms/groups that actually changed, exploiting the existing response-hash cache).
Per the standing "stop-and-report on cost over cap" rule, **this audit stops here
and hands the budget decision to Peter.**
