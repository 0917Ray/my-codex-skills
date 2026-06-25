# My Codex Skills / 我的 Codex Skills

This repository contains my custom Codex skills for creating polished, configurable scientific plots.

本仓库包含我的自定义 Codex skills，用于绘制风格统一、可配置、适合科研展示的图表。

## Skills / Skills 列表

### `plot-training-curves`

Create configurable line plots for LLM and machine-learning training logs.

用于绘制 LLM / 机器学习训练日志曲线，包括：

- Training loss / 训练损失
- Validation loss / 验证损失
- Training vs. validation loss / 训练损失与验证损失对比
- Learning-rate schedule / 学习率调度

The skill emphasizes reusable plotting code with explicit config interfaces for figure size, colors, line styles, alpha, markers, titles, labels, legends, ticks, grids, and export settings.

该 skill 强调可复用绘图代码，要求显式预留 config 接口，用于控制图尺寸、颜色、线型、透明度、marker、标题、坐标轴标签、图例、刻度、网格和导出参数。

### `plot-bar-charts`

Create configurable single and grouped bar charts for scientific comparisons.

用于绘制科研对比类柱状图，包括：

- Single bar charts / 单组柱状图
- Highlighted-method bar charts / 突出某个方法的柱状图
- Grouped bar charts / 分组柱状图
- Error bars and value labels / 误差条与数值标签

The skill also requires generated bar-plot code to expose config controls for bar width, colors, alpha, edge style, error bars, value labels, legend placement, axis settings, and export formats.

该 skill 同样要求生成的柱状图代码预留 config 控制项，包括柱宽、颜色、透明度、边框、误差条、数值标签、图例位置、坐标轴设置和导出格式。

## Examples / 效果示例

Each preview links to the corresponding PDF file.

每张预览图都可以点击打开对应的 PDF 文件。

### Training Curves / 训练曲线

<table>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_a_train_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_a_train_loss.png" alt="Training loss" width="100%">
      </a>
      <br>
      <strong>(a) Training loss / 训练损失</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_b_val_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_b_val_loss.png" alt="Validation loss" width="100%">
      </a>
      <br>
      <strong>(b) Validation loss / 验证损失</strong>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_c_train_vs_val_loss.pdf">
        <img src="assets/examples/sample_llm_training_curves_c_train_vs_val_loss.png" alt="Training vs validation loss" width="100%">
      </a>
      <br>
      <strong>(c) Training vs. validation loss / 训练损失与验证损失对比</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_llm_training_curves_d_lr_schedule.pdf">
        <img src="assets/examples/sample_llm_training_curves_d_lr_schedule.png" alt="Learning-rate schedule" width="100%">
      </a>
      <br>
      <strong>(d) Learning-rate schedule / 学习率调度</strong>
    </td>
  </tr>
</table>

### Bar Charts / 柱状图

<table>
  <tr>
    <td align="center" width="50%">
      <a href="assets/examples/sample_bar_single.pdf">
        <img src="assets/examples/sample_bar_single.png" alt="Single highlighted bar chart" width="100%">
      </a>
      <br>
      <strong>Single highlighted bar chart / 单组高亮柱状图</strong>
    </td>
    <td align="center" width="50%">
      <a href="assets/examples/sample_bar_grouped.pdf">
        <img src="assets/examples/sample_bar_grouped.png" alt="Grouped bar chart" width="100%">
      </a>
      <br>
      <strong>Grouped bar chart / 分组柱状图</strong>
    </td>
  </tr>
</table>

## Installation / 安装

Install with Codex's GitHub skill installer:

可以使用 Codex 的 GitHub skill installer 安装：

```bash
python install-skill-from-github.py \
  --repo 0917Ray/my-codex-skills \
  --path skills/plot-training-curves skills/plot-bar-charts
```

Or manually copy the skill folders to your Codex skills directory:

也可以手动复制 skill 文件夹到 Codex 的 skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R skills/plot-training-curves ~/.codex/skills/
cp -R skills/plot-bar-charts ~/.codex/skills/
```

Restart Codex after installation.

安装后需要重启 Codex 才能识别新 skills。

## Repository Layout / 仓库结构

```text
my-codex-skills/
├── skills/
│   ├── plot-training-curves/
│   └── plot-bar-charts/
└── assets/
    └── examples/
```

## Notes / 说明

The bundled scripts require a Python environment with `matplotlib` and `numpy`.

脚本需要 Python 环境中安装 `matplotlib` 和 `numpy`。

These skills are intended both as runnable tools and as plotting-code templates. When Codex writes new plotting code using these skills, it should expose a clear config interface rather than hard-coding visual parameters.

这些 skills 既可以作为可运行工具，也可以作为绘图代码模板。Codex 使用这些 skills 编写新绘图代码时，应提供清晰的 config 接口，而不是把视觉参数硬编码在绘图语句中。
