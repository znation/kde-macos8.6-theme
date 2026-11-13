"""Tests for the sampler's completed-run maximum length filter."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleRunsMaximumLength(CliTestCase):
    """The scanline runs report's ``--max-run-length`` cutoff."""

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
        empty = self._run(*base, "--min-run-length", "4", "--max-run-length", "9", "--json")
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

    def test_vertical_rectangle_keeps_columns_and_scanlines_separate(self):
        _, data = rgb_image(4, 4, lambda x, y: (4, 5, 6) if y < 2 else (8, 9, 10))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        # Region (1, 1) 3x3: each column scans y=1..3, giving one length-1 run
        # at the top edge and one length-2 run ending at the bottom edge.
        base = (path, "1", "1", "--width", "3", "--height", "3", "--runs",
                "--run-axis", "vertical", "--json")
        result = self._run(*base, "--max-run-length", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 1, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            {"x": 1, "y": 2, "length": 2, "rgb": [8, 9, 10], "hex": "#08090A"},
            {"x": 2, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            {"x": 2, "y": 2, "length": 2, "rgb": [8, 9, 10], "hex": "#08090A"},
            {"x": 3, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            {"x": 3, "y": 2, "length": 2, "rgb": [8, 9, 10], "hex": "#08090A"},
        ])
        # Adjacent columns hold equal colors yet stay separate scanlines.
        short = self._run(*base, "--max-run-length", "1")
        self.assertEqual(short.returncode, 0, short.stderr)
        self.assertEqual(json.loads(short.stdout)["runs"], [
            {"x": 1, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            {"x": 2, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            {"x": 3, "y": 1, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
        ])

    def test_alpha_runs_split_before_filtering_and_opaque_fallback(self):
        # Six equal-RGB pixels: two with alpha 0, four with alpha 255.
        row = bytes((1, 2, 3, 0)) * 2 + bytes((1, 2, 3, 255)) * 4
        path = self._write(self._tmp_dir(), "alpha.png", make_png(6, 1, [row], color_type=6))
        base = (path, "0", "0", "--width", "6", "--runs", "--json")
        # Without --alpha the different alphas merge into one RGB run of 6;
        # a maximum of 6 keeps it, a maximum of 2 drops it entirely.
        merged = self._run(*base, "--max-run-length", "6")
        self.assertEqual(json.loads(merged.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 6, "rgb": [1, 2, 3], "hex": "#010203"},
        ])
        merged_out = self._run(*base, "--max-run-length", "2")
        self.assertEqual(json.loads(merged_out.stdout)["runs"], [])
        # With --alpha the same pixels split into runs of 2 and 4 before the
        # maximum filter, and RGB is preserved beneath the zero alpha.
        alpha_base = base + ("--alpha",)
        unfiltered = self._run(*alpha_base)
        self.assertEqual(json.loads(unfiltered.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 0},
            {"x": 2, "y": 0, "length": 4, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 255},
        ])
        filtered = self._run(*alpha_base, "--max-run-length", "2")
        self.assertEqual(json.loads(filtered.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 0},
        ])
        # Combining the cutoffs keeps only the opaque length-4 run.
        kept = self._run(*alpha_base, "--min-run-length", "3", "--max-run-length", "4")
        self.assertEqual(json.loads(kept.stdout)["runs"], [
            {"x": 2, "y": 0, "length": 4, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 255},
        ])
        _, opaque_data = rgb_image(2, 1, lambda x, y: (3, 4, 5))
        opaque = self._write(self._tmp_dir(), "opaque.png", opaque_data)
        fallback = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha",
                             "--max-run-length", "2", "--json")
        self.assertEqual(json.loads(fallback.stdout)["runs"][0]["alpha"], 255)

    def test_offset_crop_cutoffs_keep_segment_starts_and_gaps(self):
        colors = [(1, 2, 3), (1, 2, 3), (9, 8, 7), (9, 8, 7), (9, 8, 7),
                  (1, 2, 3), (4, 5, 6), (4, 5, 6)]
        _, data = rgb_image(10, 3, lambda x, y: colors[x - 2] if y == 1 and 2 <= x < 10 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "offset.png", data)
        base = (path, "2", "1", "--width", "8", "--runs")
        result = self._run(*base, "--max-run-length", "2", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 2, "y": 1, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 7, "y": 1, "length": 1, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 8, "y": 1, "length": 2, "rgb": [4, 5, 6], "hex": "#040506"},
        ])
        text = self._run(*base, "--max-run-length", "1")
        self.assertEqual(text.stdout.splitlines(), [f"image: {path}  10x3", "region (2, 1) 8x1:",
                         "axis: horizontal", "(7, 1): 1,2,3  #010203  length=1"])
        exact = self._run(*base, "--min-run-length", "2", "--max-run-length", "2", "--json")
        self.assertEqual([run["length"] for run in json.loads(exact.stdout)["runs"]], [2, 2])
        empty = self._run(*base, "--min-run-length", "4", "--max-run-length", "9", "--json")
        self.assertEqual(json.loads(empty.stdout)["runs"], [])
        empty_text = self._run(*base, "--min-run-length", "4", "--max-run-length", "9")
        self.assertEqual(empty_text.stdout.splitlines(), [f"image: {path}  10x3", "region (2, 1) 8x1:", "axis: horizontal"])

    def test_vertical_rectangle_alpha_and_omitted_parity(self):
        values = [(1, 1, 1), (1, 1, 1), (2, 2, 2), (3, 3, 3), (3, 3, 3)]
        _, data = rgb_image(5, 6, lambda x, y: values[y - 1] if x == 2 and 1 <= y <= 5 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        args = (path, "2", "1", "--height", "5", "--runs", "--max-run-length", "2", "--json")
        result = self._run(*args)
        self.assertEqual(json.loads(result.stdout)["axis"], "vertical")
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 2, "y": 1, "length": 2, "rgb": [1, 1, 1], "hex": "#010101"},
            {"x": 2, "y": 3, "length": 1, "rgb": [2, 2, 2], "hex": "#020202"},
            {"x": 2, "y": 4, "length": 2, "rgb": [3, 3, 3], "hex": "#030303"},
        ])
        long_max = self._run(path, "2", "1", "--height", "5", "--runs", "--max-run-length", "5", "--json")
        no_max = self._run(path, "2", "1", "--height", "5", "--runs", "--json")
        self.assertEqual(json.loads(long_max.stdout)["runs"], json.loads(no_max.stdout)["runs"])
        rgba = bytes((8, 7, 6, 0, 8, 7, 6, 255, 8, 7, 6, 0))
        alpha_path = self._write(self._tmp_dir(), "alpha.png", make_png(3, 1, [rgba], color_type=6))
        rgb = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--max-run-length", "3", "--json")
        self.assertEqual(json.loads(rgb.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 3, "rgb": [8, 7, 6], "hex": "#080706"},
        ])
        alpha = self._run(alpha_path, "0", "0", "--width", "3", "--runs", "--alpha", "--max-run-length", "1", "--json")
        self.assertEqual(json.loads(alpha.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 1, "rgb": [8, 7, 6], "hex": "#080706", "alpha": 0},
            {"x": 1, "y": 0, "length": 1, "rgb": [8, 7, 6], "hex": "#080706", "alpha": 255},
            {"x": 2, "y": 0, "length": 1, "rgb": [8, 7, 6], "hex": "#080706", "alpha": 0},
        ])

    def test_validation_help_parser_default_and_direct_script(self):
        parser = build_parser()
        self.assertIsNone(parser.parse_args(("image.png", "0", "0", "--runs")).max_run_length)
        self.assertIn("--max-run-length N", parser.format_help())
        for value in ("0", "-1", "１２", "1.5", "bad"):
            result = self._run("missing.png", "0", "0", "--runs", "--max-run-length", value)
            self.assertEqual((result.returncode, result.stdout), (2, ""), value)
        missing = self._run("missing.png", "0", "0", "--runs", "--max-run-length")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        _, data = rgb_image(3, 1, lambda x, y: (1, 2, 3) if x < 2 else (4, 5, 6))
        path = self._write(self._tmp_dir(), "direct.png", data)
        args = (path, "0", "0", "--width", "3", "--runs", "--max-run-length", "2", "--json")
        package, direct = self._run(*args), self._run_script(*args)
        self.assertEqual((package.returncode, package.stdout, package.stderr),
                         (direct.returncode, direct.stdout, direct.stderr))


if __name__ == "__main__":
    import unittest

    unittest.main()
