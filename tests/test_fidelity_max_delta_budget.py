"""CLI coverage for the worst-channel fidelity budget."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, solid_rgb  # noqa: E402
from tools import fidelity  # noqa: E402


class TestMaxDeltaBudget(FidelityCliTestCase):
    """Test maximum-delta budgets and CLI validation."""
    def test_sparse_error_and_combined_budgets(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        self._assert_pass(self._run(candidate, altered, "--max-mae", "2"))
        self._assert_pass(self._run(candidate, altered, "--max-frac", "0.2"))
        result = self._run(candidate, altered, "--max-delta", "49", "--json")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["passed"])
        self.assertEqual(json.loads(self._run(candidate, altered, "--max-delta", "50", "--json").stdout)["thresholds"]["max_delta"], 50)
        self._assert_pass(self._run(candidate, altered, "--max-mae", "2", "--max-delta", "50"))
        self._assert_fail(self._run(candidate, altered, "--max-frac", "0.2", "--max-delta", "49"))

    def test_tolerance_alpha_transparent_rgb_and_caps(self):
        _, identical = solid_rgb(1, 1)
        same_path = self._write(self._tmp_dir(), "same.png", identical)
        self._assert_pass(self._run(same_path, same_path, "--max-delta", "0"))
        self._assert_pass(self._run(same_path, same_path, "--max-delta", "255"))
        clear = make_png(1, 1, [bytes([0, 0, 0, 0])], color_type=6)
        different_clear = make_png(1, 1, [bytes([255, 0, 0, 0])], color_type=6)
        self._assert_fail(self._run_png_pair(clear, different_clear, "--tolerance", "255", "--max-delta", "254"))
        self._assert_pass(self._run_png_pair(clear, different_clear, "--max-delta", "255"))
        opaque = make_png(1, 1, [bytes([0, 0, 0, 255])], color_type=6)
        self._assert_fail(self._run_png_pair(clear, opaque, "--tolerance", "255", "--max-delta", "254"))
        self._assert_pass(self._run_png_pair(clear, opaque, "--max-delta", "255"))

    def test_crops_json_text_and_omitted_shape(self):
        candidate = make_png(3, 1, [bytes([0, 0, 0, 0, 0, 0, 0, 0, 0])])
        reference = make_png(3, 1, [bytes([255, 0, 0, 0, 0, 0, 0, 0, 0])])
        cropped = self._run_png_pair(candidate, reference, "--candidate-crop", "1,0,2,1", "--crop", "1,0,2,1", "--max-delta", "0")
        self._assert_pass(cropped)
        self._assert_fail(self._run_png_pair(candidate, reference, "--candidate-crop", "0,0,2,1", "--crop", "0,0,2,1", "--max-delta", "0"))
        _, png = solid_rgb(1, 1)
        path = self._write(self._tmp_dir(), "plain.png", png)
        default = self._run(path, path, "--json")
        self.assertNotIn("max_delta", json.loads(default.stdout)["thresholds"])
        self.assertIn("PASS: max-mae=unset max-frac=unset tolerance=0", self._run(path, path).stdout)
        self.assertIn("PASS:", self._run(path, path, "--max-delta", "0").stdout)
        direct = self._run_script(path, path, "--max-delta", "0", "--json")
        self.assertEqual(direct.returncode, 0)
        self.assertIn('"max_delta": 0', direct.stdout)
        help_result = self._run(path, path, "--help")
        self.assertIn("--max-delta N", help_result.stdout)

    def test_invalid_values_fail_before_image_reads(self):
        for value in ("-1", "256", "1.0", "nan", "1x", "１"):
            with self.subTest(value=value), mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
                result = self._run("missing.png", "missing.png", "--max-delta", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        result = self._run("missing.png", "missing.png", "--max-delta")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
