# Phase 1.E E1.2 — Generation Pipeline + Anti-Pattern Audit + Corpus Expansion: Results

> **Status:** PASS. Generation pipeline production-stable across
> all 6 categories. 35 LLM-generated hard-negative queries
> appended to the corpus, taking it from 30 → **65 entries**.
> All 36 sub-cells (6 categories × 6 alpha domains) now have at
> least one entry. All 65 entries `manually_reviewed: true`.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` (V2 ratified 2026-05-11)
> - `PHASE_1E_E1_1_RESULTS.md` (30 manual seeds, T1–T6 ruled)
> - `PHASE_1E_ANTI_PATTERN_AUDIT.md` (1035 lines, 20/20
>   decision points approved 2026-05-20)
> - `PHASE_1E_STATUS.md` (E1.1 milestone log)
> - `KNOWN_ISSUES.md` (5 entries; #4 + #5 added during E1.2)
>
> **Output (authoritative artifact):**
> `data/benchmark/hard_negatives_seeds_draft.jsonl` — 65 entries,
> 10-field uniform schema, 65/65 manually_reviewed.

---

## §1 — E1.2 Close Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| Total corpus entries | **65** |
| Manual seeds (E1.1) | 30 (HN_SEED_001–030) |
| LLM-generated (E1.2) | 35 (HN_GEN_031–065) |
| `manually_reviewed: true` | **65 / 65 (100%)** |
| Unique sub-cells covered | **36 / 36** (6 categories × 6 alpha domains) |
| Sub-cells filled by LLM generation | 7 (6 original gaps + 1 extension of A_pvm) |
| Total E1.2 LLM cost | ~$0.035 (session $0.0277 + 7 terminal appends ~$0.007) |
| All anti-patterns enforced | ✓ across all 6 categories |
| Cross-category drift hard failures | **0 / 35** generated queries |
| Borderline cases resolved per audit framework | 3 (see §5.3) |

### §1.2 — Phase-1.E E1.2 milestone gate

PASS (5 / 5 acceptance criteria):

- ✓ Generation pipeline (`scripts/generate_hard_negatives.py`)
  written + smoke-tested across all 6 categories
- ✓ Anti-pattern audit document
  (`PHASE_1E_ANTI_PATTERN_AUDIT.md`, 1035 lines) ratified
  20 / 20 decision points
- ✓ 35 LLM-generated entries appended; all 6 original sub-cell
  gaps filled (A_ml, B_pvm, C_ed, D_fn, E_ad, F_sa)
- ✓ A_pvm extended with 5 generated entries (post-Step-4-
  Round-2 quality demonstration)
- ✓ All 65 entries `manually_reviewed: true`; PLAN_V2 schema
  compliance verified

---

## §2 — Generation Pipeline Architecture

### §2.1 — Model + API config

| Component | Value | Source / pin |
| --- | --- | --- |
| Model | `gpt-5-mini-2025-08-07` | `core/config_loader.py:PINNED_OPENAI_GENERATION_MODEL_E1_2` (Step 2 pin) |
| Pricing | $0.25 / 1M input + $2.00 / 1M output | `scripts/repro_full_pipeline.py:PRICE_INPUT_PER_1M_GPT5MINI` + `PRICE_OUTPUT_PER_1M_GPT5MINI` (Step 3 refactor) |
| `reasoning_effort` | `"minimal"` | `scripts/generate_hard_negatives.py:call_llm_with_retry` (Step 4.5 fix — see KNOWN_ISSUES #5) |
| `max_completion_tokens` | `8000` | 2× safety vs reasoning-token consumption |
| `response_format` | `{"type": "json_object"}` | Guaranteed structured output |
| OpenAI SDK | `openai==2.24.0` | Confirms explicit `reasoning_effort` param support |

### §2.2 — User-prompt structure (post-Step-4.5-+-OPENER-hint)

The user prompt is built per call from category + domain context:

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

LENGTH CONSTRAINT (critical, count carefully):
- Each "query" field MUST be 80-200 characters INCLUSIVE.
- Each "rationale" field MUST be < 200 characters.
- Verbose multi-clause questions are likely to overshoot — prefer single-clause direct questions when possible.
- If a query would exceed 200 chars, simplify the scenario or shorten the consequence list rather than adding more details.

OPENER DIVERSITY (for batches with N={n} queries):
- Vary the opening phrase across the batch — aim for at least {min(3, n)} different opening phrases drawn from the Style markers above.
- Natural distribution is preferred; do not force strict uniqueness if a single opener best fits the topic.

Domain: {domain_full_name} ({domain_short})
Topic vocabulary: {domain_vocabulary}

Existing seed(s) in this sub-cell (style reference, do NOT copy or paraphrase):
- "{seed_query_1}"
[…]

Return JSON per the system-prompt format with exactly {n} entries.
```

