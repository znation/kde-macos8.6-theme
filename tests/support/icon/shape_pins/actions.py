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
}
