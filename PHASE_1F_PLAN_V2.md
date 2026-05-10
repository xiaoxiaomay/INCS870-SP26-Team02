# Phase 1.F — Embedding Model Ablation Plan (V2)

> Implementation plan for PLAN.md §5 Phase-1 Deliverable F. **V2
> revision** updates the V1 plan with the user's six Q-rulings
> (locked 2026-05-09) and the four §10 tension resolutions:
>
> - **Q1:** OpenAI text-embedding-3-large EXCLUDED. 4 open-source
>   encoders only.
> - **Q2:** bge-large memory probe in M1; fallback to
>   `BAAI/bge-base-en-v1.5` if RSS-peak > 60% × 8 GB.
> - **Q3:** MiniLM cells re-run inside `eval/results/phase1_F/`
>   for a self-contained 8-cell matrix; Part-B artifacts retained
>   as historical baseline.
> - **Q4:** 12 work units → **5 milestones** (M1–M5) with one
>   gate per milestone.
> - **Q5:** New `scripts/build_phase1F_indexes.py` thin-wrapper
>   orchestrator; existing `build_secret_faiss_index.py` untouched.
> - **Q6:** One short status report per milestone gate.
> - **T1–T4:** PLAN.md tensions resolved (preserved-as-historical-
>   reference, doc-typo OK, two encoders per Q5, FPR deferred to
>   Phase 1.E).
>
> **V2 supersedes V1**; V1 retained at `PHASE_1F_PLAN.md` for diff.
> No work-unit execution this turn — V2 is itself for review.

---

## Section 1 — Encoder Selection (Q1 + Q2 ratified)

### 1.1 Final candidate list (4 open-source encoders)

| # | Encoder | Type | Dim | ~Size | HF revision (`git ls-remote refs/heads/main` 2026-05-09) |
| --- | --- | --- | --- | --- | --- |
| 1 | `sentence-transformers/all-MiniLM-L6-v2` | open-source baseline (v9-deployed) | 384 | ~80 MB | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` (already pinned in 1.0b) |
| 2 | `sentence-transformers/all-mpnet-base-v2` | open-source general-purpose | 768 | ~420 MB | `e8c3b32edf5434bc2275fc9bab85f82640a19130` |
| 3 | `BAAI/bge-large-en-v1.5` (primary) | open-source retrieval-tuned, large | 1024 | ~1.34 GB | `d4aa6901d3a41ba39fb536a557fa166f842b0e09` |
| 3' | `BAAI/bge-base-en-v1.5` (Q2 fallback) | open-source retrieval-tuned, base | 768 | ~440 MB | `a5beb1e3e68b9ab74eb54cfd186867f64f240e1a` |
| 4 | `FinLang/finance-embeddings-investopedia` | open-source domain-finetuned (finance) | TBD (likely 768) | TBD | `37d7594d02e3d656a241e099e39ac50ab921f999` |

**Q1 ruling:** OpenAI `text-embedding-3-large` is **excluded**.
Reproducibility cannot depend on a paid API; the four open-source
candidates are sufficient to test the (a) general-scale-up
hypothesis (mpnet, bge-large) and (b) domain-finetune hypothesis
(FinLang).

### 1.2 Selection rationale (unchanged from V1)

- **MiniLM** — v9 deployed baseline. Re-run in `phase1_F/` per Q3
  ruling for a self-contained matrix; numbers expected
  byte-identical to `partB_60entry/`/`partB_90entry/` (encoder +
  revision + data + driver are identical).
- **mpnet** — v9 paper Table XIII ratified +24% Gap improvement
  (0.123 vs 0.099). Phase 1.F's job: confirm or refute on full
  bypass/GLR/ULR, not just micro-Gap.
- **bge-large** — chosen over bge-small (v9 already showed bge-small
  *worse* than MiniLM at Gap=0.046). Tests scale-up of the
  open-source frontier; with Q2 contingency below.
- **FinLang** — tests whether **domain-specific fine-tuning** beats
  **general scale-up**. Either result is publishable: a win =
  recommend, a loss = "domain-finetuning didn't help" honest
  finding.

### 1.3 Pinned-revision registry extension (V2: 5 entries to support fallback)

```python
# core/config_loader.py:PINNED_REVISIONS (V2)
PINNED_REVISIONS = {
    "sentence-transformers/all-MiniLM-L6-v2":
        "c9745ed1d9f207416be6d2e6f8de32d1f16199bf",  # 1.0b
    # Phase 1.F additions (registered in M1, all HF main as of 2026-05-09):
    "sentence-transformers/all-mpnet-base-v2":
        "e8c3b32edf5434bc2275fc9bab85f82640a19130",
    "BAAI/bge-large-en-v1.5":
        "d4aa6901d3a41ba39fb536a557fa166f842b0e09",
    "BAAI/bge-base-en-v1.5":  # Q2 fallback for bge-large
        "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a",
    "FinLang/finance-embeddings-investopedia":
        "37d7594d02e3d656a241e099e39ac50ab921f999",
}
```

### 1.4 Per-corpus FAISS index requirement (unchanged from V1)

4 encoders × 2 corpora = 8 secret FAISS indexes. MiniLM's two are
existing (`secrets.faiss`, `secrets_v2.faiss`). 6 new indexes to
build in M2. Naming convention:
`data/index/secrets__<encoder_short>.faiss` and
`data/index/secrets_v2__<encoder_short>.faiss`.

If Q2 fallback fires, replace `bge_large` with `bge_base` in the
naming and `PINNED_REVISIONS` lookup; document the swap in
`REPRODUCIBILITY.md` change-log.

### 1.5 Q2 — bge-large memory contingency (NEW in V2)

**Probe specification** (executed in M1):

```bash
# scripts/probe_encoder.py --model BAAI/bge-large-en-v1.5 --memory-probe
# Reports peak RSS during model load + 1 encode + 1 batch encode.
```

**Decision rule:**

| Probe outcome | Verdict | Action |
| --- | --- | --- |
| Peak RSS ≤ 60% × 8 GB (≤ 4.8 GB) | **bge-large primary** | Proceed with bge-large; register revision; build indexes; run cells |
| 60% × 8 GB < Peak RSS ≤ 80% × 8 GB (≤ 6.4 GB) | bge-large WARN | Proceed but require user-side close all other apps before M4 bge-large cells; document in M1 status report |
| Peak RSS > 80% × 8 GB (> 6.4 GB) | bge-large FAIL → fallback | Switch to `BAAI/bge-base-en-v1.5`; rename outputs accordingly; capture `a5beb1e3e68b9ab74eb54cfd186867f64f240e1a` as the active pin in `PINNED_REVISIONS`; document switch + reasoning in M1 status report |

**Operational implementation:** the probe is a no-LLM,
sub-minute test that loads the encoder, encodes 5 reference
strings (one short query, one long secret-text), and uses
`psutil.Process().memory_info().rss` to measure peak RSS during
the load+encode window.

**Why bge-base as the fallback** (vs cutting bge entirely):
- Same architecture family; results stay comparable.
- bge-base's 768-dim matches mpnet, simplifying any
  encoder-vs-encoder side-by-side at the matrix level.
- bge-base has 110 M parameters (~440 MB), well within the 8 GB
  budget on this laptop.
- HF revision verified reachable (above).

If the fallback fires, the matrix becomes:
{MiniLM, mpnet, bge-base, FinLang}. Documented in M1 status.

---

## Section 2 — Index Build Plan (Q5 ratified)

### 2.1 Q5 — `scripts/build_phase1F_indexes.py` thin-wrapper orchestrator

Per Q5 ruling, **do not modify** `scripts/build_secret_faiss_index.py`.
Instead, create a thin orchestrator:

```python
# scripts/build_phase1F_indexes.py (NEW, ~120 lines)

