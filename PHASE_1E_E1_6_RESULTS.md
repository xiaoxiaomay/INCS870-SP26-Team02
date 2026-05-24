# Phase 1.E E1.6 — Phase 1.E Full Logical Close: Results

> **Status:** PASS. Phase 1.E E1.6 split across two sessions:
> Part 1 (master `PHASE_1E_RESULTS.md` aggregation) and Part 2
> (this session: PENDING V2.5 decisions resolved, corpus rename
> commands computed for user manual execution, validator
> DOCUMENTED_FINDINGS transitioned PENDING → RESOLVED, V5b
> idempotent refresh, memory persistence, batched commit
> sequence prepared). **Phase 1.E FULL LOGICAL CLOSE achieved.**
>
> 14 documented_findings keys in canonical artifact: 12 S-findings
> (S1, S2, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14) + 2
> RESOLVED V2.5 decisions (PLAN + SCHEMA). 0 PENDING.
>
> **Inputs (authoritative):**
> - `PHASE_1E_PLAN_V2.md` §5.1 (final corpus filename), §2.5 +
>   §5.2 (validator spec preserved as-is per Option B).
> - `PHASE_1E_RESULTS.md` (master close-out, E1.6 Part 1; §5
>   updated this Part 2).
> - Sub-phase RESULTS docs E1.1 through E1.5 (cross-referenced).
> - `eval/results/phase1_E/validation/v1b_20260524T002258Z.json`
>   (canonical before this Part 2; had 2 PENDING).
>
> **Outputs (authoritative artifacts):**
> - `scripts/validate_hard_negatives.py` (**1832 LOC**; +59 LOC
>   over E1.5 close for PENDING → RESOLVED transition + structured
>   8-sub-key dict entries).
> - `eval/results/phase1_E/validation/v1b_20260524T044018Z.json`
>   (**FINAL E1.6 canonical artifact**; 14 documented_findings = 12 S + 2 RESOLVED, 0 PENDING).
> - `PHASE_1E_RESULTS.md` (master; §5 updated post-resolution).
> - `PHASE_1E_E1_6_RESULTS.md` (this document, Part 2 close).
> - Corpus rename commands computed (NOT executed; user manual
>   git mv + sed sequence in §4 below).

---

## §1 — E1.6 Close Summary

### §1.1 — Headline numbers

| Metric | Value |
| --- | --- |
| Sub-phase E1.6 split | Part 1 (master doc) + Part 2 (this session) |
| PENDING V2.5 decisions | 2 → **0 (both RESOLVED)** |
| RESOLVED V2.5 decisions | **2** (PLAN + SCHEMA, both Option B document-only) |
| Total documented_findings | **14** (12 S + 2 RESOLVED, no PENDING) |
| Validator LOC | 1773 → **1832** (+59 for RESOLVED dict entries) |
| Corpus rename | Commands computed; user manual `git mv` execution |
| LLM cost (E1.6 Part 2) | **$0** |
| Session wall (Part 2) | ~1 hour |
| Phase 1.E total wall | ~17-19 hours across 5+ sessions |

### §1.2 — Phase 1.E E1.6 milestone gate

PASS (5 / 5 acceptance criteria):

- ✓ Both PENDING V2.5 decisions resolved with explicit Option
  ratifications (§3.1 + §3.2 below) + RESOLVED_* dict entries
  in DOCUMENTED_FINDINGS.
- ✓ Validator idempotently refreshed canonical JSON
  (`v1b_20260524T044018Z.json` has 14 keys, 0 PENDING, 2 RESOLVED).
- ✓ Corpus rename commands computed per V2 §5.1 spec; affected
  code references enumerated; user manual `git mv` sequence in
  §4 below.
- ✓ Master `PHASE_1E_RESULTS.md` §5 updated post-resolution
  with full RESOLVED prose + unified Option B philosophy.
- ✓ Atomic write discipline maintained (`.bak` rotated;
  `.preV1a` permanent baseline preserved).

---

## §2 — Part 1 vs Part 2 Split Context

Phase 1.E E1.6 was split across two sessions per user's pacing
strategy: Part 1 (master doc) tactical, Part 2 (PENDING
resolution) judgment-heavy. The split reasoning:

