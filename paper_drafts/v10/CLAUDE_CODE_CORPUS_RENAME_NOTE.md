# V2 §5.1 Corpus Rename — Approach A (Surgical) Audit Note

> **Generated:** 2026-05-26 (post-v0.5 commit, pre-LaTeX
> conversion).
>
> **Decision rationale:** Approach A (surgical) chosen over
> Approach B (full rename). Only active scripts + paper-facing
> §V.C draft updated. Historical records preserved unchanged
> to maintain audit-trail integrity per the project's
> documented "no historical revisionism" discipline.

---

## Scope

### Files modified (4)

| File | Lines modified | Type of change |
| --- | --- | --- |
| `scripts/generate_hard_negatives.py` | 8, 34, 474 | docstring + `DEFAULT_SEEDS_PATH` constant + argparse help |
| `scripts/validate_hard_negatives.py` | 5, 25, 28–33, 70 | docstring + `HARD_NEG_PATH` constant + `.bak` runtime/historical clarification |
| `paper_drafts/v10/v10_paper_section_V_C_phase1E_draft.md` | 669 + migration footnote | paper-facing corpus path + provenance prose |
| `paper_drafts/v10/CLAUDE_CODE_CORPUS_RENAME_NOTE.md` | NEW | this audit note |

### Files preserved unchanged (rationale: historical record integrity)

- `data/benchmark/hard_negatives_seeds_draft.jsonl.bak` — Phase 1.E E1.3.2 backup, on-disk filename preserved.
- `data/benchmark/hard_negatives_seeds_draft.jsonl.preV1a` — pre-V1a backup, on-disk filename preserved.
- `PHASE_1E_E1_1_RESULTS.md` … `PHASE_1E_E1_6_RESULTS.md` — Phase 1.E execution log.
- `PHASE_1E_RESULTS.md` — master Phase 1.E results.
- `PHASE_1E_STATUS.md` — Phase 1.E status.
- `eval/results/phase1_E/validation/v1a_band_report.md` — V1a validator output snapshot.
- `eval/results/phase1_E/validation/v2_benign_check_report.md` — V2 validator output snapshot.
- `eval/results/phase1_E/validation/outlier_inventory.md` — outlier-disposition snapshot.
- `paper_drafts/v10/CLAUDE_CODE_VERIFICATION_REPORT.md` — Round-2 verification record.
- `paper_drafts/v10/CLAUDE_CODE_V0.4_AUDIT_REPORT.md` — v0.4 review record.
- `paper_drafts/v10/CLAUDE_CODE_V0.5_AUDIT_REPORT.md` — v0.5 review record.

These files reference the corpus by its name AT THE TIME of execution/review. Rewriting them retroactively would constitute historical revisionism contrary to the project's audit-grade discipline.

---

## Deviations from the Approach A spec

