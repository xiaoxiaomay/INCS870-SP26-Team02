# SentinelFlow Known Issues

Cross-phase issue tracker. Entries are non-blocking and
queued for cleanup during low-pressure windows (typically
paper-rewrite weeks, Phase 3).

---

## Issue #1: Verifier exit-code bug

- **File**: scripts/verify_repro_pins.py
- **Symptom**: Prints "OVERALL: FAIL" but exits with code 0
- **Impact**: Pre-commit hooks / CI checking $? get
  false-positive PASS. Currently mitigated by manual review
  of verifier output.
- **Severity**: Low (no actual harm; manual review catches it)
- **Fix scope**: ~5 LOC in verify_repro_pins.py main() —
  track FAIL state and `sys.exit(1)` on overall failure
- **Defer to**: Phase 3 paper rewrite week (if time permits)
- **Discovered**: 2026-05-12 during Phase 1.E Step 2 L3
  verification
- **Discovered by**: Claude Code self-audit during L3 run

---

## Issue #2: Verifier env-var inheritance limitation

- **File**: scripts/verify_repro_pins.py (L3 module)
- **Symptom**: L3 fails with "OPENAI_API_KEY not set" when
  run via subprocess that doesn't inherit shell env (e.g.,
  Claude Code's bash tool)
- **Impact**: L3 must be run from user shell with `.env`
  sourced. Documented in user-facing workflow but breaks
  fully-automated CI.
- **Severity**: Low (workaround documented; no incorrect
  results, just blocked execution)
- **Fix scope**: Add `--dotenv-file <path>` optional flag to
  verifier; if present, load env from file before L3 subprocess
  invocation. ~15 LOC.
- **Defer to**: Phase 3 paper rewrite week
- **Discovered**: 2026-05-12 during Phase 1.E Step 2 L3
  verification

---

## Issue #3: Inline magic number for cost estimation

- **File**: eval/run_full_pipeline_eval.py:150
- **Symptom**: Hardcoded `0.15` for gpt-4o-mini input pricing
  with comment but no named constant
- **Impact**: If pricing changes or defender model swaps,
  this magic number doesn't auto-sync with
  scripts/repro_full_pipeline.py canonical constants. Paper-
  code drift hazard.
- **Severity**: Low (currently only used for stderr pre-
  flight estimate when OPENAI_API_KEY is missing — not in
  main cost reporting path)
- **Fix scope**: Replace `0.15` with import + reference to
  PRICE_INPUT_PER_1M_GPT4OMINI from scripts/repro_full_pipeline.py
  (or move pricing to a shared module if Phase 3 does
  Option A refactor)
- **Defer to**: Phase 3 paper rewrite week (likely bundled
  with eventual cost_tracker.py module creation)
- **Discovered**: 2026-05-12 during Phase 1.E Step 3 pricing
  inventory
- **Discovered by**: Claude Code self-audit during Step 3.1

---

## Issue #4: Validator first-violation-then-raise behavior

- **File**: scripts/generate_hard_negatives.py `validate_generated()`
- **Symptom**: Validator raises on first entry violation, losing
  visibility into entries 1–4 in the batch
- **Impact**:
  - Cost incurred but data lost (entries 1–4 never inspected)
  - Cannot determine if other entries also have violations
  - Cannot do partial acceptance (keep passing entries)
- **Severity**: Low (development workflow inefficiency, not
  correctness bug)
- **Fix scope**: Refactor validator to collect all violations
  across batch, raise single comprehensive report
- **Defer to**: Phase 3 cleanup or after E1.2 mass-generation if
  recurring
- **Discovered**: 2026-05-12 during Phase 1.E Step 4.5 C_ed smoke
  test
- **Discovered by**: Claude Code self-audit during validator raise

---

## Issue #5: GPT-5 mini reasoning_tokens consume max_completion_tokens budget

- **File**: scripts/generate_hard_negatives.py (and any future
  GPT-5-family API usage)
- **Symptom**: Default `reasoning_effort="medium"` can consume
  1500+ tokens of internal reasoning, leaving insufficient
  budget for JSON output → empty content returned. Confirmed
  empirically on 2026-05-12: 1-query call returned
  reasoning_tokens=1472, output=92 (94% reasoning, 6% output).
  5-query call without fix returned empty content (reasoning
  consumed full 4000-token budget).
- **Impact**: Generation failures, wasted API calls, hard to
  debug without `completion_tokens_details.reasoning_tokens`
  visibility
- **Severity**: Medium (recurring, can block generation
  entirely; cost incurred even on empty responses)
- **Mitigation** (applied 2026-05-12):
  1. Set `reasoning_effort="minimal"` for structured-output
     tasks (templated generation, JSON-format response).
     SDK 2.24.0+ supports this as an explicit param on
     `client.chat.completions.create()`.
  2. Bump `max_completion_tokens` from 4000 to 8000 (2× safety
     vs reasoning consumption — even with minimal effort, the
     headroom is cheap insurance).
  3. Always log `completion_tokens_details.reasoning_tokens`
     in debug output for visibility (see `call_llm_with_retry`
     diagnostic block).
  4. Use `response_format={"type": "json_object"}` to constrain
     output (already in place).
- **Defer to**: N/A (mitigated 2026-05-12 via Step 4.5 fix;
  remediation in `scripts/generate_hard_negatives.py:call_llm_with_retry`)
- **Discovered**: 2026-05-12 during Phase 1.E Step 4.5 C_ed
  smoke test attempt 2 (empty content failure)
- **Discovered by**: Claude Code stop-and-disclose + user web
  search fact-check

---

End of known issues.
