"""Per-column vertical mismatch bounds for fidelity comparisons."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools.fidelity_lib.spatial import difference_column_bounds  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceColumnBounds(unittest.TestCase):
    """Test vertical bounds of pixels over the difference threshold."""
    def test_intervals_gaps_threshold_and_bottom_edge(self):
        width, height = 4, 6
        rgb = bytearray(width * height * 3)
        for x, y, value in ((0, 1, 11), (0, 4, 20), (2, 5, 1), (3, 0, 10)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(difference_column_bounds(candidate, reference, 10),
                         [{"y": 1, "height": 4}, None, None, None])
        self.assertEqual(difference_column_bounds(candidate, reference, 0),
                         [{"y": 1, "height": 4}, None, {"y": 5, "height": 1}, {"y": 0, "height": 1}])
        self.assertEqual(difference_column_bounds(candidate, reference, 255), [None] * width)

    def test_alpha_and_stored_rgb(self):
        opaque = Image(2, 1, bytes(6))
        alpha_changed = Image(2, 1, bytes(6), bytes([255, 0]))
        self.assertEqual(difference_column_bounds(alpha_changed, opaque, 254),
                         [None, {"y": 0, "height": 1}])
        hidden_rgb = Image(1, 2, bytes([0, 0, 0, 20, 0, 0]), bytes([0, 0]))
        clear = Image(1, 2, bytes(6), bytes([0, 0]))
        self.assertEqual(difference_column_bounds(hidden_rgb, clear, 19),
                         [{"y": 1, "height": 1}])


class TestDifferenceColumnBoundsCli(FidelityCliTestCase):
    """Test vertical bounds output and crop composition in the CLI."""
    def test_crops_composition_and_verdicts(self):
        candidate_rows = [bytearray(15) for _ in range(4)]
        candidate_rows[1][6] = 40
        candidate_rows[3][6] = 40
        candidate = make_png(5, 4, [bytes(row) for row in candidate_rows])
        reference = make_png(5, 4, [bytes(15)] * 4)
        args = ("--difference-column-bounds", "--difference-row-bounds",
                "--difference-rows", "--difference-columns",
                "--candidate-crop", "1,1,3,3", "--crop", "0,1,3,3")
        failed = self._run_png_pair(candidate, reference, *args)
        self.assertEqual(failed.returncode, 1)
        self.assertIn('difference column bounds: [null, {"y": 0, "height": 3}, null]', failed.stdout)
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        self.assertEqual(data["difference_column_bounds"],
                         [None, {"y": 0, "height": 3}, None])
        self.assertEqual(data["difference_row_bounds"],
                         [{"x": 1, "width": 1}, None, {"x": 1, "width": 1}])
        passed = self._run_png_pair(candidate, reference, *args, "--max-mae", "255", "--json")
        self.assertEqual(passed.returncode, 0)
        self.assertTrue(json.loads(passed.stdout)["difference_column_bounds"][1])

    def test_opt_in_direct_script_and_errors(self):
        self.assert_difference_bounds_opt_in(
            "--difference-column-bounds", [{"y": 1, "height": 1}, None]
        )


if __name__ == "__main__":
    unittest.main()
