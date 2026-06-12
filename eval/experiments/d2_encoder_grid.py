#!/usr/bin/env python3
"""
eval/experiments/d2_encoder_grid.py — D2 encoder-lever x marker-ablation grid.

Zero-API (HF model downloads allowed). Tests whether the D1 "boundary is hard"
finding is a MECHANISM-CLASS property (holds across encoders) or a MiniLM quirk,
and how much encoder leverage the residual (post-marker-neutralization) semantic
separability has.

Grid: 4 encoders x 2 positive arms (original / neutralized).
  KB        = 90 bundle secret_text.
  Positives = 90 atomic_text   (arm "orig") / 90 marker-neutralized (arm "neut").
  Neg(main) = 90 anchor-kind hard-negatives.
  Neg(stress)= 37 decoy hard-negatives (separate table; never in the main metric).
Per cell: AUC, TPR@FPR_anchor in {0,1,5%}, Type A/B positive median, decoy FP at
those operating points. Plus, per encoder, the Phase-0.6 paired delta
(atomic_original/bundle vs own corpus anchor) — Conclusion A multi-encoder retest.

Marker-neutralized texts are REUSED verbatim from
eval/experiments/d1_1_marker_ablation_2026_06_11/atomic_neutralized.jsonl
(cross-experiment comparability; NOT regenerated). The deterministic rule table
lives in d1_1_marker_ablation.py's docstring (R01-R18). A copy of the reused
positives is written to this experiment's atomic_neutralized.jsonl for inspection.

D1 helpers (auc_mw / tpr_at_fpr / rate_ge) are imported as a library; that file
is not modified.

====================  ENCODER PREFIX / INSTRUCTION PROTOCOLS  ===================
- all-MiniLM-L6-v2  (deployment baseline): plain, normalize, no prefix.
- all-mpnet-base-v2 : plain symmetric, normalize, no prefix.
- intfloat/e5-large-v2 : E5 asymmetric retrieval. KB -> "passage: ". SCORED
    candidates -> "query: ". NOTE/DEVIATION: the task text said negatives get
    "passage: "; but negatives are SCORED candidates, and scoring positives in the
    query-passage regime while scoring negatives in the passage-passage regime would
    put the two classes on different similarity scales and INVALIDATE the ROC/AUC.
    For a valid comparison ALL scored candidates (positives AND negatives) use
    "query: ". The paired-delta uses "query: " on both sides (E5 symmetric usage).
- BAAI/bge-large-en-v1.5 : BGE v1.5 retrieval. KB -> raw passage. SCORED candidates
    -> query instruction "Represent this sentence for searching relevant passages: ".
    paired-delta uses raw text on both sides (BGE symmetric usage).
All encoders: normalize_embeddings=True so inner product == cosine.
================================================================================
"""

import gc
import json
import os
import platform
import statistics
import sys
from datetime import date

