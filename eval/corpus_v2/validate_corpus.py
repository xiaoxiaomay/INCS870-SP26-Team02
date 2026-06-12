#!/usr/bin/env python3
"""
eval/corpus_v2/validate_corpus.py — corpus_v2 validation harness (checks 1-5).

Self-contained validator for the restructured "public anchor + proprietary
offset" secret corpus (corpus_v2). UNRELATED to scripts/validate_hard_negatives.py
(the Phase 1.E V1a/V1b/V5b validator); that file is NOT touched or extended.

Design principle: every check emits MEASUREMENTS and a list of "items flagged
for manual review" ONLY. No automatic pass/fail. All thresholds quoted in the
report are advisory reference lines that a human adjudicates in chat.

Interface (batch-reusable for later corpus batches):
    python validate_corpus.py \
        --corpus corpus_batch_seed.jsonl corpus_batch_01.jsonl \
        --hard-negatives hard_negatives_v2.jsonl \
        --out validation_reports/batch_01_<date>

Embedding: config.yaml encoder (all-MiniLM-L6-v2). normalize_embeddings=True so
inner product == cosine. Fully offline, zero API cost.

Corpus row schema:  id, domain, offset_type, subset, marker_style, tags,
                    anchor_source, anchor_text, atomic_text, secret_text
Hard-neg row schema: id, kind ("anchor"|"decoy"), linked_secret_id,
                     marker_style, text
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date

import numpy as np
import yaml
import sentence_transformers
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
CONFIG_PATH = os.path.join(REPO_ROOT, "config.yaml")

# Check-4 legacy comparison corpora: (label, repo-relative path, text field).
# Resolved at runtime; any missing file -> that sub-check SKIPPED (non-blocking).
LEGACY_SETS = [
    ("secrets.jsonl",        "data/secrets/secrets.jsonl",            "text"),
    ("attack_271",           "data/attack_prompts_expanded.jsonl",    "query"),
    ("normal_100",           "data/benchmark/normal_prompts.jsonl",   "query"),
    ("hard_neg_65",          "data/benchmark/hard_negatives.jsonl",   "query"),
]

# Pre-registered decoy<->anchor focus pairs (check 4(ii)); reported regardless
# of whether they exceed 0.95. Cumulative across batches; pairs whose ids are
# absent from the current hard-neg set are reported as "id not found".
PREREG_PAIRS = [
    # batch_01 focus pairs (re-tested every batch)
    ("d3_04", "hn_p0_02"),
    ("d3_02", "hn_p0_01"),
    ("d3_06", "hn_p0_13"),
    ("d2_02", "hn_p0_11"),
    ("d1_05", "hn_p0_03"),
    # batch_02 focus pairs
    ("d2_10", "hn_b2_39"),
    ("d3_08", "hn_p0_03"),
    ("d3_09", "hn_b2_42"),
    # batch_03 focus pairs
    ("d2_16", "hn_b1_25"),  # Basel capital vs LCR (lexically adjacent)
]

# Pre-registered decoy<->decoy focus pairs (check 4(iv)); reported regardless of
# the 0.95 line. (batch_03: d2_15 / d2_13 both Treasury bills/notes.)
PREREG_DECOY_DECOY = [
    ("d2_15", "d2_13"),
]

# Check-5 template-collapse trend reference points (frozen prior-batch values).
# avg_members_per_domain = n_secrets / n_domains at that batch (16 domains throughout).
CHECK5_TREND_REFS = [
    {"label": "baseline batch_01 (frozen)", "cross_domain_nn_share": 0.667,
     "top1_secret_cosine": 0.6028, "avg_members_per_domain": 1.875},
    {"label": "batch_02", "cross_domain_nn_share": 0.622,
     "top1_secret_cosine": 0.6028, "avg_members_per_domain": 2.8125},
    {"label": "batch_03", "cross_domain_nn_share": 0.583,
     "top1_secret_cosine": 0.6220, "avg_members_per_domain": 3.75},
]

# Check-5 monitor v2 (chat-ratified): top-1 secret-secret cosine is the PRIMARY
# criterion; cross-domain share is demoted to purely descriptive. Annotate only.
CHECK5_TOP1_WARNING = 0.70
CHECK5_TOP1_STOP = 0.75

# Check-3 atomic-table annotations (id -> note).
ATOMIC_ANNOTATIONS = {
    "b2_36": "Type B exception (PI ruling, batch_03; pattern-test datapoint)",
}

# Check-2(b3) advisory stop-line for the decoy numeric-token mean (report only).
B3_DECOY_STOP_LINE = 3.5

# Check-1 quota reference lines (advisory; deviations listed, never auto-failed).
QUOTA_REF = {
    "type_b_share": 0.20,         # Type B ~20%
    "boundary_share": 0.10,       # subset=boundary_test ~10%
    "policy_quota_share_max": 0.20,  # tags含 policy_quota <=20%
    "marker_single_max": 0.50,    # 无单一 marker_style >50%
}

# Check-2(b2) vocab heuristics (lowercase whole-word match).
VOCAB_WORDS = ["our", "internal", "desk", "proprietary", "production", "firm", "ops"]

NEAR_DUP_COS = 0.95
ANCHOR_CROSSTALK_COS = 0.80

# ---------------------------------------------------------------------------
# Gate (a) v3 — scale-robust atomic criteria.
# ---------------------------------------------------------------------------
# WHY v3: gate(a) v2 used absolute atomic-rank in its violation test (Type A:
# rank==1; Type B: rank<=3). That test is NON-STATIONARY in the anchor-pool size
# N: as N grows, an unchanged atomic's rank degrades purely from more anchors
# being present, so the violation set inflates with corpus size independent of
# any data change (batch_04 evidence: seed secrets p0_07/p0_08 — zero text change
# since batch_01 — newly flagged at N=75; p0_07 even had a healthy +0.103 delta).
# This tripped PI's pre-registered Type-B-cluster trigger (p0_08 + b2_36), whose
# ratified remedy is this v3 redefinition:
#   - Type A: PRIMARY criterion = delta>0 (stationary, pool-independent);
#     violation iff delta<=0. Attribution is DEMOTED to monitoring: an atomic
#     whose own-anchor rank exceeds ceil(0.10*N) goes on an attribution-watch
#     list (NOT a violation).
#   - Type B: anchor-mirroring still not expected; identity-preservation check
#     scales with the pool — violation iff rank > ceil(0.10*N). delta reported
#     only. (At N=90, ceil(0.10*90)=9; p0_08 rank 4 / b2_36 rank 5 regress to pass.)
GATE_A_ATTR_FRACTION = 0.10  # ceil(0.10*N_anchor) threshold for Type B / Type A watch

# v3 pre-registration (chat-ratified expectations for batch_05 reconciliation):
PREREG_V3_TYPE_A_BASE = {"b1_19", "b2_34", "b2_35", "b4_66", "b4_69"}  # plus b5 A with delta<=0
PREREG_V3_TYPE_B_REGRESS = {"p0_08", "b2_36"}  # expected to regress to PASS under v3

ATOMIC_GATE_NOTE = (
    "gate (a) v3 — scale-robust, offset_type-scoped (N = anchor-pool size). "
    "Type A — PRIMARY criterion delta>0; violation iff delta<=0 (stationary in N). "
    "Attribution demoted to monitoring: own-anchor rank > ceil(0.10*N) -> "
    "attribution-watch (NOT a violation). "
    "Type B — anchor-mirroring not expected; identity-preservation scales with the "
    "pool: violation iff rank > ceil(0.10*N); delta reported but not a criterion. "
    "Violations are flagged for manual review; magnitude judgment is left to the human."
)


def v3_atomic_status(offset_type, delta, atomic_rank, n_anchor):
    """gate(a) v3 classification. Returns (violation, attribution_watch, criterion)."""
    thr = math.ceil(GATE_A_ATTR_FRACTION * n_anchor)
    if offset_type == "B":
        return (atomic_rank > thr), False, f"Type B: rank<=ceil(0.10*N)={thr}"
    # Type A
    return (delta <= 0), (atomic_rank > thr), "Type A: delta>0 (attribution rank monitored)"


def v3_violation_ids(atomic_pairs, n_anchor):
    """Re-derive the v3 violation id-set from a list of atomic-pair dicts
    (each with offset_type, delta, atomic_rank). Used to evaluate a prior
    batch's stored pairs under the CURRENT v3 criterion for 'newly-crossed'."""
    out = set()
    for a in atomic_pairs:
        viol, _, _ = v3_atomic_status(a["offset_type"], a["delta"], a["atomic_rank"], n_anchor)
        if viol:
            out.add(a["id"])
    return out


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------
def load_jsonl(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_model_name():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["embedding"]["model_name"]


# ---------------------------------------------------------------------------
# Text normalization / tokenization
# ---------------------------------------------------------------------------
_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")
_DIGIT_RE = re.compile(r"\d")


def norm_tokens(text):
    """lowercase, strip punctuation to spaces, collapse whitespace, split."""
    t = _PUNCT_RE.sub(" ", text.lower())
    t = _WS_RE.sub(" ", t).strip()
    return t.split()


def ngrams(tokens, n):
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def numeric_token_count(text):
    """count whitespace-separated tokens containing >=1 digit (documented defn)."""
    return sum(1 for tok in text.split() if _DIGIT_RE.search(tok))


def has_word(text, word):
    return re.search(rf"\b{re.escape(word)}\b", text.lower()) is not None


# ---------------------------------------------------------------------------
# stats helpers
# ---------------------------------------------------------------------------
def pct(sorted_vals, q):
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def describe(vals):
    if not vals:
        return {"n": 0}
    s = sorted(vals)
    return {
        "n": len(s), "mean": statistics.fmean(s), "median": statistics.median(s),
        "p25": pct(s, 0.25), "p75": pct(s, 0.75), "min": s[0], "max": s[-1],
    }


def fmt_stats(d):
    if d.get("n", 0) == 0:
        return "(empty)"
    return (f"n={d['n']} mean={d['mean']:.4f} median={d['median']:.4f} "
            f"p25={d['p25']:.4f} p75={d['p75']:.4f} min={d['min']:.4f} max={d['max']:.4f}")


# ===========================================================================
# CHECK 1 — quota & coverage
# ===========================================================================
def check1_quota(secrets):
    n = len(secrets)
    dims = {}
    for dim in ("domain", "offset_type", "subset", "marker_style"):
        c = Counter(s.get(dim) for s in secrets)
        dims[dim] = {str(k): {"count": v, "share": v / n} for k, v in c.most_common()}

    policy_count = sum(1 for s in secrets if "policy_quota" in (s.get("tags") or []))
    type_b = sum(1 for s in secrets if s.get("offset_type") == "B")
    boundary = sum(1 for s in secrets if s.get("subset") == "boundary_test")
    marker_top = max((v["share"] for v in dims["marker_style"].values()), default=0.0)
    marker_top_val = max(dims["marker_style"].items(),
                         key=lambda kv: kv[1]["share"], default=(None, {"share": 0}))[0]

    deviations = []
    if abs(type_b / n - QUOTA_REF["type_b_share"]) > 1e-9 and round(type_b / n, 4) != QUOTA_REF["type_b_share"]:
        deviations.append(f"Type B share {type_b}/{n}={type_b/n:.3f} vs ref ~{QUOTA_REF['type_b_share']:.2f}")
    if round(boundary / n, 4) != QUOTA_REF["boundary_share"]:
        deviations.append(f"boundary_test share {boundary}/{n}={boundary/n:.3f} vs ref ~{QUOTA_REF['boundary_share']:.2f}")
    if policy_count / n > QUOTA_REF["policy_quota_share_max"]:
        deviations.append(f"policy_quota share {policy_count}/{n}={policy_count/n:.3f} exceeds ref <= {QUOTA_REF['policy_quota_share_max']:.2f}")
    if marker_top > QUOTA_REF["marker_single_max"]:
        deviations.append(f"marker_style '{marker_top_val}' share {marker_top:.3f} exceeds ref <= {QUOTA_REF['marker_single_max']:.2f}")

    return {
        "n_secrets": n,
        "dimensions": dims,
        "type_b": {"count": type_b, "share": type_b / n},
        "boundary_test": {"count": boundary, "share": boundary / n},
        "policy_quota_tag": {"count": policy_count, "share": policy_count / n},
        "marker_style_top": {"value": marker_top_val, "share": marker_top},
        "deviations": deviations,
    }


# ===========================================================================
# CHECK 2 — surface-form / shortcut audit (b1, b2, b3)
# ===========================================================================
def check2b1_ngrams(secrets, hard_negs):
    sec_tok = [norm_tokens(s["secret_text"]) for s in secrets]
    hn_tok = [norm_tokens(h["text"]) for h in hard_negs]
    n_hn = len(hn_tok)

    # document frequency of each ngram among secrets
    sec_df = Counter()
    for toks in sec_tok:
        seen = set()
        for nn in (2, 3, 4, 5):
            seen.update(ngrams(toks, nn))
        for g in seen:
            sec_df[g] += 1

    # precompute hard-neg ngram sets for occurrence lookup
    hn_sets = []
    for toks in hn_tok:
        s = set()
        for nn in (2, 3, 4, 5):
            s.update(ngrams(toks, nn))
        hn_sets.append(s)

    candidates = []
    for g, df in sec_df.items():
        if df < 3:
            continue
        hn_occ = sum(1 for hs in hn_sets if g in hs)
        hn_rate = hn_occ / n_hn
        if hn_rate < 0.10:
            candidates.append({"ngram": g, "secret_doc_count": df,
                               "hn_occurrence": hn_occ, "hn_rate": hn_rate})
    candidates.sort(key=lambda c: (-c["secret_doc_count"], -len(c["ngram"].split()), c["ngram"]))
    return candidates


def _heuristic_eval(secrets, hard_negs, predicate):
    """predicate(text)->bool predicts 'secret'. Returns metrics + per-kind FP."""
    tp = sum(1 for s in secrets if predicate(s["secret_text"]))
    fn = len(secrets) - tp
    fp = sum(1 for h in hard_negs if predicate(h["text"]))
    anchors = [h for h in hard_negs if h["kind"] == "anchor"]
    decoys = [h for h in hard_negs if h["kind"] == "decoy"]
    fp_anchor = sum(1 for h in anchors if predicate(h["text"]))
    fp_decoy = sum(1 for h in decoys if predicate(h["text"]))
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / len(secrets) if secrets else None
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall,
        "fp_anchor": fp_anchor, "fp_anchor_rate": fp_anchor / len(anchors) if anchors else None,
        "fp_decoy": fp_decoy, "fp_decoy_rate": fp_decoy / len(decoys) if decoys else None,
        "alarm_high_pr": (precision is not None and recall is not None
                          and recall > 0.9 and precision > 0.9),
    }


