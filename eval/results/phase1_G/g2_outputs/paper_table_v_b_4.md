# Phase 1.G G2 Statistical Aggregates (n=5 per cell)

Generated: 2026-05-26T00:46:16.734612Z | Alpha: 0.05 | Cells complete: 8/8 | Multiplicity: Holm-Bonferroni step-down (k=4)

## §V.B.4.1 — Per-cell aggregate metrics

| # | Cell | $\bar{\text{Bypass}}$ ± CI | $\bar{\text{GLR}}$ ± CI | $\bar{\text{Per-BP-Leak}}$ ± CI | $\bar{\text{ULR}}$ ± CI | n |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | MiniLM × 60 | 0.4760 ± 0.0000 | 0.0199 ± 0.0089 | 0.0419 ± 0.0188 | 0.0000 ± 0.0000 | 5 |
| 2 | MiniLM × 90 | 0.4280 ± 0.0000 | 0.0339 ± 0.0082 | 0.0793 ± 0.0191 | 0.0000 ± 0.0000 | 5 |
| 3 | mpnet × 60 | 0.3690 ± 0.0000 | 0.0561 ± 0.0109 | 0.1520 ± 0.0296 | 0.0000 ± 0.0000 | 5 |
| 4 | mpnet × 90 | 0.4945 ± 0.0000 | 0.0502 ± 0.0052 | 0.1015 ± 0.0106 | 0.0000 ± 0.0000 | 5 |
| 5 | bge-large × 60 | 0.3653 ± 0.0000 | 0.1011 ± 0.0151 | 0.2768 ± 0.0412 | 0.0007 ± 0.0021 | 5 |
| 6 | bge-large × 90 | 0.5498 ± 0.0000 | 0.1188 ± 0.0104 | 0.2161 ± 0.0190 | 0.0000 ± 0.0000 | 5 |
| 7 | FinLang × 60 | 0.5424 ± 0.0000 | 0.0354 ± 0.0083 | 0.0653 ± 0.0153 | 0.0000 ± 0.0000 | 5 |
| 8 | FinLang × 90 | 0.5387 ± 0.0000 | 0.0885 ± 0.0197 | 0.1644 ± 0.0366 | 0.0000 ± 0.0000 | 5 |

## §V.B.4.2 — Within-encoder corpus delta paired t-tests

**Primary tests** (4 × GLR-rate, Holm-Bonferroni step-down adjusted):

| Test | Mean delta (60 − 90) | t-stat | p (unadj.) | Holm rank | Holm threshold | Significant @ α=0.05 |
| --- | --- | --- | --- | --- | --- | --- |
| minilm × 60 vs × 90 (GLR) | -0.0140 | -2.543 | 0.0638 | 3 | 0.0250 | No |
| mpnet × 60 vs × 90 (GLR) | +0.0059 | 1.322 | 0.2566 | 4 | 0.0500 | No |
| bge_large × 60 vs × 90 (GLR) | -0.0177 | -2.953 | 0.0419 | 2 | 0.0167 | No |
| finlang × 60 vs × 90 (GLR) | -0.0531 | -8.363 | 0.0011 | 1 | 0.0125 | Yes |

**Secondary tests** (Bypass + Per-BP-Leak; descriptive only, unadjusted p-values reported):

| Test | Metric | Mean delta | t-stat | p (unadj.) |
| --- | --- | --- | --- | --- |
| minilm × 60 vs × 90 | bypass_rate | +0.0480 | ±inf* | 0.0000 |  (deterministic gap; t/p degenerate)
| minilm × 60 vs × 90 | per_bp_leak_rate | -0.0374 | -3.064 | 0.0375 |
| mpnet × 60 vs × 90 | bypass_rate | -0.1255 | ±inf* | 0.0000 |  (deterministic gap; t/p degenerate)
| mpnet × 60 vs × 90 | per_bp_leak_rate | +0.0505 | 4.380 | 0.0119 |
| bge_large × 60 vs × 90 | bypass_rate | -0.1845 | ±inf* | 0.0000 |  (deterministic gap; t/p degenerate)
| bge_large × 60 vs × 90 | per_bp_leak_rate | +0.0607 | 4.006 | 0.0160 |
| finlang × 60 vs × 90 | bypass_rate | +0.0037 | ±inf* | 0.0000 |  (deterministic gap; t/p degenerate)
| finlang × 60 vs × 90 | per_bp_leak_rate | -0.0991 | -8.407 | 0.0011 |

## §V.B.4.3 — Cross-encoder ordering robustness (F2 verification)

Prediction F2: per-sample encoder ranking by Per-BP-Leak% should satisfy minilm = rank 1 and bge_large = rank 4 (lowest leak to highest).

### Corpus size 60

| Sample | minilm | FinLang | mpnet | bge-large | F2 holds? |
| --- | --- | --- | --- | --- | --- |
| sample_1 | r1 (0.0465) | r2 (0.0612) | r3 (0.1900) | r4 (0.2525) | Yes |
| sample_2 | r1 (0.0465) | r2 (0.0680) | r3 (0.1400) | r4 (0.2727) | Yes |
| sample_3 | r1 (0.0543) | r2 (0.0816) | r3 (0.1300) | r4 (0.2525) | Yes |
| sample_4 | r1 (0.0155) | r2 (0.0680) | r3 (0.1600) | r4 (0.3333) | Yes |
| sample_5 | r1 (0.0465) | r2 (0.0476) | r3 (0.1400) | r4 (0.2727) | Yes |

**Aggregate verdict (corpus 60): F2 prediction holds in 5 of 5 samples.**

### Corpus size 90

| Sample | minilm | FinLang | mpnet | bge-large | F2 holds? |
| --- | --- | --- | --- | --- | --- |
| sample_1 | r1 (0.0603) | r3 (0.1164) | r2 (0.1045) | r4 (0.2081) | Yes |
| sample_2 | r1 (0.0776) | r3 (0.1918) | r2 (0.1045) | r4 (0.2148) | Yes |
| sample_3 | r1 (0.0690) | r3 (0.1781) | r2 (0.0970) | r4 (0.2013) | Yes |
| sample_4 | r2 (0.0948) | r3 (0.1781) | r1 (0.0896) | r4 (0.2148) | No |
| sample_5 | r1 (0.0948) | r3 (0.1575) | r2 (0.1119) | r4 (0.2416) | Yes |

**Aggregate verdict (corpus 90): F2 prediction holds in 4 of 5 samples.**
Exceptions: samples [4]

## §V.B.4.4 — S15 predictive claim verification

Prediction (S15): ULR fires are concentrated on bge-large cells (measurement-stage over-sensitivity at $\sigma_{\text{hard}}=0.70$).

| Cell | ULR fires (sum across n) | n samples |
| --- | --- | --- |
| MiniLM × 60 | 0 | 5 |
| MiniLM × 90 | 0 | 5 |
| mpnet × 60 | 0 | 5 |
| mpnet × 90 | 0 | 5 |
| bge-large × 60 | 1 | 5 |
| bge-large × 90 | 0 | 5 |
| FinLang × 60 | 0 | 5 |
| FinLang × 90 | 0 | 5 |

**bge-large total ULR fires:** 1 | **non-bge-large total:** 0 | **Claim holds:** Yes

Evidence: bge-large total ULR fires: 1; non-bge-large total: 0
