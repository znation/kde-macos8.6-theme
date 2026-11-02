"""Per-row over-tolerance diagnostics for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_pixels import difference_rows  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRows(unittest.TestCase):
    def test_dense_rows_and_rgba_pixel_union(self):
        reference = Image(3, 4, bytes(36), bytes([255] * 12))
        rgb = bytearray(36)
        rgb[0] = 10
        rgb[12 + 1] = 11
        rgb[24 + 2] = 12
        alpha = bytearray([255] * 12)
        alpha[10] = 0
        candidate = Image(3, 4, bytes(rgb), bytes(alpha))
        self.assertEqual(difference_rows(candidate, reference, 10), [0, 1, 1, 1])
        self.assertEqual(difference_rows(candidate, reference, 255), [0, 0, 0, 0])
        self.assertEqual(difference_rows(reference, reference, 0), [0, 0, 0, 0])
        self.assertEqual(difference_rows(Image(1, 1, bytes([1, 2, 3])),
                                         Image(1, 1, bytes(3)), 0), [1])

    def test_alpha_missing_and_raw_transparent_rgb(self):
        opaque = Image(1, 1, bytes(3))
        transparent = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        self.assertEqual(difference_rows(opaque, transparent, 254), [1])
        self.assertEqual(difference_rows(transparent, opaque, 254), [1])
        hidden_rgb = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        clear = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_rows(hidden_rgb, clear, 19), [1])


class TestDifferenceRowsCli(FidelityCliTestCase):
    def test_crops_outputs_verdicts_and_default_omission(self):
        candidate = make_png(4, 4, [bytes(12)] * 4)
        reference_rows = [bytearray(12) for _ in range(4)]
        reference_rows[0][0] = 200  # outside the selected crop
        reference_rows[1][3] = 20
        reference_rows[3][6] = 30
        reference = make_png(4, 4, [bytes(row) for row in reference_rows])
        args = ("--difference-rows", "--candidate-crop", "1,1,2,3", "--crop", "1,1,2,3")
        failed = self._run_png_pair(candidate, reference, *args)
        self._assert_fail(failed)
        self.assertIn("difference rows: [1, 0, 1]", failed.stdout)
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        self.assertEqual(data["difference_rows"], [1, 0, 1])
        self.assertEqual(sum(data["difference_rows"]), data["metrics"]["differing"])
        passed = self._run_png_pair(candidate, reference, *args, "--max-mae", "255", "--json")
        passed_data = json.loads(passed.stdout)
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(passed_data["difference_rows"], [1, 0, 1])
        combined = self._run_png_pair(candidate, reference, "--difference-rows", "--channel-counts", "--json")
        self.assertIn("channel_counts", json.loads(combined.stdout))
        with mock.patch.object(fidelity, "difference_rows") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_rows", json.loads(ordinary.stdout))
        helper.assert_not_called()

    def test_direct_script_and_errors(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_altered_pair(tmp)
        script = self._run_script(candidate, reference, "--difference-rows", "--json")
        self.assertEqual(len(json.loads(script.stdout)["difference_rows"]), 3)
        bad = self._run(candidate, self._write(tmp, "missing.png", b"bad"), "--difference-rows")
        self.assertEqual((bad.returncode, bad.stdout), (2, ""))
        mismatch = self._run_png_pair(make_png(1, 1, [bytes(3)]), make_png(2, 1, [bytes(6)]),
                                      "--difference-rows")
        self.assertEqual((mismatch.returncode, mismatch.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
