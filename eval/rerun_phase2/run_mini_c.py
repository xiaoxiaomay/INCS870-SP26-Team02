#!/usr/bin/env python3
"""
eval/rerun_phase2/run_mini_c.py — Mini-Pilot step C (L1 Independent Judge, 3 arms x 27).

REUSES run_l1_judge.py's judging primitives (SYSTEM_PROMPT, build_user_msg, judge_call,
normalize_judge, is_trivial_nondisclosure, token/price constants) so the judge output
schema is IDENTICAL to the existing l1_judge runs (G2 requirement). It does NOT modify
run_l1_judge.py; it only supplies corpus_v2 secret blocks + the mini per_prompt file.

Judge: gpt-4o-2024-08-06, temperature 0, blind to cosine/substring (per the reused
SYSTEM_PROMPT). Arms = B0 / B2_raw / B2_redacted. Trivial non-disclosures
("[BLOCKED]" / empty) are scored label 0 deterministically (NO API call), matching
run_l1_judge. Local cache under mini_pilot_<date>/cache_c/.

API: needs OPENAI_API_KEY. Peter runs with `!`. Reads mini_pilot_<date>/per_prompt.jsonl
(from run_mini_b.py); writes per_prompt_judge.jsonl + l1_judge_summary.json.

Usage:
  python eval/rerun_phase2/run_mini_c.py --max-cost 0.15
"""

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import date

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, REPO_ROOT)

from eval.run_l1_judge import (  # reuse — do not modify that file
    SYSTEM_PROMPT, build_user_msg, judge_call, normalize_judge, is_trivial_nondisclosure,
    get_token_counter, JUDGE_MODEL, RUBRIC_VERSION, ARMS,
    PRICE_INPUT_PER_1M, PRICE_OUTPUT_PER_1M,
)

CORPUS_DIR = os.path.join(REPO_ROOT, "eval", "corpus_v2")
CORPUS_FILES = ["corpus_batch_seed.jsonl"] + [f"corpus_batch_0{i}.jsonl" for i in range(1, 6)]
DATE = date.today().isoformat().replace("-", "_")
OUT_DIR = os.path.join(REPO_ROOT, "eval", "rerun_phase2", f"mini_pilot_{DATE}")
PER_PROMPT = os.path.join(OUT_DIR, "per_prompt.jsonl")
CACHE_DIR = os.path.join(OUT_DIR, "cache_c")


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def corpus_secret_block(sid, by_id):
    s = by_id.get(sid, {})
    parts = []
    if s.get("domain"):
        parts.append(f"Domain: {s['domain']} (offset_type {s.get('offset_type','?')})")
    if s.get("secret_text"):
        parts.append(f"Text: {s['secret_text']}")
    return "\n".join(parts)


def ckey(arm, aid, sid, q, resp):
    # ARM-INDEPENDENT: the judge is blind to the arm label and depends only on
    # (query, secret, response). Dropping `arm` from the key dedups identical
    # responses across arms (e.g. B2_raw == B2_redacted when no redaction occurred),
    # cutting API calls without changing any verdict.
    return hashlib.sha256("\x1f".join([JUDGE_MODEL, RUBRIC_VERSION, aid, sid,
                                       q or "", resp or ""]).encode()).hexdigest()


def cache_get(k):
    p = os.path.join(CACHE_DIR, k + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def cache_put(k, obj):
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(obj, open(os.path.join(CACHE_DIR, k + ".json"), "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-cost", type=float, default=0.15)
    args = ap.parse_args()

    if not os.path.exists(PER_PROMPT):
        print(f"ERROR: {PER_PROMPT} not found — run step B first.")
        sys.exit(2)

    secrets = [s for fn in CORPUS_FILES for s in load_jsonl(os.path.join(CORPUS_DIR, fn))]
    by_id = {s["id"]: s for s in secrets}
    recs = load_jsonl(PER_PROMPT)

    from openai import OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set; aborting (no API attempted).")
        sys.exit(2)
    client = OpenAI()
    counter = get_token_counter()

    judged = []
    in_tok = out_tok = 0
    cost = 0.0
    for rec in recs:
        aid, sid, q = rec["attack_id"], rec["target_secret"], rec["query"]
        block = corpus_secret_block(sid, by_id)
        for arm, field in ARMS:
            resp = rec.get(field, "")
            row = {"attack_id": aid, "target_secret": sid, "arm": arm,
                   "category": rec.get("category"), "response_field": field}
            if is_trivial_nondisclosure(resp):
                row.update({"judge": {"label": 0, "disclosed_items": [], "paraphrased": False,
                                      "rationale": "trivial non-disclosure (blocked/empty)",
                                      "confidence": "high"},
                            "method": "deterministic", "usage": {"prompt_tokens": 0,
                            "completion_tokens": 0, "total_tokens": 0}, "cost_usd": 0.0})
                judged.append(row)
                continue
            k = ckey(arm, aid, sid, q, resp)
            cached = cache_get(k)
            if cached:
                row.update({**cached, "method": "cache_hit"})
                judged.append(row)
                continue
            verdict, usage = judge_call(client, q, resp, block)
            ci = usage["prompt_tokens"] * PRICE_INPUT_PER_1M / 1e6
            co = usage["completion_tokens"] * PRICE_OUTPUT_PER_1M / 1e6
            in_tok += usage["prompt_tokens"]
            out_tok += usage["completion_tokens"]
            cost += ci + co
            obj = {"judge": verdict, "usage": usage, "cost_usd": round(ci + co, 6)}
            cache_put(k, obj)
            row.update({**obj, "method": "api"})
            judged.append(row)
            if cost > args.max_cost:
                print(f"HALT: cumulative judge cost ${cost:.4f} exceeded --max-cost ${args.max_cost}")
                break
        else:
            continue
        break

    with open(os.path.join(OUT_DIR, "per_prompt_judge.jsonl"), "w") as f:
        for r in judged:
            f.write(json.dumps(r) + "\n")

    # summary in the existing l1_judge_summary schema
    arms_sum = {}
    for arm, _ in ARMS:
        ar = [r for r in judged if r["arm"] == arm]
        l2 = sum(1 for r in ar if r["judge"]["label"] == 2)
        ge1 = sum(1 for r in ar if r["judge"]["label"] >= 1)
        by_group = defaultdict(lambda: {"n": 0, "label2": 0, "label_ge1": 0})
        for r in ar:
            g = by_group[r["category"]]
            g["n"] += 1
            g["label2"] += int(r["judge"]["label"] == 2)
            g["label_ge1"] += int(r["judge"]["label"] >= 1)
        arms_sum[arm] = {"n": len(ar), "label2_count": l2,
                         "label2_rate": l2 / len(ar) if ar else 0.0,
                         "label_ge1_count": ge1,
                         "label_ge1_rate": ge1 / len(ar) if ar else 0.0,
                         "by_group": {k: {"n": v["n"],
                                          "label2_rate": v["label2"] / v["n"],
                                          "label_ge1_rate": v["label_ge1"] / v["n"]}
                                      for k, v in by_group.items()}}
    summary = {"task": "L1 mini-pilot disclosure adjudication (corpus_v2, 27 attacks x 3 arms)",
               "set_size": len(recs), "judge_model": JUDGE_MODEL, "rubric_version": RUBRIC_VERSION,
               "temperature": 0, "arms": arms_sum,
               "cost": {"input_tokens": in_tok, "output_tokens": out_tok,
                        "total_cost_usd": round(cost, 6), "grand_total_cost_usd": round(cost, 6)}}
    json.dump(summary, open(os.path.join(OUT_DIR, "l1_judge_summary.json"), "w"), indent=2)
    print(f"[C] judged {len(judged)} (record,arm) | input_tok={in_tok} output_tok={out_tok} "
          f"cost=${cost:.4f}")
    print(f"wrote: {OUT_DIR}/per_prompt_judge.jsonl ; l1_judge_summary.json")


if __name__ == "__main__":
    main()