| Part | Focus | Rationale |
| --- | --- | --- |
| Part 1 | Master `PHASE_1E_RESULTS.md` aggregating E1.1–E1.5 | Aggregation work; mechanical synthesis from existing sub-phase RESULTS |
| Part 2 (this) | Resolve 2 PENDING V2.5 decisions + corpus rename + final batched commit prep | Judgment-heavy ratifications deserve fresh-state attention; no time pressure |

The split is documented for reviewer-grade audit hygiene
(per Phase 1.E sequencing-divergence-acknowledgment precedent
from E1.4 §1.5).

---

## §3 — PENDING Resolutions

Both PENDING blocks resolved with unified **Option B (document-
only)** philosophy. Full RESOLVED entry texts in canonical
`v1b_20260524T044018Z.json`; summary here.

### §3.1 — `RESOLVED_V2_5_PLAN_REVISION`

**Decision:** Document-only (Option B). V2 §2.5 windows preserved
as-is. S1/S8/S9 stand as paper findings about Phase 1.F prediction
calibration.

**Rationale:** survivorship bias prevention; consistency with V1a
Option B + V1b STRICT-with-paper-escalation precedents; v10 §VI
honest prediction-miss reporting rather than refit-to-data.

**Options considered:**
- (A) Numeric re-anchor: Rejected (survivorship bias risk)
- (B) Document-only: **ADOPTED** (reviewer-grade epistemic honesty)
- (C) Hybrid selective: Rejected (inconsistent treatment risk)

**Constituent findings:** S1 (cross-domain spillover) + S8 (mpnet
prediction-miss +0.18) + S9 (bge_large band permissiveness).

### §3.2 — `RESOLVED_V2_5_SCHEMA_REVISION`

**Decision:** Document-only (Option B). V2 §5.2 4×2 schema
preserved as-is. S7 stands as paper finding about spec design
flaw caught at implementation.

**Rationale:** V2 plan history sanctity (V2 ratified at specific
date); view-before-implement discipline caught the flaw before
implementation; retroactively revising V2 plan would obscure
discovery timeline; consistency with Option B on plan revision.

**Options considered:**
- (A) Formal revision: Rejected (V2 plan history retrofit risk)
- (B) Document-only: **ADOPTED** (view-before-implement evidence preserved)

**Constituent findings:** S7 (corpus-version disjointness).

### §3.3 — Unified Option B philosophy

Both resolutions adopt the same underlying epistemic principle:
**the V2 plan + its observed deviations together constitute the
v10 paper evidence, not refitted V2.5 specs.** This continues
the precedent chain:

| Precedent | When | What |
| --- | --- | --- |
| V1a Option B | E1.3.2 | Retain 12 outliers as observations |
| V1b STRICT-with-paper-escalation | E1.3.4 | Report prediction-miss as finding |
| E1.4 RETAIN-all batch ruling | E1.4 Q3 | 23 outliers retained |
| E1.5 V2 100% PASS | E1.5 | Confirms corpus benign-by-construction |
| **E1.6 Option B for both PENDINGs** | **E1.6 Part 2 (this)** | **V2 plan + schema preserved; findings stand** |

The unified philosophy is the v10 paper's reviewer-grade
methodology contribution: **honest engineering with documented
deviations rather than retroactive refit**.

---

## §4 — Corpus Rename per V2 §5.1 (commands for user manual execution)

### §4.1 — V2 §5.1 verbatim (rationale)

> Final corpus: **`data/benchmark/hard_negatives.jsonl`** (unchanged).
> Intermediate: `hard_negatives_seeds.jsonl`, `hard_negatives_raw.jsonl`.

V2 categorizes the current `hard_negatives_seeds_draft.jsonl` as
an intermediate name; the final canonical name is
`hard_negatives.jsonl`.

### §4.2 — Affected files

**3 corpus files (`data/benchmark/`):**
- `hard_negatives_seeds_draft.jsonl` (current canonical)
- `hard_negatives_seeds_draft.jsonl.bak` (rotator; can delete)
- `hard_negatives_seeds_draft.jsonl.preV1a` (permanent baseline)

