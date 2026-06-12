# Phase 0' — Rerun Dependency Graph & Cost Tiers (READ-ONLY)

Companion to `report.md`. Textual dependency graph + minimal-viable vs full
rerun sets with total cost ranges. No execution; estimates only.

## 1. Dependency graph (text)

```
                 corpus_v2 (FROZEN ✓)  ──────────────┐
                      │                              │
                      ▼                              ▼
   [A] attack-corpus retarget/regen          [E] FPR retest  (OFFLINE, 0 API)
   (old S00xx ids → corpus_v2 ids;            (100 benign + 65 HN + 90 anc + 37 dec
    70 manual re-author + 201 variants)        through gate; deterministic)
                      │
                      ▼
   [B] B0/B2 main comparison  (defender = gpt-4o-mini)
   (B0 all 271; B2 only bypass; gates+scan offline)
                      │
        ┌─────────────┼──────────────┐
        ▼                            ▼
   [C] L1 judge                 [F] L2 taxonomy (§3.3)
   (3 arms × set; gpt-4o-2024-08-06)   (EDM/SIT/similarity/guardrail/doc-clf OFFLINE;
   *** dominant cost ***               LLM-self-check = API; net-new code)

   [D] 8-cell encoder×corpus + retrieval-utility (§3.4)
   (corpus_v2 → 4 encoders × 2 corpora; embedding + nDCG/recall@k = OFFLINE;
    per-cell leakage = optional gpt-4o-mini)   ── independent of A/B/C ──
```

### Ordering & parallelism constraints
- **Hard chain: A → B → {C, F}.** Attacks must be retargeted (A) before the main
  comparison (B) can produce arm outputs; C (judge) and F (L2 classify) both
  consume B's response set.
- **C and F are siblings** off B (can run concurrently once B is done; C is the
  cost driver, F is mostly offline + a small LLM-self-check).
- **D is independent of A–C** (consumes corpus_v2 directly) → fully parallelizable;
  its §3.4 retrieval-utility deliverable is 100% offline.
- **E is independent of A–C** and **fully offline** → can run anytime, zero cost.
- **F depends on A** only transitively (via B's responses). The 4–5 offline
  mechanism classes of F can be prototyped before B; only LLM-self-check waits on B.

### Net-new code (NOT just reruns) — flagged
- F (L2) — no existing script.
- D's retrieval-utility metric (nDCG@k/recall@k) + its relevance-label set — undefined.
- A's old→new secret id map + mechanical/rewrite triage list — undefined.
- (If FPR is redefined to response-level) an LLM-FPR path — does not exist today.

## 2. Minimal-viable rerun set (descope to the safety-critical, offline-max)

Goal: refresh only what the corpus_v2 restructure strictly invalidates, pushing
everything possible offline and descoping the judge.

- **E** FPR retest — offline — **$0.00**
- **D (§3.4 only)** retrieval-utility + 8-cell embedding — offline — **$0.00**
- **A (mechanical-max)** retarget by id/param swap; auto-rewrite only the variants
  that cannot be swapped — **$0.00–$0.05**
- **B** B0/B2 main comparison — **$0.05–$0.12**
- **C (descoped)** L1 judge on the **144 isolation set only**, exploiting the
  response-hash cache so only changed responses are re-judged — **≤$0.79**
- **F (offline classes only; defer LLM-self-check)** — **$0.00**

**Minimal-viable total ≈ $0.10 – $0.96** (dominated by the descoped C).

## 3. Full rerun set

Everything, judge on the full 271×3, per-cell leakage, LLM-self-check.

- A (full rewrite of 201 variants) — $0.05
- B (271 B0 + ~150 B2) — $0.12
- C (271 × 3 arms judged) — $1.49
- D (8-cell + per-cell leakage n=5) — $0.70
- E — $0.00
- F (incl. LLM-self-check over full response set) — $0.30

**Full total ≈ $2.6 – $2.9** (gpt-4o-mini portions ~$1.1; gpt-4o judge ~$1.5).

## 4. Budget verdict (standing cost discipline)

Standing cap = **$0.10/step, $0.40 total.**

| tier | total est. | vs $0.40 cap |
|------|-----------:|--------------|
| minimal-viable | $0.10–$0.96 | **exceeds** (C alone can breach) |
| full | $2.6–$2.9 | **exceeds ~6–7×** |

**Both tiers breach the standing total cap; C (L1 judge) is the sole reason the
minimal tier breaches.** Recommended stop-gate ladder before ANY execution:

1. Run the genuinely-free, independent work first if Peter approves *zero-cost*
   scope only: **E (FPR)** and **D §3.4 retrieval-utility** — $0.00, unblock early signal.
2. For anything with API cost (A-rewrite, B, C, D-leakage, F-self-check): obtain an
   **explicit Peter budget authorization above $0.40**, OR descope C to the cached/
   changed-only subset, before launching.
3. Honor per-step $0.10: if any single arm/cell exceeds it mid-run, **halt and report**.

This audit performs no execution and makes no API call; the budget decision is
Peter's.
