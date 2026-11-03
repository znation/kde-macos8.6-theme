"""Longest vertical mismatch run diagnostics."""

import json
import unittest
from unittest import mock

from support.fidelity_cli_case import FidelityCliTestCase
from support.png_fixtures import make_png
from tools import fidelity
from tools.fidelity_spatial import longest_difference_column_run
from tools.png import Image


class TestLongestDifferenceColumnRun(unittest.TestCase):
    def test_longest_vertical_run_and_earliest_column_tie(self):
        width, height = 4, 5
        values = [0, 11, 0, 0, 0, 11, 0, 11, 0, 12, 0, 11, 0, 11, 0, 0, 0, 0, 0, 11]
        candidate = Image(width, height, b"".join(bytes((v, 0, 0)) for v in values))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(longest_difference_column_run(candidate, reference, 10),
                         {"x": 1, "y": 0, "length": 4})

    def test_empty_and_alpha_comparison(self):
        blank = Image(1, 2, bytes(6))
        self.assertIsNone(longest_difference_column_run(blank, blank, 0))
        alpha = Image(1, 2, bytes(6), bytes((0, 255)))
        opaque = Image(1, 2, bytes(6))
        self.assertEqual(longest_difference_column_run(alpha, opaque, 254),
                         {"x": 0, "y": 0, "length": 1})


class TestLongestDifferenceColumnRunCli(FidelityCliTestCase):
    def test_crop_null_text_json_and_shared_column_runs(self):
        candidate = make_png(4, 3, [bytes(12), bytes((0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0)), bytes((0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0))])
        reference = make_png(4, 3, [bytes(12), bytes(12), bytes(12)])
        flags = ("--longest-difference-column-run", "--candidate-crop", "1,0,3,3",
                 "--crop", "0,0,3,3", "--tolerance", "10")
        report = self._run_png_pair(candidate, reference, *flags, "--json")
        self.assertEqual(json.loads(report.stdout)["longest_difference_column_run"],
                         {"x": 0, "y": 1, "length": 2})
        text = self._run_png_pair(candidate, reference, *flags)
        self.assertIn('longest difference column run: {"x": 0, "y": 1, "length": 2}', text.stdout)
        empty = self._run_png_pair(reference, reference, "--longest-difference-column-run", "--json")
        self.assertIsNone(json.loads(empty.stdout)["longest_difference_column_run"])
        with mock.patch.object(fidelity, "longest_difference_column_run") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("longest_difference_column_run", json.loads(ordinary.stdout))
        helper.assert_not_called()
        with mock.patch.object(fidelity, "difference_column_runs", side_effect=AssertionError("materialized")):
            self._run_png_pair(candidate, reference, "--longest-difference-column-run", "--json")
        combined = self._run_png_pair(candidate, reference, "--longest-difference-column-run",
                                       "--difference-column-runs", "--json", "--tolerance", "10")
        self.assertEqual(json.loads(combined.stdout)["longest_difference_column_run"],
                         {"x": 1, "y": 1, "length": 2})


if __name__ == "__main__":
    unittest.main()
