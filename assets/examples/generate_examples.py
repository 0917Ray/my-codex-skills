#!/usr/bin/env python3
"""Regenerate the README preview PNG/PDF pairs from illustrative data."""

from __future__ import annotations

import csv
import math
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = Path(__file__).resolve().parent
TRAINING_SCRIPT = ROOT / "skills/plot-training-curves/scripts/plot_training_curves.py"
BAR_SCRIPT = ROOT / "skills/plot-bar-charts/scripts/plot_bar_charts.py"


def write_training_log(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["step", "loss", "eval_loss", "learning_rate"]
        )
        writer.writeheader()
        for step in range(100, 8001, 100):
            train = 1.0 + 2.7 * math.exp(-step / 3400)
            train += 0.025 * math.sin(step / 210) + 0.012 * math.cos(step / 75)
            validation = ""
            if step % 400 == 0:
                validation = 1.05 + 2.48 * math.exp(-step / 3650)
                validation += 0.018 * math.sin(step / 340)
            if step <= 800:
                lr = 0.0002 * step / 800
            else:
                lr = 0.0001 * (1 + math.cos(math.pi * (step - 800) / 7200))
            writer.writerow(
                {
                    "step": step,
                    "loss": round(train, 5),
                    "eval_loss": round(validation, 5) if validation != "" else "",
                    "learning_rate": round(lr, 10),
                }
            )


def write_bars(single_path: Path, grouped_path: Path) -> None:
    with single_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["method", "accuracy", "std"])
        writer.writerows(
            [
                ("CNN", 74.8, 0.7),
                ("LSTM", 77.1, 0.6),
                ("Transformer", 79.4, 0.5),
                ("GraphNet", 80.2, 0.6),
                ("Ours", 83.0, 0.4),
            ]
        )

    with grouped_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dataset", "method", "accuracy", "std"])
        for dataset, scores in [
            ("Cora", [(78.7, 0.6), (79.5, 0.7), (82.2, 0.5)]),
            ("Citeseer", [(70.2, 0.7), (71.6, 0.6), (74.4, 0.5)]),
            ("PubMed", [(80.8, 0.5), (81.1, 0.6), (83.5, 0.4)]),
            ("Arxiv", [(68.0, 0.9), (69.2, 0.8), (72.1, 0.6)]),
        ]:
            for name, (score, std) in zip(
                ["Baseline A", "Baseline B", "Ours"], scores
            ):
                writer.writerow([dataset, name, score, std])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="codex-plot-examples-") as scratch:
        directory = Path(scratch)
        training = directory / "training.csv"
        single = directory / "single.csv"
        grouped = directory / "grouped.csv"
        write_training_log(training)
        write_bars(single, grouped)

        commands = [
            [
                sys.executable,
                str(TRAINING_SCRIPT),
                str(training),
                "--mode",
                "all-separate",
                "--smooth",
                "7",
                "--output",
                str(EXAMPLES / "sample_llm_training_curves.png"),
                "--pdf",
            ],
            [
                sys.executable,
                str(BAR_SCRIPT),
                str(single),
                "--mode",
                "single",
                "--label-column",
                "method",
                "--value-column",
                "accuracy",
                "--error-column",
                "std",
                "--highlight-label",
                "Ours",
                "--title",
                "(a) Single Bar Comparison",
                "--xlabel",
                "Method",
                "--ylabel",
                "Accuracy (%)",
                "--output",
                str(EXAMPLES / "sample_bar_single.png"),
                "--pdf",
            ],
            [
                sys.executable,
                str(BAR_SCRIPT),
                str(grouped),
                "--mode",
                "grouped",
                "--group-column",
                "dataset",
                "--series-column",
                "method",
                "--value-column",
                "accuracy",
                "--error-column",
                "std",
                "--title",
                "(b) Grouped Bar Comparison",
                "--xlabel",
                "Dataset",
                "--ylabel",
                "Accuracy (%)",
                "--output",
                str(EXAMPLES / "sample_bar_grouped.png"),
                "--pdf",
            ],
        ]
        for command in commands:
            subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
