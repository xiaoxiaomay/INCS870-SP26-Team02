#!/usr/bin/env python3
"""
eval/generate_latex_tables.py

Reads all JSON result files and outputs LaTeX table snippets for the paper.

Inputs:  eval/results/*.json
Outputs: eval/latex_tables/table_*.tex

Usage:
    python eval/generate_latex_tables.py --results-dir eval/results/ --output eval/latex_tables/
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def generate_ablation_table(data: dict, output_dir: str, full_pipeline: dict = None):
    """Generate ablation study table with pre-gate bypass rate and true leakage rate."""
    configs = data.get("configs", [])
    if not configs:
        return

    # Get true ASR from full pipeline eval if available
    true_asr = None
    if full_pipeline:
        true_asr = full_pipeline.get("true_asr")

    lines = [
        r"\begin{table*}[htbp]",
        r"\centering",
        r"\caption{Ablation Study: Per-Gate Contribution to Attack Prevention}",
        r"\label{tab:ablation}",
        r"\begin{tabular}{lcccccl}",
        r"\toprule",
        r"\textbf{Config} & \textbf{Pre-gate Bypass (\%)} & \textbf{True Leakage (\%)} & \textbf{FPR (\%)} & \textbf{Blocked} & \textbf{Latency (ms)} & \textbf{Gates Disabled} \\",
        r"\midrule",
    ]

    for c in configs:
        cid = c["config_id"].replace("_", r"\_")
        bypass_pct = c["asr"] * 100
        fpr = c["fpr"] * 100
        blocked = f"{c['attack_blocked']}/{c['attack_total']}"
        latency = c["avg_latency_ms"]
        desc = c["description"][:40]

        # True leakage only known for B0 and B2_full
        if c["config_id"] == "B2_full" and true_asr is not None:
            true_leak = f"{true_asr * 100:.1f}"
        elif c["config_id"] == "B0":
            true_leak = "---"
        else:
            true_leak = "---"

        lines.append(
            f"  {cid} & {bypass_pct:.1f} & {true_leak} & {fpr:.1f} & {blocked} & {latency:.1f} & {desc} \\\\"
        )

    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])

    with open(os.path.join(output_dir, "table_ablation.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_statistical_table(data: dict, output_dir: str):
    """Generate statistical evaluation table."""
    if not data:
        return

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Statistical Evaluation: B0 vs B2 ($N=" + str(data.get("n_runs", 5)) + r"$ runs)}",
        r"\label{tab:statistical}",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"\textbf{Metric} & \textbf{Mean} & \textbf{Std} & \textbf{95\% CI} \\",
        r"\midrule",
    ]

    for metric, key_prefix in [("ASR", "b2_asr"), ("FPR", "b2_fpr"), ("TPR", "b2_tpr")]:
        mean = data.get(f"{key_prefix}_mean", 0) * 100
        std = data.get(f"{key_prefix}_std", 0) * 100
        ci = data.get(f"{key_prefix}_95ci", [0, 0])
        ci_str = f"[{ci[0]*100:.1f}, {ci[1]*100:.1f}]"
        lines.append(f"  {metric} (\\%) & {mean:.1f} & {std:.1f} & {ci_str} \\\\")

    mcnemar = data.get("mcnemar", {})
    if isinstance(mcnemar, dict) and "p_value" in mcnemar:
        lines.append(r"\midrule")
        p = mcnemar["p_value"]
        sig = "Yes" if mcnemar.get("significant_at_005") else "No"
        lines.append(f"  McNemar $p$-value & \\multicolumn{{3}}{{c}}{{${p:.4f}$ (significant: {sig})}} \\\\")

    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])

    with open(os.path.join(output_dir, "table_statistical.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_latency_table(data: dict, output_dir: str):
    """Generate latency benchmark table."""
    per_gate = data.get("per_gate", {})
    if not per_gate:
        return

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Per-Gate Latency Benchmark (milliseconds)}",
        r"\label{tab:latency}",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"\textbf{Component} & \textbf{Min} & \textbf{P50} & \textbf{P95} & \textbf{P99} & \textbf{Max} \\",
        r"\midrule",
    ]

    name_map = {
        "gate_0_decode": "Gate 0 Decode",
        "gate_0a_regex": "Gate 0a (Regex)",
        "gate_0b_hardblock": "Gate 0b (Hard-block)",
        "gate_0_merged": "Gate 0 (Merged)",
        "gate_1_embedding": "Gate 1 (Embedding)",
        "embedding_encode_only": "Embedding Only",
        "faiss_search_only": "FAISS Search",
        "leakage_scan": "Leakage Scan",
        "end_to_end_gates": "End-to-End (Gates)",
    }

    for gate_key, stats in per_gate.items():
        name = name_map.get(gate_key, gate_key)
        lines.append(
            f"  {name} & {stats['min']:.2f} & {stats['p50']:.2f} & "
            f"{stats['p95']:.2f} & {stats['p99']:.2f} & {stats['max']:.2f} \\\\"
        )

    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])

    with open(os.path.join(output_dir, "table_latency.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_crossdomain_table(medical_data: dict, ablation_data: dict, output_dir: str):
    """Generate cross-domain comparison table (finance vs medical)."""
    if not medical_data:
        return

    # Get B2_full from ablation for finance comparison
    finance_asr = None
    finance_fpr = None
    if ablation_data:
        for c in ablation_data.get("configs", []):
            if c["config_id"] == "B2_full":
                finance_asr = c["asr"]
                finance_fpr = c["fpr"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Cross-Domain Generalization: Finance vs Medical}",
        r"\label{tab:crossdomain}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"\textbf{Domain} & \textbf{ASR (\%)} & \textbf{FPR (\%)} & \textbf{TPR (\%)} & \textbf{Code Changes} \\",
        r"\midrule",
    ]

    if finance_asr is not None:
        lines.append(
            f"  Finance & {finance_asr*100:.1f} & {finance_fpr*100:.1f} & {(1-finance_asr)*100:.1f} & Baseline \\\\"
        )

    med_asr = medical_data.get("asr", 0)
    med_fpr = medical_data.get("fpr", 0)
    med_tpr = medical_data.get("tpr", 0)
    lines.append(
        f"  Medical & {med_asr*100:.1f} & {med_fpr*100:.1f} & {med_tpr*100:.1f} & Config only \\\\"
    )

    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])

    with open(os.path.join(output_dir, "table_crossdomain.tex"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=str, default="eval/results/")
    ap.add_argument("--output", type=str, default="eval/latex_tables/")
    args = ap.parse_args()

    results_dir = str(REPO_ROOT / args.results_dir)
    output_dir = str(REPO_ROOT / args.output)
    os.makedirs(output_dir, exist_ok=True)

    # Load all result files (try multiple names)
    ablation = load_json(os.path.join(results_dir, "ablation_results.json"))
    if not ablation:
        ablation = load_json(os.path.join(results_dir, "ablation.json"))

    statistical = load_json(os.path.join(results_dir, "statistical_eval.json"))
    if not statistical:
        statistical = load_json(os.path.join(results_dir, "core_eval.json"))

    latency = load_json(os.path.join(results_dir, "latency_benchmark.json"))
    if not latency:
        latency = load_json(os.path.join(results_dir, "latency.json"))

    medical = load_json(os.path.join(results_dir, "medical_eval_results.json"))
    if not medical:
        medical = load_json(os.path.join(results_dir, "medical.json"))

    full_pipeline = load_json(os.path.join(results_dir, "full_pipeline_eval.json"))

    generated = []

    if ablation:
        generate_ablation_table(ablation, output_dir, full_pipeline=full_pipeline)
        generated.append("table_ablation.tex")

    if statistical:
        generate_statistical_table(statistical, output_dir)
        generated.append("table_statistical.tex")

    if latency:
        generate_latency_table(latency, output_dir)
        generated.append("table_latency.tex")

    if medical or ablation:
        generate_crossdomain_table(medical, ablation, output_dir)
        generated.append("table_crossdomain.tex")

    print(f"Generated {len(generated)} LaTeX tables in {output_dir}:")
    for t in generated:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
