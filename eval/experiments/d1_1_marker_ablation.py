#!/usr/bin/env python3
"""
eval/experiments/d1_1_marker_ablation.py — D1.1 marker-style ablation arm.

Goal: decompose the D1 positive/negative separability into a STYLE component
(institutional-voice surface markers) and a CONTENT component (proprietary
semantics). Method: mechanically neutralize the institutional-voice markers in
the 90 atomic_text positives with a DETERMINISTIC rule table, then re-run the
style-sensitive mechanisms (M2 n-gram, M3 embedding NN, M5 marker-vocab) on the
neutralized positives against the UNCHANGED negatives/KB. M1 (exact-literal) and
M4 (numeric-density) are marker-independent and are SKIPPED (noted in report).

Numbers and the syntactic skeleton are left untouched; only institutional-voice
subject/possessive marker tokens are replaced/removed.

Derived experiment — the frozen corpus_v2 files are READ-ONLY and untouched; the
neutralized variants are written only to this experiment's output dir.

=====================  DETERMINISTIC NEUTRALIZATION RULE TABLE  =================
Applied IN ORDER (regex; IGNORECASE where marked). Each rule removes/replaces an
institutional-voice marker with a neutral third-person subject ("the strategy")
or a determiner, or deletes an adjectival marker. The M5 vocabulary
{our, internal, desk, proprietary, production, firm, ops} is fully eliminated.

  R01  r"\bour desk's\b"            -> "a"            (possessive desk -> determiner)
  R02  r"\bthe ops desk\b"          -> "the strategy" (ops+desk compound subject)
  R03  r"\bops desk\b"              -> "strategy"
  R04  r"\b(?:our|the)\s+desk head\b" -> "the head"   (role; drop 'desk')
  R05  r"\bOur desk\b"              -> "The strategy"  (sentence-initial subject)
  R06  r"\bour desk\b"              -> "the strategy"
  R07  r"\bThe desk\b"              -> "The strategy"
  R08  r"\bthe desk\b"              -> "the strategy"
  R09  r"\bdesk\b"  (IGNORECASE)    -> "strategy"      (any standalone remainder)
  R10  r"\b[Ii]nternal\s+"          -> ""              (delete adjectival marker)
  R11  r"\b[Ii]nternal\b"           -> ""              (bare remainder)
  R12  r"\b[Pp]roprietary\s+"       -> ""              (adjectival marker; 0 in data)
  R13  r"\b[Pp]roduction\s+"        -> ""              (adjectival marker; 0 in data)
  R14  r"\bThe firm\b" / r"\bthe firm\b" -> "The strategy"/"the strategy"
  R15  r"\bfirm\b"  (IGNORECASE)    -> "strategy"
  R16  r"\bops\b"   (IGNORECASE)    -> "operations"    (safety; should not fire post-R02/03)
  R17  r"\bOur\b" -> "The" ; r"\bour\b" -> "the"        (generic possessive, after compounds)
  R18  r"\bWe\b" -> "The strategy" ; r"\bwe\b" -> "the strategy"
       NOTE: true passivization is not mechanically reliable; a neutral third-person
       subject is substituted instead. Verb agreement is intentionally left as-is
       (e.g. "We quote" -> "The strategy quote"); this is a documented mechanical
       artifact — the embedding/n-gram mechanisms are robust to minor agreement
       slips, and no numeric/skeletal token is altered.
  CLEANUP: collapse whitespace, drop space-before-punctuation, recapitalize the
           first character of the sentence.
================================================================================
"""

import json
import os
import platform
import re
import statistics
from collections import OrderedDict
from datetime import date

