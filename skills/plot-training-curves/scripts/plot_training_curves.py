#!/usr/bin/env python3
"""Plot LLM training loss, validation loss, and learning-rate curves."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

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
    from cycler import cycler
except ModuleNotFoundError as exc:
    missing = exc.name or "required plotting package"
    raise SystemExit(
        f"Missing Python dependency: {missing}. Run this script with a Python "
        "environment that includes matplotlib and numpy."
    ) from exc


TRAIN_LOSS_KEYS = [
    "loss",
    "train_loss",
    "training_loss",
    "train/loss",
    "train.loss",
    "train loss",
]
VAL_LOSS_KEYS = [
    "eval_loss",
    "validation_loss",
    "val_loss",
    "valid_loss",
    "dev_loss",
    "eval/loss",
    "validation/loss",
    "val/loss",
]
LR_KEYS = [
    "learning_rate",
    "lr",
    "learning rate",
    "train/learning_rate",
    "train/lr",
    "optimizer_lr",
]
X_KEYS = [
    "step",
    "global_step",
    "global step",
    "iteration",
    "iter",
    "epoch",
]


def COLORS() -> dict[str, str]:
    return {
        # Preferred color
        "blue": "#5B7CA7",
        "green": "#5E887E",
        "red": "#BA6580",
        "purple": "#75668A",

        # Optional color
        "orange": "#C48755",
        "cyan": "#5C8FA3",
        "olive": "#7F8956",
        "brown": "#8A6A58",
    }


@dataclass
class Series:
    x: np.ndarray
    y: np.ndarray
    name: str
    x_key: str
    y_key: str


DEFAULT_CONFIG: dict[str, Any] = {
    "data": {"input": None, "source": None, "x": "auto", "train_loss_key": None,
             "val_loss_key": None, "lr_key": None},
    "plot": {"mode": "auto", "smooth": 1, "title": None,
             "titles": {"training-loss": "(a) Training Loss",
                        "validation-loss": "(b) Validation Loss",
                        "train-vs-val": "(c) Training vs. Validation Loss",
                        "lr-schedule": "(d) Learning Rate Schedule"}},
    "figure": {"figsize": [7.2, 4.6], "panel_figsize": [7.4, 5.8], "dpi": 300,
               "spine_width": 2.5, "transparent": True},
    "series": {
        "train_loss": {"color": COLORS()["green"], "linewidth": 2.0, "line_alpha": 0.92,
                       "marker": "s", "marker_size": 5.0, "marker_face_alpha": 0.6,
                       "marker_edge_alpha": 0.95, "marker_edge_width": 1.35},
        "val_loss": {"color": COLORS()["red"], "linewidth": 2.0, "line_alpha": 0.92,
                     "marker": "^", "marker_size": 5.2, "marker_face_alpha": 0.6,
                     "marker_edge_alpha": 0.95, "marker_edge_width": 1.35},
        "lr": {"color": COLORS()["blue"], "linewidth": 2.0, "line_alpha": 0.92,
               "marker": "D", "marker_size": 4.8, "marker_face_alpha": 0.6,
               "marker_edge_alpha": 0.95, "marker_edge_width": 1.35},
    },
    "axis": {"target_x_ticks": 9, "target_y_ticks": 7, "y_margin": 0.07,
             "xlim": None, "ylim": None, "grid": True, "xlabel": None,
             "x_integer": None},
    "legend": {"enabled": True, "loc": "best"},
    "output": {"filename": "training_curves.png", "pdf": False},
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
        if path.suffix.lower() in {".yml", ".yaml"}:
            try:
                import yaml
            except ModuleNotFoundError as exc:
                raise SystemExit("YAML config requires PyYAML. Use JSON or install pyyaml.") from exc
            result = yaml.safe_load(handle) or {}
        else:
            result = json.load(handle)
    if not isinstance(result, dict):
        raise ValueError("Config must contain a mapping/object.")
    return result


def neutrals() -> dict[str, str]:
    return {
        "dark": "#303236",
        "axis": "#3A3D42",
        "tick": "#3A3D42",
        "grid": "#E3E5E8",
    }


def set_line_plot_style(
    fontsize: float = 12,
    title_size: float = 13,
    label_size: float = 12,
    tick_size: float = 11,
    legend_size: float = 10.5,
    line_width: float = 2.0,
    figure_size: tuple[float, float] = (7.2, 4.6),
    spine_width: float = 2.5,
    config: dict[str, Any] | None = None,
) -> None:
    if config is not None:
        figure_size = tuple(figure_size)
        spine_width = config["figure"]["spine_width"]
    c = COLORS()
    n = neutrals()

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": fontsize,
            "mathtext.fontset": "stixsans",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.figsize": figure_size,
            "figure.dpi": 140,
            "figure.facecolor": "none" if config is None or config["figure"]["transparent"] else "white",
            "axes.facecolor": "none" if config is None or config["figure"]["transparent"] else "white",
            "savefig.facecolor": "none" if config is None or config["figure"]["transparent"] else "white",
            "savefig.edgecolor": "none" if config is None or config["figure"]["transparent"] else "white",
            "savefig.transparent": True if config is None else config["figure"]["transparent"],
            "savefig.dpi": 300 if config is None else config["figure"]["dpi"],
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "axes.prop_cycle": cycler(
                color=[
                    c["blue"],
                    c["red"],
                    c["green"],
                    c["purple"],
                    c["cyan"],
                    c["orange"],
                    c["olive"],
                    c["brown"],
                ]
            ),
            "lines.linewidth": line_width,
            "lines.markersize": 5.0,
            "lines.markeredgewidth": 1.35,
            "lines.solid_capstyle": "round",
            "lines.solid_joinstyle": "round",
            "lines.antialiased": True,
            "axes.linewidth": spine_width,
            "axes.edgecolor": n["axis"],
            "axes.labelcolor": n["dark"],
            "axes.titlecolor": n["dark"],
            "axes.labelsize": label_size,
            "axes.titlesize": title_size,
            "axes.titleweight": "regular",
            "axes.axisbelow": True,
            "axes.spines.top": True,
            "axes.spines.right": True,
            "axes.spines.bottom": True,
            "axes.spines.left": True,
            "xtick.labelsize": tick_size,
            "ytick.labelsize": tick_size,
            "xtick.color": n["axis"],
            "ytick.color": n["axis"],
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 4.2,
            "ytick.major.size": 4.2,
            "xtick.major.width": 1.1,
            "ytick.major.width": 1.1,
            "xtick.minor.size": 2.2,
            "ytick.minor.size": 2.2,
            "xtick.minor.width": 0.8,
            "ytick.minor.width": 0.8,
            "axes.grid": True,
            "grid.color": n["grid"],
            "grid.linestyle": "--",
            "grid.linewidth": 0.75,
            "grid.alpha": 0.8,
            "legend.fontsize": legend_size,
            "legend.frameon": False,
            "legend.handlelength": 2.2,
            "legend.handletextpad": 0.6,
            "legend.labelspacing": 0.35,
        }
    )


def line_colors() -> list[str]:
    c = COLORS()
    return [
        c["blue"],
        c["red"],
        c["green"],
        c["purple"],
        c["cyan"],
        c["orange"],
        c["olive"],
        c["brown"],
    ]


def markers() -> list[str]:
    return ["s", "^", "D", "o", "v", "h", "X"]


def rgba(color: str, alpha: float) -> tuple[float, float, float, float]:
    return mcolors.to_rgba(color, alpha)


def auto_marker_indices(
    n_points: int,
    target_markers: int = 9,
    include_endpoints: bool = False,
) -> np.ndarray:
    if n_points <= 0:
        return np.array([], dtype=int)

    if n_points <= target_markers:
        idx = np.arange(n_points)
    else:
        step = int(np.ceil(n_points / target_markers))
        idx = np.arange(0, n_points, step)

    if include_endpoints and idx[-1] != n_points - 1:
        idx = np.r_[idx, n_points - 1]

    if not include_endpoints and n_points > 2:
        idx = idx[(idx != 0) & (idx != n_points - 1)]
        if len(idx) == 0:
            idx = np.array([n_points // 2])

    return idx


def plot_line_with_auto_marker(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    label: str | None = None,
    index: int = 0,
    color: str | None = None,
    marker: str | None = None,
    linewidth: float | None = None,
    line_alpha: float = 0.92,
    target_markers: int = 9,
    include_endpoints: bool = False,
    marker_size: float = 5,
    marker_edge_width: float = 1.35,
    marker_face_alpha: float = 0.6,
    marker_edge_alpha: float = 0.95,
    zorder: int = 3,
) -> None:
    palette = line_colors()
    marker_cycle = markers()

    if color is None:
        color = palette[index % len(palette)]
    if marker is None:
        marker = marker_cycle[index % len(marker_cycle)]

    idx = auto_marker_indices(
        len(x), target_markers=target_markers, include_endpoints=include_endpoints
    )

    ax.plot(
        x,
        y,
        color=rgba(color, line_alpha),
        linewidth=linewidth,
        marker=marker,
        markevery=idx,
        markersize=marker_size,
        markerfacecolor=rgba(color, marker_face_alpha),
        markeredgecolor=rgba(color, marker_edge_alpha),
        markeredgewidth=marker_edge_width,
        label=label,
        zorder=zorder,
    )


def apply_smart_ticks(
    ax: plt.Axes,
    x_data: np.ndarray | None = None,
    y_data: np.ndarray | None = None,
    target_x_ticks: int = 8,
    target_y_ticks: int = 6,
    x_integer: bool = True,
    y_integer: bool = False,
    x_minor_subdivisions: int = 2,
    y_minor_subdivisions: int = 2,
    show_y_minor_grid: bool = True,
    x_margin: float = 0.0,
    y_margin: float = 0.05,
    config: dict[str, Any] | None = None,
) -> None:
    if config is not None:
        axis = config["axis"]
        target_x_ticks = axis["target_x_ticks"]
        target_y_ticks = axis["target_y_ticks"]
        y_margin = axis["y_margin"]
    n = neutrals()

    if x_data is not None and len(x_data) > 0:
        x_min = float(np.nanmin(x_data))
        x_max = float(np.nanmax(x_data))
        x_range = x_max - x_min
        if x_range == 0:
            x_range = 1
        ax.set_xlim(x_min - x_margin * x_range, x_max + x_margin * x_range)

    if y_data is not None and len(y_data) > 0:
        y_min = float(np.nanmin(y_data))
        y_max = float(np.nanmax(y_data))
        y_range = y_max - y_min
        if y_range == 0:
            y_range = max(abs(y_max), 1.0)
        ax.set_ylim(y_min - y_margin * y_range, y_max + y_margin * y_range)

    ax.margins(x=0)
    ax.xaxis.set_major_locator(
        mticker.MaxNLocator(
            nbins=target_x_ticks,
            integer=x_integer,
            steps=[1, 2, 2.5, 5, 10],
            min_n_ticks=4,
        )
    )
    ax.yaxis.set_major_locator(
        mticker.MaxNLocator(
            nbins=target_y_ticks,
            integer=y_integer,
            steps=[1, 2, 2.5, 5, 10],
            min_n_ticks=4,
        )
    )
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator(x_minor_subdivisions))
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(y_minor_subdivisions))
    ax.grid(
        True,
        which="major",
        axis="both",
        color=n["grid"],
        linestyle="--",
        linewidth=0.75,
        alpha=0.80,
    )
    ax.grid(False, which="minor", axis="x")
    ax.grid(
        show_y_minor_grid,
        which="minor",
        axis="y",
        color=n["grid"],
        linestyle="--",
        linewidth=0.50,
        alpha=0.34,
    )
    if config is not None:
        if config["axis"]["xlim"] is not None:
            ax.set_xlim(*config["axis"]["xlim"])
        if config["axis"]["ylim"] is not None:
            ax.set_ylim(*config["axis"]["ylim"])
        if not config["axis"]["grid"]:
            ax.grid(False, which="both")


def normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", key.lower())


def flatten_dict(obj: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in obj.items():
        full_key = f"{prefix}/{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(flatten_dict(value, full_key))
        else:
            flat[full_key] = value
    return flat


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle, delimiter=delimiter)]

    if suffix == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(flatten_dict(item))
        return records

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            for key in ("log_history", "history", "logs", "records", "data"):
                if isinstance(data.get(key), list):
                    return [
                        flatten_dict(row)
                        for row in data[key]
                        if isinstance(row, dict)
                    ]
            return [flatten_dict(data)]
        if isinstance(data, list):
            return [flatten_dict(row) for row in data if isinstance(row, dict)]

    raise ValueError(f"Unsupported or empty input format: {path}")


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


def find_key(records: Iterable[dict[str, Any]], candidates: list[str]) -> str | None:
    available: dict[str, str] = {}
    for record in records:
        for key in record:
            available.setdefault(normalize_key(key), key)

    for candidate in candidates:
        found = available.get(normalize_key(candidate))
        if found is not None:
            return found
    return None


def choose_x_key(records: list[dict[str, Any]], requested: str) -> str | None:
    if requested == "index":
        return None
    if requested != "auto":
        found = find_key(records, [requested])
        if found is None:
            raise ValueError(f"Could not find requested x-axis key: {requested}")
        return found
    found = find_key(records, X_KEYS)
    if found is None:
        raise ValueError("No x-axis key found; provide a column with --x or explicitly use --x index.")
    return found


def build_series(
    records: list[dict[str, Any]],
    y_key: str | None,
    name: str,
    x_key: str | None,
) -> Series | None:
    if y_key is None:
        return None

    xs: list[float] = []
    ys: list[float] = []
    for number, record in enumerate(records, 1):
        y = to_float(record.get(y_key))
        if y_key in record and str(record[y_key]).strip() and not math.isfinite(y):
            raise ValueError(f"Record {number}: invalid {y_key} value.")
        if not math.isfinite(y):
            continue

        if x_key is None:
            x = float(number)
        else:
            x = to_float(record.get(x_key))
            if not math.isfinite(x):
                raise ValueError(f"Record {number}: missing or invalid {x_key} for {y_key}.")

        xs.append(x)
        ys.append(y)

    if not xs:
        return None

    order = np.argsort(xs)
    x_arr = np.asarray(xs, dtype=float)[order]
    y_arr = np.asarray(ys, dtype=float)[order]
    return Series(x=x_arr, y=y_arr, name=name, x_key=x_key or "index", y_key=y_key)


def moving_average(y: np.ndarray, window: int) -> np.ndarray:
    if window <= 1 or len(y) <= 2:
        return y.copy()
    window = min(window, len(y))
    half = window // 2
    smoothed = np.empty_like(y, dtype=float)
    for i in range(len(y)):
        start = max(0, i - half)
        stop = min(len(y), i + half + 1)
        smoothed[i] = float(np.nanmean(y[start:stop]))
    return smoothed


def x_axis_label(x_key: str | None) -> str:
    if x_key is None:
        return "Index"
    normalized = normalize_key(x_key)
    if "epoch" in normalized:
        return "Epoch"
    if "step" in normalized:
        return "Step"
    if normalized in {"iter", "iteration"}:
        return "Iteration"
    return x_key.replace("_", " ").title()


def x_is_integer(x_key: str | None) -> bool:
    if x_key is None:
        return True
    return "epoch" not in normalize_key(x_key)


def plot_loss_series(
    ax: plt.Axes,
    series: Series,
    label: str,
    index: int,
    smooth: int = 1,
    validation: bool = False,
    config: dict[str, Any] | None = None,
) -> None:
    c = COLORS()
    color = c["red"] if validation else c["green"]
    style = config["series"]["val_loss" if validation else "train_loss"] if config else None
    if style:
        color = style["color"]
    y_plot = moving_average(series.y, smooth)

    if smooth > 1 and len(series.y) > 3 and not validation:
        ax.plot(
            series.x,
            series.y,
            color=rgba(color, 0.24),
            linewidth=0.8,
            label=None,
            zorder=1,
        )
        final_label = label
    else:
        final_label = label

    plot_line_with_auto_marker(
        ax,
        series.x,
        y_plot,
        label=final_label,
        index=index,
        color=color,
        marker=style["marker"] if style else None,
        linewidth=style["linewidth"] if style else None,
        target_markers=10 if validation else 9,
        include_endpoints=validation,
        marker_size=style["marker_size"] if style else (5.2 if validation else 5.0),
        marker_edge_width=style["marker_edge_width"] if style else 1.35,
        marker_face_alpha=style["marker_face_alpha"] if style else 0.6,
        marker_edge_alpha=style["marker_edge_alpha"] if style else 0.95,
        line_alpha=style["line_alpha"] if style else 0.92,
        zorder=4 if validation else 3,
    )


def plot_lr_series(ax: plt.Axes, series: Series, label: str = "Learning rate", config: dict[str, Any] | None = None) -> None:
    style = config["series"]["lr"] if config else None
    color = style["color"] if style else COLORS()["blue"]
    plot_line_with_auto_marker(
        ax,
        series.x,
        series.y,
        label=label,
        index=2,
        color=color,
        marker=style["marker"] if style else None,
        linewidth=style["linewidth"] if style else None,
        target_markers=9,
        include_endpoints=False,
        marker_size=style["marker_size"] if style else 4.8,
        marker_edge_width=style["marker_edge_width"] if style else 1.35,
        marker_face_alpha=style["marker_face_alpha"] if style else 0.6,
        marker_edge_alpha=style["marker_edge_alpha"] if style else 0.95,
        line_alpha=style["line_alpha"] if style else 0.92,
    )
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1e"))


def combined_xy(series_list: list[Series | None]) -> tuple[np.ndarray, np.ndarray]:
    xs = [series.x for series in series_list if series is not None]
    ys = [series.y for series in series_list if series is not None]
    return np.concatenate(xs), np.concatenate(ys)


def require_series(series: Series | None, label: str) -> Series:
    if series is None:
        raise ValueError(f"Could not find {label} in the input log.")
    return series


def render_single_axis(
    mode: str,
    train: Series | None,
    val: Series | None,
    lr: Series | None,
    smooth: int,
    title: str | None,
    show_legend: bool,
    spine_width: float = 2.5,
    config: dict[str, Any] | None = None,
) -> plt.Figure:
    set_line_plot_style(spine_width=spine_width, figure_size=tuple(config["figure"]["figsize"]) if config else (7.2, 4.6), config=config)
    fig, ax = plt.subplots()

    active: list[Series | None] = []
    x_key: str | None = None

    if mode == "training-loss":
        train = require_series(train, "training loss")
        plot_loss_series(ax, train, "Training loss", index=0, smooth=smooth, config=config)
        ax.set_ylabel("Training loss")
        active = [train]
        x_key = train.x_key
    elif mode == "validation-loss":
        val = require_series(val, "validation loss")
        plot_loss_series(ax, val, "Validation loss", index=1, validation=True, config=config)
        ax.set_ylabel("Validation loss")
        active = [val]
        x_key = val.x_key
    elif mode == "train-vs-val":
        train = require_series(train, "training loss")
        val = require_series(val, "validation loss")
        plot_loss_series(ax, train, "Training loss", index=0, smooth=smooth, config=config)
        plot_loss_series(ax, val, "Validation loss", index=1, validation=True, config=config)
        ax.set_ylabel("Loss")
        active = [train, val]
        x_key = train.x_key if train.x_key != "index" else val.x_key
    elif mode == "lr-schedule":
        lr = require_series(lr, "learning rate")
        plot_lr_series(ax, lr, config=config)
        ax.set_ylabel("Learning rate")
        active = [lr]
        x_key = lr.x_key
    else:
        raise ValueError(f"Unsupported single-axis mode: {mode}")

    x_data, y_data = combined_xy(active)
    ax.set_xlabel(config["axis"]["xlabel"] if config and config["axis"]["xlabel"] is not None else x_axis_label(x_key))
    apply_smart_ticks(
        ax,
        x_data=x_data,
        y_data=y_data,
        target_x_ticks=9,
        target_y_ticks=7,
        x_integer=config["axis"]["x_integer"] if config and config["axis"]["x_integer"] is not None else x_is_integer(x_key),
        y_integer=False,
        y_margin=0.07,
        config=config,
    )

    if title:
        ax.set_title(title)
    if show_legend:
        ax.legend(loc=config["legend"]["loc"] if config else "best")
    fig.tight_layout()
    return fig


def render_loss_lr_panels(
    train: Series | None,
    val: Series | None,
    lr: Series | None,
    smooth: int,
    title: str | None,
    show_legend: bool,
    spine_width: float = 2.5,
    config: dict[str, Any] | None = None,
) -> plt.Figure:
    lr = require_series(lr, "learning rate")
    if train is None and val is None:
        raise ValueError("Could not find training or validation loss for panel plot.")

    set_line_plot_style(figure_size=tuple(config["figure"]["panel_figsize"]) if config else (7.4, 5.8), spine_width=spine_width, config=config)
    fig, axes = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [2.1, 1]})
    loss_ax, lr_ax = axes

    active_loss: list[Series | None] = []
    x_key = lr.x_key
    if train is not None:
        plot_loss_series(loss_ax, train, "Training loss", index=0, smooth=smooth, config=config)
        active_loss.append(train)
        x_key = train.x_key
    if val is not None:
        plot_loss_series(loss_ax, val, "Validation loss", index=1, validation=True, config=config)
        active_loss.append(val)
        if x_key == "index":
            x_key = val.x_key

    plot_lr_series(lr_ax, lr, config=config)

    loss_x, loss_y = combined_xy(active_loss)
    apply_smart_ticks(
        loss_ax,
        x_data=loss_x,
        y_data=loss_y,
        target_x_ticks=9,
        target_y_ticks=6,
        x_integer=config["axis"]["x_integer"] if config and config["axis"]["x_integer"] is not None else x_is_integer(x_key),
        y_integer=False,
        y_margin=0.07,
        config=config,
    )
    apply_smart_ticks(
        lr_ax,
        x_data=lr.x,
        y_data=lr.y,
        target_x_ticks=9,
        target_y_ticks=4,
        x_integer=config["axis"]["x_integer"] if config and config["axis"]["x_integer"] is not None else x_is_integer(x_key),
        y_integer=False,
        y_margin=0.12,
        config=config,
    )

    loss_ax.set_ylabel("Loss")
    lr_ax.set_ylabel("Learning rate")
    lr_ax.set_xlabel(config["axis"]["xlabel"] if config and config["axis"]["xlabel"] is not None else x_axis_label(x_key))

    if title:
        loss_ax.set_title(title)
    if show_legend:
        loss_ax.legend(loc=config["legend"]["loc"] if config else "best")
        lr_ax.legend(loc=config["legend"]["loc"] if config else "best")
    fig.tight_layout()
    return fig


def choose_auto_mode(train: Series | None, val: Series | None, lr: Series | None) -> str:
    if train is not None and val is not None and lr is not None:
        return "all-separate"
    if train is not None and val is not None:
        return "train-vs-val"
    if train is not None:
        return "training-loss"
    if val is not None:
        return "validation-loss"
    if lr is not None:
        return "lr-schedule"
    raise ValueError("No supported training metrics were found in the input log.")


def save_figure(fig: plt.Figure, output: Path, pdf: bool, config: dict[str, Any] | None = None) -> list[Path]:
    if output.suffix == "":
        output = output.with_suffix(".png")
    output.parent.mkdir(parents=True, exist_ok=True)
    transparent = config["figure"]["transparent"] if config else True
    fig.savefig(output, transparent=transparent)
    saved = [output]
    if pdf:
        pdf_path = output.with_suffix(".pdf")
        fig.savefig(pdf_path, transparent=transparent)
        saved.append(pdf_path)
    return saved


def output_stem(output: Path) -> Path:
    if output.suffix:
        return output.with_suffix("")
    return output


def save_separate_figures(
    train: Series | None,
    val: Series | None,
    lr: Series | None,
    smooth: int,
    output: Path,
    pdf: bool,
    show_legend: bool,
    spine_width: float = 2.5,
    config: dict[str, Any] | None = None,
) -> list[Path]:
    stem = output_stem(output)
    jobs = [
        ("training-loss", "a_train_loss"),
        ("validation-loss", "b_val_loss"),
        ("train-vs-val", "c_train_vs_val_loss"),
        ("lr-schedule", "d_lr_schedule"),
    ]
    saved: list[Path] = []
    for mode, suffix in jobs:
        title = config["plot"]["titles"][mode] if config else None
        fig = render_single_axis(
            mode, train, val, lr, smooth, title, show_legend, spine_width, config
        )
        saved.extend(save_figure(fig, stem.with_name(f"{stem.name}_{suffix}.png"), pdf, config))
        plt.close(fig)
    return saved


def write_bundle(
    output: Path, config: dict[str, Any], records: list[dict[str, Any]],
    x_key: str | None, keys: dict[str, str | None],
) -> list[Path]:
    stem = output_stem(output)
    data_path = stem.with_name(f"{stem.name}_data.csv")
    config_path = stem.with_name(f"{stem.name}_config.json")
    script_path = stem.with_name(f"{stem.name}_plot.py")
    if Path(config["data"]["input"] or "").resolve() != data_path.resolve():
        with data_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["x", "train_loss", "val_loss", "learning_rate"])
            writer.writeheader()
            for number, record in enumerate(records, 1):
                row: dict[str, Any] = {}
                for target, key in keys.items():
                    if key is not None:
                        value = to_float(record.get(key))
                        if math.isfinite(value):
                            row[target] = repr(value)
                if row:
                    x = float(number) if x_key is None else to_float(record.get(x_key))
                    if not math.isfinite(x):
                        raise ValueError(f"Record {number}: missing or invalid {x_key}.")
                    writer.writerow({"x": repr(x), **row})
    config["data"].update(input=data_path.name, x="x", train_loss_key="train_loss",
                          val_loss_key="val_loss", lr_key="learning_rate")
    config["output"]["filename"] = output.name
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    if Path(__file__).resolve() != script_path.resolve():
        shutil.copyfile(__file__, script_path)
    return [data_path, config_path, script_path]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot LLM training loss, validation loss, and learning-rate curves."
    )
    parser.add_argument("input", type=Path, nargs="?", help="CSV, TSV, JSONL, JSON, or trainer_state.json")
    parser.add_argument("--config", type=Path, help="JSON/YAML plotting config; input and output paths resolve relative to it.")
    parser.add_argument(
        "--mode",
        choices=[
            "auto",
            "training-loss",
            "validation-loss",
            "train-vs-val",
            "lr-schedule",
            "all-separate",
            "loss-and-lr-panels",
        ],
        default=None,
        help="Chart type to render. auto renders all-separate when train, val, and LR are present.",
    )
    parser.add_argument(
        "--x",
        default=None,
        help="X-axis key. Use auto, step, global_step, epoch, or an exact log key.",
    )
    parser.add_argument(
        "--smooth",
        type=int,
        default=None,
        help="Centered moving-average window for training loss.",
    )
    parser.add_argument("--title", default=None, help="Optional chart title.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path. For all-separate mode, this is used as the filename prefix.",
    )
    parser.add_argument("--pdf", action="store_true", default=None, help="Also save a companion PDF.")
    parser.add_argument(
        "--spine-width", type=float, default=None,
        help="Thickness in points of the four sides of the axes frame (default: 2.5).",
    )
    parser.add_argument("--no-legend", action="store_true", help="Hide the legend.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = deep_merge(DEFAULT_CONFIG, load_config(args.config))
    data = config["data"]
    plot = config["plot"]
    if args.x is not None:
        data["x"] = args.x
    if args.mode is not None:
        plot["mode"] = args.mode
    if args.smooth is not None:
        plot["smooth"] = args.smooth
    if args.title is not None:
        plot["title"] = args.title
    if args.spine_width is not None:
        config["figure"]["spine_width"] = args.spine_width
    if args.no_legend:
        config["legend"]["enabled"] = False
    if args.pdf is not None:
        config["output"]["pdf"] = args.pdf
    if config["figure"]["spine_width"] <= 0:
        raise ValueError("--spine-width must be positive.")
    if not isinstance(plot["smooth"], int) or plot["smooth"] < 1:
        raise ValueError("Smoothing window must be a positive integer.")
    input_path = args.input or (Path(data["input"]) if data["input"] else None)
    if input_path is None:
        raise ValueError("Provide an input file or set data.input in config.")
    if args.input is None and args.config and not input_path.is_absolute():
        input_path = args.config.parent / input_path
    output = args.output or Path(config["output"]["filename"])
    if args.output is None and args.config and not output.is_absolute():
        output = args.config.parent / output
    if output.suffix == "":
        output = output.with_suffix(".png")
    if data["source"] is None:
        data["source"] = str(input_path.resolve())
    records = load_records(input_path)
    if not records:
        raise ValueError(f"No records found in {input_path}")

    x_key = choose_x_key(records, data["x"])
    if config["axis"]["xlabel"] is None:
        config["axis"]["xlabel"] = x_axis_label(x_key)
    if config["axis"]["x_integer"] is None:
        config["axis"]["x_integer"] = x_is_integer(x_key)
    keys = {
        "train_loss": find_key(records, [data["train_loss_key"]] if data["train_loss_key"] else TRAIN_LOSS_KEYS),
        "val_loss": find_key(records, [data["val_loss_key"]] if data["val_loss_key"] else VAL_LOSS_KEYS),
        "learning_rate": find_key(records, [data["lr_key"]] if data["lr_key"] else LR_KEYS),
    }
    for target, explicit in (("train_loss", "train_loss_key"), ("val_loss", "val_loss_key"), ("learning_rate", "lr_key")):
        if data[explicit] and keys[target] is None:
            raise ValueError(f"Could not find configured metric column: {data[explicit]}")
    if input_path.resolve() == output_stem(output).with_name(f"{output_stem(output).name}_data.csv").resolve() and (
        x_key != "x" or any(key not in (None, target) for target, key in keys.items())
    ):
        raise ValueError("Input conflicts with the chart-ready data path; choose a different --output name.")
    train = build_series(records, keys["train_loss"], "Training loss", x_key)
    val = build_series(records, keys["val_loss"], "Validation loss", x_key)
    lr = build_series(records, keys["learning_rate"], "Learning rate", x_key)

    mode = choose_auto_mode(train, val, lr) if plot["mode"] == "auto" else plot["mode"]
    plot["mode"] = mode
    if mode == "all-separate":
        require_series(train, "training loss")
        require_series(val, "validation loss")
        require_series(lr, "learning rate")
    show_legend = config["legend"]["enabled"]

    if mode == "all-separate":
        saved = save_separate_figures(
            train, val, lr, plot["smooth"], output, config["output"]["pdf"],
            show_legend, config["figure"]["spine_width"], config,
        )
    elif mode == "loss-and-lr-panels":
        fig = render_loss_lr_panels(
            train, val, lr, plot["smooth"], plot["title"], show_legend, config["figure"]["spine_width"], config
        )
        saved = save_figure(fig, output, config["output"]["pdf"], config)
        plt.close(fig)
    else:
        fig = render_single_axis(
            mode, train, val, lr, plot["smooth"], plot["title"], show_legend,
            config["figure"]["spine_width"], config,
        )
        saved = save_figure(fig, output, config["output"]["pdf"], config)
        plt.close(fig)

    config["data"]["input"] = str(input_path.resolve())
    saved.extend(write_bundle(output, config, records, x_key, keys))

    for path in saved:
        print(path)


if __name__ == "__main__":
    main()
