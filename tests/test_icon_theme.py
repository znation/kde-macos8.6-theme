"""Validate the org.macos8.desktop icon theme package.

The package ships our own final Platinum-style art for the icons a default Mac
OS 8.6 desktop shows; these tests pin the theme's identity, the per-size SVG
shape and Platinum palette of every icon, the placeholder register (empty now
that the art is final), and the install/uninstall lifecycle.
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
from support.installed_paths import installed_icon_theme, installed_icons_dir
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo
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
# directory to plus the `user-home` and `user-desktop` places, all drawing
# the folder art, 16x16 and 22x22 renditions of the folder, aliases, Trash
# and full Trash, 16x16 and 22x22 renditions of the hard disk and document,
# the kicker logo the menu bar's top-left button shows at the two panel sizes,
# and the `go-next-symbolic` submenu arrow the reference's open Apple menu
# draws.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("16x16", "devices", "drive-harddisk.svg"),
    os.path.join("22x22", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "text-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-home.svg"),
    os.path.join("32x32", "places", "user-desktop.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
    os.path.join("32x32", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "folder.svg"),
    os.path.join("16x16", "places", "inode-directory.svg"),
    os.path.join("16x16", "places", "user-home.svg"),
    os.path.join("16x16", "places", "user-desktop.svg"),
    os.path.join("16x16", "places", "user-trash.svg"),
    os.path.join("16x16", "places", "user-trash-full.svg"),
    os.path.join("22x22", "places", "folder.svg"),
    os.path.join("22x22", "places", "inode-directory.svg"),
    os.path.join("22x22", "places", "user-home.svg"),
    os.path.join("22x22", "places", "user-desktop.svg"),
    os.path.join("22x22", "places", "user-trash.svg"),
    os.path.join("22x22", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"),
    os.path.join("16x16", "actions", "go-next-symbolic.svg"),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"),
)

# The standard XDG folder places KDE resolves; the package draws each one
# with the matching size's Platinum folder, as Mac OS 8.6 draws one folder
# shape for a directory. KIO's places model names these eight names
# (read from `libKF6KIOCore.so.6`), while the standard `user-places.xbel`
# entries spell Downloads with the plural `folder-downloads` (the installed
# file's Downloads bookmark, line 58), so ship both download names.
STANDARD_PLACES = (
    "folder-documents",
    "folder-download",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
    "folder-templates",
    "folder-public",
    "folder-temp",
)
SHIPPED_ICONS += tuple(
    os.path.join(size, "places", place + ".svg")
    for size in ("16x16", "22x22", "32x32")
    for place in STANDARD_PLACES
)

# The standard places data's folder names that this package draws. KDE
# writes these into a user's Places list, and its Downloads entry is the
# plural `folder-downloads` rather than the `folder-download` the KIO places
# model also names; pin them separately so the inventory cannot pass by
# dropping a name KDE actually resolves.
USER_PLACES_ICONS = (
    "folder-documents",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
)

# The names that share the folder art: the KDE directory alias, the Home and
# Desktop places, and every standard XDG place.
FOLDER_ALIASES = ("inode-directory", "user-home", "user-desktop", *STANDARD_PLACES)

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
        "size_ver",
        "n-resize",
        "ns-resize",
        "s-resize",
        "sb_v_double_arrow",
        "v_double_arrow",
        "00008160000006810000408080010102",
        "row-resize",
        "split_v",
        "size_fdiag",
        "nw-resize",
        "se-resize",
        "nwse-resize",
        "size_bdiag",
        "ne-resize",
        "sw-resize",
        "nesw-resize",
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
        self.assertEqual(
            shipped,
            {"index.theme", *SHIPPED_ICONS, *SHIPPED_CURSORS},
        )

    def test_placeholder_register_matches_the_icon_art(self):
        # Every shipped icon is final art, so neither side lists one: the
        # register's rows for these icons and the icons carrying a
        # `PLACEHOLDER:` marker are both empty and must stay equal.
        register = _read_icon_text(PLACEHOLDERS)
        registered = {icon for icon in SHIPPED_ICONS if _icon_path(icon) in register}
        marked = set()
        for icon in SHIPPED_ICONS:
            if "PLACEHOLDER:" in _read_icon_text(os.path.join(PACKAGE, icon)):
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
# outline, bevel, plate or ribs -- so pin each element exactly. The `folder`
# name owns the pinned folder tuple, and the `inode-directory`, `user-home`
# and `user-desktop` aliases share it at every size (Mac OS 8.6 draws one
# folder for a directory); the mapping below and the alias test cross-check
# the files themselves.
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
    os.path.join("16x16", "devices", "drive-harddisk.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#DDDDDD"),
        _shape("rect", x="2", y="4", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="4", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="2", y="11", width="12", height="1", fill="#999999"),
        _shape("rect", x="13", y="4", width="1", height="8", fill="#999999"),
        _shape("rect", x="3", y="7", width="7", height="3", fill="#000000"),
        _shape("rect", x="4", y="8", width="5", height="1", fill="#FFFFFF"),
        _shape("circle", cx="12", cy="9", r="1", fill="#000000"),
    ),
    os.path.join("22x22", "devices", "drive-harddisk.svg"): (
        _shape("rect", x="2", y="4", width="18", height="15", fill="#000000"),
        _shape("rect", x="3", y="5", width="16", height="13", fill="#DDDDDD"),
        _shape("rect", x="3", y="5", width="16", height="2", fill="#FFFFFF"),
        _shape("rect", x="3", y="5", width="1", height="13", fill="#FFFFFF"),
        _shape("rect", x="3", y="17", width="16", height="1", fill="#999999"),
        _shape("rect", x="18", y="5", width="1", height="13", fill="#999999"),
        _shape("rect", x="4", y="10", width="8", height="4", fill="#000000"),
        _shape("rect", x="5", y="11", width="6", height="2", fill="#FFFFFF"),
        _shape("circle", cx="15", cy="12", r="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"): (
        _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
        _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
        _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
        _shape("rect", x="10", y="15", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="8", height="1", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "text-x-generic.svg"): (
        _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
        _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
        _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
        _shape("rect", x="5", y="7", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="9", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="11", width="4", height="1", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "text-x-generic.svg"): (
        _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
        _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
        _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
        _shape("rect", x="7", y="10", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="13", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="16", width="5", height="1", fill="#999999"),
    ),
    os.path.join("32x32", "places", "folder.svg"): (
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
    os.path.join("16x16", "places", "folder.svg"): (
        _shape("path", d="M1 4 h5 l2 2 h6 v7 H1 Z", fill="#000000"),
        _shape("path", d="M2 5 h4 l2 2 h5 v4 H2 Z", fill="#DDDDDD"),
        _shape("path", d="M2 5 h4 l2 2 h5 v1 h-5 l-2 -2 h-4 Z", fill="#FFFFFF"),
        _shape("rect", x="2", y="5", width="1", height="6", fill="#FFFFFF"),
        _shape("rect", x="2", y="11", width="11", height="1", fill="#999999"),
        _shape("rect", x="12", y="8", width="1", height="3", fill="#999999"),
    ),
    os.path.join("16x16", "places", "user-trash.svg"): (
        _shape("rect", x="6", y="1", width="4", height="2", fill="#000000"),
        _shape("rect", x="7", y="2", width="2", height="1", fill="#DDDDDD"),
        _shape("rect", x="3", y="3", width="10", height="3", fill="#000000"),
        _shape("rect", x="4", y="4", width="8", height="2", fill="#DDDDDD"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="5", width="8", height="1", fill="#999999"),
        _shape("path", d="M5 6 h6 l-1 9 H6 Z", fill="#000000"),
        _shape("path", d="M6 7 h4 l-1 7 H7 Z", fill="#DDDDDD"),
        _shape("rect", x="7", y="8", width="1", height="5", fill="#999999"),
        _shape("rect", x="8", y="8", width="1", height="5", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "places", "user-trash-full.svg"): (
        _shape("path", d="M6 0 l2 1 l2 -1 l1 4 h-6 Z", fill="#000000"),
        _shape("path", d="M7 1 l1 1 l1 -1 l1 3 h-4 Z", fill="#FFFFFF"),
        _shape("rect", x="3", y="3", width="10", height="3", fill="#000000"),
        _shape("rect", x="4", y="4", width="8", height="2", fill="#DDDDDD"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="5", width="8", height="1", fill="#999999"),
        _shape("path", d="M5 6 h6 l-1 9 H6 Z", fill="#000000"),
        _shape("path", d="M6 7 h4 l-1 7 H7 Z", fill="#DDDDDD"),
        _shape("rect", x="7", y="8", width="1", height="5", fill="#999999"),
        _shape("rect", x="8", y="8", width="1", height="5", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "places", "folder.svg"): (
        _shape("path", d="M2 6 h7 l3 3 h8 v8 H2 Z", fill="#000000"),
        _shape("path", d="M3 7 h6 l3 3 h7 v6 H3 Z", fill="#DDDDDD"),
        _shape("path", d="M3 7 h6 l3 3 h7 v1 h-7 l-3 -3 h-6 Z", fill="#FFFFFF"),
        _shape("rect", x="3", y="7", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="3", y="15", width="16", height="1", fill="#999999"),
        _shape("rect", x="18", y="10", width="1", height="5", fill="#999999"),
    ),
    os.path.join("22x22", "places", "user-trash.svg"): (
        _shape("rect", x="8", y="1", width="6", height="3", fill="#000000"),
        _shape("rect", x="9", y="2", width="4", height="2", fill="#DDDDDD"),
        _shape("rect", x="4", y="4", width="14", height="4", fill="#000000"),
        _shape("rect", x="5", y="5", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="12", height="1", fill="#999999"),
        _shape("path", d="M6 8 h10 l-1 12 H7 Z", fill="#000000"),
        _shape("path", d="M7 9 h8 l-1 10 H8 Z", fill="#DDDDDD"),
        _shape("rect", x="9", y="11", width="1", height="8", fill="#999999"),
        _shape("rect", x="10", y="11", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="12", y="11", width="1", height="8", fill="#999999"),
        _shape("rect", x="13", y="11", width="1", height="8", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "places", "user-trash-full.svg"): (
        _shape("path", d="M8 0 l3 2 l3 -2 l1 6 h-8 Z", fill="#000000"),
        _shape("path", d="M9 1 l2 1 l2 -1 l1 4 h-6 Z", fill="#FFFFFF"),
        _shape("rect", x="4", y="4", width="14", height="4", fill="#000000"),
        _shape("rect", x="5", y="5", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="12", height="1", fill="#999999"),
        _shape("path", d="M6 8 h10 l-1 12 H7 Z", fill="#000000"),
        _shape("path", d="M7 9 h8 l-1 10 H8 Z", fill="#DDDDDD"),
        _shape("rect", x="9", y="11", width="1", height="8", fill="#999999"),
        _shape("rect", x="10", y="11", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="12", y="11", width="1", height="8", fill="#999999"),
        _shape("rect", x="13", y="11", width="1", height="8", fill="#FFFFFF"),
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

# KDE resolves a directory to `inode-directory`, names the Home and Desktop
# places `user-home` and `user-desktop`, and names the standard XDG places
# (Documents, Downloads, Music, ...) after `STANDARD_PLACES`; Mac OS 8.6
# draws one folder shape for all of them, so each alias shares its size's
# folder tuple.
for _size in ("16x16", "22x22", "32x32"):
    _folder = ICON_SHAPES[os.path.join(_size, "places", "folder.svg")]
    for _alias in FOLDER_ALIASES:
        ICON_SHAPES[os.path.join(_size, "places", _alias + ".svg")] = _folder


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

    def test_standard_places_file_names_are_shipped(self):
        # The inventory above must cover the names the standard places data
        # writes, not just the names KIO's model happens to list. In
        # particular Downloads is `folder-downloads` (plural) in the
        # standard `user-places.xbel` entries, so that shared-folder alias
        # has to be present at every size.
        for name in USER_PLACES_ICONS:
            with self.subTest(name=name):
                self.assertIn(name, STANDARD_PLACES)
                for size in ("16x16", "22x22", "32x32"):
                    self.assertIn(
                        os.path.join(size, "places", name + ".svg"),
                        SHIPPED_ICONS,
                    )

    def test_every_place_alias_shares_the_folder_art(self):
        # Mac OS 8.6 draws one folder shape for the `folder` name and every
        # place alias (`inode-directory`, `user-home`, `user-desktop` and the
        # standard XDG places), so each alias must stay the same drawing at
        # every shipped size; pinning only each one's own elements would let
        # them drift apart.
        for size in ("16x16", "22x22", "32x32"):
            with self.subTest(size=size):
                folder = _drawing_elements(
                    parse_svg(os.path.join(PACKAGE, size, "places", "folder.svg"))
                )
                for alias in FOLDER_ALIASES:
                    with self.subTest(size=size, alias=alias):
                        drawing = _drawing_elements(
                            parse_svg(
                                os.path.join(
                                    PACKAGE, size, "places", alias + ".svg"
                                )
                            )
                        )
                        self.assertEqual(drawing, folder)


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