def check2b2_heuristics(secrets, hard_negs):
    results = {}
    # vocab — per word
    for w in VOCAB_WORDS:
        results[f"vocab:{w}"] = _heuristic_eval(secrets, hard_negs,
                                                lambda t, w=w: has_word(t, w))
    # vocab — combined any-of
    results["vocab:ANY"] = _heuristic_eval(
        secrets, hard_negs, lambda t: any(has_word(t, w) for w in VOCAB_WORDS))
    # structural
    results["struct:num>=1"] = _heuristic_eval(
        secrets, hard_negs, lambda t: numeric_token_count(t) >= 1)
    results["struct:num>=3"] = _heuristic_eval(
        secrets, hard_negs, lambda t: numeric_token_count(t) >= 3)
    results["struct:semicolon>=2"] = _heuristic_eval(
        secrets, hard_negs, lambda t: t.count(";") >= 2)
    return results


def check2b3_numeric_density(secrets, hard_negs):
    sec_counts = [numeric_token_count(s["secret_text"]) for s in secrets]
    anc_counts = [numeric_token_count(h["text"]) for h in hard_negs if h["kind"] == "anchor"]
    dec_counts = [numeric_token_count(h["text"]) for h in hard_negs if h["kind"] == "decoy"]

    def hist(counts):
        c = Counter(counts)
        return {str(k): c[k] for k in sorted(c)}

    return {
        "secret": {"stats": describe(sec_counts), "hist": hist(sec_counts)},
        "anchor": {"stats": describe(anc_counts), "hist": hist(anc_counts)},
        "decoy": {"stats": describe(dec_counts), "hist": hist(dec_counts)},
    }


