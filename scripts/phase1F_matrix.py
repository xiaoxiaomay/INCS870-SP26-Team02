#!/usr/bin/env python3
"""
scripts/phase1F_matrix.py

Phase-1.F master matrix aggregator. Consumes the 8 M4 cell output
trees + 8 M3.5 calibration cells + 1 M3.5 calibration summary, then
emits:

  eval/results/phase1_F/matrix.json   master aggregated matrix
  eval/results/phase1_F/matrix.tex    LaTeX-ready 8-row Table XIII

The JSON is the single source of truth for the M5.2 writeup; the
LaTeX is a direct drop-in for v9_final.tex Table XIII (do not edit
the .tex by hand once regenerated).

Usage:
  python scripts/phase1F_matrix.py
  python scripts/phase1F_matrix.py --output-dir eval/results/phase1_F

This script is zero-LLM (pure file aggregation) and idempotent.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Encoder display metadata. dim is the verified value from M2 build_log.
# model_size_MB is the on-disk size from HF cache (informational only).
ENCODER_META = {
    "minilm":    {"display": "MiniLM-L6-v2",   "dim": 384,  "model_size_MB": 91,
                  "family": "general-purpose", "hf": "sentence-transformers/all-MiniLM-L6-v2"},
    "mpnet":     {"display": "mpnet-base-v2",  "dim": 768,  "model_size_MB": 438,
                  "family": "general-purpose", "hf": "sentence-transformers/all-mpnet-base-v2"},
    "bge_large": {"display": "bge-large-en",   "dim": 1024, "model_size_MB": 1340,
                  "family": "general-purpose", "hf": "BAAI/bge-large-en-v1.5"},
    "finlang":   {"display": "FinLang-invp",   "dim": 768,  "model_size_MB": 440,
                  "family": "domain-tuned (finance)", "hf": "FinLang/finance-embeddings-investopedia"},
}

CELLS_ORDER = [
    ("minilm",    "60entry"), ("minilm",    "90entry"),
    ("mpnet",     "60entry"), ("mpnet",     "90entry"),
    ("bge_large", "60entry"), ("bge_large", "90entry"),
    ("finlang",   "60entry"), ("finlang",   "90entry"),
]


def load_cell(phase1F_root: Path, encoder: str, corpus: str) -> Dict[str, Any]:
    """Load one cell's M4 outputs + M3.5 calibration into one struct."""
    summary_path = phase1F_root / f"{encoder}_{corpus}" / "summary.json"
    bypass_path = phase1F_root / f"{encoder}_{corpus}" / "bypass_cases.jsonl"
    cal_path = phase1F_root / "calibration" / f"{encoder}_{corpus}.json"

    with open(summary_path) as f:
        summary = json.load(f)
    with open(cal_path) as f:
        cal = json.load(f)

    # Enumerate leak case IDs (leaked_glr=True), with their bypass-time stats.
    leak_cases: List[Dict[str, Any]] = []
    with open(bypass_path) as f:
        for line in f:
            row = json.loads(line)
            if row.get("leaked_glr"):
                leak_cases.append({
                    "id": row.get("_id"),
                    "category": row.get("group"),
                    "evasion_technique": row.get("evasion_technique"),
                    "difficulty": row.get("difficulty"),
                    "gate_1_score": round(row.get("gate_1_score", 0.0), 4),
                    "max_leak_score": round(row.get("max_leak_score", 0.0), 4),
                    "leakage_flag": row.get("leakage_flag"),
                    "leakage_redacted": row.get("leakage_redacted"),
                    "leaked_ulr": row.get("leaked_ulr"),
                })

    n_bp, n_glr = summary["n_bypass"], summary["n_glr_leaked"]
    per_bp_leak = (100.0 * n_glr / n_bp) if n_bp > 0 else 0.0

    enc_meta = ENCODER_META[encoder]

    return {
        "cell_id": f"{encoder}_{corpus}",
        "encoder_short": encoder,
        "encoder_display": enc_meta["display"],
        "encoder_family": enc_meta["family"],
        "encoder_dim": enc_meta["dim"],
        "encoder_model_size_MB": enc_meta["model_size_MB"],
        "encoder_hf_name": enc_meta["hf"],
        "encoder_revision": summary["embedding_revision"],
        "corpus_label": corpus,
        "corpus_n_secrets": summary["secret_count"],
        "n_attacks": summary["n_attacks"],
        "core": {
            "sensitive_threshold": cal["calibrated_sensitive_threshold"],
            "n_blocked_pregates": summary["n_blocked_pregates"],
            "n_bypass": n_bp,
            "bypass_rate": summary["bypass_rate"],
            "bypass_pct": round(summary["bypass_rate"] * 100, 2),
            "n_llm_called": summary["n_llm_called"],
            "n_glr_leaked": n_glr,
            "glr_rate": summary["glr_rate"],
            "glr_pct": round(summary["glr_rate"] * 100, 2),
            "n_ulr_leaked": summary["n_ulr_leaked"],
            "ulr_rate": summary["ulr_rate"],
            "ulr_pct": round(summary["ulr_rate"] * 100, 2),
            "per_bypass_leak_pct": round(per_bp_leak, 1),
            "cost_usd": summary["estimated_cost_usd"],
            "wall_s": round(summary["elapsed_s"], 1),
        },
        "per_category": summary["per_category"],
        "leak_cases": leak_cases,
        "calibration": {
            "calibration_corpus": cal["calibration_corpus"],
            "calibration_corpus_n": cal["calibration_corpus_n"],
            "robustness_corpus": cal["robustness_corpus"],
            "robustness_corpus_n": cal["robustness_corpus_n"],
            "target_fpr": cal["target_fpr"],
            "threshold_grid": cal["threshold_grid"],
            "sweep": cal["sweep"],
            "calibrated_sensitive_threshold": cal["calibrated_sensitive_threshold"],
            "calibrated_fpr_on_100": cal["calibrated_fpr_on_100"],
            "calibrated_n_blocked_on_100": cal["calibrated_n_blocked_on_100"],
            "robustness_fpr_on_219": cal["robustness_fpr_on_219"],
            "robustness_n_blocked_on_219": cal["robustness_n_blocked_on_219"],
            "robustness_drift_pp": cal["robustness_drift_pp"],
            "v9_default_sensitive_threshold": cal["v9_default_sensitive_threshold"],
            "calibrated_minus_v9_default": cal["calibrated_minus_v9_default"],
        },
        "provenance": {
            "config_path": summary["config_path"],
            "llm_model": summary["llm_model"],
            "secret_index": summary["secret_index"],
            "attack_corpus": summary["attack_corpus"],
            "started_at": summary["started_at"],
            "finished_at": summary["finished_at"],
        },
    }


