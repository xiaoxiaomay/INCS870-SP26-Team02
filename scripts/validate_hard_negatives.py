"""
scripts/validate_hard_negatives.py — Phase 1.E E1.3 validator

Implements the V1a / V1b / V5b checks defined in PHASE_1E_PLAN_V2.md §4
against the hard-negative seed corpus (data/benchmark/hard_negatives_seeds_draft.jsonl).

This file covers E1.3.1 (infrastructure verification, --check-only) and
E1.3.2 (V1a: per-category MiniLM cosine band, --run-v1a). V1b (multi-encoder)
and V5b (exact-match leakage) are deferred to E1.3.4 / E1.3.5 and will be
added in a follow-up session.

Conventions reused without modification:
- MiniLM revision pin from core/config_loader.py:PINNED_REVISIONS
  (matches Phase 1.F M2 build_log.json — full reproducibility chain).
- FAISS IndexFlatIP on normalize_embeddings=True vectors → inner product
  IS cosine directly (no L2-to-cosine conversion needed).
- MiniLM index uses unsuffixed naming (data/index/secrets_v2.faiss) per
  Phase 1.F M2 historical artifact; other encoders use double-underscore
  + encoder suffix. Hard-coded below — DO NOT template-derive.
- Secret-side tier field is `level` (L1 / L2 / L3); hard-neg side uses
  `anchor_tier` (all L1 per T4). Filter excludes L3 secrets per V2 §5.3.

Outputs:
- eval/results/phase1_E/validation/v1a_<timestamp>.json — full report.
- data/benchmark/hard_negatives_seeds_draft.jsonl — atomic in-place update
  populating closest_secret_id_minilm_90 + closest_cosine_minilm_90 +
  expected_minilm_band (E1.3.2 only).
- data/benchmark/hard_negatives_seeds_draft.jsonl.bak — backup of pre-V1a
  corpus, created before the atomic write.

Field semantics (per V2 §5.2 + §5.3 dual-convention):

  target_secret_id:
    - HN_SEED_* (manual seeds, E1.1): author-set at seed time.
    - HN_GEN_*  (LLM-generated, E1.2): null (no author intent).
    Validator does NOT modify this field; it is read-only evidence of
    seed authoring methodology.

  closest_secret_id_<encoder>_<corpus>:
    Populated by validator FAISS top-1 lookup. One field per encoder ×
    corpus combination (V1a covers minilm × secrets_v2-90). L1+L2 only
    (L3 filtered per V2 §5.3, T4 ruling). Cosine value in companion
    field closest_cosine_<encoder>_<corpus> for audit-trail
    reproducibility — band classification re-derivable from the raw
    cosine + per-category bands without re-running FAISS.

  expected_minilm_band:
    Derived from closest_cosine_minilm_90 + per-category band table
    (V2 §2.2). One of {"low", "mid", "high"}.
"""

from __future__ import annotations

import argparse
import json
import pickle
import shutil
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from core.config_loader import PINNED_REVISIONS  # noqa: E402


HARD_NEG_PATH = REPO_ROOT / "data" / "benchmark" / "hard_negatives_seeds_draft.jsonl"
SECRETS_V2_PATH = REPO_ROOT / "data" / "secrets" / "secrets_v2.jsonl"  # 90-entry v2 canonical
SECRETS_60_PATH = REPO_ROOT / "data" / "secrets" / "secrets.jsonl"     # 60-entry legacy
OUTPUT_DIR = REPO_ROOT / "eval" / "results" / "phase1_E" / "validation"
R6_AUDIT_PATH = OUTPUT_DIR / "r6_audit.jsonl"

FAISS_INDEX_PATHS: Dict[str, str] = {
    # MiniLM uses unsuffixed naming per Phase 1.F M2 historical artifact
    # (build_log.json 2026-05-09). Other encoders use double-underscore +
    # encoder suffix. Preserved as-is for reproducibility chain integrity.
    "minilm":    "data/index/secrets_v2.faiss",
    "mpnet":     "data/index/secrets_v2__mpnet.faiss",
    "bge_large": "data/index/secrets_v2__bge_large.faiss",
    "finlang":   "data/index/secrets_v2__finlang.faiss",
}
FAISS_META_PATHS: Dict[str, str] = {
    "minilm":    "data/index/secrets_v2_meta.pkl",
    "mpnet":     "data/index/secrets_v2__mpnet_meta.pkl",
    "bge_large": "data/index/secrets_v2__bge_large_meta.pkl",
    "finlang":   "data/index/secrets_v2__finlang_meta.pkl",
}

ENCODER_NAMES: Dict[str, str] = {
    "minilm":    "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet":     "sentence-transformers/all-mpnet-base-v2",
    "bge_large": "BAAI/bge-large-en-v1.5",
    "finlang":   "FinLang/finance-embeddings-investopedia",
}

# Per V2 §2.2 — per-linguistic-category MiniLM expected band (mid).
# compute_expected_minilm_band partitions {< low → "low", [low, high] → "mid",
# > high → "high"}. V1a BLOCKING gate uses the global [0.40, 0.65] band from
# V2 §4.1, kept independent of the per-category band field.
CATEGORY_BANDS: Dict[str, Tuple[float, float]] = {
    "A": (0.45, 0.60),  # Industry-Typical Knowledge
    "B": (0.40, 0.55),  # Aggregated Statistics
    "C": (0.45, 0.65),  # Hypothetical Scenarios
    "D": (0.40, 0.55),  # Educational / Conceptual
    "E": (0.50, 0.65),  # Comparison / Benchmarking
    "F": (0.45, 0.60),  # Negation / Past-Tense / Conditional
}

GLOBAL_BLOCKING_BAND: Tuple[float, float] = (0.40, 0.65)
# V2 §2.5 Step-2 per-encoder acceptance windows (expected band ± 0.10 tolerance).
# Used by V1b (E1.3.4) BLOCKING check for the 3 secondary encoders.
STEP2_WINDOWS: Dict[str, Tuple[float, float]] = {
    "mpnet":     (0.07, 0.52),
    "bge_large": (0.45, 0.90),
    "finlang":   (0.20, 0.65),
}
# Expected-band midpoint per encoder (V2 §2.5 + §4.4). Used to compute the
# substantial-deviation check: |observed_mean - expected_midpoint| > 0.10
# triggers V2.5 plan revision per V2 §4.4 last paragraph.
EXPECTED_BAND_MIDPOINT: Dict[str, float] = {
    "minilm":    (0.40 + 0.65) / 2,
    "mpnet":     (0.17 + 0.42) / 2,
    "bge_large": (0.55 + 0.80) / 2,
    "finlang":   (0.30 + 0.55) / 2,
}
SECRET_TIER_ALLOWED = {"L1", "L2"}  # V2 §5.3 — exclude L3
TOP_K = 10  # Post-filter buffer; canonical top-1 picked from filtered subset.
            # Bumped 5→10 per E1.3.2 review: P(all-top-5-L3) ≈ 0.4%/query
            # (HN_SEED_009 hit this); TOP_K=10 drops it to ~0.002%/query.