"""
Phase-1.F index-build orchestrator. Loops over (encoder, corpus)
pairs and invokes the existing build logic per cell. Idempotent:
skips cells whose index already exists with matching ntotal.
"""

import argparse, hashlib, json, time
from pathlib import Path

from core.config_loader import PINNED_REVISIONS, get_pinned_revision
# Reuses (NOT modifies) the existing builder primitives:
from scripts.build_secret_faiss_index import load_jsonl

# Phase-1.F encoder × corpus matrix (Q1: open-source only; Q3: MiniLM
# included so the matrix is self-contained even though MiniLM indexes
# already exist on disk).
PHASE1F_MATRIX = [
    {
        "encoder": "sentence-transformers/all-MiniLM-L6-v2",
        "short":   "minilm",
        "corpus":  "60",
        "secrets": "data/secrets/secrets.jsonl",
        "out_idx": "data/index/secrets__minilm.faiss",   # phase1_F-namespaced
        "out_meta":"data/index/secrets__minilm_meta.pkl",
    },
    # ... (8 entries total: 4 encoders × 2 corpora)
]

def build_one(cell: dict, force: bool = False) -> dict:
    """
    Build a single FAISS index for (encoder × corpus). Returns a
    diagnostic dict including elapsed_s, ntotal, dim, encoder
    revision, file md5. Skips if output exists and ntotal matches
    expected unless --force.
    """
    ...

def main():
    """
    For each cell in PHASE1F_MATRIX: build → record diagnostics →
    write build_log.json. On any failure, stop and surface the
    error (no half-built matrix).
    """
    ...
