"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import (
    REFERENCE as ABOUTSYSTEM_REFERENCE,
    REFERENCE_ROWS as ABOUTSYSTEM_MAX_ROWS,
)
from support.desktoptheme_paths import (
    ARCHIVEORG_MAX_ROWS,
    ARCHIVEORG_REFERENCE,
    DIALOG_BACKGROUND_SVG,
    FANDOM_MAX_ROWS,
    FANDOM_REFERENCE,
)
from support.platinum_palette import BLACK, FACE, WHITE, hex_colour
from support.raised_face_case import RaisedFaceCase
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import (
    assert_edge_bevels,
    assert_face_corners,
    face_edge_bands,
    render_slices,
)


# The reference's raised window-body bevel shadow in aboutsystem_betawiki.png.
DIALOG_SHADOW = "#AAAAAA"

# The Get Info body's 3x3 corners. Unlike the shared raised table, its
# top-right and bottom-left mixed corners leave a #DDDDDD face pixel where
# the highlight and shadow bands would meet (the reference's diagonal).
DIALOG_FACE_CORNERS = {
    "topleft": (
        BLACK, BLACK, BLACK,
        BLACK, WHITE, WHITE,
        BLACK, WHITE, FACE,
    ),
    "topright": (
        BLACK, BLACK, BLACK,
        WHITE, FACE, BLACK,
        FACE, DIALOG_SHADOW, BLACK,
    ),
    "bottomleft": (
        BLACK, WHITE, FACE,
        BLACK, FACE, DIALOG_SHADOW,
        BLACK, BLACK, BLACK,
    ),
    "bottomright": (
        FACE, DIALOG_SHADOW, BLACK,
        DIALOG_SHADOW, DIALOG_SHADOW, BLACK,
        BLACK, BLACK, BLACK,
    ),
}


class TestDialogBackground(RaisedFaceCase, unittest.TestCase):
    SVG_PATH = DIALOG_BACKGROUND_SVG
    SHADOW = DIALOG_SHADOW
    CORNERS = DIALOG_FACE_CORNERS


# The Get Info window body inside the 6px Aurorae frame in
# aboutsystem_betawiki.png: the frame's inner black row/column is the visible
# outline, then the body paints a #FFFFFF top/left highlight, a #DDDDDD face
# and a #AAAAAA bottom/right shadow. Absolute image coordinates.
_REFERENCE_ANCHORS = {
    "frame_outline": (200, 46),
    "highlight": (200, 47),
    "face": (200, 100),
    "shadow": (200, 418),
}

# The four 3x3 body corners in the same image, at the frame's inner edge.
_REFERENCE_CORNERS = {
    "topleft": (12, 46),
    "topright": (352, 46),
    "bottomleft": (12, 417),
    "bottomright": (352, 417),
}


