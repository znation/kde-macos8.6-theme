"""Longest horizontal mismatch run diagnostics."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support.fidelity_cli_case import FidelityCliTestCase
from support.png_fixtures import make_png
from tools import fidelity
from tools.fidelity_spatial import _iter_difference_axis_runs, longest_difference_run
from tools.png import Image


class TestLongestDifferenceRun(unittest.TestCase):
    def test_longest_run_respects_row_edges_delta_and_earliest_tie(self):
        width, height = 6, 4
        values = [11, 12, 30, 0, 0, 11, 0, 11, 11, 11, 0, 0, 20, 20, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0]
        rgb = b"".join(bytes((value, 0, 0)) for value in values)
        candidate = Image(width, height, rgb)
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(longest_difference_run(candidate, reference, 10),
                         {"x": 0, "y": 0, "length": 3})
        # Runs are yielded lazily, in row-major order, including a right-edge run.
        runs = _iter_difference_axis_runs(candidate, reference, 10, vertical=False)
        self.assertEqual(next(runs), {"x": 0, "y": 0, "length": 3})
        self.assertEqual(list(runs), [
            {"x": 5, "y": 0, "length": 1},
            {"x": 1, "y": 1, "length": 3},
            {"x": 0, "y": 2, "length": 2},
        ])

    def test_empty_and_tolerance_boundary(self):
        reference = Image(1, 1, bytes(3))
        for candidate, tolerance in ((reference, 0),
                                     (Image(1, 1, bytes((255, 0, 0))), 255)):
            self.assertIsNone(longest_difference_run(candidate, reference, tolerance))

    def test_degenerate_sizes_alpha_and_hidden_rgb(self):
        for width, height, rgb in ((1, 1, bytes((11, 0, 0))),
                                   (1, 3, bytes((11, 0, 0, 0, 0, 0, 0, 0, 0))),
                                   (3, 1, bytes((0, 0, 0, 11, 0, 0, 0, 0, 0)))):
            image = Image(width, height, rgb)
            blank = Image(width, height, bytes(width * height * 3))
            expected = {"x": 0 if width == 1 else 1, "y": 0, "length": 1}
            self.assertEqual(longest_difference_run(image, blank, 10), expected)
            self.assertIsNone(longest_difference_run(image, blank, 255))
        alpha = Image(2, 1, bytes(6), bytes((0, 255)))
        opaque = Image(2, 1, bytes(6))
        self.assertEqual(longest_difference_run(alpha, opaque, 254),
                         {"x": 0, "y": 0, "length": 1})
        hidden = Image(1, 1, bytes((11, 0, 0)), bytes((0,)))
        hidden_reference = Image(1, 1, bytes(3), bytes((0,)))
        self.assertEqual(longest_difference_run(hidden, hidden_reference, 10),
                         {"x": 0, "y": 0, "length": 1})


class TestLongestDifferenceRunCli(FidelityCliTestCase):
    def test_cli_crop_null_text_json_and_composition(self):
        candidate = make_png(4, 2, [bytes((0, 0, 0, 11, 0, 0, 12, 0, 0, 0, 0, 0)), bytes(12)])
        reference = make_png(4, 2, [bytes(12), bytes(12)])
        args = ("--longest-difference-run", "--candidate-crop", "1,0,3,2", "--crop", "0,0,3,2")
        result = self._run_png_pair(candidate, reference, *args, "--json", "--tolerance", "10")
        self.assertEqual(json.loads(result.stdout)["longest_difference_run"],
                         {"x": 0, "y": 0, "length": 2})
        text = self._run_png_pair(candidate, reference, *args, "--tolerance", "10")
        self.assertIn('longest difference run: {"x": 0, "y": 0, "length": 2}', text.stdout)
        empty = self._run_png_pair(reference, reference, "--longest-difference-run", "--json")
        self.assertIsNone(json.loads(empty.stdout)["longest_difference_run"])
        with mock.patch.object(fidelity, "longest_difference_run") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("longest_difference_run", json.loads(ordinary.stdout))
        helper.assert_not_called()
        combined = self._run_png_pair(candidate, reference, "--longest-difference-run",
                                       "--difference-runs", "--json", "--tolerance", "10")
        self.assertEqual(json.loads(combined.stdout)["longest_difference_run"],
                         {"x": 1, "y": 0, "length": 2})
        self.assertEqual(result.returncode,
                         self._run_png_pair(candidate, reference, *args, "--json", "--tolerance", "10").returncode)
        with mock.patch.object(fidelity, "difference_runs", side_effect=AssertionError("materialized")):
            summary_only = self._run_png_pair(candidate, reference, "--longest-difference-run", "--json")
        self.assertIn("longest_difference_run", json.loads(summary_only.stdout))
        tmp = self._tmp_dir()
        a = self._write(tmp, "candidate.png", candidate)
        b = self._write(tmp, "reference.png", reference)
        direct = self._run_script(a, b, "--longest-difference-run", "--json")
        self.assertIn("longest_difference_run", json.loads(direct.stdout))


if __name__ == "__main__":
    unittest.main()
