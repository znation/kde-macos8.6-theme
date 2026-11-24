"""Pin every shipped icon's drawing elements in document order.

The folder name and every folder alias share one drawing, so each alias must
stay the same art as the folder at every shipped size.
"""

import os
import unittest

from support.icon.theme_inventory import (
    BLANK_DOCUMENTS,
    FOLDER_ALIASES,
    PACKAGE,
    SHIPPED_ICONS,
    STANDARD_PLACES,
    USER_PLACES_ICONS,
)
from support.svg_case import parse_svg
from svg_assertions import local_name


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


# The blank-document page, one tuple per size, shared by the three blank
# document names. It is the generic document's first three drawing elements
# (the page outline, the white page and the folded corner) without its text
# lines; the page-sharing test below compares it with the shipped generic file.
_BLANK_DOCUMENT_16 = (
    _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
    _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
    _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
)
_BLANK_DOCUMENT_22 = (
    _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
    _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
    _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
)
_BLANK_DOCUMENT_32 = (
    _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
    _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
    _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
)

# Every drawing element of every shipped icon, in document order. The icon art
# is our own, so nothing else re-derives it; the size, palette and structural
# tests in test_icon_theme would all pass if a path's `d`, a rect's geometry,
# an element's order or an element's fill changed -- an icon could silently
# lose its outline, bevel, plate or ribs -- so pin each element exactly. The
# `folder` name owns the pinned folder tuple, and the `inode-directory`,
# `user-home` and `user-desktop` aliases share it at every size (Mac OS 8.6
# draws one folder for a directory); the mapping below and the alias test
# cross-check the files themselves.
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
    os.path.join("32x32", "devices", "drive-removable-media.svg"): (
        _shape("rect", x="3", y="8", width="26", height="17", fill="#000000"),
        _shape("rect", x="4", y="9", width="24", height="15", fill="#DDDDDD"),
        _shape("rect", x="4", y="9", width="24", height="2", fill="#FFFFFF"),
        _shape("rect", x="4", y="9", width="1", height="15", fill="#FFFFFF"),
        _shape("rect", x="4", y="22", width="24", height="2", fill="#999999"),
        _shape("rect", x="27", y="9", width="1", height="15", fill="#999999"),
        _shape("rect", x="7", y="13", width="18", height="2", fill="#000000"),
        _shape("rect", x="7", y="15", width="18", height="1", fill="#FFFFFF"),
        _shape("rect", x="21", y="18", width="4", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "devices", "drive-removable-media.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#DDDDDD"),
        _shape("rect", x="2", y="4", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="4", width="1", height="8", fill="#FFFFFF"),
        _shape("rect", x="2", y="11", width="12", height="1", fill="#999999"),
        _shape("rect", x="13", y="4", width="1", height="8", fill="#999999"),
        _shape("rect", x="4", y="7", width="8", height="1", fill="#000000"),
        _shape("rect", x="4", y="8", width="8", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="10", width="3", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "devices", "drive-removable-media.svg"): (
        _shape("rect", x="2", y="4", width="18", height="15", fill="#000000"),
        _shape("rect", x="3", y="5", width="16", height="13", fill="#DDDDDD"),
        _shape("rect", x="3", y="5", width="16", height="2", fill="#FFFFFF"),
        _shape("rect", x="3", y="5", width="1", height="13", fill="#FFFFFF"),
        _shape("rect", x="3", y="17", width="16", height="1", fill="#999999"),
        _shape("rect", x="18", y="5", width="1", height="13", fill="#999999"),
        _shape("rect", x="5", y="9", width="12", height="2", fill="#000000"),
        _shape("rect", x="5", y="11", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="14", width="4", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "devices", "drive-optical.svg"): (
        _shape("rect", x="3", y="8", width="26", height="17", fill="#000000"),
        _shape("rect", x="4", y="9", width="24", height="15", fill="#DDDDDD"),
        _shape("rect", x="4", y="9", width="24", height="2", fill="#FFFFFF"),
        _shape("rect", x="4", y="9", width="1", height="15", fill="#FFFFFF"),
        _shape("rect", x="4", y="22", width="24", height="2", fill="#999999"),
        _shape("rect", x="27", y="9", width="1", height="15", fill="#999999"),
        _shape("circle", cx="16", cy="16", r="5", fill="#000000"),
        _shape("circle", cx="16", cy="16", r="4", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="2", fill="#000000"),
    ),
    os.path.join("16x16", "devices", "drive-optical.svg"): (
        _shape("rect", x="1", y="2", width="14", height="12", fill="#000000"),
        _shape("rect", x="2", y="3", width="12", height="10", fill="#DDDDDD"),
        _shape("rect", x="2", y="3", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="3", width="1", height="10", fill="#FFFFFF"),
        _shape("rect", x="2", y="12", width="12", height="1", fill="#999999"),
        _shape("rect", x="13", y="3", width="1", height="10", fill="#999999"),
        _shape("circle", cx="8", cy="8", r="3", fill="#000000"),
        _shape("circle", cx="8", cy="8", r="2", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="1", fill="#000000"),
    ),
    os.path.join("22x22", "devices", "drive-optical.svg"): (
        _shape("rect", x="2", y="4", width="18", height="15", fill="#000000"),
        _shape("rect", x="3", y="5", width="16", height="13", fill="#DDDDDD"),
        _shape("rect", x="3", y="5", width="16", height="2", fill="#FFFFFF"),
        _shape("rect", x="3", y="5", width="1", height="13", fill="#FFFFFF"),
        _shape("rect", x="3", y="17", width="16", height="1", fill="#999999"),
        _shape("rect", x="18", y="5", width="1", height="13", fill="#999999"),
        _shape("circle", cx="11", cy="12", r="4", fill="#000000"),
        _shape("circle", cx="11", cy="12", r="3", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="12", r="2", fill="#000000"),
    ),
    os.path.join("32x32", "devices", "media-optical.svg"): (
        _shape("circle", cx="16", cy="16", r="14", fill="#000000"),
        _shape("circle", cx="16", cy="16", r="13", fill="#DDDDDD"),
        _shape("path", d="M16 16 L8 6 L6 8 Z", fill="#FFFFFF"),
        _shape("path", d="M16 16 L24 26 L26 24 Z", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="5", fill="#999999"),
        _shape("circle", cx="16", cy="16", r="4", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="2", fill="#000000"),
    ),
    os.path.join("22x22", "devices", "media-optical.svg"): (
        _shape("circle", cx="11", cy="11", r="10", fill="#000000"),
        _shape("circle", cx="11", cy="11", r="9", fill="#DDDDDD"),
        _shape("path", d="M11 11 L6 4 L4 6 Z", fill="#FFFFFF"),
        _shape("path", d="M11 11 L16 18 L18 16 Z", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="4", fill="#999999"),
        _shape("circle", cx="11", cy="11", r="3", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="1", fill="#000000"),
    ),
    os.path.join("16x16", "devices", "media-optical.svg"): (
        _shape("circle", cx="8", cy="8", r="7", fill="#000000"),
        _shape("circle", cx="8", cy="8", r="6", fill="#DDDDDD"),
        _shape("path", d="M8 8 L5 3 L3 5 Z", fill="#FFFFFF"),
        _shape("path", d="M8 8 L11 13 L13 11 Z", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="3", fill="#999999"),
        _shape("circle", cx="8", cy="8", r="2", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="1", fill="#000000"),
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
    os.path.join("32x32", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="3", y="5", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="6", width="24", height="4", fill="#DDDDDD"),
        _shape("rect", x="4", y="6", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="20", height="1", fill="#999999"),
        _shape("rect", x="4", y="11", width="24", height="15", fill="#FFFFFF"),
        _shape("rect", x="13", y="13", width="2", height="11", fill="#000000"),
        _shape("rect", x="15", y="14", width="2", height="9", fill="#000000"),
        _shape("rect", x="17", y="15", width="2", height="7", fill="#000000"),
        _shape("rect", x="19", y="16", width="2", height="5", fill="#000000"),
        _shape("rect", x="21", y="17", width="2", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="1", y="2", width="14", height="12", fill="#000000"),
        _shape("rect", x="2", y="3", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="2", y="3", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#999999"),
        _shape("rect", x="2", y="7", width="12", height="6", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="2", height="4", fill="#000000"),
        _shape("rect", x="8", y="9", width="2", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="2", y="3", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="4", width="16", height="3", fill="#DDDDDD"),
        _shape("rect", x="3", y="4", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#999999"),
        _shape("rect", x="3", y="8", width="16", height="10", fill="#FFFFFF"),
        _shape("rect", x="9", y="9", width="1", height="8", fill="#000000"),
        _shape("rect", x="10", y="10", width="1", height="6", fill="#000000"),
        _shape("rect", x="11", y="11", width="1", height="4", fill="#000000"),
        _shape("rect", x="12", y="12", width="1", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-shellscript.svg"): (
        _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
        _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
        _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
        _shape("rect", x="10", y="15", width="12", height="7", fill="#000000"),
        _shape("rect", x="12", y="17", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="18", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="12", y="19", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="15", y="19", width="3", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-shellscript.svg"): (
        _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
        _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
        _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
        _shape("rect", x="5", y="6", width="6", height="5", fill="#000000"),
        _shape("rect", x="6", y="7", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="8", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="9", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-shellscript.svg"): (
        _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
        _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
        _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
        _shape("rect", x="7", y="10", width="8", height="5", fill="#000000"),
        _shape("rect", x="8", y="11", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="12", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="13", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "package-x-generic.svg"): (
        _shape("rect", x="3", y="6", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="7", width="24", height="3", fill="#DDDDDD"),
        _shape("rect", x="4", y="7", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="10", width="24", height="17", fill="#FFFFFF"),
        _shape("rect", x="15", y="10", width="2", height="17", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "package-x-generic.svg"): (
        _shape("rect", x="1", y="3", width="14", height="11", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="2", fill="#DDDDDD"),
        _shape("rect", x="2", y="4", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="6", width="12", height="7", fill="#FFFFFF"),
        _shape("rect", x="7", y="6", width="2", height="7", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "package-x-generic.svg"): (
        _shape("rect", x="2", y="4", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="5", width="16", height="2", fill="#DDDDDD"),
        _shape("rect", x="3", y="5", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="3", y="7", width="16", height="12", fill="#FFFFFF"),
        _shape("rect", x="10", y="7", width="2", height="12", fill="#999999"),
    ),
    os.path.join("32x32", "mimetypes", "x-office-document.svg"): (
        _shape("path", d="M6 3 h14 l6 6 v20 H6 Z", fill="#000000"),
        _shape("path", d="M7 4 h12 l6 6 v18 H7 Z", fill="#FFFFFF"),
        _shape("path", d="M19 4 L25 4 L25 10 Z", fill="#DDDDDD"),
        _shape("rect", x="10", y="12", width="12", height="2", fill="#000000"),
        _shape("rect", x="10", y="15", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="8", height="1", fill="#999999"),
        _shape("rect", x="14", y="24", width="8", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "x-office-document.svg"): (
        _shape("path", d="M3 1 h7 l3 3 v10 H3 Z", fill="#000000"),
        _shape("path", d="M4 2 h5 l3 3 v8 H4 Z", fill="#FFFFFF"),
        _shape("path", d="M9 2 L12 2 L12 5 Z", fill="#DDDDDD"),
        _shape("rect", x="5", y="5", width="6", height="1", fill="#000000"),
        _shape("rect", x="5", y="7", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="9", width="6", height="1", fill="#999999"),
        _shape("rect", x="6", y="12", width="4", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "x-office-document.svg"): (
        _shape("path", d="M4 1 h10 l4 4 v15 H4 Z", fill="#000000"),
        _shape("path", d="M5 2 h8 l4 4 v13 H5 Z", fill="#FFFFFF"),
        _shape("path", d="M13 2 L17 2 L17 6 Z", fill="#DDDDDD"),
        _shape("rect", x="7", y="7", width="8", height="2", fill="#000000"),
        _shape("rect", x="7", y="10", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="13", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="16", width="5", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="5", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "text-html.svg"): (
        _shape("rect", x="3", y="5", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="6", width="24", height="4", fill="#DDDDDD"),
        _shape("rect", x="4", y="6", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="20", height="1", fill="#999999"),
        _shape("rect", x="4", y="11", width="24", height="15", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="19", r="6", fill="#000000"),
        _shape("circle", cx="16", cy="19", r="5", fill="#FFFFFF"),
        _shape("rect", x="11", y="19", width="11", height="1", fill="#000000"),
        _shape("rect", x="16", y="14", width="1", height="11", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "text-html.svg"): (
        _shape("rect", x="1", y="2", width="14", height="12", fill="#000000"),
        _shape("rect", x="2", y="3", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="2", y="3", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#999999"),
        _shape("rect", x="2", y="7", width="12", height="6", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="10", r="2", fill="#000000"),
        _shape("circle", cx="8", cy="10", r="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="10", width="5", height="1", fill="#000000"),
        _shape("rect", x="8", y="8", width="1", height="4", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "text-html.svg"): (
        _shape("rect", x="2", y="3", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="4", width="16", height="3", fill="#DDDDDD"),
        _shape("rect", x="3", y="4", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#999999"),
        _shape("rect", x="3", y="8", width="16", height="10", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="13", r="4", fill="#000000"),
        _shape("circle", cx="11", cy="13", r="3", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="7", height="1", fill="#000000"),
        _shape("rect", x="11", y="10", width="1", height="7", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-octet-stream.svg"): _BLANK_DOCUMENT_16,
    os.path.join("16x16", "mimetypes", "application-x-zerosize.svg"): _BLANK_DOCUMENT_16,
    os.path.join("16x16", "mimetypes", "unknown.svg"): _BLANK_DOCUMENT_16,
    os.path.join("22x22", "mimetypes", "application-octet-stream.svg"): _BLANK_DOCUMENT_22,
    os.path.join("22x22", "mimetypes", "application-x-zerosize.svg"): _BLANK_DOCUMENT_22,
    os.path.join("22x22", "mimetypes", "unknown.svg"): _BLANK_DOCUMENT_22,
    os.path.join("32x32", "mimetypes", "application-octet-stream.svg"): _BLANK_DOCUMENT_32,
    os.path.join("32x32", "mimetypes", "application-x-zerosize.svg"): _BLANK_DOCUMENT_32,
    os.path.join("32x32", "mimetypes", "unknown.svg"): _BLANK_DOCUMENT_32,
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

    def test_removable_drive_shares_the_hard_disk_body_and_bevel(self):
        # The removable drive is the hard disk with a slot in place of the
        # label plate, so its first six drawing elements (the outline, face
        # and bevel) must be the hard disk's at every size. Compare the
        # shipped files, not the pinned tuples, so a drift in either file
        # fails here as well as in the pins above.
        for size in ("32x32", "22x22", "16x16"):
            disk = parse_svg(os.path.join(PACKAGE, size, "devices", "drive-harddisk.svg"))
            removable = parse_svg(
                os.path.join(PACKAGE, size, "devices", "drive-removable-media.svg")
            )
            self.assertEqual(
                _drawing_elements(removable)[:6],
                _drawing_elements(disk)[:6],
                size,
            )
        # The optical drive is also the hard disk's body and bevel holding a
        # centred disc, so its first six drawing elements must be the hard
        # disk's at 22x22 and 32x32. At 16x16 the body is two pixels taller
        # than the hard disk's face so the disc fits inside the bevel, and
        # the sharing check holds by exclusion there.
        for size in ("32x32", "22x22"):
            disk = parse_svg(os.path.join(PACKAGE, size, "devices", "drive-harddisk.svg"))
            optical = parse_svg(
                os.path.join(PACKAGE, size, "devices", "drive-optical.svg")
            )
            self.assertEqual(
                _drawing_elements(optical)[:6],
                _drawing_elements(disk)[:6],
                size,
            )

    def test_each_blank_document_shares_the_generic_page(self):
        # The blank-document names draw the generic document's page without
        # its text lines, so at each size each one must equal the first three
        # drawing elements of the shipped `text-x-generic.svg`. Comparing the
        # files catches a path edited in either file and a text line added to
        # a blank document, which would make it four or more elements long.
        for size in ("16x16", "22x22", "32x32"):
            generic = _drawing_elements(
                parse_svg(
                    os.path.join(PACKAGE, size, "mimetypes", "text-x-generic.svg")
                )
            )[:3]
            for name in BLANK_DOCUMENTS:
                with self.subTest(size=size, name=name):
                    drawing = _drawing_elements(
                        parse_svg(
                            os.path.join(PACKAGE, size, "mimetypes", name + ".svg")
                        )
                    )
                    self.assertEqual(drawing, generic)

    def test_office_document_shares_the_generic_page(self):
        # The office document is the generic document's page (its first
        # three drawing elements: the black outline, the white page and the
        # folded corner) with a heading, body lines and a signature line in
        # place of the generic's text lines, so at each size the shipped
        # `x-office-document.svg`'s first three drawing elements must be the
        # shipped `text-x-generic.svg`'s. Compare the files, so a drift in
        # either file fails both.
        for size in ("16x16", "22x22", "32x32"):
            generic = _drawing_elements(
                parse_svg(
                    os.path.join(PACKAGE, size, "mimetypes", "text-x-generic.svg")
                )
            )[:3]
            office = _drawing_elements(
                parse_svg(
                    os.path.join(PACKAGE, size, "mimetypes", "x-office-document.svg")
                )
            )
            self.assertEqual(office[:3], generic, size)

    def test_standard_places_file_names_are_shipped(self):
        # The shared inventory must cover the names the standard places data
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
                self._assert_aliases_share_folder_art(size)

    def _assert_aliases_share_folder_art(self, size):
        """Pin every folder alias's drawing to the folder's at *size*."""
        folder = _drawing_elements(
            parse_svg(os.path.join(PACKAGE, size, "places", "folder.svg"))
        )
        for alias in FOLDER_ALIASES:
            with self.subTest(size=size, alias=alias):
                drawing = _drawing_elements(
                    parse_svg(
                        os.path.join(PACKAGE, size, "places", alias + ".svg")
                    )
                )
                self.assertEqual(drawing, folder)


if __name__ == "__main__":
    unittest.main()
