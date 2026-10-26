"""Tests for the desktop theme's bar_meter_horizontal.svg progress bar artwork."""

from __future__ import annotations

import os
import unittest

from support.desktoptheme_paths import (
    BAR_METER_HORIZONTAL_SVG,
    FANDOM_MAX_COLS,
    FANDOM_MAX_ROWS,
    FANDOM_REFERENCE,
)
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT

from svg_assertions import (  # noqa: E402
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_hint_geometry,
    assert_slice_pixels,
    assert_unique_ids,
    attribute_values,
    render_slices,
)

INACTIVE = "bar-inactive"
ACTIVE = "bar-active"

REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "boot2_betawiki.png")
GRADIENT_REFERENCE = FANDOM_REFERENCE

SHADOW = "#9A9A9A"
TRACK_FACE = "#ADADAD"
TRACK_LIGHT = "#B8B8B8"

# The fill's ten 1px rows, top to bottom, sampled from the interior column
# x=1600 of the "Mac OS 30.4 MB" memory meter in desktop_fandom.png at image
# rows 1230, 1232, ..., 1248 (2 image px per logical px).
FILL_ROWS = (
    "#515372",
    "#666799",
    "#8484BB",
    "#B0B0EB",
    "#CBCCFF",
    "#B2B2E8",
    "#8586BC",
    "#66679B",
    "#50527F",
    "#24244D",
)
# The fill's flat 1px left/right edge columns, sampled at (1458, 1238) and
# (1816, 1238); the right edge repeats FILL_ROWS[8].
FILL_LEFT_EDGE = "#68688D"
FILL_RIGHT_EDGE = "#50527F"

# Each track colour with the boot2_betawiki.png pixel it is sampled from.
TRACK_REFERENCE_PIXELS = (
    (SHADOW, (120, 99)),
    (TRACK_FACE, (120, 100)),
    (TRACK_LIGHT, (120, 102)),
)

# The boot2_betawiki.png fill column the artwork's provenance comment cites
# as the same gradient downscaled, at (102,99..102). The lossless
# desktop_fandom samples replaced these as the fill's primary ground truth,
# so only (102,100) is re-derived elsewhere (the splash fill); pin all four
# here so the "the two references agree" claim stays verified.
BOOT_FILL_PIXELS = (
    ("#7D7D9A", (102, 99)),
    ("#9B9BEA", (102, 100)),
    ("#7878D1", (102, 101)),
    ("#83839D", (102, 102)),
)

TILE = 4


