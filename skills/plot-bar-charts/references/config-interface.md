# Config Interface Requirements

Generated bar-chart code must behave as a reusable template, not a one-off script. Define a config object, merge user overrides into defaults, and route all visual choices through that config.

## Required Structure

Expose one of these interfaces:

```python
DEFAULT_CONFIG = {...}

def plot_bar_chart(records, config=None):
    config = merge_config(DEFAULT_CONFIG, config or {})
    ...
```

or:

```python
@dataclass
class BarPlotConfig:
    ...

def plot_bar_chart(records, config: BarPlotConfig | None = None):
    ...
```

For command-line scripts, support `--config path.json` or `--config path.yaml` when practical. Specific CLI flags may override config values, but plotting functions must still accept a config object.

## Necessary Parameters

### Data

- `mode`: single, grouped, horizontal, stacked, or diverging when supported.
- `label_column`: category column for single bars.
- `group_column`: group/category column for grouped bars.
- `series_column`: series column for grouped bars.
- `value_column`: metric column.
- `error_column`: optional symmetric error column.
- `lower_error_column`, `upper_error_column`: optional asymmetric errors.
- `category_order`: explicit category order.
- `series_order`: explicit series order.
- `sort_by`: none, value, label, group, series, custom.
- `sort_ascending`.
- `drop_nan`.
- `value_scale`: raw, percent, basis points, custom transform.

### Figure Selection And Layout

- `figsize`: default figure size.
- `figsize_by_mode`: optional size overrides.
- `orientation`: vertical or horizontal.
- `dpi`.
- `constrained_layout`.
- `tight_layout`.
- `margins.left`, `margins.right`, `margins.top`, `margins.bottom`.
- `subplot.hspace`, `subplot.wspace`.
- `figure_facecolor`, `axes_facecolor`.
- `transparent_background`.

### Bars

- `bar_width`: width for single bars.
- `group_width`: total width allocated to each group.
- `bar_gap`: spacing inside groups.
- `group_gap`: spacing between groups when manually positioned.
- `face_alpha`: default around `0.5`.
- `edge_alpha`: default around `0.95`.
- `edge_width`: default around `1.65`.
- `bar_zorder`.
- `color_mode`: palette, highlight, semantic, manual.
- `palette`: ordered color list.
- `series_colors`: mapping from series name to color.
- `bar_colors`: mapping from category label to color.
- `highlight_label` or `highlight_index`.
- `highlight_color`: default red.
- `non_highlight_face_color`: neutral gray.
- `non_highlight_edge_color`: neutral gray edge.
- `hatch`: per-series or per-category hatch pattern when needed.

### Error Bars

- `errorbar.enabled`.
- `errorbar.color`.
- `errorbar.alpha`.
- `errorbar.linewidth`.
- `errorbar.capsize`.
- `errorbar.capthick`.
- `errorbar.zorder`.

### Value Labels

- `value_labels.enabled`.
- `value_labels.format`: e.g. `{:.1f}`, `{:.2%}`.
- `value_labels.position`: outside, inside, center, below.
- `value_labels.offset_fraction`.
- `value_labels.fontsize`.
- `value_labels.color`.
- `value_labels.rotation`.
- `value_labels.reserve_space`.
- `value_labels.pad_pixels`.
- `value_labels.clip_on`.
- `value_labels.show_errors`: whether to include uncertainty in text.

### Axes, Ticks, And Scales

- `xlim`, `ylim`: explicit limits or auto.
- `x_margin`, `y_margin`.
- `zero_baseline`: default true for positive metrics.
- `top_margin`, `lower_margin`.
- `x_scale`, `y_scale`: linear, log, symlog.
- `target_x_ticks`, `target_y_ticks`.
- `x_tick_format`, `y_tick_format`: default, scalar, percent, scientific, custom.
- `x_tick_rotation`, `y_tick_rotation`.
- `tick.direction`: in, out, inout.
- `tick.top`, `tick.right`.
- `tick.major_size`, `tick.minor_size`.
- `tick.major_width`, `tick.minor_width`.
- `minor_ticks.enabled`.
- `minor_ticks.subdivisions`.

### Grid And Spines

- `grid.major.enabled`, `grid.minor.enabled`.
- `grid.axis`: y by default for vertical bars.
- `grid.color`.
- `grid.linestyle`.
- `grid.major_width`, `grid.minor_width`.
- `grid.major_alpha`, `grid.minor_alpha`.
- `spines.top`, `spines.right`, `spines.bottom`, `spines.left`.
- `spines.color`.
- `spines.linewidth`.

### Fonts, Titles, And Labels

- `font.family`, `font.sans_serif`, `mathtext.fontset`.
- `font.size`.
- `title.enabled`, `title.text`, `title.size`, `title.weight`, `title.pad`, `title.loc`.
- `xlabel.enabled`, `xlabel.text`, `xlabel.size`, `xlabel.pad`.
- `ylabel.enabled`, `ylabel.text`, `ylabel.size`, `ylabel.pad`.
- `tick.labelsize`.
- `text.color`, `title.color`, `label.color`, `tick.color`.
- `unicode_minus`.

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

### Annotations

Keep annotations disabled by default but configurable:

- `reference_lines`: horizontal or vertical reference lines.
- `spans`: shaded x/y ranges.
- `significance.enabled`: brackets and p-value/star annotations.
- `text_annotations`: arbitrary text labels with coordinates and style.

### Output

- `output_dir`.
- `filename`.
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
    "figure": {
        "figsize": (6.8, 4.4),
        "dpi": 140,
        "transparent_background": True,
    },
    "bars": {
        "bar_width": 0.58,
        "group_width": 0.74,
        "face_alpha": 0.5,
        "edge_alpha": 0.95,
        "edge_width": 1.65,
        "highlight_color": "#A75B73",
        "non_highlight_face_color": "#C9CED3",
        "non_highlight_edge_color": "#AEB5BC",
    },
    "errorbar": {
        "enabled": True,
        "color": "#3A3D42",
        "alpha": 0.82,
        "linewidth": 1.05,
        "capsize": 3.2,
        "capthick": 1.05,
    },
    "value_labels": {
        "enabled": True,
        "format": "{:.1f}",
        "offset_fraction": 0.035,
        "fontsize": 9.5,
        "reserve_space": True,
    },
    "legend": {
        "enabled": True,
        "loc": "best",
        "frameon": False,
        "ncol": 1,
    },
}
```
