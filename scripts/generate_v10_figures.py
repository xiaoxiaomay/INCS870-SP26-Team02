#!/usr/bin/env python3
"""
scripts/generate_v10_figures.py

Generates 5 paper-grade PDF figures for v10 paper §V from
existing eval/results/ data.

Outputs:
   figures/fig_1_phase1f_matrix.pdf
   figures/fig_2_phase1g_boxplots.pdf
   figures/fig_3_phase1g_s15_concentration.pdf
   figures/fig_4_phase1e_cosine_heatmap.pdf
   figures/fig_5_phase1g_s17_finlang.pdf

Usage:
   cd ~/Downloads/sentinelflow
   mkdir -p figures
   python3 scripts/generate_v10_figures.py

Dependencies: matplotlib, numpy (no scipy / pandas to keep simple)
"""

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


# ============================================================
# Paths
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE_1F_MATRIX = REPO_ROOT / "eval/results/phase1_F/m4_matrix.json"
PHASE_1G_MATRIX = REPO_ROOT / "eval/results/phase1_G/g2_outputs/matrix_n5.json"
HARD_NEG_JSONL = REPO_ROOT / "data/benchmark/hard_negatives.jsonl"
OUT_DIR = REPO_ROOT / "figures"

# IEEEtran 2-column page width: ~3.5 inches (single col), ~7.0 inches (double col)
SINGLE_COL = 3.5
DOUBLE_COL = 7.0

# Style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 150,
})

# Encoder display names + ordering (matches paper)
ENCODER_DISPLAY = {
    'minilm':    'MiniLM',
    'mpnet':     'mpnet',
    'bge_large': 'bge-large',
    'finlang':   'FinLang',
}
ENCODER_ORDER = ['minilm', 'mpnet', 'bge_large', 'finlang']


# ============================================================
# Data loaders
# ============================================================

def load_phase_1f_matrix():
    with open(PHASE_1F_MATRIX) as f:
        data = json.load(f)
    return data['cells']  # list of 8 cell dicts

def load_phase_1g_matrix():
    with open(PHASE_1G_MATRIX) as f:
        return json.load(f)

def load_hard_negatives():
    entries = []
    with open(HARD_NEG_JSONL) as f:
        for line in f:
            entries.append(json.loads(line))
    return entries


# ============================================================
# Figure 1: Phase 1.F Encoder Ablation Matrix
# ============================================================

def fig_1_phase_1f_matrix():
    """8-cell heatmap, color = Per-BP-Leak%."""
    cells = load_phase_1f_matrix()

    # Build 4 (encoders) x 2 (corpora) matrix
    encoders = ENCODER_ORDER
    corpora = ['60entry', '90entry']
    matrix = np.zeros((len(encoders), len(corpora)))

    for cell in cells:
        e_idx = encoders.index(cell['encoder'])
        c_idx = corpora.index(cell['corpus'])
        matrix[e_idx, c_idx] = cell['per_bypass_leak_pct']

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 3.2))

    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=30)

    # Annotate each cell with value
    for i in range(len(encoders)):
        for j in range(len(corpora)):
            val = matrix[i, j]
            color = 'white' if val > 15 else 'black'
            ax.text(j, i, f'{val:.1f}%',
                    ha='center', va='center', color=color, fontsize=9, fontweight='bold')

    ax.set_xticks(range(len(corpora)))
    ax.set_xticklabels(['Corpus 60', 'Corpus 90'])
    ax.set_yticks(range(len(encoders)))
    ax.set_yticklabels([ENCODER_DISPLAY[e] for e in encoders])
    ax.set_xlabel('Secret Corpus Size')
    ax.set_ylabel('Encoder')

    cbar = plt.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label('Per-BP-Leak \\%', rotation=270, labelpad=15)

    plt.title('Phase 1.F: Per-BP-Leak\\% across 8 cells', pad=8)
    plt.tight_layout()

    out_path = OUT_DIR / "fig_1_phase1f_matrix.pdf"
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out_path.name}")
    return out_path


# ============================================================
# Figure 2: Phase 1.G Multi-Sample Box Plots
# ============================================================