```

**Key design points:**
- The orchestrator imports `load_jsonl` from
  `build_secret_faiss_index.py` — it does NOT import or call the
  existing `main()` (which has hardcoded paths). This keeps the
  surface area small and the existing thesis-era build script
  fully back-compatible.
- The orchestrator owns the per-encoder revision lookup via
  `get_pinned_revision()` (already in `core/config_loader.py`).
- Output file naming stays predictable so the new
  `config_phase1F_*.yaml` files can hardcode the paths in M1.
- Idempotent re-run: if you re-run the orchestrator, only
  missing or `--force` cells rebuild.
- Each build records a `build_log.json` entry with `(encoder,
  corpus, dim, ntotal, elapsed_s, file_md5)` for provenance.

### 2.2 Per-encoder build estimates (CPU, 8 GB Mac M3) — V2 includes MiniLM re-build

Per Q3, MiniLM cells are re-run in `phase1_F/`. The MiniLM **FAISS
indexes** can be reused from `data/index/secrets.faiss` /
`secrets_v2.faiss` — no need to rebuild them. The orchestrator's
idempotent skip handles this automatically (it sees the existing
output files, matches ntotal, marks cell as `cached`).

| Encoder | Build time per index (estimated) | New indexes needed | Total build time |
| --- | --- | --- | --- |
| MiniLM | n/a (cached) | 0 | 0 (skip) |
| mpnet | ~1.5 min | 2 | ~3 min |
| bge-large (or bge-base if fallback) | ~3 min (large) / ~1.5 min (base) | 2 | ~3–6 min |
| FinLang | ~1.5 min | 2 | ~3 min |
| **Total M2 build wall-clock** | — | **6** | **~9–12 min** |

No LLM cost.

### 2.3 FinLang dimension uncertainty (M1 captures)

FinLang dim is captured by `scripts/probe_encoder.py` in M1.
Likely 768. Recorded in `REPRODUCIBILITY.md` change-log.

### 2.4 Index sanity gates (M2 acceptance)

For each built index, M2 verifies:
- File exists at expected path.
- `faiss.read_index(...).ntotal` matches expected (60 for v1
  corpus, 90 for v2).
- `.d` (dim) matches encoder dim from probe.
- Sibling `_meta.pkl` exists and `len(meta) == ntotal`.

Any mismatch stops M2 with a status report.

---

## Section 3 — Reproduction Plan

### 3.1 Per-cell run cost (V2: includes MiniLM re-run per Q3)

| Cells | Reuse `partB_*`? | LLM cost |
| --- | --- | --- |
| MiniLM × 60-entry | **NO (Q3: re-run for self-contained matrix)** | $0.025 |
| MiniLM × 90-entry | **NO (Q3)** | $0.025 |
| mpnet × 60-entry | New | $0.025 |
| mpnet × 90-entry | New | $0.025 |
| bge-large (or bge-base) × 60-entry | New | $0.025 |
| bge-large (or bge-base) × 90-entry | New | $0.025 |
| FinLang × 60-entry | New | $0.025 |
| FinLang × 90-entry | New | $0.025 |
| **Total Phase 1.F LLM cost** | — | **$0.20** |

Hard upper bound (1.5× output × retry): **~$0.40**. Per-step
$0.10 cap holds for every individual cell. Total session cap
(informal $0.30 from prior work) tightens to **$0.40 for V2**
to accommodate Q3's MiniLM re-runs; budget is acceptable.

### 3.2 Wall-clock estimate (V2)

8 cells × ~10 min each = **~80 min sequential**, or ~40 min if
60-entry / 90-entry pairs run in parallel (acceptable since they
don't share state).

### 3.3 OPENAI_API_KEY requirement (unchanged from V1)

All 8 cells use `gpt-4o-mini-2024-07-18` per the post-B2 contract.
No env-var sidechannel (B2). LLM call count varies per encoder
based on Gate-1 decision shifts; expected range 100–150 calls per
cell.

---

## Section 3.5 — MiniLM Re-run in `phase1_F/` (Q3 ratified, NEW in V2)

Per Q3 ruling: re-run MiniLM (both 60-entry and 90-entry) inside
`eval/results/phase1_F/` for a fully self-contained matrix.

### 3.5.1 Why re-run instead of symlink/reference

- A self-contained `phase1_F/` directory is the single artifact a
  reviewer would `tar` and inspect; cross-directory references
  break that contract 6 months from now.
- The MiniLM re-run is itself a **second L3 verifier check**: if
  the re-run produces materially different numbers from
  `partB_60entry/`/`partB_90entry/`, that signals something
  unexpected has changed in the pipeline since 2026-05-09 — a
  stop-the-line event.
- The cost is $0.05 (2 cells × $0.025), which is well within the
  Phase-1.F budget.
- The Part-B artifacts are *retained* as the historical baseline.
  `phase1_F/minilm_*` becomes the matrix-era twin.

### 3.5.2 Tolerance gate for MiniLM regression cross-check (M4 part of acceptance)

| Metric | Part-B value | M4 phase1_F value tolerance | Stop-the-line condition |
| --- | --- | --- | --- |
| 60-entry bypass | 47.60% (129/271) | ±0.5pp | Any deviation > 0.5pp |
| 60-entry GLR | 1.85% (5/271) | ±0.3pp / ±1 prompt | Any deviation > 0.3pp OR > 1 prompt |
| 60-entry ULR | 0.00% (0/271) | must = 0 | Any > 0 |
| 90-entry bypass | 50.18% (136/271) | ±0.5pp | Any deviation > 0.5pp |
| 90-entry GLR | 4.06% (11/271) | ±0.3pp / ±2 prompts | Any deviation > 0.3pp OR > 2 prompts |
| 90-entry ULR | 0.00% (0/271) | must = 0 | Any > 0 |

If **any** stop-the-line condition fires on the MiniLM re-run,
M4 halts and produces a regression-investigation report.

### 3.5.3 Output namespacing

```
eval/results/phase1_F/minilm_60entry/{bypass_cases.jsonl, full_pipeline_eval.json, summary.json}
eval/results/phase1_F/minilm_90entry/{bypass_cases.jsonl, full_pipeline_eval.json, summary.json}
```

Both Part-B artifacts (`partB_60entry/`, `partB_90entry/`) remain
untouched.

---

## Section 4 — Metric Collection Plan (V2: corrected paths)

### 4.1 Output namespacing

```
eval/results/phase1_F/
├── minilm_60entry/         # NEW per Q3 (MiniLM re-run)
├── minilm_90entry/         # NEW per Q3
├── mpnet_60entry/          # NEW
├── mpnet_90entry/          # NEW
├── bge_large_60entry/      # NEW (or bge_base_60entry/ on Q2 fallback)
├── bge_large_90entry/      # NEW
├── finlang_60entry/        # NEW
├── finlang_90entry/        # NEW
├── discrimination_gap.json # cross-encoder Gap(L2-L1) (M5)
├── matrix.json             # 4×2 cross-encoder matrix (M5)
├── matrix.tex              # LaTeX table for v10 paper (M5)
└── build_log.json          # FAISS-build provenance (M2)

