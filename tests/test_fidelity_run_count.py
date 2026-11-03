"""Scalar horizontal mismatch-run count diagnostics."""

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_spatial import difference_run_count  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRunCount(unittest.TestCase):
    def test_streaming_count_handles_rows_and_tolerance(self):
        rgb = (bytes([11, 0, 0, 12, 0, 0, 0, 0, 0, 11, 0, 0])
               + bytes(12)
               + bytes([11, 0, 0, 12, 0, 0, 13, 0, 0, 14, 0, 0]))
        candidate = Image(4, 3, rgb)
        reference = Image(4, 3, bytes(len(rgb)))
        self.assertEqual(difference_run_count(candidate, reference, 10), 3)
        self.assertEqual(difference_run_count(candidate, reference, 255), 0)


class TestDifferenceRunCountCli(FidelityCliTestCase):
    def test_count_json_text_and_no_extra_scan_with_run_list(self):
        candidate = make_png(4, 3, [bytes([11, 0, 0, 12, 0, 0, 0, 0, 0, 11, 0, 0]),
                                   bytes(12),
                                   bytes([11, 0, 0, 12, 0, 0, 13, 0, 0, 14, 0, 0])])
        reference = make_png(4, 3, [bytes(12), bytes(12), bytes(12)])
        with mock.patch.object(fidelity, "difference_runs", wraps=fidelity.difference_runs):
            result = self._run_png_pair(candidate, reference, "--difference-run-count", "--json")
        self.assertEqual(json.loads(result.stdout)["difference_run_count"], 3)
        self.assertEqual(json.loads(result.stdout)["metrics"]["differing"], 7)
        text = self._run_png_pair(candidate, reference, "--difference-run-count")
        self.assertIn("difference run count: 3", text.stdout)
        with mock.patch.object(fidelity, "difference_run_count", side_effect=AssertionError):
            listed = self._run_png_pair(candidate, reference, "--difference-run-count",
                                         "--difference-runs", "--json")
        self.assertEqual(json.loads(listed.stdout)["difference_run_count"], 3)
        ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_run_count", json.loads(ordinary.stdout))



class TestCountDifferenceRuns(unittest.TestCase):
    def test_counts_maximal_runs_at_row_edges(self):
        values = (1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1)
        candidate = Image(4, 3, b"".join(bytes((value, 0, 0)) for value in values))
        reference = Image(4, 3, bytes(36))
        self.assertEqual(difference_run_count(candidate, reference, 0), 3)

    def test_empty_degenerate_alpha_and_tolerance_cases(self):
        self.assertEqual(difference_run_count(Image(2, 2, bytes(12)),
                                               Image(2, 2, bytes(12)), 0), 0)
        self.assertEqual(difference_run_count(Image(3, 2, bytes((9, 0, 0) * 6)),
                                               Image(3, 2, bytes(18)), 0), 2)
        self.assertEqual(difference_run_count(Image(1, 3, bytes((9, 0, 0) * 3)),
                                               Image(1, 3, bytes(9)), 0), 3)
        self.assertEqual(difference_run_count(Image(1, 1, bytes((9, 0, 0))),
                                               Image(1, 1, bytes(3)), 0), 1)
        boundary = Image(4, 1, bytes((11, 0, 0, 12, 0, 0, 10, 0, 0, 11, 0, 0)))
        self.assertEqual(difference_run_count(boundary, Image(4, 1, bytes(12)), 10), 2)
        self.assertEqual(difference_run_count(Image(1, 1, bytes((9, 0, 0)), bytes((0,))),
                                               Image(1, 1, bytes((9, 0, 0)), bytes((255,))), 254), 1)
        self.assertEqual(difference_run_count(Image(1, 1, bytes((9, 0, 0)), bytes((0,))),
                                               Image(1, 1, bytes(3), bytes((0,))), 8), 1)
        self.assertEqual(difference_run_count(Image(1, 1, bytes((255, 0, 0))),
                                               Image(1, 1, bytes(3)), 255), 0)


