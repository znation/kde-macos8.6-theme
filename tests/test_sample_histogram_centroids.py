"""Mean coordinates in reference-pixel histogram reports."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_histogram


class TestSampleHistogramCentroids(CliTestCase):
    """The histogram's ``--color-centroids`` option: mean pixel coordinates per emitted color."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_crop_centroids_are_means_in_text_and_json(self):
        _, data = rgb_image(5, 4, lambda x, y: (
            (1, 2, 3) if (x, y) in {(1, 1), (3, 1), (2, 2)} else (8, 8, 8)
        ))
        path = self._write(self._tmp_dir(), "centroid.png", data)
        args = (path, "1", "1", "--width", "3", "--height", "2",
                "--histogram", "--color-centroids")
        result = self._run(*args, "--json")
        self._assert_success(result)
        colors = json.loads(result.stdout)["colors"]
        self.assertEqual(colors[0]["centroid"], {"x": 2.0, "y": 1.3333333333333333})
        self.assertEqual(colors[1]["centroid"], {"x": 2.0, "y": 1.6666666666666667})
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("centroid=2.0,1.3333333333333333", text.stdout)
        self.assertIn("centroid=2.0,1.6666666666666667", text.stdout)

    def test_alpha_and_top_colors_use_all_emitted_occurrences(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, [
            bytes((1, 2, 3, 0, 9, 9, 9, 255, 1, 2, 3, 128))
        ], color_type=6))
        result = self._run(path, "0", "0", "--width", "3", "--histogram", "--alpha",
                           "--top-colors", "2", "--color-centroids", "--json")
        self._assert_success(result)
        colors = json.loads(result.stdout)["colors"]
        self.assertEqual([(item["alpha"], item["centroid"]) for item in colors], [
            (0, {"x": 0.0, "y": 0.0}), (128, {"x": 2.0, "y": 0.0}),
        ])

    def test_shared_optional_traversal_and_default_omission(self):
        _, data = rgb_image(2, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "small.png", data)
        with mock.patch.object(sample_report_histogram, "positioned_region_pixels",
                               wraps=sample_report_histogram.positioned_region_pixels) as positioned:
            plain = self._run(path, "0", "0", "--width", "2", "--height", "2", "--histogram", "--json")
            measured = self._run(path, "0", "0", "--width", "2", "--height", "2",
                                 "--histogram", "--color-centroids", "--color-bounds", "--color-positions", "--json")
        self._assert_success(plain)
        self._assert_success(measured)
        self.assertNotIn("centroid", json.loads(plain.stdout)["colors"][0])
        self.assertEqual(positioned.call_count, 1)

    def test_requires_histogram_and_direct_script_matches(self):
        _, data = rgb_image(1, 1, lambda _x, _y: (3, 4, 5))
        path = self._write(self._tmp_dir(), "one.png", data)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--color-centroids")
        self._assert_usage_error(invalid, "requires --histogram")
        args = (path, "0", "0", "--histogram", "--color-centroids", "--json")
        direct, script = self._run(*args), self._run_script(*args)
        self._assert_success(direct)
        self._assert_success(script)
        self.assertEqual(json.loads(direct.stdout), json.loads(script.stdout))
        self.assertIn("--color-centroids", self._run("--help").stdout)

    def test_crop_centroids_json_text_and_top_color_contributors(self):
        _, data = rgb_image(5, 3, lambda x, y: (
            (1, 2, 3) if (x, y) in {(1, 1), (3, 1), (1, 2)} else
            (4, 5, 6) if (x, y) == (2, 2) else (9, 9, 9)
        ))
        path = self._write(self._tmp_dir(), "centroids.png", data)
        args = (path, "1", "1", "--width", "3", "--height", "2", "--histogram", "--color-centroids")
        result = self._run(*args, "--json")
        self._assert_success(result)
        colors = json.loads(result.stdout)["colors"]
        self.assertEqual([item["centroid"] for item in colors], [
            {"x": 5 / 3, "y": 4 / 3}, {"x": 2.5, "y": 1.5}, {"x": 2.0, "y": 2.0},
        ])
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("centroid=1.6666666666666667,1.3333333333333333", text.stdout)
        top = self._run(*args, "--top-colors", "1", "--json")
        self._assert_success(top)
        self.assertEqual(json.loads(top.stdout)["colors"][0]["centroid"], {"x": 5 / 3, "y": 4 / 3})

    def test_rgba_keys_share_positioned_pass_and_plain_skips_it(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, [
            bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 0)),
        ], color_type=6))
        with mock.patch.object(sample_report_histogram, "positioned_region_pixels",
                               wraps=sample_report_histogram.positioned_region_pixels) as positioned:
            result = self._run(path, "0", "0", "--width", "3", "--histogram", "--alpha",
                               "--color-centroids", "--color-bounds", "--color-positions", "--json")
        self._assert_success(result)
        records = json.loads(result.stdout)["colors"]
        self.assertEqual([item["alpha"] for item in records], [0, 128])
        self.assertEqual([item["centroid"] for item in records], [
            {"x": 1.0, "y": 0.0}, {"x": 1.0, "y": 0.0},
        ])
        positioned.assert_called_once()
        with mock.patch.object(sample_report_histogram, "positioned_region_pixels",
                               wraps=sample_report_histogram.positioned_region_pixels) as positioned:
            plain = self._run(path, "0", "0", "--width", "3", "--histogram", "--json")
        self._assert_success(plain)
        self.assertNotIn("centroid", json.loads(plain.stdout)["colors"][0])
        positioned.assert_not_called()

    def test_requires_histogram_before_reads_and_direct_script_parity(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            result = self._run("not-read.png", "0", "0", "--color-centroids")
        self._assert_usage_error(result, "requires --histogram")
        self.assertEqual(result.stdout, "")
        _, data = rgb_image(2, 1, lambda x, _y: (x, 0, 0))
        path = self._write(self._tmp_dir(), "script.png", data)
        args = (path, "0", "0", "--width", "2", "--histogram", "--color-centroids", "--json")
        package = self._run(*args)
        script = self._run_script(*args)
        self._assert_success(package)
        self._assert_success(script)
        self.assertEqual(json.loads(package.stdout), json.loads(script.stdout))


if __name__ == "__main__":
    import unittest

    unittest.main()
