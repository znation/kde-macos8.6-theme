"""The pixel reports share one channel-delta pass per comparison run.

``tools/fidelity.py`` derives the per-channel absolute-delta byte strings
once, up front, and hands them to every pixel report the run requested:
each diagnostic's ``deltas=`` parameter takes the list, and ``None``
derives it in the call, the behavior a caller that drives one diagnostic
keeps. This module pins the shared-pass contract -- explicit and derived
deltas give identical outputs on every report, and the CLI derives the
strings once per run.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.fidelity_delta_fixtures import RGB_PAIR, RGBA_PAIR  # noqa: E402
from tools import fidelity  # noqa: E402
from tools import fidelity_pixels  # noqa: E402
from tools.fidelity_pixels import (  # noqa: E402
    channel_counts,
    channel_deltas,
    channel_maxima,
    delta_histogram,
    worst_pixels,
)

REPORTS = (
    ("worst_pixels", worst_pixels),
    ("channel_counts", channel_counts),
    ("channel_maxima", channel_maxima),
    ("delta_histogram", delta_histogram),
)

CALLS = {
    "worst_pixels": lambda pair, tolerance, **kwargs: worst_pixels(
        pair[0], pair[1], tolerance, 6, **kwargs),
    "channel_counts": lambda pair, tolerance, **kwargs: channel_counts(
        pair[0], pair[1], tolerance, **kwargs),
    "channel_maxima": lambda pair, tolerance, **kwargs: channel_maxima(
        pair[0], pair[1], **kwargs),
    "delta_histogram": lambda pair, tolerance, **kwargs: delta_histogram(
        pair[0], pair[1], **kwargs),
}


class TestSharedDeltas(unittest.TestCase):
    """Explicit deltas and derived deltas give identical pixel outputs."""

    def test_shared_deltas_reproduce_every_report(self):
        """Each report's output equals its derived-deltas output."""
        for name, pair in (("rgb", RGB_PAIR), ("rgba", RGBA_PAIR)):
            deltas = channel_deltas(*pair)
            for tolerance in (0, 9, 100):
                with self.subTest(pair=name, tolerance=tolerance):
                    self._assert_reports_match_the_deltas(pair, tolerance,
                                                          deltas)

    def _assert_reports_match_the_deltas(self, pair, tolerance, deltas):
        """Each report's output equals its derived-deltas output."""
        for report_name, call in CALLS.items():
            with self.subTest(report=report_name):
                shared = call(pair, tolerance, deltas=deltas)
                derived = call(pair, tolerance)
                self.assertEqual(shared, derived)

    def test_rgb_reports_read_the_shared_strings(self):
        """The RGB pair's reports re-derive each byte's delta from the list.

        Candidate deltas are the candidate bytes themselves (reference all
        zero), so the red byte 10 and blue byte 30 shape every value: the
        histograms maxima 30 and 10 top the ranking, the counts and maxima
        name no other channel, and the missing alpha plane contributes zeros
        rather than a fourth string.
        """
        deltas = channel_deltas(*RGB_PAIR)
        self.assertEqual(len(deltas), 3)
        self.assertEqual(worst_pixels(*RGB_PAIR, 9, 6, deltas=deltas), [
            {"x": 2, "y": 1,
             "candidate_rgba": [0, 0, 30, 255],
             "reference_rgba": [0, 0, 0, 255],
             "max_delta": 30},
            {"x": 0, "y": 0,
             "candidate_rgba": [10, 0, 0, 255],
             "reference_rgba": [0, 0, 0, 255],
             "max_delta": 10},
        ])
        self.assertEqual(channel_counts(*RGB_PAIR, 9, deltas=deltas),
                         {"r": 1, "g": 0, "b": 1, "a": 0})
        self.assertEqual(channel_maxima(*RGB_PAIR, deltas=deltas),
                         {"r": 10, "g": 0, "b": 30, "a": 0})
        self.assertEqual(delta_histogram(*RGB_PAIR, deltas=deltas), [
            {"delta": 0, "count": 6},
            {"delta": 10, "count": 1},
            {"delta": 30, "count": 1},
        ])

    def test_rgba_reports_read_the_shared_alpha_string(self):
        """The RGBA pair's reports read the fourth string.

        The compared alpha delta at (0, 0) is 255 (byte 0 against the
        reference plane's opaque 255) and the red delta there is 40, so the
        maximum at that pixel is 255 and it alone exceeds tolerance 100.
        """
        deltas = channel_deltas(*RGBA_PAIR)
        self.assertEqual(len(deltas), 4)
        self.assertEqual(worst_pixels(*RGBA_PAIR, 100, 6, deltas=deltas), [
            {"x": 0, "y": 0,
             "candidate_rgba": [40, 0, 0, 0],
             "reference_rgba": [0, 0, 0, 255],
             "max_delta": 255},
        ])
        self.assertEqual(channel_counts(*RGBA_PAIR, 100, deltas=deltas),
                         {"r": 0, "g": 0, "b": 0, "a": 1})
        self.assertEqual(channel_maxima(*RGBA_PAIR, deltas=deltas),
                         {"r": 40, "g": 0, "b": 0, "a": 255})
        self.assertEqual(delta_histogram(*RGBA_PAIR, deltas=deltas), [
            {"delta": 0, "count": 5},
            {"delta": 255, "count": 1},
        ])


class TestCliSingleDeltasPass(FidelityCliTestCase):
    """One comparison run derives the shared delta pass once."""

    def test_pixel_bundle_derives_deltas_once(self):
        """A run requesting four pixel reports computes one delta pass."""
        candidate, reference = self._delta_pair()
        derivations: list[tuple[int, int]] = []
        rederivations: list[tuple[int, int]] = []
        real = fidelity.channel_deltas

        def counting(candidate_image, reference_image):
            derivations.append((candidate_image.width, candidate_image.height))
            return real(candidate_image, reference_image)

        def counting_rederivations(candidate_image, reference_image):
            rederivations.append((candidate_image.width, candidate_image.height))
            return real(candidate_image, reference_image)

        args = ("--worst-pixels", "1", "--channel-counts", "--channel-maxima",
                "--delta-histogram", "--tolerance", "9")
        # The CLI's own derivation goes through ``fidelity.channel_deltas``;
        # a report falling back to its own derivation goes through
        # ``fidelity_pixels.channel_deltas`` via ``_resolved_deltas``, so the
        # count must show one pass at the CLI site and none at the reports'.
        with (mock.patch.object(fidelity, "channel_deltas", counting),
              mock.patch.object(fidelity_pixels, "channel_deltas",
                                counting_rederivations)):
            result = self._run_png_pair(candidate, reference, *args)
        self._assert_fail(result)
        self.assertEqual(derivations, [(4, 3)])
        self.assertEqual(rederivations, [])

    def test_default_run_derives_no_deltas(self):
        """A run without a pixel report computes no delta pass."""
        candidate, reference = self._delta_pair()
        with mock.patch.object(
            fidelity, "channel_deltas", side_effect=AssertionError
        ):
            result = self._run_png_pair(candidate, reference, "--tolerance", "9")
        self._assert_fail(result)


if __name__ == "__main__":
    unittest.main()
