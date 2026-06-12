# Tier-0 Rerun — D§3.4: 8-cell Embedding + Retrieval-Utility (OFFLINE; ZERO API)

Per-cell leakage (needs LLM) is NOT run here — deferred to Tier-2.

## Relevance protocol (ratified)

- 1 relevant doc per probe: each corpus's held-out PUBLIC PROBE -> its own secret. Decoupled from the attack set.
- corpus_v2 probe = `anchor_text` (designed public anchor).
- old secrets_v2 probe = `title` (closest intrinsic public probe; no anchor exists pre-restructure). **Cross-corpus comparison is QUALIFIED (different probe types); within-corpus cross-encoder comparison is clean.**
- bge_large uses its query instruction prefix on the probe; KB raw. Others: no prefix.

## 8-cell retrieval-utility matrix

| encoder | corpus | probe | nDCG@10 | R@1 | R@5 | R@10 | mean rank |
|---------|--------|-------|--------:|----:|----:|-----:|----------:|
| minilm | corpus_v2 | anchor | 0.8051 | 0.700 | 0.889 | 0.911 | 4.06 |
| minilm | old_secrets_v2 | title | 0.7791 | 0.511 | 0.978 | 0.989 | 2.01 |
| mpnet | corpus_v2 | anchor | 0.7588 | 0.589 | 0.844 | 0.911 | 3.96 |
| mpnet | old_secrets_v2 | title | 0.7664 | 0.478 | 1.000 | 1.000 | 1.84 |
| bge_large | corpus_v2 | anchor | 0.7838 | 0.678 | 0.856 | 0.878 | 5.08 |
| bge_large | old_secrets_v2 | title | 0.7647 | 0.478 | 0.989 | 1.000 | 1.91 |
| finlang | corpus_v2 | anchor | 0.6131 | 0.400 | 0.733 | 0.844 | 6.86 |
| finlang | old_secrets_v2 | title | 0.7553 | 0.522 | 0.889 | 1.000 | 2.41 |

## Per-encoder secret<->anchor separability (corpus_v2; D2 measure)

| encoder | own-anchor cosine (mean/median/min/max) | cross-pair rank!=1 |
|---------|------------------------------------------|-------------------:|
| minilm | 0.4812 / 0.4887 / 0.2189 / 0.7447 | 29 |
| mpnet | 0.5074 / 0.5108 / 0.2073 / 0.7730 | 34 |
| bge_large | 0.6395 / 0.6328 / 0.4874 / 0.7956 | 46 |
| finlang | 0.4593 / 0.4510 / 0.1562 / 0.7428 | 45 |

_Note: retrieval-utility (probe->secret) and separability (secret<->anchor) are the OFFLINE deliverables for §3.4; they let Tier-2 argue any per-cell leakage increase is not explained by retrieval-utility differences._
