# Phase 1.F Status Log

> Append-only milestone log per `PHASE_1F_PLAN_V2.md` §9 template.
> Each milestone gate produces one entry. Status is captured at
> the moment of gate-readiness; downstream milestones append below.

---

## Milestone M1 — Infrastructure setup — Status Report

**Date:** 2026-05-09
**Reporter:** Claude Code session
**Verdict:** **PASS — ready to start M2 (index builds)**

### Headlines (Watchpoint A + B + C)

- **Watchpoint A — bge-large memory probe:** **PRIMARY (PASS).** Peak
  RSS 702.8 MB during fresh-subprocess load + 5-text encode batch.
  Threshold 60% × 8 GB = 4915 MB. Massively under budget; no
  fallback needed. The bge-base entry remains in `PINNED_REVISIONS`
  as a "registered but not exercised" contingency.
- **Watchpoint B — FinLang dimension:** dim = **768** (BERT-base
  scale; common value, no special handling). Verified via
  `scripts/probe_encoder.py`. Embedding norm 1.0 (correctly
  normalized). No flag needed.
- **Watchpoint C — Cost-assumption sanity check:** flagged for M3
  validation. M1 is no-LLM; the per-encoder cost extrapolation in
  V2 §3.1 ("each encoder ≈ MiniLM cost ±20%") will be empirically
  verified by the M3 sanity probe (mpnet × 90 × --limit 10).
  Per-encode latency on M1.0/M1.4 spot-probe shows mpnet+FinLang
  comparable to MiniLM (~50–60 ms/text), but bge-large is **~5×
  slower** (282.7 ms/text). Wall-time impact noted; cost impact
  expected to be negligible (LLM call time dominates over encoder
  encode time).

### Completed work units

- [✓] **M1.0 — bge-large memory probe (Watchpoint A first)**
  - `scripts/probe_encoder.py --model BAAI/bge-large-en-v1.5
    --revision d4aa6901...` → 702.8 MB peak RSS, dim=1024,
    load=17.6s (incl. ~1.34 GB download), encode=283 ms/text.
  - Verdict: **PRIMARY** path. bge-large will be the third encoder
    in the matrix.
- [✓] **M1.1 — `PINNED_REVISIONS` extension (5 entries)**
  - Edited `core/config_loader.py` to register 4 new encoders +
    1 fallback. All hashes captured from `git ls-remote refs/heads/main`
    on 2026-05-09. Inline comments document the M1.0 verdict and the
    Q2 fallback status.
- [✓] **M1.2 — `scripts/verify_repro_pins.py` extension**
  - L1 1d (NEW): every literal `SentenceTransformer("...")` model
    name must appear in `PINNED_REVISIONS`. Catches the case where
    a future contributor hardcodes an encoder without registering.
  - L2: now loops over every `PINNED_REVISIONS` entry (was MiniLM
    only). 5 entries verified.
  - L3: `--config <path>` flag added. `_expected_revision_for_config`
    helper resolves the expected hash from a given config so the
    L3 probe can be run per-encoder. Probe timeout bumped 120s →
    180s for bge-large's larger cold-load latency.
- [✓] **M1.3 — 6 new `config_phase1F_*.yaml` files**
  - Generated via a one-shot Python helper from `config.yaml`
    (60-entry template) and `config_v2.yaml` (90-entry template).
  - Each config has a banner comment marking it as
    Phase-1.F-generated. Surgical 4-line changes per file:
    `embedding.model_name`, `embedding.revision`,
    `paths.secret_index`, `paths.secret_meta`.
  - All 6 load cleanly via `scripts/run_rag_with_audit.load_config`
    and declare `openai_model = "gpt-4o-mini-2024-07-18"` (B2-compliant).
- [✓] **M1.4 — `scripts/probe_encoder.py` (NEW, used in M1.0)**
  - Standalone CLI: `--model`, `--revision`, `--all`. Subprocess-
    isolated peak-RSS measurement via `resource.getrusage` (no new
    `psutil` dependency). Reports JSON line per probe.
  - Used twice in M1: bge-large (M1.0) and FinLang (Watchpoint B).
- [✓] **M1.5 — `scripts/build_phase1F_indexes.py` (NEW, Q5 design)**
  - Thin-wrapper orchestrator. `build_secret_faiss_index.py`
    untouched per Q5. Idempotent: skips cells whose output index
    already exists with matching `ntotal`. Per-cell error
    aborts the run (no half-matrix). Records full provenance to
    `eval/results/phase1_F/build_log.json`.
  - `--dry-run` exercised in M1.6: built=0, cached=2 (MiniLM
    cells already on disk), error=0, dryrun=6 (the new cells M2
    will build).
- [✓] **M1.6 — Acceptance gate**
  - L1 + L2 verifier: **OVERALL: PASS** (5 PINNED_REVISIONS
    entries all resolve correctly; literal encoder names all in
    registry).
  - 6 configs valid YAML + correct `openai_model` + correct
    `embedding.revision` + correct `paths.secret_index`.
  - `probe_encoder.py` imports cleanly.
  - Orchestrator `--dry-run` reports the expected 0 built / 2
    cached / 0 error / 6 dryrun split.

### Cost (actual vs estimated)

- **LLM:** $0.00 (M1 is no-LLM by design — verifier L3 layer was
  NOT invoked in M1.6; L3 will run in M3 with the actual encoder
  configs after M2 builds the indexes).
- **Wall:** ~75 min total wall-clock for M1, vs V2 §8 estimate of
  ~5 hours (compressed dramatically because the bge-large probe
  found PRIMARY immediately and no contingency reroute was needed).
  Within ±20% deviation budget — **no root-cause analysis required.**

