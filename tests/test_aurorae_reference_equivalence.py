"""Pin the beta About This Computer chrome to the retail System Profiler.

``macos8.6-screenshots/sources.txt`` labels ``aboutsystem_betawiki.png`` "Mac OS
8.6b2c4LB beta", and README's reference policy says a beta build "must not be
used as retail reference" -- yet the render fidelity gate
(``tests/test_render_surface.py``) and the Aurorae decoration tests
(``tests/support/aurorae_fixtures.py``) read that file. The retail Japanese 8.6
``systemprofiler_betawiki.png`` shows the same window chrome, so this module
pins the five chrome regions the beta supplies to the retail screenshot's
pixels, turning the beta into an evidence-backed proxy instead of an unrecorded
policy exception.

The two windows sit at different screen origins: aboutsystem's frame origin is
``(7, 25)`` and the profiler's is ``(209, 22)``. The left-anchored regions (the
title bar, the left border and the close box) are therefore a uniform
``(+202, -3)`` shift apart, while the right border and the collapse box are
anchored to each window's right edge and so differ in x by the window-width
difference (252px) as well.
"""

from __future__ import annotations

import os
import unittest
from collections import namedtuple

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.aurorae_fixtures import PROFILER_ROWS, REFERENCE_ROWS
from support.reference_image import read_reference, skip_unless_materialized

from tools.png import Image, pixel_at  # noqa: E402


