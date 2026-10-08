"""Tests for tools/fidelity_metrics.py's comparison metrics -- compare, crop,
and the packed-integer helpers behind them.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import fidelity_metrics  # noqa: E402
from png_fixtures import rgb_image  # noqa: E402


def assert_matches_oracle(case, actual, reference, *, arity, min_length=0):
    """Check a packed-integer routine against a naive per-byte oracle.

    ``actual`` and ``reference`` each take ``arity`` byte strings and return
    equal results.  Every length from ``min_length`` to 39, then the
    63/64/65, 255/256/257 and 1000 boundaries, is exercised on eight random
    blocks so a borrow, carry, or bit-slice bug shows up across byte positions.
    """
    rng = random.Random(0)
    lengths = list(range(min_length, 40)) + [63, 64, 65, 255, 256, 257, 1000]
    for length in lengths:
        for _ in range(8):
            args = [
                bytes(rng.randrange(256) for _ in range(length))
                for _ in range(arity)
            ]
            with case.subTest(length=length):
                case.assertEqual(actual(*args), reference(*args))


class TestAbsDiff(unittest.TestCase):
    """The packed-integer byte differ must agree with the per-byte form."""

    @staticmethod
    def _reference(a: bytes, b: bytes) -> bytes:
        return bytes(abs(x - y) for x, y in zip(a, b))

    def test_matches_per_byte_reference(self):
        assert_matches_oracle(
            self, fidelity_metrics._abs_diff, self._reference, arity=2
        )

    def test_extreme_values(self):
        # 0/255 is where a borrow or carry would show up first, for both an
        # even and an odd byte count.
        for length in (1, 2, 7):
            for x in (0, 255):
                for y in (0, 255):
                    a = bytes([x]) * length
                    b = bytes([y]) * length
                    with self.subTest(length=length, x=x, y=y):
                        self.assertEqual(
                            fidelity_metrics._abs_diff(a, b), self._reference(a, b)
                        )


class TestSumSquares(unittest.TestCase):
    """The split-table sum of squares must agree with the per-byte form."""

    @staticmethod
    def _reference(channel: bytes) -> int:
        return sum(value * value for value in channel)

    def test_matches_per_byte_reference(self):
        assert_matches_oracle(
            self, fidelity_metrics._sum_squares, self._reference, arity=1
        )

    def test_every_byte_value(self):
        # A single square can spill into the high byte (255*255 == 65025), so
        # exercise every value, both alone and repeated enough to carry.
        channel = bytes(range(256))
        self.assertEqual(
            fidelity_metrics._sum_squares(channel), self._reference(channel)
        )
        self.assertEqual(
            fidelity_metrics._sum_squares(b"\xff" * 1000),
            self._reference(b"\xff" * 1000),
        )


class TestMaxByteIndex(unittest.TestCase):
    """The bit-sliced maximum must agree with ``max`` plus ``find``."""

    @staticmethod
    def _reference(data: bytes) -> int:
        return data.find(max(data))

    def test_matches_max_and_find(self):
        assert_matches_oracle(
            self,
            fidelity_metrics._max_byte_index,
            self._reference,
            arity=1,
            min_length=1,
        )

    def test_edges_and_ties(self):
        cases = (
            b"\x00",  # single zero
            b"\xff",  # single maximum
            b"\x00\xff",  # maximum last
            b"\xff\x00",  # maximum first
            b"\x05\x05\x05",  # all equal: first wins
            bytes(range(256)),  # every value once: 255 at the end
            bytes(range(255, -1, -1)),  # every value once: 255 at the start
        )
        for data in cases:
            with self.subTest(data=data[:8]):
                self.assertEqual(
                    fidelity_metrics._max_byte_index(data), self._reference(data)
                )

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            fidelity_metrics._max_byte_index(b"")


class TestCompare(unittest.TestCase):
    def test_identical_is_zero(self):
        image, _ = rgb_image(4, 4, lambda x, y: (x * 5, y * 5, 100))
        metrics = fidelity_metrics.compare(image, image)
        self.assertEqual(metrics.mae, 0.0)
        self.assertEqual(metrics.mae_r, 0.0)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertEqual(metrics.rmse, 0.0)
        self.assertEqual(metrics.max_delta, 0)
        self.assertEqual((metrics.max_x, metrics.max_y), (0, 0))
        self.assertEqual(metrics.differing, 0)
        self.assertEqual(metrics.frac_differing, 0.0)

    def test_single_pixel_difference(self):
        a, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[0] = 10  # one red channel on the first pixel
        b = fidelity_metrics.Image(a.width, a.height, bytes(changed))
        metrics = fidelity_metrics.compare(a, b)
        self.assertEqual(metrics.pixels, 4)
        self.assertAlmostEqual(metrics.mae, 10 / 12)
        self.assertAlmostEqual(metrics.mae_r, 10 / 4)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertAlmostEqual(metrics.rmse, (100 / 12) ** 0.5)
        self.assertEqual(metrics.max_delta, 10)
        self.assertEqual(metrics.differing, 1)
        self.assertEqual(metrics.frac_differing, 0.25)

    def test_per_channel_mae_locates_colour_cast(self):
        # A uniform bias in one channel must show up in that channel's MAE and
        # nowhere else, so a colour cast is distinguishable from per-pixel noise.
        a, _ = rgb_image(2, 2, lambda x, y: (10, 20, 30))
        cast = bytes(
            a.rgb[i] + (5 if i % 3 == 0 else 0) for i in range(len(a.rgb))
        )
        metrics = fidelity_metrics.compare(a, fidelity_metrics.Image(a.width, a.height, cast))
        self.assertAlmostEqual(metrics.mae_r, 5.0)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertAlmostEqual(metrics.mae, 5 / 3)

    def test_worst_delta_location(self):
        # max_x/max_y must locate the pixel carrying the worst channel delta,
        # so a failing comparison can be inspected at the right coordinate.
        a, _ = rgb_image(3, 2, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[15] = 40  # red channel of pixel (2, 1)
        b = fidelity_metrics.Image(a.width, a.height, bytes(changed))
        metrics = fidelity_metrics.compare(a, b)
        self.assertEqual(metrics.max_delta, 40)
        self.assertEqual((metrics.max_x, metrics.max_y), (2, 1))

    def test_worst_delta_tie_and_differing_union(self):
        # Ties on the worst delta resolve to the first pixel in scan order, in
        # any channel; and a pixel with several channels over tolerance counts
        # once in ``differing``.
        a = fidelity_metrics.Image(3, 1, bytes(9))
        b = fidelity_metrics.Image(
            3,
            1,
            bytes(
                [
                    0, 10, 0,  # pixel 0: green reaches the maximum
                    10, 0, 0,  # pixel 1: red ties it and must not win
                    10, 10, 0,  # pixel 2: two channels differ
                ]
            ),
        )
        metrics = fidelity_metrics.compare(a, b, tolerance=5)
        self.assertEqual(metrics.max_delta, 10)
        self.assertEqual((metrics.max_x, metrics.max_y), (0, 0))
        self.assertEqual(metrics.differing, 3)

    def test_tolerance_absorbs_small_deltas(self):
        a, _ = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        b = fidelity_metrics.Image(1, 1, bytes([3, 0, 0]))
        self.assertEqual(fidelity_metrics.compare(a, b, tolerance=3).differing, 0)
        self.assertEqual(fidelity_metrics.compare(a, b, tolerance=2).differing, 1)

    def test_tolerance_outside_channel_range_raises(self):
        # A per-channel delta is a byte, so a tolerance above 255 can never be
        # exceeded (every pixel reads as within tolerance) and a negative one
        # is exceeded by every pixel; either silently inverts the verdict, so
        # the entry point names the rejected value instead of acting on it.
        image, _ = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        for tolerance in (-1, 256, "5"):
            with self.subTest(tolerance=tolerance):
                with self.assertRaises(fidelity_metrics.FidelityError) as caught:
                    fidelity_metrics.compare(image, image, tolerance=tolerance)
                self.assertIn(repr(tolerance), str(caught.exception))

    def test_size_mismatch_raises(self):
        a, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        b, _ = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity_metrics.FidelityError) as caught:
            fidelity_metrics.compare(a, b)
        message = str(caught.exception)
        self.assertIn("candidate 2x2", message)
        self.assertIn("reference 1x1", message)

    def test_crop_extracts_region(self):
        image, _ = rgb_image(4, 4, lambda x, y: (x, y, 0))
        region = fidelity_metrics.crop(image, 1, 2, 2, 2)
        self.assertEqual(region.width, 2)
        self.assertEqual(region.height, 2)
        self.assertEqual(region.rgb, bytes([1, 2, 0, 2, 2, 0, 1, 3, 0, 2, 3, 0]))

    def test_crop_region_ending_exactly_on_far_edges_is_allowed(self):
        # A crop whose far edges land exactly on the image's right and bottom
        # borders is inside the image: x + width == image.width is valid. An
        # off-by-one (>= instead of >) would reject this legitimate crop.
        image, _ = rgb_image(4, 4, lambda x, y: (x, y, 0))
        region = fidelity_metrics.crop(image, 1, 1, 3, 3)
        self.assertEqual((region.width, region.height), (3, 3))
        self.assertEqual(
            region.rgb,
            bytes(
                [
                    1, 1, 0, 2, 1, 0, 3, 1, 0,
                    1, 2, 0, 2, 2, 0, 3, 2, 0,
                    1, 3, 0, 2, 3, 0, 3, 3, 0,
                ]
            ),
        )

    def test_crop_whole_image_returns_it_unchanged(self):
        # Selecting the entire surface is the degenerate crop; it must be
        # accepted and preserve every pixel in order.
        image, _ = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 7))
        region = fidelity_metrics.crop(image, 0, 0, 3, 2)
        self.assertEqual((region.width, region.height), (3, 2))
        self.assertEqual(region.rgb, image.rgb)

    def test_crop_out_of_bounds_raises(self):
        image, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity_metrics.FidelityError):
            fidelity_metrics.crop(image, 1, 1, 2, 2)

    def test_crop_nonpositive_rect_error_names_values(self):
        # The message must echo the rejected rectangle so a CLI user can see
        # which of x/y/w/h was wrong without re-deriving it from the input.
        image, _ = rgb_image(4, 4, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity_metrics.FidelityError) as caught:
            fidelity_metrics.crop(image, 0, 0, 0, 2)
        message = str(caught.exception)
        self.assertIn("x=0 y=0 w=0 h=2", message)

    def test_crop_out_of_bounds_error_names_rect_and_image(self):
        # The message must name both the offending rectangle and the image it
        # was measured against, since neither is otherwise visible.
        image, _ = rgb_image(4, 4, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity_metrics.FidelityError) as caught:
            fidelity_metrics.crop(image, 3, 3, 2, 2)
        message = str(caught.exception)
        self.assertIn("x=3 y=3 w=2 h=2", message)
        self.assertIn("4x4", message)


if __name__ == "__main__":
    unittest.main()
