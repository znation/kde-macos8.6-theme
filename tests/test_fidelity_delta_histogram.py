"""Maximum-channel-delta histogram diagnostics for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_metrics import Image, compare  # noqa: E402
from tools.fidelity_pixels import delta_histogram  # noqa: E402


class TestDeltaHistogram(unittest.TestCase):
    """Test histograms of maximum per-pixel channel deltas."""
    def test_bins_track_maximum_rgba_delta_once_per_pixel(self):
        ref = Image(4, 1, bytes(12))
        cand = Image(4, 1, bytes([0, 0, 0, 7, 7, 0, 255, 0, 0, 0, 0, 0]),
                     bytes([255, 255, 255, 0]))
        histogram = delta_histogram(cand, ref)
        self.assertEqual(histogram, [
            {"delta": 0, "count": 1}, {"delta": 7, "count": 1},
            {"delta": 255, "count": 2},
        ])
        self.assertEqual(sum(item["count"] for item in histogram), 4)
        metrics = compare(cand, ref, tolerance=7)
        self.assertEqual(sum(item["count"] for item in histogram
                             if item["delta"] > 7), metrics.differing)

    def test_alpha_only_delta_and_absent_alpha_is_opaque(self):
        rgb = Image(1, 1, bytes(3))
        transparent = Image(1, 1, bytes(3), bytes([0]))
        self.assertEqual(delta_histogram(transparent, rgb),
                         [{"delta": 255, "count": 1}])
        self.assertEqual(delta_histogram(rgb, rgb), [{"delta": 0, "count": 1}])


class TestDeltaHistogramCli(FidelityCliTestCase):
    """Test histogram output, crops, and CLI validation."""
    def _pair(self):
        candidate = make_png(2, 1, [bytes([0, 0, 0, 20, 0, 0])])
        reference = make_png(2, 1, [bytes(6)])
        return candidate, reference

    def test_text_json_parity_and_tolerance_independent_histogram(self):
        candidate, reference = self._pair()
        text = self._run_png_pair(candidate, reference, "--max-mae", "10",
                                  "--delta-histogram")
        self._assert_pass(text)
        line = next(line for line in text.stdout.splitlines()
                    if line.startswith("delta histogram: "))
        histogram = json.loads(line.split(": ", 1)[1])
        report = json.loads(self._run_png_pair(
            candidate, reference, "--max-mae", "10", "--delta-histogram",
            "--json", "--tolerance", "20").stdout)
        self.assertEqual(histogram, [{"delta": 0, "count": 1},
                                     {"delta": 20, "count": 1}])
        self.assertEqual(report["delta_histogram"], histogram)
        failing = self._run_png_pair(candidate, reference, "--delta-histogram")
        self._assert_fail(failing)
        self.assertEqual(json.loads(self._run_png_pair(
            candidate, reference, "--delta-histogram", "--json").stdout)[
                "delta_histogram"], histogram)

    def test_crops_exclude_outside_pixels_and_identical_has_zero_bin(self):
        candidate = make_png(3, 1, [bytes([90, 0, 0, 0, 0, 0, 0, 0, 0])])
        reference = make_png(3, 1, [bytes(9)])
        result = self._run_png_pair(candidate, reference, "--candidate-crop",
                                    "1,0,2,1", "--crop", "1,0,2,1",
                                    "--delta-histogram", "--json")
        self.assertEqual(json.loads(result.stdout)["delta_histogram"],
                         [{"delta": 0, "count": 2}])
        same = self._run_png_pair(reference, reference, "--delta-histogram", "--json")
        self.assertEqual(json.loads(same.stdout)["delta_histogram"],
                         [{"delta": 0, "count": 3}])

    def test_flag_is_optional_and_direct_script_and_errors_work(self):
        candidate, reference = self._pair()
        ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("delta_histogram", json.loads(ordinary.stdout))
        with mock.patch.object(fidelity, "delta_histogram") as helper:
            self._run_png_pair(candidate, reference, "--json")
        helper.assert_not_called()
        tmp = self._tmp_dir()
        cand_path = self._write(tmp, "candidate.png", candidate)
        ref_path = self._write(tmp, "reference.png", reference)
        direct = self._run_script(cand_path, ref_path, "--max-mae", "10",
                                  "--delta-histogram", "--json")
        self.assertEqual(direct.returncode, 0)
        self.assertIn("delta_histogram", json.loads(direct.stdout))
        missing = self._run(cand_path, str(tmp / "missing.png"), "--delta-histogram")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
