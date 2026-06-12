#!/usr/bin/env python3
"""
eval/rerun_phase2/run_tier0_offline.py — Tier-0 offline reruns (ZERO API).

Two corpus_v2-affected reruns that need NO attack-set retargeting and NO LLM:

  E.  FPR retest (deterministic, gate-level) — reuses run_statistical_eval.evaluate_b2
      (identical 0-API gate semantics: rule_gate + embedding_secret_precheck +
      leakage_scan). Secret-detection index rebuilt IN-MEMORY from corpus_v2's 90
      bundles (nothing written to data/index/). Inputs: 100 benign + 65 old
      hard-neg + 90 corpus_v2 anchors + 37 corpus_v2 decoys. All are benign-class,
      so any block = false positive. Decoy is ALWAYS a separate table (paper
      protocol), never pooled into the main FPR. FPR stays gate-level — NO
      LLM response-level adjudication. TPR is N/A here (no attacks in this input;
      attack retargeting is Tier-1).
      McNemar: paired old-index (secrets_v2, 90) vs corpus_v2-index on the benign
      ∪ hard-neg set — does the restructure change the benign block decision?

  D§3.4.  8-cell embedding + retrieval-utility (OFFLINE half; NO per-cell leakage).
      4 encoders (minilm/mpnet/bge_large/finlang) x 2 corpora (old secrets_v2 /
      corpus_v2). Retrieval-utility relevance (ratified): each corpus's held-out
      PUBLIC PROBE -> its own secret (1 relevant doc), decoupled from the attack
      set. Probe = corpus_v2 anchor_text (designed public anchor) for the new
      corpus; = title for the old corpus (no anchor exists pre-restructure —
      title is the closest intrinsic public probe; CROSS-CORPUS comparison is
      therefore QUALIFIED, within-corpus cross-encoder comparison is clean).
      Metrics: nDCG@10, recall@{1,5,10}. Plus per-encoder secret<->anchor
      separability on corpus_v2 (reusing the D2 measure).

Zero API. No pipeline result file is modified; new outputs under eval/rerun_phase2/.
"""

import gc
import json
import math
import os
import statistics
import sys
from datetime import date

import numpy as np
import faiss
from scipy import stats as sps

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, REPO_ROOT)

from eval.run_statistical_eval import evaluate_b2  # 0-API gate, reused unmodified
from scripts.run_rag_with_audit import load_config

import sentence_transformers
from sentence_transformers import SentenceTransformer

CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = ["corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
HN_V2 = os.path.join(CORPUS_DIR, "hard_negatives_v2.jsonl")
BENIGN = os.path.join(REPO_ROOT, "data", "benchmark", "normal_prompts.jsonl")
HN_OLD = os.path.join(REPO_ROOT, "data", "benchmark", "hard_negatives.jsonl")
OLD_SECRETS = os.path.join(REPO_ROOT, "data", "secrets", "secrets_v2.jsonl")

ENCODERS = [
    {"key": "minilm", "name": "sentence-transformers/all-MiniLM-L6-v2", "bge": False},
    {"key": "mpnet", "name": "sentence-transformers/all-mpnet-base-v2", "bge": False},
    {"key": "bge_large", "name": "BAAI/bge-large-en-v1.5", "bge": True},
    {"key": "finlang", "name": "FinLang/finance-embeddings-investopedia", "bge": False},
]
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
DATE = date.today().isoformat().replace("-", "_")


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def load_corpus_v2():
    rows = []
    for fn in CORPUS_FILES:
        rows += load_jsonl(os.path.join(CORPUS_DIR, fn))
    return rows


# ===========================================================================
# E — FPR retest
# ===========================================================================
def build_index(secret_dicts, embed_model):
    texts = [d["text"] for d in secret_dicts]
    emb = embed_model.encode(texts, normalize_embeddings=True).astype("float32")
    idx = faiss.IndexFlatIP(emb.shape[1])
    idx.add(emb)
    meta = [{"_id": d["_id"], "title": d.get("title", ""), "text": d["text"],
             "category": d.get("category", "secret"),
             "source_type": d.get("source_type", "internal")} for d in secret_dicts]
    return idx, meta


def run_fpr(cfg):
    secrets = load_corpus_v2()
    hn = load_jsonl(HN_V2)
    anchors = [s["anchor_text"] for s in secrets]
    decoys = [h["text"] for h in hn if h["kind"] == "decoy"]
    benign = [r["query"] for r in load_jsonl(BENIGN)]
    hn_old = [r["query"] for r in load_jsonl(HN_OLD)]
    assert len(benign) == 100 and len(hn_old) == 65 and len(anchors) == 90 and len(decoys) == 37

    emb_name = cfg["embedding"]["model_name"]
    embed_model = SentenceTransformer(emb_name)

    # corpus_v2 index (primary) + old index (for McNemar)
    v2_dicts = [{"_id": s["id"], "title": "", "text": s["secret_text"]} for s in secrets]
    old_dicts = [{"_id": d["_id"], "title": d.get("title", ""), "text": d["text"]}
                 for d in load_jsonl(OLD_SECRETS)]
    idx_v2, meta_v2 = build_index(v2_dicts, embed_model)
    idx_old, meta_old = build_index(old_dicts, embed_model)

    groups = {"benign_100": benign, "hard_neg_old_65": hn_old,
              "anchor_v2_90": anchors, "decoy_v2_37": decoys}

    def block_rates(idx, meta):
        out = {}
        per_prompt = {}
        for g, qs in groups.items():
            flags = [evaluate_b2(q, cfg, embed_model, idx, meta) for q in qs]
            out[g] = {"n": len(qs), "blocked": int(sum(flags)),
                      "fpr": sum(flags) / len(qs)}
            per_prompt[g] = flags
        return out, per_prompt

    v2_rates, v2_flags = block_rates(idx_v2, meta_v2)
    old_rates, old_flags = block_rates(idx_old, meta_old)

    # main FPR = benign + hard_neg + anchor (benign-by-design); decoy separate
    main_groups = ["benign_100", "hard_neg_old_65", "anchor_v2_90"]
    def pooled(rates, gs):
        n = sum(rates[g]["n"] for g in gs)
        b = sum(rates[g]["blocked"] for g in gs)
        return {"n": n, "blocked": b, "fpr": b / n}
    v2_main = pooled(v2_rates, main_groups)

    # McNemar (old vs corpus_v2 index) on benign + hard_neg (exist for both)
    paired_groups = ["benign_100", "hard_neg_old_65"]
    b = c = 0  # b: old-blocked & new-not ; c: new-blocked & old-not
    for g in paired_groups:
        for o, n in zip(old_flags[g], v2_flags[g]):
            if o and not n:
                b += 1
            elif n and not o:
                c += 1
    nd = b + c
    if nd == 0:
        mcnemar = {"b": b, "c": c, "discordant": 0, "p_value": 1.0,
                   "method": "no discordant pairs", "statistic": 0.0}
    elif nd < 25:
        p = float(sps.binomtest(b, nd, 0.5).pvalue)
        mcnemar = {"b": b, "c": c, "discordant": nd, "p_value": p,
                   "method": "exact binomial (b+c<25)"}
    else:
        stat = (abs(b - c) - 1) ** 2 / nd
        p = float(sps.chi2.sf(stat, 1))
        mcnemar = {"b": b, "c": c, "discordant": nd, "p_value": p,
                   "statistic": stat, "method": "chi-square w/ continuity correction"}

    del embed_model
    gc.collect()

    return {
        "encoder": emb_name,
        "note_determinism": "Gate is per-query deterministic (rule_gate + embedding "
                            "precheck + leakage_scan); FPR std across seeds = 0 by "
                            "construction, so a single deterministic pass is reported "
                            "(mean = value, std = 0.0).",
        "note_tpr": "TPR is N/A for this benign-only input (no attacks); attack "
                    "retargeting + TPR are Tier-1.",
        "corpus_v2_index": {"per_group": v2_rates, "main_fpr_benign+hardneg+anchor": v2_main,
                            "decoy_separate": v2_rates["decoy_v2_37"]},
        "old_index": {"per_group": old_rates},
        "mcnemar_old_vs_v2_on_benign+hardneg": mcnemar,
    }


# ===========================================================================
# D§3.4 — retrieval-utility + separability
# ===========================================================================
def ndcg_recall(probe_emb, kb_emb):
    """1 relevant doc per probe (own index). Returns nDCG@10 + recall@{1,5,10}."""
    sims = probe_emb @ kb_emb.T  # (n, n)
    n = sims.shape[0]
    ranks = []
    for i in range(n):
        own = sims[i, i]
        ranks.append(int(np.sum(sims[i] > own)) + 1)  # 1-indexed rank of own secret
    ranks = np.asarray(ranks)
    ndcg10 = float(np.mean([(1.0 / math.log2(r + 1)) if r <= 10 else 0.0 for r in ranks]))
    rec = {k: float(np.mean(ranks <= k)) for k in (1, 5, 10)}
    return {"ndcg@10": ndcg10, "recall@1": rec[1], "recall@5": rec[5],
            "recall@10": rec[10], "mean_rank": float(np.mean(ranks)),
            "median_rank": float(np.median(ranks))}


def describe(vals):
    s = sorted(vals)
    return {"n": len(s), "mean": float(statistics.fmean(s)), "median": float(statistics.median(s)),
            "min": float(s[0]), "max": float(s[-1])}


def run_d34():
    v2 = load_corpus_v2()
    old = load_jsonl(OLD_SECRETS)
    corpora = {
        "corpus_v2": {"secrets": [s["secret_text"] for s in v2],
                      "probe": [s["anchor_text"] for s in v2],
                      "probe_kind": "anchor_text (designed public anchor)"},
        "old_secrets_v2": {"secrets": [d["text"] for d in old],
                           "probe": [d.get("title", "") for d in old],
                           "probe_kind": "title (closest intrinsic public probe; no anchor pre-restructure)"},
    }
    grid = {}
    separability = {}
    for enc in ENCODERS:
        model = SentenceTransformer(enc["name"])

        def E(texts, is_query=False):
            pre = BGE_QUERY_PREFIX if (enc["bge"] and is_query) else ""
            return model.encode([pre + t for t in texts], normalize_embeddings=True,
                                convert_to_numpy=True, batch_size=32)

        grid[enc["key"]] = {}
        for cname, cd in corpora.items():
            kb = E(cd["secrets"], is_query=False)
            probe = E(cd["probe"], is_query=True)
            ru = ndcg_recall(probe, kb)
            ru["probe_kind"] = cd["probe_kind"]
            grid[enc["key"]][cname] = ru

        # separability (corpus_v2 only — needs anchors; D2 measure, symmetric/no-prefix)
        sec = E([s["secret_text"] for s in v2], is_query=False)
        anc = E([s["anchor_text"] for s in v2], is_query=False)
        own = [float(np.dot(sec[i], anc[i])) for i in range(len(v2))]
        sim_sa = sec @ anc.T
        rank_viol = 0
        for i in range(len(v2)):
            if int(np.sum(sim_sa[i] > sim_sa[i, i])) + 1 != 1:
                rank_viol += 1
        separability[enc["key"]] = {
            "secret_vs_own_anchor_cosine": describe(own),
            "cross_pair_rank_violations": rank_viol,
            "n": len(v2),
        }
        print(f"[D3.4] {enc['key']}: v2 nDCG@10={grid[enc['key']]['corpus_v2']['ndcg@10']:.4f} "
              f"R@1={grid[enc['key']]['corpus_v2']['recall@1']:.3f} | "
              f"old nDCG@10={grid[enc['key']]['old_secrets_v2']['ndcg@10']:.4f}; "
              f"sep own-cos median={separability[enc['key']]['secret_vs_own_anchor_cosine']['median']:.4f}")
        del model
        gc.collect()
        try:
            import torch
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except Exception:
            pass

    return {"encoders": [e["key"] for e in ENCODERS], "grid": grid, "separability": separability}


# ===========================================================================
def write_fpr_report(out_dir, res):
    L = ["# Tier-0 Rerun — E. FPR Retest (gate-level, ZERO API)", "",
         f"Encoder (gate): `{res['encoder']}`. {res['note_determinism']}", "",
         f"_{res['note_tpr']}_", "",
         "## Per-group block rate (corpus_v2 secret index; block = false positive)", "",
         "| group | n | blocked | FPR |", "|-------|--:|--------:|----:|"]
    for g, d in res["corpus_v2_index"]["per_group"].items():
        tag = "  ← DECOY (separate, not in main FPR)" if g.startswith("decoy") else ""
        L.append(f"| {g} | {d['n']} | {d['blocked']} | {d['fpr']:.4f} |{tag}")
    m = res["corpus_v2_index"]["main_fpr_benign+hardneg+anchor"]
    L += ["", f"**Main FPR (benign + hard-neg + anchor, pooled): {m['blocked']}/{m['n']} = "
          f"{m['fpr']:.4f}** (mean; std=0.0, deterministic).",
          f"**Decoy stress (separate): {res['corpus_v2_index']['decoy_separate']['blocked']}/"
          f"{res['corpus_v2_index']['decoy_separate']['n']} = "
          f"{res['corpus_v2_index']['decoy_separate']['fpr']:.4f}.**", "",
          "## Old index (secrets_v2) — for the McNemar comparison", "",
          "| group | n | blocked | FPR |", "|-------|--:|--------:|----:|"]
    for g, d in res["old_index"]["per_group"].items():
        L.append(f"| {g} | {d['n']} | {d['blocked']} | {d['fpr']:.4f} |")
    mc = res["mcnemar_old_vs_v2_on_benign+hardneg"]
    L += ["", "## McNemar — old index vs corpus_v2 index (benign + hard-neg, paired)", "",
          f"- discordant: b(old-block, new-pass)={mc['b']}, c(new-block, old-pass)={mc['c']} "
          f"(total {mc['discordant']})",
          f"- method: {mc['method']}; **p = {mc['p_value']:.4f}**",
          "- interpretation: tests whether rebuilding the secret index on corpus_v2 "
          "significantly changes the benign block decision (FPR).", ""]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(L))
    json.dump(res, open(os.path.join(out_dir, "results.json"), "w"), indent=2)