import numpy as np
import yaml
import sentence_transformers
from sentence_transformers import SentenceTransformer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
CONFIG_PATH = os.path.join(REPO_ROOT, "config.yaml")
CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = ["corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
HN_FILE = os.path.join(CORPUS_DIR, "hard_negatives_v2.jsonl")

VOCAB_WORDS = ["our", "internal", "desk", "proprietary", "production", "firm", "ops"]
FPR_TARGETS = [0.0, 0.01, 0.05]

_PUNCT = re.compile(r"[^\w\s]")
_WS = re.compile(r"\s+")
_DIGIT = re.compile(r"\d")

# ordered rules: (name, compiled_pattern, replacement)
_RULES = [
    ("R01", re.compile(r"\bour desk's\b", re.I), "a"),
    ("R02", re.compile(r"\bthe ops desk\b", re.I), "the strategy"),
    ("R03", re.compile(r"\bops desk\b", re.I), "strategy"),
    ("R04", re.compile(r"\b(?:our|the)\s+desk head\b", re.I), "the head"),
    ("R05", re.compile(r"\bOur desk\b"), "The strategy"),
    ("R06", re.compile(r"\bour desk\b"), "the strategy"),
    ("R07", re.compile(r"\bThe desk\b"), "The strategy"),
    ("R08", re.compile(r"\bthe desk\b"), "the strategy"),
    ("R09", re.compile(r"\bdesk\b", re.I), "strategy"),
    ("R10", re.compile(r"\b[Ii]nternal\s+"), ""),
    ("R11", re.compile(r"\b[Ii]nternal\b"), ""),
    ("R12", re.compile(r"\b[Pp]roprietary\s+"), ""),
    ("R13", re.compile(r"\b[Pp]roduction\s+"), ""),
    ("R14a", re.compile(r"\bThe firm\b"), "The strategy"),
    ("R14b", re.compile(r"\bthe firm\b"), "the strategy"),
    ("R15", re.compile(r"\bfirm\b", re.I), "strategy"),
    ("R16", re.compile(r"\bops\b", re.I), "operations"),
    ("R17a", re.compile(r"\bOur\b"), "The"),
    ("R17b", re.compile(r"\bour\b"), "the"),
    ("R18a", re.compile(r"\bWe\b"), "The strategy"),
    ("R18b", re.compile(r"\bwe\b"), "the strategy"),
]


def neutralize(text):
    """Apply the ordered rule table. Returns (new_text, fired_rule_names)."""
    s = text
    fired = []
    for name, pat, rep in _RULES:
        s2 = pat.sub(rep, s)
        if s2 != s:
            fired.append(name)
            s = s2
    # cleanup
    s = _WS.sub(" ", s).strip()
    s = re.sub(r"\s+([,.;:%])", r"\1", s)
    if s:
        s = s[0].upper() + s[1:]
    return s, fired


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def norm_tokens(text):
    return _WS.sub(" ", _PUNCT.sub(" ", text.lower())).strip().split()


def four_grams(tokens):
    return set(tuple(tokens[i:i + 4]) for i in range(len(tokens) - 3))


def has_word(text, w):
    return re.search(rf"\b{re.escape(w)}\b", text.lower()) is not None


def auc_mw(pos, neg):
    if not pos or not neg:
        return None
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    s = 0.0
    for q in neg:
        s += np.sum(pos > q) + 0.5 * np.sum(pos == q)
    return float(s / (len(pos) * len(neg)))


def tpr_at_fpr(pos, neg, target):
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    thr = sorted(set(pos.tolist() + neg.tolist()), reverse=True)
    best = (None, 0.0, 0.0)
    for t in thr:
        fpr = float(np.mean(neg >= t)); tpr = float(np.mean(pos >= t))
        if fpr <= target + 1e-9 and tpr >= best[2]:
            best = (float(t), fpr, tpr)
    return best


def rate_ge(scores, t):
    if t is None or not scores:
        return None
    return float(np.mean(np.asarray(scores, float) >= t))


def main():
    cfg = yaml.safe_load(open(CONFIG_PATH))
    model_name = cfg["embedding"]["model_name"]

    secrets = []
    for fn in CORPUS_FILES:
        secrets += load_jsonl(os.path.join(CORPUS_DIR, fn))
    hard = load_jsonl(HN_FILE)
    assert len(secrets) == 90 and len(hard) == 127
    anchors = [h for h in hard if h["kind"] == "anchor"]
    decoys = [h for h in hard if h["kind"] == "decoy"]

    # neutralize positives
    pos_rows = []
    for s in secrets:
        orig = s["atomic_text"]
        neut, fired = neutralize(orig)
        pos_rows.append({
            "id": s["id"], "offset_type": s["offset_type"], "subset": s["subset"],
            "domain": s["domain"], "atomic_original": orig, "atomic_neutralized": neut,
            "rules_fired": fired,
            "m5_markers_before": sum(1 for w in VOCAB_WORDS if has_word(orig, w)),
            "m5_markers_after": sum(1 for w in VOCAB_WORDS if has_word(neut, w)),
        })
    residual = [r["id"] for r in pos_rows if r["m5_markers_after"] > 0]

    kb_texts = [s["secret_text"] for s in secrets]
    neg_texts = [h["text"] for h in anchors]
    dec_texts = [h["text"] for h in decoys]

    model = SentenceTransformer(model_name)
    def emb(ts):
        return model.encode(ts, normalize_embeddings=True, convert_to_numpy=True)
    kb_emb = emb(kb_texts)
    orig_emb = emb([r["atomic_original"] for r in pos_rows])
    neut_emb = emb([r["atomic_neutralized"] for r in pos_rows])
    neg_emb = emb(neg_texts)
    dec_emb = emb(dec_texts)
    kb_4 = [four_grams(norm_tokens(t)) for t in kb_texts]

    def m2(text):
        cg = four_grams(norm_tokens(text))
        if not cg:
            return 0.0
        best = 0.0
        for kg in kb_4:
            if kg:
                inter = len(cg & kg)
                if inter:
                    j = inter / len(cg | kg)
                    best = max(best, j)
        return best

    def m3_scores(E):
        return list(np.max(E @ kb_emb.T, axis=1))

    def m5(text):
        return float(sum(1 for w in VOCAB_WORDS if has_word(text, w)))

    scores = {
        "orig": {"M2": [m2(r["atomic_original"]) for r in pos_rows],
                 "M3": m3_scores(orig_emb),
                 "M5": [m5(r["atomic_original"]) for r in pos_rows]},
        "neut": {"M2": [m2(r["atomic_neutralized"]) for r in pos_rows],
                 "M3": m3_scores(neut_emb),
                 "M5": [m5(r["atomic_neutralized"]) for r in pos_rows]},
    }
    neg_scores = {"M2": [m2(t) for t in neg_texts], "M3": m3_scores(neg_emb),
                  "M5": [m5(t) for t in neg_texts]}
    dec_scores = {"M2": [m2(t) for t in dec_texts], "M3": m3_scores(dec_emb),
                  "M5": [m5(t) for t in dec_texts]}

    MECHS = ["M2", "M3", "M5"]
    out = {}
    for m in MECHS:
        row = {"auc_orig": auc_mw(scores["orig"][m], neg_scores[m]),
               "auc_neut": auc_mw(scores["neut"][m], neg_scores[m]),
               "ops_orig": [], "ops_neut": []}
        for tag, sc in (("ops_orig", scores["orig"][m]), ("ops_neut", scores["neut"][m])):
            for tgt in FPR_TARGETS:
                t, fpr, tpr = tpr_at_fpr(sc, neg_scores[m], tgt)
                row[tag].append({"target_fpr": tgt, "threshold": t, "fpr": fpr, "tpr": tpr,
                                 "decoy_fp": rate_ge(dec_scores[m], t)})
        row["delta_auc"] = (row["auc_orig"] - row["auc_neut"]) if (row["auc_orig"] is not None and row["auc_neut"] is not None) else None
        out[m] = row

    # pre-registration verdicts
    prereg = {
        "a_M5_collapse": {"auc_orig": out["M5"]["auc_orig"], "auc_neut": out["M5"]["auc_neut"]},
        "b_M3_decompose": {
            "auc_orig": out["M3"]["auc_orig"], "auc_neut": out["M3"]["auc_neut"],
            "style_contribution_delta": out["M3"]["delta_auc"],
            "content_contribution_above_0.5": (out["M3"]["auc_neut"] - 0.5) if out["M3"]["auc_neut"] is not None else None,
        },
        "c_M2_small_drop": {"auc_orig": out["M2"]["auc_orig"], "auc_neut": out["M2"]["auc_neut"],
                            "delta": out["M2"]["delta_auc"]},
    }

    meta = {
        "model_name": model_name, "st_version": sentence_transformers.__version__,
        "python": platform.python_version(), "platform": platform.platform(),
        "run_date": date.today().isoformat(),
        "n_pos": len(pos_rows), "n_neg_main": len(neg_texts), "n_neg_stress": len(dec_texts),
        "n_kb": len(kb_texts),
        "n_pos_with_marker_before": sum(1 for r in pos_rows if r["m5_markers_before"] > 0),
        "residual_marker_ids": residual,
    }

    out_dir = os.path.join(HERE, f"d1_1_marker_ablation_{date.today().isoformat().replace('-', '_')}")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "atomic_neutralized.jsonl"), "w") as f:
        for r in pos_rows:
            f.write(json.dumps(r) + "\n")

    json.dump({"meta": meta, "mechanisms": out, "prereg": prereg},
              open(os.path.join(out_dir, "results.json"), "w"), indent=2)

    render_report(out_dir, meta, out, prereg, pos_rows, MECHS)

    print(f"[D1.1] positives with marker (before): {meta['n_pos_with_marker_before']}/90; "
          f"residual after: {residual or 'none'}")
    for m in MECHS:
        print(f"[D1.1] {m}: AUC orig={out[m]['auc_orig']:.4f} -> neut={out[m]['auc_neut']:.4f} "
              f"(Δ={out[m]['delta_auc']:+.4f})")
    print(f"wrote: {os.path.join(out_dir, 'report.md')}")
    print(f"wrote: {os.path.join(out_dir, 'results.json')}")
    print(f"wrote: {os.path.join(out_dir, 'atomic_neutralized.jsonl')}")


