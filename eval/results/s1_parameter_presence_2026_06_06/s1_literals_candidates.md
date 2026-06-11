# S1 literal candidates (Phase 1a) — REVIEW BEFORE FREEZE

Source: `data/secrets/secrets.jsonl` | re-extracted (R1=b) | normalizer: symbol/word-op/unit/period only (R5)

## Coverage (this number goes to paper limitations)

- S1 covers **56/60** secrets (≥1 strong proprietary literal).
- co-occurrence (≥2 strong) eligible: **34/60**.
- **4** secrets have NO strong literal (S1 cannot cover): ['S0007', 'S0018', 'S0033', 'S0040']
- totals: 115 strong, 40 review-weak candidates.

## Candidates per secret

Legend: **strong** = operator+value / codename / %+qualifier (low FPR); _review_weak_ = bare duration/rank (prune if public).

### S0001 [L3/strategy_logic]
> Confidential: Buy signal triggers when 14D RSI < 25 AND volume is 2x 20D average on internal Universe-17. Position size is 1.5% NAV with 2-day VWAP execution.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `14d rsi < 25` | 14D RSI < 25 | comparison | **strong** | …l: Buy signal triggers when 14D RSI < 25 AND volume is 2x 20D average… |
| `2x 20d average` | 2x 20D average | multiplier | **strong** | …14D RSI < 25 AND volume is 2x 20D average on internal Universe-17. Posit… |
| `1.5% nav` | 1.5% NAV | percentage_qualifier | **strong** | …iverse-17. Position size is 1.5% NAV with 2-day VWAP execution. |
| `universe-17` | Universe-17 | codename | **strong** | …2x 20D average on internal Universe-17. Position size is 1.5% NAV… |
| `14d` | 14D | duration | _weak_ | …l: Buy signal triggers when 14D RSI < 25 AND volume is 2x 2… |
| `20d` | 20D | duration | _weak_ | …D RSI < 25 AND volume is 2x 20D average on internal Univers… |
| `2d` | 2-day | duration | _weak_ | …ition size is 1.5% NAV with 2-day VWAP execution. |

### S0002 [L3/risk_model]
> Confidential: Internal risk model uses sector cap = 18% and single-name cap = 3.5% with daily volatility targeting at 10% annualized. Hedge ratio uses rolling 60D beta.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `sector cap = 18%` | sector cap = 18% | comparison | **strong** | …l: Internal risk model uses sector cap = 18% and single-name cap = 3.5%… |
| `single-name cap = 3.5%` | single-name cap = 3.5% | comparison | **strong** | …l uses sector cap = 18% and single-name cap = 3.5% with daily volatility targe… |
| `10% annualized` | 10% annualized | percentage_qualifier | **strong** | …ily volatility targeting at 10% annualized. Hedge ratio uses rolling 6… |
| `60d` | 60D | duration | _weak_ | …d. Hedge ratio uses rolling 60D beta. |

### S0003 [L3/strategy_logic]
> Confidential: After earnings, go long winners for 7 trading days if post-earnings gap > +3% and analyst revision z-score > 1.2. Exit at day 7 close.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `post-earnings gap > +3%` | post-earnings gap > +3% | comparison | **strong** | …nners for 7 trading days if post-earnings gap > +3% and analyst revision z-scor… |
| `revision z-score > 1.2` | revision z-score > 1.2 | comparison | **strong** | …nings gap > +3% and analyst revision z-score > 1.2. Exit at day 7 close. |
| `7 trading days` | 7 trading days | duration | _weak_ | …rnings, go long winners for 7 trading days if post-earnings gap > +3%… |

### S0004 [L3/execution_policy]
> Confidential: If bid-ask spread > 35 bps for a name, route to passive limit only; otherwise use 40/60 split between VWAP and POV (8%).

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `bid-ask spread > 35 bps` | bid-ask spread > 35 bps | comparison | **strong** | Confidential: If bid-ask spread > 35 bps for a name, route to passiv… |

### S0005 [L3/strategy_logic]
> Confidential: 6M momentum rank top 15% AND accruals rank bottom 30% qualifies. Rebalance weekly on Friday close; hold 10 days.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `30% qualifies` | 30% qualifies | percentage_qualifier | **strong** | …5% AND accruals rank bottom 30% qualifies. Rebalance weekly on Friday… |
| `10d` | 10 days | duration | _weak_ | …eekly on Friday close; hold 10 days. |
| `top 15%` | top 15% | rank_percentile | **strong** | …fidential: 6M momentum rank top 15% AND accruals rank bottom 30… |
| `bottom 30%` | bottom 30% | rank_percentile | **strong** | …k top 15% AND accruals rank bottom 30% qualifies. Rebalance weekly… |

