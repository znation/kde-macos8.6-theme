"""Ranked pixel diagnostics for the fidelity comparison tool."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_metrics import Image  # noqa: E402
from tools.fidelity_pixels import worst_pixels  # noqa: E402
from tools import fidelity  # noqa: E402


class TestWorstPixels(unittest.TestCase):
    def test_severity_ties_alpha_and_tolerance(self):
        ref = Image(3, 2, bytes(18))
        cand = Image(3, 2, bytes([5, 0, 0, 9, 0, 0, 8, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0]),
                     bytes([255, 255, 255, 255, 250, 255]))
        got = worst_pixels(cand, ref, 5, 2)
        self.assertEqual([(p["x"], p["y"], p["max_delta"]) for p in got],
                         [(1, 0, 9), (2, 0, 8)])
        self.assertEqual(worst_pixels(cand, ref, 9, 10), [])

    def test_deterministic_matrices_match_full_sort(self):
        for width, height in ((1, 1), (3, 2), (4, 2)):
            ref = Image(width, height, bytes(width * height * 3))
            rgb = bytes((i * 17) % 256 for i in range(width * height * 3))
            cand = Image(width, height, rgb)
            ordered = sorted(
                ((-max(rgb[i * 3:i * 3 + 3]), i) for i in range(width * height)
                 if max(rgb[i * 3:i * 3 + 3]) > 0)
            )
            expected = [(i % width, i // width, -delta) for delta, i in ordered[:3]]
            actual = [(p["x"], p["y"], p["max_delta"])
                      for p in worst_pixels(cand, ref, 0, 3)]
            self.assertEqual(actual, expected)


class TestWorstPixelsCli(FidelityCliTestCase):
    def test_json_and_text_and_crop_relative_coordinates(self):
        surface, candidate = rgb_image(2, 1, lambda x, y: (10 if x == 1 else 0, 0, 0))
        reference = make_png(4, 1, [bytes(12)])
        result = self._run_png_pair(candidate, reference, "--candidate-crop", "0,0,2,1",
                                    "--crop", "1,0,2,1", "--max-mae", "10",
                                    "--worst-pixels", "1", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["worst_pixels"], [{"x": 1, "y": 0,
                         "candidate_rgba": [10, 0, 0, 255],
                         "reference_rgba": [0, 0, 0, 255], "max_delta": 10}])
        self.assertEqual(result.returncode, 0)

    def test_default_does_not_call_helper_and_invalid_is_early(self):
        _, png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with mock.patch.object(fidelity, "worst_pixels") as helper:
            result = self._run_png_pair(png, png, "--json")
        self.assertNotIn("worst_pixels", json.loads(result.stdout))
        helper.assert_not_called()
        for invalid in ("0", "-1", "1001", "1.2", "١", ""):
            with self.subTest(invalid=invalid):
                result = self._run_png_pair(png, png, "--worst-pixels", invalid)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
