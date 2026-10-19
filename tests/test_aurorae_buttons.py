"""Tests for the org.macos8.desktop Aurorae title-bar boxes.

The close, maximize, restore and collapse (windowshade) widget SVGs with
their active and inactive states, re-derived from
`macos8.6-screenshots/aboutsystem_betawiki.png` and
`systemprofiler_betawiki.png` through `tools/png/read.py`. The inactive greys are
KDE-required provenance (the reference's inactive windows draw no close,
zoom or collapse boxes in their title bars). The
references are stored with Git LFS, so a clone without them skips these
tests rather than failing `make check`.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.aurorae_fixtures import (
    AURORAE_DIR,
    INACTIVE_GREY,
    ReferenceImageCase,
    ZOOM_BOX_X,
)
from support.platinum_palette import hex_colour
from svg_assertions import (
    assert_no_script_elements,
    assert_unique_ids,
    render_slices,
)


CLOSE_SVG = os.path.join(AURORAE_DIR, "close.svg")
MAXIMIZE_SVG = os.path.join(AURORAE_DIR, "maximize.svg")
RESTORE_SVG = os.path.join(AURORAE_DIR, "restore.svg")
SHADE_SVG = os.path.join(AURORAE_DIR, "shade.svg")

# The four Aurorae button SVGs: the close widget on the left, and on the right
# the maximize and restore states of the zoom widget plus the collapse
# (windowshade) widget.
BUTTON_SVGS = (CLOSE_SVG, MAXIMIZE_SVG, RESTORE_SVG, SHADE_SVG)
ZOOM_SVGS = (MAXIMIZE_SVG, RESTORE_SVG)


def _parsed_svgs(paths):
    """Return each SVG in *paths* as a ``(basename, parsed tree)`` pair.

    The button tests parse one or more of the button SVGs and label each
    subTest with the file's basename; pairing the name and the tree here keeps
    that parse-and-label step in one place.
    """
    return [(os.path.basename(path), ET.parse(path)) for path in paths]


def _inactive_fill(active_fill):
    """The inactive box keeps the #888888/#222222 outlines, flattens the rest."""
    if active_fill in ("#888888", "#222222"):
        return active_fill
    return INACTIVE_GREY


class TestButtons(ReferenceImageCase, unittest.TestCase):
    # The collapse glyph: two horizontal #222222 bars at local y=5 and y=7
    # spanning x=2..10.
    COLLAPSE_GLYPH = frozenset((x, y) for x in range(2, 11) for y in (5, 7))
    # The zoom glyph: the inner square's top and left sides, at local x=7 for
    # y=2..6 and local y=7 for x=2..7.
    ZOOM_GLYPH = frozenset(
        [(7, y) for y in range(2, 7)] + [(x, 7) for x in range(2, 8)]
    )

    needs_profiler = True

    def test_close_box_matches_reference(self):
        expected = self.reference_box(11, 29)
        slices = render_slices(ET.parse(CLOSE_SVG))
        self.assertEqual(slices["active-center"], expected)
        self.assertEqual(slices["active-center"], self.profiler_box(213, 26))

    def test_zoom_box_matches_reference(self):
        # The profiler's zoom widget (x=776..796, y=26..38) is the stripe-free
        # gap, the close box plus the inner square, and the spacing before the
        # collapse box. Pin every pixel against it.
        expected = self.profiler_region(776, 26, 21, 13)
        for name, tree in _parsed_svgs(ZOOM_SVGS):
            with self.subTest(svg=name):
                slices = render_slices(tree)
                self.assertEqual(slices["active-center"], expected)

    def test_collapse_box_matches_reference(self):
        # The collapse box is identical in aboutsystem (343,29) and the
        # profiler (797,26).
        slices = render_slices(ET.parse(SHADE_SVG))
        self.assertEqual(slices["active-center"], self.reference_box(343, 29))
        self.assertEqual(slices["active-center"], self.profiler_box(797, 26))

    def test_highlight_is_reference_white(self):
        # Each reference box's 13th column and row are the white highlight,
        # with #CCCCCC at the column's top and the row's left end.
        boxes = (
            ("aboutsystem close", self.reference_pixel, 11, 29),
            ("aboutsystem collapse", self.reference_pixel, 343, 29),
            ("profiler close", self.profiler_pixel, 213, 26),
            ("profiler zoom", self.profiler_pixel, 781, 26),
            ("profiler collapse", self.profiler_pixel, 797, 26),
        )
        for name, pixel, x0, y0 in boxes:
            with self.subTest(box=name):
                for dy in range(1, 13):
                    self.assertEqual(pixel(x0 + 12, y0 + dy), (255, 255, 255))
                for dx in range(1, 13):
                    self.assertEqual(pixel(x0 + dx, y0 + 12), (255, 255, 255))
                self.assertEqual(pixel(x0 + 12, y0), (204, 204, 204))
                self.assertEqual(pixel(x0, y0 + 12), (204, 204, 204))

    def _glyph(self, path, group, offset=0):
        """Return the art and its points differing from the close box.

        *offset* is the art's local x of the box's left column; the
        differing points are returned in box-local coordinates.
        """
        art = render_slices(ET.parse(path))[group]
        base = render_slices(ET.parse(CLOSE_SVG))[group]
        return art, {(x, y) for x, y in base if art[(x + offset, y)] != base[(x, y)]}

    def _assert_reference_glyph(self, path, glyph, pixel, x0, y0, offset=0):
        art, differing = self._glyph(path, "active-center", offset)
        self.assertEqual(differing, glyph)
        for x, y in sorted(glyph):
            self.assertEqual(
                art[(x + offset, y)], hex_colour(pixel(x0 + x, y0 + y)), (x, y)
            )

    def test_zoom_glyph_is_the_reference_glyph(self):
        for name, path in (("maximize", MAXIMIZE_SVG), ("restore", RESTORE_SVG)):
            with self.subTest(svg=name):
                self._assert_reference_glyph(
                    path, self.ZOOM_GLYPH, self.profiler_pixel, 781, 26,
                    offset=ZOOM_BOX_X,
                )

    def test_collapse_glyph_is_the_reference_glyph(self):
        self._assert_reference_glyph(
            SHADE_SVG, self.COLLAPSE_GLYPH, self.reference_pixel, 343, 29
        )

    def test_inactive_center_is_flat(self):
        # The inactive box keeps the active box's #888888/#222222 outlines and
        # flattens its gradient face to #CCCCCC (KDE-required provenance: the
        # reference's inactive windows draw no close, zoom or collapse boxes
        # in their title bars). The glyphs are #222222, so
        # they survive over the flat face.
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                slices = render_slices(tree)
                active = slices["active-center"]
                inactive = slices["inactive-center"]
                self.assertEqual(set(inactive), set(active))
                for point, fill in active.items():
                    self.assertEqual(
                        inactive[point], _inactive_fill(fill), point
                    )

    def test_inactive_glyphs_survive(self):
        for glyph, svgs, offset in (
            (self.ZOOM_GLYPH, ZOOM_SVGS, ZOOM_BOX_X),
            (self.COLLAPSE_GLYPH, (SHADE_SVG,), 0),
        ):
            for path in svgs:
                with self.subTest(svg=os.path.basename(path)):
                    _, differing = self._glyph(path, "inactive-center", offset)
                    self.assertEqual(differing, glyph)

    def test_button_svgs_are_self_contained(self):
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                assert_no_script_elements(self, tree)


if __name__ == "__main__":
    unittest.main()
