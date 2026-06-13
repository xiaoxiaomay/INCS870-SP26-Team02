#!/usr/bin/env python3
"""R4-d splice: v13_1 + all R-fragments -> v14. Deterministic, anchor-based, asserted."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
def rd(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()

V13 = "sentinelflow_journal_v13_1.tex"
T = rd(V13)
report = []

def between(s, a, b, inc_a=True, inc_b=True):
    i = s.index(a); j = s.index(b, i)
    return s[(i if inc_a else i+len(a)):(j+len(b) if inc_b else j)]

def after(s, a):
    i = s.index(a); return s[i+len(a):]

# ---- extract fragment sub-parts ----
def strip_header(s):
    """drop the leading contiguous %-comment + blank block (the fragment header),
    so commented examples like '\\begin{abstract}...' don't collide with real content."""
    lines = s.splitlines(keepends=True)
    k = 0
    while k < len(lines) and (lines[k].lstrip().startswith("%") or lines[k].strip() == ""):
        k += 1
    return "".join(lines[k:])

r4a = strip_header(rd("r4a_abstract_contributions.tex"))
ABSTRACT = between(r4a, r"\begin{abstract}", r"\end{abstract}")
KEYWORDS = between(r4a, r"\begin{IEEEkeywords}", r"\end{IEEEkeywords}")
CONTRIB  = between(r4a, r"\subsection{Summary of Contributions}", r"\end{itemize}")
r4c2 = rd("r4c2_intro_conclusion.tex")
INTRO = between(r4c2, "(A) INTRO: frontier keyword sentence (insert after contributions list) ----",
                "% ---- (B) CONCLUSION", inc_a=False, inc_b=False).strip()
CONCL = after(r4c2, "(B) CONCLUSION: full replacement body ----").strip()
r4c = rd("r4c_limitations.tex")
NEWPARAS = between(r4c, "NEW PARAGRAPHS (append inside Sect:VI_1_Limitations) ----",
                   "% ---- REPLACEMENT", inc_a=False, inc_b=False).strip()
CONSTRUCT = (r"\paragraph{Construct validity (updated for the primary measurements)}"
             + after(r4c, r"\paragraph{Construct validity (updated for the primary measurements)}")).strip()
R2, R3, R3S = rd("r2_sectionIII_testbed_fragment.tex"), rd("r3_sectionIV_dseries_fragment.tex"), rd("r3supp_tier0_fragment.tex")
R4B1, R4B2, R4B3 = rd("r4b1_primary_results.tex"), rd("r4b2_sensitivity.tex"), rd("r4b3_salami.tex")

def cut(start, end, repl, name, inc_end=True):
    global T
    assert T.count(start) >= 1, f"{name}: start anchor missing"
    i = T.index(start); j = T.index(end, i)
    j = j + len(end) if inc_end else j
    T = T[:i] + repl + T[j:]
    report.append(f"{name}: DONE (cut {j-i} chars -> {len(repl)})")

def ins_before(anchor, frag, name):
    global T
    assert T.count(anchor) >= 1, f"{name}: anchor missing"
    i = T.index(anchor)
    T = T[:i] + frag + "\n\n" + T[i:]
    report.append(f"{name}: DONE (inserted {len(frag)} chars before anchor)")

# ===== [D1] abstract + keywords =====
cut(r"\begin{abstract}", r"\end{abstract}", ABSTRACT, "[D1] abstract")
cut(r"\begin{IEEEkeywords}", r"\end{IEEEkeywords}", KEYWORDS, "[D1] keywords")
# ===== [D2] Summary of Contributions (through the stale 'Experimental detail...' para) =====
cut(r"\subsection{Summary of Contributions}",
    "reported in Section~\\ref{Sect:Experimental_Procedure_Performance_Evaluation} and the public repository.",
    CONTRIB, "[D2] contributions")
# ===== [E] intro frontier sentence (before Roadmap) =====
ins_before(r"\subsection{Roadmap}", INTRO, "[E] intro frontier")
# ===== [F-III] r2 testbed replaces Confidential Strategy Assets subsubsection =====
cut(r"\subsubsection{Confidential Strategy Assets}",
    "This triplet design creates a precise sensitivity gradient for evaluating the system's discrimination ability.",
    R2, "[F-III] r2 testbed")
# ===== [C1+C2+F-IV+G] replace old PathA block with the full new ordered IV block =====
NEW_IV = "\n".join([R3, R3S, R4B1, R4B3, R4B2]) + "\n"
cut(r"\subsection{Isolation-Failure Defense Validation}",
    r"\subsection{Encoder Choice as a Defense Lever}",
    NEW_IV + r"\subsection{Encoder Choice as a Defense Lever}",
    "[C/F-IV/G] D-series+Tier0+Layer1+salami+Layer2(PathA)", inc_end=True)
# ===== [B1] limitations new paragraphs before Threats to validity =====
ins_before(r"\paragraph{Threats to validity}", NEWPARAS, "[B1] limitations paragraphs")
# ===== [B2] construct-validity replacement =====
cut("First, \\emph{construct validity}:",
    "Second, \\emph{external validity}:",
    CONSTRUCT + "\n\n" + "Second, \\emph{external validity}:",
    "[B2] construct validity", inc_end=True)
# ===== [A] conclusion body replacement =====
cut("This paper presented SentinelFlow, an inline AI security gateway designed",
    "retargets to new domains through configuration alone.",
    CONCL, "[A] conclusion body")

# safety: corpus_v2 must be escaped in body (fragments already use corpus\_v2)
raw_unescaped = T.count("corpus_v2") - T.count("corpus\\_v2")
report.append(f"corpus_v2 raw (unescaped) occurrences remaining: {raw_unescaped}")

open(os.path.join(ROOT, "sentinelflow_journal_v14_draft.tex"), "w", encoding="utf-8").write(T)
report.append(f"WROTE v14: {len(T)} chars")
print("\n".join(report))
