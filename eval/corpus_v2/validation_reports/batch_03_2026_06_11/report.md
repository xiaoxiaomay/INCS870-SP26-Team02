# corpus_v2 — Validation Report (checks 1-5)

MEASUREMENT ONLY. Every check emits measurements + a manual-review list; no automatic pass/fail. Reference/quota lines are advisory.

## Header

- Encoder: `sentence-transformers/all-MiniLM-L6-v2` (sentence-transformers `5.2.2`)
- Python: `3.12.2`  |  Platform: `macOS-14.5-arm64-arm-64bit`
- Run date: `2026-06-11`
- cosine = dot product of L2-normalized embeddings (`normalize_embeddings=True`).
- Corpus files:
    - `eval/corpus_v2/corpus_batch_seed.jsonl` — 15 rows
    - `eval/corpus_v2/corpus_batch_01.jsonl` — 15 rows
    - `eval/corpus_v2/corpus_batch_02.jsonl` — 15 rows
    - `eval/corpus_v2/corpus_batch_03.jsonl` — 15 rows
- Hard-negatives: `eval/corpus_v2/hard_negatives_v2.jsonl` — 97 rows (60 anchor + 37 decoy)
- **Quota base = 60 cumulative secrets** (cumulative tally: Type B 13/60, policy_quota 5/60, boundary_test 5/60).

## Check 1 — Quota & coverage

Reference (advisory): Type B ~20% | boundary_test ~10% | policy_quota tag <=20% | no single marker_style >50%.

**domain**

| value | count | share |
|-------|------:|------:|
| technical_indicator | 4 | 0.067 |
| factor_model | 4 | 0.067 |
| position_sizing | 4 | 0.067 |
| risk_model | 4 | 0.067 |
| settlement_ops | 4 | 0.067 |
| portfolio_construction | 4 | 0.067 |
| liquidity_management | 4 | 0.067 |
| prime_brokerage_margin | 4 | 0.067 |
| market_making | 4 | 0.067 |
| stat_arb | 4 | 0.067 |
| portfolio_insurance | 4 | 0.067 |
| credit_screening | 4 | 0.067 |
| regulatory_concentration | 3 | 0.050 |
| exchange_rule_execution | 3 | 0.050 |
| execution_vwap | 3 | 0.050 |
| execution_scheduling | 3 | 0.050 |

**offset_type**

| value | count | share |
|-------|------:|------:|
| A | 47 | 0.783 |
| B | 13 | 0.217 |

**subset**

| value | count | share |
|-------|------:|------:|
| core | 55 | 0.917 |
| boundary_test | 5 | 0.083 |

**marker_style**

| value | count | share |
|-------|------:|------:|
| none | 23 | 0.383 |
| internal | 10 | 0.167 |
| desk | 9 | 0.150 |
| production | 6 | 0.100 |
| our | 5 | 0.083 |
| ops | 4 | 0.067 |
| firm | 3 | 0.050 |

- Type B: 13/60 (0.217)
- boundary_test: 5/60 (0.083)
- policy_quota tag: 5/60 (0.083)
- marker_style top: 'none' (0.383)

_Manual-review items (Check 1):_
- Type B share 13/60=0.217 vs ref ~0.20
- boundary_test share 5/60=0.083 vs ref ~0.10

## Check 2 — Surface-form / shortcut audit

### (b1) regex n-gram shortcut candidates

n-grams (n=2..5, lowercased, punctuation-stripped) in >=3 secrets AND appearing in <10% of the 55 hard-negatives. Descending by secret doc count.

