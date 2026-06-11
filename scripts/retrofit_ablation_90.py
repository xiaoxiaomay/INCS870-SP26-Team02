#!/usr/bin/env python3
"""Retrofit follow-up: per-gate ablation on the 90-entry secret index.

Re-runs the ablation harness from scripts/retrofit_results.py against
data/index/secrets_v2.faiss (90-entry corpus) instead of the 60-entry index.
Reports pre_gate_bypass_rate, fpr, and p50_latency_ms for each config against
the 271-prompt attack corpus + 100 benign queries.

Configs:
  B2_full           — all gates on, deployed dual-tau (confirms expected 50.18%)
  B2_no_G0a         — G0b + G1 + LS only
  B2_no_G0b         — G0a + G1 + LS only
  B2_no_G1          — pre-gates without embedding precheck (confirms 75.65%)
  B2_single_tau_062 — Gate 1 single threshold tau=0.62

B0 is skipped (trivially 100% bypass under no gates).

Deterministic: no LLM is invoked.

Writes to eval/results/retrofit_2026_06_04/ablation_90.json. Touches nothing
in production: the 90-corpus FAISS file (data/index/secrets_v2.faiss) is opened
read-only via load_faiss_index().
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

os.environ["USE_POSTGRES"] = "false"

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(REPO_ROOT / ".env")

import yaml  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402
from core.config_loader import get_pinned_revision  # noqa: E402
from scripts.leakage_scan import load_faiss_index  # noqa: E402

# Reuse the deterministic gate-walker from the retrofit harness — no duplication.
from scripts.retrofit_results import (  # noqa: E402
    read_jsonl, load_config, run_corpus_through_gates,
    ATTACK_271, BENIGN_100, MINILM_NAME,
)

OUT_DIR = REPO_ROOT / "eval" / "results" / "retrofit_2026_06_04"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "ablation_90.json"

SECRETS_90 = REPO_ROOT / "data" / "index" / "secrets_v2.faiss"
SECRETS_90_META = REPO_ROOT / "data" / "index" / "secrets_v2_meta.pkl"
CONFIG_PATH = REPO_ROOT / "config.yaml"

CONFIGS = [
    {"id": "B2_full",           "desc": "Full SentinelFlow — all gates, dual-tau (90-corpus)", "g0a": True,  "g0b": True,  "g1": True,  "g1_mode": "dual"},
    {"id": "B2_no_G0a",         "desc": "Remove Gate 0a (intent regex) — G0b+G1+LS only",      "g0a": False, "g0b": True,  "g1": True,  "g1_mode": "dual"},
    {"id": "B2_no_G0b",         "desc": "Remove Gate 0b (hard-block verb*obj) — G0a+G1+LS",    "g0a": True,  "g0b": False, "g1": True,  "g1_mode": "dual"},
    {"id": "B2_no_G1",          "desc": "Remove Gate 1 (embedding precheck)",                   "g0a": True,  "g0b": True,  "g1": False, "g1_mode": "off"},
    {"id": "B2_single_tau_062", "desc": "Gate 1 single threshold tau=0.62 (all gates)",         "g0a": True,  "g0b": True,  "g1": True,  "g1_mode": "single_062"},
]


def now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main():
    print("=== Retrofit follow-up: per-gate ablation on 90-entry index ===")
    print(f"output: {OUT_PATH.relative_to(REPO_ROOT)}")

    # Disclosure: what config.yaml actually points at
    cfg = load_config()
    config_secret_path = cfg.get("paths", {}).get("secret_index")
    print(f"config.yaml:paths.secret_index = {config_secret_path}")
    print(f"this script overrides to:        {SECRETS_90.relative_to(REPO_ROOT)} (per request)")
    config_vs_request_mismatch = (config_secret_path != str(SECRETS_90.relative_to(REPO_ROOT)))
    if config_vs_request_mismatch:
        print("DISCLOSURE: the committed config.yaml points at the 60-entry index;")
        print("            this run uses the 90-entry index per the explicit request.")

    print(f"loading MiniLM (pinned) ...")
    rev = get_pinned_revision(MINILM_NAME)
    embed_model = SentenceTransformer(MINILM_NAME, revision=rev)

    print(f"loading 90-corpus secret index (read-only) ...")
    sec_idx, sec_meta = load_faiss_index(str(SECRETS_90), str(SECRETS_90_META))

    print(f"loading corpora ...")
    attacks = read_jsonl(ATTACK_271)
    benigns = read_jsonl(BENIGN_100)
    print(f"  attacks: {len(attacks)}, benigns: {len(benigns)}")

    rows = []
    for c in CONFIGS:
        print(f"\nconfig {c['id']}: {c['desc']}")
        atk_agg = run_corpus_through_gates(
            rows=attacks, embed_model=embed_model,
            secret_index=sec_idx, secret_meta=sec_meta, cfg=cfg,
            enable_g0a=c["g0a"], enable_g0b=c["g0b"],
            enable_g1=c["g1"], g1_mode=c["g1_mode"],
        )
        ben_agg = run_corpus_through_gates(
            rows=benigns, embed_model=embed_model,
            secret_index=sec_idx, secret_meta=sec_meta, cfg=cfg,
            enable_g0a=c["g0a"], enable_g0b=c["g0b"],
            enable_g1=c["g1"], g1_mode=c["g1_mode"],
        )
        rows.append({
            "config_id": c["id"],
            "description": c["desc"],
            "gates_active": {
                "gate_0a": c["g0a"], "gate_0b": c["g0b"],
                "gate_1": c["g1"], "g1_mode": c["g1_mode"],
            },
            "attack_total": atk_agg["n"],
            "attack_blocked_at_pregate": atk_agg["n_blocked"],
            "pre_gate_bypass_rate": atk_agg["pre_gate_bypass_rate"],
            "attack_blocked_at_counts": atk_agg["blocked_at_counts"],
            "benign_total": ben_agg["n"],
            "benign_blocked": ben_agg["n_blocked"],
            "fpr": ben_agg["block_rate"],
            "p50_latency_ms_attacks": atk_agg["p50_latency_ms"],
            "p50_latency_ms_benign": ben_agg["p50_latency_ms"],
            "p50_latency_ms_combined": round(median(
                [r["lat_total_ms"] for r in atk_agg["per_row"]] +
                [r["lat_total_ms"] for r in ben_agg["per_row"]]
            ), 4),
        })
        bp = (atk_agg["pre_gate_bypass_rate"] or 0) * 100
        fpr = (ben_agg["block_rate"] or 0) * 100
        print(f"  pre-gate bypass: {atk_agg['n_bypass']}/{atk_agg['n']} = {bp:.2f}%")
        print(f"  FPR:             {ben_agg['n_blocked']}/{ben_agg['n']} = {fpr:.2f}%")
        print(f"  P50 latency:     {rows[-1]['p50_latency_ms_combined']:.4f} ms")
        print(f"  blocked@:        {atk_agg['blocked_at_counts']}")

    # Deltas vs B2_full (pre-gate bypass)
    full = next(r for r in rows if r["config_id"] == "B2_full")
    full_bp = full["pre_gate_bypass_rate"] or 0.0
    deltas_bp = {r["config_id"]: round(((r["pre_gate_bypass_rate"] or 0) - full_bp) * 100, 2) for r in rows}

    out = {
        "task": "ablation_pre_gate_90_corpus",
        "generated_at": now_z(),
        "attack_corpus": str(ATTACK_271.relative_to(REPO_ROOT)),
        "benign_corpus": str(BENIGN_100.relative_to(REPO_ROOT)),
        "secret_index_used": str(SECRETS_90.relative_to(REPO_ROOT)),
        "config_secret_index_committed": config_secret_path,
        "config_vs_run_mismatch": config_vs_request_mismatch,
        "note": (
            "Per-gate ablation re-run on the 90-entry secret index "
            "(data/index/secrets_v2.faiss) at the deployed dual-threshold config. "
            "B0 omitted (trivially 100% pre-gate bypass under no gates). "
            "DISCLOSURE: the committed config.yaml points paths.secret_index to "
            "data/index/secrets.faiss (60-entry); this run overrides to the "
            "90-entry index per the explicit request, in order to produce the "
            "canonical 90-corpus ablation numbers."
        ),
        "configs": rows,
        "deltas_pre_gate_bypass_vs_B2_full_pp": deltas_bp,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"\n[done] wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
