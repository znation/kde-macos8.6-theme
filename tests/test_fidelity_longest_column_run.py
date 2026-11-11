"""Longest vertical mismatch run diagnostics."""

import json
import unittest
from unittest import mock

from support.fidelity_cli_case import (
    FidelityCliTestCase,
    patched_column_calls,
)
from support.png_fixtures import make_png
from tools.fidelity_spatial import longest_difference_column_run
from tools.png import Image


class TestLongestDifferenceColumnRun(unittest.TestCase):
    def test_longest_vertical_run(self):
        width, height = 4, 5
        values = [0, 11, 0, 0, 0, 11, 0, 11, 0, 12, 0, 11, 0, 11, 0, 0, 0, 0, 0, 11]
        candidate = Image(width, height, b"".join(bytes((v, 0, 0)) for v in values))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(longest_difference_column_run(candidate, reference, 10),
                         {"x": 1, "y": 0, "length": 4})

    def test_tied_column_runs_keep_first_scanline(self):
        values = [11, 0, 11, 0, 11, 0, 11, 0]
        candidate = Image(2, 4, b"".join(bytes((v, 0, 0)) for v in values))
        reference = Image(2, 4, bytes(2 * 4 * 3))
        self.assertEqual(longest_difference_column_run(candidate, reference, 10),
                         {"x": 0, "y": 0, "length": 4})

    def test_earliest_column_and_row_ties(self):
        # Two columns hold length-2 runs (x=0 at y=0, x=2 at y=2); the
        # earlier column wins. Within that column the run also starts
        # at the earlier row.
        width, height = 3, 5
        values = [11, 0, 11, 11, 0, 0, 0, 0, 11, 11, 0, 11, 0, 0, 0]
        candidate = Image(width, height, b"".join(bytes((v, 0, 0)) for v in values))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(longest_difference_column_run(candidate, reference, 10),
                         {"x": 0, "y": 0, "length": 2})
        # One column with two equal-length runs keeps the earlier row.
        single = Image(1, 4, bytes((11, 0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 0)))
        self.assertEqual(longest_difference_column_run(single, Image(1, 4, bytes(12)), 10),
                         {"x": 0, "y": 0, "length": 1})

    def test_empty_and_alpha_comparison(self):
        blank = Image(1, 2, bytes(6))
        self.assertIsNone(longest_difference_column_run(blank, blank, 0))
        alpha = Image(1, 2, bytes(6), bytes((0, 255)))
        opaque = Image(1, 2, bytes(6))
        self.assertEqual(longest_difference_column_run(alpha, opaque, 254),
                         {"x": 0, "y": 0, "length": 1})


class TestLongestDifferenceColumnRunCli(FidelityCliTestCase):
    def test_ties_match_between_summary_and_combined_json(self):
        candidate = make_png(2, 5, [
            bytes((0, 0, 0, 11, 0, 0)),
            bytes((11, 0, 0, 11, 0, 0)),
            bytes((11, 0, 0, 11, 0, 0)),
            bytes((11, 0, 0, 0, 0, 0)),
            bytes(6),
        ])
        reference = make_png(2, 5, [bytes(6) for _ in range(5)])
        for extra in ((), ("--difference-column-runs",)):
            result = self._run_png_pair(candidate, reference,
                                        "--longest-difference-column-run",
                                        "--tolerance", "10", "--json", *extra)
            self.assertEqual(json.loads(result.stdout)["longest_difference_column_run"],
                             {"x": 0, "y": 1, "length": 3})

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
        with patched_column_calls(longest_run=mock.Mock()) as patched:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("longest_difference_column_run", json.loads(ordinary.stdout))
        patched.longest_run.assert_not_called()
        with patched_column_calls(
                runs=mock.Mock(side_effect=AssertionError("materialized"))):
            self._run_png_pair(candidate, reference, "--longest-difference-column-run", "--json")
        combined = self._run_png_pair(candidate, reference, "--longest-difference-column-run",
                                       "--difference-column-runs", "--json", "--tolerance", "10")
        self.assertEqual(json.loads(combined.stdout)["longest_difference_column_run"],
                         {"x": 1, "y": 1, "length": 2})
        with patched_column_calls(
                longest_run=mock.Mock(side_effect=AssertionError("rescanned image"))):
            combined = self._run_png_pair(candidate, reference,
                                           "--longest-difference-column-run",
                                           "--difference-column-runs", "--json", "--tolerance", "10")
        self.assertEqual(json.loads(combined.stdout)["longest_difference_column_run"],
                         {"x": 1, "y": 1, "length": 2})
        empty_combined = self._run_png_pair(reference, reference,
                                            "--longest-difference-column-run",
                                            "--difference-column-runs", "--json")
        self.assertIsNone(json.loads(empty_combined.stdout)["longest_difference_column_run"])

        tmp = self._tmp_dir()
        a = self._write(tmp, "candidate.png", candidate)
        b = self._write(tmp, "reference.png", reference)
        direct = self._run_script(a, b, "--longest-difference-column-run", "--json")
        self.assertIn("longest_difference_column_run", json.loads(direct.stdout))


if __name__ == "__main__":
    unittest.main()
