"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import (
    ARCHIVEORG_MAX_ROWS,
    ARCHIVEORG_REFERENCE,
    DIALOG_BACKGROUND_SVG,
    FANDOM_MAX_ROWS,
    FANDOM_REFERENCE,
)
from support.platinum_palette import FACE, hex_colour
from support.raised_face_case import RaisedFaceCase
from support.reference_image import ReferenceScreenshotMixin


class TestDialogBackground(RaisedFaceCase, unittest.TestCase):
    SVG_PATH = DIALOG_BACKGROUND_SVG


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
