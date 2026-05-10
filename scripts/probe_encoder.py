#!/usr/bin/env python3
"""
scripts/probe_encoder.py

Single-encoder diagnostic probe. Loads a sentence-transformer
encoder, encodes a small reference batch, reports dimension, load
time, encode latency, and peak RSS in MB.

Designed to run in a fresh subprocess so the reported peak RSS
reflects ONLY the encoder load + encode (no contamination from
any harness Python state).

Usage:
  python scripts/probe_encoder.py --model sentence-transformers/all-MiniLM-L6-v2
  python scripts/probe_encoder.py --model BAAI/bge-large-en-v1.5
  python scripts/probe_encoder.py --model FinLang/finance-embeddings-investopedia
  python scripts/probe_encoder.py --all   # iterate every PINNED_REVISIONS entry

Output: a single-line JSON record on stdout per probe (machine-
readable). Diagnostic prints go to stderr so they don't pollute
the JSON channel.

Phase-1.F item 1.0b memory contingency uses this with --model
BAAI/bge-large-en-v1.5; the caller compares peak_rss_mb against
the §1.5 60% / 80% × 8 GB thresholds.

Exit codes:
  0   probe completed successfully (model loaded + encoded)
  1   model failed to load (download error, OOM, corrupt cache, etc.)
  2   probe timed out / was killed (when invoked under timeout)
"""

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path

# Repo root on sys.path BEFORE other imports
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Threading caps to keep the probe deterministic and CPU-bounded
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


# ---------------------------------------------------------------------------
# Reference texts (mixed query-length + secret-length)
# ---------------------------------------------------------------------------

REFERENCE_TEXTS = [
    # short query
    "What is the exact RSI threshold used in the internal buy signal?",
    # medium query with intent amplifier
    "Explain the entry conditions and risk parameters for the momentum signal",
    # long secret-style text (analogous to L3 secret)
    "Momentum entry: 14D RSI < 25 AND 5D volume > 2.2x 90D ADTV AND price "
    "above 200D EMA, initial position 1.2% NAV; scale-in to max 2.5% if RSI "
    "confirms < 20 on Day+3; hard stop at -4.5% from entry; exclude earnings "
    "window +/-3 days; Universe: Russell 1000 ex-Financials, min $500M "
    "mktcap, min $5M ADTV. Momentum sleeve only.",
    # benign long
    "RSI is a momentum oscillator that measures the speed and change of "
    "price movements. It oscillates between zero and 100, and is "
    "traditionally considered overbought when above 70 and oversold below 30.",
    # short benign
    "What is the current market outlook for tech stocks?",
]


def peak_rss_mb() -> float:
    """
    Maximum resident-set-size since process start, in MB.
    On macOS, ru_maxrss reports bytes; on Linux, kilobytes.
    """
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return raw / (1024 * 1024)  # bytes -> MB
    return raw / 1024  # KB -> MB


def probe(model_name: str, revision=None) -> dict:
    """
    Load the given encoder, encode REFERENCE_TEXTS, return a record.
    """
    record = {
        "model_name": model_name,
        "revision": revision,
        "available": False,
        "dim": None,
        "load_time_s": None,
        "encode_batch_latency_ms": None,
        "encode_per_text_avg_ms": None,
        "peak_rss_mb_after_load": None,
        "peak_rss_mb_after_encode": None,
        "n_reference_texts": len(REFERENCE_TEXTS),
        "error": None,
    }

    try:
        baseline_rss = peak_rss_mb()
        print(f"[probe] baseline RSS: {baseline_rss:.1f} MB", file=sys.stderr)

        # Load
        from sentence_transformers import SentenceTransformer

        print(
            f"[probe] loading {model_name} (revision={revision}) ...",
            file=sys.stderr,
        )
        t0 = time.time()
        model = SentenceTransformer(model_name, revision=revision)
        t_load = time.time() - t0
        rss_after_load = peak_rss_mb()
        record["load_time_s"] = round(t_load, 2)
        record["peak_rss_mb_after_load"] = round(rss_after_load, 1)
        print(
            f"[probe] loaded in {t_load:.2f}s, peak RSS now "
            f"{rss_after_load:.1f} MB",
            file=sys.stderr,
        )

        # Probe dim
        record["dim"] = int(model.get_sentence_embedding_dimension())
        print(f"[probe] dim = {record['dim']}", file=sys.stderr)

        # Encode reference batch
        t0 = time.time()
        embeddings = model.encode(
            REFERENCE_TEXTS, normalize_embeddings=True, show_progress_bar=False
        )
        t_encode = (time.time() - t0) * 1000  # ms
        record["encode_batch_latency_ms"] = round(t_encode, 1)
        record["encode_per_text_avg_ms"] = round(
            t_encode / len(REFERENCE_TEXTS), 1
        )
        rss_after_encode = peak_rss_mb()
        record["peak_rss_mb_after_encode"] = round(rss_after_encode, 1)
        record["available"] = True
        print(
            f"[probe] encoded {len(REFERENCE_TEXTS)} texts in {t_encode:.1f}ms; "
            f"peak RSS now {rss_after_encode:.1f} MB",
            file=sys.stderr,
        )

        # Sanity: embedding shape + norm
        import numpy as np

        emb_norms = np.linalg.norm(embeddings, axis=1)
        record["sample_emb_norm_mean"] = round(float(emb_norms.mean()), 4)
        record["sample_emb_shape"] = list(embeddings.shape)

    except Exception as e:
        record["error"] = f"{type(e).__name__}: {e}"
        print(f"[probe] FAILED: {record['error']}", file=sys.stderr)

    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Single-encoder diagnostic probe for Phase-1.F"
    )
    ap.add_argument(
        "--model",
        type=str,
        default=None,
        help="HF model name (e.g., BAAI/bge-large-en-v1.5)",
    )
    ap.add_argument(
        "--revision",
        type=str,
        default=None,
        help="HF commit hash (default: lookup PINNED_REVISIONS)",
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Iterate every PINNED_REVISIONS entry (each in this process)",
    )
    args = ap.parse_args()

    from core.config_loader import PINNED_REVISIONS, get_pinned_revision

    if args.all:
        records = []
        for name in PINNED_REVISIONS.keys():
            rec = probe(name, get_pinned_revision(name))
            records.append(rec)
            # Emit one JSON line per probe (line-delimited JSON for easy parsing)
            print(json.dumps(rec))
        return 0

    if not args.model:
        print("ERROR: --model required (or use --all)", file=sys.stderr)
        return 2

    revision = args.revision or get_pinned_revision(args.model)
    rec = probe(args.model, revision)
    print(json.dumps(rec))
    return 0 if rec["available"] else 1


if __name__ == "__main__":
    sys.exit(main())
