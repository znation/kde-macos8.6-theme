"""The spatial reports share one differing-flags pass per comparison run.

``tools/fidelity.py`` derives the row-major flag string once, up front, and
hands it to every spatial report the run requested: each diagnostic's
``flags=`` parameter takes the string, and ``None`` derives it in the call,
the behavior a caller that drives one diagnostic keeps. This module pins the
shared-pass contract -- explicit and derived flags give identical outputs on
every report, and the CLI derives the string once per run.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.fidelity_delta_fixtures import (
    ALPHA_CANDIDATE,
    RGB_PAIR,
    RGBA_PAIR,
)  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_metrics import compare  # noqa: E402
from tools.fidelity_spatial import (  # noqa: E402
    difference_centroid,
    difference_column_bounds,
    difference_column_run_count,
    difference_column_runs,
    difference_columns,
    difference_row_bounds,
    difference_rows,
    difference_run_count,
    difference_runs,
    differing_flags,
    longest_difference_column_run,
    longest_difference_run,
    _axis_scanlines,
)
from tools.png import Image  # noqa: E402

REPORTS = (
    ("difference_rows", difference_rows),
    ("difference_columns", difference_columns),
    ("difference_row_bounds", difference_row_bounds),
    ("difference_column_bounds", difference_column_bounds),
    ("difference_runs", difference_runs),
    ("difference_run_count", difference_run_count),
    ("difference_column_runs", difference_column_runs),
    ("difference_column_run_count", difference_column_run_count),
    ("longest_difference_run", longest_difference_run),
    ("longest_difference_column_run", longest_difference_column_run),
    ("difference_centroid", difference_centroid),
)


class TestSharedFlags(unittest.TestCase):
    """Explicit flags and derived flags give identical spatial outputs."""

    def test_axis_scanlines_preserve_row_and_column_order(self):
        flags = bytes((1, 0, 1, 0, 1, 1))
        self.assertEqual(list(_axis_scanlines(flags, 3, 2, False)), [
            (0, bytes((1, 0, 1))),
            (1, bytes((0, 1, 1))),
        ])
        self.assertEqual(list(_axis_scanlines(flags, 3, 2, True)), [
            (0, bytes((1, 0))),
            (1, bytes((0, 1))),
            (2, bytes((1, 1))),
        ])

    def test_shared_flags_reproduce_every_report(self):
        """Each report's output equals its derived-flags output."""
        for name, pair in (("rgb", RGB_PAIR), ("rgba", RGBA_PAIR)):
            for tolerance in (0, 9, 100):
                with self.subTest(pair=name, tolerance=tolerance):
                    self._assert_reports_match_the_flags(pair, tolerance)

    def _assert_reports_match_the_flags(self, pair, tolerance):
        """Each report's output equals its derived-flags output."""
        flags = differing_flags(*pair, tolerance)
        for report_name, report in REPORTS:
            with self.subTest(report=report_name):
                shared = report(*pair, tolerance, flags=flags)
                derived = report(*pair, tolerance, flags=None)
                self.assertEqual(shared, derived)

    def test_flags_union_matches_the_comparison_metrics(self):
        """The shared string's population equals compare's differing count."""
        candidate, reference = ALPHA_CANDIDATE, Image(3, 2, bytes(18))
        rgba_flags = differing_flags(candidate, reference, 100)
        metrics = compare(candidate, reference, tolerance=100)
        self.assertEqual(rgba_flags.count(1), metrics.differing)
        self.assertEqual(rgba_flags.count(1), 1)
        self.assertEqual(differing_flags(*RGB_PAIR, 9).count(1), 2)
        self.assertEqual(difference_rows(*RGB_PAIR, 9), [1, 1])
        self.assertEqual(difference_columns(*RGB_PAIR, 9), [1, 0, 1, 0])
        self.assertEqual(difference_runs(*RGB_PAIR, 9),
                         [{"x": 0, "y": 0, "length": 1},
                          {"x": 2, "y": 1, "length": 1}])
        self.assertEqual(difference_run_count(*RGB_PAIR, 9), 2)
        self.assertEqual(difference_centroid(*RGB_PAIR, 9),
                         {"x": 1.0, "y": 0.5})
        self.assertEqual(difference_row_bounds(*RGB_PAIR, 9),
                         [{"x": 0, "width": 1}, {"x": 2, "width": 1}])

    def test_reports_read_shared_flags_over_tolerance_100(self):
        """Tolerance 100 leaves one over-tolerance pixel on the RGBA pair.

        The RGB-only bytes top out at delta 40, inside the tolerance, and the
        compared alpha delta at (0, 0) is 255, so every spatial report reads
        its one differing pixel from the shared string.
        """
        candidate, reference = ALPHA_CANDIDATE, Image(3, 2, bytes(18))
        flags = differing_flags(candidate, reference, 100)
        self.assertEqual(difference_rows(*RGBA_PAIR, 100, flags=flags), [1, 0])
        self.assertEqual(difference_columns(*RGBA_PAIR, 100, flags=flags),
                         [1, 0, 0])
        self.assertEqual(difference_column_bounds(*RGBA_PAIR, 100, flags=flags),
                         [{"y": 0, "height": 1}, None, None])
        self.assertEqual(
            difference_column_run_count(*RGBA_PAIR, 100, flags=flags), 1
        )
        self.assertEqual(longest_difference_column_run(
            *RGBA_PAIR, 100, flags=flags),
            {"x": 0, "y": 0, "length": 1})
        self.assertEqual(longest_difference_run(*RGBA_PAIR, 100, flags=flags),
                         {"x": 0, "y": 0, "length": 1})
        self.assertEqual(difference_centroid(*RGBA_PAIR, 100, flags=flags),
                         {"x": 0.0, "y": 0.0})


class TestCliSingleFlagsPass(FidelityCliTestCase):
    """One comparison run derives the shared flags pass once."""

    def test_spatial_bundle_derives_flags_once(self):
        """A run requesting three spatial reports computes one flag pass."""
        candidate, reference = self._delta_pair()
        derivations: list[tuple[int, int, int]] = []
        real = fidelity.differing_flags

        def counting(candidate_image, reference_image, tolerance, **kwargs):
            derivations.append((
                candidate_image.width,
                candidate_image.height,
                tolerance,
            ))
            return real(candidate_image, reference_image, tolerance, **kwargs)

        args = ("--difference-rows", "--difference-runs", "--difference-centroid",
                "--tolerance", "9")
        with mock.patch.object(fidelity, "differing_flags", counting):
            result = self._run_png_pair(candidate, reference, *args)
        self._assert_fail(result)
        self.assertEqual(derivations, [(4, 3, 9)])

    def test_default_run_derives_no_flags(self):
        """A run without a spatial report computes no flag pass."""
        candidate, reference = self._delta_pair()
        with mock.patch.object(
            fidelity, "differing_flags", side_effect=AssertionError
        ):
            result = self._run_png_pair(candidate, reference, "--tolerance", "9")
        self._assert_fail(result)


if __name__ == "__main__":
    unittest.main()
