# Phase 1.E E1.3.6 — Outlier Inventory (V1a + V1b + V5b)

> **Status:** E1.3.6 outlier consolidation across all three Phase 1.E
> validators (V1a MiniLM, V1b multi-encoder, V5b exact-match). Drop
> decisions are **deferred to E1.4 regeneration phase**; this document
> is a forensic inventory, not a drop list.
>
> **Inputs (authoritative):**
> - `v1a_20260522T013349Z.json` — V1a canonical (12 outliers)
> - `v1b_20260523T045118Z.json` — V1b + V5b merged canonical
>   (14 mpnet + 0 bge_large + 4 finlang outliers; 0 V5b hits)
> - `r6_audit.jsonl` — R6 audit log (4 Layer 5 paraphrase signatures)
> - `hard_negatives_seeds_draft.jsonl` — 65 entries with all
>   V1a/V1b/V5b fields populated

---

## §1 — Executive Summary

Across 65 hard-negative entries, **23 unique entries (35.4%)** were
flagged by at least one validator stage. The complement (42/65 = 64.6%)
passed all V1a + V1b + V5b BLOCKING checks — matching the
`all_blocking_pass` cross-encoder agreement rate from S10.

| Validator stage | Outliers | Rate | Notes |
| --- | --- | --- | --- |
| V1a (MiniLM BLOCKING, [0.40, 0.65]) | **12** | 18.5% | 10 below + 2 above-band |
| V1b mpnet ([0.07, 0.52]) | **14** | 21.5% | All above-band (cos > 0.52) |
| V1b bge_large ([0.45, 0.90]) | **0** | 0.0% | S9 null result; band too permissive |
| V1b finlang ([0.20, 0.65]) | **4** | 6.2% | All above-band (cos > 0.65) |
| V5b exact-string match | **0** | 0.0% | S12 null result; Layer 1 prompt template held |
| **Layer 5 paraphrase signatures (≥2 encoders above-band)** | **4** | 6.2% | Logged in r6_audit.jsonl |
| **Union (unique entries flagged)** | **23** | **35.4%** | matches 1 − all_blocking_pass (S10) |

Per-source breakdown: **12/30 manual seeds (40.0%)** vs **11/35
LLM-generated (31.4%)** were flagged at least once. This is a less
asymmetric profile than V1a alone (where the SEED-vs-GEN gap was 26.7%
vs 5.7% on below-band failures); V1b's above-band failures (mostly
LLM-generated Cat D/E) close the gap because the audit framework's
domain-vocabulary scaffolding pushes generated queries higher into
the cosine distribution.

Per-category breakdown of the 23 unique outliers:

| Cat | Outliers | Total | Rate |
| --- | --- | --- | --- |
| A | 5 | 15 | 33.3% |
| B | 3 | 10 | 30.0% |
| C | 2 | 10 | 20.0% |
| **D** | **7** | 10 | **70.0%** ← S11 multi-encoder concentration |
| **E** | **4** | 10 | **40.0%** ← S11 multi-encoder concentration |
| F | 2 | 10 | 20.0% |

---

## §2 — V1a Outliers (12 entries from MiniLM BLOCKING)

Source: `v1a_20260522T013349Z.json`. Direction relative to global
BLOCKING band [0.40, 0.65].

### §2.1 — Below-band (n=10; cosine < 0.40)

Predominantly **cross-domain spillover** (S1): 8/10 below-band
entries map via MiniLM top-1 to a v2 secret in a *different* alpha
domain than the hard-neg's authored domain.

| `_id` | cat | src | cos | hn_domain | sec_domain | same-domain? |
| --- | --- | --- | --- | --- | --- | --- |
| HN_SEED_004 | A | SEED | 0.368 | alternative_data | alternative_data | Y |
| HN_SEED_006 | B | SEED | 0.384 | event_driven | statistical_arbitrage | N |
| HN_SEED_007 | B | SEED | **0.315** | statistical_arbitrage | event_driven | N |
| HN_SEED_010 | B | SEED | 0.399 | ml_signals | factor_neutral | N |
| HN_SEED_013 | C | SEED | 0.399 | alternative_data | factor_neutral | N |
| HN_SEED_019 | D | SEED | 0.396 | alternative_data | statistical_arbitrage | N |
| HN_SEED_025 | E | SEED | 0.398 | ml_signals | ml_signals | Y |
| HN_SEED_028 | F | SEED | 0.382 | alternative_data | event_driven | N |
| HN_GEN_039 | C | GEN | 0.339 | event_driven | statistical_arbitrage | N |
| HN_GEN_062 | F | GEN | 0.382 | statistical_arbitrage | factor_neutral | N |

**Cross-references:** S1 (cross-domain spillover), S2 (E1.1 vs E1.2
asymmetry — 8/10 are SEED).