class TestDialogBackgroundRaisedReference(
    ReferenceScreenshotMixin, unittest.TestCase
):
    """The window body's raised bevel is the reference Get Info body's.

    The archiveorg reference below pins only the #DDDDDD face. This re-derives
    the body's bevel colours and corner slices from the beta Get Info
    screenshot and requires the shipped artwork to paint them, so a body that
    keeps the other raised faces' #999999 shadow or fills its mixed corners
    fails.
    """

    REFERENCE = ABOUTSYSTEM_REFERENCE
    MAX_ROWS = ABOUTSYSTEM_MAX_ROWS

    def _reference_colours(self):
        """Return the reference body's four colours, sampled at their anchors."""
        return {
            name: hex_colour(self.pixel(x, y))
            for name, (x, y) in _REFERENCE_ANCHORS.items()
        }

    def _reference_corners(self):
        """Return the body's four 3x3 corners, sampled at their origins."""
        return {
            name: tuple(
                hex_colour(self.pixel(x, y))
                for y in range(origin_y, origin_y + 3)
                for x in range(origin_x, origin_x + 3)
            )
            for name, (origin_x, origin_y) in _REFERENCE_CORNERS.items()
        }

    def test_reference_window_body_is_the_raised_arrangement(self):
        # Derive the colours from one pixel each, then pin the values. The
        # frame's inner black row/column sits just outside the body's white
        # highlight and #AAAAAA shadow on every edge.
        colours = self._reference_colours()
        self.assertEqual(colours["frame_outline"], BLACK)
        self.assertEqual(colours["highlight"], WHITE)
        self.assertEqual(colours["face"], FACE)
        self.assertEqual(colours["shadow"], DIALOG_SHADOW)
        self.assertEqual(hex_colour(self.pixel(12, 200)), BLACK)
        self.assertEqual(hex_colour(self.pixel(13, 200)), WHITE)
        self.assertEqual(hex_colour(self.pixel(200, 419)), BLACK)
        self.assertEqual(hex_colour(self.pixel(353, 200)), DIALOG_SHADOW)
        self.assertEqual(hex_colour(self.pixel(354, 200)), BLACK)
        self.assertEqual(self._reference_corners(), DIALOG_FACE_CORNERS)

    def test_shipped_dialog_paints_the_reference_bevel(self):
        # Build the expected bands and corners from the reference colours, not
        # the SVG's own literals: a #999999 bottom/right shadow, a swapped
        # bevel or a filled mixed corner fails. The edge slices and corners
        # are rects, so `render_slices` composites them.
        colours = self._reference_colours()
        tree = parse_svg(DIALOG_BACKGROUND_SVG)
        slices = render_slices(tree)
        outward, mirrored = face_edge_bands(
            colours["face"], "raised", shadow=colours["shadow"]
        )
        assert_edge_bevels(self, slices, "", outward, mirrored, size=10)
        assert_face_corners(self, slices, "", self._reference_corners())


# The solid 4x6 #DDDDDD window-body block of the About This Computer window
# in macos8.6-screenshots/desktop_archiveorg8.6hd.png, below its title bar.
WINDOW_BODY_X = 583
WINDOW_BODY_Y = 95
WINDOW_BODY_WIDTH = 4
WINDOW_BODY_HEIGHT = 6


class TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = ARCHIVEORG_REFERENCE
    MAX_ROWS = ARCHIVEORG_MAX_ROWS

    def test_window_body_is_the_reference_grey(self):
        # The reference is a 1x 800x600 capture, so one image pixel per
        # logical pixel; the body is re-derived here rather than trusted from
        # the artwork's FACE constant.
        for y in range(WINDOW_BODY_Y, WINDOW_BODY_Y + WINDOW_BODY_HEIGHT):
            for x in range(WINDOW_BODY_X, WINDOW_BODY_X + WINDOW_BODY_WIDTH):
                self.assertEqual(hex_colour(self.pixel(x, y)), FACE, (x, y))


# The cross-check dialogs/background.svg's comment cites: the same window-body
# grey at (1792, 1126) of macos8.6-screenshots/desktop_fandom.png, a 2x
# upscale, in the About This Computer window. A 4x4 block around the cited
# pixel proves it sits in a solid region rather than on an edge.
FANDOM_BODY_X = 1792
FANDOM_BODY_Y = 1126
FANDOM_BODY_WIDTH = 4
FANDOM_BODY_HEIGHT = 4


class TestDialogBackgroundFandomReference(
    ReferenceScreenshotMixin, unittest.TestCase
):
    REFERENCE = FANDOM_REFERENCE
    MAX_ROWS = FANDOM_MAX_ROWS

    def test_cross_check_body_is_the_reference_grey(self):
        # Re-derive the #DDDDDD value at the coordinate the SVG comment
        # cites. This pins the pixel, not the comment text: editing the
        # coordinate in background.svg would not fail this test.
        for y in range(FANDOM_BODY_Y, FANDOM_BODY_Y + FANDOM_BODY_HEIGHT):
            for x in range(FANDOM_BODY_X, FANDOM_BODY_X + FANDOM_BODY_WIDTH):
                self.assertEqual(hex_colour(self.pixel(x, y)), FACE, (x, y))


if __name__ == "__main__":
    unittest.main()
