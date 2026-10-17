"""Tests for the org.macos8.desktop look-and-feel desktop layout.

The layout script is plain JavaScript run by plasmashell, so these tests read
its text with regular expressions. The panel height is tied back to the rows of
the reference desktop screenshot so a height that drifts from the menu bar in
``macos8.6-screenshots/desktop_betawiki.png`` fails here.
"""

from __future__ import annotations

import os
import re
import unittest

from reference_image import ReferenceScreenshotMixin
from theme_install import ROOT

from tools import png  # noqa: E402

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
LAYOUT = os.path.join(
    PACKAGE, "contents", "layouts", "org.kde.plasma.desktop-layout.js"
)
REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "desktop_betawiki.png")

MENU_BAR_WIDGETS = [
    "org.kde.plasma.kicker",
    "org.kde.plasma.appmenu",
    "org.kde.plasma.panelspacer",
    "org.kde.plasma.systemtray",
    "org.kde.plasma.digitalclock",
    "org.kde.plasma.windowlist",
]

WHITE = (255, 255, 255)
BAR_GREY = (221, 221, 221)
BEVEL_GREY = (153, 153, 153)
BLACK = (0, 0, 0)
SAMPLE_COLUMN = 400


def _read_layout():
    with open(LAYOUT, encoding="utf-8") as handle:
        return handle.read()


def panel_height(text):
    match = re.search(r"^\s*panel\.height\s*=\s*(\d+)\s*;", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def menu_bar_rows(image, x):
    """Return the bar height at column *x*: the row after its black bottom rule.

    The rule is the first #000000 pixel whose next row is neither bar grey nor
    bevel grey.
    """
    for y in range(image.height - 1):
        if png.pixel_at(image, x, y) != BLACK:
            continue
        if png.pixel_at(image, x, y + 1) not in (BAR_GREY, BEVEL_GREY):
            return y + 1
    raise AssertionError(f"no menu-bar bottom rule at column {x}")


class TestLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = _read_layout() if os.path.isfile(LAYOUT) else ""

    def test_layout_file_is_shipped(self):
        self.assertTrue(os.path.isfile(LAYOUT), LAYOUT)

    def test_exactly_one_panel(self):
        self.assertEqual(1, len(re.findall(r"\bnew\s+Panel\b", self.text)))

    def test_panel_is_a_flush_top_bar(self):
        self.assertRegex(self.text, r'(?m)^panel\.location\s*=\s*"top"\s*;')
        self.assertRegex(self.text, r"(?m)^panel\.floating\s*=\s*false\s*;")
        self.assertIsNotNone(panel_height(self.text), "no literal panel.height")

    def test_widgets_in_menu_bar_order(self):
        ids = re.findall(r'^panel\.addWidget\("([^"]+)"\)\s*;', self.text, re.M)
        self.assertEqual(MENU_BAR_WIDGETS, ids)
        self.assertEqual(
            len(MENU_BAR_WIDGETS), self.text.count("addWidget("), "addWidget count"
        )

    def test_desktops_use_the_image_wallpaper(self):
        self.assertRegex(self.text, r"wallpaperPlugin\s*=\s*'org\.kde\.image'")

    def test_no_taskbar_template_is_loaded(self):
        self.assertNotIn("loadTemplate", self.text)


class TestPanelHeightMatchesReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE

    def test_panel_height_matches_the_reference(self):
        height = menu_bar_rows(self.image, SAMPLE_COLUMN)
        self.assertEqual(height, panel_height(_read_layout()))

    def test_reference_bar_rows(self):
        height = menu_bar_rows(self.image, SAMPLE_COLUMN)
        pixel = lambda y: self.pixel(SAMPLE_COLUMN, y)
        self.assertEqual(WHITE, pixel(0))
        self.assertEqual(BEVEL_GREY, pixel(height - 2))
        self.assertEqual(BLACK, pixel(height - 1))


if __name__ == "__main__":
    unittest.main()
