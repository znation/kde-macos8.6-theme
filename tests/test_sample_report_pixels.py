"""Unit tests for pixel iteration used by the sampler's report modules."""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_pixels import _positioned_region_pixels  # noqa: E402


class TestPositionedRegionPixels(unittest.TestCase):
    def test_positions_advance_across_rows_with_row_major_rgb_values(self):
        class Image:
            width = 3
            rgb = bytes((
                10, 11, 12, 20, 21, 22, 30, 31, 32,
                40, 41, 42, 50, 51, 52, 60, 61, 62,
            ))

        self.assertEqual(
            list(_positioned_region_pixels(Image(), 1, 0, 2, 2)),
            [
                (1, 0, (20, 21, 22)),
                (2, 0, (30, 31, 32)),
                (1, 1, (50, 51, 52)),
                (2, 1, (60, 61, 62)),
            ],
        )


if __name__ == "__main__":
    unittest.main()
