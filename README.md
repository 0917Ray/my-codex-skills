# My Codex Skills

<p align="center">
  <a href="README.md"><strong>English</strong></a>
  ·
  <a href="README.zh-CN.md"><strong>中文</strong></a>
</p>

This repository contains my custom Codex skills for creating polished, configurable scientific plots.

## Skills

### `plot-training-curves`

Create configurable line plots for LLM and machine-learning training logs, including:

- Training loss
- Validation loss
- Training vs. validation loss
- Learning-rate schedule

The skill emphasizes reusable plotting code with explicit config interfaces for figure size, colors, line styles, alpha, markers, titles, labels, legends, ticks, grids, and export settings.

### `plot-bar-charts`

Create configurable single and grouped bar charts for scientific comparisons, including:

- Single bar charts
- Highlighted-method bar charts
- Grouped bar charts
- Error bars and value labels

The skill also requires generated bar-plot code to expose config controls for bar width, colors, alpha, edge style, error bars, value labels, legend placement, axis settings, and export formats.

## Examples

Each preview links to the corresponding PDF file.

### Training Curves

<table>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_a_train_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_a_train_loss.png" alt="Training loss" width="100%">
      </a>
      <br>
      <strong>(a) Training loss</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_b_val_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_b_val_loss.png" alt="Validation loss" width="100%">
      </a>
      <br>
      <strong>(b) Validation loss</strong>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_c_train_vs_val_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_c_train_vs_val_loss.png" alt="Training vs validation loss" width="100%">
      </a>
      <br>
      <strong>(c) Training vs. validation loss</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_d_lr_schedule.pdf">
        <img src="assets/examples/sample_llm_training_curves_d_lr_schedule.png" alt="Learning-rate schedule" width="100%">
      </a>
      <br>
      <strong>(d) Learning-rate schedule</strong>
    </td>
  </tr>
</table>

### Bar Charts

<table>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_bar_single.pdf">
        <img src="assets/examples/sample_bar_single.png" alt="Single highlighted bar chart" width="100%">
      </a>
      <br>
      <strong>Single highlighted bar chart</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_bar_grouped.pdf">
        <img src="assets/examples/sample_bar_grouped.png" alt="Grouped bar chart" width="100%">
      </a>
      <br>
      <strong>Grouped bar chart</strong>
    </td>
  </tr>
</table>

## Installation

Install with Codex's GitHub skill installer:

```bash
python install-skill-from-github.py \
  --repo 0917Ray/my-codex-skills \
  --path skills/plot-training-curves skills/plot-bar-charts
```

Or manually copy the skill folders to your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/plot-training-curves ~/.codex/skills/
cp -R skills/plot-bar-charts ~/.codex/skills/
```

Restart Codex after installation.

## Repository Layout

```text
my-codex-skills/
├── skills/
│   ├── plot-training-curves/
│   └── plot-bar-charts/
└── assets/
    └── examples/
```

## Notes

The bundled scripts require a Python environment with `matplotlib` and `numpy`.

These skills are intended both as runnable tools and as plotting-code templates. When Codex writes new plotting code using these skills, it should expose a clear config interface rather than hard-coding visual parameters.
