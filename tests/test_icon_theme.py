"""Validate the org.macos8.desktop icon theme package.

The package ships original Platinum-style icon placeholders; these tests pin
the theme's identity, per-size SVG shape and palette, placeholder tracking,
and the install/uninstall lifecycle. The per-icon drawing pins live in
`test_icon_theme_geometry`.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

from support import containment
from support.install_lifecycle_cases import InstallLifecycleCases
from support.kde_config import read as read_kde_config
from support.platinum_palette import PLATINUM_FILLS
from support.shipped_files import shipped_files
from support.svg_case import parse_svg
from support.icon.theme_inventory import ICON_ID, PACKAGE, SHIPPED_ICONS
from support.installed_paths import installed_icon_theme, installed_icons_dir
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
)

INDEX = os.path.join(PACKAGE, "index.theme")
PLACEHOLDERS = os.path.join(ROOT, "PLACEHOLDERS.md")

# The package also ships the Platinum Xcursor pointer set with their X-name
# aliases. These are binary Xcursor files, not SVGs, so the SVG-level
# assertions below keep iterating `SHIPPED_ICONS` only.
SHIPPED_CURSORS = tuple(
    os.path.join("cursors", name)
    for name in (
        "left_ptr",
        "arrow",
        "default",
        "top_left_arrow",
        "dnd-none",
        "xterm",
        "text",
        "ibeam",
        "hand2",
        "hand1",
        "pointer",
        "pointing_hand",
        "watch",
        "wait",
        "fleur",
        "move",
        "all-scroll",
        "size_all",
        "dnd-move",
        "size_hor",
        "e-resize",
        "ew-resize",
        "w-resize",
        "h_double_arrow",
        "sb_h_double_arrow",
        "col-resize",
        "split_h",
        "left_side",
        "right_side",
        "size_ver",
        "n-resize",
        "ns-resize",
        "s-resize",
        "sb_v_double_arrow",
        "v_double_arrow",
        "00008160000006810000408080010102",
        "row-resize",
        "split_v",
        "top_side",
        "bottom_side",
        "size_fdiag",
        "nw-resize",
        "se-resize",
        "nwse-resize",
        "top_left_corner",
        "bottom_right_corner",
        "size_bdiag",
        "ne-resize",
        "sw-resize",
        "nesw-resize",
        "top_right_corner",
        "bottom_left_corner",
        "crosshair",
        "cross",
        "tcross",
        "not-allowed",
        "circle",
        "crossed_circle",
        "03b6e0fcb3499374a867c041f52298f0",
        "forbidden",
        "no-drop",
        "dnd-no-drop",
        "dnd-copy",
        "cell",
        "plus",
        "grab",
        "openhand",
        "grabbing",
        "closedhand",
        "help",
        "left_ptr_help",
        "question_arrow",
        "whats_this",
        "5c6cd98b3f3ebcb1f9c7f1c204630408",
        "d9ce0ab605698f320427677b458ad60b",
        "progress",
        "half-busy",
        "left_ptr_watch",
        "00000000000000020006000e7e9ffc3f",
        "08e8e1c95fe2fc01f976f1e063a24ccd",
        "3ecb610c1bf2410f44200f48c40d3599",
        "pencil",
        "zoom-in",
        "zoom-out",
        "context-menu",
    )
)


def _declared_size(icon):
    """Return the pixel size declared by *icon*'s leading ``NNxNN`` directory."""
    directory = os.path.dirname(icon).split(os.sep)[0]
    return int(directory.split("x", 1)[0])


SVG_NS = "{http://www.w3.org/2000/svg}"


def _icon_path(icon):
    """Return *icon*'s path as PLACEHOLDERS.md writes it."""
    return "theme/icons/" + ICON_ID + "/" + icon.replace(os.sep, "/")


def _read_icon_text(path):
    """Read contributor-supplied icon-theme text, refusing a symlink escape.

    The placeholder check reads PLACEHOLDERS.md and every shipped icon as raw
    text. A checked-in symlink at either path can point at a private file or
    a device outside the repository, and an unbounded read would load it
    whole; the shared guard refuses that path before it is opened and caps
    the read, the same way the other theme-text readers do.
    """
    return containment.read_text(path, ROOT)


class TestIconTextContainment(unittest.TestCase):
    """The placeholder check's text reads refuse a symlink escape."""

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "PLACEHOLDERS.md", "private marker\n"
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    _read_icon_text(link)
        self.assertIn(str(link), str(caught.exception))
        self.assertNotIn("private marker", str(caught.exception))

    def test_reads_a_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp,
                "PLACEHOLDERS.md",
                "placeholder text\n",
                target="theme/PLACEHOLDERS.md",
            )
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                text = _read_icon_text(link)
        self.assertEqual(text, "placeholder text\n")


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.parser = read_kde_config(INDEX)

    def test_names_the_theme_and_inherits_breeze(self):
        self.assertEqual(self.parser.get("Icon Theme", "Name"), "Platinum")
        self.assertEqual(self.parser.get("Icon Theme", "Inherits"), "breeze")

    def test_comment_names_platinum_icon_art(self):
        self.assertEqual(
            self.parser.get("Icon Theme", "Comment"),
            "Platinum icon theme with original placeholder artwork",
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
        self.assertEqual(
            shipped,
            {"index.theme", *SHIPPED_ICONS, *SHIPPED_CURSORS},
        )

    def test_placeholder_register_matches_the_icon_art(self):
        # Tracked placeholder art and its register stay in agreement: every
        # shipped icon carrying a `PLACEHOLDER:` marker has a row, every row
        # names a marked shipped icon, and the tracked set never silently
        # empties. Icons without a marker ship untracked.
        register = _read_icon_text(PLACEHOLDERS)
        registered = {icon for icon in SHIPPED_ICONS if _icon_path(icon) in register}
        marked = set()
        for icon in SHIPPED_ICONS:
            if "PLACEHOLDER:" in _read_icon_text(os.path.join(PACKAGE, icon)):
                marked.add(icon)
        self.assertEqual(registered, set(SHIPPED_ICONS))
        self.assertEqual(marked, set(SHIPPED_ICONS))


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


class TestInstall(InstallLifecycleCases, unittest.TestCase):
    PACKAGE_ID = ICON_ID
    MAKE_PACKAGES = "icon-theme"
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = ("index.theme",) + SHIPPED_ICONS + SHIPPED_CURSORS

    def installed_parent(self, tmp):
        """Return the directory holding the installed icon themes."""
        return installed_icons_dir(tmp)

    def installed_package_dir(self, tmp):
        """Return the installed icon theme's own directory."""
        return installed_icon_theme(tmp, self.PACKAGE_ID)


if __name__ == "__main__":
    unittest.main()
