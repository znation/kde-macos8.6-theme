"""Validate the Mac OS 8.6 Platinum color scheme and its install path."""

import configparser
import math
import os
import re
import shutil
import subprocess
import tempfile
import unittest

from theme_install import ROOT, install, uninstall

SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

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
# tests below; the effect selectors have their own integer test, and the [KDE]
# scalar is checked only for presence by test_other_sections_and_keys.
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

    def test_cli_id_matches_filename_and_config_value(self):
        """KDE lists a scheme by the filename before its first dot but resolves
        a config value V to `<V>.colors`, so the two must agree or applying the
        scheme breaks on the next start."""
        cli_id = os.path.basename(SCHEME).split(".", 1)[0]
        self.assertEqual(cli_id, self.parser.get("General", "ColorScheme"))
        resolved = os.path.join(os.path.dirname(SCHEME), cli_id + ".colors")
        self.assertTrue(os.path.isfile(resolved), resolved)

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
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = os.path.join(
                tmp, "share", "color-schemes", "MacOS8.colors"
            )
            self.assertTrue(os.path.isfile(installed), installed)
            with open(SCHEME, "rb") as source, open(installed, "rb") as target:
                self.assertEqual(source.read(), target.read())

    def test_make_install_names_the_scheme_after_its_source_basename(self):
        # KDE derives the scheme id from the installed filename, so install must
        # follow the source basename: a hardcoded destination name would install
        # a renamed scheme under the old id and break its restart resolution.
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "Platinum.colors")
            shutil.copy(SCHEME, source)
            result = subprocess.run(
                [
                    "make", "install", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share",
                    f"COLOR_SCHEME={source}",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = os.path.join(
                tmp, "share", "color-schemes", "Platinum.colors"
            )
            self.assertTrue(os.path.isfile(installed), installed)
            with open(source, "rb") as original, open(installed, "rb") as copy:
                self.assertEqual(original.read(), copy.read())
            self.assertFalse(
                os.path.exists(
                    os.path.join(tmp, "share", "color-schemes", "MacOS8.colors")
                ),
                "the old hardcoded name should not be installed",
            )

    def test_make_uninstall_removes_the_scheme_under_its_source_basename(self):
        # `uninstall` must remove the same basename `install` wrote: a hardcoded
        # name would leave a renamed scheme behind and delete the wrong file.
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "Platinum.colors")
            shutil.copy(SCHEME, source)
            installed = subprocess.run(
                [
                    "make", "install", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share",
                    f"COLOR_SCHEME={source}",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            schemes = os.path.join(tmp, "share", "color-schemes")
            renamed = os.path.join(schemes, "Platinum.colors")
            self.assertTrue(os.path.isfile(renamed), renamed)
            decoy = os.path.join(schemes, "MacOS8.colors")
            with open(decoy, "w", encoding="utf-8") as handle:
                handle.write("[General]\nName=Decoy\n")

            removed = subprocess.run(
                [
                    "make", "uninstall", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share",
                    f"COLOR_SCHEME={source}",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(
                os.path.exists(renamed),
                "the renamed scheme should have been uninstalled",
            )
            self.assertTrue(
                os.path.isfile(decoy),
                "uninstall must not remove a file it did not install",
            )

    def test_make_uninstall_removes_only_the_scheme_it_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            schemes = os.path.join(tmp, "share", "color-schemes")
            other = os.path.join(schemes, "Other.colors")
            with open(other, "w", encoding="utf-8") as handle:
                handle.write("[General]\nName=Other\n")

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(
                os.path.exists(os.path.join(schemes, "MacOS8.colors")),
                "the installed scheme should be gone",
            )
            self.assertTrue(os.path.isfile(other), other)

            again = uninstall(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


@unittest.skipUnless(
    shutil.which("plasma-apply-colorscheme"), "needs plasma-apply-colorscheme"
)
class TestRestartRoundTrip(unittest.TestCase):
    """Applying the listed id must leave a config KDE resolves on restart.

    `plasma-apply-colorscheme <id>` writes `[General] ColorScheme=<id>`; the next
    start resolves that value to `<id>.colors`. A dotted filename makes the
    listed id differ from the resolvable value, so the scheme falls back to
    BreezeLight after a restart.
    """

    def test_applied_id_survives_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = os.path.join(tmp, "data")
            config = os.path.join(tmp, "config")
            schemes = os.path.join(data, "color-schemes")
            os.makedirs(schemes)
            os.makedirs(config)
            shutil.copy(SCHEME, os.path.join(schemes, os.path.basename(SCHEME)))
            kdeglobals = os.path.join(config, "kdeglobals")
            with open(kdeglobals, "w", encoding="utf-8") as handle:
                handle.write("[General]\nColorScheme=BreezeLight\n")
            env = dict(
                os.environ,
                XDG_DATA_HOME=data,
                XDG_CONFIG_HOME=config,
                XDG_DATA_DIRS=data + os.pathsep + "/usr/share",
            )
            cli_id = os.path.basename(SCHEME).split(".", 1)[0]
            applied = subprocess.run(
                ["plasma-apply-colorscheme", cli_id],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            with open(kdeglobals, encoding="utf-8") as handle:
                written = handle.read()
            self.assertIn(f"ColorScheme={cli_id}", written)
            restarted = subprocess.run(
                ["plasma-apply-colorscheme"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertNotIn(
                "Could not find",
                restarted.stdout + restarted.stderr,
                "applied scheme id did not resolve on restart",
            )


if __name__ == "__main__":
    unittest.main()
