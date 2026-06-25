# Config Interface Requirements

Generated plotting code must behave as a reusable template, not a one-off script. Define a config object, merge user overrides into defaults, and route all visual choices through that config.

## Required Structure

Expose one of these interfaces:

```python
DEFAULT_CONFIG = {...}

def plot_training_curves(records, config=None):
    config = merge_config(DEFAULT_CONFIG, config or {})
    ...
```

or:

```python
@dataclass
class PlotConfig:
    ...

def plot_training_curves(records, config: PlotConfig | None = None):
    ...
```

For command-line scripts, support `--config path.json` or `--config path.yaml` when practical. Specific CLI flags may override config values, but the plotting functions themselves must still accept a config object.

## Necessary Parameters

### Data

- `x_key`: step, global_step, epoch, iteration, or explicit column name.
- `train_loss_key`: training loss column/key candidates.
- `val_loss_key`: validation/eval loss column/key candidates.
- `lr_key`: learning-rate column/key candidates.
- `sort_by_x`: whether to sort points by x before plotting.
- `drop_nan`: whether to drop invalid metric values.
- `x_as_integer`: whether x-axis tick locator should prefer integers.
- `smoothing.enabled`: whether to smooth training loss.
- `smoothing.window`: moving-average or rolling window size.
- `smoothing.method`: centered moving average, trailing moving average, EMA, or none.
- `raw_line.enabled`: whether to show faint raw training loss under the smoothed line.
- `raw_line.width`, `raw_line.alpha`, `raw_line.linestyle`, `raw_line.label`.

### Figure Selection

- `mode`: all-separate, training-loss, validation-loss, train-vs-val, lr-schedule, or combined panel.
- `figures.enabled`: per-figure on/off controls for train, val, train_vs_val, and lr.
- `figures.order`: output order, for example `["train", "val", "train_vs_val", "lr"]`.
- `figures.filename_suffix`: suffixes such as `a_train_loss`, `b_val_loss`, `c_train_vs_val_loss`, `d_lr_schedule`.
- `figures.title`: per-figure title text.
- `figures.show_title`: per-figure title visibility.
- `figures.xlabel`, `figures.ylabel`: per-figure axis labels.

### Figure Layout

- `figsize`: default single-figure size.
- `figsize_by_mode`: optional per-mode size overrides.
- `dpi`: figure display/rendering DPI.
- `constrained_layout`: whether to use Matplotlib constrained layout.
- `tight_layout`: whether to call `fig.tight_layout()`.
- `margins.left`, `margins.right`, `margins.top`, `margins.bottom`.
- `subplot.hspace`, `subplot.wspace`.
- `panel.height_ratios`: only for combined panel figures.
- `sharex`, `sharey`: panel sharing controls.
- `aspect`: auto, equal, or explicit numeric aspect.
- `figure_facecolor`, `axes_facecolor`.
- `transparent_background`: save with transparent background.

### Fonts And Text

- `font.family`, `font.sans_serif`, `mathtext.fontset`.
- `font.size`: base font size.
- `title.size`, `title.weight`, `title.pad`.
- `label.size`, `label.pad`.
- `tick.labelsize`.
- `legend.fontsize`.
- `text.color`, `title.color`, `label.color`, `tick.color`.
- `unicode_minus`: whether to render minus signs correctly.

### Series Styles

Expose one config block per semantic series: `train_loss`, `val_loss`, and `lr`.

Each series block must support:

- `label`: legend label.
- `color`: line and marker base color.
- `linestyle`: solid, dashed, dotted, dashdot, or custom dash tuple.
- `linewidth`: visible line width.
- `line_alpha`: line transparency.
- `marker`: marker shape, such as square, triangle, diamond, circle, or none.
- `marker_size`.
- `marker_every`: explicit marker indices or Matplotlib markevery value.
- `target_markers`: desired approximate number of markers on long curves.
- `include_endpoints`: whether markers must include first/last point.
- `marker_face_alpha`: fill alpha, default around `0.6`.
- `marker_edge_alpha`: edge alpha, default around `0.95`.
- `marker_edge_width`: edge width, default around `1.2`.
- `zorder`: draw order.

