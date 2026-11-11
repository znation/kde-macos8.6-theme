"""Disjoint horizontal mismatch runs for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import (  # noqa: E402
    FidelityCliTestCase,
    patched_horizontal_calls,
)
from support.png_fixtures import make_png  # noqa: E402
from tools.fidelity_spatial import difference_runs  # noqa: E402
from tools.fidelity_spatial import difference_column_runs  # noqa: E402
from tools.fidelity_metrics import compare  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRuns(unittest.TestCase):
    """Test maximal horizontal difference runs and their ordering."""
    def test_both_axes_match_literal_intervals_on_nonsquare_image(self):
        width, height = 5, 4
        rgb = bytearray(width * height * 3)
        for x, y, value in ((0, 0, 11), (1, 0, 12), (4, 0, 30),
                            (0, 2, 20), (4, 2, 11), (4, 3, 11)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        horizontal = [
            {"x": 0, "y": 0, "length": 2}, {"x": 4, "y": 0, "length": 1},
            {"x": 0, "y": 2, "length": 1}, {"x": 4, "y": 2, "length": 1},
            {"x": 4, "y": 3, "length": 1},
        ]
        vertical = [
            {"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 1},
            {"x": 1, "y": 0, "length": 1},
            {"x": 4, "y": 0, "length": 1}, {"x": 4, "y": 2, "length": 2},
        ]
        self.assertEqual(difference_runs(candidate, reference, 10), horizontal)
        self.assertEqual(difference_column_runs(candidate, reference, 10), vertical)
        differing = compare(candidate, reference, tolerance=10).differing
        self.assertEqual(sum(run["length"] for run in horizontal), differing)
        self.assertEqual(sum(run["length"] for run in vertical), differing)

    def test_degenerate_dimensions_and_tolerance_boundaries(self):
        for width, height, rgb, alpha, expected_h, expected_v in (
            (1, 1, bytes([11, 0, 0]), None,
             [{"x": 0, "y": 0, "length": 1}], [{"x": 0, "y": 0, "length": 1}]),
            (1, 3, bytes([11, 0, 0, 10, 0, 0, 0, 0, 0]), None,
             [{"x": 0, "y": 0, "length": 1}], [{"x": 0, "y": 0, "length": 1}]),
            (3, 1, bytes([0, 0, 0, 11, 0, 0, 10, 0, 0]), None,
             [{"x": 1, "y": 0, "length": 1}], [{"x": 1, "y": 0, "length": 1}]),
        ):
            candidate = Image(width, height, rgb, alpha)
            reference = Image(width, height, bytes(width * height * 3))
            self.assertEqual(difference_runs(candidate, reference, 10), expected_h)
            self.assertEqual(difference_column_runs(candidate, reference, 10), expected_v)
            self.assertEqual(difference_runs(candidate, reference, 255), [])
            self.assertEqual(difference_column_runs(candidate, reference, 255), [])

    def test_alpha_missing_alpha_and_hidden_rgb(self):
        candidate = Image(2, 2, bytes([0, 0, 0] * 4), bytes([255, 0, 255, 255]))
        opaque = Image(2, 2, bytes([0, 0, 0] * 4))
        expected_h = [{"x": 1, "y": 0, "length": 1}]
        expected_v = [{"x": 1, "y": 0, "length": 1}]
        self.assertEqual(difference_runs(candidate, opaque, 254), expected_h)
        self.assertEqual(difference_column_runs(candidate, opaque, 254), expected_v)
        hidden = Image(1, 1, bytes([11, 0, 0]), bytes([0]))
        hidden_reference = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_runs(hidden, hidden_reference, 10),
                         [{"x": 0, "y": 0, "length": 1}])
        self.assertEqual(difference_column_runs(hidden, hidden_reference, 10),
                         [{"x": 0, "y": 0, "length": 1}])

    def test_runs_split_at_gaps_and_row_boundaries(self):
        width, height = 5, 2
        rgb = bytearray(width * height * 3)
        for x, y, value in ((0, 0, 11), (1, 0, 12), (3, 0, 30), (4, 1, 11)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        runs = difference_runs(candidate, reference, 10)
        self.assertEqual(runs,
                         [{"x": 0, "y": 0, "length": 2},
                          {"x": 3, "y": 0, "length": 1},
                          {"x": 4, "y": 1, "length": 1}])
        self.assertEqual(difference_runs(candidate, reference, 255), [])
        # Each compared pixel belongs to exactly one run.
        self.assertEqual(sum(run["length"] for run in runs),
                         compare(candidate, reference, 10).differing)

    def test_raw_alpha_and_hidden_rgb(self):
        candidate = Image(2, 1, bytes([20, 0, 0, 0, 0, 0]), bytes([255, 0]))
        reference = Image(2, 1, bytes(6), bytes([255, 255]))
        self.assertEqual(difference_runs(candidate, reference, 254),
                         [{"x": 1, "y": 0, "length": 1}])
        # Stored RGB beneath fully transparent pixels still participates:
        # the only difference is hidden RGB, and it is raw bytes, never
        # composited away.
        hidden = Image(1, 1, bytes([250, 0, 0]), bytes([0]))
        transparent = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_runs(hidden, transparent, 200),
                         [{"x": 0, "y": 0, "length": 1}])
        self.assertEqual(difference_runs(hidden, transparent, 250), [])


class TestDifferenceRunsCli(FidelityCliTestCase):
    """Test horizontal run reports, crops, and CLI read errors."""
    def test_opt_in_crops_text_json_and_direct_script(self):
        candidate = make_png(4, 2, [bytes([0, 0, 0, 20, 0, 0, 0, 0, 0, 30, 0, 0]), bytes(12)])
        reference = make_png(4, 2, [bytes(12), bytes(12)])
        args = ("--difference-runs", "--candidate-crop", "1,0,3,2", "--crop", "0,0,3,2")
        result = self._run_png_pair(candidate, reference, *args, "--json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["difference_runs"],
                         [{"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 1}])
        text = self._run_png_pair(candidate, reference, *args)
        self.assertIn('difference runs: [{"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 1}]', text.stdout)
        with patched_horizontal_calls(runs=mock.Mock()) as patched:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_runs", json.loads(ordinary.stdout))
        patched.runs.assert_not_called()
        tmp = self._tmp_dir()
        a = self._write(tmp, "a.png", candidate)
        b = self._write(tmp, "b.png", reference)
        direct = self._run_script(a, b, "--difference-runs", "--json")
        self.assertIn("difference_runs", json.loads(direct.stdout))


if __name__ == "__main__":
    unittest.main()
