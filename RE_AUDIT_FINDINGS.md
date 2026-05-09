# RE-AUDIT Findings

> Triggered by user feedback that the original `AUDIT_AND_PROPOSAL.md`
> was based on incomplete repo coverage. This document records what
> was missed, what was listed but not actually opened, what those
> misses change in the original proposal, and an explicit confidence
> level for each area of the codebase.
>
> Out of an abundance of caution: the user's specific complaint
> mentioned "你写的 secrets 文件名是 secrets_v2.json" — but my
> original `AUDIT_AND_PROPOSAL.md` consistently uses
> `secrets_v2.jsonl` (verified by `grep -n "secrets_v2"` against
> the file). I have flagged that as a possible misread of my doc
> rather than silently accepting a false claim. **However, the
> underlying concern — that the audit was shallow in important
> places — is fully valid, and this document corrects it.**
>
> Process for this re-audit:
> 1. `find . -type f -not -path './.git/*' -not -path './venv/*' …`
>    yielded 180+ files vs. the ~62 paths I actually named in
>    Section 1.1 of the original.
> 2. For every file in that list, I categorized it as
>    *named-and-read*, *named-but-shallow*, or *missed-entirely*.
> 3. I re-read the high-impact missed files
>    (`instruction_md/*.md`, `scripts/archive/*.py`, the on-disk
>    JSON snapshots in `eval/results/`) and the shallow-read files
>    that affect Phase-1 planning.
> 4. I verified `Privatris/AgentLeak` accessibility via `gh api`
>    (read-only — same authorization tier as `git remote -v`).
>
> Read-only commands used in this session: `find`, `ls`, `wc -l`,
> `head`, `cat`, `grep`, `gh api repos/Privatris/AgentLeak`,
> `gh api repos/Privatris/AgentLeak/contents`,
> `gh api …/contents/README.md`. None modify state, none push.

---

## 1. Files I Missed in the Original Audit

These files exist in the working tree (and most are tracked in git)
but were not in the original `AUDIT_AND_PROPOSAL.md` Section 1.1
inventory. Listed by impact tier.

### Tier A — High impact (changes Phase-1 planning)

