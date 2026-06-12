# Attack id-map — CANDIDATE table for human ratification (READ-ONLY, ZERO API)

Candidate old->new (corpus_v2) attack retarget map. NOTHING was rewritten or retargeted; this is input for human review before the actual A-step.

## Method

- Mapping: MiniLM (`sentence-transformers/all-MiniLM-L6-v2`, the gate encoder) cosine between each old target secret text and the 90 corpus_v2 secret_texts; top-3 candidates listed.
- Old-secret texts merged from `secrets_full.jsonl` (preferred) + `secrets.jsonl` (fallback) to cover all 24 real S00xx targets.
- 'same domain' is a PROXY (old `category` vs new `domain` are different vocabularies): top1 cosine >= 0.5 AND top-2 candidates' new-domain agree.
- Numbers: digit-bearing query tokens (value-swappable params), listed for the human.

## Triage counts

| triage | count |
|--------|------:|
| mechanical | 0 |
| rewrite | 201 |
| manual-reauthor | 70 |
| **total** | **271** |

- original-70 (manual-reauthor): 70
- multi-target ('multiple') attacks: 68

## Why `mechanical` = 0 (mapping-strength diagnostic — key scoping result)

- top1 old->new cosine over all mapped attacks: **mean=0.477, median=0.498, min=0.324, max=0.527** — the BEST any old secret maps onto a single corpus_v2 secret is ~0.53; the restructure deliberately moved secrets into a fresh single-domain anchor+offset space, so old targets have NO close new twin.
- of the 201 generated attacks, only **19 carry a value-swappable number**, and **0 of those reach top1 cosine >= 0.5**.
- top-2 candidate domains agree (`domain_stable`) for **0/271** rows.
- **Conclusion: purely-mechanical retarget is not viable on this corpus pair.** The A-step is effectively rewrite (201) + manual re-author (70); the id-map's value is the top-3 candidate new targets per attack to seed those rewrites.

## ⚠️ Cross-domain-risk rows (top-2 candidate domains disagree) — human focus

| attack_id | orig_target | top1_cos | cand1 | cand2 | triage |
|-----------|-------------|---------:|-------|-------|--------|
| ATK_D01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_D02 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | manual-reauthor |
| ATK_D03 | S0003 | 0.4837 | p0_13|stat_arb|0.484 | b3_47|execution_vwap|0.470 | manual-reauthor |
| ATK_D04 | S0015 | 0.4085 | b2_33|market_making|0.408 | b2_31|settlement_ops|0.385 | manual-reauthor |
| ATK_D05 | S0019 | 0.4131 | b2_43|portfolio_insurance|0.413 | b4_69|stat_arb|0.401 | manual-reauthor |
| ATK_D06 | S0032 | 0.5272 | b1_24|portfolio_construction|0.527 | b1_21|prime_brokerage_margin|0.516 | manual-reauthor |
| ATK_D07 | S0013 | 0.4708 | b1_29|portfolio_insurance|0.471 | p0_03|regulatory_concentration|0.459 | manual-reauthor |
| ATK_D08 | S0045 | 0.3243 | b3_58|position_sizing|0.324 | b5_79|execution_scheduling|0.298 | manual-reauthor |
| ATK_D09 | S0050 | 0.5136 | b3_51|risk_model|0.514 | b1_21|prime_brokerage_margin|0.508 | manual-reauthor |
| ATK_D10 | S0034 | 0.5018 | p0_03|regulatory_concentration|0.502 | b3_58|position_sizing|0.489 | manual-reauthor |
| ATK_I01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_I02 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | manual-reauthor |
| ATK_I03 | S0003 | 0.4837 | p0_13|stat_arb|0.484 | b3_47|execution_vwap|0.470 | manual-reauthor |
| ATK_I04 | S0005 | 0.5059 | b5_79|execution_scheduling|0.506 | b2_34|regulatory_concentration|0.502 | manual-reauthor |
| ATK_I05 | S0046 | 0.4948 | b1_24|portfolio_construction|0.495 | b2_43|portfolio_insurance|0.491 | manual-reauthor |
| ATK_I06 | S0018 | 0.3775 | b2_34|regulatory_concentration|0.377 | b3_58|position_sizing|0.361 | manual-reauthor |
| ATK_I07 | S0035 | 0.4632 | b1_24|portfolio_construction|0.463 | b5_83|credit_screening|0.441 | manual-reauthor |
| ATK_I08 | S0042 | 0.4341 | b4_69|stat_arb|0.434 | b3_58|position_sizing|0.431 | manual-reauthor |
| ATK_I09 | S0038 | 0.4890 | b1_24|portfolio_construction|0.489 | b1_28|position_sizing|0.475 | manual-reauthor |
| ATK_I10 | S0015 | 0.4085 | b2_33|market_making|0.408 | b2_31|settlement_ops|0.385 | manual-reauthor |
| ATK_P01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_P02 | S0008 | 0.4454 | p0_13|stat_arb|0.445 | b2_41|technical_indicator|0.402 | manual-reauthor |
| ATK_P03 | S0011 | 0.5079 | p0_03|regulatory_concentration|0.508 | b5_88|position_sizing|0.453 | manual-reauthor |
| ATK_P04 | S0030 | 0.3966 | b1_16|technical_indicator|0.397 | b5_81|factor_model|0.366 | manual-reauthor |
| ATK_P05 | S0031 | 0.4464 | b3_58|position_sizing|0.446 | b2_36|credit_screening|0.442 | manual-reauthor |
| ATK_SAL01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SAL02 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SAL03 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SAL04 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SAL05 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SAL06 | S0013 | 0.4708 | b1_29|portfolio_insurance|0.471 | p0_03|regulatory_concentration|0.459 | manual-reauthor |
| ATK_SAL07 | S0013 | 0.4708 | b1_29|portfolio_insurance|0.471 | p0_03|regulatory_concentration|0.459 | manual-reauthor |
| ATK_SAL08 | S0013 | 0.4708 | b1_29|portfolio_insurance|0.471 | p0_03|regulatory_concentration|0.459 | manual-reauthor |
| ATK_SAL09 | S0013 | 0.4708 | b1_29|portfolio_insurance|0.471 | p0_03|regulatory_concentration|0.459 | manual-reauthor |
| ATK_SE01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_SE02 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | manual-reauthor |
| ATK_SE03 | S0039 | 0.4797 | b5_76|regulatory_concentration|0.480 | p0_15|credit_screening|0.468 | manual-reauthor |
| ATK_SE04 | S0019 | 0.4131 | b2_43|portfolio_insurance|0.413 | b4_69|stat_arb|0.401 | manual-reauthor |
| ATK_SE05 | S0032 | 0.5272 | b1_24|portfolio_construction|0.527 | b1_21|prime_brokerage_margin|0.516 | manual-reauthor |
| ATK_ENC01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_ENC02 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | manual-reauthor |
| ATK_ENC03 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_ENC04 | S0050 | 0.5136 | b3_51|risk_model|0.514 | b1_21|prime_brokerage_margin|0.508 | manual-reauthor |
| ATK_PI05 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_HB01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_IND01 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_IND03 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | manual-reauthor |
| ATK_IND04 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_IND05 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | manual-reauthor |
| ATK_D11 | S0083 | 0.4331 | b2_38|portfolio_construction|0.433 | b1_28|position_sizing|0.412 | manual-reauthor |
| ATK_D12 | S0095 | 0.4641 | p0_03|regulatory_concentration|0.464 | p0_09|portfolio_construction|0.430 | manual-reauthor |
| ATK_D13 | S0105 | 0.4976 | p0_03|regulatory_concentration|0.498 | b2_35|risk_model|0.467 | manual-reauthor |
| ATK_D01_V1 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | rewrite |
| ATK_D01_V2 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | rewrite |
| ATK_D01_V3 | S0001 | 0.4978 | b5_78|execution_vwap|0.498 | p0_01|technical_indicator|0.475 | rewrite |
| ATK_D02_V1 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | rewrite |
| ATK_D02_V2 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | rewrite |
| ATK_D02_V3 | S0002 | 0.5041 | b3_58|position_sizing|0.504 | b2_34|regulatory_concentration|0.495 | rewrite |
| ATK_D03_V1 | S0003 | 0.4837 | p0_13|stat_arb|0.484 | b3_47|execution_vwap|0.470 | rewrite |
| ATK_D03_V2 | S0003 | 0.4837 | p0_13|stat_arb|0.484 | b3_47|execution_vwap|0.470 | rewrite |
| … | (+143 more in CSV) | | | | |

