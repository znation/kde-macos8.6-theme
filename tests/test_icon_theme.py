"""Validate the org.macos8.desktop icon theme package.

The package ships our own placeholder art for the icons a default Mac OS 8.6
desktop shows (see PLACEHOLDERS.md); these tests pin the theme's identity, the
32x32 SVG shape of every icon, and the install/uninstall lifecycle.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from install_lifecycle_cases import InstallLifecycleCases
from kde_config import read as read_kde_config
from theme_install import (
    ROOT,
    installed_icon_theme,
    installed_icons_dir,
)

ICON_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "icons", ICON_ID)
INDEX = os.path.join(PACKAGE, "index.theme")
PLACEHOLDERS = os.path.join(ROOT, "PLACEHOLDERS.md")

# The 32x32 icons the package ships: the desktop's hard disk, folder, document
# and Trash, plus the `inode-directory` alias KDE resolves a directory to.
# PLACEHOLDERS.md tracks each one for replacement with final art.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
)

SVG_NS = "{http://www.w3.org/2000/svg}"


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.parser = read_kde_config(INDEX)

    def test_names_the_theme_and_inherits_breeze(self):
        self.assertEqual(self.parser.get("Icon Theme", "Name"), ICON_ID)
        self.assertEqual(self.parser.get("Icon Theme", "Inherits"), "breeze")

    def test_every_shipped_icon_lives_in_a_declared_32px_directory(self):
        directories = [
            entry.strip()
            for entry in self.parser.get("Icon Theme", "Directories").split(",")
        ]
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                directory = os.path.dirname(icon)
                self.assertIn(directory, directories)
                self.assertEqual(self.parser.get(directory, "Size"), "32")

    def test_icon_theme_ships_exactly_the_tracked_icons(self):
        shipped = set()
        for dirpath, _, filenames in os.walk(PACKAGE):
            for filename in filenames:
                shipped.add(
                    os.path.relpath(os.path.join(dirpath, filename), PACKAGE)
                )
        self.assertEqual(shipped, {"index.theme", *SHIPPED_ICONS})

    def test_placeholders_are_tracked_for_replacement(self):
        with open(PLACEHOLDERS, encoding="utf-8") as handle:
            text = handle.read()
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                self.assertIn(
                    "theme/icons/" + ICON_ID + "/" + icon.replace(os.sep, "/"),
                    text,
                )


class TestIcons(unittest.TestCase):
    def test_each_icon_is_a_32_pixel_svg(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                root = ET.parse(os.path.join(PACKAGE, icon)).getroot()
                self.assertEqual(root.tag, SVG_NS + "svg")
                self.assertEqual(root.get("width"), "32")
                self.assertEqual(root.get("height"), "32")
                self.assertEqual(root.get("viewBox"), "0 0 32 32")


class TestInstall(InstallLifecycleCases, unittest.TestCase):
    PACKAGE_ID = ICON_ID
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = ("index.theme",) + SHIPPED_ICONS

    def installed_parent(self, tmp):
        return installed_icons_dir(tmp)

    def installed_package_dir(self, tmp):
        return installed_icon_theme(tmp, self.PACKAGE_ID)


if __name__ == "__main__":
    unittest.main()
