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

    def test_offset_crop_count_and_filtered_lists(self):
        target = (10, 20, 30)
        masks = ((1, 0, 1), (1, 0, 0), (0, 0, 1), (1, 0, 1))
        _, encoded = rgb_image(6, 6, lambda x, y: target if
                               (x, y) in ((0, 0), (5, 5)) or
                               (2 <= x <= 4 and 1 <= y <= 4 and
                                masks[y - 1][x - 2]) else (0, 0, 0))
        path = self._write(self._tmp_dir(), "column-count.png", encoded)
        common = (path, "2", "1", "--width", "3", "--height", "4",
                  "--find-color", "0a141e", "--match-column-run-count")
        result = self._run(*common, "--json")
        match = json.loads(result.stdout)["match"]
        self.assertEqual((match["count"], match["column_run_count"]), (6, 4))
        self.assertNotIn("column_runs", match)
        self.assertIn("matching column run count: 4", self._run(*common).stdout)
        combined_text = self._run(*common, "--match-column-runs").stdout
        self.assertLess(combined_text.index("matching column run count:"),
                        combined_text.index("matching column runs:"))
        listed = self._run(*common, "--match-column-runs", "--json")
        expected = [
            {"x": 2, "y": 1, "length": 2},
            {"x": 2, "y": 4, "length": 1},
            {"x": 4, "y": 1, "length": 1},
            {"x": 4, "y": 3, "length": 2},
        ]
        self.assertEqual(json.loads(listed.stdout)["match"]["column_runs"], expected)
        for filters, kept in (( ("--min-match-column-run-length", "2"), 2),
                              (("--max-match-column-run-length", "1"), 2),
                              (("--min-match-column-run-length", "3",
                                "--max-match-column-run-length", "9"), 0)):
            filtered = self._run(*common, "--match-column-runs", *filters, "--json")
            report = json.loads(filtered.stdout)["match"]
            self.assertEqual(report["column_run_count"], 4)
            self.assertEqual(len(report["column_runs"]), kept)
        paged = self._run(*common, "--match-pixels", "1", "--json")
        beyond = self._run(*common, "--match-pixels", "1", "--match-pixel-offset",
                           "99", "--json")
        self.assertEqual(json.loads(paged.stdout)["match"]["column_run_count"], 4)
        self.assertEqual(json.loads(beyond.stdout)["match"]["column_run_count"], 4)
        for option, key in (("--match-run-count", "run_count"),
                            ("--longest-match-column-run", "longest_column_run")):
            separate = self._run(*common[:-1], option, "--json")
            combined = self._run(*common, option, "--match-column-run-count", "--json")
            self.assertEqual(json.loads(separate.stdout)["match"][key],
                             json.loads(combined.stdout)["match"][key])

    def test_boundaries_count_only_and_empty(self):
        target = (10, 20, 30)
        _, encoded = rgb_image(4, 4, lambda x, y: target if
                               x in (1, 2, 3) and y in (1, 2) else (0, 0, 0))
        path = self._write(self._tmp_dir(), "solid-columns.png", encoded)
        for width, height, expected in ((3, 2, 3), (1, 3, 1), (1, 1, 1)):
            args = (path, "1", "1", "--width", str(width), "--height", str(height),
                    "--find-color", "0a141e", "--match-column-run-count", "--json")
            actual = json.loads(self._run(*args).stdout)["match"]["column_run_count"]
            self.assertEqual(actual, expected)
        no_match = self._run(path, "1", "1", "--width", "3", "--height", "2",
                             "--find-color", "ffffff", "--match-column-run-count", "--json")
        self.assertEqual(json.loads(no_match.stdout)["match"]["column_run_count"], 0)
        from tools.sample_match_runs import MatchRuns
        collector = MatchRuns(0, 0, 2, 4, horizontal=False, vertical=True,
                               collect_column_runs=False)
        for y, values in enumerate(((True, False), (True, True), (False, False), (True, True))):
            for x, matches in enumerate(values):
                collector.observe(x, y, matches)
        collector.finish()
        self.assertEqual(collector.column_run_count, 4)
        self.assertEqual(collector.column_runs, [])
        without = self._run(path, "1", "1", "--width", "3", "--height", "2",
                            "--find-color", "0a141e", "--json")
        self.assertNotIn("column_run_count", json.loads(without.stdout)["match"])

    def test_dependency_validation_help_and_direct_script(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("read")), \
                mock.patch.object(sample.os, "open", side_effect=AssertionError("open")):
            invalid = self._run("missing.png", "0", "0", "--match-column-run-count")
        self._assert_usage_error(invalid, "--match-column-run-count requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--match-column-run-count", self._run("--help").stdout)
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one-column.png", encoded)
        script = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-column-run-count", "--json")
        self.assertEqual(json.loads(script.stdout)["match"]["column_run_count"], 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