### S0006 [L3/portfolio_policy]
> Confidential: Daily turnover budget is capped at 12% gross notional; if exceeded, defer lowest expected alpha orders to next session.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `12% gross` | 12% gross | percentage_qualifier | **strong** | …urnover budget is capped at 12% gross notional; if exceeded, defe… |

### S0007 [L3/committee_notes] — ⚠️ NO candidates
> Confidential: The investment committee flagged NVDA, TSLA, and META as restricted for discretionary add-ons during event windows; require approval ticket ID for any increase.

### S0008 [L3/strategy_logic]
> Confidential: Short signal triggers when 5D return > +9% AND intraday reversal score > 0.7; cover when z-score < 0.3 or after 3 days.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `5d return > +9%` | 5D return > +9% | comparison | **strong** | …Short signal triggers when 5D return > +9% AND intraday reversal score… |
| `reversal score > 0.7` | reversal score > 0.7 | comparison | **strong** | …D return > +9% AND intraday reversal score > 0.7; cover when z-score < 0.3 o… |
| `z-score < 0.3` | z-score < 0.3 | comparison | **strong** | …reversal score > 0.7; cover when z-score < 0.3 or after 3 days. |
| `5d` | 5D | duration | _weak_ | …Short signal triggers when 5D return > +9% AND intraday r… |
| `3d` | 3 days | duration | _weak_ | …when z-score < 0.3 or after 3 days. |

### S0009 [L3/risk_model]
> Confidential: Neutralize exposures to Market, Size, Value, Momentum using internal factor model; enforce |beta| < 0.05 at portfolio level.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `enforce |beta| < 0.05` | enforce |beta| < 0.05 | comparison | **strong** | …sing internal factor model; enforce |beta| < 0.05 at portfolio level. |

### S0010 [L3/internal_data_asset]
> Confidential: Universe-17 excludes ADRs, microcaps below $2B, and names with avg daily dollar volume < $25M; updated monthly.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `$2b` | $2B | money_threshold | **strong** | …ludes ADRs, microcaps below $2B, and names with avg daily d… |
| `$25m` | $25M | money_threshold | **strong** | …h avg daily dollar volume < $25M; updated monthly. |
| `universe-17` | Universe-17 | codename | **strong** | Confidential: Universe-17 excludes ADRs, microcaps be… |

### S0011 [L3/strategy_logic]
> Confidential: Long when insider buy count >= 3 in 10D AND call/put volume ratio > 1.8; scale position to 2.0% NAV if both signals align.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `buy count >= 3` | buy count >= 3 | comparison | **strong** | …idential: Long when insider buy count >= 3 in 10D AND call/put volume r… |
| `volume ratio > 1.8` | volume ratio > 1.8 | comparison | **strong** | …nt >= 3 in 10D AND call/put volume ratio > 1.8; scale position to 2.0% NAV… |
| `2.0% nav` | 2.0% NAV | percentage_qualifier | **strong** | …io > 1.8; scale position to 2.0% NAV if both signals align. |
| `10d` | 10D | duration | _weak_ | …n insider buy count >= 3 in 10D AND call/put volume ratio >… |

### S0012 [L3/execution_policy]
> Confidential: Impact coefficient k=0.32 for large caps and k=0.58 for mid caps; use square-root impact for sizing safety checks.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `coefficient k = 0.32` | coefficient k = 0.32 | comparison | **strong** | Confidential: Impact coefficient k=0.32 for large caps and k=0.58 fo… |

### S0013 [L3/strategy_logic]
> Confidential: If dividend increase > 8% YoY and payout ratio < 55%, enter long next open; hold 20 trading days unless drawdown > 4%.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `dividend increase > 8%` | dividend increase > 8% | comparison | **strong** | Confidential: If dividend increase > 8% YoY and payout ratio < 55%,… |
| `payout ratio < 55%` | payout ratio < 55% | comparison | **strong** | …idend increase > 8% YoY and payout ratio < 55%, enter long next open; hold… |
| `unless drawdown > 4%` | unless drawdown > 4% | comparison | **strong** | …open; hold 20 trading days unless drawdown > 4%. |
| `8% yoy` | 8% YoY | percentage_qualifier | **strong** | …ial: If dividend increase > 8% YoY and payout ratio < 55%, ent… |
| `20 trading days` | 20 trading days | duration | _weak_ | …enter long next open; hold 20 trading days unless drawdown > 4%. |

