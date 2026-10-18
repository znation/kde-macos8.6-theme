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


CLOCK_ID = "org.kde.plasma.digitalclock"
CLOCK_FORMAT = {"showDate": False, "showSeconds": 0, "use24hFormat": 0}
JS_LITERALS = {"false": False, "true": True}


def clock_variable(text):
    match = re.search(
        r'^var\s+(\w+)\s*=\s*panel\.addWidget\("%s"\)\s*;' % re.escape(CLOCK_ID),
        text,
        re.M,
    )
    return match.group(1) if match else None


def clock_config(text):
    """Return the clock's ``writeConfig`` calls as ``{key: value}`` (JS literals)."""
    name = clock_variable(text)
    if name is None:
        return {}
    calls = re.findall(
        r'^%s\.writeConfig\("([^"]+)",\s*(\w+)\s*\)\s*;' % re.escape(name),
        text,
        re.M,
    )
    return {
        key: JS_LITERALS[raw] if raw in JS_LITERALS else int(raw)
        for key, raw in calls
    }


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
        ids = re.findall(
            r'^(?:var\s+\w+\s*=\s*)?panel\.addWidget\("([^"]+)"\)\s*;',
            self.text,
            re.M,
        )
        self.assertEqual(MENU_BAR_WIDGETS, ids)
        self.assertEqual(
            len(MENU_BAR_WIDGETS), self.text.count("addWidget("), "addWidget count"
        )

    def test_clock_writes_the_appearance_group(self):
        name = clock_variable(self.text)
        self.assertIsNotNone(name, "clock widget handle is not kept in a variable")
        group = re.search(
            r'^%s\.currentConfigGroup\s*=\s*\["Appearance"\]\s*;' % re.escape(name),
            self.text,
            re.M,
        )
        self.assertIsNotNone(group, "no currentConfigGroup = [\"Appearance\"]")
        first_write = re.search(r"^%s\.writeConfig\(" % re.escape(name), self.text, re.M)
        self.assertIsNotNone(first_write, "no writeConfig call")
        self.assertLess(group.start(), first_write.start())

    def test_clock_format_matches_reference(self):
        self.assertEqual(CLOCK_FORMAT, clock_config(self.text))

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


class TestClockMatchesReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE

    CLOCK_LEFT = 882
    CLOCK_RIGHT = 925
    CLOCK_TOP = 5
    CLOCK_BOTTOM = 13
    PM_LEFT = 909
    PM_GLYPH = [
        "#####..##......##",
        "##..##.##......##",
        "##..##.###....###",
        "##..##.###....###",
        "#####..#.##..#.##",
        "##.....#.##..#.##",
        "##.....#..###..##",
        "##.....#..###..##",
        "##.....#...#...##",
    ]

    def dark(self, x, y):
        return self.pixel(x, y)[0] < 100

    def test_reference_clock_is_one_line(self):
        dark = [
            (x, y)
            for y in range(1, 18)
            for x in range(800, 933)
            if self.dark(x, y)
        ]
        columns = [x for x, _ in dark]
        self.assertEqual((self.CLOCK_LEFT, self.CLOCK_RIGHT), (min(columns), max(columns)))
        rows = [y for _, y in dark]
        self.assertGreaterEqual(min(rows), self.CLOCK_TOP)
        self.assertLessEqual(max(rows), self.CLOCK_BOTTOM)

    def test_reference_clock_has_am_pm_suffix(self):
        glyph = [
            "".join(
                "#" if self.dark(x, y) else "."
                for x in range(self.PM_LEFT, self.CLOCK_RIGHT + 1)
            )
            for y in range(self.CLOCK_TOP, self.CLOCK_BOTTOM + 1)
        ]
        self.assertEqual(self.PM_GLYPH, glyph)


if __name__ == "__main__":
    unittest.main()
