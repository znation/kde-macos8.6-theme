"""Tests for limiting displayed scanline runs."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleRunsLimit(CliTestCase):
    """The scanline runs report's ``--max-runs`` page cap."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_global_prefix_filters_summaries_and_text(self):
        colors = [(1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
                  (1, 1, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3)]
        _, data = rgb_image(4, 2, lambda x, y: colors[y * 4 + x])
        path = self._write(self._tmp_dir(), "runs.png", data)
        base = (path, "0", "0", "--width", "4", "--height", "2", "--runs",
                "--run-axis", "horizontal", "--max-runs", "2")
        result = self._run(*base, "--run-count", "--scanline-run-counts", "--longest-run", "--json")
        report = json.loads(result.stdout)
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in report["runs"]],
                         [(0, 0, 2), (2, 0, 2)])
        self.assertEqual((report["omitted_runs"], report["run_count"],
                          report["scanline_run_counts"], report["longest_run"]["length"]),
                         (2, 4, [2, 2], 3))
        third = json.loads(self._run(*base[:-1], "3", "--json").stdout)
        self.assertEqual([(r["x"], r["y"]) for r in third["runs"]],
                         [(0, 0), (2, 0), (0, 1)])
        self.assertEqual(third["omitted_runs"], 1)
        complete = json.loads(self._run(*base[:-1], "4", "--json").stdout)
        self.assertEqual(complete["omitted_runs"], 0)
        text = self._run(*base)
        self.assertEqual(text.stdout.splitlines()[-1], "omitted runs: 2")

    def test_limit_spans_vertical_scans_and_eligible_filters(self):
        colors = [(1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
                  (1, 1, 1), (3, 3, 3), (3, 3, 3), (3, 3, 3)]
        _, data = rgb_image(4, 2, lambda x, y: colors[y * 4 + x])
        path = self._write(self._tmp_dir(), "vertical.png", data)
        vertical = self._run(path, "1", "0", "--width", "2", "--height", "2",
                             "--runs", "--run-axis", "vertical", "--max-runs", "2", "--json")
        report = json.loads(vertical.stdout)
        self.assertEqual([(r["x"], r["y"]) for r in report["runs"]], [(1, 0), (1, 1)])
        self.assertEqual(report["omitted_runs"], 2)
        excluded = self._run(path, "0", "0", "--width", "4", "--height", "2", "--runs",
                             "--run-axis", "horizontal", "--exclude-run-color", "010101",
                             "--max-runs", "1", "--json")
        self.assertEqual([r["rgb"] for r in json.loads(excluded.stdout)["runs"]], [[2, 2, 2]])
        self.assertEqual(json.loads(excluded.stdout)["omitted_runs"], 1)
        empty = self._run(path, "0", "0", "--width", "4", "--height", "2", "--runs",
                          "--run-axis", "horizontal", "--run-color", "ABCDEF",
                          "--max-runs", "1", "--json")
        self.assertEqual(json.loads(empty.stdout)["omitted_runs"], 0)
        empty_cutoff = self._run(path, "0", "0", "--width", "4", "--height", "2", "--runs",
                                 "--run-axis", "horizontal", "--min-run-length", "4",
                                 "--max-run-length", "9", "--max-runs", "1", "--json")
        self.assertEqual(json.loads(empty_cutoff.stdout)["omitted_runs"], 0)

    def test_alpha_groups_consume_individual_slots(self):
        row = bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, [row], color_type=6))
        base = (path, "0", "0", "--width", "3", "--runs", "--max-runs", "1", "--json")
        rgb = json.loads(self._run(*base).stdout)
        rgba = json.loads(self._run(*base[:-1], "--alpha", "--json").stdout)
        self.assertEqual((len(rgb["runs"]), rgb["omitted_runs"]), (1, 1))
        self.assertEqual((len(rgba["runs"]), rgba["omitted_runs"], rgba["runs"][0]["alpha"]),
                         (1, 2, 0))

    def test_limit_validation_and_default_schema(self):
        _, data = rgb_image(2, 1, lambda x, y: (x, 0, 0))
        path = self._write(self._tmp_dir(), "small.png", data)
        normal = self._run(path, "0", "0", "--width", "2", "--runs", "--json")
        self.assertNotIn("omitted_runs", json.loads(normal.stdout))
        for value in ("0", "-1", "1.5", "１２"):
            invalid = self._run("missing.png", "0", "0", "--runs", "--max-runs", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""), value)


if __name__ == "__main__":
    import unittest

    unittest.main()
