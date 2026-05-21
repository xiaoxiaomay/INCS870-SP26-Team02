import os
import yaml
from pathlib import Path

# -----------------------------------------------------------------------------
# Reproducibility pins (Phase-1 item 1.0b).
# Keep this dict authoritative — every SentenceTransformer instantiation in
# the codebase reads its revision from here via get_pinned_revision().
# Update only when a deliberate model upgrade is made; record the change in
# REPRODUCIBILITY.md.
# -----------------------------------------------------------------------------
PINNED_REVISIONS = {
    # HuggingFace commit hash of all-MiniLM-L6-v2 currently used in v9
    # evaluation. Verified via ~/.cache/huggingface/hub/.../refs/main on
    # 2026-05-08. Pinning this prevents the upstream-update drift documented
    # in V9_REPRODUCTION.md §3.
    "sentence-transformers/all-MiniLM-L6-v2": "c9745ed1d9f207416be6d2e6f8de32d1f16199bf",
    # Phase-1.F encoder ablation candidates (registered 2026-05-09).
    # Each revision is HF main as of 2026-05-09, captured via
    # `git ls-remote https://huggingface.co/<model> refs/heads/main`.
    # Dim values verified via scripts/probe_encoder.py M1.0 / M1.4.
    # See PHASE_1F_PLAN_V2.md §1.3 for context.
    "sentence-transformers/all-mpnet-base-v2":
        "e8c3b32edf5434bc2275fc9bab85f82640a19130",  # dim=768
    "BAAI/bge-large-en-v1.5":
        "d4aa6901d3a41ba39fb536a557fa166f842b0e09",  # dim=1024 (M1.0 PRIMARY: 702.8 MB peak RSS, well under 60% × 8 GB)
    "BAAI/bge-base-en-v1.5":
        "a5beb1e3e68b9ab74eb54cfd186867f64f240e1a",  # dim=768 (Q2 fallback for bge-large; not exercised — bge-large PASSED probe)
    "FinLang/finance-embeddings-investopedia":
        "37d7594d02e3d656a241e099e39ac50ab921f999",  # dim=768 (M1.4 verified)
}

# Dated OpenAI model snapshot for stable reproduction. Replace the alias
# "gpt-4o-mini" everywhere with this dated form.
#
# Reproducibility design (B2, applied 2026-05-09): callers MUST resolve
# the LLM model name via `cfg.get("openai_model") or PINNED_OPENAI_MODEL`.
# The historical `os.getenv("OPENAI_MODEL")`-first chain was removed
# because a stale env var (e.g., `.env` carrying an unpinned alias)
# silently overrode the dated snapshot in config and broke
# `summary.json`'s provenance contract. To use a different LLM, edit
# `config*.yaml:openai_model` or pass `--config <other.yaml>`; do NOT
# set the `OPENAI_MODEL` env var. Verified end-to-end by
# `scripts/verify_repro_pins.py` (three-layer check: static / runtime /
# end-to-end). See REPRODUCIBILITY.md §6 change-log entry for context.
PINNED_OPENAI_MODEL = "gpt-4o-mini-2024-07-18"

# Phase 1.E E1.2 hard-negative query generation (pinned 2026-05-12).
# Used by scripts/generate_hard_negatives.py (E1.3).
# Smoke-tested 2026-05-12 (22 tokens, $0.00002). Pricing tracked in
# scripts/repro_full_pipeline.py (PRICE_INPUT_PER_1M_GPT5MINI=0.25,
# PRICE_OUTPUT_PER_1M_GPT5MINI=2.00 per 1M tokens, pinned 2026-05-12).
# Reproducibility contract: callers MUST resolve via
# cfg.get("openai_generation_model") or PINNED_OPENAI_GENERATION_MODEL_E1_2.
# No env-var sidechannel (mirrors B2 defender model contract).
PINNED_OPENAI_GENERATION_MODEL_E1_2 = "gpt-5-mini-2025-08-07"


def get_pinned_revision(model_name: str):
    """Return pinned HF revision for a known model, else None (HF default)."""
    return PINNED_REVISIONS.get(model_name)


def get_project_root() -> Path:
    """动态获取项目根目录"""
    return Path(__file__).parent.parent

def load_global_config():
    root = get_project_root()
    config_path = root / "config.yaml"
    with open(config_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)

def use_postgres() -> bool:
    """Check if PostgreSQL should be used. Defaults to False if USE_POSTGRES=false."""
    val = os.environ.get("USE_POSTGRES", "true").lower()
    return val not in ("false", "0", "no", "off")

def get_db_params():
    """获取数据库连接参数"""
    cfg = load_global_config()
    db = cfg.get("db", {})
    return {
        "host": os.environ.get("DB_HOST", db.get("host", "localhost")),
        "database": os.environ.get("DB_NAME", db.get("name", "sentinel_db")),
        "user": os.environ.get("DB_USER", db.get("user", "postgres")),
        "password": os.environ.get("DB_PASSWORD", db.get("password", "")),
        "port": int(os.environ.get("DB_PORT", db.get("port", 5432)))
    }

def get_engine_configs():
    """获取引擎所需的各种子配置"""
    cfg = load_global_config()
    return {
        "embedding": cfg.get("embedding", {}),
        "paths": cfg.get("paths", {}),
        "audit": cfg.get("audit", {})
    }