**2 active code files (7 references):**
- `scripts/validate_hard_negatives.py`:
  - Line 5 (docstring), Line 25 (docstring), Line 28 (docstring), Line 70 (`HARD_NEG_PATH` constant)
- `scripts/generate_hard_negatives.py`:
  - Line 8 (docstring), Line 34 (`DEFAULT_SEEDS_PATH` constant), Line 474 (CLI help)

**Historical docs (NOT to update — preserve state-at-time-of-writing):**
- `PHASE_1E_E1_1_RESULTS.md` through `PHASE_1E_E1_5_RESULTS.md`
- `PHASE_1E_STATUS.md`
- `eval/results/phase1_E/validation/outlier_inventory.md`
- (Master `PHASE_1E_RESULTS.md` is post-rename; references the
  new name where appropriate)

### §4.3 — Suggested rename sequence (user manual execution)

```bash
cd ~/Downloads/sentinelflow

# Step 1: Rename 3 corpus files (git tracks as rename, preserves history)
git mv data/benchmark/hard_negatives_seeds_draft.jsonl \
       data/benchmark/hard_negatives.jsonl

git mv data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a \
       data/benchmark/hard_negatives.jsonl.preV1a

# .bak is operational rotator; can delete (next validator run will recreate)
rm data/benchmark/hard_negatives_seeds_draft.jsonl.bak

# Step 2: Update 4 references in validate_hard_negatives.py
sed -i '' \
  's|hard_negatives_seeds_draft.jsonl|hard_negatives.jsonl|g' \
  scripts/validate_hard_negatives.py

# Step 3: Update 3 references in generate_hard_negatives.py
sed -i '' \
  's|hard_negatives_seeds_draft.jsonl|hard_negatives.jsonl|g' \
  scripts/generate_hard_negatives.py

# Step 4: Verify code still references the new path correctly
grep -n "hard_negatives" scripts/validate_hard_negatives.py \
  | grep -v "draft" | head -5
grep -n "hard_negatives" scripts/generate_hard_negatives.py \
  | grep -v "draft" | head -5

# Step 5: Smoke test — validator infrastructure check
python3 scripts/validate_hard_negatives.py --check-only

# Step 6: Verify-no-orphans: confirm no remaining draft references
grep -rn "hard_negatives_seeds_draft" \
  --include="*.py" \
  scripts/ \
  || echo "OK: no remaining draft references in active code"
```

`sed -i ''` empty argument is for macOS BSD sed; on Linux, use
`sed -i 's|...|...|g'` without the empty quotes.

### §4.4 — Verification checklist post-rename

After running the above sequence, verify:
- ✓ `data/benchmark/hard_negatives.jsonl` exists (65 entries × 22 fields)
- ✓ `data/benchmark/hard_negatives.jsonl.preV1a` exists (34207 bytes)
- ✓ `data/benchmark/hard_negatives_seeds_draft.jsonl*` files removed
- ✓ Validator runs cleanly: `python3 scripts/validate_hard_negatives.py --check-only`
- ✓ No remaining `hard_negatives_seeds_draft` references in `scripts/`
- ✓ Git status shows clean rename detection (renames preserve blame/history)

---

## §5 — Validator Updates + V5b Refresh

### §5.1 — DOCUMENTED_FINDINGS transition

| Change | Detail |
| --- | --- |
| Removed | `PENDING_V2_5_PLAN_REVISION` (string entry) |
| Removed | `PENDING_V2_5_SCHEMA_REVISION` (string entry) |
| Added | `RESOLVED_V2_5_PLAN_REVISION` (dict, 8 sub-keys: type / decision / rationale / constituent_findings / options_considered / paper_implication / v11_future_work / resolved_at) |
| Added | `RESOLVED_V2_5_PLAN_REVISION` (dict, 8 sub-keys: same structure) |
| Net change | 14 keys → 14 keys (same count; PENDING string → RESOLVED dict structure migration) |

### §5.2 — Validator LOC delta

| State | LOC |
| --- | --- |
| E1.5 close | 1773 |
| E1.6 Part 2 (this) | **1832** |
| Delta | +59 LOC (structured 8-sub-key dict entries replace 2-line PENDING strings) |

### §5.3 — V5b idempotent refresh

