"""Validate the org.macos8.desktop Plasma desktop theme package.

Widget artwork is pinned in the per-widget test modules; this module covers the
package itself: metadata, the shared root canvas, defaults wiring, and install.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import (
    BACKGROUND_SVG,
    BUTTON_SVG,
    CHECKMARKS_SVG,
    DIALOG_BACKGROUND_SVG,
    DTHEME_ID,
    FRAME_SVG,
    LINEEDIT_SVG,
    LISTITEM_SVG,
    LNF_DEFAULTS,
    METADATA,
    PACKAGE,
    PANEL_SVG,
    RADIOBUTTON_SVG,
    SCROLLBAR_SVG,
)
from install_failure_cases import FailedInstallPreservesPackage
from install_lifecycle_cases import InstallLifecycleCases
from kpackage_install_case import KPackageInstallCase
from kde_config import read as read_kde_config
from package_metadata import PackageMetadata, kplugin, load_metadata
from svg_assertions import assert_root_canvas, assert_unique_ids
from theme_install import install, run, shadow_command_env


# configparser reads the KDE `[plasmarc][Theme]` header greedily, so the
# section key includes the inner bracket pair.
PLASMA_SECTION = "plasmarc][Theme"


# Each shipped SVG's root canvas. Five nine-slice widgets share a tight 12x12
# canvas; the scrollbar, the menu body and the dialog window body are 16x16;
# checkmarks is two stacked 16x16 cells and radiobutton two side-by-side, so
# their canvases are 16x32 and 48x16.
SVG_CANVASES = (
    ("panel-background.svg", PANEL_SVG, 12, 12),
    ("frame.svg", FRAME_SVG, 12, 12),
    ("button.svg", BUTTON_SVG, 12, 12),
    ("lineedit.svg", LINEEDIT_SVG, 12, 12),
    ("listitem.svg", LISTITEM_SVG, 12, 12),
    ("scrollbar.svg", SCROLLBAR_SVG, 16, 16),
    ("background.svg", BACKGROUND_SVG, 16, 16),
    ("checkmarks.svg", CHECKMARKS_SVG, 16, 32),
    ("radiobutton.svg", RADIOBUTTON_SVG, 48, 16),
    ("dialogs/background.svg", DIALOG_BACKGROUND_SVG, 16, 16),
)


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/Theme"
    PACKAGE_ID = DTHEME_ID
    PLASMA_API_KEY = "X-Plasma-API"
    PLASMA_API_VERSION = "5.0"


class TestSvgRootCanvas(unittest.TestCase):
    def test_root_canvas_matches_the_artwork_layout(self):
        # A root viewBox/width/height change rescales the whole widget while
        # every per-element test keeps passing, so pin the canvas for every
        # widget and tie it to the margin hints where there are any.
        for name, path, width, height in SVG_CANVASES:
            with self.subTest(svg=name):
                assert_root_canvas(self, ET.parse(path), width, height)

    def test_every_svg_declares_unique_ids(self):
        # `elements_by_id` and `rect_geometry` key their maps by id, and
        # `attribute_values` reads ids as a set, so a duplicate id would
        # silently resolve to one element in any id-keyed test map; KSvg
        # resolves it to one element too. Pin uniqueness for every registered
        # SVG, not only the widgets whose tests happen to read by id.
        for name, path, _, _ in SVG_CANVASES:
            with self.subTest(svg=name):
                assert_unique_ids(self, ET.parse(path))

    def test_registry_covers_every_shipped_svg(self):
        # The canvas pin above only visits the SVGs listed in SVG_CANVASES, so
        # a newly shipped SVG that is never added to the registry silently
        # escapes the check and its canvas is unpinned. Derive the shipped set
        # from the package on disk and require it to equal the registry, so
        # adding or removing an SVG without updating SVG_CANVASES fails here.
        registered = {path for _, path, _, _ in SVG_CANVASES}
        shipped = set()
        for dirpath, _, filenames in os.walk(PACKAGE):
            for filename in filenames:
                if filename.endswith(".svg"):
                    shipped.add(os.path.join(dirpath, filename))
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
        os.path.join("widgets", "scrollbar.svg"),
        os.path.join("widgets", "background.svg"),
        os.path.join("dialogs", "background.svg"),
    )

    def reinstall_failure_env(self, tmp):
        # Shadow `cp` with a fake that fails only when copying the desktop
        # theme (the look-and-feel copy must still succeed), writing part of
        # the tree then dying like a killed or out-of-space `cp` would.
        real_cp = shutil.which("cp")
        return shadow_command_env(
            tmp,
            "cp",
            "#!/bin/sh\n"
            'case "$2" in\n'
            "  */desktop-themes/*)\n"
            '    dest="$3/$(basename "$2")"\n'
            '    mkdir -p "$dest"\n'
            '    printf partial > "$dest/metadata.json"\n'
            "    exit 1;;\n"
            "esac\n"
            f'exec "{real_cp}" "$@"\n',
        )


@unittest.skipUnless(
    shutil.which("plasma-apply-desktoptheme"),
    "needs plasma-apply-desktoptheme",
)
class TestApplyDesktopTheme(unittest.TestCase):
    def test_apply_lists_and_selects_the_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            env = dict(
                os.environ,
                XDG_DATA_HOME=os.path.join(tmp, "share"),
                XDG_CONFIG_HOME=os.path.join(tmp, "config"),
            )
            listed = run(
                ["plasma-apply-desktoptheme", "--list-themes"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn(DTHEME_ID, listed.stdout)
            applied = run(
                ["plasma-apply-desktoptheme", DTHEME_ID],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            parser = read_kde_config(os.path.join(tmp, "config", "plasmarc"))
            self.assertEqual(parser.get("Theme", "name"), DTHEME_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Plasma/Theme"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = DTHEME_ID


if __name__ == "__main__":
    unittest.main()
