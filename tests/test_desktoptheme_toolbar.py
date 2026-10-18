"""Tests for the desktop theme's widgets/toolbar.svg Platinum toolbar background."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import TOOLBAR_SVG
from support.raised_face_case import RaisedFaceCase


class TestToolBar(RaisedFaceCase, unittest.TestCase):
    SVG_PATH = TOOLBAR_SVG


if __name__ == "__main__":
    unittest.main()
