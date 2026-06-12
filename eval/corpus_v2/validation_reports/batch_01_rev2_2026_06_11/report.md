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
- Hard-negatives: `eval/corpus_v2/hard_negatives_v2.jsonl` — 55 rows (30 anchor + 25 decoy)
- **Quota base = 30 cumulative secrets** (expected ref: Type B 6/30, policy 3/30, boundary 3/30).

## Check 1 — Quota & coverage

Reference (advisory): Type B ~20% | boundary_test ~10% | policy_quota tag <=20% | no single marker_style >50%.

**domain**

| value | count | share |
|-------|------:|------:|
| factor_model | 3 | 0.100 |
| technical_indicator | 2 | 0.067 |
| exchange_rule_execution | 2 | 0.067 |
| position_sizing | 2 | 0.067 |
| risk_model | 2 | 0.067 |
| settlement_ops | 2 | 0.067 |
| portfolio_construction | 2 | 0.067 |
| liquidity_management | 2 | 0.067 |
| prime_brokerage_margin | 2 | 0.067 |
| market_making | 2 | 0.067 |
| stat_arb | 2 | 0.067 |
| portfolio_insurance | 2 | 0.067 |
| credit_screening | 2 | 0.067 |
| regulatory_concentration | 1 | 0.033 |
| execution_vwap | 1 | 0.033 |
| execution_scheduling | 1 | 0.033 |

**offset_type**

| value | count | share |
|-------|------:|------:|
| A | 24 | 0.800 |
| B | 6 | 0.200 |

**subset**

| value | count | share |
|-------|------:|------:|
| core | 27 | 0.900 |
| boundary_test | 3 | 0.100 |

**marker_style**

| value | count | share |
|-------|------:|------:|
| none | 12 | 0.400 |
| desk | 5 | 0.167 |
| internal | 5 | 0.167 |
| our | 3 | 0.100 |
| ops | 2 | 0.067 |
| production | 2 | 0.067 |
| firm | 1 | 0.033 |

- Type B: 6/30 (0.200)
- boundary_test: 3/30 (0.100)
- policy_quota tag: 3/30 (0.100)
- marker_style top: 'none' (0.400)

_Manual-review items (Check 1):_
- none (all dimensions within advisory reference lines).

## Check 2 — Surface-form / shortcut audit

### (b1) regex n-gram shortcut candidates

n-grams (n=2..5, lowercased, punctuation-stripped) in >=3 secrets AND appearing in <10% of the 55 hard-negatives. Descending by secret doc count.

| n-gram | secret docs | hn occ | hn rate |
|--------|------------:|-------:|--------:|
| `capped at` | 7 | 2 | 0.036 |
| `of nav` | 6 | 1 | 0.018 |
| `at 1` | 4 | 0 | 0.000 |
| `of adv` | 4 | 1 | 0.018 |
| `60 40 with` | 3 | 0 | 0.000 |
| `exposure capped at` | 3 | 0 | 0.000 |
| `1 5x` | 3 | 0 | 0.000 |
| `1 8x` | 3 | 0 | 0.000 |
| `40 with` | 3 | 0 | 0.000 |
| `5 day` | 3 | 0 | 0.000 |
| `60 40` | 3 | 0 | 0.000 |
| `at 2` | 3 | 0 | 0.000 |
| `at the` | 3 | 5 | 0.091 |
| `desk rule` | 3 | 0 | 0.000 |
| `exposure capped` | 3 | 0 | 0.000 |
| `half life` | 3 | 2 | 0.036 |
| `is under` | 3 | 0 | 0.000 |
| `of book` | 3 | 0 | 0.000 |
| `on a` | 3 | 1 | 0.018 |
| `with a` | 3 | 1 | 0.018 |

### (b2) marker / heuristic separability

predicate -> predicts 'secret'. positives = secrets, negatives = hard-negs. FP broken down by hard-neg kind (anchor / decoy), NOT merged. Alarm line (annotate only): recall>0.9 AND precision>0.9.