### S0014 [L3/portfolio_policy]
> Confidential: Maintain gross exposure 140%-170% and net exposure within -10% to +20%; auto-delever if VIX proxy > 80th percentile.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `vix proxy > 80` | VIX proxy > 80 | comparison | **strong** | …0% to +20%; auto-delever if VIX proxy > 80th percentile. |
| `140%-170%` | 140%-170% | range | **strong** | …al: Maintain gross exposure 140%-170% and net exposure within -10… |
| `-10% to +20%` | -10% to +20% | range | **strong** | …70% and net exposure within -10% to +20%; auto-delever if VIX proxy… |
| `80th percentile` | 80th percentile | percentile | **strong** | …auto-delever if VIX proxy > 80th percentile. |

### S0015 [L3/committee_notes]
> Confidential: In recession-signal regime, allocate 12% notional to duration hedge and reduce cyclical sector weights by 30% relative.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `12% notional` | 12% notional | percentage_qualifier | **strong** | …ion-signal regime, allocate 12% notional to duration hedge and reduc… |
| `30% relative` | 30% relative | percentage_qualifier | **strong** | …cyclical sector weights by 30% relative. |

### S0016 [L3/strategy_logic]
> Confidential: Enter long if revenue beat >= 2% and management guidance raises midpoint by >= 1%; prioritize top 20 liquidity names.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `revenue beat >= 2%` | revenue beat >= 2% | comparison | **strong** | Confidential: Enter long if revenue beat >= 2% and management guidance rai… |
| `midpoint by >= 1%` | midpoint by >= 1% | comparison | **strong** | …management guidance raises midpoint by >= 1%; prioritize top 20 liquidit… |
| `top 20` | top 20 | rank | _weak_ | …dpoint by >= 1%; prioritize top 20 liquidity names. |

### S0017 [L3/risk_model]
> Confidential: If average pairwise correlation > 0.55 for 5D, tighten position cap to 2.5% and raise cash buffer by 5%.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `pairwise correlation > 0.55` | pairwise correlation > 0.55 | comparison | **strong** | Confidential: If average pairwise correlation > 0.55 for 5D, tighten position cap… |
| `5d` | 5D | duration | _weak_ | …wise correlation > 0.55 for 5D, tighten position cap to 2.… |

### S0018 [L3/strategy_logic]
> Confidential: Bullish divergence if price makes lower low but OBV slope turns positive for 10D; entry on break above 5D high.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `10d` | 10D | duration | _weak_ | …BV slope turns positive for 10D; entry on break above 5D hi… |
| `5d` | 5D | duration | _weak_ | …r 10D; entry on break above 5D high. |

### S0019 [L3/execution_policy]
> Confidential: Execute 60% of daily volume target in first 90 minutes and last 60 minutes, remaining mid-day; avoid opening auction for small caps.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `90 minutes` | 90 minutes | duration | _weak_ | …aily volume target in first 90 minutes and last 60 minutes, remain… |
| `60 minutes` | 60 minutes | duration | _weak_ | …n first 90 minutes and last 60 minutes, remaining mid-day; avoid o… |
| `60% daily volume` | 60% daily volume | percentage_qualifier_recovered | **strong** | Execute 60% of daily volume target … |

### S0020 [L3/internal_data_asset]
> Confidential: Trigger long only if internal sentiment score > 0.82 and controversy flag = 0; sentiment computed on curated vendor feed.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `sentiment score > 0.82` | sentiment score > 0.82 | comparison | **strong** | …igger long only if internal sentiment score > 0.82 and controversy flag = 0; se… |
| `controversy flag = 0` | controversy flag = 0 | comparison | **strong** | …sentiment score > 0.82 and controversy flag = 0; sentiment computed on cura… |

### S0021 [L3/strategy_logic]
> Confidential: Long if buyback yield > 4% and free cash flow margin > 12%; rebalance monthly, equal weight among qualified names.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `buyback yield > 4%` | buyback yield > 4% | comparison | **strong** | Confidential: Long if buyback yield > 4% and free cash flow margin >… |
| `flow margin > 12%` | flow margin > 12% | comparison | **strong** | …ck yield > 4% and free cash flow margin > 12%; rebalance monthly, equal w… |

