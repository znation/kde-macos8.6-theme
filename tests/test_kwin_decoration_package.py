"""Tests for the org.macos8.desktop KWin decoration QML package.

The `KWin/Decoration` KPackage under theme/kwin-decoration/: the metadata
KPackage discovers, the engine QML component copies (byte-equal where the
engine file references no auroraeTheme, rename-only where it does, gated on
window activity where it draws a button hit cell, all part 3/3), the
`AuroraeTheme` singleton that answers the context name KWin withholds from
QML packages, and the install/uninstall lifecycle. The shipped look-and-feel
defaults select the package: `[kwinrc][org.kde.kdecoration2]` publishes
`library=org.kde.kwin.aurorae` beside `theme=org.macos8.desktop`, the
`KPlugin.Id` KWin matches under `kwin/decorations/` (the selection pins live
in `tests/test_theme_defaults.py`, the default-value render publishes it and
README documents the headless A/B equality evidence).

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
# `main.qml`, the component Helper::loadComponent() reads. Part 3/3 and the
# 2026-11-05 shadow fix moved the gated copies out of these tuples into the
# expectations that follow: equal-plus-gate, not plain equal.
BYTE_EQUAL_COPIES = ("Decoration.qml",)
RENAMED_COPIES = (
    ("aurorae.qml", "main.qml"),
    ("AuroraeButtonGroup.qml", "AuroraeButtonGroup.qml"),
    ("AuroraeMaximizeButton.qml", "AuroraeMaximizeButton.qml"),
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

# The part 3/3 hit-area gating (2026-11-04): the package copy equals its engine
# file with only the additions below, so an un-gated copy or an engine byte
# touched anywhere else fails. The comments are the dated plan-notes the
# copies carry; each expected text re-derives from the engine file on disk.
DECORATION_BUTTON_COMMENT = """\
    // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
    // part 3/3": Platinum is active=frontmost (the 2026-11-04 direction), so an
    // unfocused window's bar is the flat buttonless strip its empty
    // inactive-centre art draws while this button's hit cell stayed live and a
    // click meant only to refocus could close or maximize the window. This
    // KWin/Decoration package copy -- run instead of the engine file only through
    // the loadComponent() KPackage route, the Option A plan part 1/3 chose over
    // Option B's data-home shadow of the shared engine component -- gates the
    // interactive hit area on window activity. Geometry and art are untouched:
    // active windows draw and press as before, and on an unfocused window the
    // disabled Item drops its MouseArea so the click falls through to the title
    // bar's activate.
"""
MENU_BUTTON_COMMENT = """\
        // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- on an
        // unfocused window's flat buttonless bar a long-press here eats the
        // refocusing click and, with closeOnDoubleClick, a second click could
        // even close the window; the active=frontmost direction (2026-11-04) and
        // the package KPackage route (part 1/3's Option A, not Option B's
        // data-home engine shadow) are recorded in this file's package copy.
"""
MAXIMIZE_BUTTON_COMMENT = """\
        // 2026-11-04, feature role, PLANS-DONE.md "Platinum KWin Decoration package,
        // part 3/3": gate the standalone hit area on window activity -- the
        // maximize/restore cell on an unfocused window's flat buttonless bar
        // maximized windows meant only to be refocused; the active=frontmost
        // direction (2026-11-04) and the package KPackage route (part 1/3's
        // Option A, not Option B's data-home engine shadow) are recorded in this
        // package's copy of the engine file (AuroraeTheme singleton spelling).
"""
DECORATION_BUTTON_COMMENT_HEAD = "    id: button\n"
ENABLED_BLOCK_HEAD = "    enabled: {\n"
MOUSEAREA_HEAD = "    MouseArea {\n        anchors.fill: parent\n"
INACTIVE_GUARD = """\
        if (!decoration.client.active) {
            return false;
        }
"""
INACTIVE_MOUSEAREA_GATE = "        enabled: decoration.client.active\n"

# The 2026-11-05 shadowing fix: the imported module's DecorationButton wins
# over the package's same-named base file, so the effective gate moved onto
# the AuroraeButton subclass item and the AppMenuButton fallback.
AURORAE_BUTTON_GATE = """\
    // 2026-11-05: the imported `org.kde.kwin.decoration` module also provides
    // a `DecorationButton`, and the explicit import wins over this package's
    // same-named local file -- so the base copy's `enabled` gate never ran and
    // an unfocused window's close, maximize and shade cells stayed live.
    // Gate this subclass item itself, reproducing the base's capability
    // switch; a disabled item drops its inherited MouseArea, so the click
    // falls through to the title bar's activation.
    enabled: {
        if (!decoration.client.active) {
            return false;
        }
        switch (buttonType) {
        case DecorationOptions.DecorationButtonClose:
            return decoration.client.closeable;
        case DecorationOptions.DecorationButtonMaximizeRestore:
            return decoration.client.maximizeable;
        case DecorationOptions.DecorationButtonMinimize:
            return decoration.client.minimizeable;
        case DecorationOptions.DecorationButtonExplicitSpacer:
            return false;
        default:
            return true;
        }
    }
