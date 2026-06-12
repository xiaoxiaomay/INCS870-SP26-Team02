#!/usr/bin/env python3
"""
Phase 0.5 / 0.6 — offline cosine measurement on anchor/offset minimal pairs.

Phase 0.5 (bundle): measured the cosine distribution between 15 human-reviewed
"public anchor" / "proprietary offset (secret)" seed pairs.

Phase 0.6 (dilution diagnostic): Phase 0.5 found that bundle-form offset text
has a much wider anchor cosine distribution than expected (0.22-0.72). This run
adds 5 "atomic" variants (each mother offset compressed to a single-parameter
sentence) and measures the within-pair change in cosine when the offset is
compressed. Goal: characterize whether — and by how much — a dilution effect
(longer offset text depressing the similarity reading) exists. This is a probe-
behavior DIAGNOSTIC measurement, NOT a data-quality gate. No thresholding, no
pass/fail. Judgment is performed by Peter in chat.

Zero API cost: uses the local sentence-transformers encoder configured for the
pipeline (config.yaml -> embedding.model_name). cosine = dot product of
L2-normalized embeddings (normalize_embeddings=True).

Anchor pool / ranking note: cross-pair anchor_rank is computed against the 15
DISTINCT mother (bundle) anchors. Atomic variants copy their mother anchor text
verbatim, so including them in the anchor pool would create rank-1 ties; ranking
both bundle and atomic secrets against the single 15-anchor pool keeps the two
granularities directly comparable in the same space.
"""

import json
import os
import platform
import statistics
import sys
from datetime import date

import yaml
from sentence_transformers import SentenceTransformer
import sentence_transformers

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
CONFIG_PATH = os.path.join(REPO_ROOT, "config.yaml")
PAIRS_PATH = os.path.join(HERE, "phase0_pairs.jsonl")
# Phase 0.6 output dir (Phase 0.5 dir results_2026_06_11/ is left frozen).
RESULTS_DIR = os.path.join(HERE, "results_2026_06_11_p06")


def load_model_name():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["embedding"]["model_name"]


