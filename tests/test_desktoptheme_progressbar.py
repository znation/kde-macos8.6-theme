"""Tests for the desktop theme's bar_meter_horizontal.svg progress bar artwork."""

from __future__ import annotations

import os
import unittest

from desktoptheme_paths import BAR_METER_HORIZONTAL_SVG
from nine_slice_case import NineSliceCase
from platinum_palette import hex_colour
from reference_image import read_reference, skip_unless_materialized
from theme_install import ROOT

from tools import png  # noqa: E402
from svg_assertions import (  # noqa: E402
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_hint_geometry,
    assert_unique_ids,
    attribute_values,
    render_slices,
)

INACTIVE = "bar-inactive"
ACTIVE = "bar-active"

REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "boot2_betawiki.png")

SHADOW = "#9A9A9A"
TRACK_FACE = "#ADADAD"
TRACK_LIGHT = "#B8B8B8"
FILL_FACE = "#9B9BEA"
FILL_LIGHT = "#7878D1"

# Each colour with the boot2_betawiki.png pixel it is sampled from.
REFERENCE_PIXELS = (
    (SHADOW, (120, 99)),
    (TRACK_FACE, (120, 100)),
    (TRACK_LIGHT, (120, 102)),
    (FILL_FACE, (102, 100)),
    (FILL_LIGHT, (102, 101)),
)

TILE = 4


class TestProgressBar(NineSliceCase, unittest.TestCase):
    SVG_PATH = BAR_METER_HORIZONTAL_SVG
    PREFIXES = (INACTIVE, ACTIVE)

    def test_progressbar_ids_are_unique(self):
        assert_unique_ids(self, self.tree)

    def test_progressbar_hint_geometry(self):
        # A 3px border around a 4px centre tile on the 10x10 canvas, plus the
        # hint-bar-size element ProgressBar.qml reads for the bar's height.
        assert_hint_geometry(
            self,
            self.tree,
            [INACTIVE, ACTIVE],
            3,
            TILE,
            extra={"hint-bar-size": ("0", "0", "10", "10")},
        )

    def _assert_bar_pixels(self, prefix, face, light):
        slices = render_slices(self.tree)
        assert_center_tile_is(self, slices, f"{prefix}-center", face, TILE)
        assert_edge_band_pixels(
            self, slices, f"{prefix}-top", "top", (SHADOW, face, face), TILE
        )
        assert_edge_band_pixels(
            self, slices, f"{prefix}-bottom", "bottom", (face, face, light), TILE
        )
        assert_edge_band_pixels(
            self, slices, f"{prefix}-left", "left", (SHADOW, face, face), TILE
        )
        assert_edge_band_pixels(
            self, slices, f"{prefix}-right", "right", (face, face, light), TILE
        )
        corners = {
            "topleft": (SHADOW,) * 3 + (SHADOW, face, face) * 2,
            "topright": (SHADOW,) * 3 + (face, face, light) * 2,
            "bottomleft": (SHADOW, face, face) * 2 + (SHADOW, light, light),
            "bottomright": (face, face, light) * 2 + (light,) * 3,
        }
        for name, expected in corners.items():
            assert_corner_pixels(self, slices, f"{prefix}-{name}", expected)

    def test_track_pixels(self):
        self._assert_bar_pixels(INACTIVE, TRACK_FACE, TRACK_LIGHT)

    def test_fill_pixels(self):
        self._assert_bar_pixels(ACTIVE, FILL_FACE, FILL_LIGHT)

    def test_progressbar_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the five
        # artwork colours.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {SHADOW, TRACK_FACE, TRACK_LIGHT, FILL_FACE, FILL_LIGHT},
        )


class TestProgressBarReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, cls.image_error = read_reference(REFERENCE)

    def setUp(self):
        skip_unless_materialized(self, REFERENCE, self.image_error)

    def test_colours_match_reference(self):
        # Every colour the slice tests pin is the value of a boot-screen
        # progress bar pixel, not a guess.
        for colour, (x, y) in REFERENCE_PIXELS:
            with self.subTest(colour=colour, pixel=(x, y)):
                self.assertEqual(hex_colour(png.pixel_at(self.image, x, y)), colour)


if __name__ == "__main__":
    unittest.main()