# Verbatim findings text — written into the JSON report so the artifact is
# self-contained and the paper-grade observations are co-located with the
# evidence they emerged from. Drafted from E1.3.2 investigation ruling.
DOCUMENTED_FINDINGS: Dict[str, Any] = {
    "S1_cross_domain_spillover": (
        "Hard-negative corpus geometry interacts with secret corpus coverage "
        "in a previously unmodeled way. When a hard-negative's authored "
        "linguistic domain has insufficient vocabulary-aligned secrets, "
        "FAISS top-1 lookup crosses domain boundaries, resulting in cosine "
        "values below the expected per-encoder band. This 'cross-domain "
        "spillover' is structurally distinct from V2 §2.5's anticipated "
        "'easy negative' failure mode and represents a corpus-coverage "
        "finding (secrets_v2 has ~5 entries per domain×level), not a "
        "query-quality failure. Evidence: 80% (8/10) of below-band "
        "hard-negatives map via top-1 to a v2 secret in a DIFFERENT alpha "
        "domain than the hard-neg's authored domain. Cross-domain mapping "
        "is the dominant mechanism for cosine < 0.40 in this corpus."
    ),
    "S2_e11_vs_e12_asymmetry": (
        "Audit-driven hard-negative generation produces tighter MiniLM band "
        "centrality than manual seed authoring. Manual E1.1 seeds show "
        "26.7% (8/30) below-band failure rate; LLM-generated E1.2 entries "
        "show 5.7% (2/35), a 5x improvement attributable to the per-category "
        "anti-pattern audit and prompt scaffolding. This is empirical "
        "evidence that the audit framework has measurable corpus-quality "
        "impact, not just theoretical separation. Per V2 §2.2 specification, "
        "the LLM-generated cohort more reliably lands within expected "
        "per-category bands."
    ),
    "S5_length_nonsignal": (
        "Query length is not a band-failure discriminator. Below-band "
        "queries (mean 134 chars) show no meaningful length difference "
        "from corpus baseline (mean 138 chars). Failures correlate with "
        "domain-secret coverage gaps, not query verbosity."
    ),
    "S6_author_vs_measurement_divergence": {
        "type": "author_intent_vs_encoder_measurement_alignment",
        "summary": (
            "Author-intent target_secret_id (manual seeds, n=30) vs "
            "MiniLM-measured closest_secret_id_minilm_90 show divergence "
            "at three semantic layers: 17% exact-secret match, 67% "
            "same-alpha-domain, 40% same-tier alignment."
        ),
        "data": {
            "exact_secret_match": "5/30 (17%)",
            "same_alpha_domain":  "20/30 (67%)",
            "same_tier_L1":       "12/30 (40%)",
        },
        "interpretation": (
            "Manual seed authors operate at domain-level semantic "
            "intuition (67% domain alignment) but cannot reliably target "
            "the exact most-similar secret (17% exact match). This "
            "mechanistically explains the S2 finding (audit-driven "
            "generation 5x lower below-band fail rate): authors lack the "
            "semantic-precision intuition that LLM-with-domain-vocabulary-"
            "injection provides."
        ),
        "paper_implication": (
            "Provides 'author-intuition vs encoder-measurement' axis for "
            "methodology rigor. Reviewer-grade evidence that the audit "
            "framework operates at semantic precision level beyond human "
            "authorial intuition."
        ),
        "emerged_from": (
            "V2 §5.2 + §5.3 dual-field schema (Option C ratification "
            "2026-05-22) — both target_secret_id (author intent) and "
            "closest_secret_id_minilm_90 (validator measurement) preserved "
            "in same record, enabling direct comparison."
        ),
    },
    "S7_corpus_version_disjointness": {
        "type": "schema_assumption_vs_corpus_reality",
        "summary": (
            "V2 §5.2 schema (closest_secret_id 4 × 2) implies 4 encoders × 2 "
            "corpora with the implicit assumption that the 60-entry corpus "
            "is a subset of or calibration-comparable to the 90-entry "
            "corpus. Pre-flight verification for E1.3.4 surfaced that the "
            "corpora are completely disjoint (|60 ∩ 90| = 0) and have "
            "incompatible tier distributions: 60-entry (L1=0, L2=10, L3=50) "
            "vs 90-entry (L1=30, L2=30, L3=30)."
        ),
        "data": {
            "overlap":            "0 / 60",
            "60_entry_tiers":     {"L1": 0,  "L2": 10, "L3": 50},
            "90_entry_tiers":     {"L1": 30, "L2": 30, "L3": 30},
            "60_entry_id_format": "S0001 (legacy pre-v2)",
            "90_entry_id_format": "v2_L<tier>_<domain>_<NNN>",
        },
        "interpretation": (
            "The 60-entry corpus is the original pre-v2 secret reference; "
            "the 90-entry corpus is the v2 redesign with structured "
            "per-tier-per-domain coverage. They are parallel canonical "
            "sources, not a subset relationship. Applying V2 §5.3's L1+L2 "
            "filter to the 60-entry corpus leaves only 10 candidate "
            "secrets (all L2), making FAISS top-K post-filter degenerate."
        ),
        "paper_implication": (
            "V2 §2.5's '60-entry warns if disagrees with 90-entry' "
            "provision fails semantically with disjoint corpora — "
            "disagreement becomes structural noise rather than calibration "
            "signal. E1.3.4 scope was revised to 4 encoders × 90-entry "
            "only; 60-entry comparison is properly scoped to v10 §VI "
            "reproducibility appendix or a future V1c sub-step."
        ),
        "emerged_from": (
            "E1.3.4 V1b pre-flight verification 2026-05-22, before any "
            "V1b code execution. View-before-implement methodology rigor "
            "surfaced the schema-vs-reality gap before it propagated into "
            "a shipped validator."
        ),
    },
    "S8_mpnet_expected_band_prediction_miss": {
        "type": "predicted_vs_observed_band_calibration_deviation",
        "summary": (
            "mpnet observed mean cosine 0.4725 exceeds V2 §2.5 predicted "
            "band midpoint 0.295 by +0.18, unambiguously triggering V2 "
            "§4.4 substantial-deviation threshold (> 0.10)."
        ),
        "data": {
            "predicted_band":         "[0.17, 0.42]",
            "predicted_midpoint":     0.295,
            "observed_mean":          0.4725,
            "observed_p10":           0.3889,
            "observed_p90":           0.5769,
            "delta_mean_vs_midpoint": "+0.1775",
            "deviation_threshold":    "0.10 (V2 §4.4)",
            "outliers_above_window":  "14/65 (21.5%)",
        },
        "interpretation": (
            "V2 §2.5 mpnet band was derived from Phase 1.F M3 attack-"
            "corpus shift observations (~0.23 shift). The hard-negative-"
            "corpus shift is asymmetric to the attack-corpus shift: "
            "hard-negs land +0.18 above the predicted midpoint on mpnet, "
            "indicating hard-negs sit closer to the secret manifold on "
            "mpnet than the attack-corpus prediction suggested."
        ),
        "paper_implication": (
            "Honest reporting of prediction-vs-observed calibration "
            "deviation. Per Q1 STRICT-with-paper-escalation ruling: "
            "document prediction miss as v10 contribution, do NOT post-"
            "hoc re-anchor mpnet band to fit observed data (survivorship "
            "bias). V2.5 plan revision is triggered (V2 §4.4 clause); "
            "revision wording defers to E1.3.7 / E1.6 close."
        ),
        "emerged_from": (
            "E1.3.4 V1b multi-encoder run 2026-05-22. Substantial-"
            "deviation check was added to validator per V2 §4.4 reporting "
            "requirement; mpnet triggered as the sole encoder exceeding "
            "the 0.10 threshold."
        ),
    },
    "S9_bge_large_band_permissiveness_null_result": {
        "type": "encoder_band_calibration_observation",
        "summary": (
            "bge_large 0/65 outliers — the V2 §2.5 predicted band "
            "[0.45, 0.90] catches all 65 hard-negs with observed mean "
            "0.7034 (P10=0.6408, P90=0.7909) sitting well-centered. The "
            "widest predicted band catches the most hard-negs "
            "(informative null result)."
        ),
        "data": {
            "predicted_band":          "[0.45, 0.90]",
            "band_width":              0.45,
            "observed_mean":           0.7034,
            "observed_p10":            0.6408,
            "observed_p90":            0.7909,
            "outliers_above_window":   "0/65 (0.0%)",
            "outliers_below_window":   "0/65 (0.0%)",
        },
        "interpretation": (
            "Two readings: (a) the bge_large [0.45, 0.90] window is too "
            "wide to function as a useful BLOCKING constraint for this "
            "corpus; (b) bge_large embedding has unusually tight "
            "clustering of finance-domain content where all hard-negs "
            "naturally land mid-band. The observed P10-P90 span "
            "(0.64-0.79) suggests the actual hard-neg cluster sits in "
            "the upper-mid portion of the predicted band, leaving "
            "substantial unused window below."
        ),
        "paper_implication": (
            "Informative null result. V2.5 consideration: either tighten "
            "bge_large window to ~[0.60, 0.80] (still admits all 65 "
            "entries based on observed P10=0.64 with margin) for stronger "
            "BLOCKING semantics, OR document that bge_large is the most "
            "permissive encoder family member in finance hard-neg "
            "geometry as a v10 finding. Defer revision decision to "
            "E1.3.7 / E1.6 close."
        ),
        "emerged_from": (
            "E1.3.4 V1b multi-encoder run 2026-05-22. Per-encoder "
            "BLOCKING rate report surfaced bge_large 0% fail rate as the "
            "only all-pass encoder."
        ),
    },
    "S10_encoder_family_consensus_structurally_weak": {
        "type": "cross_encoder_picking_consensus_vs_band_consistency",
        "summary": (
            "Only 9/65 (13.8%) of entries have all 4 encoders pick the "
            "same closest secret; 11/65 (16.9%) have all 4 encoders pick "
            "completely different secrets. Same-domain agreement is "
            "52.3%, same-tier agreement 40.0%. Cross-encoder consensus "
            "on which-secret-is-closest is structurally weak."
        ),
        "data": {
            "exact_secret_id_agreement": "9/65 (13.8%)",
            "same_domain_agreement":     "34/65 (52.3%)",
            "same_tier_agreement":       "26/65 (40.0%)",
            "all_blocking_pass":         "42/65 (64.6%)",
            "distinct_picks_distribution": {
                "1_distinct_all_agree": 9,
                "2_distinct":           23,
                "3_distinct":           22,
                "4_distinct_all_differ": 11,
            },
        },
        "interpretation": (
            "Mechanistically: the V1b BLOCKING check asks 'is each "
            "encoder's hard-neg-vs-secret cosine in its predicted band?' "
            "— not 'do the 4 encoders agree on which secret is nearest?' "
            "The 4 encoders are NOT picking the same closest secret most "
            "of the time; they are validating semantic-band consistency "
            "for what each independently calls 'closest secret'. This "
            "aligns with V2 §2.5's stated scope: 'closeness to secret "
            "manifold across encoder family' (not 'consensus on nearest "
            "secret')."
        ),
        "paper_implication": (
            "Reviewer-clarifying methodology note. Cross-encoder hard-"
            "negative validation is about no encoder finding the hard-neg "
            "dangerously close to ITS nearest secret, not about consensus "
            "on which secret is universally nearest. The 13.8% exact-"
            "secret-id agreement rate is NOT a failure — it is the "
            "expected operating profile of a heterogeneous encoder family "
            "on a structurally hard corpus."
        ),
        "emerged_from": (
            "E1.3.4 V1b cross-encoder agreement analysis 2026-05-22. "
            "The 4-way agreement matrix (exact/domain/tier/blocking) was "
            "added per Q2 ratification multi-level agreement spec."
        ),
    },
    "S11_cat_d_e_cross_encoder_above_band_concentration": {
        "type": "linguistic_category_x_encoder_systematic_pattern",
        "summary": (
            "Cat D (Educational/Conceptual) and Cat E (Comparison/"
            "Benchmarking) linguistic categories dominate cross-encoder "
            "above-band outliers: Cat D = 6/14 mpnet outliers and 2/4 "
            "finlang outliers; Cat E = 3/14 mpnet outliers and 2/4 "
            "finlang outliers. Cat B and Cat F produce 0 outliers across "
            "all encoders. Pattern is structural across 3 of 4 encoders, "
            "confirming V2 §2.2 prediction that D is band-tightest."
        ),
        "data": {
            "mpnet_outliers_by_category":     {"D": 6, "A": 4, "E": 3, "C": 1, "B": 0, "F": 0},
            "finlang_outliers_by_category":   {"D": 2, "E": 2, "A": 0, "B": 0, "C": 0, "F": 0},
            "bge_large_outliers_by_category": {},
            "v1a_d_high_band_carryover": (
                "HN_SEED_016, HN_SEED_017, HN_GEN_051/053/054 fail mpnet; "
                "HN_SEED_016 and HN_GEN_051 also fail finlang"
            ),
            "v1a_e_high_band_carryover": (
                "HN_GEN_056 fails mpnet AND finlang (3 of 4 encoders "
                "above-band)"
            ),
        },
        "interpretation": (
            "Cat D and Cat E share a structural vocabulary-overlap with "
            "secret-text content: D uses concept-name vocabulary (e.g., "
            "'factor neutrality') that aligns lexically with secret "
            "titles and bodies (e.g., 'Multi-Factor Neutralization "
            "Framework'); E uses comparison-axis vocabulary that often "
            "names two strategy/data types both present in the secret "
            "corpus. Cat B (aggregated statistics) and Cat F (negation/"
            "past-tense) use linguistic structures (aggregation verbs, "
            "past-tense markers) that are vocabulary-distant from "
            "secret-text style and don't cluster on the secret manifold."
        ),
        "paper_implication": (
            "V2 §2.2 design prediction (D band-tightest) is multi-"
            "encoder-confirmed, not MiniLM-specific. Cat D and Cat E "
            "above-band behavior is a property of the linguistic-"
            "category × secret-corpus geometry, not an encoder artifact. "
            "This validates the per-category band differentiation in V2 "
            "§2.2 and reinforces the audit framework's per-category "
            "prompt scaffolding (S2)."
        ),
        "emerged_from": (
            "E1.3.4 V1b per-encoder outlier category breakdown 2026-05-22. "
            "Pattern surfaced by aggregating mpnet + finlang outlier "
            "categories and cross-referencing with V1a §2 per-category "
            "high-band entries."
        ),
    },
    "S12_v5b_zero_corpus_contamination": {
        "type": "corpus_contamination_null_result_audit_grade",
        "summary": (
            "V5b exact-string match (V2 §4.1 BLOCKING Layer 2) yielded "
            "0 hits across 65 hard-negs × 150 secrets × 2 fields (query "
            "+ rationale) = ~19,500 pairwise comparisons. The audit-"
            "driven generation pipeline (E1.2) + V2 §7.2 Layer 1 prompt "
            "template constraints successfully prevented verbatim secret-"
            "content leakage."
        ),
        "data": {
            "v5b_match_count":                0,
            "secrets_checked":                "150 (60 legacy + 90 v2 canonical)",
            "hard_negs_checked":              65,
            "fields_checked_per_entry":       "query + rationale",
            "total_pairwise_comparisons":     "~19500",
            "exact_match_against_secret_distribution": {"True": 0, "False": 65},
            "layer_5_paraphrase_candidates":  4,
            "layer_2_v5b_hits":               0,
        },
        "interpretation": (
            "Null result confirms Layer 1 prompt template constraints "
            "(V2 §7.2) held across all 35 LLM-generated entries and all "
            "30 manual seeds. No verbatim secret text emitted by GPT-5-"
            "mini generation or paraphrased into seed rationale by "
            "manual authors. Note: Layer 5 paraphrase signatures (4 V1b "
            "multi-encoder above-band entries) are recorded in "
            "r6_audit.jsonl as forensic evidence of paraphrase-shaped "
            "CANDIDATES, distinct from Layer 2 exact-match leakage. "
            "Layer 5 candidates remain awaiting content review (2 "
            "dispositioned 'retained_non_paraphrase' per V1a Action 1a; "
            "2 dispositioned 'requires_content_review_at_E1_4')."
        ),
        "paper_implication": (
            "Per V2 §7.2: 'If any V5b match was found, V2.5 plan "
            "revision is triggered.' With 0 hits, NO V2.5 revision "
            "needed for Layer 1 prompt constraints. The audit-grade R6 "
            "6-layer mitigation chain holds. Reviewer-grade confirmation "
            "that the corpus-generation methodology is audit-defensible "
            "against secret-content leakage."
        ),
        "emerged_from": (
            "E1.3.5 V5b run 2026-05-22. Both secrets corpora checked "
            "exhaustively. Pairwise comparison ~19500; 0 matches "
            "confirms null-result target."
        ),
    },
    "PENDING_V2_5_PLAN_REVISION": (
        "PENDING — V2.5 plan revision references S1 (cross-domain "
        "spillover), S8 (mpnet prediction-miss), S9 (bge_large "
        "permissiveness). Decision needed: should V2 §2.5 windows be "
        "revised post-hoc, or kept as Phase 1.F-derived predictions with "
        "documented deviations from observed values? Per Q1 STRICT-with-"
        "paper-escalation ruling, the default is documented-prediction-"
        "miss (no post-hoc re-anchor) to avoid survivorship bias. Defer "
        "final ruling to E1.3.7 results write-up or E1.6 Phase 1.E close."
    ),
    "PENDING_V2_5_SCHEMA_REVISION": (
        "PENDING — V2 §5.2 schema describes closest_secret_id (4 × 2) "
        "implying 4 encoders × 2 corpora. E1.3.4 pre-flight (S7) surfaced "
        "that the 60-entry and 90-entry corpora are disjoint with "
        "incompatible tier distributions, making the L1+L2 filter "
        "degenerate against the 60-entry corpus. V2.5 schema revision "
        "should either (a) restrict the schema to 4 × 1 for E1 validation "
        "scope (90-entry only) or (b) introduce explicit "
        "60-entry-legacy-reference field semantics distinct from V1b "
        "BLOCKING measurement. Resolution deferred to E1.3.7 results "
        "write-up or E1.6 Phase 1.E close."
    ),
}