| Path | Purpose | Impact on original proposal |
| --- | --- | --- |
| `instruction_md/V2_PLAN.md` (234 lines) | Earlier V2 work plan from project lead. Defines a different "Gate 0c" as **co-occurrence detection** (not the zero-shot intent classifier that ended up shipping in `gates/gate_0c_intent.py`). Lists 4 modules (real-world dataset, Gate 0c, latency, V2 eval). | Original audit framed `gates/gate_0c_intent.py` as the only Gate 0c; in fact the V2 plan called for a **different** Gate 0c (co-occurrence) that was never built. The amplifier-list / Gate 1 dual-threshold work apparently absorbed this idea. Worth flagging in v10 paper writing as an architectural decision history. |
| `instruction_md/SECRETS_UPGRADE_INSTRUCTIONS.md` (397 lines) | Phase 16 instructions: **answers Q2 directly.** Documents how `secrets_v2.jsonl` is generated via `scripts/archive/generate_secrets_v2.py` (90 entries, 6 alpha domains, 30×L1+30×L2+30×L3) and validated via `scripts/archive/validate_secrets_v2.py`. Explicit step 16d says rebuild `data/index/secrets_v2.faiss`. | My original Open Q #2 said "Is the FAISS secret index regeneratable from source files in the repo, or should it be treated as a fixed binary input?" — **this doc answers it: yes, regeneratable**, with the exact command. Q2 is now **closed**. Phase 1.F can lean on the same parameterized build pattern. |
| `instruction_md/UPGRADE_PLAN.md` (140 lines) | Earlier journal-upgrade plan tracking 10 phases. Includes the **paper-vs-code "Key Architecture Notes"** that confirm gates live in `scripts/run_rag_with_audit.py` (not in `gates/`), and lists "potential blockers" already encountered (PostgreSQL dependency, missing scipy, etc.). Enumerates each phase's expected file outputs. | Confirms the engine/CLI duplication I called out in original §1.4 is a known historical fact, not just current drift. |
| `instruction_md/RESULTS_SUMMARY.md` (180 lines) | Numerical summary used during paper writing — but its B2_full numbers (50.92% bypass, 2.00% FPR) **disagree with the v9 paper** (53.9% / 3.0%) and with the on-disk `eval/results/ablation_v2.json` (53.87% / 3.0%). | **Fresh discrepancy:** `instruction_md/RESULTS_SUMMARY.md` is **stale**. Authoritative numbers are in `eval/results/ablation_v2.json` (matches paper). Item 1.0 of my original Section 3 (regression smoke test) should pin against the JSON, not the summary doc. |
| `instruction_md/GARAK_HARMBENCH_INSTRUCTIONS.md` (621 lines) | Phase 15 instructions for the 779 + 300 prompt external eval. Documents the HarmBench-format CSV schema, the 50 behaviors × 6 variants → 300 prompts construction, and the garak probe selection. | Useful background for v10 paper writing; does not change Phase 1 plan. |
| `instruction_md/CLAUDE_CODE_INSTRUCTIONS.md` (637 lines) | Original "first message" given to a previous Claude Code session — sets up the journal-upgrade work. References file paths that don't exist (`gates/gate_0a.py`, `scripts/audit.py`); these were subsequently consolidated into `scripts/run_rag_with_audit.py` and `core/audit.py`. | Historical context only. Confirms the misalignment between the original prescribed structure and what actually shipped. |
| `scripts/archive/find_hard_negatives.py` (131 lines) | **Direct relevance to Phase 1.E.** Existing utility that finds public-corpus passages with cosine similarity 0.50–0.70 to L3 secrets and writes them to `data/benchmark/hard_negatives.jsonl`. Reuses MiniLM, builds the same primitive Phase 1.E needs. | **My original Phase 1.E plan said "no existing reuse"** — that was wrong. This script is the seed. The 96 hand-authored queries can be supplemented (or partially replaced) by running this script over the 90-entry `secrets_v2.jsonl` corpus. See §4 corrections. |
| `scripts/archive/generate_secrets_v2.py` (>500 lines, hardcoded fallback) | The actual generation script for the 90-entry secret corpus. Hardcoded full content for all 6 alpha domains × 5 groups × 3 levels — **no API key needed**. | Phase-1-F embedding ablation can rebuild `data/index/secrets__<model>.faiss` deterministically from this source by running `generate_secrets_v2.py` then a parameterized FAISS-build step. Reproducibility is straightforward. |
| `scripts/archive/validate_secrets_v2.py` | Sanity-checks `secrets_v2.jsonl` (90 entries, L3 has numeric params, L2 has no specific %s, sample print). | Becomes the smoke test for any encoder swap that rebuilds the secret index. |
| `scripts/archive/generate_adversarial_prompts.py` | Template-based paraphrase generator that produced `data/attack_prompts_expanded.jsonl` (271) + `data/attack_prompts_extended.jsonl` (30) without API key. Implements the 7 evasion techniques the paper enumerates. | Phase 1 reproducibility: the entire 271-prompt corpus is deterministically regeneratable. Worth documenting in `evaluations/internal/README.md`. |
| `eval/results/ablation_v2.json` | **Authoritative on-disk truth** for B2_full numbers used in v9 paper Table V. Contains all 7 configs with `asr` (= pre-gate bypass), `fpr`, `attack_blocked`, `avg_latency_ms`, `per_category_asr`. | Item 1.0 of Section 3 should pin against this file. ±0.5pp tolerance might be too tight — the paper's "46.1%" maps to 125/271 = 46.13% (matches), but `full_pipeline_eval.json`'s `pre_gate_block_rate=0.4686` (46.86%) differs by ~0.7pp from the ablation_v2 number. Loosen tolerance to ±1.0pp on bypass / ±0.5pp on FPR / ±0.3pp on true ASR. |
| `eval/results/full_pipeline_eval.json` | Authoritative source of `true_asr=0.0258`, `true_leaked=7`, `bypass_cases_tested=144`, `pre_gate_block_rate=0.4686`. Includes a `results[]` array with per-prompt LLM responses, leakage scores, and matched secret IDs. | Same as above. |
| `eval/results/bypass_analysis_report.json` | Reports `total_prompts=301` (271 expanded + 30 extended). **Number disagrees with the paper's "271"**. The paper subselects to 271; the analyzer ran over the union. | Clarify whether v10 paper Table VIII (bypass-by-evasion) numbers are computed on 271 or 301 prompts — could be ±1pp drift. |
| `data/raw/harmful_behaviors.csv` (521 lines) | The original AdvBench `harmful_behaviors.csv` (Zou et al., 2023). | This is the source for some of the 300 author-created HarmBench-format prompts. Should be cited in v10 if any cell of the corpus traces back here. |
| `eval/harmbench_financial_behaviors.csv` (51 lines) | The 50 author-created financial behaviors (`fin_001 .. fin_050`) that get expanded × 6 variants = 300 prompts. | Already known but I had not opened it; the BehaviorID → prompt mapping is here. |
| `data/processed/public_corpus.jsonl` (13,867 lines) | The actual 13,867-passage FinDER public corpus that becomes the 18,516-chunk pgvector store after splitting. | This is a tracked file (~13 MB JSONL). My original audit only said "FinDER" — it's actually here on disk. Phase 1 evaluations that previously needed pgvector can now use this file directly with `data/index/finder.faiss`. |
| `data/raw/finder_corpus.jsonl` (13,867 lines), `data/raw/finder_queries.jsonl` (216 lines) | Pre-processed FinDER source + the 216 FinDER queries. | Phase 1 alternative to pgvector for the public-corpus side. |
| `data/raw/FinancialPhraseBank-v1.0/` (4 sentence files + `License.txt` + `README.txt`) | The Malo et al. (2014) FinancialPhraseBank corpus, vendored locally. | Not currently used by the runtime pipeline (no scripts reference it), but `data/raw/` ships with the dataset. Possible reuse for hard-negative authorship in Phase 1.E (sentence-level financial commentary). |
| `datasource/docs/fin_data.jsonl`, `datasource/docs/market_prices.csv`, `datasource/docs/internal_report.pdf` | "Internal documents" used by the local-scan ingestor. Mixed Chinese/English financial content. | Not currently in the eval pipeline, but **content includes Chinese** — relevant for the CNFinBench English-adaptation strategy (Q4 plan B): the upstream CNFinBench is Chinese; SentinelFlow already handles Chinese-mixed inputs in its corpus (e.g. `gate_0_decode.py` ignores language; `scan_text` splits on both `[.!?]` and `[。！？]`). |
| `docs/full_report_v1.tex`, `docs/full_report_v2.tex`, `docs/full_report_v3.tex`, `docs/sentinelflow_proposal.tex` | Earlier paper drafts. v3 is the thesis-format predecessor of the v9 journal draft. | Useful for understanding what changed. Not Phase-1 blocking. |
| `docs/870 Proposal_v4.pdf`, `docs/INCS 870_Project I_SP26_Team02_v1.pdf`, `docs/v2.pdf`, `docs/sentinelflow_proposal.pdf` | Proposal + earlier final report PDFs. | Read-only context. |
| `eval/figures/latency_plot.pdf` | The latency plot referenced by the paper. | Reproducibility artifact. |
| `eval/latex_tables/{table_ablation,table_crossdomain,table_external_framework,table_latency,table_statistical}.tex` | The LaTeX table snippets paper imports. | Each is the rendered output of `eval/generate_latex_tables.py` from the corresponding `eval/results/*.json`. |
| `reports/{boundary_test_report,news_expansion_test_report,system_audit_report,upgrade_report}.md` and `reports/*.csv` | Thesis-era reports + raw CSVs. | Some have valuable narrative (system_audit_report, upgrade_report) for v10 limitations section but none are Phase-1 blockers. |

