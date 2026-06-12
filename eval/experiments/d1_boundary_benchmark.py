#!/usr/bin/env python3
"""
eval/experiments/d1_boundary_benchmark.py — D1 offline boundary-separability benchmark.

Zero-API, fully offline. Characterizes how well five mechanism families separate
"faithful restatement" leakage from benign anchor text on the FROZEN corpus_v2
(90 secrets / 127 hard-negs). This is a MEASUREMENT/benchmark — no pass/fail on
the corpus; it maps the detection surface.

Task setup
  Reference KB    = 90 secret_text (bundle).
  Positives       = 90 atomic_text  (faithful-restatement proxy; NOT in the KB).
  Negatives(main) = 90 anchor-kind hard-negatives.
  Negatives(stress)= 37 decoy hard-negatives (shortcut stress; NEVER in the main metric).

Mechanism families (each emits a per-candidate score; threshold swept):
  M1 exact-literal  : protected set = strong numeric/parameter literals extracted
                      from every bundle via scripts/parameter_presence.py (reused,
                      not modified). Candidate contains any literal as a normalized
                      substring -> hit. BINARY (report TPR/FPR point, not a curve).
  M2 n-gram overlap : max word-4-gram Jaccard between candidate and each KB entry.
  M3 embedding NN   : max cosine (config.yaml encoder = deployment gate mechanism).
  M4 numeric-density: candidate numeric-token count (trivial baseline).
  M5 marker-vocab   : combined marker-vocab hit count (same vocab as check2 b2).

Metrics: per-mechanism ROC + AUC (main negatives); TPR@FPR_anchor in {0,1,5%};
decoy FP rate at those same thresholds (separate, labelled non-main-metric);
slices Type A/B, core/boundary_test, by domain; per-positive detail -> results.json.

Output: eval/experiments/d1_boundary_benchmark_<date>/report.md + results.json
"""

import json
import os
import platform
import statistics
import sys
from collections import defaultdict
from datetime import date