# ===========================================================================
# CHECK 3 — embedding hygiene
# ===========================================================================
def check3_embedding(secrets, sec_emb, anc_emb, atom_emb, atom_mask,
                     prev_v3_violation_ids=None, n_anchor=None):
    n = len(secrets)
    # secret vs own anchor cosine (diagonal of sec x anc)
    own_cos = [float(np.dot(sec_emb[i], anc_emb[i])) for i in range(n)]

    by_type = defaultdict(list)
    by_domain = defaultdict(list)
    for i, s in enumerate(secrets):
        by_type[s["offset_type"]].append(own_cos[i])
        by_domain[s["domain"]].append(own_cos[i])

    # cross-pair rank: secret vs all 30 anchors
    sim_sa = sec_emb @ anc_emb.T  # (n, n)
    cross_rank = []
    for i in range(n):
        row = sim_sa[i]
        oc = float(row[i])
        rank = int((row > oc).sum()) + 1
        ni = int(row.argmax())
        if rank != 1:
            cross_rank.append({
                "id": secrets[i]["id"], "own_cosine": oc, "anchor_rank": rank,
                "nearest_anchor_id": secrets[ni]["id"],
                "nearest_anchor_cosine": float(row[ni]),
            })

    # anchor pairwise crosstalk (upper triangle > 0.80)
    sim_aa = anc_emb @ anc_emb.T
    crosstalk = []
    for i in range(n):
        for j in range(i + 1, n):
            c = float(sim_aa[i, j])
            if c > ANCHOR_CROSSTALK_COS:
                crosstalk.append({"a": secrets[i]["id"], "b": secrets[j]["id"],
                                  "a_domain": secrets[i]["domain"],
                                  "b_domain": secrets[j]["domain"], "cosine": c})
    crosstalk.sort(key=lambda x: -x["cosine"])

    # atomic paired delta (rows with atomic_text) — gate (a) v3
    N = n_anchor if n_anchor is not None else n
    thr = math.ceil(GATE_A_ATTR_FRACTION * N)
    sim_atom_a = atom_emb @ anc_emb.T  # (n, n); rows for masked entries are meaningless
    atomic = []
    for i in range(n):
        if not atom_mask[i]:
            continue
        a_oc = float(sim_atom_a[i, i])
        row = sim_atom_a[i]
        a_rank = int((row > a_oc).sum()) + 1
        delta = a_oc - own_cos[i]
        otype = secrets[i]["offset_type"]
        violation, attr_watch, criterion = v3_atomic_status(otype, delta, a_rank, N)
        atomic.append({
            "id": secrets[i]["id"], "offset_type": otype,
            "bundle_cosine": own_cos[i],
            "atomic_cosine": a_oc, "delta": delta, "atomic_rank": a_rank,
            "violation": violation, "attribution_watch": attr_watch,
            "criterion": criterion,
        })
    deltas = [a["delta"] for a in atomic]
    prev_viol = set(prev_v3_violation_ids or [])
    cur_viol = [a["id"] for a in atomic if a["violation"]]
    type_a_viol = [a["id"] for a in atomic if a["violation"] and a["offset_type"] == "A"]
    type_b_viol = [a["id"] for a in atomic if a["violation"] and a["offset_type"] == "B"]
    attr_watch_ids = [a["id"] for a in atomic if a["attribution_watch"]]
    # corrected "newly-crossed" counter: items that ARE violations now but were NOT
    # under the same v3 criterion last round (independent of which batch the id is in).
    newly_crossed = [i for i in cur_viol if i not in prev_viol] if prev_v3_violation_ids is not None else None
    atomic_summary = {
        "n": len(atomic),
        "n_anchor": N,
        "attr_threshold": thr,
        "delta_pos": sum(1 for d in deltas if d > 0),
        "delta_neg": sum(1 for d in deltas if d < 0),
        "delta_zero": sum(1 for d in deltas if d == 0),
        "delta_mean": statistics.fmean(deltas) if deltas else None,
        "delta_min": min(deltas) if deltas else None,
        "delta_max": max(deltas) if deltas else None,
        "violations": cur_viol,
        "type_a_violations": type_a_viol,
        "type_b_violations": type_b_viol,
        "attribution_watch": attr_watch_ids,
        "newly_crossed": newly_crossed,
        "type_b_violation_cum": len(type_b_viol),
        "type_b_violation_new": (len([i for i in type_b_viol if i not in prev_viol])
                                 if prev_v3_violation_ids is not None else None),
    }

    return {
        "own_cosine_overall": describe(own_cos),
        "own_cosine_by_type": {k: describe(v) for k, v in by_type.items()},
        "own_cosine_by_domain": {k: describe(v) for k, v in by_domain.items()},
        "cross_pair_rank_violations": cross_rank,
        "anchor_crosstalk_gt080": crosstalk,
        "atomic_pairs": atomic,
        "atomic_summary": atomic_summary,
    }


# ===========================================================================
# CHECK 4 — overlap & near-dup
# ===========================================================================
def _exact_norm(text):
    return _WS_RE.sub(" ", text.strip().lower())