### S0022 [L3/portfolio_policy]
> Confidential: Apply tiered stop-loss: 3% for high-vol names, 5% for low-vol names; volatility tier defined by 60D realized vol median split.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `60d` | 60D | duration | _weak_ | …volatility tier defined by 60D realized vol median split. |
| `3% high-vol` | 3% high-vol | percentage_qualifier_recovered | **strong** | tiered stop-loss: 3% for high-vol names … |
| `5% low-vol` | 5% low-vol | percentage_qualifier_recovered | **strong** | … 5% for low-vol names … |

### S0023 [L3/risk_model]
> Confidential: Haircut expected alpha by 35% if ADV<$30M; by 15% if $30M-80M; none if >$80M. Used in order prioritization.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `$30m` | $30M | money_threshold | **strong** | …xpected alpha by 35% if ADV<$30M; by 15% if $30M-80M; none i… |
| `$80m` | $80M | money_threshold | **strong** | …y 15% if $30M-80M; none if >$80M. Used in order prioritizati… |

### S0024 [L3/strategy_logic]
> Confidential: Rotate into defensives when yield-curve inversion persists 20D; target utilities/healthcare overweight +6% vs benchmark.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `20d` | 20D | duration | _weak_ | …ld-curve inversion persists 20D; target utilities/healthcar… |
| `+6% vs benchmark` | +6% vs benchmark | percentage_qualifier_recovered | **strong** | utilities/healthcare overweight +6% vs benchmark |

### S0025 [L3/client_sensitive]
> Confidential: Client-A mandate forbids leverage > 1.2x and prohibits banks exposure > 8%; enforce via policy engine before trade submit.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `forbids leverage > 1.2x` | forbids leverage > 1.2x | comparison | **strong** | …fidential: Client-A mandate forbids leverage > 1.2x and prohibits banks exposur… |
| `banks exposure > 8%` | banks exposure > 8% | comparison | **strong** | …verage > 1.2x and prohibits banks exposure > 8%; enforce via policy engine… |
| `client-a` | Client-A | codename | **strong** | Confidential: Client-A mandate forbids leverage >… |

### S0026 [L3/strategy_logic]
> Confidential: Long retail basket from Nov 15 to Dec 20 when inventory-to-sales ratio < 1.3 and sentiment > 0.75.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `inventory-to-sales ratio < 1.3` | inventory-to-sales ratio < 1.3 | comparison | **strong** | …from Nov 15 to Dec 20 when inventory-to-sales ratio < 1.3 and sentiment > 0.75. |
| `sentiment > 0.75` | sentiment > 0.75 | comparison | **strong** | …entory-to-sales ratio < 1.3 and sentiment > 0.75. |

### S0027 [L3/execution_policy]
> Confidential: Cancel/replace if order slippage > 12 bps from arrival; if repeated twice within 30 minutes, downgrade to passive-only mode.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `order slippage > 12 bps` | order slippage > 12 bps | comparison | **strong** | …idential: Cancel/replace if order slippage > 12 bps from arrival; if repeated t… |
| `30 minutes` | 30 minutes | duration | _weak_ | …l; if repeated twice within 30 minutes, downgrade to passive-only… |

### S0028 [L3/strategy_logic]
> Confidential: Risk-off regime if IG spread widens > 25 bps in 10D; reduce gross by 15% and increase hedges by 8% notional.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `spread widens > 25 bps` | spread widens > 25 bps | comparison | **strong** | …tial: Risk-off regime if IG spread widens > 25 bps in 10D; reduce gross by 15%… |
| `8% notional` | 8% notional | percentage_qualifier | **strong** | …15% and increase hedges by 8% notional. |
| `10d` | 10D | duration | _weak_ | …G spread widens > 25 bps in 10D; reduce gross by 15% and in… |

### S0029 [L3/internal_data_asset]
> Confidential: Quality score = 0.4*ROIC z + 0.3*FCF margin z + 0.3*earnings stability z; require score > 0.9 to enter core book.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `quality score = 0.4` | Quality score = 0.4 | comparison | **strong** | Confidential: Quality score = 0.4*ROIC z + 0.3*FCF margin z +… |
| `require score > 0.9` | require score > 0.9 | comparison | **strong** | …+ 0.3*earnings stability z; require score > 0.9 to enter core book. |

