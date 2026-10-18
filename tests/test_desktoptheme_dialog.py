"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import unittest

from desktoptheme_paths import DIALOG_BACKGROUND_SVG
from raised_face_case import RaisedFaceCase


class TestDialogBackground(RaisedFaceCase, unittest.TestCase):
    SVG_PATH = DIALOG_BACKGROUND_SVG


if __name__ == "__main__":
    unittest.main()
