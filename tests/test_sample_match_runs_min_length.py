"""Tests for filtering short horizontal color-search match segments."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchRunsMinLength(CliTestCase):
    """The horizontal match runs' ``--min-match-run-length`` cutoff."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_cutoff_filters_only_emitted_runs_and_preserves_other_diagnostics(self):
        target = (10, 20, 30)
        rows = [
            [(0, 0, 0), target, (11, 20, 30), (0, 0, 0), target, (0, 0, 0)],
            [target, target, (0, 0, 0), target, (0, 0, 0), (0, 0, 0)],
            [(0, 0, 0), target, target, target, (0, 0, 0), (0, 0, 0)],
        ]
        _, encoded = rgb_image(8, 5, lambda x, y: rows[y - 1][x - 1]
                               if 1 <= x <= 6 and 1 <= y <= 3 else (90, 90, 90))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        base = (path, "1", "1", "--width", "6", "--height", "3", "--find-color",
                "0a141e", "--color-tolerance", "1", "--match-runs", "--longest-match-run",
                "--longest-match-column-run", "--match-column-runs", "--match-pixels", "1")
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            unfiltered = self._run(*base, "--json")
            filtered = self._run(*base, "--min-match-run-length", "2", "--json")
        self._assert_success(unfiltered)
        self._assert_success(filtered)
        full = json.loads(unfiltered.stdout)["match"]
        result = json.loads(filtered.stdout)["match"]
        self.assertEqual(result["runs"], [
            {"x": 2, "y": 1, "length": 2},
            {"x": 1, "y": 2, "length": 2},
            {"x": 2, "y": 3, "length": 3},
        ])
        for key in ("count", "bounds", "pixels", "column_runs", "longest_run",
                    "longest_column_run"):
            self.assertEqual(result[key], full[key], key)
        self.assertEqual(result["count"], 9)
        self.assertEqual(result["longest_run"], {"x": 2, "y": 3, "length": 3})
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        too_high = self._run(*base, "--min-match-run-length", "7", "--json")
        self._assert_success(too_high)
        high_match = json.loads(too_high.stdout)["match"]
        self.assertEqual(high_match["runs"], [])
        self.assertEqual(high_match["longest_run"], full["longest_run"])
        self.assertEqual(high_match["count"], full["count"])
        text = self._run(*base, "--min-match-run-length", "7")
        self._assert_success(text)
        self.assertIn("matching runs: []", text.stdout)
        omitted = self._run(*base, "--json")
        self._assert_success(omitted)
        self.assertEqual(json.loads(omitted.stdout)["match"]["runs"], full["runs"])

    def test_cutoff_one_empty_matches_alpha_and_direct_script(self):
        rgba = make_png(5, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 255,
                                     1, 2, 3, 0, 9, 9, 9, 0))], color_type=6)
        path = self._write(self._tmp_dir(), "rgba.png", rgba)
        options = (path, "0", "0", "--width", "5", "--find-color", "010203",
                   "--match-alpha", "0", "--match-runs")
        baseline = self._run(*options, "--json")
        cutoff = self._run(*options, "--min-match-run-length", "1", "--json")
        self._assert_success(baseline)
        self._assert_success(cutoff)
        self.assertEqual(json.loads(baseline.stdout)["match"]["runs"],
                         json.loads(cutoff.stdout)["match"]["runs"])
        self.assertEqual(json.loads(cutoff.stdout)["match"]["runs"], [
            {"x": 0, "y": 0, "length": 2}, {"x": 3, "y": 0, "length": 1}])
        opaque_png = rgb_image(2, 1, lambda x, y: (1, 2, 3))[1]
        opaque = self._write(self._tmp_dir(), "opaque.png", opaque_png)
        fallback = self._run(opaque, "0", "0", "--width", "2", "--find-color", "010203",
                             "--match-alpha", "255", "--match-runs",
                             "--min-match-run-length", "2", "--json")
        self._assert_success(fallback)
        self.assertEqual(json.loads(fallback.stdout)["match"]["runs"],
                         [{"x": 0, "y": 0, "length": 2}])
        empty = self._run(*options[:-1], "--match-runs", "--min-match-run-length", "1",
                          "--find-color", "ffffff", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["match"]["runs"], [])
        direct = self._run_script(*options, "--min-match-run-length", "2", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["runs"],
                         [{"x": 0, "y": 0, "length": 2}])

    def test_invalid_values_and_help(self):
        for value in ("0", "-1", "１", "nope"):
            with self.subTest(value=value):
                result = self._run("missing.png", "0", "0", "--find-color", "010203",
                                   "--match-runs", "--min-match-run-length", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-runs", "--min-match-run-length")
        self.assertEqual(missing.returncode, 2)
        help_result = self._run("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--min-match-run-length N", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
