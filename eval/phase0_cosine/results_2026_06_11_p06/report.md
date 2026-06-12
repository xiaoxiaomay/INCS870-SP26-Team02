# Phase 0.6 — Dilution-Effect Diagnostic (atomic-variant incremental cosine)

DIAGNOSTIC MEASUREMENT ONLY. No thresholding, no pass/fail, no data-quality gate. This run characterizes how the anchor cosine reading changes when an offset is compressed from bundle form to a single-parameter atomic sentence. All interpretation is done in chat, not by this script.

## Run environment

- Model (from config.yaml `embedding.model_name`): `sentence-transformers/all-MiniLM-L6-v2`
- sentence-transformers version: `5.2.2`
- Python: `3.12.2` (/opt/anaconda3/bin/python)
- Platform: `macOS-14.5-arm64-arm-64bit`
- Run date (label dir): `2026_06_11_p06` (date.today()=2026-06-11)
- Pairs: 20 (15 bundle + 5 atomic)
- cosine = dot product of L2-normalized embeddings (`normalize_embeddings=True`).
- delta = atomic_cosine - bundle_cosine (positive => compression RAISED similarity).
- anchor_rank computed against the 15 distinct mother (bundle) anchors; atomic variants share their mother anchor verbatim and are ranked in the same 15-anchor pool.

## (1) Atomic vs bundle paired comparison (5 groups)

| id | domain | bundle cosine | atomic cosine | delta (atomic-bundle) | atomic anchor_rank |
|----|--------|--------------:|--------------:|----------------------:|:------------------:|
| p0_01 -> p0_01a | technical_indicator | 0.4933 | 0.9155 | +0.4222 | 1 |
| p0_02 -> p0_02a | factor_model | 0.6550 | 0.7331 | +0.0781 | 1 |
| p0_10 -> p0_10a | liquidity_management | 0.7235 | 0.8054 | +0.0819 | 1 |
| p0_12 -> p0_12a | market_making | 0.2284 | 0.8044 | +0.5760 | 1 |
| p0_14 -> p0_14a | portfolio_insurance | 0.2189 | 0.9261 | +0.7072 | 1 |

## (2) Direction counts and delta distribution

- groups with delta > 0 (atomic raised cosine): 5 / 5
- groups with delta < 0 (atomic lowered cosine): 0 / 5
- groups with delta == 0: 0 / 5
- delta mean: +0.3731
- delta min:  +0.0781
- delta max:  +0.7072

## (3) Atomic cross-pair anchor_rank (vs 15 mother anchors)

| atomic id | domain | atomic cosine | anchor_rank | nearest_anchor_id | nearest_anchor_cosine |
|-----------|--------|--------------:|:-----------:|-------------------|----------------------:|
| p0_01a | technical_indicator | 0.9155 | 1 | p0_01 | 0.9155 |
| p0_02a | factor_model | 0.7331 | 1 | p0_02 | 0.7331 |
| p0_10a | liquidity_management | 0.8054 | 1 | p0_10 | 0.8054 |
| p0_12a | market_making | 0.8044 | 1 | p0_12 | 0.8044 |
| p0_14a | portfolio_insurance | 0.9261 | 1 | p0_14 | 0.9261 |

All 5 atomic variants have their own mother anchor as nearest (anchor_rank == 1).

## (Appendix) Full-set descriptive context (all 20 rows)

- overall (n=20): n=20 | mean=0.5530 | median=0.5450 | p25=0.3823 | p75=0.7259 | min=0.2189 | max=0.9261
- bundle (n=15): n=15 | mean=0.4584 | median=0.4283 | p25=0.3502 | p75=0.5807 | min=0.2189 | max=0.7235
- atomic (n=5): n=5 | mean=0.8369 | median=0.8054 | p25=0.8044 | p75=0.9155 | min=0.7331 | max=0.9261
- Type A (n=17): n=17 | mean=0.5813 | median=0.5870 | p25=0.4235 | p75=0.7331 | min=0.2189 | max=0.9261
- Type B (n=3): n=3 | mean=0.3929 | median=0.3617 | p25=0.3315 | p75=0.4387 | min=0.3012 | max=0.5157
