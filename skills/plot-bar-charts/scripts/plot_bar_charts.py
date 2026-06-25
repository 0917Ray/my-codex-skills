#!/usr/bin/env python3
"""Plot configurable scientific single and grouped bar charts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "codex-matplotlib-cache")
)

try:
    import matplotlib as mpl

    mpl.use("Agg")

    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
except ModuleNotFoundError as exc:
    missing = exc.name or "required plotting package"
    raise SystemExit(
        f"Missing Python dependency: {missing}. Run this script with a Python "
        "environment that includes matplotlib and numpy."
    ) from exc


DEFAULT_CONFIG: dict[str, Any] = {
    "figure": {
        "figsize": [6.8, 4.4],
        "grouped_figsize": [7.4, 4.6],
        "dpi": 140,
        "transparent_background": True,
        "tight_layout": True,
    },
    "font": {
        "family": "sans-serif",
        "sans_serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "size": 12,
        "title_size": 13,
        "label_size": 12,
        "tick_size": 11,
        "legend_size": 10.5,
    },
    "colors": {
        "blue": "#516480",
        "green": "#4F7C65",
        "red": "#A75B73",
        "purple": "#75668A",
        "orange": "#C48755",
        "cyan": "#5C8FA3",
        "olive": "#7F8956",
        "brown": "#8A6A58",
        "dark": "#303236",
        "axis": "#3A3D42",
        "grid": "#DADDE2",
        "bar_gray_face": "#C9CED3",
        "bar_gray_edge": "#AEB5BC",
    },
    "bars": {
        "bar_width": 0.58,
        "group_width": 0.74,
        "face_alpha": 0.5,
        "edge_alpha": 0.95,
        "edge_width": 1.65,
        "color_mode": "highlight",
        "highlight_color": "#A75B73",
        "palette": [
            "#516480",
            "#4F7C65",
            "#A75B73",
            "#75668A",
            "#5C8FA3",
            "#C48755",
            "#7F8956",
            "#8A6A58",
        ],
    },
    "errorbar": {
        "enabled": True,
        "color": "#3A3D42",
        "alpha": 0.82,
        "linewidth": 1.05,
        "capsize": 3.2,
        "capthick": 1.05,
    },
    "axis": {
        "target_y_ticks": 6,
        "y_minor_subdivisions": 2,
        "top_margin": 0.24,
        "label_top_margin": 0.30,
        "lower_margin": 0.04,
        "zero_baseline": True,
        "x_tick_rotation": 0,
        "y_tick_format": None,
    },
    "grid": {
        "major_alpha": 0.80,
        "minor_alpha": 0.28,
        "major_width": 0.75,
        "minor_width": 0.45,
        "linestyle": "--",
    },
    "spines": {
        "top": True,
        "right": True,
        "linewidth": 1.05,
    },
    "value_labels": {
        "enabled": True,
        "format": "{:.1f}",
        "offset_fraction": 0.035,
        "fontsize": 9.5,
        "reserve_space": True,
        "pad_pixels": 8,
        "max_iter": 4,
    },
    "legend": {
        "enabled": True,
        "loc": "best",
        "grouped_loc": "upper center",
        "grouped_bbox_to_anchor": [0.5, 1.14],
        "frameon": False,
        "ncol": None,
        "columnspacing": 1.1,
    },
    "text": {
        "title": None,
        "xlabel": None,
        "ylabel": None,
    },
    "output": {
        "dpi": 300,
        "bbox_inches": "tight",
        "pad_inches": 0.04,
        "transparent": True,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except ModuleNotFoundError as exc:
                raise SystemExit("YAML config requires PyYAML. Use JSON or install pyyaml.") from exc
            data = yaml.safe_load(handle) or {}
        else:
            data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Config file must contain an object/dictionary.")
    return data


def rgba(color: str, alpha: float) -> tuple[float, float, float, float]:
    return mcolors.to_rgba(color, alpha)


def to_float(value: Any) -> float:
    if value is None or isinstance(value, bool):
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            for key in ("data", "records", "rows"):
                if isinstance(data.get(key), list):
                    return [row for row in data[key] if isinstance(row, dict)]
    raise ValueError(f"Unsupported input format: {path}")


def set_style(config: dict[str, Any], figure_size: list[float]) -> None:
    font = config["font"]
    c = config["colors"]
    output = config["output"]
    figure = config["figure"]
    spines = config["spines"]

    mpl.rcParams.update(
        {
            "font.family": font["family"],
            "font.sans-serif": font["sans_serif"],
            "font.size": font["size"],
            "mathtext.fontset": "stixsans",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.figsize": tuple(figure_size),
            "figure.dpi": figure["dpi"],
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "savefig.edgecolor": "none",
            "savefig.transparent": output["transparent"],
            "savefig.dpi": output["dpi"],
            "savefig.bbox": output["bbox_inches"],
            "savefig.pad_inches": output["pad_inches"],
            "axes.linewidth": spines["linewidth"],
            "axes.edgecolor": c["axis"],
            "axes.labelcolor": c["dark"],
            "axes.titlecolor": c["dark"],
            "axes.labelsize": font["label_size"],
            "axes.titlesize": font["title_size"],
            "axes.titleweight": "regular",
            "axes.axisbelow": True,
            "axes.spines.top": spines["top"],
            "axes.spines.right": spines["right"],
            "xtick.labelsize": font["tick_size"],
            "ytick.labelsize": font["tick_size"],
            "xtick.color": c["axis"],
            "ytick.color": c["axis"],
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": False,
            "ytick.right": True,
            "xtick.major.size": 0,
            "ytick.major.size": 4.2,
            "ytick.major.width": 1.0,
            "ytick.minor.size": 2.2,
            "ytick.minor.width": 0.75,
            "legend.fontsize": font["legend_size"],
            "legend.frameon": config["legend"]["frameon"],
            "legend.handlelength": 1.4,
            "legend.handletextpad": 0.5,
            "legend.labelspacing": 0.35,
        }
    )


def apply_axis_style(
    ax: plt.Axes,
    y_values: np.ndarray,
    y_errors: np.ndarray | None,
    config: dict[str, Any],
    value_labels: bool = False,
) -> float:
    c = config["colors"]
    axis = config["axis"]
    grid = config["grid"]

    y_values = np.asarray(y_values, dtype=float)
    if y_errors is None:
        y_errors = np.zeros_like(y_values, dtype=float)
    else:
        y_errors = np.asarray(y_errors, dtype=float)

    y_low = float(np.nanmin(y_values - y_errors))
    y_high = float(np.nanmax(y_values + y_errors))
    data_span = y_high - y_low
    if data_span == 0:
        data_span = max(abs(y_high), 1.0)

    lower = (
        0
        if axis["zero_baseline"] and y_low >= 0
        else y_low - axis["lower_margin"] * data_span
    )
    top_margin = axis["label_top_margin"] if value_labels else axis["top_margin"]
    upper = y_high + top_margin * data_span
    ax.set_ylim(lower, upper)

    ax.yaxis.set_major_locator(
        mticker.MaxNLocator(
            nbins=axis["target_y_ticks"],
            steps=[1, 2, 2.5, 5, 10],
            min_n_ticks=4,
        )
    )
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(axis["y_minor_subdivisions"]))
    if axis["y_tick_format"]:
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter(axis["y_tick_format"]))

    ax.grid(
        True,
        which="major",
        axis="y",
        color=c["grid"],
        linestyle=grid["linestyle"],
        linewidth=grid["major_width"],
        alpha=grid["major_alpha"],
    )
    ax.grid(
        True,
        which="minor",
        axis="y",
        color=c["grid"],
        linestyle=grid["linestyle"],
        linewidth=grid["minor_width"],
        alpha=grid["minor_alpha"],
    )
    ax.grid(False, axis="x")
    return data_span


def add_value_labels(
    ax: plt.Axes,
    bars: Any,
    values: np.ndarray,
    errors: np.ndarray | None,
    data_span: float,
    config: dict[str, Any],
) -> list[Any]:
    labels_cfg = config["value_labels"]
    c = config["colors"]
    if errors is None:
        errors = np.zeros_like(values, dtype=float)
    offset = labels_cfg["offset_fraction"] * data_span
    texts = []
    for bar, value, err in zip(bars, values, errors):
        text = ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + err + offset,
            labels_cfg["format"].format(value),
            ha="center",
            va="bottom",
            fontsize=labels_cfg["fontsize"],
            color=c["dark"],
            clip_on=False,
        )
        texts.append(text)
    return texts


def reserve_space_for_labels(ax: plt.Axes, texts: list[Any], config: dict[str, Any]) -> None:
    labels_cfg = config["value_labels"]
    if not texts or not labels_cfg["reserve_space"]:
        return
    fig = ax.figure
    for _ in range(labels_cfg["max_iter"]):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        text_top = max(text.get_window_extent(renderer).y1 for text in texts if text.get_visible())
        axes_top = ax.bbox.y1
        overflow = text_top + labels_cfg["pad_pixels"] - axes_top
        if overflow <= 0:
            break
        y0, y1 = ax.get_ylim()
        pixel_to_data = (y1 - y0) / ax.bbox.height
        ax.set_ylim(y0, y1 + overflow * pixel_to_data * 1.25)


def error_kw(config: dict[str, Any]) -> dict[str, Any]:
    err = config["errorbar"]
    return {
        "ecolor": rgba(err["color"], err["alpha"]),
        "elinewidth": err["linewidth"],
        "capsize": err["capsize"],
        "capthick": err["capthick"],
    }


def apply_text(ax: plt.Axes, config: dict[str, Any]) -> None:
    text = config["text"]
    if text.get("title"):
        ax.set_title(text["title"])
    if text.get("xlabel"):
        ax.set_xlabel(text["xlabel"])
    if text.get("ylabel"):
        ax.set_ylabel(text["ylabel"])


def plot_single_bar(
    labels: list[str],
    values: np.ndarray,
    errors: np.ndarray | None,
    config: dict[str, Any],
    highlight_label: str | None = None,
) -> plt.Figure:
    set_style(config, config["figure"]["figsize"])
    fig, ax = plt.subplots()
    c = config["colors"]
    bars_cfg = config["bars"]
    x = np.arange(len(labels))

    if bars_cfg["color_mode"] == "highlight" and highlight_label in labels:
        highlight_index = labels.index(highlight_label)
        face_colors = [c["bar_gray_face"]] * len(labels)
        edge_colors = [c["bar_gray_edge"]] * len(labels)
        face_colors[highlight_index] = bars_cfg["highlight_color"]
        edge_colors[highlight_index] = bars_cfg["highlight_color"]
    else:
        palette = bars_cfg["palette"]
        face_colors = [palette[i % len(palette)] for i in range(len(labels))]
        edge_colors = face_colors

    yerr = errors if config["errorbar"]["enabled"] else None
    bars = ax.bar(
        x,
        values,
        yerr=yerr,
        width=bars_cfg["bar_width"],
        color=[rgba(color, bars_cfg["face_alpha"]) for color in face_colors],
        edgecolor=[rgba(color, bars_cfg["edge_alpha"]) for color in edge_colors],
        linewidth=bars_cfg["edge_width"],
        error_kw=error_kw(config),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=config["axis"]["x_tick_rotation"])
    data_span = apply_axis_style(
        ax, values, errors, config, value_labels=config["value_labels"]["enabled"]
    )
    texts = []
    if config["value_labels"]["enabled"]:
        texts = add_value_labels(ax, bars, values, errors, data_span, config)
    apply_text(ax, config)
    if config["figure"]["tight_layout"]:
        fig.tight_layout()
    reserve_space_for_labels(ax, texts, config)
    return fig


def plot_grouped_bar(
    group_labels: list[str],
    series_names: list[str],
    values: np.ndarray,
    errors: np.ndarray | None,
    config: dict[str, Any],
) -> plt.Figure:
    set_style(config, config["figure"]["grouped_figsize"])
    fig, ax = plt.subplots()
    bars_cfg = config["bars"]
    legend_cfg = config["legend"]
    n_groups, n_series = values.shape
    x = np.arange(n_groups)
    bar_width = bars_cfg["group_width"] / n_series
    offsets = (np.arange(n_series) - (n_series - 1) / 2) * bar_width
    palette = bars_cfg["palette"]

    for j, name in enumerate(series_names):
        yerr = None
        if errors is not None and config["errorbar"]["enabled"]:
            yerr = errors[:, j]
        color = palette[j % len(palette)]
        ax.bar(
            x + offsets[j],
            values[:, j],
            yerr=yerr,
            width=bar_width * 0.88,
            label=name,
            color=rgba(color, bars_cfg["face_alpha"]),
            edgecolor=rgba(color, bars_cfg["edge_alpha"]),
            linewidth=bars_cfg["edge_width"],
            error_kw=error_kw(config),
        )

    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, rotation=config["axis"]["x_tick_rotation"])
    apply_axis_style(ax, values, errors, config, value_labels=False)
    apply_text(ax, config)
    if legend_cfg["enabled"]:
        ncol = legend_cfg["ncol"] or min(n_series, 3)
        ax.legend(
            loc=legend_cfg["grouped_loc"],
            bbox_to_anchor=tuple(legend_cfg["grouped_bbox_to_anchor"]),
            ncol=ncol,
            columnspacing=legend_cfg["columnspacing"],
        )
    if config["figure"]["tight_layout"]:
        fig.tight_layout()
    return fig


def save_figure(fig: plt.Figure, output: Path, pdf: bool, config: dict[str, Any]) -> list[Path]:
    if output.suffix == "":
        output = output.with_suffix(".png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, transparent=config["output"]["transparent"])
    saved = [output]
    if pdf:
        pdf_path = output.with_suffix(".pdf")
        fig.savefig(pdf_path, transparent=config["output"]["transparent"])
        saved.append(pdf_path)
    return saved


def parse_single(records: list[dict[str, Any]], label_col: str, value_col: str, error_col: str | None):
    labels = []
    values = []
    errors = [] if error_col else None
    for row in records:
        labels.append(str(row[label_col]))
        values.append(to_float(row[value_col]))
        if error_col and errors is not None:
            errors.append(to_float(row.get(error_col)))
    return labels, np.asarray(values, dtype=float), None if errors is None else np.asarray(errors)


def parse_grouped(
    records: list[dict[str, Any]],
    group_col: str,
    series_col: str,
    value_col: str,
    error_col: str | None,
):
    groups = list(dict.fromkeys(str(row[group_col]) for row in records))
    series = list(dict.fromkeys(str(row[series_col]) for row in records))
    values = np.full((len(groups), len(series)), np.nan)
    errors = np.full((len(groups), len(series)), np.nan) if error_col else None
    group_index = {name: i for i, name in enumerate(groups)}
    series_index = {name: i for i, name in enumerate(series)}
    for row in records:
        i = group_index[str(row[group_col])]
        j = series_index[str(row[series_col])]
        values[i, j] = to_float(row[value_col])
        if error_col and errors is not None:
            errors[i, j] = to_float(row.get(error_col))
    return groups, series, values, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot scientific single or grouped bar charts.")
    parser.add_argument("input", type=Path, help="CSV, TSV, or JSON table.")
    parser.add_argument("--mode", choices=["single", "grouped"], required=True)
    parser.add_argument("--config", type=Path, default=None, help="Optional JSON/YAML config.")
    parser.add_argument("--label-column", default=None, help="Category label column for single mode.")
    parser.add_argument("--group-column", default=None, help="Group/category column for grouped mode.")
    parser.add_argument("--series-column", default=None, help="Series column for grouped mode.")
    parser.add_argument("--value-column", required=True, help="Metric value column.")
    parser.add_argument("--error-column", default=None, help="Optional symmetric error column.")
    parser.add_argument("--highlight-label", default=None, help="Single-mode label to highlight.")
    parser.add_argument("--title", default=None)
    parser.add_argument("--xlabel", default=None)
    parser.add_argument("--ylabel", default=None)
    parser.add_argument("--output", type=Path, default=Path("bar_chart.png"))
    parser.add_argument("--pdf", action="store_true", help="Also save a companion PDF.")
    parser.add_argument("--no-value-labels", action="store_true")
    parser.add_argument("--no-legend", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = deep_merge(DEFAULT_CONFIG, load_config(args.config))
    if args.title:
        config["text"]["title"] = args.title
    if args.xlabel:
        config["text"]["xlabel"] = args.xlabel
    if args.ylabel:
        config["text"]["ylabel"] = args.ylabel
    if args.no_value_labels:
        config["value_labels"]["enabled"] = False
    if args.no_legend:
        config["legend"]["enabled"] = False

    records = load_records(args.input)
    if not records:
        raise ValueError(f"No records found in {args.input}")

    if args.mode == "single":
        if not args.label_column:
            raise ValueError("--label-column is required for single mode.")
        labels, values, errors = parse_single(
            records, args.label_column, args.value_column, args.error_column
        )
        fig = plot_single_bar(labels, values, errors, config, args.highlight_label)
    else:
        if not args.group_column or not args.series_column:
            raise ValueError("--group-column and --series-column are required for grouped mode.")
        groups, series, values, errors = parse_grouped(
            records,
            args.group_column,
            args.series_column,
            args.value_column,
            args.error_column,
        )
        fig = plot_grouped_bar(groups, series, values, errors, config)

    saved = save_figure(fig, args.output, args.pdf, config)
    for path in saved:
        print(path)


if __name__ == "__main__":
    main()
