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
    - `eval/corpus_v2/corpus_batch_04.jsonl` — 15 rows
    - `eval/corpus_v2/corpus_batch_05.jsonl` — 15 rows
- Hard-negatives: `eval/corpus_v2/hard_negatives_v2.jsonl` — 127 rows (90 anchor + 37 decoy)
- **Quota base = 90 cumulative secrets** (cumulative tally: Type B 18/90, policy_quota 7/90, boundary_test 9/90).

## Check 1 — Quota & coverage

Reference (advisory): Type B ~20% | boundary_test ~10% | policy_quota tag <=20% | no single marker_style >50%.

**domain**

| value | count | share |
|-------|------:|------:|
| technical_indicator | 6 | 0.067 |
| factor_model | 6 | 0.067 |
| position_sizing | 6 | 0.067 |
| risk_model | 6 | 0.067 |
| settlement_ops | 6 | 0.067 |
| portfolio_construction | 6 | 0.067 |
| liquidity_management | 6 | 0.067 |
| prime_brokerage_margin | 6 | 0.067 |
| market_making | 6 | 0.067 |
| stat_arb | 6 | 0.067 |
| credit_screening | 6 | 0.067 |
| regulatory_concentration | 5 | 0.056 |
| exchange_rule_execution | 5 | 0.056 |
| execution_vwap | 5 | 0.056 |
| execution_scheduling | 5 | 0.056 |
| portfolio_insurance | 4 | 0.044 |

**offset_type**

| value | count | share |
|-------|------:|------:|
| A | 72 | 0.800 |
| B | 18 | 0.200 |

**subset**

| value | count | share |
|-------|------:|------:|
| core | 81 | 0.900 |
| boundary_test | 9 | 0.100 |

**marker_style**

| value | count | share |
|-------|------:|------:|
| none | 34 | 0.378 |
| internal | 16 | 0.178 |
| desk | 12 | 0.133 |
| production | 9 | 0.100 |
| our | 7 | 0.078 |
| ops | 6 | 0.067 |
| firm | 6 | 0.067 |

- Type B: 18/90 (0.200)
- boundary_test: 9/90 (0.100)
- policy_quota tag: 7/90 (0.078)
- marker_style top: 'none' (0.378)

_Manual-review items (Check 1):_
- none (all dimensions within advisory reference lines).

## Check 2 — Surface-form / shortcut audit

### (b1) regex n-gram shortcut candidates

n-grams (n=2..5, lowercased, punctuation-stripped) in >=3 secrets AND appearing in <10% of the 55 hard-negatives. Descending by secret doc count.

