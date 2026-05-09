# SentinelFlow v2 — Audit & Implementation Proposal

> Read order completed: `KICKOFF.md` → `README.md` → `PLAN.md` →
> `sentinelflow_journal_v9_final.tex` (1,173 lines) →
> `INCS_870_Project_I__SP26__Team02_final_04072026.pdf` (extracted via
> `pdftotext`, 1,279 lines; content essentially mirrors v9 .tex —
> same abstract, same 271 / 779 / 300 / 90-secret numbers, same 7
> contributions, same Future Work list) → codebase walk under
> `core/`, `gates/`, `scripts/`, `eval/`, `data/`, `tests/`,
> `config*.yaml`, `requirements.txt`, `Dockerfile`,
> `reproduce_paper_results.sh`, `streamlit_app.py`, `web_chat_app.py`.

This document is the gating deliverable for this session. **No
business code has been written**; only this file has been
created in the working tree.

---

## Section 1 — Codebase Audit

### 1.1 Module Inventory (path → one-line purpose)

#### Top-level entry points
| Path | Purpose |
| --- | --- |
| `core/engine.py` | `SentinelEngine` class — full pipeline orchestrator used by the Streamlit web UI. Imports gate logic from `scripts/run_rag_with_audit.py` and reuses `scan_text` from `scripts/leakage_scan.py`. |
| `core/audit.py` | `HashChainWriter` — append-only JSONL writer with global + per-session SHA-256 chains; replays existing file on init. |
| `core/config_loader.py` | DB params + `USE_POSTGRES` env-flag helpers. |
| `scripts/run_rag_with_audit.py` | Authoritative CLI evaluation pipeline: Gate 0 Decode → Gate 0a regex (`intent_precheck`) → Gate 0b (`hardblock_precheck`) → Gate 0c (optional ML intent) → Gate 1 (`embedding_secret_precheck`) → Llama-Guard async (optional, disabled) → pgvector retrieval → fallback decision → LLM call → grounding → C4 prompt monitor (disabled by default) → leakage scan → final_output. 1,193 lines; contains every function `engine.py` re-imports. |
| `scripts/leakage_scan.py` | `scan_text` — sentence-split + SBERT-encode + FAISS top-k secret search + hard/soft/cascade tier decisions + optional DFP fusion + optional grounding-action redaction. `load_faiss_index`, `split_sentences` helpers. |
| `scripts/salami_detector.py` | `SalamiSessionTracker` — thread-safe rolling-window (N=10) per-session secret-proximity accumulator; flags when ≥3 queries score ≥0.55 against the same secret_id and the avg ≥ session_alert_threshold. |
| `scripts/prompt_monitor.py` | C4 centroid load + z-score anomaly check (referenced from engine and run_rag, currently disabled). |
| `scripts/dfp.py` | Digital fingerprinting helpers (entropy / co-occurrence / Mahalanobis cluster distance / boost). |
| `scripts/llm_guard.py` | Llama-Guard / Prompt-Guard wrapper used asynchronously by run_rag (off by default). |
| `gates/gate_0_decode.py` | Encoding normalizer — Base64, ROT13, hex, URL, unicode-escape, reversed-text detectors + integrated `decode_gate(query, cfg)`. Pure transformation, never blocks. |
| `gates/gate_0c_intent.py` | Optional zero-shot ML intent classifier wrapper; `enabled: false` in `config.yaml`. |
| `scripts/build_secret_faiss_index.py` | Build `data/index/secrets.faiss` from `data/secrets/secrets.jsonl` with all-MiniLM-L6-v2, `IndexFlatIP`, normalized embeddings. |
| `scripts/build_faiss_index.py` | Build `data/index/finder.faiss` from `data/processed/public_corpus.jsonl` (note: only used in legacy CPU path; production retrieval uses pgvector). |
| `scripts/build_prompt_centroid.py` | Build C4 centroid pickle from 100 normal analyst queries. |
| `scripts/embedding_benchmark.py` | Side-by-side L1/L2/L3 discrimination-gap measurement across 3 encoders (already wired for `bge-small-en-v1.5`, `all-mpnet-base-v2`, baseline MiniLM). |
| `scripts/verify_audit.py` | CLI hash-chain verifier (global + session modes). |
| `scripts/eval_finance_attacks.py`, `scripts/eval_real_world.py`, `scripts/b0_spectrum_test.py`, `scripts/boundary_test.py`, `scripts/news_data_test.py` | Legacy thesis-era evaluation drivers (output → `reports/`). |
| `scripts/run_demo.py`, `scripts/latency_benchmark.py` | Demo + per-gate latency benchmark. |
| `scripts/archive/*.py` | 12 archived utility scripts (curate / inspect / scrape) — explicitly marked superseded. |
| `eval/run_ablation.py` | 7-config ablation driver (B0 + 5 ablated + B2_full + B2_single_tau). |
| `eval/run_statistical_eval.py` | 5-run McNemar comparison. |
| `eval/run_latency_benchmark.py` | Publication-quality per-gate latency + plot. |
| `eval/run_medical_eval.py` | Cross-domain pilot driver. |
| `eval/run_full_pipeline_eval.py` | End-to-end LLM evaluation on bypass cases. |
| `eval/run_external_framework_eval.py` | garak + HarmBench-format 1,079-prompt large-scale eval. |
| `eval/analyze_bypass_cases.py` | Bypass root-cause classifier. |
| `eval/generate_latex_tables.py` | Emits `eval/latex_tables/*.tex` from `eval/results/*.json`. |
| `eval/garak_financial_detector.py`, `eval/garak_sentinelflow_adapter.py` | garak integration shims. |
| `web_chat_app.py`, `app.py`, `streamlit_app.py` | Streamlit UIs (chat + forensic dashboard + wrapper). |
| `build.py`, `run_local_scan_docs_ingestor.py`, `run_spider.py`, `web_upload_docs_ingestor.py` | Index/ingestion entry points. |
| `datasource/knowledge_base.py`, `datasource/local_scan_docs_ingestor.py`, `datasource/sentinelflow_crawler/`, `datasource/dao/`, `datasource/models/` | Public-corpus ingestion + ORM (financial_corpus, chat_history, ingestion_tasks, etc.). |
| `tests/test_encoding_gate.py` | 17 unit tests for `gate_0_decode.py`. |
| `tests/test_dfp.py` | Unit tests for digital fingerprinting helpers. |
| `config.yaml`, `config_v2.yaml`, `config_medical.yaml` | Externalized security thresholds; `config.yaml` is the active default loaded by `engine.py` and `run_rag_with_audit.py`. |
| `Dockerfile`, `docker-compose.yml`, `reproduce_paper_results.sh` | Containerized reproduction tooling. |
| `data/secrets/{secrets,secrets_full,secrets_v2}.jsonl` | 60 / 80 / 90-entry secret corpora (v2 is the active 90-entry institutional-grade set with L1/L2/L3 triplets across 6 alpha domains). |
| `data/benchmark/{attack_prompts,normal_prompts,sensitivity_spectrum,custom_strategy_exfil}.jsonl` | 70 / 100 / 20 / 60-row thesis-era datasets. |
| `data/attack_prompts_expanded.jsonl` | 271 paraphrase-expanded attack prompts (the journal-era corpus). |
| `data/attack_prompts_extended.jsonl` | 30-row cross-category attack supplement. |
| `data/medical/medical_secrets.jsonl`, `data/medical/medical_attacks.jsonl`, `data/medical/medical_secrets.faiss` | 20 / 20 medical pilot dataset + standalone FAISS. |
| `data/index/{finder,secrets,secrets_v2}.faiss + *_meta.pkl + normal_centroid.pkl` | Tracked FAISS indexes and centroid pickle. |
| `data/audit/audit_log.jsonl` | 2,194-line cumulative audit log (gitignored). |

#### Configured but disabled-by-default features
- `gate_0c.enabled: false` (zero-shot intent classifier).
- `prompt_monitoring.enabled: false` (C4).
- `dfp.enabled: false`.
- `guard.enabled: false` (Llama-Guard async).
- `salami_detection.enabled: true` is the **only** post-thesis feature toggled on.

