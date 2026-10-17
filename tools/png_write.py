"""Encode an 8-bit RGB image as a PNG file using only the standard library.

``tools/png.py`` is the reader; this is its minimal inverse, used to generate
the wallpaper images. The output is deterministic: every row uses filter type
0 and one IDAT chunk is compressed at zlib level 9, so the same pixels always
produce the same bytes.
"""

from __future__ import annotations

import struct
import zlib

_MAGIC = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", crc)


def _is_dimension(value: object) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool) and value > 0
    )


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    """Return the PNG bytes of a *width* x *height* image of packed *rgb* pixels.

    Raises ``ValueError`` when a dimension is not a positive integer or *rgb*
    is not ``bytes``/``bytearray`` of exactly ``width * height * 3`` bytes.
    """
    for name, value in (("width", width), ("height", height)):
        if not _is_dimension(value):
            raise ValueError(
                f"PNG {name} must be a positive integer: {name}={value!r}"
            )
    if not isinstance(rgb, (bytes, bytearray)):
        raise ValueError(
            f"PNG rgb must be bytes or bytearray, not {type(rgb).__name__}"
        )
    expected = width * height * 3
    if len(rgb) != expected:
        raise ValueError(
            f"{len(rgb)} RGB bytes given; a {width}x{height} image needs "
            f"{expected} (width*height*3)"
        )
    stride = width * 3
    raw = b"".join(
        b"\x00" + bytes(rgb[row * stride : (row + 1) * stride])
        for row in range(height)
    )
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        _MAGIC
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )
