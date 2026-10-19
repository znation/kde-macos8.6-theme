"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import os
import unittest

from support.desktoptheme_paths import DIALOG_BACKGROUND_SVG
from support.platinum_palette import FACE, hex_colour
from support.raised_face_case import RaisedFaceCase
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT


class TestDialogBackground(RaisedFaceCase, unittest.TestCase):
    SVG_PATH = DIALOG_BACKGROUND_SVG


# The solid 4x6 #DDDDDD window-body block of the About This Computer window
# in macos8.6-screenshots/desktop_archiveorg8.6hd.png, below its title bar.
WINDOW_BODY_X = 583
WINDOW_BODY_Y = 95
WINDOW_BODY_WIDTH = 4
WINDOW_BODY_HEIGHT = 6


class TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = os.path.join(
        ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png"
    )
    MAX_ROWS = 101

    def test_window_body_is_the_reference_grey(self):
        # The reference is a 1x 800x600 capture, so one image pixel per
        # logical pixel; the body is re-derived here rather than trusted from
        # the artwork's FACE constant.
        for y in range(WINDOW_BODY_Y, WINDOW_BODY_Y + WINDOW_BODY_HEIGHT):
            for x in range(WINDOW_BODY_X, WINDOW_BODY_X + WINDOW_BODY_WIDTH):
                self.assertEqual(hex_colour(self.pixel(x, y)), FACE, (x, y))


if __name__ == "__main__":
    unittest.main()