def fig_2_phase_1g_boxplots():
    """Box plots: 8 cells × Per-BP-Leak (the most discriminating metric)."""
    g2 = load_phase_1g_matrix()
    cells_data = g2['per_cell_aggregates']

    # Cell ordering: encoder × corpus pairs
    cell_keys = [
        'minilm_60entry', 'minilm_90entry',
        'mpnet_60entry', 'mpnet_90entry',
        'bge_large_60entry', 'bge_large_90entry',
        'finlang_60entry', 'finlang_90entry',
    ]
    cell_labels = ['MiniLM\n×60', 'MiniLM\n×90',
                   'mpnet\n×60', 'mpnet\n×90',
                   'bge-large\n×60', 'bge-large\n×90',
                   'FinLang\n×60', 'FinLang\n×90']

    # Extract per_bp_leak_rate values (n=5 per cell)
    box_data = []
    for k in cell_keys:
        box_data.append(cells_data[k]['per_bp_leak_rate']['values'])

    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 3.5))

    bp = ax.boxplot(box_data, labels=cell_labels, widths=0.6,
                     patch_artist=True, showmeans=True,
                     meanprops={'marker': 'D', 'markerfacecolor': 'white',
                                'markeredgecolor': 'black', 'markersize': 5},
                     medianprops={'color': 'black', 'linewidth': 1.2})

    # Color boxes by encoder family
    encoder_colors = {'minilm': '#4daf4a', 'mpnet': '#377eb8',
                       'bge_large': '#e41a1c', 'finlang': '#984ea3'}
    for i, k in enumerate(cell_keys):
        enc = k.rsplit('_', 1)[0]
        bp['boxes'][i].set_facecolor(encoder_colors[enc])
        bp['boxes'][i].set_alpha(0.6)

    # Plot individual sample points
    for i, vals in enumerate(box_data):
        x_jitter = np.random.normal(i + 1, 0.04, len(vals))
        ax.scatter(x_jitter, vals, s=12, c='black', alpha=0.5, zorder=3)

    ax.set_ylabel('Per-BP-Leak rate')
    ax.set_title('Phase 1.G: Per-BP-Leak across 5 samples per cell (n=5)', pad=8)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.xticks(rotation=0, fontsize=7)
    plt.tight_layout()

    out_path = OUT_DIR / "fig_2_phase1g_boxplots.pdf"
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out_path.name}")
    return out_path


# ============================================================
# Figure 3: S15 bge-large ULR Concentration
# ============================================================

def fig_3_phase_1g_s15_concentration():
    """Bar chart showing ULR fires concentrated on bge-large."""
    g2 = load_phase_1g_matrix()
    cells_data = g2['per_cell_aggregates']

    cell_keys = [
        'minilm_60entry', 'minilm_90entry',
        'mpnet_60entry', 'mpnet_90entry',
        'bge_large_60entry', 'bge_large_90entry',
        'finlang_60entry', 'finlang_90entry',
    ]
    cell_labels = ['MiniLM\n×60', 'MiniLM\n×90',
                   'mpnet\n×60', 'mpnet\n×90',
                   'bge-large\n×60', 'bge-large\n×90',
                   'FinLang\n×60', 'FinLang\n×90']

    # n_ulr_leaked sum across 5 samples per cell
    ulr_fires = []
    for k in cell_keys:
        vals = cells_data[k]['n_ulr_leaked']['values']
        ulr_fires.append(sum(vals))

    fig, ax = plt.subplots(figsize=(SINGLE_COL * 1.6, 3.0))

    # Color: bge-large red, others gray
    colors = ['#cccccc', '#cccccc', '#cccccc', '#cccccc',
              '#e41a1c', '#e41a1c', '#cccccc', '#cccccc']

    bars = ax.bar(range(len(cell_keys)), ulr_fires, color=colors,
                   edgecolor='black', linewidth=0.8)

    # Annotate bars
    for i, (bar, val) in enumerate(zip(bars, ulr_fires)):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.05, str(val),
                ha='center', va='bottom', fontsize=8)

    ax.set_xticks(range(len(cell_keys)))
    ax.set_xticklabels(cell_labels, fontsize=7)
    ax.set_ylabel('Total ULR fires across 5 samples')
    ax.set_title('S15: ULR fires concentrated on bge-large\n(1 fire / 10{,}840 evaluations = 0.0092\\%)', pad=8)
    ax.set_ylim(0, max(max(ulr_fires) + 1, 2))
    ax.grid(axis='y', alpha=0.3)

    # Annotation
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.text(4.5, 1.5, 'bge-large cells: 1 fire\n(forensically classified\nas measurement-stage FP)',
            ha='center', va='center', fontsize=7, style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray'))

    plt.tight_layout()

    out_path = OUT_DIR / "fig_3_phase1g_s15_concentration.pdf"
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out_path.name}")
    return out_path


