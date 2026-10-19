"""Validate the org.macos8.desktop icon theme package.

The package ships our own final Platinum-style art for the icons a default Mac
OS 8.6 desktop shows; these tests pin the theme's identity, the per-size SVG
shape and Platinum palette of every icon, the placeholder register (empty now
that the art is final), and the install/uninstall lifecycle.
"""

from __future__ import annotations

import os
import unittest

from support.install_lifecycle_cases import InstallLifecycleCases
from support.kde_config import read as read_kde_config
from support.platinum_palette import PLATINUM_FILLS
from support.shipped_files import shipped_files
from support.svg_case import parse_svg
from support.installed_paths import installed_icon_theme, installed_icons_dir
from support.theme_install import ROOT
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
    local_name,
)

ICON_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "icons", ICON_ID)
INDEX = os.path.join(PACKAGE, "index.theme")
PLACEHOLDERS = os.path.join(ROOT, "PLACEHOLDERS.md")

# The icons the package ships: the desktop's hard disk, folder, document,
# Trash and full Trash (32x32), the `inode-directory` alias KDE resolves a
# directory to, the kicker logo the menu bar's top-left button shows at the
# two panel sizes, and the `go-next-symbolic` submenu arrow the reference's
# open Apple menu draws.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
    os.path.join("32x32", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"),
    os.path.join("16x16", "actions", "go-next-symbolic.svg"),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"),
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
                root = parse_svg(os.path.join(PACKAGE, icon)).getroot()
                self.assertEqual(root.tag, SVG_NS + "svg")
                self.assertEqual(root.get("width"), size)
                self.assertEqual(root.get("height"), size)
                self.assertEqual(root.get("viewBox"), f"0 0 {size} {size}")

    def test_each_icon_uses_only_the_platinum_palette(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                tree = parse_svg(os.path.join(PACKAGE, icon))
                self.assertLessEqual(
                    attribute_values(tree, "fill"),
                    PLATINUM_FILLS,
                    "a fill is outside the Platinum palette",
                )

    def test_the_icons_together_use_the_full_platinum_palette(self):
        colours = set()
        for icon in SHIPPED_ICONS:
            tree = parse_svg(os.path.join(PACKAGE, icon))
            colours |= attribute_values(tree, "fill")
        self.assertEqual(colours, PLATINUM_FILLS)

    def test_each_icon_has_no_scripts_styles_external_refs_or_duplicate_ids(self):
        for icon in SHIPPED_ICONS:
            with self.subTest(icon=icon):
                tree = parse_svg(os.path.join(PACKAGE, icon))
                assert_no_script_elements(self, tree)
                assert_no_style_elements(self, tree)
                assert_no_external_references(self, tree)
                assert_unique_ids(self, tree)


def _shape(tag, **attributes):
    """Return one expected drawing element: its tag and its attributes."""
    return (tag, attributes)


def _drawing_elements(tree):
    """Return each of *tree*'s root children as ``(tag, attributes)``.

    In document order, so an added, removed, reordered or re-drawn element
    changes the tuple; the icon art holds only drawing elements, with no
    groups or ids, so every root child is one.
    """
    return tuple(
        (local_name(element), dict(element.attrib))
        for element in tree.getroot()
    )


# Every drawing element of every shipped icon, in document order. The icon art
# is our own, so nothing else re-derives it; the size, palette and structural
# tests above would all pass if a path's `d`, a rect's geometry, an element's
# order or an element's fill changed -- an icon could silently lose its
# outline, bevel, plate or ribs -- so pin each element exactly. The 32x32
# folder and its `inode-directory` alias share one shape (Mac OS 8.6 draws one
# folder for both names); they are pinned separately and cross-checked below.
ICON_SHAPES = {
    os.path.join("32x32", "devices", "drive-harddisk.svg"): (
        _shape("rect", x="3", y="8", width="26", height="17", fill="#000000"),
        _shape("rect", x="4", y="9", width="24", height="15", fill="#DDDDDD"),
        _shape("rect", x="4", y="9", width="24", height="2", fill="#FFFFFF"),
        _shape("rect", x="4", y="9", width="1", height="15", fill="#FFFFFF"),
        _shape("rect", x="4", y="22", width="24", height="2", fill="#999999"),
        _shape("rect", x="27", y="9", width="1", height="15", fill="#999999"),
        _shape("rect", x="6", y="14", width="14", height="6", fill="#000000"),
        _shape("rect", x="7", y="15", width="12", height="4", fill="#FFFFFF"),
        _shape("circle", cx="24", cy="17", r="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"): (
        _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
        _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
        _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
        _shape("rect", x="10", y="15", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="8", height="1", fill="#999999"),
    ),
    os.path.join("32x32", "places", "folder.svg"): (
        _shape("path", d="M3 8 h10 l3 3 h13 v14 H3 Z", fill="#000000"),
        _shape("path", d="M4 9 h9 l3 3 h12 v12 H4 Z", fill="#DDDDDD"),
        _shape("path", d="M4 9 h9 l3 3 h12 v1 h-12 l-3 -3 h-9 Z", fill="#FFFFFF"),
        _shape("rect", x="4", y="9", width="1", height="15", fill="#FFFFFF"),
        _shape("rect", x="4", y="23", width="21", height="1", fill="#999999"),
        _shape("rect", x="27", y="12", width="1", height="12", fill="#999999"),
    ),
    os.path.join("32x32", "places", "inode-directory.svg"): (
        _shape("path", d="M3 8 h10 l3 3 h13 v14 H3 Z", fill="#000000"),
        _shape("path", d="M4 9 h9 l3 3 h12 v12 H4 Z", fill="#DDDDDD"),
        _shape("path", d="M4 9 h9 l3 3 h12 v1 h-12 l-3 -3 h-9 Z", fill="#FFFFFF"),
        _shape("rect", x="4", y="9", width="1", height="15", fill="#FFFFFF"),
        _shape("rect", x="4", y="23", width="21", height="1", fill="#999999"),
        _shape("rect", x="27", y="12", width="1", height="12", fill="#999999"),
    ),
    os.path.join("32x32", "places", "user-trash.svg"): (
        _shape("rect", x="12", y="4", width="8", height="4", fill="#000000"),
        _shape("rect", x="13", y="5", width="6", height="3", fill="#DDDDDD"),
        _shape("rect", x="6", y="8", width="20", height="5", fill="#000000"),
        _shape("rect", x="7", y="9", width="18", height="4", fill="#DDDDDD"),
        _shape("rect", x="7", y="9", width="18", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="12", width="18", height="1", fill="#999999"),
        _shape("path", d="M9 13 h14 l-2 16 H11 Z", fill="#000000"),
        _shape("path", d="M10 14 h12 l-2 14 H12 Z", fill="#DDDDDD"),
        _shape("rect", x="13", y="16", width="1", height="10", fill="#999999"),
        _shape("rect", x="14", y="16", width="1", height="10", fill="#FFFFFF"),
        _shape("rect", x="17", y="16", width="1", height="10", fill="#999999"),
        _shape("rect", x="18", y="16", width="1", height="10", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "places", "user-trash-full.svg"): (
        _shape("path", d="M12 2 l3 2 l3 -2 l1 7 h-8 Z", fill="#000000"),
        _shape("path", d="M13 3 l2 1 l2 -1 l1 5 h-6 Z", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="20", height="5", fill="#000000"),
        _shape("rect", x="7", y="9", width="18", height="4", fill="#DDDDDD"),
        _shape("rect", x="7", y="9", width="18", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="12", width="18", height="1", fill="#999999"),
        _shape("path", d="M9 13 h14 l-2 16 H11 Z", fill="#000000"),
        _shape("path", d="M10 14 h12 l-2 14 H12 Z", fill="#DDDDDD"),
        _shape("rect", x="13", y="16", width="1", height="10", fill="#999999"),
        _shape("rect", x="14", y="16", width="1", height="10", fill="#FFFFFF"),
        _shape("rect", x="17", y="16", width="1", height="10", fill="#999999"),
        _shape("rect", x="18", y="16", width="1", height="10", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"): (
        _shape("rect", x="1", y="1", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="2", width="12", height="8", fill="#DDDDDD"),
        _shape("rect", x="2", y="2", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="2", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="2", y="9", width="12", height="1", fill="#999999"),
        _shape("rect", x="13", y="2", width="1", height="8", fill="#999999"),
        _shape("rect", x="7", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="4", y="13", width="8", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"): (
        _shape("rect", x="1", y="1", width="20", height="14", fill="#000000"),
        _shape("rect", x="2", y="2", width="18", height="12", fill="#DDDDDD"),
        _shape("rect", x="2", y="2", width="18", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="2", width="1", height="12", fill="#FFFFFF"),
        _shape("rect", x="2", y="13", width="18", height="1", fill="#999999"),
        _shape("rect", x="19", y="2", width="1", height="12", fill="#999999"),
        _shape("rect", x="10", y="15", width="2", height="3", fill="#000000"),
        _shape("rect", x="6", y="18", width="10", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "actions", "go-next-symbolic.svg"): (
        _shape("path", d="M 6,3 L 6,11 L 10,7 Z", fill="#000000"),
    ),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"): (
        _shape("path", d="M 8,4 L 8,15 L 14,10 Z", fill="#000000"),
    ),
}


class TestIconGeometry(unittest.TestCase):
    """Pin every shipped icon's drawing elements, in document order."""

    def test_the_geometry_registry_covers_every_shipped_icon(self):
        # The per-icon pins below only visit the icons listed in ICON_SHAPES,
        # so a newly shipped icon that is never added there would silently
        # escape them. Derive the shipped set from the same list TestIndex
        # checks and require the registry to equal it.
        self.assertEqual(set(ICON_SHAPES), set(SHIPPED_ICONS))

    def test_each_icon_draws_its_pinned_artwork(self):
        for icon, expected in ICON_SHAPES.items():
            with self.subTest(icon=icon):
                tree = parse_svg(os.path.join(PACKAGE, icon))
                self.assertEqual(_drawing_elements(tree), expected)

    def test_the_folder_alias_shares_the_folder_art(self):
        # Mac OS 8.6 draws one folder shape for both the `folder` and
        # `inode-directory` names, so the alias must stay the same drawing;
        # pinning only each one's own elements would let them drift apart.
        folder = _drawing_elements(
            parse_svg(os.path.join(PACKAGE, "32x32", "places", "folder.svg"))
        )
        alias = _drawing_elements(
            parse_svg(
                os.path.join(PACKAGE, "32x32", "places", "inode-directory.svg")
            )
        )
        self.assertEqual(alias, folder)


class TestInstall(InstallLifecycleCases, unittest.TestCase):
    PACKAGE_ID = ICON_ID
    MAKE_PACKAGES = "icon-theme"
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = ("index.theme",) + SHIPPED_ICONS

    def installed_parent(self, tmp):
        """Return the directory holding the installed icon themes."""
        return installed_icons_dir(tmp)

    def installed_package_dir(self, tmp):
        """Return the installed icon theme's own directory."""
        return installed_icon_theme(tmp, self.PACKAGE_ID)


if __name__ == "__main__":
    unittest.main()
