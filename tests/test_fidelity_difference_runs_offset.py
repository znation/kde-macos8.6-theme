"""Pagination for horizontal fidelity mismatch intervals."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402


class TestDifferenceRunsOffset(FidelityCliTestCase):
    def _pair(self):
        changed_rows = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        rows = []
        for changed in changed_rows:
            pixels = bytearray(9 * 3)
            for x in changed:
                pixels[x * 3] = 20
            rows.append(bytes(pixels))
        return make_png(9, 2, rows), make_png(9, 2, [bytes(27), bytes(27)])

    def test_offset_is_global_after_length_filters(self):
        candidate, reference = self._pair()
        base = ("--difference-runs", "--difference-run-count",
                "--longest-difference-run", "--json")
        all_runs = [
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 2},
            {"x": 5, "y": 0, "length": 3}, {"x": 0, "y": 1, "length": 4},
            {"x": 8, "y": 1, "length": 1},
        ]
        page = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-runs", "2",
            "--difference-run-offset", "2").stdout)
        self.assertEqual(page["difference_runs"], all_runs[2:4])
        self.assertEqual(page["omitted_difference_runs"], 3)
        self.assertEqual(page["difference_run_offset"], 2)
        self.assertEqual(page["difference_run_count"], 5)
        self.assertEqual(page["longest_difference_run"], {"x": 0, "y": 1, "length": 4})

        minimum = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-run-length", "2",
            "--max-difference-runs", "1", "--difference-run-offset", "1").stdout)
        self.assertEqual(minimum["difference_runs"], [all_runs[2]])
        self.assertEqual(minimum["omitted_difference_runs"], 2)
        maximum = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-run-length", "2",
            "--max-difference-runs", "1", "--difference-run-offset", "1").stdout)
        self.assertEqual(maximum["difference_runs"], [all_runs[1]])
        self.assertEqual(maximum["omitted_difference_runs"], 2)
        beyond = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-runs", "2",
            "--difference-run-offset", "5").stdout)
        self.assertEqual(beyond["difference_runs"], [])
        self.assertEqual(beyond["omitted_difference_runs"], 5)

    def test_zero_text_and_omitted_offset_contract(self):
        candidate, reference = self._pair()
        text = self._run_png_pair(candidate, reference, "--difference-runs",
                                  "--max-difference-runs", "2",
                                  "--difference-run-offset", "0")
        self.assertIn("difference run offset: 0", text.stdout)
        self.assertIn('difference runs: [{"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 2}]', text.stdout)
        unpaged = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--json").stdout)
        self.assertNotIn("difference_run_offset", unpaged)
        self.assertNotIn("omitted_difference_runs", unpaged)
        capped = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--json",
            "--max-difference-runs", "2").stdout)
        self.assertNotIn("difference_run_offset", capped)

    def test_invalid_offset_and_dependencies_fail_before_reads(self):
        for value in ("-1", "+1", "1.5", " 1", "x", "١"):
            result = self._run("missing.png", "missing.png", "--difference-runs",
                               "--max-difference-runs", "2",
                               "--difference-run-offset", value)
            self._assert_usage_error(result, "--difference-run-offset")
            self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "missing.png", "--difference-runs",
                            "--max-difference-runs", "2", "--difference-run-offset")
        self._assert_usage_error(missing, "expected one argument")
        self.assertEqual(missing.stdout, "")
        for args, message in [
            (("--difference-runs", "--difference-run-offset", "0"),
             "--difference-run-offset requires --max-difference-runs"),
            (("--max-difference-runs", "2", "--difference-run-offset", "0"),
             "--max-difference-runs requires --difference-runs"),
        ]:
            result = self._run("missing.png", "missing.png", *args)
            self._assert_usage_error(result, message)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
