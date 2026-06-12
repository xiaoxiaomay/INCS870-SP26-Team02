# Attack Pilot — 90 target-specific DRAFTS (templated, ZERO LLM/API)

Drafts for human ratification (Peter + domain reviewer). NOT an official attack set; no pipeline run, no LLM. Route P+ (keep 10-category taxonomy; re-author per corpus_v2 secret) because old->new mechanical remap is not viable (top1 cos max 0.527).

## Category coverage (pilot vs old 271 distribution; floor = >=3 each)

| category | pilot | floor ok | old-271 |
|----------|------:|:-------:|--------:|
| direct_extraction | 15 | ✓ | 51 |
| paraphrase_extraction | 12 | ✓ | 20 |
| indirect_extraction | 15 | ✓ | 40 |
| social_engineering | 9 | ✓ | 23 |
| prompt_injection | 9 | ✓ | 29 |
| encoding_extraction | 6 | ✓ | 20 |
| indirect_injection | 6 | ✓ | 20 |
| hard_block | 6 | ✓ | 19 |
| adversarial_exfil | 6 | ✓ | 16 |
| salami_attack | 6 | ✓ | 33 |
| **total** | **90** | | **271** |

- all 10 categories >=3: **True**

## Attack-vector allocation by offset_type

- secrets by type: {'A': 72, 'B': 18} (A=param-substitution, B=operational).

| offset_type | category | count |
|:-----------:|----------|------:|
| A | adversarial_exfil | 5 |
| A | direct_extraction | 15 |
| A | encoding_extraction | 6 |
| A | hard_block | 6 |
| A | indirect_extraction | 4 |
| A | indirect_injection | 6 |
| A | paraphrase_extraction | 12 |
| A | prompt_injection | 7 |
| A | salami_attack | 6 |
| A | social_engineering | 5 |
| B | adversarial_exfil | 1 |
| B | indirect_extraction | 11 |
| B | prompt_injection | 2 |
| B | social_engineering | 4 |

## Flags

- boundary_test secrets (difficulty forced hard, anchor-hugging): **9**
- total difficulty=hard: **30**
- multi_turn (salami, round-1 probe only): **6**

## ⚠️ LEAK_IN_QUERY self-check hits (0) — HUMAN REWRITE REQUIRED

Drafts whose query contains a numeric token also present in the target secret_text (would self-leak the answer). Hard constraint — must be reworded before use.

_None — no draft query contains a secret numeric value (templates ask, never reveal)._

## Next step (human, NOT done here)
- Domain reviewer ratifies/edits each `draft_query`, confirms category fit + expected_outcome, expands `multi_turn` salami rounds, and rewrites any LEAK_IN_QUERY row. Only AFTER ratification does this become an official attack file.
