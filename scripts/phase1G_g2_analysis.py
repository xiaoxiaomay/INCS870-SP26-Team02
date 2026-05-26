#!/usr/bin/env python3
"""Phase 1.G G2 statistical analysis.

Reads per-sample summaries from `eval/results/phase1_F/<cell>/summary.json`
(sample 1) and `eval/results/phase1_G/<cell>/sample_<n>/summary.json`
(samples 2-5) and produces three outputs:

  1. matrix_n5.json         — machine-readable aggregates + tests
  2. paper_table_v_b_4.md   — paper-ready markdown table for v10 §V.B.4
  3. g2_audit_report.md     — human-readable audit report

Statistical content per PHASE_1G_PLAN.md §3 (V2.5):
  - Per-cell mean ± Student's t 95% CI (n=5, df=4, t_{0.025,4}=2.776)
  - Within-encoder paired t-tests (60 vs 90 corpus), 4 primary tests
    on glr_rate adjusted with Holm-Bonferroni step-down (FWER ≤ 0.05)
  - Cross-encoder ordering verification (F2 prediction)
  - S15 predictive claim verification (ULR fires concentrated on bge-large)

Run with `--partial` against in-progress G1 data; without `--partial`
all 8 cells must be at n=5 (will raise otherwise).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as scipy_stats


CELLS = [
    "minilm_60entry",
    "minilm_90entry",
    "mpnet_60entry",
    "mpnet_90entry",
    "bge_large_60entry",
    "bge_large_90entry",
    "finlang_60entry",
    "finlang_90entry",
]

ENCODERS = ["minilm", "mpnet", "bge_large", "finlang"]
RATE_METRICS = ["bypass_rate", "glr_rate", "per_bp_leak_rate", "ulr_rate"]
COUNT_METRICS = ["n_glr_leaked", "n_ulr_leaked"]
PRIMARY_PAIRED_METRIC = "glr_rate"
SECONDARY_PAIRED_METRICS = ["bypass_rate", "per_bp_leak_rate"]


def aggregate_metric(values: list[float], alpha: float = 0.05) -> dict[str, Any]:
    """Mean, Bessel-corrected std, and Student's t two-sided CI."""
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n == 0:
        return {
            "values": [],
            "mean": None,
            "std": None,
            "ci_low": None,
            "ci_high": None,
            "ci_half_width": None,
        }
    mean = float(arr.mean())
    if n < 2:
        return {
            "values": arr.tolist(),
            "mean": mean,
            "std": None,
            "ci_low": None,
            "ci_high": None,
            "ci_half_width": None,
        }
    std = float(arr.std(ddof=1))
    t_crit = float(scipy_stats.t.ppf(1 - alpha / 2, df=n - 1))
    half_width = t_crit * std / np.sqrt(n)
    return {
        "values": arr.tolist(),
        "mean": mean,
        "std": std,
        "ci_low": float(mean - half_width),
        "ci_high": float(mean + half_width),
        "ci_half_width": float(half_width),
    }


def paired_t_test(
    values_a: list[float], values_b: list[float], label: str = ""
) -> dict[str, Any]:
    """Paired t-test on equal-length sequences (matched by sample index)."""
    if len(values_a) != len(values_b):
        raise ValueError(
            f"Paired test requires equal-length arrays: "
            f"{label} ({len(values_a)} vs {len(values_b)})"
        )
    arr_a = np.array(values_a, dtype=float)
    arr_b = np.array(values_b, dtype=float)
    diffs = arr_a - arr_b
    std_diff = float(diffs.std(ddof=1)) if len(diffs) > 1 else None
    degenerate = False
    if np.allclose(diffs, 0.0):
        # All paired differences exactly zero: cells are bit-identical.
        t_stat, p_val = 0.0, 1.0
        degenerate = True
    elif std_diff is not None and std_diff < 1e-12:
        # Differences identical and non-zero (e.g., deterministic bypass-rate
        # gap). Standard t-statistic is ±inf, p-value is degenerate; report
        # the mean difference as a deterministic delta and flag it.
        t_stat = float("inf") if diffs.mean() > 0 else float("-inf")
        p_val = 0.0
        degenerate = True
    else:
        t_stat_raw, p_val_raw = scipy_stats.ttest_rel(arr_a, arr_b)
        t_stat = float(t_stat_raw)
        p_val = float(p_val_raw)
    return {
        "samples_a": arr_a.tolist(),
        "samples_b": arr_b.tolist(),
        "differences": diffs.tolist(),
        "mean_diff": float(diffs.mean()),
        "std_diff": std_diff,
        "t_statistic": t_stat,
        "p_value_unadjusted": p_val,
        "degenerate_zero_variance": degenerate,
    }


