"""Maximum length filtering for vertical fidelity mismatch runs."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402


class TestColumnRunsMaximumLength(FidelityCliTestCase):
    def _pair(self):
        changed_columns = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        rows = []
        for y in range(9):
            pixels = bytearray(2 * 3)
            for x, changed in enumerate(changed_columns):
                if y in changed:
                    pixels[x * 3] = 20
            rows.append(bytes(pixels))
        return make_png(2, 9, rows), make_png(2, 9, [bytes(6) for _ in rows])

    def test_inclusive_maximum_and_intersection_preserve_full_summary(self):
        candidate, reference = self._pair()
        base = ("--difference-column-runs", "--longest-difference-column-run", "--json")
        plain = json.loads(self._run_png_pair(candidate, reference, *base).stdout)
        limited = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-column-run-length", "2").stdout)
        self.assertEqual(limited["difference_column_runs"], [
            {"x": 0, "y": 0, "length": 1},
            {"x": 0, "y": 2, "length": 2},
            {"x": 1, "y": 8, "length": 1},
        ])
        self.assertEqual(limited["longest_difference_column_run"],
                         plain["longest_difference_column_run"])
        self.assertEqual(limited["metrics"], plain["metrics"])
        singles = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-column-run-length", "1").stdout)
        self.assertEqual(singles["difference_column_runs"], [
            {"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 8, "length": 1},
        ])
        intersected = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-column-run-length", "2",
            "--max-difference-column-run-length", "2").stdout)
        self.assertEqual(intersected["difference_column_runs"], [
            {"x": 0, "y": 2, "length": 2},
        ])
        contradictory = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-column-run-length", "3",
            "--max-difference-column-run-length", "2").stdout)
        self.assertEqual(contradictory["difference_column_runs"], [])
        self.assertEqual(contradictory["longest_difference_column_run"],
                         plain["longest_difference_column_run"])

    def test_dependency_and_invalid_lengths_are_usage_errors_before_read(self):
        for value in ("0", "-1", "١", "1.5", "bad"):
            result = self._run("missing.png", "missing.png", "--difference-column-runs",
                               "--max-difference-column-run-length", value)
            self._assert_usage_error(result, "--max-difference-column-run-length")
        result = self._run("missing.png", "missing.png",
                           "--max-difference-column-run-length", "2")
        self._assert_usage_error(result, "requires --difference-column-runs")
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            result = self._run("missing.png", "missing.png",
                               "--min-difference-column-run-length", "2",
                               "--max-difference-column-run-length", "2")
        self._assert_usage_error(result, "--min-difference-column-run-length requires")


if __name__ == "__main__":
    unittest.main()