def compute_expected_minilm_band(cosine: float, category: str) -> str:
    low, high = CATEGORY_BANDS[category]
    if cosine < low:
        return "low"
    if cosine <= high:
        return "mid"
    return "high"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_encoder_components(short_name: str) -> Tuple[Any, Any, List[Dict[str, Any]]]:
    """Generic encoder + FAISS index + meta loader for any of the 4 pinned
    encoders. Returns (model, index, meta). Used by V1a (minilm only) and V1b
    (all 4)."""
    import faiss  # type: ignore
    from sentence_transformers import SentenceTransformer  # type: ignore

    encoder_name = ENCODER_NAMES[short_name]
    revision = PINNED_REVISIONS[encoder_name]

    print(f"  loading {short_name} (rev {revision[:12]}...)")
    model = SentenceTransformer(encoder_name, revision=revision)

    idx_path = REPO_ROOT / FAISS_INDEX_PATHS[short_name]
    meta_path = REPO_ROOT / FAISS_META_PATHS[short_name]
    print(f"  loading FAISS index: {idx_path.relative_to(REPO_ROOT)}")
    index = faiss.read_index(str(idx_path))
    with meta_path.open("rb") as f:
        meta = pickle.load(f)

    if index.ntotal != len(meta):
        raise RuntimeError(
            f"FAISS / meta size mismatch for {short_name}: "
            f"index.ntotal={index.ntotal} vs meta len={len(meta)}"
        )
    return model, index, meta