Default semantic colors:

- `train_loss.color`: `#4F7C65` green.
- `val_loss.color`: `#A75B73` red.
- `lr.color`: `#516480` blue.

### Axes, Ticks, And Scales

- `xlim`, `ylim`: explicit axis limits or auto.
- `x_margin`, `y_margin`: automatic padding.
- `x_scale`, `y_scale`: linear, log, symlog.
- `target_x_ticks`, `target_y_ticks`.
- `x_integer`, `y_integer`.
- `x_minor_subdivisions`, `y_minor_subdivisions`.
- `x_tick_format`, `y_tick_format`: default, scalar, percent, scientific, or custom formatter.
- `scientific_notation`: enable for learning-rate y-axis.
- `tick.direction`: in, out, inout.
- `tick.top`, `tick.right`: whether to show top/right ticks.
- `tick.major_size`, `tick.minor_size`.
- `tick.major_width`, `tick.minor_width`.
- `tick.rotation`: per-axis tick label rotation.

### Grid And Spines

- `grid.major.enabled`, `grid.minor.enabled`.
- `grid.axis`: x, y, or both.
- `grid.color`.
- `grid.linestyle`.
- `grid.major_width`, `grid.minor_width`.
- `grid.major_alpha`, `grid.minor_alpha`.
- `spines.top`, `spines.right`, `spines.bottom`, `spines.left`: visibility.
- `spines.color`.
- `spines.linewidth`.

### Legends

Expose legend config globally and allow per-figure overrides:

- `legend.enabled`.
- `legend.loc`.
- `legend.bbox_to_anchor`.
- `legend.ncol`.
- `legend.frameon`.
- `legend.framealpha`.
- `legend.facecolor`.
- `legend.edgecolor`.
- `legend.handlelength`.
- `legend.handletextpad`.
- `legend.labelspacing`.
- `legend.columnspacing`.
- `legend.borderaxespad`.
- `legend.title`.

### Titles And Labels

Per figure, expose:

- `show_title`.
- `title`.
- `title_loc`: left, center, right.
- `title_pad`.
- `xlabel`, `ylabel`.
- `show_xlabel`, `show_ylabel`.
- `labelpad`.

### Annotations

Keep annotations disabled by default but configurable:

- `vlines`: list of vertical reference lines with x, color, linestyle, width, alpha, label.
- `hlines`: list of horizontal reference lines.
- `spans`: shaded x/y ranges.
- `point_labels.enabled`: whether to label selected points.
- `point_labels.which`: first, last, min, max, best, or explicit indices.
- `text_annotations`: arbitrary text labels with coordinates and style.

### Output

- `output_dir`.
- `filename_prefix`.
- `filename_suffix_by_figure`.
- `formats`: png, pdf, svg.
- `dpi`.
- `savefig.transparent`.
- `savefig.bbox_inches`.
- `savefig.pad_inches`.
- `pdf.fonttype`.
- `ps.fonttype`.
- `svg.fonttype`.
- `overwrite`.
- `close_figures`.

## Minimal Example

```python
DEFAULT_CONFIG = {
    "output": {
        "filename_prefix": "training_curves",
        "formats": ["png", "pdf"],
        "dpi": 300,
        "transparent": True,
    },
    "figure": {
        "figsize": (7.2, 4.6),
        "show_title": True,
    },
    "series": {
        "train_loss": {
            "label": "Training loss",
            "color": "#4F7C65",
            "linestyle": "-",
            "linewidth": 1.65,
            "line_alpha": 0.92,
            "marker": "s",
            "marker_face_alpha": 0.6,
            "marker_edge_alpha": 0.95,
            "marker_edge_width": 1.2,
        },
        "val_loss": {
            "label": "Validation loss",
            "color": "#A75B73",
            "marker": "^",
        },
        "lr": {
            "label": "Learning rate",
            "color": "#516480",
            "marker": "D",
        },
    },
    "legend": {
        "enabled": True,
        "loc": "best",
        "bbox_to_anchor": None,
        "ncol": 1,
        "frameon": False,
    },
}
```
