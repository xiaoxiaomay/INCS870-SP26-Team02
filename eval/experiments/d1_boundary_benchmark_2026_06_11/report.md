# D1 — Offline Boundary-Separability Benchmark

MEASUREMENT / benchmark only — maps the detection surface on the FROZEN corpus_v2. No pass/fail on the corpus.

## Setup

- Encoder: `sentence-transformers/all-MiniLM-L6-v2` (sentence-transformers `5.2.2`)
- Python `3.12.2` | macOS-14.5-arm64-arm-64bit | run 2026-06-11
- Reference KB = 90 secret_text (bundle).
- Positives = 90 atomic_text (faithful-restatement proxy, NOT in KB).
- Negatives(main) = 90 anchor-kind HN.
- Negatives(stress) = 37 decoy HN — shortcut stress, **NEVER part of the main metric**.
- M1 protected literal set: 96 strong literals (extracted via scripts/parameter_presence.py, reused unmodified).
- cosine = dot of L2-normalized embeddings; AUC = Mann-Whitney (ties=0.5).

## Summary — AUC (main negatives)

| mechanism | description | AUC |
|-----------|-------------|----:|
| M1 | exact-literal (binary; protected set from parameter_presence.py) | 0.6167 |
| M2 | max word-4-gram Jaccard vs KB | 0.8279 |
| M3 | max cosine vs KB (MiniLM — deployment gate mechanism) | 0.8788 |
| M4 | numeric-token count (trivial baseline) | 0.4327 |
| M5 | marker-vocab hit count | 0.8281 |

## M1 — exact-literal (binary; protected set from parameter_presence.py)

- AUC (main) = 0.6167
- M1 is BINARY: the operating point below is its single (FPR, TPR); AUC of a binary point = (TPR + (1-FPR))/2.

| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |
|-----------:|----------:|-----------:|----:|----------------------------:|
| 0% | n/a | 0.0000 | 0.0000 | n/a |
| 1% | n/a | 0.0000 | 0.0000 | n/a |
| 5% | 1.0000 | 0.0111 | 0.2444 | 0.0000 |

- score dist — positives: n=90 mean=0.2444 median=0.0000 min=0.0000 max=1.0000
- score dist — neg(main): n=90 mean=0.0111 median=0.0000 min=0.0000 max=1.0000
- score dist — decoy(stress): n=37 mean=0.0000 median=0.0000 min=0.0000 max=0.0000

Slice AUC (pos vs neg within slice):

| slice | n_pos | n_neg | AUC |
|-------|------:|------:|----:|
| Type A | 72 | 72 | 0.6111 |
| Type B | 18 | 18 | 0.6389 |
| core | 81 | 81 | 0.5988 |
| boundary_test | 9 | 9 | 0.7778 |

Per-domain AUC:

| domain | n_pos | n_neg | AUC |
|--------|------:|------:|----:|
| credit_screening | 6 | 6 | 0.5833 |
| exchange_rule_execution | 5 | 5 | 0.5000 |
| execution_scheduling | 5 | 5 | 0.5000 |
| execution_vwap | 5 | 5 | 0.5000 |
| factor_model | 6 | 6 | 0.6667 |
| liquidity_management | 6 | 6 | 0.5833 |
| market_making | 6 | 6 | 0.7500 |
| portfolio_construction | 6 | 6 | 0.6667 |
| portfolio_insurance | 4 | 4 | 0.7500 |
| position_sizing | 6 | 6 | 0.7500 |
| prime_brokerage_margin | 6 | 6 | 0.6667 |
| regulatory_concentration | 5 | 5 | 0.6000 |
| risk_model | 6 | 6 | 0.5833 |
| settlement_ops | 6 | 6 | 0.6667 |
| stat_arb | 6 | 6 | 0.5833 |
| technical_indicator | 6 | 6 | 0.5000 |

Positive score dist by offset_type — A: n=72 mean=0.2361 median=0.0000 min=0.0000 max=1.0000 | B: n=18 mean=0.2778 median=0.0000 min=0.0000 max=1.0000

## M2 — max word-4-gram Jaccard vs KB

- AUC (main) = 0.8279

| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |
|-----------:|----------:|-----------:|----:|----------------------------:|
| 0% | 0.0400 | 0.0000 | 0.5000 | 0.0000 |
| 1% | 0.0400 | 0.0000 | 0.5000 | 0.0000 |
| 5% | 0.0192 | 0.0444 | 0.6667 | 0.0270 |

- score dist — positives: n=90 mean=0.0685 median=0.0379 min=0.0000 max=0.3333
- score dist — neg(main): n=90 mean=0.0018 median=0.0000 min=0.0000 max=0.0364
- score dist — decoy(stress): n=37 mean=0.0009 median=0.0000 min=0.0000 max=0.0333

Slice AUC (pos vs neg within slice):

| slice | n_pos | n_neg | AUC |
|-------|------:|------:|----:|
| Type A | 72 | 72 | 0.7915 |
| Type B | 18 | 18 | 0.9707 |
| core | 81 | 81 | 0.8363 |
| boundary_test | 9 | 9 | 0.7531 |

Per-domain AUC:

| domain | n_pos | n_neg | AUC |
|--------|------:|------:|----:|
| credit_screening | 6 | 6 | 0.6667 |
| exchange_rule_execution | 5 | 5 | 1.0000 |
| execution_scheduling | 5 | 5 | 0.9000 |
| execution_vwap | 5 | 5 | 0.6400 |
| factor_model | 6 | 6 | 0.9167 |
| liquidity_management | 6 | 6 | 0.7500 |
| market_making | 6 | 6 | 0.8333 |
| portfolio_construction | 6 | 6 | 0.8056 |
| portfolio_insurance | 4 | 4 | 0.6250 |
| position_sizing | 6 | 6 | 1.0000 |
| prime_brokerage_margin | 6 | 6 | 0.8333 |
| regulatory_concentration | 5 | 5 | 0.9000 |
| risk_model | 6 | 6 | 0.7083 |
| settlement_ops | 6 | 6 | 1.0000 |
| stat_arb | 6 | 6 | 0.9167 |
| technical_indicator | 6 | 6 | 0.7500 |

Positive score dist by offset_type — A: n=72 mean=0.0566 median=0.0267 min=0.0000 max=0.2941 | B: n=18 mean=0.1158 median=0.0981 min=0.0000 max=0.3333

## M3 — max cosine vs KB (MiniLM — deployment gate mechanism)

- AUC (main) = 0.8788

| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |
|-----------:|----------:|-----------:|----:|----------------------------:|
| 0% | 0.7448 | 0.0000 | 0.2556 | 0.0000 |
| 1% | 0.7448 | 0.0000 | 0.2556 | 0.0000 |
| 5% | 0.6695 | 0.0444 | 0.5000 | 0.0000 |

- score dist — positives: n=90 mean=0.6707 median=0.6736 min=0.4149 max=0.9220
- score dist — neg(main): n=90 mean=0.5076 median=0.4957 min=0.3506 max=0.7447
- score dist — decoy(stress): n=37 mean=0.4652 median=0.4699 min=0.2661 max=0.6604

Slice AUC (pos vs neg within slice):

| slice | n_pos | n_neg | AUC |
|-------|------:|------:|----:|
| Type A | 72 | 72 | 0.8657 |
| Type B | 18 | 18 | 0.9290 |
| core | 81 | 81 | 0.8951 |
| boundary_test | 9 | 9 | 0.7654 |

Per-domain AUC:

| domain | n_pos | n_neg | AUC |
|--------|------:|------:|----:|
| credit_screening | 6 | 6 | 1.0000 |
| exchange_rule_execution | 5 | 5 | 0.8800 |
| execution_scheduling | 5 | 5 | 0.8800 |
| execution_vwap | 5 | 5 | 0.7200 |
| factor_model | 6 | 6 | 0.9167 |
| liquidity_management | 6 | 6 | 0.8056 |
| market_making | 6 | 6 | 0.8889 |
| portfolio_construction | 6 | 6 | 0.8889 |
| portfolio_insurance | 4 | 4 | 0.8125 |
| position_sizing | 6 | 6 | 0.8333 |
| prime_brokerage_margin | 6 | 6 | 0.7778 |
| regulatory_concentration | 5 | 5 | 1.0000 |
| risk_model | 6 | 6 | 0.8611 |
| settlement_ops | 6 | 6 | 0.9444 |
| stat_arb | 6 | 6 | 0.9444 |
| technical_indicator | 6 | 6 | 0.9167 |