def load_minilm_components() -> Tuple[Any, Any, List[Dict[str, Any]]]:
    """Backward-compat wrapper for V1a's MiniLM-only path."""
    return load_encoder_components("minilm")


def encode_queries(model: Any, queries: List[str]) -> Any:
    """Encode queries with normalize_embeddings=True to match index convention."""
    import numpy as np  # type: ignore
    emb = model.encode(
        queries,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.asarray(emb, dtype="float32")


def run_check_only() -> int:
    print("=== E1.3.1 infrastructure verification (--check-only) ===")
    print()

    # Corpora
    hard_negs = load_jsonl(HARD_NEG_PATH)
    print(f"  hard-neg corpus: {len(hard_negs)} entries "
          f"({HARD_NEG_PATH.relative_to(REPO_ROOT)})")
    if len(hard_negs) != 65:
        print(f"  ! UNEXPECTED: expected 65 entries, got {len(hard_negs)}")
        return 1

    secrets = load_jsonl(SECRETS_V2_PATH)
    print(f"  secrets_v2 corpus: {len(secrets)} entries "
          f"({SECRETS_V2_PATH.relative_to(REPO_ROOT)})")
    if len(secrets) != 90:
        print(f"  ! UNEXPECTED: expected 90 entries, got {len(secrets)}")
        return 1

    level_dist = Counter(s.get("level") for s in secrets)
    print(f"  secret tier distribution: {dict(level_dist)}")
    filtered = [s for s in secrets if s.get("level") in SECRET_TIER_ALLOWED]
    print(f"  filtered to {{L1, L2}}: {len(filtered)} secrets "
          f"(L3 excluded per V2 §5.3)")

    # MiniLM model + index
    model, index, meta = load_minilm_components()
    print(f"  MiniLM dim: {model.get_sentence_embedding_dimension()}")
    print(f"  FAISS ntotal: {index.ntotal}; meta len: {len(meta)}")
    print(f"  MiniLM pin: "
          f"{PINNED_REVISIONS[ENCODER_NAMES['minilm']]}")

    # Hard-neg anchor_tier check
    hn_anchor_dist = Counter(h.get("anchor_tier") for h in hard_negs)
    print(f"  hard-neg anchor_tier distribution: {dict(hn_anchor_dist)}")
    if set(hn_anchor_dist) != {"L1"}:
        print(f"  ! UNEXPECTED: T4 ruling expects all anchor_tier=L1")
        return 1

    # Output dir creation (validator must create on first run)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  output dir ready: {OUTPUT_DIR.relative_to(REPO_ROOT)}")

    print()
    print("PASS: infrastructure verified.")
    return 0


def run_v1a() -> int:
    print("=== E1.3.2 V1a — per-encoder MiniLM cosine band (--run-v1a) ===")
    print()
    t_start = time.time()

    hard_negs = load_jsonl(HARD_NEG_PATH)
    if len(hard_negs) != 65:
        print(f"  ! UNEXPECTED: expected 65 hard-neg entries, got {len(hard_negs)}")
        return 1

    model, index, meta = load_minilm_components()

    # Validate ID ordering: FAISS row i ↔ meta[i]
    queries = [h["query"] for h in hard_negs]
    print(f"  encoding {len(queries)} queries...")
    q_emb = encode_queries(model, queries)
    print(f"  query embedding shape: {q_emb.shape}")

    t_search0 = time.time()
    D, I = index.search(q_emb, TOP_K)
    t_search = time.time() - t_search0
    print(f"  FAISS search complete in {t_search:.3f}s "
          f"(top_k={TOP_K})")

    # Per-entry post-filter to {L1, L2}, take top-1
    band_table: Dict[str, Counter] = defaultdict(Counter)
    tier_counts: Counter = Counter()
    blocking_pass = 0
    outliers: List[Dict[str, Any]] = []
    fallback_warnings: List[Dict[str, Any]] = []

    for row, entry in enumerate(hard_negs):
        cat = entry["category"]
        # Walk top-K, find first with level in {L1, L2}
        chosen_idx = None
        for k in range(TOP_K):
            secret_idx = int(I[row][k])
            if secret_idx < 0:
                continue
            if meta[secret_idx].get("level") in SECRET_TIER_ALLOWED:
                chosen_idx = (k, secret_idx)
                break

        if chosen_idx is None:
            # All TOP_K were L3 — flag and skip; do NOT touch target_secret_id
            # (V2 §5.3 dual-convention: only the validator-measurement fields
            # are mutated here; author-set target_secret_id is read-only).
            fallback_warnings.append({
                "_id": entry["_id"],
                "category": cat,
                "top_k_levels": [meta[int(I[row][k])].get("level")
                                  for k in range(TOP_K)],
            })
            entry["closest_secret_id_minilm_90"] = None
            entry["closest_cosine_minilm_90"] = None
            entry["expected_minilm_band"] = None
            continue

        k_taken, secret_idx = chosen_idx
        cosine = float(D[row][k_taken])
        secret = meta[secret_idx]

        # V2 §5.3: do NOT overwrite target_secret_id. Validator-measurement
        # fields go in closest_secret_id_<encoder>_<corpus> per V2 §5.2.
        entry["closest_secret_id_minilm_90"] = secret["_id"]
        entry["closest_cosine_minilm_90"] = round(cosine, 4)
        entry["expected_minilm_band"] = compute_expected_minilm_band(cosine, cat)
        entry["_v1a_k_taken"] = k_taken
        entry["_v1a_secret_level"] = secret.get("level")

        band_table[cat][entry["expected_minilm_band"]] += 1
        tier_counts[secret.get("level")] += 1

        lo, hi = GLOBAL_BLOCKING_BAND
        if lo <= cosine <= hi:
            blocking_pass += 1
        else:
            outliers.append({
                "_id": entry["_id"],
                "category": cat,
                "cosine": round(cosine, 4),
                "target_secret_id": secret["_id"],
                "direction": "below" if cosine < lo else "above",
            })

    # Reports
    print()
    print("--- Band distribution (per-category, per-band) ---")
    cats = sorted(CATEGORY_BANDS.keys())
    print(f"  {'Cat':4s} {'low':>5s} {'mid':>5s} {'high':>5s}  band")
    for cat in cats:
        lo, hi = CATEGORY_BANDS[cat]
        print(f"  {cat:4s} "
              f"{band_table[cat]['low']:>5d} "
              f"{band_table[cat]['mid']:>5d} "
              f"{band_table[cat]['high']:>5d}  [{lo:.2f}, {hi:.2f}]")

    print()
    print("--- Per-tier breakdown (target_secret_id level) ---")
    for lvl in ("L1", "L2"):
        print(f"  {lvl}: {tier_counts[lvl]} entries")

    print()
    print("--- Global BLOCKING band check ([0.40, 0.65]) ---")
    print(f"  PASS: {blocking_pass}/65")
    print(f"  FAIL: {len(outliers)}/65")
    if outliers:
        print()
        print("--- Outliers (cosine outside global BLOCKING band) ---")
        for o in outliers:
            print(f"  {o['_id']:14s} cat={o['category']} "
                  f"cosine={o['cosine']:.4f} ({o['direction']}) "
                  f"→ {o['target_secret_id']}")

    if fallback_warnings:
        print()
        print(f"--- ! Fallback warnings: {len(fallback_warnings)} entries had "
              f"no L1/L2 secret in top-{TOP_K} ---")
        for w in fallback_warnings:
            print(f"  {w['_id']} cat={w['category']} "
                  f"top_levels={w['top_k_levels']}")

    # Atomic JSONL write
    print()
    print("--- Atomic in-place update ---")
    bak_path = HARD_NEG_PATH.with_suffix(HARD_NEG_PATH.suffix + ".bak")
    shutil.copy2(HARD_NEG_PATH, bak_path)
    print(f"  backup: {bak_path.relative_to(REPO_ROOT)}")

    # Strip internal _v1a_* diagnostic fields before writing
    persisted = []
    for h in hard_negs:
        clean = {k: v for k, v in h.items() if not k.startswith("_v1a_")}
        persisted.append(clean)
    write_jsonl(HARD_NEG_PATH, persisted)

    verify = load_jsonl(HARD_NEG_PATH)
    if len(verify) != 65:
        print(f"  ! WRITE VERIFY FAILED: read back {len(verify)} entries; "
              f"restoring from .bak")
        shutil.copy2(bak_path, HARD_NEG_PATH)
        return 1
    target_populated = sum(1 for v in verify if v.get("target_secret_id") is not None)
    closest_populated = sum(1 for v in verify
                             if v.get("closest_secret_id_minilm_90") is not None)
    band_populated = sum(1 for v in verify
                          if v.get("expected_minilm_band") is not None)
    print(f"  re-read: {len(verify)} entries")
    print(f"  target_secret_id populated:           {target_populated}/65 "
          f"(expect 30 — manual seeds only, V2 §5.3)")
    print(f"  closest_secret_id_minilm_90 populated:{closest_populated}/65")
    print(f"  expected_minilm_band populated:       {band_populated}/65")

    # Per-category high-band entries (Finding #3 documentation)
    per_category_high_band: Dict[str, List[str]] = defaultdict(list)
    for v in verify:
        if v.get("expected_minilm_band") == "high":
            per_category_high_band[v["category"]].append(v["_id"])

    # Report file
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "1.E.E1.3.2 — V1a",
        "minilm_revision": PINNED_REVISIONS[ENCODER_NAMES["minilm"]],
        "hard_neg_count": len(hard_negs),
        "secret_corpus_size": index.ntotal,
        "secret_tier_filter": sorted(SECRET_TIER_ALLOWED),
        "top_k": TOP_K,
        "band_distribution_per_category": {
            cat: dict(band_table[cat]) for cat in cats
        },
        "tier_breakdown": dict(tier_counts),
        "global_blocking_band": list(GLOBAL_BLOCKING_BAND),
        "blocking_pass": blocking_pass,
        "blocking_fail": len(outliers),
        "outliers": outliers,
        "fallback_warnings": fallback_warnings,
        "field_population": {
            "target_secret_id":             target_populated,
            "closest_secret_id_minilm_90":  closest_populated,
            "expected_minilm_band":         band_populated,
        },
        "per_category_high_band": {
            **{cat: ids for cat, ids in per_category_high_band.items()},
            "note": (
                "V2 §2.2 predicts D band-tightest; V1b cross-encoder "
                "(E1.3.4) will determine MiniLM-specific vs systematic."
            ),
        },
        "documented_findings": DOCUMENTED_FINDINGS,
        "wall_seconds": round(time.time() - t_start, 2),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"v1a_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  report: {report_path.relative_to(REPO_ROOT)}")

    print()
    print(f"E1.3.2 V1a complete in {report['wall_seconds']:.2f}s.")
    return 0