ABOUTSYSTEM = os.path.join(
    repo_root.ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
PROFILER = os.path.join(
    repo_root.ROOT, "macos8.6-screenshots", "systemprofiler_betawiki.png"
)

# A named window-chrome region: the same crop in each screenshot, as
# ``(x, y, width, height)``. The crops are the same size in both images; only
# their origins differ with the windows' positions.
Region = namedtuple("Region", "name about profiler")

REGIONS = (
    Region("title bar", (30, 25, 80, 22), (232, 22, 80, 22)),
    Region("left border", (7, 47, 6, 212), (209, 44, 6, 212)),
    Region("right border", (354, 47, 6, 212), (808, 44, 6, 212)),
    Region("close box", (11, 29, 13, 13), (213, 26, 13, 13)),
    Region("collapse box", (343, 29, 13, 13), (797, 26, 13, 13)),
)


def first_difference(first, first_crop, second, second_crop):
    """Return the first region-local ``(x, y)`` where two crops differ, or None.

    Both crops must be the same size; the shared width and height come from
    *first_crop*. A difference is reported at its region-local coordinate so a
    caller can name which pixel drifted without re-deriving the origin, and
    ``None`` means the two crops are pixel-for-pixel equal.
    """
    x0, y0, width, height = first_crop
    u0, v0, other_width, other_height = second_crop
    if (width, height) != (other_width, other_height):
        raise ValueError(
            f"crops differ in size: {width}x{height} vs "
            f"{other_width}x{other_height}"
        )
    for y in range(height):
        for x in range(width):
            if pixel_at(first, x0 + x, y0 + y) != pixel_at(
                second, u0 + x, v0 + y
            ):
                return (x, y)
    return None


def changed_pixel(image, x, y):
    """Return a copy of *image* with one pixel's red channel flipped.

    Flipping a channel guarantees a different RGB triple, so the copy differs
    from *image* at exactly ``(x, y)`` and nowhere else. The reference file
    stays read-only: the mutation test mutates this in-memory copy.
    """
    rgb = bytearray(image.rgb)
    offset = (y * image.width + x) * 3
    rgb[offset] ^= 0xFF
    return Image(image.width, image.height, bytes(rgb))


class TestReferenceEquivalence(unittest.TestCase):
    """The beta's chrome regions equal the retail System Profiler's pixels.

    ``make check`` must not require the Git LFS reference set, so each test
    skips when either screenshot is not materialized instead of failing.
    """

    @classmethod
    def setUpClass(cls):
        # The shared bounds cover every region below, and match the Aurorae
        # readers' bounds so the reference cache decodes each screenshot once.
        cls.aboutsystem, cls.aboutsystem_error = read_reference(
            ABOUTSYSTEM, max_rows=REFERENCE_ROWS
        )
        cls.profiler, cls.profiler_error = read_reference(
            PROFILER, max_rows=PROFILER_ROWS
        )

    def setUp(self):
        skip_unless_materialized(self, ABOUTSYSTEM, self.aboutsystem_error)
        skip_unless_materialized(self, PROFILER, self.profiler_error)

    def test_every_region_matches_the_retail_screenshot(self):
        for region in REGIONS:
            with self.subTest(region=region.name):
                difference = first_difference(
                    self.aboutsystem, region.about, self.profiler, region.profiler
                )
                self.assertIsNone(
                    difference,
                    f"the {region.name} differs at region-local {difference}: "
                    "the beta and retail screenshots no longer agree",
                )

    def test_a_one_pixel_change_in_either_image_is_detected(self):
        for region in REGIONS:
            about_x, about_y, _, _ = region.about
            profiler_x, profiler_y, _, _ = region.profiler
            cases = (
                (
                    "aboutsystem",
                    changed_pixel(self.aboutsystem, about_x, about_y),
                    region.about,
                    self.profiler,
                    region.profiler,
                ),
                (
                    "profiler",
                    self.aboutsystem,
                    region.about,
                    changed_pixel(self.profiler, profiler_x, profiler_y),
                    region.profiler,
                ),
            )
            for label, first, first_crop, second, second_crop in cases:
                with self.subTest(region=region.name, image=label):
                    self.assertIsNotNone(
                        first_difference(first, first_crop, second, second_crop),
                        f"a one-pixel change in the {label} {region.name} "
                        "went undetected",
                    )


class TestRegionHelpers(unittest.TestCase):
    """The two comparison helpers, independent of the reference images.

    ``first_difference`` and ``changed_pixel`` carry the module's evidence:
    the mutation test is only sound if ``changed_pixel`` flips exactly one
    pixel, and a size mismatch between two crops must be rejected rather than
    silently compared over the overlap. Both behaviours are pinned here so
    they hold even when the Git LFS screenshots are absent.
    """

    def test_changed_pixel_flips_exactly_the_named_pixel(self):
        original = Image(3, 2, bytes(range(18)))
        mutated = changed_pixel(original, 1, 1)
        self.assertEqual((mutated.width, mutated.height), (3, 2))
        for y in range(original.height):
            for x in range(original.width):
                if (x, y) == (1, 1):
                    self.assertNotEqual(
                        pixel_at(mutated, x, y), pixel_at(original, x, y)
                    )
                else:
                    self.assertEqual(
                        pixel_at(mutated, x, y), pixel_at(original, x, y)
                    )
        # The source image is untouched, so a caller can mutate it repeatedly.
        self.assertEqual(pixel_at(original, 1, 1), (12, 13, 14))

    def test_first_difference_returns_none_for_equal_crops(self):
        image = Image(2, 2, bytes(range(12)))
        self.assertIsNone(
            first_difference(image, (0, 0, 2, 2), image, (0, 0, 2, 2))
        )

    def test_first_difference_reports_the_first_differing_pixel(self):
        # Differences at (2, 1) and (1, 0); the row-major scan must report the
        # earlier row's difference, not the first one stored or the last.
        first = Image(3, 2, bytes(range(18)))
        second = changed_pixel(changed_pixel(first, 2, 1), 1, 0)
        self.assertEqual(
            first_difference(first, (0, 0, 3, 2), second, (0, 0, 3, 2)),
            (1, 0),
        )

    def test_first_difference_rejects_crops_of_different_sizes(self):
        # Comparing a 2x2 crop against a 3x2 one would either read out of
        # bounds or silently compare only the overlap, letting the equality
        # test pass without checking the whole region.
        image = Image(4, 3, bytes(4 * 3 * 3))
        with self.assertRaises(ValueError) as caught:
            first_difference(image, (0, 0, 2, 2), image, (0, 0, 3, 2))
        message = str(caught.exception)
        self.assertIn("2x2", message)
        self.assertIn("3x2", message)


if __name__ == "__main__":
    unittest.main()