| heuristic | precision | recall | TP | FP | FN | FP_anchor (rate) | FP_decoy (rate) | ALARM |
|-----------|----------:|-------:|---:|---:|---:|-----------------|----------------|:-----:|
| vocab:our | 0.429 | 0.100 | 3 | 4 | 27 | 0 (0.000) | 4 (0.160) |  |
| vocab:internal | 0.667 | 0.200 | 6 | 3 | 24 | 0 (0.000) | 3 (0.120) |  |
| vocab:desk | 0.714 | 0.333 | 10 | 4 | 20 | 0 (0.000) | 4 (0.160) |  |
| vocab:proprietary | 0.000 | 0.000 | 0 | 1 | 30 | 0 (0.000) | 1 (0.040) |  |
| vocab:production | 0.667 | 0.067 | 2 | 1 | 28 | 0 (0.000) | 1 (0.040) |  |
| vocab:firm | 0.500 | 0.033 | 1 | 1 | 29 | 0 (0.000) | 1 (0.040) |  |
| vocab:ops | 1.000 | 0.067 | 2 | 0 | 28 | 0 (0.000) | 0 (0.000) |  |
| vocab:ANY | 0.667 | 0.667 | 20 | 10 | 10 | 0 (0.000) | 10 (0.400) |  |
| struct:num>=1 | 0.455 | 1.000 | 30 | 36 | 0 | 18 (0.600) | 18 (0.720) |  |
| struct:num>=3 | 0.682 | 1.000 | 30 | 14 | 0 | 4 (0.133) | 10 (0.400) |  |
| struct:semicolon>=2 | 0.794 | 0.900 | 27 | 7 | 3 | 0 (0.000) | 7 (0.280) |  |

### (b3) numeric-token density

numeric token = whitespace-separated token containing >=1 digit.

