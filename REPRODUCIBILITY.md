# Reproducibility — Pinned Versions and Environment

> Companion to PLAN.md and the audit-phase docs (AUDIT_AND_PROPOSAL.md
> → V9_REPRODUCTION.md). This file documents every external version
> pin made under Phase-1 item 1.0b ("PIN ALL EXTERNAL MODEL VERSIONS")
> and records the reference environment used for the v9 reproduction
> and Phase-1 baseline runs.
>
> **If you change any pin in this document, update the matching
> reference in `core/config_loader.py:PINNED_REVISIONS` /
> `PINNED_OPENAI_MODEL` / `requirements.txt` / `config*.yaml` and
> append a row to §6 (Change Log).**

---

## 1. Why this file exists

`V9_REPRODUCTION.md` (Part A, 2026-05-08) discovered that the v9
paper's headline ablation numbers were not reproducible without a
~3.7 percentage-point drift in pre-gate bypass rate, despite:
- byte-identical secret-corpus FAISS index (`secrets_v2.faiss`),
- byte-identical secret-corpus source (`secrets_v2.jsonl`),
- byte-identical gate code (`scripts/leakage_scan.py`,
  `scripts/run_rag_with_audit.py:rule_gate / embedding_secret_precheck`),
- byte-identical config (`config_v2.yaml.policy.*` and
  `query_precheck.*`).

The remaining suspected drift source was upstream / numerical:
either the HuggingFace `all-MiniLM-L6-v2` revision shifted, or
`torch` / `transformers` numerical determinism shifted. Item 1.0b
removes both possibilities by pinning every external dependency
that affects gate decisions.

---

## 2. Pinned external versions

### 2.1 Embedding model

