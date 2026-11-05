"""Tests for the org.macos8.desktop KWin decoration QML package.

The `KWin/Decoration` KPackage under theme/kwin-decoration/: the metadata
KPackage discovers, the engine QML component copies (byte-equal where the
engine file references no auroraeTheme, rename-only where it does), the
`AuroraeTheme` singleton that answers the context name KWin withholds from
QML packages, and the install/uninstall lifecycle. Nothing selects the
package: selection is a later plan's work, so no installed file or running
session changes here.

The copy pins compare against the engine files (`/usr/share/kwin/aurorae/`,
upstream KWin 6.3.6) and skip when that directory is absent, like
`tests/test_aurorae_buttons.py` presents its reference-set skips. The
singleton pins re-derive the values upstream's Aurorae::ThemeConfig::load
derives from `org.macos8.desktoprc`, so the singleton cannot drift from the
rc the SVG path also reads.
"""

from __future__ import annotations

import os
import re
import unittest

from support.aurorae_fixtures import AURORAE_DIR, AURORAE_ID
from support.install_lifecycle_cases import InstallLifecycleCases
from support.installed_paths import (
    installed_kwin_decoration,
    installed_kwin_decoration_dir,
)
from support.package_metadata import kplugin, load_metadata
from support.repo_root import ROOT

ENGINE_DIR = "/usr/share/kwin/aurorae"
PACKAGE_ID = AURORAE_ID
PACKAGE_DIR = f"{ROOT}/theme/kwin-decoration/{PACKAGE_ID}"
METADATA = f"{PACKAGE_DIR}/metadata.json"
RC_PATH = f"{AURORAE_DIR}/org.macos8.desktoprc"

# The engine files the package copies byte-equal (no `auroraeTheme` source
# token), and the rename each engine file needs. `aurorae.qml` ships as
# `main.qml`, the component Helper::loadComponent() reads.
BYTE_EQUAL_COPIES = ("Decoration.qml", "DecorationButton.qml", "MenuButton.qml")
RENAMED_COPIES = (
    ("aurorae.qml", "main.qml"),
    ("AuroraeButton.qml", "AuroraeButton.qml"),
    ("AuroraeButtonGroup.qml", "AuroraeButtonGroup.qml"),
    ("AuroraeMaximizeButton.qml", "AuroraeMaximizeButton.qml"),
    ("AppMenuButton.qml", "AppMenuButton.qml"),
)

INSTALLED_FILES = (
    "metadata.json",
    "contents/ui/AuroraeTheme.qml",
    "contents/ui/AppMenuButton.qml",
    "contents/ui/AuroraeButton.qml",
    "contents/ui/AuroraeButtonGroup.qml",
    "contents/ui/AuroraeMaximizeButton.qml",
    "contents/ui/Decoration.qml",
    "contents/ui/DecorationButton.qml",
    "contents/ui/MenuButton.qml",
    "contents/ui/main.qml",
    "contents/ui/qmldir",
)

PROPERTY_RE = re.compile(r"^\s*property (\w+) (\w+): (.*)$")
REFERENCE_RE = re.compile(r"\bauroraeTheme\.(\w+)")


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def singleton_properties(path):
    """Return the singleton file's declared properties, name -> (type, value).

    Each declaration must sit on one `property <type> <name>: <value>` line;
    a wrapped declaration parses wrongly, and every value the test pins must
    stay visible to this parser.
    """
    properties = {}
    for line in read_text(path).splitlines():
        match = PROPERTY_RE.match(line)
        if match:
            name = match.group(2)
            if name in properties:
                raise AssertionError(
                    f"{path}: property {name} declared twice"
                )
            properties[name] = (match.group(1), match.group(3).strip())
    return properties


def parse_rc(path):
    values = {}
    section = None
    for line in read_text(path).splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section and "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            values[f"{section}/{key}"] = value.strip()
    return values


class TestCopies(unittest.TestCase):
    """The package copies as the engine files spell them."""

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_byte_equal_copies_match_the_engine_files(self):
        for name in BYTE_EQUAL_COPIES:
            with open(f"{ENGINE_DIR}/{name}", "rb") as engine_handle:
                engine = engine_handle.read()
            with open(f"{PACKAGE_DIR}/contents/ui/{name}", "rb") as copy_handle:
                copy = copy_handle.read()
            self.assertEqual(copy, engine, name)

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_renamed_copies_replace_only_the_theme_token(self):
        for engine_name, copy_name in RENAMED_COPIES:
            engine = read_text(f"{ENGINE_DIR}/{engine_name}")
            copy = read_text(f"{PACKAGE_DIR}/contents/ui/{copy_name}")
            self.assertEqual(copy, engine.replace("auroraeTheme.", "AuroraeTheme."))
            self.assertNotIn("auroraeTheme", copy, engine_name)
            self.assertEqual(
                engine.count("auroraeTheme."),
                copy.count("AuroraeTheme."),
                engine_name,
            )

