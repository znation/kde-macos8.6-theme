"""Validate the org.macos8.desktop icon theme package.

The package ships our own final Platinum-style art for the icons a default Mac
OS 8.6 desktop shows; these tests pin the theme's identity, the per-size SVG
shape and Platinum palette of every icon, the placeholder register (empty now
that the art is final), and the install/uninstall lifecycle.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.install_lifecycle_cases import InstallLifecycleCases
from support.kde_config import read as read_kde_config
from support.platinum_palette import PLATINUM_FILLS
from support.shipped_files import shipped_files
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
)
from support.theme_install import (
    ROOT,
    installed_icon_theme,
    installed_icons_dir,
)

ICON_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "icons", ICON_ID)
INDEX = os.path.join(PACKAGE, "index.theme")
PLACEHOLDERS = os.path.join(ROOT, "PLACEHOLDERS.md")

# The icons the package ships: the desktop's hard disk, folder, document and
# Trash (32x32), the `inode-directory` alias KDE resolves a directory to, and
# the kicker logo the menu bar's top-left button shows at the two panel sizes.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"),
)


def _declared_size(icon):
    """Return the pixel size declared by *icon*'s leading ``NNxNN`` directory."""
    directory = os.path.dirname(icon).split(os.sep)[0]
    return int(directory.split("x", 1)[0])


SVG_NS = "{http://www.w3.org/2000/svg}"


def _icon_path(icon):
    """Return *icon*'s path as PLACEHOLDERS.md writes it."""
    return "theme/icons/" + ICON_ID + "/" + icon.replace(os.sep, "/")


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.parser = read_kde_config(INDEX)

    def test_names_the_theme_and_inherits_breeze(self):
        self.assertEqual(self.parser.get("Icon Theme", "Name"), ICON_ID)
        self.assertEqual(self.parser.get("Icon Theme", "Inherits"), "breeze")

    def test_comment_names_the_final_platinum_art(self):
        # The art is final (see PLACEHOLDERS.md), so the description KDE shows
        # in System Settings must not still call these icons placeholders.
        self.assertEqual(
            self.parser.get("Icon Theme", "Comment"),
            "Mac OS 8.6 Platinum icon theme",
        )

    def test_every_shipped_icon_lives_in_a_declared_size_directory(self):
        directories = [
            entry.strip()
            for entry in self.parser.get("Icon Theme", "Directories").split(",")
        ]
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                directory = os.path.dirname(icon)
                self.assertIn(directory, directories)
                self.assertEqual(
                    self.parser.get(directory, "Size"),
                    str(_declared_size(icon)),
                )

    def test_icon_theme_ships_exactly_the_tracked_icons(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, {"index.theme", *SHIPPED_ICONS})

    def test_placeholder_register_matches_the_icon_art(self):
        # Every shipped icon is final art, so neither side lists one: the
        # register's rows for these icons and the icons carrying a
        # `PLACEHOLDER:` marker are both empty and must stay equal.
        with open(PLACEHOLDERS, encoding="utf-8") as handle:
            register = handle.read()
        registered = {icon for icon in SHIPPED_ICONS if _icon_path(icon) in register}
        marked = set()
        for icon in SHIPPED_ICONS:
            with open(os.path.join(PACKAGE, icon), encoding="utf-8") as handle:
                if "PLACEHOLDER:" in handle.read():
                    marked.add(icon)
        self.assertEqual(registered, marked)


class TestIcons(unittest.TestCase):
    def test_each_icon_is_a_square_svg_of_its_declared_size(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                size = str(_declared_size(icon))
                root = ET.parse(os.path.join(PACKAGE, icon)).getroot()
                self.assertEqual(root.tag, SVG_NS + "svg")
                self.assertEqual(root.get("width"), size)
                self.assertEqual(root.get("height"), size)
                self.assertEqual(root.get("viewBox"), f"0 0 {size} {size}")

    def test_each_icon_uses_only_the_platinum_palette(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                tree = ET.parse(os.path.join(PACKAGE, icon))
                self.assertLessEqual(
                    attribute_values(tree, "fill"),
                    PLATINUM_FILLS,
                    "a fill is outside the Platinum palette",
                )

    def test_the_icons_together_use_the_full_platinum_palette(self):
        colours = set()
        for icon in SHIPPED_ICONS:
            tree = ET.parse(os.path.join(PACKAGE, icon))
            colours |= attribute_values(tree, "fill")
        self.assertEqual(colours, PLATINUM_FILLS)

    def test_each_icon_has_no_scripts_styles_external_refs_or_duplicate_ids(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                tree = ET.parse(os.path.join(PACKAGE, icon))
                assert_no_script_elements(self, tree)
                assert_no_style_elements(self, tree)
                assert_no_external_references(self, tree)
                assert_unique_ids(self, tree)


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
