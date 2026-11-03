"""Tests for the sampler's completed-run maximum length filter."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleRunsMaximumLength(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_filters_completed_runs_in_offset_crop_and_combines_cutoffs(self):
        colors = [(1, 2, 3), (9, 8, 7), (9, 8, 7), (1, 2, 3),
                  (4, 5, 6), (4, 5, 6), (4, 5, 6)]
        _, data = rgb_image(9, 1, lambda x, y: colors[x - 1] if 1 <= x <= 7 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "runs.png", data)
        base = (path, "1", "0", "--width", "7", "--runs")
        result = self._run(*base, "--max-run-length", "2", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 1, "y": 0, "length": 1, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 2, "y": 0, "length": 2, "rgb": [9, 8, 7], "hex": "#090807"},
            {"x": 4, "y": 0, "length": 1, "rgb": [1, 2, 3], "hex": "#010203"},
        ])
        combined = self._run(*base, "--min-run-length", "2", "--max-run-length", "2", "--json")
        self.assertEqual([r["length"] for r in json.loads(combined.stdout)["runs"]], [2])
        empty = self._run(*base, "--min-run-length", "3", "--max-run-length", "2", "--json")
        self.assertEqual(json.loads(empty.stdout)["runs"], [])
        text = self._run(*base, "--max-run-length", "2")
        self.assertEqual(text.stdout.splitlines(), [f"image: {path}  9x1", "region (1, 0) 7x1:",
                         "axis: horizontal", "(1, 0): 1,2,3  #010203  length=1",
                         "(2, 0): 9,8,7  #090807  length=2", "(4, 0): 1,2,3  #010203  length=1"])

    def test_help_default_and_direct_script_parity(self):
        self.assertIn("--max-run-length N", self._run("--help").stdout)
        _, data = rgb_image(3, 1, lambda x, y: (1, 2, 3) if x < 2 else (4, 5, 6))
        path = self._write(self._tmp_dir(), "direct.png", data)
        base = (path, "0", "0", "--width", "3", "--runs", "--json")
        default, large = self._run(*base), self._run(*base, "--max-run-length", "3")
        self.assertEqual((large.returncode, large.stdout, large.stderr),
                         (default.returncode, default.stdout, default.stderr))
        filtered = self._run(*base, "--max-run-length", "1")
        direct = self._run_script(*base, "--max-run-length", "1")
        self.assertEqual((direct.returncode, direct.stdout, direct.stderr),
                         (filtered.returncode, filtered.stdout, filtered.stderr))
        for value in ("0", "-1", "１２", "1.5", "bad"):
            invalid = self._run("missing.png", "0", "0", "--runs", "--max-run-length", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""), value)
        missing = self._run("missing.png", "0", "0", "--runs", "--max-run-length")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))


if __name__ == "__main__":
    import unittest

    unittest.main()
