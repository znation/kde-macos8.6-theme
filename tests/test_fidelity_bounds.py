"""Bounding rectangles for pixels beyond the fidelity tolerance."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_metrics import Image, compare  # noqa: E402


def _mask_changes(width, height, mask):
    """Return ``(reference, changed bytes, changed points)`` for *mask*."""
    reference, _ = rgb_image(width, height, lambda x, y: (0, 0, 0))
    changed = bytearray(reference.rgb)
    points = []
    for index in range(width * height):
        if mask & (1 << index):
            x, y = index % width, index // width
            points.append((x, y))
            changed[index * 3] = 1
    return reference, changed, points


class TestDifferenceBounds(unittest.TestCase):
    def test_bounds_cover_union_of_changed_channels_and_rows(self):
        reference, _ = rgb_image(6, 5, lambda x, y: (0, 0, 0))
        changed = bytearray(reference.rgb)
        for x, y, channel in ((4, 0, 0), (1, 2, 1), (3, 4, 2)):
            changed[(y * 6 + x) * 3 + channel] = 1
        candidate = Image(6, 5, bytes(changed))
        self.assertEqual(compare(candidate, reference).difference_bounds, (1, 0, 4, 5))

    def test_empty_threshold_edges_and_full_surface(self):
        reference, _ = rgb_image(3, 2, lambda x, y: (0, 0, 0))
        changed = Image(3, 2, bytes([10, 0, 0] * 6))
        self.assertIsNone(compare(reference, reference).difference_bounds)
        self.assertIsNone(compare(changed, reference, tolerance=10).difference_bounds)
        self.assertEqual(compare(changed, reference, tolerance=9).difference_bounds, (0, 0, 3, 2))
        self.assertIsNone(compare(changed, reference, tolerance=255).difference_bounds)
        one_pixel = Image(3, 2, bytes([10, 0, 0] + [0] * 15))
        self.assertEqual(compare(one_pixel, reference).difference_bounds, (0, 0, 1, 1))

    def test_alpha_difference_is_included(self):
        rgb, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        rgba = Image(2, 2, rgb.rgb, bytes([255, 255, 0, 255]))
        self.assertEqual(compare(rgba, rgb).difference_bounds, (0, 1, 1, 1))

    def test_small_matrices_match_coordinate_enumeration(self):
        for width, height in ((1, 1), (4, 3), (5, 2)):
            for mask in range(1 << (width * height)):
                reference, changed, points = _mask_changes(width, height, mask)
                expected = None if not points else (
                    min(x for x, _ in points), min(y for _, y in points),
                    max(x for x, _ in points) - min(x for x, _ in points) + 1,
                    max(y for _, y in points) - min(y for _, y in points) + 1,
                )
                with self.subTest(width=width, height=height, mask=mask):
                    self.assertEqual(compare(Image(width, height, bytes(changed)), reference).difference_bounds, expected)


class TestBoundsCli(FidelityCliTestCase):
    def test_text_and_json_report_crop_relative_bounds_with_aggregate_pass(self):
        def pixel(x, y):
            if 2 <= x < 4 and 1 <= y < 3:
                return (1 if (x, y) == (3, 2) else (x - 2) * 9, (y - 1) * 9, 5)
            return (0, 0, 0)

        candidate_image, _ = rgb_image(5, 4, pixel)
        candidate = make_png(5, 4, [candidate_image.rgb[i:i + 15] for i in range(0, 60, 15)])
        reference = self._padded_surface_png(6, 5, 1, 2)
        text_run = self._run_png_pair(candidate, reference, "--candidate-crop", "2,1,2,2", "--crop", "1,2,2,2", "--max-mae", "1")
        self._assert_pass(text_run)
        self.assertIn("difference bounds: 1,1,1,1", text_run.stdout)
        self.assertIn("candidate difference bounds: 3,2,1,1", text_run.stdout)
        self.assertIn("reference difference bounds: 2,3,1,1", text_run.stdout)
        json_run = self._run_png_pair(candidate, reference, "--candidate-crop", "2,1,2,2", "--crop", "1,2,2,2", "--max-mae", "1", "--json")
        result = json.loads(json_run.stdout)
        self.assertEqual(json_run.returncode, 0)
        self.assertEqual(result["metrics"]["difference_bounds"], [1, 1, 1, 1])
        self.assertEqual(result["candidate_difference_bounds"], [3, 2, 1, 1])
        self.assertEqual(result["reference_difference_bounds"], [2, 3, 1, 1])
        self.assertTrue(result["passed"])

    def test_json_null_for_no_differences(self):
        _, png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        result = self._run_png_pair(png, png, "--json")
        self.assertIsNone(json.loads(result.stdout)["metrics"]["difference_bounds"])
        self.assertIsNone(json.loads(result.stdout)["candidate_difference_bounds"])
        self.assertIsNone(json.loads(result.stdout)["reference_difference_bounds"])
        text_run = self._run_png_pair(png, png)
        self.assertIn("candidate difference bounds: none", text_run.stdout)
        self.assertIn("reference difference bounds: none", text_run.stdout)

    def test_source_bounds_use_zero_for_an_omitted_crop(self):
        candidate, _ = rgb_image(2, 2, lambda x, y: (1 if (x, y) == (1, 1) else 0, 0, 0))
        reference, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        run = self._run_png_pair(make_png(2, 2, [candidate.rgb[:6], candidate.rgb[6:]]),
                                 make_png(2, 2, [reference.rgb[:6], reference.rgb[6:]]), "--json")
        result = json.loads(run.stdout)
        self.assertEqual(result["candidate_difference_bounds"], [1, 1, 1, 1])
        self.assertEqual(result["reference_difference_bounds"], [1, 1, 1, 1])

    def test_direct_script_emits_source_bounds(self):
        _, candidate_png = rgb_image(1, 1, lambda x, y: (1, 0, 0))
        _, reference_png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        tmp = self._tmp_dir()
        candidate_path = self._write(tmp, "direct-candidate.png", candidate_png)
        reference_path = self._write(tmp, "direct-reference.png", reference_png)
        script = repo_root.ROOT / "tools" / "fidelity.py"
        run = subprocess.run([sys.executable, str(script), candidate_path, reference_path, "--json", "--max-mae", "1"],
                             capture_output=True, text=True, check=False)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)["candidate_difference_bounds"], [0, 0, 1, 1])


if __name__ == "__main__":
    unittest.main()
