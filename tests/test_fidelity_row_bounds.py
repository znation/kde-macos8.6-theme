"""Per-row horizontal mismatch bounds for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_spatial import difference_column_bounds, difference_row_bounds  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRowBounds(unittest.TestCase):
    def test_axis_bounds_degenerate_full_and_transpose_cases(self):
        empty = Image(3, 2, bytes(18))
        self.assertEqual(difference_row_bounds(empty, empty, 0), [None, None])
        full = Image(3, 2, bytes([1, 0, 0] * 6))
        self.assertEqual(difference_row_bounds(full, empty, 0),
                         [{"x": 0, "width": 3}, {"x": 0, "width": 3}])

        single_row = Image(3, 1, bytes([0, 0, 0, 1, 0, 0, 0, 0, 0]))
        self.assertEqual(difference_row_bounds(single_row, Image(3, 1, bytes(9)), 0),
                         [{"x": 1, "width": 1}])
        single_column = Image(1, 3, bytes([0, 0, 0, 1, 0, 0, 0, 0, 0]))
        self.assertEqual(difference_column_bounds(single_column, Image(1, 3, bytes(9)), 0),
                         [{"y": 1, "height": 1}])

        # Transposing a 3x2 mismatch map swaps scanline orientation and keys.
        rgb = bytearray(3 * 2 * 3)
        for x, y in ((0, 0), (2, 0), (1, 1)):
            rgb[(y * 3 + x) * 3] = 1
        image = Image(3, 2, bytes(rgb))
        transposed_rgb = bytearray(2 * 3 * 3)
        for x, y in ((0, 0), (2, 0), (1, 1)):
            transposed_rgb[(x * 2 + y) * 3] = 1
        transposed = Image(2, 3, bytes(transposed_rgb))
        expected_rows = [{"x": 0, "width": 3}, {"x": 1, "width": 1}]
        expected_columns = [{"y": 0, "height": 1}, {"y": 1, "height": 1},
                            {"y": 0, "height": 1}]
        self.assertEqual(difference_row_bounds(image, Image(3, 2, bytes(18)), 0), expected_rows)
        self.assertEqual(difference_column_bounds(transposed, Image(2, 3, bytes(18)), 0),
                         [{"y": 0, "height": 3}, {"y": 1, "height": 1}])
        self.assertEqual(difference_column_bounds(image, Image(3, 2, bytes(18)), 0),
                         expected_columns)
        self.assertEqual(difference_row_bounds(transposed, Image(2, 3, bytes(18)), 0),
                         [{"x": 0, "width": 1}, {"x": 1, "width": 1},
                          {"x": 0, "width": 1}])

    def test_intervals_gaps_threshold_and_far_edge(self):
        width, height = 8, 4
        rgb = bytearray(width * height * 3)
        for x, y, value in ((1, 0, 10), (6, 0, 20), (7, 2, 1)):
            rgb[(y * width + x) * 3] = value
        candidate = Image(width, height, bytes(rgb))
        reference = Image(width, height, bytes(width * height * 3))
        self.assertEqual(difference_row_bounds(candidate, reference, 10),
                         [{"x": 6, "width": 1}, None, None, None])
        self.assertEqual(difference_row_bounds(candidate, reference, 0),
                         [{"x": 1, "width": 6}, None, {"x": 7, "width": 1}, None])
        self.assertEqual(difference_row_bounds(candidate, reference, 255), [None] * height)

    def test_alpha_and_stored_rgb(self):
        opaque = Image(1, 2, bytes(6))
        alpha_changed = Image(1, 2, bytes(6), bytes([255, 0]))
        self.assertEqual(difference_row_bounds(alpha_changed, opaque, 254),
                         [None, {"x": 0, "width": 1}])
        hidden_rgb = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        clear = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_row_bounds(hidden_rgb, clear, 19),
                         [{"x": 0, "width": 1}])


class TestDifferenceRowBoundsCli(FidelityCliTestCase):
    def test_crops_output_composition_and_verdicts(self):
        candidate_rows = [bytearray(15) for _ in range(3)]
        candidate_rows[1][3] = 40
        candidate_rows[1][12] = 40
        candidate = make_png(5, 3, [bytes(row) for row in candidate_rows])
        reference = make_png(5, 3, [bytes(15)] * 3)
        args = ("--difference-row-bounds", "--difference-rows", "--difference-columns",
                "--candidate-crop", "1,0,4,3", "--crop", "0,0,4,3")
        failed = self._run_png_pair(candidate, reference, *args)
        self.assertEqual(failed.returncode, 1)
        self.assertIn('difference row bounds: [null, {"x": 0, "width": 4}, null]', failed.stdout)
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        self.assertEqual(data["difference_row_bounds"], [None, {"x": 0, "width": 4}, None])
        self.assertEqual(data["difference_rows"], [0, 2, 0])
        self.assertIn("difference_columns", data)
        passed = self._run_png_pair(candidate, reference, *args, "--max-mae", "255", "--json")
        self.assertEqual(passed.returncode, 0)
        self.assertTrue(json.loads(passed.stdout)["difference_row_bounds"][1])

    def test_opt_in_direct_script_and_errors(self):
        candidate = make_png(2, 2, [bytes(6), bytes([1, 0, 0, 0, 0, 0])])
        reference = make_png(2, 2, [bytes(6), bytes(6)])
        with mock.patch.object(fidelity, "difference_row_bounds") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_row_bounds", json.loads(ordinary.stdout))
        self.assertNotIn("difference row bounds:", ordinary.stdout)
        helper.assert_not_called()
        tmp = self._tmp_dir()
        candidate_path = self._write(tmp, "candidate.png", candidate)
        reference_path = self._write(tmp, "reference.png", reference)
        direct = self._run_script(candidate_path, reference_path, "--difference-row-bounds", "--json")
        self.assertEqual(json.loads(direct.stdout)["difference_row_bounds"],
                         [None, {"x": 0, "width": 1}])
        bad = self._run(candidate_path, self._write(tmp, "missing.png", b"bad"),
                         "--difference-row-bounds")
        self.assertEqual((bad.returncode, bad.stdout), (2, ""))
        mismatch = self._run_png_pair(make_png(1, 1, [bytes(3)]),
                                      make_png(2, 1, [bytes(6)]), "--difference-row-bounds")
        self.assertEqual((mismatch.returncode, mismatch.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
