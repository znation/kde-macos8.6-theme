"""Pins for the places family: folders, trash cans, the network server
and the symbolic start-here icon.

Every entry is a ``os.path.join(size, "places", name.svg)`` key holding
the pinned tuple of drawing elements for that shipped file, in document
order. The pins live beside ``theme_inventory``; the geometry tests in
``test_icon_theme_geometry`` compare each shipped SVG with its tuple.
"""

import os

from support.icon.shape_pins._shared import (
    _TRASH_BODY_16,
    _TRASH_BODY_22,
    _TRASH_BODY_32,
    _shape,
)
from support.icon.theme_inventory import FOLDER_ALIASES

PINS = {
    os.path.join("32x32", "places", "network-server.svg"): (
        _shape("rect", x="8", y="4", width="16", height="24", fill="#000000"),
        _shape("rect", x="9", y="5", width="14", height="22", fill="#DDDDDD"),
        _shape("rect", x="9", y="5", width="14", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="5", width="1", height="22", fill="#FFFFFF"),
        _shape("rect", x="22", y="5", width="1", height="22", fill="#999999"),
        _shape("rect", x="9", y="26", width="14", height="1", fill="#999999"),
        _shape("rect", x="11", y="9", width="10", height="3", fill="#000000"),
        _shape("rect", x="11", y="15", width="10", height="3", fill="#000000"),
        _shape("rect", x="11", y="21", width="2", height="2", fill="#999999"),
    ),
    os.path.join("16x16", "places", "network-server.svg"): (
        _shape("rect", x="4", y="1", width="8", height="14", fill="#000000"),
        _shape("rect", x="5", y="2", width="6", height="12", fill="#DDDDDD"),
        _shape("rect", x="5", y="2", width="6", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="2", width="1", height="12", fill="#FFFFFF"),
        _shape("rect", x="10", y="2", width="1", height="12", fill="#999999"),
        _shape("rect", x="5", y="13", width="6", height="1", fill="#999999"),
        _shape("rect", x="6", y="5", width="4", height="2", fill="#000000"),
        _shape("rect", x="6", y="9", width="4", height="2", fill="#000000"),
        _shape("rect", x="6", y="11", width="1", height="1", fill="#999999"),
    ),
    os.path.join("22x22", "places", "network-server.svg"): (
        _shape("rect", x="5", y="2", width="12", height="18", fill="#000000"),
        _shape("rect", x="6", y="3", width="10", height="16", fill="#DDDDDD"),
        _shape("rect", x="6", y="3", width="10", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="3", width="1", height="16", fill="#FFFFFF"),
        _shape("rect", x="15", y="3", width="1", height="16", fill="#999999"),
        _shape("rect", x="6", y="18", width="10", height="1", fill="#999999"),
        _shape("rect", x="7", y="7", width="8", height="2", fill="#000000"),
        _shape("rect", x="7", y="12", width="8", height="2", fill="#000000"),
        _shape("rect", x="7", y="15", width="2", height="2", fill="#999999"),
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
        *_TRASH_BODY_32,
    ),
    os.path.join("32x32", "places", "user-trash-full.svg"): (
        _shape("path", d="M12 2 l3 2 l3 -2 l1 7 h-8 Z", fill="#000000"),
        _shape("path", d="M13 3 l2 1 l2 -1 l1 5 h-6 Z", fill="#FFFFFF"),
        *_TRASH_BODY_32,
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
        *_TRASH_BODY_16,
    ),
    os.path.join("16x16", "places", "user-trash-full.svg"): (
        _shape("path", d="M6 0 l2 1 l2 -1 l1 4 h-6 Z", fill="#000000"),
        _shape("path", d="M7 1 l1 1 l1 -1 l1 3 h-4 Z", fill="#FFFFFF"),
        *_TRASH_BODY_16,
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
        *_TRASH_BODY_22,
    ),
    os.path.join("22x22", "places", "user-trash-full.svg"): (
        _shape("path", d="M8 0 l3 2 l3 -2 l1 6 h-8 Z", fill="#000000"),
        _shape("path", d="M9 1 l2 1 l2 -1 l1 4 h-6 Z", fill="#FFFFFF"),
        *_TRASH_BODY_22,
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
}

# KDE resolves a directory to `inode-directory`, names the Home and Desktop
# places `user-home` and `user-desktop`, and names the standard XDG places
# (Documents, Downloads, Music, ...) after `STANDARD_PLACES`; Mac OS 8.6
# draws one folder shape for all of them, so each alias shares its size's
# folder tuple.
for _size in ("16x16", "22x22", "32x32"):
    _folder = PINS[os.path.join(_size, "places", "folder.svg")]
    for _alias in FOLDER_ALIASES:
        PINS[os.path.join(_size, "places", _alias + ".svg")] = _folder