| n-gram | secret docs | hn occ | hn rate |
|--------|------------:|-------:|--------:|
| `with a` | 10 | 6 | 0.047 |
| `at 1` | 8 | 0 | 0.000 |
| `of adv` | 8 | 1 | 0.008 |
| `2 of` | 7 | 1 | 0.008 |
| `bps of` | 7 | 1 | 0.008 |
| `capped at` | 7 | 2 | 0.016 |
| `6 of` | 6 | 0 | 0.000 |
| `at 0` | 6 | 2 | 0.016 |
| `bounded at` | 6 | 0 | 0.000 |
| `of nav` | 6 | 2 | 0.016 |
| `1 5` | 5 | 1 | 0.008 |
| `30 minutes` | 5 | 1 | 0.008 |
| `at 2` | 5 | 0 | 0.000 |
| `days of` | 5 | 2 | 0.016 |
| `held under` | 5 | 0 | 0.000 |
| `in a` | 5 | 1 | 0.008 |
| `in the` | 5 | 11 | 0.087 |
| `of book` | 5 | 0 | 0.000 |
| `of fund` | 5 | 0 | 0.000 |
| `days of adv` | 4 | 0 | 0.000 |
| `0 6` | 4 | 2 | 0.016 |
| `1 2` | 4 | 1 | 0.008 |
| `1 5x` | 4 | 0 | 0.000 |
| `10 day` | 4 | 1 | 0.008 |
| `10 sessions` | 4 | 0 | 0.000 |
| `2 2` | 4 | 0 | 0.000 |
| `2 5x` | 4 | 0 | 0.000 |
| `35 bps` | 4 | 0 | 0.000 |
| `5 day` | 4 | 0 | 0.000 |
| `add on` | 4 | 0 | 0.000 |
| `after 2` | 4 | 0 | 0.000 |
| `at 8` | 4 | 1 | 0.008 |
| `at the` | 4 | 8 | 0.063 |
| `exit at` | 4 | 1 | 0.008 |
| `on a` | 4 | 2 | 0.016 |
| `only after` | 4 | 1 | 0.008 |
| `only when` | 4 | 0 | 0.000 |
| `realized vol` | 4 | 0 | 0.000 |
| `the first` | 4 | 1 | 0.008 |
| `versus the` | 4 | 0 | 0.000 |
| `with the` | 4 | 5 | 0.039 |
| `60 40 with` | 3 | 0 | 0.000 |
| `exposure capped at` | 3 | 0 | 0.000 |
| `0 5` | 3 | 3 | 0.024 |
| `0 55` | 3 | 0 | 0.000 |
| `1 3x` | 3 | 0 | 0.000 |
| `1 4` | 3 | 1 | 0.008 |
| `1 6` | 3 | 1 | 0.008 |
| `1 8x` | 3 | 0 | 0.000 |
| `10 minutes` | 3 | 0 | 0.000 |
| `20 day` | 3 | 3 | 0.024 |
| `3 2` | 3 | 0 | 0.000 |
| `3 5` | 3 | 4 | 0.031 |
| `3 sessions` | 3 | 0 | 0.000 |
| `30 days` | 3 | 0 | 0.000 |
| `40 with` | 3 | 0 | 0.000 |
| `6 with` | 3 | 0 | 0.000 |
| `60 40` | 3 | 0 | 0.000 |
| `8 bps` | 3 | 0 | 0.000 |
| `a 0` | 3 | 0 | 0.000 |
| `a 1` | 3 | 0 | 0.000 |
| `a week` | 3 | 0 | 0.000 |
| `above 0` | 3 | 1 | 0.008 |
| `above 4` | 3 | 0 | 0.000 |
| `above the` | 3 | 2 | 0.016 |
| `and 0` | 3 | 3 | 0.024 |
| `at 15` | 3 | 1 | 0.008 |
| `at 28` | 3 | 0 | 0.000 |
| `at 7` | 3 | 1 | 0.008 |
| `at a` | 3 | 1 | 0.008 |
| `ceiling 3` | 3 | 0 | 0.000 |
| `desk rule` | 3 | 0 | 0.000 |
| `entry at` | 3 | 1 | 0.008 |
| `exceeds 1` | 3 | 0 | 0.000 |
| `exposure capped` | 3 | 0 | 0.000 |
| `falls below` | 3 | 0 | 0.000 |
| `for positions` | 3 | 0 | 0.000 |
| `for the` | 3 | 3 | 0.024 |
| `half life` | 3 | 2 | 0.016 |
| `into the` | 3 | 1 | 0.008 |
| `is under` | 3 | 0 | 0.000 |
| `move to` | 3 | 0 | 0.000 |
| `next day` | 3 | 0 | 0.000 |
| `of any` | 3 | 0 | 0.000 |
| `of equity` | 3 | 2 | 0.016 |
| `one third` | 3 | 0 | 0.000 |
| `p m` | 3 | 3 | 0.024 |
| `per name` | 3 | 0 | 0.000 |
| `percentile over` | 3 | 0 | 0.000 |
| `rather than` | 3 | 0 | 0.000 |
| `runs under` | 3 | 0 | 0.000 |
| `same day` | 3 | 0 | 0.000 |
| `sign off` | 3 | 0 | 0.000 |
| `single issuer` | 3 | 2 | 0.016 |
| `single name` | 3 | 0 | 0.000 |
| `the close` | 3 | 0 | 0.000 |
| `the top` | 3 | 0 | 0.000 |
| `to the` | 3 | 7 | 0.055 |
| `week move` | 3 | 0 | 0.000 |
| `when the` | 3 | 1 | 0.008 |
| `within 10` | 3 | 1 | 0.008 |
| `within 3` | 3 | 0 | 0.000 |
| `within 5` | 3 | 3 | 0.024 |

### (b2) marker / heuristic separability

predicate -> predicts 'secret'. positives = secrets, negatives = hard-negs. FP broken down by hard-neg kind (anchor / decoy), NOT merged. Alarm line (annotate only): recall>0.9 AND precision>0.9.

| heuristic | precision | recall | TP | FP | FN | FP_anchor (rate) | FP_decoy (rate) | ALARM |
|-----------|----------:|-------:|---:|---:|---:|-----------------|----------------|:-----:|
| vocab:our | 0.667 | 0.089 | 8 | 4 | 82 | 0 (0.000) | 4 (0.108) |  |
| vocab:internal | 0.789 | 0.167 | 15 | 4 | 75 | 1 (0.011) | 3 (0.081) |  |
| vocab:desk | 0.818 | 0.200 | 18 | 4 | 72 | 0 (0.000) | 4 (0.108) |  |
| vocab:proprietary | 0.000 | 0.000 | 0 | 1 | 90 | 0 (0.000) | 1 (0.027) |  |
| vocab:production | 0.800 | 0.044 | 4 | 1 | 86 | 0 (0.000) | 1 (0.027) |  |
| vocab:firm | 0.500 | 0.011 | 1 | 1 | 89 | 0 (0.000) | 1 (0.027) |  |
| vocab:ops | 1.000 | 0.067 | 6 | 0 | 84 | 0 (0.000) | 0 (0.000) |  |
| vocab:ANY | 0.804 | 0.500 | 45 | 11 | 45 | 1 (0.011) | 10 (0.270) |  |
| struct:num>=1 | 0.455 | 1.000 | 90 | 108 | 0 | 78 (0.867) | 30 (0.811) |  |
| struct:num>=3 | 0.621 | 1.000 | 90 | 55 | 0 | 33 (0.367) | 22 (0.595) |  |
| struct:semicolon>=2 | 0.888 | 0.967 | 87 | 11 | 3 | 0 (0.000) | 11 (0.297) |  |

### (b3) numeric-token density

numeric token = whitespace-separated token containing >=1 digit.

