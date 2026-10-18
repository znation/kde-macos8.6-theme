"""Tests for the desktop theme's menubaritem.svg menu-bar title background."""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.desktoptheme_paths import MENUBARITEM_SVG
from support.nine_slice_case import NineSliceCase
from support.reference_image import ReferenceScreenshotMixin
from svg_assertions import (
    assert_slice_pixels,
    assert_slices_have_no_fill,
    assert_slices_uniform,
    attribute_values,
    nine_slice_tile_sizes,
    pixel_map,
    rect_geometry,
    render_slices,
)
from support.theme_install import ROOT

from tools import png  # noqa: E402

LEFT = RIGHT = 7
TOP = BOTTOM = 3
TILE = 6
SIZES = nine_slice_tile_sizes(20, 12, LEFT, RIGHT, TOP, BOTTOM)

REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "desktop_betawiki.png")
BLACK = (0, 0, 0)
TITLE_COLUMNS = range(32, 260)
TITLE_ROWS = range(1, 18)
TITLE_BREAK = 8


def title_gaps(image):
    """Return the blank-column gaps between the menu-bar titles of *image*.

    A column is ink when any pixel of rows 1..17 is #000000; a gap of
    TITLE_BREAK or more blank columns starts a new title.
    """
    ink = [
        x
        for x in TITLE_COLUMNS
        if any(png.pixel_at(image, x, y) == BLACK for y in TITLE_ROWS)
    ]
    gaps = []
    for previous, column in zip(ink, ink[1:]):
        blank = column - previous - 1
        if blank >= TITLE_BREAK:
            gaps.append(blank)
    return gaps


def expected_hint_geometry():
    """Return the expected ``{id: (x, y, width, height)}`` map for the hint rects."""
    expected = {"hint-tile-center": ("7", "3", "6", "6")}
    for prefix in ("normal", "hover", "pressed"):
        expected.update(
            {
                f"{prefix}-hint-top-margin": ("7", "0", "6", "3"),
                f"{prefix}-hint-bottom-margin": ("7", "9", "6", "3"),
                f"{prefix}-hint-left-margin": ("0", "3", "7", "6"),
                f"{prefix}-hint-right-margin": ("13", "3", "7", "6"),
            }
        )
    return expected


class TestMenuBarItem(NineSliceCase, unittest.TestCase):
    SVG_PATH = MENUBARITEM_SVG
    PREFIXES = ("normal", "hover", "pressed")

    def test_menubaritem_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the title out wrong. Pin every hint: all three prefixes share a
        # 7px left/right and 3px top/bottom border around a 6x6 centre tile on
        # the 20x12 canvas. The shared helper assumes one square border, so
        # the expected map is spelled out.
        self.assertEqual(rect_geometry(self.tree), expected_hint_geometry())

    def test_menubaritem_normal_and_hover_have_no_fill(self):
        # An idle or merely hovered title paints nothing perceptible: the
        # normal and hover rects carry no `fill` attribute and a 0.01 opacity,
        # so only their margins apply.
        assert_slices_have_no_fill(self, self.tree, "normal", "hover")

    def test_menubaritem_pressed_is_flat_selection_colour(self):
        # Every pressed slice must be the flat selection fill, so the open-menu
        # title cannot silently gain a bevel or the grey button face.
        assert_slices_uniform(
            self, render_slices(self.tree), "pressed", "#CCCCFF"
        )

    def test_menubaritem_slices_fill_their_tiles(self):
        # The colour tests above iterate each slice's pixels, so a rect one
        # pixel short (or long) passes while KSvg leaves a transparent stripe
        # in the stretched tile. Pin every slice to its exact tile region:
        # pressed is flat #CCCCFF, normal and hover carry no `fill` attribute
        # (only a 0.01-opacity style), so render_slices reads them as None.
        slices = render_slices(self.tree)
        for prefix, colour in (
            ("normal", None),
            ("hover", None),
            ("pressed", "#CCCCFF"),
        ):
            for name, (w, h) in SIZES.items():
                assert_slice_pixels(
                    self,
                    slices,
                    f"{prefix}-{name}",
                    pixel_map((colour,) * (w * h), w, h),
                )

    def test_menubaritem_colours(self):
        # The hints and the normal/hover slices use `style`, so the parsed
        # `fill` set is exactly the selection fill.
        self.assertEqual(attribute_values(self.tree, "fill"), {"#CCCCFF"})


class TestMenuTitleSpacingMatchesReference(
    ReferenceScreenshotMixin, unittest.TestCase
):
    REFERENCE = REFERENCE

    def test_reference_title_gaps(self):
        # File, Edit, View, Special and Help sit 15, 13, 14 and 15 blank
        # columns apart in the reference menu bar.
        self.assertEqual(title_gaps(self.image), [15, 13, 14, 15])

    def test_horizontal_margin_is_half_the_mean_gap(self):
        # An open title's highlight meets its neighbour's, so each side of a
        # title takes half the mean gap: 57 // 8 = 7.
        gaps = title_gaps(self.image)
        expected = str(sum(gaps) // (2 * len(gaps)))
        geometry = rect_geometry(ET.parse(MENUBARITEM_SVG))
        self.assertEqual(geometry["normal-hint-left-margin"][2], expected)
        self.assertEqual(geometry["normal-hint-right-margin"][2], expected)


if __name__ == "__main__":
    unittest.main()
