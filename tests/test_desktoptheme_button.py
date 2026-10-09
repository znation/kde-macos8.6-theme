"""Tests for the desktop theme's button.svg push-button artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import BUTTON_SVG
from nine_slice_case import NineSliceCase
from platinum_palette import assert_fill_palette
from svg_assertions import (
    arc_center,
    assert_center_tile_is,
    assert_edge_bevels,
    assert_hint_geometry,
    assert_slice_pixels,
    children_named,
    elements_by_id,
    face_edge_bands,
    nine_slice_margins,
    path_arcs,
    render_slices,
)


BUTTON_PREFIXES = ("normal", "pressed", "focus")


class TestButton(NineSliceCase, unittest.TestCase):
    SVG_PATH = BUTTON_SVG
    PREFIXES = BUTTON_PREFIXES

    def test_button_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, and normal/pressed use a 3px
        # border while focus uses 2px, so pin every state's margins and the
        # shared centre tile.
        assert_hint_geometry(
            self,
            self.tree,
            ("normal", "pressed"),
            3,
            6,
            nine_slice_margins("focus", 2, 8),
        )

    def test_button_colours(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment and the hint rects (which set colour through `style`)
        # would otherwise make a text search pass without any Platinum grey.
        assert_fill_palette(self, self.tree)

    def test_button_bevel_direction(self):
        # `test_button_colours` sees the same four fills whichever way the
        # normal/pressed bevels run, so only the per-slice paint order pins
        # the direction: normal is #FFFFFF inside top/left and #999999 inside
        # bottom/right, and pressed is the exact inverse. Composite the edge
        # slices (their rects) and read the corner paths' document order.
        slices = render_slices(self.tree)
        # (outer outline, bevel, inner face), from the slice's outer edge in.
        outward = {
            "normal-top": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-bottom": ("#000000", "#999999", "#DDDDDD"),
            "normal-left": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-right": ("#000000", "#999999", "#DDDDDD"),
            "pressed-top": ("#000000", "#999999", "#DDDDDD"),
            "pressed-bottom": ("#000000", "#FFFFFF", "#DDDDDD"),
            "pressed-left": ("#000000", "#999999", "#DDDDDD"),
            "pressed-right": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in outward.items():
            pixels = slices[name]
            horizontal = name.endswith(("top", "bottom"))
            reversed_axis = name.endswith(("bottom", "right"))
            for depth, colour in enumerate(colours):
                local = 2 - depth if reversed_axis else depth
                point = (0, local) if horizontal else (local, 0)
                with self.subTest(slice=name, depth=depth):
                    self.assertEqual(pixels.get(point), colour, name)

        # The corner paths carry no rects, so `render_slices` cannot composite
        # them; pin the order they are painted in instead: the black outline,
        # the corner's bevel colour, then the face.
        by_id = elements_by_id(self.tree)
        corners = {
            "normal-topleft": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-topright": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomleft": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomright": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topleft": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topright": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomleft": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomright": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in corners.items():
            fills = tuple(
                child.get("fill")
                for child in children_named(by_id[name], "path")
            )
            with self.subTest(corner=name):
                self.assertEqual(fills, colours, name)

    def test_button_corner_arcs_curve_around_the_inner_corner(self):
        # `test_button_bevel_direction` reads the corner paths' fills only, so
        # a corner path whose `d` arcs the wrong way, at the wrong radius, or
        # around the wrong point passes every other test: the rounded corner
        # is the button's one piece of geometry no pixel test reaches. Read
        # each arc's centre and radius from `d` and pin both against the
        # slice's inner corner and the corner's layer radii. A flipped sweep
        # flag moves the centre to the opposite corner; a changed radius moves
        # it too, so this catches an arc the fill-order test cannot.
        expected = {
            # group: (inner corner, radii in document order)
            "normal-topleft": ((3, 3), (3, 2, 1)),
            "normal-topright": ((0, 3), (3, 2, 2, 1, 1)),
            "normal-bottomleft": ((3, 0), (3, 2, 2, 1, 1)),
            "normal-bottomright": ((0, 0), (3, 2, 1)),
            "pressed-topleft": ((3, 3), (3, 2, 1)),
            "pressed-topright": ((0, 3), (3, 2, 2, 1, 1)),
            "pressed-bottomleft": ((3, 0), (3, 2, 2, 1, 1)),
            "pressed-bottomright": ((0, 0), (3, 2, 1)),
            "focus-topleft": ((2, 2), (2, 1)),
            "focus-topright": ((0, 2), (2, 1)),
            "focus-bottomleft": ((2, 0), (2, 1)),
            "focus-bottomright": ((0, 0), (2, 1)),
        }
        by_id = elements_by_id(self.tree)
        for name, (center, radii) in expected.items():
            entries = [
                entry
                for path in children_named(by_id[name], "path")
                for entry in path_arcs(path.get("d"))
            ]
            with self.subTest(corner=name):
                self.assertEqual(
                    [arc[0] for _, arc, _ in entries], list(radii), name
                )
                for start, arc, end in entries:
                    rx, ry = arc[0], arc[1]
                    self.assertEqual(rx, ry, name)
                    actual = arc_center(start, arc, end)
                    # The mixed-corner arcs meet the diagonal at coordinates
                    # rounded to three decimals, so their reconstructed centre
                    # is within a thousandth of the exact inner corner.
                    self.assertAlmostEqual(actual[0], center[0], places=2, msg=name)
                    self.assertAlmostEqual(actual[1], center[1], places=2, msg=name)

    def test_button_edge_pixels(self):
        # `test_button_bevel_direction` reads only the first column of each
        # horizontal band and the first row of each vertical one, so it pins
        # the band order only while the band stays uniform along its axis: a
        # rect narrowed to one pixel -- an outline or bevel missing along most
        # of the edge -- still passes. The frame and lineedit edge tests pin
        # every pixel; do the same for the button's normal/pressed bands.
        slices = render_slices(self.tree)
        # (outer outline, bevel, inner face) for top/left, read from the
        # slice's outer edge in; bottom/right mirror it, with the outline
        # still on the outer edge and the bevel colour swapped.
        directions = {"normal": "raised", "pressed": "sunken"}
        for prefix, direction in directions.items():
            outward, mirrored = face_edge_bands("#DDDDDD", direction)
            assert_edge_bevels(self, slices, prefix, outward, mirrored)

    def test_button_center_tiles_are_face(self):
        # `test_button_colours` pins only the set of fills, so a centre tile
        # recoloured to another Platinum grey (#FFFFFF or #999999) passes it,
        # and neither bevel test reads the centre. The centre is the button
        # face for both states, so pin every pixel.
        slices = render_slices(self.tree)
        for name in ("normal-center", "pressed-center"):
            assert_center_tile_is(self, slices, name, "#DDDDDD", size=6)

    def test_button_focus_ring_pixels(self):
        # The focus state is a 1px #000000 ring on the outer pixel of its 2px
        # border, transparent inside and in the centre, so ButtonFocus draws
        # it 1-2px outside the button outline. `test_button_colours` sees the
        # same four fills whichever pixel of the border is painted, so only
        # pinning the pixels keeps the ring from sliding to the inner pixel,
        # being recoloured to another Platinum grey, or the centre from being
        # filled in.
        slices = render_slices(self.tree)
        expected = {
            "focus-top": {(x, 0): "#000000" for x in range(8)},
            "focus-bottom": {(x, 1): "#000000" for x in range(8)},
            "focus-left": {(0, y): "#000000" for y in range(8)},
            "focus-right": {(1, y): "#000000" for y in range(8)},
            "focus-center": {},
        }
        for name, pixels in expected.items():
            assert_slice_pixels(self, slices, name, pixels)

        # The rounded corners are paths, so `render_slices` cannot composite
        # them; pin that each carries exactly the one black ring path.
        by_id = elements_by_id(self.tree)
        for name in (
            "focus-topleft", "focus-topright",
            "focus-bottomleft", "focus-bottomright",
        ):
            with self.subTest(corner=name):
                self.assertEqual(
                    [
                        child.get("fill")
                        for child in children_named(by_id[name], "path")
                    ],
                    ["#000000"],
                    name,
                )


if __name__ == "__main__":
    unittest.main()