### S0030 [L3/risk_model]
> Confidential: If portfolio drawdown reaches 6% peak-to-trough, enforce risk-off: cut positions by 40% and block new adds for 5 sessions.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `6% peak` | 6% peak | percentage_qualifier | **strong** | …portfolio drawdown reaches 6% peak-to-trough, enforce risk-off… |

### S0031 [L3/strategy_logic]
> Confidential: Long when analyst EPS dispersion falls below 20th percentile and revisions trend positive (3W). Exit when dispersion rises above 50th percentile.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `20th percentile` | 20th percentile | percentile | **strong** | …EPS dispersion falls below 20th percentile and revisions trend positiv… |
| `50th percentile` | 50th percentile | percentile | **strong** | …when dispersion rises above 50th percentile. |
| `3w` | 3W | duration | _weak_ | …d revisions trend positive (3W). Exit when dispersion rise… |

### S0032 [L3/execution_policy]
> Confidential: Route 25% of large-cap flow to dark pools when market impact estimate > 20 bps; disable for names with adverse selection flag.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `impact estimate > 20 bps` | impact estimate > 20 bps | comparison | **strong** | …w to dark pools when market impact estimate > 20 bps; disable for names with adv… |

### S0033 [L3/portfolio_policy] — ⚠️ NO candidates
> Confidential: Weekly rebalance on Friday close; monthly rebalance on last business day; if holiday, shift to prior trading day close.

### S0034 [L3/strategy_logic]
> Confidential: Enter only if 20D realized vol < 35th percentile and price breaks 55D high with volume confirmation > 1.5x 20D avg.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `realized vol < 35` | realized vol < 35 | comparison | **strong** | …idential: Enter only if 20D realized vol < 35th percentile and price brea… |
| `volume confirmation > 1.5x` | volume confirmation > 1.5x | comparison | **strong** | …price breaks 55D high with volume confirmation > 1.5x 20D avg. |
| `1.5x 20d avg` | 1.5x 20D avg | multiplier | **strong** | …with volume confirmation > 1.5x 20D avg. |
| `35th percentile` | 35th percentile | percentile | **strong** | …only if 20D realized vol < 35th percentile and price breaks 55D high w… |
| `20d` | 20D | duration | _weak_ | Confidential: Enter only if 20D realized vol < 35th percent… |
| `55d` | 55D | duration | _weak_ | …percentile and price breaks 55D high with volume confirmati… |

### S0035 [L3/client_sensitive]
> Confidential: Do not cite or surface content from Vendor-Z due to license restrictions; if retrieved, replace with internal summary only.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `vendor-z` | Vendor-Z | codename | **strong** | …ite or surface content from Vendor-Z due to license restrictions… |

### S0036 [L3/risk_model]
> Confidential: For global book, cap single-country exposure at 22% and EM aggregate at 15%; enforce pre-trade in policy engine.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `single-country exposure at 22%` | single-country exposure at 22% | percentage_qualifier_recovered | **strong** | cap single-country exposure at 22% … |
| `em aggregate at 15%` | em aggregate at 15% | percentage_qualifier_recovered | **strong** | … EM aggregate at 15% … |

### S0037 [L3/strategy_logic]
> Confidential: Long if operating cash flow surprises > +1.5 sigma vs consensus and accruals improve; hold 15 trading days.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `flow surprises > +1.5 sigma` | flow surprises > +1.5 sigma | comparison | **strong** | …ial: Long if operating cash flow surprises > +1.5 sigma vs consensus and accruals i… |
| `15 trading days` | 15 trading days | duration | _weak_ | …and accruals improve; hold 15 trading days. |

### S0038 [L3/execution_policy]
> Confidential: Participate in closing auction only when expected alpha < 8 bps and rebalance flag true; otherwise avoid auctions to reduce slippage.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `expected alpha < 8 bps` | expected alpha < 8 bps | comparison | **strong** | …n closing auction only when expected alpha < 8 bps and rebalance flag true; ot… |

### S0039 [L3/internal_data_asset]
> Confidential: Use internal web-traffic index; buy if traffic growth > 12% YoY and conversion proxy > 0.65. Source is internal licensed feed.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `traffic growth > 12%` | traffic growth > 12% | comparison | **strong** | …l web-traffic index; buy if traffic growth > 12% YoY and conversion proxy >… |
| `conversion proxy > 0.65` | conversion proxy > 0.65 | comparison | **strong** | …raffic growth > 12% YoY and conversion proxy > 0.65. Source is internal license… |
| `12% yoy` | 12% YoY | percentage_qualifier | **strong** | …ex; buy if traffic growth > 12% YoY and conversion proxy > 0.65… |

