#!/usr/bin/env python3
"""
scripts/calibrate_thresholds.py

Phase-1.F M3.5: per-encoder Gate-1 threshold calibration.

Background
----------
M3 sanity (mpnet × 90, 10 prompts) showed mpnet's cosine
distribution is ~0.23 lower than MiniLM's in the threshold band,
so the v9-tuned `query_precheck.sensitive_threshold = 0.50`
under-blocks on mpnet (and presumably other non-MiniLM encoders).
Per V2 §7.1 prescription and the user's M3.5 ruling, calibrate
the `sensitive_threshold` per encoder to yield Gate-1 cumulative
FPR ≈ 3.0% on the v9-canonical 100-query benign corpus.

Methodology
-----------
For each (encoder, corpus) cell:
  1. Load encoder with pinned revision.
  2. Load secret FAISS index.
  3. For each benign query in `data/benchmark/normal_prompts.jsonl`:
     - Run Gate 0 Decode + Gate 0a + Gate 0b (encoder-independent).
     - Encode query and compute cosine vs secret index → cache
       `gate_1_score`.
     - Cache whether the query has an intent amplifier (determines
       which threshold tier applies) and whether HYP_01 fires.
  4. For each threshold value in {0.30, 0.35, ..., 0.80}:
     - For each query: replay the gate stack with the sweep value
       substituted for `sensitive_threshold`. Block iff Gate 0a/0b
       fired OR (amplifier-present AND score >= sweep) OR
       (HYP_01 AND score >= 0.45) OR (no-amplifier AND
       score >= 0.75).
     - Count cumulative blocks → FPR = blocks / total.
  5. Select calibrated threshold = sweep value with FPR closest to
     3.0%. Tie-broken toward higher threshold (more conservative
     / fewer false blocks).
  6. Robustness check: re-evaluate the calibrated threshold on
     the 219-query real-world corpus
     (`data/eval/real_world_normal_prompts.json`). Record drift.

Scope
-----
- Calibrates only `sensitive_threshold` (the tier that fires on
  intent-amplifier queries — the M3 finding's locus of mismatch).
- Keeps `threshold` (0.75) and `strict_threshold` (0.45) at v9
  values. Documented as a design choice; deeper tri-tier
  calibration deferred to a future phase if needed.
- $0 LLM cost (pre-gate only — encoder + FAISS).
- Wall: ~10s per cell × 8 cells ≈ ~80s total.

Usage
-----
  # Sweep one cell
  python scripts/calibrate_thresholds.py \\
      --encoder sentence-transformers/all-mpnet-base-v2 \\
      --secret-index data/index/secrets_v2__mpnet.faiss \\
      --secret-meta data/index/secrets_v2__mpnet_meta.pkl \\
      --output eval/results/phase1_F/calibration/mpnet_90.json

  # Sweep all 8 cells in one run
  python scripts/calibrate_thresholds.py --all

Output
------
Per-cell JSON record with: encoder, corpus, all sweep points
(threshold, fpr, n_blocked, breakdown), calibrated_threshold,
robustness_fpr_on_219.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Threading caps (consistent with other Phase-1.F scripts)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("USE_POSTGRES", "false")

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

import numpy as np  # noqa: E402

from scripts.run_rag_with_audit import (  # noqa: E402
    rule_gate,
    embedding_secret_precheck,
    load_config,
)
from scripts.leakage_scan import load_faiss_index  # noqa: E402
from gates.gate_0_decode import decode_gate  # noqa: E402
from core.config_loader import (  # noqa: E402
    PINNED_REVISIONS,
    get_pinned_revision,
)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

CALIBRATION_CORPUS = REPO_ROOT / "data" / "benchmark" / "normal_prompts.jsonl"
ROBUSTNESS_CORPUS = REPO_ROOT / "data" / "eval" / "real_world_normal_prompts.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "eval" / "results" / "phase1_F" / "calibration"

THRESHOLD_GRID = [round(x * 0.05 + 0.30, 2) for x in range(11)]  # 0.30, 0.35, …, 0.80
TARGET_FPR = 0.03

# Phase-1.F encoder × corpus matrix (8 cells)
PHASE1F_CALIBRATION_CELLS: List[Dict[str, str]] = [
    # MiniLM (re-calibrated for symmetry per user's M3.5 instruction)
    {
        "encoder_short": "minilm",
        "encoder_name": "sentence-transformers/all-MiniLM-L6-v2",
        "corpus_label": "60entry",
        "secret_index": "data/index/secrets.faiss",
        "secret_meta":  "data/index/secrets_meta.pkl",
        "config_template": "config.yaml",
        "config_target":   "config_phase1F_minilm_60entry.yaml",
    },
    {
        "encoder_short": "minilm",
        "encoder_name": "sentence-transformers/all-MiniLM-L6-v2",
        "corpus_label": "90entry",
        "secret_index": "data/index/secrets_v2.faiss",
        "secret_meta":  "data/index/secrets_v2_meta.pkl",
        "config_template": "config_v2.yaml",
        "config_target":   "config_phase1F_minilm_90entry.yaml",
    },
    # mpnet
    {
        "encoder_short": "mpnet",
        "encoder_name": "sentence-transformers/all-mpnet-base-v2",
        "corpus_label": "60entry",
        "secret_index": "data/index/secrets__mpnet.faiss",
        "secret_meta":  "data/index/secrets__mpnet_meta.pkl",
        "config_template": "config.yaml",
        "config_target":   "config_phase1F_mpnet_60entry.yaml",
    },
    {
        "encoder_short": "mpnet",
        "encoder_name": "sentence-transformers/all-mpnet-base-v2",
        "corpus_label": "90entry",
        "secret_index": "data/index/secrets_v2__mpnet.faiss",
        "secret_meta":  "data/index/secrets_v2__mpnet_meta.pkl",
        "config_template": "config_v2.yaml",
        "config_target":   "config_phase1F_mpnet_90entry.yaml",
    },
    # bge_large
    {
        "encoder_short": "bge_large",
        "encoder_name": "BAAI/bge-large-en-v1.5",
        "corpus_label": "60entry",
        "secret_index": "data/index/secrets__bge_large.faiss",
        "secret_meta":  "data/index/secrets__bge_large_meta.pkl",
        "config_template": "config.yaml",
        "config_target":   "config_phase1F_bge_large_60entry.yaml",
    },
    {
        "encoder_short": "bge_large",
        "encoder_name": "BAAI/bge-large-en-v1.5",
        "corpus_label": "90entry",
        "secret_index": "data/index/secrets_v2__bge_large.faiss",
        "secret_meta":  "data/index/secrets_v2__bge_large_meta.pkl",
        "config_template": "config_v2.yaml",
        "config_target":   "config_phase1F_bge_large_90entry.yaml",
    },
    # FinLang
    {
        "encoder_short": "finlang",
        "encoder_name": "FinLang/finance-embeddings-investopedia",
        "corpus_label": "60entry",
        "secret_index": "data/index/secrets__finlang.faiss",
        "secret_meta":  "data/index/secrets__finlang_meta.pkl",
        "config_template": "config.yaml",
        "config_target":   "config_phase1F_finlang_60entry.yaml",
    },
    {
        "encoder_short": "finlang",
        "encoder_name": "FinLang/finance-embeddings-investopedia",
        "corpus_label": "90entry",
        "secret_index": "data/index/secrets_v2__finlang.faiss",
        "secret_meta":  "data/index/secrets_v2__finlang_meta.pkl",
        "config_template": "config_v2.yaml",
        "config_target":   "config_phase1F_finlang_90entry.yaml",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_benign_corpus(path: Path) -> List[Dict[str, Any]]:
    """
    Loads benign-corpus rows. Handles both:
      - .jsonl  (data/benchmark/normal_prompts.jsonl, 100 rows)
      - .json with list root (data/eval/real_world_normal_prompts.json)
        — filter to is_synthetic=False (real-world only) per M3-FACT.
    """
    if str(path).endswith(".jsonl"):
        return load_jsonl(path)
    with open(path) as f:
        rows = json.load(f)
    if isinstance(rows, list):
        return [
            r for r in rows
            if str(r.get("is_synthetic", True)).lower() != "true"
        ]
    raise ValueError(f"unexpected JSON shape at {path}")


def precompute_query_features(
    queries: List[Dict[str, Any]],
    embed_model,
    sec_index,
    sec_meta,
    cfg: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    For each benign query, run the encoder-dependent measurements ONCE:
      - Gate 0 Decode (encoder-independent but cheap, run uniformly)
      - Gate 0a + Gate 0b → block flag (encoder-independent)
      - HYP_01 flag (encoder-independent)
      - amplifier-present flag (encoder-independent)
      - Gate 1 cosine score (encoder-DEPENDENT — we cache this)

    Returns one row per query with the cached features. The threshold
    sweep then operates only on these cached rows (no re-encoding).
    """
    pre_cfg = cfg.get("query_precheck", {}) or {}
    amplifiers = [str(a).lower() for a in pre_cfg.get("intent_amplifiers", [])]
    decode_cfg = cfg.get("gate_0_decode", {}) or {}
    policy_cfg = cfg.get("policy", {}) or {}

    results = []
    for q_row in queries:
        query = q_row.get("query", "") or q_row.get("prompt", "") or q_row.get("text", "")
        if not query:
            continue
        # Gate 0 Decode (rare on benigns; track for completeness)
        decoded_query = query
        if decode_cfg.get("enabled", False):
            d_res = decode_gate(query, decode_cfg)
            if d_res.get("encoding_detected"):
                decoded_query = d_res["decoded_text"]
        # Gate 0a + 0b
        g0_res = rule_gate(decoded_query, policy_cfg)
        gate_0_blocked = bool(g0_res.get("blocked", False))
        flagged_strict = bool(g0_res.get("flagged_for_strict", False))
        # Amplifier check
        q_lower = decoded_query.lower()
        has_amplifier = any(amp in q_lower for amp in amplifiers)
        # Gate 1 score (single FAISS search — encoder-dependent, cached)
        # Use a high threshold (1.0) so embedding_secret_precheck does NOT
        # report blocked=True; we just want the score.
        qv = embed_model.encode(
            [decoded_query], normalize_embeddings=True
        ).astype("float32")
        g1_res = embedding_secret_precheck(
            embed_model,
            decoded_query,
            sec_index,
            sec_meta,
            threshold=1.0,
            top_k=int(pre_cfg.get("top_k_secrets", 3)),
            query_vec=qv,
        )
        results.append({
            "_id": q_row.get("_id") or q_row.get("id") or "",
            "query": query[:200],
            "gate_0_blocked": gate_0_blocked,
            "flagged_strict": flagged_strict,
            "has_amplifier": has_amplifier,
            "gate_1_score": float(g1_res["best_score"]),
        })
    return results