| # | Deviation | Reason |
| --- | --- | --- |
| 1 | **§V.C migration footnote contains old path name** in prose at line 671. | The migration footnote by definition must name the file it was renamed FROM. The post-edit grep returns 1 ref in §V.C (the footnote's documentation prose), not the "empty" the spec expected. This is a documentation necessity, not a missed substitution. |
| 2 | **Validator line 28–33 rewritten beyond the suggested two-line replacement.** | The validator's `.bak` path is **runtime-derived** from `HARD_NEG_PATH` (see line 921: `bak_path = HARD_NEG_PATH.with_suffix(HARD_NEG_PATH.suffix + ".bak")`). Post-rename, future validator runs will create `hard_negatives.jsonl.bak`, NOT the literal `hard_negatives_seeds_draft.jsonl.bak`. The docstring at lines 23–29 documents the validator's runtime "Outputs" — keeping it accurate to runtime behavior requires using the new `.bak` filename. To also satisfy the spec's "preserve `.bak` filepath" instruction, the rewrite documents both: (a) what the validator writes at runtime (`hard_negatives.jsonl.bak`) and (b) the pre-rename historical artifact on disk (`hard_negatives_seeds_draft.jsonl.bak`). This is more honest than the literal-preservation interpretation. |

---

## Verification

Post-edit grep on the 4 modified files:

```bash
grep -rn "hard_negatives_seeds_draft" \
  scripts/generate_hard_negatives.py \
  scripts/validate_hard_negatives.py \
  paper_drafts/v10/v10_paper_section_V_C_phase1E_draft.md
```

**Actual output (post-edit):**

```
paper_drafts/v10/v10_paper_section_V_C_phase1E_draft.md:671:  `hard_negatives_seeds_draft.jsonl` per V2 §5.1 spec on
scripts/validate_hard_negatives.py:31:  data/benchmark/hard_negatives_seeds_draft.jsonl.bak also exists on
```

Both refs are intentional documentation:
- §V.C line 671 — migration footnote (names what the file was renamed FROM).
- Validator line 31 — historical artifact reference (pre-rename `.bak` on disk).

`scripts/generate_hard_negatives.py` has **zero** refs (cleanly substituted).

---

## User git commands (when ready to commit)

After verifying the above is acceptable, the user runs:

```bash
cd ~/Downloads/sentinelflow

# Stage 1: rename the file on disk (preserves git history via git mv)
git mv data/benchmark/hard_negatives_seeds_draft.jsonl \
       data/benchmark/hard_negatives.jsonl

# Verify the rename succeeded (active corpus renamed; .bak + .preV1a unchanged)
ls -la data/benchmark/hard_negatives*

# Stage 2: stage the modified code + draft + audit-note files
git add scripts/generate_hard_negatives.py
git add scripts/validate_hard_negatives.py
git add paper_drafts/v10/v10_paper_section_V_C_phase1E_draft.md
git add paper_drafts/v10/CLAUDE_CODE_CORPUS_RENAME_NOTE.md

# Verify what's staged
git status
git diff --stat --cached HEAD

# Stage 3: commit
git commit -m "V2 §5.1 corpus rename: hard_negatives_seeds_draft.jsonl → hard_negatives.jsonl

Approach A (surgical): only active scripts + §V.C paper draft updated.
Historical records (Phase 1.E logs, audit reports, eval outputs,
.bak/.preV1a backups) preserved unchanged to maintain audit-trail
integrity.

Files modified (4):
- scripts/generate_hard_negatives.py (3 refs)
- scripts/validate_hard_negatives.py (4 refs; line 31 preserves
  reference to historical .bak artifact)
- paper_drafts/v10/v10_paper_section_V_C_phase1E_draft.md
  (1 ref + migration footnote)
- paper_drafts/v10/CLAUDE_CODE_CORPUS_RENAME_NOTE.md (NEW audit note)

Active corpus renamed via git mv (preserves git blame history).
Backup files (.bak, .preV1a) retain original names as historical
artifacts. See CLAUDE_CODE_CORPUS_RENAME_NOTE.md for scope rationale."

# Optional: push (or batch with later commits)
# git push origin main
```

## Post-rename smoke tests (user runs)

```bash
# Confirm validator can read the new path
python3 scripts/validate_hard_negatives.py --help | head -20

# Confirm generator can read the new path
python3 scripts/generate_hard_negatives.py --help | grep -A 1 "JSONL file"

# Confirm corpus intact at new path
wc -l data/benchmark/hard_negatives.jsonl
# Expected: 65

# Confirm .bak files unchanged
ls -lh data/benchmark/hard_negatives_seeds_draft.jsonl*
# Expected: .bak (75K) + .preV1a (33K) — both preserved
```

Expected: validator + generator help text show the new path; corpus has 65 entries; both `.bak` historical backups intact.

---

*End of `CLAUDE_CODE_CORPUS_RENAME_NOTE.md`. The rename
is staged for the user's manual `git mv` + `git commit`.
After the commit, the active corpus name aligns with the
V2 §5.1 spec and the v10 paper's published name.*