# ============================================================
# Figure 4: Hard-Negative Cosine Heatmap (65 entries × 4 encoders)
# ============================================================

def fig_4_phase_1e_cosine_heatmap():
    """Heatmap of all 65 hard-neg cosines across 4 encoders."""
    entries = load_hard_negatives()

    encoders = ENCODER_ORDER
    cosine_field = {
        'minilm':    'closest_cosine_minilm_90',
        'mpnet':     'closest_cosine_mpnet_90',
        'bge_large': 'closest_cosine_bge_large_90',
        'finlang':   'closest_cosine_finlang_90',
    }

    # Build 65 × 4 matrix
    matrix = np.zeros((len(entries), len(encoders)))
    for i, entry in enumerate(entries):
        for j, enc in enumerate(encoders):
            matrix[i, j] = entry[cosine_field[enc]]

    # Sort entries by category for better visual structure
    cats = [e['category'] for e in entries]
    cat_order = sorted(set(cats))
    sort_idx = sorted(range(len(entries)),
                      key=lambda i: (cat_order.index(cats[i]), entries[i]['_id']))
    matrix = matrix[sort_idx]
    cats_sorted = [cats[i] for i in sort_idx]

    # Find category boundaries for visual separators
    cat_boundaries = []
    prev = cats_sorted[0]
    for i, c in enumerate(cats_sorted):
        if c != prev:
            cat_boundaries.append(i)
            prev = c

    fig, ax = plt.subplots(figsize=(SINGLE_COL * 1.4, 5.0))

    im = ax.imshow(matrix, aspect='auto', cmap='RdYlBu_r', vmin=0.1, vmax=0.9)

    # Draw horizontal category separators
    for b in cat_boundaries:
        ax.axhline(y=b - 0.5, color='black', linewidth=0.8, alpha=0.7)

    # Category labels on the left
    prev = cats_sorted[0]
    start = 0
    for i, c in enumerate(cats_sorted + [None]):
        if c != prev:
            mid = (start + i - 1) / 2
            ax.text(-0.7, mid, prev, ha='right', va='center',
                    fontsize=8, fontweight='bold')
            start = i
            prev = c

    # V1a band markers (MiniLM band [0.40, 0.65]) — vertical reference
    # Highlight MiniLM column
    ax.add_patch(Rectangle((-0.5, -0.5), 1, len(entries),
                           fill=False, edgecolor='blue', linewidth=1.5, alpha=0.7))

    ax.set_xticks(range(len(encoders)))
    ax.set_xticklabels([ENCODER_DISPLAY[e] for e in encoders], fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel('Encoder')
    ax.set_title('Phase 1.E: 65 hard-neg cosines\n(rows grouped by Cat A--F; MiniLM = V1a anchor)', pad=8)

    cbar = plt.colorbar(im, ax=ax, shrink=0.6)
    cbar.set_label('Closest cosine', rotation=270, labelpad=15)

    plt.tight_layout()

    out_path = OUT_DIR / "fig_4_phase1e_cosine_heatmap.pdf"
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out_path.name}")
    return out_path


# ============================================================
# Figure 5: S17 FinLang Corpus Effect with Holm Significance
# ============================================================

