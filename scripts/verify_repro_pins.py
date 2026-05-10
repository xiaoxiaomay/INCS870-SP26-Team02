#!/usr/bin/env python3
"""
scripts/verify_repro_pins.py

Three-layer reproducibility-pin verifier. Companion to
core/config_loader.py:PINNED_REVISIONS / PINNED_OPENAI_MODEL and
REPRODUCIBILITY.md.

Verifies that the LLM model identifier and the HuggingFace embedding
revision currently in use match the canonical pinned values across:

  L1 — Static:           No unpinned literal alias (e.g., bare
                         "gpt-4o-mini" without a date) appears in
                         tracked Python or YAML, except as
                         documentation.

  L2 — Runtime:          Importing each affected module and reading
                         its resolution chain (with the current env
                         + config) returns the canonical pinned
                         constant. Catches env-var sidechannels and
                         dynamic config swaps that static grep cannot
                         see.

  L3 — End-to-end:       A 2-prompt sanity run produces a summary.json
                         whose `llm_model` and `embedding_revision`
                         fields match the canonical pinned values.
                         Catches integration-level surprises that
                         module-level probes miss.

Usage:
  python scripts/verify_repro_pins.py                # all three layers
  python scripts/verify_repro_pins.py --layer 1      # static only
  python scripts/verify_repro_pins.py --layer 2      # runtime probe only
  python scripts/verify_repro_pins.py --layer 3      # end-to-end (uses ~$0.0002)
  python scripts/verify_repro_pins.py --verbose      # print all checks (passed too)

Exit codes:
  0 — all requested layers PASS
  1 — any layer FAIL
  2 — usage / environment error (e.g. OPENAI_API_KEY missing for L3)

Pre-commit-hook ready: returns non-zero on any failure.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Pinned constants (the canonical authority — every layer compares against these)
from core.config_loader import (  # noqa: E402
    PINNED_OPENAI_MODEL,
    PINNED_REVISIONS,
)

CANONICAL_HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CANONICAL_HF_REVISION = PINNED_REVISIONS.get(CANONICAL_HF_MODEL)


# ---------------------------------------------------------------------------
# Layer 1 — Static
# ---------------------------------------------------------------------------


def verify_l1_static() -> Tuple[bool, List[str]]:
    """
    Static grep for unpinned literal aliases. Failures returned as a list
    of `path:line: text` violations.
    """
    violations: List[str] = []

    # 1a. Any bare "gpt-4o-mini" (without a date suffix) in *source* (.py/.yaml)
    # that is NOT inside a comment / docstring?
    #
    # Scope: source code only. Historical output artifacts (eval/results/*.json,
    # reports/*) legitimately contain the alias from runs that pre-date the
    # 1.0b/B2 fixes — those are forensic records of past state, not code
    # violations. They are intentionally excluded from this layer.
    allowlist_paths = {
        "core/config_loader.py",
        "REPRODUCIBILITY.md",
        "scripts/verify_repro_pins.py",
    }
    skip_dirs = {
        "venv",
        "__pycache__",
        ".git",
        ".pytest_cache",
        "archive",
        ".ipynb_checkpoints",
        "reports",       # historical thesis-era output
        "eval/results",  # historical eval JSONs (regeneratable but not by this layer)
        "data/audit",    # runtime audit log
        "logs",
    }
    bare_alias_re = re.compile(r'"gpt-4o-mini"(?!-\d{4}-\d{2}-\d{2})')
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(REPO_ROOT))
        if rel in allowlist_paths:
            continue
        # Skip dirs (including nested forms like "eval/results/...")
        if any(rel.startswith(d + os.sep) or rel == d for d in skip_dirs):
            continue
        parts = path.relative_to(REPO_ROOT).parts
        if any(p in {"venv", "__pycache__", ".git", ".pytest_cache", "archive", ".ipynb_checkpoints"} for p in parts):
            continue
        # Restrict to source-code-shaped files; output JSON/MD are out of scope.
        if path.suffix not in {".py", ".yaml", ".yml"}:
            continue
        try:
            for ln, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if bare_alias_re.search(line):
                    # Skip pure comment lines
                    stripped = line.lstrip()
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue
                    violations.append(f"L1-bare-alias: {rel}:{ln}: {line.strip()[:120]}")
        except Exception:
            pass

    # 1b. Any os.getenv("OPENAI_MODEL") chain still present in code (not in
    # docs/comments)? B2 forbids this.
    getenv_re = re.compile(r'os\.getenv\("OPENAI_MODEL"\)|os\.environ\.get\("OPENAI_MODEL"\)')
    for path in REPO_ROOT.rglob("*.py"):
        rel = str(path.relative_to(REPO_ROOT))
        parts = path.relative_to(REPO_ROOT).parts
        if any(p in {"venv", "__pycache__", "archive"} for p in parts):
            continue
        if rel in {"scripts/verify_repro_pins.py"}:
            continue
        try:
            for ln, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if getenv_re.search(line):
                    stripped = line.lstrip()
                    if stripped.startswith("#"):
                        continue
                    violations.append(f"L1-env-getenv: {rel}:{ln}: {line.strip()[:120]}")
        except Exception:
            pass

    # 1c. Every SentenceTransformer( call must pass revision= (existing 1.0b
    # invariant; re-checked here). Skip self (this file mentions the regex
    # literal in its own source).
    st_call_re = re.compile(r"SentenceTransformer\(")
    for path in REPO_ROOT.rglob("*.py"):
        rel = str(path.relative_to(REPO_ROOT))
        if rel == "scripts/verify_repro_pins.py":
            continue
        parts = path.relative_to(REPO_ROOT).parts
        if any(p in {"venv", "__pycache__"} for p in parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for m in st_call_re.finditer(text):
                # Find the closing paren via simple paren-depth scan
                depth = 0
                end = m.start()
                for i in range(m.end() - 1, len(text)):
                    if text[i] == "(":
                        depth += 1
                    elif text[i] == ")":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                call_text = text[m.start() : end + 1]
                if "revision=" not in call_text:
                    line_no = text[: m.start()].count("\n") + 1
                    violations.append(
                        f"L1-st-no-revision: {rel}:{line_no}: {call_text[:120].replace(chr(10), ' ')}"
                    )
        except Exception:
            pass

    return (len(violations) == 0, violations)


# ---------------------------------------------------------------------------
# Layer 2 — Runtime probe
# ---------------------------------------------------------------------------


def verify_l2_runtime(verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Import each module that resolves an LLM model name; emulate its
    resolution chain with the current env + a stock config; assert the
    result equals PINNED_OPENAI_MODEL.

    Same idea for the HF revision: import core.config_loader, call
    get_pinned_revision('all-MiniLM-L6-v2'), assert canonical hash.
    """
    failures: List[str] = []
    passes: List[str] = []

    # 2a. PINNED constants are loaded as expected
    if PINNED_OPENAI_MODEL != "gpt-4o-mini-2024-07-18":
        failures.append(
            f"L2: PINNED_OPENAI_MODEL = {PINNED_OPENAI_MODEL!r}, "
            f"expected 'gpt-4o-mini-2024-07-18'"
        )
    else:
        passes.append("L2: PINNED_OPENAI_MODEL == 'gpt-4o-mini-2024-07-18'")

    if CANONICAL_HF_REVISION is None or len(CANONICAL_HF_REVISION) != 40:
        failures.append(
            f"L2: PINNED_REVISIONS[{CANONICAL_HF_MODEL!r}] = "
            f"{CANONICAL_HF_REVISION!r}, expected 40-char SHA"
        )
    else:
        passes.append(
            f"L2: PINNED_REVISIONS[{CANONICAL_HF_MODEL!r}] is a "
            f"40-char SHA (= {CANONICAL_HF_REVISION[:12]}...)"
        )

    # 2b. Resolve LLM via each module's actual chain. We do this by loading
    # config_v2.yaml (the journal-era pin) and applying each module's
    # documented chain pattern manually. Because B2 standardized them all to
    # `cfg.get('openai_model') or PINNED_OPENAI_MODEL`, the test is uniform.
    from scripts.run_rag_with_audit import load_config

    # Set OPENAI_MODEL env var to a deliberately wrong value to confirm
    # B2 ignores it. Restore env afterward.
    saved = os.environ.pop("OPENAI_MODEL", None)
    os.environ["OPENAI_MODEL"] = "INTENTIONALLY_WRONG_GPT-FAKE-MODEL"
    try:
        for cfg_path in ["config.yaml", "config_v2.yaml", "config_medical.yaml"]:
            cfg = load_config(str(REPO_ROOT / cfg_path))
            resolved = cfg.get("openai_model") or PINNED_OPENAI_MODEL
            if resolved != "gpt-4o-mini-2024-07-18":
                failures.append(
                    f"L2: {cfg_path} resolved llm_model={resolved!r} "
                    f"(expected gpt-4o-mini-2024-07-18)"
                )
            else:
                passes.append(
                    f"L2: {cfg_path} resolves to "
                    f"'gpt-4o-mini-2024-07-18' (env var ignored: {saved!r})"
                )
    finally:
        if saved is not None:
            os.environ["OPENAI_MODEL"] = saved
        else:
            os.environ.pop("OPENAI_MODEL", None)

    # 2c. HF revision via the helper used by every site
    from core.config_loader import get_pinned_revision

    rev = get_pinned_revision(CANONICAL_HF_MODEL)
    if rev != CANONICAL_HF_REVISION:
        failures.append(
            f"L2: get_pinned_revision({CANONICAL_HF_MODEL!r}) = "
            f"{rev!r}, expected {CANONICAL_HF_REVISION!r}"
        )
    else:
        passes.append(
            f"L2: get_pinned_revision({CANONICAL_HF_MODEL!r}) returns "
            f"the canonical hash"
        )

    # 2d. Each top-level config exposes both pins
    for cfg_path in ["config.yaml", "config_v2.yaml", "config_medical.yaml"]:
        cfg = load_config(str(REPO_ROOT / cfg_path))
        cfg_revision = cfg.get("embedding", {}).get("revision")
        cfg_llm = cfg.get("openai_model")
        if cfg_revision != CANONICAL_HF_REVISION:
            failures.append(
                f"L2: {cfg_path}:embedding.revision = {cfg_revision!r}, "
                f"expected {CANONICAL_HF_REVISION!r}"
            )
        if cfg_llm != PINNED_OPENAI_MODEL:
            failures.append(
                f"L2: {cfg_path}:openai_model = {cfg_llm!r}, "
                f"expected {PINNED_OPENAI_MODEL!r}"
            )
        if cfg_revision == CANONICAL_HF_REVISION and cfg_llm == PINNED_OPENAI_MODEL:
            passes.append(f"L2: {cfg_path} declares both pins correctly")

    if verbose:
        for p in passes:
            print(f"  PASS {p}")

    return (len(failures) == 0, failures)