"""
APP_MENU_VISIBLE_HEAD = "        visible: !AuroraeTheme.appMenuButtonPath\n"
APP_MENU_FALLBACK_GATE = """\
        // 2026-11-05: the imported module's DecorationButton shadows the
        // package copy, so gate the fallback's hit area here too.
        enabled: decoration.client.active
"""


def expected_gated_aurorae_button(engine):
    """The package AuroraeButton.qml copy: rename, then the subclass gate.

    2026-11-05: the imported org.kde.kwin.decoration module exports its own
    DecorationButton, so the package base copy is shadowed and the effective
    hit-area gate lives on this subclass item.
    """
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count("DecorationButton {\n") == 1, ENGINE_DIR
    return renamed.replace(
        "DecorationButton {\n",
        "DecorationButton {\n" + AURORAE_BUTTON_GATE,
        1,
    )


def expected_gated_app_menu_button(engine):
    """The package AppMenuButton.qml copy: rename and the fallback gate."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(APP_MENU_VISIBLE_HEAD) == 1, ENGINE_DIR
    return renamed.replace(
        APP_MENU_VISIBLE_HEAD,
        APP_MENU_VISIBLE_HEAD + APP_MENU_FALLBACK_GATE,
        1,
    )


def expected_gated_decoration_button(engine):
    """The package DecorationButton.qml copy: comment, then the guarded switch."""
    assert engine.count(DECORATION_BUTTON_COMMENT_HEAD) == 1, ENGINE_DIR
    copy = engine.replace(
        DECORATION_BUTTON_COMMENT_HEAD,
        DECORATION_BUTTON_COMMENT_HEAD + DECORATION_BUTTON_COMMENT,
    )
    assert copy.count(ENABLED_BLOCK_HEAD) == 1, ENGINE_DIR
    return copy.replace(ENABLED_BLOCK_HEAD, ENABLED_BLOCK_HEAD + INACTIVE_GUARD)


def expected_gated_menu_button(engine):
    """The package MenuButton.qml copy: the enabled MouseArea, comment first."""
    assert engine.count(MOUSEAREA_HEAD) == 1, ENGINE_DIR
    return engine.replace(
        MOUSEAREA_HEAD,
        MOUSEAREA_HEAD + MENU_BUTTON_COMMENT + INACTIVE_MOUSEAREA_GATE,
    )


def expected_gated_aurorae_maximize_button(engine):
    """The package AuroraeMaximizeButton.qml copy: rename, comment, gate."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(MOUSEAREA_HEAD) == 1, ENGINE_DIR
    return renamed.replace(
        MOUSEAREA_HEAD,
        MOUSEAREA_HEAD + MAXIMIZE_BUTTON_COMMENT + INACTIVE_MOUSEAREA_GATE,
    )


# The 2026-11-12 caption gap: the package main.qml copy adds a solid band
# behind the caption, the way Mac OS 8.6 clears the title-bar pinstripes
# behind the title text (reference apps_macrumors8.6.jpg, columns sampled
# 2026-11-12). The engine caption Text is untouched; the band sits before it
# so the Text paints on top.
CAPTION_HEAD = "    Text {\n        id: caption\n"
CAPTION_GAP_BLOCK = """\
    // 2026-11-12, caption gap: Mac OS 8.6 clears the title-bar pinstripes
    // behind the caption -- the reference screenshots draw a solid #CCCCCC
    // band the width of the painted caption plus about 4px each side,
    // spanning the stripe rows while the frame's top highlight and bottom
    // rule stay (apps_macrumors8.6.jpg "About This Computer", pixel columns
    // sampled 2026-11-12) -- so the title reads over the stripes. The band
    // shows only on an active window: the inactive art is stripe-free.
    Rectangle {
        id: captionGap
        color: "#cccccc"
        visible: decoration.client.active
        // The band is the painted caption plus 4px each side, never wider
        // than the space between the button groups.
        property real bandWidth: Math.min(caption.width, caption.contentWidth + 8)
        x: {
            if (caption.horizontalAlignment === Text.AlignRight) {
                return caption.x + caption.width - bandWidth;
            }
            if (caption.horizontalAlignment === Text.AlignHCenter) {
                return caption.x + (caption.width - bandWidth) / 2;
            }
            return caption.x;
        }
        y: caption.y + 2
        width: bandWidth
        height: caption.height - 4
    }
