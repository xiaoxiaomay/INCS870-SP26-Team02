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
}

# Dated OpenAI model snapshot for stable reproduction. Replace the alias
# "gpt-4o-mini" everywhere with this dated form.
PINNED_OPENAI_MODEL = "gpt-4o-mini-2024-07-18"


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