### §2.2 — Above-band (n=2; cosine > 0.65)

| `_id` | cat | src | cos | hn_domain | sec_domain | Action 1a verdict |
| --- | --- | --- | --- | --- | --- | --- |
| HN_GEN_051 | D | GEN | 0.678 | factor_neutral | factor_neutral | NON-paraphrase (mechanism vs system) |
| HN_GEN_056 | E | GEN | 0.678 | alternative_data | alternative_data | NON-paraphrase (comparison vs combined-strategy) |

Both Action 1a content-reviewed (2026-05-21); ruled non-paraphrase.
**Cross-references:** S11 (Cat D/E concentration), R6_AUDIT_002/003
(Layer 5 paraphrase signatures, disposition retained).

---

## §3 — V1b Outliers (mpnet 14 / bge_large 0 / finlang 4)

Source: `v1b_20260523T045118Z.json` per-encoder outlier blocks. All
V1b outliers are **above-band** (no below-band failures on any
secondary encoder).

### §3.1 — mpnet (n=14; cosine > 0.52)

| `_id` | cat | src | cos | also-flagged-in |
| --- | --- | --- | --- | --- |
| HN_SEED_003 | A | SEED | 0.525 | (mpnet only) |
| HN_SEED_013 | C | SEED | 0.571 | V1a (below; opposite-direction) |
| HN_SEED_016 | D | SEED | 0.668 | finlang, Layer 5 |
| HN_SEED_017 | D | SEED | 0.658 | (mpnet only) |
| HN_SEED_021 | E | SEED | 0.581 | (mpnet only) |
| HN_GEN_033 | A | GEN | 0.542 | (mpnet only) |
| HN_GEN_034 | A | GEN | 0.532 | (mpnet only) |
| HN_GEN_043 | A | GEN | 0.540 | (mpnet only) |
| **HN_GEN_051** | D | GEN | 0.650 | V1a (above), finlang, Layer 5 |
| HN_GEN_053 | D | GEN | 0.567 | (mpnet only) |
| HN_GEN_054 | D | GEN | 0.612 | (mpnet only) |
| HN_GEN_055 | D | GEN | 0.527 | (mpnet only) |
| **HN_GEN_056** | E | GEN | 0.687 | V1a (above), finlang, Layer 5 |
| **HN_GEN_059** | E | GEN | 0.650 | finlang, Layer 5 |

By category: **D=6, A=4, E=3, C=1, B=0, F=0** (S11 multi-encoder
concentration confirmed).

**Critical context (S8):** mpnet's observed mean (0.4725) exceeds
V2 §2.5 predicted midpoint (0.295) by **+0.18**, triggering V2 §4.4
substantial-deviation V2.5 plan revision. The 14 mpnet outliers are
all in (0.52, 0.69); a re-anchored band (e.g., [0.39, 0.58]) would
reduce outliers to ~9. **Per Q1 ruling, no post-hoc re-anchor — the
prediction-miss is itself a paper finding (S8).**

### §3.2 — bge_large (n=0)

**Null result.** All 65 entries pass bge_large's [0.45, 0.90] window;
observed mean 0.7034 (P10=0.6408, P90=0.7909) sits well-centered.

**Cross-references:** S9 (bge_large band permissiveness). The widest
predicted band catches the most hard-negs; V2.5 may consider
tightening to [0.60, 0.80].

### §3.3 — finlang (n=4; cosine > 0.65)

| `_id` | cat | src | cos | also-flagged-in |
| --- | --- | --- | --- | --- |
| HN_SEED_016 | D | SEED | 0.665 | mpnet, Layer 5 |
| **HN_GEN_051** | D | GEN | 0.677 | V1a (above), mpnet, Layer 5 |
| **HN_GEN_056** | E | GEN | 0.703 | V1a (above), mpnet, Layer 5 |
| **HN_GEN_059** | E | GEN | 0.656 | mpnet, Layer 5 |

All 4 finlang outliers are **also mpnet outliers** — finlang ⊂ mpnet
in this corpus. Domain concentration: D=2, E=2, others=0 (S11).

---

## §4 — V5b Outliers (n=0; clean null result)

**Source:** `v1b_20260523T045118Z.json` (V5b section merged).
**Coverage:** 65 hard-negs × 150 secrets (60 legacy + 90 v2
canonical) × 2 fields (query + rationale) = ~19,500 STRICT
character-equality comparisons.

**Result:** 0 hits across all comparison axes.

**Cross-reference:** S12 (V5b confirms zero corpus contamination).
Layer 1 prompt template constraints (V2 §7.2) held — corpus-
generation LLM did not emit verbatim secret content, and no manual
seed author paraphrased secret content into the rationale field.

---

