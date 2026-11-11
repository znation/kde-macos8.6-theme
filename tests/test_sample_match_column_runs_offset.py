"""Tests for paging vertical color-search match intervals."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchColumnRunsOffset(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def setUp(self):
        super().setUp()
        target = (1, 2, 3)
        rows = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        _, encoded = rgb_image(4, 11, lambda x, y: target
                               if 2 <= x < 4 and y - 1 in rows[x - 2]
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        self.base = (path, "2", "1", "--width", "2", "--height", "9",
                     "--find-color", "010203", "--match-column-runs",
                     "--match-column-run-count", "--longest-match-column-run", "--json")

    def test_offset_pages_globally_after_filters_and_preserves_summaries(self):
        common = ("--max-match-column-runs", "2")
        page = self._run(*self.base, *common, "--match-column-run-offset", "2")
        zero = self._run(*self.base, *common, "--match-column-run-offset", "0")
        end = self._run(*self.base, *common, "--match-column-run-offset", "5")
        minimum = self._run(*self.base, "--min-match-column-run-length", "2",
                            "--max-match-column-runs", "1", "--match-column-run-offset", "1")
        maximum = self._run(*self.base, "--max-match-column-run-length", "2",
                            "--max-match-column-runs", "1", "--match-column-run-offset", "1")
        empty_window = self._run(*self.base, "--min-match-column-run-length", "5",
                                 "--max-match-column-run-length", "9", *common,
                                 "--match-column-run-offset", "0")
        absent = self._run(*self.base[:7], "--find-color", "FFFFFF",
                           "--match-column-runs", "--max-match-column-runs", "2",
                           "--match-column-run-offset", "0", "--json")
        for result in (page, zero, end, minimum, maximum, empty_window, absent):
            self._assert_success(result)
        match = json.loads(page.stdout)["match"]
        self.assertEqual(match["column_runs"], [
            {"x": 2, "y": 6, "length": 3}, {"x": 3, "y": 1, "length": 4},
        ])
        self.assertEqual((match["omitted_column_runs"], match["column_run_offset"]), (3, 2))
        self.assertEqual((match["count"], match["column_run_count"]), (11, 5))
        self.assertEqual(match["longest_column_run"], {"x": 3, "y": 1, "length": 4})
        self.assertEqual(json.loads(zero.stdout)["match"]["column_run_offset"], 0)
        self.assertEqual((json.loads(end.stdout)["match"]["column_runs"],
                          json.loads(end.stdout)["match"]["omitted_column_runs"]), ([], 5))
        self.assertEqual(json.loads(minimum.stdout)["match"]["column_runs"],
                         [{"x": 2, "y": 6, "length": 3}])
        self.assertEqual(json.loads(minimum.stdout)["match"]["omitted_column_runs"], 2)
        self.assertEqual(json.loads(maximum.stdout)["match"]["column_runs"],
                         [{"x": 2, "y": 3, "length": 2}])
        self.assertEqual(json.loads(maximum.stdout)["match"]["omitted_column_runs"], 2)
        self.assertEqual((json.loads(empty_window.stdout)["match"]["column_runs"],
                          json.loads(empty_window.stdout)["match"]["omitted_column_runs"]), ([], 0))
        self.assertEqual((json.loads(absent.stdout)["match"]["column_runs"],
                          json.loads(absent.stdout)["match"]["omitted_column_runs"]), ([], 0))

    def test_tolerance_and_alpha_define_intervals_before_paging(self):
        rows = [bytes(pixel) for pixel in (
            (10, 20, 30, 255), (11, 20, 30, 255),
            (10, 20, 30, 0), (10, 20, 30, 255),
        )]
        path = self._write(self._tmp_dir(), "rgba.png",
                           make_png(1, 4, rows, color_type=6))
        base = (path, "0", "0", "--height", "4", "--find-color", "0a141e",
                "--color-tolerance", "1", "--match-column-runs",
                "--max-match-column-runs", "1", "--match-column-run-offset", "0", "--json")
        tolerant = self._run(*base)
        alpha_filtered = self._run(*base, "--match-alpha", "255")
        self._assert_success(tolerant)
        self._assert_success(alpha_filtered)
        self.assertEqual(json.loads(tolerant.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 4}])
        self.assertEqual(json.loads(alpha_filtered.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 2}])
        self.assertEqual(json.loads(alpha_filtered.stdout)["match"]["omitted_column_runs"], 1)

    def test_text_default_direct_script_and_invalid_offsets(self):
        args = self.base[:-1] + ("--max-match-column-runs", "2", "--match-column-run-offset", "2")
        direct = self._run_script(*args, "--json")
        default = self._run(*self.base, "--max-match-column-runs", "2")
        for result in (direct, default):
            self._assert_success(result)
        text_args = self.base[:-1] + ("--max-match-column-runs", "2", "--match-column-run-offset", "2")
        text = self._run(*text_args)
        self._assert_success(text)
        self.assertIn("matching column run offset: 2\nmatching column runs:", text.stdout)
        self.assertNotIn("column_run_offset", json.loads(default.stdout)["match"])
        self.assertEqual(json.loads(direct.stdout)["match"]["column_runs"],
                         json.loads(self._run(*text_args, "--json").stdout)["match"]["column_runs"])
        for value in ("-1", "1.5", "bad", "１"):
            invalid = self._run("missing.png", "0", "0", "--match-column-runs",
                                "--max-match-column-runs", "1", "--match-column-run-offset", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""))
        dependency = self._run("missing.png", "0", "0", "--match-column-run-offset", "0")
        self.assertEqual(dependency.returncode, 2)
        self.assertIn("--match-column-run-offset requires --max-match-column-runs", dependency.stderr)
        self.assertIn("--match-column-run-offset K", self._run("--help").stdout)


if __name__ == "__main__":
    import unittest
    unittest.main()
