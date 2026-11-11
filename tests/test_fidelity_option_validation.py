"""Refusals of contradictory fidelity filter windows before image reads."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402


class TestFidelityOptionValidation(FidelityCliTestCase):
    """A minimum above its paired maximum is refused before any image read.

    A typo'd window would otherwise exit 0 with an empty list beside full
    metrics and full-scan counts, indistinguishable from a genuine
    no-mismatch measurement. The reference-pixel sampler's five min/max
    pairs carry the same refusal; equal bounds stay a legal window that
    reaches the image read.
    """

    CASES = (
        (("--difference-runs", "--min-difference-run-length", "3",
          "--max-difference-run-length", "2"),
         "--min-difference-run-length must not exceed"
         " --max-difference-run-length (3 > 2)"),
        (("--difference-column-runs", "--min-difference-column-run-length", "3",
          "--max-difference-column-run-length", "2"),
         "--min-difference-column-run-length must not exceed"
         " --max-difference-column-run-length (3 > 2)"),
    )

    def test_contradictory_windows_are_rejected_before_reads(self):
        for options, diagnostic in self.CASES:
            with self.subTest(options=options), \
                    mock.patch.object(fidelity, "_read_source",
                                      side_effect=AssertionError("read")):
                result = self._run("missing.png", "missing.png", *options)
            self._assert_diagnostic(result, diagnostic)

    def _assert_diagnostic(self, result, diagnostic: str) -> None:
        """Assert *result* is a usage error whose last line is *diagnostic*.

        ``argparse`` prints the full usage block before the error line, so the
        pinned contract is the exact ``fidelity: error:`` line at the end of
        stderr.
        """
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.startswith("usage: fidelity"),
                        result.stderr)
        self.assertTrue(
            result.stderr.endswith(f"fidelity: error: {diagnostic}\n"),
            result.stderr)

    def test_missing_mode_flag_reports_requires_before_the_cross_check(self):
        for options, _diagnostic in self.CASES:
            mode_flag, minimum_flag = options[0], options[1]
            with self.subTest(options=options), \
                    mock.patch.object(fidelity, "_read_source",
                                      side_effect=AssertionError("read")):
                result = self._run("missing.png", "missing.png", *options[1:])
            self._assert_diagnostic(
                result, f"{minimum_flag} requires {mode_flag}")

    def test_equal_bounds_still_run_the_comparison(self):
        same = make_png(2, 1, [bytes(6)])
        horizontal = self._run_png_pair(
            same, same, "--difference-runs",
            "--min-difference-run-length", "2",
            "--max-difference-run-length", "2", "--json")
        self.assertEqual(horizontal.returncode, 0,
                         horizontal.stdout + horizontal.stderr)
        self.assertEqual(json.loads(horizontal.stdout)["difference_runs"], [])
        vertical = self._run_png_pair(
            same, same, "--difference-column-runs",
            "--min-difference-column-run-length", "2",
            "--max-difference-column-run-length", "2", "--json")
        self.assertEqual(vertical.returncode, 0,
                         vertical.stdout + vertical.stderr)
        self.assertEqual(
            json.loads(vertical.stdout)["difference_column_runs"], [])

    def test_direct_script_reports_the_same_refusal(self):
        options, diagnostic = self.CASES[0]
        script = self._run_script("missing.png", "missing.png", *options)
        self._assert_diagnostic(script, diagnostic)


if __name__ == "__main__":
    unittest.main()
