#!/usr/bin/env python3
"""Plot LLM training loss, validation loss, and learning-rate curves."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
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


@dataclass
class Series:
    x: np.ndarray
    y: np.ndarray
    name: str
    x_key: str
    y_key: str


def colors() -> dict[str, str]:
    return {
        "blue": "#516480",
        "green": "#4F7C65",
        "red": "#A75B73",
        "purple": "#75668A",
        "orange": "#C48755",
        "cyan": "#5C8FA3",
        "olive": "#7F8956",
        "brown": "#8A6A58",
    }


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
    line_width: float = 1.65,
    figure_size: tuple[float, float] = (7.2, 4.6),
) -> None:
    c = colors()
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
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "savefig.edgecolor": "none",
            "savefig.transparent": True,
            "savefig.dpi": 300,
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
            "lines.markeredgewidth": 1.0,
            "lines.solid_capstyle": "round",
            "lines.solid_joinstyle": "round",
            "lines.antialiased": True,
            "axes.linewidth": 1.05,
            "axes.edgecolor": n["axis"],
            "axes.labelcolor": n["dark"],
            "axes.titlecolor": n["dark"],
            "axes.labelsize": label_size,
            "axes.titlesize": title_size,
            "axes.titleweight": "regular",
            "axes.axisbelow": True,
            "axes.spines.top": True,
            "axes.spines.right": True,
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
            "xtick.major.width": 1.0,
            "ytick.major.width": 1.0,
            "xtick.minor.size": 2.2,
            "ytick.minor.size": 2.2,
            "xtick.minor.width": 0.75,
            "ytick.minor.width": 0.75,
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
    c = colors()
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
    marker_edge_width: float = 1.2,
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
) -> None:
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
    if requested != "auto":
        found = find_key(records, [requested])
        if found is None:
            raise ValueError(f"Could not find requested x-axis key: {requested}")
        return found
    return find_key(records, X_KEYS)


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
    for record in records:
        y = to_float(record.get(y_key))
        if not math.isfinite(y):
            continue

        if x_key is None:
            x = float(len(xs) + 1)
        else:
            x = to_float(record.get(x_key))
            if not math.isfinite(x):
                x = float(len(xs) + 1)

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
) -> None:
    c = colors()
    color = c["red"] if validation else c["green"]
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
        target_markers=10 if validation else 9,
        include_endpoints=validation,
        marker_size=5.2 if validation else 5.0,
        marker_edge_width=1.2,
        marker_face_alpha=0.6,
        marker_edge_alpha=0.95,
        line_alpha=0.92,
        zorder=4 if validation else 3,
    )


def plot_lr_series(ax: plt.Axes, series: Series, label: str = "Learning rate") -> None:
    color = colors()["blue"]
    plot_line_with_auto_marker(
        ax,
        series.x,
        series.y,
        label=label,
        index=2,
        color=color,
        target_markers=9,
        include_endpoints=False,
        marker_size=4.8,
        marker_edge_width=1.2,
        marker_face_alpha=0.6,
        marker_edge_alpha=0.95,
        line_alpha=0.92,
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
) -> plt.Figure:
    set_line_plot_style()
    fig, ax = plt.subplots()

    active: list[Series | None] = []
    x_key: str | None = None

    if mode == "training-loss":
        train = require_series(train, "training loss")
        plot_loss_series(ax, train, "Training loss", index=0, smooth=smooth)
        ax.set_ylabel("Training loss")
        active = [train]
        x_key = train.x_key
    elif mode == "validation-loss":
        val = require_series(val, "validation loss")
        plot_loss_series(ax, val, "Validation loss", index=1, validation=True)
        ax.set_ylabel("Validation loss")
        active = [val]
        x_key = val.x_key
    elif mode == "train-vs-val":
        train = require_series(train, "training loss")
        val = require_series(val, "validation loss")
        plot_loss_series(ax, train, "Training loss", index=0, smooth=smooth)
        plot_loss_series(ax, val, "Validation loss", index=1, validation=True)
        ax.set_ylabel("Loss")
        active = [train, val]
        x_key = train.x_key if train.x_key != "index" else val.x_key
    elif mode == "lr-schedule":
        lr = require_series(lr, "learning rate")
        plot_lr_series(ax, lr)
        ax.set_ylabel("Learning rate")
        active = [lr]
        x_key = lr.x_key
    else:
        raise ValueError(f"Unsupported single-axis mode: {mode}")

    x_data, y_data = combined_xy(active)
    ax.set_xlabel(x_axis_label(x_key))
    apply_smart_ticks(
        ax,
        x_data=x_data,
        y_data=y_data,
        target_x_ticks=9,
        target_y_ticks=7,
        x_integer=x_is_integer(x_key),
        y_integer=False,
        y_margin=0.07,
    )

    if title:
        ax.set_title(title)
    if show_legend:
        ax.legend(loc="best")
    fig.tight_layout()
    return fig


def render_loss_lr_panels(
    train: Series | None,
    val: Series | None,
    lr: Series | None,
    smooth: int,
    title: str | None,
    show_legend: bool,
) -> plt.Figure:
    lr = require_series(lr, "learning rate")
    if train is None and val is None:
        raise ValueError("Could not find training or validation loss for panel plot.")

    set_line_plot_style(figure_size=(7.4, 5.8))
    fig, axes = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [2.1, 1]})
    loss_ax, lr_ax = axes

    active_loss: list[Series | None] = []
    x_key = lr.x_key
    if train is not None:
        plot_loss_series(loss_ax, train, "Training loss", index=0, smooth=smooth)
        active_loss.append(train)
        x_key = train.x_key
    if val is not None:
        plot_loss_series(loss_ax, val, "Validation loss", index=1, validation=True)
        active_loss.append(val)
        if x_key == "index":
            x_key = val.x_key

    plot_lr_series(lr_ax, lr)

    loss_x, loss_y = combined_xy(active_loss)
    apply_smart_ticks(
        loss_ax,
        x_data=loss_x,
        y_data=loss_y,
        target_x_ticks=9,
        target_y_ticks=6,
        x_integer=x_is_integer(x_key),
        y_integer=False,
        y_margin=0.07,
    )
    apply_smart_ticks(
        lr_ax,
        x_data=lr.x,
        y_data=lr.y,
        target_x_ticks=9,
        target_y_ticks=4,
        x_integer=x_is_integer(x_key),
        y_integer=False,
        y_margin=0.12,
    )

    loss_ax.set_ylabel("Loss")
    lr_ax.set_ylabel("Learning rate")
    lr_ax.set_xlabel(x_axis_label(x_key))

    if title:
        loss_ax.set_title(title)
    if show_legend:
        loss_ax.legend(loc="best")
        lr_ax.legend(loc="best")
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


def save_figure(fig: plt.Figure, output: Path, pdf: bool) -> list[Path]:
    if output.suffix == "":
        output = output.with_suffix(".png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, transparent=True)
    saved = [output]
    if pdf:
        pdf_path = output.with_suffix(".pdf")
        fig.savefig(pdf_path, transparent=True)
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
) -> list[Path]:
    stem = output_stem(output)
    jobs = [
        ("training-loss", "a_train_loss", "(a) Training Loss"),
        ("validation-loss", "b_val_loss", "(b) Validation Loss"),
        ("train-vs-val", "c_train_vs_val_loss", "(c) Training vs. Validation Loss"),
        ("lr-schedule", "d_lr_schedule", "(d) Learning Rate Schedule"),
    ]
    saved: list[Path] = []
    for mode, suffix, title in jobs:
        fig = render_single_axis(mode, train, val, lr, smooth, title, show_legend)
        saved.extend(save_figure(fig, stem.with_name(f"{stem.name}_{suffix}.png"), pdf))
        plt.close(fig)
    return saved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot LLM training loss, validation loss, and learning-rate curves."
    )
    parser.add_argument("input", type=Path, help="CSV, TSV, JSONL, JSON, or trainer_state.json")
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
        default="auto",
        help="Chart type to render. auto renders all-separate when train, val, and LR are present.",
    )
    parser.add_argument(
        "--x",
        default="auto",
        help="X-axis key. Use auto, step, global_step, epoch, or an exact log key.",
    )
    parser.add_argument(
        "--smooth",
        type=int,
        default=1,
        help="Centered moving-average window for training loss.",
    )
    parser.add_argument("--title", default=None, help="Optional chart title.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("training_curves.png"),
        help="Output file path. For all-separate mode, this is used as the filename prefix.",
    )
    parser.add_argument("--pdf", action="store_true", help="Also save a companion PDF.")
    parser.add_argument("--no-legend", action="store_true", help="Hide the legend.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.input)
    if not records:
        raise ValueError(f"No records found in {args.input}")

    x_key = choose_x_key(records, args.x)
    train = build_series(records, find_key(records, TRAIN_LOSS_KEYS), "Training loss", x_key)
    val = build_series(records, find_key(records, VAL_LOSS_KEYS), "Validation loss", x_key)
    lr = build_series(records, find_key(records, LR_KEYS), "Learning rate", x_key)

    mode = choose_auto_mode(train, val, lr) if args.mode == "auto" else args.mode
    show_legend = not args.no_legend

    if mode == "all-separate":
        saved = save_separate_figures(
            train, val, lr, args.smooth, args.output, args.pdf, show_legend
        )
    elif mode == "loss-and-lr-panels":
        fig = render_loss_lr_panels(train, val, lr, args.smooth, args.title, show_legend)
        saved = save_figure(fig, args.output, args.pdf)
    else:
        fig = render_single_axis(mode, train, val, lr, args.smooth, args.title, show_legend)
        saved = save_figure(fig, args.output, args.pdf)

    for path in saved:
        print(path)


if __name__ == "__main__":
    main()
