"""Validate the org.macos8.desktop Plasma desktop theme package.

Widget artwork is pinned in the per-widget test modules; this module covers the
package itself: metadata, the shared root canvas, defaults wiring, and install.
"""

from __future__ import annotations

import os
import shutil
import unittest
import xml.etree.ElementTree as ET

from support.desktoptheme_paths import (
    ACTIONBUTTON_SVG,
    ACTION_OVERLAYS_SVG,
    ARROWS_SVG,
    BACKGROUND_SVG,
    BAR_METER_HORIZONTAL_SVG,
    BUSYWIDGET_SVG,
    BUTTON_SVG,
    CHECKMARKS_SVG,
    DIALOG_BACKGROUND_SVG,
    DTHEME_ID,
    FRAME_SVG,
    LINE_SVG,
    LINEEDIT_SVG,
    LISTITEM_SVG,
    LNF_DEFAULTS,
    MENUBARITEM_SVG,
    METADATA,
    PACKAGE,
    PANEL_SVG,
    PLASMOIDHEADING_SVG,
    RADIOBUTTON_SVG,
    SCROLLBAR_SVG,
    SLIDER_SVG,
    SOLID_PANEL_SVG,
    SOLID_TOOLTIP_SVG,
    SWITCH_SVG,
    TABBAR_SVG,
    TOOLBAR_SVG,
    TOOLTIP_SVG,
    VIEWITEM_SVG,
)
from support.install_failure_cases import FailedInstallPreservesPackage
from support.install_lifecycle_cases import InstallLifecycleCases
from support.kde_config import read as read_kde_config
from support.kpackage_install_case import KPackageInstallCase
from support.package_metadata import PackageMetadata, kplugin, load_metadata
from support.process_assertions import assert_succeeded
from support.shipped_files import shipped_files
from support.theme_install import installed_destdir, run_captured
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    assert_unique_ids,
)


# configparser reads the KDE `[plasmarc][Theme]` header greedily, so the
# section key includes the inner bracket pair.
PLASMA_SECTION = "plasmarc][Theme"


# Each shipped SVG's root canvas. Seven widgets (the frame, button,
# line edit, list item, view item, tab bar and plasmoid heading) share a tight
# 12x12 canvas; the menu bar is 12x22 (its `north-` state is 18px tall in the
# centre); the menu-bar item is 20x12 (7px side borders); the scrollbar,
# slider, toolbar, arrows, menu body, tooltip (and its solid/ copy) and dialog
# window body are 16x16; checkmarks is two stacked 16x16 cells and radiobutton
# three side-by-side, so their canvases are 16x32 and 48x16; the progress bar
# is a 10x10 canvas and the etched separator a 4x2 canvas. The switch is a
# 30x18 canvas grown from a 16x16 track to hold its 12x18 thumb, the busy
# indicator a 36x36 square for its 32px ring, and the round action button a
# 36x36 square for its 34px outline. The desktop icon action overlays are a
# 16x16 canvas holding nine 14px action buttons.
SVG_CANVASES = (
    ("panel-background.svg", PANEL_SVG, 12, 22),
    ("solid/widgets/panel-background.svg", SOLID_PANEL_SVG, 12, 22),
    ("frame.svg", FRAME_SVG, 12, 12),
    ("button.svg", BUTTON_SVG, 12, 12),
    ("lineedit.svg", LINEEDIT_SVG, 12, 12),
    ("listitem.svg", LISTITEM_SVG, 12, 12),
    ("viewitem.svg", VIEWITEM_SVG, 12, 12),
    ("menubaritem.svg", MENUBARITEM_SVG, 20, 12),
    ("scrollbar.svg", SCROLLBAR_SVG, 16, 16),
    ("slider.svg", SLIDER_SVG, 16, 16),
    ("switch.svg", SWITCH_SVG, 30, 18),
    ("busywidget.svg", BUSYWIDGET_SVG, 36, 36),
    ("actionbutton.svg", ACTIONBUTTON_SVG, 36, 36),
    ("action-overlays.svg", ACTION_OVERLAYS_SVG, 16, 16),
    ("bar_meter_horizontal.svg", BAR_METER_HORIZONTAL_SVG, 10, 10),
    ("background.svg", BACKGROUND_SVG, 16, 16),
    ("checkmarks.svg", CHECKMARKS_SVG, 16, 32),
    ("radiobutton.svg", RADIOBUTTON_SVG, 48, 16),
    ("tabbar.svg", TABBAR_SVG, 12, 12),
    ("toolbar.svg", TOOLBAR_SVG, 16, 16),
    ("arrows.svg", ARROWS_SVG, 16, 16),
    ("line.svg", LINE_SVG, 4, 2),
    ("plasmoidheading.svg", PLASMOIDHEADING_SVG, 12, 12),
    ("tooltip.svg", TOOLTIP_SVG, 16, 16),
    ("solid/widgets/tooltip.svg", SOLID_TOOLTIP_SVG, 16, 16),
    ("dialogs/background.svg", DIALOG_BACKGROUND_SVG, 16, 16),
)


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/Theme"
    PACKAGE_ID = DTHEME_ID
    PLASMA_API_KEY = "X-Plasma-API"
    PLASMA_API_VERSION = "5.0"


# The menu bar's unprefixed state sits at the origin of the 12x22 canvas grown
# for its taller `north-` state, so its margin rects stop above the bottom.
# The switch's inactive/active tracks likewise sit at the origin of the 30x18
# canvas grown to hold the 18px thumb, so their margin rects stop short of the
# 30px width (and of the bottom).
ORIGIN_STATES = {
    "panel-background.svg": ("",),
    "solid/widgets/panel-background.svg": ("",),
    "switch.svg": ("inactive", "active"),
}


