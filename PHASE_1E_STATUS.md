# Phase 1.E — Milestone Status Log

> Append-only milestone log for Phase 1.E (Hard-Negative FPR Set).
> Format matches `PHASE_1F_STATUS.md` convention: one section per
> milestone gate, with status + date + acceptance gate + notes.
> No retroactive edits; corrections via new dated entries below.
>
> **Authoritative inputs:** `PHASE_1E_PLAN_V2.md` (V2 ratified
> 2026-05-11 afternoon); `PLAN.md` §5 Deliverable E; `KICKOFF.md`.
>
> **Milestone topology:** E1.1 (manual seeds) → E1.2 (gen prompt
> design) → E1.3 (LLM extend) → E1.4 (filter) → E1.5 (validate +
> finalize) → E1.6 (E1 status update) → E2 (8 cells) → E3 (compare)
> → E4 (writeup). This log appends one entry per milestone gate.

---

## E1.1 — Manual Seed Authoring

**Status:** PASS
**Date:** 2026-05-11
**Wall time:** ~3.5 h authoring (Round 1) + ~30 min schema /
correction pass (Round 2) ≈ **4 h total**
**LLM cost:** $0
**Files produced:**

- `data/benchmark/hard_negatives_seeds_draft.jsonl` (30 entries;
  schema complete; `manually_reviewed: true`; `anchor_tier: L1`
  on all)
- `PHASE_1E_E1_1_RESULTS.md` (Round 1 draft + Round 2 closure
  appended; full transcript of design tensions surfaced +
  resolutions)

**Acceptance gate (5/5 PASS):**

- ✓ 30 seeds with complete schema (V2 §5.2 fields + `anchor_tier`
  added per T4 ruling)
- ✓ Manual review complete on all 30 (`manually_reviewed: true`)
- ✓ 6 categories × 6 domains coverage matrix: **30/36 sub-cells
  filled**; 6 gaps planned for E1.2 LLM-assisted generation
- ✓ Predicted band distribution: **4 low / 18 mid / 8 high**
  (envelope spans [0.40, 0.65] MiniLM target)
- ✓ Anchor-tier metadata complete (all 30 = L1; L2/L3
  introductions optional in E1.2 to support T4 per-tier
  breakdown)

**Notes for E1.2:**

- **6 sub-cell gaps to fill** (in V2 §10.2 order):
  A × ml_signals, B × price_volume_momentum, C × event_driven,
  D × factor_neutral, E × alternative_data, F × statistical_arbitrage
- **B-category named-entity ratio cap:** ≤ 30% in LLM extensions
  per Q3 (T6) ruling. Current state in seeds: 2 of 5 B-seeds
  carry named entities (HN_SEED_006: HFR; HN_SEED_010: AIMA or
  PivotalPath) — 40% named-entity ratio is intentional Round-1
  diversity baseline; LLM extension brings overall B-category
  density down toward 30%.
- **Per-tier (L1 / L2 / L3) FPR breakdown** mandated as a
  sub-section in `PHASE_1E_RESULTS.md` §4 per T4 ruling. E1.2
  may introduce L2- or L3-anchored hard-negs (currently 30/30
  L1-anchored) to support this breakdown.
- **R6 leakage defense (V2 §7.2) active throughout E1.2–E1.5:**
  generation prompts must NOT include actual secret content;
  validator V5b exact-match check enforces.

**Anomalies / surfaced issues:**

- **Round 2 initial-prompt-misreference incident
  (2026-05-11 afternoon).** The initial Round 2 prompt
  referenced named entities (Aon, Greenwich, BarclayHedge) and
  stacked-specific-numbers patterns that were not present in
  the Round 1 draft. `grep` confirmed 0 occurrences across all
  three. Stop-and-disclose protocol invoked per
  `feedback_stop_and_report`; user retracted instructions and
  re-issued corrected Round 2 prompt with actual JSONL content
  in scope. Net effect: revised Round 2 reduced from 8
  modifications (5 REPLACE + 3 REFINE) to 1 micro-refine
  (HN_SEED_006 PivotalPath de-dup) + schema additions. Documents
  the value of grep-verify before edit-execute.
- No paper-code inconsistency surfaced.
- No watchpoint fired (E1.1 budget compliant; no LLM use).

---

## E1.2 — Generation Pipeline + Anti-Pattern Audit + Corpus Expansion

**Status:** PASS
**Date:** 2026-05-21 (close-out; work spanned 2026-05-12 → 2026-05-21)
**Wall time:** ~10 h active across ~9 days (Steps 2 → 5.5 close)
**LLM cost:** ~$0.035 total
**Files produced:**

- `scripts/generate_hard_negatives.py` (~617 LOC; generation
  pipeline with anti_patterns + LENGTH CONSTRAINT + OPENER
  DIVERSITY injection layers; diagnostic logging for
  reasoning_tokens visibility)
- `PHASE_1E_ANTI_PATTERN_AUDIT.md` (1035 lines; per-category
  5-pass framework; 20/20 decision points ratified)
- `PHASE_1E_E1_2_RESULTS.md` (497 lines; E1.2 close-out
  document; 9 sections covering pipeline / audit / 7 batches
  / metrics)
- `KNOWN_ISSUES.md` — Issues #4 (validator first-violation
  behavior) + #5 (GPT-5 mini reasoning_tokens consumption,
  mitigated) appended
- `core/config_loader.py` — Step 2 added
  `PINNED_OPENAI_GENERATION_MODEL_E1_2 = "gpt-5-mini-2025-08-07"`;
  Step 3 updated pricing comment to reference correct file
