"""Behavioral checks for portable, data-preserving figure bundles."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BAR = ROOT / "skills/plot-bar-charts/scripts/plot_bar_charts.py"
TRAINING = ROOT / "skills/plot-training-curves/scripts/plot_training_curves.py"


class PlotBundleTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name)

    def run_plot(self, script, *args, success=True, cwd=None):
        result = subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            cwd=cwd or self.directory, text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def write_csv(self, name, fields, rows):
        path = self.directory / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            writer.writerows(rows)
        return path

    def redraw_without_source(self, stem, change):
        data = self.directory / f"{stem}_data.csv"
        config_path = self.directory / f"{stem}_config.json"
        script = self.directory / f"{stem}_plot.py"
        self.assertTrue(data.exists() and config_path.exists() and script.exists())
        before = data.read_bytes()
        mtime = data.stat().st_mtime_ns
        image = self.directory / (f"{stem}.png" if (self.directory / f"{stem}.png").exists() else f"{stem}_a_train_loss.png")
        image_before = image.read_bytes()
        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertTrue(Path(config["data"]["source"]).is_absolute())
        change(config)
        config_path.write_text(json.dumps(config), encoding="utf-8")
        self.run_plot(script, "--config", config_path, cwd=ROOT)
        self.assertEqual(data.read_bytes(), before)
        self.assertEqual(data.stat().st_mtime_ns, mtime)
        self.assertNotEqual(image.read_bytes(), image_before)

    def test_single_bar_replots_without_analysis(self):
        source = self.write_csv("source.csv", ["method", "score", "std"],
                                [["Base", "0.7100000000001", 0.02], ["Ours", 0.83, 0.01]])
        output = self.directory / "single.png"
        self.run_plot(BAR, source, "--mode", "single", "--label-column", "method",
                      "--value-column", "score", "--error-column", "std", "--output", output)
        source.unlink()
        self.redraw_without_source("single", lambda config: config["bars"].update(bar_width=0.42))
        self.assertTrue(output.exists())
        self.assertIn("0.7100000000001", (self.directory / "single_data.csv").read_text())

    def test_grouped_bar_replots_without_analysis(self):
        source = self.write_csv("source.csv", ["dataset", "method", "score"],
                                [["A", "Base", 0.5], ["A", "Ours", 0.7],
                                 ["B", "Base", 0.6], ["B", "Ours", 0.8]])
        self.run_plot(BAR, source, "--mode", "grouped", "--group-column", "dataset",
                      "--series-column", "method", "--value-column", "score",
                      "--output", self.directory / "grouped.png")
        source.unlink()
        self.redraw_without_source("grouped", lambda config: config["figure"].update(grouped_figsize=[8, 5]))

    def test_training_multiple_and_single_replot(self):
        source = self.write_csv("source.csv", ["step", "loss", "eval_loss", "learning_rate"],
                                [[1, 1.9, "", 0.001], [2, 1.7, 1.8, 0.0008],
                                 [3, 1.5, "", 0.0005], [4, 1.3, 1.4, 0.0002]])
        self.run_plot(TRAINING, source, "--mode", "all-separate", "--output", self.directory / "curves.png")
        source.unlink()
        self.redraw_without_source("curves", lambda config: config["plot"].update(smooth=3))
        self.assertTrue((self.directory / "curves_d_lr_schedule.png").exists())
        config_path = self.directory / "curves_config.json"
        config = json.loads(config_path.read_text())
        config["plot"]["mode"] = "validation-loss"
        config_path.write_text(json.dumps(config))
        self.run_plot(self.directory / "curves_plot.py", "--config", config_path,
                      "--output", self.directory / "validation.png")
        self.assertTrue((self.directory / "validation.png").exists())
        self.assertEqual(config["axis"]["xlabel"], "Step")

    def test_bar_rejects_duplicates_missing_pairs_and_invalid_errors(self):
        cases = [
            ([["A", "X", 1], ["A", "X", 2]], "duplicate"),
            ([["A", "X", 1], ["A", "Y", 2], ["B", "X", 3]], "Missing"),
        ]
        for rows, message in cases:
            with self.subTest(message=message):
                source = self.write_csv("bad.csv", ["group", "series", "value"], rows)
                result = self.run_plot(BAR, source, "--mode", "grouped", "--group-column", "group",
                                       "--series-column", "series", "--value-column", "value", success=False)
                self.assertIn(message, result.stderr)
        source = self.write_csv("bad_error.csv", ["label", "value", "error"], [["A", 2, -1]])
        result = self.run_plot(BAR, source, "--mode", "single", "--label-column", "label",
                               "--value-column", "value", "--error-column", "error", success=False)
        self.assertIn("invalid nonnegative", result.stderr)

    def test_training_rejects_missing_x_and_required_series(self):
        source = self.write_csv("missing_x.csv", ["step", "loss", "eval_loss"], [[1, 1.1, ""], ["", 0.9, ""]])
        result = self.run_plot(TRAINING, source, "--mode", "training-loss", success=False)
        self.assertIn("missing or invalid step", result.stderr)
        source = self.write_csv("no_val.csv", ["step", "loss", "learning_rate"], [[1, 1.1, 0.001]])
        result = self.run_plot(TRAINING, source, "--mode", "all-separate", success=False)
        self.assertIn("validation loss", result.stderr)

    def test_bundle_name_cannot_overwrite_raw_input(self):
        source = self.write_csv("figure_data.csv", ["method", "score"], [["A", 0.5]])
        original = source.read_bytes()
        result = self.run_plot(BAR, source, "--mode", "single", "--label-column", "method",
                               "--value-column", "score", "--output", self.directory / "figure.png",
                               success=False)
        self.assertIn("conflicts", result.stderr)
        self.assertEqual(source.read_bytes(), original)
        source = self.write_csv("curve_data.csv", ["step", "loss"], [[1, 0.5]])
        original = source.read_bytes()
        result = self.run_plot(TRAINING, source, "--mode", "training-loss",
                               "--output", self.directory / "curve.png", success=False)
        self.assertIn("conflicts", result.stderr)
        self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
