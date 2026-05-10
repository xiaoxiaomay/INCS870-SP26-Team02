# Phase 1.F — Embedding Model Ablation Plan

> Implementation plan for PLAN.md §5 Phase-1 Deliverable F. Submitted
> for review BEFORE any work-unit execution per the
> "approve-then-implement" working norm. Lock in encoder selection,
> sequencing, and cost envelope here; commit individual work units
> against this document as gating reference.
>
> **Context:** Audit phase closed 2026-05-09 with three-layer
> reproducibility verifier (1.0b + B2 patches), 90-entry full-pipeline
> baseline (bypass=50.18%, GLR=4.06%, ULR=0.00%), and 5 documented
> paper-code inconsistencies queued for v10 rewrite. Phase 1.F starts
> from a clean post-pin baseline.

---

## Section 1 — Encoder Selection

### 1.1 Final candidate list (locked in based on Q4/Q10 + reachability check)

| # | Encoder | Type | Dim | ~Size | HF revision (verified `git ls-remote refs/heads/main` 2026-05-09) |
| --- | --- | --- | --- | --- | --- |
| 1 | `sentence-transformers/all-MiniLM-L6-v2` | open-source baseline (v9-deployed) | 384 | ~80 MB | `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` (already pinned in 1.0b) |
| 2 | `sentence-transformers/all-mpnet-base-v2` | open-source general-purpose | 768 | ~420 MB | `e8c3b32edf5434bc2275fc9bab85f82640a19130` |
| 3 | `BAAI/bge-large-en-v1.5` | open-source retrieval-tuned | 1024 | ~1.34 GB | `d4aa6901d3a41ba39fb536a557fa166f842b0e09` |
| 4 | `FinLang/finance-embeddings-investopedia` | open-source domain-finetuned (finance) | TBD (likely 768) | TBD | `37d7594d02e3d656a241e099e39ac50ab921f999` |

**Tier-3 deferred:** `OpenAI text-embedding-3-large` (paid API). Per
Q6 ruling, paid encoders are low-priority; reproducibility benefits
from open-source-only matrix. **Skip unless explicitly requested.**

### 1.2 Selection rationale

- **MiniLM** — v9-deployed baseline. Already pinned and benchmarked in
  Part B; `eval/results/v9_reproduction/partB_60entry/` and
  `partB_90entry/` are the canonical cells. Re-included in the matrix
  for apples-to-apples comparison; do NOT re-run (reuse Part B output).