class TestSingleton(unittest.TestCase):
    """The singleton property set and the values it spells."""

    def setUp(self):
        self.path = f"{PACKAGE_DIR}/contents/ui/AuroraeTheme.qml"
        self.properties = singleton_properties(self.path)

    def value(self, name):
        return self.properties[name][1]

    def qmltype(self, name):
        return self.properties[name][0]

    def test_property_set_equals_the_references_the_copies_spell(self):
        referenced = set()
        for _, copy_name in RENAMED_COPIES:
            copy_text = read_text(f"{PACKAGE_DIR}/contents/ui/{copy_name}")
            for match in re.finditer(r"\bAuroraeTheme\.(\w+)", copy_text):
                referenced.add(match.group(1))
        self.assertEqual(self.properties.keys(), referenced)

    def test_declared_types_serve_the_references(self):
        expected = {
            "activeTextColor": "color",
            "inactiveTextColor": "color",
            "horizontalAlignment": "int",
            "verticalAlignment": "int",
            "buttonSizeFactor": "real",
        }
        for kind in ("decorationPath", "closeButtonPath"):
            expected[kind] = "string"
        for name, kind in expected.items():
            self.assertEqual(self.qmltype(name), kind, name)

    def test_rc_metrics_match_org_macos8_dot_desktoprc(self):
        rc = parse_rc(RC_PATH)
        # A color property spells a QML colour literal, so the pinned value
        # keeps the literal's quotes.
        expected = {
            "activeTextColor": ("General/ActiveTextColor", '"#000000"'),
            "inactiveTextColor": ("General/InactiveTextColor", '"#777777"'),
            "animationTime": ("General/Animation", "0"),
            "horizontalAlignment": ("General/TitleAlignment", "4"),
            "verticalAlignment": ("General/TitleVerticalAlignment", "128"),
            "buttonWidth": ("Layout/ButtonWidth", "13"),
            "buttonHeight": ("Layout/ButtonHeight", "13"),
            "buttonWidthMaximizeRestore": (
                "Layout/ButtonWidthMaximizeRestore",
                "21",
            ),
            "buttonSpacing": ("Layout/ButtonSpacing", "0"),
            "buttonMarginTop": ("Layout/ButtonMarginTop", "4"),
            "titleHeight": ("Layout/TitleHeight", "22"),
            "titleEdgeTop": ("Layout/TitleEdgeTop", "0"),
            "titleEdgeLeft": ("Layout/TitleEdgeLeft", "4"),
            "titleEdgeRight": ("Layout/TitleEdgeRight", "4"),
        }
        for name, (key, literal) in expected.items():
            self.assertEqual(self.value(name), literal, name)

    def test_derived_top_borders_match_upstreams_borders(self):
        # upstream auroraetheme.cpp borders(): the exposed top border is
        # max(TitleHeight, ButtonHeight * buttonSizeFactor + ButtonMarginTop)
        # + TitleEdgeTop + TitleEdgeBottom, and the maximized twin the same
        # with the Maximised edge pair -- never the rc BorderTop key.
        rc = parse_rc(RC_PATH)
        title_height = int(rc["Layout/TitleHeight"])
        title = round(
            max(
                title_height,
                int(rc["Layout/ButtonHeight"]) * 1.0
                + int(rc["Layout/ButtonMarginTop"]),
            )
        )
        self.assertEqual(
            self.value("borderTop"),
            f"{title + int(rc['Layout/TitleEdgeTop']) + int(rc['Layout/TitleEdgeBottom'])}",
        )
        self.assertEqual(
            self.value("borderTopMaximized"),
            f"{title}",
        )

    def test_side_borders_are_the_clamped_rc_literals(self):
        # upstream borders() clamps the side rc values to
        # KDecoration3::BorderSize::Normal's 4..6 range; 6 clamps to 6, and
        # the maximized DecorationTop sides are 0.
        rc = parse_rc(RC_PATH)
        for name, key in (
            ("borderLeft", "Layout/BorderLeft"),
            ("borderRight", "Layout/BorderRight"),
            ("borderBottom", "Layout/BorderBottom"),
        ):
            self.assertEqual(self.value(name), rc[key], name)
        for name in (
            "borderBottomMaximized",
            "borderLeftMaximized",
            "borderRightMaximized",
        ):
            self.assertEqual(self.value(name), "0", name)

    def test_engine_derived_defaults_match_upstream(self):
        # upstream themeconfig.h's default* functions and
        # auroraetheme.cpp's buttonSizeFactor() when the rc names no key.
        expected = {
            "buttonSizeFactor": "1.0",
            "explicitButtonSpacer": "10",
            "titleBorderLeft": "5",
            "titleBorderRight": "5",
            "titleEdgeTopMaximized": "0",
            "titleEdgeLeftMaximized": "0",
            "titleEdgeRightMaximized": "0",
            "buttonMarginTopMaximized": "0",
            "paddingTop": "0",
            "paddingBottom": "0",
            "paddingLeft": "0",
            "paddingRight": "0",
            "buttonWidthMinimize": "13",
            "buttonWidthClose": "13",
            "buttonWidthAllDesktops": "13",
            "buttonWidthKeepAbove": "13",
            "buttonWidthKeepBelow": "13",
            "buttonWidthShade": "13",
            "buttonWidthHelp": "13",
            "buttonWidthMenu": "13",
            "buttonWidthAppMenu": "13",
        }
        for name, literal in expected.items():
            self.assertEqual(self.value(name), literal, name)

    def test_paths_walk_five_levels_to_the_aurorae_family(self):
        # The walk leads from contents/ui through the package id and the
        # two components of `kwin/decorations` to the data home, then into
        # the aurorae family `make install` places beside the package.
        walk = "../../../../../aurorae/themes/org.macos8.desktop/"
        self.assertEqual(
            self.value("decorationPath"),
            f'asLocalPath("{walk}decoration.svg")',
        )
        for name, svg in (
            ("closeButtonPath", "close.svg"),
            ("maximizeButtonPath", "maximize.svg"),
            ("restoreButtonPath", "restore.svg"),
            ("shadeButtonPath", "shade.svg"),
        ):
            self.assertEqual(
                self.value(name), f'asLocalPath("{walk}{svg}")', name
            )
        # upstream BUTTON_PATH spells an empty string when the aurorae
        # package ships no widget SVG for the widget.
        for name, svg in (
            ("minimizeButtonPath", "minimize.svg"),
            ("allDesktopsButtonPath", "alldesktops.svg"),
            ("keepAboveButtonPath", "keepabove.svg"),
            ("keepBelowButtonPath", "keepbelow.svg"),
            ("helpButtonPath", "help.svg"),
            ("appMenuButtonPath", "appmenu.svg"),
        ):
            self.assertEqual(self.value(name), '""', name)
            self.assertFalse(
                os.path.exists(f"{AURORAE_DIR}/{svg}"),
                f"{name} spells empty but {svg} exists in the aurorae "
                "package",
            )

    def test_qmldir_declares_the_singleton(self):
        lines = [
            line.strip()
            for line in read_text(f"{PACKAGE_DIR}/contents/ui/qmldir").splitlines()
            if line.strip()
        ]
        self.assertEqual(
            lines, ["singleton AuroraeTheme 1.0 AuroraeTheme.qml"]
        )


class TestMetadata(unittest.TestCase):
    def test_metadata_identifies_the_decoration_package(self):
        metadata = load_metadata(METADATA)
        self.assertEqual(metadata["KPackageStructure"], "KWin/Decoration")
        plugin = kplugin(metadata, METADATA)
        self.assertEqual(plugin["Id"], PACKAGE_ID)
        self.assertEqual(plugin["Name"], "Platinum")
        self.assertEqual(plugin["License"], "GPL-2.0-or-later")
        self.assertIsNone(
            re.search("apple|mac\\s*os", plugin["Description"], re.IGNORECASE),
            plugin["Description"],
        )


class TestInstall(InstallLifecycleCases, unittest.TestCase):
    MAKE_PACKAGES = "kwin-decoration"
    PACKAGE_ID = PACKAGE_ID
    PACKAGE_DIR = PACKAGE_DIR
    INSTALLED_FILES = INSTALLED_FILES

    def installed_parent(self, tmp):
        return installed_kwin_decoration_dir(tmp)

    def installed_package_dir(self, tmp):
        return installed_kwin_decoration(tmp, self.PACKAGE_ID)


if __name__ == "__main__":
    unittest.main()