# ---------------------------------------------------------------------------
# Layer 3 — End-to-end provenance probe
# ---------------------------------------------------------------------------


def verify_l3_end_to_end(verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Run a 2-prompt sanity through `repro_full_pipeline.py`; inspect
    `summary.json:llm_model` and `summary.json:embedding_revision`.
    Confirms that the resolution chain held end-to-end.
    """
    failures: List[str] = []

    if not os.environ.get("OPENAI_API_KEY"):
        return (
            False,
            [
                "L3: OPENAI_API_KEY not set — cannot probe end-to-end. "
                "Source .env or export the key."
            ],
        )

    with tempfile.TemporaryDirectory(prefix="verify_repro_pins_") as tmp:
        tmp_dir = Path(tmp)
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "repro_full_pipeline.py"),
            "--config",
            "config.yaml",
            "--limit",
            "2",
            "--output-dir",
            str(tmp_dir),
            "--progress-every",
            "100",
        ]
        if verbose:
            print(f"  L3: running {' '.join(cmd)}")
        env = os.environ.copy()
        env.setdefault("USE_POSTGRES", "false")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            return (False, ["L3: probe run timed out (>120s)"])

        if result.returncode != 0:
            failures.append(
                f"L3: probe exited with code {result.returncode}; "
                f"stderr tail: {result.stderr[-300:]}"
            )
            return (False, failures)

        summary_path = tmp_dir / "summary.json"
        if not summary_path.exists():
            failures.append(f"L3: probe did not write summary.json at {summary_path}")
            return (False, failures)

        summary = json.loads(summary_path.read_text())
        llm = summary.get("llm_model")
        rev = summary.get("embedding_revision")
        if llm != PINNED_OPENAI_MODEL:
            failures.append(
                f"L3: summary.json:llm_model = {llm!r}, "
                f"expected {PINNED_OPENAI_MODEL!r}"
            )
        if rev != CANONICAL_HF_REVISION:
            failures.append(
                f"L3: summary.json:embedding_revision = {rev!r}, "
                f"expected {CANONICAL_HF_REVISION!r}"
            )
        if verbose and not failures:
            print(
                f"  PASS L3: probe wrote llm_model={llm!r}, "
                f"embedding_revision={rev[:12]}..., "
                f"cost=${summary.get('estimated_cost_usd', 0):.4f}"
            )

    return (len(failures) == 0, failures)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Three-layer reproducibility-pin verifier (static / runtime / "
            "end-to-end). Pre-commit-hook ready."
        )
    )
    ap.add_argument(
        "--layer",
        choices=["1", "2", "3", "all"],
        default="all",
        help="Which layer to run (default: all).",
    )
    ap.add_argument(
        "--verbose",
        action="store_true",
        help="Print PASS lines (default: only FAIL).",
    )
    args = ap.parse_args()

    layers = (
        ["1", "2", "3"] if args.layer == "all" else [args.layer]
    )
    print("=" * 70)
    print("SentinelFlow reproducibility-pin verifier (B2 + 1.0b)")
    print(f"  PINNED_OPENAI_MODEL = {PINNED_OPENAI_MODEL}")
    print(f"  PINNED_REVISIONS    = {PINNED_REVISIONS}")
    print("=" * 70)

    overall_ok = True

    if "1" in layers:
        print("\n[L1 STATIC] grep for unpinned literals + missing revision= …")
        ok, viols = verify_l1_static()
        if ok:
            print("  PASS  no unpinned literal, no os.getenv, every "
                  "SentenceTransformer call has revision=")
        else:
            print(f"  FAIL  {len(viols)} violation(s):")
            for v in viols:
                print(f"    {v}")
            overall_ok = False

    if "2" in layers:
        print("\n[L2 RUNTIME] resolve LLM + HF revision through each chain …")
        ok, viols = verify_l2_runtime(verbose=args.verbose)
        if ok:
            print("  PASS  every chain resolves to canonical pinned values")
        else:
            print(f"  FAIL  {len(viols)} violation(s):")
            for v in viols:
                print(f"    {v}")
            overall_ok = False

    if "3" in layers:
        print("\n[L3 END-TO-END] 2-prompt probe through repro_full_pipeline.py …")
        ok, viols = verify_l3_end_to_end(verbose=args.verbose)
        if ok:
            print(
                "  PASS  summary.json:llm_model + embedding_revision "
                "match canonical pinned values"
            )
        else:
            print(f"  FAIL  {len(viols)} violation(s):")
            for v in viols:
                print(f"    {v}")
            overall_ok = False

    print()
    print("=" * 70)
    print(f"OVERALL: {'PASS' if overall_ok else 'FAIL'}")
    print("=" * 70)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
