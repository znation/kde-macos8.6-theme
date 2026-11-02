"""CLI coverage for the absolute differing-pixel fidelity budget."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, solid_rgb  # noqa: E402
from tools import fidelity  # noqa: E402


class TestCountBudget(FidelityCliTestCase):
    def test_inclusive_count_and_budget_conjunction(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        self._assert_pass(self._run(candidate, altered, "--max-differing", "1"))
        self._assert_fail(self._run(candidate, altered, "--max-differing", "0"))
        self._assert_pass(self._run(candidate, altered, "--max-differing", "10"))
        self._assert_pass(self._run(candidate, altered, "--tolerance", "50", "--max-differing", "0"))
        self._assert_fail(self._run(candidate, altered, "--tolerance", "49", "--max-differing", "0"))
        self._assert_pass(self._run(candidate, altered, "--max-differing", "1", "--max-mae", "2"))
        self._assert_pass(self._run(candidate, altered, "--max-differing", "1", "--max-frac", "0.2"))
        self._assert_pass(self._run(candidate, altered, "--max-differing", "1", "--max-rmse", "9"))
        self._assert_pass(self._run(candidate, altered, "--max-differing", "1", "--max-delta", "50"))
        for option, value in (("--max-mae", "0"), ("--max-frac", "0"),
                              ("--max-rmse", "0"), ("--max-delta", "0")):
            with self.subTest(option=option):
                self._assert_fail(self._run(candidate, altered, "--max-differing", "1", option, value))
        self._assert_fail(self._run(candidate, altered, "--max-differing", "0", "--max-mae", "2"))

    def test_pixel_union_alpha_transparency_and_opaque_fallback(self):
        left = make_png(1, 1, [bytes([0, 0, 0, 0])], color_type=6)
        multi_channel_change = make_png(1, 1, [bytes([2, 3, 4, 0])], color_type=6)
        self._assert_pass(self._run_png_pair(left, multi_channel_change, "--max-differing", "1"))
        self._assert_fail(self._run_png_pair(left, multi_channel_change, "--max-differing", "0"))
        alpha_change = make_png(1, 1, [bytes([0, 0, 0, 1])], color_type=6)
        self._assert_fail(self._run_png_pair(left, alpha_change, "--max-differing", "0"))
        rgb_under_clear = make_png(1, 1, [bytes([1, 0, 0, 0])], color_type=6)
        self._assert_fail(self._run_png_pair(left, rgb_under_clear, "--max-differing", "0"))
        opaque = make_png(1, 1, [bytes([0, 0, 0])])
        opaque_changed = make_png(1, 1, [bytes([0, 0, 1])])
        self._assert_fail(self._run_png_pair(opaque, opaque_changed, "--max-differing", "0"))

    def test_crop_origins_json_text_default_and_direct_script(self):
        candidate = make_png(4, 1, [bytes([0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])])
        reference = make_png(4, 1, [bytes([0, 0, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0])])
        self._assert_pass(self._run_png_pair(candidate, reference,
            "--candidate-crop", "1,0,2,1", "--crop", "2,0,2,1", "--max-differing", "0"))
        candidate_path = self._write(self._tmp_dir(), "candidate.png", candidate)
        reference_path = self._write(self._tmp_dir(), "reference.png", reference)
        report = self._run(candidate_path, reference_path, "--max-differing", "2", "--json")
        data = json.loads(report.stdout)
        self.assertEqual(data["thresholds"]["max_differing"], 2)
        self.assertIs(type(data["thresholds"]["max_differing"]), int)
        self.assertEqual(report.returncode, 0)
        self.assertIn("PASS: max-mae=unset max-frac=unset max-differing=2 tolerance=0",
                      self._run(candidate_path, reference_path, "--max-differing", "2").stdout)
        _, same_png = solid_rgb(1, 1)
        same = self._write(self._tmp_dir(), "same.png", same_png)
        default = json.loads(self._run(same, same, "--json").stdout)
        self.assertNotIn("max_differing", default["thresholds"])
        self.assertNotIn("max-differing=", self._run(same, same).stdout)
        self._assert_pass(self._run(same, same, "--max-differing", "0"))
        direct = self._run_script(same, same, "--max-differing", "0", "--json")
        self.assertEqual(direct.returncode, 0)
        self.assertIn("--max-differing N", self._run("--help").stdout)

    def test_invalid_values_fail_before_image_reads(self):
        for value in ("-1", "1.0", "1e2", "1_0", "１", " 1", "1 ", "no", "9" * 5000):
            with self.subTest(value=value[:20]), mock.patch.object(
                fidelity, "_read_source", side_effect=AssertionError("read")
            ):
                result = self._run("missing.png", "missing.png", "--max-differing", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)
        missing = self._run("missing.png", "missing.png", "--max-differing")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
