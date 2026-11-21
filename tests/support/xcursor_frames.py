"""Opaque Xcursor frame fixtures shared by the writer and reader test suites."""

from __future__ import annotations

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.png.write import encode_rgba_png

FILE_HEADER_SIZE = 16
TOC_ENTRY_SIZE = 12


def opaque_frame(width, height):
    """Return a *width* x *height* RGBA frame whose opaque pixels vary by position."""
    return bytes(
        value
        for y in range(height)
        for x in range(width)
        for value in (
            (x * 37 + y * 11) % 256,
            (x * 17 + y * 53) % 256,
            (x * 7 + y * 91) % 256,
            255,
        )
    )


def frame_record(size):
    """Return one opaque frame record whose hotspot is the bottom-right tip."""
    png = encode_rgba_png(size, size, opaque_frame(size, size))
    return (size, size, size, size - 1, size - 1, png)