- **secret**: n=30 mean=5.6000 median=6.0000 p25=5.0000 p75=6.7500 min=3.0000 max=9.0000
    - histogram (count -> #items): {'3': 3, '4': 4, '5': 6, '6': 9, '7': 6, '8': 1, '9': 1}
- **anchor**: n=30 mean=1.1333 median=1.0000 p25=0.0000 p75=2.0000 min=0.0000 max=4.0000
    - histogram (count -> #items): {'0': 12, '1': 8, '2': 6, '3': 2, '4': 2}
- **decoy**: n=25 mean=2.2400 median=2.0000 p25=0.0000 p75=3.0000 min=0.0000 max=7.0000
    - histogram (count -> #items): {'0': 7, '1': 4, '2': 4, '3': 4, '4': 1, '5': 3, '6': 1, '7': 1}

_Manual-review items (Check 2):_
- 20 n-gram shortcut candidate(s) (b1) — inspect for regex-anchorability.
- (b3) inspect whether secret vs hard-neg numeric-count distributions are near-disjoint (would make 'count the numbers' itself a shortcut).

## Check 3 — Embedding hygiene

### secret vs own anchor_text cosine

- overall: n=30 mean=0.4602 median=0.4488 p25=0.3850 p75=0.5255 min=0.2189 max=0.7235
- offset_type A: n=24 mean=0.4708 median=0.4638 p25=0.4149 p75=0.5763 min=0.2189 max=0.7235
- offset_type B: n=6 mean=0.4177 median=0.3994 p25=0.3672 p75=0.4906 min=0.3012 max=0.5288

by domain:

| domain | stats |
|--------|-------|
| credit_screening | n=2 mean=0.4390 median=0.4390 p25=0.4141 p75=0.4640 min=0.3891 max=0.4889 |
| exchange_rule_execution | n=2 mean=0.3582 median=0.3582 p25=0.3297 p75=0.3867 min=0.3012 max=0.4151 |
| execution_scheduling | n=1 mean=0.4685 median=0.4685 p25=0.4685 p75=0.4685 min=0.4685 max=0.4685 |
| execution_vwap | n=1 mean=0.5743 median=0.5743 p25=0.5743 p75=0.5743 min=0.5743 max=0.5743 |
| factor_model | n=3 mean=0.5320 median=0.5027 p25=0.4705 p75=0.5788 min=0.4383 max=0.6550 |
| liquidity_management | n=2 mean=0.5770 median=0.5770 p25=0.5037 p75=0.6502 min=0.4305 max=0.7235 |
| market_making | n=2 mean=0.3284 median=0.3284 p25=0.2784 p75=0.3784 min=0.2284 max=0.4284 |
| portfolio_construction | n=2 mean=0.4192 median=0.4192 p25=0.3790 p75=0.4595 min=0.3387 max=0.4997 |
| portfolio_insurance | n=2 mean=0.4006 median=0.4006 p25=0.3098 p75=0.4915 min=0.2189 max=0.5824 |
| position_sizing | n=2 mean=0.6254 median=0.6254 p25=0.6062 p75=0.6446 min=0.5870 max=0.6638 |
| prime_brokerage_margin | n=2 mean=0.5222 median=0.5222 p25=0.5190 p75=0.5255 min=0.5157 max=0.5288 |
| regulatory_concentration | n=1 mean=0.6367 median=0.6367 p25=0.6367 p75=0.6367 min=0.6367 max=0.6367 |
| risk_model | n=2 mean=0.3513 median=0.3513 p25=0.3128 p75=0.3898 min=0.2743 max=0.4283 |
| settlement_ops | n=2 mean=0.3727 median=0.3727 p25=0.3672 p75=0.3782 min=0.3617 max=0.3837 |
| stat_arb | n=2 mean=0.3952 median=0.3952 p25=0.3811 p75=0.4094 min=0.3669 max=0.4235 |
| technical_indicator | n=2 mean=0.4762 median=0.4762 p25=0.4677 p75=0.4848 min=0.4592 max=0.4933 |

### cross-pair rank violations (secret's own anchor NOT nearest among 30)

| id | own cosine | anchor_rank | nearest_anchor_id | nearest cosine |
|----|-----------:|:-----------:|-------------------|---------------:|
| p0_04 | 0.3012 | 3 | b1_19 | 0.4490 |
| p0_08 | 0.3617 | 5 | b1_27 | 0.4218 |
| p0_09 | 0.3387 | 2 | p0_14 | 0.3814 |
| p0_12 | 0.2284 | 5 | b1_16 | 0.2821 |
| p0_14 | 0.2189 | 11 | p0_07 | 0.3515 |
| b1_18 | 0.2743 | 5 | p0_02 | 0.3096 |
| b1_20 | 0.3837 | 3 | p0_11 | 0.4362 |
| b1_24 | 0.4997 | 2 | b1_28 | 0.5332 |

### anchor-anchor crosstalk (cosine > 0.8)

_No anchor pair exceeds 0.8._

### atomic paired delta

gate (a), offset_type-scoped: Type A — atomic should rank==1 AND be higher than its bundle (delta>0); violation = rank!=1 OR delta<=0. Type B — anchor-mirroring is NOT expected by design; only an identity-preservation attribution check applies: violation = rank>3. For Type B, delta is still reported but is NOT a criterion. Violations are flagged for manual review; magnitude judgment is left to the human.

- delta>0: 25/30 | delta<0: 5 | delta==0: 0
- delta mean +0.1710 | min -0.1034 | max +0.7072

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
| p0_08 | B | 0.3617 | 0.3327 | -0.0290 | 1 | Type B: rank<=3 attribution check only |  |
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
| b1_20 | B | 0.3837 | 0.3298 | -0.0538 | 1 | Type B: rank<=3 attribution check only |  |
| b1_21 | B | 0.5288 | 0.6581 | +0.1293 | 1 | Type B: rank<=3 attribution check only |  |
| b1_22 | A | 0.4284 | 0.4297 | +0.0012 | 1 | Type A: rank==1 & delta>0 |  |
| b1_23 | A | 0.3669 | 0.5268 | +0.1599 | 1 | Type A: rank==1 & delta>0 |  |
| b1_24 | A | 0.4997 | 0.6411 | +0.1414 | 1 | Type A: rank==1 & delta>0 |  |
| b1_25 | A | 0.4305 | 0.8281 | +0.3976 | 1 | Type A: rank==1 & delta>0 |  |
| b1_26 | A | 0.4889 | 0.7061 | +0.2172 | 1 | Type A: rank==1 & delta>0 |  |
| b1_27 | B | 0.4151 | 0.3117 | -0.1034 | 1 | Type B: rank<=3 attribution check only |  |
| b1_28 | A | 0.6638 | 0.7064 | +0.0426 | 1 | Type A: rank==1 & delta>0 |  |
| b1_29 | A | 0.5824 | 0.9260 | +0.3437 | 1 | Type A: rank==1 & delta>0 |  |
| b1_30 | A | 0.4383 | 0.6544 | +0.2161 | 1 | Type A: rank==1 & delta>0 |  |

_Manual-review items (Check 3):_
- 8 secret(s) whose own anchor is not nearest.
- atomic gate(a) violations (offset_type-scoped): b1_19.

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

### (iii) secret <-> secret exact duplicate

_None._

_Manual-review items (Check 4):_
- none.

## Check 5 — Secret-Secret Nearest Neighbor Audit

Motivation: template-collapse monitor. A rising cross-domain NN share batch-over-batch flags surface-template convergence. This batch = baseline.

- same-domain NN: 10/30 (0.333)
- cross-domain NN share: 0.667

### (i) each secret's nearest-neighbour secret

| id | domain | NN id | NN domain | cosine | same-domain |
|----|--------|-------|-----------|-------:|:-----------:|
| p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 | yes |
| p0_02 | factor_model | b1_30 | factor_model | 0.4628 | yes |
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 | NO |
| p0_04 | exchange_rule_execution | b1_20 | settlement_ops | 0.4310 | NO |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 | NO |
| p0_06 | risk_model | b1_18 | risk_model | 0.5334 | yes |
| p0_07 | execution_vwap | b1_19 | execution_scheduling | 0.4709 | NO |
| p0_08 | settlement_ops | b1_20 | settlement_ops | 0.5604 | yes |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 | NO |
| p0_10 | liquidity_management | p0_03 | regulatory_concentration | 0.5061 | NO |
| p0_11 | prime_brokerage_margin | b1_20 | settlement_ops | 0.4848 | NO |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 | NO |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 | NO |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 | NO |
| p0_15 | credit_screening | b1_26 | credit_screening | 0.4673 | yes |
| b1_16 | technical_indicator | p0_01 | technical_indicator | 0.6028 | yes |
| b1_17 | factor_model | b1_30 | factor_model | 0.5183 | yes |
| b1_18 | risk_model | p0_06 | risk_model | 0.5334 | yes |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 | NO |
| b1_20 | settlement_ops | p0_08 | settlement_ops | 0.5604 | yes |
| b1_21 | prime_brokerage_margin | p0_10 | liquidity_management | 0.5037 | NO |
| b1_22 | market_making | b1_21 | prime_brokerage_margin | 0.4372 | NO |
| b1_23 | stat_arb | b1_19 | execution_scheduling | 0.4587 | NO |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 | NO |
| b1_25 | liquidity_management | b1_26 | credit_screening | 0.4880 | NO |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 | NO |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 | NO |
| b1_28 | position_sizing | b1_24 | portfolio_construction | 0.5565 | NO |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 | NO |
| b1_30 | factor_model | b1_17 | factor_model | 0.5183 | yes |

### (ii) cross-domain NN pairs

| id | domain | NN id | NN domain | cosine |
|----|--------|-------|-----------|-------:|
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 |
| p0_04 | exchange_rule_execution | b1_20 | settlement_ops | 0.4310 |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 |
| p0_07 | execution_vwap | b1_19 | execution_scheduling | 0.4709 |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 |
| p0_10 | liquidity_management | p0_03 | regulatory_concentration | 0.5061 |
| p0_11 | prime_brokerage_margin | b1_20 | settlement_ops | 0.4848 |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 |
| b1_21 | prime_brokerage_margin | p0_10 | liquidity_management | 0.5037 |
| b1_22 | market_making | b1_21 | prime_brokerage_margin | 0.4372 |
| b1_23 | stat_arb | b1_19 | execution_scheduling | 0.4587 |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 |
| b1_25 | liquidity_management | b1_26 | credit_screening | 0.4880 |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 |
| b1_28 | position_sizing | b1_24 | portfolio_construction | 0.5565 |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 |

### (iii) top-10 secret-secret cosine (any domain)

| rank | A | A domain | B | B domain | cosine |
|-----:|---|----------|---|----------|-------:|
| 1 | p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 |
| 2 | p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| 3 | p0_08 | settlement_ops | b1_20 | settlement_ops | 0.5604 |
| 4 | b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 |
| 5 | p0_06 | risk_model | b1_18 | risk_model | 0.5334 |
| 6 | p0_06 | risk_model | b1_29 | portfolio_insurance | 0.5269 |
| 7 | p0_12 | market_making | b1_16 | technical_indicator | 0.5220 |
| 8 | b1_17 | factor_model | b1_30 | factor_model | 0.5183 |
| 9 | p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 |
| 10 | p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 |

_Manual-review items (Check 5):_
- baseline cross-domain NN share = 0.667; compare against batch 2+ for template-collapse trend.
- highest secret-secret cosine: p0_01 ~ b1_16 = 0.6028 (inspect if approaching duplication).
