"""Tests counting horizontal color-match segments."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchRunCount(CliTestCase):
    """The find-color search's ``--match-run-count`` total."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_crop_count_is_independent_of_list_filters_and_paging(self):
        target = (10, 20, 30)
        masks = ((1, 1, 0, 1), (0, 0, 0, 0), (1, 1, 1, 1))
        _, encoded = rgb_image(7, 5, lambda x, y: target if
                               (x, y) in ((1, 0), (6, 4)) or
                               (1 <= y <= 3 and 2 <= x <= 5 and masks[y - 1][x - 2])
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        common = (path, "2", "1", "--width", "4", "--height", "3",
                  "--find-color", "0a141e", "--match-run-count")
        report = self._run(*common, "--json")
        match = json.loads(report.stdout)["match"]
        self.assertEqual((match["count"], match["run_count"]), (7, 3))
        self.assertNotIn("runs", match)
        self.assertNotIn("column_runs", match)
        self.assertIn("matching run count: 3", self._run(*common).stdout)
        listed = self._run(*common, "--match-runs", "--json")
        self.assertEqual(json.loads(listed.stdout)["match"]["runs"], [
            {"x": 2, "y": 1, "length": 2},
            {"x": 5, "y": 1, "length": 1},
            {"x": 2, "y": 3, "length": 4},
        ])
        for filters in (("--min-match-run-length", "3"),
                        ("--max-match-run-length", "1")):
            result = self._run(*common, "--match-runs", *filters, "--json")
            match = json.loads(result.stdout)["match"]
            self.assertEqual(match["run_count"], 3)
            self.assertEqual(len(match["runs"]), 1)
        for paging in (("--match-pixels", "1"),
                       ("--match-pixels", "1", "--match-pixel-offset", "99")):
            result = self._run(*common, *paging, "--json")
            self.assertEqual(json.loads(result.stdout)["match"]["run_count"], 3)

    def test_empty_full_rows_and_collector_without_list(self):
        target = (10, 20, 30)
        _, encoded = rgb_image(4, 4, lambda x, y: target if x in (1, 2, 3) and y in (1, 2)
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "solid.png", encoded)
        args = (path, "1", "1", "--width", "3", "--height", "2",
                "--find-color", "0a141e", "--match-run-count", "--json")
        self.assertEqual(json.loads(self._run(*args).stdout)["match"]["run_count"], 2)
        narrow = self._run(path, "1", "1", "--width", "1", "--height", "2",
                           "--find-color", "0a141e", "--match-run-count", "--json")
        self.assertEqual(json.loads(narrow.stdout)["match"]["run_count"], 2)
        empty = self._run(path, "1", "1", "--width", "3", "--height", "2",
                          "--find-color", "ffffff", "--match-run-count", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["run_count"], 0)
        from tools.sample_match_runs import MatchRuns
        collector = MatchRuns(0, 0, 4, 1, horizontal=True, vertical=False,
                               collect_runs=False)
        for x, yes in enumerate((True, True, False, True)):
            collector.observe(x, 0, yes)
        collector.finish()
        self.assertEqual(collector.run_count, 2)
        self.assertEqual(collector.runs, [])
        without_flag = self._run(*args[:-2], "--json")
        self.assertNotIn("run_count", json.loads(without_flag.stdout)["match"])

    def test_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--match-run-count")
        self._assert_usage_error(invalid, "--match-run-count requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--match-run-count", self._run("--help").stdout)
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        script = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-run-count", "--json")
        self.assertEqual(json.loads(script.stdout)["match"]["run_count"], 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
