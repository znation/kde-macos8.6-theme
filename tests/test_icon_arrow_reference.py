"""Ground the icon theme's submenu arrow in the open Apple menu.

The reference's open Apple menu draws a solid black right triangle on each
submenu row. This module re-derives the "Automated Tasks" row's triangle from
``macos8.6-screenshots/desktop_archiveorg8.6hd.png`` and checks the shipped
``go-next-symbolic`` 16x16 path is the same 5x9 right triangle.
"""

from __future__ import annotations

import os
import re
import unittest
import xml.etree.ElementTree as ET

from support.reference_image import ReferenceScreenshotMixin
from support.theme_install import ROOT

REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png"
)
ICON_16 = os.path.join(
    ROOT,
    "theme",
    "icons",
    "org.macos8.desktop",
    "16x16",
    "actions",
    "go-next-symbolic.svg",
)

# The "Automated Tasks" submenu row's triangle. A dark pixel is one whose every
# channel is below DARK; the triangle is pure #000000 at TIP. REGION is the
# half-open x0, y0, x1, y1 window around the triangle.
DARK = 170
REGION = (146, 86, 160, 105)
# The reference triangle's bounding box: x=151..155, y=91..99.
REFERENCE_BOX = (151, 91, 5, 9)
TIP = (152, 93)


def _box(points):
    """Return the half-open ``(x, y, width, height)`` box of *points*."""
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def _path_vertices(d):
    """Return the ``(x, y)`` vertices of an ``M``/``L``/``Z`` path's ``d``."""
    return [(int(x), int(y)) for x, y in re.findall(r"(-?\d+),(-?\d+)", d)]


class TestSubmenuArrowReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE

    def _dark_pixels(self):
        return [
            (x, y)
            for y in range(REGION[1], REGION[3])
            for x in range(REGION[0], REGION[2])
            if max(self.pixel(x, y)) < DARK
        ]

    def test_reference_draws_a_5x9_right_triangle(self):
        dark = self._dark_pixels()
        self.assertEqual(_box(dark), REFERENCE_BOX)
        self.assertEqual(self.pixel(*TIP), (0, 0, 0))
        # A right triangle: the left column spans the full height, and the
        # widest row is the vertical middle (the tip points right).
        left = [y for x, y in dark if x == REFERENCE_BOX[0]]
        self.assertEqual(
            left,
            list(range(REFERENCE_BOX[1], REFERENCE_BOX[1] + REFERENCE_BOX[3])),
        )
        rows = {}
        for x, y in dark:
            rows.setdefault(y, []).append(x)
        widest = max(rows, key=lambda y: len(rows[y]))
        self.assertEqual(widest, REFERENCE_BOX[1] + REFERENCE_BOX[3] // 2)
        self.assertEqual(len(rows[widest]), REFERENCE_BOX[2])

    def test_shipped_16px_path_is_the_reference_triangle(self):
        root = ET.parse(ICON_16).getroot()
        paths = [child for child in root if child.tag.endswith("path")]
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].get("fill"), "#000000")
        box = _box(_path_vertices(paths[0].get("d")))
        # The canvas is KDE-required (16px), so the path's origin differs from
        # the reference's (x=151, y=91); its 5x9 extent is what must match.
        self.assertEqual(box[2:], REFERENCE_BOX[2:])


if __name__ == "__main__":
    unittest.main()
