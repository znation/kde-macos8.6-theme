"""Tests for excluding named RGB colors from sampler run reports."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleRunsExclusions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_exclusion_follows_segmentation_and_length_filters(self):
        a, b, c = (1, 2, 3), (9, 8, 7), (4, 5, 6)
        colors = [a, a, b, b, b, a, c, c]
        _, data = rgb_image(10, 3, lambda x, y: colors[x - 2] if y == 1 and 2 <= x < 10 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "exclusions.png", data)
        base = (path, "2", "1", "--width", "8", "--runs")
        excluded = self._run(*base, "--exclude-run-color", "#090807", "--json")
        records = json.loads(excluded.stdout)["runs"]
        self.assertEqual([(r["x"], r["y"], r["length"], r["rgb"]) for r in records], [
            (2, 1, 2, [1, 2, 3]), (7, 1, 1, [1, 2, 3]), (8, 1, 2, [4, 5, 6]),
        ])
        minimum = self._run(*base, "--exclude-run-color", "090807", "--min-run-length", "2", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(minimum.stdout)["runs"]], [(2, 2), (8, 2)])
        maximum = self._run(*base, "--exclude-run-color", "090807", "--max-run-length", "1", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(maximum.stdout)["runs"]], [(7, 1)])
        both = self._run(*base, "--run-color", "010203", "--run-color", "090807",
                         "--exclude-run-color", "090807", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(both.stdout)["runs"]], [(2, 2), (7, 1)])
        absent = self._run(*base, "--exclude-run-color", "abcdef", "--json")
        plain = self._run(*base, "--json")
        self.assertEqual(json.loads(absent.stdout)["runs"], json.loads(plain.stdout)["runs"])
        all_excluded = self._run(*base, "--exclude-run-color", "010203", "--exclude-run-color", "090807",
                                 "--exclude-run-color", "040506", "--json")
        self.assertEqual(json.loads(all_excluded.stdout)["runs"], [])
        empty_text = self._run(*base, "--exclude-run-color", "010203", "--exclude-run-color", "090807",
                               "--exclude-run-color", "040506")
        self.assertEqual(empty_text.stdout.splitlines(), [
            f"image: {path}  10x3", "region (2, 1) 8x1:", "axis: horizontal",
        ])
        normalized = self._run(*base, "--exclude-run-color", "090807", "--exclude-run-color", "#090807", "--json")
        self.assertEqual(json.loads(normalized.stdout)["runs"], records)

    def test_rgb_exclusion_ignores_alpha_and_preserves_alpha_segmentation(self):
        rgba = bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))
        path = self._write(self._tmp_dir(), "alpha.png", make_png(3, 1, [rgba], color_type=6))
        base = (path, "0", "0", "--width", "3", "--runs")
        rgb = self._run(*base, "--exclude-run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["length"], r["rgb"]) for r in json.loads(rgb.stdout)["runs"]],
                         [(2, 1, [4, 5, 6])])
        alpha = self._run(*base, "--alpha", "--exclude-run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["length"], r["alpha"]) for r in json.loads(alpha.stdout)["runs"]],
                         [(2, 1, 255)])
        absent = self._run(*base, "--alpha", "--exclude-run-color", "abcdef", "--json")
        self.assertEqual([(r["length"], r["alpha"]) for r in json.loads(absent.stdout)["runs"]],
                         [(1, 0), (1, 128), (1, 255)])

    def test_vertical_scanlines_keep_separate_runs_and_coordinates(self):
        a, b = (1, 2, 3), (9, 8, 7)
        pixels = {(1, 1): a, (1, 2): a, (1, 3): b, (2, 1): b, (2, 2): a, (2, 3): a}
        _, data = rgb_image(4, 5, lambda x, y: pixels.get((x, y), (0, 0, 0)))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        result = self._run(path, "1", "1", "--width", "2", "--height", "3", "--runs",
                           "--run-axis", "vertical", "--exclude-run-color", "090807", "--json")
        self.assertEqual([(r["x"], r["y"], r["length"], r["rgb"]) for r in json.loads(result.stdout)["runs"]], [
            (1, 1, 2, [1, 2, 3]), (2, 2, 2, [1, 2, 3]),
        ])

    def test_validation_help_text_and_script_parity(self):
        parser = build_parser()
        self.assertIsNone(parser.parse_args(("image.png", "0", "0", "--runs")).excluded_run_colors)
        self.assertIn("--exclude-run-color RRGGBB", parser.format_help())
        for value in ("12345", "gggggg", "#1234567", " 010203"):
            with mock.patch.object(sample.os, "open") as open_image:
                invalid = self._run("missing.png", "0", "0", "--runs", "--exclude-run-color", value)
            self.assertEqual((invalid.returncode, invalid.stdout), (2, ""), value)
            open_image.assert_not_called()
        _, data = rgb_image(3, 1, lambda x, y: ((1, 2, 3), (9, 8, 7), (4, 5, 6))[x])
        path = self._write(self._tmp_dir(), "parity.png", data)
        args = (path, "0", "0", "--width", "3", "--runs", "--exclude-run-color", "090807")
        package, direct = self._run(*args), self._run_script(*args)
        self.assertEqual((package.returncode, package.stdout, package.stderr),
                         (direct.returncode, direct.stdout, direct.stderr))
        self.assertEqual(package.stdout.splitlines()[-2:], [
            "(0, 0): 1,2,3  #010203  length=1", "(2, 0): 4,5,6  #040506  length=1",
        ])


if __name__ == "__main__":
    import unittest

    unittest.main()