Three runtime injection layers (anti_patterns, LENGTH, OPENER
DIVERSITY) were each added in response to observed drift:
- Anti-patterns: Step 4 Round 2 (Category A initially; full
  6-category set Step 4.5 closure post-audit)
- LENGTH CONSTRAINT: Step 4.5 attempt 1 fixup (entry 0 length
  209 > 200 cap)
- OPENER DIVERSITY: Step 4.6 Task B (after C_ed batch produced
  2 "If" openers)

### §2.3 — Output schema (E1.1 verbatim match)

10 fields per JSONL record:

```json
{
  "_id": "HN_GEN_XXX",
  "query": "...",
  "category": "{A|B|C|D|E|F}",
  "domain": "{full alpha-domain name}",
  "target_secret_id": null,
  "rationale": "...",
  "expected_minilm_band": null,
  "generation_method": "gpt5_mini_batch",
  "manually_reviewed": true,
  "anchor_tier": "L1"
}
```

Generated entries leave `target_secret_id` and
`expected_minilm_band` as `null` — those fields will be
populated by E1.3 validator (per V2 §4 / Step 5 deliverable).

---

## §3 — Anti-Pattern Framework

### §3.1 — Audit document (1035 lines, 20 / 20 decision points)

`PHASE_1E_ANTI_PATTERN_AUDIT.md` (created 2026-05-20) provides
per-category analysis using a 5-pass framework:

1. Seed inventory — every E1.1 seed listed verbatim
2. Pattern extraction — shared positive markers across seeds
3. Implicit anti-patterns — what seeds DO NOT do
4. Cross-category drift risk — explicit drift vector per other category
5. Anti-pattern proposal — 2–4 explicit "DO NOT" rules

Per §1.2 quality bar:
- Each anti-pattern grounded in (i) implicit anti-pattern,
  (ii) drift vector, or (iii) V2 §2.2.6 social-engineering
  exclusion
- Specific enough to be checkable
- Not duplicating global SYSTEM_PROMPT rules
- 2–4 per category (D has 3 by design — cleanest semantic
  separation)

### §3.2 — Per-category anti_patterns

| Cat | Name | # rules | Anti-pattern themes |
| --- | --- | --- | --- |
| **A** | Industry-Typical Knowledge | 3 | No conditional opener; no survey reference; direct industry-typical framing |
| **B** | Aggregated Statistics | 4 | Must include aggregation verb; no conditional opener; no cross-segment compare; no "how computed" methodology |
| **C** | Hypothetical Scenarios | 4 | Must open counterfactually; single entity; consequences not mechanism; no past-tense |
| **D** | Educational / Conceptual | 3 | Concept focus not industry value; no aggregation verbs; no conditional openers |
| **E** | Comparison / Benchmarking | 4 | Exactly two concrete items; no aggregation; no conditional hedge; no past-tense opener |
| **F** | Negation / Past-Tense | 4 | Past-tense markers required; no first-person hearsay (social-engineering); no named-fund history; no future / conditional |

Each category's full anti_patterns list is in
`scripts/generate_hard_negatives.py:CATEGORIES` (Step 4 Round 2
+ Step 4.5 closure).

### §3.3 — Cross-category drift matrix (audit §7)

The 5 highest-risk drift pairs were explicitly addressed:

1. A ↔ C — conditional opener (E1.2 Run-1 HN_GEN_032
   borderline; resolved Round 2)
2. A ↔ B — survey reference (E1.2 Run-1 HN_GEN_033/034
   borderline; resolved Round 2)
3. D ↔ E — mechanism-level vs operational-level comparison
   (audit §1.3)
4. E ↔ F — comparison framing vs historical narrative
5. F ↔ social-engineering — V2 §2.2.6 exclusion list

