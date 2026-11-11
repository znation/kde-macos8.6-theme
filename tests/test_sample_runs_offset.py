"""Tests for paging through eligible scanline runs."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleRunsOffset(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_pages_after_filters_and_counts_skipped_and_trailing(self):
        colors = [(1, 0, 0), (1, 0, 0), (2, 0, 0), (2, 0, 0),
                  (1, 0, 0), (3, 0, 0), (3, 0, 0), (3, 0, 0)]
        _, data = rgb_image(4, 2, lambda x, y: colors[y * 4 + x])
        path = self._write(self._tmp_dir(), "runs.png", data)
        base = (path, "0", "0", "--width", "4", "--height", "2", "--runs",
                "--run-axis", "horizontal", "--max-runs", "2", "--run-offset", "1")
        report = json.loads(self._run(*base, "--run-count", "--scanline-run-counts",
                                      "--longest-run", "--json").stdout)
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in report["runs"]],
                         [(2, 0, 2), (0, 1, 1)])
        self.assertEqual((report["run_offset"], report["omitted_runs"]), (1, 2))
        self.assertEqual((report["run_count"], report["scanline_run_counts"],
                          report["longest_run"]["length"]), (4, [2, 2], 3))
        excluded = json.loads(self._run(path, "0", "0", "--width", "4", "--height", "2",
                                        "--runs", "--run-axis", "horizontal", "--max-runs", "1",
                                        "--run-offset", "1", "--exclude-run-color", "010000",
                                        "--json").stdout)
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in excluded["runs"]], [(1, 1, 3)])
        self.assertEqual(excluded["omitted_runs"], 1)
        empty_window = json.loads(self._run(path, "0", "0", "--width", "4", "--height", "2",
                                            "--runs", "--run-axis", "horizontal", "--max-runs", "1",
                                            "--run-offset", "1",
                                            "--min-run-length", "4", "--max-run-length", "9",
                                            "--json").stdout)
        self.assertEqual((empty_window["runs"], empty_window["omitted_runs"]), ([], 0))

    def test_past_end_empty_text_and_zero_offset(self):
        _, data = rgb_image(2, 1, lambda x, y: (x, 0, 0))
        path = self._write(self._tmp_dir(), "runs.png", data)
        base = (path, "0", "0", "--width", "2", "--runs", "--max-runs", "1")
        report = json.loads(self._run(*base, "--run-offset", "4", "--json").stdout)
        self.assertEqual((report["runs"], report["omitted_runs"], report["run_offset"]), ([], 2, 4))
        page = self._run(*base, "--run-offset", "0")
        self.assertIn("run offset: 0", page.stdout)
        self.assertIn("omitted runs: 1", page.stdout)
        zero = json.loads(self._run(*base, "--run-offset", "0", "--json").stdout)
        self.assertEqual((zero["runs"][0]["x"], zero["run_offset"]), (0, 0))

    def test_vertical_crop_and_alpha_runs_share_one_offset(self):
        _, data = rgb_image(3, 3, lambda x, y: ((x + y) % 2, 0, 0))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        vertical = json.loads(self._run(path, "1", "1", "--width", "2", "--height", "2",
                                        "--runs", "--run-axis", "vertical", "--max-runs", "1",
                                        "--run-offset", "1", "--json").stdout)
        self.assertEqual([(r["x"], r["y"]) for r in vertical["runs"]], [(1, 2)])
        self.assertEqual(vertical["omitted_runs"], 3)
        rgba = bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))
        from support.png_fixtures import make_png
        alpha_path = self._write(self._tmp_dir(), "alpha.png",
                                 make_png(3, 1, [rgba], color_type=6))
        alpha = json.loads(self._run(alpha_path, "0", "0", "--width", "3", "--runs",
                                     "--max-runs", "1", "--run-offset", "1", "--alpha",
                                     "--json").stdout)
        self.assertEqual((alpha["runs"][0]["alpha"], alpha["runs"][0]["rgb"],
                          alpha["omitted_runs"]), (128, [1, 2, 3], 2))

    def test_offset_validation_precedes_image_read_and_default_schema(self):
        invalid = self._run("missing.png", "0", "0", "--run-offset", "1")
        self.assertEqual((invalid.returncode, invalid.stdout), (2, ""))
        self.assertIn("--run-offset requires --max-runs", invalid.stderr)
        for value in ("-1", "1.5", "１２"):
            invalid = self._run("missing.png", "0", "0", "--runs", "--max-runs", "1",
                                 "--run-offset", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""), value)


if __name__ == "__main__":
    import unittest

    unittest.main()
