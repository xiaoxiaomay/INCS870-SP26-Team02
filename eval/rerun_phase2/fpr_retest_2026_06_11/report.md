# Tier-0 Rerun — E. FPR Retest (gate-level, ZERO API)

Encoder (gate): `sentence-transformers/all-MiniLM-L6-v2`. Gate is per-query deterministic (rule_gate + embedding precheck + leakage_scan); FPR std across seeds = 0 by construction, so a single deterministic pass is reported (mean = value, std = 0.0).

_TPR is N/A for this benign-only input (no attacks); attack retargeting + TPR are Tier-1._

## Per-group block rate (corpus_v2 secret index; block = false positive)

| group | n | blocked | FPR |
|-------|--:|--------:|----:|
| benign_100 | 100 | 1 | 0.0100 |
| hard_neg_old_65 | 65 | 2 | 0.0308 |
| anchor_v2_90 | 90 | 17 | 0.1889 |
| decoy_v2_37 | 37 | 6 | 0.1622 |  ← DECOY (separate, not in main FPR)

**Main FPR (benign + hard-neg + anchor, pooled): 20/255 = 0.0784** (mean; std=0.0, deterministic).
**Decoy stress (separate): 6/37 = 0.1622.**

## Old index (secrets_v2) — for the McNemar comparison

| group | n | blocked | FPR |
|-------|--:|--------:|----:|
| benign_100 | 100 | 3 | 0.0300 |
| hard_neg_old_65 | 65 | 26 | 0.4000 |
| anchor_v2_90 | 90 | 6 | 0.0667 |
| decoy_v2_37 | 37 | 2 | 0.0541 |

## McNemar — old index vs corpus_v2 index (benign + hard-neg, paired)

- discordant: b(old-block, new-pass)=27, c(new-block, old-pass)=1 (total 28)
- method: chi-square w/ continuity correction; **p = 0.0000**
- interpretation: tests whether rebuilding the secret index on corpus_v2 significantly changes the benign block decision (FPR).