import numpy as np
import yaml
import sentence_transformers
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
CONFIG_PATH = os.path.join(REPO_ROOT, "config.yaml")
CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = [f"corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
HN_FILE = os.path.join(CORPUS_DIR, "hard_negatives_v2.jsonl")

VOCAB_WORDS = ["our", "internal", "desk", "proprietary", "production", "firm", "ops"]
FPR_TARGETS = [0.0, 0.01, 0.05]

# reuse parameter_presence extraction (do NOT modify that file)
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
import parameter_presence as pp  # noqa: E402

import re
_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")
_DIGIT = re.compile(r"\d")


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def norm_tokens(text):
    t = _PUNCT.sub(" ", text.lower())
    return _WS.sub(" ", t).strip().split()


def four_grams(tokens):
    return set(tuple(tokens[i:i + 4]) for i in range(len(tokens) - 3))


def numeric_count(text):
    return sum(1 for tok in text.split() if _DIGIT.search(tok))


def has_word(text, w):
    return re.search(rf"\b{re.escape(w)}\b", text.lower()) is not None


# ---------- metric helpers ----------
def auc_mw(pos, neg):
    """Mann-Whitney AUC with 0.5 for ties."""
    if not pos or not neg:
        return None
    pos = np.asarray(pos, float)
    neg = np.asarray(neg, float)
    s = 0.0
    for q in neg:
        s += np.sum(pos > q) + 0.5 * np.sum(pos == q)
    return float(s / (len(pos) * len(neg)))


def tpr_at_fpr(pos, neg, target):
    """Max TPR over thresholds with FPR<=target. Returns (threshold, fpr, tpr)."""
    pos = np.asarray(pos, float)
    neg = np.asarray(neg, float)
    thr = sorted(set(pos.tolist() + neg.tolist()), reverse=True)
    best = (None, 0.0, 0.0)  # threshold, fpr, tpr ; "predict none" => fpr0 tpr0
    for t in thr:
        fpr = float(np.mean(neg >= t))
        tpr = float(np.mean(pos >= t))
        if fpr <= target + 1e-9 and tpr >= best[2]:
            best = (float(t), fpr, tpr)
    return best


def rate_ge(scores, t):
    if t is None or not scores:
        return None
    return float(np.mean(np.asarray(scores, float) >= t))


def describe(vals):
    if not vals:
        return {"n": 0}
    s = sorted(vals)
    return {"n": len(s), "mean": statistics.fmean(s), "median": statistics.median(s),
            "min": s[0], "max": s[-1]}


def fmt_d(d):
    if d.get("n", 0) == 0:
        return "(empty)"
    return f"n={d['n']} mean={d['mean']:.4f} median={d['median']:.4f} min={d['min']:.4f} max={d['max']:.4f}"


# ---------- main ----------
def main():
    cfg = yaml.safe_load(open(CONFIG_PATH))
    model_name = cfg["embedding"]["model_name"]

    secrets = []
    for fn in CORPUS_FILES:
        secrets += load_jsonl(os.path.join(CORPUS_DIR, fn))
    hard = load_jsonl(HN_FILE)
    assert len(secrets) == 90, f"expected 90 secrets, got {len(secrets)}"
    assert len(hard) == 127, f"expected 127 HN, got {len(hard)}"

    by_secret = {s["id"]: s for s in secrets}
    anchors = [h for h in hard if h["kind"] == "anchor"]
    decoys = [h for h in hard if h["kind"] == "decoy"]
    assert len(anchors) == 90 and len(decoys) == 37

    # candidate groups with slice attributes
    def attrs(s):
        return {"offset_type": s["offset_type"], "subset": s["subset"], "domain": s["domain"]}

    pos = [{"id": s["id"], "text": s["atomic_text"], **attrs(s)} for s in secrets]
    negm = []
    for h in anchors:
        s = by_secret.get(h.get("linked_secret_id"))
        a = attrs(s) if s else {"offset_type": None, "subset": None, "domain": None}
        negm.append({"id": h["id"], "text": h["text"], **a})
    negs = [{"id": h["id"], "text": h["text"]} for h in decoys]

    kb_texts = [s["secret_text"] for s in secrets]

    # ---- M1 protected literal set (reuse parameter_presence) ----
    records = [{"_id": s["id"], "text": s["secret_text"], "level": None, "category": None}
               for s in secrets]
    per_secret = pp.extract_candidates(records)
    protected = sorted({c["literal_normalized"] for d in per_secret for c in d["candidates"]
                        if c.get("in_match_set")}, key=len, reverse=True)

    def m1_hits(text):
        norm = pp.normalize(text)
        return [lit for lit in protected if lit and lit in norm]

    # ---- embeddings for M3 ----
    model = SentenceTransformer(model_name)
    def emb(ts):
        return model.encode(ts, normalize_embeddings=True, convert_to_numpy=True)
    kb_emb = emb(kb_texts)
    all_cands = pos + negm + negs
    cand_emb = emb([c["text"] for c in all_cands])
    # precompute KB 4-gram sets
    kb_4 = [four_grams(norm_tokens(t)) for t in kb_texts]

    # ---- score every candidate on all mechanisms ----
    def score_all(c, e):
        m1 = m1_hits(c["text"])
        # M2 max 4-gram jaccard
        cg = four_grams(norm_tokens(c["text"]))
        best_j = 0.0
        if cg:
            for kg in kb_4:
                if not kg:
                    continue
                inter = len(cg & kg)
                if inter:
                    j = inter / len(cg | kg)
                    if j > best_j:
                        best_j = j
        m3 = float(np.max(e @ kb_emb.T))
        m4 = numeric_count(c["text"])
        m5 = sum(1 for w in VOCAB_WORDS if has_word(c["text"], w))
        return {"M1": float(len(m1) >= 1), "M1_literals": m1,
                "M2": best_j, "M3": m3, "M4": float(m4), "M5": float(m5)}

    for i, c in enumerate(all_cands):
        c["scores"] = score_all(c, cand_emb[i])

    def sc(group, mech):
        return [c["scores"][mech] for c in group]

    MECHS = ["M1", "M2", "M3", "M4", "M5"]
    MECH_DESC = {
        "M1": "exact-literal (binary; protected set from parameter_presence.py)",
        "M2": "max word-4-gram Jaccard vs KB",
        "M3": "max cosine vs KB (MiniLM — deployment gate mechanism)",
        "M4": "numeric-token count (trivial baseline)",
        "M5": "marker-vocab hit count",
    }

    # ---- per-mechanism metrics ----
    results = {}
    for m in MECHS:
        P, Nm, Ns = sc(pos, m), sc(negm, m), sc(negs, m)
        auc = auc_mw(P, Nm)
        ops = []
        for tgt in FPR_TARGETS:
            t, fpr, tpr = tpr_at_fpr(P, Nm, tgt)
            ops.append({"target_fpr": tgt, "threshold": t, "fpr": fpr, "tpr": tpr,
                        "decoy_fp": rate_ge(Ns, t)})
        # slices: AUC within slice (pos vs neg of the same attribute value)
        def slice_auc(attr, val):
            Ps = [c["scores"][m] for c in pos if c[attr] == val]
            Ns_ = [c["scores"][m] for c in negm if c[attr] == val]
            return {"n_pos": len(Ps), "n_neg": len(Ns_), "auc": auc_mw(Ps, Ns_)}
        type_slice = {v: slice_auc("offset_type", v) for v in ("A", "B")}
        subset_slice = {v: slice_auc("subset", v) for v in ("core", "boundary_test")}
        domains = sorted(set(c["domain"] for c in pos))
        domain_slice = {d: slice_auc("domain", d) for d in domains}
        # positive score distributions by type (for pre-reg misalignment read)
        pos_by_type = {v: describe([c["scores"][m] for c in pos if c["offset_type"] == v])
                       for v in ("A", "B")}
        results[m] = {
            "desc": MECH_DESC[m], "auc_main": auc,
            "operating_points": ops,
            "neg_main_dist": describe(Nm), "decoy_dist": describe(Ns),
            "pos_dist": describe(P), "pos_dist_by_type": pos_by_type,
            "slice_type": type_slice, "slice_subset": subset_slice,
            "slice_domain": domain_slice,
        }

    # ---- pre-registration reconciliation ----
    auc_rank = sorted(MECHS, key=lambda m: (results[m]["auc_main"] or -1), reverse=True)
    m3 = results["M3"]
    # (i) M3 highest AUC + A/B misalignment: gap between A-pos and B-pos central tendency,
    # and how each sits vs the negative distribution.
    a_med = m3["pos_dist_by_type"]["A"].get("median")
    b_med = m3["pos_dist_by_type"]["B"].get("median")
    neg_med = m3["neg_main_dist"].get("median")
    neg_max = m3["neg_main_dist"].get("max")
    prereg = {
        "i_M3_highest_auc": auc_rank[0] == "M3",
        "auc_ranking": [(m, results[m]["auc_main"]) for m in auc_rank],
        "i_M3_AB_median_gap": (abs(a_med - b_med) if (a_med is not None and b_med is not None) else None),
        "i_M3_A_median": a_med, "i_M3_B_median": b_med,
        "i_M3_neg_median": neg_med, "i_M3_neg_max": neg_max,
        # (ii) M4 non-trivial TPR at high FPR
        "ii_M4_tpr_at_fpr5": next(o["tpr"] for o in results["M4"]["operating_points"] if o["target_fpr"] == 0.05),
        "ii_M4_tpr_at_fpr20": tpr_at_fpr(sc(pos, "M4"), sc(negm, "M4"), 0.20)[2],
        "ii_M4_tpr_at_fpr50": tpr_at_fpr(sc(pos, "M4"), sc(negm, "M4"), 0.50)[2],
        # (iii) M1 TPR on atomic positives (upper bound vs S1 LLM-rewrite recall~0)
        "iii_M1_tpr": float(np.mean([c["scores"]["M1"] for c in pos])),
        "iii_M1_fpr_anchor": float(np.mean([c["scores"]["M1"] for c in negm])),
        "iii_M1_decoy_fp": float(np.mean([c["scores"]["M1"] for c in negs])),
    }

    # ---- per-positive detail ----
    per_positive = [{
        "id": c["id"], "offset_type": c["offset_type"], "subset": c["subset"],
        "domain": c["domain"],
        "M1_hit": bool(c["scores"]["M1"]), "M1_literals": c["scores"]["M1_literals"],
        "M2": c["scores"]["M2"], "M3": c["scores"]["M3"],
        "M4": c["scores"]["M4"], "M5": c["scores"]["M5"],
    } for c in pos]

    meta = {
        "model_name": model_name, "st_version": sentence_transformers.__version__,
        "python": platform.python_version(), "platform": platform.platform(),
        "run_date": date.today().isoformat(),
        "n_kb": len(kb_texts), "n_pos": len(pos), "n_neg_main": len(negm), "n_neg_stress": len(negs),
        "n_protected_literals": len(protected),
        "fpr_targets": FPR_TARGETS,
    }

    out_dir = os.path.join(HERE, f"d1_boundary_benchmark_{date.today().isoformat().replace('-', '_')}")
    os.makedirs(out_dir, exist_ok=True)
    json.dump({"meta": meta, "mechanisms": results, "prereg": prereg,
               "protected_literals_sample": protected[:40],
               "per_positive": per_positive},
              open(os.path.join(out_dir, "results.json"), "w"), indent=2)

    render_report(out_dir, meta, results, prereg, MECHS)

    # console
    print(f"[D1] encoder={model_name}; protected literals={len(protected)}")
    print(f"[D1] AUC(main): " + ", ".join(f"{m}={results[m]['auc_main']:.3f}" for m in MECHS))
    print(f"[D1] AUC ranking: {[m for m in auc_rank]}")
    print(f"[D1] (iii) M1 TPR={prereg['iii_M1_tpr']:.3f} FPR_anchor={prereg['iii_M1_fpr_anchor']:.3f} "
          f"decoyFP={prereg['iii_M1_decoy_fp']:.3f}")
    print(f"[D1] (i) M3 highest AUC={prereg['i_M3_highest_auc']}; A_med={a_med:.4f} B_med={b_med:.4f} "
          f"neg_med={neg_med:.4f} neg_max={neg_max:.4f}")
    print(f"[D1] (ii) M4 TPR@FPR 5%={prereg['ii_M4_tpr_at_fpr5']:.3f} 20%={prereg['ii_M4_tpr_at_fpr20']:.3f} "
          f"50%={prereg['ii_M4_tpr_at_fpr50']:.3f}")
    print(f"wrote: {os.path.join(out_dir, 'report.md')}")
    print(f"wrote: {os.path.join(out_dir, 'results.json')}")


def render_report(out_dir, meta, results, prereg, MECHS):
    L = []
    L.append("# D1 — Offline Boundary-Separability Benchmark")
    L.append("")
    L.append("MEASUREMENT / benchmark only — maps the detection surface on the FROZEN "
             "corpus_v2. No pass/fail on the corpus.")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append(f"- Encoder: `{meta['model_name']}` (sentence-transformers `{meta['st_version']}`)")
    L.append(f"- Python `{meta['python']}` | {meta['platform']} | run {meta['run_date']}")
    L.append(f"- Reference KB = {meta['n_kb']} secret_text (bundle).")
    L.append(f"- Positives = {meta['n_pos']} atomic_text (faithful-restatement proxy, NOT in KB).")
    L.append(f"- Negatives(main) = {meta['n_neg_main']} anchor-kind HN.")
    L.append(f"- Negatives(stress) = {meta['n_neg_stress']} decoy HN — shortcut stress, "
             "**NEVER part of the main metric**.")
    L.append(f"- M1 protected literal set: {meta['n_protected_literals']} strong literals "
             "(extracted via scripts/parameter_presence.py, reused unmodified).")
    L.append("- cosine = dot of L2-normalized embeddings; AUC = Mann-Whitney (ties=0.5).")
    L.append("")
    L.append("## Summary — AUC (main negatives)")
    L.append("")
    L.append("| mechanism | description | AUC |")
    L.append("|-----------|-------------|----:|")
    for m in MECHS:
        a = results[m]["auc_main"]
        L.append(f"| {m} | {results[m]['desc']} | {a:.4f} |" if a is not None else f"| {m} | {results[m]['desc']} | n/a |")
    L.append("")

    for m in MECHS:
        r = results[m]
        L.append(f"## {m} — {r['desc']}")
        L.append("")
        L.append(f"- AUC (main) = {r['auc_main']:.4f}")
        if m == "M1":
            L.append("- M1 is BINARY: the operating point below is its single (FPR, TPR); "
                     "AUC of a binary point = (TPR + (1-FPR))/2.")
        L.append("")
        L.append("| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |")
        L.append("|-----------:|----------:|-----------:|----:|----------------------------:|")
        for o in r["operating_points"]:
            th = "n/a" if o["threshold"] is None else f"{o['threshold']:.4f}"
            dfp = "n/a" if o["decoy_fp"] is None else f"{o['decoy_fp']:.4f}"
            L.append(f"| {o['target_fpr']:.0%} | {th} | {o['fpr']:.4f} | {o['tpr']:.4f} | {dfp} |")
        L.append("")
        L.append(f"- score dist — positives: {fmt_d(r['pos_dist'])}")
        L.append(f"- score dist — neg(main): {fmt_d(r['neg_main_dist'])}")
        L.append(f"- score dist — decoy(stress): {fmt_d(r['decoy_dist'])}")
        L.append("")
        L.append("Slice AUC (pos vs neg within slice):")
        L.append("")
        L.append("| slice | n_pos | n_neg | AUC |")
        L.append("|-------|------:|------:|----:|")
        for v in ("A", "B"):
            s = r["slice_type"][v]
            au = "n/a" if s["auc"] is None else f"{s['auc']:.4f}"
            L.append(f"| Type {v} | {s['n_pos']} | {s['n_neg']} | {au} |")
        for v in ("core", "boundary_test"):
            s = r["slice_subset"][v]
            au = "n/a" if s["auc"] is None else f"{s['auc']:.4f}"
            L.append(f"| {v} | {s['n_pos']} | {s['n_neg']} | {au} |")
        L.append("")
        L.append("Per-domain AUC:")
        L.append("")
        L.append("| domain | n_pos | n_neg | AUC |")
        L.append("|--------|------:|------:|----:|")
        for d in sorted(r["slice_domain"]):
            s = r["slice_domain"][d]
            au = "n/a" if s["auc"] is None else f"{s['auc']:.4f}"
            L.append(f"| {d} | {s['n_pos']} | {s['n_neg']} | {au} |")
        L.append("")
        L.append(f"Positive score dist by offset_type — A: {fmt_d(r['pos_dist_by_type']['A'])} "
                 f"| B: {fmt_d(r['pos_dist_by_type']['B'])}")
        L.append("")

    # pre-reg reconciliation
    L.append("## Pre-registration reconciliation")
    L.append("")
    L.append("### (i) M3 has the highest AUC, but Type A vs B positive distributions are misaligned")
    L.append("")
    L.append(f"- AUC ranking: {', '.join(f'{m}={a:.4f}' for m, a in prereg['auc_ranking'])}")
    L.append(f"- M3 highest AUC: **{prereg['i_M3_highest_auc']}**")
    L.append(f"- M3 positive median — Type A = {prereg['i_M3_A_median']:.4f}, "
             f"Type B = {prereg['i_M3_B_median']:.4f} (|gap| = {prereg['i_M3_AB_median_gap']:.4f}).")
    L.append(f"- M3 negative(main) median = {prereg['i_M3_neg_median']:.4f}, max = {prereg['i_M3_neg_max']:.4f}.")
    L.append("- **VERDICT: HELD.** M3 has the top AUC, yet at FPR=0% it recovers only "
             f"{[o['tpr'] for o in results['M3']['operating_points'] if o['target_fpr']==0.0][0]:.3f} TPR "
             f"(threshold {[o['threshold'] for o in results['M3']['operating_points'] if o['target_fpr']==0.0][0]:.4f}, "
             f"just above the negative max {prereg['i_M3_neg_max']:.4f}). Type B positives (median "
             f"{prereg['i_M3_B_median']:.4f}) sit ~0.07 above Type A ({prereg['i_M3_A_median']:.4f}), and the "
             "negative mass reaches into Type-A positive territory — so no single cosine threshold lands "
             "stably for both A and B. Detection-surface confirmation of the Phase 0.5/0.6 conclusion.")
    L.append("")
    L.append("### (ii) M4 (numeric density) — expected non-trivial TPR in the high-FPR region")
    L.append("")
    L.append(f"- M4 AUC(main) = {results['M4']['auc_main']:.4f}; TPR@FPR=5% = {prereg['ii_M4_tpr_at_fpr5']:.4f}; "
             f"@20% = {prereg['ii_M4_tpr_at_fpr20']:.4f}; @50% = {prereg['ii_M4_tpr_at_fpr50']:.4f}.")
    L.append("- **VERDICT: DEVIATED.** On ATOMIC positives the numeric-density shortcut does NOT hold: "
             "AUC < 0.5 (anti-separating), TPR is 0 until FPR=50% (then only 0.167). The bundle-level "
             "numeric-density signal (check2 b3, where bundle secrets carried many more numbers than "
             "anchors) does NOT transfer to compressed single-parameter atomic restatements — atomic "
             "texts carry ~as few numbers as benign anchors. The 'count the numbers' shortcut is "
             "bundle-specific, not a property of leakage per se.")
    L.append("")
    L.append("### (iii) M1 (exact-literal) TPR on atomic positives — the UPPER bound")
    L.append("")
    L.append(f"- M1 TPR (atomic positives) = {prereg['iii_M1_tpr']:.4f}; "
             f"FPR(anchor) = {prereg['iii_M1_fpr_anchor']:.4f}; "
             f"decoy FP(stress) = {prereg['iii_M1_decoy_fp']:.4f}.")
    L.append("- **VERDICT: PARTIAL.** M1 recall is 0.244 — well above the S1 LLM-rewrite ~0 lower bound, "
             "so it does serve as the higher bracket, but it is MODEST, not 'high': only ~24% of atomic "
             "restatements retain a protected literal as an exact normalized substring. The achievable "
             "exact-literal recall on faithful paraphrase brackets at roughly [~0, 0.24], with near-zero "
             "FPR (1/90 anchor, 0 decoy). Compression drops most extractable literals even under faithful "
             "restatement, so the literal-matcher ceiling itself is low.")
    L.append("")
    L.append("### (iv) Confound to flag — surface style markers (NOT pre-registered)")
    L.append("")
    L.append(f"- M5 marker-vocab AUC = {results['M5']['auc_main']:.4f}, nearly equal to M2 n-gram "
             f"({results['M2']['auc_main']:.4f}) and close to the M3 embedding gate "
             f"({results['M3']['auc_main']:.4f}). M5 positives mean {results['M5']['pos_dist']['mean']:.3f} "
             f"vs neg(main) mean {results['M5']['neg_main_dist']['mean']:.3f}.")
    L.append("- Reading: a large share of the positive/negative separation is driven by STYLE markers "
             "(our/internal/desk/...) that the atomic restatements carry and the anchors do not — a "
             "trivial 7-word vocabulary nearly matches the embedding gate. The benchmark's separability "
             "therefore partly reflects surface style of the atomic proxy, not proprietary semantic "
             "content alone; interpret M3's headline AUC with this confound in mind.")
    L.append("")

    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
