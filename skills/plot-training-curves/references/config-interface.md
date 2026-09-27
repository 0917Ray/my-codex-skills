# Training-curve configuration and reproducible data

The bundled script accepts `--config path.json` (or YAML with PyYAML). CLI flags override config values; omitted flags leave them intact. Each run creates the image(s), plus `<stem>_data.csv`, `<stem>_config.json`, and `<stem>_plot.py`. Replot with `python <stem>_plot.py --config <stem>_config.json`. The chart-ready CSV preserves unsmoothed metric values and sparse validation observations; changing `plot.smooth` recomputes only the display curve. `data.source` records the original log location without copying it.

When generating curves from custom training or analysis code, persist the plotted x/metric values with full numeric precision before any visual smoothing. Do not make the plotting script import the training pipeline or recalculate expensive results. Keep paths relative to the config, retain the original source reference, and test replotting with the original log unavailable. Do not interpolate missing validation values or imply that a smoothed series is the observed data.

## Supported bundled config

```json
{
  "data": {
    "input": "training_data.csv",
    "source": "/path/to/original/trainer_state.json",
    "x": "x",
    "train_loss_key": "train_loss",
    "val_loss_key": "val_loss",
    "lr_key": "learning_rate"
  },
  "plot": {"mode": "all-separate", "smooth": 7, "title": null, "titles": {"training-loss": "(a) Training Loss", "validation-loss": "(b) Validation Loss", "train-vs-val": "(c) Training vs. Validation Loss", "lr-schedule": "(d) Learning Rate Schedule"}},
  "figure": {"figsize": [7.2, 4.6], "panel_figsize": [7.4, 5.8], "dpi": 300, "spine_width": 2.5, "transparent": true},
  "series": {
    "train_loss": {"color": "#4F7C65", "linewidth": 2.0, "line_alpha": 0.92, "marker": "s", "marker_size": 5.0},
    "val_loss": {"color": "#A75B73", "linewidth": 2.0, "line_alpha": 0.92, "marker": "^", "marker_size": 5.2},
    "lr": {"color": "#516480", "linewidth": 2.0, "line_alpha": 0.92, "marker": "D", "marker_size": 4.8}
  },
  "axis": {"xlabel": "Step", "x_integer": true, "xlim": null, "ylim": null, "grid": true, "target_x_ticks": 9, "target_y_ticks": 7},
  "legend": {"enabled": true, "loc": "best"},
  "output": {"filename": "training_curves.png", "pdf": true}
}
```

The supported modes are `auto`, `training-loss`, `validation-loss`, `train-vs-val`, `lr-schedule`, `all-separate`, and `loss-and-lr-panels`. All fields and series marker alpha/edge settings are defined in `DEFAULT_CONFIG` in the bundled script. Do not promise controls absent from that config. `all-separate` requires all three metrics; choose only the available figures when a log does not contain them. A missing or invalid x value on a metric record fails; use `--x index` only when record index is intentionally the experimental x-axis, not as a silent replacement for missing steps.