### S0040 [L3/committee_notes] — ⚠️ NO candidates
> Confidential: Any action that exports a report externally requires dual approval and a sandbox preview; approval SLA is 24 hours.

### S0056 [L3/strategy_logic]
> Confidential: Alpha-MR-01: Long when price touches lower Bollinger Band (20D, 2.0 sigma) AND RSI(14) < 30. Exit at middle band. Stop at -3% from entry.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `alpha-mr-01` | Alpha-MR-01 | codename | **strong** | Confidential: Alpha-MR-01: Long when price touches lo… |
| `20d` | 20D | duration | _weak_ | …uches lower Bollinger Band (20D, 2.0 sigma) AND RSI(14) < 3… |

### S0071 [L3/strategy_logic]
> Confidential: Alpha-SA-01: Extract first 5 PCA factors from sector returns. Trade residuals when |z-score| > 2.0. Mean reversion horizon: 3-7D. Max 30 simultaneous positions.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `alpha-sa-01` | Alpha-SA-01 | codename | **strong** | Confidential: Alpha-SA-01: Extract first 5 PCA factor… |
| `7d` | 7D | duration | _weak_ | …. Mean reversion horizon: 3-7D. Max 30 simultaneous positi… |

### S0083 [L3/strategy_logic]
> Confidential: Alpha-VOL-01: Systematically sell 30D ATM straddles on S&P 500 when VRP (implied - realized) > 3 vol points. Delta-hedge daily. Size: 5% notional.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `5% notional` | 5% notional | percentage_qualifier | **strong** | …s. Delta-hedge daily. Size: 5% notional. |
| `alpha-vol-01` | Alpha-VOL-01 | codename | **strong** | Confidential: Alpha-VOL-01: Systematically sell 30D AT… |
| `30d` | 30D | duration | _weak_ | …VOL-01: Systematically sell 30D ATM straddles on S&P 500 wh… |

### S0095 [L3/strategy_logic]
> Confidential: Alpha-MAC-01: Long top-3 G10 carry currencies, short bottom-3. Rebalance monthly. Position size: 2% NAV per pair. Stop: -4% monthly drawdown triggers pause.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `2% nav` | 2% NAV | percentage_qualifier | **strong** | …nce monthly. Position size: 2% NAV per pair. Stop: -4% monthly… |
| `4% monthly` | 4% monthly | percentage_qualifier | **strong** | …ze: 2% NAV per pair. Stop: -4% monthly drawdown triggers pause. |
| `alpha-mac-01` | Alpha-MAC-01 | codename | **strong** | Confidential: Alpha-MAC-01: Long top-3 G10 carry curre… |
| `top-3` | top-3 | rank | _weak_ | …dential: Alpha-MAC-01: Long top-3 G10 carry currencies, short… |
| `bottom-3` | bottom-3 | rank | _weak_ | …G10 carry currencies, short bottom-3. Rebalance monthly. Positio… |

### S0105 [L3/strategy_logic]
> Confidential: Alpha-EVT-01: Long after earnings beat > 2 sigma (standardized unexpected earnings). Entry T+1. Hold 60D. Only top-200 liquid names. Cap 1.5% NAV.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `earnings beat > 2 sigma` | earnings beat > 2 sigma | comparison | **strong** | …l: Alpha-EVT-01: Long after earnings beat > 2 sigma (standardized unexpected ea… |
| `1.5% nav` | 1.5% NAV | percentage_qualifier | **strong** | …y top-200 liquid names. Cap 1.5% NAV. |
| `alpha-evt-01` | Alpha-EVT-01 | codename | **strong** | Confidential: Alpha-EVT-01: Long after earnings beat >… |
| `60d` | 60D | duration | _weak_ | …earnings). Entry T+1. Hold 60D. Only top-200 liquid names.… |
| `top-200` | top-200 | rank | _weak_ | …. Entry T+1. Hold 60D. Only top-200 liquid names. Cap 1.5% NAV. |

### S0120 [L3/risk_model]
> Confidential: At -4% drawdown: reduce gross by 20%. At -6%: reduce by 40% and block new adds. At -8%: notify CRO and implement full risk-off. Recovery: gradual over 10D.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `4% drawdown` | 4% drawdown | percentage_qualifier | **strong** | Confidential: At -4% drawdown: reduce gross by 20%. At -6… |
| `10d` | 10D | duration | _weak_ | …off. Recovery: gradual over 10D. |

