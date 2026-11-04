"""Parser construction and argument behavior for the fidelity CLI."""

from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from tools import fidelity
from tools import fidelity_arguments
from tools.fidelity_cli_parser import build_parser


class TestFidelityCliParser(unittest.TestCase):
    def test_per_channel_limits_accept_bounds_and_reject_values_outside_them(self):
        for validator in (
            fidelity_arguments.max_mae,
            fidelity_arguments.max_rmse,
            fidelity_arguments.max_delta,
            fidelity_arguments.tolerance,
        ):
            with self.subTest(validator=validator.__name__):
                self.assertEqual(validator("0"), 0)
                self.assertEqual(validator("255"), 255)
                for value in ("-1", "256"):
                    with self.subTest(value=value), self.assertRaises(
                        fidelity_arguments.argparse.ArgumentTypeError
                    ):
                        validator(value)

        for validator in (fidelity_arguments.max_mae, fidelity_arguments.max_rmse):
            for value in ("nan", "inf", "-inf"):
                with self.subTest(validator=validator.__name__, value=value), \
                        self.assertRaises(
                            fidelity_arguments.argparse.ArgumentTypeError
                        ):
                    validator(value)

    def test_max_frac_accepts_endpoints_and_rejects_nonfinite_or_out_of_range(self):
        self.assertEqual(fidelity_arguments.max_frac("0"), 0.0)
        self.assertEqual(fidelity_arguments.max_frac("1"), 1.0)
        for value in ("-0.01", "1.01", "nan", "inf", "-inf"):
            with self.subTest(value=value), self.assertRaises(
                fidelity_arguments.argparse.ArgumentTypeError
            ):
                fidelity_arguments.max_frac(value)

    def test_max_differing_accepts_zero_and_rejects_negative_counts(self):
        self.assertEqual(fidelity_arguments.max_differing("0"), 0)
        self.assertEqual(fidelity_arguments.max_differing("-0"), 0)
        self.assertEqual(fidelity_arguments.max_differing("123"), 123)
        for value in ("-1",):
            with self.subTest(value=value), self.assertRaisesRegex(
                fidelity_arguments.argparse.ArgumentTypeError,
                "--max-differing must not be negative",
            ):
                fidelity_arguments.max_differing(value)

    def test_worst_pixel_limit_accepts_inclusive_bounds_and_ascii_digits_only(self):
        self.assertEqual(fidelity_arguments.worst_pixel_limit("1"), 1)
        self.assertEqual(fidelity_arguments.worst_pixel_limit("1000"), 1000)
        for value in ("0", "1001", "+1", "１", "1.0", ""):
            with self.subTest(value=value), self.assertRaisesRegex(
                fidelity_arguments.argparse.ArgumentTypeError,
                "ASCII integer from 1 to 1000",
            ):
                fidelity_arguments.worst_pixel_limit(value)

    def test_worst_pixel_offset_accepts_nonnegative_ascii_decimal(self):
        self.assertEqual(fidelity_arguments.worst_pixel_offset("0"), 0)
        self.assertEqual(fidelity_arguments.worst_pixel_offset("123"), 123)
        for value in ("-1", "+1", "1.0", "", "١"):
            with self.subTest(value=value), self.assertRaisesRegex(
                fidelity_arguments.argparse.ArgumentTypeError, "nonnegative ASCII integer"
            ):
                fidelity_arguments.worst_pixel_offset(value)

    def test_crop_parser_accepts_field_whitespace_and_names_empty_fields(self):
        self.assertEqual(fidelity_arguments.parse_crop(" 1, 2 , 3,4 "), (1, 2, 3, 4))
        for value, diagnostic in (
            ("1,,3,4", "crop field 2 is empty"),
            ("1,2,3,", "crop field 4 is empty"),
        ):
            with self.subTest(value=value), self.assertRaisesRegex(
                fidelity_arguments.argparse.ArgumentTypeError, diagnostic
            ):
                fidelity_arguments.parse_crop(value)

    def test_help_text_is_stable(self):
        help_text = build_parser().format_help()
        self.assertIn("usage: fidelity [-h] [--json] [--worst-pixels N]", help_text)
        self.assertIn("--candidate-crop X,Y,W,H", help_text)
        self.assertIn("--worst-pixel-offset K", help_text)
        self.assertIn("--max-differing N", help_text)
        self.assertIn("exit status: 0 when the comparison passes", help_text)
        self.assertIn("--difference-column-runs", help_text)
        self.assertIn("--difference-column-run-count", help_text)
        self.assertIn("--difference-centroid", help_text)
        self.assertIn("--longest-difference-run", help_text)
        self.assertIn("--longest-difference-column-run", help_text)
        self.assertIn("--min-difference-run-length N", help_text)
        self.assertIn("--min-difference-column-run-length N", help_text)
        self.assertIn("--max-difference-column-run-length N", help_text)
        self.assertIn("--max-difference-column-runs N", help_text)
        self.assertIn("--max-difference-runs N", help_text)

    def test_defaults_and_explicit_options(self):
        first = build_parser()
        second = build_parser()
        defaults = first.parse_args(["candidate.png", "reference.png"])
        self.assertEqual(vars(defaults), {
            "candidate": "candidate.png",
            "reference": "reference.png",
            "json": False,
            "worst_pixels": None,
            "worst_pixel_offset": None,
            "channel_counts": False,
            "channel_bias": False,
            "channel_maxima": False,
            "difference_rows": False,
            "difference_columns": False,
            "difference_row_bounds": False,
            "difference_column_bounds": False,
            "difference_runs": False,
            "difference_run_count": False,
            "difference_column_run_count": False,
            "min_difference_run_length": None,
            "max_difference_run_length": None,
            "max_difference_runs": None,
            "difference_run_offset": None,
            "min_difference_column_run_length": None,
            "max_difference_column_run_length": None,
            "max_difference_column_runs": None,
            "difference_column_runs": False,
            "difference_centroid": False,
            "longest_difference_run": False,
            "longest_difference_column_run": False,
            "delta_histogram": False,
            "delta_percentiles": False,
            "explain_worst": False,
            "candidate_crop": None,
            "crop": None,
            "tolerance": 0,
            "max_mae": None,
            "max_frac": None,
            "max_rmse": None,
            "max_delta": None,
            "max_differing": None,
        })
        explicit = second.parse_args([
            "candidate.png", "reference.png", "--json", "--worst-pixels", "7",
            "--worst-pixel-offset", "3",
            "--candidate-crop", "1,2,3,4", "--crop", "5,6,7,8",
            "--channel-counts", "--channel-bias", "--channel-maxima",
            "--difference-rows", "--difference-columns", "--difference-row-bounds",
            "--difference-column-bounds", "--difference-runs", "--difference-run-count",
            "--min-difference-run-length", "2",
            "--max-difference-run-length", "4",
            "--max-difference-runs", "6",
            "--difference-run-offset", "2",
            "--min-difference-column-run-length", "3",
            "--max-difference-column-run-length", "5",
            "--difference-column-runs", "--difference-column-run-count", "--difference-centroid", "--longest-difference-run", "--longest-difference-column-run", "--delta-histogram", "--delta-percentiles",
            "--explain-worst", "--tolerance", "9", "--max-mae", "1.5",
            "--max-frac", "0.25", "--max-rmse", "2.5", "--max-delta", "12",
            "--max-differing", "3",
        ])
        self.assertEqual(explicit.candidate_crop, (1, 2, 3, 4))
        self.assertEqual(explicit.crop, (5, 6, 7, 8))
        self.assertEqual((explicit.worst_pixels, explicit.tolerance), (7, 9))
        self.assertEqual(explicit.worst_pixel_offset, 3)
        self.assertTrue(explicit.difference_run_count)
        self.assertEqual((explicit.max_mae, explicit.max_frac, explicit.max_rmse),
                         (1.5, 0.25, 2.5))
        self.assertEqual((explicit.max_delta, explicit.max_differing), (12, 3))
        self.assertEqual(explicit.min_difference_run_length, 2)
        self.assertEqual(explicit.max_difference_run_length, 4)
        self.assertEqual(explicit.max_difference_runs, 6)
        self.assertEqual(explicit.difference_run_offset, 2)
        self.assertEqual(explicit.min_difference_column_run_length, 3)
        self.assertEqual(explicit.max_difference_column_run_length, 5)
        self.assertTrue(all(getattr(explicit, name) for name in (
            "json", "channel_counts", "channel_bias", "channel_maxima",
            "difference_rows", "difference_columns", "difference_row_bounds",
            "difference_column_bounds", "difference_runs", "difference_column_runs",
            "difference_centroid", "longest_difference_run", "longest_difference_column_run", "delta_histogram", "delta_percentiles", "explain_worst",
        )))

    def test_usage_errors_keep_status_two_and_escape_controls_without_reading(self):
        invalid_arguments = (
            ["missing.png", "missing.png", "--crop", "1,2,3"],
            ["missing.png", "missing.png", "--max-differing", "-1"],
            ["missing.png", "missing.png", "--worst-pixels", "1001"],
            ["missing.png", "missing.png", "--unknown\x1b"],
        )
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            for argv in (["--help"], *invalid_arguments):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with self.subTest(argv=argv), contextlib.redirect_stdout(stdout), \
                        contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as raised:
                        fidelity.main(argv)
                self.assertEqual(raised.exception.code, 0 if argv == ["--help"] else 2)
                if argv != ["--help"]:
                    self.assertIn("fidelity: error:", stderr.getvalue())
                    self.assertNotIn("\x1b", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
