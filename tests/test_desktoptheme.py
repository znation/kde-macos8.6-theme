"""Validate the org.macos8.desktop Plasma desktop theme package."""

import json
import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from kde_config import read as read_kde_config
from theme_install import (
    ROOT,
    install,
    installed_package,
    installed_plasma_dir,
    run,
    shadow_command_env,
    uninstall,
)

DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktop-themes", DTHEME_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
PANEL_SVG = os.path.join(PACKAGE, "widgets", "panel-background.svg")
FRAME_SVG = os.path.join(PACKAGE, "widgets", "frame.svg")
FRAME_PREFIXES = ("plain", "raised", "sunken")
BUTTON_SVG = os.path.join(PACKAGE, "widgets", "button.svg")
BUTTON_PREFIXES = ("normal", "pressed", "focus")
BUTTON_MARGIN_HINTS = (
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
)

LNF_DEFAULTS = os.path.join(
    ROOT, "theme", "look-and-feel", DTHEME_ID, "contents", "defaults"
)
# configparser reads the KDE `[plasmarc][Theme]` header greedily, so the
# section key includes the inner bracket pair.
PLASMA_SECTION = "plasmarc][Theme"

SLICE_IDS = [
    "center", "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
]
HINT_IDS = [
    "hint-tile-center",
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
    "hint-top-inset", "hint-bottom-inset",
    "hint-left-inset", "hint-right-inset",
]

# Every pixel of each raised/sunken 3x3 corner slice, row-major in slice-local
# coordinates. The bevel must turn the corner: the edge bevel colours continue
# into the corner and meet there. A corner that stops the bevel one pixel short
# leaves a face-coloured (#DDDDDD) notch where the side tile shows highlight or
# shadow, so pinning the pixels makes that defect fail the suite.
CORNER_PIXELS = {
    "raised": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#FFFFFF", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#FFFFFF", "#999999", "#000000",
            "#DDDDDD", "#999999", "#000000",
        ),
        "bottomleft": (
            "#000000", "#FFFFFF", "#DDDDDD",
            "#000000", "#999999", "#999999",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#999999", "#000000",
            "#999999", "#999999", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
    "sunken": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#999999", "#999999",
            "#000000", "#999999", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#999999", "#FFFFFF", "#000000",
            "#DDDDDD", "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", "#999999", "#DDDDDD",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#FFFFFF", "#000000",
            "#FFFFFF", "#FFFFFF", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
}


def render_slices(tree):
    """Composite each id-bearing <g> of the frame into a {(x, y): fill} map.

    Coordinates are slice-local: the groups are pure translations, so a
    slice's appearance is its rects painted in document order, with a later
    rect overriding an earlier one as KSvg composites one nine-slice tile.
    """
    slices = {}
    for group in tree.iter():
        if group.tag.rsplit("}", 1)[-1] != "g" or not group.get("id"):
            continue
        pixels = {}
        for rect in group:
            if rect.tag.rsplit("}", 1)[-1] != "rect":
                continue
            x = int(rect.get("x", 0))
            y = int(rect.get("y", 0))
            for dx in range(int(rect.get("width"))):
                for dy in range(int(rect.get("height"))):
                    pixels[(x + dx, y + dy)] = rect.get("fill")
        slices[group.get("id")] = pixels
    return slices


