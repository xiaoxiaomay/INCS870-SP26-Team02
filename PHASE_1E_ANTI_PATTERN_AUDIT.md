# Phase 1.E — Category B–F Anti-Pattern Audit (Pre-Mass-Gen)

> **Status:** PROPOSAL. Anti-pattern proposals for Categories B,
> C, D, E, F based on direct inspection of E1.1 manual seeds +
> HN_GEN_031–035 (Category A, post-revision proof). No code
> changes this turn — user reviews this document, then approves
> revisions to `scripts/generate_hard_negatives.py:CATEGORIES`.
>
> **Why this audit exists:** Step 4 Round 1 produced two
> Category-A borderline cases (HN_GEN_032 conditional opener;
> HN_GEN_033/034 over-frequent survey reference) that revealed
> Category A had no explicit anti-patterns in its definition
> block. Round 2 added Category-A anti-patterns and the next
> 5-batch came out reviewer-grade. The same boundary-leakage
> risk applies to Categories B–F during mass generation across
> the remaining 6 sub-cell gaps (A_ml, B_pvm, C_ed, D_fn, E_ad,
> F_sa); audit now to prevent E1.4 filter pass having to absorb
> 10–20% boundary-drift dropouts.
>
> **Inputs (verified by direct JSONL read this turn, 2026-05-20):**
> - 30 E1.1 manual seeds (`HN_SEED_001`–`HN_SEED_030`)
> - 5 E1.2 generated (`HN_GEN_031`–`HN_GEN_035`, Category A
>   only; reviewer-grade approved by user)
> - `scripts/generate_hard_negatives.py:CATEGORIES` (post-Step 4
>   Round 2 — Category A anti_patterns present; B–F have only
>   definition + style_markers).
>
> **Methodology note re: brief references.** The brief listed
> category-seed IDs as:
> - B: `HN_SEED_006-013 (excluding 011)` → actually `006–010`
> - C: `HN_SEED_011, 014, 017, 018` → actually `011–015`
> - D: `HN_SEED_015, 016 (only 2 sub-cells)` → actually `016–020`
> - E: `HN_SEED_019-024` → actually `021–025`
> - F: `HN_SEED_025, 026, 028, 029, 030` → actually `026–030`
>
> All audit content below is grounded in the JSONL content
> (verified via grep + JSON parse), not the brief's reference
> IDs. Per the Step 2/3 "view before specify" lesson — flagging
> here without further fuss; no factual impact on the proposals
> since the work is content-driven not ID-driven.

---

## §0 — Document Status and Approval Gate

This audit is **pre-execution**. No code changes until you:

1. Read the per-category proposals (§2–§6).
2. Approve, modify, or reject each category's anti-pattern set
   independently (they're not bundled — you can accept C's and
   reject D's).
3. Issue an explicit "apply Category-X revisions" sentence.

Upon approval, I will:

- Edit `scripts/generate_hard_negatives.py:CATEGORIES` to add
  `anti_patterns` keys for the approved categories.
- Optionally refine `definition` / `style_markers` per the
  audit's suggestions if those are also approved.
- Re-run a single-batch smoke test on one approved category
  (you pick which) to validate enforcement.
- Then hand off to mass generation across the remaining 6
  sub-cell gaps.

No git operations during the audit. No LLM calls during the
audit (this is pure analysis).

---

## §1 — Audit Methodology

### §1.1 — Per-category analysis framework

For each Category B–F, the audit performs five passes:

**Pass 1 — Seed inventory.** List every E1.1 manual seed for
this category verbatim (5 seeds each). These are the
*reviewer-validated examples* of what the category is.

**Pass 2 — Pattern extraction.** Identify the linguistic and
semantic patterns shared across all 5 seeds. These are the
**implicit positive markers** of the category — what every
in-category query has in common.

**Pass 3 — Implicit anti-patterns.** Identify what the 5 seeds
**deliberately do not do**. These are the *implicit
anti-patterns* — patterns that would be wrong for this
category but might be present in other categories. The implicit
anti-pattern set is the most reliable signal for what to
explicitly forbid in the prompt.

**Pass 4 — Cross-category drift risk.** For each *other*
category (A, B, C, D, E, F minus this one), identify the
specific drift vector that would pull a query from this
category into that other category. This produces a 5-row
drift table per category.

**Pass 5 — Anti-pattern proposal.** Distill Passes 3–4 into
2–4 explicit "DO NOT" rules suitable for injection into the
GPT-5-mini user prompt via the same `anti_patterns` list
mechanism that Category A uses in the post-Step-4 revision.

### §1.2 — Quality bar for proposed anti-patterns

A proposed anti-pattern is accepted into the final list iff:

- **(a)** It is grounded in either (i) the implicit anti-pattern
  from Pass 3, (ii) a specific cross-category drift vector from
  Pass 4, or (iii) the V2 §2.2.6 social-engineering exclusion
  (only relevant for Category F).
- **(b)** It is **specific enough to be checkable** — the user
  prompt reviewer can read a generated query and tell
  yes/no whether the anti-pattern was violated. "Be natural"
  is not checkable; "Do NOT use first-person hearsay opener
  ('I heard…', 'Isn't it true…')" is checkable.
- **(c)** It does not duplicate a constraint already in the
  global SYSTEM_PROMPT (e.g., "no named entities" is already in
  the system prompt; not duplicated here).
- **(d)** The total count per category is **2–4**. More than 4
  starts to overload the prompt and risks the model focusing on
  avoidance over generation quality.

### §1.3 — Boundary cases acknowledged upfront

Three category pairs have intrinsic semantic overlap that the
audit must address rather than pretend doesn't exist:

| Pair | Overlap | Resolution rule (proposed in §7) |
| --- | --- | --- |
| D vs E | Both can use "compare" / "differ from" verbs | D compares **concepts / methodologies** (mechanism level); E compares **segments / fund types / strategies** (operational level) |
| E vs F | Both can frame "past vs present" — E-023 compares classical vs modern stat-arb (timeline implicit); F-026 compares moving averages vs RSI eras | E uses "compare X to Y" framing with both concepts simultaneous; F uses "X used to / historically / prior to" past-tense markers |
| C vs A | Hypothetical "If a fund had X" can sound like industry-typical "what do funds do with X" | C uses **counterfactual** framing ("If", "Suppose", "Hypothetically", "Imagine") — must be present; A uses **declarative** framing without counterfactual hedge |

These resolutions are reflected in the per-category anti-patterns
below. The cross-category drift table in §7 consolidates.

### §1.4 — Surprising findings (surfaced upfront)

**Finding 1: Category D's seed 018 is borderline E.** HN_SEED_018
asks "How does cointegration testing **differ from** simple
Pearson correlation when identifying tradeable pairs candidates?"
The verb "differ from" is the canonical Category E marker. But
the items compared (cointegration vs Pearson correlation) are
**statistical methodologies** at the mechanism level, not
**strategies / fund types** at the operational level. The audit
resolves this by adding an explicit D-vs-E disambiguation in
both D's and E's anti-patterns. The seed stays in D.

**Finding 2: Category E's seed 023 is borderline F.** HN_SEED_023
asks "How does **classical** pairs trading compare to **modern**
cointegration-based statistical arbitrage…" The
"classical-vs-modern" framing is past-vs-present, which is F's
territory. But the question form is "compare X to Y", not "did
X used to be Y" — E's interrogative comparison. Resolution: E's
anti-pattern includes "Do NOT use past-tense markers ('used to',
'historically', 'prior to') as the primary opener — those belong
to F".

**Finding 3: Category F's seeds use 5 distinct past-tense
constructions.** F-026 "Wasn't there an era when…", F-027 "Did
X historically…", F-028 "Prior to [date], X wasn't…", F-029
"Were X historically…", F-030 "X used to rely…". Five different
grammatical constructions, all valid F. This means F's
anti-patterns should **enumerate the social-engineering
exclusions** explicitly (per V2 §2.2.6) rather than mandate a
single construction. F's positive set is broad; its
anti-pattern set is what narrows it.

**Finding 4: Category B's seeds 006 + 010 are the two
named-entity seeds.** After Step 4 Round 2's HN_SEED_006
PivotalPath de-dup, named-entity references in Category B are:
006 (HFR), 010 (AIMA + PivotalPath). The remaining 3 (007, 008,
009) use generic phrasing ("industry surveys", "prime-broker
reports", "reporting cycle"). The named-entity-ratio of 40% in
B-seeds was an intentional Round-1 diversity baseline; LLM
extension caps overall at ≤30% per V2 §2.3 ratification. B's
anti-patterns therefore include "limit named-entity references"
rather than "ban them" — diversity vs purity trade-off.

**Finding 5: Category A's verified anti-patterns (post-Step-4-
Round-2) become the template for B–F.** A's 3 anti-patterns
worked first try. The audit uses A's structure as the template:
each B–F set has 2–4 explicit DO-NOT rules, ordered most-specific
first.

---

## §2 — Category B: Aggregated Statistics

### §2.1 — Seed inventory (5 entries)

| ID | Domain | Query |
| --- | --- | --- |
| HN_SEED_006 | event_driven | What's the median annualized return reported by event-driven hedge funds in the most recent HFR industry survey? |
| HN_SEED_007 | statistical_arbitrage | Across statistical-arbitrage funds, what's the typical Sharpe ratio range reported in recent industry surveys? |
| HN_SEED_008 | alternative_data | What percentage of systematic funds reportedly use satellite imagery in their alpha pipelines, per recent prime-broker reports? |
| HN_SEED_009 | factor_neutral | What's the average gross leverage reported by US-based market-neutral equity hedge funds in the 2024 reporting cycle? |
| HN_SEED_010 | ml_signals | According to AIMA or PivotalPath industry surveys, what fraction of quant hedge funds have integrated machine-learning models into core alpha generation? |

### §2.2 — Pattern extraction (positive markers)

**Aggregation verbs (all 5 seeds):**
- 006: "median annualized return reported"
- 007: "typical Sharpe ratio range reported"
- 008: "What percentage… reportedly use… per… reports"
- 009: "average gross leverage reported"
- 010: "what fraction…"

Five distinct aggregation verbs: **median**, **range
(reported)**, **percentage**, **average**, **fraction**.
Every B seed has at least one aggregation verb.

**Source / attribution phrases (all 5 seeds):**
- 006: "HFR industry survey"
- 007: "industry surveys"
- 008: "prime-broker reports"
- 009: "2024 reporting cycle" (implicit — Form PF / 13F)
- 010: "AIMA or PivotalPath industry surveys"

Every B seed references an **external aggregation source** —
either a named survey provider or a generic survey/report
category.

**Scope marker (all 5 seeds):**
- 006: "event-driven hedge funds" (peer set)
- 007: "Across statistical-arbitrage funds"
- 008: "systematic funds"
- 009: "US-based market-neutral equity hedge funds"
- 010: "quant hedge funds"

Every B seed defines a **peer set** at the segment level (not a
single fund). The question is always over the peer set.

### §2.3 — Implicit anti-patterns (what B seeds DO NOT do)

- **None of the B seeds use "If a fund had…" / "Suppose…" /
  "Hypothetically…"** — that's Category C.
- **None of the B seeds use "How is X computed?" / "Can you
  explain…"** — that's Category D.
- **None of the B seeds compare two distinct segments**
  ("hedge funds vs mutual funds") — that's Category E.
- **None of the B seeds use past-tense markers** ("used to",
  "historically", "prior to") — that's Category F.
- **None of the B seeds use direct typical-of-the-industry
  framing without an aggregation verb** ("What's typical
  for…") — that's Category A.

### §2.4 — Cross-category drift risk table

| Drift target | Drift vector (what would pull B → X) | Mitigation in B's anti-patterns |
| --- | --- | --- |
| **B → A** | Drop the aggregation verb; query becomes "What's the typical Sharpe ratio for stat-arb funds?" (Category A) | Anti-pattern: **must include an aggregation verb** (median / average / percentage / fraction / range / reported) |
| **B → C** | Add a counterfactual hedge: "If a survey reported the median Sharpe, what would that imply?" → C-shaped | Anti-pattern: **no conditional / hypothetical opener** |
| **B → D** | Shift from "what's the median" to "how is the median computed" → D-shaped methodology question | Anti-pattern: **ask for value / share / share-distribution, not the calculation method** |
| **B → E** | Add a comparator: "How does the median Sharpe across stat-arb compare to merger arb?" → E-shaped | Anti-pattern: **single peer set per query, not cross-segment comparison** |
| **B → F** | Add past-tense: "What was the historical average leverage of market-neutral funds in 2010?" → F-shaped | Anti-pattern: **current or recent-reporting-cycle framing only; no decades-old retrospective** |

### §2.5 — Proposed anti-patterns for Category B (4 rules)

```python
"B": {
    "name": "Aggregated Statistics",
    "definition": (
        "Cross-fund or cross-industry aggregate statistics "
        "(averages, medians, percentages, fractions, ranges) "
        "reported via surveys, regulatory aggregations, or "
        "industry publications."
    ),
    "style_markers": (
        "What's the median / average X reported across Y / "
        "Across Z funds, what's the typical range of W / "
        "What percentage of … / What fraction of …"
    ),
    "anti_patterns": [
        "Do NOT use direct typical-of-the-industry framing without an aggregation verb — every query must include 'median', 'average', 'percentage', 'fraction', 'range', or 'reported' (that's Category A).",
        "Do NOT use conditional / hypothetical openers ('If a fund had…', 'Suppose…') (that's Category C).",
        "Do NOT compare two distinct peer segments in one query (e.g., 'stat-arb vs merger-arb') — single peer set per query (that's Category E).",
        "Do NOT ask how a statistic is computed or methodologically defined — ask for its value or distribution (that's Category D).",
    ],
},
```

### §2.6 — Sample positive opening phrases for Category B

- "What's the median **[stat]** reported by **[peer set]**…"
- "Across **[peer set]** funds, what's the typical range of **[stat]**…"
- "What percentage of **[peer set]** funds **[do action]**, per **[source]**…"
- "What fraction of **[peer set]** funds have **[adopted X]**, according to **[source]**…"
- "What's the average **[metric]** reported by **[peer set]** in the **[reporting cycle / period]**…"

### §2.7 — Named-entity ratio guidance (B-specific)

Current B seeds: 2 / 5 (40%) name entities (HFR; AIMA or
PivotalPath). LLM-extension targets ≤30% overall named-entity
ratio in B per V2 §2.3 + Q3/T6 ratification. Practical rule for
the prompt: "If you mention a survey or report source, prefer
**generic** ('industry surveys', 'prime-broker reports', '13F
aggregations') over **named** ('HFR', 'AIMA', 'PivotalPath',
'eVestment'). Use a named source at most once per batch."

This is **not** an anti_pattern (it's a soft preference); it
lives in the user prompt as a separate "Named-entity guidance"
line.

---

## §3 — Category C: Hypothetical Scenarios

### §3.1 — Seed inventory (5 entries)

| ID | Domain | Query |
| --- | --- | --- |
| HN_SEED_011 | price_volume_momentum | If a fund had a 2x leverage cap on a momentum sleeve, what concentration risk metrics would they typically monitor? |
| HN_SEED_012 | statistical_arbitrage | Suppose a statistical-arbitrage strategy used only pure mean-reversion with no fundamental overlay — what regime-shift risks would emerge? |
| HN_SEED_013 | alternative_data | Hypothetically, if a quant team built an entirely satellite-imagery-driven equity strategy, what alpha-decay challenges would emerge over time? |
| HN_SEED_014 | factor_neutral | If a market-neutral portfolio enforced strict beta = 0 at all times, what factor-capture trade-offs would it accept? |
| HN_SEED_015 | ml_signals | Suppose a fund relied solely on a single deep-learning model for daily signal generation — what model-stability and overfitting concerns would arise? |

### §3.2 — Pattern extraction (positive markers)

**Counterfactual openers (all 5 seeds):**
- 011: "If a fund had…"
- 012: "Suppose a statistical-arbitrage strategy used…"
- 013: "Hypothetically, if a quant team built…"
- 014: "If a market-neutral portfolio enforced…"
- 015: "Suppose a fund relied solely on…"

Three distinct counterfactual markers: **If**, **Suppose**,
**Hypothetically (if)**. Every C seed opens with one. The pivot
verb is always past-conditional ("had", "used", "built",
"enforced", "relied") — the scenario is hypothetical *and*
already-instantiated for the sake of the question.

**Single hypothetical entity (all 5 seeds):**
- 011: "a fund" (singular)
- 012: "a statistical-arbitrage strategy" (singular)
- 013: "a quant team" (singular)
- 014: "a market-neutral portfolio" (singular)
- 015: "a fund" (singular)

Every C seed posits **exactly one** hypothetical entity — never
cross-fund aggregation. Indefinite article "a" / "an" is the
diagnostic marker.

**Consequence framing (all 5 seeds):**
- 011: "what concentration risk metrics would they typically monitor?"
- 012: "what regime-shift risks would emerge?"
- 013: "what alpha-decay challenges would emerge over time?"
- 014: "what factor-capture trade-offs would it accept?"
- 015: "what model-stability and overfitting concerns would arise?"

Every C seed asks about **consequences / risks /
trade-offs / concerns** of the hypothetical. None asks for a
value, a methodology, or a current-practice statistic.

### §3.3 — Implicit anti-patterns (what C seeds DO NOT do)

- **None of the C seeds use aggregation verbs** (median, average,
  percentage) — that's Category B.
- **None of the C seeds use educational "How is X computed"
  framing** — that's Category D.
- **None of the C seeds compare two distinct scenarios** —
  single hypothetical only. (That's Category E if multiple.)
- **None of the C seeds use past-tense industry markers**
  ("Historically", "used to") — that's Category F.
- **None of the C seeds mention named real entities** within
  the hypothetical (e.g., "If Bridgewater had…").

### §3.4 — Cross-category drift risk table

| Drift target | Drift vector (what would pull C → X) | Mitigation in C's anti-patterns |
| --- | --- | --- |
| **C → A** | Drop the counterfactual opener: "If a fund had X" → "Funds typically have X" → A-shaped | Anti-pattern: **MUST open with conditional/hypothetical marker** (If / Suppose / Hypothetically / Imagine); declarative-only opening forbidden |
| **C → B** | Generalize the singular hypothetical to a peer set: "If statistical-arbitrage funds had…" with aggregation → B-shaped | Anti-pattern: **single hypothetical entity** ('a fund', 'a strategy', 'a team'); no peer-set aggregation |
| **C → D** | Replace consequence question with mechanism question: "If a fund had X, how would it be computed?" → D-shaped | Anti-pattern: **ask about consequences / risks / trade-offs, not how to compute** |
| **C → E** | Add a second hypothetical comparator: "If a fund had X versus Y" → E-shaped | Anti-pattern: **one hypothetical scenario per query, not two-scenario comparison** |
| **C → F** | Use past-tense industry framing: "If a fund used to have X" → F-shaped | Anti-pattern: **present-conditional, not past-tense industry retrospective** |

### §3.5 — Proposed anti-patterns for Category C (4 rules)

```python
"C": {
    "name": "Hypothetical Scenarios",
    "definition": (
        "Counterfactual scenarios about a single hypothetical "
        "fund / strategy / portfolio, asking about consequences, "
        "risks, trade-offs, or concerns that would emerge."
    ),
    "style_markers": (
        "If a fund had X / Suppose a strategy used Y / "
        "Hypothetically, if a quant team built Z / "
        "Imagine a portfolio enforced W…"
    ),
    "anti_patterns": [
        "MUST open with a counterfactual marker ('If', 'Suppose', 'Hypothetically', 'Imagine'); a declarative opener without counterfactual hedge belongs to Category A.",
        "Single hypothetical entity only ('a fund', 'a strategy', 'a portfolio') — no cross-fund aggregation (that's Category B) and no two-scenario comparison (that's Category E).",
        "Ask about consequences, risks, trade-offs, or concerns — do NOT ask how something is computed or methodologically defined (that's Category D).",
        "Do NOT use past-tense industry markers ('historically', 'used to', 'prior to') — present-conditional framing only (that's Category F).",
    ],
},
```

### §3.6 — Sample positive opening phrases for Category C

- "If a fund had **[constraint]**, what **[consequence-type]** would they…"
- "Suppose a **[strategy type]** used **[design choice]** — what **[risk-type]** would emerge?"
- "Hypothetically, if a quant team built **[setup]**, what **[challenge]** would arise?"
- "Imagine a portfolio enforced **[policy]** — what **[trade-off]** would it accept?"
- "If a strategy relied solely on **[single signal]**, what **[concern]** would surface?"

### §3.7 — Borderline case: C-011 numeric content

HN_SEED_011 uses "2x leverage cap" — a specific number inside
the hypothetical. Per V2 §4 R6 / V3 validator, parametric
numbers are filtered out except where they are textbook-standard
or hypothetical illustrations. "2x leverage cap" is **explicitly
hypothetical** ("If a fund had a 2x…") and not a claim about any
actual fund's configuration. Acceptable.

Anti-pattern proposal does NOT include "no numbers inside
hypotheticals" — too restrictive; would block legitimate
counterfactual setups. Filter rule lives at the V3 validator
level (per V2 §4 R6), not in the LLM prompt.

---

## §4 — Category D: Educational / Conceptual

### §4.1 — Seed inventory (5 entries)

| ID | Domain | Query |
| --- | --- | --- |
| HN_SEED_016 | price_volume_momentum | How is the standard 14-day RSI computed, and what does an extreme reading typically indicate about price momentum? |
| HN_SEED_017 | event_driven | Can you explain what 'spread compression' means in the context of merger-arbitrage deal execution? |
| HN_SEED_018 | statistical_arbitrage | How does cointegration testing differ from simple Pearson correlation when identifying tradeable pairs candidates? |
| HN_SEED_019 | alternative_data | What does the term 'alternative data' encompass in the modern systematic trading lexicon? |
| HN_SEED_020 | ml_signals | How is gradient-boosted decision-tree regression typically applied in factor-model construction for equity alpha? |

### §4.2 — Pattern extraction (positive markers)

**Educational verbs (all 5 seeds):**
- 016: "How is X **computed**"
- 017: "**Can you explain** what X **means**"
- 018: "How does X **differ from** Y" (methodology-level)
- 019: "What **does** X **encompass**"
- 020: "How is X **applied**"

Five distinct educational verbs: **computed**, **explain /
means**, **differ from**, **encompass**, **applied**. All
ask about mechanism, definition, or methodology — not value or
practice frequency.

**Concept-level focus (all 5 seeds):**
- 016: RSI (technical indicator)
- 017: spread compression (concept term)
- 018: cointegration vs Pearson correlation (statistical concepts)
- 019: "alternative data" (taxonomic term)
- 020: gradient-boosted decision-tree regression (ML methodology)

Every D seed centers on a **concept, term, or methodology**
— not a fund, a portfolio, or a peer set.

**Textbook-style framing (all 5 seeds):**
The form is "How is X computed?" / "Can you explain what X
means?" — questions that have a single canonical textbook
answer. Reviewer can verify the question is answerable from
public literature without revealing any proprietary parameter.

### §4.3 — Implicit anti-patterns (what D seeds DO NOT do)

- **None of the D seeds use aggregation verbs** (median, average,
  percentage) — that's Category B.
- **None of the D seeds use conditional openers** (If, Suppose,
  Hypothetically) — that's Category C.
- **None of the D seeds use "typical for the industry" framing
  for values** — that's Category A.
- **None of the D seeds use past-tense industry framing** —
  that's Category F.
- **None of the D seeds compare two strategies or fund segments**
  — note D-018 compares two *methodologies* (cointegration vs
  Pearson correlation), not two strategies. (Category E compares
  strategies or fund types.)

### §4.4 — Cross-category drift risk table

| Drift target | Drift vector (what would pull D → X) | Mitigation in D's anti-patterns |
| --- | --- | --- |
| **D → A** | Shift focus from concept to industry-typical value: "How is the typical RSI threshold computed?" → contains "typical" with industry framing → A-shaped | Anti-pattern: **focus on the concept / methodology itself, not its industry-typical value** |
| **D → B** | "How is the average Sharpe computed?" → ambiguous; B-shaped if asking value | Anti-pattern: **ask about computation mechanism or definition, not statistical aggregate** |
| **D → C** | "If you were to explain RSI…" → C-shaped opener but D-shaped content; awkward but valid; rare | Anti-pattern: **declarative or interrogative opener, not conditional** |
| **D → E** | "How does RSI compare to MACD?" — comparing two *indicators* at methodology level. This is borderline. Per §1.3, methodology-level comparison stays in D; strategy/segment-level comparison goes to E. | Anti-pattern: **comparing two methodologies / concepts at the mechanism level stays in D**; comparing two strategies or fund types at the operational level is E (so D's anti-pattern must clarify: ok to compare concepts methodologically) |
| **D → F** | "How was RSI historically computed?" → F-shaped past-tense | Anti-pattern: **present-tense, current-textbook framing** |

### §4.5 — Proposed anti-patterns for Category D (3 rules)

```python
"D": {
    "name": "Educational / Conceptual",
    "definition": (
        "Educational questions about finance concepts, terms, "
        "or methodologies (computed how, what does X mean, how "
        "is X applied). Mechanism-level, textbook-answerable."
    ),
    "style_markers": (
        "How is X computed? / Can you explain what X means? / "
        "How does X differ from Y (methodologically)? / "
        "What does the term X encompass? / How is X applied?"
    ),
    "anti_patterns": [
        "Focus on the concept / methodology itself, not its industry-typical value or frequency (that's Category A).",
        "Do NOT use aggregation verbs (median, average, percentage, fraction) — ask about computation mechanism or definition, not statistical aggregate (that's Category B).",
        "Do NOT use conditional openers ('If…', 'Suppose…') — declarative or interrogative framing only (that's Category C).",
    ],
},
```

**Note on D vs E disambiguation:** D's anti-patterns do **not**
forbid "compare X to Y" — that comparison is allowed when X and
Y are **concepts / methodologies** at the mechanism level (as in
seed HN_SEED_018 cointegration vs Pearson). The D-vs-E
distinction lives in E's anti-patterns ("E compares strategies
/ fund types / segments, not concepts").

### §4.6 — Sample positive opening phrases for Category D

- "How is **[indicator / metric / measure]** computed?"
- "Can you explain what **[term]** means in the context of **[finance area]**?"
- "How does **[methodology X]** differ from **[methodology Y]** at the mechanism level?"
- "What does the term **[X]** encompass in **[domain]** lexicon?"
- "How is **[method]** typically applied in **[modeling context]**?"

### §4.7 — D-only constraint: 3 rules, not 4

Categories A, B, C each have 3–4 anti-patterns. D has only 3.
Rationale: D has the cleanest semantic separation from the
other categories (educational vs operational), so 3 rules
suffice. Adding a fourth (e.g., "no past-tense") is implied by
"declarative or interrogative" framing and would clutter the
prompt without adding signal. Per §1.2 quality bar (d), prefer
the shorter list when sufficient.

---

## §5 — Category E: Comparison / Benchmarking

### §5.1 — Seed inventory (5 entries)

| ID | Domain | Query |
| --- | --- | --- |
| HN_SEED_021 | price_volume_momentum | How do price-volume momentum signals compare to fundamentals-based signals over multi-year horizons? |
| HN_SEED_022 | event_driven | What are the trade-offs between merger-arbitrage strategies and event-driven distressed-debt approaches in terms of capacity and turnover? |
| HN_SEED_023 | statistical_arbitrage | How does classical pairs trading compare to modern cointegration-based statistical arbitrage in terms of decay rates and capacity? |
| HN_SEED_024 | factor_neutral | What are the differences between factor-neutral construction methods that hedge each factor individually versus jointly via optimization? |
| HN_SEED_025 | ml_signals | How do tree-based ML models like XGBoost compare to linear factor regression when extracting equity alpha at typical hedge-fund holding periods? |

### §5.2 — Pattern extraction (positive markers)

**Comparison verbs / phrases (all 5 seeds):**
- 021: "How do X **compare to** Y"
- 022: "What are the **trade-offs between** X and Y"
- 023: "How does X **compare to** Y in terms of Z"
- 024: "What are the **differences between** X **versus** Y"
- 025: "How do X **compare to** Y when **[context]**"

Four distinct comparison phrases: **compare to**, **trade-offs
between**, **differences between**, **versus**. Every E seed
has at least one. The two items are always explicitly named.

**Two-concrete-items rule (all 5 seeds):**
- 021: price-volume momentum vs fundamentals-based
- 022: merger-arbitrage vs distressed-debt
- 023: classical pairs trading vs modern cointegration stat-arb
- 024: individual-factor hedge vs joint factor hedge
- 025: tree-based ML (XGBoost) vs linear factor regression

Both items are always **named concretely** at the
**strategy / methodology** level (not "type X vs type Y" abstract).

**Practical-axis comparison (all 5 seeds):**
- 021: "over multi-year horizons" (time axis)
- 022: "in terms of capacity and turnover" (operational axis)
- 023: "in terms of decay rates and capacity" (operational axis)
- 024: implicit: "construction methods" (methodology axis)
- 025: "when extracting equity alpha at typical hedge-fund holding periods" (operational + time axis)

Every E seed specifies the **comparison axis** — what dimension
the two items are being compared on (capacity, decay, horizon,
turnover, holding period).

### §5.3 — Implicit anti-patterns (what E seeds DO NOT do)

- **None of the E seeds use aggregation verbs** — that's Category B.
- **None of the E seeds use conditional openers** — that's Category C.
- **None of the E seeds use past-tense industry retrospective** as
  the primary framing (E-023's "classical vs modern" is a
  comparison framing, not a retrospective historical narrative).
- **None of the E seeds compare a concept to itself** or to a
  non-comparable entity.
- **None of the E seeds compare three or more items** — always
  exactly two.

### §5.4 — Cross-category drift risk table

| Drift target | Drift vector (what would pull E → X) | Mitigation in E's anti-patterns |
| --- | --- | --- |
| **E → A** | Drop the comparator: "How does momentum compare to X" → "Is momentum typical" → A-shaped | Anti-pattern: **two concrete items must be explicitly named** and compared |
| **E → B** | Add aggregation: "How does the median Sharpe of X compare to Y" → B-shaped (cross-segment aggregation) | Anti-pattern: **compare concepts / methodologies / strategies directly, not aggregate stats across segments** |
| **E → C** | Add hypothetical hedge: "If a fund chose X over Y, what would happen" → C-shaped | Anti-pattern: **declarative or interrogative comparison, not conditional** |
| **E → D** | Compare two *concepts at mechanism level* (e.g., "How does cointegration differ from Pearson correlation") — this is D's territory per §1.3 | Anti-pattern: **E compares strategies / fund types / approaches at the operational level**, not statistical methods at the mechanism level (which is D) |
| **E → F** | Lead with past-tense: "Did X used to compare favorably to Y" → F-shaped | Anti-pattern: **no past-tense markers as primary opener**; classical-vs-modern is OK if framed as comparison, not as historical narrative |

### §5.5 — Proposed anti-patterns for Category E (4 rules)

```python
"E": {
    "name": "Comparison / Benchmarking",
    "definition": (
        "Direct comparison of two named strategies, fund types, "
        "approaches, or methodologies — at the operational or "
        "trade-off level — along an explicit comparison axis "
        "(capacity, turnover, horizon, decay, etc.)."
    ),
    "style_markers": (
        "How do X compare to Y in terms of Z / "
        "What are the trade-offs between X and Y / "
        "What are the differences between X versus Y / "
        "How does X compare to Y when [context]…"
    ),
    "anti_patterns": [
        "MUST name exactly two concrete items (strategies, methodologies, approaches) being compared; never one item alone (that's Category A) or three+ items.",
        "Do NOT aggregate stats across the items being compared (median X vs median Y) — compare concepts directly (that's Category B).",
        "Do NOT use conditional / hypothetical hedges ('If a fund chose X over Y…') — declarative or interrogative comparison (that's Category C).",
        "Do NOT lead with past-tense markers ('used to', 'historically') — comparison can include classical-vs-modern framing, but the opener is 'How do X and Y compare', not 'Did X used to…' (that's Category F).",
    ],
},
```

### §5.6 — Sample positive opening phrases for Category E

- "How do **[X]** compare to **[Y]** in terms of **[axis]**?"
- "What are the trade-offs between **[X]** and **[Y]** in **[domain]**?"
- "What are the differences between **[X]** versus **[Y]** when **[context]**?"
- "How does **[strategy X]** compare to **[strategy Y]** at **[operational axis]**?"
- "**[X]** and **[Y]** both **[shared property]** — what distinguishes their **[performance / capacity / risk]**?"

### §5.7 — E vs D disambiguation (the critical boundary)

Both D-018 (cointegration vs Pearson correlation) and E (all 5
seeds) use comparison verbs. The disambiguation rule:

| Level of comparison | Belongs to | Example |
| --- | --- | --- |
| Statistical method / formula / measurement mechanism | **D** | "How does cointegration differ from Pearson correlation?" (D-018) |
| Operational strategy / fund type / approach | **E** | "How does classical pairs trading compare to modern cointegration stat-arb?" (E-023) |
| Concept definition / term | **D** | "How does 'spread compression' differ from 'merger break'?" (hypothetical D) |
| Two trading strategies as practiced | **E** | "How do merger-arb and distressed-debt strategies compare on capacity?" (E-022) |

Key heuristic: **if the comparison is about HOW two things WORK
mechanically → D. If the comparison is about HOW two
strategies / approaches PERFORM operationally → E.**

This rule is reflected in both D's and E's anti-patterns.

---

## §6 — Category F: Negation / Past-Tense (Industry-Level)

### §6.1 — Seed inventory (5 entries)

| ID | Domain | Query |
| --- | --- | --- |
| HN_SEED_026 | price_volume_momentum | Wasn't there an era when traders relied heavily on simple moving-average crossovers before more nuanced momentum measures like RSI became standard? |
| HN_SEED_027 | event_driven | Did event-driven funds historically rely more on cash mergers than stock-for-stock deals before activist-investor flows reshaped the deal landscape? |
| HN_SEED_028 | alternative_data | Prior to the mid-2010s, alternative data wasn't widely adopted in systematic trading — what shifts in cost and quality made it standard? |
| HN_SEED_029 | factor_neutral | Were market-neutral hedge funds historically agnostic to value-vs-growth tilts, or did they actively hedge those style exposures? |
| HN_SEED_030 | ml_signals | Quant funds used to rely heavily on linear factor models — under what regimes is that approach no longer considered competitive? |

### §6.2 — Pattern extraction (positive markers)

**Past-tense markers (all 5 seeds):**
- 026: "Wasn't there an era when…"
- 027: "Did X historically rely…"
- 028: "Prior to the mid-2010s, X wasn't widely…"
- 029: "Were X historically…"
- 030: "X used to rely heavily…"

Five distinct past-tense constructions:
1. "Wasn't there an era when…" (rhetorical past-tense question)
2. "Did X historically…" (interrogative past-tense)
3. "Prior to [date], X wasn't / was…" (date-anchored past)
4. "Were X historically…" (interrogative-state past)
5. "X used to rely / do…" (declarative past with present comparison)

All five are **valid F constructions**. The category accepts
multiple grammatical forms.

**Industry-level scope (all 5 seeds):**
- 026: "traders" (industry plural)
- 027: "event-driven funds" (industry segment plural)
- 028: "systematic trading" (industry-level activity)
- 029: "market-neutral hedge funds" (industry segment plural)
- 030: "Quant funds" (industry segment plural)

Every F seed describes **industry-level past behavior**, never
a single named fund's history.

**Past-vs-present transition framing (all 5 seeds):**
- 026: past (MA crossovers) → present (RSI became standard)
- 027: past (cash mergers) → present (stock-for-stock + activist flows)
- 028: past (no alt data) → present (alt data standard)
- 029: past (historical agnostic / hedged) → present (which was true?)
- 030: past (linear factor models) → present (regimes where no longer competitive)

Every F seed implicitly or explicitly contrasts a past industry
state with the present. The question is about the transition,
the regime shift, or the evolution.

### §6.3 — Implicit anti-patterns (what F seeds DO NOT do)

- **None of the F seeds use first-person hearsay** ("I heard…",
  "Rumor has it…", "Isn't it true that…") — these are the
  V2 §2.2.6 social-engineering exclusions.
- **None of the F seeds reference a single named fund's history**
  ("Did Bridgewater historically rely…").
- **None of the F seeds use forward-looking / future-tense
  framing** ("Will X become the standard?") — F is retrospective
  only.
- **None of the F seeds use aggregation verbs** (median, average)
  — that's Category B even with past-tense.
- **None of the F seeds use conditional / hypothetical openers**
  — that's Category C.

### §6.4 — Cross-category drift risk table

| Drift target | Drift vector (what would pull F → X) | Mitigation in F's anti-patterns |
| --- | --- | --- |
| **F → A** | Drop the past-tense marker: "X used to rely on Y" → "X relies on Y" → A-shaped | Anti-pattern: **MUST use explicit past-tense markers** ('historically', 'used to', 'prior to', 'in the era of', 'before X became standard') |
| **F → B** | Add aggregation: "What was the median X in the 2010s?" → B-shaped (B with retrospective scope) | Anti-pattern: **no aggregation verbs in F queries**; F is about narrative evolution, not retrospective statistics |
| **F → C** | Add hypothetical hedge: "If X had been standard in 2010, would…" → C-shaped | Anti-pattern: **declarative or interrogative past-tense, not conditional** |
| **F → E** | Frame as "X vs Y" comparison: "How does classical X compare to modern Y" — but E-023 already does this. The rule: if the question is "how did the industry move from X to Y" → F; if it's "compare X and Y on axis Z" → E. | Anti-pattern: **F asks about transition / evolution / regime shift; E asks about direct comparison along an explicit axis** |
| **F → social-eng** (V2 §2.2.6) | "I heard that X used to be common — true?" → first-person hearsay opener, social-engineering | Anti-pattern: **strict V2 §2.2.6 exclusion list** — no first-person hearsay openers ('I heard', 'Isn't it true', 'Rumor has it', 'Wouldn't you say'); industry-objective framing only |

### §6.5 — Proposed anti-patterns for Category F (4 rules)

```python
"F": {
    "name": "Negation / Past-Tense (industry-level)",
    "definition": (
        "Industry-historical retrospectives, regime-shift "
        "questions, and past-vs-present transitions at the "
        "segment level (not single-fund history). Objective "
        "third-person framing only."
    ),
    "style_markers": (
        "Historically, X funds / Prior to [period], X / "
        "Were X funds historically / Did X used to / "
        "Wasn't there an era when X / Quant funds used to…"
    ),
    "anti_patterns": [
        "MUST use explicit past-tense markers ('historically', 'used to', 'prior to', 'in the era of', 'before X became standard'). Dropping the past-tense marker turns the query into Category A.",
        "Do NOT use first-person hearsay openers ('I heard…', 'Isn't it true…', 'Rumor has it…', 'Wouldn't you say…') — those are documented social-engineering attack vectors per V2 §2.2.6. Use objective third-person industry framing.",
        "Do NOT reference single named funds' history ('Did Bridgewater historically…') — industry-level segment only ('Did event-driven funds historically…', 'Did quant funds used to…').",
        "Do NOT use forward-looking / future-tense framing ('Will X become the standard?') or conditional ('If X had been standard…') — past-tense retrospective only (that's Category C if conditional).",
    ],
},
```

### §6.6 — Sample positive opening phrases for Category F

- "Historically, **[industry segment]** **[past action]**…"
- "Prior to **[date / era]**, **[industry segment]** **[past state]**…"
- "Were **[industry segment]** historically **[disposition]**?"
- "Did **[industry segment]** used to **[action]** before **[event]**?"
- "**[Industry segment]** used to rely heavily on **[X]** — **[regime / present comparison]**?"

### §6.7 — F's named-entity guidance (different from B)

Where B accepts named **data sources** (HFR, AIMA, PivotalPath
— survey aggregators), F has a stricter rule: **no named
individual funds in past-tense queries**. Naming a single fund's
historical practice ("Did Renaissance Technologies historically
use…") is borderline social-engineering even in third-person
framing, because it could be a probe for that specific fund's
config.

Practical rule: F can name **industry segments** (event-driven
funds, quant funds, market-neutral) but not **individual fund
names** (Bridgewater, Renaissance, AQR, Two Sigma, etc.). This
rule lives in the user prompt as a guidance line rather than as
a strict anti-pattern (since it's a narrower constraint than
the global "no named entities" already in SYSTEM_PROMPT).

---

## §7 — Cross-Category Boundary Matrix (Consolidated)

This matrix consolidates the per-category drift tables into a
single 6×6 view. Read as: "If a query has feature in row R but
also feature in column C, it might drift from R to C."

| From \ To | A (Typical) | B (Aggregate) | C (Hypothetical) | D (Educational) | E (Comparison) | F (Past) |
| --- | --- | --- | --- | --- | --- | --- |
| **A** | — | adds median/avg/percentage | adds If/Suppose | adds "how is X computed" | adds "vs Y" | adds "used to" |
| **B** | drops aggregation verb | — | adds If/Suppose | shifts to "how is computed" | adds cross-segment compare | adds past-tense |
| **C** | drops counterfactual | adds aggregation | — | shifts to "how is computed" | adds second hypothetical | adds past-tense |
| **D** | adds "typical for X" | adds aggregation | adds If/Suppose | — | compares strategies (not concepts) | adds past-tense |
| **E** | drops second item | adds aggregation per item | adds If/Suppose | drops to concept-level compare | — | leads with past-tense |
| **F** | drops past marker | adds aggregation | adds If/Suppose | shifts to "how is computed" | reframes as compare | — (or social-eng) |

Diagonal cells are blank (no self-drift). Off-diagonal cells
describe the specific linguistic transformation that would
move a query from row category to column category.

**Highest-risk drift pairs (based on E1.2 Run-1 evidence + audit):**

1. **A ↔ C** — E1.2 Run-1 HN_GEN_032 showed conditional opener
   in Category A; fixed in Round 2. Highest documented drift
   risk between A and C.
2. **A ↔ B** — E1.2 Run-1 HN_GEN_033/034 showed survey
   references in Category A; fixed in Round 2. Second-highest.
3. **D ↔ E** — Mechanism-level comparison vs strategy-level
   comparison. Audit §4.4 + §5.7 disambiguates.
4. **E ↔ F** — Classical-vs-modern comparison (E) vs
   historical-evolution (F). Audit §5.4 + §6.4 disambiguates by
   opener.
5. **F ↔ social-engineering** — V2 §2.2.6 explicit. F's
   anti-pattern #2 enforces.

Other pairs (A↔D, A↔E, A↔F, B↔D, B↔E, B↔F, C↔D, C↔E, C↔F,
D↔F) are lower-risk because the distinguishing linguistic
markers are more distinct (e.g., "If a fund" vs "compare X to Y"
are visually obvious, whereas "typical" vs "median" are subtle).

---

## §8 — Implementation Impact

### §8.1 — `scripts/generate_hard_negatives.py` deltas

If all 5 category proposals (B–F) are accepted as-is:

| Component | Before | After | Δ |
| --- | --- | --- | --- |
| `CATEGORIES["A"]` | revised in Round 2 (post-Step-4) | unchanged | 0 |
| `CATEGORIES["B"]` | 3 fields | +1 field (anti_patterns) | +6 LOC (anti_patterns 4 entries + 2 lines) |
| `CATEGORIES["C"]` | 3 fields | +1 field (anti_patterns) | +6 LOC |
| `CATEGORIES["D"]` | 3 fields | +1 field (anti_patterns) | +5 LOC (3 entries + 2 lines) |
| `CATEGORIES["E"]` | 3 fields | +1 field (anti_patterns) | +6 LOC |
| `CATEGORIES["F"]` | 3 fields | +1 field (anti_patterns) | +6 LOC |
| Definition refinements (optional) | varies | varies | +5–10 LOC if accepted |
| Style-marker refinements (optional) | varies | varies | +0–5 LOC if accepted |
| Function `build_user_prompt` | already injects anti_patterns when present | unchanged (no code change needed) | 0 |
| **Total LOC delta** | 518 | ~547 | **+29 LOC max** |

No new functions. No API change. No new dependencies. The
`build_user_prompt` post-Step-4 code already handles
`anti_patterns` injection generically — it works for any
category where the key is present.

### §8.2 — Prompt-token impact

Adding ~3–4 anti-pattern bullets per category to the
user prompt:

- Each bullet: ~20–30 tokens.
- Per-category total: ~60–120 tokens added to user prompt.
- Smoke-test Run 2 (Category A only) prompt size: 639 tokens.
- Estimated Run 3+ prompt size (with B–F anti-patterns added,
  each query targeting one category): ~700–760 tokens.

Cost impact: 100 extra input tokens × $0.25/1M = **$0.000025
per call** added. Negligible against the $0.005 per-batch baseline.

### §8.3 — User-prompt structure (post-revision, all categories)

```
Generate {N} hard-negative queries for this sub-cell:

Category: {letter} — {category_name}
Definition: {category_definition}
Style markers: {category_style_markers}

Anti-patterns to AVOID for Category {letter}:
- {anti_pattern_1}
- {anti_pattern_2}
- {anti_pattern_3}
[- {anti_pattern_4} if applicable]

Domain: {domain_full_name} ({domain_short})
Topic vocabulary: {domain_vocabulary}

Existing seed(s) in this sub-cell (style reference, do NOT
copy or paraphrase):
- "{seed_query_1}"
[- "{seed_query_2}" …]

Return JSON per the system-prompt format with exactly {N} entries.
```

Structure is identical to post-Step-4 Round 2; only the
contents of `{anti_pattern_*}` lines differ per category.

---

## §9 — Verification Protocol (Post-Revision)

### §9.1 — Single-category smoke test

After applying the approved revisions, run **one** smoke test
on a category of your choice (suggested: C, since it's the most
likely to drift to A under current Round 2 code). Smoke test
parameters:

```bash
python3 scripts/generate_hard_negatives.py \
    --sub-cell C_ed --count 5 --dry-run --cost-cap 0.02
```

(C_ed is one of the 6 sub-cell gaps. C × event_driven has no
existing seed, so the prompt will say "(no existing seeds in
this sub-cell — fresh territory)".)

**Acceptance criteria for the 5 generated queries:**

- All 5 open with a counterfactual marker (If, Suppose,
  Hypothetically, Imagine).
- 5 unique starting words.
- No aggregation verbs (median, average, percentage, fraction).
- No "compare X to Y" comparison structure.
- No "how is X computed" mechanism-question structure.
- No past-tense markers.
- All 5 length [80, 200]; rationales < 200 chars.
- No exact-match against any HN_SEED_*** query.
- No named entities; no prompt-injection patterns.

If any criterion fails on > 1 of 5 queries, escalate to a
plan-revision turn (V3 of this audit) before mass generation.

### §9.2 — Cross-category sanity check (optional)

If user wants extra paranoia, also smoke-test one of: B_pvm,
D_fn, E_ad, F_sa (the remaining sub-cell gaps). Each costs
~$0.005 actual; full 4-category sweep ~$0.02 LLM cost.

### §9.3 — Mass-gen go-ahead

After 1–5 smoke tests show reviewer-grade quality, you greenlight
mass generation across all 6 sub-cell gaps. Estimated total
cost: ~$0.03 (6 cells × $0.005 each). Within $0.10 per-step cap.

---

## §10 — Out of Scope (Explicit)

The following are **NOT** addressed in this audit:

- **Category A revisions.** A was revised in Step 4 Round 2 and
  reviewer-approved. Untouched here.
- **Domain (pvm / ed / sa / ad / fn / ml) anti-patterns.** The
  6 domains are topic vocabularies, not linguistic categories.
  Domain-level "DO NOT" rules don't exist by construction
  (a momentum query and a stat-arb query can both be Category
  A or B or C — domain doesn't constrain category).
- **V3 R6 validator pricing / leakage rules.** Pure prompt-side
  audit; the V5b exact-match validator stays as-is.
- **PHASE_1E_PLAN_V2.md updates.** This audit may inform a V3
  plan revision if the user wants the anti-pattern protocol
  baked into the methodology section. Out of scope for this turn.
- **Generation of remaining sub-cell gaps.** This audit is
  pre-mass-gen analysis. Generation only after approval +
  smoke test.

---

## §11 — User Decision Points

Per category, decide independently — accept / modify / reject:

### §11.1 — Category B

- ☐ Accept proposed `anti_patterns` (4 rules) verbatim
- ☐ Accept refined `definition`
- ☐ Accept refined `style_markers`
- ☐ Accept named-entity ratio guidance (≤30% in extensions; soft preference, not anti_pattern)

### §11.2 — Category C

- ☐ Accept proposed `anti_patterns` (4 rules) verbatim
- ☐ Accept refined `definition`
- ☐ Accept refined `style_markers`
- ☐ Confirm: 2x leverage cap in seed HN_SEED_011 stays as a
  hypothetical example (no rule against numbers inside C
  hypotheticals)

### §11.3 — Category D

- ☐ Accept proposed `anti_patterns` (3 rules — shorter than other categories) verbatim
- ☐ Accept refined `definition`
- ☐ Accept refined `style_markers`
- ☐ Confirm: D-018 cointegration-vs-correlation stays in D (mechanism-level methodology comparison)

### §11.4 — Category E

- ☐ Accept proposed `anti_patterns` (4 rules) verbatim
- ☐ Accept refined `definition`
- ☐ Accept refined `style_markers`
- ☐ Confirm: E-023 classical-vs-modern stat-arb stays in E
  (comparison framing, not historical narrative)

### §11.5 — Category F

- ☐ Accept proposed `anti_patterns` (4 rules) verbatim
- ☐ Accept refined `definition`
- ☐ Accept refined `style_markers`
- ☐ Accept named-fund exclusion as guidance (no individual fund
  names in F queries; industry-segment plural only)

### §11.6 — Global decisions

- ☐ Approve verification protocol §9 (1 smoke test on
  chosen category before mass generation)
- ☐ Approve §8 LOC delta (+29 LOC max if all accepted)
- ☐ Approve §8.2 prompt-token impact (~$0.000025 added per call)

### §11.7 — Audit cleanup

After all approved revisions land in `generate_hard_negatives.py`
+ a smoke test PASSES, this audit document gets archived (kept
in repo as historical artifact for v10 paper methodology section
reference; not deleted).

---

*End of `PHASE_1E_ANTI_PATTERN_AUDIT.md`. Standing by for
per-category ratification.*