### 1.2 Existing Test Coverage

| Suite | Tests | Runs on clean checkout? |
| --- | --- | --- |
| `tests/test_encoding_gate.py` | 17 unit tests across 6 encoding detectors + gate integration. | Yes — pure stdlib + project import; no API key, no network. The paper claims "17/17 passing". |
| `tests/test_dfp.py` | DFP entropy / co-occurrence / cluster-distance unit tests (~295 LOC). | Yes — pure stdlib + numpy. |

**What is NOT tested** (explicit gaps to surface to the user before Phase 1 starts):
- **No unit tests** for `core/audit.py` hash-chain semantics, despite the paper claiming "100% audit chain integrity." Verification is done end-to-end via `scripts/verify_audit.py` against a live audit log.
- **No unit tests** for `scripts/leakage_scan.py` `scan_text` (sentence split, soft/hard/cascade tiering).
- **No unit tests** for `scripts/salami_detector.py` `SalamiSessionTracker`.
- **No unit tests** for the merged `rule_gate` in `scripts/run_rag_with_audit.py` (`intent_precheck` + `hardblock_precheck`).
- **No unit tests** for `embedding_secret_precheck` dual-threshold logic.
- **No regression suite** that would catch a silent change in B2 ASR after Phase-1-F embedding swap (Deliverable F's DoD references "preserve v9 numbers" but there is no automated guard for this — only the JSON files in `eval/results/`).
- All 1,079-prompt external framework results live as a single JSON artifact (`eval/results/external_framework_eval.json`) without a regression test.

This means Phase 2's "existing single-agent flow continues to pass all v9 tests unchanged" DoD (Deliverable G) currently maps to two unit-test files plus end-to-end JSON snapshots. Anything that is not encoding-gate or DFP behavior has no automated guard. A trivial `pytest` smoke test that runs `eval/run_ablation.py --config B2_full` against a tiny fixture should be a Phase-1-A0 add (proposed below).

### 1.3 Integration Points for Upcoming Work

- **Where would a Phase-2 "channel inspector" plug in?**
  Today there is exactly one channel: user → SentinelEngine.run_query → user. C2/C3/C4/C5/C6/C7 channels do not exist as code. The natural seam is `core/engine.py:run_query` lines 98–493: every existing pre-/post-LLM step (Gate 0 Decode, rule_gate, embedding_secret_precheck, salami_tracker, retrieve, grounding_validate, scan_text, audit append) is a function call against `(text, ctx)` with explicit audit logging. A new Channel inspector should live in `multiagent/inspector.py` (new module) and reuse the same `(text → embedding → secret_index search → tier decision)` primitive that `embedding_secret_precheck` (line 270 of `run_rag_with_audit.py`) and `scan_text` (line 59 of `leakage_scan.py`) already implement. **The cheapest implementation reuses both, parameterized by sensitivity ceiling**, rather than authoring a new detector.

- **Where does the audit hash chain currently get written and verified?**
  - Writer: `core/audit.py` `HashChainWriter` — single class, two chains (global `prev_hash` + per-session `session_prev_hash`), JSONL append, replay on construct. Used by `scripts/run_rag_with_audit.py` (CLI) and `core/engine.py` (web). Default path: `data/audit/audit_log.jsonl`.
  - Verifier: `scripts/verify_audit.py` — global + session modes. Note: verifier reads `event_hash`/`prev_hash` keys but does **not** re-hash the canonical body to confirm `event_hash` itself is correct (it only checks chain linkage). Tampering with a body without changing `event_hash` would not be detected by the current verifier; this is a real but bounded limitation. Worth flagging if the threat-model section of v10 wants stronger claims.
  - Per-edge / Merkle root chain (Deliverable I) does not exist; it would be added as new fields in the same record schema, written by an extended writer subclass.

- **Where is the embedding model loaded (Phase 1.F)?**
  Three load sites, all hard-pinned to `sentence-transformers/all-MiniLM-L6-v2`:
  1. `core/engine.py:29` — `SentenceTransformer(model_name)` (reads `embedding.model_name` from config.yaml, default = MiniLM).
  2. `scripts/run_rag_with_audit.py:572` — same env, same default.
  3. `scripts/build_secret_faiss_index.py:13` (constant) and `scripts/build_faiss_index.py:13` (constant) — **hard-coded** module-level constants, NOT config-driven.
  Phase 1.F therefore needs either (a) parameterizing the build scripts to read from config, or (b) a per-model index suffix scheme (`secrets__mpnet.faiss`, `secrets__bge.faiss`) so multiple indexes coexist. `scripts/embedding_benchmark.py` already iterates over three model names but only computes the discrimination gap; it does not rebuild a FAISS index per model.

- **Where is the FAISS secret index built and queried?**
  - **Built by**: `scripts/build_secret_faiss_index.py` (`data/secrets/secrets.jsonl` → `data/index/secrets.faiss` + `data/index/secrets_meta.pkl`). 384-dim, normalized, `IndexFlatIP`. Tracked in git for the v2 variant (`secrets_v2.faiss` / `secrets_v2_meta.pkl`); the canonical 90-entry index loaded by config is `data/index/secrets.faiss` (gitignored — must be rebuilt locally from `data/secrets/secrets.jsonl`).
  - **Queried in**: `scripts/leakage_scan.py:154` (`secret_index.search`), `scripts/run_rag_with_audit.py:282` (`secret_index.search` inside `embedding_secret_precheck`), `scripts/salami_detector.py:67` (`secret_index.search`). All three pass an L2-normalized `float32` query vector; the abstraction is consistent.

- **Where are amplifier keywords / sensitive object lists stored (Phase 3.K adaptive attack)?**
  Single source of truth: `config.yaml` — verified counts:
  - `policy.intent_rules` — 6 categories (INJ_01, SYS_01, AUD_01, INT_01, EXF_01, HYP_01) with embedded regex patterns.
  - `policy.hard_block.exfil_verbs` — **13 entries**.
  - `policy.hard_block.sensitive_objects` — **23 entries**.
  - `query_precheck.intent_amplifiers` — **62 entries** (matches the paper's "62 keywords" claim exactly).
  - `policy.hard_block.direct_patterns` — 9 patterns.
  These three lists ARE the white-box attack surface for Deliverable K and need to be passed to the GPT-4o adaptive-attacker generator verbatim.

### 1.4 Hidden Technical Debt That Will Block Phase 1 or Phase 2

These are concrete, file-and-line specific. Vague debt is not listed.

1. **Two divergent default thresholds for Gate 1** (silent inconsistency).
   `core/engine.py:168` uses `pre_cfg.get("threshold", 0.75)` while `scripts/run_rag_with_audit.py:745` uses `pre_cfg.get("threshold", 0.70)`. The active `config.yaml` sets `query_precheck.threshold: 0.75`, so production behavior is consistent today. But any code path that does not set the config key (e.g. the AgentLeak runner Phase 1.B will write) would behave differently between web and CLI. Phase 1 should normalize this to a shared constant in `scripts/run_rag_with_audit.py`.
2. **Engine and CLI are partially parallel implementations.** `core/engine.py` re-imports `rule_gate`, `embedding_secret_precheck`, `build_prompt`, `build_fallback_prompt`, `call_llm`, `grounding_validate` from `scripts/run_rag_with_audit.py`, but its main `run_query` body duplicates ~200 lines of orchestration logic from `run_rag_with_audit.py:main`. The C4 prompt-monitoring block alone is duplicated nearly verbatim (engine.py 286–321 ≈ run_rag 1066–1103). Phase 2 should extract a `Pipeline` class to a single module before adding multi-agent channels, otherwise every channel inspector will need to be wired in twice.
3. **`scripts/build_faiss_index.py` and `scripts/build_secret_faiss_index.py` hard-code the embedding model name** (lines 13 of both files). Phase 1.F cannot complete without either parameterizing these scripts or adding a CLI flag.
4. **`config.yaml` has a hard-coded production DB host (`18.220.95.90`) with the password `root`.** This is committed in git history. Out of scope for this audit, but worth noting because Phase 1 evaluation runs that hit `USE_POSTGRES=true` would need credentials rotated; the safer default is to keep `USE_POSTGRES=false` for all Phase 1 runs (which is what `Dockerfile` already sets).
5. **The 90-entry secrets corpus index file `data/index/secrets.faiss` is gitignored** but `data/secrets/secrets.jsonl` (the source) is tracked. This means a fresh checkout has the source but not the index; `python scripts/build_secret_faiss_index.py` must run before any benchmark. The Phase 1 `make reproduce-<deliverable>` targets need to depend on this build step.
6. **`scripts/verify_audit.py` does not re-compute `event_hash` from the body** (it only checks chain linkage between `prev_hash` and the previous `event_hash`). Per Section 1.3 above; relevant to Phase 2.G and 2.I when the threat model is formalized.
7. **No `make` / `Makefile` exists.** PLAN.md Section 7 says "All randomized experiments use seeded RNG. Reproducibility scripts checked into repo, invoked via `make reproduce-<deliverable>`". Today the equivalent is `reproduce_paper_results.sh` (a single bash script). Phase 1 should add a real Makefile or click-CLI to honor that DoD.
8. **`scripts/run_rag_with_audit.py` and `core/engine.py` both contain a gigantic `if rag_mode == "fallback_general" / else` block** (engine 248–473, run_rag 904–1156) that duplicates ~95% of code between the two branches. This is not a Phase 1 blocker but is a foreseeable merge-conflict generator if Phase 2 adds new gates.
9. **`reports/` and `eval/results/` both contain JSON artifacts**. `.gitignore` ignores `reports/` but tracks `eval/results/`. The split is historical (thesis vs journal) and confusing. Phase 1 should write all new artifacts to `eval/results/` exclusively.
10. **No `garak` dependency pin.** `eval/run_external_framework_eval.py` imports garak probes but `requirements.txt` does not list garak; it must already be installed locally for that script to work. Phase 1 should pin `garak` in `requirements.txt` or factor it into a separate `requirements-eval.txt`.

### 1.5 Paper-Code Reconciliation

> Question from KICKOFF.md §1: "does the codebase match what `sentinelflow_journal_v9_final.tex` describes? Note any gap between paper claims and implementation reality."

| Paper claim | Code reality | Gap? |
| --- | --- | --- |
| 4 pre-LLM gates (Decode, 0a regex, 0b verb×obj, 1 embedding) + 2 post-LLM (grounding advisory, leakage scan) | `gate_0_decode.py` + `intent_precheck` + `hardblock_precheck` (merged into `rule_gate`) + `embedding_secret_precheck` + `grounding_validate` + `scan_text`. | **Match.** |
| 62 intent amplifier keywords | `config.yaml:241` list — counted **62 entries**. | **Match.** |
| 13 exfiltration verbs × 23 sensitive objects | `config.yaml` `exfil_verbs` (13) × `sensitive_objects` (23). | **Match.** |
| 90-entry secret corpus, 6 alpha domains, L1/L2/L3 triplets | `data/secrets/secrets_v2.jsonl` has **90 lines**. The active `data/secrets/secrets.jsonl` has **60 lines** — this is the older corpus. | **Mismatch worth flagging.** The paper's headline 2.58% / 53.9% bypass numbers are reported on the 90-entry corpus. To reproduce them, `data/secrets/secrets.jsonl` must be replaced with `secrets_v2.jsonl` content (or `paths.secret_index` must be repointed to `data/index/secrets_v2.faiss`). The README does not document this swap. Open question for the user. |
| 271 paraphrased adversarial prompts | `data/attack_prompts_expanded.jsonl` = **271 lines**. | **Match.** |
| 100 normal analyst queries (C4 baseline + FPR) | `data/benchmark/normal_prompts.jsonl` = **100 lines**. | **Match.** |
| 20-entry sensitivity spectrum (10 L0 + 10 L1) | `data/benchmark/sensitivity_spectrum.jsonl` = **20 lines**. | **Match.** |
| 16 audit event types | enumerated in `core/engine.py` and `run_rag_with_audit.py` audit calls — 14 unconditional + 2 conditional (`encoding_detected`, `gate_0c`, `session_salami_check`, `prompt_monitoring`); README says 14 total. | Minor numeric drift between README (14), paper (16), and code (≥16 if you count conditional events). Not a Phase-1 blocker. |
| Gate 1 P50 = 14.82 ms; end-to-end gates P50 = 28.75 ms | `eval/results/latency_benchmark.json` exists. | **Trust the JSON; not re-validated this session.** |
| Audit chain 100% verified | `scripts/verify_audit.py` checks **chain linkage**, not body integrity (does not re-hash `event_hash`). | **Partial gap.** Paper's "tamper-evident" wording is supported by the chain construction in `core/audit.py`, but the verifier could not detect a body edit that simultaneously updated `event_hash`. Worth noting in the threat-model formalization (Deliverable M). |
| Multi-agent / inter-agent channels | **Does not exist in code.** Paper's Section II-F (Agentic Security) discusses arXiv:2601.11893 conceptually only. | **As expected — that is the entire Phase 2.** |
| CNFinBench / AgentLeak / AgentDojo benchmarks | **Not integrated.** `eval/run_external_framework_eval.py` integrates garak + author-created HarmBench-format only. | **As expected — that is the entire Phase 1 (A/B/C).** |
| `make reproduce-<deliverable>` | Only `reproduce_paper_results.sh` (bash). | Minor process gap. |
| Hard-negative FPR set | Does not exist. Paper's Section IV-G "Limitations" enumerates this as future work. | **As expected — Deliverable E.** |

**Bottom line:** the v9 paper accurately describes the single-agent pipeline as built. Where the paper says "future work" or "limitation," that gap is real. Phase 1 closes 5 of those 6 limitations (FPR set, salami eval, embedding ablation, two external benchmarks); Phase 2 closes the multi-agent gap; Phase 3 closes the adaptive-attack and PoisonedRAG gaps.

---

## Section 2 — Reading of PLAN.md

For each deliverable: existing reuse, new modules, dependencies (with justification), required external resources, effort estimate (pessimistic), top risks.

> Layout note: PLAN.md §8 prescribes `sentinelflow/multiagent/`,
> `sentinelflow/evaluations/benchmarks/cnfinbench/`, etc. — i.e. a
> top-level `sentinelflow/` namespace package. The current repo is
> flat at the root (`core/`, `gates/`, `scripts/`, `eval/`,
> `data/`, `tests/`) with imports like `from core.audit import …`
> rather than `from sentinelflow.core.audit import …`. Introducing
> the prescribed namespace would require updating every import
> across ~50 files. **My recommendation, defended in §3, is to
> keep paths flat** (e.g. `evaluations/benchmarks/cnfinbench/`,
> `multiagent/`) and document the discrepancy with PLAN.md §8 as a
> deliberate scope-cut. This is flagged as Open Question #1.

### Phase 1

#### Deliverable A — CNFinBench Safety Subset Integration

- **Existing reuse**:
  - `scripts/run_rag_with_audit.py:rule_gate / embedding_secret_precheck / build_prompt / build_fallback_prompt / call_llm` — turn-by-turn gate execution.
  - `scripts/leakage_scan.py:scan_text` — per-turn HICS scoring substrate (cosine score on the response is already what the leakage scan computes).
  - `core/audit.py:HashChainWriter` — every turn must append to the chain.
  - `eval/run_external_framework_eval.py` — closest existing template (loads external prompts, runs them through gate stack, records bypass + leakage).
- **New modules**:
  - `evaluations/benchmarks/cnfinbench/adapter.py` — translate CNFinBench upstream record → SentinelFlow input format (query, expected harm category, persona id, strategy id).
  - `evaluations/benchmarks/cnfinbench/multi_turn_runner.py` — driver: GPT-4o (attacker) vs. GPT-4o-mini (defender behind SentinelFlow), 5–10 turns per session, with persona × strategy iteration.
  - `evaluations/benchmarks/cnfinbench/hics_scorer.py` — HICS (Harmful Instruction Compliance Score) computation per session (0–100).
  - `evaluations/benchmarks/cnfinbench/english_adapter.py` — translate Chinese CNFinBench records into English (paraphrase via GPT-4o + manual review of templates).
  - `evaluations/benchmarks/cnfinbench/README.md` + `LICENSE_NOTES.md` — DoD requirement.
- **Deps**: `openai` (already pinned). Optional: `tenacity` for retry on rate limits (~5 LOC; can avoid with manual backoff).
- **External resources from user** (BLOCKING):
  - CNFinBench dataset access: arXiv:2512.09506 says the corpus is primarily Chinese; Open Question #4.
  - GPT-4o quota for attacker (estimate 50 cells × 7 strategies × 8 turns = 2,800 attacker-side calls).
  - GPT-4o-mini quota for defender (same 2,800 calls).
  - English-adaptation review pass (a domain expert spotting bad translations).
- **Effort (pessimistic)**: 25–30 hours, dominated by English adaptation + persona QA, not by code.
- **Top risks**:
  1. Dataset gated / language barrier ⇒ adapter cannot ingest. *Mitigation*: build a CNFinBench-format **template** layer first, parameterized by 17 personas × 7 strategies, and seed it from the paper's described categories; fall back to author-translated subset if upstream is unavailable.
  2. HICS scoring is paper-defined but not open-sourced. *Mitigation*: implement the algorithm from arXiv:2512.09506 §4 (or whichever section defines HICS) and document divergence in `cnfinbench/README.md`.
  3. Cost: 5,600 calls × ~$0.50/1K input tokens × ~1K tokens/call ≈ $3 — small, but multiply by 5–10× for retries, persona shaping, and the inevitable re-run after a bug fix.

#### Deliverable B — AgentLeak Finance Subset (Single-Agent C1)

- **Existing reuse**: same as A — `rule_gate`, `embedding_secret_precheck`, `scan_text`, `HashChainWriter`. Plus `eval/run_external_framework_eval.py` as a structural template.
- **New modules**:
  - `evaluations/benchmarks/agentleak/loader.py` — clone/parse `Privatris/AgentLeak` finance subset.
  - `evaluations/benchmarks/agentleak/single_agent_runner.py` — flatten the multi-agent task into one prompt; record SentinelFlow gate decisions + true leakage per scenario.
  - `evaluations/benchmarks/agentleak/comparator.py` — produce the v9-internal (271) vs. AgentLeak (250) comparison table; flag any cross-table delta >5pp.
  - `LICENSE_NOTES.md`.
- **Deps**: none new; `gitpython` is overkill, just shell-clone in a setup script.
- **External resources**: GitHub access to `Privatris/AgentLeak` (Open Question #3). GPT-4o-mini quota for ~250 LLM calls (ASR negligible cost).
- **Effort (pessimistic)**: 12–16 hours.
- **Top risks**:
  1. Repo access gated. *Mitigation*: AgentLeak paper (arXiv:2602.11510) describes 250 finance scenarios; if the repo is unreachable we can still author a reduced replica from the paper's taxonomy as a stop-gap, clearly labeled as a partial reproduction.
  2. Sensitive-entity ground-truth annotations may not be one-to-one with SentinelFlow's L0–L3 spectrum. *Mitigation*: keep the AgentLeak annotations verbatim and produce a side-by-side table; do not coerce labels.

#### Deliverable C — AgentDojo Banking Suite

- **Existing reuse**: `rule_gate`, `embedding_secret_precheck`, `scan_text`. Tool-calling is **not** in the current pipeline; it must be added.
- **New modules**:
  - `evaluations/benchmarks/agentdojo/wrapper.py` — wrap AgentDojo banking tools so the SentinelFlow channel inspector intercepts C3 (tool-input) and C4 (tool-output).
  - `evaluations/benchmarks/agentdojo/runner.py` — runs the banking suite under benign + injection conditions; reports utility + security separately.
  - **Channel inspector primitive** — needs to land here as a Phase-1 dependency, even though the IFG abstraction is Phase-2 (Deliverable G). The minimum viable inspector is "embed-and-score against secret index" — a single function that wraps `embedding_secret_precheck` to operate on a tool I/O string. This is intentional: the same primitive then becomes the C3/C4 inspector in Phase 2.
- **Deps**: `agentdojo` (PyPI: `agentdojo`; pin a commit SHA). New dep — justify: the deliverable explicitly requires AgentDojo; alternative is reimplementing the banking suite (not viable in scope).
- **External resources**: AgentDojo install + tool catalog. GPT-4o-mini quota for tool-using agent runs (estimate ~100 banking tasks × ~5 tool calls = 500 LLM calls).
- **Effort (pessimistic)**: 18–24 hours, dominated by tool-calling adapter, not the eval driver.
- **Top risks**:
  1. AgentDojo's tool-calling agent contract may not align with the OpenAI Responses API used in `scripts/run_rag_with_audit.py:call_llm`. *Mitigation*: keep AgentDojo's own agent runner intact; SentinelFlow only inspects the I/O strings, not the agent. This makes integration far cheaper but means Phase 1.C's "Utility" metric is whatever AgentDojo reports natively.
  2. Smoke-test budget (5 minutes per PLAN.md §7). *Mitigation*: subset the suite to 5 scenarios for the smoke test.

#### Deliverable D — Multi-Turn Salami Attack Evaluator

- **Existing reuse**:
  - `scripts/salami_detector.py:SalamiSessionTracker` (already wired into `core/engine.py` and toggled on in `config.yaml`) is the runtime detector; its accumulator output is the data we need to plot the cumulative-by-turn curve.
  - `data/secrets/secrets_v2.jsonl` — L3 entries with explicit parameters; the decomposition prompt seeds itself from them.
  - `scripts/run_rag_with_audit.py:embedding_secret_precheck`, `scripts/leakage_scan.py:scan_text` — per-turn evaluation.
  - `core/audit.py` — every turn already appends to the chain.
- **New modules**:
  - `evaluations/internal/salami/decomposer.py` — given an L3 secret, GPT-4o emits N (≥7) benign-looking sub-questions that collectively cover all parameters.
  - `evaluations/internal/salami/runner.py` — turn-by-turn driver that feeds the sequence to `core.engine.SentinelEngine` (or a thin wrapper of `run_rag_with_audit`'s gate stack), captures per-turn cumulative leakage, records cascade trigger turn.
  - `evaluations/internal/salami/plot.py` — cumulative-leakage-by-turn curve (matplotlib).
- **Deps**: `matplotlib` is already used by the latency benchmark. No new deps.
- **External resources**: GPT-4o quota for ≥100 sequences × 7 turns = 700 attacker calls; GPT-4o-mini for the same as defender.
- **Effort (pessimistic)**: 14–18 hours.
- **Top risks**:
  1. The decomposer must produce **innocent-looking** sub-queries; if it produces queries that trigger Gate 1 individually (i.e. the LLM disobeys the "innocent" instruction), we are not measuring salami. *Mitigation*: filter generated sub-queries through Gate 0a/0b/1 in dry-run; reject any sub-query that scores ≥0.55 individually. Loop until N innocent ones survive.
  2. Cascade-trigger statistics depend on session-window length (currently 10 in `config.yaml`). The paper's threshold-tuning data is internal; we may need to sweep `min_targeting_queries` and `session_alert_threshold`.

#### Deliverable E — Hard-Negative FPR Set

- **Existing reuse**:
  - `data/benchmark/sensitivity_spectrum.jsonl` (20 rows: 10 L0 + 10 L1) is the seed: each entry is annotated with its target alpha domain and shares vocabulary with L2/L3.
  - `data/benchmark/normal_prompts.jsonl` (100 rows) is a pre-existing benign set but is **not** vocabulary-overlapping with the 6 alpha domains; this deliverable is specifically a harder distribution.
  - `data/secrets/secrets_v2.jsonl` — group_id field already organizes the corpus into L1/L2/L3 triplets across 6 domains, so each L1 entry is the natural seed for an "L1-boundary" FPR query.
  - `scripts/run_rag_with_audit.py` gate stack — this deliverable does not need new evaluation infra, only new data.
- **New modules**:
  - `evaluations/internal/hard_negatives/seeds.jsonl` — ~96 hand-authored queries (6 domains × 16 queries), each annotated with the target L2/L3 secret it borders.
  - `evaluations/internal/hard_negatives/runner.py` — runs the set through the gate stack; reports FPR-on-hard-negatives separately from the existing 100-query benign baseline.
- **Deps**: none.
- **External resources**: a finance-literate human author (the user or supervisor) to confirm queries are genuinely benign at L1.
- **Effort (pessimistic)**: 8–10 hours, dominated by the authoring step.
- **Top risks**:
  1. Authoring circularity (same risk the v9 paper acknowledges) — the same team that built the gates is now constructing the hard negatives. *Mitigation*: stratify by domain and have a second reviewer; document this in the paper as a known limitation rather than hide it.

#### Deliverable F — Embedding Model Ablation

- **Existing reuse**:
  - `scripts/embedding_benchmark.py` already iterates `all-MiniLM-L6-v2`, `all-mpnet-base-v2`, `bge-small-en-v1.5` and computes the L2–L1 discrimination gap (Table XIII in v9 — `Gap = 0.099` / `0.123` / `0.046`). This is the seed.
  - `scripts/build_secret_faiss_index.py` — must be parameterized by model name (currently hard-coded; see Tech Debt #3).
  - `eval/run_ablation.py` and `eval/run_full_pipeline_eval.py` — the same drivers that produce the deployed-model numbers.
- **New modules**:
  - `evaluations/internal/embedding_ablation/build_indexes.py` — for each candidate encoder, build `data/index/secrets__<model>.faiss` + `_meta.pkl`.
  - `evaluations/internal/embedding_ablation/run_compare.py` — for each encoder, run the full B2 pipeline against the 271 attacks + 100 normals + 100 hard-negatives + 20 spectrum, and produce a per-model TPR / FPR / true ASR / P50 / P95 latency table.
- **Deps**: `BAAI/bge-large-en-v1.5` weights via `sentence-transformers` (no new pip install; just a download). For a finance-finetuned encoder, candidates are FinBERT-derived encoders such as `yiyanghkust/finbert-pretrain` (BERT-style, will need pooling) or `voyageai/voyage-finance-2` (API-only, paid). Open Question #5.
- **External resources**: ~1.3 GB download for `bge-large` + ~0.4 GB for `all-mpnet-base-v2` (probably already cached). GPU optional for `bge-large` to keep latency comparable.
- **Effort (pessimistic)**: 10–14 hours (including index rebuild × 3, eval rerun × 3).
- **Top risks**:
  1. A finance-finetuned encoder may have different output dim → FAISS index incompatible. *Mitigation*: the build script always reads `dim` from the encoder; per-model index keeps things isolated.
  2. Latency comparison is unfair on CPU for `bge-large`; GPU may not be available. *Mitigation*: report both CPU + GPU where feasible; if no GPU, **document the asymmetry** and recommend MiniLM-or-mpnet for the v10 deployment numbers, with bge-large as "future work pending GPU" (this is what the v9 paper essentially does already).

### Phase 2

#### Deliverable G — Information Flow Graph Module

- **Existing reuse**:
  - `core/audit.py` for the audit substrate (extended to per-edge chains in I).
  - The single-channel detection primitive that already lives in `embedding_secret_precheck` and `scan_text` — wrap it as `Inspector` and parameterize by sensitivity ceiling.
  - `core/engine.py:SentinelEngine` as the single-agent reference; multi-agent orchestrator wraps multiple `SentinelEngine`-equivalent nodes.
- **New modules**: as PLAN.md §5.G enumerates — `multiagent/ifg.py` (graph/edge/node types), `multiagent/channels.py` (C1–C7 enum + per-channel policy hooks), `multiagent/inspector.py` (the wrapped detection primitive), `multiagent/agent_wrapper.py` (each agent has role / sensitivity_max / identity / permission set), `multiagent/orchestrator.py` (LangGraph driver), `multiagent/policies/role_policy.yaml` + `multiagent/policies/flow_policy.yaml`.
- **Deps**: `langgraph` (PyPI). New dep — justify: PLAN.md §5.G makes LangGraph the orchestration choice; rationale per PLAN ("built-in checkpointing, easier audit"). Pin a recent stable release. No conflict expected with current pins, but verify against `langchain-core==1.2.15` (Open Question #8).
- **External resources**: none; all internal.
- **Effort (pessimistic)**: 35–45 hours. This is the single largest deliverable.
- **Top risks**:
  1. LangGraph version conflict with the pinned `langchain-core==1.2.15`. *Mitigation*: pre-flight `pip install --dry-run` and bump langchain-core if needed.
  2. The "single-agent flow continues to pass all v9 tests unchanged" DoD relies on tests that mostly do not exist (see §1.2). *Mitigation*: as a Phase-1-A0 step, write a regression smoke test that pins B2_full ASR / FPR within ±0.5pp of `eval/results/ablation_v2.json`.

#### Deliverable H — Three Concrete Multi-Agent Scenarios (A, B, C)

- **Existing reuse**: Deliverable G's IFG + inspector. AgentLeak finance subset (Deliverable B) becomes the attack corpus for Scenario A. AgentDojo wrapper (Deliverable C) becomes Scenario C.
- **New modules**:
  - `multiagent/scenarios/a_customer_pipeline.py` — CustomerAgent (L0) / ResearchAgent (L3) / SalesAgent (L1) topology + A1/A2/A3 attack scripts.
  - `multiagent/scenarios/b_privilege_escalation.py` — reproduce arXiv:2601.11893's anonymous-intermediate attack; defense via identity propagation + delegation hash.
  - `multiagent/scenarios/c_tool_io.py` — reuse Deliverable C's wrapper.
- **Deps**: none beyond G.
- **External resources**: GPT-4o-mini quota for multi-agent runs (each AgentLeak scenario in true MAS mode is 3–5× the single-agent token budget).
- **Effort (pessimistic)**: 30–40 hours (10–14 per scenario).
- **Top risks**:
  1. Scenario B's defense (delegation chain hash) may not reproduce arXiv:2601.11893 cleanly. *Mitigation*: implement identity propagation as the primary defense; treat the hash chain as a logging-side reinforcement.
  2. Scenario A's "C2 must redact L3 content when passing to a SalesAgent whose sensitivity_max is L1" is a strict policy — initial ASR may be high. *Mitigation*: that itself is the result; honest reporting (per PLAN.md §5.J) is the DoD.

#### Deliverable I — Cross-Agent Salami Tracker + Per-Edge Hash Chain

- **Existing reuse**: `scripts/salami_detector.py` (single-key tracker; extend to (originating_user, strategy_domain) keys). `core/audit.py` (extend writer with per-edge chains and a periodic Merkle-root row).
- **New modules**: `multiagent/cross_agent_salami.py` (extended tracker), `multiagent/edge_chain.py` (per-edge writer + Merkle accumulator + new audit event types `edge_chain_root`, `edge_chain_segment`).
- **Deps**: none (Merkle tree is ~30 LOC over hashlib).
- **External resources**: none.
- **Effort (pessimistic)**: 14–18 hours.
- **Top risks**: regression on the existing single-chain audit. *Mitigation*: keep the global chain unchanged; add per-edge chains as a parallel structure with their own verifier mode in `scripts/verify_audit.py`.

#### Deliverable J — Multi-Agent Re-evaluation

- **Existing reuse**: Deliverable B's AgentLeak runner; Deliverable G's IFG; `core/audit.py`.
- **New modules**: `evaluations/benchmarks/agentleak/multi_agent_runner.py` — same 250 scenarios, true multi-agent topology, per-channel (C1/C2/C3/C5) leak-rate breakdown.
- **Deps**: none beyond G.
- **External resources**: GPT-4o-mini quota for 250 scenarios × ~3× single-agent cost ≈ ~750 effective calls.
- **Effort (pessimistic)**: 8–12 hours (most of the work is in B, G, H).
- **Top risks**: the comparison table format must match AgentLeak's paper exactly. *Mitigation*: copy their table layout 1:1 from arXiv:2602.11510.

### Phase 3 (lighter sketches)

#### Deliverable K — Adaptive Attack Evaluation

- Reuse: GPT-4o attacker pattern from D + B; `data/secrets/secrets_v2.jsonl`; gate stack.
- New: `threats/adaptive/generator.py` (white-box attacker prompt, parameterized by the **exact** amplifier list / dual thresholds / cascade k from `config.yaml`), `threats/adaptive/runner.py`, `threats/adaptive/report.py` (static-vs-adaptive ASR delta).
- Effort: 12–16 hours.
- Risk: large ASR gap is likely; honest reporting per PLAN.md §5.K.

#### Deliverable L — PoisonedRAG Corpus Injection

- Reuse: `datasource/knowledge_base.py` + 18,516-chunk pgvector corpus + `data/processed/public_corpus.jsonl`.
- New: `threats/poisoned_rag/inject.py` (5–20 crafted chunks targeting specific high-value queries), `threats/poisoned_rag/measure.py`.
- Effort: 8–12 hours.
- Risk: requires write access to a clone of the pgvector index; do **not** run against the production AWS DB. *Mitigation*: build a local pgvector container fixture for L; never inject into the AWS instance.

#### Deliverable M — Threat Model Formalization (Writing)

- Reuse: paper LaTeX scaffolding.
- New: a Section III-X containing IFG formal definition + adversary capabilities + attack surface + security goal. **Writing only**, post Phase 2.
- Effort: 10–14 hours.

#### Deliverable N — Paper Rewrite to v10

- Reuse: v9 .tex.
- New: incorporate Phase 1–3 results, restructure Lit Review using PLAN.md §2 sources, add Industry Deployments paragraph (≥5 named institutions per PLAN.md §2.5), update Limitations + Discussion.
- Effort: 25–40 hours.

### Feasibility Flags

- **A (CNFinBench)** — feasibility depends entirely on dataset access (Open Q #4). If gated, the work degrades to a "CNFinBench-format" template authored by us, which is a meaningful reduction in external validity.
- **C (AgentDojo)** — straightforward if the AgentDojo pip package installs; non-trivial if its agent contract collides with our `call_llm`. Should bench-test in the first hour of the deliverable.
- **F (Embedding F-step)** — the third "finance-finetuned" candidate is unspecified in PLAN.md and asks for our recommendation in this document. **Recommendation: `BAAI/bge-large-en-v1.5`** as the open-source candidate (best discrimination-gap track-record on retrieval tasks; same embedding family as the already-tested `bge-small-en-v1.5`). FinBERT-style encoders need a pooling shim and do not have a competitive sentence-similarity reputation. Open Question #5 for confirmation.
- **G (IFG / LangGraph)** — feasibility OK; risk is the langchain-core pin (Open Q #8).
- **K (Adaptive)** — feasibility OK; the result will likely show a large ASR gap and that is the point.
- **L (PoisonedRAG)** — feasibility OK only if a local pgvector fixture is acceptable; running against AWS is out of bounds (Open Q #7).

---

## Section 3 — Sequenced Implementation Plan

Ordering rationale: PLAN.md §4 mandates Phase 1 before Phase 2.
Within Phase 1, PLAN.md says `F → E → D → A → B → C` is a
recommendation. **I am proposing one deviation**: insert a 30-minute
"Phase 1 prelude" item (1.0) BEFORE F to add a regression smoke
test that pins the v9-deployed B2 numbers. Without that, we have
no automated way to prove F (or anything else in Phase 1) does not
silently regress single-agent performance, and the §5.G DoD
("existing single-agent flow continues to pass all v9 tests
unchanged") is meaningless. Justification: this is one ≤4-hour
item that pays for itself in every later phase. The remainder of
the order matches PLAN.md §4 verbatim.

| # | Item | Phase | Est. (h) | External resource needed first? |
| -- | --- | --- | --- | --- |
| 1.0 | **Add a B2_full regression smoke test** that pins ASR / FPR / pre-gate-bypass within ±0.5pp of `eval/results/ablation_v2.json`. Wire it into `pytest` and document `make test-regression`. | Phase-1 prelude | 3 | No |
| 1.1 | **Bootstrap `evaluations/internal/embedding_ablation/build_indexes.py`** — parameterize the secret-FAISS build by encoder name; produce `secrets__minilm.faiss`, `secrets__mpnet.faiss`, `secrets__bge_large.faiss`. | F | 3 | No |
| 1.2 | Run B2_full × 3 encoders against (271 attacks + 100 normals + 20 spectrum); produce per-encoder TPR / FPR / true ASR / P50 / P95 table. Pick primary for v10. | F | 3 | No (but GPU optional) |
| 1.3 | **Author 96 hard-negative L1-boundary queries** (6 domains × 16 queries each), annotated with target secret. | E | 4 | Human review (user) |
| 1.4 | Build hard-negative runner; report FPR separately from the 100-query benign baseline; integrate into `eval/run_ablation.py`. | E | 2 | No |
| 1.5 | **Salami decomposer** (GPT-4o emits ≥7 sub-queries per L3 secret, filtered for individual innocence); store ≥100 sequences. | D | 4 | OpenAI key (GPT-4o) |
| 1.6 | Salami runner — per-turn cumulative leakage curve, cascade-trigger statistics. Plot. | D | 3 | OpenAI key (GPT-4o-mini) |
| 1.7 | **CNFinBench English-adapted template layer** (17 personas × 7 strategies seeded from arXiv:2512.09506 §4). Skip if upstream available. | A | 4 | Dataset access OR template authorship |
| 1.8 | CNFinBench multi-turn runner (5–10 turns/session, ≥50 cells). | A | 4 | OpenAI key (GPT-4o + GPT-4o-mini) |
| 1.9 | CNFinBench HICS scorer + heatmap CSV + ≥30 broken-session case logs + `LICENSE_NOTES.md`. | A | 3 | No |
| 1.10 | **AgentLeak finance loader** — clone `Privatris/AgentLeak`, parse 250 finance scenarios. | B | 2 | GitHub access (Open Q #3) |
| 1.11 | AgentLeak single-agent runner — flatten each multi-agent task into one prompt; record gate decisions + true leakage; produce v9-internal-vs-AgentLeak comparison table. | B | 4 | OpenAI key (GPT-4o-mini) |
| 1.12 | **AgentDojo install + smoke test** (subset of 5 banking tasks, <5 min). | C | 3 | AgentDojo install |
| 1.13 | AgentDojo runner — full banking suite under benign + injection; report Utility + Security; first version of channel-inspector primitive (wraps `embedding_secret_precheck`). | C | 4 | OpenAI key (GPT-4o-mini) |
| 1.14 | Phase 1 wrap: `make reproduce-phase1`, regenerate all LaTeX tables. | — | 2 | No |
| 2.1 | **Extract a `Pipeline` class** from `core/engine.py` + `scripts/run_rag_with_audit.py` (deduplicate the parallel implementations called out in §1.4 #2 and #8); make the regression test still pass. | G prelude | 4 | No |
| 2.2 | `multiagent/ifg.py` + `multiagent/channels.py` + `multiagent/inspector.py` + `multiagent/agent_wrapper.py` (no orchestrator yet). Unit tests per channel inspector. | G | 4 | No |
| 2.3 | `multiagent/orchestrator.py` (LangGraph driver) + `multiagent/policies/*.yaml`. Existing single-agent flow regression still green. | G | 4 | LangGraph + langchain-core compat (Open Q #8) |
| 2.4 | Scenario A (CustomerAgent / ResearchAgent / SalesAgent with A1/A2/A3 attacks). | H-A | 4 | OpenAI quota |
| 2.5 | Scenario B (privilege-escalation reproduction; identity propagation + delegation hash). | H-B | 4 | No |
| 2.6 | Scenario C (tool I/O — reuses Phase 1.13). | H-C | 3 | AgentDojo |
| 2.7 | Cross-agent salami tracker + per-edge hash chain + Merkle root + verifier extension. | I | 4 | No |
| 2.8 | AgentLeak 250-scenario rerun in true multi-agent mode; per-channel leak rates table. | J | 4 | OpenAI quota |
| 3.x | K, L, M, N as PLAN.md §5 sketches. Out of detailed scope for this proposal. | — | — | Various |

### First Item Sub-plan (Item 1.0 — B2_full regression smoke test)

**Why this is item 1.** Without it, Phase 1.F (encoder swap) and
every Phase 2 step that touches `core/engine.py` or
`scripts/run_rag_with_audit.py` carries an unverifiable risk of
silently regressing the single-agent v9 numbers that the entire
paper depends on.

**Files to create**:
- `tests/test_regression_b2_full.py` — pytest module.
- `tests/fixtures/regression_b2_targets.json` — pinned numbers
  copied verbatim from `eval/results/ablation_v2.json` (B2_full
  row: pre_gate_bypass = 53.9, true_leakage = 2.58, FPR = 3.0).
  Tolerance window ±0.5pp on each.

**No new module under `core/` or `scripts/` is needed for this
item.** It is purely a test scaffold around existing entry points.

**Function signatures** (pytest, no class required):

```python
# tests/test_regression_b2_full.py
import json, pytest, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TARGETS = json.loads((REPO / "tests/fixtures/regression_b2_targets.json").read_text())
TOL_PP = 0.5  # percentage-point tolerance

@pytest.mark.regression
def test_b2_full_against_v9_pin():
    """Run eval/run_ablation.py --config B2_full and compare ASR/FPR/bypass to v9 pin."""
    out = REPO / "eval/results/_regression_b2_full.json"
    subprocess.check_call([
        "python", "eval/run_ablation.py",
        "--config", "B2_full",
        "--output", str(out),
    ], cwd=REPO)
    actual = json.loads(out.read_text())["B2_full"]
    for key in ("pre_gate_bypass_pct", "true_leakage_pct", "fpr_pct"):
        diff = abs(actual[key] - TARGETS[key])
        assert diff <= TOL_PP, f"{key} drifted by {diff:.2f}pp (limit {TOL_PP})"
```

**Test cases the smoke test must cover**:
1. Pre-gate bypass within ±0.5pp of 53.9.
2. True leakage within ±0.5pp of 2.58.
3. FPR within ±0.5pp of 3.0.
4. Exit code 0 from `eval/run_ablation.py --config B2_full`.

**Smoke test** (used to demonstrate completion of item 1.0):
```bash
pytest tests/test_regression_b2_full.py -v -m regression
```
Expected outcome: 1 passed in ~120s on a warm cache (the bottleneck
is loading the SBERT model + 271 prompt encodings; no LLM calls
because `--config B2_full` in `eval/run_ablation.py` does not
invoke the LLM, only the gate stack — confirmed by reading
`eval/run_ablation.py:47–82` (the CONFIGS dict)). Note: this
particular eval driver does **not** need an OpenAI key, which is
why item 1.0 has no external-resource gate and can run first.

**Acceptance**: file diff is two new files only; `pytest -m
regression` is green; `make test-regression` (added in 1.14) wraps
it; the targets JSON is the single source of truth for "what was
true at v9."

### Items requiring external resources before they can start

- **1.5, 1.6** — OpenAI GPT-4o + GPT-4o-mini quota for ~700 + ~700 calls.
- **1.7, 1.8, 1.9** — CNFinBench dataset access OR explicit go-ahead to author the template layer (Open Q #4).
- **1.10, 1.11** — `Privatris/AgentLeak` GitHub access (Open Q #3).
- **1.12, 1.13** — AgentDojo PyPI install + GPT-4o-mini quota.
- **2.3** — confirmation that LangGraph is acceptable as a new dependency and does not break `langchain-core==1.2.15` (Open Q #8).
- **2.4–2.8** — non-trivial OpenAI quota; a rough estimate is in Open Q #2.

---

## Section 4 — Open Questions for the User

1. **Repo layout discrepancy.** PLAN.md §8 prescribes a top-level
   `sentinelflow/` namespace package
   (`sentinelflow/multiagent/`, `sentinelflow/evaluations/…`) but
   the existing repo is flat (`core/`, `gates/`, `scripts/`,
   `eval/`, `data/`). All current imports are `from core.audit
   import …`, `from scripts.leakage_scan import …`. Adopting
   PLAN.md's layout means renaming ~50 import sites. **Should I
   keep the flat layout (and place new code under
   `evaluations/benchmarks/cnfinbench/`, `multiagent/`,
   `threats/`) or invest the import-rewrite session up-front?** My
   recommendation: keep flat.

2. **OpenAI quota.** Phase 1 alone needs roughly:
   - ~700 GPT-4o attacker calls + ~700 GPT-4o-mini defender calls
     for D (salami).
   - ~2,800 GPT-4o + ~2,800 GPT-4o-mini for A (CNFinBench at 50
     cells × 7 strategies × 8 turns).
   - ~250 GPT-4o-mini for B (AgentLeak single-agent).
   - ~500 GPT-4o-mini for C (AgentDojo banking).
   That is ~3,500 GPT-4o + ~4,250 GPT-4o-mini (assume ~1K tokens
   in/out per call). Cost is on the order of $5–20 for Phase 1
   inclusive of retries. **Confirm OpenAI account has the quota
   and that GPT-4o is enabled** (not all accounts are).

3. **`Privatris/AgentLeak` GitHub repo.** Is the user able to
   access this repo? If not, what is the fallback for the 250
   finance scenarios? The arXiv:2602.11510 paper itself describes
   the taxonomy (32 attack classes; 250 finance scenarios) and we
   can author a reduced replica from the paper's tables, but it
   would be a partial reproduction.

4. **CNFinBench dataset.** arXiv:2512.09506 says the corpus is
   primarily Chinese. How should English adaptation be approached:
   (a) translate upstream Chinese → English with GPT-4o + manual
   review, or (b) author a CNFinBench-format template layer
   (17 personas × 7 strategies) seeded from the paper's
   description, with no upstream record-level reproduction? The
   v10 paper would need to clearly disclose either choice. My
   recommendation: (b), and document it as a minor contribution
   per PLAN.md §2.2.

5. **Phase 1.F finance-finetuned encoder.** PLAN.md says "suggest
   `BAAI/bge-large-en-v1.5` or a FinBERT-style encoder; final
   choice in `AUDIT_AND_PROPOSAL.md`." My recommendation:
   **`BAAI/bge-large-en-v1.5`** as the third encoder — same family
   as the already-benchmarked `bge-small-en-v1.5`, well-supported
   in `sentence-transformers`, no pooling shim. FinBERT-style
   alternatives (e.g. `yiyanghkust/finbert-pretrain`) require
   pooling adaptation and have not been validated for
   sentence-similarity. **Should we constrain to open-source-only,
   or are paid API encoders (Voyage, OpenAI text-embedding-3)
   acceptable?** Cost / vendor-lock-in implications.

6. **`data/secrets/secrets.jsonl` versus
   `data/secrets/secrets_v2.jsonl`.** The active corpus pointed to
   by `config.yaml:paths.secret_index` is `data/index/secrets.faiss`
   built from the **60-entry** `secrets.jsonl`, but the v9 paper's
   2.58% / 53.9% headline numbers are reported on the **90-entry**
   `secrets_v2.jsonl`. The 90-entry FAISS exists at
   `data/index/secrets_v2.faiss` but is not the default. **Should
   I switch the default `paths.secret_index` to
   `secrets_v2.faiss` as part of item 1.0, or treat 60-entry as
   "thesis era" and 90-entry as "journal era" with a separate
   `config_journal.yaml`?**

7. **AWS PostgreSQL + pgvector for evaluation runs.**
   `config.yaml` hard-codes `db.host: 18.220.95.90` with the
   password `root`. Phase 1 is best run with `USE_POSTGRES=false`
   (FAISS-only path, which is what the Dockerfile already does).
   **Confirm Phase 1 evals must NOT touch the AWS instance**
   (cost, blast radius, accidental writes). For PoisonedRAG (3.L),
   I plan to spin up a local pgvector docker container as the
   target — confirm this is acceptable.

8. **LangGraph dependency.** Phase 2.G depends on LangGraph. The
   current `langchain-core` pin is `1.2.15`. **Confirm I am
   authorized to add `langgraph` to `requirements.txt` and to
   bump `langchain-core` if the LangGraph install requires it.**
   (PLAN.md §10 says new deps need justification; this is the
   justification — LangGraph is the prescribed orchestration
   layer.)

9. **Compute / time budget.** Is the entire Phase 1 expected to
   run on a single laptop overnight (~8 hours), or is there a
   shared GPU box / cloud machine I should target? This matters
   for the embedding-ablation P50/P95 numbers (`bge-large` on CPU
   is ~5× MiniLM latency). The v9 paper reports CPU-only numbers;
   if the v10 paper wants GPU numbers the encoder ablation needs
   GPU access.

10. **Cross-checked arXiv IDs from PLAN.md §2.** All eight are
    syntactically well-formed (YYMM.NNNNN). The ones I cannot
    independently confirm against my training data (cutoff Jan
    2026) are:
    - **`arXiv:2602.11510` (AgentLeak)** — Feb 2026; post-cutoff.
      I cannot verify the title / author / 250-scenarios-per-vertical
      claim; I am taking PLAN.md at its word.
    - **`arXiv:2512.09506` (CNFinBench)** — Dec 2025; near
      cutoff; treating as authoritative-per-PLAN.
    - **`arXiv:2510.05244` (Indirect Prompt Injections)** — Oct 2025.
    - **`arXiv:2510.07920` (Profit Mirage)** — Oct 2025.
    - **`arXiv:2601.11893` (MAC for Agent Systems)** — Jan 2026.
      *Independently corroborated:* the v9 paper's
      `\bibitem{arxiv_privilege_escalation_2025}` already cites
      this exact ID with the exact same description.
    - **`arXiv:2406.13352` (AgentDojo, NeurIPS 2024 D&B per
      PLAN.md)** — *Inconsistency.* The v9 paper's
      `\bibitem{agentdojo}` cites AgentDojo as
      **`arXiv:2407.01392`**, not 2406.13352. **Which ID is
      correct?** This is the only direct ID conflict between
      PLAN.md and the v9 paper. I will not cite AgentDojo in any
      v10 draft until you resolve which ID is authoritative.
    - **`arXiv:2410.09024` (AgentHarm, ICLR 2025)** — believed
      correct.
    - **`arXiv:2504.15800` (FinDER)** — believed correct.

    All eight are documented as questions rather than
    hallucinated. None are yet baked into any draft text.

---

## Section 5 — What I Will NOT Do (Descope / Defer)

- **Skip entirely (this submission):**
  - Zero-knowledge audit chain (zk-MCP). PLAN.md §6 already marks
    this as v3-paper future work.
  - Differential privacy on query embeddings. Future work mention
    only.
  - Production-grade streaming optimization beyond current P50.
    The 28.75 ms is already within interactive bounds.
  - Cross-domain pilots beyond medical. The medical pilot already
    in v9 (Section 1.5 of this audit) is sufficient for v10's
    generalization claim.
  - Re-architecting the existing single-agent pipeline. Multi-agent
    is additive (per PLAN.md §6).
  - Touching the AWS pgvector instance from any Phase 1 evaluation
    (Open Q #7).
  - Modifying `sentinelflow_journal_v9_final.tex` in this session
    (per PLAN.md §10).

- **Defer until later in the timeline:**
  - **PLAN.md §8 Repository Layout target state** (introducing a
    `sentinelflow/` namespace). I will keep paths flat and
    document this as a deliberate scope cut (Open Q #1).
  - **`Makefile`-based reproducibility** (PLAN.md §7 says `make
    reproduce-<deliverable>`). I will provide the equivalent
    targets via either an extended `reproduce_paper_results.sh`
    or a tiny `Makefile`; either way, this lands at item 1.14
    (Phase 1 wrap), not before.
  - **Strengthening `scripts/verify_audit.py` to re-hash event
    bodies** (Tech Debt #6). Mention as a Phase-2.M (threat-model
    formalization) writing/code item, not a Phase-1 blocker.
  - **`bge-large-en-v1.5` GPU benchmarking** if the user has no
    GPU access (Open Q #9). CPU numbers + a documented asymmetry
    is the fallback.
  - **Running LangGraph alongside the existing pinned
    `langchain-core==1.2.15`** if a version conflict surfaces
    during Phase 2.G install. Fallback: a minimal hand-written
    orchestrator (~150 LOC) with explicit checkpoint hooks. Only
    invoke this fallback if the dep conflict cannot be resolved
    in <2 hours.
  - **CNFinBench upstream reproduction.** If the upstream dataset
    is gated (Open Q #4), I will deliver a CNFinBench-format
    template layer authored from the arXiv:2512.09506 description
    and document the divergence in `cnfinbench/README.md`.
    Faithful upstream reproduction is deferred until access is
    confirmed.
  - **AgentLeak upstream reproduction.** Same fallback structure
    as CNFinBench (Open Q #3).
  - **Phase 3 deliverables (K, L, M, N)** are noted in Section 2
    but not detailed. They are deferred to a later proposal once
    Phase 1 + 2 are stable.

---

## Section 6 — Self-Check on Git Policy

I have read **PLAN.md §10.1 (Git Policy — STRICT — Authoritative)**
and **KICKOFF.md §6**, and I confirm my understanding that **the
following are forbidden without per-command, in-session
authorization from the user (i.e. an explicit sentence in this
chat session granting permission)**:

- **`git push` in any form** — including `git push`, `git push
  --force`, `git push --force-with-lease`, `git push --tags`,
  `git push origin <anything>`, `git push <any-remote>`.
- **`git remote add`, `git remote set-url`, `git remote rm`,
  `git remote rename`** — any write to remote configuration.
- **Direct edits of `.git/config`, `.git/hooks/`, or anything
  inside `.git/`** that could change remote configuration or
  install hooks.
- **`gh pr create`, `gh pr merge`, `gh repo create`,
  `gh repo fork`** — or any other GitHub CLI command that writes
  to a remote.
- **`git svn dcommit`, `git p4 submit`** — or any VCS bridge that
  uploads.
- **Any shell pipe that writes to a remote** — e.g.
  `curl -X POST .../git-receive-pack`, `rsync` to a remote git
  directory.

I additionally confirm:

- **Standing authorization from PLAN.md, KICKOFF.md, earlier
  sessions, or implied by phrases like "please finalize this"
  does NOT count.** Authorization must be per-command and in the
  current chat session.
- **If a workflow seems to require pushing** (CI trigger, share
  with teammate, open a PR), I MUST stop, explain why, and ask
  the user to push manually.
- **If I accidentally execute any forbidden command** (e.g. a
  tool wrapper auto-pushes), I MUST immediately report this in
  chat with full details of what was pushed and where, before
  proceeding with anything else.

**Per-this-session compliance plan:**

- This session writes exactly **one** new file:
  `AUDIT_AND_PROPOSAL.md` (this document), at the repo root.
- The file is left **unstaged** (no `git add`, no `git commit`)
  for the user's review, per the KICKOFF.md "Constraints for This
  Session" line "Do NOT commit anything in this session."
- I will not run any of the forbidden commands above. I have not
  run any of them so far in this session.

**One area I want to flag for explicit user clarification rather
than assume:** does running `git ls-files` (which I used in the
audit to inspect what is tracked under `data/index/` and
`data/secrets/`) count as a write/upload operation? My reading
is **no** — `git ls-files` only reads the index and the working
tree — but I prefer to err on the side of asking. If you consider
even reads of the git plumbing out of scope for an "audit only"
session, let me know and I will avoid them in subsequent sessions.

End of proposal. Stopping for review.
