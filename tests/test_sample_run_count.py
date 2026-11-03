"""Tests counting scanline color runs in the requested --runs region."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleRunCount(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    A = (1, 2, 3)
    B = (9, 8, 7)

    def _rows_region(self):
        """4x3 region whose horizontal rows carry 2, 2 and 1 color runs."""
        rows = [b"".join(bytes(rgb) for rgb in row)
                for row in ((self.A, self.A, self.B, self.B),
                            (self.B, self.B, self.A, self.A),
                            (self.A, self.A, self.A, self.A))]
        return self._write(self._tmp_dir(), "runs.png", make_png(4, 3, rows))

    def _offset_rows_region(self):
        """The same 4x3 run pattern with one-image pixel of margin around it."""
        rows = [b"".join(bytes(rgb) for rgb in row) for row in (
            [(0, 0, 0)] * 6,
            [(0, 0, 0)] + [self.A, self.A, self.B, self.B] + [(0, 0, 0)],
            [(0, 0, 0)] + [self.B, self.B, self.A, self.A] + [(0, 0, 0)],
            [(0, 0, 0)] + [self.A, self.A, self.A, self.A] + [(0, 0, 0)],
            [(0, 0, 0)] * 6,
        )]
        return self._write(self._tmp_dir(), "offset-runs.png", make_png(6, 5, rows))

    def test_horizontal_count_reports_unfiltered_total_across_scanlines(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "4", "--height", "3",
                  "--runs", "--run-axis", "horizontal", "--run-count")
        report = self._run(*common, "--json")
        self._assert_success(report)
        parsed = json.loads(report.stdout)
        self.assertEqual(parsed["run_count"], 5)
        self.assertEqual([(run["x"], run["y"], run["length"], run["rgb"]) for run in parsed["runs"]], [
            (0, 0, 2, list(self.A)), (2, 0, 2, list(self.B)),
            (0, 1, 2, list(self.B)), (2, 1, 2, list(self.A)),
            (0, 2, 4, list(self.A)),
        ])
        text = self._run(*common)
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines()[3], "run count: 5")
        self.assertEqual(text.stdout.splitlines()[4], "(0, 0): 1,2,3  #010203  length=2")

    def test_filters_select_listed_runs_while_count_keeps_unfiltered_total(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "4", "--height", "3",
                  "--runs", "--run-axis", "horizontal", "--run-count")
        for options, listed in (
            (("--run-color", "090807"), [(2, 0), (0, 1)]),
            (("--exclude-run-color", "010203"), [(2, 0), (0, 1)]),
            (("--min-run-length", "3"), [(0, 2)]),
            (("--max-run-length", "3"), [(0, 0), (2, 0), (0, 1), (2, 1)]),
        ):
            result = self._run(*common, *options, "--json")
            self._assert_success(result)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["run_count"], 5)
            self.assertEqual([(run["x"], run["y"]) for run in parsed["runs"]], listed)
        empty = self._run(*common, "--min-run-length", "2", "--max-run-length", "1", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["run_count"], 5)
        self.assertEqual(json.loads(empty.stdout)["runs"], [])

    def test_vertical_count_and_axis_row_boundaries(self):
        rows = [b"".join(bytes(rgb) for rgb in row)
                for row in ((self.A, self.B), (self.A, self.B), (self.B, self.B))]
        path = self._write(self._tmp_dir(), "vertical.png", make_png(2, 3, rows))
        vertical = self._run(path, "0", "0", "--width", "2", "--height", "3",
                             "--runs", "--run-axis", "vertical", "--run-count", "--json")
        self._assert_success(vertical)
        self.assertEqual(json.loads(vertical.stdout)["run_count"], 3)
        self.assertEqual(json.loads(vertical.stdout)["axis"], "vertical")
        horizontal = self._run(path, "0", "0", "--width", "2", "--height", "3",
                               "--runs", "--run-axis", "horizontal", "--run-count", "--json")
        self._assert_success(horizontal)
        self.assertEqual(json.loads(horizontal.stdout)["run_count"], 5)

    def test_single_pixel_region_counts_one_run(self):
        _, data = rgb_image(1, 1, lambda _x, _y: self.A)
        path = self._write(self._tmp_dir(), "one-pixel.png", data)
        result = self._run(path, "0", "0", "--runs", "--run-count", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["run_count"], 1)

    def test_alpha_grouping_counts_follow_the_emitted_runs(self):
        alphas = [(10, 20, 30, 0), (10, 20, 30, 255), (40, 50, 60, 0)]
        rows = [b"".join(bytes(pixel) for pixel in alphas)]
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, rows, color_type=6))
        with_alpha = self._run(path, "0", "0", "--width", "3", "--runs", "--alpha", "--run-count", "--json")
        self._assert_success(with_alpha)
        parsed = json.loads(with_alpha.stdout)
        self.assertEqual((parsed["run_count"], len(parsed["runs"])), (3, 3))
        self.assertEqual([run["alpha"] for run in parsed["runs"]], [0, 255, 0])
        without_alpha = self._run(path, "0", "0", "--width", "3", "--runs", "--run-count", "--json")
        self._assert_success(without_alpha)
        self.assertEqual(json.loads(without_alpha.stdout)["run_count"], 2)
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb_image(2, 1, lambda x, y: (1, 2, 3))[1])
        opaque_result = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha", "--run-count", "--json")
        self._assert_success(opaque_result)
        opaque_parsed = json.loads(opaque_result.stdout)
        self.assertEqual((opaque_parsed["run_count"], len(opaque_parsed["runs"])), (1, 1))
        self.assertEqual(opaque_parsed["runs"][0]["alpha"], 255)

    def test_region_relative_offsets_keep_absolute_coordinates_and_count(self):
        path = self._offset_rows_region()
        result = self._run(path, "1", "1", "--width", "4", "--height", "3",
                           "--runs", "--run-axis", "horizontal", "--run-count", "--json")
        self._assert_success(result)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["run_count"], 5)
        self.assertEqual([(run["x"], run["y"]) for run in parsed["runs"]],
                         [(1, 1), (3, 1), (1, 2), (3, 2), (1, 3)])

    def test_omitting_the_flag_omits_key_line_and_counting(self):
        path = self._rows_region()
        result = self._run(path, "0", "0", "--width", "4", "--height", "3",
                           "--runs", "--run-axis", "horizontal", "--json")
        self._assert_success(result)
        self.assertNotIn("run_count", json.loads(result.stdout))
        plain_text = self._run(path, "0", "0", "--width", "4", "--height", "3",
                               "--runs", "--run-axis", "horizontal")
        self._assert_success(plain_text)
        self.assertNotIn("run count:", plain_text.stdout)
        with mock.patch.object(sample, "read_png_size", wraps=sample.read_png_size) as size, \
                mock.patch.object(sample, "report") as runs:
            self._run(path, "0", "0", "--width", "4", "--height", "3",
                      "--runs", "--run-axis", "horizontal", "--json")
        self.assertEqual(size.call_count, 1)
        args = runs.call_args[0][0]
        self.assertFalse(getattr(args, "run_count", None))

    def test_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--run-count")
        self._assert_usage_error(invalid, "--run-count requires --runs")
        self.assertEqual(invalid.stdout, "")
        histogram = self._run("missing.png", "0", "0", "--histogram", "--run-count")
        self._assert_usage_error(histogram, "--run-count requires --runs")
        self.assertIn("--run-count", self._run("--help").stdout)
        path = self._rows_region()
        shaped = self._run(path, "0", "0", "--width", "3", "--height", "3",
                           "--runs", "--run-axis", "horizontal", "--run-count", "--json")
        self._assert_success(shaped)
        self.assertEqual(json.loads(shaped.stdout)["run_count"], 5)
        script = self._run_script(path, "0", "0", "--width", "2",
                                  "--runs", "--run-count", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["run_count"], 1)
        self.assertEqual(json.loads(script.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 2, "rgb": list(self.A), "hex": "#010203"},
        ])


if __name__ == "__main__":
    import unittest

    unittest.main()
