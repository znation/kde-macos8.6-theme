"""Tests for the org.macos8.desktop look-and-feel desktop layout.

The layout script is plain JavaScript run by plasmashell, so these tests read
its text with regular expressions. The panel height, the clock's time format and
the desktop icon column are each tied back to ``desktop_betawiki.png`` in
``macos8.6-screenshots/`` (the menu-bar rows, the "PM" glyph, the right-hand
32px icon column and its one-line labels), so a value that drifts from that
screenshot fails here.
"""

from __future__ import annotations

import os
import re
import unittest

from support.reference_image import ReferenceScreenshotMixin
from support.theme_install import ROOT

from tools import make_wallpaper, png  # noqa: E402

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
    """Return the ``panel.height`` literal in *text*, or ``None`` when absent."""
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
DESKTOP_ICONS = {"arrangement": 1, "alignment": 1, "iconSize": 1, "textLines": 1}


def clock_variable(text):
    """Return the variable the clock widget is assigned to, or ``None``."""
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


def desktop_config(text):
    """Return the desktop's ``writeConfig`` calls as ``{key: int}``."""
    calls = re.findall(
        r'^\s*desktopsArray\[j\]\.writeConfig\("([^"]+)",\s*(\d+)\s*\)\s*;',
        text,
        re.M,
    )
    return {key: int(raw) for key, raw in calls}


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

    def test_desktop_writes_the_general_group(self):
        loop = re.search(r"for \(var j", self.text)
        group = re.search(
            r'(?m)^\s*desktopsArray\[j\]\.currentConfigGroup\s*=\s*\["General"\]\s*;',
            self.text,
        )
        first_write = re.search(r"desktopsArray\[j\]\.writeConfig\(", self.text)
        self.assertIsNotNone(loop, "no desktop loop")
        self.assertIsNotNone(group, 'no currentConfigGroup = ["General"]')
        self.assertIsNotNone(first_write, "no desktop writeConfig call")
        self.assertLess(loop.start(), group.start())
        self.assertLess(group.start(), first_write.start())

    def test_desktop_icon_arrangement(self):
        self.assertEqual(DESKTOP_ICONS, desktop_config(self.text))

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
        """Return whether the reference pixel at ``(x, y)`` is dark (red < 100)."""
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


class TestDesktopIconsMatchReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE

    RIGHT_COLUMN_LEFT = 880
    SCAN_ROWS = range(20, 700)
    FIRST_ICON_ROWS = range(40, 81)
    ICON_ROWS = range(284, 329)
    LABELLED_ICON_ROWS = [(157, 200), (220, 264), (284, 328), (348, 392), (668, 712)]
    ICON_BODY = range(960, 992)
    LABEL_LINE = 13

    def differing_columns(self, y, left, right):
        """The x in ``[left, right)`` whose pixel in row *y* is not the tiled wallpaper."""
        rgb, width = self.image.rgb, self.image.width
        tile_x, tile_y = make_wallpaper.TILE_ORIGIN
        size = make_wallpaper.TILE_SIZE
        start = ((tile_y + y % size) * width + tile_x) * 3
        expected = rgb[start : start + size * 3] * (width // size + 1)
        row = rgb[y * width * 3 : (y + 1) * width * 3]
        if row[left * 3 : right * 3] == expected[left * 3 : right * 3]:
            return []
        return [
            x
            for x in range(left, right)
            if row[x * 3 : x * 3 + 3] != expected[x * 3 : x * 3 + 3]
        ]

    def test_icons_sit_in_one_right_column(self):
        stray = [
            (x, y)
            for y in self.SCAN_ROWS
            for x in self.differing_columns(y, 0, self.RIGHT_COLUMN_LEFT)
        ]
        self.assertEqual([], stray[:5])
        width = self.image.width
        self.assertTrue(
            any(
                self.differing_columns(y, self.RIGHT_COLUMN_LEFT, width)
                for y in self.FIRST_ICON_ROWS
            ),
            "no icon at the top of the right-hand column",
        )

    def test_icon_body_is_32_columns_wide(self):
        columns = {
            x
            for y in self.ICON_ROWS
            for x in self.differing_columns(y, 0, self.image.width)
        }
        self.assertEqual((960, 991), (min(columns), max(columns)))
        self.assertEqual(32, max(columns) - min(columns) + 1)

    def test_each_label_is_one_line(self):
        width = self.image.width
        beside_body = [
            x for x in range(self.RIGHT_COLUMN_LEFT, width) if x not in self.ICON_BODY
        ]
        for top, bottom in self.LABELLED_ICON_ROWS:
            margin = range(top - 5, bottom + 6)
            rows = [
                y
                for y in margin
                if self.differing_columns(y, self.RIGHT_COLUMN_LEFT, width)
            ]
            self.assertEqual(list(range(top, bottom + 1)), rows)
            label_rows = [
                y
                for y in margin
                if set(self.differing_columns(y, self.RIGHT_COLUMN_LEFT, width))
                & set(beside_body)
            ]
            if label_rows:
                self.assertEqual(
                    list(range(bottom - self.LABEL_LINE + 1, bottom + 1)), label_rows
                )


if __name__ == "__main__":
    unittest.main()
