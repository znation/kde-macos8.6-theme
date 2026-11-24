"""Pins for the executables mimetype icons: the scripts, executables and zero-data files.

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

    os.path.join("32x32", "mimetypes", "application-x-executable.svg"): (
        *_PROGRAM_WINDOW_32,
        _shape("rect", x="13", y="13", width="2", height="11", fill="#000000"),
        _shape("rect", x="15", y="14", width="2", height="9", fill="#000000"),
        _shape("rect", x="17", y="15", width="2", height="7", fill="#000000"),
        _shape("rect", x="19", y="16", width="2", height="5", fill="#000000"),
        _shape("rect", x="21", y="17", width="2", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-executable.svg"): (
        *_PROGRAM_WINDOW_16,
        _shape("rect", x="6", y="8", width="2", height="4", fill="#000000"),
        _shape("rect", x="8", y="9", width="2", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-executable.svg"): (
        *_PROGRAM_WINDOW_22,
        _shape("rect", x="9", y="9", width="1", height="8", fill="#000000"),
        _shape("rect", x="10", y="10", width="1", height="6", fill="#000000"),
        _shape("rect", x="11", y="11", width="1", height="4", fill="#000000"),
        _shape("rect", x="12", y="12", width="1", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-python-bytecode.svg"): (
        *_PROGRAM_WINDOW_32,
        _shape("rect", x="10", y="15", width="13", height="7", fill="#000000"),
        _shape("rect", x="12", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="16", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="20", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="22", width="1", height="1", fill="#000000"),
        _shape("rect", x="16", y="22", width="1", height="1", fill="#000000"),
        _shape("rect", x="20", y="22", width="1", height="1", fill="#000000"),
        _shape("rect", x="16", y="18", width="2", height="2", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-python-bytecode.svg"): (
        *_PROGRAM_WINDOW_16,
        _shape("rect", x="5", y="8", width="7", height="4", fill="#000000"),
        _shape("rect", x="6", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="9", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-python-bytecode.svg"): (
        *_PROGRAM_WINDOW_22,
        _shape("rect", x="6", y="10", width="9", height="5", fill="#000000"),
        _shape("rect", x="7", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="15", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="15", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="15", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="12", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-trash.svg"): (
        *_PROGRAM_WINDOW_32,
        _shape("rect", x="7", y="17", width="6", height="1", fill="#000000"),
        _shape("rect", x="13", y="18", width="8", height="1", fill="#000000"),
        _shape("rect", x="21", y="17", width="6", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-trash.svg"): (
        *_PROGRAM_WINDOW_16,
        _shape("rect", x="3", y="9", width="3", height="1", fill="#000000"),
        _shape("rect", x="6", y="10", width="4", height="1", fill="#000000"),
        _shape("rect", x="10", y="9", width="3", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-trash.svg"): (
        *_PROGRAM_WINDOW_22,
        _shape("rect", x="4", y="11", width="4", height="1", fill="#000000"),
        _shape("rect", x="8", y="12", width="6", height="1", fill="#000000"),
        _shape("rect", x="14", y="11", width="4", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="15", width="12", height="7", fill="#000000"),
        _shape("rect", x="12", y="17", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="18", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="12", y="19", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="15", y="19", width="3", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="5", fill="#000000"),
        _shape("rect", x="6", y="7", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="8", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="9", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="10", width="8", height="5", fill="#000000"),
        _shape("rect", x="8", y="11", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="12", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="13", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-core.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="15", width="12", height="7", fill="#000000"),
        _shape("rect", x="11", y="16", width="10", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="17", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="20", y="17", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="11", y="20", width="10", height="1", fill="#FFFFFF"),
        _shape("rect", x="15", y="18", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-core.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="5", fill="#000000"),
        _shape("rect", x="6", y="7", width="4", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="8", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="9", width="4", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-core.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="10", width="8", height="5", fill="#000000"),
        _shape("rect", x="8", y="11", width="6", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="12", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="12", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="6", height="1", fill="#FFFFFF"),
        _shape("rect", x="10", y="12", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-perl.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="11", width="2", height="13", fill="#000000"),
        _shape("rect", x="12", y="11", width="5", height="1", fill="#000000"),
        _shape("rect", x="16", y="12", width="1", height="5", fill="#000000"),
        _shape("rect", x="12", y="16", width="5", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-perl.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="1", height="6", fill="#000000"),
        _shape("rect", x="6", y="6", width="3", height="1", fill="#000000"),
        _shape("rect", x="8", y="7", width="1", height="2", fill="#000000"),
        _shape("rect", x="6", y="8", width="3", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-perl.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="8", width="2", height="9", fill="#000000"),
        _shape("rect", x="9", y="8", width="4", height="1", fill="#000000"),
        _shape("rect", x="12", y="9", width="1", height="3", fill="#000000"),
        _shape("rect", x="9", y="11", width="4", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-octet-stream.svg"): _PAGE_16,
    os.path.join("16x16", "mimetypes", "application-x-zerosize.svg"): _PAGE_16,
    os.path.join("16x16", "mimetypes", "unknown.svg"): _PAGE_16,
    os.path.join("22x22", "mimetypes", "application-octet-stream.svg"): _PAGE_22,
    os.path.join("22x22", "mimetypes", "application-x-zerosize.svg"): _PAGE_22,
    os.path.join("22x22", "mimetypes", "unknown.svg"): _PAGE_22,
    os.path.join("32x32", "mimetypes", "application-octet-stream.svg"): _PAGE_32,
    os.path.join("32x32", "mimetypes", "application-x-zerosize.svg"): _PAGE_32,
    os.path.join("32x32", "mimetypes", "unknown.svg"): _PAGE_32,
}