Re-ran `python3 scripts/validate_hard_negatives.py --run-v5b`:

- Search wall: < 0.01s (V5b is hashmap lookup; idempotent)
- New canonical artifact: `v1b_20260524T044018Z.json` (FINAL)
- Historical preserved: `v1b_20260524T002258Z.json` (pre-resolution)
- All measurement data byte-identical (corpus unchanged; only
  DOCUMENTED_FINDINGS dict mutated)

**Field population (idempotent verify):**
- `exact_match_against_secret`: 65/65 (all False)
- `v2_benign_check`: 65/65 ("pass") — preserved through re-run
- Schema integrity: 65 entries × 22 fields

---

## §6 — Final Corpus State (post-Phase-1.E logical close)

### §6.1 — Validator green-light dashboard

| Check | Status | Detail |
| --- | --- | --- |
| V1a MiniLM BLOCKING | 53/65 PASS (81.5%) | 12 outliers retained per Option B (S1) |
| V1b mpnet BLOCKING | 51/65 PASS (78.5%) | 14 outliers retained per STRICT-paper-escalation (S8) |
| V1b bge_large BLOCKING | **65/65 PASS (100%)** | S9 null result |
| V1b finlang BLOCKING | 61/65 PASS (93.8%) | 4 outliers retained (S11) |
| V5b exact-match | **65/65 PASS (100%)** | S12 zero contamination |
| R6 Layer 5 paraphrase signature | 4 candidates → 0 confirmed | S13 100% false-positive rate |
| V2 manual benign | **65/65 PASS (100%)** | S14 benign-by-construction |

### §6.2 — Triple-layered defense-in-depth confirmed

S14 unified narrative + RESOLVED block confirmations validate
the v10 paper's reviewer-grade architectural claim: hard-negative
corpus construction with **three independent BLOCKING gates**
against secret-content leakage:

1. **Layer 2 V5b** — exact-string match: 0/65 hits (S12)
2. **Layer 5 R6** — multi-encoder paraphrase signature: 4/4 ruled
   non-paraphrase (S13)
3. **V2** — expected-answer benign: 65/65 PASS (S14)

All three gates green; corpus passes Phase 1.E logical close.

### §6.3 — Disposition aggregate

| Disposition | Count |
| --- | --- |
| Pass all validators | 42/65 (64.6%) |
| Outlier (flagged by ≥1 validator) | 23/65 (35.4%) |
| Drops | **0** |
| Retained per V1a Option B / V1b STRICT-with-paper-escalation | 23 |

---

## §7 — Reproducibility Provenance

### §7.1 — Canonical artifacts (post-E1.6 Part 2)

| Path | Status |
| --- | --- |
| `scripts/validate_hard_negatives.py` | 1832 LOC; 14-key DOCUMENTED_FINDINGS (0 PENDING, 2 RESOLVED) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl` | 65 entries × 22 fields (rename to `hard_negatives.jsonl` pending user manual `git mv`) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` | rotator (delete on rename) |
| `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` | permanent baseline (rename to `.preV1a` of new name) |
| `eval/results/phase1_E/validation/v1b_20260524T044018Z.json` | **FINAL E1.6 canonical** |
| `eval/results/phase1_E/validation/v1b_20260524T002258Z.json` | Historical (pre-resolution) |
| `eval/results/phase1_E/validation/r6_audit.jsonl` | 23 entries (unchanged from E1.4) |
| `eval/results/phase1_E/validation/v2_benign_check_report.md` | E1.5 deliverable (250 lines) |
| `PHASE_1E_RESULTS.md` | Master close-out (§5 updated this Part 2) |
| `PHASE_1E_E1_6_RESULTS.md` (this) | E1.6 close-out |

### §7.2 — Cost and wall

| Stage | LLM cost | Wall |
| --- | --- | --- |
| Onboarding verification | $0 | ~3 min |
| Validator PENDING → RESOLVED edit | $0 | ~10 min |
| V5b idempotent refresh | $0 | ~1 min |
| Rename command computation | $0 | ~5 min |
| Master `PHASE_1E_RESULTS.md` §5 update | $0 | ~15 min |
| `PHASE_1E_E1_6_RESULTS.md` write (this) | $0 | ~20 min |
| Memory persistence | $0 | ~10 min |
| **Total E1.6 Part 2 session** | **$0** | **~1 hour** |

