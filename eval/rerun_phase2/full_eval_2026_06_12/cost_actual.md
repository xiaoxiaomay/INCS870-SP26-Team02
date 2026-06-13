# Full Eval — Actual Cost

- B (gpt-4o-mini): total $0.031917 (bypass 65/90).
- C (gpt-4o judge): this-run cost $0.581175 (if C was topped up, l1_judge_summary records only the LAST run — add prior runs for cumulative).
- F LLM-self-check (gpt-4o-mini): $0.00977 (n=90).
- guardrail Prompt-Guard-86M: SKIPPED (gated/unavailable).

## Total + reconciliation
- **B + C + F = $0.031917 + $0.581175 + $0.00977 = $0.62286.**
- vs task estimate $0.65–0.95 -> **slightly under**. C was a single run (no top-up), so its
  $0.581 is the full cumulative C cost.
- per-step note (as authorized for full eval, recorded not halted): the **C step $0.581
  far exceeds the standing $0.10/step cap** — explicitly authorized for the full run; logged here.