def evaluate_at_threshold(
    rows: List[Dict[str, Any]],
    sensitive_threshold: float,
    base_threshold: float = 0.75,
    strict_threshold: float = 0.45,
) -> Dict[str, Any]:
    """
    Replay the gate stack at the given sensitive_threshold sweep value,
    holding base_threshold and strict_threshold at v9 defaults.
    Returns FPR + breakdown.
    """
    n = len(rows)
    blocked_g0 = blocked_g1_amp = blocked_g1_base = blocked_g1_strict = 0
    for r in rows:
        if r["gate_0_blocked"]:
            blocked_g0 += 1
            continue
        score = r["gate_1_score"]
        if r["flagged_strict"]:
            if score >= strict_threshold:
                blocked_g1_strict += 1
        elif r["has_amplifier"]:
            if score >= sensitive_threshold:
                blocked_g1_amp += 1
        else:
            if score >= base_threshold:
                blocked_g1_base += 1
    blocked_total = blocked_g0 + blocked_g1_amp + blocked_g1_base + blocked_g1_strict
    return {
        "sensitive_threshold": sensitive_threshold,
        "n_total": n,
        "n_blocked": blocked_total,
        "blocked_g0": blocked_g0,
        "blocked_g1_amplifier": blocked_g1_amp,
        "blocked_g1_base": blocked_g1_base,
        "blocked_g1_strict": blocked_g1_strict,
        "fpr": round(blocked_total / max(n, 1), 4),
    }