## §5 — Layer 5 Paraphrase Signatures (n=4 in R6 audit log)

**Source:** `r6_audit.jsonl` per V2 §7.2 Layer 5. Criterion: ≥2 of
4 encoders flag the entry as above-band simultaneously (paraphrase
signature). Layer 5 is **forensic logging, not a BLOCKING gate** —
candidates remain in corpus pending disposition.

| `audit_id` | hard-neg | cat | above-band encoders | n | disposition |
| --- | --- | --- | --- | --- | --- |
| R6_AUDIT_001 | HN_SEED_016 | D | mpnet, finlang | 2 | **requires_content_review_at_E1_4** |
| R6_AUDIT_002 | HN_GEN_051 | D | minilm, mpnet, finlang | 3 | **retained_non_paraphrase** (Action 1a) |
| R6_AUDIT_003 | HN_GEN_056 | E | minilm, mpnet, finlang | 3 | **retained_non_paraphrase** (Action 1a) |
| R6_AUDIT_004 | HN_GEN_059 | E | mpnet, finlang | 2 | **requires_content_review_at_E1_4** |

**Notable:** bge_large does NOT contribute to any Layer 5 signature
(S9 band-permissiveness). The 2-of-4 threshold is satisfied entirely
by {minilm, mpnet, finlang} combinations.

**Cross-references:** S11 (Cat D/E concentration), S12 (Layer 5
distinct from Layer 2; CANDIDATES not CONFIRMED).

---

## §6 — Overlap Analysis (multi-validator flagging)

### §6.1 — Pairwise intersections

| Overlap | Entries | n |
| --- | --- | --- |
| V1a ∩ V1b mpnet | HN_SEED_013, HN_GEN_051, HN_GEN_056 | 3 |
| V1a ∩ V1b finlang | HN_GEN_051, HN_GEN_056 | 2 |
| V1b mpnet ∩ V1b finlang | HN_SEED_016, HN_GEN_051, HN_GEN_056, HN_GEN_059 | 4 |
| V1a ∩ V1b mpnet ∩ V1b finlang | HN_GEN_051, HN_GEN_056 | 2 |
| Any-V1 ∩ V5b | — | 0 |

### §6.2 — Flag-count distribution (per outlier)

| Flag count | Entries | IDs |
| --- | --- | --- |
| Flagged by 1 validator stage | 18 | (12 V1a-only + 0 above; 5 mpnet-only; 1 finlang-only after subtractions) — see §7 disposition table |
| Flagged by 2 validator stages | 3 | HN_SEED_013 (V1a below + mpnet above; opposite-direction), HN_SEED_016 (mpnet + finlang), HN_GEN_059 (mpnet + finlang) |
| Flagged by 3 validator stages | 2 | HN_GEN_051 (V1a + mpnet + finlang), HN_GEN_056 (V1a + mpnet + finlang) |
| Flagged by all 4 (incl. V5b) | 0 | (V5b is null) |

### §6.3 — Direction analysis on multi-flag entries

| `_id` | V1a direction | mpnet direction | finlang direction | Diagnosis |
| --- | --- | --- | --- | --- |
| HN_SEED_013 | below (0.399) | above (0.571) | (in-band) | **opposite-direction**; cross-domain spillover (S1) on MiniLM, vocab-overlap on mpnet — NOT paraphrase |
| HN_GEN_051 | above (0.678) | above (0.650) | above (0.677) | **co-directional above** across 3 encoders; Action 1a confirmed non-paraphrase (S11) |
| HN_GEN_056 | above (0.678) | above (0.687) | above (0.703) | **co-directional above** across 3 encoders; Action 1a confirmed non-paraphrase (S11) |
| HN_SEED_016 | in-band (0.586) | above (0.668) | above (0.665) | 2-encoder above; awaiting content review |
| HN_GEN_059 | in-band (0.558) | above (0.650) | above (0.656) | 2-encoder above; awaiting content review |

---

## §7 — Disposition Matrix (all 23 unique outliers)

Drop decisions are **deferred to E1.4 regeneration phase**, per V1a
Option B precedent and V1b STRICT-with-paper-escalation Q1 ruling
(no per-encoder fail rate ≥30%; aggregate-of-3-secondary 21.5% also
below threshold).

