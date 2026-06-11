#!/usr/bin/env python3
"""
scripts/parameter_presence.py — S1 Hybrid parameter-presence check.

STATUS: Phase 1a (extraction + candidate list ONLY).
  This file currently contains the literal NORMALIZER and the EXTRACTOR that
  re-derives proprietary numeric conditions from data/secrets/secrets.jsonl
  (R1 option (b)). It does NOT yet contain the runtime matcher (check / check_all)
  or any engine wiring — those come in Phase 1b AFTER the candidate list below
  is reviewed and frozen by the user.

WHY re-extract (R1=b): the cached eval/.../secret_literals.json mixes proprietary
conditions with public terms ("14D RSI", "VWAP") and truncated extraction
fragments ("3% and an", "18% and si"), and leaves 23/60 secrets empty. Matching
those would catastrophically over-redact benign analyst text. We instead extract
operator+value conditions / codenames directly from the secret text, then have a
human prune public-ish candidates before freezing (Phase 1b).

S1 SCOPE (do not overclaim): S1 is a LITERAL matcher. It closes verbatim
under-reporting for secrets that HAVE a clean proprietary numeric literal. It
does NOT catch paraphrase, and cannot cover secrets with no extractable literal.

Run:  python scripts/parameter_presence.py --emit-candidates
  -> writes eval/results/s1_parameter_presence_2026_06_06/s1_literals_candidates.{json,md}
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS_JSONL = ROOT / "data" / "secrets" / "secrets.jsonl"
OUT_DIR = ROOT / "eval" / "results" / "s1_parameter_presence_2026_06_06"
CAND_JSON = OUT_DIR / "s1_literals_candidates.json"
CAND_MD = OUT_DIR / "s1_literals_candidates.md"

# -----------------------------------------------------------------------------
# Normalizer (R5: symbol / word-operator / unit / period folding ONLY.
# Explicitly NO decimal<->percent equivalence, e.g. 0.015 != 1.5%.)
# -----------------------------------------------------------------------------
_UNICODE_FOLD = {
    "×": "x", "≤": "<=", "≥": ">=", "−": "-", "–": "-", "—": "-",
    "’": "'", "‘": "'", "“": '"', "”": '"',
}
_WORD_OPERATORS = [
    (r"\bgreater than or equal to\b", ">="),
    (r"\bless than or equal to\b", "<="),
    (r"\bat least\b", ">="),
    (r"\bat most\b", "<="),
    (r"\bno more than\b", "<="),
    (r"\bno less than\b", ">="),
    (r"\bgreater than\b", ">"),
    (r"\bless than\b", "<"),
    (r"\babove\b", ">"),
    (r"\bbelow\b", "<"),
    (r"\bunder\b", "<"),
    (r"\bover\b", ">"),
    (r"\bexceeds?\b", ">"),
    (r"\bequals?\b", "="),
    (r"\bequal to\b", "="),
]


def normalize(text: str) -> str:
    """Canonicalize for matching. Applied identically to literals and candidate text."""
    if not text:
        return ""
    s = text.lower()
    for k, v in _UNICODE_FOLD.items():
        s = s.replace(k, v)
    for pat, rep in _WORD_OPERATORS:
        s = re.sub(pat, rep, s)
    # unit words
    s = re.sub(r"\b(percent|pct)\b", "%", s)
    s = re.sub(r"(\d)\s+%", r"\1%", s)                          # "15 %" -> "15%"
    s = re.sub(r"(\d(?:\.\d+)?)\s*(?:times)\b", r"\1x", s)       # "2 times" -> "2x"
    # period forms: "14-day"/"14 day"/"14day" -> "14d"; "rsi(14)" -> "14d rsi"
    s = re.sub(r"\brsi\s*\(\s*(\d+)\s*\)", r"\1d rsi", s)
    s = re.sub(r"\b(\d+)\s*-?\s*day(s)?\b", r"\1d", s)
    # collapse operator spacing and whitespace
    s = re.sub(r"\s*(<=|>=|<|>|=)\s*", r" \1 ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -----------------------------------------------------------------------------
# Extraction patterns. Each yields (pattern_type, specificity, match_span).
# specificity: "strong" = carries a specific value/identifier (low FPR);
#              "review_weak" = bare duration / rank, public-ish (prune candidate).
# -----------------------------------------------------------------------------
# comparison phrase = up to 2 tokens immediately before the operator.
# Tokens may start with a digit (so "14D RSI", "5D return" keep their leading
# number — fixes the bug where a digit-led phrase was truncated to "d rsi").
_PHRASE = r"(?:[\w/|().\-]+\s+){0,1}[\w/|().\-]+"
_NUM = r"[+\-]?\d+(?:\.\d+)?"
# leading stopwords to trim off a captured phrase (conjunctions / filler)
_LEAD_STOP = {"and", "or", "if", "when", "then", "otherwise", "is", "are", "the",
              "a", "an", "at", "vs", "by", "to", "of", "for", "with", "yoy", "on", "in"}
# stopword qualifiers that must NOT count as a percentage qualifier (fragment guard)
_PCT_STOP = {"and", "or", "to", "of", "for", "vs", "from", "with", "the", "in",
             "by", "over", "per", "a", "an", "if"}

# -----------------------------------------------------------------------------
# 1b-step1 human-ratified curation (applied AFTER regex extraction).
# Explicit, auditable edits per the reviewer's precise instructions.
# -----------------------------------------------------------------------------
# DROP: exact (secret_id, normalized_literal) pairs to remove from the strong set.
S1_DROP = {
    ("S0056", "14d rsi < 30"),                 # public knowledge (RSI<30 oversold) — FPR mine; codename alpha-mr-01 covers
    ("S0083", "- realized) > 3 vol points"),   # formula-prefix junk
    ("S0136", "small-cap. sigma = 20"),        # cross-sentence junk + "20D" truncated
    ("S0136", "vol. v = 20"),                  # cross-sentence junk + "20D" truncated
    ("S0012", "k = 0.58"),                      # bare single-letter coefficient (no anchor)
    ("S0136", "k = 0.52"),                      # bare single-letter coefficient (no anchor)
    ("S0136", "k = 0.81"),                      # bare single-letter coefficient (no anchor)
}
# RENAME: keep anchored single-letter coefficients with their anchor word.
S1_RENAME = {
    ("S0012", "k = 0.32"): "coefficient k = 0.32",
    ("S0136", "k = 0.314"): "where k = 0.314",
}
# RECOVER: %-bound nouns the stopword guard dropped (skip mid stopword, grab ≤2-token noun).
# Only for the 4 secrets the reviewer named; hand-specified to avoid regex over-reach.
S1_RECOVER = {
    "S0019": [("60% daily volume", "percentage_qualifier_recovered", "Execute 60% of daily volume target …")],
    "S0022": [("3% high-vol", "percentage_qualifier_recovered", "tiered stop-loss: 3% for high-vol names …"),
              ("5% low-vol", "percentage_qualifier_recovered", "… 5% for low-vol names …")],
    "S0024": [("+6% vs benchmark", "percentage_qualifier_recovered", "utilities/healthcare overweight +6% vs benchmark")],
    "S0036": [("single-country exposure at 22%", "percentage_qualifier_recovered", "cap single-country exposure at 22% …"),
              ("em aggregate at 15%", "percentage_qualifier_recovered", "… EM aggregate at 15% …")],
}

PAT_COMPARISON = re.compile(
    rf"({_PHRASE})\s*(<=|>=|<|>|=|≤|≥)\s*({_NUM}\s*(?:%|bps|x|×|sigma|vol points)?)",
    re.IGNORECASE,
)


def _trim_lead(phrase):
    toks = phrase.split()
    while toks and toks[0].lower() in _LEAD_STOP:
        toks.pop(0)
    return " ".join(toks)
PAT_MULTIPLIER = re.compile(rf"\b({_NUM}\s*(?:x|×))\s+(\w+(?:\s+\w+){{0,2}})", re.IGNORECASE)
PAT_PCT_QUAL = re.compile(
    r"\b(\d+(?:\.\d+)?\s*%)\s+([A-Za-z][\w\- ]{0,18}?)\b", re.IGNORECASE)
PAT_RANGE = re.compile(r"([+\-]?\d+%\s*(?:to|[-–])\s*[+\-]?\d+%)", re.IGNORECASE)
PAT_MONEY = re.compile(r"(\$\s?\d+(?:\.\d+)?\s*[mbk]?)", re.IGNORECASE)
PAT_PERCENTILE = re.compile(r"(\d+(?:st|nd|rd|th)\s+percentile)", re.IGNORECASE)
PAT_CODENAME = re.compile(r"\b([A-Z][A-Za-z]+-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b")
PAT_DURATION = re.compile(
    r"\b(\d+\s*(?:trading\s+)?days?|\d+\s*-?\s*day(?:s)?|\d+d\b|\d+\s*minutes?|\d+w\b)\b",
    re.IGNORECASE,
)
# rank: "top N%"/"bottom N%" (explicit percentile cutoff) -> strong (proprietary);
# bare "top-N"/"top N"/"bottom-N" (generic count) -> review_weak (public-ish).
PAT_RANK = re.compile(r"\b(top|bottom)\s*-?\s*\d+\s*%?", re.IGNORECASE)


def _add(cands, seen, secret_id, raw, ptype, specificity, snippet):
    norm = normalize(raw)
    key = (secret_id, norm)
    if not norm or key in seen:
        return
    seen.add(key)
    cands.append({
        "secret_id": secret_id,
        "literal_raw": raw.strip(),
        "literal_normalized": norm,
        "pattern_type": ptype,
        "specificity": specificity,
        "source_snippet": snippet,
    })


def _snippet(text, start, end, pad=28):
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return ("…" if a > 0 else "") + text[a:b].replace("\n", " ").strip() + ("…" if b < len(text) else "")


def extract_candidates(secrets):
    out = []
    for s in secrets:
        sid = s["_id"]
        text = s.get("text", "") or ""
        cands, seen = [], set()
        for m in PAT_COMPARISON.finditer(text):
            phrase = _trim_lead(m.group(1))
            # phrase must start alphanumeric (drops formula junk like "- realized)")
            if not phrase or not phrase[0].isalnum() or ")" in phrase:
                continue
            raw = f"{phrase} {m.group(2)} {m.group(3).strip()}"
            _add(cands, seen, sid, raw, "comparison", "strong", _snippet(text, *m.span()))
        for m in PAT_MULTIPLIER.finditer(text):
            mult, qual = m.group(1).strip(), (m.group(2) or "").strip()
            qtoks = qual.split()
            while qtoks and qtoks[-1].lower() in _LEAD_STOP:   # strip trailing "on" etc.
                qtoks.pop()
            if not qtoks or qtoks[0].lower() in _LEAD_STOP:    # skip "1.2x and prohibits…"
                continue
            _add(cands, seen, sid, f"{mult} {' '.join(qtoks)}", "multiplier", "strong", _snippet(text, *m.span()))
        for m in PAT_PCT_QUAL.finditer(text):
            qual = (m.group(2) or "").strip().lower()
            if qual in _PCT_STOP or len(qual) < 2:
                continue   # fragment guard: "18% and", "60% of" -> skip
            _add(cands, seen, sid, m.group(0), "percentage_qualifier", "strong", _snippet(text, *m.span()))
        for m in PAT_RANGE.finditer(text):
            _add(cands, seen, sid, m.group(0), "range", "strong", _snippet(text, *m.span()))
        for m in PAT_MONEY.finditer(text):
            _add(cands, seen, sid, m.group(0), "money_threshold", "strong", _snippet(text, *m.span()))
        for m in PAT_PERCENTILE.finditer(text):
            _add(cands, seen, sid, m.group(0), "percentile", "strong", _snippet(text, *m.span()))
        for m in PAT_CODENAME.finditer(text):
            _add(cands, seen, sid, m.group(0), "codename", "strong", _snippet(text, *m.span()))
        for m in PAT_DURATION.finditer(text):
            _add(cands, seen, sid, m.group(0), "duration", "review_weak", _snippet(text, *m.span()))
        for m in PAT_RANK.finditer(text):
            raw = m.group(0).strip()
            if raw.endswith("%"):   # explicit percentile cutoff -> proprietary
                _add(cands, seen, sid, raw, "rank_percentile", "strong", _snippet(text, *m.span()))
            else:                   # bare count (top-3 / top-200) -> public-ish, excluded
                _add(cands, seen, sid, raw, "rank", "review_weak", _snippet(text, *m.span()))
        # --- apply human-ratified curation (DROP / RENAME / RECOVER) ---
        curated = []
        for c in cands:
            key = (sid, c["literal_normalized"])
            if key in S1_DROP:
                continue
            if key in S1_RENAME:
                new = S1_RENAME[key]
                c = {**c, "literal_normalized": new, "literal_raw": new,
                     "pattern_type": c["pattern_type"] + "_anchored"}
            curated.append(c)
        for lit, ptype, snip in S1_RECOVER.get(sid, []):
            norm = normalize(lit)
            if any(cc["literal_normalized"] == norm for cc in curated):
                continue
            curated.append({"secret_id": sid, "literal_raw": lit, "literal_normalized": norm,
                            "pattern_type": ptype, "specificity": "strong", "source_snippet": snip})
        # annotate match-set membership: strong -> included; review_weak -> excluded
        for c in curated:
            c["in_match_set"] = (c["specificity"] == "strong")
        out.append({"secret_id": sid, "level": s.get("level"), "category": s.get("category"),
                    "text": text, "candidates": curated})
    return out


def emit_candidates():
    secrets = [json.loads(l) for l in open(SECRETS_JSONL, encoding="utf-8")]
    per_secret = extract_candidates(secrets)

    n_total = len(per_secret)
    n_strong = [d for d in per_secret if any(c["specificity"] == "strong" for c in d["candidates"])]
    n_ge2_strong = [d for d in per_secret
                    if sum(1 for c in d["candidates"] if c["specificity"] == "strong") >= 2]
    n_zero = [d for d in per_secret if not d["candidates"]]
    n_zero_strong = [d for d in per_secret
                     if not any(c["specificity"] == "strong" for c in d["candidates"])]

    coverage = {
        "n_secrets": n_total,
        "secrets_with_ge1_strong_literal": len(n_strong),
        "secrets_with_ge2_strong_literals_cooccurrence_eligible": len(n_ge2_strong),
        "secrets_with_zero_candidates": len(n_zero),
        "secrets_with_zero_strong_candidates": len(n_zero_strong),
        "zero_strong_secret_ids": [d["secret_id"] for d in n_zero_strong],
        "total_candidates": sum(len(d["candidates"]) for d in per_secret),
        "total_strong": sum(1 for d in per_secret for c in d["candidates"] if c["specificity"] == "strong"),
        "total_review_weak": sum(1 for d in per_secret for c in d["candidates"] if c["specificity"] == "review_weak"),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "task": "S1 parameter-presence literal candidates (Phase 1a, R1=b re-extraction)",
        "source": "data/secrets/secrets.jsonl",
        "status": "AWAITING_HUMAN_REVIEW — prune public-ish candidates before freezing in Phase 1b",
        "normalizer": "symbol/word-op/unit/period folding only; NO decimal<->percent (R5)",
        "coverage": coverage,
        "per_secret": per_secret,
    }
    json.dump(payload, open(CAND_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Markdown for human review
    lines = ["# S1 literal candidates (Phase 1a) — REVIEW BEFORE FREEZE\n",
             f"Source: `data/secrets/secrets.jsonl` | re-extracted (R1=b) | normalizer: symbol/word-op/unit/period only (R5)\n",
             "## Coverage (this number goes to paper limitations)\n",
             f"- S1 covers **{coverage['secrets_with_ge1_strong_literal']}/{coverage['n_secrets']}** secrets "
             f"(≥1 strong proprietary literal).",
             f"- co-occurrence (≥2 strong) eligible: **{coverage['secrets_with_ge2_strong_literals_cooccurrence_eligible']}/{coverage['n_secrets']}**.",
             f"- **{coverage['secrets_with_zero_strong_candidates']}** secrets have NO strong literal (S1 cannot cover): "
             f"{coverage['zero_strong_secret_ids']}",
             f"- totals: {coverage['total_strong']} strong, {coverage['total_review_weak']} review-weak candidates.\n",
             "## Candidates per secret\n",
             "Legend: **strong** = operator+value / codename / %+qualifier (low FPR); "
             "_review_weak_ = bare duration/rank (prune if public).\n"]
    for d in per_secret:
        if not d["candidates"]:
            lines.append(f"### {d['secret_id']} [{d['level']}/{d['category']}] — ⚠️ NO candidates")
            lines.append(f"> {d['text']}\n")
            continue
        lines.append(f"### {d['secret_id']} [{d['level']}/{d['category']}]")
        lines.append(f"> {d['text']}\n")
        lines.append("| literal (normalized) | raw | type | specificity | snippet |")
        lines.append("|---|---|---|---|---|")
        for c in d["candidates"]:
            lines.append(f"| `{c['literal_normalized']}` | {c['literal_raw']} | {c['pattern_type']} "
                         f"| {'**strong**' if c['specificity']=='strong' else '_weak_'} | {c['source_snippet']} |")
        lines.append("")
    open(CAND_MD, "w", encoding="utf-8").write("\n".join(lines))

    print(f"Wrote {CAND_JSON}")
    print(f"Wrote {CAND_MD}")
    print("\n=== COVERAGE ===")
    for k, v in coverage.items():
        print(f"  {k}: {v}")


# -----------------------------------------------------------------------------
# MATCHER (Phase 1b-step2). Operates on the FROZEN strong-literal set
# (in_match_set=true) from s1_literals_candidates.json. Same normalizer as
# extraction; exact normalized-substring match. S1 is a literal matcher:
# it closes verbatim under-reporting for secrets that have a clean proprietary
# literal; it does NOT catch paraphrase and cannot cover zero-strong secrets.
# -----------------------------------------------------------------------------
_FROZEN_CACHE = None


def load_frozen_literals(path=CAND_JSON):
    """Return {secret_id: [normalized strong literals]} for in_match_set candidates."""
    global _FROZEN_CACHE
    if _FROZEN_CACHE is not None:
        return _FROZEN_CACHE
    data = json.load(open(path, encoding="utf-8"))
    frozen = {}
    for d in data["per_secret"]:
        lits = sorted({c["literal_normalized"] for c in d["candidates"]
                       if c.get("in_match_set")}, key=len, reverse=True)
        if lits:
            frozen[d["secret_id"]] = lits
    _FROZEN_CACHE = frozen
    return frozen


def check(text, secret_id, frozen=None):
    """Offline matcher against ONE target secret's frozen literals.
    Returns both single-hit and co-occurrence determinations."""
    frozen = frozen if frozen is not None else load_frozen_literals()
    norm = normalize(text)
    lits = frozen.get(secret_id, [])
    matched = [lit for lit in lits if lit and lit in norm]
    n = len(matched)
    return {
        "secret_id": secret_id,
        "matched_literals": matched,
        "n_matched": n,
        "hit_single": n >= 1,
        "hit_cooccurrence": n >= 2,
    }


def check_all(text, frozen=None):
    """Runtime matcher against ALL secrets (engine does not know the target).
    Returns aggregate hit flags (both modes) + per-secret matches."""
    frozen = frozen if frozen is not None else load_frozen_literals()
    norm = normalize(text)
    by_secret = {}
    for sid, lits in frozen.items():
        matched = [lit for lit in lits if lit and lit in norm]
        if matched:
            by_secret[sid] = matched
    hit_single = any(len(m) >= 1 for m in by_secret.values())
    hit_cooccurrence = any(len(m) >= 2 for m in by_secret.values())
    return {
        "hit_single": hit_single,
        "hit_cooccurrence": hit_cooccurrence,
        "by_secret": by_secret,
        "n_secrets_hit_single": sum(1 for m in by_secret.values() if len(m) >= 1),
        "n_secrets_hit_cooccurrence": sum(1 for m in by_secret.values() if len(m) >= 2),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-candidates", action="store_true",
                    help="Phase 1a: re-extract literal candidates from secrets.jsonl and write review files")
    args = ap.parse_args()
    if args.emit_candidates:
        emit_candidates()
    else:
        ap.error("Phase 1a: only --emit-candidates is available; matcher arrives in Phase 1b after review.")


if __name__ == "__main__":
    main()
