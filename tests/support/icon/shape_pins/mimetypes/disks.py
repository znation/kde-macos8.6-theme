"""Pins for the disks mimetype icons: the disk image, database and shared-library files.

Every entry is a ``os.path.join(size, "mimetypes", name.svg)`` key
holding the pinned tuple of drawing elements for that shipped file, in
document order. This module is one group of the mimetypes family's
registry; the geometry tests in ``test_icon_theme_geometry`` compare
each shipped SVG with its tuple.
"""

import os

from support.icon.shape_pins._shared import (
    _PAGE_16,
    _PAGE_22,
    _PAGE_32,
    _PROGRAM_WINDOW_16,
    _PROGRAM_WINDOW_22,
    _PROGRAM_WINDOW_32,
    _shape,
)

PINS = {

    os.path.join("32x32", "mimetypes", "application-x-sharedlib.svg"): (
        *_PROGRAM_WINDOW_32,
        _shape("rect", x="8", y="14", width="16", height="3", fill="#000000"),
        _shape("rect", x="8", y="19", width="16", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-sharedlib.svg"): (
        *_PROGRAM_WINDOW_16,
        _shape("rect", x="4", y="8", width="8", height="2", fill="#000000"),
        _shape("rect", x="4", y="11", width="8", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-sharedlib.svg"): (
        *_PROGRAM_WINDOW_22,
        _shape("rect", x="6", y="10", width="10", height="2", fill="#000000"),
        _shape("rect", x="6", y="14", width="10", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-vnd.sqlite3.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="15", width="12", height="7", fill="#000000"),
        _shape("rect", x="11", y="15", width="10", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="16", width="1", height="5", fill="#FFFFFF"),
        _shape("rect", x="20", y="16", width="1", height="5", fill="#FFFFFF"),
        _shape("rect", x="12", y="18", width="8", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="21", width="10", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-vnd.sqlite3.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="5", fill="#000000"),
        _shape("rect", x="5", y="6", width="6", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="10", y="7", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="4", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="10", width="6", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-vnd.sqlite3.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="10", width="8", height="5", fill="#000000"),
        _shape("rect", x="8", y="10", width="6", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="11", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="13", y="11", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="9", y="12", width="4", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="14", width="6", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="16", cy="16", r="14", fill="#000000"),
        _shape("circle", cx="16", cy="16", r="13", fill="#DDDDDD"),
        _shape("path", d="M16 16 L8 6 L6 8 Z", fill="#FFFFFF"),
        _shape("path", d="M16 16 L24 26 L26 24 Z", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="5", fill="#999999"),
        _shape("circle", cx="16", cy="16", r="4", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="2", fill="#000000"),
        _shape("rect", x="22", y="10", width="6", height="2", fill="#000000"),
        _shape("rect", x="25", y="12", width="2", height="6", fill="#000000"),
        _shape("rect", x="22", y="18", width="6", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="8", cy="8", r="7", fill="#000000"),
        _shape("circle", cx="8", cy="8", r="6", fill="#DDDDDD"),
        _shape("path", d="M8 8 L5 3 L3 5 Z", fill="#FFFFFF"),
        _shape("path", d="M8 8 L11 13 L13 11 Z", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="3", fill="#999999"),
        _shape("circle", cx="8", cy="8", r="2", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="1", fill="#000000"),
        _shape("rect", x="11", y="5", width="3", height="2", fill="#000000"),
        _shape("rect", x="12", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="11", y="8", width="3", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="11", cy="11", r="10", fill="#000000"),
        _shape("circle", cx="11", cy="11", r="9", fill="#DDDDDD"),
        _shape("path", d="M11 11 L6 4 L4 6 Z", fill="#FFFFFF"),
        _shape("path", d="M11 11 L16 18 L18 16 Z", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="4", fill="#999999"),
        _shape("circle", cx="11", cy="11", r="3", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="1", fill="#000000"),
        _shape("rect", x="15", y="7", width="4", height="2", fill="#000000"),
        _shape("rect", x="16", y="9", width="2", height="3", fill="#000000"),
        _shape("rect", x="15", y="12", width="4", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-qemu-disk.svg"): (
        _shape("circle", cx="16", cy="16", r="14", fill="#000000"),
        _shape("circle", cx="16", cy="16", r="13", fill="#DDDDDD"),
        _shape("circle", cx="13", cy="13", r="5", fill="#FFFFFF"),
        _shape("circle", cx="13", cy="13", r="3", fill="#DDDDDD"),
        _shape("rect", x="16", y="16", width="2", height="2", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-qemu-disk.svg"): (
        _shape("circle", cx="8", cy="8", r="7", fill="#000000"),
        _shape("circle", cx="8", cy="8", r="6", fill="#DDDDDD"),
        _shape("circle", cx="7", cy="7", r="3", fill="#FFFFFF"),
        _shape("circle", cx="7", cy="7", r="1", fill="#DDDDDD"),
        _shape("rect", x="8", y="9", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-qemu-disk.svg"): (
        _shape("circle", cx="11", cy="11", r="10", fill="#000000"),
        _shape("circle", cx="11", cy="11", r="9", fill="#DDDDDD"),
        _shape("circle", cx="9", cy="9", r="4", fill="#FFFFFF"),
        _shape("circle", cx="9", cy="9", r="2", fill="#DDDDDD"),
        _shape("rect", x="11", y="12", width="1", height="2", fill="#FFFFFF"),
    ),
}
