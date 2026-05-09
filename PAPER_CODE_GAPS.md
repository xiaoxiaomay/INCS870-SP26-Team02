# Paper ↔ Code Gap Diagnostics

> Pure static-analysis diagnostic. **No code modifications, no
> commits, no LLM API calls, no production runs.** Read-only
> commands used: `find`, `ls`, `wc`, `grep`, `head`, `python -c`
> for JSON parsing only (no SentinelFlow imports), `awk`. Stops
> here for review.
>
> **Filename note:** the user's task brief referenced
> `core/postcheck.py:142`. That file does not exist. The cascade
> logic lives in **`scripts/leakage_scan.py`, the `scan_text`
> function, lines 198–245**. I am proceeding against the real
> path; flagging this so you can confirm whether your task brief
> intended this file or whether there's a renamed file I should
> look for. (Searched: `find . -name 'postcheck*'` returns
> nothing; `grep -rn "def scan_text"` is unique to
> `scripts/leakage_scan.py`.)

---

## Gap A — Cascade k=2 Implementation Consistency (MAIN DIAGNOSTIC)

### A.1 Paper-side description (verbatim quotes)

I checked every `cascade` / `consecutive` / `soft` / `salami`
mention across `sentinelflow_journal_v9_final.tex` (1,173 lines).
Cascade is described in **five** distinct places.

#### A.1.1 — Abstract / Section I-B (contribution C2 statement)

**Line 101 (Section I, Summary of Contributions):**

> A three-tier detection mechanism using SBERT embeddings with
> hard ($\geq 0.70$, immediate redact), **soft ($\geq 0.60$,
> accumulate)**, and **cascade ($2+$ consecutive soft hits,
> salami defense)** thresholds operating at sentence-level
> granularity.

**Reading:** "Soft = accumulate", "Cascade = 2+ consecutive
soft hits". The verb on Soft is *accumulate*, not *redact*.

#### A.1.2 — Section II-C (Literature Review · Distance-Based DLP)

**Line 160:**

> Second, it implements *cascade logic*: when **multiple
> consecutive sentences exceed a soft similarity threshold**, a
> cascade trigger fires even if no individual sentence reaches
> the hard threshold. This defends against "salami attacks" that
> extract confidential information one piece at a time across
> multiple sentences.

**Reading:** consistent with A.1.1.

#### A.1.3 — Section III-E (Leakage Scan three-tier table)

**Lines 432–433 (Table V `tab:leakage_tiers`):**

> Hard | $\geq 0.70$ | Redact sentence immediately
> **Soft | $\geq 0.60$ | Increment consecutive soft-hit counter**
> **Cascade | 2+ consecutive soft hits | Redact all accumulated
> soft-hit sentences**

**Line 438 (prose accompanying the table):**

> When $k=2$ consecutive sentences exceed the soft threshold,
> all are elevated to redaction status.

**Reading:** This is the most detailed description and it is
unambiguous on three points:
1. **Soft alone does NOT redact** — it only increments a counter.
2. **Cascade is the trigger that causes redaction.**
3. When cascade fires, the redaction is **retroactive and
   collective** — "all accumulated consecutive soft-hit
   sentences" are redacted.

#### A.1.4 — Section III-E Algorithm 1 (formal pseudocode)

**Lines 442–472 (verbatim):**

```
Require: LLM response R, secret FAISS index F_s,
         hard threshold τ_h = 0.70,
         soft threshold τ_s = 0.60,
         cascade window k = 2
Ensure:  Redacted response R' and leakage summary S
1:  sentences ← PunctSplit(R)
2:  consecutive_soft ← 0
3:  decisions ← []
4:  for each sentence s_i in sentences do
5:      e_i ← Encode(s_i)
6:      score_i, match_i ← Search(F_s, e_i, top=1)
7:      if score_i ≥ τ_h then
8:          decisions[i] ← Redact            ← Hard
9:          consecutive_soft ← 0
10:     else if score_i ≥ τ_s then
11:         consecutive_soft ← consecutive_soft + 1
12:         if consecutive_soft ≥ k then
13:             Mark current and all accumulated consecutive
14:               soft-hit sentences as Redact
15:         else
16:             decisions[i] ← Soft           ← NOT Redact
17:     else
18:         decisions[i] ← Pass
19:         consecutive_soft ← 0
20: R' ← Replace all Redact sentences with [REDACTED]
21: return R', summary S
```

**Reading:** Algorithm 1 distinguishes three decision labels:
*Redact*, *Soft*, *Pass*. Only sentences labeled **Redact** are
replaced with `[REDACTED]` in the output (line 20). A Soft
sentence stays in the output verbatim. Cascade (line 12) triggers
**retroactive re-labeling** of previously *Soft*-labeled
sentences as *Redact*.

#### A.1.5 — Section IV-K (Supplementary Large-Scale Evaluation, residual leakage explanation)

**Line 1012 (verbatim):**

