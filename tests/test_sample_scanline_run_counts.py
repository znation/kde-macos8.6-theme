"""Tests listing per-scanline color-run counts in the requested --runs region."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleScanlineRunCounts(CliTestCase):
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

    def test_horizontal_counts_list_each_scanline_in_order(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "4", "--height", "3",
                  "--runs", "--run-axis", "horizontal", "--scanline-run-counts")
        report = self._run(*common, "--json")
        self._assert_success(report)
        parsed = json.loads(report.stdout)
        self.assertEqual(parsed["scanline_run_counts"], [2, 2, 1])
        self.assertEqual([(run["x"], run["y"], run["length"], run["rgb"]) for run in parsed["runs"]], [
            (0, 0, 2, list(self.A)), (2, 0, 2, list(self.B)),
            (0, 1, 2, list(self.B)), (2, 1, 2, list(self.A)),
            (0, 2, 4, list(self.A)),
        ])
        text = self._run(*common)
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines()[3], "scanline run counts: 2, 2, 1")
        self.assertEqual(text.stdout.splitlines()[4], "(0, 0): 1,2,3  #010203  length=2")
        self.assertEqual(text.stdout.splitlines()[3],
                         "scanline run counts: " + ", ".join(str(count) for count in parsed["scanline_run_counts"]))

    def test_filters_follow_their_listed_runs_while_counts_stay_unfiltered(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "4", "--height", "3",
                  "--runs", "--run-axis", "horizontal", "--scanline-run-counts")
        for options, listed in (
            (("--run-color", "090807"), [(2, 0), (0, 1)]),
            (("--exclude-run-color", "010203"), [(2, 0), (0, 1)]),
            (("--min-run-length", "3"), [(0, 2)]),
            (("--max-run-length", "3"), [(0, 0), (2, 0), (0, 1), (2, 1)]),
        ):
            result = self._run(*common, *options, "--json")
            self._assert_success(result)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["scanline_run_counts"], [2, 2, 1])
            self.assertEqual([(run["x"], run["y"]) for run in parsed["runs"]], listed)
        empty = self._run(*common, "--min-run-length", "2", "--max-run-length", "1", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["scanline_run_counts"], [2, 2, 1])
        self.assertEqual(json.loads(empty.stdout)["runs"], [])

    def test_vertical_counts_list_each_column_left_to_right(self):
        rows = [b"".join(bytes(rgb) for rgb in row)
                for row in ((self.A, self.B), (self.A, self.B), (self.B, self.B))]
        path = self._write(self._tmp_dir(), "vertical.png", make_png(2, 3, rows))
        vertical = self._run(path, "0", "0", "--width", "2", "--height", "3",
                             "--runs", "--run-axis", "vertical", "--scanline-run-counts", "--json")
        self._assert_success(vertical)
        parsed = json.loads(vertical.stdout)
        self.assertEqual(parsed["axis"], "vertical")
        self.assertEqual(parsed["scanline_run_counts"], [2, 1])
        self.assertEqual([(run["x"], run["y"], run["length"]) for run in parsed["runs"]],
                         [(0, 0, 2), (0, 2, 1), (1, 0, 3)])
        horizontal = self._run(path, "0", "0", "--width", "2", "--height", "3",
                               "--runs", "--run-axis", "horizontal", "--scanline-run-counts", "--json")
        self._assert_success(horizontal)
        self.assertEqual(json.loads(horizontal.stdout)["scanline_run_counts"], [2, 2, 1])

    def test_single_row_single_pixel_and_one_by_one_regions(self):
        path = self._rows_region()
        single_row = self._run(path, "0", "1", "--width", "4",
                               "--runs", "--scanline-run-counts", "--json")
        self._assert_success(single_row)
        self.assertEqual(json.loads(single_row.stdout)["scanline_run_counts"], [2])
        _, data = rgb_image(1, 1, lambda _x, _y: self.A)
        single_pixel = self._write(self._tmp_dir(), "one-pixel.png", data)
        result = self._run(single_pixel, "0", "0", "--runs", "--scanline-run-counts", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["scanline_run_counts"], [1])

    def test_alpha_grouping_counts_follow_the_emitted_runs(self):
        alphas = [(10, 20, 30, 0), (10, 20, 30, 255), (40, 50, 60, 0)]
        rows = [b"".join(bytes(pixel) for pixel in alphas)]
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, rows, color_type=6))
        with_alpha = self._run(path, "0", "0", "--width", "3", "--runs", "--alpha",
                               "--scanline-run-counts", "--json")
        self._assert_success(with_alpha)
        parsed = json.loads(with_alpha.stdout)
        self.assertEqual(parsed["scanline_run_counts"], [3])
        self.assertEqual([run["alpha"] for run in parsed["runs"]], [0, 255, 0])
        without_alpha = self._run(path, "0", "0", "--width", "3", "--runs",
                                  "--scanline-run-counts", "--json")
        self._assert_success(without_alpha)
        self.assertEqual(json.loads(without_alpha.stdout)["scanline_run_counts"], [2])
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb_image(2, 1, lambda x, y: (1, 2, 3))[1])
        opaque_result = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha",
                                  "--scanline-run-counts", "--json")
        self._assert_success(opaque_result)
        self.assertEqual(json.loads(opaque_result.stdout)["scanline_run_counts"], [1])

    def test_combining_with_run_count_reports_both_totals(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "4", "--height", "3",
                  "--runs", "--run-axis", "horizontal", "--run-count", "--scanline-run-counts")
        report = self._run(*common, "--json")
        self._assert_success(report)
        parsed = json.loads(report.stdout)
        self.assertEqual(parsed["run_count"], 5)
        self.assertEqual(parsed["scanline_run_counts"], [2, 2, 1])
        self.assertEqual(sum(parsed["scanline_run_counts"]), parsed["run_count"])
        text = self._run(*common)
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines()[3], "run count: 5")
        self.assertEqual(text.stdout.splitlines()[4], "scanline run counts: 2, 2, 1")
        self.assertEqual(text.stdout.splitlines()[5], "(0, 0): 1,2,3  #010203  length=2")

    def test_omitting_the_flag_omits_key_line_and_counting(self):
        path = self._rows_region()
        result = self._run(path, "0", "0", "--width", "4", "--height", "3",
                           "--runs", "--run-axis", "horizontal", "--run-count", "--json")
        self._assert_success(result)
        self.assertNotIn("scanline_run_counts", json.loads(result.stdout))
        plain_text = self._run(path, "0", "0", "--width", "4", "--height", "3",
                               "--runs", "--run-axis", "horizontal")
        self._assert_success(plain_text)
        self.assertNotIn("scanline run counts:", plain_text.stdout)
        with mock.patch.object(sample, "read_png_size", wraps=sample.read_png_size) as size, \
                mock.patch.object(sample, "report") as runs:
            self._run(path, "0", "0", "--width", "4", "--height", "3",
                      "--runs", "--run-axis", "horizontal", "--json")
        self.assertEqual(size.call_count, 1)
        args = runs.call_args[0][0]
        self.assertFalse(getattr(args, "scanline_run_counts", None))

    def test_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--scanline-run-counts")
        self._assert_usage_error(invalid, "--scanline-run-counts requires --runs")
        self.assertEqual(invalid.stdout, "")
        histogram = self._run("missing.png", "0", "0", "--histogram", "--scanline-run-counts")
        self._assert_usage_error(histogram, "--scanline-run-counts requires --runs")
        find_color = self._run("missing.png", "0", "0", "--find-color", "010203", "--scanline-run-counts")
        self._assert_usage_error(find_color, "--scanline-run-counts requires --runs")
        self.assertIn("--scanline-run-counts", self._run("--help").stdout)
        path = self._rows_region()
        shaped = self._run(path, "0", "0", "--width", "3", "--height", "3",
                           "--runs", "--run-axis", "horizontal", "--scanline-run-counts", "--json")
        self._assert_success(shaped)
        self.assertEqual(json.loads(shaped.stdout)["scanline_run_counts"], [2, 2, 1])
        script = self._run_script(path, "0", "0", "--width", "2",
                                  "--runs", "--scanline-run-counts", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["scanline_run_counts"], [1])


if __name__ == "__main__":
    import unittest

    unittest.main()