| Item | Pinned to |
| --- | --- |
| Model name | `sentence-transformers/all-MiniLM-L6-v2` |
| HuggingFace commit hash | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` |
| Source of truth | `core/config_loader.py:PINNED_REVISIONS` (Python dict) AND `embedding.revision` field in each `config*.yaml` |
| Status as of 2026-05-08 | **Pin equals current HuggingFace `main`** (cross-checked via `git ls-remote https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 refs/heads/main` AND `huggingface_hub.HfApi().list_repo_commits(...)`; both return `c9745ed1...`). The pinned hash corresponds to the upstream commit dated 2025-03-06 with title "Remove deprecated (SEB) evaluation results section". Total 30 commits on `main`. **If a future `git ls-remote` returns a different hash, this is intentional freeze for reproducibility — do not silently update.** |
| Verification (local) | `cat ~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/refs/main` |
| Verification (upstream) | `git ls-remote https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 refs/heads/main` |
| Loaded by | every `SentenceTransformer(...)` call in the codebase passes `revision=` (27 sites total — see §3) |

### 2.2 LLM model (OpenAI)

| Item | Pinned to |
| --- | --- |
| Identifier | `gpt-4o-mini-2024-07-18` (dated snapshot, NOT the alias `gpt-4o-mini`) |
| Source of truth | `core/config_loader.py:PINNED_OPENAI_MODEL` AND `openai_model` field in each `config*.yaml` |
| Loaded by | every `cfg.get("openai_model", …)` fallback in the codebase resolves to this string (8 fallbacks updated) |

### 2.3 Python library exact-patch versions

`requirements.txt` pins the four reproducibility-critical libraries
to **exact patch versions** matching the venv installed at audit
time (2026-05-08). Minor-version pinning still allows patch drift
(e.g., `transformers>=5.0.0,<5.1.0` admits 5.0.0, 5.0.1, 5.0.2 …);
patch-exact pinning eliminates that drift.

| Library | Pin spec | Notes |
| --- | --- | --- |
| `openai` | `==2.24.0` | Was `>=2.20.0,<3.0.0` (audit drift surface); now exact |
| `sentence-transformers` | `==5.2.2` | Already exact pre-1.0b |
| `transformers` | `==5.0.0` | Was unpinned (transitive); now exact. Governs encoder numeric determinism |
| `torch` | `==2.10.0` | Was unpinned (transitive); now exact. Governs numerical determinism |
| `faiss-cpu` | `==1.13.2` | Already exact pre-1.0b |
| `numpy` | `==2.4.2` | Was `>=1.24.0` (very wide); now exact |
| `langchain-core` | `==1.2.15` | Already exact pre-1.0b |
| `langchain-community` | `==0.4.1` | Already exact pre-1.0b |
| `langchain-openai` | `==1.1.10` | Already exact pre-1.0b |
| `langchain-postgres` | `==0.0.17` | Already exact pre-1.0b |
| `langchain-text-splitters` | `==1.1.1` | Already exact pre-1.0b |
| Other libraries | (existing pins retained) | DB/web/data — see `requirements.txt` |

**Upgrade procedure for the four reproducibility-critical libs**
(`transformers`, `torch`, `numpy`, `openai`): the patch-exact pins
prevent silent drift, but they should not be sealed forever. To
upgrade:

1. Relax the pin to a minor band (e.g.
   `transformers>=5.0.0,<5.1.0`) and `pip install -U`.
2. Re-run the V9 reproduction smoke test
   (`eval/run_ablation.py --config B2_full --yaml-config
   config_v2.yaml`).
3. Verify metrics still hold within tolerance (per §5 below).
   - If yes: re-tighten to the new exact patch and append a row
     to §6.
   - If no: report the drift (matching V9_REPRODUCTION.md §3
     methodology), decide whether the upgrade is worth the
     reproduction cost, and either revert or document the new
     baseline.

This mirrors the discipline applied to the HF model revision (§2.1)
and the OpenAI dated snapshot (§2.2): every reproducibility-critical
external should be at a single, citable point.

---

## 3. Affected call sites (audit trail)

### 3.1 SentenceTransformer call sites — all 27 now pinned

Every site loads the pinned revision either via
`emb_cfg.get("revision") or get_pinned_revision(model_name)` (config-aware sites)
or via `get_pinned_revision(MODEL_NAME)` (hardcoded-name sites).

**Active eval path (14 sites):**
- `core/engine.py:31` — Streamlit web pipeline
- `scripts/run_rag_with_audit.py:572` — CLI evaluation pipeline
- `scripts/build_secret_faiss_index.py:58` — secret index builder
- `scripts/build_faiss_index.py:32` — public-corpus index builder
- `scripts/build_prompt_centroid.py:55` — C4 centroid builder
- `scripts/embedding_benchmark.py:118` — encoder ablation driver
- `eval/run_ablation.py:319` — 7-config ablation
- `eval/run_full_pipeline_eval.py:191` — end-to-end LLM eval
- `eval/run_medical_eval.py:170` — cross-domain pilot
- `eval/run_latency_benchmark.py:124` — latency benchmark
- `eval/run_statistical_eval.py:248` — multi-run McNemar's eval
- `eval/run_external_framework_eval.py:236` — garak + HarmBench eval
- `eval/analyze_bypass_cases.py:151` — bypass-case generator
- `eval/garak_financial_detector.py:48` — garak custom detector

**Auxiliary / legacy / production path (13 sites):**
- `web_upload_docs_ingestor.py:30` — Streamlit upload UI
- `datasource/local_scan_docs_ingestor.py:71` — local doc ingestor
- `datasource/sentinelflow_crawler/pipelines.py:40` — Scrapy crawler
- `scripts/search_faiss.py:23` — debug FAISS inspector
- `scripts/eval_finance_attacks.py` (3 sites in B0 / comparison / threshold-sweep modes)
- `scripts/latency_benchmark.py:178` — older legacy latency
- `scripts/boundary_test.py:307` — boundary test
- `scripts/b0_spectrum_test.py:67` — B0 spectrum
- `scripts/news_data_test.py:288` — news-anchored test
- `scripts/eval_real_world.py:191` — real-world eval
- `scripts/archive/find_hard_negatives.py:64` — hard-negative miner

### 3.2 OpenAI fallback sites — 8 updated

Every `or "gpt-4o-mini"` fallback default in code is now
`or "gpt-4o-mini-2024-07-18"`. Sites:

- `web_chat_app.py:21` — `ChatOpenAI(model=...)` direct
- `core/engine.py:243` — engine LLM call
- `scripts/run_rag_with_audit.py` (2 sites: lines 915, 1017 — fallback + RAG paths)
- `scripts/boundary_test.py:250`
- `scripts/latency_benchmark.py:134`
- `scripts/news_data_test.py:228`
- `scripts/eval_finance_attacks.py:193`
- `scripts/eval_real_world.py:136`
- `scripts/b0_spectrum_test.py:60`
- `eval/run_full_pipeline_eval.py:196`
- `eval/run_external_framework_eval.py:245`

### 3.3 Config files — 3 updated

- `config.yaml`: added `embedding.revision`; updated `openai_model`.
- `config_v2.yaml`: same.
- `config_medical.yaml`: same.

---

## 4. Reference environment (audit run, 2026-05-08)

Used for both `V9_REPRODUCTION.md` Part A (no-LLM ablation) and
the planned Part B (LLM full-pipeline reruns). Future reproductions
should match this where possible.

| Component | Value |
| --- | --- |
| Date | 2026-05-08 |
| OS | macOS 14.5 (Darwin 23.5.0, Build 23F79) |
| CPU | Apple M3 (8 cores) |
| RAM | 8 GB |
| Architecture | arm64 |
| Python | 3.12.2 |
| sentence-transformers | 5.2.2 |
| transformers | 5.0.0 |
| torch | 2.10.0 |
| faiss-cpu | 1.13.2 |
| openai | 2.24.0 |
| numpy | 2.4.2 |
| HF model `all-MiniLM-L6-v2` revision | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` |
| OpenAI model | `gpt-4o-mini-2024-07-18` |
| Pinned secret corpus (90-entry) | `data/index/secrets_v2.faiss` md5 `a03fa690a646f7f02cf0b2cc0d70dcab` |
| Pinned secret meta (90-entry) | `data/index/secrets_v2_meta.pkl` md5 `949856e2a3762631dbeb4161c190f5cd` |

