"""Direct contract tests for sampler scalar validators."""

from __future__ import annotations

import argparse
import unittest

from support import repo_root  # noqa: F401
from tools import sample_arguments, sample_validators as validators


class TestSampleValidators(unittest.TestCase):
    def test_valid_values_and_compatibility_exports(self):
        self.assertEqual(validators.rgb_argument("#aBcD09"), (171, 205, 9))
        self.assertEqual(validators.color_tolerance("0"), 0)
        self.assertEqual(validators.color_tolerance("255"), 255)
        self.assertEqual(validators.match_alpha("255"), 255)
        self.assertEqual(validators.match_pixels("1"), 1)
        self.assertEqual(validators.match_pixels("1000"), 1000)
        self.assertEqual(validators.match_pixel_offset("0"), 0)
        self.assertEqual(validators.match_pixel_offset("999999999999"), 999999999999)
        self.assertEqual(validators.color_fraction("0"), 0.0)
        self.assertEqual(validators.color_fraction("1e-1"), 0.1)
        self.assertEqual(validators.color_fraction("1"), 1.0)
        for name in ("rgb_argument", "color_tolerance", "match_alpha", "match_pixels",
                     "match_pixel_offset", "color_fraction"):
            self.assertIs(getattr(sample_arguments, name), getattr(validators, name))

    def test_invalid_values_are_argument_errors(self):
        cases = (
            (validators.rgb_argument, "１２３456"), (validators.rgb_argument, "12345g"),
            (validators.color_tolerance, "256"), (validators.match_alpha, "-1"),
            (validators.match_pixels, "0"), (validators.match_pixels, "1001"),
            (validators.match_pixel_offset, "-1"), (validators.color_fraction, "nan"),
            (validators.color_fraction, "1.1"), (validators.color_fraction, " 0.5"),
            (validators.match_alpha, "١"), (validators.match_pixels, "1.5"),
            (validators.match_pixel_offset, "9" * 5000),
        )
        for parser, value in cases:
            with self.subTest(parser=parser.__name__, value=value[:20]):
                with self.assertRaises(argparse.ArgumentTypeError):
                    parser(value)

    def test_range_errors_include_the_rejected_value(self):
        cases = (
            (validators.color_tolerance, "256",
             "--color-tolerance must be between 0 and 255: '256'"),
            (validators.color_tolerance, "-1",
             "--color-tolerance must be between 0 and 255: '-1'"),
            (validators.match_alpha, "256",
             "--match-alpha must be between 0 and 255: '256'"),
            (validators.match_alpha, "-1",
             "--match-alpha must be between 0 and 255: '-1'"),
            (validators.match_pixels, "0",
             "--match-pixels must be between 1 and 1000: '0'"),
            (validators.match_pixels, "1001",
             "--match-pixels must be between 1 and 1000: '1001'"),
            (validators.match_pixel_offset, "-1",
             "--match-pixel-offset must be nonnegative: '-1'"),
            (validators.color_offset, "-1",
             "--color-offset must be nonnegative: '-1'"),
        )
        for parser, value, message in cases:
            with self.subTest(value=value), self.assertRaisesRegex(
                argparse.ArgumentTypeError, f"^{message}$"
            ):
                parser(value)

    def test_fraction_range_errors_include_the_rejected_value(self):
        cases = (
            (validators.color_fraction, "1.1",
             "--min-color-fraction must be between 0 and 1: '1.1'"),
            (validators.color_fraction, "1e9999",
             "--min-color-fraction must be between 0 and 1: '1e9999'"),
            (validators.max_color_fraction, "-0.1",
             "--max-color-fraction must be between 0 and 1: '-0.1'"),
        )
        for parser, value, message in cases:
            with self.subTest(value=value), self.assertRaisesRegex(
                argparse.ArgumentTypeError, f"^{message}$"
            ):
                parser(value)

    def test_nonnegative_offset_factory_uses_its_option_and_rejects_negatives(self):
        run_offset = validators.nonnegative_offset("--run-offset")
        match_offset = validators.nonnegative_offset("--match-run-offset")

        self.assertEqual(run_offset("0"), 0)
        self.assertEqual(match_offset("999999999999"), 999999999999)
        with self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            r"^--run-offset must be nonnegative: '-1'$",
        ):
            run_offset("-1")
        with self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            r"^--match-run-offset must be nonnegative: '-1'$",
        ):
            match_offset("-1")


if __name__ == "__main__":
    unittest.main()