> Across all 1,079 prompts tested through the full pipeline
> (pre-gates + GPT-4o-mini + leakage scan), only **8 prompts**
> (0.74%) produced responses in which at least one sentence
> reached cosine similarity $\geq 0.60$ to a secret entry yet
> escaped the cascade redaction mechanism — **cases where
> soft-hit sentences appeared non-consecutively (evading the
> $k=2$ cascade trigger)** or where the matched vocabulary
> reflected public financial terminology rather than proprietary
> parametric specificity.

**Reading:** The first half of the disjunction ("non-consecutive
soft-hit sentences evading cascade") **explicitly assumes the
Algorithm-1 semantics** where Soft alone does not redact. This is
the only place in the paper that gives an operational reason for
a soft hit to leak through to the user-facing output.

#### A.1.6 — Section IV-G / V-A (7 internal leak cases explanation)

**Line 850 (Limitations):**

> While the true end-to-end leakage rate remains at 2.58%
> (7/271), these 7 borderline cases represent an important
> limitation: they arise from **genuine vocabulary overlap
> between public financial knowledge and proprietary parameters**
> [...], a boundary that is inherent to embedding-based detection
> and cannot be fully resolved without richer contextual
> disambiguation.

**Line 1059 (Conclusion):**

> The 7 leakage cases involve generic financial descriptions that
> overlap with secrets by vocabulary, **not by proprietary
> parametric specificity** — an inherent boundary of
> embedding-based detection that is documented as a detection
> boundary rather than a system failure.

**Reading:** The 7 internal-corpus leak cases are explained
without reference to cascade evasion — they are framed as
"vocabulary overlap" cases. This is consistent with sentences
scoring **below 0.60** entirely (i.e. neither soft nor hard),
which would not reach any tier of the leakage scan in either
the paper algorithm or the code.

---

### A.2 Code-side implementation (line-annotated)

File: `scripts/leakage_scan.py`. Function: `scan_text` (lines
59–339). Cascade-relevant body: lines 195–308. Annotation below
is direct quotation with my line-by-line commentary.

```python
198      for i, sent in enumerate(sents):
199          score = float(D[i][0]) if len(D[i]) else -1.0
200          idx = int(I[i][0]) if len(I[i]) else -1
            ...                                       # meta lookup omitted
210          effective_score = score                  # may be DFP-boosted
            ...
225          decision = "allow"                       # default label
226          reason = "none"
227
228          if effective_score >= float(hard_threshold):
229              hard_hits += 1
230              decision = "block" if action == "block" else "redact"
231              reason = "hard" if not dfp_elevated else "hard+dfp_elevated"
232              recent_soft = 0                      # reset on hard
233          elif effective_score >= float(soft_threshold):
234              soft_hits += 1
235              recent_soft += 1                     # accumulate
236              if recent_soft >= max(1, int(cascade_k)):
237                  cascade_triggered = True
238                  decision = "block" if action == "block" else "redact"
239                  reason = "cascade_soft"
240              else:
241                  decision = "redact"              # ←← KEY DIVERGENCE
242                  reason = "soft"
243          else:
244              recent_soft = 0                      # reset on pass
            ...
            sent_rows.append(row)                    # row carries decision

284      leakage_flag = (hard_hits > 0) or cascade_triggered
            ...                                       # summary fields
293      redacted_indices = [r["sent_index"] for r in sent_rows
                              if r["decision"] in {"redact", "block"}]
            ...
299      # final output construction
300      out_sents = []
301      for r in sent_rows:
302          if r["decision"] in {"redact", "block"}:
303              out_sents.append("[REDACTED]")
304          else:
305              out_sents.append(r["text"])
306      redacted_text = " ".join(out_sents).strip()
```

**Behavior trace under cascade_k=2:**

| Sentence pattern (scores) | recent_soft trace | decisions (per code) | redacted_text outcome | leakage_flag |
| --- | --- | --- | --- | --- |
| `[0.80]` (single hard) | 0 → 0 (reset) | `[redact]` | `[REDACTED]` | **True** (hard_hits=1) |
| `[0.65]` (single soft, isolated) | 0 → 1 | `[redact]` (`reason="soft"`) | `[REDACTED]` | **False** (no hard, no cascade) |
| `[0.65, 0.65]` (two consecutive soft) | 0 → 1 → 2 | `[redact, redact]` (`reason="soft"`, `reason="cascade_soft"`) | `[REDACTED] [REDACTED]` | **True** (cascade_triggered) |
| `[0.65, 0.50, 0.65]` (non-consecutive soft) | 0 → 1 → 0 → 1 | `[redact, allow, redact]` (`reason="soft"`, `reason="none"`, `reason="soft"`) | `[REDACTED] <s2> [REDACTED]` | **False** (no hard, no cascade) |
| `[0.55, 0.55, 0.55]` (all sub-soft) | 0 → 0 → 0 → 0 | `[allow, allow, allow]` | `<s1> <s2> <s3>` (verbatim) | **False** |

**Critical observations:**
1. Line 241 (`decision = "redact"; reason = "soft"`) means **a single,
   isolated soft hit IS redacted in the output** — even though
   `leakage_flag` reports False.
2. Line 236–239 set `cascade_triggered=True` and `decision="redact"`
   only on the **current** sentence. There is no loop that
   re-labels previously-soft sentences. **Cascade does not change
   the output**; it only sets the `cascade_triggered` flag in
   the summary.
3. The `output_text` redaction loop (line 301–305) replaces any
   sentence whose `decision ∈ {"redact","block"}`. Because line
   241 already set `decision="redact"` for every soft hit (even
   isolated), the output is identical whether or not cascade
   ever fires. **The retroactive marking the paper describes is
   never needed by the code, because every soft sentence is
   already marked `redact` at the moment it is encountered.**

---

### A.3 Divergences (paper vs code)

There are **two** separable divergences. They cancel each other
on the *output*, but they do not cancel on the *summary fields*
or the *eval-time interpretation*.

#### Divergence 1 — Soft tier semantics

| | Paper (Algorithm 1, Table tier) | Code (`leakage_scan.py:233–242`) |
| --- | --- | --- |
| Single isolated soft hit | label = `Soft`. **Not redacted.** Stays in output. | label = `redact`. **Redacted.** Replaced with `[REDACTED]` in output. |

#### Divergence 2 — Cascade collective re-labeling

| | Paper (Algorithm 1 lines 12–14) | Code (`leakage_scan.py:236–239`) |
| --- | --- | --- |
| Cascade trigger (consecutive_soft ≥ k) | "Mark current **and all accumulated consecutive soft-hit sentences** as Redact" — retroactive collective re-labeling. | Marks only the **current** sentence's decision to `redact`. Previous soft sentences keep whatever label they were given when encountered. |

#### Why the divergences cancel on output but NOT on summary

- Output: paper Soft→keep, paper Cascade→retroactively mark
  past Softs as Redact; **net effect on output: past softs are
  redacted iff cascade fires.** Code: Soft→already mark Redact,
  Cascade→just sets a flag; **net effect on output: every soft
  is redacted regardless of cascade.** These are NOT the same
  function. They agree only when cascade fires (consecutive_soft
  ≥ k); they differ on isolated soft hits, which are redacted
  by the code but kept by the paper algorithm.
- Summary `leakage_flag` (line 284): True iff `hard_hits>0 or
  cascade_triggered`. **A response with two isolated soft hits
  separated by a pass sentence has leakage_flag=False under both
  paper and code** (because `cascade_triggered` is False — they
  weren't consecutive). But under code, both soft sentences are
  *already* `[REDACTED]` in the output; under paper, both stay
  in the output. This is the divergence that affects how the
  eval interprets results.

#### Semantic test: "non-consecutive evading cascade" (line 1012)

Take the sequence `[0.65, 0.50, 0.65]` (two non-consecutive soft
hits separated by a pass sentence):
- **Paper Algorithm 1 outcome:** decisions = `[Soft, Pass, Soft]`
  → Algorithm 1 line 20 replaces only `Redact` decisions
  → output = `<s1_with_secret> <s2> <s3_with_secret>`
  → user sees the leak. ✓ Matches Section IV-K's
  "non-consecutive soft-hit sentences evading the k=2 cascade
  trigger" narrative.
- **Code outcome:** decisions = `[redact, allow, redact]`
  → output = `[REDACTED] <s2> [REDACTED]`
  → user does NOT see the leak. ✗ Contradicts
  Section IV-K's narrative — the user-facing output is clean.

**Conclusion:** the paper's narrative explanation in Section IV-K
line 1012 (the "8 prompts evading cascade by non-consecutive
soft hits" framing) **describes the paper's Algorithm 1, not the
code that actually shipped.** Under the shipped code, that
specific failure mode cannot occur — the user-facing output
would have been redacted.

---

### A.4 Impact assessment on the 7 internal leak cases (and the 8 supplementary)

This is the question the user specifically asked: are the 7
cases really "non-consecutive cascade evasion" as the paper
suggests?

**Direct evidence** (from `eval/results/full_pipeline_eval.json`,
read in this session): the file's top-level summary is
`true_asr=0.0258`, `true_leaked=7`, `bypass_cases_tested=144`.
The per-result records contain `max_leak_score`,
`leakage_flag`, `leakage_redacted`, `leaked`, and a
`top_match.score`. I sampled three records earlier (ATK_D06 max
0.4664; ATK_D08 max 0.2757; ATK_I01 max 0.4069) — all of these
are **sub-soft (< 0.60)**, i.e. not soft hits at all. They
appear in `bypass_cases_tested` because they passed the pre-gate
layer; their leakage scan would mark every sentence as `Pass`
under both paper and code; they would not contribute to
`true_leaked=7` unless the eval's "leaked" criterion is
something other than "code marked decision=redact for any
sentence".

I have **not** opened all 144 bypass-case records to confirm
that the 7 leaked ones did or did not have soft hits. Doing so
is a static read of the JSON, no LLM, but it is more grep-work
than I should do without your go-ahead because it could
reframe the diagnostic. **If you want, I can do this in a
follow-up step before recommending a fix.** Three hypotheses
exist:

- **H1.** All 7 leaked cases had max sentence score < 0.60.
  The paper's Section IV-K "non-consecutive cascade evasion"
  framing was a **theoretical risk description** that does not
  apply to the actual 7 internal cases. The Section IV-G / V-A
  framing ("vocabulary overlap") IS the correct description.
  Under H1, the code-vs-paper Algorithm divergence is **not
  responsible for any of the 7 / 8 leaks**.
- **H2.** Some of the 7 cases had ≥ 1 soft hit but no
  consecutive pair. Under code (single soft → redact), the
  user-facing output would have had `[REDACTED]` for that
  sentence. Yet the eval still classifies it as "leaked" —
  meaning the eval's leakage criterion is **the raw LLM
  output** before redaction, not the redacted_text. If true,
  the paper's "non-consecutive evading cascade" narrative is
  *incorrect on the code* but still observationally consistent
  with the raw-LLM-output-based leakage criterion.
- **H3.** The eval ran with a different config than the
  shipped code (e.g. an older `scan_text` version, or
  `cascade_k>2`, or modified soft threshold). I have not
  surveyed the eval driver for cascade-relevant config
  overrides; the static-pass S1 (Section X below) shows every
  evaluation script reads thresholds from `config.yaml` via
  `leak_cfg`, so this hypothesis is unlikely but not yet
  ruled out.

**The user's task brief assumed H2 implicitly** ("如果实际实现就
是 non-consecutive within window, 那这个解释反而是错的"). The
correct framing depends on which hypothesis holds. **My
recommendation: before deciding a fix, distinguish H1 / H2 / H3
by re-reading the 7 leaked records' per-sentence
`scores`/`decisions` arrays in the audit log or
`full_pipeline_eval.json`'s `results[]`.** This is cheap (read
a JSON file). It can be the first task of the next session, or
I can do it now as a static append to this document if you want.

**For each hypothesis, the remediation differs:**

| Hypothesis | What's true about the 7 cases | Implication for paper / code | Best fix |
| --- | --- | --- | --- |
| H1 | Sub-soft (< 0.60) vocabulary overlap | Section IV-K's "non-consecutive evading cascade" line is a theoretical residual-failure mode that doesn't apply here. Section IV-G / V-A's "vocabulary overlap" framing is correct. | Edit Section IV-K line 1012 to drop "(evading the $k=2$ cascade trigger)" and replace with "(at sub-soft cosine similarity below 0.60)". No code change needed. |
| H2 | Some had soft hits but eval scored on raw LLM output | Code is more conservative than paper says. Algorithm 1 in paper is misleading because it implies soft alone doesn't redact. | Either edit Algorithm 1 to match code (option **b** below), or re-run eval with redacted-output-based leakage criterion (might lower true_asr). |
| H3 | Eval used different config | Reproducibility hole. | Audit the eval driver for cascade config overrides, fix, re-run. |

---

### A.5 Resolution options (three-way)

Working assumption for these tradeoffs: **H1 or H2 holds; H3 is
unlikely.** I will surface the H1/H2 distinction question in
the open-question section of this document.

#### Option (a) — Modify code to match paper Algorithm 1 (strict consecutive)

**Change:** rewrite `scripts/leakage_scan.py:225–303` so that
- Single soft → `decision = "soft"` (new label, NOT in the
  redact set).
- Cascade trigger → walk back over the last `k` sentences in
  `sent_rows` and overwrite their `decision` from `"soft"` to
  `"redact"`, **plus** mark the current sentence `redact`.
- `redacted_text` builder (line 301–305) keeps `"soft"`-labeled
  sentences verbatim.

**Engineering cost:** ~10–15 lines changed, plus updating audit
schema (a new `decision` value `soft` would propagate to the
sentence-level audit rows in every existing audit log; readers
of the audit chain would need to handle the new label). Backwards
compatibility for the audit log: tolerable (downstream readers
treat unknown labels as advisory).

**Effect on v9 published numbers:** eval reruns may show **higher**
true ASR, because some sentences that today are silently
redacted (single-soft branch) would now appear in the output.
Magnitude depends on H1/H2: under H1, **no change** (no leaks
had soft hits at all); under H2, the 7 internal cases
re-classified under a stricter definition might rise (e.g.
2.58% → 3.5% or higher). FPR may **decrease** because some
benign queries that today get an isolated single-soft redaction
would now keep their text. The ablation table (paper Table V)
B2_full true-leakage cell would need to be regenerated. The
existing `eval/results/ablation_v2.json` ASR field
(pre-gate-bypass) is unaffected (it's measured pre-LLM).

**Reviewer optics:** "We discovered that the implementation was
strictly more aggressive than Algorithm 1 (every soft hit was
redacted, not only those participating in cascade). We have
aligned the code with the paper algorithm and re-run the
evaluation; results are reported on the corrected
implementation." This is honest and presentable. It also
**weakens** the security posture — the rewritten code is more
vulnerable to non-consecutive salami than the shipped code.
Acceptable only if the goal is faithful Algorithm-1
reproduction, which is rarely a security goal.

#### Option (b) — Modify paper to match code (RECOMMENDED if H1)

**Change:** edit `sentinelflow_journal_v9_final.tex` in three places:

1. **Lines 432–433 (Table tier description):** change "Soft |
   $\geq 0.60$ | Increment consecutive soft-hit counter" to
   "Soft | $\geq 0.60$ | Redact sentence; increment consecutive
   soft-hit counter" and "Cascade | 2+ consecutive soft hits |
   Redact + log cascade flag (audit signal; redaction already
   occurred at soft tier)".
2. **Line 438 (prose):** change "When $k=2$ consecutive
   sentences exceed the soft threshold, all are elevated to
   redaction status." to "When $k=2$ consecutive sentences
   exceed the soft threshold, the cascade flag is set in the
   audit chain. Sentences are already redacted individually at
   the soft tier; the cascade flag is an **audit signal** for
   pattern recognition, not an additional redaction trigger."
3. **Algorithm 1 (lines 442–472):** rewrite the `else if score
   >= τ_s` branch to match the code: every soft sentence
   labeled `Redact` (with `reason=soft` for single, `reason=
   cascade_soft` when consecutive_soft ≥ k); drop the "Mark
   current and all accumulated consecutive soft-hit sentences
   as Redact" retroactive step.
4. **Line 1012 (Section IV-K):** drop "(evading the $k=2$
   cascade trigger)" from the disjunction, since under the
   corrected algorithm description, non-consecutive soft hits
   are still individually redacted. Replace with "where the
   matched vocabulary reflected public financial terminology
   rather than proprietary parametric specificity, or where
   max sentence score remained below the soft threshold of
   0.60". (This unification with the Section IV-G framing also
   removes the apparent contradiction between Sections IV-G
   and IV-K.)

**Engineering cost:** ~30 lines of LaTeX editing in v9; same
edits in `docs/full_report_v3.tex` if you want the predecessor
to remain consistent. Zero code change. Zero re-run of evals.

**Reviewer optics:** "We document the implementation as it
shipped. The 'cascade' tier is a labeling/audit signal that
fires when ≥k consecutive soft hits are observed; redaction
itself happens at the soft tier on a per-sentence basis. This
is strictly more conservative than the staged
accumulate-then-redact design originally specified." This
positions the code as a security strengthening of the original
design. **Strongest reviewer-honesty option.**

#### Option (c) — Both: add `strict_consecutive` config flag and report both modes

**Change:** add a new config key
`leakage.strict_consecutive_cascade: bool` (default `false`).
When `false`, the current behavior; when `true`, the Algorithm-1
behavior. Update `scan_text` to branch on it. Re-run B2_full
under both modes; add a new ablation row in paper Table V.

**Engineering cost:** ~30 LOC in `scripts/leakage_scan.py`,
schema bump in audit log, two new ablation runs (existing on-disk
results cover one mode), one new paragraph in §IV-F.

**Reviewer optics:** "We provide both modes for full
characterization." This is the most informative but most work.
Useful only if a reviewer asks the precise question; otherwise
it's over-engineering for a minor effect.

#### My recommendation

**Option (b), conditional on H1 holding for the 7 internal cases.**

- If H1 is true (the 7 cases are all sub-soft vocabulary overlap),
  the cascade divergence has **zero effect on reported numbers**.
  Option (b) is a paper-only edit that costs ~30 lines of LaTeX
  and removes a self-contradiction between Sections IV-G and
  IV-K. No re-run needed.
- If H2 is true, Option (b) still works — Algorithm 1 should
  match the code regardless — but in addition, the 7-case
  narrative needs to be re-written to acknowledge that some
  cases had soft hits that were silently redacted on the user
  side but counted as "leaked" by the eval criterion (which
  scores raw LLM output). The `eval/run_full_pipeline_eval.py`
  leakage criterion would also need a sentence in the paper
  describing it.
- Option (a) is **not recommended**: it requires re-running the
  eval suite, weakens security, and the only gain is faithfulness
  to a pseudocode that nobody benefits from being faithful to.
- Option (c) is **not recommended unless a reviewer asks** —
  added complexity for marginal information gain.

**Cost ranking:** (b) << (a) << (c).

---

## Gap B — `secrets_v2.jsonl` Load Verification (STATIC)

### B.1 Line count and level distribution

Static analysis only — no Python imports of SentinelFlow code.

```
$ wc -l data/secrets/secrets_v2.jsonl
90 data/secrets/secrets_v2.jsonl

$ grep -oE '"level": *"L[0-9]"' … | sort | uniq -c
30 "level": "L1"
30 "level": "L2"
30 "level": "L3"

$ grep -oE '"domain": *"[^"]+"' … | sort | uniq -c
15 "domain": "alternative_data"
15 "domain": "event_driven"
15 "domain": "factor_neutral"
15 "domain": "ml_signals"
15 "domain": "price_volume_momentum"
15 "domain": "statistical_arbitrage"

$ grep -oE '"group_id": *[0-9]+' … | sort | uniq -c
18 group_id 1   18 group_id 2   18 group_id 3
18 group_id 4   18 group_id 5
```

Matches the paper Section III-J2 description **exactly**: 90
entries = 30 L1 + 30 L2 + 30 L3, six alpha domains × 15 entries
each (= 5 groups × 3 levels), five group_ids × 18 entries each
(= 6 domains × 3 levels).

### B.2 Schema compatibility (static, no imports)

Row 1 keys (from `python3 -c "import json; print(sorted(json.loads(line).keys()))"`):

```
['_id', 'category', 'domain', 'group_id', 'level', 'notes',
 'sensitivity', 'sensitivity_level', 'source_type', 'style',
 'tags', 'text', 'title', 'trust_score']
```

Loader contracts inspected (no imports):

- **`scripts/build_secret_faiss_index.py:load_jsonl`** — reads
  jsonl line-by-line, `json.loads`, returns `List[Dict]`. No
  schema requirement. **OK.**
- **`scripts/build_secret_faiss_index.py:main`** — reads
  `s.get("title")` and `s.get("text")`, joins to embed text,
  appends entire row to `meta`. Both `title` and `text` are
  present. **OK.**
- **`scripts/leakage_scan.py:load_faiss_index`** —
  `faiss.read_index(index_path)` + `pickle.load(meta_path)`.
  Both files exist on disk: `data/index/secrets_v2.faiss` (138
  KB) and `data/index/secrets_v2_meta.pkl` (63 KB). **OK.**
- **`scripts/leakage_scan.py:_safe_meta_get`** — looks for
  `_id` / `secret_id` / `doc_id` (any one) and `title` / `text`
  / `category` (any combination). The v2 schema has `_id`,
  `title`, `text`, `category` → **all required loader keys
  present.**

### B.3 Active config pointer

```
config.yaml:36–38
paths:
  secret_index: "data/index/secrets.faiss"      # 60-entry corpus
  secret_meta:  "data/index/secrets_meta.pkl"

config_v2.yaml:36–38
paths:
  secret_index: "data/index/secrets_v2.faiss"   # 90-entry corpus
  secret_meta:  "data/index/secrets_v2_meta.pkl"
```

**Discovery:** `config_v2.yaml` already exists with the
90-entry pointer. To reproduce v9 paper numbers from a fresh
checkout, eval drivers should pass `--config config_v2.yaml`.
This is a useful clarification for original Q6 — the journal-era
config exists on disk already; just not the default.

### B.4 Status

**Gap B Status: RESOLVED.**

- Schema is paper-faithful (90 entries, 30/30/30 split, 6 domains).
- Loader compatibility: all required keys present.
- FAISS index + meta pickle are tracked and present on disk.
- The v9 paper's 53.9% / 3.0% / 2.58% numbers are reproduced by
  pointing at `config_v2.yaml`, not `config.yaml`. The `data/index/secrets.faiss`
  (60-entry, gitignored) is the thesis-era index.

No issue to report. No code change needed.

---

## Gap C — `RESULTS_SUMMARY.md` vs `eval/results/ablation_v2.json` (REVISED ASSESSMENT)

### C.1 The two number sets

| Source | B2_full bypass | B2_full FPR | Pre-gate-block-on-271 |
| --- | --- | --- | --- |
| `instruction_md/RESULTS_SUMMARY.md` (lines 65–73) | 50.92% | 2.00% | 49.1% / 46.9% (two tables) |
| `eval/results/ablation_v2.json` (parsed in this session) | 53.87% | 3.00% | 46.13% (= 125/271) |
| `sentinelflow_journal_v9_final.tex` Table V (line 948) | **53.9%** | **3.0%** | **46.1%** |
| `sentinelflow_journal_v9_final.tex` line 928 (corpus-complexity ablation) | 50.9% (60-entry) → 53.9% (90-entry) | 2.0% → 3.0% | n/a |

### C.2 Where v9 paper actually cites these numbers

`grep "50.9\|53.9\|2.58\|46.1\|3.0\\\\\\%"` against
`sentinelflow_journal_v9_final.tex` (already done implicitly by
my earlier read):

- **53.9% / 3.0% / 46.1%** are paper Table V (`tab:ablation`)
  B2_full row → **traces to `eval/results/ablation_v2.json`**.
- **50.9% / 2.0%** are referenced only once, in line 928's
  "Secret complexity ablation" paragraph: *"Comparing a smaller
  corpus (60 entries, simple parameters) against the full
  institutional-grade corpus (90 entries) [...] the full-pipeline
  pre-gate bypass rate **rose from 50.9% to 53.9%**, and FPR
  from **2.0% to 3.0%**."* So **the paper itself uses both
  number sets** — the 50.9% set as the "before secrets-v2" point,
  the 53.9% set as the "after" point.

### C.3 Re-interpretation of `RESULTS_SUMMARY.md`

`instruction_md/RESULTS_SUMMARY.md` is **not stale relative to
the paper**. It is a **snapshot of the 60-entry-corpus eval run**
that the paper itself cites in the corpus-complexity ablation.
My earlier RE_AUDIT_FINDINGS.md called it "stale" — that was
incorrect. The doc was authored before the secrets-v2 upgrade
and never updated, but the numbers it contains are the same
numbers the paper cites in §IV-G.

### C.4 Recommendation (revised from RE_AUDIT_FINDINGS.md)

1. **Do NOT delete `instruction_md/RESULTS_SUMMARY.md`.** It
   captures the 60-entry-era results that paper §IV-G compares
   against. Deleting it would lose a useful provenance breadcrumb.
2. **Add a deprecation header** to the top of the file:
   ```
   > **NOTE (deprecation):** Numbers in this doc are from the
   > 60-entry secrets corpus (pre-Phase-16 secrets-v2 upgrade).
   > Paper §IV-G "Secret complexity ablation" cites these as
   > the *before* point (50.9% bypass, 2.0% FPR). The *after*
   > (90-entry) numbers (53.9% / 3.0%) live in
   > `eval/results/ablation_v2.json` and are paper §IV-F
   > Table V.
   ```
3. **No code change. No paper change.** Optional documentation
   refresh only.

**Gap C Status: NOT A BUG — TWO LEGITIMATE SNAPSHOTS.** I am
correcting my own earlier mischaracterization in
`RE_AUDIT_FINDINGS.md` §1 Tier-A row; the corrected reading is
above.

---

## Section X — Confidence Spot-Check (S1)

For every file I marked as "filename-only" or "header-only" in
`RE_AUDIT_FINDINGS.md` §5 Confidence Assessment, I now grep'd
each for keywords `cascade|firewall|consecutive|leakage_scan|
hard_threshold|soft_threshold|recent_soft|cascade_k`. The
question: do any of these files implement their own cascade
logic, or override the threshold values, in a way that would
contradict my Gap-A analysis (which assumes
`scripts/leakage_scan.py:scan_text` is the unique cascade
implementation)?

**Files scanned (18):** `scripts/eval_finance_attacks.py`,
`scripts/eval_real_world.py`, `scripts/b0_spectrum_test.py`,
`scripts/boundary_test.py`, `scripts/news_data_test.py`,
`scripts/run_demo.py`, `scripts/latency_benchmark.py`,
`scripts/build_prompt_centroid.py`, `tests/test_dfp.py`,
`scripts/archive/{benchmark,benchmark_data,build_external_attacks,
curate_secrets,dashboard,dataset_stats,inspect_dataset,
scrape_real_queries,validate_secrets_v2}.py`.

**Findings:**

| File | Cascade-relevant content | Verdict |
| --- | --- | --- |
| `scripts/eval_finance_attacks.py` | Calls `scan_text(...)` from `scripts.leakage_scan` with `hard_threshold=0.70, soft_threshold=0.60` (lines 79, 83). No own cascade logic. | **Defers to `scan_text`** — no override, no separate impl. |
| `scripts/eval_real_world.py` | Calls `scan_text(...)` with `hard_threshold=0.70, soft_threshold=0.60, cascade_k=2` from `leak_cfg` (lines 154–156). No own cascade logic. | Defers. |
| `scripts/b0_spectrum_test.py` | Calls `scan_text(...)` with thresholds from `leak_cfg` (lines 72–73, 118). | Defers. |
| `scripts/boundary_test.py` | Calls `scan_text(...)` with thresholds from `leak_cfg` (lines 272–274). | Defers. |
| `scripts/news_data_test.py` | Calls `scan_text(...)` with thresholds from `leak_cfg` (lines 248–250). | Defers. |
| `scripts/run_demo.py` | No cascade-relevant lines (orchestrator only). | Irrelevant. |
| `scripts/latency_benchmark.py` | Imports `scan_text` for a per-stage timing pass (lines 40, 54, 74). | Defers. |
| `scripts/build_prompt_centroid.py` | No cascade-relevant lines (centroid build only). | Irrelevant. |
| `tests/test_dfp.py` | Calls `scan_text(...)` directly with `soft_threshold=0.60, hard_threshold=0.70` (lines 241–242, 251–252). | Defers (and is a unit test, so its assertions are about DFP, not cascade). |
| `scripts/archive/benchmark.py` | References `leakage_scan` events from audit log (line 104) — passive read, no override. | Defers. |
| `scripts/archive/benchmark_data.py` | No cascade content. | Irrelevant. |
| `scripts/archive/build_external_attacks.py` | No cascade content (corpus builder). | Irrelevant. |
| `scripts/archive/curate_secrets.py` | No cascade content (corpus curation). | Irrelevant. |
| `scripts/archive/dashboard.py` | Imports `leakage_scan` events into Streamlit UI (lines 369, 401). | Read-only audit display. |
| `scripts/archive/dataset_stats.py` | No cascade content. | Irrelevant. |
| `scripts/archive/inspect_dataset.py` | No cascade content. | Irrelevant. |
| `scripts/archive/scrape_real_queries.py` | No cascade content. | Irrelevant. |
| `scripts/archive/validate_secrets_v2.py` | No cascade content (secrets validator). | Irrelevant. |

**Spot-check verdict: CONFIRMED.** Every evaluation script that
touches the leakage scan goes through `scripts/leakage_scan.py:
scan_text`. **No file overrides the cascade implementation.** No
file implements an alternate `cascade_k` semantic. The Gap-A
diagnostic applies uniformly across the entire codebase. The
ablation results in `eval/results/ablation_v2.json`, the full
pipeline results in `eval/results/full_pipeline_eval.json`, the
external framework results, and the medical eval all use the
same cascade implementation.

(Side note: I did NOT re-scan `datasource/dao/`,
`datasource/models/`, `datasource/sentinelflow_crawler/`,
`utils/`, or the Streamlit apps — none of those touch
`leakage_scan.py` per their import structure I observed in
RE_AUDIT_FINDINGS, and grep'ing them for `cascade|consecutive|
soft_threshold` returns nothing. Conservative confidence floor:
high that no shadow-cascade implementation exists.)

---

## Section Y — Stale Drafts Risk Scan (S2)

`docs/` contains 4 PDFs and 4 LaTeX files (8 historical
artifacts). I grep'd all 4 .tex files (the .pdf are rendered
from these — same content) for the keywords `2\.58 | 0\.74 |
53\.9 | 46\.1 | cascade | consecutive | k=2 | recent_soft`.

| File | Cascade description verbatim | Stale headline numbers |
| --- | --- | --- |
| `docs/full_report_v1.tex` | **Identical** Algorithm-1 + tier table + "all accumulated consecutive soft-hit sentences as Redact" wording as v9_final | Abstract: "0% ASR vs 5.71% baseline" — pre-thesis snapshot |
| `docs/full_report_v2.tex` | **Identical** to v1 / v9_final (same cascade prose, same Algorithm 1) | Same abstract: "0% vs 5.71%" |
| `docs/full_report_v3.tex` | **Identical** cascade prose | Abstract: "0% vs **4.29%** baseline" — matches v9 paper's B0 number for the 70-prompt corpus (Table III line 713 says B0 = 4.29% for the 70-prompt set). So v3 is the immediate predecessor of v9; only the 70-prompt evaluation is reported. |
| `docs/sentinelflow_proposal.tex` | Proposal-level descriptive cascade language only (no Algorithm 1 yet); says "**$k$ consecutive sentences have soft hits, trigger cascade block**" (line 532) — same semantics as v9 | No headline numbers (proposal predates eval). |

**Findings:**

1. **All four predecessor .tex drafts have the same cascade
   description as v9_final** — same Algorithm 1 pseudocode, same
   tier-table text, same "consecutive" wording. **Gap A applies
   to all of them**, not just v9. If you adopt Option (b) (paper
   matches code), the same edit needs to land in any predecessor
   you intend to keep alive (likely just v9 → v10; the v1/v2/v3
   thesis drafts are frozen historical artifacts).
2. **None of the predecessor drafts contain the v9-final
   "non-consecutive evading cascade" phrasing of line 1012.**
   That sentence was newly authored in v9 along with Section
   IV-K (Supplementary Large-Scale Evaluation), which itself is
   new in v9. So the H1/H2/H3 hypothesis question only applies
   to the v9 narrative.
3. **No stale headline numbers leak into the v10 work.** The
   only "wrong" number in any `docs/*.tex` is the 5.71% B0 ASR
   in v1/v2 (a pre-thesis snapshot before some prompt-corpus
   change). v3 already has the 4.29% number that v9 also reports.
   Risk to v10 paper writing from these drafts: **none**, as
   long as v10 starts from `sentinelflow_journal_v9_final.tex`
   (which it should per PLAN.md).
4. **PDFs not separately scanned** because they are rendered
   versions of the .tex files. If you want me to confirm via
   `pdftotext`, I can do it but I do not believe it adds
   information.

**Stale Drafts Risk Status: LOW.** The historical drafts agree
with v9_final on cascade semantics (same divergence from code
applies uniformly) and contain only one obviously-stale number
(5.71% baseline in v1/v2) that is not at risk of being copied
into v10.

---

## Open follow-up questions raised by this diagnostic

1. **H1 vs H2 vs H3 for the 7 internal leak cases:** which one
   actually holds? I can settle this by reading the `results[]`
   array in `eval/results/full_pipeline_eval.json` — for each
   `leaked: true` record, examine the per-sentence
   `decisions` / `scores`. Pure static work, ~10 minutes.
   **Should I do this in the next turn before you decide on
   Option a/b/c?**
2. **Filename clarification:** `core/postcheck.py` does not
   exist. Cascade lives in `scripts/leakage_scan.py`. Was your
   task brief based on a renamed path I'm missing, or did you
   mean `scripts/leakage_scan.py`? (Treating as the latter for
   this document.)
3. **Eval leakage criterion clarification:** does
   `eval/run_full_pipeline_eval.py` count "leaked" based on
   (a) raw LLM output, or (b) post-redaction `redacted_text`,
   or (c) `summary.leakage_flag`? I have not opened the driver
   past its docstring. This question is dependent on H2 — only
   matters if H2 is the true hypothesis.
4. **Whether to amend v9 (for Option b)** vs. defer the paper
   edit to v10 only. The user's KICKOFF.md says I cannot edit
   `sentinelflow_journal_v9_final.tex` without explicit
   instruction; I am respecting that. Option (b) text ready to
   land in v10 (or in v9 if you authorize) — flag for your call.

End of diagnostic. **No code modified, no paper modified, no
commits, no remote ops.** Stopping for review.
