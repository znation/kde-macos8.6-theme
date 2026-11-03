"""Tests counting vertical color-match segments."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchColumnRunCount(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_crop_count_is_independent_of_list_filters_and_paging(self):
        target = (10, 20, 30)
        masks = ((1, 0, 1), (1, 0, 0), (0, 0, 1), (1, 0, 1))
        _, encoded = rgb_image(7, 6, lambda x, y: target if
                               (x, y) in ((0, 0), (6, 5)) or
                               (2 <= x <= 4 and 1 <= y <= 4 and
                                masks[y - 1][x - 2]) else (0, 0, 0))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        common = (path, "2", "1", "--width", "3", "--height", "4",
                  "--find-color", "0a141e", "--match-column-run-count")
        report = self._run(*common, "--json")
        match = json.loads(report.stdout)["match"]
        self.assertEqual((match["count"], match["column_run_count"]), (6, 4))
        self.assertNotIn("column_runs", match)
        text = self._run(*common).stdout
        self.assertIn("matching column run count: 4", text)

        listed = self._run(*common, "--match-column-runs", "--json")
        match = json.loads(listed.stdout)["match"]
        self.assertEqual(match["column_run_count"], 4)
        self.assertEqual(match["column_runs"], [
            {"x": 2, "y": 1, "length": 2},
            {"x": 2, "y": 4, "length": 1},
            {"x": 4, "y": 1, "length": 1},
            {"x": 4, "y": 3, "length": 2},
        ])
        combined_text = self._run(*common, "--match-column-runs").stdout
        self.assertLess(combined_text.index("matching column run count:"),
                        combined_text.index("matching column runs:"))
        for filters in (("--min-match-column-run-length", "2"),
                        ("--max-match-column-run-length", "1")):
            result = self._run(*common, "--match-column-runs", *filters, "--json")
            match = json.loads(result.stdout)["match"]
            self.assertEqual(match["column_run_count"], 4)
            self.assertEqual(len(match["column_runs"]), 2)
        result = self._run(*common, "--match-column-runs",
                           "--min-match-column-run-length", "3",
                           "--max-match-column-run-length", "1", "--json")
        match = json.loads(result.stdout)["match"]
        self.assertEqual((match["column_run_count"], match["column_runs"]), (4, []))
        for paging in (("--match-pixels", "1"),
                       ("--match-pixels", "1", "--match-pixel-offset", "99")):
            result = self._run(*common, *paging, "--json")
            self.assertEqual(json.loads(result.stdout)["match"]["column_run_count"], 4)

    def test_empty_solid_and_collector_without_list(self):
        target = (10, 20, 30)
        _, encoded = rgb_image(4, 4, lambda x, y: target if x in (1, 2, 3) and y in (1, 2)
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "solid.png", encoded)
        base = (path, "1", "1", "--width", "3", "--height", "2",
                "--find-color", "0a141e", "--match-column-run-count", "--json")
        self.assertEqual(json.loads(self._run(*base).stdout)["match"]["column_run_count"], 3)
        empty = self._run(path, "1", "1", "--width", "3", "--height", "2",
                          "--find-color", "ffffff", "--match-column-run-count", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["column_run_count"], 0)
        from tools.sample_match_runs import _MatchRuns
        collector = _MatchRuns(0, 0, 2, 4, horizontal=False, vertical=True,
                               collect_column_runs=False)
        for y, yes in enumerate((True, True, False, True)):
            collector.observe(0, y, yes)
        collector.finish()
        self.assertEqual(collector.column_run_count, 2)
        self.assertEqual(collector.column_runs, [])
        without_flag = self._run(*base[:-2], "--json")
        self.assertNotIn("column_run_count", json.loads(without_flag.stdout)["match"])

    def test_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--match-column-run-count")
        self._assert_usage_error(invalid, "--match-column-run-count requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--match-column-run-count", self._run("--help").stdout)
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        script = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-column-run-count", "--json")
        self.assertEqual(json.loads(script.stdout)["match"]["column_run_count"], 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
