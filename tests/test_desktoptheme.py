"""Validate the org.macos8.desktop Plasma desktop theme package."""

import configparser
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

from theme_install import ROOT, install, uninstall

DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktop-themes", DTHEME_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
SVG = os.path.join(PACKAGE, "widgets", "panel-background.svg")

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
        self.tree = ET.parse(SVG)
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


class TestDefaultsWiring(unittest.TestCase):
    def test_defaults_select_the_desktop_theme(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        with open(LNF_DEFAULTS, encoding="utf-8") as handle:
            parser.read_file(handle)
        self.assertEqual(
            parser.get(PLASMA_SECTION, "name"),
            load_metadata()["KPlugin"]["Id"],
        )


class TestInstall(unittest.TestCase):
    def test_make_install_copies_package_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = os.path.join(
                tmp, "share", "plasma", "desktoptheme", DTHEME_ID
            )
            for name in (
                "metadata.json",
                os.path.join("widgets", "panel-background.svg"),
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
            installed = os.path.join(
                tmp, "share", "plasma", "desktoptheme", DTHEME_ID
            )
            metadata = os.path.join(installed, "metadata.json")
            with open(metadata, "rb") as handle:
                good = handle.read()

            # Shadow `cp` with a fake that fails only when copying the desktop
            # theme (the look-and-feel copy must still succeed), writing part of
            # the tree then dying like a killed or out-of-space `cp` would.
            real_cp = shutil.which("cp")
            bindir = os.path.join(tmp, "fakebin")
            os.makedirs(bindir)
            fake_cp = os.path.join(bindir, "cp")
            with open(fake_cp, "w", encoding="utf-8") as handle:
                handle.write(
                    "#!/bin/sh\n"
                    'case "$2" in\n'
                    "  */desktop-themes/*)\n"
                    '    dest="$3/$(basename "$2")"\n'
                    '    mkdir -p "$dest"\n'
                    '    printf partial > "$dest/metadata.json"\n'
                    "    exit 1;;\n"
                    "esac\n"
                    f'exec "{real_cp}" "$@"\n'
                )
            os.chmod(fake_cp, 0o755)

            env = dict(os.environ)
            env["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")
            result = subprocess.run(
                ["make", "install", f"DESTDIR={tmp}", "XDG_DATA_HOME=/share"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertFalse(
                os.path.exists(
                    os.path.join(
                        tmp, "share", "plasma", "desktoptheme",
                        "." + DTHEME_ID + ".staging",
                    )
                ),
                "staging directory leaked after a failed install",
            )
            self.assertTrue(os.path.isdir(installed), installed)
            with open(metadata, "rb") as handle:
                self.assertEqual(handle.read(), good)

    def test_make_uninstall_removes_the_installed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            package = os.path.join(
                tmp, "share", "plasma", "desktoptheme", DTHEME_ID
            )
            self.assertTrue(os.path.isdir(package), package)

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(package), package)

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
            listed = subprocess.run(
                ["plasma-apply-desktoptheme", "--list-themes"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn(DTHEME_ID, listed.stdout)
            applied = subprocess.run(
                ["plasma-apply-desktoptheme", DTHEME_ID],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            parser.read(os.path.join(tmp, "config", "plasmarc"))
            self.assertEqual(parser.get("Theme", "name"), DTHEME_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(unittest.TestCase):
    def test_kpackagetool6_installs_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
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
