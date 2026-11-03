"""Tests for reference-pixel scanline color runs."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import control_named_png, make_png, rgb_image, solid_rgb
from support.symlink_fixtures import symlinked_repo
from tools import sample


class TestSampleRuns(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        colors = [(1, 2, 3), (1, 2, 3), (9, 8, 7), (1, 2, 3), (4, 5, 6)]
        _, data = rgb_image(6, 5, lambda x, y: colors[x - 1] if y == 2 and 1 <= x <= 5 else (0, 0, 0))
        return self._write(self._tmp_dir(), "runs.png", data)

    def test_horizontal_json_and_text_keep_separated_runs(self):
        path = self._fixture()
        expected = {
            "image": path, "image_width": 6, "image_height": 5,
            "region": {"x": 1, "y": 2, "width": 5, "height": 1},
            "axis": "horizontal",
            "runs": [
                {"x": 1, "y": 2, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
                {"x": 3, "y": 2, "length": 1, "rgb": [9, 8, 7], "hex": "#090807"},
                {"x": 4, "y": 2, "length": 1, "rgb": [1, 2, 3], "hex": "#010203"},
                {"x": 5, "y": 2, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            ],
        }
        result = self._run(path, "1", "2", "--width", "5", "--runs", "--json")
        self._assert_success(result)
        actual = json.loads(result.stdout)
        self.assertEqual(actual, expected)
        self.assertEqual(sum(run["length"] for run in actual["runs"]), 5)
        self.assertTrue(all(a["rgb"] != b["rgb"] for a, b in zip(actual["runs"], actual["runs"][1:])))
        text = self._run(path, "1", "2", "--width", "5", "--runs")
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines(), [
            f"image: {path}  6x5", "region (1, 2) 5x1:", "axis: horizontal",
            "(1, 2): 1,2,3  #010203  length=2", "(3, 2): 9,8,7  #090807  length=1",
            "(4, 2): 1,2,3  #010203  length=1", "(5, 2): 4,5,6  #040506  length=1",
        ])

    def test_vertical_uniform_and_single_pixel_scans(self):
        _, data = rgb_image(4, 4, lambda x, y: (7, 6, 5) if x == 2 else (x, y, 0))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "2", "1", "--height", "3", "--runs", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 2, "y": 1, "length": 3, "rgb": [7, 6, 5], "hex": "#070605"},
        ])
        self.assertEqual(json.loads(result.stdout)["axis"], "vertical")
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        vertical_text = self._run(path, "2", "1", "--height", "3", "--runs")
        self._assert_success(vertical_text)
        self.assertEqual(vertical_text.stdout.splitlines(), [
            f"image: {path}  4x4", "region (2, 1) 1x3:", "axis: vertical",
            "(2, 1): 7,6,5  #070605  length=3",
        ])
        single = self._run(path, "2", "2", "--runs", "--json")
        self._assert_success(single)
        data = json.loads(single.stdout)
        self.assertEqual(data["axis"], "horizontal")
        self.assertEqual(data["runs"][0]["length"], 1)

    def test_minimum_run_length_filters_emitted_runs_and_can_empty_report(self):
        path = self._fixture()
        filtered = self._run(
            path, "1", "2", "--width", "5", "--runs",
            "--min-run-length", "2", "--json",
        )
        self._assert_success(filtered)
        report = json.loads(filtered.stdout)
        self.assertEqual(report["runs"], [
            {"x": 1, "y": 2, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
        ])

        above_all = self._run(
            path, "1", "2", "--width", "5", "--runs",
            "--min-run-length", "6", "--json",
        )
        self._assert_success(above_all)
        self.assertEqual(json.loads(above_all.stdout)["runs"], [])

    def test_rectangular_axes_keep_scanlines_independent(self):
        _, data = rgb_image(4, 3, lambda x, y: (1, 2, 3) if x < 3 else (9, 8, 7))
        path = self._write(self._tmp_dir(), "rectangle.png", data)
        horizontal = self._run(path, "1", "0", "--width", "2", "--height", "3",
                               "--runs", "--run-axis", "horizontal", "--json")
        self._assert_success(horizontal)
        parsed = json.loads(horizontal.stdout)
        self.assertEqual(parsed["axis"], "horizontal")
        self.assertEqual([(run["x"], run["y"], run["length"]) for run in parsed["runs"]],
                         [(1, 0, 2), (1, 1, 2), (1, 2, 2)])
        vertical = self._run(path, "0", "0", "--width", "4", "--height", "3",
                             "--runs", "--run-axis", "vertical", "--json")
        self._assert_success(vertical)
        parsed = json.loads(vertical.stdout)
        self.assertEqual(parsed["axis"], "vertical")
        self.assertEqual([(run["x"], run["y"], run["length"]) for run in parsed["runs"]],
                         [(0, 0, 3), (1, 0, 3), (2, 0, 3), (3, 0, 3)])
        one_pixel = self._run(path, "0", "0", "--runs", "--run-axis", "vertical", "--json")
        self._assert_success(one_pixel)
        self.assertEqual(json.loads(one_pixel.stdout)["axis"], "vertical")

    def test_explicit_vertical_axis_keeps_one_row_pixels_in_separate_columns(self):
        _, data = rgb_image(3, 1, lambda x, y: (7, 6, 5))
        path = self._write(self._tmp_dir(), "one-row.png", data)
        result = self._run(path, "0", "0", "--width", "3", "--height", "1",
                           "--runs", "--run-axis", "vertical", "--json")
        self._assert_success(result)
        report = json.loads(result.stdout)
        self.assertEqual(report["axis"], "vertical")
        self.assertEqual([(run["x"], run["y"], run["length"], run["rgb"])
                          for run in report["runs"]], [
            (0, 0, 1, [7, 6, 5]),
            (1, 0, 1, [7, 6, 5]),
            (2, 0, 1, [7, 6, 5]),
        ])

    def test_run_axis_requires_runs_before_read(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            result = self._run("missing.png", "0", "0", "--run-axis", "vertical")
        self._assert_usage_error(result, "requires --runs")
        self.assertEqual(result.stdout, "")

    def test_alpha_runs_group_by_rgba_and_preserve_transparent_rgb(self):
        colors = [(10, 20, 30, 0), (10, 20, 30, 128), (10, 20, 30, 255),
                  (10, 20, 30, 255), (40, 50, 60, 0), (70, 80, 90, 0)]
        rows = [b"".join(bytes(pixel) for pixel in colors[:3]),
                b"".join(bytes(pixel) for pixel in colors[3:])]
        path = self._write(self._tmp_dir(), "rgba-runs.png", make_png(3, 2, rows, color_type=6))
        result = self._run(path, "0", "0", "--width", "3", "--alpha", "--runs", "--json")
        self._assert_success(result)
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["runs"], [
            {"x": 0, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 0},
            {"x": 1, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 128},
            {"x": 2, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 255},
        ])
        self.assertEqual(sum(run["length"] for run in parsed["runs"]), 3)
        text = self._run(path, "0", "0", "--width", "3", "--alpha", "--runs")
        self._assert_success(text)
        self.assertTrue(text.stdout.endswith("(2, 0): 10,20,30  #0A141E  length=1  alpha=255\n"))

        vertical = self._run(path, "2", "0", "--height", "2", "--alpha", "--runs", "--json")
        self._assert_success(vertical)
        vertical_data = json.loads(vertical.stdout)
        self.assertEqual(vertical_data["axis"], "vertical")
        self.assertEqual(vertical_data["runs"], [
            {"x": 2, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 255},
            {"x": 2, "y": 1, "length": 1, "rgb": [70, 80, 90], "hex": "#46505A", "alpha": 0},
        ])

        rgb_only = self._run(path, "0", "0", "--width", "3", "--runs", "--json")
        self._assert_success(rgb_only)
        self.assertEqual(json.loads(rgb_only.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 3, "rgb": [10, 20, 30], "hex": "#0A141E"},
        ])

    def test_alpha_runs_keep_opaque_and_trns_defaults(self):
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb_image(2, 1, lambda x, y: (1, 2, 3))[1])
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(opaque, "0", "0", "--width", "2", "--alpha", "--runs", "--json")
        self._assert_success(result)
        self.assertEqual([run["alpha"] for run in json.loads(result.stdout)["runs"]], [255])
        self.assertTrue(read.call_args.kwargs["alpha"])
        self.assertEqual(read.call_args.kwargs["max_rows"], 1)
        trns = self._write(self._tmp_dir(), "trns.png", make_png(
            2, 1, [bytes((1, 2, 3, 1, 2, 4))], color_type=2,
            trns=b"\x00\x01\x00\x02\x00\x03"))
        result = self._run(trns, "0", "0", "--width", "2", "--alpha", "--runs", "--json")
        self._assert_success(result)
        self.assertEqual([(run["length"], run["alpha"]) for run in json.loads(result.stdout)["runs"]], [(1, 0), (1, 255)])

    def test_alpha_runs_group_rgba_and_preserve_transparent_rgb(self):
        row = bytes((10, 20, 30, 0, 10, 20, 30, 0,
                     10, 20, 30, 128, 1, 2, 3, 0,
                     1, 2, 3, 255, 10, 20, 30, 0))
        path = self._write(self._tmp_dir(), "rgba-runs.png",
                           make_png(6, 1, [row], color_type=6))
        result = self._run(path, "2", "0", "--width", "4", "--runs", "--alpha", "--json")
        self._assert_success(result)
        report = json.loads(result.stdout)
        self.assertEqual(report["axis"], "horizontal")
        self.assertEqual(report["runs"], [
            {"x": 2, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 128},
            {"x": 3, "y": 0, "length": 1, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 0},
            {"x": 4, "y": 0, "length": 1, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 255},
            {"x": 5, "y": 0, "length": 1, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 0},
        ])
        self.assertEqual(sum(run["length"] for run in report["runs"]), 4)
        text = self._run(path, "2", "0", "--width", "4", "--runs", "--alpha")
        self._assert_success(text)
        self.assertIn("(2, 0): 10,20,30  #0A141E  length=1  alpha=128", text.stdout)
        rgb_only = self._run(path, "0", "0", "--width", "6", "--runs", "--json")
        self._assert_success(rgb_only)
        plain_runs = json.loads(rgb_only.stdout)["runs"]
        self.assertNotIn("alpha", plain_runs[0])
        self.assertEqual(plain_runs[0]["length"], 3)
        self.assertEqual(plain_runs[-1]["length"], 1)

    def test_alpha_vertical_runs_and_opaque_fallback(self):
        rows = [bytes((5, 6, 7, alpha)) for alpha in (0, 128, 255)]
        path = self._write(self._tmp_dir(), "vertical-rgba.png",
                           make_png(1, 3, rows, color_type=6))
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "0", "1", "--height", "2", "--runs", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(read.call_args.kwargs, {"max_rows": 3, "alpha": True})
        report = json.loads(result.stdout)
        self.assertEqual(report["axis"], "vertical")
        self.assertEqual(report["runs"], [
            {"x": 0, "y": 1, "length": 1, "rgb": [5, 6, 7], "hex": "#050607", "alpha": 128},
            {"x": 0, "y": 2, "length": 1, "rgb": [5, 6, 7], "hex": "#050607", "alpha": 255},
        ])
        opaque = self._write(self._tmp_dir(), "opaque-runs.png",
                             make_png(2, 1, [bytes((2, 3, 4, 2, 3, 4))]))
        result = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["runs"][0]["alpha"], 255)
        trns = self._write(self._tmp_dir(), "trns-runs.png", make_png(
            2, 1, [bytes((4, 5, 6, 7, 8, 9))], color_type=2,
            trns=b"\x00\x04\x00\x05\x00\x06"))
        result = self._run(trns, "0", "0", "--width", "2", "--runs", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual([run["alpha"] for run in json.loads(result.stdout)["runs"]], [0, 255])

    def test_invalid_regions_and_reads_have_no_stdout(self):
        path = self._fixture()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            two_dimensional = self._run(path, "0", "0", "--width", "2", "--height", "2", "--runs")
        self._assert_usage_error(two_dimensional, "single row or column")
        self.assertEqual(two_dimensional.stdout, "")
        conflict = self._run(path, "0", "0", "--runs", "--histogram")
        self._assert_usage_error(conflict)
        self.assertEqual(conflict.stdout, "")
        invalid_alpha_runs = self._run(path, "0", "0", "--width", "2", "--height", "2", "--runs", "--alpha")
        self._assert_usage_error(invalid_alpha_runs, "single row or column")
        self.assertEqual(invalid_alpha_runs.stdout, "")

        outside = self._run(path, "5", "2", "--width", "2", "--runs")
        self._assert_usage_error(outside, "outside the 6x5 image")
        self.assertEqual(outside.stdout, "")
        bad = self._write(self._tmp_dir(), "bad.png", b"not png")
        malformed = self._run(bad, "0", "0", "--runs")
        self._assert_usage_error(malformed)
        self.assertEqual(malformed.stdout, "")
        missing = self._run(str(self._tmp_dir() / "missing.png"), "0", "0", "--runs")
        self._assert_usage_error(missing)
        self.assertEqual(missing.stdout, "")
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "ref.png", data)
        with mock.patch.object(sample, "ROOT", str(root)):
            escaped = self._run(str(link), "0", "0", "--runs")
        self._assert_usage_error(escaped, "resolves outside")
        self.assertEqual(escaped.stdout, "")

    def test_script_control_path_round_trips_as_json(self):
        with control_named_png() as path:
            result = self._run_script(path, "0", "0", "--runs", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["image"], path)
        self.assertNotIn("\x1b", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