def check4_overlap(model, secrets, hard_negs, sec_emb, anc_emb, hn_emb, hn_by_id):
    decoys = [h for h in hard_negs if h["kind"] == "decoy"]
    anchor_hns = [h for h in hard_negs if h["kind"] == "anchor"]
    dec_idx = [i for i, h in enumerate(hard_negs) if h["kind"] == "decoy"]
    anc_idx = [i for i, h in enumerate(hard_negs) if h["kind"] == "anchor"]
    dec_emb = hn_emb[dec_idx]
    anc_hn_emb = hn_emb[anc_idx]

    # ---- (i) new corpus (secret + anchor + decoy) vs legacy sets ----
    new_groups = {
        "secret": ([s["id"] for s in secrets], [s["secret_text"] for s in secrets], sec_emb),
        "anchor": ([s["id"] for s in secrets], [s["anchor_text"] for s in secrets], anc_emb),
        "decoy": ([h["id"] for h in decoys], [h["text"] for h in decoys], dec_emb),
    }

    legacy_results = {}
    for label, rel, field in LEGACY_SETS:
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(path):
            legacy_results[label] = {"status": "SKIPPED", "reason": f"not found: {rel}"}
            continue
        rows = load_jsonl(path)
        texts = [str(r.get(field, "")) for r in rows]
        ids = [str(r.get("_id", f"row{i}")) for i, r in enumerate(rows)]
        leg_emb = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        leg_norm = [_exact_norm(t) for t in texts]

        exact_hits, near_hits = [], []
        for gname, (gids, gtexts, gemb) in new_groups.items():
            gnorm = [_exact_norm(t) for t in gtexts]
            sim = gemb @ leg_emb.T  # (len group, len legacy)
            for gi in range(len(gids)):
                for lj in range(len(ids)):
                    if gnorm[gi] == leg_norm[lj] and gnorm[gi]:
                        exact_hits.append({"group": gname, "new_id": gids[gi],
                                           "legacy_id": ids[lj]})
                    c = float(sim[gi, lj])
                    if c > NEAR_DUP_COS:
                        near_hits.append({"group": gname, "new_id": gids[gi],
                                          "legacy_id": ids[lj], "cosine": c})
        near_hits.sort(key=lambda x: -x["cosine"])
        legacy_results[label] = {"status": "OK", "n_rows": len(rows),
                                 "exact_overlap": exact_hits, "near_dup_gt095": near_hits}

    # ---- (ii) decoy <-> anchor near-dup ----
    sim_da = dec_emb @ anc_hn_emb.T  # (n_decoy, n_anchor)
    dec_norm = [_exact_norm(h["text"]) for h in decoys]
    anc_norm = [_exact_norm(h["text"]) for h in anchor_hns]
    da_exact, da_near = [], []
    for i, d in enumerate(decoys):
        for j, a in enumerate(anchor_hns):
            if dec_norm[i] == anc_norm[j] and dec_norm[i]:
                da_exact.append({"decoy": d["id"], "anchor": a["id"]})
            c = float(sim_da[i, j])
            if c > NEAR_DUP_COS:
                da_near.append({"decoy": d["id"], "anchor": a["id"], "cosine": c})
    da_near.sort(key=lambda x: -x["cosine"])

    # pre-registered focus pairs (report regardless of threshold)
    prereg = []
    for dec_id, anc_id in PREREG_PAIRS:
        di = next((k for k, h in enumerate(decoys) if h["id"] == dec_id), None)
        aj = next((k for k, h in enumerate(anchor_hns) if h["id"] == anc_id), None)
        if di is None or aj is None:
            prereg.append({"decoy": dec_id, "anchor": anc_id, "cosine": None,
                           "note": "id not found"})
        else:
            prereg.append({"decoy": dec_id, "anchor": anc_id,
                           "cosine": float(sim_da[di, aj]),
                           "exceeds_095": float(sim_da[di, aj]) > NEAR_DUP_COS})

    # ---- (iii) secret <-> secret exact duplicate ----
    sec_norm = [_exact_norm(s["secret_text"]) for s in secrets]
    sec_dup = []
    for i in range(len(secrets)):
        for j in range(i + 1, len(secrets)):
            if sec_norm[i] == sec_norm[j] and sec_norm[i]:
                sec_dup.append({"a": secrets[i]["id"], "b": secrets[j]["id"]})

    # ---- (iv) decoy <-> decoy near-dup (exact + cosine>0.95) ----
    sim_dd = dec_emb @ dec_emb.T
    dd_exact, dd_near = [], []
    for i in range(len(decoys)):
        for j in range(i + 1, len(decoys)):
            if dec_norm[i] == dec_norm[j] and dec_norm[i]:
                dd_exact.append({"a": decoys[i]["id"], "b": decoys[j]["id"]})
            c = float(sim_dd[i, j])
            if c > NEAR_DUP_COS:
                dd_near.append({"a": decoys[i]["id"], "b": decoys[j]["id"], "cosine": c})
    dd_near.sort(key=lambda x: -x["cosine"])
    dec_pos = {h["id"]: k for k, h in enumerate(decoys)}
    dd_prereg = []
    for a_id, b_id in PREREG_DECOY_DECOY:
        ai, bj = dec_pos.get(a_id), dec_pos.get(b_id)
        if ai is None or bj is None:
            dd_prereg.append({"a": a_id, "b": b_id, "cosine": None, "note": "id not found"})
        else:
            cos = float(sim_dd[ai, bj])
            dd_prereg.append({"a": a_id, "b": b_id, "cosine": cos,
                              "exceeds_095": cos > NEAR_DUP_COS})

    return {
        "legacy_overlap": legacy_results,
        "decoy_anchor_exact": da_exact,
        "decoy_anchor_near_gt095": da_near,
        "prereg_pairs": prereg,
        "secret_secret_exact_dup": sec_dup,
        "decoy_decoy_exact": dd_exact,
        "decoy_decoy_near_gt095": dd_near,
        "decoy_decoy_prereg": dd_prereg,
    }


# ===========================================================================
# CHECK 5 — secret-secret nearest neighbor audit
# ---------------------------------------------------------------------------
# Motivation: monitor TEMPLATE COLLAPSE as the corpus scales. If the share of
# cross-domain nearest neighbours rises batch-over-batch, secrets are converging
# onto a shared surface template (an early warning that generation is producing
# stylistically homogeneous text). This batch's numbers are the BASELINE for the
# batch-2+ trend comparison. Descriptive only — no pass/fail.
# ===========================================================================
def check5_secret_nn(secrets, sec_emb, current_batch_ids=None):
    n = len(secrets)
    cur_ids = set(current_batch_ids or [])
    sim = sec_emb @ sec_emb.T
    np.fill_diagonal(sim, -np.inf)  # exclude self

    nn_rows = []
    same_domain = 0
    cross_pairs = []
    for i in range(n):
        j = int(sim[i].argmax())
        c = float(sim[i, j])
        same = secrets[i]["domain"] == secrets[j]["domain"]
        same_domain += int(same)
        nn_rows.append({
            "id": secrets[i]["id"], "domain": secrets[i]["domain"],
            "nn_id": secrets[j]["id"], "nn_domain": secrets[j]["domain"],
            "cosine": c, "same_domain": same,
        })
        if not same:
            cross_pairs.append({
                "id": secrets[i]["id"], "domain": secrets[i]["domain"],
                "nn_id": secrets[j]["id"], "nn_domain": secrets[j]["domain"],
                "cosine": c,
            })

    # top-10 secret-secret cosine (upper triangle, any domain)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((float(sim[i, j]), secrets[i]["id"], secrets[j]["id"],
                          secrets[i]["domain"], secrets[j]["domain"]))
    pairs.sort(key=lambda x: -x[0])
    top10 = [{"a": a, "b": b, "a_domain": ad, "b_domain": bd, "cosine": c}
             for c, a, b, ad, bd in pairs[:10]]

    # monitor v2: top-1 secret-secret cosine is the PRIMARY criterion.
    top1 = top10[0]["cosine"] if top10 else None
    if top1 is None:
        top1_status = "n/a"
    elif top1 > CHECK5_TOP1_STOP:
        top1_status = "STOP-AND-REVIEW"
    elif top1 > CHECK5_TOP1_WARNING:
        top1_status = "WARNING"
    else:
        top1_status = "ok"

    n_domains = len(set(s["domain"] for s in secrets))
    # cross-domain NN pairs newly contributed by this batch's secrets (source id).
    new_cross = [p for p in cross_pairs if p["id"] in cur_ids]

    return {
        "n_secrets": n,
        "n_domains": n_domains,
        "avg_members_per_domain": n / n_domains if n_domains else None,
        "same_domain_nn": same_domain,
        "same_domain_nn_share": same_domain / n,
        "cross_domain_nn_share": (n - same_domain) / n,
        "top1_cosine": top1,
        "top1_status": top1_status,
        "nn_all": nn_rows,
        "cross_domain_nn_pairs": cross_pairs,
        "new_cross_domain_nn_pairs": new_cross,
        "top10_cosine": top10,
    }


