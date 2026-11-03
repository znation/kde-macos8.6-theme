"""Direct result assembly and output ordering for reference histograms."""

from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace

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
                               color_positions=False, color_fractions=False)
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
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(vars(args), original)

    def test_alpha_on_rgb_image_uses_opaque_fallback(self):
        image = SimpleNamespace(width=1, rgb=bytes((7, 8, 9)), alpha=None)
        args = SimpleNamespace(image="fixture.png", x=0, y=0, width=1, height=1,
                               alpha=True, top_colors=None, color_bounds=False,
                               color_positions=False, color_fractions=False)
        self.assertEqual(sample_report_histogram._histogram_result(args, image, 1, 1)["colors"], [
            {"rgb": [7, 8, 9], "hex": "#070809", "count": 1, "alpha": 255},
        ])

    def test_cropped_alpha_result_and_combined_cli_order(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(4, 2, [
            bytes((9, 9, 9, 255, 1, 2, 3, 0, 4, 5, 6, 128, 8, 8, 8, 255)),
            bytes((9, 9, 9, 255, 1, 2, 3, 0, 1, 2, 3, 0, 8, 8, 8, 255)),
        ], color_type=6))
        result = self._run(path, "1", "0", "--width", "2", "--height", "2",
                           "--histogram", "--alpha", "--top-colors", "1",
                           "--color-fractions", "--color-bounds", "--color-positions", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual(payload, {
            "image": path, "image_width": 4, "image_height": 2,
            "region": {"x": 1, "y": 0, "width": 2, "height": 2},
            "colors": [{"rgb": [1, 2, 3], "hex": "#010203", "count": 3,
                        "alpha": 0, "fraction": 0.75, "position": {"x": 1, "y": 0},
                        "bounds": {"x": 1, "y": 0, "width": 2, "height": 2}}],
            "total_colors": 2, "omitted_pixels": 1,
        })
        text = self._run(path, "1", "0", "--width", "2", "--height", "2",
                         "--histogram", "--alpha", "--top-colors", "1",
                         "--color-fractions", "--color-bounds", "--color-positions")
        self._assert_success(text)
        self.assertEqual(text.stdout, (
            f"image: {path}  4x2\nregion (1, 0) 2x2:\n"
            "1,2,3  #010203  count=3  alpha=0  bounds=1,0,2,2  fraction=0.75  position=1,0\n"
            "total colors: 2\nomitted pixels: 1\n"
        ))
        direct = self._run(path, "1", "0", "--width", "2", "--height", "2",
                           "--histogram", "--alpha", "--top-colors", "1",
                           "--color-fractions", "--color-bounds", "--color-positions", "--json")
        script = self._run_script(path, "1", "0", "--width", "2", "--height", "2",
                                  "--histogram", "--alpha", "--top-colors", "1",
                                  "--color-fractions", "--color-bounds", "--color-positions", "--json")
        self.assertEqual((direct.stdout, direct.stderr, direct.returncode),
                         (script.stdout, script.stderr, script.returncode))


if __name__ == "__main__":
    import unittest

    unittest.main()