def holm_bonferroni_adjust(
    tests: list[dict[str, Any]], alpha: float = 0.05
) -> list[dict[str, Any]]:
    """Augment tests with holm_rank, holm_threshold, significant_at_alpha_0_05.

    Step-down: sort p ascending; threshold for rank i is alpha/(k-i+1);
    reject p_(i) iff p_(j) rejected for all j ≤ i. As soon as a test
    fails its threshold, all subsequent ranks fail.
    """
    if not tests:
        return tests
    k = len(tests)
    order = sorted(range(k), key=lambda i: tests[i]["p_value_unadjusted"])
    any_failed = False
    for rank, orig_idx in enumerate(order, start=1):
        t = tests[orig_idx]
        threshold = alpha / (k - rank + 1)
        t["holm_rank"] = rank
        t["holm_threshold"] = float(threshold)
        if any_failed:
            t["significant_at_alpha_0_05"] = False
        else:
            if t["p_value_unadjusted"] <= threshold:
                t["significant_at_alpha_0_05"] = True
            else:
                t["significant_at_alpha_0_05"] = False
                any_failed = True
    return tests


def cross_encoder_ordering(
    per_cell: dict[str, dict[str, Any]],
    corpus_size: str,
    metric_key: str,
) -> dict[str, Any]:
    """Per-sample ranking of the 4 encoders for one corpus size.

    F2 prediction (encoder × Per-BP-Leak%, ascending): minilm ≤ finlang
    ≈ mpnet < bge_large. The encode test below verifies the strong-form
    claim that minilm has rank 1 and bge_large has rank 4 in each sample.
    """
    rankings: dict[str, Any] = {}
    # Maximum n across the four encoder cells (so we don't index past the
    # shortest series). All cells should match in partial-run modes too.
    max_n = 0
    for enc in ENCODERS:
        cell = f"{enc}_{corpus_size}entry"
        vals = per_cell.get(cell, {}).get(metric_key, {}).get("values", [])
        max_n = max(max_n, len(vals))

    prediction_per_sample: list[bool] = []
    exception_samples: list[int] = []
    for sample_idx in range(max_n):
        values: dict[str, float] = {}
        for enc in ENCODERS:
            cell = f"{enc}_{corpus_size}entry"
            vals = per_cell.get(cell, {}).get(metric_key, {}).get("values", [])
            if sample_idx < len(vals):
                values[enc] = float(vals[sample_idx])
        if len(values) < 4:
            rankings[f"sample_{sample_idx + 1}"] = {
                "values": values,
                "rank": None,
                "complete": False,
            }
            continue
        sorted_encs = sorted(values.keys(), key=lambda e: values[e])
        rank = {enc: i + 1 for i, enc in enumerate(sorted_encs)}
        rankings[f"sample_{sample_idx + 1}"] = {
            "values": values,
            "rank": rank,
            "complete": True,
        }
        f2_holds = rank.get("minilm") == 1 and rank.get("bge_large") == 4
        prediction_per_sample.append(f2_holds)
        if not f2_holds:
            exception_samples.append(sample_idx + 1)

    return {
        "corpus_size": corpus_size,
        "metric": metric_key,
        "prediction_F2": "minilm <= finlang ~= mpnet < bge_large",
        "per_sample_rankings": rankings,
        "prediction_holds_per_sample": prediction_per_sample,
        "prediction_holds_aggregate": (
            all(prediction_per_sample) if prediction_per_sample else None
        ),
        "exception_samples": exception_samples,
    }


