"""Direct result assembly and output ordering for reference histograms."""

from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace
from unittest.mock import patch

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png
from tools import sample
from tools import sample_report_histogram


class TestSampleHistogramResult(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_direct_rgb_result_ties_and_no_side_effects(self):
        image = SimpleNamespace(width=2, rgb=bytes((4, 5, 6, 1, 2, 3)), alpha=None)
        args = SimpleNamespace(image="fixture.png", x=0, y=0, width=2, height=1,
                               alpha=False, top_colors=None, color_bounds=False,
                               color_positions=False, color_fractions=False,
                               color_centroids=False)
        original = vars(args).copy()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = sample_report_histogram._histogram_result(args, image, 2, 1)
        self.assertEqual(result, {
            "image": "fixture.png", "image_width": 2, "image_height": 1,
            "region": {"x": 0, "y": 0, "width": 2, "height": 1},
            "colors": [
                {"rgb": [1, 2, 3], "hex": "#010203", "count": 1},
                {"rgb": [4, 5, 6], "hex": "#040506", "count": 1},
            ],
        })
        self.assertNotIn("total_colors", result)
        self.assertNotIn("omitted_pixels", result)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(vars(args), original)

    def test_alpha_on_rgb_image_uses_opaque_fallback(self):
        image = SimpleNamespace(width=1, rgb=bytes((7, 8, 9)), alpha=None)
        args = SimpleNamespace(image="fixture.png", x=0, y=0, width=1, height=1,
                               alpha=True, top_colors=None, color_bounds=False,
                               color_positions=False, color_fractions=False,
                               color_centroids=False)
        self.assertEqual(sample_report_histogram._histogram_result(args, image, 1, 1)["colors"], [
            {"rgb": [7, 8, 9], "hex": "#070809", "count": 1, "alpha": 255},
        ])

    def test_filtering_every_color_keeps_empty_page_totals(self):
        image = SimpleNamespace(width=2, rgb=bytes((1, 2, 3, 4, 5, 6)), alpha=None)
        args = SimpleNamespace(image="fixture.png", x=0, y=0, width=2, height=1,
                               alpha=False, top_colors=None, color_offset=None,
                               min_color_count=3, max_color_count=None,
                               min_color_fraction=None, max_color_fraction=None,
                               exclude_colors=None, color_bounds=False,
                               color_positions=False, color_fractions=True)
        result = sample_report_histogram._histogram_result(args, image, 2, 1)
        self.assertEqual(result["colors"], [])
        self.assertEqual((result["total_colors"], result["omitted_pixels"]), (2, 2))

    def test_cropped_rgba_result_truncation_and_disconnected_bounds(self):
        image = SimpleNamespace(width=5, rgb=bytes(
            (99, 0, 0, 1, 2, 3, 8, 8, 8, 1, 2, 3, 99, 0, 0,
             99, 0, 0, 1, 2, 3, 4, 5, 6, 1, 2, 3, 99, 0, 0)),
            alpha=bytes((255, 0, 128, 0, 255, 255, 0, 255, 0, 255)))
        args = SimpleNamespace(image="fixture.png", x=1, y=0, width=4, height=2,
                               alpha=True, top_colors=1, color_bounds=True,
                               color_positions=True, color_fractions=True)
        self.assertEqual(sample_report_histogram._histogram_result(args, image, 5, 2), {
            "image": "fixture.png", "image_width": 5, "image_height": 2,
            "region": {"x": 1, "y": 0, "width": 4, "height": 2},
            "colors": [{"rgb": [1, 2, 3], "hex": "#010203", "count": 4,
                        "alpha": 0, "fraction": 4 / 8, "position": {"x": 1, "y": 0},
                        "bounds": {"x": 1, "y": 0, "width": 3, "height": 2}}],
            "total_colors": 4, "omitted_pixels": 4,
        })

    def test_cropped_alpha_result_and_combined_cli_order(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(4, 2, [
            bytes((9, 9, 9, 255, 1, 2, 3, 0, 4, 5, 6, 128, 8, 8, 8, 255)),
            bytes((9, 9, 9, 255, 1, 2, 3, 0, 1, 2, 3, 0, 8, 8, 8, 255)),
        ], color_type=6))
        result = self._run(path, "1", "0", "--width", "2", "--height", "2",
                           "--histogram", "--alpha", "--top-colors", "1",
                           "--color-fractions", "--color-bounds", "--color-positions",
                           "--color-centroids", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual(list(payload), ["image", "image_width", "image_height",
                                         "region", "colors", "total_colors",
                                         "omitted_pixels"])
        self.assertEqual(payload, {
            "image": path, "image_width": 4, "image_height": 2,
            "region": {"x": 1, "y": 0, "width": 2, "height": 2},
            "colors": [{"rgb": [1, 2, 3], "hex": "#010203", "count": 3,
                        "alpha": 0, "fraction": 0.75, "position": {"x": 1, "y": 0},
                        "centroid": {"x": 1.3333333333333333, "y": 0.6666666666666666},
                        "bounds": {"x": 1, "y": 0, "width": 2, "height": 2}}],
            "total_colors": 2, "omitted_pixels": 1,
        })
        text = self._run(path, "1", "0", "--width", "2", "--height", "2",
                         "--histogram", "--alpha", "--top-colors", "1",
                         "--color-fractions", "--color-bounds", "--color-positions", "--color-centroids")
        self._assert_success(text)
        self.assertEqual(text.stdout, (
            f"image: {path}  4x2\nregion (1, 0) 2x2:\n"
            "1,2,3  #010203  count=3  alpha=0  bounds=1,0,2,2  fraction=0.75  position=1,0  centroid=1.3333333333333333,0.6666666666666666\n"
            "total colors: 2\nomitted pixels: 1\n"
        ))
        direct = self._run(path, "1", "0", "--width", "2", "--height", "2",
                           "--histogram", "--alpha", "--top-colors", "1",
                           "--color-fractions", "--color-bounds", "--color-positions", "--color-centroids", "--json")
        script = self._run_script(path, "1", "0", "--width", "2", "--height", "2",
                                  "--histogram", "--alpha", "--top-colors", "1",
                                  "--color-fractions", "--color-bounds", "--color-positions", "--color-centroids", "--json")
        self.assertEqual((direct.stdout, direct.stderr, direct.returncode),
                         (script.stdout, script.stderr, script.returncode))

    def test_spatial_collector_selected_colors_and_skips_unrequested_scan(self):
        image = SimpleNamespace(width=4, rgb=bytes((
            9, 9, 9, 1, 2, 3, 1, 2, 3, 1, 2, 3,
            9, 9, 9, 1, 2, 3, 1, 2, 3, 1, 2, 3,
            9, 9, 9, 1, 2, 3, 1, 2, 3, 1, 2, 3,
        )), alpha=bytes((255, 0, 0, 0, 255, 0, 4, 0, 255, 0, 0, 4)))
        args = SimpleNamespace(x=1, y=1, width=3, height=2, alpha=True,
                               color_bounds=True, color_positions=True, color_centroids=True)
        colors = [((1, 2, 3, 0), 4), ((1, 2, 3, 4), 2)]
        fields = sample_report_histogram._histogram_spatial_fields(args, image, colors)
        self.assertEqual(fields, {
            (1, 2, 3, 0): {"position": {"x": 1, "y": 1},
                           "centroid": {"x": 1.75, "y": 1.5},
                           "bounds": {"x": 1, "y": 1, "width": 3, "height": 2}},
            (1, 2, 3, 4): {"position": {"x": 2, "y": 1},
                           "centroid": {"x": 2.5, "y": 1.5},
                           "bounds": {"x": 2, "y": 1, "width": 2, "height": 2}},
        })
        args.color_bounds = args.color_positions = args.color_centroids = False
        with patch.object(sample_report_histogram, "_positioned_region_pixels") as scan:
            self.assertEqual(sample_report_histogram._histogram_spatial_fields(args, image, colors),
                             {color: {} for color, _ in colors})
        scan.assert_not_called()
        args.color_bounds = args.color_positions = args.color_centroids = True
        with patch.object(sample_report_histogram, "_positioned_region_pixels",
                          wraps=sample_report_histogram._positioned_region_pixels) as scan:
            sample_report_histogram._histogram_spatial_fields(args, image, colors)
        scan.assert_called_once_with(image, 1, 1, 3, 2)


if __name__ == "__main__":
    import unittest

    unittest.main()
