# D1.1 — Marker-Style Ablation (decompose style vs content AUC)

Derived experiment. Frozen corpus_v2 untouched; neutralized positives written only to this dir. Mechanically neutralizes institutional-voice markers in the 90 atomic positives, then re-runs the style-sensitive mechanisms vs UNCHANGED negatives/KB. M1 (exact-literal) and M4 (numeric-density) are marker-independent and SKIPPED.

## Setup

- Encoder: `sentence-transformers/all-MiniLM-L6-v2` (sentence-transformers `5.2.2`)
- Python `3.12.2` | macOS-14.5-arm64-arm-64bit | run 2026-06-11
- positives=90 (neutralized), neg(main)=90 anchor, neg(stress)=37 decoy, KB=90.
- atomic positives carrying >=1 marker before neutralization: 60/90.
- residual markers after neutralization: NONE (M5 vocab fully eliminated).
- Rule table: see the module docstring (R01-R18, deterministic, ordered).

## Original vs neutralized — AUC (main negatives)

| mechanism | AUC original | AUC neutralized | Δ (style contribution) |
|-----------|-------------:|----------------:|-----------------------:|
| M2 | 0.8279 | 0.8219 | +0.0060 |
| M3 | 0.8788 | 0.8536 | +0.0252 |
| M5 | 0.8281 | 0.4944 | +0.3337 |

| skipped | reason |
|---------|--------|
| M1 exact-literal | marker-independent (matches numeric/parameter literals; neutralization touches no literals) |
| M4 numeric-density | marker-independent (counts numeric tokens; unchanged by neutralization) |

## Operating points + decoy FP (original vs neutralized)

### M2

| variant | target FPR | threshold | actual FPR | TPR | decoy FP (stress) |
|---------|-----------:|----------:|-----------:|----:|------------------:|
| original | 0% | 0.0400 | 0.0000 | 0.5000 | 0.0000 |
| original | 1% | 0.0400 | 0.0000 | 0.5000 | 0.0000 |
| original | 5% | 0.0192 | 0.0444 | 0.6667 | 0.0270 |
| neutralized | 0% | 0.0400 | 0.0000 | 0.4889 | 0.0000 |
| neutralized | 1% | 0.0400 | 0.0000 | 0.4889 | 0.0000 |
| neutralized | 5% | 0.0192 | 0.0444 | 0.6556 | 0.0270 |

### M3

| variant | target FPR | threshold | actual FPR | TPR | decoy FP (stress) |
|---------|-----------:|----------:|-----------:|----:|------------------:|
| original | 0% | 0.7448 | 0.0000 | 0.2556 | 0.0000 |
| original | 1% | 0.7448 | 0.0000 | 0.2556 | 0.0000 |
| original | 5% | 0.6695 | 0.0444 | 0.5000 | 0.0000 |
| neutralized | 0% | 0.7448 | 0.0000 | 0.1889 | 0.0000 |
| neutralized | 1% | 0.7448 | 0.0000 | 0.1889 | 0.0000 |
| neutralized | 5% | 0.6695 | 0.0444 | 0.4778 | 0.0000 |

### M5

| variant | target FPR | threshold | actual FPR | TPR | decoy FP (stress) |
|---------|-----------:|----------:|-----------:|----:|------------------:|
| original | 0% | 2.0000 | 0.0000 | 0.0667 | 0.1081 |
| original | 1% | 2.0000 | 0.0000 | 0.0667 | 0.1081 |
| original | 5% | 1.0000 | 0.0111 | 0.6667 | 0.2703 |
| neutralized | 0% | n/a | 0.0000 | 0.0000 | n/a |
| neutralized | 1% | n/a | 0.0000 | 0.0000 | n/a |
| neutralized | 5% | 1.0000 | 0.0111 | 0.0000 | 0.2703 |

## Pre-registration reconciliation

### (a) M5 (marker-vocab) AUC collapses to ~0.5

- M5 AUC: 0.8281 -> 0.4944. **VERDICT: HELD** (markers eliminated -> mechanism has no signal left; residual offset only from any marker remaining in NEGATIVES, which were not neutralized).

### (b) M3 (embedding) AUC drops; Δ = style, residual-above-0.5 = content

- M3 AUC: 0.8788 -> 0.8536.
- **style contribution Δ = +0.0252**.
- **content contribution (neutralized AUC - 0.5) = +0.3536** (the key reading: separability that survives marker removal = proprietary semantic content).

### (c) M2 (n-gram) drops slightly

- M2 AUC: 0.8279 -> 0.8219 (Δ=+0.0060). **VERDICT: HELD (small drop)**.

## Sample transforms (10)

- **p0_01** (rules R01):
    - orig: A 10-day RSI reading below 24 indicates an oversold condition and is used as our desk's mean-reversion entry signal.
    - neut: A 10-day RSI reading below 24 indicates an oversold condition and is used as a mean-reversion entry signal.
- **p0_02** (rules R17a):
    - orig: Our momentum factor is the exponentially weighted sum of daily log excess returns over a 378-day window with a 10-day lag and a 63-day half-life.
    - neut: The momentum factor is the exponentially weighted sum of daily log excess returns over a 378-day window with a 10-day lag and a 63-day half-life.
- **p0_03** (rules R10,R17a):
    - orig: Our internal single-issuer concentration cap is 6.5% of NAV, tighter than the UCITS 10% limit.
    - neut: The single-issuer concentration cap is 6.5% of NAV, tighter than the UCITS 10% limit.
- **p0_04** (rules R07):
    - orig: The desk suspends algo participation when price comes within 1.2% of the LULD band.
    - neut: The strategy suspends algo participation when price comes within 1.2% of the LULD band.
- **p0_07** (rules R17a):
    - orig: Our VWAP curve blends the 20-day average volume profile 60/40 with the same-weekday profile.
    - neut: The VWAP curve blends the 20-day average volume profile 60/40 with the same-weekday profile.
- **p0_08** (rules R02,R10):
    - orig: The ops desk triggers auto-borrow when the internal fail-probability score exceeds 60%.
    - neut: The strategy triggers auto-borrow when the fail-probability score exceeds 60%.
- **p0_09** (rules R17b):
    - orig: The Black-Litterman uncertainty scalar tau is set to 0.018 in our configuration.
    - neut: The Black-Litterman uncertainty scalar tau is set to 0.018 in the configuration.
- **p0_10** (rules R17a):
    - orig: Our framework classifies holdings into four liquidity buckets and holds the HLIM at 12%; bucket classification assumes participation up to 15% of ADV.
    - neut: The framework classifies holdings into four liquidity buckets and holds the HLIM at 12%; bucket classification assumes participation up to 15% of ADV.
- **p0_12** (rules R05):
    - orig: Our desk sets reservation price and optimal spread as functions of inventory, with the risk-aversion parameter gamma calibrated to 0.12.
    - neut: The strategy sets reservation price and optimal spread as functions of inventory, with the risk-aversion parameter gamma calibrated to 0.12.
- **p0_14** (rules R17a):
    - orig: Our CPPI implementation allocates a multiple m = 4.2 of the cushion (portfolio value minus floor) to the risky asset.
    - neut: The CPPI implementation allocates a multiple m = 4.2 of the cushion (portfolio value minus floor) to the risky asset.