"""


def expected_gated_main(engine):
    """The package main.qml copy: rename, then the caption gap band."""
    renamed = engine.replace("auroraeTheme.", "AuroraeTheme.")
    assert renamed.count(CAPTION_HEAD) == 1, ENGINE_DIR
    return renamed.replace(CAPTION_HEAD, CAPTION_GAP_BLOCK + CAPTION_HEAD, 1)


# Renamed copies that carry a gated addition on top of the theme-token
# rename; the plain rename-only expectation does not apply to them.
RENAMED_GATED_COPIES = {
    "AuroraeMaximizeButton.qml": expected_gated_aurorae_maximize_button,
    "main.qml": expected_gated_main,
}


GATED_COPIES = (
    ("DecorationButton.qml", expected_gated_decoration_button),
    ("MenuButton.qml", expected_gated_menu_button),
    ("AuroraeMaximizeButton.qml", expected_gated_aurorae_maximize_button),
    ("AuroraeButton.qml", expected_gated_aurorae_button),
    ("AppMenuButton.qml", expected_gated_app_menu_button),
)


def read_text(path):
    """Return the UTF-8 text at *path*."""
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
    """Return a ``section/key`` mapping parsed from the ini file at *path*."""
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
            expected = engine.replace("auroraeTheme.", "AuroraeTheme.")
            if copy_name in RENAMED_GATED_COPIES:
                expectation = RENAMED_GATED_COPIES[copy_name]
                with self.subTest(name=copy_name):
                    self.assertEqual(copy, expectation(engine))
                continue
            self.assertEqual(copy, expected)
            self.assertNotIn("auroraeTheme", copy, engine_name)
            self.assertEqual(
                engine.count("auroraeTheme."),
                copy.count("AuroraeTheme."),
                engine_name,
            )

    @unittest.skipUnless(
        os.path.isdir(ENGINE_DIR), "needs /usr/share/kwin/aurorae/"
    )
    def test_gated_copies_match_the_engine_files_with_their_gate(self):
        # Part 3/3 (2026-11-04): a hit-surface copy equals its engine file plus
        # exactly the dated comment and the window-activity gate, so a dropped
        # gate or an engine byte changed anywhere else fails rather than
        # silently changing what a pressed invisible button does.
        for name, expectation in GATED_COPIES:
            engine = read_text(f"{ENGINE_DIR}/{name}")
            copy = read_text(f"{PACKAGE_DIR}/contents/ui/{name}")
            with self.subTest(name=name):
                self.assertEqual(copy, expectation(engine))

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
        copy_names = [copy for _, copy in RENAMED_COPIES] + [
            name for name, _ in GATED_COPIES
        ]
        for copy_name in copy_names:
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
        # Engine defaults from upstream KWin, except the maximized button
        # margin: the zoomed reference places title boxes 4px below the edge.
        expected = {
            "buttonSizeFactor": "1.0",
            "explicitButtonSpacer": "10",
            "titleBorderLeft": "5",
            "titleBorderRight": "5",
            "titleEdgeTopMaximized": "0",
            "titleEdgeLeftMaximized": "0",
            "titleEdgeRightMaximized": "0",
            "buttonMarginTopMaximized": "4",
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

    def test_singleton_loads_in_the_package_import_context(self):
        """The 2026-11-04 selection-route session probe, pinned statically.

        A KWin/Decoration QML package loads the singleton through the package
        qmldir's implicit import, which provides no types: without
        `pragma Singleton` the qmldir singleton declaration refuses the file
        (qml: qmldir defines type as singleton, but no pragma Singleton), and
        without an explicit import `QtObject` and the `color` valuetype stay
        unresolvable (qml: QtObject is not a type / color is not a type).
        The engine copies get both through their own QtQuick import, which is
        why only the singleton needs the spelling below.
        """
        text = read_text(self.path)
        pragma = text.find("pragma Singleton")
        imp = text.find("import QtQuick")
        self.assertNotEqual(pragma, -1, "the singleton needs pragma Singleton")
        self.assertGreater(
            imp, pragma, "pragma Singleton must come before the import"
        )
        self.assertGreater(
            pragma, text.find("*/"), "pragma must follow the header comment"
        )
        imports = re.findall(r"^import .*$", text, re.MULTILINE)
        self.assertEqual(imports, ["import QtQuick"], imports)

    def test_as_local_path_stringifies_resolved_url(self):
        # Qt.resolvedUrl answers a QUrl in this engine (TypeError: Property
        # 'slice' ... is not a function, 2026-11-04 session probe), so the
        # prefix walk below needs a string.
        text = read_text(self.path)
        self.assertIn(
            "Qt.resolvedUrl(name).toString()", text,
            "asLocalPath must stringify Qt.resolvedUrl before its prefix walk",
        )
        self.assertNotIn("Qt.resolvedUrl(name);", text)


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
