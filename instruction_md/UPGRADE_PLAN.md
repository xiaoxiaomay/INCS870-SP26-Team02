# SentinelFlow Journal Upgrade Plan

**Target:** IEEE TIFS / Computers & Security
**Date:** 2026-03-20
**Status:** In progress

---

## 1. Current State Analysis

### What Already Exists

| Component | Location | Status |
|-----------|----------|--------|
| Gate 0a (regex intent) | `scripts/run_rag_with_audit.py:intent_precheck()` | Complete |
| Gate 0b (verb×object) | `scripts/run_rag_with_audit.py:hardblock_precheck()` | Complete |
| Gate 1 (embedding precheck) | `scripts/run_rag_with_audit.py:embedding_secret_precheck()` | Complete, dual-threshold |
| Grounding validation | `scripts/run_rag_with_audit.py:grounding_validate()` | Complete |
| Leakage scan | `scripts/leakage_scan.py:scan_text()` | Complete, with DFP fusion |
| Audit (hash chain) | `core/audit.py:HashChainWriter` | Complete, dual SHA-256 |
| Engine orchestrator | `core/engine.py:SentinelEngine` | Complete (PostgreSQL-backed) |
| Config | `config.yaml` | Complete (all thresholds) |
| Attack prompts | `data/benchmark/attack_prompts.jsonl` | 70 entries |
| Normal prompts | `data/benchmark/normal_prompts.jsonl` | 100 entries |
| Secrets | `data/secrets/secrets.jsonl` | 60 entries (L2/L3) |
| Custom exfil | `data/benchmark/custom_strategy_exfil.jsonl` | 60 entries |
| External attacks | `data/eval/external_attack_prompts.json` | Exists |
| Benchmark runner | `scripts/benchmark.py` | Partial (attack/benign/leakage/ablation modes) |
| Latency benchmark | `scripts/latency_benchmark.py` | Exists (basic) |
| FAISS indexes | `data/index/secrets.faiss`, `secrets_meta.pkl` | Built |
| DFP (fingerprinting) | `scripts/dfp.py` | Complete but disabled by default |
| Llama Guard | `scripts/llm_guard.py` | Complete but disabled |
| Prompt monitoring | `scripts/prompt_monitor.py` | Complete but disabled |
| LaTeX report | `docs/full_report_v3.tex` | Thesis format (1-column) |

### What Needs to Be Built

| Deliverable | Phase | Notes |
|-------------|-------|-------|
| 130+ new attack prompts | Phase 2 | Template-based (no API key assumed) |
| Cross-category prompts (30) | Phase 2 | Multi-turn, authority, hypothetical, context injection |
| `eval/run_ablation.py` | Phase 3 | 6 configs with gate bypass; existing `benchmark.py` has framework only |
| `eval/ablation_table.py` | Phase 3 | LaTeX table generator |
| `eval/run_statistical_eval.py` | Phase 4 | Multi-run with McNemar's test |
| `gates/gate_0_decode.py` | Phase 5 | Encoding detection (Base64/ROT13/Hex/URL/Unicode) |
| Engine integration of decode gate | Phase 5 | Pre-Gate 0a step |
| `tests/test_encoding_gate.py` | Phase 5 | Unit tests |
| `eval/run_latency_benchmark.py` | Phase 6 | Publication-quality (P50/P95/P99, scalability) |
| Medical domain data + eval | Phase 7 | `data/medical/`, `config_medical.yaml`, `eval/run_medical_eval.py` |
| Docker + reproducibility | Phase 8 | Dockerfile, docker-compose.yml, reproduce script |
| `eval/generate_latex_tables.py` | Phase 8 | All result tables as .tex snippets |
| Journal LaTeX conversion | Phase 9 | 2-column IEEE format |
| README + RESULTS_SUMMARY | Phase 10 | Final documentation |

### Key Architecture Notes

- **Gate functions are NOT in a `gates/` directory** — they live in `scripts/run_rag_with_audit.py` as functions (`intent_precheck`, `hardblock_precheck`, `embedding_secret_precheck`). The `rule_gate()` function merges 0a+0b.
- **Engine has two paths:** `core/engine.py` (class-based, PostgreSQL) and `scripts/run_rag_with_audit.py` (script-based, also PostgreSQL). Ablation should work at the function level, not subprocess level, for speed.
- **No `gates/` directory exists** — will create it for the encoding gate.
- **Existing `scripts/benchmark.py`** has an ablation stub but no actual gate toggling. Need to build proper ablation with config overrides.

