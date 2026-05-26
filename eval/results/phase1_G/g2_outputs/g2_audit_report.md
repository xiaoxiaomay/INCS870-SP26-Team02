# Phase 1.G G2 Statistical Analysis — Audit Report

**Generated:** 2026-05-26T00:46:16.734612Z
**Data root:** /Users/wuxiaoxiao/Downloads/sentinelflow/eval/results
**Alpha:** 0.05
**Multiplicity correction:** Holm-Bonferroni step-down (k=4)
**Cells complete (n=5):** 8 / 8 | **Cells partial / missing:** 0 / 8

## §1. Data completeness

| Cell | n samples | Complete? | Missing files |
| --- | --- | --- | --- |
| `minilm_60entry` | 5 | Yes | — |
| `minilm_90entry` | 5 | Yes | — |
| `mpnet_60entry` | 5 | Yes | — |
| `mpnet_90entry` | 5 | Yes | — |
| `bge_large_60entry` | 5 | Yes | — |
| `bge_large_90entry` | 5 | Yes | — |
| `finlang_60entry` | 5 | Yes | — |
| `finlang_90entry` | 5 | Yes | — |

## §2. Per-cell aggregates (summary)

### `minilm_60entry`  (n=5)

- Bypass: 0.4760 ± 0.0000  values=[0.476, 0.476, 0.476, 0.476, 0.476]
- GLR:    0.0199 ± 0.0089  values=[0.0221, 0.0221, 0.0258, 0.0074, 0.0221]
- Per-BP-Leak: 0.0419 ± 0.0188  values=[0.0465, 0.0465, 0.0543, 0.0155, 0.0465]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [6, 6, 7, 2, 6] (sum=27)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `minilm_90entry`  (n=5)

- Bypass: 0.4280 ± 0.0000  values=[0.428, 0.428, 0.428, 0.428, 0.428]
- GLR:    0.0339 ± 0.0082  values=[0.0258, 0.0332, 0.0295, 0.0406, 0.0406]
- Per-BP-Leak: 0.0793 ± 0.0191  values=[0.0603, 0.0776, 0.0690, 0.0948, 0.0948]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [7, 9, 8, 11, 11] (sum=46)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `mpnet_60entry`  (n=5)

- Bypass: 0.3690 ± 0.0000  values=[0.369, 0.369, 0.369, 0.369, 0.369]
- GLR:    0.0561 ± 0.0109  values=[0.0701, 0.0517, 0.048, 0.059, 0.0517]
- Per-BP-Leak: 0.1520 ± 0.0296  values=[0.1900, 0.1400, 0.1300, 0.1600, 0.1400]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [19, 14, 13, 16, 14] (sum=76)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `mpnet_90entry`  (n=5)

- Bypass: 0.4945 ± 0.0000  values=[0.4945, 0.4945, 0.4945, 0.4945, 0.4945]
- GLR:    0.0502 ± 0.0052  values=[0.0517, 0.0517, 0.048, 0.0443, 0.0554]
- Per-BP-Leak: 0.1015 ± 0.0106  values=[0.1045, 0.1045, 0.0970, 0.0896, 0.1119]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [14, 14, 13, 12, 15] (sum=68)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `bge_large_60entry`  (n=5)

- Bypass: 0.3653 ± 0.0000  values=[0.3653, 0.3653, 0.3653, 0.3653, 0.3653]
- GLR:    0.1011 ± 0.0151  values=[0.0923, 0.0996, 0.0923, 0.1218, 0.0996]
- Per-BP-Leak: 0.2768 ± 0.0412  values=[0.2525, 0.2727, 0.2525, 0.3333, 0.2727]
- ULR:    0.0007 ± 0.0021  values=[0.0, 0.0, 0.0037, 0.0, 0.0]
- n_glr_leaked counts: [25, 27, 25, 33, 27] (sum=137)
- n_ulr_leaked counts: [0, 0, 1, 0, 0] (sum=1)

### `bge_large_90entry`  (n=5)