def run_v1b() -> int:
    """E1.3.4 — V1b multi-encoder cosine band check (90-entry corpus).

    For each of {minilm, mpnet, bge_large, finlang}: encode all 65 queries,
    FAISS top-K with L1/L2 post-filter, compute per-encoder pass/fail vs the
    encoder's BLOCKING window (V2 §4.1 for minilm; V2 §2.5 Step-2 windows for
    the other 3). Populate per-encoder closest_secret_id_*_90 +
    closest_cosine_*_90 fields and aggregate v1b_blocking_pass +
    cross_encoder_agreement fields. Atomic JSONL write + v1b_<ts>.json report.
    Scope: 4 encoders × 90-entry only (per S7 finding; 60-entry deferred).
    """
    import numpy as np  # type: ignore

    print("=== E1.3.4 V1b — multi-encoder cosine band check (--run-v1b) ===")
    print()
    t_start = time.time()

    hard_negs = load_jsonl(HARD_NEG_PATH)
    if len(hard_negs) != 65:
        print(f"  ! UNEXPECTED: expected 65 hard-neg entries, got {len(hard_negs)}")
        return 1

    encoders = ("minilm", "mpnet", "bge_large", "finlang")
    components: Dict[str, Tuple[Any, Any, Any]] = {}
    for enc in encoders:
        components[enc] = load_encoder_components(enc)

    # All 4 metas are byte-identical (verified pre-flight 2026-05-22) — a
    # single sec_by_id map suffices across encoders.
    sec_by_id = {s["_id"]: s for s in components["minilm"][2]}

    queries = [h["query"] for h in hard_negs]
    n = len(hard_negs)

    # Per-encoder: encode + FAISS top-K + L1/L2 post-filter top-1
    per_encoder_picks: Dict[str, List[Any]] = {}
    for enc in encoders:
        model, index, meta = components[enc]
        print(f"\n  [{enc}] encoding {n} queries...")
        q_emb = encode_queries(model, queries)
        t0 = time.time()
        D, I = index.search(q_emb, TOP_K)
        print(f"  [{enc}] FAISS search: {time.time()-t0:.3f}s "
              f"(query_dim={q_emb.shape[1]})")
        picks: List[Any] = []
        for row in range(n):
            chosen = None
            for k in range(TOP_K):
                si = int(I[row][k])
                if si < 0:
                    continue
                if meta[si].get("level") in SECRET_TIER_ALLOWED:
                    chosen = (meta[si]["_id"], float(D[row][k]), k)
                    break
            picks.append(chosen)
        per_encoder_picks[enc] = picks

    # Encoder windows: MiniLM uses V2 §4.1 V1a global band; secondary
    # encoders use V2 §2.5 Step-2 windows.
    encoder_windows: Dict[str, Tuple[float, float]] = {
        "minilm": GLOBAL_BLOCKING_BAND,
        **STEP2_WINDOWS,
    }

    per_encoder_outliers: Dict[str, List[Dict[str, Any]]] = {e: [] for e in encoders}
    per_encoder_cosines: Dict[str, List[float]] = {e: [] for e in encoders}
    per_encoder_pass_count: Dict[str, int] = {e: 0 for e in encoders}
    fallback_count: Dict[str, int] = {e: 0 for e in encoders}
    agreement_counts = {
        "exact_secret_id":  0,
        "same_domain":      0,
        "same_tier":        0,
        "all_blocking_pass": 0,
    }

    for row, entry in enumerate(hard_negs):
        per_pass: Dict[str, bool] = {}
        for enc in encoders:
            pick = per_encoder_picks[enc][row]
            if pick is None:
                if enc != "minilm":
                    entry[f"closest_secret_id_{enc}_90"] = None
                    entry[f"closest_cosine_{enc}_90"] = None
                per_pass[enc] = False
                fallback_count[enc] += 1
                continue
            sid, cos, _k = pick
            if enc != "minilm":
                # MiniLM closest_* fields already populated by V1a; do not
                # overwrite. Only populate the 3 new encoders here.
                entry[f"closest_secret_id_{enc}_90"] = sid
                entry[f"closest_cosine_{enc}_90"] = round(cos, 4)
            per_encoder_cosines[enc].append(cos)
            lo, hi = encoder_windows[enc]
            passed = lo <= cos <= hi
            per_pass[enc] = passed
            if passed:
                per_encoder_pass_count[enc] += 1
            else:
                per_encoder_outliers[enc].append({
                    "_id": entry["_id"],
                    "category": entry["category"],
                    "cosine": round(cos, 4),
                    "direction": "below" if cos < lo else "above",
                    "target_secret_id": sid,
                })

        # v1b_blocking_pass: per-Q4 spec, only the 3 new encoders (MiniLM
        # has its own BLOCKING reporting under V1a's blocking_pass).
        entry["v1b_blocking_pass"] = {
            e: per_pass[e] for e in ("mpnet", "bge_large", "finlang")
        }

        # Cross-encoder agreement across all 4 encoders.
        all_picks = [per_encoder_picks[enc][row] for enc in encoders]
        if any(p is None for p in all_picks):
            agreement = {
                "exact_secret_id":  False,
                "same_domain":      False,
                "same_tier":        False,
                "all_blocking_pass": all(per_pass.values()),
            }
        else:
            sids = [p[0] for p in all_picks]
            picked_secrets = [sec_by_id[sid] for sid in sids]
            agreement = {
                "exact_secret_id":  len(set(sids)) == 1,
                "same_domain":      len({s["domain"] for s in picked_secrets}) == 1,
                "same_tier":        len({s["level"] for s in picked_secrets}) == 1,
                "all_blocking_pass": all(per_pass.values()),
            }
        entry["cross_encoder_agreement"] = agreement
        for ak in agreement_counts:
            if agreement[ak]:
                agreement_counts[ak] += 1

    # Per-encoder BLOCKING report
    print()
    print("--- Per-encoder BLOCKING pass/fail ---")
    print(f"  {'enc':10s} {'pass':>6s} {'fail':>6s} {'rate':>8s}  {'window':>18s}")
    escalation_flags: List[Tuple[str, int, int, float]] = []
    for enc in encoders:
        lo, hi = encoder_windows[enc]
        passed = per_encoder_pass_count[enc]
        failed = n - passed
        rate = failed / n
        print(f"  {enc:10s} {passed:6d} {failed:6d}  {100*rate:5.1f}%   "
              f"[{lo:.2f}, {hi:.2f}]")
        if rate >= 0.30:
            escalation_flags.append((enc, failed, n, rate))

    any_fail_count = sum(1 for h in hard_negs
                          if not all(h["v1b_blocking_pass"].values()))
    any_fail_rate = any_fail_count / n
    print(f"  any-of-3-secondary-fails: {any_fail_count}/{n} = "
          f"{100*any_fail_rate:.1f}%")
    if any_fail_rate >= 0.30:
        escalation_flags.append(("ANY_SECONDARY", any_fail_count, n, any_fail_rate))

    # Cross-encoder agreement
    print()
    print("--- Cross-encoder agreement (4 encoders) ---")
    for ak in ("exact_secret_id", "same_domain", "same_tier", "all_blocking_pass"):
        c = agreement_counts[ak]
        print(f"  {ak:22s} {c:>3d}/{n}  =  {100*c/n:5.1f}%")

    # Per-encoder cosine stats (V2 §4.4)
    cosine_stats: Dict[str, Any] = {}
    print()
    print("--- Per-encoder cosine stats (V2 §4.4 observed) ---")
    print(f"  {'enc':10s} {'mean':>7s} {'P10':>7s} {'P90':>7s}  n")
    for enc in encoders:
        cs = np.array(per_encoder_cosines[enc])
        if len(cs) == 0:
            cosine_stats[enc] = None
            continue
        mean_v = float(cs.mean())
        p10 = float(np.percentile(cs, 10))
        p90 = float(np.percentile(cs, 90))
        cosine_stats[enc] = {"mean": round(mean_v, 4), "p10": round(p10, 4),
                             "p90": round(p90, 4), "n": int(len(cs))}
        print(f"  {enc:10s} {mean_v:7.4f} {p10:7.4f} {p90:7.4f}  {len(cs)}")

    # Substantial-deviation check (V2 §4.4 last paragraph)
    deviation_flags: List[Tuple[str, float]] = []
    print()
    print("--- Substantial-deviation check (V2 §4.4: |obs_mean - "
          "expected_midpoint| > 0.10 triggers V2.5 plan revision) ---")
    print(f"  {'enc':10s} {'obs_mean':>9s} {'mid':>7s} {'delta':>8s}  flag")
    for enc in encoders:
        if cosine_stats[enc] is None:
            continue
        obs_mean = cosine_stats[enc]["mean"]
        mid = EXPECTED_BAND_MIDPOINT[enc]
        delta = obs_mean - mid
        flag = "DEVIATION" if abs(delta) > 0.10 else ""
        print(f"  {enc:10s} {obs_mean:9.4f} {mid:7.4f} {delta:+8.4f}  {flag}")
        if abs(delta) > 0.10 and enc != "minilm":  # MiniLM band is design, not predicted
            deviation_flags.append((enc, delta))

    # Per-encoder outliers detail
    print()
    print("--- Per-encoder outliers ---")
    for enc in ("mpnet", "bge_large", "finlang"):
        outs = per_encoder_outliers[enc]
        print(f"  [{enc}] {len(outs)} outlier(s)")
        for o in outs[:25]:
            print(f"    {o['_id']:14s} cat={o['category']}  cos={o['cosine']:.4f}  "
                  f"{o['direction']:>5s}  → {o['target_secret_id']}")
        if len(outs) > 25:
            print(f"    (+{len(outs)-25} more)")

    # Atomic write
    print()
    print("--- Atomic in-place update ---")
    bak_path = HARD_NEG_PATH.with_suffix(HARD_NEG_PATH.suffix + ".bak")
    shutil.copy2(HARD_NEG_PATH, bak_path)
    print(f"  backup: {bak_path.relative_to(REPO_ROOT)}")

    persisted = []
    for h in hard_negs:
        clean = {k: v for k, v in h.items()
                 if not k.startswith("_v1a_") and not k.startswith("_v1b_")}
        persisted.append(clean)
    write_jsonl(HARD_NEG_PATH, persisted)

    verify = load_jsonl(HARD_NEG_PATH)
    if len(verify) != 65:
        print(f"  ! WRITE VERIFY FAILED: read back {len(verify)} entries; "
              f"restoring from .bak")
        shutil.copy2(bak_path, HARD_NEG_PATH)
        return 1
    new_fields = [
        "closest_secret_id_mpnet_90", "closest_cosine_mpnet_90",
        "closest_secret_id_bge_large_90", "closest_cosine_bge_large_90",
        "closest_secret_id_finlang_90", "closest_cosine_finlang_90",
        "v1b_blocking_pass", "cross_encoder_agreement",
    ]
    print(f"  re-read: {len(verify)} entries")
    for fld in new_fields:
        pop = sum(1 for v in verify if v.get(fld) is not None)
        print(f"  {fld:36s} populated: {pop}/{n}")

    # JSON report
    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "1.E.E1.3.4 — V1b",
        "encoders": list(encoders),
        "scope_note": (
            "4 encoders × 90-entry corpus only. 60-entry deferred per S7 "
            "(corpus-version disjointness; see DOCUMENTED_FINDINGS)."
        ),
        "pinned_revisions": {
            ENCODER_NAMES[e]: PINNED_REVISIONS[ENCODER_NAMES[e]] for e in encoders
        },
        "encoder_windows":         {e: list(encoder_windows[e]) for e in encoders},
        "expected_band_midpoint":  {e: round(EXPECTED_BAND_MIDPOINT[e], 4) for e in encoders},
        "top_k": TOP_K,
        "hard_neg_count": n,
        "secret_tier_filter": sorted(SECRET_TIER_ALLOWED),
        "per_encoder_blocking_pass_count": dict(per_encoder_pass_count),
        "per_encoder_fail_count": {e: n - per_encoder_pass_count[e] for e in encoders},
        "per_encoder_fail_rate":  {e: round(1 - per_encoder_pass_count[e]/n, 4)
                                     for e in encoders},
        "any_secondary_fails_count": any_fail_count,
        "any_secondary_fails_rate":  round(any_fail_rate, 4),
        "cross_encoder_agreement_summary": {
            ak: f"{agreement_counts[ak]}/{n}" for ak in agreement_counts
        },
        "cross_encoder_agreement_rate": {
            ak: round(agreement_counts[ak]/n, 4) for ak in agreement_counts
        },
        "cosine_stats_per_encoder": cosine_stats,
        "deviation_from_expected_midpoint": {
            e: round(cosine_stats[e]["mean"] - EXPECTED_BAND_MIDPOINT[e], 4)
            if cosine_stats[e] else None
            for e in encoders
        },
        "deviation_flags": [
            {"encoder": e, "delta": round(d, 4)} for e, d in deviation_flags
        ],
        "escalation_flags": [
            {"encoder": e, "failed": f, "total": t, "rate": round(r, 4)}
            for e, f, t, r in escalation_flags
        ],
        "per_encoder_outliers":   per_encoder_outliers,
        "fallback_count_per_encoder": fallback_count,
        "documented_findings":    DOCUMENTED_FINDINGS,
        "wall_seconds": round(time.time() - t_start, 2),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"v1b_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  report: {report_path.relative_to(REPO_ROOT)}")

    # Surface escalations
    if escalation_flags or deviation_flags:
        print()
        print("=== ESCALATION FLAGS RAISED ===")
        for e, f, t, r in escalation_flags:
            print(f"  [BLOCKING-fail >= 30%] {e}: {f}/{t} = {100*r:.1f}%")
        for e, d in deviation_flags:
            print(f"  [substantial deviation] {e}: delta={d:+.4f}")
        print("  → Per Q1 STRICT-with-paper-escalation: pause for ratification "
              "of S-numbered finding text before adding to DOCUMENTED_FINDINGS.")

    print(f"\nV1b complete in {report['wall_seconds']:.2f}s.")
    return 0