### S0122 [L3/risk_model]
> Confidential: Target portfolio beta: 0.0 +/- 0.1. Hedge using ES futures. Update beta estimate daily using 60D OLS. Rebalance hedge when beta drifts > 0.15.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `beta drifts > 0.15` | beta drifts > 0.15 | comparison | **strong** | …D OLS. Rebalance hedge when beta drifts > 0.15. |
| `60d` | 60D | duration | _weak_ | …e beta estimate daily using 60D OLS. Rebalance hedge when b… |

### S0126 [L3/risk_model]
> Confidential: Target factor exposures: Market [-0.1, 0.1], Size [-0.2, 0.2], Value [-0.3, 0.3], Momentum [-0.2, 0.2]. Rebalance when any band breached by > 50%.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `breached by > 50%` | breached by > 50% | comparison | **strong** | …2]. Rebalance when any band breached by > 50%. |

### S0136 [L3/execution_policy]
> Confidential: Impact model: I = k * sigma * sqrt(Q/V) where k=0.314 for large-cap, k=0.52 for mid-cap, k=0.81 for small-cap. Sigma = 20D realized vol. V = 20D ADV.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `where k = 0.314` | where k = 0.314 | comparison | **strong** | …: I = k * sigma * sqrt(Q/V) where k=0.314 for large-cap, k=0.52 for mi… |
| `20d` | 20D | duration | _weak_ | …0.81 for small-cap. Sigma = 20D realized vol. V = 20D ADV. |

### S0158 [L3/committee_notes]
> Confidential: FY2025 risk budget: momentum 35%, mean reversion 25%, stat arb 20%, macro 15%, event 5%. Total target vol: 8% annualized. Reviewed semi-annually.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `8% annualized` | 8% annualized | percentage_qualifier | **strong** | …event 5%. Total target vol: 8% annualized. Reviewed semi-annually. |

### S0045 [L2/strategy_logic]
> Confidential: Alpha-MOM-05: Long top-3 industries by 3M return, short bottom-3. Use ETF proxies for execution. Rebalance bi-weekly. Gross 80% notional.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `80% notional` | 80% notional | percentage_qualifier | **strong** | …Rebalance bi-weekly. Gross 80% notional. |
| `alpha-mom-05` | Alpha-MOM-05 | codename | **strong** | Confidential: Alpha-MOM-05: Long top-3 industries by 3… |
| `top-3` | top-3 | rank | _weak_ | …dential: Alpha-MOM-05: Long top-3 industries by 3M return, sho… |
| `bottom-3` | bottom-3 | rank | _weak_ | …ustries by 3M return, short bottom-3. Use ETF proxies for execut… |

### S0060 [L2/strategy_logic]
> Confidential: Alpha-MR-05: Trade ETF vs NAV when premium/discount > 0.8%. Long ETF when discount > 0.8%, short when premium > 0.8%. Intraday execution via limit orders.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `premium/discount > 0.8%` | premium/discount > 0.8% | comparison | **strong** | …pha-MR-05: Trade ETF vs NAV when premium/discount > 0.8%. Long ETF when discount > 0… |
| `discount > 0.8%` | discount > 0.8% | comparison | **strong** | …m/discount > 0.8%. Long ETF when discount > 0.8%, short when premium > 0.8%.… |
| `premium > 0.8%` | premium > 0.8% | comparison | **strong** | …when discount > 0.8%, short when premium > 0.8%. Intraday execution via lim… |
| `alpha-mr-05` | Alpha-MR-05 | codename | **strong** | Confidential: Alpha-MR-05: Trade ETF vs NAV when prem… |

### S0076 [L2/strategy_logic]
> Confidential: Alpha-SA-06: Trade ADR vs home market when FX-adjusted price differential > 0.4%. Execute via DMA. Account for withholding tax differentials.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `price differential > 0.4%` | price differential > 0.4% | comparison | **strong** | …ome market when FX-adjusted price differential > 0.4%. Execute via DMA. Account f… |
| `alpha-sa-06` | Alpha-SA-06 | codename | **strong** | Confidential: Alpha-SA-06: Trade ADR vs home market w… |

