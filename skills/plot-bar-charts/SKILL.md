---
name: plot-bar-charts
description: Create polished, configurable Matplotlib bar charts and plotting-code templates for scientific comparisons. Use when Codex needs to write or run code for single bar charts, highlighted-method bar charts, grouped bar charts, bar charts with error bars, value labels, transparent fills, publication-ready styling, or configurable bar-plot templates from CSV, TSV, JSON, or inline tabular data.
---

# Plot Bar Charts

## Overview

Use this skill to turn tabular comparison data into clean, publication-ready bar charts and to guide agents writing reusable bar-plot code. Prefer the bundled script for standard single or grouped bar charts, then patch or extend it only when the user's data format or layout requires custom handling.

## Workflow

1. Inspect the user's table columns, category labels, series labels, values, and error columns before plotting.
2. When writing or modifying plotting code, expose a config interface for the actual style controls. Read `references/config-interface.md` for the bundled interface and the reproducible-data contract.
3. Use `scripts/plot_bar_charts.py` when the data is CSV, TSV, JSON, or a simple rectangular table.
4. Choose the chart mode:
   - `single` for one value per category.
   - `grouped` for multiple series per category.
5. Use highlighted single bars for "ours vs baselines" comparisons when one method should stand out.
6. If analysis code computes plotted values, save a separate full-precision chart-ready CSV (including error magnitudes) before plotting. Keep the source reference and error-bar meaning; never embed those numbers only in plotting calls. Deliver a standalone plot script and JSON config alongside the data and PNG, plus PDF for publication use. Changing the config must redraw from saved data without rerunning the analysis. The bundled script generates these companion files automatically.
7. Reject ambiguous duplicate categories, incomplete grouped combinations, and invalid values rather than silently aggregating. Visually verify labels, error bars, and legend placement.

## Script Usage

Run from the skill directory or pass an absolute path to the script:

```bash
python scripts/plot_bar_charts.py single.csv --mode single --label-column method --value-column accuracy --error-column std --highlight-label Ours --output single_bar.png --pdf
python scripts/plot_bar_charts.py grouped.csv --mode grouped --group-column dataset --series-column method --value-column accuracy --error-column std --output grouped_bar.png --pdf
python scripts/plot_bar_charts.py grouped.json --mode grouped --group-column dataset --series-column method --value-column score --output comparison.png
```

Use a Python environment with `matplotlib` and `numpy`. If the default `python` lacks those packages, switch to the active project, notebook, conda, or runtime Python that produced the data.

## Input Conventions

For `single` mode, provide one row per bar:

```csv
method,accuracy,std
CNN,74.8,0.7
LSTM,77.1,0.6
Ours,83.0,0.4
```

For `grouped` mode, provide one row per group/series pair:

```csv
dataset,method,accuracy,std
Cora,Baseline A,78.4,0.6
Cora,Ours,82.1,0.4
PubMed,Baseline A,80.6,0.5
PubMed,Ours,83.2,0.4
```

## Plotting Standards

Use the bundled visual style unless the user requests a different house style:

- Use low-saturation scientific colors with transparent bar fills and near-solid edges.
- Default single highlighted bars should render non-highlight bars in neutral gray and the highlighted bar in red.
- Default grouped bars should use blue, green, red, purple, cyan, orange, olive, then brown.
- Use `face_alpha` around `0.5`, `edge_alpha` around `0.95`, and bar `edge_width` around `2.0 pt`.
- Keep the complete axes frame visible and set its default spine width to `2.5 pt` in a dark neutral color; keep bar edge and frame widths configurable.
- Use restrained error bars with dark neutral color, narrow caps, and moderate alpha.
- Put value labels above bars only when they improve readability; reserve vertical space so labels do not clip.
- Use subtle dashed y-axis grid lines; do not draw x-axis grid lines by default.
- Use zero baseline for positive metrics unless the user asks for a narrowed y-axis.
- Prefer separate figures over overloaded multi-panel layouts unless the user asks for panels.

## Config Interface

Any custom plotting code produced under this skill must accept an external JSON config and a data-file path, with paths relative to the config for portable replotting. Keep the chart-ready data separate from code, and keep user-visible style choices in config.

Read `references/config-interface.md` before writing or substantially modifying plotting code. Implement only relevant controls, and ensure documented controls actually work; do not imply that the bundled script supports an option it does not implement.
