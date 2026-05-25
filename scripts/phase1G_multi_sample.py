#!/usr/bin/env python3
"""
scripts/phase1G_multi_sample.py — Phase 1.G G1 multi-sample driver

Pure orchestrator that adds 4 additional samples per cell (samples 2–5)
to Phase 1.F's 8-cell ablation matrix, treating Phase 1.F (commit
007c460) outputs as sample 1. Implements V2 plan §13 + PHASE_1F_RESULTS
§11.1 #2 (Phase 1.G multi-sample LLM stochasticity probe).

Per `PHASE_1G_PLAN.md` D1–D7 design ratification (2026-05-24):
  D1 n=5 (4 additional samples here; Phase 1.F = sample 1)
  D2 No seed (natural stochasticity is the measurand)
  D3 All 8 cells in scope
  D4 gpt-4o-mini-2024-07-18 pinned (same as Phase 1.F)
  D5 Statistical analysis happens in G2 (separate stage), not here
  D6 Phase 1.F immutable; this script writes to eval/results/phase1_G/
  D7 $1.00 phase cap; $0.15 per-cell cap; $0.70 LLM forecast

Architecture: subprocess-based orchestrator that invokes existing
`scripts/repro_full_pipeline.py` per (cell, sample). Adds:
  - Resumability ledger (run_state.json) — skip already-completed
    samples; recover from crash mid-sample.
  - Cost-cap enforcement (per-cell + global) with STOP_AND_DISCLOSE.
  - ULR=0% BLOCKING in-loop check (RG4 kill-switch).
  - Append-only event log (run_log.jsonl) for forensic trail.
  - Dry-run modes ($0 LLM) for pre-production verification.

V2.5 modifications 2026-05-25 (after sample_3 RG4 trigger
2026-05-24T20:44:35Z forensically confirmed as bge-large
measurement-stage false positive per §V.A F2 over-sensitivity):
  - Change A: Added --disable-rg4 CLI flag. When set, non-zero
    ULR samples no longer halt the driver.
  - Change B: When --disable-rg4 is active and ULR > 0 is
    observed, the driver writes a detailed `ulr_observed` event
    to run_log.jsonl with per-leak forensic detail (attack_id,
    category, max_leak_score, redacted_text_preview first 200
    chars) extracted from the sample's full_pipeline_eval.json.
    This event type accumulates the S15 evidence chain for
    v10 paper §V.B downstream analysis.

NO MODIFICATIONS to Phase 1.F scripts. Phase 1.F output tree
(eval/results/phase1_F/) remains untouched.

Usage:
  # Dry-run modes ($0 LLM; pre-production verification):
  python3 scripts/phase1G_multi_sample.py --dry-run
  python3 scripts/phase1G_multi_sample.py --dry-run-trigger-cap
  python3 scripts/phase1G_multi_sample.py --dry-run-trigger-ulr

  # Partial production (testing):
  python3 scripts/phase1G_multi_sample.py --max-samples 2

  # Full production (LLM-bound; ~$0.70, ~11h):
  python3 scripts/phase1G_multi_sample.py

Exit codes:
  0 = all 32 samples complete (or --max-samples reached cleanly)
  1 = STOP_AND_DISCLOSE triggered (cost cap / ULR / crash recovery)
  2 = unrecoverable error (missing config, invalid state, etc.)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Constants — ratified per PHASE_1G_PLAN.md D1, D3, D7
# ---------------------------------------------------------------------------

# 8 cells in canonical order (matches Phase 1.F phase1F_matrix.py CELLS_ORDER)
CELLS_ORDER: List[Tuple[str, str]] = [
    ("minilm",    "60entry"), ("minilm",    "90entry"),
    ("mpnet",     "60entry"), ("mpnet",     "90entry"),
    ("bge_large", "60entry"), ("bge_large", "90entry"),
    ("finlang",   "60entry"), ("finlang",   "90entry"),
]

# Sample IDs this phase contributes (sample 1 = Phase 1.F 007c460, immutable).
PHASE_1G_SAMPLE_IDS: List[int] = [2, 3, 4, 5]
N_SAMPLES_TARGET = len(PHASE_1G_SAMPLE_IDS)

# Cost caps (per PHASE_1G_PLAN.md D7).
# Per-cell cap is CUMULATIVE across all 4 samples for that cell.
# Cap triggers if sum of sample costs reaches $0.15 within cell's run.
PER_CELL_CAP_USD = 0.15
PHASE_CAP_USD    = 1.00
STOP_AT_PHASE_PCT = 0.90  # Pre-emptive halt at 90% of phase cap

# Phase 1.G output tree.
OUTPUT_ROOT = REPO_ROOT / "eval" / "results" / "phase1_G"
STATE_FILE  = OUTPUT_ROOT / "run_state.json"
RUN_LOG     = OUTPUT_ROOT / "run_log.jsonl"

# Phase 1.F config path pattern (re-using existing 8 configs).
CONFIG_PATH_FMT = "config_phase1F_{cell_label}.yaml"

# Phase 1.F cell-runner script (subprocess target).
CELL_RUNNER_SCRIPT = REPO_ROOT / "scripts" / "repro_full_pipeline.py"

# Subprocess timeout: max ~3h per sample (Cell 6 at ~1.86h has margin).
SUBPROCESS_TIMEOUT_S = 3 * 60 * 60


# ---------------------------------------------------------------------------
# Time + I/O helpers
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """Atomic write via temp file + rename. fsync for crash safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    tmp_path.replace(path)


