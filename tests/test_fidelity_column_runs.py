"""Disjoint vertical mismatch runs for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_pixels import difference_column_runs  # noqa: E402
from tools.fidelity_metrics import compare  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceColumnRuns(unittest.TestCase):
    def test_column_major_runs_split_at_gaps_and_columns(self):
        width, height = 4, 5
        rgb = bytearray(width * height * 3)
        for x, y, value in ((0, 0, 11), (0, 1, 12), (0, 3, 30),
                            (1, 4, 11), (3, 1, 11), (3, 4, 11)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        records = difference_column_runs(candidate, reference, 10)
        self.assertEqual(records, [
            {"x": 0, "y": 0, "length": 2},
            {"x": 0, "y": 3, "length": 1},
            {"x": 1, "y": 4, "length": 1},
            {"x": 3, "y": 1, "length": 1},
            {"x": 3, "y": 4, "length": 1},
        ])
        self.assertEqual(sum(run["length"] for run in records), 6)
        self.assertEqual(sum(run["length"] for run in records),
                         compare(candidate, reference, tolerance=10).differing)
        self.assertEqual(difference_column_runs(candidate, reference, 255), [])

    def test_alpha_missing_alpha_and_hidden_rgb(self):
        candidate = Image(2, 3, bytes(18), bytes([255, 0, 255, 255, 255, 255]))
        reference = Image(2, 3, bytes(18), bytes([255, 255, 255, 255, 255, 255]))
        self.assertEqual(difference_column_runs(candidate, reference, 254),
                         [{"x": 1, "y": 0, "length": 1}])
        hidden = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        opaque_rgb = Image(1, 1, bytes(3))
        self.assertEqual(difference_column_runs(hidden, opaque_rgb, 0),
                         [{"x": 0, "y": 0, "length": 1}])
        hidden_reference = Image(1, 1, bytes([0, 0, 0]), bytes([0]))
        self.assertEqual(difference_column_runs(hidden, hidden_reference, 0),
                         [{"x": 0, "y": 0, "length": 1}])
        missing_alpha = Image(1, 1, bytes(3))
        transparent = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_column_runs(missing_alpha, transparent, 254),
                         [{"x": 0, "y": 0, "length": 1}])
        self.assertEqual(difference_column_runs(opaque_rgb, opaque_rgb, 0), [])


class TestDifferenceColumnRunsCli(FidelityCliTestCase):
    def test_crops_json_text_composition_and_direct_script(self):
        candidate = make_png(4, 3, [bytes(12), bytes([0, 0, 0, 20, 0, 0, 0, 0, 0, 30, 0, 0]), bytes(12)])
        reference = make_png(4, 3, [bytes(12), bytes(12), bytes(12)])
        args = ("--difference-column-runs", "--difference-runs",
                "--difference-column-bounds", "--candidate-crop", "1,0,3,3",
                "--crop", "0,0,3,3", "--max-frac", "1")
        result = self._run_png_pair(candidate, reference, *args, "--json")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["difference_column_runs"],
                         [{"x": 0, "y": 1, "length": 1}, {"x": 2, "y": 1, "length": 1}])
        self.assertEqual(data["difference_runs"],
                         [{"x": 0, "y": 1, "length": 1}, {"x": 2, "y": 1, "length": 1}])
        failing = self._run_png_pair(candidate, reference,
                                     "--difference-column-runs", "--json")
        self.assertEqual(failing.returncode, 1)
        self.assertFalse(json.loads(failing.stdout)["passed"])
        text = self._run_png_pair(candidate, reference, *args)
        self.assertIn('difference column runs: [{"x": 0, "y": 1, "length": 1}, {"x": 2, "y": 1, "length": 1}]', text.stdout)
        with mock.patch.object(fidelity, "difference_column_runs") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_column_runs", json.loads(ordinary.stdout))
        helper.assert_not_called()
        tmp = self._tmp_dir()
        a = self._write(tmp, "a.png", candidate)
        b = self._write(tmp, "b.png", reference)
        direct = self._run_script(a, b, "--difference-column-runs", "--json")
        self.assertIn("difference_column_runs", json.loads(direct.stdout))

    def test_read_and_unequal_size_errors_have_no_stdout(self):
        candidate = make_png(2, 1, [bytes(6)])
        reference = make_png(1, 1, [bytes(3)])
        result = self._run_png_pair(candidate, reference, "--difference-column-runs")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