- `scripts/repro_full_pipeline.py` — Step 3 renamed
  `PRICE_INPUT_PER_1M` / `PRICE_OUTPUT_PER_1M` to suffix-tagged
  `*_GPT4OMINI` and added `*_GPT5MINI` constants for the
  generation model
- `data/benchmark/hard_negatives_seeds_draft.jsonl` —
  30 → **65 entries** (30 manual + 35 LLM-generated); 65/65
  `manually_reviewed: true`; 36/36 sub-cells covered

**Acceptance gate (5/5 PASS):**

- ✓ Generation pipeline (`scripts/generate_hard_negatives.py`)
  written and smoke-tested across all 6 categories
  (A/B/C/D/E/F)
- ✓ Anti-pattern audit document
  (`PHASE_1E_ANTI_PATTERN_AUDIT.md`, 1035 lines) ratified
  20/20 decision points 2026-05-20
- ✓ 35 LLM-generated entries appended; all 6 original
  sub-cell gaps filled (A_ml, B_pvm, C_ed, D_fn, E_ad, F_sa)
  + A_pvm extended with 5 generated entries
- ✓ All 65 entries `manually_reviewed: true`; PLAN_V2 §5.2
  schema (10 fields) match verbatim
- ✓ Pipeline cost (~$0.035) well under V2 §12 caps
  (per-step $0.10, per-phase $0.40); reasoning_tokens=0
  across all 6 categories post-fix; 0/35 cross-category
  hard failures

**Notes for E1.3:**

- **E1.3 scope** (per V2 §4): `scripts/validate_hard_negatives.py`
  with V1a (MiniLM anchor cosine band), V1b (multi-encoder
  agreement: mpnet + bge-large + FinLang), V5b (exact-match
  against secret corpus per R6 leakage defense)
- **E1.3 entry conditions met:** 65 entries; all
  `manually_reviewed: true`; all `target_secret_id: null`
  (validator will populate with V1a top-1 result); all
  `expected_minilm_band: null` (validator will populate);
  all `anchor_tier: L1` (per T4 ruling)
- **E1.3 cost estimate:** $0 LLM (local validator only);
  ~1–2 h work + ~5–10 min runtime on 65-entry corpus
- **Per-tier breakdown** (L1/L2/L3) mandate per T4 reaffirmed
  for `PHASE_1E_RESULTS.md` §4 in E4 writeup; all current
  entries are L1-anchored, future E2/E3 may introduce
  L2/L3 anchors

**Anomalies / surfaced issues:**

- **Step 4 Round 1 anti-pattern drift** (2026-05-12 — early
  E1.2). Category A had no explicit anti_patterns; first
  5-query batch produced 1 conditional-opener borderline
  (HN_GEN_032 "If a fund…") + 2 over-frequent survey
  references (HN_GEN_033/034). Resolved by Round 2: added 3
  explicit anti_patterns to Category A; re-run produced
  reviewer-grade output. Documented as the trigger for the
  full Phase 1.E anti-pattern audit (PHASE_1E_ANTI_PATTERN_AUDIT.md).
- **Step 4.5 length-overshoot defect** (2026-05-12 → 5-20). C_ed
  attempt 1 produced entry 0 query of 209 chars (9 over the
  200 cap). System-prompt length rule not weighted enough at
  larger prompt size. Resolved by injecting an explicit
  LENGTH CONSTRAINT block in the user prompt (positioned
  after anti_patterns, before domain info).
- **Step 4.5 GPT-5 mini empty-response failure** (2026-05-12).
  After length-constraint injection, second C_ed attempt
  returned empty content. Root cause confirmed empirically
  via diagnostic logging: reasoning_tokens = 1472 / 1564
  (94% of completion budget) under default
  `reasoning_effort="medium"`. Logged as KNOWN_ISSUES #5;
  mitigated via `reasoning_effort="minimal"` +
  `max_completion_tokens=8000`. Post-fix: 13/13 production
  runs returned reasoning_tokens=0.
- **3 borderline category-drift cases** (Step 5.3 + 5.4)
  surfaced and resolved per `PHASE_1E_ANTI_PATTERN_AUDIT.md`
  framework:
  - HN_GEN_053 (D_fn) "differ from" → D vs E disambiguation:
    concept-vs-concept stays in D (audit §4.4 / §5.7)
  - HN_GEN_054 (D_fn) "typically achieve" → A vs D
    disambiguation: adverb-of-manner modifying verb, not
    adjective-of-prevalence modifying noun
  - HN_GEN_059 (E_ad) rule-based vs ML → D vs E
    disambiguation: operational-axis ("maintenance cost +
    false-positive decay") is E-marker, not D
- **State-coordination incidents (2026-05-12 / 2026-05-20).**
  Round 2 anti-pattern audit prompt referenced named entities
  (Aon, Greenwich, BarclayHedge) and stacked-specifics
  patterns that did not exist in the Round-1 jsonl. `grep`
  confirmed 0 occurrences. Stop-and-disclose protocol
  invoked; user retracted and re-issued corrected
  instructions. Also: two terminal-side appends (E_ad,
  F_sa) ran in parallel with my dry-run sessions, producing
  state-prediction mismatches in my reports (45 expected,
  60 actual; 55 expected, 65 actual). Both surfaced
  cleanly; no data corruption.
- **No watchpoint fired** (V2 §12 α/β/γ/δ/ε/ζ all clean).
  Per-step LLM cost max $0.005 (well under $0.10 cap);
  cumulative phase-1.E cost $0.035 (well under $0.40 cap);
  no paper-code inconsistency; no ULR-equivalent leakage
  alarm.

---

*Append next milestone (E1.3) below in same format.*