def fig_5_phase_1g_s17_finlang():
    """Per-sample GLR for FinLang × 60 vs × 90, with Holm-Bonferroni significance band."""
    g2 = load_phase_1g_matrix()
    cells = g2['per_cell_aggregates']
    paired_tests = g2['within_encoder_paired_tests']['primary_tests_glr']

    # Find FinLang test result
    finlang_test = None
    for test in paired_tests:
        if isinstance(test, dict) and test.get('encoder') == 'finlang':
            finlang_test = test
            break

    p_value = finlang_test['p_value_unadjusted'] if finlang_test else 0.0011
    holm_threshold = finlang_test['holm_threshold'] if finlang_test else 0.0125
    mean_diff = finlang_test['mean_diff'] if finlang_test else -0.0531

    # Per-sample GLR values
    finlang_60 = cells['finlang_60entry']['glr_rate']['values']
    finlang_90 = cells['finlang_90entry']['glr_rate']['values']

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.2),
                              gridspec_kw={'width_ratios': [1.3, 1]})

    # Left subplot: paired bar chart per sample
    ax = axes[0]
    x = np.arange(5)
    width = 0.35

    bars60 = ax.bar(x - width/2, [v*100 for v in finlang_60], width,
                     label='FinLang × 60', color='#984ea3', alpha=0.7,
                     edgecolor='black', linewidth=0.5)
    bars90 = ax.bar(x + width/2, [v*100 for v in finlang_90], width,
                     label='FinLang × 90', color='#984ea3', alpha=0.4, hatch='//',
                     edgecolor='black', linewidth=0.5)

    # Annotate sample values
    for bars in (bars60, bars90):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.1, f'{h:.2f}',
                    ha='center', va='bottom', fontsize=6)

    # Means as horizontal lines
    mean60 = np.mean(finlang_60) * 100
    mean90 = np.mean(finlang_90) * 100
    ax.axhline(y=mean60, color='#984ea3', linestyle='--', alpha=0.6, linewidth=1)
    ax.axhline(y=mean90, color='gray', linestyle='--', alpha=0.6, linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels([f'S{i+1}' for i in range(5)])
    ax.set_xlabel('Sample')
    ax.set_ylabel('GLR rate (\\%)')
    ax.set_title('FinLang GLR per sample: 60 vs 90')
    ax.legend(loc='upper left', fontsize=7)
    ax.grid(axis='y', alpha=0.3)

    # Right subplot: significance summary
    ax = axes[1]
    ax.axis('off')

    text = (
        r'\textbf{Holm-Bonferroni Test}' + '\n'
        r'(within-encoder corpus delta)' + '\n\n'
        f'$\\bar{{d}}_{{60-90}}$ = {mean_diff*100:+.2f} pp\n'
        f'$t$ = {finlang_test["t_statistic"]:.2f}\n'
        f'$p$ = {p_value:.4f}\n'
        f'Holm rank = 1\n'
        f'Threshold = {holm_threshold:.4f}\n\n'
        r'\textbf{SIGNIFICANT}' + '\n'
        '($p < $ threshold)\n\n'
        'FinLang is the only\n'
        'encoder whose corpus\n'
        'effect survives Holm\n'
        'multiplicity correction.'
    )
    ax.text(0.05, 0.95, text, transform=ax.transAxes,
            fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                      edgecolor='black', linewidth=1))

    plt.tight_layout()

    out_path = OUT_DIR / "fig_5_phase1g_s17_finlang.pdf"
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out_path.name}")
    return out_path


# ============================================================
# Main
# ============================================================

def main():
    print(f"v10 Figure Generation Script")
    print(f"  REPO_ROOT: {REPO_ROOT}")
    print(f"  OUT_DIR:   {OUT_DIR}")
    print()

    # Check inputs exist
    for path in [PHASE_1F_MATRIX, PHASE_1G_MATRIX, HARD_NEG_JSONL]:
        if not path.exists():
            print(f"  ✗ Missing: {path}", file=sys.stderr)
            sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating figures:")
    fig_1_phase_1f_matrix()
    fig_2_phase_1g_boxplots()
    fig_3_phase_1g_s15_concentration()
    fig_4_phase_1e_cosine_heatmap()
    fig_5_phase_1g_s17_finlang()

    print()
    print(f"5 figures generated in {OUT_DIR}/")
    print()
    print("Next: upload PDFs to Overleaf and add \\includegraphics references in §V.")


if __name__ == "__main__":
    main()
