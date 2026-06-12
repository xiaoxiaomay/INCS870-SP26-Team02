# D2 — Encoder-Lever x Marker-Ablation Grid

Zero-API (HF downloads). Frozen corpus_v2 untouched; neutralized positives REUSED verbatim from D1.1. Mechanism = embedding NN (max cosine vs the 90-bundle KB).

## Setup

- Deployment encoder: `sentence-transformers/all-MiniLM-L6-v2`
- sentence-transformers `5.2.2` | Python `3.12.2` | macOS-14.5-arm64-arm-64bit
- run 2026-06-11
- KB=90 bundle | positives=90 (orig/neut arms) | neg(main)=90 anchor | neg(stress)=37 decoy
- neutralized source: d1_1_marker_ablation_2026_06_11/atomic_neutralized.jsonl (reused, not regenerated)

### Encoder protocols

- **minilm** `sentence-transformers/all-MiniLM-L6-v2` — plain (deployment baseline); no prefix
- **mpnet** `sentence-transformers/all-mpnet-base-v2` — plain symmetric; no prefix
- **e5** `intfloat/e5-large-v2` — E5: KB->'passage: ', scored candidates (pos+neg)->'query: ' (see deviation note); delta sym 'query: '
- **bge** `BAAI/bge-large-en-v1.5` — BGE v1.5: KB->raw, scored candidates->query instruction; delta sym raw

> **Deviation note (e5):** the task text assigned negatives the `passage: ` prefix, but negatives are SCORED candidates; scoring positives query-vs-passage and negatives passage-vs-passage would place the two classes on different similarity scales and invalidate the ROC. For validity ALL scored candidates (positives AND negatives) use `query: `; KB uses `passage: `.

## Grid — AUC, TPR@FPR_anchor, A/B median (main negatives)

| encoder | arm | AUC | TPR@0% | TPR@1% | TPR@5% | median A | median B |
|---------|-----|----:|-------:|-------:|-------:|---------:|---------:|
| minilm | orig | 0.8788 | 0.256 | 0.256 | 0.500 | 0.6607 | 0.7330 |
| minilm | neut | 0.8536 | 0.189 | 0.189 | 0.478 | 0.6524 | 0.6953 |
| mpnet | orig | 0.8464 | 0.133 | 0.133 | 0.411 | 0.6571 | 0.7009 |
| mpnet | neut | 0.8100 | 0.111 | 0.111 | 0.344 | 0.6343 | 0.6682 |
| e5 | orig | 0.9469 | 0.256 | 0.256 | 0.578 | 0.8650 | 0.8722 |
| e5 | neut | 0.9374 | 0.233 | 0.233 | 0.556 | 0.8626 | 0.8704 |
| bge | orig | 0.9094 | 0.156 | 0.156 | 0.600 | 0.7851 | 0.8109 |
| bge | neut | 0.8856 | 0.156 | 0.156 | 0.567 | 0.7766 | 0.8055 |

ΔAUC (style contribution = orig − neut) and semantic residual (neut AUC − 0.5):

| encoder | AUC orig | AUC neut | Δ style | semantic residual (neut−0.5) |
|---------|---------:|---------:|--------:|-----------------------------:|
| minilm | 0.8788 | 0.8536 | +0.0252 | +0.3536 |
| mpnet | 0.8464 | 0.8100 | +0.0364 | +0.3100 |
| e5 | 0.9469 | 0.9374 | +0.0095 | +0.4374 |
| bge | 0.9094 | 0.8856 | +0.0238 | +0.3856 |

## Decoy FP (stress; non-main-metric) at the FPR-anchor operating points

| encoder | arm | decoy FP @0% | @1% | @5% |
|---------|-----|------------:|----:|----:|
| minilm | orig | 0.0000 | 0.0000 | 0.0000 |
| minilm | neut | 0.0000 | 0.0000 | 0.0000 |
| mpnet | orig | 0.0000 | 0.0000 | 0.0000 |
| mpnet | neut | 0.0000 | 0.0000 | 0.0000 |
| e5 | orig | 0.0000 | 0.0000 | 0.0000 |
| e5 | neut | 0.0000 | 0.0000 | 0.0000 |
| bge | orig | 0.0000 | 0.0000 | 0.0270 |
| bge | neut | 0.0000 | 0.0000 | 0.0270 |

## Paired delta (Conclusion A retest): atomic_original vs bundle, own corpus anchor

| encoder | delta>0 | delta<0 | mean | min | max |
|---------|--------:|--------:|-----:|----:|----:|
| minilm | 71/90 | 19/90 | +0.1216 | -0.1743 | +0.7072 |
| mpnet | 65/90 | 25/90 | +0.1044 | -0.1746 | +0.6112 |
| e5 | 72/90 | 18/90 | +0.0279 | -0.0426 | +0.1193 |
| bge | 60/90 | 30/90 | +0.0272 | -0.1557 | +0.2881 |

## Pre-registration reconciliation

### (a) Boundary-hard is a mechanism-class property, not a MiniLM quirk

- TPR@FPR=0% (orig arm), per encoder: minilm=0.256, mpnet=0.133, e5=0.256, bge=0.156
- all below 0.5: **True**
- A/B median gap (B−A), per encoder: minilm=+0.0722, mpnet=+0.0438, e5=+0.0072, bge=+0.0257
- A/B gap same sign across encoders: **True**
- **VERDICT: HELD.** If both true, the hard boundary + type-dependent misalignment is a property of the embedding-NN mechanism class, not a MiniLM artifact.

### (b) Style vs content decomposition per encoder; residual ranking = encoder leverage

| encoder | style Δ | semantic residual |
|---------|--------:|------------------:|
| minilm | +0.0252 | +0.3536 |
| mpnet | +0.0364 | +0.3100 |
| e5 | +0.0095 | +0.4374 |
| bge | +0.0238 | +0.3856 |

- ΔAUC>0 for all encoders: **True**
- **Residual-semantic ranking (encoder leverage, best first): e5 > bge > minilm > mpnet**

### (c) Dilution effect (paired delta) holds across encoders

- delta>0 count per encoder: minilm=71/90, mpnet=65/90, e5=72/90, bge=60/90
- all encoders majority-positive: **True**
- **VERDICT: HELD.** Conclusion A (atomic compression raises anchor cosine) reproduces across encoders.

## Sample transforms (10; reused from D1.1)

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
