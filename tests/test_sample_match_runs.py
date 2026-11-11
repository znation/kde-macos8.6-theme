"""Tests for contiguous color-search match segments."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_search


class TestSampleMatchRuns(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_runs_cover_tolerance_matches_and_stop_at_rows(self):
        rows = [
            [(8, 8, 8), (10, 20, 30), (11, 20, 30), (0, 0, 0), (10, 20, 30)],
            [(0, 0, 0), (0, 0, 0), (10, 20, 30), (10, 20, 30), (0, 0, 0)],
            [(0, 0, 0)] * 5,
        ]
        _, encoded = rgb_image(7, 4, lambda x, y: rows[y - 1][x - 1]
                               if 1 <= x <= 5 and 1 <= y <= 3 else (99, 99, 99))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        args = (path, "1", "1", "--width", "5", "--height", "3", "--find-color", "0a141e",
                "--color-tolerance", "1", "--match-runs")
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-pixels", "1", "--match-fraction", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        expected = [
            {"x": 2, "y": 1, "length": 2}, {"x": 5, "y": 1, "length": 1},
            {"x": 3, "y": 2, "length": 2},
        ]
        self.assertEqual(match["runs"], expected)
        self.assertEqual(sum(run["length"] for run in expected), match["count"])
        self.assertEqual((match["count"], len(match["pixels"]), match["fraction"]), (5, 1, 1 / 3))
        read.assert_called_once()
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn('matching runs: [{"x":2,"y":1,"length":2},{"x":5,"y":1,"length":1},{"x":3,"y":2,"length":2}]', text.stdout)
        ordinary = self._run(path, "1", "1", "--width", "5", "--height", "3", "--find-color", "0a141e", "--json")
        self._assert_success(ordinary)
        self.assertNotIn("runs", json.loads(ordinary.stdout)["match"])

    def test_empty_full_single_cell_and_direct_script(self):
        _, encoded = rgb_image(3, 2, lambda x, y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "full.png", encoded)
        full = self._run(path, "0", "0", "--width", "3", "--height", "2", "--find-color", "010203", "--match-runs", "--json")
        self._assert_success(full)
        self.assertEqual(json.loads(full.stdout)["match"]["runs"], [
            {"x": 0, "y": 0, "length": 3}, {"x": 0, "y": 1, "length": 3}])
        empty = self._run(path, "0", "0", "--width", "3", "--height", "2", "--find-color", "ffffff", "--match-runs", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["match"]["runs"], [])
        one = self._run(path, "2", "1", "--find-color", "010203", "--match-runs", "--json")
        self._assert_success(one)
        self.assertEqual(json.loads(one.stdout)["match"]["runs"], [{"x": 2, "y": 1, "length": 1}])
        direct = self._run_script(path, "0", "0", "--width", "3", "--find-color", "010203", "--match-runs", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["runs"][0]["length"], 3)
        column = self._run(path, "1", "0", "--height", "2", "--find-color", "010203", "--match-runs", "--json")
        self._assert_success(column)
        self.assertEqual(json.loads(column.stdout)["match"]["runs"], [
            {"x": 1, "y": 0, "length": 1}, {"x": 1, "y": 1, "length": 1}])

    def test_alpha_filter_and_validation_precede_reads(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1,
            [bytes((1, 2, 3, 0, 1, 2, 3, 255, 1, 2, 3, 0))], color_type=6))
        result = self._run(path, "0", "0", "--width", "3", "--find-color", "010203",
                           "--match-alpha", "0", "--match-runs", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"]["runs"], [
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 1}])
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb_image(2, 1, lambda x, y: (1, 2, 3))[1])
        fallback = self._run(opaque, "0", "0", "--width", "2", "--find-color", "010203",
                             "--match-alpha", "255", "--match-runs", "--json")
        self._assert_success(fallback)
        self.assertEqual(json.loads(fallback.stdout)["match"]["runs"], [
            {"x": 0, "y": 0, "length": 2}])
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run("missing.png", "0", "0", "--match-runs")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")

    def test_combined_intervals_flush_crop_edges_and_use_one_full_traversal(self):
        target = (10, 20, 30)
        rows = [
            [(11, 20, 30), target, target],
            [target, (0, 0, 0), target],
            [target, target, (9, 20, 30)],
        ]
        encoded = make_png(5, 5, [bytes(
            channel for x in range(5) for channel in (
                (*rows[y - 2][x - 1], 255) if 1 <= x <= 3 and 2 <= y <= 4
                else (0, 0, 0, 255))) for y in range(1, 6)], color_type=6)
        path = self._write(self._tmp_dir(), "crop.png", encoded)
        args = (path, "1", "1", "--width", "3", "--height", "3", "--find-color",
                "0a141e", "--color-tolerance", "1", "--match-alpha", "255",
                "--match-runs", "--match-column-runs", "--match-pixels", "1")
        with mock.patch.object(sample_report_search, "positioned_region_pixels",
                               wraps=sample_report_search.positioned_region_pixels) as pixels:
            result = self._run(*args, "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["count"], 8)
        self.assertEqual(match["pixels"], [{"x": 1, "y": 1}])
        self.assertEqual(match["runs"], [
            {"x": 1, "y": 1, "length": 3}, {"x": 1, "y": 2, "length": 1},
            {"x": 3, "y": 2, "length": 1}, {"x": 1, "y": 3, "length": 3}])
        self.assertEqual(match["column_runs"], [
            {"x": 1, "y": 1, "length": 3}, {"x": 2, "y": 1, "length": 1},
            {"x": 2, "y": 3, "length": 1}, {"x": 3, "y": 1, "length": 3}])
        pixels.assert_called_once()
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn('matching runs: ' + json.dumps(match["runs"], separators=(",", ":")), text.stdout)
        self.assertIn('matching column runs: ' + json.dumps(match["column_runs"], separators=(",", ":")), text.stdout)
        direct = self._run_script(path, *args[1:], "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"], match)


if __name__ == "__main__":
    import unittest

    unittest.main()
