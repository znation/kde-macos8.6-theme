"""Parser construction and argument behavior for the fidelity CLI."""

from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from tools import fidelity
from tools.fidelity_cli_parser import build_parser


class TestFidelityCliParser(unittest.TestCase):
    def test_help_text_is_stable(self):
        help_text = build_parser().format_help()
        self.assertIn("usage: fidelity [-h] [--json] [--worst-pixels N]", help_text)
        self.assertIn("--candidate-crop X,Y,W,H", help_text)
        self.assertIn("--max-differing N", help_text)
        self.assertIn("exit status: 0 when the comparison passes", help_text)
        self.assertIn("--difference-column-runs", help_text)

    def test_defaults_and_explicit_options(self):
        first = build_parser()
        second = build_parser()
        defaults = first.parse_args(["candidate.png", "reference.png"])
        self.assertEqual(vars(defaults), {
            "candidate": "candidate.png",
            "reference": "reference.png",
            "json": False,
            "worst_pixels": None,
            "channel_counts": False,
            "channel_bias": False,
            "channel_maxima": False,
            "difference_rows": False,
            "difference_columns": False,
            "difference_row_bounds": False,
            "difference_column_bounds": False,
            "difference_runs": False,
            "difference_column_runs": False,
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
            "--candidate-crop", "1,2,3,4", "--crop", "5,6,7,8",
            "--channel-counts", "--channel-bias", "--channel-maxima",
            "--difference-rows", "--difference-columns", "--difference-row-bounds",
            "--difference-column-bounds", "--difference-runs",
            "--difference-column-runs", "--delta-histogram", "--delta-percentiles",
            "--explain-worst", "--tolerance", "9", "--max-mae", "1.5",
            "--max-frac", "0.25", "--max-rmse", "2.5", "--max-delta", "12",
            "--max-differing", "3",
        ])
        self.assertEqual(explicit.candidate_crop, (1, 2, 3, 4))
        self.assertEqual(explicit.crop, (5, 6, 7, 8))
        self.assertEqual((explicit.worst_pixels, explicit.tolerance), (7, 9))
        self.assertEqual((explicit.max_mae, explicit.max_frac, explicit.max_rmse),
                         (1.5, 0.25, 2.5))
        self.assertEqual((explicit.max_delta, explicit.max_differing), (12, 3))
        self.assertTrue(all(getattr(explicit, name) for name in (
            "json", "channel_counts", "channel_bias", "channel_maxima",
            "difference_rows", "difference_columns", "difference_row_bounds",
            "difference_column_bounds", "difference_runs", "difference_column_runs",
            "delta_histogram", "delta_percentiles", "explain_worst",
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