def write_d34_report(out_dir, res):
    keys = res["encoders"]
    L = ["# Tier-0 Rerun — D§3.4: 8-cell Embedding + Retrieval-Utility (OFFLINE; ZERO API)", "",
         "Per-cell leakage (needs LLM) is NOT run here — deferred to Tier-2.", "",
         "## Relevance protocol (ratified)", "",
         "- 1 relevant doc per probe: each corpus's held-out PUBLIC PROBE -> its own secret. "
         "Decoupled from the attack set.",
         "- corpus_v2 probe = `anchor_text` (designed public anchor).",
         "- old secrets_v2 probe = `title` (closest intrinsic public probe; no anchor exists "
         "pre-restructure). **Cross-corpus comparison is QUALIFIED (different probe types); "
         "within-corpus cross-encoder comparison is clean.**",
         "- bge_large uses its query instruction prefix on the probe; KB raw. Others: no prefix.", "",
         "## 8-cell retrieval-utility matrix", "",
         "| encoder | corpus | probe | nDCG@10 | R@1 | R@5 | R@10 | mean rank |",
         "|---------|--------|-------|--------:|----:|----:|-----:|----------:|"]
    for k in keys:
        for cname in ("corpus_v2", "old_secrets_v2"):
            c = res["grid"][k][cname]
            probe = "anchor" if cname == "corpus_v2" else "title"
            L.append(f"| {k} | {cname} | {probe} | {c['ndcg@10']:.4f} | {c['recall@1']:.3f} | "
                     f"{c['recall@5']:.3f} | {c['recall@10']:.3f} | {c['mean_rank']:.2f} |")
    L += ["", "## Per-encoder secret<->anchor separability (corpus_v2; D2 measure)", "",
          "| encoder | own-anchor cosine (mean/median/min/max) | cross-pair rank!=1 |",
          "|---------|------------------------------------------|-------------------:|"]
    for k in keys:
        s = res["separability"][k]["secret_vs_own_anchor_cosine"]
        L.append(f"| {k} | {s['mean']:.4f} / {s['median']:.4f} / {s['min']:.4f} / {s['max']:.4f} | "
                 f"{res['separability'][k]['cross_pair_rank_violations']} |")
    L += ["", "_Note: retrieval-utility (probe->secret) and separability (secret<->anchor) are the "
          "OFFLINE deliverables for §3.4; they let Tier-2 argue any per-cell leakage increase is "
          "not explained by retrieval-utility differences._", ""]
    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(L))
    json.dump(res, open(os.path.join(out_dir, "results.json"), "w"), indent=2)