class TestFidelityRunCountCli(FidelityCliTestCase):
    @staticmethod
    def _pair():
        masks = ("1101", "0000", "1111")

        def image(origin_x, patterned):
            rows = []
            for y in range(5):
                row = bytearray(18)
                for x in range(6):
                    local_x, local_y = x - origin_x, y - 1
                    if (patterned and 0 <= local_x < 4 and 0 <= local_y < 3
                            and masks[local_y][local_x] == "1"):
                        row[x * 3] = 20
                rows.append(bytes(row))
            return make_png(6, 5, rows)

        return image(1, True), image(2, False)

    def test_count_json_text_filters_and_crop_origins(self):
        candidate, reference = self._pair()
        crops = ("--candidate-crop", "1,1,4,3", "--crop", "2,1,4,3")
        result = self._run_png_pair(candidate, reference, *crops,
                                    "--difference-run-count", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["difference_run_count"], 3)
        self.assertEqual(data["metrics"]["differing"], 7)
        self.assertNotIn("difference_runs", data)
        self.assertNotIn("difference_column_runs", data)
        text = self._run_png_pair(candidate, reference, *crops, "--difference-run-count")
        self.assertIn("difference run count: 3", text.stdout)

        combined = self._run_png_pair(candidate, reference, *crops,
                                      "--difference-runs", "--difference-run-count", "--json")
        data = json.loads(combined.stdout)
        self.assertEqual(data["difference_runs"], [
            {"x": 0, "y": 0, "length": 2},
            {"x": 3, "y": 0, "length": 1},
            {"x": 0, "y": 2, "length": 4},
        ])
        self.assertEqual(data["difference_run_count"], 3)
        for cutoff in (("--min-difference-run-length", "3"),
                       ("--max-difference-run-length", "1")):
            filtered = self._run_png_pair(candidate, reference, *crops,
                                          "--difference-runs", "--difference-run-count",
                                          *cutoff, "--json")
            data = json.loads(filtered.stdout)
            self.assertEqual(data["difference_run_count"], 3)
            self.assertEqual(len(data["difference_runs"]), 1)
        conflict = self._run_png_pair(candidate, reference, *crops, "--difference-runs",
                                      "--difference-run-count", "--min-difference-run-length", "4",
                                      "--max-difference-run-length", "1", "--json")
        data = json.loads(conflict.stdout)
        self.assertEqual(data["difference_run_count"], 3)
        self.assertEqual(data["difference_runs"], [])

    def test_scan_selection_and_default_omission(self):
        candidate, reference = self._pair()
        with mock.patch.object(fidelity, "difference_run_count",
                               side_effect=AssertionError("extra count scan")):
            combined = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                          "--crop", "2,1,4,3", "--difference-runs",
                                          "--difference-run-count", "--json")
        self.assertEqual(json.loads(combined.stdout)["difference_run_count"], 3)
        with mock.patch.object(fidelity, "difference_runs",
                               side_effect=AssertionError("full list collected")):
            count_only = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                            "--crop", "2,1,4,3",
                                            "--difference-run-count", "--json")
        self.assertEqual(json.loads(count_only.stdout)["difference_run_count"], 3)
        with mock.patch.object(fidelity, "difference_run_count") as counter:
            ordinary = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                           "--crop", "2,1,4,3", "--json")
        counter.assert_not_called()
        self.assertNotIn("difference_run_count", json.loads(ordinary.stdout))
        self.assertNotIn("difference run count:", ordinary.stdout)

        failing = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                     "--crop", "2,1,4,3", "--max-differing", "0")
        failing_counted = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                             "--crop", "2,1,4,3", "--max-differing", "0",
                                             "--difference-run-count", "--json")
        self.assertEqual(failing.returncode, 1)
        self.assertEqual(failing_counted.returncode, failing.returncode)
        passing = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                     "--crop", "2,1,4,3", "--max-differing", "12")
        passing_counted = self._run_png_pair(candidate, reference, "--candidate-crop", "1,1,4,3",
                                             "--crop", "2,1,4,3", "--max-differing", "12",
                                             "--difference-run-count", "--json")
        self.assertEqual(passing.returncode, 0)
        self.assertEqual(passing_counted.returncode, passing.returncode)

    def test_zero_count_and_direct_script(self):
        blank = make_png(1, 3, [bytes(3), bytes(3), bytes(3)])
        result = self._run_png_pair(blank, blank, "--difference-run-count", "--json")
        self.assertEqual(json.loads(result.stdout)["difference_run_count"], 0)
        path = self._write(self._tmp_dir(), "blank.png", blank)
        direct = self._run_script(path, path, "--difference-run-count", "--json")
        self.assertEqual(json.loads(direct.stdout)["difference_run_count"], 0)
        self.assertIn("--difference-run-count", self._run("--help").stdout)


if __name__ == "__main__":
    unittest.main()