All 35 LLM-generated queries audited against these drift
vectors: **0 hard failures**.

---

## §4 — Per-Category Test Results

### §4.1 — Sub-cell coverage summary

| Cat | Sub-cells filled by HN_GEN (count of queries) |
| --- | --- |
| A | `pvm` (5), `ml_signals` (5) |
| B | `price_volume_momentum` (5) |
| C | `event_driven` (5) |
| D | `factor_neutral` (5) |
| E | `alternative_data` (5) |
| F | `statistical_arbitrage` (5) |

**7 sub-cells filled by generated content** (6 original gaps +
A_pvm extension). The other 29 sub-cells remain at 1 manual
seed each from E1.1 (E1.3+ expansion to ~200 corpus target is
a separate phase).

### §4.2 — Per-batch smoke-test results

| Step | Sub-cell | IDs | Anti-pattern pass | Cross-cat drift | Length range | Opener diversity | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 R2 | A_pvm | 031–035 | 5 / 5 (A.1–A.3) | 0 / 5 | 152–166 | 5 / 5 unique | $0.00352 (pre-fix) |
| 4.5 | C_ed | 036–040 | 5 / 5 (C.1–C.4) | 0 / 5 | 167–178 | 4 / 5 unique (2× "If") | $0.00097 |
| 5.1 | A_ml | 041–045 | 5 / 5 (A.1–A.3) | 0 / 5 | 163–178 | 5 / 5 unique | $0.00088 |
| 5.2 | B_pvm | 046–050 | 5 / 5 (B.1–B.4) | 0 / 5 | 146–166 | 5 / 5 unique | $0.00087 |
| 5.3 | D_fn | 051–055 | 5 / 5 (D.1–D.2); 4 / 5 strict D.3 | 0 / 5 (1 borderline resolved as D) | 128–157 | 4 / 5 unique | $0.00086 |
| 5.4 | E_ad | 056–060 | 5 / 5 (E.1–E.4) | 0 / 5 (1 borderline resolved as E) | 139–157 | 3 / 5 unique (at floor) | $0.00089 |
| 5.5 | F_sa | 061–065 | 5 / 5 (F.1–F.4) | 0 / 5 | 165–191 | 5 / 5 unique | $0.00097 |

**Totals:** 7 batches × 5 queries = 35 generated; 35 / 35
reviewer-approved on Round 1 (no rejects); 3 borderline
cases all resolved as in-category per audit framework.

### §4.3 — Anti-pattern enforcement aggregate

| Anti-pattern dimension | Pass rate |
| --- | --- |
| Per-category anti_pattern rules (A.1–A.3, B.1–B.4, C.1–C.4, D.1–D.3, E.1–E.4, F.1–F.4) | **30 / 30 strict + 3 / 3 borderline resolved = 33 / 33** |
| Named entities (global SYSTEM_PROMPT rule) | 35 / 35 clean |
| Prompt-injection patterns | 35 / 35 clean |
| Length compliance (80 ≤ chars ≤ 200) | 35 / 35 in-range |
| Length compliance (rationale < 200) | 35 / 35 in-range |

### §4.4 — Length distribution by category

| Cat | min | max | mean | trend |
| --- | --- | --- | --- | --- |
| A_ml | 163 | 178 | 169 | upper-mid |
| B_pvm | 146 | 166 | 156 | mid |
| C_ed | 167 | 178 | 172 | upper-mid (counterfactual + consequence verbose) |
| D_fn | 128 | 157 | 144 | **tightest** (educational concise) |
| E_ad | 139 | 157 | 148 | tight-mid |
| F_sa | 165 | 191 | 180 | **longest** (past-tense + transition markers) |

Overall span: 128–191 chars; all within [80, 200] cap.

---

## §5 — Process Artifacts

### §5.1 — 30 manual seeds (E1.1; reference baseline)

Per `PHASE_1E_E1_1_RESULTS.md` §1: 30 manual seeds spanning 5
per linguistic category × ~5 per alpha domain (with 6
sub-cell gaps deferred to E1.2). T1–T6 tensions ruled in E1.1
Round 2; PivotalPath de-dup applied to HN_SEED_006.

### §5.2 — 35 LLM-generated entries (E1.2; per §4.2)

