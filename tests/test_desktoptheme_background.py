"""Tests for the desktop theme's widgets/background.svg Platinum menu body."""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.desktoptheme_paths import (
    BACKGROUND_SVG,
    TRANSLUCENT_BACKGROUND_SVG,
)
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import BLACK, FACE, hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    attribute_values,
    nine_slice_inset_hints,
    render_slices,
)


class TestBackground(NineSliceCase, unittest.TestCase):
    SVG_PATH = BACKGROUND_SVG

    def test_background_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # inset rect with the wrong position or size passes it while KSvg lays
        # the menu body out wrong. Pin every hint: a 3px border around a 10px
        # centre tile on the 16x16 canvas, plus the zero-size inset rects.
        assert_hint_geometry(
            self,
            self.tree,
            [""],
            3,
            10,
            nine_slice_inset_hints("", 3, 10, 10),
        )

    def test_background_pixels(self):
        # The body is a flat #DDDDDD face: a 1px #000000 outline on the outer
        # edge of each slice and no bevel. `assert_face_bevel` pins the 10x10
        # centre, the four edge tiles, and the four corners where the outline
        # turns.
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, "", FACE, "flat", size=10)

    def test_translucent_copy_is_identical(self):
        # BasicAppletContainer.qml resolves an applet's TranslucentBackground
        # hint to `widgets/translucentbackground`; the theme has no
        # translucent Platinum body, so that surface is the same opaque grey
        # artwork as the standard hint. A byte-identical copy keeps the two in
        # step.
        with open(BACKGROUND_SVG, "rb") as plain, open(
            TRANSLUCENT_BACKGROUND_SVG, "rb"
        ) as translucent:
            self.assertEqual(translucent.read(), plain.read())

    def test_background_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: the grey face and the black outline.
        self.assertEqual(
            attribute_values(self.tree, "fill"), {BLACK, FACE}
        )


class TestBackgroundMatchesReference(
    ReferenceScreenshotMixin, unittest.TestCase
):
    REFERENCE = os.path.join(
        ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png"
    )

    def test_menu_body_is_the_reference_grey(self):
        # The open Apple menu's empty right margin is clear of item text and
        # icons: (150, 60) and (150, 200) are the Platinum face. Compare them
        # to the artwork's own rendered face, so a recoloured SVG fails here
        # and not only in the shared FACE constant.
        face = render_slices(ET.parse(BACKGROUND_SVG))["center"][(5, 5)]
        for x, y in ((150, 60), (150, 200)):
            with self.subTest(pixel=(x, y)):
                self.assertEqual(hex_colour(self.pixel(x, y)), face)


if __name__ == "__main__":
    unittest.main()