eval/results/v9_reproduction/    # Part-A + Part-B artifacts retained as historical baseline
├── partB_60entry/
├── partB_90entry/
├── partB_sanity_60entry/
├── ablation_B2full.json
└── _archive/{bypass_cases_pre_repro.jsonl, bypass_analysis_report_pre_repro.json}
```

### 4.2 Per-cell summary contents (unchanged from V1)

`bypass_rate`, `glr_rate`, `ulr_rate`, `n_blocked_pregates`,
`n_llm_called`, `per_category` breakdown, `embedding_model`,
`embedding_revision`, `secret_count`, `elapsed_s`,
`estimated_cost_usd`. Plus full pipeline records for forensic
re-derivation.

### 4.3 Discrimination Gap (Table XIII analog) computation

Extend `scripts/embedding_benchmark.py` to compute the v9
Table XIII discrimination Gap for **each (encoder, corpus)**:
8 cells. Output `phase1_F/discrimination_gap.json`. No-LLM,
runs in ~5 min. Feeds the v10 Table XIII upgrade.

### 4.4 Cross-encoder matrix script

New `scripts/phase1F_matrix.py` (~80 lines, no LLM):
- Reads each per-cell `summary.json`
- Reads `discrimination_gap.json`
- Emits `matrix.json` + `matrix.tex` + console comparison

### 4.5 Per-encoder FPR — DEFERRED to Phase 1.E (T4 ruling)

Per the T4 ruling (§10), per-encoder FPR is **explicitly out
of scope** for Phase 1.F. FPR was confirmed at 3.0% (90-entry
MiniLM) in Part A; whether other encoders preserve that depends
on the hard-negative FPR set being constructed in Phase 1.E.

When Phase 1.E lands its 96-query hard-negative set, a follow-up
(Phase 1.E/F joint cell) will measure per-encoder FPR on the
hard-negative set with the same 4-encoder matrix. Phase 1.F
defers and documents.

---

## Section 5 — Three-Layer Verification Application (V2: fallback-aware)

### 5.1 L1 (static) — V2 extension

V1's L1 already enforces:
- No `os.getenv("OPENAI_MODEL")` chains
- Every `SentenceTransformer(...)` call has `revision=`
- No bare `"gpt-4o-mini"` literal

V2 adds (in M1):
- **L1 1d:** every `SentenceTransformer(model_name, ...)` call's
  `model_name` argument resolves to a key in `PINNED_REVISIONS`
  (or is a parameter passed in by the caller — i.e. the caller
  is responsible). If the model_name is a literal string, it
  must be a `PINNED_REVISIONS` key. Catches the case where
  someone hard-codes a new encoder without registering it.

Verifier extension scope: ~15 LOC.

### 5.2 L2 (runtime) — V2 extension

V1's L2 only tests MiniLM. V2 (M1):
- Loop over every key in `PINNED_REVISIONS`
- For each: assert `get_pinned_revision(key)` returns the
  canonical hash (not None, not stale)
- For each: assert the corresponding `config_phase1F_*.yaml`
  declares the same `embedding.revision`

Verifier extension scope: ~20 LOC.

### 5.3 L3 (end-to-end) — V2 extension

V1's L3 runs `repro_full_pipeline.py --config config.yaml --limit 2`
once. V2 (M1):
- Add `--config <path>` flag to L3 probe
- Run L3 probe per encoder × corpus = 8 cells
- Cost: 8 × 2 prompts × $0.0002 = ~$0.0016 total

Each L3 probe verifies `summary.json:llm_model` is the dated
snapshot AND `summary.json:embedding_revision` matches the
encoder's canonical hash.

Verifier extension scope: ~10 LOC.

### 5.4 6 new `config_phase1F_*.yaml` files (M1)

For each (encoder, corpus) cell, one new config:

```
config_phase1F_mpnet_60entry.yaml      → embedding.model_name + revision (mpnet); paths.secret_index points at secrets__mpnet.faiss
config_phase1F_mpnet_90entry.yaml      → same encoder, secrets_v2__mpnet.faiss
config_phase1F_bge_large_60entry.yaml  (or bge_base_60entry.yaml on fallback)
config_phase1F_bge_large_90entry.yaml  (or bge_base_90entry.yaml on fallback)
config_phase1F_finlang_60entry.yaml
config_phase1F_finlang_90entry.yaml
```

MiniLM cells reuse existing `config.yaml` (60-entry) and
`config_v2.yaml` (90-entry).

Each new config copies the corresponding base config and edits
3 lines:
- `embedding.model_name` ← new encoder
- `embedding.revision` ← canonical hash
- `paths.secret_index` ← per-encoder path
- `paths.secret_meta` ← per-encoder meta

---

## Section 6 — v10 Paper Table XIII Upgrade (unchanged from V1)

V2 keeps V1's §6 verbatim. v9 Table XIII becomes a 2-row
historical reference; v10 Table XIII becomes an 8-row matrix
(4 encoders × 2 corpora) with 8 columns (Dim, Corpus, Gap,
Bypass, GLR, ULR, FPR, P50). Decision criterion (ULR=0 hard +
maximize Gap subject to bypass-not-degraded-by-5pp + P50 ≤ 100ms)
unchanged.

If Q2 fallback fires, the table swaps `bge-large` for `bge-base`
and adds a footnote explaining the contingency.

---

## Section 7 — Risk Assessment (V2: Q2 contingency expanded)

V1's risks remain. V2 strengthens the bge-large memory item:

| Risk | Probability | Impact | V2 Mitigation (M1 binding) |
| --- | --- | --- | --- |
| bge-large OOM on 8 GB Mac M3 | Medium | Medium | M1 mandatory `probe_encoder.py --memory-probe BAAI/bge-large-en-v1.5`. Decision tree per §1.5. Fallback to bge-base is pre-approved; no further user input needed at fallback time. |
| FinLang HF model gated/private | Low (verified reachable) | High | Already verified; if it changes status mid-execution, M1 would surface immediately and we stop. |
| Encoder swap requires Gate-1 threshold re-tuning | High | Medium | Keep thresholds fixed at v9 values for primary comparison. Add a sensitivity-analysis row if any cell shows >70% bypass. |
| MiniLM re-run produces different numbers from Part B | Low (same inputs, same code, same pinned versions) | High (would invalidate Part B's reproducibility claim) | M4 stop-the-line condition per §3.5.2. ±0.5pp / ±1–2 prompt tolerance. |
| Wall-clock overrun (8 cells × 10 min ≈ 80 min sequential) | Medium | Low | Acceptable; can run pairs in parallel if needed. |
| LLM cost overrun | Low ($0.20 estimated, $0.40 upper) | Medium | Hard-stop and report at $0.10/step (existing cap). |
| 6th paper-code inconsistency surfacing | Medium (every prior phase found one) | Medium-high | Stop-and-report; treat as v10-rewrite TODO, do not fix in 1.F. |

---

## Section 8 — Milestone Mapping (NEW in V2 per Q4 ruling)

V1's 12 fine-grained work units consolidate into **5 milestones**.
Each milestone is bounded by a status-report gate (template in
§9). Milestones are sequential; the user approves each gate before
the next milestone starts.

### M1 — Infrastructure setup (NEW work unit grouping)

**Composed of work units:**
- 1.F-A0 (PINNED_REVISIONS extension + verifier L1+L2 extension +
  `scripts/probe_encoder.py` new)
- 1.F-A2 (6 `config_phase1F_*.yaml` files + L3 `--config` flag)
- bge-large memory probe + Q2 fallback decision

**Effort:** ~5 hours.
**LLM cost:** ~$0.0016 (the L3 verifier probes — 8 × 2 prompts).
**Wall:** ~5 hours including human review of the configs.

**Gate (M1 acceptance, mandatory before M2):**
- `python scripts/verify_repro_pins.py --layer 1 --layer 2` returns `OVERALL: PASS` with **all 4 (or 5 if fallback) encoders covered**.
- All 6 `config_phase1F_*.yaml` files exist, valid YAML, declare both `embedding.revision` AND `openai_model` (= dated snapshot).
- `scripts/probe_encoder.py` reports dim + load time + memory peak for all 4 encoders.
- bge-large vs bge-base decision is made and documented.
- M1 status report produced (template §9).

### M2 — Index builds

**Composed of work units:**
- 1.F-A1 (`scripts/build_phase1F_indexes.py` new + 6 FAISS index builds)

**Effort:** ~2 hours.
**LLM cost:** $0.
**Wall:** ~10 min for the orchestrator + ~12 min build wall-clock.

**Gate (M2 acceptance, mandatory before M3):**
- 8 secret FAISS indexes exist (4 encoders × 2 corpora;
  MiniLM's 2 cached).
- Per-index `ntotal` matches expected (60 / 90); `dim` matches
  encoder dim from M1 probe.
- `phase1_F/build_log.json` written with provenance per cell.
- `verify_repro_pins.py --layer 1 --layer 2` still PASS.
- M2 status report produced.

### M3 — Sanity reproduction

**Composed of work units:**
- New work unit: `repro_full_pipeline.py --config
  config_phase1F_mpnet_90entry.yaml --limit 10`

**Effort:** ~30 min wall.
**LLM cost:** ~$0.0025 (10 prompts, 5–8 LLM calls).
**Wall:** ~30 min including review.

**Gate (M3 acceptance, mandatory before M4):**
- Driver completes with exit 0.
- `summary.json` provenance correct: `llm_model =
  gpt-4o-mini-2024-07-18`, `embedding_model = mpnet`,
  `embedding_revision = e8c3b32...`, `secret_count = 90`.
- `verify_repro_pins.py --layer 3 --config
  config_phase1F_mpnet_90entry.yaml` PASS.
- M3 status report produced.

### M4 — Full ablation matrix (8 cells)

**Composed of work units:**
- 1.F-B1 (mpnet × 60), 1.F-B2 (mpnet × 90)
- 1.F-C1 (bge-large/bge-base × 60), 1.F-C2 (× 90)
- 1.F-D1 (FinLang × 60), 1.F-D2 (× 90)
- NEW: MiniLM × 60-entry, MiniLM × 90-entry (per Q3)

**Effort:** ~3–4 hours wall (parallel pairs possible).
**LLM cost:** ~$0.20 (8 cells × $0.025).
**Wall:** ~80 min sequential, ~40 min parallel pairs.

**Gate (M4 acceptance, mandatory before M5):**
- 8 `summary.json` files exist under
  `eval/results/phase1_F/<cell>/`.
- Each cell's provenance verified by `verify_repro_pins.py
  --layer 3 --config <cell-config>`.
- MiniLM re-run cells pass the §3.5.2 regression cross-check
  (within ±0.5pp on bypass, ±0.3pp on GLR, =0 on ULR, against
  Part-B baseline).
- No cell shows ULR > 0% (hard requirement; if any does, that's
  a stop-the-line event and a Phase-1.F finding).
- Total LLM spend ≤ $0.40.
- M4 status report produced.

### M5 — Matrix aggregation + writeup

**Composed of work units:**
- 1.F-A3 (extend `scripts/embedding_benchmark.py` → 8 cells of
  discrimination Gap)
- 1.F-E (`scripts/phase1F_matrix.py` new + `matrix.json` +
  `matrix.tex`)
- 1.F-F (`PHASE_1F_RESULTS.md` writeup + v10 Table XIII draft +
  encoder recommendation)

**Effort:** ~6 hours.
**LLM cost:** $0.
**Wall:** ~6 hours of writing/scripting.

**Gate (M5 acceptance, Phase 1.F complete):**
- `eval/results/phase1_F/discrimination_gap.json` exists with
  8 entries.
- `eval/results/phase1_F/matrix.{json,tex}` exist; matrix.tex
  is paper-importable.
- `PHASE_1F_RESULTS.md` exists at repo root with sections:
  Methodology / Per-cell results / Cross-encoder matrix /
  Discrimination-Gap analysis / v10 Table XIII draft / Encoder
  recommendation per §6.3 selection criterion / Anomalies and
  honest-disclosure section.
- M5 status report produced.

### M6 — (NOT a milestone, just noting): Phase 1.F is **complete** at M5 gate.

Phase 1.E (hard-negative FPR set) is the next deliverable after
Phase 1.F closes. Per-encoder FPR cross-check folds into Phase 1.E
naturally (T4 ruling).

---

## Section 9 — Status Report Template (Q6, NEW in V2)

Each milestone gate produces a short status report (≤ 2
paragraphs + a checklist). Append to `PHASE_1F_STATUS.md` (or
similar) at the repo root, NOT staged into git unless explicitly
requested.

```
## Milestone <Mn> — Status Report