def load_pairs():
    rows = []
    with open(PAIRS_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                row = json.loads(line)
                # granularity defaults to "bundle" for the original 15 rows.
                row.setdefault("granularity", "bundle")
                rows.append(row)
    return rows


def mother_id(pair_id):
    """Map an atomic id (p0_01a) to its mother bundle id (p0_01)."""
    return pair_id[:-1] if pair_id.endswith("a") else pair_id


def pct(sorted_vals, q):
    """Linear-interpolation percentile (q in [0,1]) on an already-sorted list."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac


def describe(vals):
    if not vals:
        return {"n": 0}
    s = sorted(vals)
    return {
        "n": len(s),
        "mean": statistics.fmean(s),
        "median": statistics.median(s),
        "p25": pct(s, 0.25),
        "p75": pct(s, 0.75),
        "min": s[0],
        "max": s[-1],
    }


def fmt_stats(d):
    if d.get("n", 0) == 0:
        return "(empty group)"
    return (
        f"n={d['n']} | mean={d['mean']:.4f} | median={d['median']:.4f} | "
        f"p25={d['p25']:.4f} | p75={d['p75']:.4f} | "
        f"min={d['min']:.4f} | max={d['max']:.4f}"
    )


def main():
    model_name = load_model_name()
    pairs = load_pairs()

    print(f"[phase0.6] model: {model_name}")
    print(f"[phase0.6] sentence-transformers: {sentence_transformers.__version__}")
    print(f"[phase0.6] pairs: {len(pairs)}")

    model = SentenceTransformer(model_name)

    # ----- anchor pool = the 15 distinct mother (bundle) anchors -----
    bundle_rows = [p for p in pairs if p["granularity"] == "bundle"]
    pool_ids = [p["id"] for p in bundle_rows]
    pool_index = {pid: i for i, pid in enumerate(pool_ids)}
    pool_anchor_texts = [p["anchor_text"] for p in bundle_rows]

    anchor_emb = model.encode(
        pool_anchor_texts, normalize_embeddings=True, convert_to_numpy=True
    )
    secret_emb = model.encode(
        [p["secret_text"] for p in pairs], normalize_embeddings=True, convert_to_numpy=True
    )

    # cosine = dot product (vectors are L2-normalized)
    sim_matrix = secret_emb @ anchor_emb.T  # rows = secret (20), cols = anchor pool (15)

    records = []
    for i, p in enumerate(pairs):
        own_anchor = mother_id(p["id"])
        own_col = pool_index[own_anchor]
        row = sim_matrix[i]
        own_cos = float(row[own_col])
        rank = int((row > own_cos).sum()) + 1
        nearest_idx = int(row.argmax())
        records.append({
            "id": p["id"],
            "domain": p["domain"],
            "offset_type": p["offset_type"],
            "subset": p["subset"],
            "granularity": p["granularity"],
            "mother_id": own_anchor,
            "cosine": own_cos,
            "anchor_rank": rank,
            "nearest_anchor_id": pool_ids[nearest_idx],
            "nearest_anchor_cosine": float(row[nearest_idx]),
        })

    rec_by_id = {r["id"]: r for r in records}

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # ----- results.json -----
    results_json = os.path.join(RESULTS_DIR, "results.json")
    with open(results_json, "w") as f:
        json.dump(
            {
                "model_name": model_name,
                "sentence_transformers_version": sentence_transformers.__version__,
                "n_pairs": len(pairs),
                "anchor_pool": "15 distinct mother (bundle) anchors",
                "pairs": [
                    {k: r[k] for k in (
                        "id", "domain", "offset_type", "subset", "granularity",
                        "mother_id", "cosine", "anchor_rank",
                        "nearest_anchor_id", "nearest_anchor_cosine",
                    )}
                    for r in records
                ],
            },
            f,
            indent=2,
        )

    # ----- group splits (all 20 rows) -----
    all_cos = [r["cosine"] for r in records]
    type_a = [r["cosine"] for r in records if r["offset_type"] == "A"]
    type_b = [r["cosine"] for r in records if r["offset_type"] == "B"]
    bundle = [r["cosine"] for r in records if r["granularity"] == "bundle"]
    atomic = [r["cosine"] for r in records if r["granularity"] == "atomic"]

    overall = describe(all_cos)

    # ----- atomic vs bundle paired comparison (5 groups) -----
    atomic_ids = [r["id"] for r in records if r["granularity"] == "atomic"]
    comp_rows = []
    for aid in atomic_ids:
        mid = mother_id(aid)
        b = rec_by_id[mid]
        a = rec_by_id[aid]
        delta = a["cosine"] - b["cosine"]  # atomic - bundle
        comp_rows.append({
            "mother_id": mid,
            "atomic_id": aid,
            "domain": a["domain"],
            "bundle_cosine": b["cosine"],
            "atomic_cosine": a["cosine"],
            "delta": delta,
            "atomic_anchor_rank": a["anchor_rank"],
            "atomic_nearest_anchor_id": a["nearest_anchor_id"],
            "atomic_nearest_anchor_cosine": a["nearest_anchor_cosine"],
        })

    deltas = [c["delta"] for c in comp_rows]
    n_pos = sum(1 for d in deltas if d > 0)
    n_neg = sum(1 for d in deltas if d < 0)
    n_zero = sum(1 for d in deltas if d == 0)

    # ----- report.md -----
    report_path = os.path.join(RESULTS_DIR, "report.md")
    L = []
    L.append("# Phase 0.6 — Dilution-Effect Diagnostic (atomic-variant incremental cosine)")
    L.append("")
    L.append("DIAGNOSTIC MEASUREMENT ONLY. No thresholding, no pass/fail, no data-quality "
             "gate. This run characterizes how the anchor cosine reading changes when an "
             "offset is compressed from bundle form to a single-parameter atomic sentence. "
             "All interpretation is done in chat, not by this script.")
    L.append("")
    L.append("## Run environment")
    L.append("")
    L.append(f"- Model (from config.yaml `embedding.model_name`): `{model_name}`")
    L.append(f"- sentence-transformers version: `{sentence_transformers.__version__}`")
    L.append(f"- Python: `{platform.python_version()}` ({sys.executable})")
    L.append(f"- Platform: `{platform.platform()}`")
    L.append(f"- Run date (label dir): `2026_06_11_p06` (date.today()={date.today().isoformat()})")
    L.append(f"- Pairs: {len(pairs)} ({len(bundle)} bundle + {len(atomic)} atomic)")
    L.append("- cosine = dot product of L2-normalized embeddings (`normalize_embeddings=True`).")
    L.append("- delta = atomic_cosine - bundle_cosine (positive => compression RAISED similarity).")
    L.append("- anchor_rank computed against the 15 distinct mother (bundle) anchors; atomic "
             "variants share their mother anchor verbatim and are ranked in the same 15-anchor pool.")
    L.append("")

    # (1) 5-group comparison table
    L.append("## (1) Atomic vs bundle paired comparison (5 groups)")
    L.append("")
    L.append("| id | domain | bundle cosine | atomic cosine | delta (atomic-bundle) | atomic anchor_rank |")
    L.append("|----|--------|--------------:|--------------:|----------------------:|:------------------:|")
    for c in comp_rows:
        L.append(
            f"| {c['mother_id']} -> {c['atomic_id']} | {c['domain']} | "
            f"{c['bundle_cosine']:.4f} | {c['atomic_cosine']:.4f} | "
            f"{c['delta']:+.4f} | {c['atomic_anchor_rank']} |"
        )
    L.append("")

    # (2) direction counts + delta stats
    L.append("## (2) Direction counts and delta distribution")
    L.append("")
    L.append(f"- groups with delta > 0 (atomic raised cosine): {n_pos} / {len(comp_rows)}")
    L.append(f"- groups with delta < 0 (atomic lowered cosine): {n_neg} / {len(comp_rows)}")
    L.append(f"- groups with delta == 0: {n_zero} / {len(comp_rows)}")
    if deltas:
        L.append(f"- delta mean: {statistics.fmean(deltas):+.4f}")
        L.append(f"- delta min:  {min(deltas):+.4f}")
        L.append(f"- delta max:  {max(deltas):+.4f}")
    L.append("")

    # (3) atomic cross-pair anchor_rank
    L.append("## (3) Atomic cross-pair anchor_rank (vs 15 mother anchors)")
    L.append("")
    L.append("| atomic id | domain | atomic cosine | anchor_rank | nearest_anchor_id | nearest_anchor_cosine |")
    L.append("|-----------|--------|--------------:|:-----------:|-------------------|----------------------:|")
    for c in comp_rows:
        flag = "" if c["atomic_anchor_rank"] == 1 else "  <-- own anchor NOT nearest"
        L.append(
            f"| {c['atomic_id']} | {c['domain']} | {c['atomic_cosine']:.4f} | "
            f"{c['atomic_anchor_rank']} | {c['atomic_nearest_anchor_id']} | "
            f"{c['atomic_nearest_anchor_cosine']:.4f} |{flag}"
        )
    L.append("")
    non1 = [c for c in comp_rows if c["atomic_anchor_rank"] != 1]
    if non1:
        L.append("Atomic variants whose own (mother) anchor is NOT nearest:")
        for c in non1:
            L.append(
                f"- {c['atomic_id']}: rank={c['atomic_anchor_rank']}, "
                f"nearest={c['atomic_nearest_anchor_id']} "
                f"(own={c['atomic_cosine']:.4f}, nearest={c['atomic_nearest_anchor_cosine']:.4f})"
            )
    else:
        L.append("All 5 atomic variants have their own mother anchor as nearest (anchor_rank == 1).")
    L.append("")

    # (Appendix) full 20-row context (descriptive only)
    L.append("## (Appendix) Full-set descriptive context (all 20 rows)")
    L.append("")
    L.append(f"- overall (n=20): {fmt_stats(overall)}")
    L.append(f"- bundle (n={len(bundle)}): {fmt_stats(describe(bundle))}")
    L.append(f"- atomic (n={len(atomic)}): {fmt_stats(describe(atomic))}")
    L.append(f"- Type A (n={len(type_a)}): {fmt_stats(describe(type_a))}")
    L.append(f"- Type B (n={len(type_b)}): {fmt_stats(describe(type_b))}")
    L.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(L))

    # ----- console summary -----
    print()
    print("=== atomic vs bundle (delta = atomic - bundle) ===")
    for c in comp_rows:
        print(f"  {c['mother_id']:>6} -> {c['atomic_id']:<7} "
              f"bundle={c['bundle_cosine']:.4f} atomic={c['atomic_cosine']:.4f} "
              f"delta={c['delta']:+.4f} rank={c['atomic_anchor_rank']}")
    print(f"delta>0: {n_pos}/{len(comp_rows)} | delta<0: {n_neg} | "
          f"mean={statistics.fmean(deltas):+.4f} min={min(deltas):+.4f} max={max(deltas):+.4f}")
    print()
    print(f"wrote: {results_json}")
    print(f"wrote: {report_path}")


if __name__ == "__main__":
    main()
