"""The vertical match-run collector retains only the requested page."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_match_runs import _ColumnRuns


class TestColumnRunsStorage(unittest.TestCase):

    def test_capped_collector_bounds_retained_runs_during_scan_and_final_flush(self):
        collector = _ColumnRuns(0, 0, 3, 6, run_limit=2, run_offset=1)
        matches = {
            0: {0, 2, 3},
            1: {0, 1, 2, 5},
            2: set(),
        }
        for column in range(3):
            for row in range(6):
                collector.observe(column, row, row in matches[column])
                assert len(collector.runs) <= 2

        runs = collector.finish()

        # Column-major completion order: (0,0,1), (0,2,2), (1,0,3), (1,5,1).
        assert runs == [{"x": 0, "y": 2, "length": 2},
                        {"x": 1, "y": 0, "length": 3}]
        assert collector.eligible_run_count == 4
        assert len(collector.runs) == 2

    def test_offset_beyond_the_eligible_total_returns_an_empty_page(self):
        collector = _ColumnRuns(0, 0, 3, 6, run_limit=2, run_offset=5)
        matches = {
            0: {0, 2, 3},
            1: {0, 1, 2, 5},
            2: set(),
        }
        for column in range(3):
            for row in range(6):
                collector.observe(column, row, row in matches[column])

        assert collector.finish() == []
        assert collector.eligible_run_count == 4

    def test_cutoffs_and_absence_return_empty_pages_with_correct_totals(self):
        skip_long = _ColumnRuns(0, 0, 1, 4, min_run_length=3)
        match = [True, True, False, False]
        for row in range(4):
            skip_long.observe(0, row, match[row])
        assert skip_long.finish() == []
        assert skip_long.eligible_run_count == 0

        contradictory = _ColumnRuns(0, 0, 1, 4,
                                    min_run_length=3, max_run_length=2)
        for row in range(4):
            contradictory.observe(0, row, True)
            assert len(contradictory.runs) == 0
        assert contradictory.finish() == []
        assert contradictory.eligible_run_count == 0

        absent = _ColumnRuns(0, 0, 2, 4, run_limit=2)
        for column in range(2):
            for row in range(4):
                absent.observe(column, row, False)
        assert absent.finish() == []
        assert absent.eligible_run_count == 0


class TestCappedColumnRunsStorage(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def setUp(self):
        super().setUp()
        target = (10, 20, 30)
        positions = {(0, 0), (0, 2), (0, 3), (0, 5), (0, 6), (0, 7), (1, 8)}
        _, encoded = rgb_image(4, 11, lambda x, y: target
                               if (x - 2, y - 1) in positions else (0, 0, 0))
        self.path = self._write(self._tmp_dir(), "columns.png", encoded)
        self.options = ("--find-color", "0a141e", "--match-column-runs",
                        "--match-column-run-count", "--longest-match-column-run")

    def _capped(self, extra=("--min-match-column-run-length", "2",
                             "--match-column-run-offset", "1",
                             "--max-match-column-runs", "1"), json=True):
        return self._run(self.path, "2", "1", "--width", "2", "--height", "9",
                         *self.options, *extra, *(("--json",) if json else ()))

    def test_pinned_crop_pages_after_filters_with_bounded_retained_storage(self):
        capped = self._capped()
        self._assert_success(capped)
        match = json.loads(capped.stdout)["match"]
        self.assertEqual(match["column_runs"], [{"x": 2, "y": 6, "length": 3}])
        self.assertEqual((match["omitted_column_runs"],
                          match["column_run_offset"]), (1, 1))

        uncapped = self._capped(extra=())
        self._assert_success(uncapped)
        uncapped_match = json.loads(uncapped.stdout)["match"]
        self.assertNotIn("omitted_column_runs", uncapped_match)
        self.assertEqual(uncapped_match["column_runs"], [
            {"x": 2, "y": 1, "length": 1},
            {"x": 2, "y": 3, "length": 2},
            {"x": 2, "y": 6, "length": 3},
            {"x": 3, "y": 9, "length": 1},
        ])
        for key in ("count", "column_run_count", "longest_column_run"):
            self.assertEqual(match[key], uncapped_match[key])

    def test_capped_text_pages_like_json_and_keeps_summaries(self):
        text = self._capped(json=False)
        self._assert_success(text)
        self.assertIn("matching column run count: 4\n"
                      "matching column run offset: 1\n"
                      "matching column runs: [{\"x\":2,\"y\":6,\"length\":3}]\n"
                      "omitted matching column runs: 1\n"
                      "longest matching column run: 2,6,3\n", text.stdout)
        offset_json = self._run(self.path, "2", "1", "--width", "2",
                                "--height", "9", *self.options,
                                "--max-match-column-runs", "2", "--json")
        self._assert_success(offset_json)
        self.assertNotIn("column_run_offset",
                         json.loads(offset_json.stdout)["match"])

        direct = self._run_script(self.path, "2", "1", "--width", "2",
                                  "--height", "9", *self.options,
                                  "--min-match-column-run-length", "2",
                                  "--match-column-run-offset", "1",
                                  "--max-match-column-runs", "1", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["column_runs"],
                         [{"x": 2, "y": 6, "length": 3}])

    def test_capped_column_scan_pairs_each_alpha_with_its_own_pixel(self):
        # Alpha 255 sits on the region's left column in both rows: the column
        # scan must serve alphas in its own, column-major order. A row-major
        # alpha iterator consumed column-major would pair (3,0)'s alpha 0 with
        # (2,1) and (2,1)'s alpha 255 with (3,0), splitting the one length-2
        # column run into two length-1 runs in different columns.
        rows = [bytes((0, 0, 0, 0)) * 2 + bytes((4, 5, 6, 255)) + bytes((4, 5, 6, 0)),
                bytes((0, 0, 0, 0)) * 2 + bytes((4, 5, 6, 255)) + bytes((4, 5, 6, 0))]
        path = self._write(self._tmp_dir(), "alpha-columns.png",
                           make_png(4, 2, rows, color_type=6))
        capped = self._run(path, "2", "0", "--width", "2", "--height", "2",
                           "--find-color", "040506", "--match-column-runs",
                           "--match-alpha", "255",
                           "--max-match-column-runs", "2", "--json")
        self._assert_success(capped)
        match = json.loads(capped.stdout)["match"]
        self.assertEqual(match["column_runs"], [{"x": 2, "y": 0, "length": 2}])
        self.assertEqual(match["omitted_column_runs"], 0)
        self.assertEqual(match["count"], 2)


if __name__ == "__main__":
    unittest.main()