def load_metadata():
    with open(METADATA, encoding="utf-8") as handle:
        return json.load(handle)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = load_metadata()

    def test_package_structure(self):
        self.assertEqual(self.metadata.get("KPackageStructure"), "Plasma/Theme")

    def test_plugin_id_and_name(self):
        plugin = self.metadata["KPlugin"]
        self.assertEqual(plugin["Id"], DTHEME_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")

    def test_plugin_version(self):
        self.assertTrue(self.metadata["KPlugin"].get("Version"))

    def test_plasma_api_version(self):
        self.assertEqual(self.metadata.get("X-Plasma-API"), "5.0")


class TestPanelBackground(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(PANEL_SVG)
        self.ids = {el.get("id") for el in self.tree.iter() if el.get("id")}

    def test_nine_slice_ids_present(self):
        for name in SLICE_IDS:
            self.assertIn(name, self.ids, name)

    def test_hint_ids_present(self):
        for name in HINT_IDS:
            self.assertIn(name, self.ids, name)

    def test_platinum_colours_present(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment names all four colours, so a text search would pass
        # even if the artwork used none of them.
        fills = {el.get("fill") for el in self.tree.iter() if el.get("fill")}
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_no_script_elements(self):
        for element in self.tree.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            self.assertFalse(tag.endswith("script"), tag)


class TestButton(unittest.TestCase):
    def test_button_slice_ids(self):
        tree = ET.parse(BUTTON_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for prefix in BUTTON_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for hint in BUTTON_MARGIN_HINTS:
                self.assertIn(f"{prefix}-{hint}", ids, hint)
        self.assertIn("hint-tile-center", ids)

    def test_button_colours(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment and the hint rects (which set colour through `style`)
        # would otherwise make a text search pass without any Platinum grey.
        tree = ET.parse(BUTTON_SVG)
        fills = {el.get("fill") for el in tree.iter() if el.get("fill")}
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_no_script_elements(self):
        tree = ET.parse(BUTTON_SVG)
        for element in tree.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            self.assertFalse(tag.endswith("script"), tag)


class TestFrame(unittest.TestCase):
    def test_frame_svg_contract(self):
        tree = ET.parse(FRAME_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for prefix in FRAME_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for side in ("top", "bottom", "left", "right"):
                self.assertIn(f"{prefix}-hint-{side}-margin", ids, side)
        self.assertIn("hint-tile-center", ids)
        # Read the raw file for the palette: the frame's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(FRAME_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)
        for element in tree.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            self.assertFalse(tag.endswith("script"), tag)

    def test_frame_corner_bevels_turn_the_corner(self):
        slices = render_slices(ET.parse(FRAME_SVG))
        for prefix, corners in CORNER_PIXELS.items():
            for name, expected in corners.items():
                pixels = slices[f"{prefix}-{name}"]
                actual = tuple(
                    pixels.get((x, y))
                    for y in range(3)
                    for x in range(3)
                )
                self.assertEqual(actual, expected, f"{prefix}-{name}")

    def test_frame_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = os.path.join(
                installed_package(tmp, "desktoptheme", DTHEME_ID),
                "widgets", "frame.svg",
            )
            self.assertTrue(os.path.isfile(target), target)
            with open(FRAME_SVG, "rb") as source, open(target, "rb") as installed:
                self.assertEqual(source.read(), installed.read())
            again = install(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


class TestDefaultsWiring(unittest.TestCase):
    def test_defaults_select_the_desktop_theme(self):
        parser = read_kde_config(LNF_DEFAULTS)
        self.assertEqual(
            parser.get(PLASMA_SECTION, "name"),
            load_metadata()["KPlugin"]["Id"],
        )


class TestInstall(unittest.TestCase):
    def test_make_install_copies_package_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = installed_package(tmp, "desktoptheme", DTHEME_ID)
            for name in (
                "metadata.json",
                os.path.join("widgets", "panel-background.svg"),
                os.path.join("widgets", "button.svg"),
            ):
                source = os.path.join(PACKAGE, name)
                target = os.path.join(installed, name)
                self.assertTrue(os.path.isfile(target), target)
                with open(source, "rb") as a, open(target, "rb") as b:
                    self.assertEqual(a.read(), b.read(), name)

    def test_make_install_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)

    def test_failed_reinstall_keeps_the_previous_package(self):
        """A copy that dies partway must not delete or damage the working install.

        `make install` copies into a sibling staging directory and swaps it in
        with a rename, so a copy that fails or is interrupted leaves the working
        desktop theme installed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed = installed_package(tmp, "desktoptheme", DTHEME_ID)
            metadata = os.path.join(installed, "metadata.json")
            with open(metadata, "rb") as handle:
                good = handle.read()

            # Shadow `cp` with a fake that fails only when copying the desktop
            # theme (the look-and-feel copy must still succeed), writing part of
            # the tree then dying like a killed or out-of-space `cp` would.
            real_cp = shutil.which("cp")
            env = shadow_command_env(
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
            result = install(tmp, env=env)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(
                os.path.exists(
                    os.path.join(
                        installed_plasma_dir(tmp, "desktoptheme"),
                        "." + DTHEME_ID + ".staging",
                    )
                ),
                "staging directory leaked after a failed install",
            )
            self.assertTrue(os.path.isdir(installed), installed)
            with open(metadata, "rb") as handle:
                self.assertEqual(handle.read(), good)

    def test_failed_swap_keeps_the_previous_package(self):
        """A rename that fails after the old package is moved aside restores it.

        `make install` moves the working desktop theme to a hidden sibling
        before renaming the staged copy into place. If that final rename fails,
        the EXIT trap must move the old package back, so a failed swap leaves
        the working theme rather than deleting it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            installed = installed_package(tmp, "desktoptheme", DTHEME_ID)
            metadata = os.path.join(installed, "metadata.json")
            with open(metadata, "rb") as handle:
                good = handle.read()

            # Shadow `mv` so only the final rename of the staged desktop theme
            # into place fails (the look-and-feel rename must still succeed),
            # like an IO error or a kill in the swap window would.
            real_mv = shutil.which("mv")
            env = shadow_command_env(
                tmp,
                "mv",
                "#!/bin/sh\n"
                'case "$2" in\n'
                f"  */plasma/desktoptheme/{DTHEME_ID})\n"
                '    case "$1" in\n'
                f"      */.{DTHEME_ID}.staging) exit 1;;\n"
                "    esac;;\n"
                "esac\n"
                f'exec "{real_mv}" "$@"\n',
            )
            result = install(tmp, env=env)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            parent = installed_plasma_dir(tmp, "desktoptheme")
            for leaked in (
                "." + DTHEME_ID + ".staging",
                "." + DTHEME_ID + ".old",
            ):
                self.assertFalse(
                    os.path.exists(os.path.join(parent, leaked)),
                    f"{leaked} leaked after a failed swap",
                )
            self.assertTrue(os.path.isdir(installed), installed)
            with open(metadata, "rb") as handle:
                self.assertEqual(handle.read(), good)

    def test_make_uninstall_removes_the_installed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            parent = installed_plasma_dir(tmp, "desktoptheme")
            package = os.path.join(parent, DTHEME_ID)
            self.assertTrue(os.path.isdir(package), package)

            # SIGKILL cannot be trapped, so an install killed in the swap
            # window leaves a hidden staging directory and the moved-aside old
            # package behind. `uninstall` must remove those leftovers too.
            leaked = [
                os.path.join(parent, "." + DTHEME_ID + ".staging"),
                os.path.join(parent, "." + DTHEME_ID + ".old"),
            ]
            for path in leaked:
                os.makedirs(path)
                with open(
                    os.path.join(path, "metadata.json"), "w", encoding="utf-8"
                ) as handle:
                    handle.write("{}")

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(package), package)
            for path in leaked:
                self.assertFalse(
                    os.path.exists(path),
                    f"{path} leaked after uninstall",
                )

            again = uninstall(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


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
class TestPackageValid(unittest.TestCase):
    def test_kpackagetool6_installs_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                [
                    "kpackagetool6", "-t", "Plasma/Theme",
                    "-p", tmp, "-i", PACKAGE,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                os.path.isfile(os.path.join(tmp, DTHEME_ID, "metadata.json"))
            )


if __name__ == "__main__":
    unittest.main()
