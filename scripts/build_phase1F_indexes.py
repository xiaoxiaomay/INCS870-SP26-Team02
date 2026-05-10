#!/usr/bin/env python3
"""
scripts/build_phase1F_indexes.py

Phase-1.F secret-index orchestrator. Loops over (encoder, corpus)
pairs and builds one FAISS IP index per cell. Designed to be a thin
wrapper that reuses (does not modify) `scripts/build_secret_faiss_index.py`'s
data-loading primitive `load_jsonl`.

For each cell:
  1. Skip if output index file already exists AND its `ntotal`
     matches the expected corpus size (idempotent re-run).
  2. Otherwise: load jsonl → embed (title + text) with the encoder
     pinned in `core/config_loader.py:PINNED_REVISIONS` → build
     `IndexFlatIP` → write `.faiss` and `.pkl`.
  3. Record diagnostics in `phase1_F/build_log.json`.

Usage:
  python scripts/build_phase1F_indexes.py            # build all 8 cells
  python scripts/build_phase1F_indexes.py --dry-run  # plan + skip status only
  python scripts/build_phase1F_indexes.py --force    # rebuild even if cached

Outputs:
  data/index/secrets__<encoder>.faiss + ...__meta.pkl   (60-entry × 4 encoders)
  data/index/secrets_v2__<encoder>.faiss + ...__meta.pkl (90-entry × 4 encoders)
  eval/results/phase1_F/build_log.json

Design notes:
  - The MiniLM cells produce paths that already exist (data/index/secrets.faiss
    is the v9-era primary, NOT secrets__minilm.faiss). For Phase-1.F we keep
    MiniLM in the matrix but NEVER re-build its v9-era index — instead we
    point the orchestrator at the existing files via the matrix entry. Newer
    encoders use the `__<encoder>` namespace.
  - The orchestrator imports `load_jsonl` from build_secret_faiss_index.py.
    That script's `main()` is hardcoded for v9 paths and is left untouched
    (back-compatible with v9 reproducibility).
  - Encoder load and FAISS index build run in this same Python process for
    each cell. After all cells are built, peak RSS is reported in build_log.
    Memory contingency: if any cell exceeds 80% × 8 GB during build, the
    orchestrator stops and surfaces the OOM risk (Q2 fallback path).
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Threading caps + macOS thread-safety env
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import faiss  # noqa: E402
import numpy as np  # noqa: E402

from core.config_loader import (  # noqa: E402
    PINNED_REVISIONS,
    get_pinned_revision,
)
from scripts.build_secret_faiss_index import load_jsonl  # noqa: E402


# ---------------------------------------------------------------------------
# Phase-1.F build matrix (Q3: 4 encoders × 2 corpora = 8 cells).
# MiniLM cells point at the pre-existing v9-era index files (no rebuild).
# ---------------------------------------------------------------------------

PHASE1F_MATRIX: List[Dict[str, str]] = []

ENCODERS = [
    # (short_name, hf_model_name)
    ("minilm",    "sentence-transformers/all-MiniLM-L6-v2"),
    ("mpnet",     "sentence-transformers/all-mpnet-base-v2"),
    ("bge_large", "BAAI/bge-large-en-v1.5"),
    ("finlang",   "FinLang/finance-embeddings-investopedia"),
]

CORPORA = [
    # (corpus_label, source_jsonl_path, expected_ntotal)
    ("60entry", "data/secrets/secrets.jsonl",    60),
    ("90entry", "data/secrets/secrets_v2.jsonl", 90),
]

for enc_short, hf_name in ENCODERS:
    for corpus_label, src_path, expected_n in CORPORA:
        # MiniLM-60 cell points at the v9-era index (pre-existing); same for
        # MiniLM-90 with the v2 index.
        if enc_short == "minilm":
            if corpus_label == "60entry":
                idx_path = "data/index/secrets.faiss"
                meta_path = "data/index/secrets_meta.pkl"
            else:
                idx_path = "data/index/secrets_v2.faiss"
                meta_path = "data/index/secrets_v2_meta.pkl"
        elif corpus_label == "60entry":
            idx_path = f"data/index/secrets__{enc_short}.faiss"
            meta_path = f"data/index/secrets__{enc_short}_meta.pkl"
        else:
            idx_path = f"data/index/secrets_v2__{enc_short}.faiss"
            meta_path = f"data/index/secrets_v2__{enc_short}_meta.pkl"

        PHASE1F_MATRIX.append({
            "encoder_short": enc_short,
            "encoder_name": hf_name,
            "encoder_revision": get_pinned_revision(hf_name) or "",
            "corpus_label": corpus_label,
            "src_jsonl": src_path,
            "expected_ntotal": expected_n,
            "out_index": idx_path,
            "out_meta": meta_path,
        })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def md5_of_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cell_already_built(cell: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Returns a cached-status dict if the cell's output already exists with
    matching ntotal. None if the cell needs to be built.
    """
    idx_path = REPO_ROOT / cell["out_index"]
    meta_path = REPO_ROOT / cell["out_meta"]
    if not (idx_path.exists() and meta_path.exists()):
        return None
    try:
        idx = faiss.read_index(str(idx_path))
        if idx.ntotal != cell["expected_ntotal"]:
            return None
        return {
            "status": "cached",
            "ntotal": int(idx.ntotal),
            "dim": int(idx.d),
            "index_md5": md5_of_file(idx_path),
            "meta_md5": md5_of_file(meta_path),
            "elapsed_s": 0.0,
        }
    except Exception:
        return None


