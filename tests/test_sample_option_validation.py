"""Tests for sampler option compatibility checks before image access."""

from __future__ import annotations

import copy
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from tools import sample
from tools.sample_arguments import build_parser, option_error


class TestSampleOptionValidation(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_incompatible_options_are_rejected_before_png_reads(self):
        cases = (
            (("--top-colors", "1"), "--top-colors requires --histogram"),
            (("--color-bounds",), "--color-bounds requires --histogram"),
            (("--color-fractions",), "--color-fractions requires --histogram"),
            (("--color-tolerance", "0"), "--color-tolerance requires --find-color"),
            (("--match-alpha", "0"), "--match-alpha requires --find-color"),
            (("--match-pixels", "1"), "--match-pixels requires --find-color"),
            (("--match-fraction",), "--match-fraction requires --find-color"),
            (("--match-runs",), "--match-runs requires --find-color"),
            (("--match-column-runs",), "--match-column-runs requires --find-color"),
            (("--runs", "--width", "2", "--height", "2"),
             "--runs requires a single row or column unless --run-axis is given"),
            (("--run-axis", "vertical"), "--run-axis requires --runs"),
            (("--find-color", "010203", "--alpha"), "--alpha cannot be combined with --find-color"),
        )
        for options, diagnostic in cases:
            with self.subTest(options=options), \
                    mock.patch.object(sample, "read_png_size") as size, \
                    mock.patch.object(sample, "read_png") as read:
                result = self._run("unread.png", "0", "0", *options)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, f"sample: error: {diagnostic}\n")
            size.assert_not_called()
            read.assert_not_called()

    def test_first_compatibility_error_keeps_existing_order(self):
        result = self._run("unread.png", "0", "0", "--match-runs", "--find-color", "010203", "--alpha")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "sample: error: --alpha cannot be combined with --find-color\n")
        result = self._run("unread.png", "0", "0", "--match-runs", "--alpha")
        self.assertIn("sample: error: --match-runs requires --find-color\n", result.stderr)

    def test_valid_namespaces_return_none_without_mutation(self):
        parser = build_parser()
        cases = (
            ("image.png", "0", "0"),
            ("image.png", "0", "0", "--histogram", "--top-colors", "2"),
            ("image.png", "0", "0", "--find-color", "010203", "--color-tolerance", "0", "--match-alpha", "0"),
            ("image.png", "0", "0", "--width", "2", "--height", "2", "--runs", "--run-axis", "vertical"),
            ("image.png", "0", "0", "--width", "1", "--height", "1", "--runs"),
        )
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                before = copy.deepcopy(vars(args))
                self.assertIsNone(option_error(args))
                self.assertEqual(vars(args), before)


if __name__ == "__main__":
    import unittest

    unittest.main()

    def test_direct_script_reports_invalid_option_combination(self):
        result = self._run_script("missing.png", "0", "0", "--match-runs")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--match-runs requires --find-color", result.stderr)