Within all per-step ($0.005) and per-phase ($0.40) cost caps.

### §7.3 — Phase 1.E total cost summary

| Sub-phase | LLM cost |
| --- | --- |
| E1.1 manual seeds | $0 |
| E1.2 audit-driven generation | **$0.035** |
| E1.3 V1a + V1b + V5b validators | $0 |
| E1.4 outlier disposition | $0 |
| E1.5 V2 benign check | $0 |
| E1.6 Part 1 (master doc) | $0 |
| E1.6 Part 2 (this) | $0 |
| **Phase 1.E TOTAL** | **$0.035** |

**8.75% of $0.40 phase cap utilized.** Reviewer-grade cost
discipline; substantial budget reserve for Phase 1.G.

---

## §8 — Commit-Prep Summary

Per project no-commit discipline, no commit initiated by Claude
Code. User runs git operations manually.

### §8.1 — Suggested batched commit + push sequence

**Outstanding state to commit (per user's batching plan):**

| Commit | Content | Status |
| --- | --- | --- |
| (existing) `7f57f05` | E1.4 close | local-only, unpushed |
| (existing) `e8bc030` | E1.5 close | local-only, unpushed |
| Part 1 (deferred from prior session) | `PHASE_1E_RESULTS.md` master | untracked, pending commit |
| Part 2 (this session) | All E1.6 Part 2 changes | untracked, pending commit |

Per user's brief: batched push at Phase 1.E logical close.

### §8.2 — Part 1 commit (if not yet committed)

```bash
cd ~/Downloads/sentinelflow

git add PHASE_1E_RESULTS.md

cat > /tmp/e16_part1_commit_msg.txt << 'EOF'
phase1E: Part 1 of close - master RESULTS doc aggregating E1.1-E1.5

PHASE_1E_RESULTS.md authored as master Phase 1.E close-out:
- 12 paper-publishable findings (S1-S14 with S3/S4 gaps)
- 2 PENDING V2.5 decisions (DEFERRED to Part 2)
- Corpus: 65 entries × 22 fields, paper-grade methodology
- Total Phase 1.E LLM cost: $0.035 (E1.2 generation only)
- Cumulative wall: ~16-18 hours across 5 sub-phases

Part 2 (next session) resolves PENDING decisions, renames corpus
per V2 §5.1, and batches push (7f57f05 E1.4 + e8bc030 E1.5 +
this Part 1 + Part 2 commits pushed together at Phase 1.E
logical close).
EOF

git commit -F /tmp/e16_part1_commit_msg.txt
```

### §8.3 — Part 2 commit (after corpus rename in §4.3)

```bash
cd ~/Downloads/sentinelflow

# Stage Part 2 work (after running §4.3 rename sequence)
git add scripts/validate_hard_negatives.py
git add scripts/generate_hard_negatives.py
git add eval/results/phase1_E/validation/v1b_20260524T044018Z.json
git add PHASE_1E_RESULTS.md
git add PHASE_1E_E1_6_RESULTS.md

# Note: git mv from §4.3 above already stages the rename detection
# Note: if rename NOT executed yet, omit the data/benchmark/ files
#       from this commit (rename can be a separate commit if preferred)

cat > /tmp/e16_part2_commit_msg.txt << 'EOF'
phase1E: Part 2 of close - PENDING V2.5 resolved + corpus rename

Phase 1.E E1.6 Part 2 OFFICIALLY CLOSED:
- RESOLVED_V2_5_PLAN_REVISION: Option B (document-only).
  V2 §2.5 windows preserved. S1/S8/S9 stand as paper findings.
- RESOLVED_V2_5_SCHEMA_REVISION: Option B (document-only).
  V2 §5.2 schema preserved. S7 stands as paper finding.
- Corpus renamed per V2 §5.1: hard_negatives_seeds_draft.jsonl
  → hard_negatives.jsonl
- Validator updated: PENDING entries removed, RESOLVED entries
  added (8-sub-key dict structure), corpus path constants updated.

Phase 1.E FULL LOGICAL CLOSE:
- 5 sub-phases complete (E1.1-E1.6)
- 12 paper-publishable findings (S1-S14 with S3/S4 gaps)
- 2 RESOLVED V2.5 decisions (both Option B document-only)
- Corpus: 65 entries × 22 fields, paper-grade methodology
- Total Phase 1.E LLM cost: $0.035 (8.75% of $0.40 phase cap)
- Cumulative wall: ~17-19 hours across 5+ sessions

Next: Phase 1.G adaptive attacker (3-5 day sub-project) + v10
paper rewrite (§V + §VI + §VII).
EOF

git commit -F /tmp/e16_part2_commit_msg.txt
```

### §8.4 — Batched push

```bash
# Verify final state — 4 Phase 1.E commits unpushed
git log --oneline origin/main..HEAD

# Push all 4 commits as Phase 1.E logical close batch
git push origin main

# Verify push succeeded (output should be empty)
git log --oneline origin/main..HEAD
```

### §8.5 — .gitignore consideration (carry-forward from E1.3 §13.2)

`*.jsonl.bak` recommended for `.gitignore` (operational rotator
files). `.preV1a` parallels `.preE14` precedent — user choice
on commit vs gitignore for permanent snapshots.

---

## §9 — Phase 1.E → Paper §VI Mapping (final post-E1.6)

Per master `PHASE_1E_RESULTS.md` §11, with E1.6 Part 2 updates:

| Paper section | Phase 1.E sources |
| --- | --- |
| §V Methodology — Corpus Construction | E1.1 + E1.2 + V2 §2.2 taxonomy + V2 §2.4 size rationale |
| §V Methodology — Validation Pipeline | E1.3 V1a + V1b + V5b + V2 §4 spec + R6 6-layer mitigation |
| §V Methodology — Unified Option B Philosophy | **NEW (this E1.6)**: documented-deviations-over-refit doctrine; precedent chain V1a Option B → V1b STRICT → E1.4 RETAIN → E1.5 V2 PASS → E1.6 RESOLVED |
| §VI Reproducibility | E1.3 pinned components + FAISS conventions + 3-tier backup + 65-entry close + V3 deferral + sequencing divergence + corpus rename per V2 §5.1 |
| §VI Findings | S1–S14 (12 findings) — each gets 1–2 paragraphs |
| §VI RESOLVED Decisions | RESOLVED_V2_5_PLAN_REVISION + RESOLVED_V2_5_SCHEMA_REVISION — methodology decision documentation |
| §VII Limitations / Future Work | V8 sub-cell balance + 200-entry v11 + V3 v11 + multi-agent + Phase 1.G integration |

The **unified Option B philosophy** is the v10 paper's central
methodology-discipline claim, emerging organically from the
Phase 1.E precedent chain. v10 §V should treat this as a
contribution claim alongside the audit-driven generation
framework + layered defense-in-depth validators.

---

## §10 — Next Phase Roadmap

### §10.1 — Phase 1.G — Adaptive Attacker

Reviewer-mandatory sub-project per Phase 1.F audit feedback.
Estimated 3–5 days wall. Can begin once Phase 1.E batched push
completes (user manual). Independent of paper rewrite.

### §10.2 — Paper rewrite (§V + §VI + §VII + integration)

All 12 S-findings + 2 RESOLVED decisions need paper placement.
Master `PHASE_1E_RESULTS.md` §11 + this doc §9 provide
finding-to-section traceability. Estimated 15–20 hours focused
writing.

### §10.3 — Realistic timeline to v10 submission-ready

~3 weeks from Phase 1.E batched push:
- Week 1: Phase 1.G adaptive attacker (parallel-track with start
  of paper rewrite)
- Week 2: Paper §V + §VI + §VII drafts
- Week 3: Integration + review + final polish

---

*End of `PHASE_1E_E1_6_RESULTS.md` Part 2. Phase 1.E E1.6 sub-
phase PASS; Phase 1.E FULL LOGICAL CLOSE achieved (5 sub-phases
complete; 12 findings; 2 RESOLVED V2.5 decisions; corpus rename
commands prepared for user manual execution; batched commit +
push sequence ready). Standing by for user manual git operations
+ Phase 1.G kickoff.*