def run_v5b() -> int:
    """E1.3.5 — V5b exact-string match + R6 corpus-gen LLM leakage audit log.

    Per V2 §4.1 V5b + §7.2 R6 spec:
    - STRICT character-by-character equality (no normalization). Near-verbatim
      leaks (cosine ≈ 1.0) are caught at V1a/V1b level (defense-in-depth).
    - Compare hn.query AND hn.rationale against secret.text from BOTH
      secrets.jsonl (60-entry legacy) AND secrets_v2.jsonl (90-entry v2).
    - exact_match_against_secret bool added to each JSONL entry.
    - R6 audit log (`eval/results/phase1_E/validation/r6_audit.jsonl`)
      captures Layer 2 (V5b hits) + Layer 5 (V1b ≥2-encoder above-band
      paraphrase signatures). Layer 4 (manual drops) appended later at E1.4.
    """
    print("=== E1.3.5 V5b — exact-string match + R6 audit log (--run-v5b) ===")
    print()
    t_start = time.time()

    hard_negs = load_jsonl(HARD_NEG_PATH)
    if len(hard_negs) != 65:
        print(f"  ! UNEXPECTED: expected 65 hard-neg entries, got {len(hard_negs)}")
        return 1

    secrets_90 = load_jsonl(SECRETS_V2_PATH)
    secrets_60 = load_jsonl(SECRETS_60_PATH)
    print(f"  secrets_v2 (90-entry canonical): {len(secrets_90)} entries")
    print(f"  secrets (60-entry legacy):       {len(secrets_60)} entries")

    # Build secret.text → list of (secret_id, corpus_label) for O(1) exact match
    secret_text_index: Dict[str, List[Tuple[str, str]]] = {}
    for s in secrets_90:
        secret_text_index.setdefault(s["text"], []).append((s["_id"], "secrets_v2.jsonl"))
    for s in secrets_60:
        secret_text_index.setdefault(s["text"], []).append((s["_id"], "secrets.jsonl"))
    print(f"  built secret_text_index with {len(secret_text_index)} unique texts "
          f"across both corpora")

    # Layer 2 — V5b exact-string match
    print()
    print("--- Layer 2: V5b exact-string match check ---")
    v5b_hits: List[Dict[str, Any]] = []
    for entry in hard_negs:
        query_hits = secret_text_index.get(entry["query"], [])
        rationale_hits = []
        rationale = entry.get("rationale", "")
        if rationale.strip():
            rationale_hits = secret_text_index.get(rationale, [])
        has_match = bool(query_hits or rationale_hits)
        entry["exact_match_against_secret"] = has_match
        if query_hits:
            v5b_hits.append({
                "hard_neg_id": entry["_id"],
                "match_type": "exact_string_query",
                "matched_secret_ids": [h[0] for h in query_hits],
                "matched_secret_corpora": list({h[1] for h in query_hits}),
                "category": entry["category"],
                "domain": entry["domain"],
            })
        if rationale_hits:
            v5b_hits.append({
                "hard_neg_id": entry["_id"],
                "match_type": "exact_string_rationale",
                "matched_secret_ids": [h[0] for h in rationale_hits],
                "matched_secret_corpora": list({h[1] for h in rationale_hits}),
                "category": entry["category"],
                "domain": entry["domain"],
            })

    pop = sum(1 for e in hard_negs if e.get("exact_match_against_secret") is True)
    pop_false = sum(1 for e in hard_negs if e.get("exact_match_against_secret") is False)
    print(f"  exact_match_against_secret populated: True={pop}, False={pop_false}, "
          f"Σ={pop+pop_false}/65")
    print(f"  V5b hits: {len(v5b_hits)} (across query + rationale; expected 0)")

    # Layer 5 — V1b ≥2-encoder above-band paraphrase signatures
    # Above-band thresholds: encoder window's upper bound (per V2 §2.5).
    above_band_threshold = {
        "minilm":    GLOBAL_BLOCKING_BAND[1],   # 0.65
        "mpnet":     STEP2_WINDOWS["mpnet"][1], # 0.52
        "bge_large": STEP2_WINDOWS["bge_large"][1], # 0.90
        "finlang":   STEP2_WINDOWS["finlang"][1],   # 0.65
    }

    print()
    print("--- Layer 5: V1b ≥2-encoder above-band paraphrase signatures ---")
    layer5_candidates: List[Dict[str, Any]] = []
    for entry in hard_negs:
        cosines = {
            enc: entry.get(f"closest_cosine_{enc}_90")
            for enc in ("minilm", "mpnet", "bge_large", "finlang")
        }
        if any(c is None for c in cosines.values()):
            continue  # Skip entries with incomplete V1a/V1b data
        above_band = [enc for enc, c in cosines.items()
                      if c > above_band_threshold[enc]]
        if len(above_band) >= 2:
            layer5_candidates.append({
                "hard_neg_id": entry["_id"],
                "category": entry["category"],
                "domain": entry["domain"],
                "above_band_encoders": above_band,
                "cosines": cosines,
                "closest_secret_ids": {
                    enc: entry.get(f"closest_secret_id_{enc}_90")
                    for enc in ("minilm", "mpnet", "bge_large", "finlang")
                },
            })
            print(f"  {entry['_id']:14s} cat={entry['category']} "
                  f"above_band={above_band} "
                  f"({len(above_band)} encoder{'s' if len(above_band)>1 else ''})")
    print(f"  Layer 5 candidates: {len(layer5_candidates)}")

    # Per-entry disposition for Layer 5 (action-1a content review status)
    action_1a_ruled = {
        "HN_GEN_051": (
            "V1a Action 1a manual content review 2026-05-21 ruled NON-paraphrase. "
            "Secret text describes one fund's operational system; query asks "
            "textbook definition of factor neutrality."
        ),
        "HN_GEN_056": (
            "V1a Action 1a manual content review 2026-05-21 ruled NON-paraphrase. "
            "Query asks comparative methodology (decay + cadence); secret describes "
            "combined-source strategy (we use both together)."
        ),
    }

    # Compose R6 audit log entries
    timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    audit_entries: List[Dict[str, Any]] = []
    counter = 1
    # Layer 5 first (per Q5 ratification ordering)
    for c in layer5_candidates:
        hn_id = c["hard_neg_id"]
        if hn_id in action_1a_ruled:
            disposition = "retained_non_paraphrase"
            disposition_evidence = action_1a_ruled[hn_id]
            disposition_review_required_by = None
        else:
            disposition = "requires_content_review_at_E1_4"
            disposition_review_required_by = "E1.4_regeneration_phase"
            n_above = len(c["above_band_encoders"])
            disposition_evidence = (
                f"Not yet content-reviewed. {n_above} encoders "
                f"({', '.join(c['above_band_encoders'])}) above-band. "
                f"Audit-grade forensic record per V2 §7.2 Layer 5."
            )
        audit_entries.append({
            "audit_id":            f"R6_AUDIT_{counter:03d}",
            "source_layer":        "Layer_5_V1b_paraphrase_signature",
            "hard_neg_id":         hn_id,
            "category":            c["category"],
            "domain":              c["domain"],
            "match_type":          "multi_encoder_above_band",
            "matched_secret_ids":  sorted({s for s in c["closest_secret_ids"].values()
                                            if s is not None}),
            "matched_secret_corpus": "secrets_v2.jsonl",  # V1b is 90-entry only
            "evidence": {
                "encoders_above_band": c["above_band_encoders"],
                "cosines":             c["cosines"],
                "closest_secret_ids":  c["closest_secret_ids"],
                "above_band_thresholds": above_band_threshold,
            },
            "disposition":         disposition,
            "disposition_evidence": disposition_evidence,
            "disposition_review_required_by": disposition_review_required_by,
            "findings_reference":  [
                "S11_cat_d_e_cross_encoder_above_band_concentration",
                "S12_v5b_zero_corpus_contamination",
            ],
            "timestamp_utc":       timestamp_utc,
        })
        counter += 1

    # Layer 2 V5b hits (if any)
    for hit in v5b_hits:
        audit_entries.append({
            "audit_id":            f"R6_AUDIT_{counter:03d}",
            "source_layer":        "Layer_2_V5b",
            "hard_neg_id":         hit["hard_neg_id"],
            "category":            hit["category"],
            "domain":              hit["domain"],
            "match_type":          hit["match_type"],
            "matched_secret_ids":  hit["matched_secret_ids"],
            "matched_secret_corpus": ("both" if len(hit["matched_secret_corpora"]) > 1
                                       else hit["matched_secret_corpora"][0]),
            "evidence": {
                "match_field": ("query" if hit["match_type"] == "exact_string_query"
                                else "rationale"),
                "leak_classification": "Layer_1_prompt_template_failure_candidate",
            },
            "disposition":         "drop_immediate",
            "disposition_evidence": (
                "V2 §4.3 V5b BLOCKING: 'Drop immediately; flag R6 audit log entry'. "
                "V2.5 plan revision triggered per V2 §7.2 Layer 5."
            ),
            "disposition_review_required_by": "E1.4_regeneration_phase",
            "findings_reference":  ["S12_v5b_corpus_contamination_event"],
            "timestamp_utc":       timestamp_utc,
        })
        counter += 1

    # Write R6 audit log
    print()
    print("--- R6 audit log write ---")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with R6_AUDIT_PATH.open("w", encoding="utf-8") as f:
        for ae in audit_entries:
            f.write(json.dumps(ae, ensure_ascii=False) + "\n")
    print(f"  wrote {len(audit_entries)} entries to "
          f"{R6_AUDIT_PATH.relative_to(REPO_ROOT)}")
    layer_counts = {"Layer_2_V5b": 0, "Layer_5_V1b_paraphrase_signature": 0,
                    "Layer_4_manual_drop": 0}
    for ae in audit_entries:
        layer_counts[ae["source_layer"]] = layer_counts.get(ae["source_layer"], 0) + 1
    for lyr, c in layer_counts.items():
        print(f"    {lyr}: {c}")

    # Atomic JSONL write (only adds exact_match_against_secret field)
    print()
    print("--- Atomic JSONL in-place update ---")
    bak_path = HARD_NEG_PATH.with_suffix(HARD_NEG_PATH.suffix + ".bak")
    shutil.copy2(HARD_NEG_PATH, bak_path)
    print(f"  backup: {bak_path.relative_to(REPO_ROOT)}")
    persisted = []
    for h in hard_negs:
        clean = {k: v for k, v in h.items()
                 if not k.startswith("_v1a_") and not k.startswith("_v1b_")}
        persisted.append(clean)
    write_jsonl(HARD_NEG_PATH, persisted)
    verify = load_jsonl(HARD_NEG_PATH)
    if len(verify) != 65:
        print(f"  ! WRITE VERIFY FAILED: {len(verify)} entries; restoring")
        shutil.copy2(bak_path, HARD_NEG_PATH)
        return 1
    field_pop = sum(1 for v in verify if "exact_match_against_secret" in v)
    print(f"  re-read: {len(verify)} entries; "
          f"exact_match_against_secret present: {field_pop}/65")
    true_count = sum(1 for v in verify if v.get("exact_match_against_secret") is True)
    print(f"  exact_match_against_secret=True: {true_count}/65")

    # V5b results — merged into a fresh v1b_<ts>.json artifact (per
    # 2026-05-22 ruling, V5b results are appended to v1b canonical
    # artifact rather than written to a separate v5b_*.json file).
    v5b_section = {
        "v5b_phase":                "1.E.E1.3.5 — V5b appended",
        "v5b_generated_at":         timestamp_utc,
        "v5b_scope_note": (
            "STRICT character-equality check. Both corpora "
            "(secrets.jsonl 60 + secrets_v2.jsonl 90 = 150 secrets). "
            "Compared hn.query AND hn.rationale against secret.text. "
            "Near-verbatim leaks caught by V1a/V1b cosine layers."
        ),
        "v5b_hard_neg_count":       65,
        "v5b_secrets_60_count":     len(secrets_60),
        "v5b_secrets_90_count":     len(secrets_90),
        "v5b_secrets_unique_text_count": len(secret_text_index),
        "v5b_match_count":          len(v5b_hits),
        "v5b_match_details":        v5b_hits,
        "v5b_exact_match_true_count":  true_count,
        "v5b_exact_match_false_count": 65 - true_count,
        "v5b_layer_5_paraphrase_candidates_count": len(layer5_candidates),
        "v5b_layer_5_above_band_threshold": above_band_threshold,
        "r6_audit_log_total_entries":  len(audit_entries),
        "r6_audit_log_per_layer":      layer_counts,
        "r6_audit_log_path":           str(R6_AUDIT_PATH.relative_to(REPO_ROOT)),
        "v5b_wall_seconds": round(time.time() - t_start, 2),
    }

    # Locate most-recent v1b artifact, merge V5b section, write new v1b_<ts>.json
    prior_v1b_files = sorted(OUTPUT_DIR.glob("v1b_*.json"))
    if not prior_v1b_files:
        print("  ! no prior v1b_*.json found — V5b requires V1b to have run first")
        return 1
    latest_v1b = prior_v1b_files[-1]
    with latest_v1b.open("r", encoding="utf-8") as f:
        merged = json.load(f)
    merged.update(v5b_section)
    # Refresh DOCUMENTED_FINDINGS to current state (may include S12 added
    # after the prior v1b artifact was written).
    merged["documented_findings"] = DOCUMENTED_FINDINGS
    merged["generated_at"] = timestamp_utc  # canonical-ts now reflects V5b
    new_v1b_path = OUTPUT_DIR / f"v1b_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    with new_v1b_path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"  merged V5b into v1b canonical: "
          f"{new_v1b_path.relative_to(REPO_ROOT)}")
    print(f"  (prior v1b kept as historical: "
          f"{latest_v1b.relative_to(REPO_ROOT)})")

    # Escalation surface
    if v5b_hits:
        print()
        print("=== V5b CORPUS-CONTAMINATION ALERT ===")
        print(f"  {len(v5b_hits)} exact-string match(es) found.")
        print("  V2 §7.2 Layer 5: V2.5 plan revision triggered for root-cause "
              "analysis on Layer 1 prompt template.")
        print("  → Pause for user ratification of S12 paper-finding text.")

    print(f"\nV5b complete in {v5b_section['v5b_wall_seconds']:.2f}s.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="E1.3.1 mode: verify infrastructure only.")
    parser.add_argument("--run-v1a", action="store_true",
                        help="E1.3.2 mode: run V1a (cosine band + atomic write).")
    parser.add_argument("--run-v1b", action="store_true",
                        help="E1.3.4 mode: run V1b (4-encoder cosine band + agreement).")
    parser.add_argument("--run-v5b", action="store_true",
                        help="E1.3.5 mode: run V5b (exact-string match + R6 audit log).")
    args = parser.parse_args()

    if not (args.check_only or args.run_v1a or args.run_v1b or args.run_v5b):
        parser.error("specify --check-only / --run-v1a / --run-v1b / --run-v5b")

    if args.check_only:
        rc = run_check_only()
        if rc != 0:
            return rc

    if args.run_v1a:
        rc = run_v1a()
        if rc != 0:
            return rc

    if args.run_v1b:
        rc = run_v1b()
        if rc != 0:
            return rc

    if args.run_v5b:
        return run_v5b()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