**Date:** YYYY-MM-DD
**Completed work units:**
- 1.F-X1 — <short title>
- 1.F-X2 — <short title>
- (additional sub-steps)

**Cost (actual vs estimated):**
- LLM: $X.XXXX vs estimated $Y.YYYY (within ±20% / off by Z%)
- Wall time: Xh Ym vs estimated Yh Zm (within ±20% / off by W%)
(±20% deviations need no explanation; >20% requires a one-paragraph root-cause)

**Unexpected discoveries:** (≤ 5 bullets, or "None")

**Gate condition checks:** (one line per condition)
- [✓/✗] <condition 1>
- [✓/✗] <condition 2>
- ...

**Next milestone:** M<n+1> — <name>
**Approval requested:** YES / NO
**Blockers (if any):** <one paragraph>
```

---

## Section 10 — PLAN.md / KICKOFF.md Tensions — V2 Resolutions (T1–T4 ruled)

| # | Tension (from V1 §10) | V2 ruling |
| --- | --- | --- |
| **T1** | "preserve v9 numbers" (PLAN.md §5 Deliverable F) | **Partial preservation as historical reference**, with the −5.54pp / −3.69pp drift documented in `V9_REPRODUCTION.md` §12.5 as a **backward-reproducibility footnote**. v10 cites the v9 numbers AS historical AND the post-pin numbers AS the new canonical baseline. Both are reported; the relationship is explained. |
| **T2** | PLAN.md says "Table XX"; v9 paper has Table XIII | **Typo, ignored.** PLAN.md is a planning document, not a paper artifact; no edit needed. v10 paper rewrite owns the Table XIII upgrade. |
| **T3** | "one finance-finetuned model" (PLAN.md) vs Q5 "two open-source candidates (bge-large + FinLang)" | **Q5 wins.** Phase 1.F runs **both** bge-large (general retrieval) and FinLang (domain-finetuned) — they test different hypotheses. PLAN.md's one-encoder phrasing was directional, not prescriptive. |
| **T4** | DoD requires per-encoder FPR (PLAN.md §5 Deliverable F) | **DEFERRED to Phase 1.E joint cell.** Phase 1.F does NOT measure FPR per encoder. Rationale: FPR requires hard-negative queries; Phase 1.E (hard-negative FPR set) is the proper home for that work. After Phase 1.E lands its 96-query set, a 4-encoder × 96-query FPR matrix gets generated in Phase 1.E/F joint follow-up. Documented as scope-cut in `PHASE_1F_RESULTS.md` (M5). |

---

## Section 11 — Audit Phase Lessons (UNCHANGED — preserved from V1 verbatim per user instruction)

Captured here as Phase 1.F's "posture" — patterns this phase should
expect and handle.

### 11.1 The 5 paper-code inconsistencies — a pattern

The audit phase surfaced 5 distinct paper-code or paper-paper
gaps. Listed by depth, not chronology:

1. **Cascade k=2 implementation divergence** (PAPER_CODE_GAPS.md §A) —
   v9 paper Algorithm 1 says single soft hits stay "Soft" and
   only cascade triggers redaction; code redacts every soft hit
   immediately. Output is structurally safer than paper claims.
2. **Two-corpus conflation** (V9_REPRODUCTION.md §0) — v9 paper
   reports 53.9% bypass + 2.58% GLR side-by-side as if from one
   run; in fact bypass came from 90-entry ablation_v2.json,
   GLR came from 60-entry full_pipeline_eval.json.
3. **GLR vs ULR semantic gap** (LEAK_CASES_FORENSICS.md) — the
   v9 eval criterion `max_score ≥ 0.60 AND not leakage_flag`
   counts isolated soft hits as "leaked" even though the
   user-facing redacted_text was clean. ULR=0% empirically holds.
4. **`RESULTS_SUMMARY.md` apparent staleness** (RE_AUDIT_FINDINGS.md
   §1, then resolved in PAPER_CODE_GAPS.md §C) — the doc reports
   numbers that don't match the paper headlines, but on
   investigation it's a legitimate 60-entry-era snapshot, not a
   bug.
5. **OpenAI alias env-var sidechannel** (V9_REPRODUCTION.md §10,
   resolved by B2) — `.env` had `OPENAI_MODEL=gpt-4o-mini`
   (alias) and the resolution chain put env first, silently
   overriding the dated snapshot in config.

**Common pattern:** all five live at *seams* between layers
(eval-driver vs paper, two scripts using the same data with
different defaults, config vs env, summary doc vs eval JSON,
algorithm spec vs implementation). **None** are bugs in any
individual file; they're all coherence-across-files issues. This
is the typical signature of a deadline-pushed academic codebase.

### 11.2 Cross-document consistency check methodology

The audit-phase tactic that surfaced 4 of the 5 was *cross-document
consistency triangulation*:

- Compare paper §X to ablation_v2.json
- Compare ablation_v2.json to full_pipeline_eval.json
- Compare full_pipeline_eval.json to bypass_cases.jsonl
- Compare bypass_cases.jsonl mtime to FAISS index mtime
- ...

Each pair-wise check is cheap; mismatches are the discoveries.
**v10 paper rewrite should plan a systematic
cross-section consistency audit** before submission: every metric
in every table cross-checked to its source eval JSON, every
config value cross-checked to its on-disk file, every
forward-citation cross-checked to its target. ~3 hours of work,
catches the kind of issues reviewers notice.

### 11.3 Three-layer verification engineering

The B2 fix landed on the back of a 1.0b verification gap: static
grep verified literals but not runtime resolution. The fix was a
process improvement (3-layer verifier), not just a code patch.

**Phase 1.F implication:** every new external (encoder, config,
LLM model, library version) gets registered in `PINNED_REVISIONS`
or its analog AND extended into the verifier's L1+L2+L3
coverage. If a new external doesn't have a verifier hook, that's a
red flag: it means future drift won't be caught.

### 11.4 Static verification's blind spots

Static analysis cannot inspect:

- Environment variables (1.0b regression)
- Dynamic config swaps at process start
- Mocked test fixtures that hide real resolution
- Side-effecting imports that mutate `sys.path` or `os.environ`
- Order-of-side-effect dependencies (e.g., `dotenv.load_dotenv()`
  called before vs after a fallback chain)

For each new piece of reproducibility-critical code in Phase 1.F,
ask: "is the value I claim to use the value the running process
actually uses?" If yes-via-static-grep alone, it's not enough.

### 11.5 v10 rewrite phase recommendation

When Phase 3 starts (v10 paper rewrite per PLAN.md §5N), allocate
~4 hours specifically for **systematic cross-section consistency
audit**:

- For every metric cited in the paper, walk to its source JSON
  and verify the cited number matches.
- For every figure, walk to the regenerating script and verify
  it runs cleanly on the current commit.
- For every claimed reproducibility guarantee, run
  `verify_repro_pins.py --layer all`.
- For every citation, verify the arXiv ID resolves (per the
  audit-phase open question).
- For every attack-corpus number (e.g., "271 attacks"), verify
  it matches the file size on disk.

This is "boring" work but reviewer-impact-positive.

---

## Section 12 — Acceptance Criteria for V2 Plan

Approve V2 if:
- §1.1 encoder shortlist (4 open-source + 1 contingency) is correct.
- §1.5 Q2 contingency decision rule is acceptable.
- §3.1 cost envelope ($0.20 for 8 cells; $0.40 hard upper) is
  within budget.
- §3.5 MiniLM re-run regression-cross-check tolerance (±0.5pp
  bypass / ±0.3pp GLR / =0 ULR) is acceptable.
- §8 milestone structure (M1–M5 with one gate each) matches what
  you want as the cadence.
- §10 T1–T4 rulings are correctly captured.

Re-scope if:
- You want a tighter cadence (e.g., gate inside M4 between cells).
- You want a different MiniLM regression tolerance.
- You want OpenAI text-embedding-3-large included after all (Q1
  reversal).

Reject + rewrite if:
- The Q2 fallback decision rule (60% / 80% RSS thresholds) is
  too strict or too loose.
- The PHASE_1F_RESULTS.md scope at M5 is wrong.

Stopping for review of V2 plan. After V2 approval, M1 starts.

---

## Section 13 — Phase 1.F Scope-Cut Disclosure (NEW in V2 per T4)

For inclusion at the end of `PHASE_1F_RESULTS.md` (M5
deliverable), the Phase 1.F writeup MUST include this paragraph:

> **Scope cut: per-encoder FPR.** PLAN.md §5 Deliverable F's
> definition-of-done lists "TPR, FPR, true leakage rate, P50/P95
> latency on CPU and (if feasible) GPU" for each model. Phase 1.F
> reports TPR (via bypass-rate complement), GLR, ULR, P50/P95
> latency, and discrimination Gap, but **does not measure
> per-encoder FPR**. The justification is methodological: FPR
> requires hard-negative benign queries that share vocabulary with
> protected secrets. Phase 1.E (hard-negative FPR set,
> PLAN.md §5 Deliverable E) is constructing that 96-query
> hard-negative corpus. Once Phase 1.E lands, a Phase 1.E/F joint
> follow-up will produce the 4-encoder × 96-query FPR matrix.
> Until then, the only ratified per-encoder FPR is for MiniLM on
> the 100-query benign baseline (3.0%, from Part A — see
> `V9_REPRODUCTION.md` §3.1). Phase 1.F's encoder recommendation
> in §6.3 explicitly notes this scope cut and defers any FPR-based
> encoder ranking to the Phase 1.E/F joint cell.

This disclosure ensures the v10 paper section IV-K honestly
acknowledges the gap rather than reporting the per-encoder FPR
column with stale or extrapolated values.
