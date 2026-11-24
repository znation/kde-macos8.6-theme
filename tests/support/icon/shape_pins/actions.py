"""Pins for the actions family (symbolic arrows).

Every entry is a ``os.path.join(size, "actions", name.svg)`` key holding
the pinned tuple of drawing elements for that shipped file, in document
order. The pins live beside ``theme_inventory``; the geometry tests in
``test_icon_theme_geometry`` compare each shipped SVG with its tuple.
"""

import os

from support.icon.shape_pins._shared import (
    _shape,
)

PINS = {
    os.path.join("16x16", "actions", "go-next-symbolic.svg"): (
        _shape("path", d="M 6,3 L 6,11 L 10,7 Z", fill="#000000"),
    ),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"): (
        _shape("path", d="M 8,4 L 8,15 L 14,10 Z", fill="#000000"),
    ),
    # The media-eject eject glyph, our own triangle and bar sharing the
    # same horizontal extent and centre at each size.
    os.path.join("16x16", "actions", "media-eject.svg"): (
        _shape("path", d="M4 9 L12 9 L8 4 Z", fill="#000000"),
        _shape("rect", x="4", y="11", width="8", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "actions", "media-eject.svg"): (
        _shape("path", d="M7 13 L15 13 L11 6 Z", fill="#000000"),
        _shape("rect", x="7", y="15", width="8", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "actions", "media-eject.svg"): (
        _shape("path", d="M10 19 L22 19 L16 8 Z", fill="#000000"),
        _shape("rect", x="10", y="22", width="12", height="3", fill="#000000"),
    ),
}