class TestSvgRootCanvas(unittest.TestCase):
    def test_root_canvas_matches_the_artwork_layout(self):
        # A root viewBox/width/height change rescales the whole widget while
        # every per-element test keeps passing, so pin the canvas for every
        # widget and tie it to the margin hints where there are any.
        for name, path, width, height in SVG_CANVASES:
            with self.subTest(svg=name):
                assert_root_canvas(
                    self,
                    ET.parse(path),
                    width,
                    height,
                    ORIGIN_STATES.get(name, ()),
                )

    def test_every_svg_declares_unique_ids(self):
        # `elements_by_id` and `rect_geometry` key their maps by id, and
        # `attribute_values` reads ids as a set, so a duplicate id would
        # silently resolve to one element in any id-keyed test map; KSvg
        # resolves it to one element too. Pin uniqueness for every registered
        # SVG, not only the widgets whose tests happen to read by id.
        for name, path, _, _ in SVG_CANVASES:
            with self.subTest(svg=name):
                assert_unique_ids(self, ET.parse(path))

    def test_every_svg_is_self_contained(self):
        # The per-widget pixel tests composite only the rects and groups
        # `render_slices` models, so a `<style>` element or a reference to
        # another file would be skipped silently and the widget could pass
        # while rendering wrong (or blank), and a `<script>` element is
        # executed by KSvg rather than drawn. Pin all three structural
        # properties for every registered SVG, not only the widgets whose
        # tests happen to reach them.
        for name, path, _, _ in SVG_CANVASES:
            with self.subTest(svg=name):
                tree = ET.parse(path)
                assert_no_style_elements(self, tree)
                assert_no_external_references(self, tree)
                assert_no_script_elements(self, tree)

    def test_registry_covers_every_shipped_svg(self):
        # The canvas pin above only visits the SVGs listed in SVG_CANVASES, so
        # a newly shipped SVG that is never added to the registry silently
        # escapes the check and its canvas is unpinned. Derive the shipped set
        # from the package on disk and require it to equal the registry, so
        # adding or removing an SVG without updating SVG_CANVASES fails here.
        registered = {
            os.path.relpath(path, PACKAGE) for _, path, _, _ in SVG_CANVASES
        }
        shipped = shipped_files(PACKAGE, suffix=".svg")
        self.assertEqual(shipped, registered)


class TestDefaultsWiring(unittest.TestCase):
    def test_defaults_select_the_desktop_theme(self):
        parser = read_kde_config(LNF_DEFAULTS)
        self.assertEqual(
            parser.get(PLASMA_SECTION, "name"),
            kplugin(load_metadata(METADATA), METADATA)["Id"],
        )


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "desktoptheme"
    PACKAGE_ID = DTHEME_ID
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = (
        "metadata.json",
        os.path.join("widgets", "panel-background.svg"),
        os.path.join("widgets", "frame.svg"),
        os.path.join("widgets", "button.svg"),
        os.path.join("widgets", "radiobutton.svg"),
        os.path.join("widgets", "checkmarks.svg"),
        os.path.join("widgets", "lineedit.svg"),
        os.path.join("widgets", "listitem.svg"),
        os.path.join("widgets", "viewitem.svg"),
        os.path.join("widgets", "menubaritem.svg"),
        os.path.join("widgets", "tabbar.svg"),
        os.path.join("widgets", "toolbar.svg"),
        os.path.join("widgets", "arrows.svg"),
        os.path.join("widgets", "line.svg"),
        os.path.join("widgets", "plasmoidheading.svg"),
        os.path.join("widgets", "scrollbar.svg"),
        os.path.join("widgets", "slider.svg"),
        os.path.join("widgets", "switch.svg"),
        os.path.join("widgets", "busywidget.svg"),
        os.path.join("widgets", "actionbutton.svg"),
        os.path.join("widgets", "action-overlays.svg"),
        os.path.join("widgets", "bar_meter_horizontal.svg"),
        os.path.join("widgets", "background.svg"),
        os.path.join("widgets", "tooltip.svg"),
        os.path.join("solid", "widgets", "tooltip.svg"),
        os.path.join("solid", "widgets", "panel-background.svg"),
        os.path.join("dialogs", "background.svg"),
    )
    COPY_FAILURE_GLOB = "*/desktop-themes/*"


@unittest.skipUnless(
    shutil.which("plasma-apply-desktoptheme"),
    "needs plasma-apply-desktoptheme",
)
class TestApplyDesktopTheme(unittest.TestCase):
    def test_apply_lists_and_selects_the_theme(self):
        with installed_destdir(self) as tmp:
            env = dict(
                os.environ,
                XDG_DATA_HOME=os.path.join(tmp, "share"),
                XDG_CONFIG_HOME=os.path.join(tmp, "config"),
            )
            listed = run_captured(
                ["plasma-apply-desktoptheme", "--list-themes"],
                env=env,
            )
            assert_succeeded(self, listed)
            self.assertIn(DTHEME_ID, listed.stdout)
            applied = run_captured(
                ["plasma-apply-desktoptheme", DTHEME_ID],
                env=env,
            )
            assert_succeeded(self, applied)
            parser = read_kde_config(os.path.join(tmp, "config", "plasmarc"))
            self.assertEqual(parser.get("Theme", "name"), DTHEME_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Plasma/Theme"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = DTHEME_ID


if __name__ == "__main__":
    unittest.main()