- **mpnet** — v9 paper Table XIII already showed the strongest
  discrimination Gap of the three encoders v9 tested
  (Gap(L2−L1) = 0.123 vs MiniLM's 0.099, +24%). The v9 paper itself
  recommends migrating to mpnet "when GPU is available." Phase 1.F's
  job is to ratify or refute that recommendation with full bypass/GLR/ULR
  data on **both** corpora, not just the discrimination-Gap micro-metric.
- **bge-large-en-v1.5** — chosen over bge-small (which v9 already
  benchmarked and found *worse* than MiniLM with Gap=0.0456). bge-large
  is the most competitive open-source retrieval encoder as of Q1 2026
  (MTEB leaderboard). Tests whether scaling-up open-source encoders
  delivers the predicted discrimination improvement on the financial
  secret task.
- **FinLang/finance-embeddings-investopedia** — finance-finetuned
  encoder. Tests whether **domain-specific fine-tuning** beats
  **general scale-up** for our task. If FinLang outperforms bge-large
  with smaller params, that's a strong v10 Section IV-K recommendation
  (cheaper, better, more reproducible). If bge-large wins, FinLang
  becomes a documented "why domain-finetuned didn't help" finding —
  also valuable for v10 honesty.

### 1.3 Pinned-revision registry extension

Add to `core/config_loader.py:PINNED_REVISIONS`:

```python
PINNED_REVISIONS = {
    "sentence-transformers/all-MiniLM-L6-v2":
        "c9745ed1d9f207416be6d2e6f8de32d1f16199bf",
    # Phase 1.F additions (registered 2026-05-09, HF main as of:):
    "sentence-transformers/all-mpnet-base-v2":
        "e8c3b32edf5434bc2275fc9bab85f82640a19130",
    "BAAI/bge-large-en-v1.5":
        "d4aa6901d3a41ba39fb536a557fa166f842b0e09",
    "FinLang/finance-embeddings-investopedia":
        "37d7594d02e3d656a241e099e39ac50ab921f999",
}
```

Each entry must be added in work-unit 1.F-A0 with the verifier's L2
layer extended to test all four (currently only MiniLM is L2-checked).

### 1.4 Per-corpus FAISS index requirement

Each encoder produces embeddings of a different dimension and value
distribution; the secret FAISS index built with one encoder is **not
reusable** by another. For four encoders × two corpora (60-entry +
90-entry), we need **8 secret FAISS indexes total**:

| | 60-entry corpus (`secrets.jsonl`) | 90-entry corpus (`secrets_v2.jsonl`) |
| --- | --- | --- |
| MiniLM | `data/index/secrets.faiss` (pre-existing, v9) | `data/index/secrets_v2.faiss` (pre-existing, v9) |
| mpnet | `data/index/secrets__mpnet.faiss` (NEW) | `data/index/secrets_v2__mpnet.faiss` (NEW) |
| bge-large | `data/index/secrets__bge_large.faiss` (NEW) | `data/index/secrets_v2__bge_large.faiss` (NEW) |
| FinLang | `data/index/secrets__finlang.faiss` (NEW) | `data/index/secrets_v2__finlang.faiss` (NEW) |

**6 new FAISS indexes to build.** Naming convention proposed:
double-underscore separator + lowercased encoder shortname. Same
pattern for `_meta.pkl` siblings.

---

## Section 2 — Index Build Plan

### 2.1 Reuse vs new code

`scripts/build_secret_faiss_index.py` already accepts the model name
implicitly (it reads `MODEL_NAME` constant + uses the 1.0b
`get_pinned_revision` lookup). To support per-encoder builds, two
options:

- **Option A (minimal change):** add `--model` and `--input` and
  `--output` and `--meta-output` CLI args to the existing script.
  Backward-compatible; defaults to the v9-era behavior.
- **Option B (Phase 1.F-only orchestrator):** new
  `scripts/build_phase1F_indexes.py` that loops over all 4 encoders ×
  2 corpora = 8 builds, calling the existing logic via direct import.
  Skips MiniLM cells that already exist.

**Recommendation: Option B.** It's a one-off batch job; the looped
form is easier to verify and idempotent. Existing
`build_secret_faiss_index.py` stays untouched (which means existing
v9-era reproducibility is unaffected).

### 2.2 Per-encoder build estimates (CPU, 8GB Mac M3)

Estimates derived from v9's `embedding_benchmark.json`'s
`encode_latency_ms` field (per 100 queries) extrapolated to the
90-entry secret corpus:

| Encoder | encode_latency_ms (per 100, v9 measured) | Estimated build time per index | New indexes needed | Total build time |
| --- | --- | --- | --- | --- |
| MiniLM | 869.8 | n/a (already built) | 0 | — |
| mpnet | 1770.4 | ~1.5 min (90 entries × titles+text encoding) | 2 | ~3 min |
| bge-large | not in v9 (extrapolate ~3500ms/100) | ~3 min (model load 30-60s + encode) | 2 | ~6 min |
| FinLang | not in v9 (assume ~500ms/100, BERT-base scale) | ~1 min | 2 | ~2 min |

**Total index-build wall-clock: ~11 minutes.** No LLM cost.

Memory check needed for **bge-large** specifically (1.34 GB model
on an 8 GB system; should fit, but other processes may compete).
Plan: clear caches before bge-large step; if OOM, document and
recommend a 16GB workstation for that encoder.

### 2.3 FinLang dimension uncertainty

`FinLang/finance-embeddings-investopedia`'s exact dimension is
unknown without loading the model. Likely 768 (BERT-base), but
could be 384 or larger. Work unit 1.F-A0 must verify and document
in `REPRODUCIBILITY.md` change-log.

---

## Section 3 — Reproduction Plan

### 3.1 Per-cell run cost (extrapolation from Part B baseline)

Each encoder × corpus = 1 `repro_full_pipeline.py` run. The
encoder swap does NOT change LLM call count by much (Gate-1
decisions shift slightly, but `±10` calls is the typical range
based on Part B's 60-vs-90 comparison: 129 vs 136 calls).

Per-cell upper-bound: **$0.0250** (matches Part B's average).
Per-cell wall: **~10 min** (model load 1–60s + 271 prompts).

### 3.2 Total cost envelope

| Cells | Reuse Part B? | Cost |
| --- | --- | --- |
| MiniLM × 60-entry | Yes (`partB_60entry/`) | $0.000 |
| MiniLM × 90-entry | Yes (`partB_90entry/`) | $0.000 |
| mpnet × 60-entry | New | $0.025 |
| mpnet × 90-entry | New | $0.025 |
| bge-large × 60-entry | New | $0.025 |
| bge-large × 90-entry | New | $0.025 |
| FinLang × 60-entry | New | $0.025 |
| FinLang × 90-entry | New | $0.025 |
| **Total Phase 1.F LLM cost** | — | **$0.150** |

With 2× retry buffer: **~$0.30 hard upper bound**. Per-step cap
($0.10) holds for every individual run.

Wall-clock for 6 new runs: **~60 min sequential**, or ~30 min if
two are run in parallel (acceptable since they don't share state).

### 3.3 OPENAI_API_KEY requirement

All 6 new runs need `OPENAI_API_KEY` (gpt-4o-mini-2024-07-18 calls).
No other external services needed (FAISS-only, USE_POSTGRES=false).
Per the B2 fix: `OPENAI_MODEL` env var is **ignored**; LLM identity
comes from `config*.yaml:openai_model`.

---

## Section 4 — Metric Collection Plan

### 4.1 Output namespacing

```
eval/results/phase1_F/
├── minilm_60entry/         # symlink to partB_60entry/ OR rerun for clean comparison
├── minilm_90entry/         # symlink to partB_90entry/ OR rerun
├── mpnet_60entry/          # NEW
├── mpnet_90entry/          # NEW
├── bge_large_60entry/      # NEW
├── bge_large_90entry/      # NEW
├── finlang_60entry/        # NEW
├── finlang_90entry/        # NEW
├── discrimination_gap.json # cross-encoder Gap(L2-L1) computed by analysis script
├── matrix.json             # 4×2 cross-encoder bypass/GLR/ULR/FPR/latency matrix
└── matrix.tex              # LaTeX table for v10 paper
```

**Recommendation: rerun MiniLM for clean comparison.** Symlinks across
phase boundaries create surprises 6 months from now. The cost is
$0.05 (two rerun cells). Provenance from the rerun will be
identical-to-Part-B numbers (it's the same encoder + same code), so
this also serves as a **second L3 verifier check**.

### 4.2 Per-cell summary contents

Each cell's `summary.json` (driver default) reports:
`bypass_rate`, `glr_rate`, `ulr_rate`, `n_blocked_pregates`,
`n_llm_called`, `per_category` breakdown, `embedding_model`,
`embedding_revision`, `secret_count`, `elapsed_s`,
`estimated_cost_usd`. All fields needed for the cross-encoder matrix.

### 4.3 Discrimination Gap (Table XIII analog) computation

Extend `scripts/embedding_benchmark.py` (already iterates 3
encoders) to:

1. Iterate the 4 candidates (extending the hardcoded list).
2. For each (encoder, corpus), compute Gap(L2−L1) using the same
   methodology as v9's existing values: `mean(L2→L3 max) − mean(L1→L3 max)`.
3. Output `phase1_F/discrimination_gap.json` with
   `{encoder, corpus, dim, gap_l2_vs_l1, encode_latency_ms,
   l1_to_l3_max_mean, l2_to_l3_max_mean, same_domain_l3_l1_sim}`.

This is no-LLM; runs in ~5 min total across all encoders. Output
feeds the v10 Table XIII upgrade.

### 4.4 Cross-encoder matrix script

New `scripts/phase1F_matrix.py` (~80 lines, no LLM):
- Reads each per-cell `summary.json`
- Reads `discrimination_gap.json`
- Emits `matrix.json` with one row per (encoder, corpus) cell
- Emits `matrix.tex` LaTeX (paper-ready)
- Emits a console comparison table (sorted by GLR ascending)

### 4.5 Per-encoder FPR

Phase 1.F does NOT re-measure FPR per encoder (Part A confirmed
3.0% on the 90-entry/MiniLM combination only). Re-measuring FPR
requires running 100 benign queries per cell × LLM calls; that's
800 additional calls = ~$0.10. Defer to Phase 1.B/E as a follow-up
unless an encoder shows clearly degraded behavior.

---

## Section 5 — Three-Layer Verification Application to Phase 1.F

### 5.1 L1 (static)

Already enforced by `scripts/verify_repro_pins.py`:
- No `os.getenv("OPENAI_MODEL")` chain anywhere
- Every `SentenceTransformer(...)` call passes `revision=`
- No bare `"gpt-4o-mini"` literal

Phase 1.F adds: **no bare encoder name** without a corresponding
`PINNED_REVISIONS` entry. Need to extend the verifier to grep for
`SentenceTransformer\(` followed by a name lookup, and assert
that name appears in `PINNED_REVISIONS`.

**Verifier extension scope: ~10 LOC.** Add a fourth check `1d`
in `verify_l1_static()`.

### 5.2 L2 (runtime)

Currently `verify_l2_runtime()` only tests
`get_pinned_revision("sentence-transformers/all-MiniLM-L6-v2")`.
Need to extend to test all 4 encoders. Loop over
`PINNED_REVISIONS` keys and assert the helper returns the
canonical hash for each.

**Verifier extension scope: ~5 LOC** (loop + assertion).

### 5.3 L3 (end-to-end)

Currently `verify_l3_end_to_end()` runs
`repro_full_pipeline.py --config config.yaml --limit 2`. This
only checks the MiniLM cell.

For Phase 1.F coverage, the verifier needs to optionally accept
`--config config_*.yaml` to run the L3 probe against any encoder
config. New config files needed:

```
config_phase1F_mpnet_60entry.yaml
config_phase1F_mpnet_90entry.yaml
config_phase1F_bge_large_60entry.yaml
config_phase1F_bge_large_90entry.yaml
config_phase1F_finlang_60entry.yaml
config_phase1F_finlang_90entry.yaml
```

Each is a copy of `config.yaml` (or `config_v2.yaml`) with:
- `embedding.model_name` swapped to the new encoder
- `embedding.revision` set to the canonical hash
- `paths.secret_index` pointing to the per-encoder FAISS

**6 new config files.** ~50 lines each (copy + 3-line edit).

L3 verifier extended to take `--config` and run the probe per
config. Pre-merge gating: `verify_repro_pins.py --layer 3` runs
once per config (8 total: 6 new + 2 existing) before declaring
Phase 1.F complete.

### 5.4 Verifier extension summary

| Extension | LOC | When |
| --- | --- | --- |
| L1 1d: encoder names → PINNED_REVISIONS lookup | ~10 | 1.F-A0 |
| L2: loop over all 4 encoders | ~5 | 1.F-A0 |
| L3: `--config` flag for arbitrary config | ~10 | 1.F-A1 |
| 6 new `config_phase1F_*.yaml` files | ~300 (copy+edit) | 1.F-A1 |

Total verifier+config extension: ~325 LOC over two work units.

---

## Section 6 — v10 Paper Table XIII Upgrade

### 6.1 v9 Table XIII (current)

```
Model                 | Dim  | L1→L3 Max | L2→L3 Max | Gap(L2-L1)
all-MiniLM-L6-v2      | 384  | 0.560     | 0.659     | 0.099       ← v9 baseline
all-mpnet-base-v2     | 768  | 0.608     | 0.731     | 0.123
bge-small-en-v1.5     | 384  | 0.769     | 0.815     | 0.046       ← worse than baseline
```

Computed against the **60-entry corpus only**. No bypass/GLR/ULR
columns. No latency. No FPR. No security ranking.

### 6.2 Proposed v10 Table XIII

```
Encoder               | Dim  | Corpus  | Gap(L2-L1) | Bypass% | GLR% | ULR% | FPR% | P50 (ms) | Verdict
MiniLM (v9 baseline)  | 384  | 60      | 0.099 (v9) | 47.60   | 1.85 | 0.00 | 3.0  | TBD      | preserved
MiniLM                | 384  | 90      | TBD        | 50.18   | 4.06 | 0.00 | 3.0  | TBD      | v10 baseline
mpnet                 | 768  | 60      | 0.123 (v9) | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
mpnet                 | 768  | 90      | TBD        | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
bge-large             | 1024 | 60      | TBD        | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
bge-large             | 1024 | 90      | TBD        | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
FinLang               | TBD  | 60      | TBD        | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
FinLang               | TBD  | 90      | TBD        | TBD     | TBD  | TBD  | TBD  | TBD      | TBD
```

### 6.3 v10 selection criterion (proposed)

Decision rule for v10's recommended primary encoder, applied to
the 90-entry corpus row (Phase-1 baseline per PLAN.md):

1. **ULR = 0%** (hard requirement — system must not leak to user).
2. Maximize **Gap(L2−L1)** (better discrimination).
3. Subject to **bypass ≤ baseline + 5pp** (don't allow a worse
   pre-gate posture in exchange for better discrimination).
4. Subject to **P50 latency ≤ 100 ms** (interactive viability;
   v9's 28.75 ms was for MiniLM, 100 ms is the OWASP-aligned
   real-time-firewall threshold).

Tie-breaker: smaller model size (deployment cost).

### 6.4 Negative-result handling

If FinLang (the riskiest candidate) shows worse Gap than MiniLM,
or shows ULR > 0%, this is a **publishable negative result**:
"finance-finetuned encoders do not automatically improve
strategy-leakage detection." This goes in v10 Section IV-K with
the same forensic depth as the LEAK_CASES_FORENSICS analysis.

---

## Section 7 — Risk Assessment

### 7.1 Likely failure modes

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| `FinLang/finance-embeddings-investopedia` HF model is private/gated | Low (verified reachable via `git ls-remote`) | High (drops a candidate) | Already verified in the spot-check above. If it later requires login, fall back to documenting the access requirement and either skip or use an HF token. |
| bge-large OOM on 8 GB Mac M3 | Medium (1.34 GB model) | Medium (drops a candidate or forces hardware change) | Pre-check available memory before 1.F-C steps; clear OS caches; if still OOM, document and run on a borrowed 16 GB workstation. |
| Encoder swap requires Gate-1 threshold re-tuning | High (different cosine distributions per encoder) | Medium (apples-to-apples comparison clouded) | Keep thresholds fixed at v9 values (0.75/0.50/0.45) for primary comparison. Add a sensitivity-analysis row that re-tunes per encoder if any cell shows >70% bypass — that's a clear signal of threshold mismatch. |
| Wall-clock overrun (8 cells × 10 min = 80 min sequential) | Medium | Low (just slower turnaround) | Run 60-entry and 90-entry pairs in parallel (~40 min wall). |
| LLM cost overrun | Low ($0.15 estimated, $0.30 upper) | Medium (under $0.20 cap if conservative) | Hard-stop and report at $0.10/step (existing cap). |
| Discrimination Gap stays compatible with v9's 60-entry numbers but breaks on 90-entry | Medium | Medium (suggests v9's encoder choice was lucky on 60-entry) | Document directionally; this is informative, not a bug. |
| **6th paper-code inconsistency surfacing during 1.F** | Medium (every prior phase found one) | Medium-high (delays Phase 1.F) | Stop-and-report on detection (consistent with audit-phase posture). Treat the inconsistency as a v10-rewrite TODO; don't try to fix it in Phase 1.F unless it blocks a cell from running. |

### 7.2 Distinguishing framework problems from encoder problems

If a non-MiniLM cell shows surprising numbers, the diagnostic is:

| Symptom | Likely cause | Diagnostic |
| --- | --- | --- |
| Cell exits 0 but `n_llm_called` differs from MiniLM by >25% | Encoder shifts Gate-1 borderline cases — not a bug | Compare `gate_1_score` distribution per cell; expect ±20% shift for different encoders |
| Cell shows ULR > 0 | Real leak through stronger encoder, OR the encoder's per-sentence cosines are scaled differently | Inspect the per-prompt records; if `max_leak_score` is ≥0.60 for sentences that obviously aren't leaks, it's a calibration issue → flag as paper-code finding #6 |
| Cell shows bypass < 30% AND GLR = 0 | Encoder is over-aggressive — Gate-1 threshold needs re-tuning for fair comparison | Document; per §7.1 mitigation, add re-tuned row |
| Cell crashes on FAISS load | dim mismatch between built index and queried encoder | Trace `paths.secret_index` provenance; ensure it was built with the same encoder this cell uses |
| Discrimination Gap drops on 90-entry vs 60-entry for the same encoder | Expected — 90-entry is harder | Document; this is the corpus-complexity ablation |
| Discrimination Gap is HIGHER on 90-entry | Suspicious — investigate metadata mismatch in the index | Re-build the affected index; verify `meta.pkl` `level` field distribution matches expectation |

### 7.3 Reproducibility regression watch

The B2 patch and 1.0b pin landed after the audit phase. Phase 1.F
must not re-introduce regressions:

- **Every new config file** must declare `embedding.revision` AND
  `openai_model` per the post-B2 contract. The L1 verifier catches
  missing `embedding.revision`; need to extend it to also catch
  missing `openai_model` in `config_phase1F_*.yaml`.
- **Every new SentenceTransformer call site** (only in batch
  build/orchestrator scripts; the driver doesn't add any) must
  pass `revision=`.
- **No new env-var-first chains.** The 1d L1 check should
  evolve to forbid any new `os.getenv()` chain over LLM/encoder
  identifiers.

### 7.4 v10 baseline preservation

Whatever happens in Phase 1.F, the 90-entry MiniLM cell
(`partB_90entry/`) is the v10 baseline and must remain
reproducible from the current commit forward. Each Phase-1.F cell
includes a **regression cross-check** against partB_90entry: if
re-running MiniLM on 90-entry as part of the matrix produces
materially different numbers from `partB_90entry/summary.json`, that
is a stop-the-line event (suggests something in Phase-1.F code
broke MiniLM). Tolerance: ±0.5pp on bypass/GLR.

---

## Section 8 — Sequencing

### 8.1 Work units (each ≤4 hours, gating-approved before next starts)

| # | Unit | Output | Effort | LLM | Approve-before-next |
| --- | --- | --- | --- | --- | --- |
| 1.F-A0 | Encoder availability + dim discovery + `PINNED_REVISIONS` extension + verifier L1+L2 extensions | Updated `core/config_loader.py`, `scripts/verify_repro_pins.py` | 2 h | $0 | yes |
| 1.F-A1 | Build all 6 new FAISS indexes via `scripts/build_phase1F_indexes.py` orchestrator | 6 new `data/index/secrets*__<encoder>.faiss` + meta files; `phase1F_indexes.log` | 2 h | $0 | yes |
| 1.F-A2 | Generate 6 new `config_phase1F_*.yaml` files; verifier L3 extension to take `--config` | 6 configs + verifier patch | 1.5 h | $0 | yes |
| 1.F-A3 | Discrimination-Gap script extension (`scripts/embedding_benchmark.py`) — 4 encoders × 2 corpora | `eval/results/phase1_F/discrimination_gap.json` | 2 h | $0 | yes |
| 1.F-A4 | Three-layer verifier full pass on Phase 1.F infrastructure (8 configs × L1/L2/L3) | `OVERALL: PASS` proof + cost tally | 1.5 h | ~$0.0016 (8 × $0.0002) | yes (gating: PASS or stop) |
| 1.F-B1 | mpnet × 60-entry full repro | `phase1_F/mpnet_60entry/{3 files}` | 0.5 h | $0.025 | continue |
| 1.F-B2 | mpnet × 90-entry full repro | `phase1_F/mpnet_90entry/{3 files}` | 0.5 h | $0.025 | continue |
| 1.F-C1 | bge-large × 60-entry full repro | `phase1_F/bge_large_60entry/{3 files}` | 1 h (incl. memory check) | $0.025 | continue |
| 1.F-C2 | bge-large × 90-entry full repro | `phase1_F/bge_large_90entry/{3 files}` | 1 h | $0.025 | continue |
| 1.F-D1 | FinLang × 60-entry full repro | `phase1_F/finlang_60entry/{3 files}` | 0.5 h | $0.025 | continue |
| 1.F-D2 | FinLang × 90-entry full repro | `phase1_F/finlang_90entry/{3 files}` | 0.5 h | $0.025 | continue |
| 1.F-E | Cross-encoder matrix script + JSON + LaTeX | `phase1_F/matrix.json` + `phase1_F/matrix.tex` | 2 h | $0 | yes |
| 1.F-F | v10 Table XIII draft + recommendations + Phase-1.F section | proposed v10 §III-J3 text | 2 h | $0 | yes |

**Total: ~17 hours, $0.15 LLM cost.** Within Phase-1 budget.

### 8.2 First unit detailed sub-plan (1.F-A0)

**Goal:** Register the three new encoders in `PINNED_REVISIONS`,
verify dimensions, extend verifier coverage. No FAISS build yet.

**Files to create or modify:**
- `core/config_loader.py` — extend `PINNED_REVISIONS` (4 entries
  total).
- `scripts/verify_repro_pins.py` — extend L1 1c/1d and L2 to loop
  over all `PINNED_REVISIONS` entries.
- `scripts/probe_encoder.py` — NEW. ~60 lines. Loads each encoder,
  reports dim + load time + sample embedding norm. Used to verify
  FinLang dim and confirm bge-large fits in memory.

**Function signatures:**

```python
# scripts/probe_encoder.py
def probe_encoder(model_name: str, revision: str = None) -> dict:
    """
    Load encoder, encode a known reference string, return diagnostics.
    Returns {name, revision, dim, load_time_s, embed_latency_ms,
             sample_norm, available, error?}.
    """

def probe_all() -> list[dict]:
    """Probe every encoder in PINNED_REVISIONS; return list."""

# scripts/verify_repro_pins.py (extension, not new file)
def verify_l2_runtime():  # extended:
    # NEW: loop PINNED_REVISIONS keys, assert get_pinned_revision returns each
```

**Test cases for `probe_encoder.py`:**
1. MiniLM (sanity — should match the canonical revision).
2. mpnet (verify dim=768, load time, sample embed norm ≈ 1.0).
3. bge-large (verify dim=1024, memory footprint, sample norm).
4. FinLang (verify dim, document if not 768).

**Smoke test for completion:**

```bash
python scripts/verify_repro_pins.py --layer 1   # PASS
python scripts/verify_repro_pins.py --layer 2   # PASS for ALL 4 encoders
python scripts/probe_encoder.py                 # all 4 report dim + load successfully
```

**Acceptance criteria:**
- 4 encoders × `PINNED_REVISIONS` entries present.
- Verifier L1 + L2 PASS.
- `probe_encoder.py` confirms dim values + reports any unexpected
  size (especially for FinLang).
- No code path uses an encoder without a pinned revision.

**Cost: $0.** (No LLM calls; encoder loads only.)

**Acceptance gate:** stop and report; user approves before
1.F-A1 starts.

---

## Section 9 — Open Questions for User Before 1.F-A0 Starts

1. **OpenAI text-embedding-3-large inclusion?** — current plan
   excludes per Q4/Q6. Confirm. (If included, +1 hour scope, +$0.02
   cost, requires OpenAI rate-limit handling for the index build
   step.)
2. **Memory check for bge-large** — system has 8 GB. Will the user
   close other apps for 1.F-C1/C2, or should I plan for 1.F-C runs
   to be skipped + flagged with a hardware-requirement note?
3. **Re-run MiniLM cells in `phase1_F/`?** — current
   recommendation: yes, for clean self-contained matrix and second
   L3 verifier check. Cost: $0.05. Confirm.
4. **First unit gating (1.F-A0)** — does my proposed sub-plan
   (§8.2) match what you want as the first 4-hour cap, or do you
   want me to compress (e.g., merge A0 + A1 + A2 into one unit)?
5. **Phase-1.F-only orchestrator vs CLI args** — Section 2.1
   proposed Option B (new orchestrator). Confirm or override.
6. **Acceptance gate cadence** — current plan asks for approval
   between EVERY unit (12 gates). User may prefer a coarser
   "approve A-bundle, then B-bundle, then C-bundle" cadence (3
   gates). Specify.

---

## Section 10 — Conflicts with PLAN.md / KICKOFF.md

Per the audit-phase honest-disclosure norm:

- **PLAN.md §5 Deliverable F** says: "all-MiniLM-L6-v2 (current
  baseline; preserve v9 numbers)". Phase-1.F preserves v9 numbers
  via `partB_60entry/` + `partB_90entry/` (the v9-equivalent runs
  done in Part B against pinned-but-drifted dependencies). The
  −5.54pp / −3.69pp drift documented in
  `V9_REPRODUCTION.md` §12.5 is "preserved" only in the sense that
  v10 documents it explicitly; the raw v9 numbers are NOT
  exactly reproducible without un-pinning torch/transformers/numpy
  (which would defeat 1.0b). **No conflict per se**, but worth
  flagging to ensure the user accepts that "preserve v9 numbers"
  in Phase 1.F means "preserve them as documented historical
  reference, not as exact current-run numbers."
- **PLAN.md §5 Deliverable F** says: "all-mpnet-base-v2 (paper's
  own Table XX shows +24% Gap)". The Table number is XX (placeholder)
  in PLAN.md; v9's actual Table is XIII per my audit. Trivial doc
  inconsistency; flagging for v10 rewrite.
- **PLAN.md §5 Deliverable F** says: "One finance-finetuned model
  (suggest BAAI/bge-large-en-v1.5 or a FinBERT-style encoder; final
  choice in AUDIT_AND_PROPOSAL.md)". `AUDIT_AND_PROPOSAL.md`
  recommended `bge-large` as the open-source candidate; the user's
  Q5 ruling added FinLang. So the final shortlist is
  bge-large + FinLang (both finance-relevant, in different ways:
  bge-large is general-purpose retrieval-tuned, FinLang is
  domain-finetuned). PLAN.md's wording could be read as "one
  encoder", but Q5 made it explicit that **both** are wanted. **No
  conflict, just a note.**
- **PLAN.md §5 Deliverable F DoD** says: "For each model: TPR,
  FPR, true leakage rate, P50/P95 latency on CPU and (if feasible)
  GPU." Phase-1.F **does not measure FPR per encoder** (per §4.5
  rationale; FPR was only ratified for MiniLM/90-entry in Part A).
  This is a partial DoD violation. Mitigation: document the
  scope-cut in 1.F-F's writeup; promote per-encoder FPR to a
  Phase-1.F follow-up (or fold into Phase 1.E's hard-negative FPR
  set deliverable).

None of these are blockers. Each gets a one-line callout in the
final 1.F writeup so reviewers (paper or peer) see the
intentionality.

---

## Section 11 — Audit Phase Lessons (reflection)

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

## Section 12 — Acceptance criteria for this plan

Approve if:
- §1 encoder shortlist is correct.
- §3 cost envelope ($0.15 for 6 new runs) is acceptable.
- §8 sequencing (12 work units, ~17 hours) is realistic given your
  schedule.
- §9 open questions are answered (or you say "your call, proceed").

Re-scope if:
- You want OpenAI text-embedding-3-large included (Tier-3 → Tier-1).
- You want bge-large dropped (memory concern).
- You want a finer-grained gating cadence (per work-unit vs
  per-bundle).

Reject + rewrite if:
- The recommended FinLang model is not what you intended.
- You want per-encoder FPR within Phase 1.F (not deferred).
- You want Phase 1.F to also re-tune Gate-1 thresholds per encoder.

Stopping for review. After approval of §9 questions, I will execute
1.F-A0 (the first 2-hour work unit) and report back.
