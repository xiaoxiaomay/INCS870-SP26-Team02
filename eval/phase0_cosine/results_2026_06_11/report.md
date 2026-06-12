# Phase 0.5 — Offline Cosine Measurement (anchor/offset minimal pairs)

MEASUREMENT ONLY. No thresholding, no pass/fail. Gate (a) re-calibration judgment is performed in chat, not by this script.

## Run environment

- Model (from config.yaml `embedding.model_name`): `sentence-transformers/all-MiniLM-L6-v2`
- sentence-transformers version: `5.2.2`
- Python: `3.12.2` (/opt/anaconda3/bin/python)
- Platform: `macOS-14.5-arm64-arm-64bit`
- Run date (label dir): `2026_06_11` (date.today()=2026-06-11)
- Pairs: 15
- cosine = dot product of L2-normalized embeddings (`normalize_embeddings=True`).

## (1) Per-pair cosine (descending)

| rank | id | domain | type | subset | cosine | anchor_rank |
|-----:|----|--------|:----:|--------|-------:|:-----------:|
| 1 | p0_10 | liquidity_management | A | core | 0.7235 | 1 |
| 2 | p0_02 | factor_model | A | core | 0.6550 | 1 |
| 3 | p0_03 | regulatory_concentration | A | core | 0.6367 | 1 |
| 4 | p0_05 | position_sizing | A | boundary_test | 0.5870 | 1 |
| 5 | p0_07 | execution_vwap | A | core | 0.5743 | 1 |
| 6 | p0_11 | prime_brokerage_margin | B | core | 0.5157 | 1 |
| 7 | p0_01 | technical_indicator | A | core | 0.4933 | 1 |
| 8 | p0_06 | risk_model | A | core | 0.4283 | 1 |
| 9 | p0_13 | stat_arb | A | core | 0.4235 | 1 |
| 10 | p0_15 | credit_screening | A | core | 0.3891 | 1 |
| 11 | p0_08 | settlement_ops | B | core | 0.3617 | 2 |
| 12 | p0_09 | portfolio_construction | A | core | 0.3387 | 2 |
| 13 | p0_04 | exchange_rule_execution | B | core | 0.3012 | 1 |
| 14 | p0_12 | market_making | A | core | 0.2284 | 2 |
| 15 | p0_14 | portfolio_insurance | A | boundary_test | 0.2189 | 7 |

## (2) Overall distribution

- n=15 | mean=0.4584 | median=0.4283 | p25=0.3502 | p75=0.5807 | min=0.2189 | max=0.7235

## (3) Group distributions (descriptive only; groups small, no significance tests)

### Type A vs Type B

- Type A: n=12 | mean=0.4747 | median=0.4608 | p25=0.3765 | p75=0.5994 | min=0.2189 | max=0.7235
- Type B: n=3 | mean=0.3929 | median=0.3617 | p25=0.3315 | p75=0.4387 | min=0.3012 | max=0.5157

### core vs boundary_test

- core:          n=13 | mean=0.4669 | median=0.4283 | p25=0.3617 | p75=0.5743 | min=0.2284 | max=0.7235
- boundary_test: n=2 | mean=0.4029 | median=0.4029 | p25=0.3109 | p75=0.4950 | min=0.2189 | max=0.5870

## (4) Cross-pair check: pairs where own anchor is NOT nearest (anchor_rank != 1)

| id | domain | own cosine | anchor_rank | nearest_anchor_id | nearest_anchor_cosine |
|----|--------|-----------:|:-----------:|-------------------|----------------------:|
| p0_08 | settlement_ops | 0.3617 | 2 | p0_11 | 0.3805 |
| p0_09 | portfolio_construction | 0.3387 | 2 | p0_14 | 0.3814 |
| p0_12 | market_making | 0.2284 | 2 | p0_04 | 0.2617 |
| p0_14 | portfolio_insurance | 0.2189 | 7 | p0_07 | 0.3515 |
