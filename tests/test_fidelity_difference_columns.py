"""Per-column over-tolerance diagnostics for fidelity comparisons."""

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_spatial import difference_columns  # noqa: E402
from tools.fidelity_metrics import compare  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceColumns(unittest.TestCase):
    def test_dense_columns_count_each_pixel_once(self):
        reference = Image(4, 3, bytes(36), bytes([255] * 12))
        rgb = bytearray(36)
        rgb[0] = 10
        rgb[1] = 20
        rgb[12 + 3] = 11
        rgb[2 * 12 + 2 * 3 + 2] = 12
        candidate = Image(4, 3, bytes(rgb), bytes([255] * 12))
        self.assertEqual(difference_columns(candidate, reference, 10), [1, 1, 1, 0])
        self.assertEqual(sum(difference_columns(candidate, reference, 10)), compare(candidate, reference, 10).differing)
        self.assertEqual(difference_columns(candidate, reference, 255), [0, 0, 0, 0])
        self.assertEqual(difference_columns(reference, reference, 0), [0, 0, 0, 0])

    def test_missing_alpha_and_hidden_rgb(self):
        opaque = Image(1, 1, bytes(3))
        transparent = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        self.assertEqual(difference_columns(opaque, transparent, 254), [1])
        self.assertEqual(difference_columns(transparent, opaque, 254), [1])
        hidden = Image(1, 1, bytes([20, 0, 0]), bytes([0]))
        clear = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(difference_columns(hidden, clear, 19), [1])


class TestDifferenceColumnsCli(FidelityCliTestCase):
    def test_crops_outputs_verdicts_and_default_omission(self):
        candidate = make_png(4, 4, [bytes(12)] * 4)
        rows = [bytearray(12) for _ in range(4)]
        rows[0][0] = 200
        rows[1][3] = 20
        rows[3][6] = 30
        reference = make_png(4, 4, [bytes(row) for row in rows])
        args = ("--difference-columns", "--candidate-crop", "1,1,2,3", "--crop", "1,1,2,3")
        failed = self._run_png_pair(candidate, reference, *args)
        self._assert_fail(failed)
        self.assertIn("difference columns: [1, 1]", failed.stdout)
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        self.assertEqual(data["difference_columns"], [1, 1])
        self.assertEqual(sum(data["difference_columns"]), data["metrics"]["differing"])
        passed = self._run_png_pair(candidate, reference, *args, "--max-mae", "255", "--json")
        passed_data = json.loads(passed.stdout)
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(passed_data["difference_columns"], [1, 1])
        combined = self._run_png_pair(candidate, reference, "--difference-columns", "--difference-rows", "--json")
        combined_data = json.loads(combined.stdout)
        self.assertEqual(combined_data["difference_rows"], [1, 1, 0, 1])
        self.assertEqual(combined_data["difference_columns"], [1, 1, 1, 0])
        self.assertEqual(sum(combined_data["difference_columns"]), sum(combined_data["difference_rows"]))
        with mock.patch.object(fidelity, "difference_columns") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_columns", json.loads(ordinary.stdout))
        helper.assert_not_called()

    def test_direct_script_and_errors(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_altered_pair(tmp)
        script = self._run_script(candidate, reference, "--difference-columns", "--json")
        self.assertEqual(len(json.loads(script.stdout)["difference_columns"]), 3)
        bad = self._run(candidate, self._write(tmp, "missing.png", b"bad"), "--difference-columns")
        self.assertEqual((bad.returncode, bad.stdout), (2, ""))
        mismatch = self._run_png_pair(make_png(1, 1, [bytes(3)]), make_png(2, 1, [bytes(6)]),
                                      "--difference-columns")
        self.assertEqual((mismatch.returncode, mismatch.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
