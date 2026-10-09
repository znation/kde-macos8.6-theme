"""Validate the Mac OS 8.6 Platinum color scheme file.

The scheme's structure, its palette anchors, and the provenance note on the
tooltip token. The reference-screenshot anchors and the install/uninstall
lifecycle live in ``test_colorscheme_reference`` and
``test_colorscheme_install``.
"""

import math
import os
import re
import unittest

from colorscheme_fixtures import SCHEME, load_scheme

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
    # KDE reads `[KDE] contrast` as an integer (KColorScheme::contrastF scales
    # an int), so it gets its own format test below rather than only presence.
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
# tests below; the effect selectors and the [KDE] scalar have their own integer
# tests.
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

# KDE reads these as integer selectors into its ColorEffect/ContrastEffect/
# IntensityEffect enums; a non-integer value is silently treated as a default,
# so a typo would quietly change how disabled/inactive colours are derived.
EFFECT_SELECTORS = [
    (section, key)
    for section in ("ColorEffects:Disabled", "ColorEffects:Inactive")
    for key in ("ColorEffect", "ContrastEffect", "IntensityEffect")
]

# KDE boolean spellings, lower-cased for comparison.
KDE_BOOLEANS = frozenset({"true", "false", "1", "0", "on", "off"})
BOOLEAN_VALUES = [
    ("ColorEffects:Inactive", "ChangeSelectionColor"),
    ("ColorEffects:Inactive", "Enable"),
    ("General", "shadeSortColumn"),
]


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.parser = load_scheme()

    def test_parses(self):
        self.assertTrue(self.parser.sections())

    def test_cli_id_matches_filename_and_config_value(self):
        """KDE lists a scheme by the filename before its first dot but resolves
        a config value V to `<V>.colors`, so the two must agree or applying the
        scheme breaks on the next start."""
        cli_id = os.path.basename(SCHEME).split(".", 1)[0]
        self.assertEqual(cli_id, self.parser.get("General", "ColorScheme"))
        resolved = os.path.join(os.path.dirname(SCHEME), cli_id + ".colors")
        self.assertTrue(os.path.isfile(resolved), resolved)

    def test_general_name_is_the_product_name(self):
        # System Settings lists the scheme by `General/Name`, but the section
        # and key registry above checks only that the key exists, so a blank
        # or mistyped name ships without another test noticing. Pin it to the
        # product name both package metadata files also carry.
        self.assertEqual(
            self.parser.get("General", "Name"),
            "Mac OS 8.6",
            "General/Name",
        )

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

    def test_section_and_key_registries_cover_the_scheme(self):
        """The registries must name every section and key the scheme defines.

        The presence and format tests above iterate only the registries, so a
        new ``[Colors:*]`` section, a new semantic key, or a new key in an
        ``OTHER_SECTIONS`` section would ship without any check. Derive the
        ``(section, key)`` set from the parsed file and require it to equal the
        registry union, so adding or removing one without updating the
        registries fails here.
        """
        registered = {
            (section, key)
            for section in COLORS_SECTIONS
            for key in COLORS_KEYS
        }
        registered |= {
            (section, key)
            for section, keys in OTHER_SECTIONS.items()
            for key in keys
        }
        found = {
            (section, key)
            for section in self.parser.sections()
            for key in self.parser.options(section)
        }
        self.assertEqual(found, registered)

    def test_colorscheme_value_names_the_scheme_file(self):
        # KDE's scheme resolver turns a `ColorScheme=<value>` config value into
        # `<value>.colors` looked up beside this file (see the BUGS.md entry on
        # the dotted filename), and every installed KDE scheme sets the value to
        # its own filename stem. A rename or edit that breaks the pairing makes
        # the scheme silently fall back to BreezeLight on the next load.
        value = self.parser.get("General", "ColorScheme")
        self.assertEqual(
            os.path.basename(SCHEME),
            f"{value}.colors",
            "General/ColorScheme must name this file (without the .colors suffix)",
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

    def test_coloreffects_selectors_are_nonnegative_integers(self):
        for section, key in EFFECT_SELECTORS:
            value = self.parser.get(section, key)
            try:
                selector = int(value)
            except ValueError:
                self.fail(f"{section}/{key} is not an integer: {value!r}")
            self.assertGreaterEqual(selector, 0, f"{section}/{key} = {value!r}")

    def test_kde_contrast_is_an_integer(self):
        # KDE reads `[KDE] contrast` with readEntry<int>, so a non-integer
        # (e.g. 4.0 or a typo) silently falls back to the default instead of
        # failing, quietly changing the contrast-derived colours.
        value = self.parser.get("KDE", "contrast")
        try:
            int(value)
        except ValueError:
            self.fail(f"KDE/contrast is not an integer: {value!r}")

    def test_boolean_values_use_kde_spellings(self):
        for section, key in BOOLEAN_VALUES:
            value = self.parser.get(section, key)
            self.assertIn(
                value.lower(), KDE_BOOLEANS, f"{section}/{key} = {value!r}"
            )


class TestAnchors(unittest.TestCase):
    """The palette anchors sampled from the retail reference screenshots.

    ``[Colors:Tooltip]`` is the exception: it is a KDE-required semantic role
    whose value comes from the classic Platinum palette, and no Mac OS 8.6
    reference in the set shows a tooltip, so it is not a sampled anchor.
    """

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
        self.assert_value("Colors:Selection", "BackgroundNormal", "204,204,255")

    def test_tooltip_background(self):
        # KDE-required semantic role; classic Platinum pale-yellow, not sampled
        # from a reference screenshot (no tooltip appears in the set).
        self.assert_value("Colors:Tooltip", "BackgroundNormal", "255,255,204")

    def test_window_foreground(self):
        self.assert_value("Colors:Window", "ForegroundNormal", "0,0,0")


class TestProvenanceNote(unittest.TestCase):
    """The scheme header must not present the tooltip as reference-sampled.

    The tooltip anchor has no Mac OS 8.6 image in the reference set, so the
    header names it as the one token that is not reference-derived; this pins
    that exception so a later edit cannot quietly re-overclaim it.
    """

    def test_tooltip_is_named_as_not_reference_sampled(self):
        with open(SCHEME, encoding="utf-8") as handle:
            text = "".join(
                line[1:].strip() + " "
                for line in handle
                if line.startswith("#")
            )
        self.assertIn("[Colors:Tooltip]", text)
        self.assertRegex(
            text,
            r"\[Colors:Tooltip\][\s\S]{0,300}?\b(no|not)\b",
        )


if __name__ == "__main__":
    unittest.main()