def render_report(out_dir, meta, out, prereg, pos_rows, MECHS):
    L = []
    L.append("# D1.1 — Marker-Style Ablation (decompose style vs content AUC)")
    L.append("")
    L.append("Derived experiment. Frozen corpus_v2 untouched; neutralized positives written "
             "only to this dir. Mechanically neutralizes institutional-voice markers in the 90 "
             "atomic positives, then re-runs the style-sensitive mechanisms vs UNCHANGED "
             "negatives/KB. M1 (exact-literal) and M4 (numeric-density) are marker-independent "
             "and SKIPPED.")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append(f"- Encoder: `{meta['model_name']}` (sentence-transformers `{meta['st_version']}`)")
    L.append(f"- Python `{meta['python']}` | {meta['platform']} | run {meta['run_date']}")
    L.append(f"- positives={meta['n_pos']} (neutralized), neg(main)={meta['n_neg_main']} anchor, "
             f"neg(stress)={meta['n_neg_stress']} decoy, KB={meta['n_kb']}.")
    L.append(f"- atomic positives carrying >=1 marker before neutralization: "
             f"{meta['n_pos_with_marker_before']}/90.")
    L.append(f"- residual markers after neutralization: {meta['residual_marker_ids'] or 'NONE (M5 vocab fully eliminated)'}.")
    L.append("- Rule table: see the module docstring (R01-R18, deterministic, ordered).")
    L.append("")
    L.append("## Original vs neutralized — AUC (main negatives)")
    L.append("")
    L.append("| mechanism | AUC original | AUC neutralized | Δ (style contribution) |")
    L.append("|-----------|-------------:|----------------:|-----------------------:|")
    for m in MECHS:
        r = out[m]
        L.append(f"| {m} | {r['auc_orig']:.4f} | {r['auc_neut']:.4f} | {r['delta_auc']:+.4f} |")
    L.append("")
    L.append("| skipped | reason |")
    L.append("|---------|--------|")
    L.append("| M1 exact-literal | marker-independent (matches numeric/parameter literals; "
             "neutralization touches no literals) |")
    L.append("| M4 numeric-density | marker-independent (counts numeric tokens; unchanged by neutralization) |")
    L.append("")
    L.append("## Operating points + decoy FP (original vs neutralized)")
    L.append("")
    for m in MECHS:
        L.append(f"### {m}")
        L.append("")
        L.append("| variant | target FPR | threshold | actual FPR | TPR | decoy FP (stress) |")
        L.append("|---------|-----------:|----------:|-----------:|----:|------------------:|")
        for variant, key in (("original", "ops_orig"), ("neutralized", "ops_neut")):
            for o in out[m][key]:
                th = "n/a" if o["threshold"] is None else f"{o['threshold']:.4f}"
                dfp = "n/a" if o["decoy_fp"] is None else f"{o['decoy_fp']:.4f}"
                L.append(f"| {variant} | {o['target_fpr']:.0%} | {th} | {o['fpr']:.4f} | {o['tpr']:.4f} | {dfp} |")
        L.append("")

    L.append("## Pre-registration reconciliation")
    L.append("")
    m5o, m5n = prereg["a_M5_collapse"]["auc_orig"], prereg["a_M5_collapse"]["auc_neut"]
    L.append("### (a) M5 (marker-vocab) AUC collapses to ~0.5")
    L.append("")
    L.append(f"- M5 AUC: {m5o:.4f} -> {m5n:.4f}. "
             f"**VERDICT: {'HELD' if abs(m5n-0.5)<0.03 else 'CHECK'}** "
             "(markers eliminated -> mechanism has no signal left; residual offset only from any "
             "marker remaining in NEGATIVES, which were not neutralized).")
    L.append("")
    b = prereg["b_M3_decompose"]
    L.append("### (b) M3 (embedding) AUC drops; Δ = style, residual-above-0.5 = content")
    L.append("")
    L.append(f"- M3 AUC: {b['auc_orig']:.4f} -> {b['auc_neut']:.4f}.")
    L.append(f"- **style contribution Δ = {b['style_contribution_delta']:+.4f}**.")
    L.append(f"- **content contribution (neutralized AUC - 0.5) = {b['content_contribution_above_0.5']:+.4f}** "
             "(the key reading: separability that survives marker removal = proprietary semantic content).")
    L.append("")
    c = prereg["c_M2_small_drop"]
    L.append("### (c) M2 (n-gram) drops slightly")
    L.append("")
    L.append(f"- M2 AUC: {c['auc_orig']:.4f} -> {c['auc_neut']:.4f} (Δ={c['delta']:+.4f}). "
             f"**VERDICT: {'HELD (small drop)' if (c['delta'] is not None and 0 <= c['delta'] < 0.10) else 'CHECK'}**.")
    L.append("")
    L.append("## Sample transforms (10)")
    L.append("")
    samples = [r for r in pos_rows if r["rules_fired"]][:10]
    for r in samples:
        L.append(f"- **{r['id']}** (rules {','.join(r['rules_fired'])}):")
        L.append(f"    - orig: {r['atomic_original']}")
        L.append(f"    - neut: {r['atomic_neutralized']}")
    L.append("")

    open(os.path.join(out_dir, "report.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