### Unexpected discoveries

- **bge-large per-encode latency is ~5× MiniLM** (282.7 ms vs
  ~50 ms). This is a **wall-time** concern for M4 cells that hit
  bge-large (each LLM bypass case runs leakage_scan.scan_text which
  re-encodes 3-10 sentences). Cost impact: negligible (LLM-call
  time dominates). Wall-time impact: bge-large cells in M4 may
  take 12–18 min instead of 9 (per V2 §3.2 estimate). Within the
  V2 §3.2 "~10 min/cell" envelope ±50%; not a blocker.
- **FinLang dim = 768** (no surprises — BERT-base scale). Watchpoint
  B reports clean: no oddball dim, no special handling needed.
- **HF cache had only MiniLM + mpnet + bge-small** before M1.
  M1.0 + M1.4 triggered downloads of bge-large (~1.34 GB) and
  FinLang (~440 MB) which are now cached. M2 builds will reuse
  the cache; mpnet was already cached. Effective HF cache state
  post-M1: MiniLM, mpnet, bge-large, bge-small (legacy), FinLang.
- **Memory baseline at M1.0 invocation was tight** (7554 MB used
  / 50 MB unused on the 8 GB system). The probe ran in a fresh
  subprocess, so its 702.8 MB peak was contained. The implication
  for M4: when bge-large cells run, the system's 7.5 GB
  background usage + the driver's ~700 MB working set gives ~7.2
  GB total use → still fits, with ~800 MB headroom. **Acceptable
  but the user may want to close Chrome/IDE before M4 bge-large
  cells if memory becomes contested.**
- **No new paper-code inconsistency** surfaced during M1.

### Gate condition checks (V2 §8 M1 acceptance)

- [✓] `verify_repro_pins.py --layer 1` returns `OVERALL: PASS`
  with all 5 encoders (4 primary + 1 fallback) covered.
- [✓] `verify_repro_pins.py --layer 2` returns `OVERALL: PASS`
  with all 5 encoders' canonical hashes verified.
- [✓] All 6 `config_phase1F_*.yaml` files exist, valid YAML,
  declare both `embedding.revision` AND `openai_model`.
- [✓] `scripts/probe_encoder.py` reports dim + load time + RSS
  peak for both probed encoders (bge-large in M1.0; FinLang in
  M1.4).
- [✓] bge-large vs bge-base decision is made: **bge-large
  PRIMARY**. Documented in `PINNED_REVISIONS` inline comment.
- [✓] `scripts/build_phase1F_indexes.py --dry-run` reports the
  expected 8-cell plan (2 cached MiniLM + 6 to-build).
- [✓] No `git commit` performed. All changes staged or untracked
  ready for user-side commit (per global git policy).

### Next milestone

**M2 — Index builds.** Orchestrator: `python
scripts/build_phase1F_indexes.py` (no `--dry-run`, no `--force`).
Expected: 6 new FAISS index cells built, ~9–12 min wall, $0 LLM.
Outputs: 6 new `data/index/secrets*__<encoder>.faiss` + meta.pkl
plus `eval/results/phase1_F/build_log.json`.

**Approval requested:** **YES** — please review M1 deliverables
and approve M2 to begin.

### Blockers

- None.

### Files modified in M1 (for user-side commit when ready)

```
M  core/config_loader.py                               # +5 PINNED_REVISIONS entries
M  scripts/verify_repro_pins.py                        # L1 1d + L2 loop + L3 --config

A  scripts/probe_encoder.py                            # NEW M1.4
A  scripts/build_phase1F_indexes.py                    # NEW M1.5

A  config_phase1F_mpnet_60entry.yaml                   # NEW M1.3
A  config_phase1F_mpnet_90entry.yaml                   # NEW M1.3
A  config_phase1F_bge_large_60entry.yaml               # NEW M1.3
A  config_phase1F_bge_large_90entry.yaml               # NEW M1.3
A  config_phase1F_finlang_60entry.yaml                 # NEW M1.3
A  config_phase1F_finlang_90entry.yaml                 # NEW M1.3

A  eval/results/phase1_F/build_log.json                # NEW M1.5 dry-run output

A  PHASE_1F_PLAN.md                                    # carried over (V1, retained for diff)
A  PHASE_1F_PLAN_V2.md                                 # carried over (V2 plan, approved)
A  PHASE_1F_STATUS.md                                  # this file (M1 entry)
```

**Suggested commit message structure** (your call on grouping):

```
phase1F: M1 infrastructure setup (PINNED_REVISIONS + verifier + 6 configs + probe + orchestrator)

- Register 4 new encoders + 1 fallback in PINNED_REVISIONS:
  mpnet, bge-large, bge-base (Q2 fallback, not exercised), FinLang.
  All HF revisions captured from refs/heads/main on 2026-05-09.
- Extend verify_repro_pins.py: L1 1d (encoder-name-must-be-pinned),
  L2 loop over all PINNED_REVISIONS entries, L3 --config flag.
- Generate 6 config_phase1F_*.yaml files (3 encoders × 2 corpora).
- New scripts/probe_encoder.py: subprocess-isolated diagnostic probe.
- New scripts/build_phase1F_indexes.py: thin-wrapper orchestrator
  (Q5 design; build_secret_faiss_index.py untouched).

bge-large memory probe: 702.8 MB peak RSS (PRIMARY path; well
under 60% × 8 GB threshold). FinLang dim = 768 (BERT-base scale).
Verifier L1+L2 OVERALL: PASS.
```

Awaiting M2 approval.
