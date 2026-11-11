"""Tests the optional longest horizontal match summary."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleLongestMatchRun(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_summary_and_full_runs_use_offset_crop_and_row_major_ties(self):
        target = (10, 20, 30)
        rows = [[target, target, (0, 0, 0), target],
                [target, target, (0, 0, 0), target]]
        _, encoded = rgb_image(6, 4, lambda x, y: rows[y - 1][x - 1]
                               if 1 <= y <= 2 and 1 <= x <= 4 else (80, 80, 80))
        path = self._write(self._tmp_dir(), "runs.png", encoded)
        result = self._run(path, "1", "1", "--width", "4", "--height", "2",
                           "--find-color", "0a141e", "--longest-match-run", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["longest_run"], {"x": 1, "y": 1, "length": 2})
        self.assertNotIn("runs", match)
        combined = self._run(path, "1", "1", "--width", "4", "--height", "2",
                             "--find-color", "0a141e", "--longest-match-run",
                             "--match-runs", "--match-pixels", "1", "--json")
        self.assertEqual(json.loads(combined.stdout)["match"]["runs"], [
            {"x": 1, "y": 1, "length": 2}, {"x": 4, "y": 1, "length": 1},
            {"x": 1, "y": 2, "length": 2}, {"x": 4, "y": 2, "length": 1}])
        self.assertIn("longest matching run: 1,1,2", self._run(
            path, "1", "1", "--width", "4", "--height", "2", "--find-color",
            "0a141e", "--longest-match-run").stdout)

    def test_edge_flush_empty_and_summary_only_collection(self):
        _, encoded = rgb_image(3, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "full.png", encoded)
        result = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--find-color", "010203", "--longest-match-run", "--json")
        self.assertEqual(json.loads(result.stdout)["match"]["longest_run"],
                         {"x": 0, "y": 0, "length": 3})
        empty = self._run(path, "0", "0", "--find-color", "ffffff",
                          "--longest-match-run", "--json")
        self.assertIsNone(json.loads(empty.stdout)["match"]["longest_run"])
        from tools.sample_match_runs import MatchRuns
        collector = MatchRuns(0, 0, 100, 1, horizontal=True, vertical=False,
                               summarize=True, collect_runs=False)
        for x in range(100):
            collector.observe(x, 0, x % 2 == 0)
        collector.finish()
        self.assertEqual(collector.runs, [])
        self.assertEqual(collector.longest_run, {"x": 0, "y": 0, "length": 1})

    def test_crossed_summary_and_opposite_axis_list_modes(self):
        target = (10, 20, 30)
        cells = {(1, 1), (2, 1), (3, 1), (2, 2), (2, 3), (3, 3)}
        _, encoded = rgb_image(6, 5, lambda x, y: target if (x, y) in cells else (0, 0, 0))
        path = self._write(self._tmp_dir(), "crossed.png", encoded)
        horizontal = self._run(path, "1", "1", "--width", "4", "--height", "3",
                               "--find-color", "0a141e", "--longest-match-run",
                               "--match-column-runs", "--json")
        match = json.loads(horizontal.stdout)["match"]
        self.assertEqual(match["longest_run"], {"x": 1, "y": 1, "length": 3})
        self.assertEqual(match["column_runs"], [
            {"x": 1, "y": 1, "length": 1}, {"x": 2, "y": 1, "length": 3},
            {"x": 3, "y": 1, "length": 1}, {"x": 3, "y": 3, "length": 1}])
        self.assertNotIn("runs", match)
        self.assertNotIn("longest_column_run", match)

        vertical = self._run(path, "1", "1", "--width", "4", "--height", "3",
                             "--find-color", "0a141e", "--match-runs",
                             "--longest-match-column-run", "--json")
        match = json.loads(vertical.stdout)["match"]
        self.assertEqual(match["longest_column_run"], {"x": 2, "y": 1, "length": 3})
        self.assertEqual(match["runs"], [
            {"x": 1, "y": 1, "length": 3}, {"x": 2, "y": 2, "length": 1},
            {"x": 2, "y": 3, "length": 2}])
        self.assertNotIn("column_runs", match)
        self.assertNotIn("longest_run", match)

    def test_requires_find_color_help_and_direct_script(self):
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--longest-match-run")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--longest-match-run", self._run("--help").stdout)
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--longest-match-run", "--json")
        self.assertEqual(json.loads(direct.stdout)["match"]["longest_run"],
                         {"x": 0, "y": 0, "length": 1})


if __name__ == "__main__":
    import unittest

    unittest.main()