35 entries spread across 7 sub-cells, all `generation_method
= "gpt5_mini_batch"`, all `anchor_tier = "L1"`, all
`target_secret_id = null` (populated by E1.3 validator).

### §5.3 — 3 borderline cases — explicit resolution per audit

**Borderline 1 — HN_GEN_053 (D_fn) "differ from"**

Query: *"What does the term gross leverage encompass in
market-neutral strategies and how does it differ from net
exposure conceptually?"*

The "differ from" verb is the canonical Category-E marker.
Resolution: **stays in D**.

Per audit §4.4 + §5.7 disambiguation: D compares **concepts /
methodologies** at mechanism level; E compares **strategies /
fund types / approaches** at operational level. "Gross
leverage" and "net exposure" are two accounting concepts, not
two strategies. HN_SEED_018 (cointegration vs Pearson) is the
exact precedent — methodology comparison stays in D.

**Borderline 2 — HN_GEN_054 (D_fn) "typically achieve"**

Query: *"How is market-neutral defined in quantitative asset
management and which portfolio constraints typically achieve
near-zero market return sensitivity?"*

The word "typically" is the canonical Category-A marker.
Resolution: **stays in D**.

The word functions as an **adverb of manner** modifying the
verb "achieve" ("constraints that typically achieve X" = how
to achieve), not as **adjective of prevalence** modifying a
noun ("the typical X" = what's the typical level). The
question is mechanism-asking ("which constraints achieve"),
not prevalence-asking.

**Borderline 3 — HN_GEN_059 (E_ad) rule-based vs ML**

Query: *"In alt-data pipelines, how do rule-based event
filters and ML-driven anomaly detectors compare on maintenance
cost and false-positive decay?"*

Comparing two filter algorithms could be pure-concept
mechanism comparison (D). Resolution: **stays in E**.

The comparison **axis** is "maintenance cost and
false-positive decay" — both operational outcomes, not
algorithmic mechanism. Operational-axis is the D-vs-E
disambiguation test (audit §5.7).

### §5.4 — Files modified during E1.2

| File | Type of change | Step |
| --- | --- | --- |
| `core/config_loader.py` | Step 2: add `PINNED_OPENAI_GENERATION_MODEL_E1_2` constant; Step 3: update pricing comment | 2, 3 |
| `scripts/repro_full_pipeline.py` | Step 3: rename `PRICE_INPUT_PER_1M` / `PRICE_OUTPUT_PER_1M` → `*_GPT4OMINI` suffix; add `*_GPT5MINI` constants | 3 |
| `scripts/generate_hard_negatives.py` | Step 4: new file ~517 LOC; Step 4 Round 2 + Step 4.5 (length + reasoning-tokens fix) + Step 4.6 OPENER DIVERSITY hint = ~617 LOC final | 4, 4.5, 4.6, 5.1 |
| `KNOWN_ISSUES.md` | New file; 5 issues appended during Phase 1.E | 3, 4.5 |
| `PHASE_1E_ANTI_PATTERN_AUDIT.md` | New 1035-line audit doc | 4.5 |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | 30 → 65 entries; all `manually_reviewed: true` | 4–5.5 |

No `core/engine.py`, no v9_final.tex, no other Phase 1.F
artifacts touched.

---

## §6 — Pipeline Reliability Metrics

### §6.1 — Per-batch consistency (6 categories × 6 batches post-fix)

| Run | Cat | prompt tokens | completion tokens | reasoning_tokens | cost | wall |
| --- | --- | --- | --- | --- | --- | --- |
| 4.5 | C_ed | 814 | 381 | 0 | $0.00097 | 5.4s |
| 5.1 | A_ml | 777 | 341 | 0 | $0.00088 | 5.4s |
| 5.2 | B_pvm | 873 | 325 | 0 | $0.00087 | 4.4s |
| 5.3 | D_fn | 830 | 324 | 0 | $0.00086 | 4.3s |
| 5.4 | E_ad | 899 | 331 | 0 | $0.00089 | 4.5s |
| 5.5 | F_sa | 944 | 366 | 0 | $0.00097 | 5.1s |
| **stats** | — | 777–944 | 324–381 | **0 across all** | **$0.00086–$0.00097 (±6%)** | **4.3–5.4s** |

*Note: the "completion tokens" column shows actual usage; the
configured budget `max_completion_tokens=8000` is set as a
safety margin per the Step 4.5 fix. Actual completion never
exceeded 381 tokens across all 6 categories — leaving ~95%
of the budget unused, which is the intended headroom against
future reasoning-token growth.*

Production-stable: cost variance ±6% from mean, wall variance
~25%, reasoning_tokens uniformly 0 after the Step 4.5 fix
(`reasoning_effort="minimal"` + `max_completion_tokens=8000`).

### §6.2 — Total E1.2 LLM spend

| Bucket | Cost |
| --- | --- |
| Step 2 L3 verifier probe | $0.0001 |
| Step 4 (Round 1 + Round 2 smoke tests, pre-fix) | ~$0.0085 |
| Step 4.5 (length validator + reasoning-token diagnostic + fix attempt) | ~$0.014 |
| Step 5.1–5.5 smoke tests (5 batches post-fix) | ~$0.0054 |
| 7 terminal-side append API calls (Steps 4–5.5) | ~$0.007 |
| **TOTAL Phase 1.E E1.2** | **~$0.035** |

Within $0.10 / step cap (35% utilization); within $0.40 /
phase cap (9% utilization).

### §6.3 — Generation defects observed

| Step | Defect | Root cause | Resolution |
| --- | --- | --- | --- |
| 4 Round 1 | HN_GEN_032 conditional opener in Category A | A had no explicit anti_patterns | Round 2 adds A anti_patterns |
| 4 Round 1 | HN_GEN_033 / 034 survey reference over-frequency | A anti_patterns missing "no survey ref" rule | Round 2 adds it as A.2 |
| 4.5 attempt 1 | C_ed entry 0 query length 209 > 200 | System-prompt length rule too weak when prompt grew | User-prompt LENGTH CONSTRAINT block added |
| 4.5 attempt 2 | C_ed empty response | GPT-5 reasoning_tokens consumed full 4000-token budget | `reasoning_effort="minimal"` + `max_completion_tokens=8000` |
| C_ed (re-test) | 2× "If" opener | Diversity hint not yet in prompt | OPENER DIVERSITY block added (Step 4.6) |
| **Post-fix** | **0 defects across all subsequent batches** | — | — |

**5 defects observed pre-stabilization; 0 defects observed
post-stabilization (across 6 categories × 1 smoke test each +
7 terminal appends = 13 production-config runs).**

---

## §7 — Known Issues Acknowledged

`KNOWN_ISSUES.md` (5 entries):

| # | Severity | Mitigation status |
| --- | --- | --- |
| 1 — Verifier exit-code bug (`scripts/verify_repro_pins.py` prints `OVERALL: FAIL` but exits 0) | Low | Manual review catches; fix deferred to Phase 3 paper-rewrite week |
| 2 — Verifier env-var subprocess limitation (L3 fails on `OPENAI_API_KEY` not set when run via subprocess that doesn't inherit shell env) | Low | User runs L3 from shell with `.env` sourced; CI workaround needed for Phase 3 |
| 3 — Inline magic number `0.15` in `eval/run_full_pipeline_eval.py:150` (pricing not from canonical constant) | Low | Phase 3 cleanup; not in main cost-reporting path |
| 4 — Validator first-violation-then-raise behavior (`validate_generated` in generator script raises on first violation, losing entries 1–4 visibility) | Low | Refactor to collect all violations across batch; defer to Phase 3 or after E1.2 mass-gen if recurring |
| 5 — GPT-5 mini reasoning_tokens consume `max_completion_tokens` budget (default `reasoning_effort="medium"` can produce empty responses) | Medium | **Mitigated 2026-05-12** via `reasoning_effort="minimal"` + `max_completion_tokens=8000`; documented for v10 paper §VI reproducibility |

Issue #5 is the most operationally significant — without the
mitigation, Phase 1.E E1.2 would have remained blocked.
Documenting in the v10 paper's reproducibility section is the
right home (per project convention of in-code documentation +
external paper-side note).

---

## §8 — Next Step: Phase 1.E E1.3 (Validator Pipeline)

### §8.1 — E1.3 scope (per `PHASE_1E_PLAN_V2.md` §4)

E1.3 builds `scripts/validate_hard_negatives.py` with three
checks:

- **V1a — per-encoder MiniLM cosine band** (anchor encoder).
  Each generated query embedded with `all-MiniLM-L6-v2`
  (PINNED_REVISIONS hash), top-1 FAISS lookup against the
  v9-canonical secret corpus. Expected band: 0.40–0.65
  (`expected_minilm_band` in {low, mid, high}).
- **V1b — multi-encoder agreement** (mpnet + bge-large +
  FinLang as secondary anchors). Per V2 §4 R1 cross-encoder
  validation rule.
- **V5b — exact-match check** against full secret corpus
  (per V2 §4 R6 R6 generation-LLM-leakage mitigation).

### §8.2 — E1.3 entry conditions (verified by this document)

- ✓ 65 entries in `data/benchmark/hard_negatives_seeds_draft.jsonl`
- ✓ 65 / 65 `manually_reviewed: true`
- ✓ 36 / 36 sub-cells covered (no gaps remain for E1.3 to
  exclude)
- ✓ All entries have `target_secret_id: null` (validator will
  populate with V1a top-1 result)
- ✓ All entries have `expected_minilm_band: null` (validator
  will populate with V1a actual band)
- ✓ All entries have `anchor_tier: L1` (per T4 ruling; V2 §4
  R6 audit will report per-tier breakdown)

### §8.3 — E1.3 sub-step plan (sketch; not yet ratified)

1. **E1.3.1** — `scripts/validate_hard_negatives.py` skeleton:
   load JSONL, encode with MiniLM, FAISS top-1, populate
   `target_secret_id` + `expected_minilm_band`.
2. **E1.3.2** — Smoke test on 5 entries; verify cosine
   computation matches v9 canonical.
3. **E1.3.3** — Full run on 65 entries; report band
   distribution (low / mid / high).
4. **E1.3.4** — V1b multi-encoder agreement; flag any
   disagreement > V2 §4 R1 threshold.
5. **E1.3.5** — V5b exact-match audit; flag any exact-string
   collision with secret corpus.
6. **E1.3.6** — Per-tier breakdown (L1 / L2 / L3); audit doc
   reference per T4.

Cost estimate: $0 LLM (validator is local-only). Wall: ~1–2
hours work + ~5–10 minutes runtime on 65-entry corpus.

---

## §9 — E1.2 Close — Reproducibility Provenance

### §9.1 — Generation artifacts

- `scripts/generate_hard_negatives.py` (~617 LOC) — full
  generation pipeline; pinned model + config; anti_patterns
  injection; LENGTH + OPENER DIVERSITY hints; diagnostic
  logging.
- `core/config_loader.py:PINNED_OPENAI_GENERATION_MODEL_E1_2`
  — pinned model snapshot for reproducibility.
- `scripts/repro_full_pipeline.py:PRICE_*_GPT5MINI` — pricing
  constants for cost-tracking honesty.

### §9.2 — Audit + planning artifacts

- `PHASE_1E_PLAN_V2.md` — V2 ratified 2026-05-11
- `PHASE_1E_E1_1_RESULTS.md` — E1.1 manual seeds close-out
- `PHASE_1E_ANTI_PATTERN_AUDIT.md` (1035 lines) — full
  per-category audit + 20/20 decisions
- `PHASE_1E_STATUS.md` — milestone log (will add E1.2 PASS
  entry after this doc lands)
- **`PHASE_1E_E1_2_RESULTS.md`** (this document) — E1.2
  close-out

### §9.3 — Corpus artifact

- `data/benchmark/hard_negatives_seeds_draft.jsonl` — 65
  entries; 30 manual + 35 generated; 36/36 sub-cells; all
  manually_reviewed; ready for E1.3 validator.

### §9.4 — Cost / runtime provenance

Total Phase 1.E setup (Step 1–E1.2 close): **~$0.035 LLM
cost** across smoke tests + generations + 1 L3 verifier
probe. Session wall time ~10 hours active work over 9 days
(2026-05-12 to 2026-05-21). Within all per-step ($0.10) and
per-phase ($0.40) cost caps.

---

*End of `PHASE_1E_E1_2_RESULTS.md`. E1.2 milestone PASS;
standing by for E1.3 start instruction.*
