"""CLI coverage for the explicit RMSE comparison budget."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, solid_rgb  # noqa: E402
from tools import fidelity  # noqa: E402


class TestRmseBudget(FidelityCliTestCase):
    def test_rmse_budget_detects_sparse_error_and_replaces_default(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        result = self._run(candidate, altered, "--max-mae", "2", "--max-rmse", "8")
        self._assert_fail(result)
        self.assertIn("FAIL:", result.stdout)
        result = self._run(candidate, altered, "--max-rmse", "8.333333333333334")
        self._assert_pass(result)

    def test_exact_thresholds_combine_and_report_json_text(self):
        _, identical = solid_rgb(1, 1)
        changed = make_png(1, 1, [bytes([1, 0, 0])])
        candidate = self._write(self._tmp_dir(), "candidate.png", changed)
        reference = self._write(self._tmp_dir(), "reference.png", identical)
        passed = self._run(candidate, reference, "--max-rmse", "0.5", "--json")
        self.assertEqual(passed.returncode, 0)
        data = json.loads(passed.stdout)
        self.assertEqual(data["thresholds"]["max_rmse"], 0.5)
        self.assertTrue(data["passed"])
        failed = self._run(candidate, reference, "--max-rmse", "0.499", "--json")
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["passed"])
        self.assertIn("FAIL:", self._run(candidate, reference, "--max-rmse", "0.499").stdout)

    def test_alpha_crop_tolerance_and_upper_bound(self):
        candidate_png = make_png(3, 1, [bytes([0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255])], color_type=6)
        reference_png = make_png(3, 1, [bytes([255, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255])], color_type=6)
        result = self._run_png_pair(candidate_png, reference_png, "--candidate-crop", "1,0,2,1", "--crop", "1,0,2,1", "--tolerance", "255", "--max-rmse", "0")
        self._assert_pass(result)
        alpha_clear = make_png(1, 1, [bytes([0, 0, 0, 0])], color_type=6)
        alpha_full = make_png(1, 1, [bytes([0, 0, 0, 255])], color_type=6)
        self._assert_fail(self._run_png_pair(alpha_clear, alpha_full, "--tolerance", "255", "--max-rmse", "127.499"))
        self._assert_pass(self._run_png_pair(alpha_clear, alpha_full, "--max-rmse", "127.5"))
        all_channels_clear = make_png(1, 1, [bytes([0, 0, 0, 0])], color_type=6)
        all_channels_full = make_png(1, 1, [bytes([255, 255, 255, 255])], color_type=6)
        self._assert_pass(self._run_png_pair(all_channels_clear, all_channels_full, "--max-rmse", "255"))

    def test_invalid_values_fail_before_image_reads(self):
        for value in ("-1", "256", "nan", "inf", "1.2.3", "１"):
            with self.subTest(value=value), mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
                result = self._run("missing.png", "missing.png", "--max-rmse", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")

    def test_omitted_budget_shape_and_direct_script(self):
        _, png = solid_rgb(1, 1)
        candidate = self._write(self._tmp_dir(), "candidate.png", png)
        result = self._run(candidate, candidate, "--json")
        data = json.loads(result.stdout)
        self.assertNotIn("max_rmse", data["thresholds"])
        self.assertIn("PASS: max-mae=unset max-frac=unset tolerance=0", self._run(candidate, candidate).stdout)
        direct = self._run_script(candidate, candidate, "--max-rmse", "0", "--json")
        self.assertEqual(direct.returncode, 0)
        self.assertIn('"passed": true', direct.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()

