"""Tests for selecting named RGB colors in sampler run reports."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleRunsColors(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_color_selection_follows_segmentation_and_cutoffs(self):
        colors = [(1, 2, 3)] * 2 + [(9, 8, 7)] * 3 + [(1, 2, 3)] + [(4, 5, 6)] * 2
        _, data = rgb_image(10, 3, lambda x, y: colors[x - 2] if y == 1 and 2 <= x < 10 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "colors.png", data)
        base = (path, "2", "1", "--width", "8", "--runs")
        result = self._run(*base, "--run-color", "#010203", "--run-color", "040506", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)["runs"]
        self.assertEqual([(r["x"], r["y"], r["length"], r["rgb"]) for r in records], [
            (2, 1, 2, [1, 2, 3]), (7, 1, 1, [1, 2, 3]), (8, 1, 2, [4, 5, 6]),
        ])
        only_a = self._run(*base, "--run-color", "010203", "--min-run-length", "2", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(only_a.stdout)["runs"]], [(2, 2)])
        singleton = self._run(*base, "--run-color", "010203", "--max-run-length", "1", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(singleton.stdout)["runs"]], [(7, 1)])
        absent = self._run(*base, "--run-color", "abcdef", "--json")
        self.assertEqual(json.loads(absent.stdout)["runs"], [])
        all_colors = self._run(*base, "--run-color", "010203", "--run-color", "090807",
                               "--run-color", "040506", "--json")
        unfiltered = self._run(*base, "--json")
        self.assertEqual(json.loads(all_colors.stdout)["runs"], json.loads(unfiltered.stdout)["runs"])
        _, data = rgb_image(4, 2, lambda x, y: (1, 2, 3))
        rows_path = self._write(self._tmp_dir(), "rows.png", data)
        rows = self._run(rows_path, "0", "0", "--width", "4", "--height", "2", "--runs",
                         "--run-axis", "horizontal", "--run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in json.loads(rows.stdout)["runs"]],
                         [(0, 0, 4), (0, 1, 4)])

    def test_alpha_grouping_selection_and_vertical_scanlines(self):
        rgba = bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))
        alpha_path = self._write(self._tmp_dir(), "alpha.png", make_png(3, 1, [rgba], color_type=6))
        rgb = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["length"]) for r in json.loads(rgb.stdout)["runs"]], [(0, 2)])
        alpha = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--alpha",
                          "--run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["length"], r["alpha"]) for r in json.loads(alpha.stdout)["runs"]],
                         [(0, 1, 0), (1, 1, 128)])
        short = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--alpha",
                          "--run-color", "010203", "--min-run-length", "2", "--json")
        self.assertEqual(json.loads(short.stdout)["runs"], [])
        _, data = rgb_image(2, 1, lambda x, y: (7, 8, 9))
        opaque_path = self._write(self._tmp_dir(), "opaque.png", data)
        opaque = self._run(opaque_path, "0", "0", "--width", "2", "--runs", "--alpha",
                           "--run-color", "070809", "--json")
        self.assertEqual([(r["x"], r["length"], r["alpha"]) for r in json.loads(opaque.stdout)["runs"]],
                         [(0, 2, 255)])
        _, data = rgb_image(5, 5, lambda x, y: (1, 2, 3) if x == 2 and y in (1, 2, 4) else (0, 0, 0))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        vertical = self._run(path, "2", "1", "--height", "4", "--runs", "--run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in json.loads(vertical.stdout)["runs"]],
                         [(2, 1, 2), (2, 4, 1)])

    def test_rectangular_scanlines_keep_coordinates_order_and_boundaries(self):
        a, b, c = (1, 2, 3), (9, 8, 7), (4, 5, 6)
        pixels = {
            (1, 1): a, (2, 1): b, (3, 1): c,
            (1, 2): a, (2, 2): a, (3, 2): c,
        }
        _, data = rgb_image(5, 4, lambda x, y: pixels.get((x, y), (0, 0, 0)))
        path = self._write(self._tmp_dir(), "rectangle.png", data)
        base = (path, "1", "1", "--width", "3", "--height", "2", "--runs")
        horizontal = self._run(*base, "--run-axis", "horizontal", "--run-color", "010203",
                               "--run-color", "040506", "--json")
        records = json.loads(horizontal.stdout)["runs"]
        self.assertEqual([(r["x"], r["y"], r["length"], r["rgb"]) for r in records], [
            (1, 1, 1, [1, 2, 3]), (3, 1, 1, [4, 5, 6]),
            (1, 2, 2, [1, 2, 3]), (3, 2, 1, [4, 5, 6]),
        ])
        vertical = self._run(*base, "--run-axis", "vertical", "--run-color", "010203",
                             "--run-color", "040506", "--json")
        records = json.loads(vertical.stdout)["runs"]
        self.assertEqual([(r["x"], r["y"], r["length"], r["rgb"]) for r in records], [
            (1, 1, 2, [1, 2, 3]), (2, 2, 1, [1, 2, 3]), (3, 1, 2, [4, 5, 6]),
        ])
        inferred = self._run(path, "1", "1", "--height", "2", "--runs", "--run-color", "010203", "--json")
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in json.loads(inferred.stdout)["runs"]],
                         [(1, 1, 2)])
        singleton = self._run(path, "3", "2", "--runs", "--run-axis", "vertical",
                              "--run-color", "040506", "--json")
        self.assertEqual([(r["x"], r["y"], r["length"]) for r in json.loads(singleton.stdout)["runs"]],
                         [(3, 2, 1)])

    def test_duplicate_names_absence_and_alpha_minimum(self):
        _, data = rgb_image(3, 1, lambda x, y: [(10, 2, 3), (4, 5, 6), (10, 2, 3)][x])
        path = self._write(self._tmp_dir(), "selection.png", data)
        base = (path, "0", "0", "--width", "3", "--runs")
        selected = self._run(*base, "--run-color", "0A0203", "--run-color", "#0a0203",
                             "--run-color", "040506", "--json")
        plain = self._run(*base, "--json")
        self.assertEqual(json.loads(selected.stdout)["runs"], json.loads(plain.stdout)["runs"])
        absent = self._run(*base, "--run-color", "abcdef")
        self.assertEqual(absent.stdout.splitlines(), [
            f"image: {path}  3x1", "region (0, 0) 3x1:", "axis: horizontal",
        ])

        rgba = bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))
        alpha_path = self._write(self._tmp_dir(), "alpha-cutoff.png",
                                 make_png(3, 1, [rgba], color_type=6))
        filtered = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--alpha",
                             "--run-color", "010203", "--min-run-length", "2", "--json")
        self.assertEqual(json.loads(filtered.stdout)["runs"], [])
        opaque = self._run(*base, "--alpha", "--json")
        self.assertEqual([r["alpha"] for r in json.loads(opaque.stdout)["runs"]], [255, 255, 255])

    def test_validation_default_text_and_direct_script(self):
        parser = build_parser()
        self.assertIsNone(parser.parse_args(("image.png", "0", "0", "--runs")).run_colors)
        self.assertIn("--run-color RRGGBB", parser.format_help())
        for value in ("12345", "gggggg", "#1234567", " 010203", "010203 "):
            result = self._run("missing.png", "0", "0", "--runs", "--run-color", value)
            self.assertEqual((result.returncode, result.stdout), (2, ""), value)
        with mock.patch.object(sample.os, "open") as open_image:
            missing = self._run("missing.png", "0", "0", "--runs", "--run-color")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        open_image.assert_not_called()
        _, data = rgb_image(2, 1, lambda x, y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "parity.png", data)
        args = (path, "0", "0", "--width", "2", "--runs", "--run-color", "010203")
        package, direct = self._run(*args), self._run_script(*args)
        self.assertEqual((package.returncode, package.stdout, package.stderr),
                         (direct.returncode, direct.stdout, direct.stderr))
        text = self._run(*args)
        self.assertEqual(text.stdout.splitlines()[-1], "(0, 0): 1,2,3  #010203  length=2")


if __name__ == "__main__":
    import unittest

    unittest.main()
