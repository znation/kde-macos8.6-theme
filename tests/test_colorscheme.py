"""Validate the Mac OS 8.6 Platinum color scheme and its install path."""

import configparser
import math
import os
import re
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.6.colors")

# configparser reads the KDE `[Colors:Header][Inactive]` header greedily, so the
# section key includes the inner bracket pair.
COLORS_SECTIONS = [
    "Colors:Button",
    "Colors:Complementary",
    "Colors:Header",
    "Colors:Header][Inactive",
    "Colors:Selection",
    "Colors:Tooltip",
    "Colors:View",
    "Colors:Window",
]

COLORS_KEYS = [
    "BackgroundAlternate",
    "BackgroundNormal",
    "DecorationFocus",
    "DecorationHover",
    "ForegroundActive",
    "ForegroundInactive",
    "ForegroundLink",
    "ForegroundNegative",
    "ForegroundNeutral",
    "ForegroundNormal",
    "ForegroundPositive",
    "ForegroundVisited",
]

OTHER_SECTIONS = {
    "ColorEffects:Disabled": [
        "Color", "ColorAmount", "ColorEffect", "ContrastAmount",
        "ContrastEffect", "IntensityAmount", "IntensityEffect",
    ],
    "ColorEffects:Inactive": [
        "ChangeSelectionColor", "Color", "ColorAmount", "ColorEffect",
        "ContrastAmount", "ContrastEffect", "Enable", "IntensityAmount",
        "IntensityEffect",
    ],
    "General": ["ColorScheme", "Name", "shadeSortColumn"],
    "KDE": ["contrast"],
    "WM": [
        "activeBackground", "activeBlend", "activeForeground",
        "inactiveBackground", "inactiveBlend", "inactiveForeground",
    ],
}

RGB_RE = re.compile(r"^\d{1,3},\d{1,3},\d{1,3}$")

# Every value KDE parses as an RGB triple: the semantic roles in each [Colors:*]
# section, the [WM] window-decoration colours, and the base `Color` of the two
# ColorEffects sections. The amounts and booleans have their own range/format
# tests below; the effect selectors and the [KDE] scalar are checked only for
# presence by test_other_sections_and_keys.
RGB_VALUES = (
    [(section, key) for section in COLORS_SECTIONS for key in COLORS_KEYS]
    + [(section, "Color") for section in ("ColorEffects:Disabled", "ColorEffects:Inactive")]
    + [("WM", key) for key in OTHER_SECTIONS["WM"]]
)

# KDE reads these as qreal amounts in [0, 1]; a value outside that range silently
# changes how disabled/inactive colours are derived.
EFFECT_AMOUNTS = [
    (section, key)
    for section in ("ColorEffects:Disabled", "ColorEffects:Inactive")
    for key in ("ColorAmount", "ContrastAmount", "IntensityAmount")
]

# KDE boolean spellings, lower-cased for comparison.
KDE_BOOLEANS = frozenset({"true", "false", "1", "0", "on", "off"})
BOOLEAN_VALUES = [
    ("ColorEffects:Inactive", "ChangeSelectionColor"),
    ("ColorEffects:Inactive", "Enable"),
    ("General", "shadeSortColumn"),
]


def load_scheme():
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # KDE keys are case-sensitive.
    with open(SCHEME, encoding="utf-8") as handle:
        parser.read_file(handle)
    return parser


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.parser = load_scheme()

    def test_parses(self):
        self.assertTrue(self.parser.sections())

    def test_colors_sections_and_keys(self):
        for section in COLORS_SECTIONS:
            self.assertTrue(self.parser.has_section(section), section)
            for key in COLORS_KEYS:
                self.assertTrue(
                    self.parser.has_option(section, key), f"{section}/{key}"
                )

    def test_other_sections_and_keys(self):
        for section, keys in OTHER_SECTIONS.items():
            self.assertTrue(self.parser.has_section(section), section)
            for key in keys:
                self.assertTrue(
                    self.parser.has_option(section, key), f"{section}/{key}"
                )

    def test_color_values_are_rgb(self):
        for section, key in RGB_VALUES:
            value = self.parser.get(section, key)
            self.assertRegex(value, RGB_RE, f"{section}/{key}")
            for component in value.split(","):
                self.assertLessEqual(int(component), 255, f"{section}/{key}")

    def test_coloreffects_amounts_are_in_range(self):
        for section, key in EFFECT_AMOUNTS:
            value = self.parser.get(section, key)
            try:
                amount = float(value)
            except ValueError:
                self.fail(f"{section}/{key} is not a number: {value!r}")
            self.assertTrue(
                math.isfinite(amount), f"{section}/{key} is not finite: {value!r}"
            )
            self.assertGreaterEqual(amount, 0.0, f"{section}/{key}")
            self.assertLessEqual(amount, 1.0, f"{section}/{key}")

    def test_boolean_values_use_kde_spellings(self):
        for section, key in BOOLEAN_VALUES:
            value = self.parser.get(section, key)
            self.assertIn(
                value.lower(), KDE_BOOLEANS, f"{section}/{key} = {value!r}"
            )


class TestAnchors(unittest.TestCase):
    """The palette anchors sampled from the retail reference screenshots."""

    def setUp(self):
        self.parser = load_scheme()

    def assert_value(self, section, key, expected):
        self.assertEqual(self.parser.get(section, key), expected, f"{section}/{key}")

    def test_face_backgrounds(self):
        for section in ("Colors:Window", "Colors:Button", "Colors:Header"):
            self.assert_value(section, "BackgroundNormal", "221,221,221")

    def test_view_background(self):
        self.assert_value("Colors:View", "BackgroundNormal", "255,255,255")

    def test_selection_background(self):
        self.assert_value("Colors:Selection", "BackgroundNormal", "206,206,255")

    def test_tooltip_background(self):
        self.assert_value("Colors:Tooltip", "BackgroundNormal", "255,255,204")

    def test_window_foreground(self):
        self.assert_value("Colors:Window", "ForegroundNormal", "0,0,0")


class TestInstall(unittest.TestCase):
    def test_make_install_copies_scheme_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["make", "install", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = os.path.join(
                tmp, "share", "color-schemes", "MacOS8.6.colors"
            )
            self.assertTrue(os.path.isfile(installed), installed)
            with open(SCHEME, "rb") as source, open(installed, "rb") as target:
                self.assertEqual(source.read(), target.read())


if __name__ == "__main__":
    unittest.main()