def select_calibrated_threshold(
    sweep_results: List[Dict[str, Any]],
    target_fpr: float = TARGET_FPR,
) -> Tuple[float, Dict[str, Any]]:
    """
    Pick the threshold whose FPR is closest to target. Ties broken
    toward HIGHER threshold (more conservative — blocks fewer benigns).
    Returns (calibrated_threshold, the_winning_sweep_row).
    """
    best = None
    best_eps = float("inf")
    for r in sweep_results:
        eps = abs(r["fpr"] - target_fpr)
        # Tie-break: prefer higher threshold
        if eps < best_eps - 1e-9 or (
            abs(eps - best_eps) < 1e-9 and (
                best is None or r["sensitive_threshold"] > best["sensitive_threshold"]
            )
        ):
            best = r
            best_eps = eps
    return best["sensitive_threshold"], best


# ---------------------------------------------------------------------------
# Per-cell driver
# ---------------------------------------------------------------------------


def calibrate_cell(cell: Dict[str, str], output_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Full M3.5 pipeline for one (encoder, corpus) cell:
      1. Load encoder + FAISS index.
      2. Pre-compute features on 100 calibration queries.
      3. Sweep sensitive_threshold across THRESHOLD_GRID; record FPR per point.
      4. Select calibrated threshold (closest to TARGET_FPR=0.03).
      5. Robustness verify: same threshold on 219 real-world queries; record drift.
      6. Persist per-cell JSON to <output_dir>/<encoder_short>_<corpus_label>.json.
    Returns the per-cell record dict (also returned for aggregation).
    """
    print(f"\n=== Calibrating {cell['encoder_short']} × {cell['corpus_label']} ===")
    print(f"  encoder = {cell['encoder_name']}")
    print(f"  index   = {cell['secret_index']}")
    print(f"  template = {cell['config_template']}  →  target = {cell['config_target']}")

    # Load encoder
    from sentence_transformers import SentenceTransformer
    revision = get_pinned_revision(cell["encoder_name"])
    if not revision:
        raise RuntimeError(f"no PINNED_REVISIONS entry for {cell['encoder_name']}")
    t0 = time.time()
    embed_model = SentenceTransformer(cell["encoder_name"], revision=revision)
    t_load = time.time() - t0
    print(f"  encoder loaded in {t_load:.1f}s, revision={revision[:12]}...")

    # Load secret index + base config
    sec_index, sec_meta = load_faiss_index(
        str(REPO_ROOT / cell["secret_index"]),
        str(REPO_ROOT / cell["secret_meta"]),
    )
    template_cfg = load_config(str(REPO_ROOT / cell["config_template"]))

    # Pre-compute calibration corpus features
    print(f"  pre-computing features on {CALIBRATION_CORPUS.name}...")
    cal_queries = load_benign_corpus(CALIBRATION_CORPUS)
    t0 = time.time()
    cal_rows = precompute_query_features(
        cal_queries, embed_model, sec_index, sec_meta, template_cfg
    )
    t_features = time.time() - t0
    print(
        f"  cached features for {len(cal_rows)} queries "
        f"in {t_features:.1f}s (mean Gate-1 cosine = "
        f"{np.mean([r['gate_1_score'] for r in cal_rows]):.4f}, "
        f"max = {np.max([r['gate_1_score'] for r in cal_rows]):.4f})"
    )

    # Sweep sensitive_threshold across grid
    print(f"  sweep grid: {THRESHOLD_GRID}")
    sweep_results = [
        evaluate_at_threshold(cal_rows, t)
        for t in THRESHOLD_GRID
    ]
    if verbose:
        for r in sweep_results:
            print(
                f"    sensitive_threshold={r['sensitive_threshold']:.2f}: "
                f"fpr={r['fpr']:.4f} (g0={r['blocked_g0']} "
                f"amp={r['blocked_g1_amplifier']} base={r['blocked_g1_base']} "
                f"strict={r['blocked_g1_strict']})"
            )

    # Select calibrated threshold
    calibrated_threshold, calibrated_row = select_calibrated_threshold(sweep_results)
    print(
        f"  calibrated sensitive_threshold = {calibrated_threshold:.2f} "
        f"(fpr = {calibrated_row['fpr']:.4f}, "
        f"target = {TARGET_FPR}, "
        f"|eps| = {abs(calibrated_row['fpr'] - TARGET_FPR):.4f})"
    )

    # Robustness check on 219-real corpus
    print(f"  robustness check on {ROBUSTNESS_CORPUS.name}...")
    rb_queries = load_benign_corpus(ROBUSTNESS_CORPUS)
    rb_rows = precompute_query_features(
        rb_queries, embed_model, sec_index, sec_meta, template_cfg
    )
    robustness = evaluate_at_threshold(rb_rows, calibrated_threshold)
    print(
        f"  robustness: 219-corpus FPR at calibrated threshold "
        f"= {robustness['fpr']:.4f} (drift from 100-corpus = "
        f"{robustness['fpr'] - calibrated_row['fpr']:+.4f}pp)"
    )

    # Persist
    record = {
        "encoder_short": cell["encoder_short"],
        "encoder_name": cell["encoder_name"],
        "encoder_revision": revision,
        "corpus_label": cell["corpus_label"],
        "secret_index": cell["secret_index"],
        "config_template": cell["config_template"],
        "config_target":   cell["config_target"],
        "calibration_corpus": str(CALIBRATION_CORPUS.relative_to(REPO_ROOT)),
        "calibration_corpus_n": len(cal_rows),
        "robustness_corpus":  str(ROBUSTNESS_CORPUS.relative_to(REPO_ROOT)),
        "robustness_corpus_n": len(rb_rows),
        "target_fpr": TARGET_FPR,
        "threshold_grid": THRESHOLD_GRID,
        "sweep": sweep_results,
        "calibrated_sensitive_threshold": calibrated_threshold,
        "calibrated_fpr_on_100": calibrated_row["fpr"],
        "calibrated_n_blocked_on_100": calibrated_row["n_blocked"],
        "robustness_fpr_on_219": robustness["fpr"],
        "robustness_n_blocked_on_219": robustness["n_blocked"],
        "robustness_drift_pp": round(
            robustness["fpr"] - calibrated_row["fpr"], 4
        ),
        "encoder_load_time_s": round(t_load, 2),
        "encoder_n_features_s": round(t_features, 2),
        "v9_default_sensitive_threshold": 0.50,
        "calibrated_minus_v9_default": round(calibrated_threshold - 0.50, 2),
        "design_choice_note": (
            "Only `query_precheck.sensitive_threshold` is calibrated. "
            "`threshold` (0.75 generic) and `strict_threshold` (0.45 HYP_01) "
            "are kept at v9 values. Per-tier calibration deferred."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{cell['encoder_short']}_{cell['corpus_label']}.json"
    out_path.write_text(json.dumps(record, indent=2, default=str))
    print(f"  wrote {out_path}")

    return record


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Phase-1.F M3.5 per-encoder Gate-1 threshold calibration"
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Run all 8 cells (4 encoders × 2 corpora).",
    )
    ap.add_argument(
        "--cell",
        type=str,
        default=None,
        help='Run a single cell by short name (e.g. "mpnet_90entry").',
    )
    ap.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Where to write per-cell JSON records.",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-threshold sweep table.",
    )
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    cells = []
    if args.all:
        cells = PHASE1F_CALIBRATION_CELLS
    elif args.cell:
        for c in PHASE1F_CALIBRATION_CELLS:
            if f"{c['encoder_short']}_{c['corpus_label']}" == args.cell:
                cells = [c]
                break
        if not cells:
            print(f"ERROR: unknown --cell '{args.cell}'", file=sys.stderr)
            return 2
    else:
        print("ERROR: must specify --all or --cell", file=sys.stderr)
        return 2

    print("=" * 72)
    print(f"M3.5 calibration — {len(cells)} cell(s)")
    print(f"calibration corpus: {CALIBRATION_CORPUS} (100 v9-canonical)")
    print(f"robustness corpus:  {ROBUSTNESS_CORPUS} (219 real-world V2-era)")
    print(f"target FPR: {TARGET_FPR}")
    print(f"sweep grid: {THRESHOLD_GRID}")
    print("=" * 72)

    records: List[Dict[str, Any]] = []
    t_start = time.time()
    for cell in cells:
        rec = calibrate_cell(cell, output_dir, verbose=args.verbose)
        records.append(rec)
    elapsed = time.time() - t_start

    # Aggregate summary
    summary_path = output_dir / "summary.json"
    summary = {
        "n_cells": len(records),
        "elapsed_s": round(elapsed, 2),
        "target_fpr": TARGET_FPR,
        "threshold_grid": THRESHOLD_GRID,
        "cells": records,
    }
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nsummary: {summary_path}")

    print("\n" + "=" * 72)
    print(f"{'cell':24s} {'cal_thr':>8s} {'fpr_100':>8s} {'fpr_219':>8s} "
          f"{'drift':>7s} {'eps_target':>10s}")
    print("-" * 72)
    for r in records:
        label = f"{r['encoder_short']}_{r['corpus_label']}"
        print(
            f"{label:24s} "
            f"{r['calibrated_sensitive_threshold']:>8.2f} "
            f"{r['calibrated_fpr_on_100']:>8.4f} "
            f"{r['robustness_fpr_on_219']:>8.4f} "
            f"{r['robustness_drift_pp']:>+7.4f} "
            f"{abs(r['calibrated_fpr_on_100'] - TARGET_FPR):>10.4f}"
        )
    print("=" * 72)
    print(f"total elapsed: {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
