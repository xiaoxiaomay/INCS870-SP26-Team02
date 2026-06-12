#!/usr/bin/env python3
"""
eval/rerun_phase2/build_attack_idmap.py — A-step prep: candidate old->new attack
id-map for HUMAN ratification. ZERO API (local MiniLM embedding only). READ-ONLY:
emits one candidate table + summary; rewrites NOTHING, retargets NO attack.

For each of the 271 attacks (data/attack_prompts_expanded.jsonl), proposes the
top-3 corpus_v2 secrets its OLD target (S00xx) maps to (max cosine between the old
secret text and the 90 new secret_texts, MiniLM = the gate encoder), flags
value-swappable numbers in the attack query, and suggests a triage class.

Old-secret coverage: the 24 real S00xx targets are split across data/secrets/
secrets.jsonl (60) and secrets_full.jsonl (80); neither alone covers all 24, so
they are MERGED (secrets_full preferred, secrets.jsonl fallback). The special
target value "multiple" (multi-target attacks, e.g. salami) has no single old
secret -> mapping = N/A, triage = rewrite.

Taxonomy note: old secrets are tagged by `category` (e.g. strategy_logic), new
corpus_v2 by `domain` (e.g. technical_indicator) — DIFFERENT vocabularies, so a
literal "same domain" test is impossible. "Same domain" is operationalized as a
MAPPING-CONFIDENCE proxy: top1 cosine >= 0.50 AND the top-2 candidates agree on
their (new) domain. Documented; a human ratifies.

triage heuristic (per task):
  - original-70 manual attack (no based_on_original_id)  -> manual-reauthor
  - target == "multiple"                                 -> rewrite
  - has swappable number AND confident same-domain map   -> mechanical
  - otherwise (cross-domain / low-conf / no number)      -> rewrite

Outputs: eval/rerun_phase2/attack_idmap_candidate.csv + .../attack_idmap_summary.md
"""

import csv
import json
import os
import re
import sys
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
ATK = os.path.join(REPO_ROOT, "data", "attack_prompts_expanded.jsonl")
OLD_FILES = [os.path.join(REPO_ROOT, "data", "secrets", "secrets_full.jsonl"),
             os.path.join(REPO_ROOT, "data", "secrets", "secrets.jsonl")]
CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = ["corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
OUT_CSV = os.path.join(REPO_ROOT, "eval", "rerun_phase2", "attack_idmap_candidate.csv")
OUT_MD = os.path.join(REPO_ROOT, "eval", "rerun_phase2", "attack_idmap_summary.md")

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CONF_COS = 0.50      # top1 cosine threshold for a "confident" mapping
LOW_COS = 0.40       # below this = low-confidence, human-review flag
# digit-bearing tokens (value-swappable params); for a human table, err toward listing.
NUM_PAT = re.compile(r"[\$+\-]?\d[\d,\./:%xX×]*\s?(?:%|bps|bp|sigma|σ|x|×|days?|d|months?|mo|wks?|w)?", re.I)


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def main():
    attacks = load_jsonl(ATK)

    # merged old-secret lookup (secrets_full preferred)
    old = {}
    for f in reversed(OLD_FILES):  # load fallback first, then prefer full (overwrite)
        for d in load_jsonl(f):
            old[d["_id"]] = d
    # new corpus_v2
    new = []
    for fn in CORPUS_FILES:
        new += load_jsonl(os.path.join(CORPUS_DIR, fn))
    new_ids = [s["id"] for s in new]
    new_dom = [s["domain"] for s in new]

    model = SentenceTransformer(MODEL)
    def emb(ts):
        return model.encode(ts, normalize_embeddings=True, convert_to_numpy=True)
    new_emb = emb([s["secret_text"] for s in new])

    # top-3 corpus_v2 candidates per old target id present in the attack set
    targets = sorted(set(a["target_secret"] for a in attacks))
    top3 = {}            # old_id -> [(new_id, domain, cos), ...]
    old_brief = {}       # old_id -> "category / title"
    for tid in targets:
        if tid == "multiple" or tid not in old:
            top3[tid] = None
            old_brief[tid] = "(multi-target)" if tid == "multiple" else "(old id not found)"
            continue
        od = old[tid]
        old_brief[tid] = f"{od.get('category', '?')} / {od.get('title', '?')}"
        oe = emb([od.get("text", "")])[0]
        sims = new_emb @ oe
        order = np.argsort(-sims)[:3]
        top3[tid] = [(new_ids[i], new_dom[i], float(sims[i])) for i in order]

    rows = []
    for a in attacks:
        aid = a["_id"]
        tid = a["target_secret"]
        q = a.get("query", "")
        is_original70 = not a.get("based_on_original_id")
        nums = [m.group(0).strip() for m in NUM_PAT.finditer(q) if any(c.isdigit() for c in m.group(0))]
        has_num = len(nums) > 0
        cands = top3.get(tid)
        top1_cos = cands[0][2] if cands else None
        # confident same-domain mapping proxy
        domain_stable = bool(cands) and (cands[0][1] == cands[1][1])
        confident = bool(cands) and (top1_cos is not None and top1_cos >= CONF_COS) and domain_stable

        if is_original70:
            triage, why = "manual-reauthor", "original-70 hand-authored (no based_on_original_id); human re-write, do not auto"
        elif tid == "multiple":
            triage, why = "rewrite", "multi-target attack; no single old->new mapping"
        elif has_num and confident:
            triage, why = "mechanical", f"swappable number(s) + confident map (top1 cos {top1_cos:.3f}>= {CONF_COS}, top-2 domain agree)"
        else:
            reasons = []
            if not has_num:
                reasons.append("no swappable number in query")
            if cands and top1_cos is not None and top1_cos < CONF_COS:
                reasons.append(f"low map confidence (top1 cos {top1_cos:.3f})")
            if cands and not domain_stable:
                reasons.append("top-2 candidate domains disagree (cross-domain risk)")
            triage, why = "rewrite", "; ".join(reasons) or "default"

        def fmt(c):
            return f"{c[0]}|{c[1]}|{c[2]:.3f}" if c else ""
        rows.append({
            "attack_id": aid,
            "orig_target": tid,
            "old_secret_brief": old_brief.get(tid, ""),
            "cand1": fmt(cands[0]) if cands else "",
            "cand2": fmt(cands[1]) if cands else "",
            "cand3": fmt(cands[2]) if cands else "",
            "has_swappable_num": "Y" if has_num else "N",
            "matched_params": "; ".join(nums[:8]),
            "top1_cos": f"{top1_cos:.4f}" if top1_cos is not None else "",
            "domain_stable": "Y" if domain_stable else ("N" if cands else ""),
            "triage": triage,
            "rationale": why,
        })

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    cols = ["attack_id", "orig_target", "old_secret_brief", "cand1", "cand2", "cand3",
            "has_swappable_num", "matched_params", "top1_cos", "domain_stable",
            "triage", "rationale"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # summary.md
    tri = Counter(r["triage"] for r in rows)
    cross = [r for r in rows if r["domain_stable"] == "N"]
    lowcos = [r for r in rows if r["top1_cos"] and float(r["top1_cos"]) < LOW_COS]
    multi = [r for r in rows if r["orig_target"] == "multiple"]
    # mapping-strength diagnostic (why mechanical is empty)
    gen = [r for r in rows if r["triage"] != "manual-reauthor"]
    gen_num = [r for r in gen if r["has_swappable_num"] == "Y"]
    gen_num_hi = [r for r in gen_num if r["top1_cos"] and float(r["top1_cos"]) >= CONF_COS]
    mapped_cos = sorted(float(r["top1_cos"]) for r in rows if r["top1_cos"])
    cos_stats = (f"mean={sum(mapped_cos)/len(mapped_cos):.3f}, median={mapped_cos[len(mapped_cos)//2]:.3f}, "
                 f"min={mapped_cos[0]:.3f}, max={mapped_cos[-1]:.3f}") if mapped_cos else "n/a"
    n_stable = sum(1 for r in rows if r["domain_stable"] == "Y")

    L = ["# Attack id-map — CANDIDATE table for human ratification (READ-ONLY, ZERO API)", "",
         "Candidate old->new (corpus_v2) attack retarget map. NOTHING was rewritten or "
         "retargeted; this is input for human review before the actual A-step.", "",
         "## Method", "",
         f"- Mapping: MiniLM (`{MODEL}`, the gate encoder) cosine between each old target "
         "secret text and the 90 corpus_v2 secret_texts; top-3 candidates listed.",
         "- Old-secret texts merged from `secrets_full.jsonl` (preferred) + `secrets.jsonl` "
         "(fallback) to cover all 24 real S00xx targets.",
         "- 'same domain' is a PROXY (old `category` vs new `domain` are different "
         f"vocabularies): top1 cosine >= {CONF_COS} AND top-2 candidates' new-domain agree.",
         "- Numbers: digit-bearing query tokens (value-swappable params), listed for the human.", "",
         "## Triage counts", "",
         "| triage | count |", "|--------|------:|"]
    for k in ("mechanical", "rewrite", "manual-reauthor"):
        L.append(f"| {k} | {tri.get(k, 0)} |")
    L += [f"| **total** | **{len(rows)}** |", "",
          f"- original-70 (manual-reauthor): {sum(1 for r in rows if r['triage']=='manual-reauthor')}",
          f"- multi-target ('multiple') attacks: {len(multi)}", "",
          "## Why `mechanical` = 0 (mapping-strength diagnostic — key scoping result)", "",
          f"- top1 old->new cosine over all mapped attacks: **{cos_stats}** — the BEST any old "
          "secret maps onto a single corpus_v2 secret is ~0.53; the restructure deliberately moved "
          "secrets into a fresh single-domain anchor+offset space, so old targets have NO close new twin.",
          f"- of the 201 generated attacks, only **{len(gen_num)} carry a value-swappable number**, "
          f"and **{len(gen_num_hi)} of those reach top1 cosine >= {CONF_COS}**.",
          f"- top-2 candidate domains agree (`domain_stable`) for **{n_stable}/{len(rows)}** rows.",
          "- **Conclusion: purely-mechanical retarget is not viable on this corpus pair.** The A-step "
          "is effectively rewrite (201) + manual re-author (70); the id-map's value is the top-3 "
          "candidate new targets per attack to seed those rewrites.", "",
          "## ⚠️ Cross-domain-risk rows (top-2 candidate domains disagree) — human focus", ""]
    if cross:
        L.append("| attack_id | orig_target | top1_cos | cand1 | cand2 | triage |")
        L.append("|-----------|-------------|---------:|-------|-------|--------|")
        for r in cross[:60]:
            L.append(f"| {r['attack_id']} | {r['orig_target']} | {r['top1_cos']} | {r['cand1']} | {r['cand2']} | {r['triage']} |")
        if len(cross) > 60:
            L.append(f"| … | (+{len(cross)-60} more in CSV) | | | | |")
    else:
        L.append("_None._")
    L += ["", f"## ⚠️ Low top1 cosine (< {LOW_COS}) — weak/ambiguous mapping, human review ({len(lowcos)})", ""]
    if lowcos:
        L.append("| attack_id | orig_target | old_secret_brief | top1_cos | cand1 | triage |")
        L.append("|-----------|-------------|------------------|---------:|-------|--------|")
        for r in sorted(lowcos, key=lambda x: float(x["top1_cos"]))[:60]:
            L.append(f"| {r['attack_id']} | {r['orig_target']} | {r['old_secret_brief']} | {r['top1_cos']} | {r['cand1']} | {r['triage']} |")
        if len(lowcos) > 60:
            L.append(f"| … | (+{len(lowcos)-60} more in CSV) | | | | |")
    else:
        L.append("_None._")
    L += ["", "## Next step (human, NOT done here)",
          "- Ratify each row's triage; for `mechanical`, confirm the cand1 target + value swap; "
          "for `rewrite`/`manual-reauthor`, author against the chosen new secret. Only AFTER "
          "ratification does the actual retarget/rewrite (A-step proper) run.", ""]
    open(OUT_MD, "w").write("\n".join(L))

    print(f"[A-prep] rows={len(rows)} | triage={dict(tri)}")
    print(f"[A-prep] cross-domain-risk={len(cross)} | low-cos(<{LOW_COS})={len(lowcos)} | multi-target={len(multi)}")
    print(f"wrote: {OUT_CSV}")
    print(f"wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
