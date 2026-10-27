"""Tests for the desktop theme's containment-controls.svg panel edit-mode art."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import CONTAINMENT_CONTROLS_SVG
from support.platinum_palette import BLACK, FACE, SELECTION, assert_fill_palette
from support.svg_case import SvgCase
from support.thumb_fixtures import raised_thumb_pixels
from svg_assertions import (
    assert_ids_present,
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_slice_pixels,
    assert_unique_ids,
    children_named,
    elements_by_id,
    local_name,
    render_slices,
    tile_origins,
)


FRAME_ELEMENTS = {}
for _side in ("north", "south"):
    FRAME_ELEMENTS[f"{_side}-center"] = (10, 12)
    FRAME_ELEMENTS[f"{_side}-top"] = (10, 1)
    FRAME_ELEMENTS[f"{_side}-bottom"] = (10, 1)
for _side in ("east", "west"):
    FRAME_ELEMENTS[f"{_side}-center"] = (12, 10)
    FRAME_ELEMENTS[f"{_side}-left"] = (1, 10)
    FRAME_ELEMENTS[f"{_side}-right"] = (1, 10)

INDICATORS = ("vertical-centerindicator", "horizontal-centerindicator")

# The centre grip each slider paints over its raised 9x9 thumb. The four
# offset sliders carry a 3x3 dot; a north/south min or max thumb carries a
# vertical 1x5 bar and an east/west one the horizontal 5x1 bar, so a grip
# turned onto the wrong axis fails.
OFFSET_GRIP = frozenset(
    (x, y) for x in range(3, 6) for y in range(3, 6)
)
VERTICAL_GRIP = frozenset((4, y) for y in range(2, 7))
HORIZONTAL_GRIP = frozenset((x, 4) for x in range(2, 7))

SLIDER_GRIPS = {}
for _side in ("north", "south", "east", "west"):
    SLIDER_GRIPS[f"{_side}-offsetslider"] = OFFSET_GRIP
    _minmax_grip = (
        VERTICAL_GRIP if _side in ("north", "south") else HORIZONTAL_GRIP
    )
    SLIDER_GRIPS[f"{_side}-minslider"] = _minmax_grip
    SLIDER_GRIPS[f"{_side}-maxslider"] = _minmax_grip

# The 42x1/1x42 line each centre indicator stretches along its panel edge.
INDICATOR_PIXELS = {
    "vertical-centerindicator": {
        (x, 0): SELECTION for x in range(42)
    },
    "horizontal-centerindicator": {
        (0, y): SELECTION for y in range(42)
    },
}


def _thumb_with_grip(grip):
    """Return the raised 9x9 thumb's pixel map with *grip* painted black."""
    pixels = raised_thumb_pixels(9, 9)
    for point in grip:
        pixels[point] = BLACK
    return pixels


class TestContainmentControls(SvgCase, unittest.TestCase):
    SVG_PATH = CONTAINMENT_CONTROLS_SVG

    def test_containment_controls_contract(self):
        # PanelConfiguration.qml resolves the twelve prefixed slider ids and
        # the twelve prefixed ruler frame slices, Ruler.qml the two centre
        # indicators, so a missing or duplicate id would leave a handle,
        # frame edge or indicator undrawn or mis-resolved.
        assert_ids_present(
            self, self.tree, (*FRAME_ELEMENTS, *SLIDER_GRIPS, *INDICATORS)
        )
        assert_unique_ids(self, self.tree)
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)

    def test_groups_sit_at_the_origin(self):
        # render_slices composites each group slice-locally and ignores its
        # transform, so a translated group would draw from the wrong canvas
        # region and still pass every pixel check. Pin every id-bearing group
        # at the origin the reference grid's 0-based coordinates promise.
        origins = tile_origins(self.tree)
        self.assertEqual(
            set(origins),
            set(FRAME_ELEMENTS) | set(SLIDER_GRIPS) | set(INDICATORS),
        )
        for name, origin in origins.items():
            with self.subTest(element=name):
                self.assertEqual(origin, (0, 0))

    def test_ruler_frame_slices_are_black_edges_on_a_face_band(self):
        # Ruler.qml's FrameSvgItem stretches each slice along the panel edge,
        # so a slice's natural size is its whole visible geometry: the 1px
        # black edge strips and the Platinum face centre. Pin each one so a
        # swapped edge or a shrunken centre cannot silently change the band.
        slices = render_slices(self.tree)
        by_id = elements_by_id(self.tree)
        for name, (width, height) in FRAME_ELEMENTS.items():
            with self.subTest(element=name):
                rects = children_named(by_id[name], "rect")
                self.assertEqual(len(rects), 1)
                self.assertEqual(local_name(rects[0]), "rect")
                self.assertEqual(
                    [rects[0].get(key) for key in ("width", "height")],
                    [str(width), str(height)],
                )
                fill = BLACK if "center" not in name else FACE
                self.assertEqual(rects[0].get("fill"), fill)
                self.assertEqual(
                    slices[name],
                    {(x, y): fill for x in range(width) for y in range(height)},
                )

    def test_sliders_are_raised_platinum_thumbs_with_grips(self):
        # Pin every pixel of each 9x9 group: a shifted bevel, a resized group
        # or a grip on the wrong axis would otherwise still pass an id or
        # fill-set check while the handle renders wrong.
        slices = render_slices(self.tree)
        for name, grip in SLIDER_GRIPS.items():
            assert_slice_pixels(self, slices, name, _thumb_with_grip(grip))

    def test_center_indicators_are_lavender_lines(self):
        # Each indicator is one pinned 42px line so a panel stretching it
        # along its edge draws a full-length line; every rect must also keep
        # KDE's 0.4 opacity or the line hides the widgets under it.
        slices = render_slices(self.tree)
        by_id = elements_by_id(self.tree)
        for name, expected in INDICATOR_PIXELS.items():
            with self.subTest(element=name):
                self.assertEqual(slices[name], expected)
                rects = children_named(by_id[name], "rect")
                self.assertEqual(len(rects), 1)
                self.assertEqual(local_name(rects[0]), "rect")
                self.assertEqual(rects[0].get("fill"), SELECTION)
                self.assertEqual(rects[0].get("fill-opacity"), "0.4")

    def test_containment_controls_colours(self):
        # The artwork reuses the grounded Platinum face/bevel palette plus the
        # selection lavender; a stray colour fails before any pixel check
        # could miss it.
        assert_fill_palette(self, self.tree, extra={SELECTION})


if __name__ == "__main__":
    unittest.main()
