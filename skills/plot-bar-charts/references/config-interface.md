# Bar-chart configuration and reproducible data

The bundled script accepts `--config path.json` (or YAML with PyYAML). CLI flags override the corresponding config values; omitted flags leave config values intact. Its output is a PNG, optional PDF, and three companion files: `<stem>_data.csv`, `<stem>_config.json`, and `<stem>_plot.py`. Replot with `python <stem>_plot.py --config <stem>_config.json`. These files belong together; the original input is referenced as `data.source`, never required for replotting.

When writing custom analysis or plotting code, keep expensive computations outside the plot script. Export the exact chart-ready numeric values and uncertainties (not rounded display labels) in a standalone CSV before plotting. The plot script should read only that CSV and a persisted JSON config; it must run without importing the analysis program or referring to an absolute path. Preserve the original source location and the units/meaning of error bars in the config or accompanying research record. Smoothing and other appearance changes should not overwrite the saved values.

## Supported bundled config

```json
{
  "data": {
    "input": "comparison_data.csv",
    "source": "/path/to/original/results.csv",
    "mode": "grouped",
    "group_column": "group",
    "series_column": "series",
    "value_column": "value",
    "error_column": "error",
    "highlight_label": null
  },
  "figure": {"figsize": [6.8, 4.4], "grouped_figsize": [7.4, 4.6], "dpi": 140, "tight_layout": true},
  "bars": {"bar_width": 0.58, "group_width": 0.74, "face_alpha": 0.5, "edge_alpha": 0.95, "edge_width": 2.0},
  "errorbar": {"enabled": true, "color": "#3A3D42", "alpha": 0.82, "linewidth": 1.05, "capsize": 3.2},
  "value_labels": {"enabled": true, "format": "{:.1f}", "fontsize": 9.5},
  "axis": {"zero_baseline": true, "target_y_ticks": 6, "x_tick_rotation": 0},
  "spines": {"top": true, "right": true, "linewidth": 2.5},
  "legend": {"enabled": true, "grouped_loc": "upper center"},
  "text": {"title": null, "xlabel": null, "ylabel": null},
  "output": {"filename": "comparison.png", "pdf": true, "dpi": 300, "transparent": true}
}
```

For a single chart use `data.label_column` rather than `group_column` and `series_column`. Available palette, color-mode, margin, grid, font, error-bar, value-label, and legend details are defined in `DEFAULT_CONFIG` in the bundled script; config files may override any of those existing keys. Do not advertise an option unless the code uses it. Explicitly label whether error values represent standard deviation, standard error, or a confidence interval; the script does not calculate them.

Duplicate categories or group/series pairs, nonfinite values, missing combinations, and invalid error magnitudes fail instead of being silently aggregated or replaced. Compute any aggregation upstream, then save its resulting plotted values.