# ===========================================================================
# Report rendering
# ===========================================================================
def render_report(meta, c1, c2b1, c2b2, c2b3, c3, c4, c5):
    L = []
    L.append("# corpus_v2 — Validation Report (checks 1-5)")
    L.append("")
    L.append("MEASUREMENT ONLY. Every check emits measurements + a manual-review "
             "list; no automatic pass/fail. Reference/quota lines are advisory.")
    L.append("")
    L.append("## Header")
    L.append("")
    L.append(f"- Encoder: `{meta['model_name']}` (sentence-transformers `{meta['st_version']}`)")
    L.append(f"- Python: `{meta['python']}`  |  Platform: `{meta['platform']}`")
    L.append(f"- Run date: `{meta['run_date']}`")
    L.append(f"- cosine = dot product of L2-normalized embeddings (`normalize_embeddings=True`).")
    L.append("- Corpus files:")
    for f in meta["corpus_files"]:
        L.append(f"    - `{f['path']}` — {f['lines']} rows")
    L.append(f"- Hard-negatives: `{meta['hn_file']['path']}` — {meta['hn_file']['lines']} rows "
             f"({meta['hn_anchor']} anchor + {meta['hn_decoy']} decoy)")
    L.append(f"- **Quota base = {c1['n_secrets']} cumulative secrets** "
             f"(cumulative tally: Type B {c1['type_b']['count']}/{c1['n_secrets']}, "
             f"policy_quota {c1['policy_quota_tag']['count']}/{c1['n_secrets']}, "
             f"boundary_test {c1['boundary_test']['count']}/{c1['n_secrets']}).")
    L.append("")

    # ---------------- Check 1 ----------------
    L.append("## Check 1 — Quota & coverage")
    L.append("")
    L.append("Reference (advisory): Type B ~20% | boundary_test ~10% | "
             "policy_quota tag <=20% | no single marker_style >50%.")
    L.append("")
    for dim in ("domain", "offset_type", "subset", "marker_style"):
        L.append(f"**{dim}**")
        L.append("")
        L.append("| value | count | share |")
        L.append("|-------|------:|------:|")
        for val, d in c1["dimensions"][dim].items():
            L.append(f"| {val} | {d['count']} | {d['share']:.3f} |")
        L.append("")
    L.append(f"- Type B: {c1['type_b']['count']}/{c1['n_secrets']} ({c1['type_b']['share']:.3f})")
    L.append(f"- boundary_test: {c1['boundary_test']['count']}/{c1['n_secrets']} ({c1['boundary_test']['share']:.3f})")
    L.append(f"- policy_quota tag: {c1['policy_quota_tag']['count']}/{c1['n_secrets']} ({c1['policy_quota_tag']['share']:.3f})")
    L.append(f"- marker_style top: '{c1['marker_style_top']['value']}' ({c1['marker_style_top']['share']:.3f})")
    L.append("")
    L.append("_Manual-review items (Check 1):_")
    if c1["deviations"]:
        for d in c1["deviations"]:
            L.append(f"- {d}")
    else:
        L.append("- none (all dimensions within advisory reference lines).")
    L.append("")

    # ---------------- Check 2 ----------------
    L.append("## Check 2 — Surface-form / shortcut audit")
    L.append("")
    L.append("### (b1) regex n-gram shortcut candidates")
    L.append("")
    L.append("n-grams (n=2..5, lowercased, punctuation-stripped) in >=3 secrets AND "
             "appearing in <10% of the 55 hard-negatives. Descending by secret doc count.")
    L.append("")
    if c2b1:
        L.append("| n-gram | secret docs | hn occ | hn rate |")
        L.append("|--------|------------:|-------:|--------:|")
        for c in c2b1:
            L.append(f"| `{c['ngram']}` | {c['secret_doc_count']} | {c['hn_occurrence']} | {c['hn_rate']:.3f} |")
    else:
        L.append("_No n-gram met the (>=3 secrets, <10% hard-neg) criterion._")
    L.append("")

    L.append("### (b2) marker / heuristic separability")
    L.append("")
    L.append("predicate -> predicts 'secret'. positives = secrets, negatives = hard-negs. "
             "FP broken down by hard-neg kind (anchor / decoy), NOT merged. "
             "Alarm line (annotate only): recall>0.9 AND precision>0.9.")
    L.append("")
    L.append("| heuristic | precision | recall | TP | FP | FN | FP_anchor (rate) | FP_decoy (rate) | ALARM |")
    L.append("|-----------|----------:|-------:|---:|---:|---:|-----------------|----------------|:-----:|")
    for name, r in c2b2.items():
        p = "n/a" if r["precision"] is None else f"{r['precision']:.3f}"
        rec = "n/a" if r["recall"] is None else f"{r['recall']:.3f}"
        fa = f"{r['fp_anchor']} ({r['fp_anchor_rate']:.3f})" if r["fp_anchor_rate"] is not None else f"{r['fp_anchor']}"
        fd = f"{r['fp_decoy']} ({r['fp_decoy_rate']:.3f})" if r["fp_decoy_rate"] is not None else f"{r['fp_decoy']}"
        alarm = "**YES**" if r["alarm_high_pr"] else ""
        L.append(f"| {name} | {p} | {rec} | {r['tp']} | {r['fp']} | {r['fn']} | {fa} | {fd} | {alarm} |")
    L.append("")

    L.append("### (b3) numeric-token density")
    L.append("")
    L.append("numeric token = whitespace-separated token containing >=1 digit.")
    L.append("")
    for grp in ("secret", "anchor", "decoy"):
        d = c2b3[grp]
        L.append(f"- **{grp}**: {fmt_stats(d['stats'])}")
        L.append(f"    - histogram (count -> #items): {d['hist']}")
    dec_mean = c2b3["decoy"]["stats"].get("mean")
    if dec_mean is not None:
        L.append(f"- decoy-pool numeric-token mean = {dec_mean:.4f} vs 3.5 stop-line "
                 f"(delta {dec_mean - B3_DECOY_STOP_LINE:+.4f}) — reported only, not judged.")
    L.append("")
    L.append("_Manual-review items (Check 2):_")
    mr2 = []
    if c2b1:
        mr2.append(f"{len(c2b1)} n-gram shortcut candidate(s) (b1) — inspect for regex-anchorability.")
    alarms = [n for n, r in c2b2.items() if r["alarm_high_pr"]]
    if alarms:
        mr2.append(f"high-separability heuristics (recall>0.9 & precision>0.9): {', '.join(alarms)}.")
    mr2.append("(b3) inspect whether secret vs hard-neg numeric-count distributions are near-disjoint "
               "(would make 'count the numbers' itself a shortcut).")
    for m in mr2:
        L.append(f"- {m}")
    L.append("")

    # ---------------- Check 3 ----------------
    L.append("## Check 3 — Embedding hygiene")
    L.append("")
    L.append("### secret vs own anchor_text cosine")
    L.append("")
    L.append(f"- overall: {fmt_stats(c3['own_cosine_overall'])}")
    for k, v in c3["own_cosine_by_type"].items():
        L.append(f"- offset_type {k}: {fmt_stats(v)}")
    L.append("")
    L.append("by domain:")
    L.append("")
    L.append("| domain | " + fmt_stats({"n":0}).replace("(empty)", "stats") + " |")
    L.append("|--------|-------|")
    for k, v in sorted(c3["own_cosine_by_domain"].items()):
        L.append(f"| {k} | {fmt_stats(v)} |")
    L.append("")
    L.append("### cross-pair rank violations (secret's own anchor NOT nearest among 30)")
    L.append("")
    if c3["cross_pair_rank_violations"]:
        L.append("| id | own cosine | anchor_rank | nearest_anchor_id | nearest cosine |")
        L.append("|----|-----------:|:-----------:|-------------------|---------------:|")
        for r in c3["cross_pair_rank_violations"]:
            L.append(f"| {r['id']} | {r['own_cosine']:.4f} | {r['anchor_rank']} | "
                     f"{r['nearest_anchor_id']} | {r['nearest_anchor_cosine']:.4f} |")
    else:
        L.append("_None — every secret's own anchor is its nearest (rank==1)._")
    L.append("")
    L.append(f"### anchor-anchor crosstalk (cosine > {ANCHOR_CROSSTALK_COS})")
    L.append("")
    if c3["anchor_crosstalk_gt080"]:
        L.append("| anchor A | anchor B | A domain | B domain | cosine |")
        L.append("|----------|----------|----------|----------|-------:|")
        for r in c3["anchor_crosstalk_gt080"]:
            L.append(f"| {r['a']} | {r['b']} | {r['a_domain']} | {r['b_domain']} | {r['cosine']:.4f} |")
    else:
        L.append(f"_No anchor pair exceeds {ANCHOR_CROSSTALK_COS}._")
    L.append("")
    L.append("### atomic paired delta — gate (a) v3 (scale-robust)")
    L.append("")
    L.append(f"{ATOMIC_GATE_NOTE}")
    L.append("")
    asum = c3["atomic_summary"]
    L.append(f"- **N (anchor pool) = {asum['n_anchor']}; ceil(0.10*N) = {asum['attr_threshold']}** "
             "(Type B violation line; Type A attribution-watch line).")
    L.append(f"- delta>0: {asum['delta_pos']}/{asum['n']} | delta<0: {asum['delta_neg']} | "
             f"delta==0: {asum['delta_zero']}")
    if asum["n"]:
        L.append(f"- delta mean {asum['delta_mean']:+.4f} | min {asum['delta_min']:+.4f} | max {asum['delta_max']:+.4f}")
    L.append("")
    L.append("_Type A violation = delta<=0 (rank not used). Type B violation = "
             f"rank > {asum['attr_threshold']}. 'watch' = Type A attribution-watch (rank>{asum['attr_threshold']}, not a violation)._")
    L.append("")
    L.append("| id | type | bundle cos | atomic cos | delta | atomic rank | criterion | violation | watch | note |")
    L.append("|----|:----:|-----------:|-----------:|------:|:-----------:|-----------|:---------:|:-----:|------|")
    for a in c3["atomic_pairs"]:
        note = ATOMIC_ANNOTATIONS.get(a["id"], "")
        L.append(f"| {a['id']} | {a['offset_type']} | {a['bundle_cosine']:.4f} | {a['atomic_cosine']:.4f} | "
                 f"{a['delta']:+.4f} | {a['atomic_rank']} | {a['criterion']} | "
                 f"{'YES' if a['violation'] else ''} | {'w' if a['attribution_watch'] else ''} | {note} |")
    L.append("")
    L.append(f"- Type A violations (delta<=0): {asum['type_a_violations'] or 'none'}")
    L.append(f"- Type B violations (rank>{asum['attr_threshold']}): {asum['type_b_violations'] or 'none'}")
    L.append(f"- Type A attribution-watch (rank>{asum['attr_threshold']}, NOT violations): "
             f"{asum['attribution_watch'] or 'none'}")
    # corrected newly-crossed counter (prev pairs re-evaluated under v3)
    if asum["newly_crossed"] is not None:
        prev_meta = meta.get("prev_report") or {}
        L.append(f"- **newly-crossed this round** (vs prior batch re-evaluated under v3, "
                 f"N_prev={prev_meta.get('n_prev','?')}): {asum['newly_crossed'] or 'none'} "
                 "(definition: violation now AND not a v3 violation last round — independent of "
                 "which batch the id belongs to, so pool-growth seed crossings are counted).")
        L.append(f"- Type B pattern-test: cumulative {asum['type_b_violation_cum']} "
                 f"(newly-crossed: {asum['type_b_violation_new']}).")
    else:
        L.append("- newly-crossed counter: n/a (no --prev-report supplied).")
    L.append("")
    # v3 pre-registration reconciliation
    b5_a_delta_le0 = sorted(a["id"] for a in c3["atomic_pairs"]
                            if a["offset_type"] == "A" and a["id"].startswith("b5_") and a["delta"] <= 0)
    expected_a = set(PREREG_V3_TYPE_A_BASE) | set(b5_a_delta_le0)
    actual_a = set(asum["type_a_violations"])
    actual_b = set(asum["type_b_violations"])
    L.append("**v3 pre-registration reconciliation:**")
    L.append("")
    L.append(f"- expected Type A violations = base{sorted(PREREG_V3_TYPE_A_BASE)} "
             f"∪ b5-A-with-delta<=0{b5_a_delta_le0} = {sorted(expected_a)}")
    L.append(f"- actual Type A violations = {sorted(actual_a)}")
    a_missing = sorted(expected_a - actual_a)
    a_extra = sorted(actual_a - expected_a)
    L.append(f"  - deviations: missing={a_missing or 'none'} | unexpected={a_extra or 'none'}")
    L.append(f"- expected Type B violations = only rank>{asum['attr_threshold']} "
             f"(pre-reg: {sorted(PREREG_V3_TYPE_B_REGRESS)} expected to REGRESS to PASS)")
    L.append(f"- actual Type B violations = {sorted(actual_b)}")
    regress_ok = sorted(PREREG_V3_TYPE_B_REGRESS - actual_b)
    regress_fail = sorted(PREREG_V3_TYPE_B_REGRESS & actual_b)
    L.append(f"  - p0_08/b2_36 regression: passed={regress_ok or 'none'} | "
             f"still-violating={regress_fail or 'none'}")
    L.append("")
    L.append("_Manual-review items (Check 3):_")
    mr3 = []
    if c3["cross_pair_rank_violations"]:
        mr3.append(f"{len(c3['cross_pair_rank_violations'])} secret(s) whose own anchor is not nearest "
                   "(secret-vs-anchor cross-pair; informational, not a gate).")
    if c3["anchor_crosstalk_gt080"]:
        mr3.append(f"{len(c3['anchor_crosstalk_gt080'])} anchor pair(s) with cosine>{ANCHOR_CROSSTALK_COS}.")
    if asum["violations"]:
        mr3.append(f"atomic gate(a) v3 violations: Type A {asum['type_a_violations'] or 'none'}; "
                   f"Type B {asum['type_b_violations'] or 'none'}.")
    if asum["attribution_watch"]:
        mr3.append(f"Type A attribution-watch (monitor, not violation): {asum['attribution_watch']}.")
    if a_missing or a_extra or regress_fail:
        mr3.append(f"v3 pre-reg deviations: A-missing={a_missing or 'none'}, "
                   f"A-unexpected={a_extra or 'none'}, B-regress-fail={regress_fail or 'none'}.")
    if not mr3:
        mr3.append("none.")
    for m in mr3:
        L.append(f"- {m}")
    L.append("")

    # ---------------- Check 4 ----------------
    L.append("## Check 4 — Overlap & near-dup")
    L.append("")
    L.append(f"Exact string overlap (normalized: trim+lower+collapse-ws) + cosine > {NEAR_DUP_COS} near-dup.")
    L.append("")
    L.append("### (i) new corpus (secret+anchor+decoy) vs legacy eval sets")
    L.append("")
    for label, res in c4["legacy_overlap"].items():
        if res["status"] == "SKIPPED":
            L.append(f"- **{label}**: SKIPPED — {res['reason']}")
            continue
        ne = len(res["exact_overlap"])
        nn = len(res["near_dup_gt095"])
        L.append(f"- **{label}** ({res['n_rows']} rows): exact={ne}, near-dup(>0.95)={nn}")
        for h in res["exact_overlap"]:
            L.append(f"    - EXACT [{h['group']}] {h['new_id']} == {h['legacy_id']}")
        for h in res["near_dup_gt095"][:20]:
            L.append(f"    - NEAR [{h['group']}] {h['new_id']} ~ {h['legacy_id']} cos={h['cosine']:.4f}")
    L.append("")
    L.append("### (ii) decoy <-> anchor near-dup")
    L.append("")
    L.append(f"- exact: {len(c4['decoy_anchor_exact'])} | near-dup(>0.95): {len(c4['decoy_anchor_near_gt095'])}")
    for h in c4["decoy_anchor_exact"]:
        L.append(f"    - EXACT decoy {h['decoy']} == anchor {h['anchor']}")
    for h in c4["decoy_anchor_near_gt095"][:20]:
        L.append(f"    - NEAR decoy {h['decoy']} ~ anchor {h['anchor']} cos={h['cosine']:.4f}")
    L.append("")
    L.append("Pre-registered focus pairs (reported regardless of 0.95):")
    L.append("")
    L.append("| decoy | anchor | cosine | >0.95 |")
    L.append("|-------|--------|-------:|:-----:|")
    for p in c4["prereg_pairs"]:
        cos = "n/a" if p["cosine"] is None else f"{p['cosine']:.4f}"
        ex = p.get("note") or ("YES" if p.get("exceeds_095") else "no")
        L.append(f"| {p['decoy']} | {p['anchor']} | {cos} | {ex} |")
    L.append("")
    L.append("### (iii) secret <-> secret exact duplicate")
    L.append("")
    if c4["secret_secret_exact_dup"]:
        for h in c4["secret_secret_exact_dup"]:
            L.append(f"- EXACT DUP {h['a']} == {h['b']}")
    else:
        L.append("_None._")
    L.append("")
    L.append("### (iv) decoy <-> decoy near-dup")
    L.append("")
    L.append(f"- exact: {len(c4['decoy_decoy_exact'])} | near-dup(>0.95): {len(c4['decoy_decoy_near_gt095'])}")
    for h in c4["decoy_decoy_exact"]:
        L.append(f"    - EXACT decoy {h['a']} == decoy {h['b']}")
    for h in c4["decoy_decoy_near_gt095"][:20]:
        L.append(f"    - NEAR decoy {h['a']} ~ decoy {h['b']} cos={h['cosine']:.4f}")
    L.append("")
    L.append("Pre-registered decoy<->decoy focus pairs (reported regardless of 0.95):")
    L.append("")
    L.append("| decoy A | decoy B | cosine | >0.95 |")
    L.append("|---------|---------|-------:|:-----:|")
    for p in c4["decoy_decoy_prereg"]:
        cos = "n/a" if p["cosine"] is None else f"{p['cosine']:.4f}"
        ex = p.get("note") or ("YES" if p.get("exceeds_095") else "no")
        L.append(f"| {p['a']} | {p['b']} | {cos} | {ex} |")
    L.append("")
    L.append("_Manual-review items (Check 4):_")
    mr4 = []
    for label, res in c4["legacy_overlap"].items():
        if res["status"] == "OK" and (res["exact_overlap"] or res["near_dup_gt095"]):
            mr4.append(f"{label}: {len(res['exact_overlap'])} exact / {len(res['near_dup_gt095'])} near-dup.")
    if c4["decoy_anchor_exact"] or c4["decoy_anchor_near_gt095"]:
        mr4.append(f"decoy<->anchor: {len(c4['decoy_anchor_exact'])} exact / {len(c4['decoy_anchor_near_gt095'])} near-dup.")
    if c4["secret_secret_exact_dup"]:
        mr4.append(f"{len(c4['secret_secret_exact_dup'])} exact secret duplicate(s).")
    if c4["decoy_decoy_exact"] or c4["decoy_decoy_near_gt095"]:
        mr4.append(f"decoy<->decoy: {len(c4['decoy_decoy_exact'])} exact / "
                   f"{len(c4['decoy_decoy_near_gt095'])} near-dup.")
    hi_prereg = [p for p in c4["prereg_pairs"] if p.get("exceeds_095")]
    hi_dd = [p for p in c4["decoy_decoy_prereg"] if p.get("exceeds_095")]
    if hi_prereg:
        mr4.append(f"{len(hi_prereg)} pre-registered decoy<->anchor pair(s) exceed 0.95.")
    if hi_dd:
        mr4.append(f"{len(hi_dd)} pre-registered decoy<->decoy pair(s) exceed 0.95.")
    if not mr4:
        mr4.append("none.")
    for m in mr4:
        L.append(f"- {m}")
    L.append("")

    # ---------------- Check 5 ----------------
    L.append("## Check 5 — Secret-Secret Nearest Neighbor Audit (monitor v2)")
    L.append("")
    L.append("Monitor v2 (chat-ratified): the PRIMARY criterion is the top-1 secret-secret "
             "cosine (WARNING > 0.70, STOP-AND-REVIEW > 0.75, annotate only — no auto-judgment). "
             "cross-domain NN share is demoted to purely DESCRIPTIVE (no health framing); any "
             "direction change is accompanied only by the list of newly-contributing pairs.")
    L.append("")
    this_top1 = c5["top1_cosine"]
    if this_top1 is not None:
        top_pair = c5["top10_cosine"][0]
        L.append(f"- **PRIMARY: top-1 secret-secret cosine = {this_top1:.4f} "
                 f"-> [{c5['top1_status']}]** ({top_pair['a']} ~ {top_pair['b']}; "
                 f"thresholds: WARNING>0.70, STOP-AND-REVIEW>0.75).")
    L.append(f"- (descriptive) same-domain NN: {c5['same_domain_nn']}/{c5['n_secrets']} "
             f"({c5['same_domain_nn_share']:.3f}); cross-domain NN share {c5['cross_domain_nn_share']:.3f}.")
    L.append(f"- (descriptive) domains={c5['n_domains']}, avg members/domain "
             f"= {c5['avg_members_per_domain']:.4f}.")
    L.append("")
    # trend table vs frozen prior-batch reference points
    L.append("**Trend (this batch vs frozen prior batches):**")
    L.append("")
    L.append("| metric | this batch | " +
             " | ".join(r["label"] for r in CHECK5_TREND_REFS) + " |")
    L.append("|--------|-----------:|" + "|".join(["-----------:"] * len(CHECK5_TREND_REFS)) + "|")
    if this_top1 is not None:
        top1_cells = " | ".join(
            f"{r['top1_secret_cosine']:.4f} (Δ{this_top1-r['top1_secret_cosine']:+.4f})"
            for r in CHECK5_TREND_REFS)
        L.append(f"| top-1 secret-secret cosine (PRIMARY) | {this_top1:.4f} | {top1_cells} |")
    share_cells = " | ".join(
        f"{r['cross_domain_nn_share']:.3f} (Δ{c5['cross_domain_nn_share']-r['cross_domain_nn_share']:+.3f})"
        for r in CHECK5_TREND_REFS)
    L.append(f"| cross-domain NN share (descriptive) | {c5['cross_domain_nn_share']:.3f} | {share_cells} |")
    avg_cells = " | ".join(
        f"{r['avg_members_per_domain']:.4f}" for r in CHECK5_TREND_REFS)
    L.append(f"| avg members/domain | {c5['avg_members_per_domain']:.4f} | {avg_cells} |")
    L.append("")
    # newly-contributing cross-domain NN pairs (source = this batch's secrets)
    L.append("**Newly-contributing cross-domain NN pairs (source = this batch's secrets):**")
    L.append("")
    if c5["new_cross_domain_nn_pairs"]:
        L.append("| id | domain | NN id | NN domain | cosine |")
        L.append("|----|--------|-------|-----------|-------:|")
        for r in c5["new_cross_domain_nn_pairs"]:
            L.append(f"| {r['id']} | {r['domain']} | {r['nn_id']} | {r['nn_domain']} | {r['cosine']:.4f} |")
    else:
        L.append("_None from this batch._")
    L.append("")
    L.append("### (i) each secret's nearest-neighbour secret")
    L.append("")
    L.append("| id | domain | NN id | NN domain | cosine | same-domain |")
    L.append("|----|--------|-------|-----------|-------:|:-----------:|")
    for r in c5["nn_all"]:
        L.append(f"| {r['id']} | {r['domain']} | {r['nn_id']} | {r['nn_domain']} | "
                 f"{r['cosine']:.4f} | {'yes' if r['same_domain'] else 'NO'} |")
    L.append("")
    L.append("### (ii) cross-domain NN pairs")
    L.append("")
    if c5["cross_domain_nn_pairs"]:
        L.append("| id | domain | NN id | NN domain | cosine |")
        L.append("|----|--------|-------|-----------|-------:|")
        for r in c5["cross_domain_nn_pairs"]:
            L.append(f"| {r['id']} | {r['domain']} | {r['nn_id']} | {r['nn_domain']} | {r['cosine']:.4f} |")
    else:
        L.append("_None — every secret's nearest neighbour is same-domain._")
    L.append("")
    L.append("### (iii) top-10 secret-secret cosine (any domain)")
    L.append("")
    L.append("| rank | A | A domain | B | B domain | cosine |")
    L.append("|-----:|---|----------|---|----------|-------:|")
    for k, r in enumerate(c5["top10_cosine"], 1):
        L.append(f"| {k} | {r['a']} | {r['a_domain']} | {r['b']} | {r['b_domain']} | {r['cosine']:.4f} |")
    L.append("")
    L.append("_Manual-review items (Check 5):_")
    if c5["top1_cosine"] is not None:
        top = c5["top10_cosine"][0]
        L.append(f"- PRIMARY top-1 secret-secret cosine {c5['top1_cosine']:.4f} -> "
                 f"[{c5['top1_status']}] ({top['a']} ~ {top['b']}).")
    if c5["new_cross_domain_nn_pairs"]:
        L.append(f"- {len(c5['new_cross_domain_nn_pairs'])} newly-contributing cross-domain NN "
                 "pair(s) from this batch (descriptive — see table above).")
    L.append("")

    return "\n".join(L)