- **secret**: n=90 mean=5.0333 median=5.0000 p25=4.0000 p75=6.0000 min=3.0000 max=9.0000
    - histogram (count -> #items): {'3': 10, '4': 22, '5': 27, '6': 20, '7': 9, '8': 1, '9': 1}
- **anchor**: n=90 mean=2.0889 median=2.0000 p25=1.0000 p75=3.0000 min=0.0000 max=7.0000
    - histogram (count -> #items): {'0': 12, '1': 16, '2': 29, '3': 22, '4': 9, '5': 1, '7': 1}
- **decoy**: n=37 mean=3.4595 median=3.0000 p25=1.0000 p75=5.0000 min=0.0000 max=10.0000
    - histogram (count -> #items): {'0': 7, '1': 4, '2': 4, '3': 4, '4': 1, '5': 9, '6': 4, '7': 3, '10': 1}
- decoy-pool numeric-token mean = 3.4595 vs 3.5 stop-line (delta -0.0405) — reported only, not judged.

_Manual-review items (Check 2):_
- 103 n-gram shortcut candidate(s) (b1) — inspect for regex-anchorability.
- (b3) inspect whether secret vs hard-neg numeric-count distributions are near-disjoint (would make 'count the numbers' itself a shortcut).

## Check 3 — Embedding hygiene

### secret vs own anchor_text cosine

- overall: n=90 mean=0.4812 median=0.4887 p25=0.4052 p75=0.5590 min=0.2189 max=0.7447
- offset_type A: n=72 mean=0.4796 median=0.4872 p25=0.4032 p75=0.5619 min=0.2189 max=0.7447
- offset_type B: n=18 mean=0.4874 median=0.5069 p25=0.4267 p75=0.5417 min=0.2652 max=0.6695

by domain:

| domain | stats |
|--------|-------|
| credit_screening | n=6 mean=0.4677 median=0.4872 p25=0.4676 p75=0.4889 min=0.3891 max=0.4924 |
| exchange_rule_execution | n=5 mean=0.4144 median=0.4151 p25=0.3012 p75=0.5178 min=0.2652 max=0.5728 |
| execution_scheduling | n=5 mean=0.4445 median=0.4679 p25=0.4038 p75=0.4685 min=0.3537 max=0.5287 |
| execution_vwap | n=5 mean=0.5451 median=0.5743 p25=0.5241 p75=0.6154 min=0.2672 max=0.7447 |
| factor_model | n=6 mean=0.4778 median=0.4543 p25=0.4390 p75=0.4940 min=0.3622 max=0.6550 |
| liquidity_management | n=6 mean=0.5251 median=0.5101 p25=0.4390 p75=0.5886 min=0.3768 max=0.7235 |
| market_making | n=6 mean=0.4141 median=0.4189 p25=0.3692 p75=0.4374 min=0.2284 max=0.6221 |
| portfolio_construction | n=6 mean=0.4829 median=0.4942 p25=0.3815 p75=0.5450 min=0.3387 max=0.6645 |
| portfolio_insurance | n=4 mean=0.3930 median=0.3853 p25=0.3316 p75=0.4466 min=0.2189 max=0.5824 |
| position_sizing | n=6 mean=0.5520 median=0.5797 p25=0.5185 p75=0.6446 min=0.3055 max=0.6828 |
| prime_brokerage_margin | n=6 mean=0.5331 median=0.5222 p25=0.4899 p75=0.5417 min=0.4573 max=0.6695 |
| regulatory_concentration | n=5 mean=0.5846 median=0.5758 p25=0.5553 p75=0.6341 min=0.5213 max=0.6367 |
| risk_model | n=6 mean=0.4521 median=0.4569 p25=0.4300 p75=0.5166 min=0.2743 max=0.5672 |
| settlement_ops | n=6 mean=0.4793 median=0.4895 p25=0.4080 p75=0.5208 min=0.3617 max=0.6230 |
| stat_arb | n=6 mean=0.4312 median=0.4104 p25=0.3745 p75=0.4744 min=0.3274 max=0.5806 |
| technical_indicator | n=6 mean=0.4833 median=0.5062 p25=0.4677 p75=0.5397 min=0.2794 max=0.6024 |

### cross-pair rank violations (secret's own anchor NOT nearest among 30)

| id | own cosine | anchor_rank | nearest_anchor_id | nearest cosine |
|----|-----------:|:-----------:|-------------------|---------------:|
| p0_04 | 0.3012 | 8 | b1_19 | 0.4490 |
| p0_07 | 0.5743 | 2 | b5_78 | 0.6132 |
| p0_08 | 0.3617 | 6 | b2_40 | 0.4800 |
| p0_09 | 0.3387 | 3 | p0_14 | 0.3814 |
| p0_12 | 0.2284 | 20 | b2_41 | 0.3251 |
| p0_14 | 0.2189 | 31 | b4_63 | 0.3830 |
| p0_15 | 0.3891 | 3 | b4_68 | 0.4596 |
| b1_16 | 0.4592 | 2 | b2_41 | 0.5283 |
| b1_18 | 0.2743 | 10 | b3_57 | 0.3139 |
| b1_20 | 0.3837 | 5 | b4_75 | 0.5043 |
| b1_22 | 0.4284 | 2 | b5_85 | 0.5570 |
| b1_23 | 0.3669 | 2 | b3_51 | 0.3717 |
| b1_24 | 0.4997 | 3 | b1_28 | 0.5332 |
| b2_37 | 0.3274 | 9 | p0_01 | 0.3806 |
| b2_39 | 0.3768 | 2 | b2_40 | 0.4348 |
| b2_43 | 0.4014 | 2 | b3_56 | 0.4120 |
| b2_44 | 0.2672 | 15 | b2_41 | 0.3820 |
| b3_50 | 0.3622 | 3 | b4_71 | 0.3681 |
| b3_51 | 0.4790 | 2 | b5_82 | 0.5141 |
| b3_53 | 0.3974 | 4 | b2_40 | 0.4305 |
| b3_60 | 0.4813 | 3 | b2_39 | 0.5013 |
| b4_65 | 0.2794 | 21 | b2_41 | 0.4523 |
| b4_67 | 0.4349 | 2 | b3_46 | 0.4897 |
| b4_70 | 0.3558 | 4 | b5_85 | 0.4319 |
| b4_71 | 0.3457 | 6 | p0_12 | 0.3921 |
| b4_73 | 0.3055 | 19 | b3_56 | 0.4228 |
| b5_77 | 0.2652 | 8 | b4_62 | 0.3353 |
| b5_85 | 0.4404 | 3 | b2_36 | 0.4500 |
| b5_87 | 0.4646 | 2 | p0_04 | 0.4973 |

### anchor-anchor crosstalk (cosine > 0.8)

_No anchor pair exceeds 0.8._

### atomic paired delta — gate (a) v3 (scale-robust)

gate (a) v3 — scale-robust, offset_type-scoped (N = anchor-pool size). Type A — PRIMARY criterion delta>0; violation iff delta<=0 (stationary in N). Attribution demoted to monitoring: own-anchor rank > ceil(0.10*N) -> attribution-watch (NOT a violation). Type B — anchor-mirroring not expected; identity-preservation scales with the pool: violation iff rank > ceil(0.10*N); delta reported but not a criterion. Violations are flagged for manual review; magnitude judgment is left to the human.

- **N (anchor pool) = 90; ceil(0.10*N) = 9** (Type B violation line; Type A attribution-watch line).
- delta>0: 71/90 | delta<0: 19 | delta==0: 0
- delta mean +0.1216 | min -0.1743 | max +0.7072

_Type A violation = delta<=0 (rank not used). Type B violation = rank > 9. 'watch' = Type A attribution-watch (rank>9, not a violation)._

| id | type | bundle cos | atomic cos | delta | atomic rank | criterion | violation | watch | note |
|----|:----:|-----------:|-----------:|------:|:-----------:|-----------|:---------:|:-----:|------|
| p0_01 | A | 0.4933 | 0.9155 | +0.4222 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_02 | A | 0.6550 | 0.7331 | +0.0781 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_03 | A | 0.6367 | 0.6450 | +0.0083 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_04 | B | 0.3012 | 0.2925 | -0.0088 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| p0_05 | A | 0.5870 | 0.6066 | +0.0196 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_06 | A | 0.4283 | 0.8531 | +0.4247 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_07 | A | 0.5743 | 0.6777 | +0.1033 | 2 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_08 | B | 0.3617 | 0.3327 | -0.0290 | 4 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| p0_09 | A | 0.3387 | 0.6692 | +0.3305 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_10 | A | 0.7235 | 0.8054 | +0.0819 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_11 | B | 0.5157 | 0.5706 | +0.0549 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| p0_12 | A | 0.2284 | 0.8044 | +0.5760 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_13 | A | 0.4235 | 0.6950 | +0.2715 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_14 | A | 0.2189 | 0.9261 | +0.7072 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| p0_15 | A | 0.3891 | 0.3930 | +0.0039 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_16 | A | 0.4592 | 0.8680 | +0.4088 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_17 | A | 0.5027 | 0.5314 | +0.0287 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_18 | A | 0.2743 | 0.4730 | +0.1988 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_19 | A | 0.4685 | 0.4263 | -0.0421 | 1 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b1_20 | B | 0.3837 | 0.3298 | -0.0538 | 3 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b1_21 | B | 0.5288 | 0.6581 | +0.1293 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b1_22 | A | 0.4284 | 0.4297 | +0.0012 | 2 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_23 | A | 0.3669 | 0.5268 | +0.1599 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_24 | A | 0.4997 | 0.6411 | +0.1414 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_25 | A | 0.4305 | 0.8281 | +0.3976 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_26 | A | 0.4889 | 0.7061 | +0.2172 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_27 | B | 0.4151 | 0.3117 | -0.1034 | 3 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b1_28 | A | 0.6638 | 0.7064 | +0.0426 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_29 | A | 0.5824 | 0.9260 | +0.3437 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b1_30 | A | 0.4383 | 0.6544 | +0.2161 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_31 | B | 0.4980 | 0.4750 | -0.0230 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b2_32 | B | 0.5178 | 0.4575 | -0.0603 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b2_33 | B | 0.6221 | 0.5660 | -0.0560 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b2_34 | A | 0.5758 | 0.5462 | -0.0296 | 3 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b2_35 | A | 0.5292 | 0.4340 | -0.0952 | 3 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b2_36 | B | 0.4615 | 0.3339 | -0.1276 | 5 | Type B: rank<=ceil(0.10*N)=9 |  |  | Type B exception (PI ruling, batch_03; pattern-test datapoint) |
| b2_37 | A | 0.3274 | 0.5459 | +0.2186 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_38 | A | 0.5601 | 0.5736 | +0.0134 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_39 | A | 0.3768 | 0.5439 | +0.1671 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_40 | B | 0.5460 | 0.5769 | +0.0309 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b2_41 | A | 0.5466 | 0.8985 | +0.3519 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_42 | A | 0.5005 | 0.6763 | +0.1758 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_43 | A | 0.4014 | 0.6160 | +0.2146 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_44 | A | 0.2672 | 0.3822 | +0.1150 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b2_45 | A | 0.4038 | 0.4819 | +0.0781 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_46 | A | 0.5213 | 0.5419 | +0.0206 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_47 | A | 0.6154 | 0.7926 | +0.1772 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_48 | A | 0.4679 | 0.5437 | +0.0758 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_49 | A | 0.5191 | 0.8374 | +0.3183 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_50 | A | 0.3622 | 0.4743 | +0.1121 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_51 | A | 0.4790 | 0.6051 | +0.1261 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_52 | A | 0.4887 | 0.5803 | +0.0917 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_53 | A | 0.3974 | 0.4822 | +0.0848 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_54 | A | 0.4094 | 0.4578 | +0.0484 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_55 | A | 0.4887 | 0.6954 | +0.2066 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_56 | A | 0.3692 | 0.4735 | +0.1043 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_57 | A | 0.5555 | 0.7456 | +0.1901 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_58 | A | 0.6828 | 0.7045 | +0.0217 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b3_59 | B | 0.6230 | 0.4487 | -0.1743 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b3_60 | B | 0.4813 | 0.5357 | +0.0544 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b4_61 | A | 0.6341 | 0.8068 | +0.1728 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_62 | B | 0.5728 | 0.4286 | -0.1443 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b4_63 | A | 0.5241 | 0.9646 | +0.4406 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_64 | A | 0.3537 | 0.4554 | +0.1017 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_65 | A | 0.2794 | 0.4522 | +0.1728 | 2 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_66 | A | 0.4677 | 0.4243 | -0.0435 | 1 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b4_67 | A | 0.4349 | 0.8053 | +0.3704 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_68 | A | 0.4858 | 0.5424 | +0.0566 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_69 | A | 0.4914 | 0.4791 | -0.0123 | 2 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b4_70 | A | 0.3558 | 0.4606 | +0.1048 | 2 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_71 | A | 0.3457 | 0.6429 | +0.2972 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_72 | A | 0.5996 | 0.7505 | +0.1509 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_73 | A | 0.3055 | 0.3250 | +0.0195 | 7 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b4_74 | B | 0.4810 | 0.7174 | +0.2363 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b4_75 | B | 0.6695 | 0.7912 | +0.1217 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b5_76 | A | 0.5553 | 0.6379 | +0.0826 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_77 | B | 0.2652 | 0.2317 | -0.0335 | 6 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b5_78 | A | 0.7447 | 0.7973 | +0.0526 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_79 | A | 0.5287 | 0.5541 | +0.0254 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_80 | A | 0.6024 | 0.7959 | +0.1935 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_81 | A | 0.4409 | 0.2922 | -0.1487 | 5 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b5_82 | A | 0.5672 | 0.5792 | +0.0120 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_83 | A | 0.4924 | 0.6683 | +0.1759 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_84 | A | 0.5806 | 0.7202 | +0.1396 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_85 | A | 0.4404 | 0.8007 | +0.3603 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_86 | A | 0.6645 | 0.8212 | +0.1567 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |
| b5_87 | A | 0.4646 | 0.3519 | -0.1127 | 5 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b5_88 | A | 0.5723 | 0.4558 | -0.1165 | 2 | Type A: delta>0 (attribution rank monitored) | YES |  |  |
| b5_89 | B | 0.5284 | 0.7392 | +0.2108 | 1 | Type B: rank<=ceil(0.10*N)=9 |  |  |  |
| b5_90 | A | 0.4573 | 0.7982 | +0.3409 | 1 | Type A: delta>0 (attribution rank monitored) |  |  |  |

- Type A violations (delta<=0): ['b1_19', 'b2_34', 'b2_35', 'b4_66', 'b4_69', 'b5_81', 'b5_87', 'b5_88']
- Type B violations (rank>9): none
- Type A attribution-watch (rank>9, NOT violations): none
- **newly-crossed this round** (vs prior batch re-evaluated under v3, N_prev=75): ['b5_81', 'b5_87', 'b5_88'] (definition: violation now AND not a v3 violation last round — independent of which batch the id belongs to, so pool-growth seed crossings are counted).
- Type B pattern-test: cumulative 0 (newly-crossed: 0).

**v3 pre-registration reconciliation:**

- expected Type A violations = base['b1_19', 'b2_34', 'b2_35', 'b4_66', 'b4_69'] ∪ b5-A-with-delta<=0['b5_81', 'b5_87', 'b5_88'] = ['b1_19', 'b2_34', 'b2_35', 'b4_66', 'b4_69', 'b5_81', 'b5_87', 'b5_88']
- actual Type A violations = ['b1_19', 'b2_34', 'b2_35', 'b4_66', 'b4_69', 'b5_81', 'b5_87', 'b5_88']
  - deviations: missing=none | unexpected=none
- expected Type B violations = only rank>9 (pre-reg: ['b2_36', 'p0_08'] expected to REGRESS to PASS)
- actual Type B violations = []
  - p0_08/b2_36 regression: passed=['b2_36', 'p0_08'] | still-violating=none

_Manual-review items (Check 3):_
- 29 secret(s) whose own anchor is not nearest (secret-vs-anchor cross-pair; informational, not a gate).
- atomic gate(a) v3 violations: Type A ['b1_19', 'b2_34', 'b2_35', 'b4_66', 'b4_69', 'b5_81', 'b5_87', 'b5_88']; Type B none.

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

## Check 5 — Secret-Secret Nearest Neighbor Audit (monitor v2)

Monitor v2 (chat-ratified): the PRIMARY criterion is the top-1 secret-secret cosine (WARNING > 0.70, STOP-AND-REVIEW > 0.75, annotate only — no auto-judgment). cross-domain NN share is demoted to purely DESCRIPTIVE (no health framing); any direction change is accompanied only by the list of newly-contributing pairs.

- **PRIMARY: top-1 secret-secret cosine = 0.7444 -> [WARNING]** (p0_07 ~ b5_78; thresholds: WARNING>0.70, STOP-AND-REVIEW>0.75).
- (descriptive) same-domain NN: 45/90 (0.500); cross-domain NN share 0.500.
- (descriptive) domains=16, avg members/domain = 5.6250.

**Trend (this batch vs frozen prior batches):**

| metric | this batch | baseline batch_01 (frozen) | batch_02 | batch_03 |
|--------|-----------:|-----------:|-----------:|-----------:|
| top-1 secret-secret cosine (PRIMARY) | 0.7444 | 0.6028 (Δ+0.1416) | 0.6028 (Δ+0.1416) | 0.6220 (Δ+0.1224) |
| cross-domain NN share (descriptive) | 0.500 | 0.667 (Δ-0.167) | 0.622 (Δ-0.122) | 0.583 (Δ-0.083) |
| avg members/domain | 5.6250 | 1.8750 | 2.8125 | 3.7500 |

**Newly-contributing cross-domain NN pairs (source = this batch's secrets):**

| id | domain | NN id | NN domain | cosine |
|----|--------|-------|-----------|-------:|
| b5_76 | regulatory_concentration | p0_10 | liquidity_management | 0.5574 |
| b5_79 | execution_scheduling | b2_37 | stat_arb | 0.4900 |
| b5_80 | technical_indicator | b5_84 | stat_arb | 0.4363 |
| b5_82 | risk_model | b1_22 | market_making | 0.4605 |
| b5_83 | credit_screening | b4_72 | liquidity_management | 0.5053 |
| b5_85 | market_making | b2_38 | portfolio_construction | 0.5217 |
| b5_90 | prime_brokerage_margin | b4_73 | position_sizing | 0.4272 |

### (i) each secret's nearest-neighbour secret

| id | domain | NN id | NN domain | cosine | same-domain |
|----|--------|-------|-----------|-------:|:-----------:|
| p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 | yes |
| p0_02 | factor_model | b4_66 | factor_model | 0.5746 | yes |
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 | NO |
| p0_04 | exchange_rule_execution | b5_77 | exchange_rule_execution | 0.4893 | yes |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 | NO |
| p0_06 | risk_model | b1_18 | risk_model | 0.5334 | yes |
| p0_07 | execution_vwap | b5_78 | execution_vwap | 0.7444 | yes |
| p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 | NO |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 | NO |
| p0_10 | liquidity_management | b5_76 | regulatory_concentration | 0.5574 | NO |
| p0_11 | prime_brokerage_margin | b4_75 | prime_brokerage_margin | 0.5305 | yes |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 | NO |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 | NO |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 | NO |
| p0_15 | credit_screening | b4_68 | credit_screening | 0.6104 | yes |
| b1_16 | technical_indicator | p0_01 | technical_indicator | 0.6028 | yes |
| b1_17 | factor_model | b5_81 | factor_model | 0.5408 | yes |
| b1_18 | risk_model | p0_06 | risk_model | 0.5334 | yes |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 | NO |
| b1_20 | settlement_ops | b3_59 | settlement_ops | 0.5822 | yes |
| b1_21 | prime_brokerage_margin | b3_58 | position_sizing | 0.5467 | NO |
| b1_22 | market_making | b4_70 | market_making | 0.6404 | yes |
| b1_23 | stat_arb | b5_84 | stat_arb | 0.5037 | yes |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 | NO |
| b1_25 | liquidity_management | b2_39 | liquidity_management | 0.5954 | yes |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 | NO |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 | NO |
| b1_28 | position_sizing | b3_48 | execution_scheduling | 0.5663 | NO |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 | NO |
| b1_30 | factor_model | b4_66 | factor_model | 0.5325 | yes |
| b2_31 | settlement_ops | b5_89 | settlement_ops | 0.4723 | yes |
| b2_32 | exchange_rule_execution | b5_89 | settlement_ops | 0.4962 | NO |
| b2_33 | market_making | b4_70 | market_making | 0.4758 | yes |
| b2_34 | regulatory_concentration | b4_73 | position_sizing | 0.5353 | NO |
| b2_35 | risk_model | b3_58 | position_sizing | 0.5641 | NO |
| b2_36 | credit_screening | b2_34 | regulatory_concentration | 0.5176 | NO |
| b2_37 | stat_arb | b1_19 | execution_scheduling | 0.4998 | NO |
| b2_38 | portfolio_construction | b5_85 | market_making | 0.5217 | NO |
| b2_39 | liquidity_management | b1_25 | liquidity_management | 0.5954 | yes |
| b2_40 | prime_brokerage_margin | p0_08 | settlement_ops | 0.5870 | NO |
| b2_41 | technical_indicator | b1_16 | technical_indicator | 0.4640 | yes |
| b2_42 | position_sizing | b5_88 | position_sizing | 0.4907 | yes |
| b2_43 | portfolio_insurance | b3_56 | portfolio_insurance | 0.6220 | yes |
| b2_44 | execution_vwap | b4_63 | execution_vwap | 0.5159 | yes |
| b2_45 | execution_scheduling | b5_79 | execution_scheduling | 0.4568 | yes |
| b3_46 | regulatory_concentration | p0_03 | regulatory_concentration | 0.4755 | yes |
| b3_47 | execution_vwap | b5_78 | execution_vwap | 0.5823 | yes |
| b3_48 | execution_scheduling | b1_28 | position_sizing | 0.5663 | NO |
| b3_49 | technical_indicator | b2_37 | stat_arb | 0.4852 | NO |
| b3_50 | factor_model | b1_30 | factor_model | 0.4574 | yes |
| b3_51 | risk_model | p0_03 | regulatory_concentration | 0.4790 | NO |
| b3_52 | credit_screening | b4_68 | credit_screening | 0.4635 | yes |
| b3_53 | stat_arb | p0_08 | settlement_ops | 0.4577 | NO |
| b3_54 | market_making | p0_11 | prime_brokerage_margin | 0.4544 | NO |
| b3_55 | portfolio_construction | b4_71 | portfolio_construction | 0.5355 | yes |
| b3_56 | portfolio_insurance | b2_43 | portfolio_insurance | 0.6220 | yes |
| b3_57 | liquidity_management | b4_69 | stat_arb | 0.5518 | NO |
| b3_58 | position_sizing | b2_35 | risk_model | 0.5641 | NO |
| b3_59 | settlement_ops | b1_20 | settlement_ops | 0.5822 | yes |
| b3_60 | prime_brokerage_margin | b4_61 | regulatory_concentration | 0.5418 | NO |
| b4_61 | regulatory_concentration | b3_60 | prime_brokerage_margin | 0.5418 | NO |
| b4_62 | exchange_rule_execution | b2_32 | exchange_rule_execution | 0.4438 | yes |
| b4_63 | execution_vwap | b2_44 | execution_vwap | 0.5159 | yes |
| b4_64 | execution_scheduling | b1_29 | portfolio_insurance | 0.4313 | NO |
| b4_65 | technical_indicator | p0_07 | execution_vwap | 0.4701 | NO |
| b4_66 | factor_model | p0_02 | factor_model | 0.5746 | yes |
| b4_67 | risk_model | p0_10 | liquidity_management | 0.4952 | NO |
| b4_68 | credit_screening | p0_15 | credit_screening | 0.6104 | yes |
| b4_69 | stat_arb | b3_57 | liquidity_management | 0.5518 | NO |
| b4_70 | market_making | b1_22 | market_making | 0.6404 | yes |
| b4_71 | portfolio_construction | b3_55 | portfolio_construction | 0.5355 | yes |
| b4_72 | liquidity_management | b5_83 | credit_screening | 0.5053 | NO |
| b4_73 | position_sizing | b2_34 | regulatory_concentration | 0.5353 | NO |
| b4_74 | settlement_ops | b2_39 | liquidity_management | 0.4629 | NO |
| b4_75 | prime_brokerage_margin | p0_11 | prime_brokerage_margin | 0.5305 | yes |
| b5_76 | regulatory_concentration | p0_10 | liquidity_management | 0.5574 | NO |
| b5_77 | exchange_rule_execution | p0_04 | exchange_rule_execution | 0.4893 | yes |
| b5_78 | execution_vwap | p0_07 | execution_vwap | 0.7444 | yes |
| b5_79 | execution_scheduling | b2_37 | stat_arb | 0.4900 | NO |
| b5_80 | technical_indicator | b5_84 | stat_arb | 0.4363 | NO |
| b5_81 | factor_model | b1_17 | factor_model | 0.5408 | yes |
| b5_82 | risk_model | b1_22 | market_making | 0.4605 | NO |
| b5_83 | credit_screening | b4_72 | liquidity_management | 0.5053 | NO |
| b5_84 | stat_arb | b1_23 | stat_arb | 0.5037 | yes |
| b5_85 | market_making | b2_38 | portfolio_construction | 0.5217 | NO |
| b5_86 | portfolio_construction | b1_24 | portfolio_construction | 0.4362 | yes |
| b5_87 | liquidity_management | b3_57 | liquidity_management | 0.4846 | yes |
| b5_88 | position_sizing | b2_42 | position_sizing | 0.4907 | yes |
| b5_89 | settlement_ops | b3_59 | settlement_ops | 0.5772 | yes |
| b5_90 | prime_brokerage_margin | b4_73 | position_sizing | 0.4272 | NO |

### (ii) cross-domain NN pairs

| id | domain | NN id | NN domain | cosine |
|----|--------|-------|-----------|-------:|
| p0_03 | regulatory_concentration | p0_10 | liquidity_management | 0.5061 |
| p0_05 | position_sizing | p0_03 | regulatory_concentration | 0.4841 |
| p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 |
| p0_09 | portfolio_construction | b1_29 | portfolio_insurance | 0.3899 |
| p0_10 | liquidity_management | b5_76 | regulatory_concentration | 0.5574 |
| p0_12 | market_making | b1_16 | technical_indicator | 0.5220 |
| p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| p0_14 | portfolio_insurance | b1_28 | position_sizing | 0.5180 |
| b1_19 | execution_scheduling | p0_13 | stat_arb | 0.5950 |
| b1_21 | prime_brokerage_margin | b3_58 | position_sizing | 0.5467 |
| b1_24 | portfolio_construction | b1_28 | position_sizing | 0.5565 |
| b1_26 | credit_screening | b1_25 | liquidity_management | 0.4880 |
| b1_27 | exchange_rule_execution | p0_01 | technical_indicator | 0.4287 |
| b1_28 | position_sizing | b3_48 | execution_scheduling | 0.5663 |
| b1_29 | portfolio_insurance | p0_06 | risk_model | 0.5269 |
| b2_32 | exchange_rule_execution | b5_89 | settlement_ops | 0.4962 |
| b2_34 | regulatory_concentration | b4_73 | position_sizing | 0.5353 |
| b2_35 | risk_model | b3_58 | position_sizing | 0.5641 |
| b2_36 | credit_screening | b2_34 | regulatory_concentration | 0.5176 |
| b2_37 | stat_arb | b1_19 | execution_scheduling | 0.4998 |
| b2_38 | portfolio_construction | b5_85 | market_making | 0.5217 |
| b2_40 | prime_brokerage_margin | p0_08 | settlement_ops | 0.5870 |
| b3_48 | execution_scheduling | b1_28 | position_sizing | 0.5663 |
| b3_49 | technical_indicator | b2_37 | stat_arb | 0.4852 |
| b3_51 | risk_model | p0_03 | regulatory_concentration | 0.4790 |
| b3_53 | stat_arb | p0_08 | settlement_ops | 0.4577 |
| b3_54 | market_making | p0_11 | prime_brokerage_margin | 0.4544 |
| b3_57 | liquidity_management | b4_69 | stat_arb | 0.5518 |
| b3_58 | position_sizing | b2_35 | risk_model | 0.5641 |
| b3_60 | prime_brokerage_margin | b4_61 | regulatory_concentration | 0.5418 |
| b4_61 | regulatory_concentration | b3_60 | prime_brokerage_margin | 0.5418 |
| b4_64 | execution_scheduling | b1_29 | portfolio_insurance | 0.4313 |
| b4_65 | technical_indicator | p0_07 | execution_vwap | 0.4701 |
| b4_67 | risk_model | p0_10 | liquidity_management | 0.4952 |
| b4_69 | stat_arb | b3_57 | liquidity_management | 0.5518 |
| b4_72 | liquidity_management | b5_83 | credit_screening | 0.5053 |
| b4_73 | position_sizing | b2_34 | regulatory_concentration | 0.5353 |
| b4_74 | settlement_ops | b2_39 | liquidity_management | 0.4629 |
| b5_76 | regulatory_concentration | p0_10 | liquidity_management | 0.5574 |
| b5_79 | execution_scheduling | b2_37 | stat_arb | 0.4900 |
| b5_80 | technical_indicator | b5_84 | stat_arb | 0.4363 |
| b5_82 | risk_model | b1_22 | market_making | 0.4605 |
| b5_83 | credit_screening | b4_72 | liquidity_management | 0.5053 |
| b5_85 | market_making | b2_38 | portfolio_construction | 0.5217 |
| b5_90 | prime_brokerage_margin | b4_73 | position_sizing | 0.4272 |

### (iii) top-10 secret-secret cosine (any domain)

| rank | A | A domain | B | B domain | cosine |
|-----:|---|----------|---|----------|-------:|
| 1 | p0_07 | execution_vwap | b5_78 | execution_vwap | 0.7444 |
| 2 | b1_22 | market_making | b4_70 | market_making | 0.6404 |
| 3 | b2_43 | portfolio_insurance | b3_56 | portfolio_insurance | 0.6220 |
| 4 | p0_15 | credit_screening | b4_68 | credit_screening | 0.6104 |
| 5 | p0_01 | technical_indicator | b1_16 | technical_indicator | 0.6028 |
| 6 | b1_25 | liquidity_management | b2_39 | liquidity_management | 0.5954 |
| 7 | p0_13 | stat_arb | b1_19 | execution_scheduling | 0.5950 |
| 8 | p0_08 | settlement_ops | b2_40 | prime_brokerage_margin | 0.5870 |
| 9 | b3_47 | execution_vwap | b5_78 | execution_vwap | 0.5823 |
| 10 | b1_20 | settlement_ops | b3_59 | settlement_ops | 0.5822 |

_Manual-review items (Check 5):_
- PRIMARY top-1 secret-secret cosine 0.7444 -> [WARNING] (p0_07 ~ b5_78).
- 7 newly-contributing cross-domain NN pair(s) from this batch (descriptive — see table above).