- Bypass: 0.5498 ± 0.0000  values=[0.5498, 0.5498, 0.5498, 0.5498, 0.5498]
- GLR:    0.1188 ± 0.0104  values=[0.1144, 0.1181, 0.1107, 0.1181, 0.1328]
- Per-BP-Leak: 0.2161 ± 0.0190  values=[0.2081, 0.2148, 0.2013, 0.2148, 0.2416]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [31, 32, 30, 32, 36] (sum=161)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `finlang_60entry`  (n=5)

- Bypass: 0.5424 ± 0.0000  values=[0.5424, 0.5424, 0.5424, 0.5424, 0.5424]
- GLR:    0.0354 ± 0.0083  values=[0.0332, 0.0369, 0.0443, 0.0369, 0.0258]
- Per-BP-Leak: 0.0653 ± 0.0153  values=[0.0612, 0.0680, 0.0816, 0.0680, 0.0476]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [9, 10, 12, 10, 7] (sum=48)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

### `finlang_90entry`  (n=5)

- Bypass: 0.5387 ± 0.0000  values=[0.5387, 0.5387, 0.5387, 0.5387, 0.5387]
- GLR:    0.0885 ± 0.0197  values=[0.0627, 0.1033, 0.0959, 0.0959, 0.0849]
- Per-BP-Leak: 0.1644 ± 0.0366  values=[0.1164, 0.1918, 0.1781, 0.1781, 0.1575]
- ULR:    0.0000 ± 0.0000  values=[0.0, 0.0, 0.0, 0.0, 0.0]
- n_glr_leaked counts: [17, 28, 26, 26, 23] (sum=120)
- n_ulr_leaked counts: [0, 0, 0, 0, 0] (sum=0)

## §3. Within-encoder paired t-tests

Primary tests (GLR rate, Holm-Bonferroni step-down):

- **minilm** (60 vs 90 GLR): mean Δ = -0.0140, t = -2.543, p = 0.0638, Holm rank 3, threshold 0.0250 → not significant
- **mpnet** (60 vs 90 GLR): mean Δ = +0.0059, t = 1.322, p = 0.2566, Holm rank 4, threshold 0.0500 → not significant
- **bge_large** (60 vs 90 GLR): mean Δ = -0.0177, t = -2.953, p = 0.0419, Holm rank 2, threshold 0.0167 → not significant
- **finlang** (60 vs 90 GLR): mean Δ = -0.0531, t = -8.363, p = 0.0011, Holm rank 1, threshold 0.0125 → **SIGNIFICANT** at α=0.05

**Summary:** 1 of 4 primary tests reject H_0 after Holm-Bonferroni adjustment at FWER ≤ 0.05.

## §4. Cross-encoder ordering (F2 verification)

- **Corpus 60:** F2 holds in 5/5 samples
- **Corpus 90:** F2 holds in 4/5 samples
  Exceptions: samples [4]

## §5. S15 predictive claim

- Prediction: ULR fires concentrated on bge-large cells
- bge-large total ULR fires: **1**
- non-bge-large total ULR fires: **0**
- Claim holds: **YES** (bge-large total ULR fires: 1; non-bge-large total: 0)

Per-cell ULR fires:
  - minilm_60entry: 0
  - minilm_90entry: 0
  - mpnet_60entry: 0
  - mpnet_90entry: 0
  - bge_large_60entry: 1  ← bge-large
  - bge_large_90entry: 0  ← bge-large
  - finlang_60entry: 0
  - finlang_90entry: 0

## §6. Recommendations for §V.B paper draft updates

- All 8 cells at n=5. Outputs are production-ready for §V.B.4 paper draft.
- Substitute numerical values in `paper_drafts/v10/v10_paper_section_V_B_phase1G_draft.md` §V.B.4 [TBD] markers with values from `paper_table_v_b_4.md`.
- S15 predictive claim verified empirically; update §V.B.5.1 status to reflect full-G1 evidence.

---

*End of audit report.*