| n-gram | secret docs | hn occ | hn rate |
|--------|------------:|-------:|--------:|
| `capped at` | 7 | 2 | 0.021 |
| `at 1` | 6 | 0 | 0.000 |
| `of nav` | 6 | 2 | 0.021 |
| `with a` | 6 | 4 | 0.041 |
| `2 of` | 5 | 1 | 0.010 |
| `at 0` | 5 | 1 | 0.010 |
| `1 5x` | 4 | 0 | 0.000 |
| `10 day` | 4 | 1 | 0.010 |
| `30 minutes` | 4 | 0 | 0.000 |
| `5 day` | 4 | 0 | 0.000 |
| `at the` | 4 | 7 | 0.072 |
| `held under` | 4 | 0 | 0.000 |
| `of adv` | 4 | 1 | 0.010 |
| `on a` | 4 | 2 | 0.021 |
| `only when` | 4 | 0 | 0.000 |
| `realized vol` | 4 | 0 | 0.000 |
| `versus the` | 4 | 0 | 0.000 |
| `60 40 with` | 3 | 0 | 0.000 |
| `exposure capped at` | 3 | 0 | 0.000 |
| `0 5` | 3 | 2 | 0.021 |
| `0 6` | 3 | 1 | 0.010 |
| `1 4` | 3 | 1 | 0.010 |
| `1 8x` | 3 | 0 | 0.000 |
| `10 sessions` | 3 | 0 | 0.000 |
| `2 5x` | 3 | 0 | 0.000 |
| `20 day` | 3 | 3 | 0.031 |
| `3 2` | 3 | 0 | 0.000 |
| `3 5` | 3 | 4 | 0.041 |
| `40 with` | 3 | 0 | 0.000 |
| `60 40` | 3 | 0 | 0.000 |
| `add on` | 3 | 0 | 0.000 |
| `at 2` | 3 | 0 | 0.000 |
| `at 28` | 3 | 0 | 0.000 |
| `bps of` | 3 | 0 | 0.000 |
| `desk rule` | 3 | 0 | 0.000 |
| `exit at` | 3 | 1 | 0.010 |
| `exposure capped` | 3 | 0 | 0.000 |
| `falls below` | 3 | 0 | 0.000 |
| `half life` | 3 | 2 | 0.021 |
| `is under` | 3 | 0 | 0.000 |
| `of book` | 3 | 0 | 0.000 |
| `of fund` | 3 | 0 | 0.000 |
| `one third` | 3 | 0 | 0.000 |
| `rather than` | 3 | 0 | 0.000 |
| `within 3` | 3 | 0 | 0.000 |

### (b2) marker / heuristic separability

predicate -> predicts 'secret'. positives = secrets, negatives = hard-negs. FP broken down by hard-neg kind (anchor / decoy), NOT merged. Alarm line (annotate only): recall>0.9 AND precision>0.9.

| heuristic | precision | recall | TP | FP | FN | FP_anchor (rate) | FP_decoy (rate) | ALARM |
|-----------|----------:|-------:|---:|---:|---:|-----------------|----------------|:-----:|
| vocab:our | 0.556 | 0.083 | 5 | 4 | 55 | 0 (0.000) | 4 (0.108) |  |
| vocab:internal | 0.733 | 0.183 | 11 | 4 | 49 | 1 (0.017) | 3 (0.081) |  |
| vocab:desk | 0.789 | 0.250 | 15 | 4 | 45 | 0 (0.000) | 4 (0.108) |  |
| vocab:proprietary | 0.000 | 0.000 | 0 | 1 | 60 | 0 (0.000) | 1 (0.027) |  |
| vocab:production | 0.800 | 0.067 | 4 | 1 | 56 | 0 (0.000) | 1 (0.027) |  |
| vocab:firm | 0.500 | 0.017 | 1 | 1 | 59 | 0 (0.000) | 1 (0.027) |  |
| vocab:ops | 1.000 | 0.067 | 4 | 0 | 56 | 0 (0.000) | 0 (0.000) |  |
| vocab:ANY | 0.766 | 0.600 | 36 | 11 | 24 | 1 (0.017) | 10 (0.270) |  |
| struct:num>=1 | 0.435 | 1.000 | 60 | 78 | 0 | 48 (0.800) | 30 (0.811) |  |
| struct:num>=3 | 0.561 | 1.000 | 60 | 47 | 0 | 25 (0.417) | 22 (0.595) |  |
| struct:semicolon>=2 | 0.838 | 0.950 | 57 | 11 | 3 | 0 (0.000) | 11 (0.297) |  |

### (b3) numeric-token density

numeric token = whitespace-separated token containing >=1 digit.

