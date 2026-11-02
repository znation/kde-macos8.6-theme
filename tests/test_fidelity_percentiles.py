"""Nearest-rank maximum RGBA delta percentiles for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_metrics import Image  # noqa: E402
from tools.fidelity_pixels import delta_histogram  # noqa: E402
from tools.fidelity_reports import delta_percentiles  # noqa: E402


class TestDeltaPercentiles(unittest.TestCase):
    def test_nearest_rank_boundaries_and_sparse_tail(self):
        self.assertEqual(delta_percentiles([
            {"delta": 0, "count": 1}, {"delta": 10, "count": 94},
            {"delta": 20, "count": 4}, {"delta": 255, "count": 1},
        ]), {"p50": 10, "p95": 10, "p99": 20})
        self.assertEqual(delta_percentiles([{"delta": 255, "count": 1}]),
                         {"p50": 255, "p95": 255, "p99": 255})
        self.assertEqual(delta_percentiles([{"delta": 0, "count": 4}]),
                         {"p50": 0, "p95": 0, "p99": 0})
        # Independently sorted values pin upward rounding at the rank boundary.
        values = [0, 3, 3, 7, 255]
        expected = {f"p{p}": values[(p * len(values) + 99) // 100 - 1]
                    for p in (50, 95, 99)}
        self.assertEqual(delta_percentiles([
            {"delta": 0, "count": 1}, {"delta": 3, "count": 2},
            {"delta": 7, "count": 1}, {"delta": 255, "count": 1},
        ]), expected)

    def test_histogram_percentiles_include_alpha_and_opaque_rgb(self):
        self.assertEqual(delta_percentiles(delta_histogram(
            Image(2, 1, bytes(6), bytes([255, 0])), Image(2, 1, bytes(6)))),
            {"p50": 0, "p95": 255, "p99": 255})


class TestDeltaPercentilesCli(FidelityCliTestCase):
    def test_text_json_parity_percentiles_only_and_gate_independence(self):
        candidate = make_png(5, 1, [bytes([0, 0, 0] * 4 + [25, 0, 0])])
        reference = make_png(5, 1, [bytes(15)])
        text = self._run_png_pair(candidate, reference, "--delta-percentiles", "--max-mae", "10")
        self._assert_pass(text)
        values = json.loads(next(line for line in text.stdout.splitlines()
                                 if line.startswith("delta percentiles: ")).split(": ", 1)[1])
        report = json.loads(self._run_png_pair(candidate, reference,
                                               "--delta-percentiles", "--json",
                                               "--tolerance", "25").stdout)
        self.assertEqual(values, {"p50": 0, "p95": 25, "p99": 25})
        self.assertEqual(report["delta_percentiles"], values)
        self.assertNotIn("delta_histogram", report)
        self.assertEqual(json.loads(self._run_png_pair(
            candidate, reference, "--delta-percentiles", "--delta-histogram", "--json"
        ).stdout)["delta_histogram"], [{"delta": 0, "count": 4},
                                      {"delta": 25, "count": 1}])
        failed = self._run_png_pair(candidate, reference, "--delta-percentiles")
        self._assert_fail(failed)

    def test_optional_shared_scan_crops_alpha_and_direct_script(self):
        candidate = make_png(3, 1, [bytes([99, 0, 0, 0, 0, 0, 0, 0, 0])])
        reference = make_png(3, 1, [bytes(9)])
        with mock.patch.object(fidelity, "delta_histogram", wraps=delta_histogram) as helper:
            result = self._run_png_pair(candidate, reference, "--delta-percentiles",
                                        "--delta-histogram", "--candidate-crop", "1,0,2,1",
                                        "--crop", "1,0,2,1", "--json")
        helper.assert_called_once()
        self.assertEqual(json.loads(result.stdout)["delta_percentiles"],
                         {"p50": 0, "p95": 0, "p99": 0})
        with mock.patch.object(fidelity, "delta_histogram") as helper:
            self._run_png_pair(candidate, reference, "--json")
        helper.assert_not_called()
        tmp = self._tmp_dir()
        cp = self._write(tmp, "candidate.png", candidate)
        rp = self._write(tmp, "reference.png", reference)
        direct = self._run_script(cp, rp, "--delta-percentiles", "--tolerance", "99", "--json")
        self.assertEqual(direct.returncode, 0)
        self.assertIn("delta_percentiles", json.loads(direct.stdout))

        missing = self._run(cp, str(tmp / "absent.png"), "--delta-percentiles")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        wrong_size = make_png(1, 1, [bytes(3)])
        wrong_path = self._write(tmp, "wrong-size.png", wrong_size)
        size_error = self._run(cp, wrong_path, "--delta-percentiles")
        self.assertEqual((size_error.returncode, size_error.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()

