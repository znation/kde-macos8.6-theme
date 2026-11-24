"""Tests pinning the shared PNG header limits at their boundaries.

The decode and size-read tests exercise ``check_pixel_limit`` only through
streams declared far above the cap (``tests/test_png_malformed.py``,
``tests/test_png_read_size.py``), so the guard's own boundary — a declared
image exactly at the cap accepted, one pixel over refused — has no pin and a
``>``/``>=`` slip in the comparison would pass the suite unnoticed. These
tests call ``check_pixel_limit`` directly to pin that boundary.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.png import header
from tools.png.image import PngError


class TestPixelLimit(unittest.TestCase):
    def test_a_declaration_at_the_pixel_cap_is_accepted(self):
        # tools/png/header.py: the guard refuses a declared image that
        # *exceeds* MAX_PIXELS, so exactly 64,000,000 declared pixels (the
        # 8000x8000 square, or the same product through one tall dimension)
        # must pass without raising.
        self.assertEqual(header.MAX_PIXELS, 64_000_000)
        for width, height in (
            (8000, 8000),
            (header.MAX_PIXELS, 1),
            (1, header.MAX_PIXELS),
        ):
            with self.subTest(width=width, height=height):
                header.check_pixel_limit(width, height)

    def test_a_declaration_one_pixel_over_the_cap_is_refused(self):
        # The same guard refuses beyond the cap whichever dimension carries
        # the surplus, and names the declared dimensions, the declared pixel
        # count and the cap itself in its diagnostic (the callers'
        # read_png_size message re-uses it).
        for width, height in (
            (header.MAX_PIXELS + 1, 1),
            (1, header.MAX_PIXELS + 1),
            (6400, 10001),  # 64,006,400 pixels, over without a huge factor
        ):
            with self.subTest(width=width, height=height):
                message = self._refusal(width, height)
                self.assertIn(f"{width}x{height}", message)
                self.assertIn(f"({width * height} pixels)", message)
                self.assertIn(f"{header.MAX_PIXELS}-pixel limit", message)

    def test_a_declaration_one_pixel_under_the_cap_is_accepted(self):
        # The below-cap side of the boundary stays open too: 63,999,999
        # declared pixels must not trip the guard.
        header.check_pixel_limit(header.MAX_PIXELS - 1, 1)

    def _refusal(self, width: int, height: int) -> str:
        with self.assertRaises(PngError) as caught:
            header.check_pixel_limit(width, height)
        return str(caught.exception)


if __name__ == "__main__":
    unittest.main()
