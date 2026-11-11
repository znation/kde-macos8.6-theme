"""Scalar vertical mismatch-run count diagnostics."""

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import (  # noqa: E402
    FidelityCliTestCase,
    patched_column_calls,
)
from support.png_fixtures import make_png  # noqa: E402
from tools.fidelity_spatial import difference_column_run_count  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceColumnRunCount(unittest.TestCase):
    def test_streaming_count_uses_vertical_maximal_intervals(self):
        masks = ("101", "100", "001", "111")
        values = bytes(int(bit) * 20 for row in masks for bit in row)
        rgb = b"".join(bytes((value, 0, 0)) for value in values)
        self.assertEqual(difference_column_run_count(Image(3, 4, rgb),
                                                     Image(3, 4, bytes(len(rgb))), 0), 5)
        self.assertEqual(difference_column_run_count(Image(3, 4, rgb),
                                                     Image(3, 4, bytes(len(rgb))), 255), 0)
        self.assertEqual(difference_column_run_count(Image(3, 2, bytes((9, 0, 0) * 6)),
                                                     Image(3, 2, bytes(18)), 0), 3)
        self.assertEqual(difference_column_run_count(Image(1, 3, bytes((9, 0, 0) * 3)),
                                                     Image(1, 3, bytes(9)), 0), 1)
        self.assertEqual(difference_column_run_count(
            Image(1, 1, bytes((5, 0, 0)), bytes((0,))),
            Image(1, 1, bytes((5, 0, 0)), bytes((255,))), 254), 1)
        self.assertEqual(difference_column_run_count(
            Image(1, 1, bytes((5, 0, 0)), bytes((0,))),
            Image(1, 1, bytes((0, 0, 0)), bytes((0,))), 0), 1)


class TestDifferenceColumnRunCountCli(FidelityCliTestCase):
    @staticmethod
    def _pair():
        masks = ("101", "100", "001", "111")

        def image(origin_x, patterned):
            rows = []
            for y in range(6):
                row = bytearray(15)
                for x in range(5):
                    local_x, local_y = x - origin_x, y - 1
                    if patterned and 0 <= local_x < 3 and 0 <= local_y < 4 and masks[local_y][local_x] == "1":
                        row[x * 3] = 20
                rows.append(bytes(row))
            return make_png(5, 6, rows)

        return image(1, True), image(2, False)

    def test_count_filters_origins_and_output(self):
        candidate, reference = self._pair()
        crops = ("--candidate-crop", "1,1,3,4", "--crop", "2,1,3,4")
        result = self._run_png_pair(candidate, reference, *crops,
                                    "--difference-column-run-count", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["difference_column_run_count"], 5)
        self.assertEqual(data["metrics"]["differing"], 7)
        self.assertNotIn("difference_column_runs", data)
        text = self._run_png_pair(candidate, reference, *crops, "--difference-column-run-count")
        self.assertIn("difference column run count: 5", text.stdout)

        with patched_column_calls(
                run_count=mock.Mock(side_effect=AssertionError("extra counter scan"))):
            listed = self._run_png_pair(candidate, reference, *crops,
                                        "--difference-column-runs", "--difference-column-run-count", "--json")
        records = json.loads(listed.stdout)["difference_column_runs"]
        self.assertEqual([record["length"] for record in records], [2, 1, 1, 1, 2])
        for flag, value, expected in (("--min-difference-column-run-length", "2", 2),
                                      ("--max-difference-column-run-length", "1", 3)):
            filtered = self._run_png_pair(candidate, reference, *crops, "--difference-column-runs",
                                          "--difference-column-run-count", flag, value, "--json")
            data = json.loads(filtered.stdout)
            self.assertEqual(data["difference_column_run_count"], 5)
            self.assertEqual(len(data["difference_column_runs"]), expected)
        ordinary = self._run_png_pair(candidate, reference, *crops, "--json")
        self.assertNotIn("difference_column_run_count", json.loads(ordinary.stdout))
        self.assertNotIn("difference column run count:", ordinary.stdout)

    def test_empty_and_direct_script(self):
        blank = make_png(1, 2, [bytes(3), bytes(3)])
        result = self._run_png_pair(blank, blank, "--difference-column-run-count", "--json")
        self.assertEqual(json.loads(result.stdout)["difference_column_run_count"], 0)
        path = self._write(self._tmp_dir(), "blank.png", blank)
        direct = self._run_script(path, path, "--difference-column-run-count", "--json")
        self.assertEqual(json.loads(direct.stdout)["difference_column_run_count"], 0)
        self.assertIn("--difference-column-run-count", self._run("--help").stdout)


if __name__ == "__main__":
    unittest.main()
