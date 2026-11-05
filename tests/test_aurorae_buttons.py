"""Tests for the org.macos8.desktop Aurorae title-bar boxes.

The close, maximize, restore and collapse (windowshade) widget SVGs, their
active state re-derived from `macos8.6-screenshots/aboutsystem_betawiki.png`
and `systemprofiler_betawiki.png` through `tools/png/loader.py`. The
reference's unfocused windows (`desktop_fandom.png`) draw no close, zoom or
collapse boxes in their title bars, so the inactive states ship no visible
art: each `inactive-center` group carries one paintless full-canvas path and
never a rect, so it renders nothing. The geometry keeps the group for a
platform reason: `/usr/share/kwin/aurorae/AuroraeButton.qml`'s
`buttonActive` overlay draws the active art on unfocused windows when
`supportsInactive` is false, and `FrameSvg::hasElementPrefix("inactive")`
reports true only for an element with valid bounds -- an empty `<g>` has
none, which is how the active boxes kept drawing on unfocused bars. The
references are stored with Git LFS, so a clone without them skips these
tests rather than failing `make check`.
"""

from __future__ import annotations

import os
import unittest

from support.aurorae_fixtures import (
    AURORAE_DIR,
    ReferenceImageCase,
    ZOOM_BOX_X,
)
from support.platinum_palette import hex_colour
from support.svg_case import parse_svg
from svg_assertions import (
    assert_no_script_elements,
    assert_unique_ids,
    children_named,
    groups_with_id,
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
    return [(os.path.basename(path), parse_svg(path)) for path in paths]


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
        slices = render_slices(parse_svg(CLOSE_SVG))
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
        slices = render_slices(parse_svg(SHADE_SVG))
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
        art = render_slices(parse_svg(path))[group]
        base = render_slices(parse_svg(CLOSE_SVG))[group]
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

    def test_inactive_center_ships_nothing(self):
        # The reference's unfocused windows draw no close, zoom or collapse
        # box at all (desktop_fandom.png), so every inactive state renders
        # nothing: the inactive-center slice holds no painted pixel, which is
        # fully transparent at every pixel of the widget's canvas. The one
        # paintless path it carries supplies KSvg geometry, not paint, so
        # hovering or pressing an unfocused window's button cannot erase or
        # change anything (BUGS.md's erasure symptom has nothing it can act
        # on).
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                slices = render_slices(tree)
                self.assertEqual(slices["inactive-center"], {})
                # The active art stays: focused windows keep the reference
                # boxes, so the canvas is not emptied wholesale.
                self.assertTrue(slices["active-center"])

    def test_inactive_center_keeps_paintless_geometry(self):
        # Each button SVG keeps exactly one element whose id carries the
        # `inactive` prefix, and that `inactive-center` group carries
        # geometry (one paintless full-canvas path) rather than being an
        # empty <g>. `/usr/share/kwin/aurorae/AuroraeButton.qml` (KWin
        # 6.3.6) hides the `buttonActive` overlay on unfocused windows only
        # when `supportsInactive` is true; KSvg resolves that through
        # `hasElement("inactive-center")` and a valid `boundsOnElement`, and
        # an empty group's zero bounds read as false -- so KWin painted the
        # active box on unfocused bars (reported 2026-11-05). The path's
        # `fill="none"` paints nothing, and the slice test above pins the
        # rendered result as fully transparent.
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                ids = [group.get("id") for group in groups_with_id(tree)]
                self.assertEqual(
                    [gid for gid in ids if "inactive" in gid],
                    ["inactive-center"],
                )
                (group,) = [
                    element
                    for element in tree.iter()
                    if element.get("id") == "inactive-center"
                ]
                (path,) = children_named(group, "path")
                self.assertEqual(path.get("fill"), "none")
                self.assertIsNone(path.get("stroke"))
                self.assertEqual(children_named(group, "rect"), [])

    def test_button_svgs_are_self_contained(self):
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                assert_no_script_elements(self, tree)


if __name__ == "__main__":
    unittest.main()