- **secret**: n=60 mean=5.1000 median=5.0000 p25=4.0000 p75=6.0000 min=3.0000 max=9.0000
    - histogram (count -> #items): {'3': 8, '4': 13, '5': 16, '6': 14, '7': 7, '8': 1, '9': 1}
- **anchor**: n=60 mean=2.0000 median=2.0000 p25=1.0000 p75=3.0000 min=0.0000 max=5.0000
    - histogram (count -> #items): {'0': 12, '1': 9, '2': 14, '3': 18, '4': 6, '5': 1}
- **decoy**: n=37 mean=3.4595 median=3.0000 p25=1.0000 p75=5.0000 min=0.0000 max=10.0000
    - histogram (count -> #items): {'0': 7, '1': 4, '2': 4, '3': 4, '4': 1, '5': 9, '6': 4, '7': 3, '10': 1}
- decoy-pool numeric-token mean = 3.4595 vs 3.5 stop-line (delta -0.0405) — reported only, not judged.

_Manual-review items (Check 2):_
- 45 n-gram shortcut candidate(s) (b1) — inspect for regex-anchorability.
- (b3) inspect whether secret vs hard-neg numeric-count distributions are near-disjoint (would make 'count the numbers' itself a shortcut).

## Check 3 — Embedding hygiene

### secret vs own anchor_text cosine

- overall: n=60 mean=0.4734 median=0.4850 p25=0.4004 p75=0.5461 min=0.2189 max=0.7235
- offset_type A: n=47 mean=0.4712 median=0.4790 p25=0.3994 p75=0.5510 min=0.2189 max=0.7235
- offset_type B: n=13 mean=0.4812 median=0.4980 p25=0.4151 p75=0.5288 min=0.3012 max=0.6230

by domain:

| domain | stats |
|--------|-------|
| credit_screening | n=4 mean=0.4571 median=0.4751 p25=0.4434 p75=0.4888 min=0.3891 max=0.4889 |
| exchange_rule_execution | n=3 mean=0.4114 median=0.4151 p25=0.3582 p75=0.4665 min=0.3012 max=0.5178 |
| execution_scheduling | n=3 mean=0.4467 median=0.4679 p25=0.4359 p75=0.4682 min=0.4038 max=0.4685 |
| execution_vwap | n=3 mean=0.4856 median=0.5743 p25=0.4208 p75=0.5949 min=0.2672 max=0.6154 |
| factor_model | n=4 mean=0.4895 median=0.4705 p25=0.4193 p75=0.5408 min=0.3622 max=0.6550 |
| liquidity_management | n=4 mean=0.5215 median=0.4930 p25=0.4170 p75=0.5975 min=0.3768 max=0.7235 |
| market_making | n=4 mean=0.4221 median=0.4189 p25=0.3641 p75=0.4768 min=0.2284 max=0.6221 |
| portfolio_construction | n=4 mean=0.4718 median=0.4942 p25=0.4512 p75=0.5148 min=0.3387 max=0.5601 |
| portfolio_insurance | n=4 mean=0.3930 median=0.3853 p25=0.3316 p75=0.4466 min=0.2189 max=0.5824 |
| position_sizing | n=4 mean=0.6085 median=0.6254 p25=0.5654 p75=0.6685 min=0.5005 max=0.6828 |
| prime_brokerage_margin | n=4 mean=0.5179 median=0.5222 p25=0.5071 p75=0.5331 min=0.4813 max=0.5460 |
| regulatory_concentration | n=3 mean=0.5779 median=0.5758 p25=0.5485 p75=0.6063 min=0.5213 max=0.6367 |
| risk_model | n=4 mean=0.4277 median=0.4537 p25=0.3898 p75=0.4915 min=0.2743 max=0.5292 |
| settlement_ops | n=4 mean=0.4666 median=0.4408 p25=0.3782 p75=0.5293 min=0.3617 max=0.6230 |
| stat_arb | n=4 mean=0.3788 median=0.3821 p25=0.3570 p75=0.4039 min=0.3274 max=0.4235 |
| technical_indicator | n=4 mean=0.5045 median=0.5062 p25=0.4848 p75=0.5260 min=0.4592 max=0.5466 |

### cross-pair rank violations (secret's own anchor NOT nearest among 30)

| id | own cosine | anchor_rank | nearest_anchor_id | nearest cosine |
|----|-----------:|:-----------:|-------------------|---------------:|
| p0_04 | 0.3012 | 5 | b1_19 | 0.4490 |
| p0_08 | 0.3617 | 6 | b2_40 | 0.4800 |
| p0_09 | 0.3387 | 3 | p0_14 | 0.3814 |
| p0_12 | 0.2284 | 13 | b2_41 | 0.3251 |
| p0_14 | 0.2189 | 24 | p0_07 | 0.3515 |
| p0_15 | 0.3891 | 2 | b2_35 | 0.4040 |
| b1_16 | 0.4592 | 2 | b2_41 | 0.5283 |
| b1_18 | 0.2743 | 8 | b3_57 | 0.3139 |
| b1_20 | 0.3837 | 4 | p0_11 | 0.4362 |
| b1_23 | 0.3669 | 2 | b3_51 | 0.3717 |
| b1_24 | 0.4997 | 2 | b1_28 | 0.5332 |
| b2_37 | 0.3274 | 7 | p0_01 | 0.3806 |
| b2_39 | 0.3768 | 2 | b2_40 | 0.4348 |
| b2_43 | 0.4014 | 2 | b3_56 | 0.4120 |
| b2_44 | 0.2672 | 10 | b2_41 | 0.3820 |
| b3_50 | 0.3622 | 2 | b1_17 | 0.3655 |
| b3_53 | 0.3974 | 4 | b2_40 | 0.4305 |
| b3_60 | 0.4813 | 3 | b2_39 | 0.5013 |

### anchor-anchor crosstalk (cosine > 0.8)

_No anchor pair exceeds 0.8._

### atomic paired delta

gate (a), offset_type-scoped: Type A — atomic should rank==1 AND be higher than its bundle (delta>0); violation = rank!=1 OR delta<=0. Type B — anchor-mirroring is NOT expected by design; only an identity-preservation attribution check applies: violation = rank>3. For Type B, delta is still reported but is NOT a criterion. Violations are flagged for manual review; magnitude judgment is left to the human.

- delta>0: 48/60 | delta<0: 12 | delta==0: 0
- delta mean +0.1260 | min -0.1743 | max +0.7072

_Type B: anchor-mirroring not expected by design; rank<=3 attribution check only (delta shown but not a criterion)._

| id | type | bundle cos | atomic cos | delta | atomic rank | criterion | violation |
|----|:----:|-----------:|-----------:|------:|:-----------:|-----------|:---------:|
| p0_01 | A | 0.4933 | 0.9155 | +0.4222 | 1 | Type A: rank==1 & delta>0 |  |
| p0_02 | A | 0.6550 | 0.7331 | +0.0781 | 1 | Type A: rank==1 & delta>0 |  |
| p0_03 | A | 0.6367 | 0.6450 | +0.0083 | 1 | Type A: rank==1 & delta>0 |  |
| p0_04 | B | 0.3012 | 0.2925 | -0.0088 | 1 | Type B: rank<=3 attribution check only |  |
| p0_05 | A | 0.5870 | 0.6066 | +0.0196 | 1 | Type A: rank==1 & delta>0 |  |
| p0_06 | A | 0.4283 | 0.8531 | +0.4247 | 1 | Type A: rank==1 & delta>0 |  |
| p0_07 | A | 0.5743 | 0.6777 | +0.1033 | 1 | Type A: rank==1 & delta>0 |  |
| p0_08 | B | 0.3617 | 0.3327 | -0.0290 | 2 | Type B: rank<=3 attribution check only |  |
| p0_09 | A | 0.3387 | 0.6692 | +0.3305 | 1 | Type A: rank==1 & delta>0 |  |
| p0_10 | A | 0.7235 | 0.8054 | +0.0819 | 1 | Type A: rank==1 & delta>0 |  |
| p0_11 | B | 0.5157 | 0.5706 | +0.0549 | 1 | Type B: rank<=3 attribution check only |  |
| p0_12 | A | 0.2284 | 0.8044 | +0.5760 | 1 | Type A: rank==1 & delta>0 |  |
| p0_13 | A | 0.4235 | 0.6950 | +0.2715 | 1 | Type A: rank==1 & delta>0 |  |
| p0_14 | A | 0.2189 | 0.9261 | +0.7072 | 1 | Type A: rank==1 & delta>0 |  |
| p0_15 | A | 0.3891 | 0.3930 | +0.0039 | 1 | Type A: rank==1 & delta>0 |  |
| b1_16 | A | 0.4592 | 0.8680 | +0.4088 | 1 | Type A: rank==1 & delta>0 |  |
| b1_17 | A | 0.5027 | 0.5314 | +0.0287 | 1 | Type A: rank==1 & delta>0 |  |
| b1_18 | A | 0.2743 | 0.4730 | +0.1988 | 1 | Type A: rank==1 & delta>0 |  |
| b1_19 | A | 0.4685 | 0.4263 | -0.0421 | 1 | Type A: rank==1 & delta>0 | YES |
| b1_20 | B | 0.3837 | 0.3298 | -0.0538 | 2 | Type B: rank<=3 attribution check only |  |
| b1_21 | B | 0.5288 | 0.6581 | +0.1293 | 1 | Type B: rank<=3 attribution check only |  |
| b1_22 | A | 0.4284 | 0.4297 | +0.0012 | 1 | Type A: rank==1 & delta>0 |  |
| b1_23 | A | 0.3669 | 0.5268 | +0.1599 | 1 | Type A: rank==1 & delta>0 |  |
| b1_24 | A | 0.4997 | 0.6411 | +0.1414 | 1 | Type A: rank==1 & delta>0 |  |
| b1_25 | A | 0.4305 | 0.8281 | +0.3976 | 1 | Type A: rank==1 & delta>0 |  |
| b1_26 | A | 0.4889 | 0.7061 | +0.2172 | 1 | Type A: rank==1 & delta>0 |  |
| b1_27 | B | 0.4151 | 0.3117 | -0.1034 | 2 | Type B: rank<=3 attribution check only |  |
| b1_28 | A | 0.6638 | 0.7064 | +0.0426 | 1 | Type A: rank==1 & delta>0 |  |
| b1_29 | A | 0.5824 | 0.9260 | +0.3437 | 1 | Type A: rank==1 & delta>0 |  |
| b1_30 | A | 0.4383 | 0.6544 | +0.2161 | 1 | Type A: rank==1 & delta>0 |  |
| b2_31 | B | 0.4980 | 0.4750 | -0.0230 | 1 | Type B: rank<=3 attribution check only |  |
| b2_32 | B | 0.5178 | 0.4575 | -0.0603 | 1 | Type B: rank<=3 attribution check only |  |
| b2_33 | B | 0.6221 | 0.5660 | -0.0560 | 1 | Type B: rank<=3 attribution check only |  |
| b2_34 | A | 0.5758 | 0.5462 | -0.0296 | 1 | Type A: rank==1 & delta>0 | YES |
| b2_35 | A | 0.5292 | 0.4340 | -0.0952 | 2 | Type A: rank==1 & delta>0 | YES |
| b2_36 | B | 0.4615 | 0.3339 | -0.1276 | 5 | Type B: rank<=3 attribution check only | YES |
| b2_37 | A | 0.3274 | 0.5459 | +0.2186 | 1 | Type A: rank==1 & delta>0 |  |
| b2_38 | A | 0.5601 | 0.5736 | +0.0134 | 1 | Type A: rank==1 & delta>0 |  |
| b2_39 | A | 0.3768 | 0.5439 | +0.1671 | 1 | Type A: rank==1 & delta>0 |  |
| b2_40 | B | 0.5460 | 0.5769 | +0.0309 | 1 | Type B: rank<=3 attribution check only |  |
| b2_41 | A | 0.5466 | 0.8985 | +0.3519 | 1 | Type A: rank==1 & delta>0 |  |
| b2_42 | A | 0.5005 | 0.6763 | +0.1758 | 1 | Type A: rank==1 & delta>0 |  |
| b2_43 | A | 0.4014 | 0.6160 | +0.2146 | 1 | Type A: rank==1 & delta>0 |  |
| b2_44 | A | 0.2672 | 0.3822 | +0.1150 | 1 | Type A: rank==1 & delta>0 |  |
| b2_45 | A | 0.4038 | 0.4819 | +0.0781 | 1 | Type A: rank==1 & delta>0 |  |
| b3_46 | A | 0.5213 | 0.5419 | +0.0206 | 1 | Type A: rank==1 & delta>0 |  |
| b3_47 | A | 0.6154 | 0.7926 | +0.1772 | 1 | Type A: rank==1 & delta>0 |  |
| b3_48 | A | 0.4679 | 0.5437 | +0.0758 | 1 | Type A: rank==1 & delta>0 |  |
| b3_49 | A | 0.5191 | 0.8374 | +0.3183 | 1 | Type A: rank==1 & delta>0 |  |
| b3_50 | A | 0.3622 | 0.4743 | +0.1121 | 1 | Type A: rank==1 & delta>0 |  |
| b3_51 | A | 0.4790 | 0.6051 | +0.1261 | 1 | Type A: rank==1 & delta>0 |  |
| b3_52 | A | 0.4887 | 0.5803 | +0.0917 | 1 | Type A: rank==1 & delta>0 |  |
| b3_53 | A | 0.3974 | 0.4822 | +0.0848 | 1 | Type A: rank==1 & delta>0 |  |
| b3_54 | A | 0.4094 | 0.4578 | +0.0484 | 1 | Type A: rank==1 & delta>0 |  |
| b3_55 | A | 0.4887 | 0.6954 | +0.2066 | 1 | Type A: rank==1 & delta>0 |  |
| b3_56 | A | 0.3692 | 0.4735 | +0.1043 | 1 | Type A: rank==1 & delta>0 |  |
| b3_57 | A | 0.5555 | 0.7456 | +0.1901 | 1 | Type A: rank==1 & delta>0 |  |
| b3_58 | A | 0.6828 | 0.7045 | +0.0217 | 1 | Type A: rank==1 & delta>0 |  |
| b3_59 | B | 0.6230 | 0.4487 | -0.1743 | 1 | Type B: rank<=3 attribution check only |  |
| b3_60 | B | 0.4813 | 0.5357 | +0.0544 | 1 | Type B: rank<=3 attribution check only |  |

_Manual-review items (Check 3):_
- 18 secret(s) whose own anchor is not nearest.
- atomic gate(a) violations (offset_type-scoped): b1_19, b2_34, b2_35, b2_36.

## Check 4 — Overlap & near-dup

Exact string overlap (normalized: trim+lower+collapse-ws) + cosine > 0.95 near-dup.

### (i) new corpus (secret+anchor+decoy) vs legacy eval sets

- **secrets.jsonl** (60 rows): exact=0, near-dup(>0.95)=0
- **attack_271** (271 rows): exact=0, near-dup(>0.95)=0
- **normal_100** (100 rows): exact=0, near-dup(>0.95)=0
- **hard_neg_65** (65 rows): exact=0, near-dup(>0.95)=0

### (ii) decoy <-> anchor near-dup

- exact: 0 | near-dup(>0.95): 0

Pre-registered focus pairs (reported regardless of 0.95):

| decoy | anchor | cosine | >0.95 |
|-------|--------|-------:|:-----:|
| d3_04 | hn_p0_02 | 0.6669 | no |
| d3_02 | hn_p0_01 | 0.7256 | no |
| d3_06 | hn_p0_13 | 0.4304 | no |
| d2_02 | hn_p0_11 | 0.6144 | no |
| d1_05 | hn_p0_03 | 0.5836 | no |
| d2_10 | hn_b2_39 | 0.6824 | no |
| d3_08 | hn_p0_03 | 0.6408 | no |
| d3_09 | hn_b2_42 | 0.6811 | no |
| d2_16 | hn_b1_25 | 0.5844 | no |

### (iii) secret <-> secret exact duplicate

_None._

### (iv) decoy <-> decoy near-dup

- exact: 0 | near-dup(>0.95): 0

Pre-registered decoy<->decoy focus pairs (reported regardless of 0.95):

| decoy A | decoy B | cosine | >0.95 |
|---------|---------|-------:|:-----:|
| d2_15 | d2_13 | 0.7624 | no |

_Manual-review items (Check 4):_
- none.

## Check 5 — Secret-Secret Nearest Neighbor Audit

Motivation: template-collapse monitor. A rising cross-domain NN share batch-over-batch flags surface-template convergence. This batch = baseline.

- same-domain NN: 25/60 (0.417)
- cross-domain NN share: 0.583

**Template-collapse trend (this batch vs frozen prior batches):**

| metric | this batch | baseline batch_01 (frozen) | batch_02 |
|--------|-----------:|-----------:|-----------:|
| cross-domain NN share | 0.583 | 0.667 (Δ-0.084) | 0.622 (Δ-0.039) |
| top-1 secret-secret cosine | 0.6220 | 0.6028 (Δ+0.0192) | 0.6028 (Δ+0.0192) |

### (i) each secret's nearest-neighbour secret

| id | domain | NN id | NN domain | cosine | same-domain |
|----|--------|-------|-----------|-------:|:-----------:|
| p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 | yes |
| p0_02 | factor_model | b1_30 | factor_model | 0.4628 | yes |
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 | NO |
| p0_04 | exchange_rule_execution | b2_32 | exchange_rule_execution | 0.4641 | yes |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 | NO |
| p0_06 | risk_model | b1_18 | risk_model | 0.5334 | yes |
| p0_07 | execution_vwap | b3_47 | execution_vwap | 0.5220 | yes |
| p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 | NO |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 | NO |
| p0_10 | liquidity_management | p0_03 | regulatory_concentration | 0.5061 | NO |
| p0_11 | prime_brokerage_margin | b1_20 | settlement_ops | 0.4848 | NO |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 | NO |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 | NO |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 | NO |
| p0_15 | credit_screening | b2_36 | credit_screening | 0.4782 | yes |
| b1_16 | technical_indicator | p0_01 | technical_indicator | 0.6028 | yes |
| b1_17 | factor_model | b1_30 | factor_model | 0.5183 | yes |
| b1_18 | risk_model | p0_06 | risk_model | 0.5334 | yes |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 | NO |
| b1_20 | settlement_ops | b3_59 | settlement_ops | 0.5822 | yes |
| b1_21 | prime_brokerage_margin | b3_58 | position_sizing | 0.5467 | NO |
| b1_22 | market_making | b1_21 | prime_brokerage_margin | 0.4372 | NO |
| b1_23 | stat_arb | b1_19 | execution_scheduling | 0.4587 | NO |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 | NO |
| b1_25 | liquidity_management | b2_39 | liquidity_management | 0.5954 | yes |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 | NO |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 | NO |
| b1_28 | position_sizing | b3_48 | execution_scheduling | 0.5663 | NO |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 | NO |
| b1_30 | factor_model | b1_17 | factor_model | 0.5183 | yes |
| b2_31 | settlement_ops | b3_59 | settlement_ops | 0.4679 | yes |
| b2_32 | exchange_rule_execution | p0_04 | exchange_rule_execution | 0.4641 | yes |
| b2_33 | market_making | b1_22 | market_making | 0.4161 | yes |
| b2_34 | regulatory_concentration | b2_36 | credit_screening | 0.5176 | NO |
| b2_35 | risk_model | b3_58 | position_sizing | 0.5641 | NO |
| b2_36 | credit_screening | b2_34 | regulatory_concentration | 0.5176 | NO |
| b2_37 | stat_arb | b1_19 | execution_scheduling | 0.4998 | NO |
| b2_38 | portfolio_construction | b1_17 | factor_model | 0.4665 | NO |
| b2_39 | liquidity_management | b1_25 | liquidity_management | 0.5954 | yes |
| b2_40 | prime_brokerage_margin | p0_08 | settlement_ops | 0.5870 | NO |
| b2_41 | technical_indicator | b1_16 | technical_indicator | 0.4640 | yes |
| b2_42 | position_sizing | b1_28 | position_sizing | 0.4079 | yes |
| b2_43 | portfolio_insurance | b3_56 | portfolio_insurance | 0.6220 | yes |
| b2_44 | execution_vwap | b1_16 | technical_indicator | 0.5040 | NO |
| b2_45 | execution_scheduling | p0_11 | prime_brokerage_margin | 0.4316 | NO |
| b3_46 | regulatory_concentration | p0_03 | regulatory_concentration | 0.4755 | yes |
| b3_47 | execution_vwap | p0_07 | execution_vwap | 0.5220 | yes |
| b3_48 | execution_scheduling | b1_28 | position_sizing | 0.5663 | NO |
| b3_49 | technical_indicator | b2_37 | stat_arb | 0.4852 | NO |
| b3_50 | factor_model | b1_30 | factor_model | 0.4574 | yes |
| b3_51 | risk_model | p0_03 | regulatory_concentration | 0.4790 | NO |
| b3_52 | credit_screening | p0_15 | credit_screening | 0.4092 | yes |
| b3_53 | stat_arb | p0_08 | settlement_ops | 0.4577 | NO |
| b3_54 | market_making | p0_11 | prime_brokerage_margin | 0.4544 | NO |
| b3_55 | portfolio_construction | b1_30 | factor_model | 0.4418 | NO |
| b3_56 | portfolio_insurance | b2_43 | portfolio_insurance | 0.6220 | yes |
| b3_57 | liquidity_management | b1_21 | prime_brokerage_margin | 0.5024 | NO |
| b3_58 | position_sizing | b2_35 | risk_model | 0.5641 | NO |
| b3_59 | settlement_ops | b1_20 | settlement_ops | 0.5822 | yes |
| b3_60 | prime_brokerage_margin | b2_34 | regulatory_concentration | 0.4732 | NO |

### (ii) cross-domain NN pairs

| id | domain | NN id | NN domain | cosine |
|----|--------|-------|-----------|-------:|
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 |
| p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 |
| p0_10 | liquidity_management | p0_03 | regulatory_concentration | 0.5061 |
| p0_11 | prime_brokerage_margin | b1_20 | settlement_ops | 0.4848 |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 |
| b1_21 | prime_brokerage_margin | b3_58 | position_sizing | 0.5467 |
| b1_22 | market_making | b1_21 | prime_brokerage_margin | 0.4372 |
| b1_23 | stat_arb | b1_19 | execution_scheduling | 0.4587 |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 |
| b1_28 | position_sizing | b3_48 | execution_scheduling | 0.5663 |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 |
| b2_34 | regulatory_concentration | b2_36 | credit_screening | 0.5176 |
| b2_35 | risk_model | b3_58 | position_sizing | 0.5641 |
| b2_36 | credit_screening | b2_34 | regulatory_concentration | 0.5176 |
| b2_37 | stat_arb | b1_19 | execution_scheduling | 0.4998 |
| b2_38 | portfolio_construction | b1_17 | factor_model | 0.4665 |
| b2_40 | prime_brokerage_margin | p0_08 | settlement_ops | 0.5870 |
| b2_44 | execution_vwap | b1_16 | technical_indicator | 0.5040 |
| b2_45 | execution_scheduling | p0_11 | prime_brokerage_margin | 0.4316 |
| b3_48 | execution_scheduling | b1_28 | position_sizing | 0.5663 |
| b3_49 | technical_indicator | b2_37 | stat_arb | 0.4852 |
| b3_51 | risk_model | p0_03 | regulatory_concentration | 0.4790 |
| b3_53 | stat_arb | p0_08 | settlement_ops | 0.4577 |
| b3_54 | market_making | p0_11 | prime_brokerage_margin | 0.4544 |
| b3_55 | portfolio_construction | b1_30 | factor_model | 0.4418 |
| b3_57 | liquidity_management | b1_21 | prime_brokerage_margin | 0.5024 |
| b3_58 | position_sizing | b2_35 | risk_model | 0.5641 |
| b3_60 | prime_brokerage_margin | b2_34 | regulatory_concentration | 0.4732 |

### (iii) top-10 secret-secret cosine (any domain)

| rank | A | A domain | B | B domain | cosine |
|-----:|---|----------|---|----------|-------:|
| 1 | b2_43 | portfolio_insurance | b3_56 | portfolio_insurance | 0.6220 |
| 2 | p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 |
| 3 | b1_25 | liquidity_management | b2_39 | liquidity_management | 0.5954 |
| 4 | p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| 5 | p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 |
| 6 | b1_20 | settlement_ops | b3_59 | settlement_ops | 0.5822 |
| 7 | b1_28 | position_sizing | b3_48 | execution_scheduling | 0.5663 |
| 8 | b2_35 | risk_model | b3_58 | position_sizing | 0.5641 |
| 9 | p0_08 | settlement_ops | b1_20 | settlement_ops | 0.5604 |
| 10 | b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 |

_Manual-review items (Check 5):_
- baseline cross-domain NN share = 0.583; compare against batch 2+ for template-collapse trend.
- highest secret-secret cosine: b2_43 ~ b3_56 = 0.6220 (inspect if approaching duplication).
