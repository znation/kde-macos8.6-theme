"""Tests for the desktop theme's widgets/tooltip.svg Platinum tooltip."""

from __future__ import annotations

import unittest

from support.colorscheme_fixtures import load_scheme
from support.desktoptheme_paths import SOLID_TOOLTIP_SVG, TOOLTIP_SVG
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import BLACK, TOOLTIP_FACE, hex_colour
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    attribute_values,
    nine_slice_inset_hints,
    render_slices,
)


class TestTooltip(NineSliceCase, unittest.TestCase):
    SVG_PATH = TOOLTIP_SVG

    def test_tooltip_hint_geometry(self):
        # The 3px margins are the tooltip's text padding (ToolTip.qml reads
        # them as its paddings), so pin every hint, not only the ids.
        assert_hint_geometry(
            self,
            self.tree,
            [""],
            3,
            10,
            nine_slice_inset_hints("", 3, 10, 10),
        )

    def test_tooltip_pixels(self):
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, "", TOOLTIP_FACE, "flat", size=10)

    def test_tooltip_colours(self):
        self.assertEqual(
            attribute_values(self.tree, "fill"), {BLACK, TOOLTIP_FACE}
        )

    def test_face_is_the_scheme_tooltip_background(self):
        rgb = load_scheme().get("Colors:Tooltip", "BackgroundNormal")
        self.assertEqual(
            hex_colour([int(part) for part in rgb.split(",")]), TOOLTIP_FACE
        )

    def test_solid_copy_is_identical(self):
        # KSvg does not map `solid/widgets/tooltip` onto `widgets/tooltip`,
        # so PlasmaComponents.ToolTip needs its own copy of the artwork.
        with open(TOOLTIP_SVG, "rb") as plain, open(SOLID_TOOLTIP_SVG, "rb") as solid:
            self.assertEqual(solid.read(), plain.read())


if __name__ == "__main__":
    unittest.main()
