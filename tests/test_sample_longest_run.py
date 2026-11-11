"""Tests summarizing the longest scanline color run in the requested --runs region."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleLongestRun(CliTestCase):
    """The scanline runs report's ``--longest-run`` summary."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    A = (1, 2, 3)
    B = (9, 8, 7)
    CDEF = (20, 30, 40)
    GHIJ = (50, 60, 70)
    KLMN = (90, 100, 110)
    OPQ = (130, 140, 150)
    BG = (0, 0, 0)

    def _rows_region(self):
        """5x4 region whose scanlines yield runs of lengths 2+3, then 5, 5, then 4.

        Rows 1 and 2 both hold a length-5 run, so the earliest scanline wins the
        cross-scanline tie at its first (only) run.
        """
        rows = [b"".join(bytes(rgb) for rgb in row)
                for row in ((self.A, self.A, self.B, self.B, self.B),
                            (self.CDEF,) * 5,
                            (self.GHIJ,) * 5,
                            (self.KLMN,) * 4 + (self.OPQ,))]
        return self._write(self._tmp_dir(), "runs.png", make_png(5, 4, rows))

    def _offset_rows_region(self):
        """The same 5x4 run pattern with one-image pixel of margin around it."""
        rows = [b"".join(bytes(rgb) for rgb in row) for row in (
            [self.BG] * 7,
            [self.BG] + [self.A, self.A, self.B, self.B, self.B] + [self.BG],
            [self.BG] + [self.CDEF] * 5 + [self.BG],
            [self.BG] + [self.GHIJ] * 5 + [self.BG],
            [self.BG] + [self.KLMN] * 4 + [self.OPQ] + [self.BG],
            [self.BG] * 7,
        )]
        return self._write(self._tmp_dir(), "offset-runs.png", make_png(7, 6, rows))

    def test_horizontal_summary_holds_first_maximal_run_in_scan_order(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "5", "--height", "4",
                  "--runs", "--run-axis", "horizontal", "--longest-run")
        report = self._run(*common, "--json")
        self._assert_success(report)
        parsed = json.loads(report.stdout)
        self.assertEqual(parsed["longest_run"], {
            "x": 0, "y": 1, "length": 5,
            "rgb": list(self.CDEF), "hex": "#141E28",
        })
        self.assertEqual([(run["x"], run["y"], run["length"]) for run in parsed["runs"]], [
            (0, 0, 2), (2, 0, 3), (0, 1, 5), (0, 2, 5), (0, 3, 4), (4, 3, 1),
        ])
        text = self._run(*common)
        self._assert_success(text)
        lines = text.stdout.splitlines()
        self.assertEqual(lines[3], "longest run: 0,1,5")
        self.assertEqual(lines[4], "(0, 0): 1,2,3  #010203  length=2")

    def test_filters_select_listed_runs_while_summary_keeps_unfiltered_run(self):
        path = self._rows_region()
        common = (path, "0", "0", "--width", "5", "--height", "4",
                  "--runs", "--run-axis", "horizontal", "--longest-run")
        longest = {"x": 0, "y": 1, "length": 5,
                   "rgb": list(self.CDEF), "hex": "#141E28"}
        for options, listed in (
            (("--run-color", "010203"), [(0, 0, 2)]),
            (("--exclude-run-color", "141E28"), [(0, 0, 2), (2, 0, 3), (0, 2, 5), (0, 3, 4), (4, 3, 1)]),
            (("--min-run-length", "4"), [(0, 1, 5), (0, 2, 5), (0, 3, 4)]),
            (("--max-run-length", "3"), [(0, 0, 2), (2, 0, 3), (4, 3, 1)]),
        ):
            result = self._run(*common, *options, "--json")
            self._assert_success(result)
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["longest_run"], longest)
            self.assertEqual([(run["x"], run["y"], run["length"]) for run in parsed["runs"]], listed)
        empty = self._run(*common, "--min-run-length", "6", "--max-run-length", "9", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["longest_run"], longest)
        self.assertEqual(json.loads(empty.stdout)["runs"], [])

    def test_region_relative_offsets_keep_absolute_coordinates(self):
        path = self._offset_rows_region()
        result = self._run(path, "1", "1", "--width", "5", "--height", "4",
                           "--runs", "--run-axis", "horizontal", "--longest-run", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["longest_run"],
                         {"x": 1, "y": 2, "length": 5,
                          "rgb": list(self.CDEF), "hex": "#141E28"})

    def test_vertical_summary_resolves_column_ties_by_scan_order(self):
        rows = [b"".join(bytes(rgb) for rgb in row)
                for row in ((self.A, self.A, self.B), (self.A, self.B, self.B))]
        path = self._write(self._tmp_dir(), "vertical.png", make_png(3, 2, rows))
        vertical = self._run(path, "0", "0", "--width", "3", "--height", "2",
                             "--runs", "--run-axis", "vertical", "--longest-run", "--json")
        self._assert_success(vertical)
        parsed = json.loads(vertical.stdout)
        self.assertEqual(parsed["axis"], "vertical")
        self.assertEqual(parsed["longest_run"],
                         {"x": 0, "y": 0, "length": 2,
                          "rgb": list(self.A), "hex": "#010203"})
        # The same region shifted by one-image pixel keeps absolute coordinates.
        margin = [(self.BG, self.BG, self.BG, self.BG),
                  (self.BG, self.A, self.A, self.BG),
                  (self.BG, self.A, self.B, self.BG),
                  (self.BG, self.BG, self.BG, self.BG)]
        shifted_path = self._write(self._tmp_dir(), "vertical-offset.png",
                                   make_png(4, 4, [b"".join(bytes(rgb) for rgb in row) for row in margin]))
        shifted = self._run(shifted_path, "1", "1", "--width", "2", "--height", "2",
                            "--runs", "--run-axis", "vertical", "--longest-run", "--json")
        self._assert_success(shifted)
        self.assertEqual(json.loads(shifted.stdout)["longest_run"],
                         {"x": 1, "y": 1, "length": 2,
                          "rgb": list(self.A), "hex": "#010203"})

    def test_single_row_scan_reports_that_row_and_single_pixel_reports_one(self):
        row = (self.A, self.A, self.B, self.B)
        path = self._write(self._tmp_dir(), "row.png", make_png(4, 1, [b"".join(bytes(rgb) for rgb in row)]))
        result = self._run(path, "0", "0", "--width", "4", "--runs", "--longest-run", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 2,
                          "rgb": list(self.A), "hex": "#010203"})
        one, data = rgb_image(1, 1, lambda _x, _y: self.A)
        del one
        single = self._write(self._tmp_dir(), "one-pixel.png", data)
        pixel = self._run(single, "0", "0", "--runs", "--longest-run", "--json")
        self._assert_success(pixel)
        self.assertEqual(json.loads(pixel.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 1,
                          "rgb": list(self.A), "hex": "#010203"})

    def test_alpha_grouping_mirrors_the_emitted_runs(self):
        alphas = [(10, 20, 30, 0), (10, 20, 30, 255), (40, 50, 60, 0)]
        path = self._write(self._tmp_dir(), "rgba.png",
                           make_png(3, 1, [b"".join(bytes(pixel) for pixel in alphas)], color_type=6))
        with_alpha = self._run(path, "0", "0", "--width", "3", "--runs", "--alpha", "--longest-run", "--json")
        self._assert_success(with_alpha)
        self.assertEqual(json.loads(with_alpha.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 1, "rgb": [10, 20, 30],
                          "hex": "#0A141E", "alpha": 0})
        without_alpha = self._run(path, "0", "0", "--width", "3", "--runs", "--longest-run", "--json")
        self._assert_success(without_alpha)
        self.assertEqual(json.loads(without_alpha.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 2, "rgb": [10, 20, 30], "hex": "#0A141E"})
        opaque = self._write(self._tmp_dir(), "opaque.png",
                             rgb_image(2, 1, lambda x, y: (1, 2, 3))[1])
        opaque_result = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha",
                                  "--longest-run", "--json")
        self._assert_success(opaque_result)
        self.assertEqual(json.loads(opaque_result.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 2, "rgb": [1, 2, 3],
                          "hex": "#010203", "alpha": 255})

    def test_omitting_the_flag_omits_key_line_comparison_and_extra_scans(self):
        path = self._rows_region()
        result = self._run(path, "0", "0", "--width", "5", "--height", "4",
                           "--runs", "--run-axis", "horizontal", "--json")
        self._assert_success(result)
        self.assertNotIn("longest_run", json.loads(result.stdout))
        plain_text = self._run(path, "0", "0", "--width", "5", "--height", "4",
                               "--runs", "--run-axis", "horizontal")
        self._assert_success(plain_text)
        self.assertNotIn("longest run:", plain_text.stdout)
        with mock.patch.object(sample, "read_png_size", wraps=sample.read_png_size) as size, \
                mock.patch.object(sample, "report") as runs:
            self._run(path, "0", "0", "--width", "5", "--height", "4",
                      "--runs", "--run-axis", "horizontal", "--json")
        self.assertEqual(size.call_count, 1)
        args = runs.call_args[0][0]
        self.assertFalse(getattr(args, "longest_run", None))

    def test_no_second_scan_when_requested_or_omitted(self):
        path = self._rows_region()
        from tools import sample_report_runs
        for extra in ((), ("--longest-run",)):
            with self.subTest(extra=extra), \
                    mock.patch.object(sample_report_runs, "_color_runs",
                                      wraps=sample_report_runs._color_runs) as color_runs:
                result = self._run(path, "0", "0", "--width", "5", "--height", "4",
                                   "--runs", "--run-axis", "horizontal", *extra, "--json")
                self._assert_success(result)
                self.assertEqual(color_runs.call_count, 4)

    def test_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--longest-run")
        self._assert_usage_error(invalid, "--longest-run requires --runs")
        self.assertEqual(invalid.stdout, "")
        histogram = self._run("missing.png", "0", "0", "--histogram", "--longest-run")
        self._assert_usage_error(histogram, "--longest-run requires --runs")
        search = self._run("missing.png", "0", "0", "--find-color", "010203", "--longest-run")
        self._assert_usage_error(search, "--longest-run requires --runs")
        self.assertIn("--longest-run", self._run("--help").stdout)
        path = self._rows_region()
        script = self._run_script(path, "0", "0", "--height", "4",
                                  "--runs", "--longest-run", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["longest_run"],
                         {"x": 0, "y": 0, "length": 1,
                          "rgb": list(self.A), "hex": "#010203"})


if __name__ == "__main__":
    import unittest

    unittest.main()