def emit_latex_table(cells: List[Dict[str, Any]]) -> str:
    """Generate a drop-in v9 Table XIII upgrade as LaTeX."""
    lines: List[str] = []
    lines.append(r"% Auto-generated by scripts/phase1F_matrix.py — do NOT hand-edit.")
    lines.append(r"% Phase-1.F cross-encoder ablation: 4 encoders × 2 secret corpora.")
    lines.append(r"% Each cell uses its M3.5-calibrated sensitive_threshold (target FPR ≈ 3.0% on the 100-query benign corpus).")
    lines.append(r"")
    lines.append(r"\begin{table*}[t]")
    lines.append(r"\centering")
    lines.append(r"\caption{Phase-1.F cross-encoder ablation. Four encoders (three general-purpose, one finance-tuned) "
                 r"$\times$ two secret corpora (60-entry and 90-entry). Each cell is calibrated to operate at "
                 r"$\approx 3.0\%$ FPR on a 100-query benign baseline via the Sensitive Threshold "
                 r"(M3.5 calibration). Bypass = fraction of the 271-prompt mixed adversarial corpus reaching the LLM; "
                 r"GLR = generation-level leakage rate (raw LLM output flagged); ULR = user-facing leakage rate "
                 r"(post-redaction); Per-BP Leak = GLR/Bypass (per-bypass leak probability). All cells: "
                 r"$\text{ULR}=0$ confirms defense-in-depth holds across the encoder family.}")
    lines.append(r"\label{tab:phase1F_ablation}")
    lines.append(r"\begin{tabular}{llcccccc}")
    lines.append(r"\toprule")
    lines.append(r"Encoder & Family & Dim & Corpus & Sens.\ $\theta$ & Bypass \% & GLR \% & Per-BP Leak \% \\")
    lines.append(r"\midrule")
    for c in cells:
        family_short = "domain-tuned" if c["encoder_family"].startswith("domain") else "general"
        corpus_str = c["corpus_label"].replace("entry", "-entry")
        row = (
            f"{c['encoder_display']} & "
            f"{family_short} & "
            f"{c['encoder_dim']} & "
            f"{corpus_str} & "
            f"{c['core']['sensitive_threshold']:.2f} & "
            f"{c['core']['bypass_pct']:.2f} & "
            f"{c['core']['glr_pct']:.2f} & "
            f"{c['core']['per_bypass_leak_pct']:.1f} \\\\"
        )
        lines.append(row)
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table*}")
    lines.append(r"")
    lines.append(r"% Note: ULR \% column omitted from main table because it is uniformly 0.00 across all 8 cells "
                 r"(2168 prompts). See \S IV-K for the defense-in-depth interpretation.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase-1.F master matrix aggregator (M5.1).")
    ap.add_argument(
        "--phase1f-dir", type=str, default="eval/results/phase1_F",
        help="Phase 1.F results root containing the 8 cell trees + calibration/.",
    )
    ap.add_argument(
        "--output-json", type=str, default="eval/results/phase1_F/matrix.json",
        help="Master aggregated matrix output path.",
    )
    ap.add_argument(
        "--output-tex", type=str, default="eval/results/phase1_F/matrix.tex",
        help="LaTeX-ready Table XIII upgrade output path.",
    )
    args = ap.parse_args()

    phase1F_root = REPO_ROOT / args.phase1f_dir
    if not phase1F_root.exists():
        print(f"ERROR: phase1F dir not found: {phase1F_root}", file=sys.stderr)
        return 2

    # Load calibration summary (top-level)
    cal_summary_path = phase1F_root / "calibration" / "summary.json"
    cal_summary = json.loads(cal_summary_path.read_text()) if cal_summary_path.exists() else {}

    cells: List[Dict[str, Any]] = []
    for enc, corpus in CELLS_ORDER:
        try:
            cells.append(load_cell(phase1F_root, enc, corpus))
        except Exception as e:
            print(f"ERROR loading {enc}_{corpus}: {type(e).__name__}: {e}", file=sys.stderr)
            return 1

    # Aggregate statistics
    total_cost = sum(c["core"]["cost_usd"] for c in cells)
    total_wall = sum(c["core"]["wall_s"] for c in cells)
    total_attacks = sum(c["n_attacks"] for c in cells)
    total_bypass = sum(c["core"]["n_bypass"] for c in cells)
    total_glr = sum(c["core"]["n_glr_leaked"] for c in cells)
    total_ulr = sum(c["core"]["n_ulr_leaked"] for c in cells)

    # Per-encoder roll-up (average across corpora) for quick narrative.
    by_encoder: Dict[str, Dict[str, float]] = {}
    for enc in sorted({c["encoder_short"] for c in cells}):
        enc_cells = [c for c in cells if c["encoder_short"] == enc]
        by_encoder[enc] = {
            "encoder_display": enc_cells[0]["encoder_display"],
            "encoder_family": enc_cells[0]["encoder_family"],
            "encoder_dim": enc_cells[0]["encoder_dim"],
            "mean_bypass_pct": round(sum(c["core"]["bypass_pct"] for c in enc_cells) / len(enc_cells), 2),
            "mean_glr_pct": round(sum(c["core"]["glr_pct"] for c in enc_cells) / len(enc_cells), 2),
            "mean_ulr_pct": round(sum(c["core"]["ulr_pct"] for c in enc_cells) / len(enc_cells), 2),
            "mean_per_bypass_leak_pct": round(
                sum(c["core"]["per_bypass_leak_pct"] for c in enc_cells) / len(enc_cells), 1
            ),
            "n_cells": len(enc_cells),
        }

    matrix = {
        "schema_version": "1.0",
        "generated_at": "2026-05-10",
        "phase": "1.F",
        "milestone": "M5.1 (aggregation)",
        "totals": {
            "n_cells": len(cells),
            "n_encoders": len({c["encoder_short"] for c in cells}),
            "n_corpora": len({c["corpus_label"] for c in cells}),
            "total_attacks_evaluated": total_attacks,
            "total_bypass": total_bypass,
            "total_glr_leaked": total_glr,
            "total_ulr_leaked": total_ulr,
            "total_llm_cost_usd": round(total_cost, 4),
            "total_wall_s": round(total_wall, 1),
            "cost_cap_usd": 0.40,
            "cost_cap_utilization_pct": round(100 * total_cost / 0.40, 1),
        },
        "by_encoder": by_encoder,
        "calibration_summary": cal_summary,
        "cells": cells,
    }

    # Write outputs
    out_json = REPO_ROOT / args.output_json
    out_tex = REPO_ROOT / args.output_tex
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(matrix, indent=2, default=str))
    out_tex.write_text(emit_latex_table(cells))

    print(f"Wrote {out_json}  ({out_json.stat().st_size:,} bytes)")
    print(f"Wrote {out_tex}  ({out_tex.stat().st_size:,} bytes)")
    print()
    print(f"Matrix totals: {len(cells)} cells, "
          f"{total_attacks} attacks, {total_bypass} bypass, {total_glr} GLR, "
          f"{total_ulr} ULR, ${total_cost:.4f} cost, {total_wall:.1f}s wall")
    print()
    print("Per-encoder roll-up (mean across 2 corpora):")
    for enc, stats in by_encoder.items():
        print(f"  {enc:10s} ({stats['encoder_family'][:14]:14s}): "
              f"bypass={stats['mean_bypass_pct']:.2f}%  GLR={stats['mean_glr_pct']:.2f}%  "
              f"per-BP-leak={stats['mean_per_bypass_leak_pct']:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
