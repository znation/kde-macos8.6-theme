"""Pins for the media mimetype icons: the multimedia, image and mail files.

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
    _shape,
)

PINS = {

    os.path.join("32x32", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="3", y="7", width="26", height="20", fill="#000000"),
        _shape("rect", x="4", y="8", width="24", height="18", fill="#FFFFFF"),
        _shape("path", d="M13 11 L23 17 L13 23 Z", fill="#000000"),
        _shape("rect", x="12", y="27", width="8", height="2", fill="#000000"),
        _shape("rect", x="8", y="29", width="16", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#FFFFFF"),
        _shape("path", d="M7 6 L10 8 L7 10 Z", fill="#000000"),
        _shape("rect", x="6", y="13", width="4", height="1", fill="#000000"),
        _shape("rect", x="4", y="14", width="8", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="2", y="5", width="18", height="13", fill="#000000"),
        _shape("rect", x="3", y="6", width="16", height="11", fill="#FFFFFF"),
        _shape("path", d="M9 8 L15 11 L9 14 Z", fill="#000000"),
        _shape("rect", x="8", y="19", width="6", height="1", fill="#000000"),
        _shape("rect", x="5", y="20", width="12", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-ogg.svg"): (
        *_PAGE_32,
        _shape("rect", x="9", y="14", width="14", height="8", fill="#000000"),
        _shape("rect", x="10", y="15", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="15", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="16", y="15", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="19", y="15", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="17", width="10", height="2", fill="#FFFFFF"),
        _shape("rect", x="10", y="20", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="20", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="16", y="20", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="19", y="20", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-ogg.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="6", fill="#000000"),
        _shape("rect", x="6", y="7", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="7", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="4", height="2", fill="#FFFFFF"),
        _shape("rect", x="6", y="10", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="10", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-ogg.svg"): (
        *_PAGE_22,
        _shape("rect", x="6", y="10", width="10", height="8", fill="#000000"),
        _shape("rect", x="7", y="11", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="10", y="11", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="11", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="6", height="2", fill="#FFFFFF"),
        _shape("rect", x="7", y="16", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="10", y="16", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="16", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="6", y="23", width="7", height="4", fill="#000000"),
        _shape("rect", x="11", y="6", width="2", height="21", fill="#000000"),
        _shape("rect", x="18", y="21", width="7", height="4", fill="#000000"),
        _shape("rect", x="23", y="6", width="2", height="19", fill="#000000"),
        _shape("rect", x="11", y="6", width="14", height="5", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="4", y="16", width="5", height="3", fill="#000000"),
        _shape("rect", x="8", y="4", width="2", height="15", fill="#000000"),
        _shape("rect", x="12", y="14", width="5", height="3", fill="#000000"),
        _shape("rect", x="15", y="4", width="2", height="13", fill="#000000"),
        _shape("rect", x="8", y="4", width="9", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="2", y="11", width="4", height="2", fill="#000000"),
        _shape("rect", x="5", y="3", width="1", height="10", fill="#000000"),
        _shape("rect", x="9", y="10", width="4", height="2", fill="#000000"),
        _shape("rect", x="12", y="3", width="1", height="9", fill="#000000"),
        _shape("rect", x="5", y="3", width="8", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "audio-ogg.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="18", width="2", height="5", fill="#000000"),
        _shape("rect", x="13", y="15", width="2", height="8", fill="#000000"),
        _shape("rect", x="16", y="12", width="2", height="11", fill="#000000"),
        _shape("rect", x="19", y="16", width="2", height="7", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "audio-ogg.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="8", width="1", height="3", fill="#000000"),
        _shape("rect", x="7", y="7", width="1", height="4", fill="#000000"),
        _shape("rect", x="9", y="6", width="1", height="5", fill="#000000"),
        _shape("rect", x="11", y="9", width="1", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "audio-ogg.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="13", width="1", height="4", fill="#000000"),
        _shape("rect", x="9", y="11", width="1", height="6", fill="#000000"),
        _shape("rect", x="11", y="9", width="1", height="8", fill="#000000"),
        _shape("rect", x="13", y="12", width="1", height="5", fill="#000000"),
    ),
    # The FLAC audio item icon KDE draws for `audio/flac` items (the
    # type-spelled icon name of the installed shared MIME database's
    # `audio/flac` type, which has no `icon`, `generic-icon` or
    # `sub-class-of` element, one alias and a single `*.flac` glob, so
    # one file covers exactly its own name); the drawing shares the
    # generic document's page and holds a waveform-pulse ribbon (an
    # EKG-style connected zigzag mark distinct from the four disjoint
    # equalizer bars `audio-ogg.svg` draws on the same page and the
    # beamed note pair `audio-x-generic.svg` draws).
    os.path.join("32x32", "mimetypes", "audio-flac.svg"): (
        *_PAGE_32,
        _shape("polygon", points="9,21 12,21 14,15 15,15 17,25 20,21 23,21 23,23 20,23 17,27 15,17 14,17 12,23 9,23", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "audio-flac.svg"): (
        *_PAGE_16,
        _shape("polygon", points="5,9 6,9 7,6 8,6 9,10 10,8 11,8 11,10 10,10 9,12 8,8 7,8 6,11 5,11", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "audio-flac.svg"): (
        *_PAGE_22,
        _shape("polygon", points="7,15 9,15 10,11 11,11 12,18 14,15 16,15 16,17 14,17 12,20 11,13 10,13 9,17 7,17", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="2", y="6", width="28", height="20", fill="#000000"),
        _shape("rect", x="3", y="7", width="26", height="18", fill="#DDDDDD"),
        _shape("path", d="M3 7 L16 17 L29 7 Z", fill="#000000"),
        _shape("path", d="M4 8 L16 16 L28 8 Z", fill="#DDDDDD"),
    ),
    os.path.join("16x16", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#DDDDDD"),
        _shape("path", d="M2 4 L8 9 L14 4 Z", fill="#000000"),
        _shape("path", d="M3 5 L8 8 L13 5 Z", fill="#DDDDDD"),
    ),
    os.path.join("22x22", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="1", y="4", width="20", height="14", fill="#000000"),
        _shape("rect", x="2", y="5", width="18", height="12", fill="#DDDDDD"),
        _shape("path", d="M2 5 L11 12 L20 5 Z", fill="#000000"),
        _shape("path", d="M3 6 L11 11 L19 6 Z", fill="#DDDDDD"),
    ),
    os.path.join("32x32", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="3", y="3", width="26", height="26", fill="#000000"),
        _shape("rect", x="4", y="4", width="24", height="24", fill="#DDDDDD"),
        _shape("rect", x="6", y="6", width="20", height="20", fill="#FFFFFF"),
        _shape("rect", x="21", y="9", width="3", height="3", fill="#999999"),
        _shape("rect", x="6", y="18", width="4", height="3", fill="#999999"),
        _shape("rect", x="10", y="16", width="4", height="5", fill="#999999"),
        _shape("rect", x="14", y="14", width="4", height="7", fill="#999999"),
        _shape("rect", x="18", y="16", width="4", height="5", fill="#999999"),
        _shape("rect", x="22", y="18", width="4", height="3", fill="#999999"),
        _shape("rect", x="6", y="21", width="20", height="5", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="1", y="1", width="14", height="14", fill="#000000"),
        _shape("rect", x="2", y="2", width="12", height="12", fill="#DDDDDD"),
        _shape("rect", x="3", y="3", width="10", height="10", fill="#FFFFFF"),
        _shape("rect", x="10", y="4", width="2", height="2", fill="#999999"),
        _shape("rect", x="3", y="8", width="2", height="2", fill="#999999"),
        _shape("rect", x="5", y="7", width="2", height="3", fill="#999999"),
        _shape("rect", x="7", y="6", width="2", height="4", fill="#999999"),
        _shape("rect", x="9", y="8", width="2", height="2", fill="#999999"),
        _shape("rect", x="3", y="10", width="10", height="3", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="2", y="2", width="18", height="18", fill="#000000"),
        _shape("rect", x="3", y="3", width="16", height="16", fill="#DDDDDD"),
        _shape("rect", x="4", y="4", width="14", height="14", fill="#FFFFFF"),
        _shape("rect", x="15", y="6", width="2", height="2", fill="#999999"),
        _shape("rect", x="4", y="12", width="3", height="2", fill="#999999"),
        _shape("rect", x="7", y="10", width="3", height="4", fill="#999999"),
        _shape("rect", x="10", y="9", width="3", height="5", fill="#999999"),
        _shape("rect", x="13", y="11", width="3", height="3", fill="#999999"),
        _shape("rect", x="4", y="14", width="14", height="4", fill="#999999"),
    ),
}