### Potential Blockers

1. **API keys:** `OPENAI_API_KEY` may not be set. Phase 2 prompt generation will use template-based approach as fallback. Evaluation phases that require LLM calls will include `--dry-run` mode.
2. **PostgreSQL dependency:** `core/engine.py` requires a live PostgreSQL database. Ablation and offline evaluations should use FAISS-only path to avoid DB dependency.
3. **No `eval/` directory at project root** — eval data is in `data/eval/`. Will create `eval/` for new scripts.
4. **Python 3.12** — all dependencies should be compatible.
5. **scipy/statsmodels** not in requirements.txt — need to add for Phase 4.
6. **matplotlib** not in requirements.txt — need to add for Phase 6.

### Deviations from Instructions

1. **Phase 2:** Will use template-based adversarial generation (no Claude/Anthropic API dependency) unless `ANTHROPIC_API_KEY` is available. This ensures reproducibility without API costs.
2. **Phase 3:** Ablation will operate at the function level (calling gate functions directly with config overrides) rather than spawning subprocesses, for efficiency and to avoid PostgreSQL dependency.
3. **Phase 9:** The LaTeX file is `docs/full_report_v3.tex`, not `sentinelflow_report_overleaf_v6_20260303.tex`. Will adapt accordingly.
4. **Benign query count:** Instructions mention "219-query benign set" but we have 100 in `normal_prompts.jsonl` + 60 in `custom_strategy_exfil.jsonl` (which are attack prompts). Will use the 100 benign queries available.

---

## 2. Phase-by-Phase Scope

### Phase 1 — Codebase Analysis & Plan
- [x] Read all key files
- [x] Understand file structure
- [x] Check data files
- [x] Write this plan

### Phase 2 — Expand Attack Prompts (Est: ~200 lines of code)
- Create `scripts/generate_adversarial_prompts.py` with template-based paraphrase generation
- Generate 150+ new prompts via synonym substitution, framing changes, evasion techniques
- Create 30 cross-category prompts (multi-turn, authority, hypothetical, context injection)
- Validate all prompts target real secrets
- Output: `data/attack_prompts_expanded.jsonl`, `data/attack_prompts_extended.jsonl`

### Phase 3 — Ablation Study (Est: ~300 lines)
- Create `eval/run_ablation.py` with direct gate function calls
- 6 configurations (B0, B2_no_G0a, B2_no_G0b, B2_no_G1, B2_no_LS, B2_full)
- Add B2_single_tau variant
- Record ASR, FPR, latency, API call count per config
- Create `eval/ablation_table.py` for LaTeX output

### Phase 4 — Statistical Significance (Est: ~200 lines)
- Create `eval/run_statistical_eval.py`
- N runs with different seeds
- McNemar's test (B0 vs B2)
- 95% CI computation
- `--dry-run` cost estimation

### Phase 5 — Encoding Evasion Fix (Est: ~250 lines)
- Create `gates/gate_0_decode.py` (Base64, ROT13, Hex, URL, Unicode, reversed)
- Integrate as first step in pipeline
- Add config section
- Unit tests in `tests/test_encoding_gate.py`

### Phase 6 — Latency Benchmark (Est: ~250 lines)
- Create `eval/run_latency_benchmark.py`
- Per-gate timing (min/P50/P95/P99/max)
- Scalability test (60/120/240/480 secrets)
- matplotlib plot + LaTeX table

### Phase 7 — Medical Pilot (Est: ~200 lines)
- Create medical secrets (20) and attacks (20)
- Create `config_medical.yaml`
- Create `eval/run_medical_eval.py`
- Demonstrate domain-agnostic architecture

### Phase 8 — Docker & Reproducibility (Est: ~150 lines)
- Dockerfile, docker-compose.yml
- `reproduce_paper_results.sh`
- `eval/generate_latex_tables.py`

### Phase 9 — LaTeX Conversion
- Change document class to 2-column
- Remove lineno, course sections
- Fix wide tables/figures with `*` variants
- Add placeholder sections for new content

### Phase 10 — Documentation
- Update README.md
- Create RESULTS_SUMMARY.md