def main():
    cfg = load_config(os.path.join(REPO_ROOT, "config.yaml"))
    base = os.path.join(REPO_ROOT, "eval", "rerun_phase2")

    print("=== E. FPR retest ===")
    fpr = run_fpr(cfg)
    fpr_dir = os.path.join(base, f"fpr_retest_{DATE}")
    os.makedirs(fpr_dir, exist_ok=True)
    write_fpr_report(fpr_dir, fpr)
    m = fpr["corpus_v2_index"]["main_fpr_benign+hardneg+anchor"]
    print(f"[E] main FPR (benign+hardneg+anchor) = {m['blocked']}/{m['n']} = {m['fpr']:.4f}; "
          f"decoy = {fpr['corpus_v2_index']['decoy_separate']['fpr']:.4f}; "
          f"McNemar p={fpr['mcnemar_old_vs_v2_on_benign+hardneg']['p_value']:.4f}")

    print("=== D§3.4. retrieval-utility ===")
    d34 = run_d34()
    d34_dir = os.path.join(base, f"d34_retrieval_utility_{DATE}")
    os.makedirs(d34_dir, exist_ok=True)
    write_d34_report(d34_dir, d34)

    print(f"wrote: {fpr_dir}/report.md")
    print(f"wrote: {d34_dir}/report.md")


if __name__ == "__main__":
    main()
