---
name: plot-training-curves
description: Create polished, configurable Matplotlib line plots and plotting-code templates for LLM and machine-learning training logs. Use when Codex needs to write or run code for training loss, validation/eval loss, learning-rate schedules, train-vs-validation loss comparisons, or separate loss/LR figures from CSV, JSONL, JSON, Hugging Face trainer_state.json, W&B exports, or similar experiment logs.
---

# Plot Training Curves

## Overview

Use this skill to turn experiment logs into clean, publication-ready training curves and to guide agents writing reusable plotting code. Prefer the bundled script for repeatability, then patch or extend it only when the user's log format requires custom handling.

## Workflow

1. Inspect the user's log file headers or JSON keys before plotting.
2. When writing or modifying plotting code, read `references/config-interface.md` for the supported controls and reproducible-data contract.
3. Use `scripts/plot_training_curves.py` when the data is CSV, TSV, JSONL, JSON, or Hugging Face `trainer_state.json`.
4. Choose the smallest chart mode that answers the request:
   - `all-separate` for the standard four independent figures: `(a) training loss`, `(b) validation loss`, `(c) training vs validation loss`, and `(d) learning-rate schedule`.
   - `training-loss` for training loss only.
   - `validation-loss` for validation/eval loss only.
   - `train-vs-val` for comparing training and validation loss.
   - `lr-schedule` for learning-rate schedule only.
   - `loss-and-lr-panels` only when the user explicitly asks for a combined panel figure.
5. When analysis code computes the plotted values, persist unsmoothed, full-precision chart-ready values to a separate CSV before drawing; keep sparse evaluation points sparse and retain the original log reference. Deliver the standalone plot script, JSON config, CSV, and PNG together (plus PDF for publication use). Changing smoothing or style must redraw from the CSV without restarting training or rerunning analysis. The bundled script generates these companion files automatically from an existing log.
6. Never silently substitute a record index for missing steps or infer absent metrics. Visually verify the rendered chart and distinguish a smoothed trend from measured values.

## Script Usage

Run from the skill directory or pass an absolute path to the script:

```bash
python scripts/plot_training_curves.py trainer_state.json --mode all-separate --smooth 25 --output training_curves.png --pdf
python scripts/plot_training_curves.py trainer_state.json --mode train-vs-val --smooth 25 --output loss_curve.png --pdf
python scripts/plot_training_curves.py metrics.csv --mode lr-schedule --output lr_schedule.png
```

Use `--spine-width 2.5` to set the frame thickness explicitly; the default is `2.5 pt`.

In `all-separate` mode, `--output training_curves.png` is treated as a prefix and creates:

- `training_curves_a_train_loss.png`
- `training_curves_b_val_loss.png`
- `training_curves_c_train_vs_val_loss.png`
- `training_curves_d_lr_schedule.png`

Use a Python environment with `matplotlib` and `numpy`. If the default `python` lacks those packages, switch to the active project, notebook, conda, or runtime Python that produced the logs.

To redraw, run `python training_curves_plot.py --config training_curves_config.json` next to the saved `training_curves_data.csv`; edit `plot.smooth`, colors, or axes in the config. The original log is not needed.

The script auto-detects common columns and keys:

- x-axis: `step`, `global_step`, or `epoch`; an index requires explicit `--x index`.
- training loss: `loss`, `train_loss`, `training_loss`, `train/loss`.
- validation loss: `eval_loss`, `validation_loss`, `val_loss`, `eval/loss`.
- learning rate: `learning_rate`, `lr`, `train/learning_rate`.

Use `--x step` or `--x epoch` when the automatic x-axis choice is not what the user wants.

## Plotting Standards

Use the bundled visual style unless the user requests a different house style:

- Use semantic default colors: training loss green, validation/eval loss red, and learning-rate schedule blue. Use the remaining low-saturation palette colors only for additional series.
- Use slightly transparent main lines rather than fully opaque strokes; the default script uses RGBA line alpha around `0.92` and line width around `2.0 pt`, which stays slightly lighter than the `2.5 pt` axes frame.
- Draw markers with semi-transparent fills and near-solid edges: keep `marker_face_alpha` around `0.6`, `marker_edge_alpha` around `0.95`, and `marker_edge_width` around `1.35`.
- Keep the complete axes frame visible and set its default spine width to `2.5 pt`, using dark neutral axes color. Keep marker edges around `1.35 pt` so they remain subordinate to the stronger frame; preserve config overrides.
- Transparent background, high-DPI PNG, and vector-friendly PDF/SVG font settings.
- Smart major/minor ticks with subtle dashed grids.
- Sparse markers on long curves so dense training logs remain readable.
- For noisy training loss, plot the raw curve faintly and the smoothed curve prominently when `--smooth` is greater than 1.
- Keep validation/eval loss markers visible because those points are usually sparse.
- Avoid dual y-axes and combined panels by default. Prefer `all-separate` for full training summaries unless the user explicitly asks for a combined panel figure.

## Config Interface

Any custom plotting code produced under this skill must read an external JSON config and chart-ready data file, with paths relative to the config, and keep user-visible plotting choices in config.

Read `references/config-interface.md` before writing or substantially modifying plotting code. Expose the controls relevant to the requested chart and avoid promising unsupported controls in the bundled script.

## Log Handling Notes

Hugging Face `trainer_state.json` usually stores useful entries under `log_history`; use the script directly on that file.

W&B CSV exports often use slash-separated names such as `train/loss` and `eval/loss`; the script normalizes common separators during key detection.

When automatic key detection fails, inspect the headers and use `--x` or `data.*_key` to name actual columns; choose `--x index` only if record index has the intended experimental meaning.