def verify_s15_claim(per_cell: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Sum n_ulr_leaked per cell; classify bge-large vs non-bge-large."""
    ulr_per_cell: dict[str, int] = {}
    for cell, data in per_cell.items():
        vals = data.get("n_ulr_leaked", {}).get("values", [])
        ulr_per_cell[cell] = int(sum(vals))
    bge_total = sum(v for c, v in ulr_per_cell.items() if c.startswith("bge_large_"))
    non_bge_total = sum(
        v for c, v in ulr_per_cell.items() if not c.startswith("bge_large_")
    )
    claim_holds = (non_bge_total == 0) or (bge_total > non_bge_total)
    return {
        "prediction": "ULR fires concentrated on bge-large cells",
        "ulr_fires_per_cell": ulr_per_cell,
        "non_bge_large_ulr_total": int(non_bge_total),
        "bge_large_ulr_total": int(bge_total),
        "claim_holds": bool(claim_holds),
        "evidence": (
            f"bge-large total ULR fires: {bge_total}; "
            f"non-bge-large total: {non_bge_total}"
        ),
    }


def load_per_sample_data(
    data_root: Path, allow_partial: bool = False
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load summary.json for each cell × 5 samples.

    Sample 1 from `phase1_F/<cell>/summary.json`; samples 2-5 from
    `phase1_G/<cell>/sample_<n>/summary.json`.
    """
    per_cell: dict[str, dict[str, Any]] = {}
    cells_status: dict[str, dict[str, Any]] = {}

    for cell in CELLS:
        samples: list[dict[str, Any]] = []
        missing: list[str] = []

        f1_path = data_root / "phase1_F" / cell / "summary.json"
        if f1_path.exists():
            with f1_path.open() as fp:
                samples.append(json.load(fp))
        else:
            missing.append(str(f1_path.relative_to(data_root)))

        for s_idx in range(2, 6):
            g_path = data_root / "phase1_G" / cell / f"sample_{s_idx}" / "summary.json"
            if g_path.exists():
                with g_path.open() as fp:
                    samples.append(json.load(fp))
            else:
                missing.append(str(g_path.relative_to(data_root)))

        cells_status[cell] = {
            "n": len(samples),
            "complete": len(samples) == 5,
            "missing_files": missing,
        }

        if not cells_status[cell]["complete"] and not allow_partial:
            raise RuntimeError(
                f"Cell {cell} has only {len(samples)} samples (need 5). "
                f"Missing: {missing}. Use --partial to run on incomplete data."
            )

        per_cell[cell] = {
            "bypass_rate": {"values": [s["bypass_rate"] for s in samples]},
            "glr_rate": {"values": [s["glr_rate"] for s in samples]},
            "ulr_rate": {"values": [s["ulr_rate"] for s in samples]},
            "n_glr_leaked": {"values": [int(s["n_glr_leaked"]) for s in samples]},
            "n_ulr_leaked": {"values": [int(s["n_ulr_leaked"]) for s in samples]},
            "n_bypass": {"values": [int(s["n_bypass"]) for s in samples]},
            "n_attacks": {"values": [int(s["n_attacks"]) for s in samples]},
            "per_bp_leak_rate": {
                "values": [
                    (s["n_glr_leaked"] / s["n_bypass"]) if s["n_bypass"] > 0 else 0.0
                    for s in samples
                ]
            },
        }

    return per_cell, cells_status


def format_rate_ci(agg: dict[str, Any], precision: int = 4) -> str:
    if agg.get("mean") is None:
        return "—"
    mean = agg["mean"]
    hw = agg.get("ci_half_width")
    if hw is None:
        return f"{mean:.{precision}f} (n<2)"
    return f"{mean:.{precision}f} ± {hw:.{precision}f}"


def write_paper_table(output: dict[str, Any], path: Path) -> None:
    """Write paper-ready markdown table for v10 §V.B.4."""
    meta = output["metadata"]
    per_cell = output["per_cell_aggregates"]
    primary = output["within_encoder_paired_tests"]["primary_tests_glr"]
    secondary = output["within_encoder_paired_tests"]["secondary_tests"]
    cross_60 = output["cross_encoder_ordering"]["60_corpus"]
    cross_90 = output["cross_encoder_ordering"]["90_corpus"]
    s15 = output["S15_predictive_claim"]

    lines: list[str] = []
    lines.append("# Phase 1.G G2 Statistical Aggregates (n=5 per cell)")
    lines.append("")
    lines.append(
        f"Generated: {meta['generated_at']} | Alpha: {meta['alpha']} | "
        f"Cells complete: {meta['n_cells_complete']}/8 | "
        f"Multiplicity: {meta['multiplicity_correction']}"
    )
    lines.append("")

    # §V.B.4.1
    lines.append("## §V.B.4.1 — Per-cell aggregate metrics")
    lines.append("")
    lines.append(
        "| # | Cell | $\\bar{\\text{Bypass}}$ ± CI | $\\bar{\\text{GLR}}$ ± CI |"
        " $\\bar{\\text{Per-BP-Leak}}$ ± CI | $\\bar{\\text{ULR}}$ ± CI | n |"
    )
    lines.append(
        "| --- | --- | --- | --- | --- | --- | --- |"
    )
    pretty_cell = {
        "minilm_60entry": "MiniLM × 60",
        "minilm_90entry": "MiniLM × 90",
        "mpnet_60entry": "mpnet × 60",
        "mpnet_90entry": "mpnet × 90",
        "bge_large_60entry": "bge-large × 60",
        "bge_large_90entry": "bge-large × 90",
        "finlang_60entry": "FinLang × 60",
        "finlang_90entry": "FinLang × 90",
    }
    for i, cell in enumerate(CELLS, start=1):
        n = meta["cells_status"][cell]["n"]
        bp = format_rate_ci(per_cell[cell]["bypass_rate"])
        glr = format_rate_ci(per_cell[cell]["glr_rate"])
        pbl = format_rate_ci(per_cell[cell]["per_bp_leak_rate"])
        ulr = format_rate_ci(per_cell[cell]["ulr_rate"])
        marker = "" if meta["cells_status"][cell]["complete"] else " *"
        lines.append(
            f"| {i} | {pretty_cell[cell]}{marker} | {bp} | {glr} | {pbl} | {ulr} | {n} |"
        )
    if any(not s["complete"] for s in meta["cells_status"].values()):
        lines.append("")
        lines.append("\\* = partial cell (n < 5); aggregates reported with available samples.")
    lines.append("")

    # §V.B.4.2
    lines.append("## §V.B.4.2 — Within-encoder corpus delta paired t-tests")
    lines.append("")
    lines.append("**Primary tests** (4 × GLR-rate, Holm-Bonferroni step-down adjusted):")
    lines.append("")
    lines.append(
        "| Test | Mean delta (60 − 90) | t-stat | p (unadj.) | Holm rank |"
        " Holm threshold | Significant @ α=0.05 |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for t in primary:
        enc = t["encoder"]
        mean_d = t["mean_diff"]
        t_stat = t["t_statistic"]
        p = t["p_value_unadjusted"]
        rank = t.get("holm_rank", "—")
        thr = t.get("holm_threshold")
        sig = "Yes" if t.get("significant_at_alpha_0_05") else "No"
        if t.get("degenerate_zero_variance"):
            sig = "DEGENERATE (zero-variance diffs)"
        thr_s = f"{thr:.4f}" if thr is not None else "—"
        t_s = "±inf" if not np.isfinite(t_stat) else f"{t_stat:.3f}"
        lines.append(
            f"| {enc} × 60 vs × 90 (GLR) | {mean_d:+.4f} | {t_s} | "
            f"{p:.4f} | {rank} | {thr_s} | {sig} |"
        )
    if not primary:
        lines.append("| (no complete encoder pairs available) | — | — | — | — | — | — |")
    lines.append("")
    if secondary:
        lines.append(
            "**Secondary tests** (Bypass + Per-BP-Leak; descriptive only, "
            "unadjusted p-values reported):"
        )
        lines.append("")
        lines.append(
            "| Test | Metric | Mean delta | t-stat | p (unadj.) |"
        )
        lines.append("| --- | --- | --- | --- | --- |")
        for t in secondary:
            enc = t["encoder"]
            metric = t["metric"]
            t_stat = t["t_statistic"]
            t_s = "±inf*" if not np.isfinite(t_stat) else f"{t_stat:.3f}"
            note = "  (deterministic gap; t/p degenerate)" if t.get("degenerate_zero_variance") else ""
            lines.append(
                f"| {enc} × 60 vs × 90 | {metric} | {t['mean_diff']:+.4f} | "
                f"{t_s} | {t['p_value_unadjusted']:.4f} |{note}"
            )
        lines.append("")

    # §V.B.4.3
    lines.append("## §V.B.4.3 — Cross-encoder ordering robustness (F2 verification)")
    lines.append("")
    lines.append(
        "Prediction F2: per-sample encoder ranking by Per-BP-Leak% should satisfy "
        "minilm = rank 1 and bge_large = rank 4 (lowest leak to highest)."
    )
    lines.append("")
    for corpus, cross in [("60", cross_60), ("90", cross_90)]:
        lines.append(f"### Corpus size {corpus}")
        lines.append("")
        lines.append(
            "| Sample | minilm | FinLang | mpnet | bge-large | F2 holds? |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for s_key, s_data in cross["per_sample_rankings"].items():
            if not s_data.get("complete"):
                lines.append(f"| {s_key} | (incomplete) | | | | — |")
                continue
            rank = s_data["rank"]
            vals = s_data["values"]
            holds = (rank.get("minilm") == 1 and rank.get("bge_large") == 4)
            lines.append(
                f"| {s_key} | r{rank['minilm']} ({vals['minilm']:.4f}) | "
                f"r{rank['finlang']} ({vals['finlang']:.4f}) | "
                f"r{rank['mpnet']} ({vals['mpnet']:.4f}) | "
                f"r{rank['bge_large']} ({vals['bge_large']:.4f}) | "
                f"{'Yes' if holds else 'No'} |"
            )
        agg = cross.get("prediction_holds_aggregate")
        if agg is None:
            lines.append("")
            lines.append(f"**Aggregate verdict (corpus {corpus}): no complete samples available.**")
        else:
            lines.append("")
            lines.append(
                f"**Aggregate verdict (corpus {corpus}): F2 prediction holds in "
                f"{sum(cross['prediction_holds_per_sample'])} of "
                f"{len(cross['prediction_holds_per_sample'])} samples.**"
            )
            if cross["exception_samples"]:
                lines.append(
                    f"Exceptions: samples {cross['exception_samples']}"
                )
        lines.append("")

    # §V.B.4.4
    lines.append("## §V.B.4.4 — S15 predictive claim verification")
    lines.append("")
    lines.append(
        "Prediction (S15): ULR fires are concentrated on bge-large cells "
        "(measurement-stage over-sensitivity at $\\sigma_{\\text{hard}}=0.70$)."
    )
    lines.append("")
    lines.append("| Cell | ULR fires (sum across n) | n samples |")
    lines.append("| --- | --- | --- |")
    for cell in CELLS:
        ulr_sum = s15["ulr_fires_per_cell"].get(cell, 0)
        n = meta["cells_status"][cell]["n"]
        lines.append(f"| {pretty_cell[cell]} | {ulr_sum} | {n} |")
    lines.append("")
    lines.append(
        f"**bge-large total ULR fires:** {s15['bge_large_ulr_total']} | "
        f"**non-bge-large total:** {s15['non_bge_large_ulr_total']} | "
        f"**Claim holds:** {'Yes' if s15['claim_holds'] else 'No'}"
    )
    lines.append("")
    lines.append(f"Evidence: {s15['evidence']}")
    lines.append("")

    path.write_text("\n".join(lines))


def write_audit_report(output: dict[str, Any], path: Path) -> None:
    meta = output["metadata"]
    per_cell = output["per_cell_aggregates"]
    primary = output["within_encoder_paired_tests"]["primary_tests_glr"]
    s15 = output["S15_predictive_claim"]

    lines: list[str] = []
    lines.append("# Phase 1.G G2 Statistical Analysis — Audit Report")
    lines.append("")
    lines.append(f"**Generated:** {meta['generated_at']}")
    lines.append(f"**Data root:** {meta['data_root']}")
    lines.append(f"**Alpha:** {meta['alpha']}")
    lines.append(f"**Multiplicity correction:** {meta['multiplicity_correction']}")
    lines.append(
        f"**Cells complete (n=5):** {meta['n_cells_complete']} / 8 | "
        f"**Cells partial / missing:** {meta['n_cells_partial']} / 8"
    )
    lines.append("")

    # Section 1 — completeness
    lines.append("## §1. Data completeness")
    lines.append("")
    lines.append("| Cell | n samples | Complete? | Missing files |")
    lines.append("| --- | --- | --- | --- |")
    for cell in CELLS:
        st = meta["cells_status"][cell]
        miss = ", ".join(st["missing_files"]) if st["missing_files"] else "—"
        lines.append(
            f"| `{cell}` | {st['n']} | {'Yes' if st['complete'] else 'No'} | {miss} |"
        )
    lines.append("")

    # Section 2 — per-cell aggregates
    lines.append("## §2. Per-cell aggregates (summary)")
    lines.append("")
    for cell in CELLS:
        st = meta["cells_status"][cell]
        if st["n"] == 0:
            lines.append(f"### `{cell}` — NO DATA")
            lines.append("")
            continue
        bp = per_cell[cell]["bypass_rate"]
        glr = per_cell[cell]["glr_rate"]
        pbl = per_cell[cell]["per_bp_leak_rate"]
        ulr = per_cell[cell]["ulr_rate"]
        n_glr = per_cell[cell]["n_glr_leaked"]
        n_ulr = per_cell[cell]["n_ulr_leaked"]
        marker = "" if st["complete"] else " (PARTIAL)"
        lines.append(f"### `{cell}`{marker}  (n={st['n']})")
        lines.append("")
        lines.append(f"- Bypass: {format_rate_ci(bp)}  values={bp['values']}")
        lines.append(f"- GLR:    {format_rate_ci(glr)}  values={glr['values']}")
        lines.append(f"- Per-BP-Leak: {format_rate_ci(pbl)}  values=[{', '.join(f'{v:.4f}' for v in pbl['values'])}]")
        lines.append(f"- ULR:    {format_rate_ci(ulr)}  values={ulr['values']}")
        lines.append(f"- n_glr_leaked counts: {n_glr['values']} (sum={n_glr.get('sum')})")
        lines.append(f"- n_ulr_leaked counts: {n_ulr['values']} (sum={n_ulr.get('sum')})")
        lines.append("")

    # Section 3 — paired t-tests
    lines.append("## §3. Within-encoder paired t-tests")
    lines.append("")
    if not primary:
        lines.append(
            "No complete encoder × {60, 90} pairs available for primary GLR tests."
        )
    else:
        lines.append("Primary tests (GLR rate, Holm-Bonferroni step-down):")
        lines.append("")
        for t in primary:
            enc = t["encoder"]
            lines.append(
                f"- **{enc}** (60 vs 90 GLR): mean Δ = {t['mean_diff']:+.4f}, "
                f"t = {t['t_statistic']:.3f}, p = {t['p_value_unadjusted']:.4f}, "
                f"Holm rank {t['holm_rank']}, threshold {t['holm_threshold']:.4f} → "
                f"{'**SIGNIFICANT** at α=0.05' if t.get('significant_at_alpha_0_05') else 'not significant'}"
            )
    lines.append("")
    holm_rejects = sum(
        1 for t in primary if t.get("significant_at_alpha_0_05")
    )
    lines.append(
        f"**Summary:** {holm_rejects} of {len(primary)} primary tests reject H_0 "
        f"after Holm-Bonferroni adjustment at FWER ≤ {meta['alpha']}."
    )
    lines.append("")

    # Section 4 — cross-encoder ordering
    lines.append("## §4. Cross-encoder ordering (F2 verification)")
    lines.append("")
    for corpus_size, cross in [
        ("60", output["cross_encoder_ordering"]["60_corpus"]),
        ("90", output["cross_encoder_ordering"]["90_corpus"]),
    ]:
        agg = cross.get("prediction_holds_aggregate")
        held = sum(cross["prediction_holds_per_sample"])
        total = len(cross["prediction_holds_per_sample"])
        verdict = (
            f"F2 holds in {held}/{total} samples"
            if total
            else "no complete samples"
        )
        lines.append(f"- **Corpus {corpus_size}:** {verdict}")
        if cross["exception_samples"]:
            lines.append(f"  Exceptions: samples {cross['exception_samples']}")
    lines.append("")

    # Section 5 — S15
    lines.append("## §5. S15 predictive claim")
    lines.append("")
    lines.append(f"- Prediction: {s15['prediction']}")
    lines.append(f"- bge-large total ULR fires: **{s15['bge_large_ulr_total']}**")
    lines.append(f"- non-bge-large total ULR fires: **{s15['non_bge_large_ulr_total']}**")
    lines.append(
        f"- Claim holds: **{'YES' if s15['claim_holds'] else 'NO'}** "
        f"({s15['evidence']})"
    )
    lines.append("")
    lines.append("Per-cell ULR fires:")
    for cell, n_ulr in s15["ulr_fires_per_cell"].items():
        marker = "  ← bge-large" if cell.startswith("bge_large_") else ""
        lines.append(f"  - {cell}: {n_ulr}{marker}")
    lines.append("")

    # Section 6 — recommendations
    lines.append("## §6. Recommendations for §V.B paper draft updates")
    lines.append("")
    if meta["n_cells_complete"] < 8:
        lines.append(
            "- **DRY-RUN against G1 partial state.** Output reflects "
            f"{meta['n_cells_complete']}/8 cells at n=5. Numbers in this report are "
            "NOT yet production-ready for §V.B.4."
        )
        lines.append(
            "- Re-run without `--partial` once G1 completes all 32 samples; "
            "the resulting matrix_n5.json + paper_table_v_b_4.md will be the "
            "canonical §V.B.4 source."
        )
    else:
        lines.append(
            "- All 8 cells at n=5. Outputs are production-ready for §V.B.4 paper draft."
        )
        lines.append(
            "- Substitute numerical values in `paper_drafts/v10/v10_paper_section_V_B_phase1G_draft.md` "
            "§V.B.4 [TBD] markers with values from `paper_table_v_b_4.md`."
        )
    if s15["claim_holds"]:
        lines.append(
            "- S15 predictive claim verified empirically; update §V.B.5.1 status "
            "to reflect full-G1 evidence."
        )
    else:
        lines.append(
            "- **S15 predictive claim DID NOT hold under full G1 data.** Revisit "
            "§V.B.5.1 framing; the claim was based on G1 partial-run evidence."
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*End of audit report.*")

    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 1.G G2 statistical analysis: aggregates + paired t-tests "
        "+ cross-encoder ordering + S15 verification."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path("eval/results"),
        help="Root containing phase1_F/ and phase1_G/ directories.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("eval/results/phase1_G/g2_outputs"),
        help="Output directory for matrix_n5.json + markdown reports.",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.05, help="Overall significance level."
    )
    parser.add_argument(
        "--partial",
        action="store_true",
        help="Allow run against partial G1 data (cells with n<5 reported but not skipped).",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    data_root = args.data_root.resolve()
    output_dir = args.output_dir.resolve()

    print("=== Phase 1.G G2 Statistical Analysis ===")
    print(f"Data root:  {data_root}")
    print(f"Output dir: {output_dir}")
    print(f"Alpha:      {args.alpha}")
    print(f"Multiplicity: Holm-Bonferroni step-down (k=4)")
    print(f"Partial:    {args.partial}")
    print()

    print("Loading per-sample data ...")
    per_cell, cells_status = load_per_sample_data(
        data_root, allow_partial=args.partial
    )
    n_complete = sum(1 for s in cells_status.values() if s["complete"])
    n_partial = sum(1 for s in cells_status.values() if not s["complete"])
    print(f"  Cells: {n_complete} complete (n=5), {n_partial} partial / missing")
    if args.verbose:
        for cell, st in cells_status.items():
            print(f"    {cell}: n={st['n']} complete={st['complete']}")

    print("Computing per-cell aggregates ...")
    for cell in CELLS:
        for metric in RATE_METRICS:
            agg = aggregate_metric(per_cell[cell][metric]["values"], alpha=args.alpha)
            per_cell[cell][metric].update(agg)
        for count_metric in COUNT_METRICS:
            vals = per_cell[cell][count_metric]["values"]
            per_cell[cell][count_metric]["mean"] = (
                float(np.mean(vals)) if vals else None
            )
            per_cell[cell][count_metric]["std"] = (
                float(np.std(vals, ddof=1)) if len(vals) > 1 else None
            )
            per_cell[cell][count_metric]["sum"] = int(sum(vals))

    print("Running within-encoder paired t-tests ...")
    primary_tests: list[dict[str, Any]] = []
    secondary_tests: list[dict[str, Any]] = []
    for enc in ENCODERS:
        cell_60 = f"{enc}_60entry"
        cell_90 = f"{enc}_90entry"
        st_60 = cells_status[cell_60]
        st_90 = cells_status[cell_90]
        if not (st_60["complete"] and st_90["complete"]):
            if args.verbose:
                print(
                    f"  Skipping {enc}: n_60={st_60['n']} n_90={st_90['n']} "
                    f"(both must be 5)"
                )
            continue
        for metric in [PRIMARY_PAIRED_METRIC] + SECONDARY_PAIRED_METRICS:
            vals_60 = per_cell[cell_60][metric]["values"]
            vals_90 = per_cell[cell_90][metric]["values"]
            test = paired_t_test(
                vals_60, vals_90, label=f"{enc} × 60 vs × 90 ({metric})"
            )
            test["encoder"] = enc
            test["cell_a"] = cell_60
            test["cell_b"] = cell_90
            test["metric"] = metric
            if metric == PRIMARY_PAIRED_METRIC:
                primary_tests.append(test)
            else:
                secondary_tests.append(test)
    primary_tests = holm_bonferroni_adjust(primary_tests, alpha=args.alpha)
    for t in secondary_tests:
        t["holm_rank"] = None
        t["holm_threshold"] = None
        t["significant_at_alpha_0_05"] = (
            t["p_value_unadjusted"] <= args.alpha
        )
    print(
        f"  Primary tests: {len(primary_tests)} | "
        f"Secondary tests: {len(secondary_tests)}"
    )

    print("Computing cross-encoder ordering (F2 verification) ...")
    cross_60 = cross_encoder_ordering(per_cell, "60", "per_bp_leak_rate")
    cross_90 = cross_encoder_ordering(per_cell, "90", "per_bp_leak_rate")

    print("Verifying S15 predictive claim ...")
    s15 = verify_s15_claim(per_cell)
    print(f"  bge-large total ULR fires: {s15['bge_large_ulr_total']}")
    print(f"  non-bge-large total ULR fires: {s15['non_bge_large_ulr_total']}")
    print(f"  Claim holds: {s15['claim_holds']}")

    output = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "data_root": str(data_root),
            "alpha": args.alpha,
            "multiplicity_correction": "Holm-Bonferroni step-down (k=4)",
            "cells_status": cells_status,
            "n_cells_complete": n_complete,
            "n_cells_partial": n_partial,
            "n_cells_missing": 0,
        },
        "per_cell_aggregates": per_cell,
        "within_encoder_paired_tests": {
            "encoders": ENCODERS,
            "primary_tests_glr": primary_tests,
            "secondary_tests": secondary_tests,
        },
        "cross_encoder_ordering": {
            "60_corpus": cross_60,
            "90_corpus": cross_90,
        },
        "S15_predictive_claim": s15,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "matrix_n5.json"
    with json_path.open("w") as fp:
        json.dump(output, fp, indent=2)
    print(f"Wrote: {json_path}")

    md_path = output_dir / "paper_table_v_b_4.md"
    write_paper_table(output, md_path)
    print(f"Wrote: {md_path}")

    audit_path = output_dir / "g2_audit_report.md"
    write_audit_report(output, audit_path)
    print(f"Wrote: {audit_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