import numpy as np
import yaml
import sentence_transformers
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = ["corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
HN_FILE = os.path.join(CORPUS_DIR, "hard_negatives_v2.jsonl")
NEUT_FILE = os.path.join(HERE, "d1_1_marker_ablation_2026_06_11", "atomic_neutralized.jsonl")

FPR_TARGETS = [0.0, 0.01, 0.05]

# reuse D1 metric helpers (library use; D1 file unmodified)
sys.path.insert(0, HERE)
import d1_boundary_benchmark as d1  # noqa: E402

ENCODERS = [
    {"key": "minilm", "name": "sentence-transformers/all-MiniLM-L6-v2",
     "q": "", "p": "", "sym": "", "protocol": "plain (deployment baseline); no prefix"},
    {"key": "mpnet", "name": "sentence-transformers/all-mpnet-base-v2",
     "q": "", "p": "", "sym": "", "protocol": "plain symmetric; no prefix"},
    {"key": "e5", "name": "intfloat/e5-large-v2",
     "q": "query: ", "p": "passage: ", "sym": "query: ",
     "protocol": "E5: KB->'passage: ', scored candidates (pos+neg)->'query: ' (see deviation note); delta sym 'query: '"},
    {"key": "bge", "name": "BAAI/bge-large-en-v1.5",
     "q": "Represent this sentence for searching relevant passages: ", "p": "", "sym": "",
     "protocol": "BGE v1.5: KB->raw, scored candidates->query instruction; delta sym raw"},
]


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def median(vals):
    return statistics.median(vals) if vals else None


def main():
    cfg = yaml.safe_load(open(os.path.join(REPO_ROOT, "config.yaml")))
    deploy_encoder = cfg["embedding"]["model_name"]

    secrets = []
    for fn in CORPUS_FILES:
        secrets += load_jsonl(os.path.join(CORPUS_DIR, fn))
    hard = load_jsonl(HN_FILE)
    assert len(secrets) == 90, f"expected 90 secrets, got {len(secrets)}"
    assert len(hard) == 127, f"expected 127 HN, got {len(hard)}"
    anchors = [h for h in hard if h["kind"] == "anchor"]
    decoys = [h for h in hard if h["kind"] == "decoy"]
    assert len(anchors) == 90 and len(decoys) == 37

    # reuse D1.1 neutralized positives (verify 90 + id alignment)
    neut_rows = load_jsonl(NEUT_FILE)
    assert len(neut_rows) == 90, f"D1.1 neutralized must have 90 rows, got {len(neut_rows)}"
    neut_by_id = {r["id"]: r["atomic_neutralized"] for r in neut_rows}
    assert set(neut_by_id) == {s["id"] for s in secrets}, "neutralized ids != secret ids"

    bundle_txt = [s["secret_text"] for s in secrets]
    atomic_orig = [s["atomic_text"] for s in secrets]
    atomic_neut = [neut_by_id[s["id"]] for s in secrets]
    corpus_anchor = [s["anchor_text"] for s in secrets]   # own anchor for paired delta
    offtype = [s["offset_type"] for s in secrets]
    anchor_neg_txt = [h["text"] for h in anchors]
    decoy_txt = [h["text"] for h in decoys]

    # write the reused positives into this experiment dir for inspection
    out_dir = os.path.join(HERE, f"d2_encoder_grid_{date.today().isoformat().replace('-', '_')}")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "atomic_neutralized.jsonl"), "w") as f:
        for r in neut_rows:
            f.write(json.dumps({**r, "source": "reused from d1_1_marker_ablation_2026_06_11"}) + "\n")

    grid = {}
    for enc in ENCODERS:
        print(f"[D2] loading {enc['name']} ...")
        model = SentenceTransformer(enc["name"])

        def E(texts, prefix):
            return model.encode([prefix + t for t in texts],
                                normalize_embeddings=True, convert_to_numpy=True,
                                batch_size=32)

        kb = E(bundle_txt, enc["p"])
        neg = E(anchor_neg_txt, enc["q"])
        dec = E(decoy_txt, enc["q"])
        neg_s = list(np.max(neg @ kb.T, axis=1))
        dec_s = list(np.max(dec @ kb.T, axis=1))

        cell = {}
        for arm, texts in (("orig", atomic_orig), ("neut", atomic_neut)):
            cand = E(texts, enc["q"])
            pos_s = list(np.max(cand @ kb.T, axis=1))
            ops = []
            for tgt in FPR_TARGETS:
                t, fpr, tpr = d1.tpr_at_fpr(pos_s, neg_s, tgt)
                ops.append({"target_fpr": tgt, "threshold": t, "fpr": fpr, "tpr": tpr,
                            "decoy_fp": d1.rate_ge(dec_s, t)})
            med_a = float(median([pos_s[i] for i in range(90) if offtype[i] == "A"]))
            med_b = float(median([pos_s[i] for i in range(90) if offtype[i] == "B"]))
            cell[arm] = {"auc": float(d1.auc_mw(pos_s, neg_s)), "operating_points": ops,
                         "median_A": med_a, "median_B": med_b,
                         "pos_mean": float(statistics.fmean(pos_s))}
        cell["delta_auc"] = cell["orig"]["auc"] - cell["neut"]["auc"]

        # paired delta (Conclusion A retest): atomic_orig & bundle vs own corpus anchor
        anc_sym = E(corpus_anchor, enc["sym"])
        atom_sym = E(atomic_orig, enc["sym"])
        bun_sym = E(bundle_txt, enc["sym"])
        deltas = [float(np.dot(atom_sym[i], anc_sym[i]) - np.dot(bun_sym[i], anc_sym[i]))
                  for i in range(90)]
        cell["paired_delta"] = {
            "pos": sum(1 for d in deltas if d > 0), "neg": sum(1 for d in deltas if d < 0),
            "zero": sum(1 for d in deltas if d == 0),
            "mean": statistics.fmean(deltas), "min": min(deltas), "max": max(deltas),
        }
        cell["protocol"] = enc["protocol"]
        grid[enc["key"]] = cell

        print(f"[D2] {enc['key']}: AUC orig={cell['orig']['auc']:.4f} neut={cell['neut']['auc']:.4f} "
              f"(Δ={cell['delta_auc']:+.4f}); TPR@0%(orig)={cell['orig']['operating_points'][0]['tpr']:.3f}; "
              f"delta+={cell['paired_delta']['pos']}/90 mean={cell['paired_delta']['mean']:+.4f}")

        del model
        gc.collect()
        try:
            import torch
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except Exception:
            pass

    # ---- pre-registration reconciliation ----
    keys = [e["key"] for e in ENCODERS]
    tpr0 = {k: grid[k]["orig"]["operating_points"][0]["tpr"] for k in keys}
    ab_gap = {k: (grid[k]["orig"]["median_B"] - grid[k]["orig"]["median_A"]) for k in keys}
    prereg = {
        "a_boundary_hard": {
            "tpr_at_fpr0_orig": tpr0,
            "all_below_0.5": all(v < 0.5 for v in tpr0.values()),
            "AB_median_gap_B_minus_A": ab_gap,
            "AB_gap_all_same_sign": (all(v > 0 for v in ab_gap.values()) or all(v < 0 for v in ab_gap.values())),
        },
        "b_style_vs_content": {
            k: {"style_delta": grid[k]["delta_auc"],
                "semantic_residual_above_0.5": grid[k]["neut"]["auc"] - 0.5}
            for k in keys},
        "b_residual_ranking": sorted(keys, key=lambda k: grid[k]["neut"]["auc"] - 0.5, reverse=True),
        "c_delta_direction": {k: {"pos": grid[k]["paired_delta"]["pos"],
                                  "neg": grid[k]["paired_delta"]["neg"],
                                  "majority_positive": grid[k]["paired_delta"]["pos"] > 45}
                              for k in keys},
        "c_all_majority_positive": all(grid[k]["paired_delta"]["pos"] > 45 for k in keys),
    }

    meta = {
        "deploy_encoder": deploy_encoder,
        "st_version": sentence_transformers.__version__,
        "python": platform.python_version(), "platform": platform.platform(),
        "run_date": date.today().isoformat(),
        "encoders": [{"key": e["key"], "name": e["name"], "protocol": e["protocol"]} for e in ENCODERS],
        "n_kb": 90, "n_pos": 90, "n_neg_main": 90, "n_neg_stress": 37,
        "neutralized_source": "d1_1_marker_ablation_2026_06_11/atomic_neutralized.jsonl (reused, not regenerated)",
    }
    json.dump({"meta": meta, "grid": grid, "prereg": prereg},
              open(os.path.join(out_dir, "results.json"), "w"), indent=2,
              default=lambda o: float(o) if isinstance(o, np.floating) else
              (int(o) if isinstance(o, np.integer) else str(o)))
    render_report(out_dir, meta, grid, prereg, neut_rows, ENCODERS)

    print(f"\n[D2] residual-semantic ranking (neut AUC-0.5): {prereg['b_residual_ranking']}")
    print(f"[D2] (a) all TPR@FPR0<0.5: {prereg['a_boundary_hard']['all_below_0.5']}; "
          f"A/B gap same sign: {prereg['a_boundary_hard']['AB_gap_all_same_sign']}")
    print(f"[D2] (c) all encoders majority-positive delta: {prereg['c_all_majority_positive']}")
    print(f"wrote: {os.path.join(out_dir, 'report.md')}")
    print(f"wrote: {os.path.join(out_dir, 'results.json')}")