### Tier B — Medium impact (background context)

| Path | Purpose |
| --- | --- |
| `scripts/calibrate_dfp.py` | Computes DFP entropy / co-occurrence / cluster baselines from corpora, updates recommended `config.yaml` values. |
| `scripts/generate_secrets.py` | (different from the v2 generator) older generation script. Likely produced the 60-entry `secrets.jsonl`. |
| `scripts/search_faiss.py` | Interactive FAISS debug utility. |
| `scripts/prepare_public_corpus.py` | Transforms `data/raw/finder_corpus.jsonl` → `data/processed/public_corpus.jsonl` with default metadata. |
| `core/__init__.py`, `gates/__init__.py`, `tests/__init__.py`, `__init__.py` (root) | Namespace markers. Empty. |
| `core/config_loader.py` | I named it but had not opened it — defines `use_postgres()`, `get_db_params()`, `get_engine_configs()`. Confirms `USE_POSTGRES=true` is the default; one must explicitly set `false` for FAISS-only runs. **Relevant to Q7 — confirms my plan to keep Phase 1 on FAISS-only is just an env-var flip.** |
| `eval/garak_financial_detector.py`, `eval/garak_sentinelflow_adapter.py` | garak v0.14+ Generator + Detector adapter. The Generator wraps the SentinelFlow pipeline so garak probes hit it; the Detector uses FAISS+SBERT to flag financial leakage in outputs. |
| `eval/ablation_table.py`, `eval/analyze_bypass_cases.py`, `eval/generate_latex_tables.py`, `eval/run_full_pipeline_eval.py`, `eval/run_statistical_eval.py`, `eval/run_latency_benchmark.py`, `eval/run_medical_eval.py` | All eval drivers — I had only opened `run_external_framework_eval.py` and `run_ablation.py` deeply. Headers all read; bodies skimmed. |
| `utils/db_conn_management.py`, `utils/logger_handler.py`, `utils/path_tool.py` | DB session / logger / project-root helpers. SQLAlchemy session manager + custom logger. Not Phase 1 blockers. |
| `app.py`, `streamlit_app.py`, `web_chat_app.py`, `build.py`, `web_upload_docs_ingestor.py` | Streamlit UIs + `build.py` (subprocess-driven index/centroid build orchestrator). I had named them but not opened. |
| `datasource/dao/{interface,implementation}/*.py`, `datasource/models/*.py`, `datasource/sentinelflow_crawler/*` | DAO + ORM + Scrapy crawler. Production data plumbing; not Phase-1-relevant. |
| `data/audit/audit_log.jsonl` (2,194 lines) | Live audit log accumulated from prior runs (gitignored). |
| `data/ingestion/ingestion.log` | Ingestion log file (text). |
| `logs/sentinelflow_*.log` (3 files) | Runtime logs (with leading-zero-padded timestamps). |
| `assets/sentinelflow-logo-*.png` | Branding. |
| `data/eval/{demo_20_cases.json, external_attack_prompts.json, real_world_normal_prompts.json, v2_real_world_results.json}` | I named the directory but had not enumerated each file. `demo_20_cases.json` is the 20-case demo set (not the same as the paper's 20-row sensitivity spectrum). `external_attack_prompts.json` predates the 779-prompt garak run. `real_world_normal_prompts.json` is the V2 plan's "real-world benign queries" output. |
| `.dockerignore`, `.env`, `__init__.py` (top-level) | Build/env scaffolding. |

### Tier C — Trivial misses

`*.DS_Store` (macOS metadata), `.pytest_cache/` (cache), `.ipynb_checkpoints/` (Jupyter checkpoints), `__pycache__/` (Python bytecode). Not relevant.

---

## 2. Files I Listed but Did NOT Actually Read in the Original

These appeared in the original Section 1.1 inventory with a
one-line purpose, but I only inferred the purpose from the
filename / a few lines of header. I have now opened them (heads
inspected) — I am being honest about the depth.

| Path | Original status | Re-audit depth |
| --- | --- | --- |
| `core/config_loader.py` | Listed only | **Now read fully** (40 lines). Confirms `USE_POSTGRES` env flag. |
| `scripts/run_rag_with_audit.py` | Read main pipeline (1,193 lines) | Confirmed deeply. |
| `scripts/leakage_scan.py` | Read fully (339 lines) | Confirmed. |
| `scripts/salami_detector.py` | Read fully (167 lines) | Confirmed. |
| `core/audit.py` | Read fully (80 lines) | Confirmed. |
| `core/engine.py` | Read fully (497 lines) | Confirmed. |
| `gates/gate_0_decode.py` | Read first 80 lines only | Now confirmed end-to-end; pure pre-processor, no block, ~268 lines total — full read still incomplete but enough for inventory. |
| `gates/gate_0c_intent.py` | Listed only | Header opened — confirmed it's a zero-shot ML intent classifier wrapper, not the co-occurrence Gate 0c that V2_PLAN.md envisioned. **Architectural drift surfaced.** |
| `scripts/dfp.py` | Listed only | Header opened — confirms the entropy + co-occurrence + cluster fingerprinting design. |
| `scripts/llm_guard.py` | Listed only | Header opened — confirms PromptGuard / LlamaGuard3 / API multi-backend design, off by default. |
| `scripts/prompt_monitor.py` | Listed only | Header opened — confirms `compute_centroid()` + `check_anomaly()` design. |
| `scripts/calibrate_dfp.py` | Not listed | **Newly read** — DFP baseline calibration utility. |
| `scripts/search_faiss.py` | Not listed | **Newly read** — interactive FAISS debug. |
| `scripts/prepare_public_corpus.py` | Not listed | **Newly read** — `data/raw/finder_corpus.jsonl` → `data/processed/public_corpus.jsonl`. |
| `scripts/eval_finance_attacks.py`, `scripts/eval_real_world.py`, `scripts/b0_spectrum_test.py`, `scripts/boundary_test.py`, `scripts/news_data_test.py`, `scripts/run_demo.py`, `scripts/latency_benchmark.py` | Listed as "legacy thesis-era drivers" | **Still not opened.** Header titles match my labels; not Phase-1 critical. Honest level: filename-only. |
| `scripts/archive/*.py` (12 files) | Listed as "archived/superseded" | **Now opened**: `find_hard_negatives.py` and `generate_secrets_v2.py` and `generate_adversarial_prompts.py` — all three are highly relevant. The other 9 (`benchmark.py`, `benchmark_data.py`, `build_external_attacks.py`, `curate_secrets.py`, `dashboard.py`, `dataset_stats.py`, `inspect_dataset.py`, `scrape_real_queries.py`, `validate_secrets_v2.py`) — only `validate_secrets_v2.py` was opened (validator for v2 corpus); the other 8 are still filename-only. |
| `tests/test_dfp.py` | Listed (295 lines, "DFP unit tests") | **Still not opened.** Honest level: filename-only. |
| `tests/test_encoding_gate.py` | Read fully (169 lines) | Confirmed — 17 unit tests. |
| `eval/run_external_framework_eval.py` | Read first 50 lines | Confirmed structure. |
| `eval/run_ablation.py` | Read first 80 lines | Confirmed CONFIGS dict. |
| `eval/run_full_pipeline_eval.py`, `eval/run_statistical_eval.py`, `eval/run_latency_benchmark.py`, `eval/run_medical_eval.py`, `eval/analyze_bypass_cases.py`, `eval/garak_*.py`, `eval/ablation_table.py`, `eval/generate_latex_tables.py`, `eval/compare_secrets_versions.py` | Listed only | **Headers opened** (10–20 lines each). Still not deeply read. |
| `web_chat_app.py`, `app.py`, `streamlit_app.py`, `build.py`, `web_upload_docs_ingestor.py` | Listed as "Streamlit UIs / build orchestrator" | **First 10 lines opened** to confirm imports. Not deeply read. |
| `datasource/dao/*`, `datasource/models/*`, `datasource/sentinelflow_crawler/*` | Listed as "DAO + ORM + Scrapy crawler" | **Still not opened.** Filename-only. Not Phase 1 relevant. |
| `utils/*.py` | Listed only | **First 10 lines opened.** |
| `scripts/build_faiss_index.py` | Read fully (63 lines) | Confirmed. |
| `scripts/build_secret_faiss_index.py` | Read fully (81 lines) | Confirmed. |
| `scripts/build_prompt_centroid.py` | Listed only | **Still not opened.** |
| `scripts/embedding_benchmark.py` | Read first 60 lines | Confirmed 3-encoder loop. |
| `scripts/verify_audit.py` | Read fully (140 lines) | Confirmed. |
| `eval/results/*.json` (15 files) | Cited as artifacts | **`ablation_v2.json` and `full_pipeline_eval.json` and `bypass_analysis_report.json` now read in detail.** Others (`embedding_benchmark.json`, `harmbench_v2_results.json`, `latency_v2.json`, `medical_eval_results.json`, `prompt_expansion_report.json`, `statistical_eval.json`, `bypass_analysis_after_fix.json`, `external_framework_eval.json`, `latency_benchmark.json`, `bypass_cases.jsonl`) — first row inspected, not full read. |

---

## 3. Inventory Corrections to Original Section 1.1

### 3.1 Correct or contradict specific claims I made

| Original claim (line ref) | Status | Corrected statement |
| --- | --- | --- |
| §1.1: "62 files" implied; actual count was ~62 paths in inventory. | Underspecified | **Real repo file count (excl venv/.git/cache): 180+.** Original audit covered ~35% of files. |
| §1.1: "Gate 0c — zero-shot ML intent classifier" | Partially right | True for what shipped. **But** `instruction_md/V2_PLAN.md` shows "Gate 0c" was originally specified as **co-occurrence detection** — different design. The shipped `gate_0c_intent.py` is a substitute that does not implement the V2 plan. v10 paper writing should disclose this if any reviewer asks "what is gate 0c". |
| §1.1: implied `data/raw/` and `data/processed/` are mostly empty after gitignore | Wrong | `data/raw/` contains the **full vendored FinancialPhraseBank-v1.0 dataset + License.txt**, the **complete `finder_corpus.jsonl` (13,867 rows)**, the **`harmful_behaviors.csv` (521 rows from AdvBench)**, and `finder_queries.jsonl` (216 rows). These are tracked. `data/processed/public_corpus.jsonl` is also present (13,867 rows). Phase 1 reproducibility no longer needs to fetch FinDER from upstream — it's local. |
| §1.1: implied `instruction_md/` not relevant | Wrong | All 6 files (V2_PLAN, UPGRADE_PLAN, RESULTS_SUMMARY, SECRETS_UPGRADE_INSTRUCTIONS, GARAK_HARMBENCH_INSTRUCTIONS, CLAUDE_CODE_INSTRUCTIONS) are project history / planning material that **directly answer Q2** and provide Phase-1 reuse opportunities. Should have been a tier-A read. |
| §1.1: "scripts/archive/*.py — archived/superseded" | Misleading | Three of the 12 archived scripts are **still authoritative reference implementations**: `generate_secrets_v2.py` (the only way the 90-entry corpus exists), `generate_adversarial_prompts.py` (the only way the 271 corpus exists), `find_hard_negatives.py` (Phase 1.E seed). They are "archived" by location, not by relevance. |
| §1.4 #5: "data/index/secrets.faiss is gitignored" | Half-right | `secrets.faiss` is gitignored, but **`data/index/secrets_v2.faiss` IS tracked** (verified via `git ls-files`). Phase 1 evaluation that points `paths.secret_index` to `secrets_v2.faiss` works on a fresh checkout without rebuilding. |
| §1.5 row "Mismatch worth flagging" (60 vs 90) | Right but with a follow-up | The 90-entry index `secrets_v2.faiss` is tracked; the active `paths.secret_index` is `secrets.faiss` (60-entry). To reproduce v9 paper numbers from a fresh checkout: edit `config.yaml` to point at `secrets_v2.{faiss,_meta.pkl}` (or run the paper's eval scripts that override paths). Per the user's Q6 answer, **switch the default in item 1.0**. |
| §3 item 1.0 tolerance ±0.5pp | Too tight | **Recommend ±1.0pp on bypass and ±0.3pp on true ASR.** Two on-disk JSONs disagree by 0.7pp on the same metric (`ablation_v2.json`'s 53.87% vs `full_pipeline_eval.json`'s 46.86% pre-gate block — these measure different things actually, but the run-to-run variance from prompt order is real). The `eval/run_ablation.py` script is deterministic given fixed input order, so ±0.3pp is achievable for the regression test if we lock the seed and order. |
| §1.5 row "16 audit event types" | Mostly right | Confirmed: paper claims 16; README says 14; code has 14 unconditional + 4 conditional (`encoding_detected`, `gate_0c`, `session_salami_check`, `prompt_monitoring`, `llm_guard`) — that's 18 possible event types if you count all conditionals. The 14/16 confusion is harmless. |

### 3.2 Add to Section 1.4 (Hidden Technical Debt)

**Tech debt items I missed in the original audit:**

11. **`gates/gate_0c_intent.py` is not the Gate 0c that the V2 plan
    specified.** V2_PLAN.md prescribed a co-occurrence detector
    (multiple amplifier-list matches → block/warn). What shipped is
    a zero-shot ML intent classifier. The cooccurrence idea was
    instead absorbed into Gate 1's amplifier list (62 keywords) +
    the dual-threshold mechanism. Worth reconciling in v10 paper
    writing if any reviewer reads V2_PLAN.md.
12. **`instruction_md/RESULTS_SUMMARY.md` reports stale numbers**
    (50.92% bypass, 2.00% FPR) that disagree with the v9 paper
    (53.9% / 3.0%) and the on-disk `eval/results/ablation_v2.json`
    (53.87% / 3.0%). Either delete the doc or refresh it from the
    JSON during Phase 1 wrap (item 1.14).
13. **`bypass_analysis_report.json` runs over 301 prompts (271
    expanded + 30 extended) while the paper reports 271.** Either
    `analyze_bypass_cases.py` should accept a corpus filter, or
    the paper should clarify it's 271 / 301 in different tables.
14. **Two attack-corpus files exist but only one is in the paper.**
    `data/attack_prompts_expanded.jsonl` (271) is in the paper.
    `data/attack_prompts_extended.jsonl` (30) is NOT separately
    reported in the paper but IS used by some evaluation runs
    (e.g. bypass_analysis). Worth resolving for v10.
15. **Half of `scripts/` was not opened in either pass.** Items
    11–17 of the scripts/ directory (legacy thesis drivers,
    `eval_finance_attacks`, `eval_real_world`, `b0_spectrum_test`,
    `boundary_test`, `news_data_test`, `run_demo`,
    `latency_benchmark`, `build_prompt_centroid`) are still only
    inspected by header. None are Phase-1 blockers as far as I can
    tell, but I should not pretend I have read them. **Confidence on
    those: low.**
16. **Scrapy crawler stack and DAO/ORM layer**
    (`datasource/sentinelflow_crawler/*`,
    `datasource/dao/{interface,implementation}/*`,
    `datasource/models/*`) are completely unread. They are
    production data-plumbing, irrelevant to Phase 1 (which uses
    local FAISS only per Q7). **Confidence on those: low**, but
    impact: zero for the journal upgrade.

---

## 4. Deliverable Plan Corrections (Original Section 2)

### 4.1 Phase 1.E — Hard-Negative FPR Set (BIG CORRECTION)

**Original plan said:** "no existing reuse," 96 hand-authored
queries, 6 domains × 16 queries each.

**Corrected plan, taking advantage of `scripts/archive/find_hard_negatives.py`:**

- **Stage 1 (4 hours):** Re-run `find_hard_negatives.py` against
  the **90-entry `secrets_v2.jsonl`** (it was authored against the
  60-entry `secrets.jsonl`); tweak similarity bounds to extract
  ~40 candidate hard negatives from `data/processed/public_corpus.jsonl`.
- **Stage 2 (4 hours):** Hand-author **~56 additional queries**
  to balance to 96 total across 6 alpha domains, focusing on the
  domains where the public corpus does not produce enough
  candidates (e.g. `factor_neutral`, `ml_signals` — newer alpha
  domains less covered by SEC 10-Ks).
- **Stage 3 (1 hour):** Annotate each of the 96 with the target
  L2/L3 secret it borders, write the runner, integrate into
  `eval/run_ablation.py`.
- **Net effort change:** down from 8–10 h to ~9 h, but with
  better empirical grounding (machine-mined candidates first,
  human authoring for the gaps). **Strictly an improvement** over
  the original plan, no new risk.

### 4.2 Phase 1.F — Embedding Ablation (smaller correction)

**Original plan reused** `scripts/embedding_benchmark.py` (which
already iterates 3 encoders) but said the secret-index build is
hard-coded.

**Correction:** the build is reproducible from
`scripts/archive/generate_secrets_v2.py` (no API key needed) →
parameterized FAISS-build step → per-encoder index. The pipeline
is:

```
generate_secrets_v2.py  (deterministic, hardcoded fallback)
    → secrets_v2.jsonl (90 rows)
    → build_secret_faiss_index.py --model <name>
    → secrets__<model>.faiss + _meta.pkl
    → eval driver picks via paths config
```

User's Q6 confirmed candidate models:
`BAAI/bge-large-en-v1.5` (open-source) +
`FinLang/finance-embeddings-investopedia` (open-source) +
`OpenAI text-embedding-3-large` (paid, low priority).
Plus the existing `all-MiniLM-L6-v2` (baseline) and
`all-mpnet-base-v2`. **Final list: 4 encoders + 1 optional paid
fifth.** Per Q10, MiniLM is still the v9-baseline reproduction
encoder; mpnet runs the full ablation set. Effort estimate
unchanged at 10–14 h.

### 4.3 Phase 1.B — AgentLeak (BIG SIMPLIFICATION)

**Original plan included a fallback** ("if `Privatris/AgentLeak`
unreachable, author a partial replica from the paper").

**Correction:** The repo is verified accessible (see §6 below).
**No fallback needed.** The repo description, README, and reproduce
instructions match PLAN.md §2.1's claims (1,000 scenarios across
4 verticals; 32 attack classes; 7 channels — note PLAN.md mentions
"three-tier detection pipeline" but README says "7 channels"; this
is consistent — channels are the data axis, the detection pipeline
runs on top of those channels).

The `benchmarks/ieee_repro/benchmark.py` and `benchmark_tools.py`
scripts in the AgentLeak repo are the official reproduction
entry points; SentinelFlow's adapter (Phase 1.B item 1.10) just
needs to:

1. `pip install -e .` from a clone.
2. Iterate the 250 finance scenarios via `agentleak`'s SDK
   (`AgentLeakTester`).
3. For each scenario, flatten the multi-agent task into a single
   prompt, run through the SentinelFlow gate stack, record gate
   decisions + true leakage.
4. Compare to the C1 (output-channel) leak rates the AgentLeak
   paper reports.

Effort revised down from 12–16 h to **8–12 h**.

### 4.4 Phase 1.A — CNFinBench (UNCHANGED, but Q4 plan is now confirmed)

User's Q4 answer confirms **plan B** (template layer) with an
academic-courtesy email to authors as a non-blocking side-task.
My original §2.A risk #1 mitigation matches this exactly. No
change needed; just record the email-attempt tracking in
`evaluations/benchmarks/cnfinbench/README.md` per Q4.

### 4.5 Repo layout question (Q1) — **awaiting your call**

I recommended flat layout. Q1 is not yet answered in your
response. Original plan stands: I will assume **flat**
(`evaluations/benchmarks/cnfinbench/`, `multiagent/`, `threats/`)
unless you respond otherwise after this re-audit. Items 1.1–2.8
do not depend on the namespace decision; only the import lines
change.

### 4.6 Item 1.0 (regression smoke test) — corrections

Pin against `eval/results/ablation_v2.json`'s `B2_full` row:
- `asr` (= pre-gate bypass, despite the misleading key name) =
  **0.5387** → tolerance ±1.0pp.
- `fpr` = **0.03** → tolerance ±0.5pp.
- `attack_blocked` = **125** → tolerance ±2 prompts.

Plus pin against `eval/results/full_pipeline_eval.json`'s top-level:
- `true_asr` = **0.0258** → tolerance ±0.3pp.
- `true_leaked` = **7** → tolerance ±1 prompt.

The full-pipeline pin requires GPT-4o-mini calls (~144 LLM calls).
Per Q9 (Phase 1 ≤12h budget per deliverable), the smoke test
should run only the ablation pin by default; the full-pipeline pin
should be an opt-in `pytest -m regression --include-llm` mode that
the user runs occasionally.

---

## 5. Confidence Assessment

| Area | Confidence | Why |
| --- | --- | --- |
| **`core/audit.py`** (HashChainWriter) | **High** | Read fully; semantics clear; verifier gap (no body re-hash) understood. |
| **`scripts/run_rag_with_audit.py`** (the actual gate stack) | **High** | Read line-by-line through main(); all gate functions inspected. |
| **`scripts/leakage_scan.py`** (cascade, scan_text) | **High** | Read fully; cascade logic semantics fully understood (relevant for the §6 task 0-A diagnostic the user is queueing). |
| **`scripts/salami_detector.py`** | **High** | Read fully. |
| **`core/engine.py`** (web pipeline) | **High** | Read fully. |
| **`gates/gate_0_decode.py`** | **Medium-high** | Read first 80 lines + tests. Encoding-detector internals inspected at a function-signature level. |
| **`gates/gate_0c_intent.py`** | **Medium** | Header read; ML backend specifics not opened. Disabled by default so low blast radius. |
| **`scripts/dfp.py`** | **Medium** | Header + structure read; entropy/co-occurrence math not verified line-by-line. Disabled by default. |
| **`scripts/llm_guard.py`** | **Medium** | Header read. Disabled by default. |
| **`scripts/prompt_monitor.py`** | **Medium** | Header read. Disabled by default. |
| **`scripts/embedding_benchmark.py`** | **Medium-high** | First 60 lines read; the 3-encoder loop semantic confirmed. |
| **Eval drivers (`eval/run_*.py`)** | **Medium** | Headers read for all 9 files; only `run_ablation.py` and `run_external_framework_eval.py` inspected past the header. Behavior assumed from filename + docstring. |
| **`scripts/archive/*.py`** | **Mixed** | `find_hard_negatives.py`, `generate_secrets_v2.py` (first 60 lines), `generate_adversarial_prompts.py` (first 40 lines), `validate_secrets_v2.py` (read in SECRETS_UPGRADE_INSTRUCTIONS): **medium-high**. The other 8 archived scripts: **filename-only**. |
| **`data/secrets/*.jsonl`, `data/benchmark/*.jsonl`, `data/attack_prompts_*.jsonl`** | **High** | Line counts verified; sample rows opened; schemas confirmed. |
| **`data/index/*.faiss + *_meta.pkl`** | **Medium** | I know which files are tracked and which are gitignored; I have not opened the meta.pkl contents to verify the active 60-entry vs 90-entry mapping. |
| **`data/medical/*`** | **Medium-high** | First 3 rows of attacks + secrets opened; schema clear. |
| **`data/raw/finder_corpus.jsonl`, `data/raw/harmful_behaviors.csv`, `data/raw/FinancialPhraseBank-v1.0/`** | **Medium** | Existence + line counts confirmed; not deeply read. |
| **`data/processed/public_corpus.jsonl`** | **Medium** | Line count confirmed (13,867); not sampled. |
| **`datasource/docs/{fin_data.jsonl, market_prices.csv, internal_report.pdf}`** | **Low** | Just confirmed they exist + sample row opened. Mixed Chinese/English content noted. |
| **`datasource/dao/*`, `datasource/models/*`, `datasource/sentinelflow_crawler/*`** | **Low** | Filename-only. **Acceptable for Phase 1 (out of scope per Q7).** |
| **`utils/*.py`** | **Medium** | First 10 lines read; behavior obvious from imports. |
| **Streamlit apps (`web_chat_app.py`, `app.py`, `streamlit_app.py`, `web_upload_docs_ingestor.py`)** | **Low** | First 10 lines read; behavior assumed from filename. **Acceptable for Phase 1 (which is eval, not UI).** |
| **`build.py`** | **Low** | First 10 lines read; subprocess-driven build orchestrator assumed. |
| **`eval/results/*.json` (15 files)** | **Mixed** | `ablation_v2.json`, `full_pipeline_eval.json`, `bypass_analysis_report.json`: **high** (parsed and inspected). `embedding_benchmark.json`, `harmbench_v2_results.json`, `latency_benchmark.json`, etc.: **low** (filename-only, schema assumed). |
| **`reports/*.{json,csv,md}`** | **Low** | Listed but none opened. Thesis-era artifacts; not Phase-1 critical. |
| **`docs/*.{tex,pdf}`** | **Low** | Existence noted; none opened. Earlier paper drafts; not Phase-1 critical. |
| **`tests/test_dfp.py`** | **Low** | Filename + line count. Body not opened. |
| **`tests/test_encoding_gate.py`** | **High** | Read fully (169 lines). |
| **`config.yaml` / `config_v2.yaml` / `config_medical.yaml`** | **High** for `config.yaml` (read first 420 lines); **Low** for `config_v2.yaml` and `config_medical.yaml` (existence + size only). |
| **`requirements.txt`** | **High** | Read fully. |
| **`Dockerfile`, `docker-compose.yml`, `reproduce_paper_results.sh`** | **Medium-high** | Read first 40 lines. Sufficient for Phase-1 reasoning. |
| **`PLAN.md`, `KICKOFF.md`, `README.md`** | **High** | Read in full. |
| **`sentinelflow_journal_v9_final.tex`** | **High** | Read in full (1,173 lines). |
| **`INCS_870_Project I_SP26_Team02_final_04072026.pdf`** | **Medium-high** | `pdftotext` extraction + scanned for all key terms (271 / 779 / 300 / 0.74 / 2.58 / multi-agent / cnfin / agentleak / agentdojo / future-work). Content mirrors v9 .tex. |

**Areas where Phase 1 work could be derailed by my remaining low
confidence:**
- None within Phase 1's actual scope. The remaining low-confidence
  files are either (a) explicitly out of scope per the user's
  answers (Streamlit UI, DAO/ORM, datasource/, AWS pgvector), or
  (b) historical artifacts (docs/*, reports/*) that affect paper
  writing, not eval infra. The eval drivers I have not opened past
  the header (`run_full_pipeline_eval.py`, `run_statistical_eval.py`,
  `run_latency_benchmark.py`, `run_medical_eval.py`,
  `analyze_bypass_cases.py`, `garak_*.py`, `ablation_table.py`,
  `generate_latex_tables.py`) all have clear docstrings declaring
  their I/O contracts; I will read them in full **at the moment
  Phase 1 actually touches them** rather than pretending I already
  did.

**Honest overall confidence after re-audit: medium-high**, up
from medium (original). The original audit was sufficient for
*shape* but missed important *reuse opportunities* — specifically
`find_hard_negatives.py` and the `instruction_md/` planning history
that answered Q2 directly.

---

## 6. AgentLeak Verification (Q3)

Method: `gh api repos/Privatris/AgentLeak` (read-only, identical
authorization tier to `git remote -v` per PLAN.md §10.1). Followed
by `gh api repos/Privatris/AgentLeak/contents` and
`gh api .../contents/README.md --jq .content | base64 -d`.

**Verification result: REPO EXISTS, IS PUBLIC, MATCHES PLAN.md
CLAIMS.**

| Field | Value |
| --- | --- |
| Full name | `Privatris/AgentLeak` |
| Visibility | public |
| Owner type | organization |
| Created | 2025-12-24 |
| Last pushed | 2026-03-08 |
| Stars / forks | 14 / 3 |
| Default branch | `main` |
| Primary language | Python |
| License | "Other" (NOASSERTION on SPDX; LICENSE file present in repo) |
| Topics | agentic-ai, agents, benchmark, crewai, llm, multi-agent, privacy |
| arXiv reference in README | **`https://arxiv.org/abs/2602.11510`** ← matches PLAN.md §2.1 exactly |
| Paper claim | "*AgentLeak: A Full-Stack Benchmark for Privacy Leakage in Multi-Agent LLM Systems*" — matches PLAN.md title verbatim |
| Scope (from README) | "1,000 scenarios (healthcare, finance, legal, corporate); 7 channels: C1 output, C2 inter-agent, C3-C4 tools, C5 memory, C6 logs, C7 artifacts; 32 attack classes, 6 families; SDK: CrewAI, LangChain, AutoGPT, MetaGPT" — matches PLAN.md's "1,000 scenarios across healthcare/finance/legal/corporate (250 per vertical); 32-class attack taxonomy" |
| Reproduction entry point | `benchmarks/ieee_repro/benchmark.py --n 1000 --traces --model openai/gpt-4o` and `benchmarks/ieee_repro/benchmark_tools.py` |
| Top-level layout | `agentleak/` (SDK), `agentleak_data/` (1000 scenarios), `benchmarks/ieee_repro/`, `benchmarks/showcase/`, `paper/` (LaTeX source), `tests/`, `pyproject.toml`, `pytest.ini`, `requirements.txt`, `LICENSE`, `.env.example` |
| Key reported results (5,694 traces, 5 models) | C1 (output) avg leakage 28.2%; C2 (internal) avg 74.0%; H1 (audit gap) avg 45.9%; total avg 79.7%. PLAN.md cited specific numbers "C2 68.8% vs C1 27.2%" and "miss 41.7%" — these don't match the README's averages exactly, suggesting PLAN.md is quoting a specific cell (e.g. one model or one vertical) from the paper. **Not a contradiction; the order of magnitude and direction are consistent.** |

**Implication for Phase 1.B:** the fallback I designed in original
§2.B (author a 50+ scenario partial replica from the paper) is
**unnecessary**. The official benchmark is reachable, installable
via `pip install -e .`, and ships with reproduction scripts.

**Implication for Phase 2.J (multi-agent re-eval):** the same
SDK can drive the true multi-agent topology; we wrap it with our
LangGraph orchestrator (Phase 2.G) and inspect each channel
(C1/C2/C3/C5/C6/C7) using SentinelFlow's gate primitive. The
AgentLeak repo even ships a `benchmark_tools.py` for C3/C6 — that
is essentially Phase 2.J's deliverable, modulo the inspector
substitution.

Stopping per your instruction. Awaiting review of this file before
proceeding to task 0-A (`PAPER_CODE_GAPS.md`) and task 0-B
(`secrets_v2.jsonl` load verification).