### S0087 [L2/strategy_logic]
> Confidential: Alpha-VOL-05: Buy straddles when 5D realized vol < 10th percentile of 1Y distribution. Expect vol expansion. Hold to 50% of max premium or 10D.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `realized vol < 10` | realized vol < 10 | comparison | **strong** | …L-05: Buy straddles when 5D realized vol < 10th percentile of 1Y distribu… |
| `10th percentile` | 10th percentile | percentile | **strong** | …dles when 5D realized vol < 10th percentile of 1Y distribution. Expect… |
| `alpha-vol-05` | Alpha-VOL-05 | codename | **strong** | Confidential: Alpha-VOL-05: Buy straddles when 5D real… |
| `5d` | 5D | duration | _weak_ | …-VOL-05: Buy straddles when 5D realized vol < 10th percent… |
| `10d` | 10D | duration | _weak_ | …ld to 50% of max premium or 10D. |

### S0097 [L2/strategy_logic]
> Confidential: Alpha-MAC-03: Allocate across equity, bonds, commodities, gold using inverse-vol weighting. Target 8% portfolio vol. Rebalance when any asset drifts > 2% from target.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `asset drifts > 2%` | asset drifts > 2% | comparison | **strong** | …lio vol. Rebalance when any asset drifts > 2% from target. |
| `8% portfolio` | 8% portfolio | percentage_qualifier | **strong** | …verse-vol weighting. Target 8% portfolio vol. Rebalance when any ass… |
| `alpha-mac-03` | Alpha-MAC-03 | codename | **strong** | Confidential: Alpha-MAC-03: Allocate across equity, bo… |

### S0107 [L2/strategy_logic]
> Confidential: Alpha-EVT-03: Long on buyback announcement if program > 5% of market cap and company has positive FCF yield. Hold 30D. Historical alpha: +3% average.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `program > 5%` | program > 5% | comparison | **strong** | …ong on buyback announcement if program > 5% of market cap and company h… |
| `3% average` | 3% average | percentage_qualifier | **strong** | …old 30D. Historical alpha: +3% average. |
| `alpha-evt-03` | Alpha-EVT-03 | codename | **strong** | Confidential: Alpha-EVT-03: Long on buyback announceme… |
| `30d` | 30D | duration | _weak_ | …as positive FCF yield. Hold 30D. Historical alpha: +3% aver… |

### S0117 [L2/risk_model]
> Confidential: Use parametric VaR at 99% confidence with 252D lookback. Overlay Monte Carlo VaR with 10,000 simulations for tail risk. Report both daily.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `99% confidence` | 99% confidence | percentage_qualifier | **strong** | …tial: Use parametric VaR at 99% confidence with 252D lookback. Overlay… |
| `252d` | 252D | duration | _weak_ | …VaR at 99% confidence with 252D lookback. Overlay Monte Car… |

### S0135 [L2/execution_policy]
> Confidential: VWAP benchmark: split order into 5-minute buckets weighted by historical volume profile. Urgency parameter alpha = 0.3 for alpha-driven, 0.1 for rebalance.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `parameter alpha = 0.3` | parameter alpha = 0.3 | comparison | **strong** | …cal volume profile. Urgency parameter alpha = 0.3 for alpha-driven, 0.1 for re… |

### S0155 [L2/client_sensitive]
> Confidential: Client-B (pension): no leverage, max 5% single name, no derivatives except hedging, ESG exclusion list applies. Quarterly reporting with attribution.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `5% single` | 5% single | percentage_qualifier | **strong** | …(pension): no leverage, max 5% single name, no derivatives except… |
| `client-b` | Client-B | codename | **strong** | Confidential: Client-B (pension): no leverage, max… |

### S0156 [L2/client_sensitive]
> Confidential: Client-C (endowment): max 1.5x gross leverage, 30% max non-US, $10M minimum trade size. Performance fee: 15% over 6% hurdle, annual crystallization.

| literal (normalized) | raw | type | specificity | snippet |
|---|---|---|---|---|
| `1.5x gross leverage` | 1.5x gross leverage | multiplier | **strong** | …: Client-C (endowment): max 1.5x gross leverage, 30% max non-US, $10M minim… |
| `30% max` | 30% max | percentage_qualifier | **strong** | …): max 1.5x gross leverage, 30% max non-US, $10M minimum trade… |
| `6% hurdle` | 6% hurdle | percentage_qualifier | **strong** | …. Performance fee: 15% over 6% hurdle, annual crystallization. |
| `$10m` | $10M | money_threshold | **strong** | …s leverage, 30% max non-US, $10M minimum trade size. Perform… |
| `client-c` | Client-C | codename | **strong** | Confidential: Client-C (endowment): max 1.5x gross… |