| `_id` | cat | src | V1a | mpnet | bge | finlang | Layer5 | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HN_SEED_003 | A | SEED | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_SEED_004 | A | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_006 | B | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_007 | B | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_010 | B | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_013 | C | SEED | ✓ below | ✓ | — | — | — | defer_to_E1_4 (opposite-dir; not paraphrase) |
| HN_SEED_016 | D | SEED | — | ✓ | — | ✓ | ✓ | **requires_content_review_at_E1_4** |
| HN_SEED_017 | D | SEED | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_SEED_019 | D | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_021 | E | SEED | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_SEED_025 | E | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_SEED_028 | F | SEED | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_GEN_033 | A | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_034 | A | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_039 | C | GEN | ✓ below | — | — | — | — | defer_to_E1_4 |
| HN_GEN_043 | A | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_051 | D | GEN | ✓ above | ✓ | — | ✓ | ✓ | **retained_non_paraphrase** (Action 1a) |
| HN_GEN_053 | D | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_054 | D | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_055 | D | GEN | — | ✓ | — | — | — | defer_to_E1_4 |
| HN_GEN_056 | E | GEN | ✓ above | ✓ | — | ✓ | ✓ | **retained_non_paraphrase** (Action 1a) |
| HN_GEN_059 | E | GEN | — | ✓ | — | ✓ | ✓ | **requires_content_review_at_E1_4** |
| HN_GEN_062 | F | GEN | ✓ below | — | — | — | — | defer_to_E1_4 |

### §7.1 — Disposition summary

| Disposition | Count | Source |
| --- | --- | --- |
| `retained_non_paraphrase` (Action 1a) | 2 | HN_GEN_051, HN_GEN_056 |
| `requires_content_review_at_E1_4` (Layer 5, not yet reviewed) | 2 | HN_SEED_016, HN_GEN_059 |
| `defer_to_E1_4` (V1a / V1b outliers, no urgent paraphrase signal) | 19 | other 19 entries |
| **Total disposed** | **23** | |

---

## §8 — Cross-Reference to Documented Findings

| Finding | Outlier-set tie-in |
| --- | --- |
| **S1 — cross-domain spillover** | §2.1: 8/10 V1a below-band outliers are cross-domain (S1 = the dominant below-band mechanism) |
| **S2 — E1.1 vs E1.2 asymmetry** | §2.1: 8 of 10 V1a below-band entries are SEED (E1.1); audit-driven E1.2 generation 5× lower below-band fail rate |
| **S5 — length non-signal** | §2.1: V1a below-band length ≈ corpus baseline; cross-validated against this inventory |
| **S6 — author vs measurement divergence** | §2.1+§2.2: SEED entries' author-set `target_secret_id` vs measurement diverges 17% / 67% / 40%; §6.3 HN_SEED_013 is a specific case of cross-direction divergence |
| **S7 — corpus-version disjointness** | §4: 60-entry corpus excluded from V1b scope; V5b includes both per V2 §4.1 spec; 0 hits across both |
| **S8 — mpnet prediction-miss** | §3.1: mpnet observed +0.18 above predicted midpoint; explains why mpnet has the most V1b outliers (14) despite per-encoder fail rate (21.5%) below escalation threshold |
| **S9 — bge_large null result** | §3.2: 0/65 outliers; band [0.45, 0.90] permissive |
| **S10 — encoder-family consensus weak** | §6.1 + §6.2: 18 entries flagged by exactly 1 validator (single-encoder failures); only 2 flagged by 3 validators co-directionally |
| **S11 — Cat D/E cross-encoder above-band** | §1 (Cat D 70%, Cat E 40%) + §3.1 (mpnet D=6, E=3) + §3.3 (finlang D=2, E=2) + §5 (4 Layer 5 candidates all D or E) |
| **S12 — V5b zero contamination** | §4: 0 V5b hits; Layer 1 prompt template held |

---

## §9 — E1.4 Regeneration Handoff Summary

| Disposition class | Count | E1.4 action |
| --- | --- | --- |
| `retained_non_paraphrase` | 2 | No regeneration; document Action 1a rulings in E1.4 audit |
| `requires_content_review_at_E1_4` | 2 | **Priority queue**: HN_SEED_016 + HN_GEN_059 need Action-1a-style content review before final disposition |
| `defer_to_E1_4` (V1a below-band) | 10 | Refine vs drop per V2 §2.5 remediation table — S1 cross-domain spillover may inform "refine" approach (regenerate with domain-vocabulary injection) |
| `defer_to_E1_4` (V1b mpnet-only above-band) | 9 | Honest reporting per S8 — these are mpnet-specific manifestations of the +0.18 prediction-miss; no per-corpus drop indicated |
| **Total E1.4 disposition load** | **23** | |

E1.4 entry criteria from this inventory:
- 2 entries require content review (Layer 5 not yet content-reviewed)
- 21 entries enter standard V2 §4.3 remediation flow (drop / refine / retain) per validator-specific outcome table
- V2.5 plan-revision decisions (S1 / S8 / S9) remain PENDING for E1.3.7 ratification

---

*End of `outlier_inventory.md`. E1.3.6 outlier consolidation complete.
Drop decisions deferred to E1.4 per Option B precedent. Standing by
for E1.3.7 RESULTS doc write-up.*