## ⚠️ Low top1 cosine (< 0.4) — weak/ambiguous mapping, human review (12)

| attack_id | orig_target | old_secret_brief | top1_cos | cand1 | triage |
|-----------|-------------|------------------|---------:|-------|--------|
| ATK_D08 | S0045 | strategy_logic / Alpha: Multi-Factor ML Signal | 0.3243 | b3_58|position_sizing|0.324 | manual-reauthor |
| ATK_D08_V1 | S0045 | strategy_logic / Alpha: Multi-Factor ML Signal | 0.3243 | b3_58|position_sizing|0.324 | rewrite |
| ATK_D08_V2 | S0045 | strategy_logic / Alpha: Multi-Factor ML Signal | 0.3243 | b3_58|position_sizing|0.324 | rewrite |
| ATK_D08_V3 | S0045 | strategy_logic / Alpha: Multi-Factor ML Signal | 0.3243 | b3_58|position_sizing|0.324 | rewrite |
| ATK_I06 | S0018 | strategy_logic / Alpha: Sentiment NLP Score | 0.3775 | b2_34|regulatory_concentration|0.377 | manual-reauthor |
| ATK_I06_V1 | S0018 | strategy_logic / Alpha: Sentiment NLP Score | 0.3775 | b2_34|regulatory_concentration|0.377 | rewrite |
| ATK_I06_V2 | S0018 | strategy_logic / Alpha: Sentiment NLP Score | 0.3775 | b2_34|regulatory_concentration|0.377 | rewrite |
| ATK_I06_V3 | S0018 | strategy_logic / Alpha: Sentiment NLP Score | 0.3775 | b2_34|regulatory_concentration|0.377 | rewrite |
| ATK_P04 | S0030 | strategy_logic / Alpha: Supply Chain Disruption | 0.3966 | b1_16|technical_indicator|0.397 | manual-reauthor |
| ATK_P04_V1 | S0030 | strategy_logic / Alpha: Supply Chain Disruption | 0.3966 | b1_16|technical_indicator|0.397 | rewrite |
| ATK_P04_V2 | S0030 | strategy_logic / Alpha: Supply Chain Disruption | 0.3966 | b1_16|technical_indicator|0.397 | rewrite |
| ATK_P04_V3 | S0030 | strategy_logic / Alpha: Supply Chain Disruption | 0.3966 | b1_16|technical_indicator|0.397 | rewrite |

## Next step (human, NOT done here)
- Ratify each row's triage; for `mechanical`, confirm the cand1 target + value swap; for `rewrite`/`manual-reauthor`, author against the chosen new secret. Only AFTER ratification does the actual retarget/rewrite (A-step proper) run.
