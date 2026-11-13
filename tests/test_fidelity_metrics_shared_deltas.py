"""The metrics comparison shares the pixel reports' channel-delta pass.

``tools/fidelity.py`` derives the per-channel absolute-delta byte strings
once, up front, and hands them to ``compare`` as well as to the spatial
and pixels reports: ``compare`` takes the list through its keyword-only
``deltas`` parameter, and ``None`` keeps deriving the identical strings
in the call, the behavior a caller that drives only the comparison keeps.
This module pins the shared-pass contract -- explicit and derived deltas
give identical metrics (including the both-opaque 3-string list whose
``compare_alpha`` arithmetic still divides by four channels) and the CLI
deriving the strings once per mixed run while the default run derives
none.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.fidelity_delta_fixtures import RGB_PAIR, RGBA_PAIR  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_metrics import compare  # noqa: E402
from tools.fidelity_pixels import channel_deltas  # noqa: E402
from tools.png import Image  # noqa: E402

# A 3x2 RGBA pair with an all-opaque alpha plane on both sides: the list
# keeps three strings and the compared-alpha arithmetic still reads an
# alpha-aggregate fourth slot whose contribution is zero.
OPAQUE_CANDIDATE_RGB = bytearray(18)
OPAQUE_CANDIDATE_RGB[0] = 200    # (0, 0) red
OPAQUE_RGBA_PAIR = (
    Image(3, 2, bytes(OPAQUE_CANDIDATE_RGB), b"\xff" * 6),
    Image(3, 2, bytes(18), b"\xff" * 6),
)


class TestSharedDeltasMetrics(unittest.TestCase):
    """Explicit deltas and self-derived deltas give identical metrics."""

    def test_shared_deltas_reproduce_the_metrics(self):
        """Each tolerance's shared-delta metrics equal the derived metrics."""
        for name, pair in (("rgb", RGB_PAIR), ("rgba", RGBA_PAIR),
                           ("opaque-rgba", OPAQUE_RGBA_PAIR)):
            deltas = channel_deltas(*pair)
            for tolerance in (0, 9, 100):
                with self.subTest(pair=name, tolerance=tolerance):
                    shared = compare(*pair, tolerance, deltas=deltas)
                    derived = compare(*pair, tolerance)
                    self.assertEqual(shared, derived)

    def test_rgb_metrics_read_the_shared_strings(self):
        """The sharing RGB pair's metrics come from its two over-tolerance
        pixels: MAE 40/24, MAE R 1.25, MAE G 0, MAE B 3.75, RMSE
        sqrt(1000/24), worst delta 30 at pixel (2, 1), and two differing
        pixels at tolerance 9."""
        deltas = channel_deltas(*RGB_PAIR)
        self.assertEqual(len(deltas), 3)
        metrics = compare(*RGB_PAIR, 9, deltas=deltas)
        self.assertEqual(metrics.pixels, 8)
        self.assertEqual(metrics.mae, 40 / 24)
        self.assertEqual(metrics.mae_r, 1.25)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 3.75)
        self.assertEqual(metrics.rmse, (1000 / 24) ** 0.5)
        self.assertEqual(metrics.max_delta, 30)
        self.assertEqual(metrics.max_x, 2)
        self.assertEqual(metrics.max_y, 1)
        self.assertEqual(metrics.differing, 2)
        self.assertEqual(metrics.frac_differing, 2 / 8)
        self.assertEqual(metrics.difference_bounds, (0, 0, 3, 2))

    def test_rgba_metrics_read_the_shared_alpha_string(self):
        """The sharing RGBA pair's metrics include the computed alpha
        channel: MAE 295/24 over four channels, MAE A 42.5, RMSE
        sqrt(66625/24), worst delta 255 at pixel (0, 0), and one differing
        pixel at tolerance 100."""
        deltas = channel_deltas(*RGBA_PAIR)
        self.assertEqual(len(deltas), 4)
        metrics = compare(*RGBA_PAIR, 100, deltas=deltas)
        self.assertEqual(metrics.mae, 295 / 24)
        self.assertEqual(metrics.mae_r, 40 / 6)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertEqual(metrics.mae_a, 255 / 6)
        self.assertEqual(metrics.rmse, (66625 / 24) ** 0.5)
        self.assertEqual(metrics.max_delta, 255)
        self.assertEqual(metrics.max_x, 0)
        self.assertEqual(metrics.max_y, 0)
        self.assertEqual(metrics.differing, 1)
        self.assertEqual(metrics.frac_differing, 1 / 6)
        self.assertEqual(metrics.difference_bounds, (0, 0, 1, 1))

    def test_opaque_rgba_metrics_exclude_the_alpha_string(self):
        """An all-opaque alpha plane on both sides shares a three-string
        list whose comparison still reports MAE A 0.0 and divides the
        aggregates by four channels."""
        deltas = channel_deltas(*OPAQUE_RGBA_PAIR)
        self.assertEqual(len(deltas), 3)
        metrics = compare(*OPAQUE_RGBA_PAIR, 0, deltas=deltas)
        self.assertEqual(metrics.mae_a, 0.0)
        # Only the red delta 200 against the all-zero reference differs;
        # the aggregates divide by 6 pixels x 4 channels either way.
        self.assertEqual(metrics.mae, 200 / 24)
        self.assertEqual(metrics.rmse, (200 ** 2 / 24) ** 0.5)
        self.assertEqual(metrics.differing, 1)


class TestCliSharedMetricsPass(FidelityCliTestCase):
    """One comparison run derives the shared delta pass once."""

    def _counting(self, calls, real):
        def counting(candidate_image, reference_image):
            calls.append((candidate_image.width, candidate_image.height))
            return real(candidate_image, reference_image)
        return counting

    def test_mixed_run_passes_the_shared_list_to_compare(self):
        """A mixed spatial+pixel run derives the deltas once and ``compare``
        reads the shared list through its ``deltas`` argument."""
        candidate, reference = self._delta_pair()
        derivations, shared_lists = [], []
        real = fidelity.compare

        def recording(candidate_image, reference_image, tolerance=0, **kwargs):
            shared_lists.append(kwargs.get("deltas"))
            return real(candidate_image, reference_image, tolerance, **kwargs)

        with (mock.patch.object(fidelity, "channel_deltas",
               self._counting(derivations, fidelity.channel_deltas)),
              mock.patch.object(fidelity, "compare", recording)):
            result = self._run_png_pair(candidate, reference,
                                        "--difference-rows", "--channel-counts",
                                        "--tolerance", "9")
        self._assert_fail(result)
        self.assertEqual(derivations, [(4, 3)])
        self.assertEqual(len(shared_lists), 1)
        self.assertEqual(len(shared_lists[0]), 3)

    def test_default_run_derives_no_deltas(self):
        """A run with no pixel or spatial report derives no delta pass: the
        comparison derives inside its own call, exactly as before."""
        candidate, reference = self._delta_pair()
        with mock.patch.object(
            fidelity, "channel_deltas", side_effect=AssertionError
        ):
            result = self._run_png_pair(candidate, reference,
                                        "--tolerance", "9")
        self._assert_fail(result)


if __name__ == "__main__":
    unittest.main()
