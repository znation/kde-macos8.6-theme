"""Tests the optional longest vertical match summary."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png
from tools import sample


class TestSampleLongestMatchColumnRun(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_crop_ties_alpha_tolerance_and_coordinate_limit(self):
        target = (10, 20, 30)
        cells = {(1, 1), (1, 2), (1, 3), (2, 1), (2, 2),
                 (3, 1), (3, 2), (3, 3)}
        rows = [b"".join(bytes((*target, 0) if (x, y) in cells else
            ((11, 20, 30, 255) if (x, y) == (3, 4) else
             (*target, 255) if (x, y) == (1, 4) else (0, 0, 0, 255)))
            for x in range(5)) for y in range(5)]
        encoded = make_png(5, 5, rows, color_type=6)
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        result = self._run(path, "1", "1", "--width", "3", "--height", "4",
                           "--find-color", "0a141e", "--color-tolerance", "1",
                           "--match-alpha", "0", "--match-pixels", "1",
                           "--longest-match-column-run", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        # Columns x=1 and x=3 tie at length 3; the ascending (x, y) rule keeps x=1
        # even though x=1 closes first at y=4 (the collector test below covers a
        # tie whose higher-x segment closes first).
        self.assertEqual(match["longest_column_run"], {"x": 1, "y": 1, "length": 3})
        self.assertEqual(len(match["pixels"]), 1)

    def test_empty_full_degenerate_and_combined_lists(self):
        encoded = make_png(3, 3, [bytes((1, 2, 3, 255)) * 3 for _ in range(3)], color_type=6)
        path = self._write(self._tmp_dir(), "full.png", encoded)
        full = self._run(path, "0", "0", "--width", "3", "--height", "3",
                         "--find-color", "010203", "--longest-match-column-run", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["longest_column_run"],
                         {"x": 0, "y": 0, "length": 3})
        empty = self._run(path, "0", "0", "--width", "3", "--height", "3",
                          "--find-color", "ffffff", "--longest-match-column-run", "--json")
        self.assertIsNone(json.loads(empty.stdout)["match"]["longest_column_run"])
        combined = self._run(path, "0", "0", "--width", "3", "--height", "3",
                             "--find-color", "010203", "--longest-match-run",
                             "--match-runs", "--match-column-runs",
                             "--longest-match-column-run", "--json")
        match = json.loads(combined.stdout)["match"]
        self.assertEqual(match["longest_run"], {"x": 0, "y": 0, "length": 3})
        self.assertEqual(len(match["runs"]), 3)
        self.assertEqual(len(match["column_runs"]), 3)
        self.assertIn("longest matching column run: 0,0,3", self._run(
            path, "0", "0", "--width", "1", "--height", "3", "--find-color",
            "010203", "--longest-match-column-run").stdout)

    def test_transparency_rgb_tolerance_and_missing_alpha(self):
        rows = [b"".join(bytes(
            (10, 20, 30, 0) if (x, y) == (0, 0) else
            (10, 20, 30, 255) if (x, y) == (1, 0) else
            (99, 99, 99, 0) if (x, y) == (0, 1) else
            (11, 20, 30, 0) if (x, y) == (0, 2) else (0, 0, 0, 255))
            for x in range(2)) for y in range(3)]
        path = self._write(self._tmp_dir(), "predicate.png",
                           make_png(2, 3, rows, color_type=6))
        result = self._run(path, "0", "0", "--width", "2", "--height", "3",
                           "--find-color", "0a141e", "--color-tolerance", "1",
                           "--match-alpha", "0", "--longest-match-column-run", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        # Only the exact pixel and the tolerance-boundary pixel match: the
        # transparent pixel with different RGB and the opaque pixel with the
        # target RGB are both rejected, and the earlier y wins the length-1 tie.
        self.assertEqual(match["count"], 2)
        self.assertEqual(match["longest_column_run"], {"x": 0, "y": 0, "length": 1})
        rgb_path = self._write(self._tmp_dir(), "opaque.png", make_png(1, 3,
            [bytes((1, 2, 3)) for _ in range(3)], color_type=2))
        no_alpha = self._run(rgb_path, "0", "0", "--width", "1", "--height", "3",
                             "--find-color", "010203", "--match-alpha", "255",
                             "--longest-match-column-run", "--json")
        self._assert_success(no_alpha)
        self.assertEqual(json.loads(no_alpha.stdout)["match"]["longest_column_run"],
                         {"x": 0, "y": 0, "length": 3})

    def test_summary_only_tie_order_validation_help_and_direct_script(self):
        from tools.sample_match_runs import MatchRuns
        collector = MatchRuns(0, 0, 3, 5, horizontal=False, vertical=True,
                               summarize=False, collect_runs=False,
                               summarize_columns=True, collect_column_runs=False)
        for y in range(5):
            for x in range(3):
                collector.observe(x, y, (x == 2 and y < 2) or
                                  (x == 0 and 1 <= y < 3))
        collector.finish()
        self.assertEqual(collector.column_runs, [])
        self.assertEqual(collector.longest_column_run, {"x": 0, "y": 1, "length": 2})
        earlier_y = MatchRuns(0, 0, 1, 6, horizontal=False, vertical=True,
                               summarize=False, collect_runs=False,
                               summarize_columns=True, collect_column_runs=False)
        for y in range(6):
            earlier_y.observe(0, y, y in (0, 1, 4, 5))
        earlier_y.finish()
        self.assertEqual(earlier_y.longest_column_run,
                         {"x": 0, "y": 0, "length": 2})
        encoded = make_png(1, 1, [bytes((1, 2, 3, 0))], color_type=6)
        path = self._write(self._tmp_dir(), "one.png", encoded)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--longest-match-column-run")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertIn("--longest-match-column-run", self._run("--help").stdout)
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--longest-match-column-run", "--json")
        self.assertEqual(json.loads(direct.stdout)["match"]["longest_column_run"],
                         {"x": 0, "y": 0, "length": 1})


if __name__ == "__main__":
    import unittest

    unittest.main()