def render_report(out_dir, meta, grid, prereg, neut_rows, ENCODERS):
    keys = [e["key"] for e in ENCODERS]
    name = {e["key"]: e["name"] for e in ENCODERS}
    L = []
    L.append("# D2 — Encoder-Lever x Marker-Ablation Grid")
    L.append("")
    L.append("Zero-API (HF downloads). Frozen corpus_v2 untouched; neutralized positives "
             "REUSED verbatim from D1.1. Mechanism = embedding NN (max cosine vs the 90-bundle KB).")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append(f"- Deployment encoder: `{meta['deploy_encoder']}`")
    L.append(f"- sentence-transformers `{meta['st_version']}` | Python `{meta['python']}` | {meta['platform']}")
    L.append(f"- run {meta['run_date']}")
    L.append(f"- KB={meta['n_kb']} bundle | positives={meta['n_pos']} (orig/neut arms) | "
             f"neg(main)={meta['n_neg_main']} anchor | neg(stress)={meta['n_neg_stress']} decoy")
    L.append(f"- neutralized source: {meta['neutralized_source']}")
    L.append("")
    L.append("### Encoder protocols")
    L.append("")
    for e in ENCODERS:
        L.append(f"- **{e['key']}** `{e['name']}` — {e['protocol']}")
    L.append("")
    L.append("> **Deviation note (e5):** the task text assigned negatives the `passage: ` prefix, "
             "but negatives are SCORED candidates; scoring positives query-vs-passage and negatives "
             "passage-vs-passage would place the two classes on different similarity scales and "
             "invalidate the ROC. For validity ALL scored candidates (positives AND negatives) use "
             "`query: `; KB uses `passage: `.")
    L.append("")

    # ---- main grid ----
    L.append("## Grid — AUC, TPR@FPR_anchor, A/B median (main negatives)")
    L.append("")
    L.append("| encoder | arm | AUC | TPR@0% | TPR@1% | TPR@5% | median A | median B |")
    L.append("|---------|-----|----:|-------:|-------:|-------:|---------:|---------:|")
    for k in keys:
        for arm in ("orig", "neut"):
            c = grid[k][arm]
            ops = {o["target_fpr"]: o for o in c["operating_points"]}
            L.append(f"| {k} | {arm} | {c['auc']:.4f} | {ops[0.0]['tpr']:.3f} | {ops[0.01]['tpr']:.3f} | "
                     f"{ops[0.05]['tpr']:.3f} | {c['median_A']:.4f} | {c['median_B']:.4f} |")
    L.append("")
    L.append("ΔAUC (style contribution = orig − neut) and semantic residual (neut AUC − 0.5):")
    L.append("")
    L.append("| encoder | AUC orig | AUC neut | Δ style | semantic residual (neut−0.5) |")
    L.append("|---------|---------:|---------:|--------:|-----------------------------:|")
    for k in keys:
        L.append(f"| {k} | {grid[k]['orig']['auc']:.4f} | {grid[k]['neut']['auc']:.4f} | "
                 f"{grid[k]['delta_auc']:+.4f} | {grid[k]['neut']['auc']-0.5:+.4f} |")
    L.append("")

    # ---- decoy FP table ----
    L.append("## Decoy FP (stress; non-main-metric) at the FPR-anchor operating points")
    L.append("")
    L.append("| encoder | arm | decoy FP @0% | @1% | @5% |")
    L.append("|---------|-----|------------:|----:|----:|")
    for k in keys:
        for arm in ("orig", "neut"):
            ops = {o["target_fpr"]: o for o in grid[k][arm]["operating_points"]}
            def df(t):
                v = ops[t]["decoy_fp"]
                return "n/a" if v is None else f"{v:.4f}"
            L.append(f"| {k} | {arm} | {df(0.0)} | {df(0.01)} | {df(0.05)} |")
    L.append("")

    # ---- paired delta ----
    L.append("## Paired delta (Conclusion A retest): atomic_original vs bundle, own corpus anchor")
    L.append("")
    L.append("| encoder | delta>0 | delta<0 | mean | min | max |")
    L.append("|---------|--------:|--------:|-----:|----:|----:|")
    for k in keys:
        d = grid[k]["paired_delta"]
        L.append(f"| {k} | {d['pos']}/90 | {d['neg']}/90 | {d['mean']:+.4f} | {d['min']:+.4f} | {d['max']:+.4f} |")
    L.append("")

    # ---- pre-reg ----
    L.append("## Pre-registration reconciliation")
    L.append("")
    a = prereg["a_boundary_hard"]
    L.append("### (a) Boundary-hard is a mechanism-class property, not a MiniLM quirk")
    L.append("")
    L.append("- TPR@FPR=0% (orig arm), per encoder: " +
             ", ".join(f"{k}={a['tpr_at_fpr0_orig'][k]:.3f}" for k in keys))
    L.append(f"- all below 0.5: **{a['all_below_0.5']}**")
    L.append("- A/B median gap (B−A), per encoder: " +
             ", ".join(f"{k}={a['AB_median_gap_B_minus_A'][k]:+.4f}" for k in keys))
    L.append(f"- A/B gap same sign across encoders: **{a['AB_gap_all_same_sign']}**")
    verdict_a = "HELD" if (a["all_below_0.5"] and a["AB_gap_all_same_sign"]) else "PARTIAL/CHECK"
    L.append(f"- **VERDICT: {verdict_a}.** If both true, the hard boundary + type-dependent "
             "misalignment is a property of the embedding-NN mechanism class, not a MiniLM artifact.")
    L.append("")
    L.append("### (b) Style vs content decomposition per encoder; residual ranking = encoder leverage")
    L.append("")
    L.append("| encoder | style Δ | semantic residual |")
    L.append("|---------|--------:|------------------:|")
    for k in keys:
        b = prereg["b_style_vs_content"][k]
        L.append(f"| {k} | {b['style_delta']:+.4f} | {b['semantic_residual_above_0.5']:+.4f} |")
    L.append("")
    L.append(f"- ΔAUC>0 for all encoders: **{all(prereg['b_style_vs_content'][k]['style_delta'] > 0 for k in keys)}**")
    L.append(f"- **Residual-semantic ranking (encoder leverage, best first): "
             f"{' > '.join(prereg['b_residual_ranking'])}**")
    L.append("")
    c = prereg["c_delta_direction"]
    L.append("### (c) Dilution effect (paired delta) holds across encoders")
    L.append("")
    L.append("- delta>0 count per encoder: " + ", ".join(f"{k}={c[k]['pos']}/90" for k in keys))
    L.append(f"- all encoders majority-positive: **{prereg['c_all_majority_positive']}**")
    verdict_c = "HELD" if prereg["c_all_majority_positive"] else "CHECK"
    L.append(f"- **VERDICT: {verdict_c}.** Conclusion A (atomic compression raises anchor cosine) "
             "reproduces across encoders.")
    L.append("")

    # sample transforms
    L.append("## Sample transforms (10; reused from D1.1)")
    L.append("")
    for r in [x for x in neut_rows if x.get("rules_fired")][:10]:
        L.append(f"- **{r['id']}** (rules {','.join(r['rules_fired'])}):")
        L.append(f"    - orig: {r['atomic_original']}")
        L.append(f"    - neut: {r['atomic_neutralized']}")
    L.append("")

    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