# ===========================================================================
# main
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", nargs="+", required=True)
    ap.add_argument("--hard-negatives", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prev-report", default=None,
                    help="prior batch report.json; enables the corrected "
                         "'newly-crossed' counter (prior pairs re-evaluated under v3).")
    args = ap.parse_args()

    model_name = load_model_name()

    # resolve inputs relative to CWD or to this dir
    def resolve(p):
        if os.path.isabs(p) and os.path.exists(p):
            return p
        for base in (os.getcwd(), HERE):
            cand = os.path.join(base, p)
            if os.path.exists(cand):
                return cand
        return p

    corpus_paths = [resolve(p) for p in args.corpus]
    hn_path = resolve(args.hard_negatives)

    secrets = []
    corpus_files_meta = []
    current_batch_ids = []
    for p in corpus_paths:
        rows = load_jsonl(p)
        secrets.extend(rows)
        current_batch_ids = [r["id"] for r in rows]  # last corpus file = "this batch"
        corpus_files_meta.append({"path": os.path.relpath(p, REPO_ROOT), "lines": len(rows)})
    hard_negs = load_jsonl(hn_path)

    print(f"[validate_corpus] encoder: {model_name}")
    print(f"[validate_corpus] secrets: {len(secrets)} | hard-negs: {len(hard_negs)}")

    model = SentenceTransformer(model_name)

    sec_emb = model.encode([s["secret_text"] for s in secrets],
                           normalize_embeddings=True, convert_to_numpy=True)
    anc_emb = model.encode([s["anchor_text"] for s in secrets],
                           normalize_embeddings=True, convert_to_numpy=True)
    atom_texts = [(s.get("atomic_text") or "").strip() for s in secrets]
    atom_mask = [bool(t) for t in atom_texts]
    atom_emb = model.encode([t if t else " " for t in atom_texts],
                            normalize_embeddings=True, convert_to_numpy=True)
    hn_emb = model.encode([h["text"] for h in hard_negs],
                          normalize_embeddings=True, convert_to_numpy=True)
    hn_by_id = {h["id"]: h for h in hard_negs}

    # run checks
    c1 = check1_quota(secrets)
    c2b1 = check2b1_ngrams(secrets, hard_negs)
    c2b2 = check2b2_heuristics(secrets, hard_negs)
    c2b3 = check2b3_numeric_density(secrets, hard_negs)
    # corrected "newly-crossed" basis: re-evaluate the PRIOR batch's stored atomic
    # pairs under the CURRENT v3 criterion (at the prior anchor-pool size).
    prev_v3_viol = None
    prev_report_meta = None
    if args.prev_report:
        prev_path = resolve(args.prev_report)
        if os.path.exists(prev_path):
            prev = json.load(open(prev_path))
            prev_pairs = prev.get("check3_embedding", {}).get("atomic_pairs", [])
            n_prev = prev.get("check1_quota", {}).get("n_secrets", len(prev_pairs))
            prev_v3_viol = v3_violation_ids(prev_pairs, n_prev)
            prev_report_meta = {"path": os.path.relpath(prev_path, REPO_ROOT),
                                "n_prev": n_prev, "v3_violations": sorted(prev_v3_viol)}
        else:
            print(f"[validate_corpus] WARN: --prev-report not found: {prev_path}")

    c3 = check3_embedding(secrets, sec_emb, anc_emb, atom_emb, atom_mask,
                          prev_v3_violation_ids=prev_v3_viol, n_anchor=len(secrets))
    c4 = check4_overlap(model, secrets, hard_negs, sec_emb, anc_emb, hn_emb, hn_by_id)
    c5 = check5_secret_nn(secrets, sec_emb, current_batch_ids)

    n_anchor = sum(1 for h in hard_negs if h["kind"] == "anchor")
    n_decoy = sum(1 for h in hard_negs if h["kind"] == "decoy")
    meta = {
        "model_name": model_name,
        "st_version": sentence_transformers.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "run_date": date.today().isoformat(),
        "corpus_files": corpus_files_meta,
        "hn_file": {"path": os.path.relpath(hn_path, REPO_ROOT), "lines": len(hard_negs)},
        "hn_anchor": n_anchor, "hn_decoy": n_decoy,
        "quota_base": len(secrets),
        "prev_report": prev_report_meta,
    }

    out_dir = args.out if os.path.isabs(args.out) else os.path.join(os.getcwd(), args.out)
    os.makedirs(out_dir, exist_ok=True)

    report_md = render_report(meta, c1, c2b1, c2b2, c2b3, c3, c4, c5)
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write(report_md)

    report_json = {
        "meta": meta,
        "check1_quota": c1,
        "check2_b1_ngrams": c2b1,
        "check2_b2_heuristics": c2b2,
        "check2_b3_numeric_density": c2b3,
        "check3_embedding": c3,
        "check4_overlap": c4,
        "check5_secret_nn": c5,
    }
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump(report_json, f, indent=2)

    # console summary
    print()
    print(f"[check1] Type B {c1['type_b']['count']}/{c1['n_secrets']}, "
          f"policy {c1['policy_quota_tag']['count']}/{c1['n_secrets']}, "
          f"boundary {c1['boundary_test']['count']}/{c1['n_secrets']}; "
          f"deviations={len(c1['deviations'])}")
    print(f"[check2] b1 ngram candidates={len(c2b1)}; "
          f"b2 alarms={[n for n,r in c2b2.items() if r['alarm_high_pr']]}")
    _as = c3['atomic_summary']
    print(f"[check3] N={_as['n_anchor']} ceil(0.10N)={_as['attr_threshold']}; "
          f"atomic v3 violations: A={_as['type_a_violations']} B={_as['type_b_violations']}; "
          f"watch={_as['attribution_watch']}; newly-crossed={_as['newly_crossed']}")
    print(f"[check4] decoy-anchor near-dup={len(c4['decoy_anchor_near_gt095'])}, "
          f"secret-dup={len(c4['secret_secret_exact_dup'])}")
    for p in c4["prereg_pairs"]:
        print(f"         prereg {p['decoy']}<->{p['anchor']}: "
              f"{'n/a' if p['cosine'] is None else f'{p['cosine']:.4f}'}")
    print(f"[check5] same-domain NN {c5['same_domain_nn']}/{c5['n_secrets']} "
          f"(cross-domain share {c5['cross_domain_nn_share']:.3f})")
    print()
    print(f"wrote: {os.path.join(out_dir, 'report.md')}")
    print(f"wrote: {os.path.join(out_dir, 'report.json')}")


if __name__ == "__main__":
    main()