Positive score dist by offset_type — A: n=72 mean=0.6617 median=0.6607 min=0.4149 max=0.9220 | B: n=18 mean=0.7064 median=0.7330 min=0.5005 max=0.8139

## M4 — numeric-token count (trivial baseline)

- AUC (main) = 0.4327

| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |
|-----------:|----------:|-----------:|----:|----------------------------:|
| 0% | n/a | 0.0000 | 0.0000 | n/a |
| 1% | n/a | 0.0000 | 0.0000 | n/a |
| 5% | 5.0000 | 0.0222 | 0.0000 | 0.4595 |

- score dist — positives: n=90 mean=1.8111 median=2.0000 min=0.0000 max=3.0000
- score dist — neg(main): n=90 mean=2.0889 median=2.0000 min=0.0000 max=7.0000
- score dist — decoy(stress): n=37 mean=3.4595 median=3.0000 min=0.0000 max=10.0000

Slice AUC (pos vs neg within slice):

| slice | n_pos | n_neg | AUC |
|-------|------:|------:|----:|
| Type A | 72 | 72 | 0.4552 |
| Type B | 18 | 18 | 0.3395 |
| core | 81 | 81 | 0.4204 |
| boundary_test | 9 | 9 | 0.5494 |

Per-domain AUC:

| domain | n_pos | n_neg | AUC |
|--------|------:|------:|----:|
| credit_screening | 6 | 6 | 0.3333 |
| exchange_rule_execution | 5 | 5 | 0.2000 |
| execution_scheduling | 5 | 5 | 0.3200 |
| execution_vwap | 5 | 5 | 0.4200 |
| factor_model | 6 | 6 | 0.5833 |
| liquidity_management | 6 | 6 | 0.3472 |
| market_making | 6 | 6 | 0.4444 |
| portfolio_construction | 6 | 6 | 0.3750 |
| portfolio_insurance | 4 | 4 | 0.5000 |
| position_sizing | 6 | 6 | 0.7361 |
| prime_brokerage_margin | 6 | 6 | 0.4444 |
| regulatory_concentration | 5 | 5 | 0.0600 |
| risk_model | 6 | 6 | 0.4167 |
| settlement_ops | 6 | 6 | 0.5000 |
| stat_arb | 6 | 6 | 0.5000 |
| technical_indicator | 6 | 6 | 0.5556 |

Positive score dist by offset_type — A: n=72 mean=1.8889 median=2.0000 min=0.0000 max=3.0000 | B: n=18 mean=1.5000 median=2.0000 min=0.0000 max=2.0000

## M5 — marker-vocab hit count

- AUC (main) = 0.8281

| target FPR | threshold | actual FPR | TPR | decoy FP (stress, non-main) |
|-----------:|----------:|-----------:|----:|----------------------------:|
| 0% | 2.0000 | 0.0000 | 0.0667 | 0.1081 |
| 1% | 2.0000 | 0.0000 | 0.0667 | 0.1081 |
| 5% | 1.0000 | 0.0111 | 0.6667 | 0.2703 |

- score dist — positives: n=90 mean=0.7444 median=1.0000 min=0.0000 max=3.0000
- score dist — neg(main): n=90 mean=0.0111 median=0.0000 min=0.0000 max=1.0000
- score dist — decoy(stress): n=37 mean=0.3784 median=0.0000 min=0.0000 max=2.0000

Slice AUC (pos vs neg within slice):

| slice | n_pos | n_neg | AUC |
|-------|------:|------:|----:|
| Type A | 72 | 72 | 0.8477 |
| Type B | 18 | 18 | 0.7500 |
| core | 81 | 81 | 0.8276 |
| boundary_test | 9 | 9 | 0.8333 |

Per-domain AUC:

| domain | n_pos | n_neg | AUC |
|--------|------:|------:|----:|
| credit_screening | 6 | 6 | 0.8333 |
| exchange_rule_execution | 5 | 5 | 0.9000 |
| execution_scheduling | 5 | 5 | 0.8000 |
| execution_vwap | 5 | 5 | 1.0000 |
| factor_model | 6 | 6 | 0.9167 |
| liquidity_management | 6 | 6 | 0.8333 |
| market_making | 6 | 6 | 0.7500 |
| portfolio_construction | 6 | 6 | 0.8333 |
| portfolio_insurance | 4 | 4 | 0.8750 |
| position_sizing | 6 | 6 | 0.7500 |
| prime_brokerage_margin | 6 | 6 | 0.6667 |
| regulatory_concentration | 5 | 5 | 1.0000 |
| risk_model | 6 | 6 | 0.7639 |
| settlement_ops | 6 | 6 | 0.8333 |
| stat_arb | 6 | 6 | 0.5833 |
| technical_indicator | 6 | 6 | 1.0000 |

Positive score dist by offset_type — A: n=72 mean=0.7778 median=1.0000 min=0.0000 max=2.0000 | B: n=18 mean=0.6111 median=0.5000 min=0.0000 max=3.0000

## Pre-registration reconciliation

### (i) M3 has the highest AUC, but Type A vs B positive distributions are misaligned

- AUC ranking: M3=0.8788, M5=0.8281, M2=0.8279, M1=0.6167, M4=0.4327
- M3 highest AUC: **True**
- M3 positive median — Type A = 0.6607, Type B = 0.7330 (|gap| = 0.0722).
- M3 negative(main) median = 0.4957, max = 0.7447.
- **VERDICT: HELD.** M3 has the top AUC, yet at FPR=0% it recovers only 0.256 TPR (threshold 0.7448, just above the negative max 0.7447). Type B positives (median 0.7330) sit ~0.07 above Type A (0.6607), and the negative mass reaches into Type-A positive territory — so no single cosine threshold lands stably for both A and B. Detection-surface confirmation of the Phase 0.5/0.6 conclusion.

### (ii) M4 (numeric density) — expected non-trivial TPR in the high-FPR region

- M4 AUC(main) = 0.4327; TPR@FPR=5% = 0.0000; @20% = 0.0000; @50% = 0.1667.
- **VERDICT: DEVIATED.** On ATOMIC positives the numeric-density shortcut does NOT hold: AUC < 0.5 (anti-separating), TPR is 0 until FPR=50% (then only 0.167). The bundle-level numeric-density signal (check2 b3, where bundle secrets carried many more numbers than anchors) does NOT transfer to compressed single-parameter atomic restatements — atomic texts carry ~as few numbers as benign anchors. The 'count the numbers' shortcut is bundle-specific, not a property of leakage per se.

### (iii) M1 (exact-literal) TPR on atomic positives — the UPPER bound

- M1 TPR (atomic positives) = 0.2444; FPR(anchor) = 0.0111; decoy FP(stress) = 0.0000.
- **VERDICT: PARTIAL.** M1 recall is 0.244 — well above the S1 LLM-rewrite ~0 lower bound, so it does serve as the higher bracket, but it is MODEST, not 'high': only ~24% of atomic restatements retain a protected literal as an exact normalized substring. The achievable exact-literal recall on faithful paraphrase brackets at roughly [~0, 0.24], with near-zero FPR (1/90 anchor, 0 decoy). Compression drops most extractable literals even under faithful restatement, so the literal-matcher ceiling itself is low.

### (iv) Confound to flag — surface style markers (NOT pre-registered)

- M5 marker-vocab AUC = 0.8281, nearly equal to M2 n-gram (0.8279) and close to the M3 embedding gate (0.8788). M5 positives mean 0.744 vs neg(main) mean 0.011.
- Reading: a large share of the positive/negative separation is driven by STYLE markers (our/internal/desk/...) that the atomic restatements carry and the anchors do not — a trivial 7-word vocabulary nearly matches the embedding gate. The benchmark's separability therefore partly reflects surface style of the atomic proxy, not proprietary semantic content alone; interpret M3's headline AUC with this confound in mind.