def _band(rows, width, left_edge=None, right_edge=None):
    """Return the {(x, y): colour} map for *rows* painted *width* px wide.

    Each entry of *rows* is one 1px row, top to bottom. *left_edge* and
    *right_edge* override the outer column of every row, matching the flat
    edge columns the artwork paints over the gradient.
    """
    pixels = {
        (x, y): rows[y] for y in range(len(rows)) for x in range(width)
    }
    if left_edge is not None:
        for y in range(len(rows)):
            pixels[(0, y)] = left_edge
    if right_edge is not None:
        for y in range(len(rows)):
            pixels[(width - 1, y)] = right_edge
    return pixels


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

    def _assert_track_pixels(self):
        slices = render_slices(self.tree)
        assert_center_tile_is(
            self, slices, f"{INACTIVE}-center", TRACK_FACE, TILE
        )
        assert_edge_band_pixels(
            self, slices, f"{INACTIVE}-top", "top", (SHADOW, TRACK_FACE, TRACK_FACE), TILE
        )
        assert_edge_band_pixels(
            self,
            slices,
            f"{INACTIVE}-bottom",
            "bottom",
            (TRACK_FACE, TRACK_FACE, TRACK_LIGHT),
            TILE,
        )
        assert_edge_band_pixels(
            self, slices, f"{INACTIVE}-left", "left", (SHADOW, TRACK_FACE, TRACK_FACE), TILE
        )
        assert_edge_band_pixels(
            self,
            slices,
            f"{INACTIVE}-right",
            "right",
            (TRACK_FACE, TRACK_FACE, TRACK_LIGHT),
            TILE,
        )
        corners = {
            "topleft": (SHADOW,) * 3 + (SHADOW, TRACK_FACE, TRACK_FACE) * 2,
            "topright": (SHADOW,) * 3
            + (TRACK_FACE, TRACK_FACE, TRACK_LIGHT) * 2,
            "bottomleft": (SHADOW, TRACK_FACE, TRACK_FACE) * 2
            + (SHADOW, TRACK_LIGHT, TRACK_LIGHT),
            "bottomright": (TRACK_FACE, TRACK_FACE, TRACK_LIGHT) * 2
            + (TRACK_LIGHT,) * 3,
        }
        for name, expected in corners.items():
            assert_corner_pixels(self, slices, f"{INACTIVE}-{name}", expected)

    def _assert_bar_pixels(self):
        # Every fill tile is a run of the ten gradient rows, with the flat edge
        # column painted over the outer column of the left, right and corner
        # tiles.
        tiles = {
            "top": (FILL_ROWS[0:3], TILE, None, None),
            "center": (FILL_ROWS[3:7], TILE, None, None),
            "bottom": (FILL_ROWS[7:10], TILE, None, None),
            "left": (FILL_ROWS[3:7], 3, FILL_LEFT_EDGE, None),
            "right": (FILL_ROWS[3:7], 3, None, FILL_RIGHT_EDGE),
            "topleft": (FILL_ROWS[0:3], 3, FILL_LEFT_EDGE, None),
            "topright": (FILL_ROWS[0:3], 3, None, FILL_RIGHT_EDGE),
            "bottomleft": (FILL_ROWS[7:10], 3, FILL_LEFT_EDGE, None),
            "bottomright": (FILL_ROWS[7:10], 3, None, FILL_RIGHT_EDGE),
        }
        slices = render_slices(self.tree)
        for name, (rows, width, left_edge, right_edge) in tiles.items():
            assert_slice_pixels(
                self,
                slices,
                f"{ACTIVE}-{name}",
                _band(rows, width, left_edge, right_edge),
            )

    def test_track_pixels(self):
        self._assert_track_pixels()

    def test_fill_pixels(self):
        self._assert_bar_pixels()

    def test_progressbar_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the three
        # track colours plus the eleven distinct fill colours (the ten gradient
        # rows and the left edge column; the right edge repeats FILL_ROWS[8]).
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {SHADOW, TRACK_FACE, TRACK_LIGHT, *FILL_ROWS, FILL_LEFT_EDGE},
        )


class TestProgressBarReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE

    def test_track_colours_match_reference(self):
        # Every track colour the slice tests pin is the value of a boot-screen
        # progress bar pixel, not a guess.
        for colour, (x, y) in TRACK_REFERENCE_PIXELS:
            with self.subTest(colour=colour, pixel=(x, y)):
                self.assertEqual(hex_colour(self.pixel(x, y)), colour)

    def test_boot_fill_pixels_match_reference(self):
        # The artwork's provenance comment cites the boot2 fill column as the
        # same gradient downscaled, so the two references agree. The gradient
        # rows are grounded in desktop_fandom.png, and this is the only test
        # that re-derives three of these four boot2 pixels.
        for colour, (x, y) in BOOT_FILL_PIXELS:
            with self.subTest(pixel=(x, y)):
                self.assertEqual(hex_colour(self.pixel(x, y)), colour)


class TestFillGradientReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = GRADIENT_REFERENCE
    MAX_ROWS = FANDOM_MAX_ROWS
    MAX_COLS = FANDOM_MAX_COLS

    def test_fill_rows_match_reference(self):
        # The ten gradient rows are the interior column of the About This
        # Computer memory meter, two image rows apart.
        for index, colour in enumerate(FILL_ROWS):
            y = 1230 + 2 * index
            with self.subTest(row=index, pixel=(1600, y)):
                self.assertEqual(hex_colour(self.pixel(1600, y)), colour)

    def test_fill_edge_columns_match_reference(self):
        edges = ((FILL_LEFT_EDGE, 1458), (FILL_RIGHT_EDGE, 1816))
        for colour, x in edges:
            with self.subTest(colour=colour, pixel=(x, 1238)):
                self.assertEqual(hex_colour(self.pixel(x, 1238)), colour)


if __name__ == "__main__":
    unittest.main()
