"""The shipped Konsole colorscheme `theme/konsole/MacOS8.colorscheme` matches its sources.

Konsole reads a colorscheme as a KConfig INI file: one `[Group]` per color,
each holding `Color=R,G,B`. The background and foreground groups, and their
intense variants, must equal `[Colors:View]` in `MacOS8.colors`. Slots 0 to 7
must equal the classic 16-color table pinned in `tests/test_ghostty_theme.py`,
and slots 8 to 15 are the `...Intense` groups. The file has no selection group:
Konsole's colorscheme grammar has none. Every value is re-derived here, so a
drift in either source fails a pin.
"""

import configparser
import os
import unittest

from support.colorscheme_fixtures import load_scheme
from support.repo_root import ROOT
from test_ghostty_theme import PALETTE

SHIPPED = os.path.join(ROOT, "theme", "konsole", "MacOS8.colorscheme")

# Konsole's colorscheme group names: the base colors, their intense variants,
# the sixteen palette slots and the `[General]` block.
ALLOWED_GROUPS = (
    {"Background", "BackgroundIntense", "Foreground", "ForegroundIntense", "General"}
    | {f"Color{index}" for index in range(8)}
    | {f"Color{index}Intense" for index in range(8)}
)


def _read_shipped():
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(SHIPPED, encoding="utf-8")
    return parser


def _rgb_from_hex(color):
    """`#rrggbb` as an `(r, g, b)` tuple of integers."""
    return tuple(int(color[offset:offset + 2], 16) for offset in (1, 3, 5))


def _rgb_from_file(parser, group):
    """`[group] Color=R,G,B` from the shipped file, as an `(r, g, b)` tuple."""
    return tuple(int(part) for part in parser[group]["Color"].split(","))


def _rgb_from_scheme(section, key):
    """`[section] key` from MacOS8.colors, as an `(r, g, b)` tuple."""
    return tuple(int(part) for part in load_scheme()[section][key].split(","))


class TestKonsoleGroups(unittest.TestCase):
    """Only the colorscheme groups Konsole reads appear in the file."""

    @classmethod
    def setUpClass(cls):
        cls.parser = _read_shipped()

    def test_every_group_is_a_konsole_colorscheme_group(self):
        self.assertLessEqual(set(self.parser.sections()), ALLOWED_GROUPS)

    def test_every_palette_and_base_group_is_present(self):
        required = ALLOWED_GROUPS - {"General"}
        self.assertLessEqual(required, set(self.parser.sections()))


class TestKonsoleBaseColors(unittest.TestCase):
    """The base colors and their intense variants equal the `[Colors:View]` roles."""

    @classmethod
    def setUpClass(cls):
        cls.parser = _read_shipped()

    def test_background_is_the_view_background(self):
        self.assertEqual(
            _rgb_from_file(self.parser, "Background"),
            _rgb_from_scheme("Colors:View", "BackgroundNormal"),
        )

    def test_background_intense_is_the_view_background(self):
        self.assertEqual(
            _rgb_from_file(self.parser, "BackgroundIntense"),
            _rgb_from_scheme("Colors:View", "BackgroundNormal"),
        )

    def test_foreground_is_the_view_foreground(self):
        self.assertEqual(
            _rgb_from_file(self.parser, "Foreground"),
            _rgb_from_scheme("Colors:View", "ForegroundNormal"),
        )

    def test_foreground_intense_is_the_view_foreground(self):
        self.assertEqual(
            _rgb_from_file(self.parser, "ForegroundIntense"),
            _rgb_from_scheme("Colors:View", "ForegroundNormal"),
        )


class TestKonsolePalette(unittest.TestCase):
    """Slots 0 to 7 are the classic table's normal colors; 8 to 15 are the intense ones."""

    @classmethod
    def setUpClass(cls):
        cls.parser = _read_shipped()

    def test_normal_group_n_is_palette_slot_n(self):
        for index in range(8):
            self.assertEqual(
                _rgb_from_file(self.parser, f"Color{index}"),
                _rgb_from_hex(PALETTE[index]),
                f"Color{index}",
            )

    def test_intense_group_n_is_palette_slot_n_plus_eight(self):
        for index in range(8):
            self.assertEqual(
                _rgb_from_file(self.parser, f"Color{index}Intense"),
                _rgb_from_hex(PALETTE[index + 8]),
                f"Color{index}Intense",
            )


if __name__ == "__main__":
    unittest.main()