---

## 5. Tolerance budgets after pinning

Per `V9_REPRODUCTION.md` §8 and the user's tolerance ruling:

| Run context | Bypass | FPR | GLR | ULR |
| --- | --- | --- | --- | --- |
| Pre-pin (audit reproduction, before this commit) | ±5pp | ±1pp | ±1pp | must be 0% |
| Post-pin (Phase-1.F onward — formal experiments) | ±1pp | ±0.5pp | ±0.3pp | must be 0% |

Any metric exceeding tolerance triggers a single-case root-cause
report (per V9_REPRODUCTION.md §3 example).

---

## 6. Change log

| Date | What changed | Reason | Author |
| --- | --- | --- | --- |
| 2026-05-08 | Initial pinning: HF `all-MiniLM-L6-v2` revision `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`; OpenAI `gpt-4o-mini-2024-07-18`; `transformers` `>=5.0.0,<5.1.0`; `torch` `>=2.10.0,<2.11.0`; `numpy` `>=2.4.0,<2.5.0`; `openai` `>=2.24.0,<2.25.0`. Updated 27 SentenceTransformer call sites + 11 OpenAI fallback sites + 3 configs. | Item 1.0b: prevent the upstream-update drift documented in V9_REPRODUCTION.md §3 (3.7pp ablation drift in safer direction). | audit / Claude Code session |
| 2026-05-08 | Tightened the four reproducibility-critical pins from minor band to exact patch: `transformers==5.0.0`, `torch==2.10.0`, `numpy==2.4.2`, `openai==2.24.0`. Cross-checked HF main revision (`git ls-remote` and `HfApi`) — pin still equals current upstream `main`. | Verifications 1+3 (audit-phase 1.0b ratification): patch-exact provides bit-level reproducibility; minor-band would re-introduce a numerical-determinism drift surface that the v9 reproduction already exposed. | audit / Claude Code session |

---

## 7. Verification commands

To verify pins are applied correctly:

```bash
# 1. HF revision matches local cache
cat ~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/refs/main
# Expect: c9745ed1d9f207416be6d2e6f8de32d1f16199bf

# 2. Every SentenceTransformer call passes revision
grep -rn "SentenceTransformer(" --include="*.py" . \
  | grep -v "revision=" | grep -v venv | grep -v archive
# Expect: empty (all 27 call sites pass revision=)

# 3. Every OpenAI fallback uses dated snapshot
grep -rn '"gpt-4o-mini"' --include="*.py" --include="*.yaml" . \
  | grep -v venv | grep -v archive | grep -v "core/config_loader.py"
# Expect: empty (only the comment in config_loader.py mentions the alias)

# 4. requirements.txt has minor pins for the four critical libs
grep -E "^(openai|transformers|torch|numpy)" requirements.txt
# Expect: each line shows a >=X.Y.Z,<X.(Y+1).0 spec
```

---

## 8. Future-encoder notes (for Phase 1.F)

Phase 1.F will introduce additional encoders (`all-mpnet-base-v2`,
`BAAI/bge-large-en-v1.5`, possibly a finance-finetuned encoder).
For each, add an entry to `core/config_loader.py:PINNED_REVISIONS`
with the revision hash captured at the time of first use. The
`get_pinned_revision()` helper auto-resolves to `None` for any
unknown model, so untracked encoders fall back to the
HuggingFace default tag — this is acceptable for one-off
experiments but **not** for paper-cited results.

For paper-cited results in Phase 1.F:
1. Capture the revision via `cat ~/.cache/huggingface/hub/.../refs/main`
2. Add to `PINNED_REVISIONS` dict
3. Append a row to §6 Change Log of this file
4. Run the experiment once with the pinned revision
5. Cite the revision in the paper's reproducibility section

---

End of REPRODUCIBILITY.md.
