"""Tests for sampler option compatibility checks before image access."""

from __future__ import annotations

import copy
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import solid_rgb
from tools import sample
from tools.sample_arguments import build_parser, option_error, region_error


class TestSampleOptionValidation(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_incompatible_options_are_rejected_before_png_reads(self):
        cases = (
            (("--top-colors", "1"), "--top-colors requires --histogram"),
            (("--include-color", "010203"), "--include-color requires --histogram"),
            (("--color-offset", "0"), "--color-offset requires --top-colors"),
            (("--histogram", "--color-offset", "0"), "--color-offset requires --top-colors"),
            (("--color-bounds",), "--color-bounds requires --histogram"),
            (("--color-fractions",), "--color-fractions requires --histogram"),
            (("--color-cumulative-fractions",), "--color-cumulative-fractions requires --histogram"),
            (("--min-color-fraction", "0.5"), "--min-color-fraction requires --histogram"),
            (("--max-color-fraction", "0.5"), "--max-color-fraction requires --histogram"),
            (("--max-color-count", "2"), "--max-color-count requires --histogram"),
            (("--color-tolerance", "0"), "--color-tolerance requires --find-color"),
            (("--match-alpha", "0"), "--match-alpha requires --find-color"),
            (("--match-pixels", "1"), "--match-pixels requires --find-color"),
            (("--match-fraction",), "--match-fraction requires --find-color"),
            (("--match-centroid",), "--match-centroid requires --find-color"),
            (("--match-runs",), "--match-runs requires --find-color"),
            (("--min-match-run-length", "1", "--find-color", "010203"),
             "--min-match-run-length requires --match-runs"),
            (("--max-match-run-length", "1", "--find-color", "010203"),
             "--max-match-run-length requires --match-runs"),
            (("--match-column-runs",), "--match-column-runs requires --find-color"),
            (("--min-match-column-run-length", "1", "--find-color", "010203"),
             "--min-match-column-run-length requires --match-column-runs"),
            (("--max-match-column-run-length", "1", "--find-color", "010203"),
             "--max-match-column-run-length requires --match-column-runs"),
            (("--runs", "--width", "2", "--height", "2"),
             "--runs requires a single row or column unless --run-axis is given"),
            (("--run-axis", "vertical"), "--run-axis requires --runs"),
            (("--min-run-length", "2"), "--min-run-length requires --runs"),
            (("--max-run-length", "2"), "--max-run-length requires --runs"),
            (("--run-color", "010203"), "--run-color requires --runs"),
            (("--exclude-run-color", "010203"), "--exclude-run-color requires --runs"),
            (("--histogram", "--run-color", "010203"), "--run-color requires --runs"),
            (("--histogram", "--exclude-run-color", "010203"), "--exclude-run-color requires --runs"),
            (("--find-color", "010203", "--run-color", "010203"), "--run-color requires --runs"),
            (("--find-color", "010203", "--exclude-run-color", "010203"),
             "--exclude-run-color requires --runs"),
            (("--min-run-length", "2", "--max-run-length", "2"), "--min-run-length requires --runs"),
            (("--histogram", "--max-run-length", "2"), "--max-run-length requires --runs"),
            (("--find-color", "010203", "--max-run-length", "2"), "--max-run-length requires --runs"),
            (("--min-run-length", "2", "--max-run-length", "1"),
             "--min-run-length requires --runs"),
            (("--find-color", "010203", "--alpha"), "--alpha cannot be combined with --find-color"),
        )
        for options, diagnostic in cases:
            with self.subTest(options=options), \
                    mock.patch.object(sample, "read_png_size") as size, \
                    mock.patch.object(sample, "read_png") as read, \
                    mock.patch.object(sample.os, "open") as open_image:
                result = self._run("unread.png", "0", "0", *options)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, f"sample: error: {diagnostic}\n")
            size.assert_not_called()
            read.assert_not_called()
            open_image.assert_not_called()

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
            ("image.png", "0", "0", "--histogram", "--include-color", "010203"),
            ("image.png", "0", "0", "--histogram", "--top-colors", "2", "--color-offset", "0"),
            ("image.png", "0", "0", "--histogram", "--min-color-fraction", "0.5"),
            ("image.png", "0", "0", "--histogram", "--color-cumulative-fractions"),
            ("image.png", "0", "0", "--find-color", "010203", "--color-tolerance", "0", "--match-alpha", "0"),
            ("image.png", "0", "0", "--width", "2", "--height", "2", "--runs", "--run-axis", "vertical"),
            ("image.png", "0", "0", "--width", "1", "--height", "1", "--runs"),
            ("image.png", "0", "0", "--runs", "--min-run-length", "1"),
            ("image.png", "0", "0", "--runs", "--max-run-length", "1"),
            ("image.png", "0", "0", "--runs", "--run-color", "010203"),
            ("image.png", "0", "0", "--runs", "--exclude-run-color", "010203"),
            ("image.png", "0", "0", "--runs", "--min-run-length", "1", "--max-run-length", "2"),
            ("image.png", "0", "0", "--find-color", "010203", "--match-runs",
             "--min-match-run-length", "1"),
        )
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                before = copy.deepcopy(vars(args))
                self.assertIsNone(option_error(args))
                self.assertEqual(vars(args), before)

    def test_region_error_validates_pixel_and_rectangle_bounds_without_mutation(self):
        parser = build_parser()
        cases = (
            (("0", "0"), 4, 3, None),
            (("3", "2"), 4, 3, None),
            (("0", "0", "--width", "4", "--height", "3"), 4, 3, None),
            (("3", "0", "--width", "1", "--height", "3"), 4, 3, None),
            (("0", "2", "--width", "4", "--height", "1"), 4, 3, None),
            (("-1", "0"), 4, 3, "pixel (-1, 0) is outside the 4x3 image"),
            (("0", "-1", "--width", "2"), 4, 3,
             "region (0, -1) 2x1 is outside the 4x3 image"),
            (("4", "0"), 4, 3, "pixel (4, 0) is outside the 4x3 image"),
            (("0", "3"), 4, 3, "pixel (0, 3) is outside the 4x3 image"),
            (("3", "0", "--width", "2"), 4, 3,
             "region (3, 0) 2x1 is outside the 4x3 image"),
            (("0", "2", "--height", "2"), 4, 3,
             "region (0, 2) 1x2 is outside the 4x3 image"),
            (("3", "2", "--width", "2", "--height", "2"), 4, 3,
             "region (3, 2) 2x2 is outside the 4x3 image"),
        )
        for argv, width, height, expected in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(("image.png", *argv))
                before = copy.deepcopy(vars(args))
                self.assertEqual(region_error(args, width, height), expected)
                self.assertEqual(vars(args), before)

    def test_cli_reports_header_bounds_before_decoding(self):
        image = self._write(self._tmp_dir(), "header-only.png", solid_rgb(4, 3)[1])
        cases = (
            (("4", "0"), "pixel (4, 0) is outside the 4x3 image"),
            (("-1", "0", "--width", "2"),
             "region (-1, 0) 2x1 is outside the 4x3 image"),
            (("3", "2", "--width", "2", "--height", "2"),
             "region (3, 2) 2x2 is outside the 4x3 image"),
        )
        for argv, diagnostic in cases:
            with self.subTest(argv=argv), \
                    mock.patch.object(sample, "read_png_size", return_value=(4, 3)), \
                    mock.patch.object(sample, "read_png", side_effect=AssertionError("decoded invalid region")):
                    result = self._run(image, *argv)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, f"sample: error: {diagnostic}\n")

    def test_package_and_direct_script_report_same_invalid_rectangle(self):
        from support.png_fixtures import rgb_image

        _, data = rgb_image(4, 3, lambda x, y: (x, y, x + y))
        path = self._write(self._tmp_dir(), "reference.png", data)
        arguments = (path, "3", "2", "--width", "2", "--height", "2")
        package = self._run(*arguments)
        direct = self._run_script(*arguments)
        self.assertEqual((package.returncode, package.stdout, package.stderr),
                         (direct.returncode, direct.stdout, direct.stderr))
        self.assertEqual(package.stderr,
                         "sample: error: region (3, 2) 2x2 is outside the 4x3 image\n")


if __name__ == "__main__":
    import unittest

    unittest.main()

    def test_direct_script_reports_invalid_option_combination(self):
        result = self._run_script("missing.png", "0", "0", "--match-runs")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--match-runs requires --find-color", result.stderr)