def append_jsonl(path: Path, event: Dict[str, Any]) -> None:
    """Append a single JSONL line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def init_state() -> Dict[str, Any]:
    """Fresh state ledger."""
    return {
        "schema_version":            "phase1G_state_v1",
        "started_at":                utc_now_iso(),
        "last_updated_at":           utc_now_iso(),
        "n_samples_target_per_cell": N_SAMPLES_TARGET,
        "phase_cap_usd":             PHASE_CAP_USD,
        "per_cell_cap_usd":          PER_CELL_CAP_USD,
        "stop_at_phase_pct":         STOP_AT_PHASE_PCT,
        "phase_1g_cumulative_cost_usd": 0.0,
        "per_cell_cumulative_cost_usd": {f"{e}_{c}": 0.0 for e, c in CELLS_ORDER},
        "completed_samples":         [],
        "last_attempted_sample": {
            "cell_label":             None,
            "sample_id":              0,
            "subprocess_started_at":  None,
            "subprocess_completed_at": None,
        },
    }


def load_or_init_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        with STATE_FILE.open("r", encoding="utf-8") as f:
            state = json.load(f)
        print(f"  RESUME: loaded {STATE_FILE.relative_to(REPO_ROOT)}; "
              f"{len(state['completed_samples'])} samples done; "
              f"cumulative cost ${state['phase_1g_cumulative_cost_usd']:.4f}")
        return state
    state = init_state()
    atomic_write_json(STATE_FILE, state)
    print(f"  INIT: created {STATE_FILE.relative_to(REPO_ROOT)}")
    return state


def save_state(state: Dict[str, Any]) -> None:
    state["last_updated_at"] = utc_now_iso()
    atomic_write_json(STATE_FILE, state)


def recover_from_crash(state: Dict[str, Any]) -> None:
    """If last_attempted_sample exists but its sample dir lacks
    valid summary.json, delete partial dir + reset attempt marker."""
    last = state["last_attempted_sample"]
    if not last["cell_label"]:
        return
    if last["subprocess_completed_at"] is not None:
        # Last attempt completed cleanly; nothing to recover.
        return
    sample_dir = OUTPUT_ROOT / last["cell_label"] / f"sample_{last['sample_id']}"
    summary_ok = (sample_dir / "summary.json").exists()
    if summary_ok:
        # Subprocess wrote summary but driver crashed before logging completion.
        # Trust the summary; mark complete on next iteration.
        print(f"  CRASH RECOVERY: {sample_dir.relative_to(REPO_ROOT)} has summary.json; "
              f"will be detected as complete on next pass")
        return
    # Partial sample dir without summary.json → delete + retry.
    if sample_dir.exists():
        print(f"  CRASH RECOVERY: removing partial {sample_dir.relative_to(REPO_ROOT)}")
        shutil.rmtree(sample_dir)
    state["last_attempted_sample"] = init_state()["last_attempted_sample"]
    save_state(state)


# ---------------------------------------------------------------------------
# Logging events
# ---------------------------------------------------------------------------

def log_event(event_type: str, **fields: Any) -> None:
    event = {"event": event_type, "ts": utc_now_iso(), **fields}
    append_jsonl(RUN_LOG, event)


# ---------------------------------------------------------------------------
# Stop-and-disclose
# ---------------------------------------------------------------------------

def stop_and_disclose(reason: str, cell_label: str = "", sample_id: int = 0,
                       state: Optional[Dict[str, Any]] = None) -> None:
    """Append STOP event + save state + print message. Caller exits 1."""
    msg = f"STOP_AND_DISCLOSE: {reason}"
    if cell_label:
        msg += f" (at {cell_label}/sample_{sample_id})"
    print(f"\n!!! {msg}")
    log_event("stop_and_disclose", reason=reason,
              cell_label=cell_label, sample_id=sample_id)
    if state is not None:
        save_state(state)


# ---------------------------------------------------------------------------
# Mock summary writer (dry-run modes)
# ---------------------------------------------------------------------------

def write_mock_summary(sample_dir: Path, cell_label: str, sample_id: int,
                       cost_usd: float = 0.0010, ulr_rate: float = 0.0,
                       elapsed_s: float = 0.1) -> Dict[str, Any]:
    """Mock summary.json + minimal companion files for dry-run modes.
    Mirrors fields read by save_state/g2 aggregation."""
    sample_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "config_path":           f"config_phase1F_{cell_label}.yaml",
        "output_dir":            str(sample_dir),
        "started_at":            utc_now_iso(),
        "finished_at":           utc_now_iso(),
        "embedding_model":       f"mock-{cell_label}",
        "llm_model":             "gpt-4o-mini-2024-07-18",
        "secret_count":          60 if cell_label.endswith("60entry") else 90,
        "n_attacks":             271,
        "n_blocked_pregates":    140,
        "n_bypass":              131,
        "n_llm_called":          131,
        "bypass_rate":           0.4834,
        "n_glr_leaked":          5,
        "n_ulr_leaked":          0 if ulr_rate == 0.0 else int(271 * ulr_rate),
        "glr_rate":              0.0185,
        "ulr_rate":              ulr_rate,
        "estimated_cost_usd":    cost_usd,
        "elapsed_s":             elapsed_s,
        "mock_marker":           True,
        "mock_sample_id":        sample_id,
        "mock_cell_label":       cell_label,
    }
    with (sample_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    # Minimal companion artifacts (presence-only; not used in G2).
    (sample_dir / "bypass_cases.jsonl").write_text("")
    (sample_dir / "full_pipeline_eval.json").write_text("{}")
    return summary


# ---------------------------------------------------------------------------
# Real subprocess invocation (production mode)
# ---------------------------------------------------------------------------

def run_cell_subprocess(cell_label: str, sample_id: int,
                         sample_dir: Path) -> Optional[Dict[str, Any]]:
    """Invoke scripts/repro_full_pipeline.py as subprocess. Returns
    parsed summary.json dict on success, None on failure (caller
    handles failure via subprocess_failure event + stop_and_disclose)."""
    config_path = REPO_ROOT / CONFIG_PATH_FMT.format(cell_label=cell_label)
    if not config_path.exists():
        print(f"  ERROR: config not found: {config_path}")
        return None

    sample_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(CELL_RUNNER_SCRIPT),
        "--config", str(config_path),
        "--output-dir", str(sample_dir),
    ]
    print(f"  SUBPROCESS: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT),
            timeout=SUBPROCESS_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        log_event("subprocess_failure", cell_label=cell_label,
                  sample_id=sample_id, exit_code=-1, reason="timeout")
        return None
    if result.returncode != 0:
        log_event("subprocess_failure", cell_label=cell_label,
                  sample_id=sample_id, exit_code=result.returncode)
        return None
    summary_path = sample_dir / "summary.json"
    if not summary_path.exists():
        log_event("subprocess_failure", cell_label=cell_label,
                  sample_id=sample_id, exit_code=0,
                  reason="missing_summary_json")
        return None
    with summary_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main_loop(mode: str, max_samples: Optional[int],
              disable_rg4: bool = False) -> int:
    """mode ∈ {production, dry-run, dry-run-trigger-cap, dry-run-trigger-ulr}

    disable_rg4: if True, log non-zero ULR samples as 'rg4_disabled_nonzero_ulr'
    events but continue execution instead of halting. Added 2026-05-25 for
    V2.5 restart after sample_3 RG4 trigger; rationale: now that ULR ≠ 0 is
    empirically possible under multi-sample evaluation, we want continuous
    data collection across all 32 samples to characterize the ULR
    distribution (v10 paper §V.B candidate S15 finding).
    """
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    state = load_or_init_state()
    recover_from_crash(state)

    print(f"\n=== Phase 1.G G1 multi-sample driver — mode={mode} ===")
    print(f"  Cells: {len(CELLS_ORDER)}; samples per cell: {N_SAMPLES_TARGET}")
    print(f"  Target total samples: {len(CELLS_ORDER) * N_SAMPLES_TARGET}")
    print(f"  Phase cap: ${PHASE_CAP_USD:.2f}; per-cell cap: ${PER_CELL_CAP_USD:.2f}")
    print(f"  Pre-emptive stop at: {STOP_AT_PHASE_PCT*100:.0f}% of phase cap")
    print()

    samples_done_this_run = 0
    target_samples = max_samples if max_samples else (len(CELLS_ORDER) * N_SAMPLES_TARGET)

    for cell_idx, (encoder, corpus) in enumerate(CELLS_ORDER, start=1):
        cell_label = f"{encoder}_{corpus}"

        for sample_id in PHASE_1G_SAMPLE_IDS:
            sample_dir = OUTPUT_ROOT / cell_label / f"sample_{sample_id}"
            summary_path = sample_dir / "summary.json"

            # Resumability: skip if already complete
            if summary_path.exists():
                print(f"  SKIP {cell_label}/sample_{sample_id} (already complete)")
                continue

            # Per-cell cap pre-flight
            cell_cost = state["per_cell_cumulative_cost_usd"][cell_label]
            if cell_cost >= PER_CELL_CAP_USD:
                stop_and_disclose(
                    f"per-cell cumulative cost ${cell_cost:.4f} >= cap ${PER_CELL_CAP_USD:.2f}",
                    cell_label=cell_label, sample_id=sample_id, state=state,
                )
                return 1

            # Phase cap pre-flight (90% pre-emptive halt)
            phase_cost = state["phase_1g_cumulative_cost_usd"]
            if phase_cost >= PHASE_CAP_USD * STOP_AT_PHASE_PCT:
                stop_and_disclose(
                    f"phase cumulative cost ${phase_cost:.4f} >= {STOP_AT_PHASE_PCT*100:.0f}% cap",
                    cell_label=cell_label, sample_id=sample_id, state=state,
                )
                return 1

            # Mark last_attempted_sample BEFORE subprocess (crash-recovery hook)
            state["last_attempted_sample"] = {
                "cell_label":              cell_label,
                "sample_id":               sample_id,
                "subprocess_started_at":   utc_now_iso(),
                "subprocess_completed_at": None,
            }
            save_state(state)
            log_event("sample_start", cell_label=cell_label, sample_id=sample_id)

            # Execute (real or mock per mode)
            t0 = time.time()
            summary: Optional[Dict[str, Any]] = None

            if mode == "dry-run":
                # Standard dry-run: small mock cost, ulr=0
                summary = write_mock_summary(sample_dir, cell_label, sample_id,
                                              cost_usd=0.0010, ulr_rate=0.0)
            elif mode == "dry-run-trigger-cap":
                # Force per-cell cap to fire mid-cell. Mock $0.06 per sample
                # so 3 samples per cell hits $0.18 > $0.15 cap.
                summary = write_mock_summary(sample_dir, cell_label, sample_id,
                                              cost_usd=0.06, ulr_rate=0.0)
            elif mode == "dry-run-trigger-ulr":
                # First sample mocks non-zero ULR — should kill at first sample.
                trigger = (cell_idx == 1 and sample_id == 2)
                summary = write_mock_summary(sample_dir, cell_label, sample_id,
                                              cost_usd=0.0010,
                                              ulr_rate=0.5 if trigger else 0.0)
            elif mode == "production":
                summary = run_cell_subprocess(cell_label, sample_id, sample_dir)
                if summary is None:
                    stop_and_disclose(
                        f"subprocess failed at {cell_label}/sample_{sample_id}",
                        cell_label=cell_label, sample_id=sample_id, state=state,
                    )
                    return 1
            else:
                print(f"  ERROR: unknown mode '{mode}'")
                return 2

            wall_s = time.time() - t0

            # ULR=0% BLOCKING check (RG4 kill-switch).
            # Disabled via --disable-rg4 per V2.5 restart 2026-05-25:
            # multi-sample ULR characterization requires continuous collection.
            # When disabled, emit detailed `ulr_observed` event with per-leak
            # forensic detail (attack_id, max_leak_score, redacted_text_preview)
            # per Decision (b) 2026-05-25 for downstream S15 analysis.
            if float(summary.get("ulr_rate", 0.0)) != 0.0:
                if disable_rg4:
                    print(f"  RG4 DISABLED: non-zero ULR="
                          f"{summary['ulr_rate']:.4f} ("
                          f"{summary.get('n_ulr_leaked', '?')} leak"
                          f"{'s' if summary.get('n_ulr_leaked', 0) != 1 else ''}) "
                          f"at {cell_label}/sample_{sample_id} — continuing "
                          f"per V2.5 restart; logging ulr_observed event")
                    # Build forensic leak_details by reading full_pipeline_eval.json
                    leak_details: List[Dict[str, Any]] = []
                    fp_path = sample_dir / "full_pipeline_eval.json"
                    try:
                        with fp_path.open("r", encoding="utf-8") as f:
                            fp = json.load(f)
                        for r in fp.get("results", []):
                            if r.get("leaked_ulr"):
                                leak_details.append({
                                    "attack_id":             r.get("_id"),
                                    "category":              r.get("group"),
                                    "max_leak_score":        r.get("max_leak_score"),
                                    "redacted_text_preview": str(r.get("redacted_text", ""))[:200],
                                })
                    except Exception as e:
                        print(f"    WARNING: leak_details extraction failed: "
                              f"{type(e).__name__}: {e}")
                        leak_details = [{"error": f"{type(e).__name__}: {e}"}]
                    log_event("ulr_observed",
                              cell_label=cell_label, sample_id=sample_id,
                              ulr_rate=float(summary['ulr_rate']),
                              n_ulr_leaked=int(summary.get('n_ulr_leaked', 0)),
                              leak_details=leak_details)
                else:
                    stop_and_disclose(
                        f"non-zero ULR={summary['ulr_rate']:.4f} (RG4 violation)",
                        cell_label=cell_label, sample_id=sample_id, state=state,
                    )
                    return 1

            # Update state
            cost_usd = float(summary.get("estimated_cost_usd", 0.0))
            state["per_cell_cumulative_cost_usd"][cell_label] += cost_usd
            state["phase_1g_cumulative_cost_usd"] += cost_usd
            state["completed_samples"].append({
                "cell_label":    cell_label,
                "sample_id":     sample_id,
                "cost_usd":      cost_usd,
                "wall_seconds":  round(wall_s, 1),
                "completed_at":  utc_now_iso(),
            })
            state["last_attempted_sample"]["subprocess_completed_at"] = utc_now_iso()
            save_state(state)
            log_event("sample_complete", cell_label=cell_label, sample_id=sample_id,
                      cost_usd=cost_usd, wall_seconds=round(wall_s, 1))

            samples_done_this_run += 1
            cum_pct = 100.0 * state["phase_1g_cumulative_cost_usd"] / PHASE_CAP_USD
            cell_pct = 100.0 * state["per_cell_cumulative_cost_usd"][cell_label] / PER_CELL_CAP_USD
            print(f"  DONE {cell_label}/sample_{sample_id}: "
                  f"cost ${cost_usd:.4f}  wall {wall_s:.1f}s  "
                  f"cum ${state['phase_1g_cumulative_cost_usd']:.4f} ({cum_pct:.1f}%)  "
                  f"cell ${state['per_cell_cumulative_cost_usd'][cell_label]:.4f} ({cell_pct:.1f}%)")

            if max_samples is not None and samples_done_this_run >= target_samples:
                print(f"\n  REACHED --max-samples limit ({target_samples}); stopping cleanly")
                log_event("max_samples_reached", count=samples_done_this_run)
                return 0

    print(f"\n=== Phase 1.G G1 driver complete ===")
    print(f"  Total samples completed: {len(state['completed_samples'])} / {len(CELLS_ORDER) * N_SAMPLES_TARGET}")
    print(f"  Cumulative cost: ${state['phase_1g_cumulative_cost_usd']:.4f} / ${PHASE_CAP_USD:.2f}")
    log_event("driver_complete",
              n_samples=len(state["completed_samples"]),
              cumulative_cost=state["phase_1g_cumulative_cost_usd"])
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true",
                       help="Mock execution; $0 LLM; standard logic verification")
    group.add_argument("--dry-run-trigger-cap", action="store_true",
                       help="Mock high-cost samples; verifies per-cell cap STOP_AND_DISCLOSE")
    group.add_argument("--dry-run-trigger-ulr", action="store_true",
                       help="Mock non-zero ULR; verifies RG4 kill-switch STOP_AND_DISCLOSE")
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Optional limit on samples this invocation (testing)")
    parser.add_argument("--disable-rg4", action="store_true",
                        help="Disable RG4 ULR kill-switch (added 2026-05-25 for "
                             "V2.5 restart after sample_3 RG4 trigger; multi-sample "
                             "ULR characterization requires continuous data "
                             "collection across all 32 samples — log non-zero ULR "
                             "as 'rg4_disabled_nonzero_ulr' event but continue)")
    args = parser.parse_args()

    if args.dry_run:
        mode = "dry-run"
    elif args.dry_run_trigger_cap:
        mode = "dry-run-trigger-cap"
    elif args.dry_run_trigger_ulr:
        mode = "dry-run-trigger-ulr"
    else:
        mode = "production"

    if mode == "production":
        print("=" * 70)
        print("PHASE 1.G G1 PRODUCTION RUN — LLM calls will be made!")
        print(f"Expected cost: ~$0.70 LLM | Expected wall: ~11 hours")
        print(f"Phase cap: ${PHASE_CAP_USD:.2f} | Per-cell cap: ${PER_CELL_CAP_USD:.2f}")
        print("=" * 70)

    if mode == "production" and args.disable_rg4:
        print("=" * 70)
        print("RG4 ULR KILL-SWITCH DISABLED — non-zero ULR samples will be")
        print("logged ('rg4_disabled_nonzero_ulr' event) and execution continues.")
        print("=" * 70)

    return main_loop(mode, args.max_samples, args.disable_rg4)


if __name__ == "__main__":
    raise SystemExit(main())