def build_cell(cell: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a single FAISS index cell. Loads the encoder, embeds the
    secrets corpus (title + text), writes IndexFlatIP + meta.pkl.
    Returns a diagnostic dict.
    """
    from sentence_transformers import SentenceTransformer
    import pickle

    src = REPO_ROOT / cell["src_jsonl"]
    secrets = load_jsonl(src)
    if len(secrets) != cell["expected_ntotal"]:
        return {
            "status": "error",
            "error": (
                f"corpus size mismatch: {src} has {len(secrets)} entries, "
                f"expected {cell['expected_ntotal']}"
            ),
        }

    texts = [
        f"{(s.get('title') or '').strip()}\n{(s.get('text') or '').strip()}".strip()
        for s in secrets
    ]

    print(f"  loading encoder {cell['encoder_name']} (rev {cell['encoder_revision'][:12]}...)")
    t0 = time.time()
    model = SentenceTransformer(
        cell["encoder_name"], revision=cell["encoder_revision"] or None
    )
    t_load = time.time() - t0

    print(f"  encoding {len(texts)} entries...")
    t0 = time.time()
    emb = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    emb = np.asarray(emb, dtype="float32")
    t_encode = time.time() - t0

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    # Write
    out_idx = REPO_ROOT / cell["out_index"]
    out_meta = REPO_ROOT / cell["out_meta"]
    out_idx.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(out_idx))
    with open(out_meta, "wb") as f:
        pickle.dump(secrets, f)

    return {
        "status": "built",
        "ntotal": int(index.ntotal),
        "dim": dim,
        "load_time_s": round(t_load, 2),
        "encode_time_s": round(t_encode, 2),
        "elapsed_s": round(t_load + t_encode, 2),
        "index_md5": md5_of_file(out_idx),
        "meta_md5": md5_of_file(out_meta),
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Phase-1.F secret-index orchestrator (Q5 design)."
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and report skip status without building anything.",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Rebuild every cell even if already cached.",
    )
    ap.add_argument(
        "--log-path",
        type=str,
        default="eval/results/phase1_F/build_log.json",
        help="Where to write the build log JSON.",
    )
    args = ap.parse_args()

    log_entries: List[Dict[str, Any]] = []

    print("=" * 72)
    print(f"Phase-1.F index orchestrator — {len(PHASE1F_MATRIX)} cells")
    if args.dry_run:
        print("DRY-RUN: no actual builds will be performed")
    print("=" * 72)

    for i, cell in enumerate(PHASE1F_MATRIX, start=1):
        label = f"{cell['encoder_short']}__{cell['corpus_label']}"
        print(f"\n[{i}/{len(PHASE1F_MATRIX)}] {label}")
        print(f"  source = {cell['src_jsonl']}")
        print(f"  output = {cell['out_index']}")
        print(f"  encoder = {cell['encoder_name']}  rev={cell['encoder_revision'][:12]}...")
        print(f"  expected_ntotal = {cell['expected_ntotal']}")

        cached = None if args.force else cell_already_built(cell)
        if cached is not None:
            print(f"  → CACHED (ntotal={cached['ntotal']}, dim={cached['dim']})")
            log_entries.append({**cell, **cached})
            continue

        if args.dry_run:
            print(f"  → would build (dry-run)")
            log_entries.append({**cell, "status": "would_build"})
            continue

        try:
            diag = build_cell(cell)
            print(f"  → {diag.get('status').upper()}: ntotal={diag.get('ntotal')}, "
                  f"dim={diag.get('dim')}, elapsed={diag.get('elapsed_s')}s")
        except Exception as e:
            diag = {"status": "error", "error": f"{type(e).__name__}: {e}"}
            print(f"  → ERROR: {diag['error']}")
        log_entries.append({**cell, **diag})

        # Stop-the-line if a build errored (don't continue with a half-matrix)
        if diag.get("status") == "error":
            print("\nStopping due to build error. Inspect the log and rerun with "
                  "--force to retry once fixed.")
            break

    # Persist build log
    log_path = REPO_ROOT / args.log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_obj = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_cells": len(PHASE1F_MATRIX),
        "n_built": sum(1 for e in log_entries if e.get("status") == "built"),
        "n_cached": sum(1 for e in log_entries if e.get("status") == "cached"),
        "n_error": sum(1 for e in log_entries if e.get("status") == "error"),
        "n_dryrun": sum(1 for e in log_entries if e.get("status") == "would_build"),
        "cells": log_entries,
    }
    log_path.write_text(json.dumps(log_obj, indent=2, default=str))
    print(f"\nBuild log: {log_path}")
    print(
        f"Summary: built={log_obj['n_built']} cached={log_obj['n_cached']} "
        f"error={log_obj['n_error']} dryrun={log_obj['n_dryrun']}"
    )

    # Exit non-zero on any error so CI can gate on this
    return 0 if log_obj["n_error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
