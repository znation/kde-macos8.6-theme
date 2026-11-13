"""The flag derivation shares the pixel reports' channel-delta pass.

``tools/fidelity.py`` derives the per-channel absolute-delta byte strings
once, up front, and hands them to the spatial reports' flag scan and to
every pixel report the run requested: ``differing_flags`` takes the list
through its keyword-only ``deltas`` parameter, and ``None`` derives it in
the call, the behavior a caller that drives one diagnostic keeps. This
module pins the shared-pass contract -- explicit and derived deltas give
identical flags, the flag bits themselves, and the CLI deriving the
strings once per run, including a spatial-only run.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.fidelity_delta_fixtures import RGB_PAIR, RGBA_PAIR  # noqa: E402
from tools import fidelity  # noqa: E402
from tools import fidelity_pixels  # noqa: E402
from tools.fidelity_pixels import channel_deltas  # noqa: E402
from tools.fidelity_spatial import differing_flags  # noqa: E402


class TestSharedDeltasFlags(unittest.TestCase):
    """Explicit deltas and derived deltas give identical flags."""

    def test_shared_deltas_reproduce_the_flags(self):
        """Each tolerance's shared-delta flags equal its derived flags."""
        for name, pair in (("rgb", RGB_PAIR), ("rgba", RGBA_PAIR)):
            with self.subTest(pair=name):
                deltas = channel_deltas(*pair)
                for tolerance in (0, 9, 100):
                    self._assert_flags_match(pair, deltas, tolerance)

    def _assert_flags_match(self, pair, deltas, tolerance):
        """Pin the deltas-keyed flags to the freshly derived flags."""
        with self.subTest(tolerance=tolerance):
            shared = differing_flags(*pair, tolerance, deltas=deltas)
            derived = differing_flags(*pair, tolerance)
            self.assertEqual(shared, derived)

    def test_rgb_flags_read_the_shared_strings(self):
        """The RGB pair's union is exactly the two over-tolerance pixels.

        The candidate bytes' deltas are their own values (reference all
        zero), so the red byte 10 and blue byte 30 each exceed tolerance 9
        and pixel (0, 0)'s and pixel (2, 1)'s flags are 1 -- the first byte
        of the string and byte 6, with byte 6 being pixel (2, 1) of the 4-wide
        second row -- and no other byte is set.
        """
        deltas = channel_deltas(*RGB_PAIR)
        self.assertEqual(len(deltas), 3)
        flags = differing_flags(*RGB_PAIR, 9, deltas=deltas)
        self.assertEqual(flags.count(1), 2)
        self.assertEqual(flags[0], 1)            # pixel (0, 0)
        self.assertEqual(flags[6], 1)            # pixel (2, 1)
        self.assertEqual(flags[1:6].count(1), 0)
        self.assertEqual(flags[7:].count(1), 0)

    def test_rgba_flags_read_the_shared_alpha_string(self):
        """The RGBA pair's union is the compared-alpha pixel alone.

        The alpha delta at (0, 0) is 255 (byte 0 against the reference
        plane's opaque 255), so it alone exceeds tolerance 100 even though
        that pixel's red delta is 40.
        """
        deltas = channel_deltas(*RGBA_PAIR)
        self.assertEqual(len(deltas), 4)
        flags = differing_flags(*RGBA_PAIR, 100, deltas=deltas)
        self.assertEqual(flags, bytes([1] + [0] * 5))


class TestCliSharedFlagsPass(FidelityCliTestCase):
    """One comparison run derives the shared delta pass once."""

    def _counting(self, calls, real):
        def counting(candidate_image, reference_image):
            calls.append((candidate_image.width, candidate_image.height))
            return real(candidate_image, reference_image)
        return counting

    def test_mixed_run_derives_deltas_once(self):
        """A mixed spatial+pixel run computes one delta pass at the CLI."""
        candidate, reference = self._delta_pair()
        derivations, rederivations = [], []
        with (mock.patch.object(fidelity, "channel_deltas",
               self._counting(derivations, fidelity.channel_deltas)),
              mock.patch.object(fidelity_pixels, "channel_deltas",
               self._counting(rederivations, fidelity_pixels.channel_deltas))):
            result = self._run_png_pair(candidate, reference,
                                        "--difference-rows", "--channel-counts",
                                        "--tolerance", "9")
        self._assert_fail(result)
        self.assertEqual(derivations, [(4, 3)])
        self.assertEqual(rederivations, [])

    def test_spatial_run_derives_deltas_once(self):
        """A spatial-only run computes one delta pass, never re-derived."""
        candidate, reference = self._delta_pair()
        derivations, rederivations = [], []
        with (mock.patch.object(fidelity, "channel_deltas",
               self._counting(derivations, fidelity.channel_deltas)),
              mock.patch.object(fidelity_pixels, "channel_deltas",
               self._counting(rederivations, fidelity_pixels.channel_deltas))):
            result = self._run_png_pair(candidate, reference,
                                        "--difference-rows", "--tolerance", "9")
        self._assert_fail(result)
        self.assertEqual(derivations, [(4, 3)])
        self.assertEqual(rederivations, [])

    def test_default_run_derives_no_deltas(self):
        """A run with no pixel or spatial report computes no delta pass."""
        candidate, reference = self._delta_pair()
        with mock.patch.object(
            fidelity, "channel_deltas", side_effect=AssertionError
        ), mock.patch.object(
            fidelity_pixels, "channel_deltas", side_effect=AssertionError
        ):
            result = self._run_png_pair(candidate, reference, "--tolerance", "9")
        self._assert_fail(result)


if __name__ == "__main__":
    unittest.main()
