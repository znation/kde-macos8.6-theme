"""Encode an 8-bit RGB image as a PNG file using only the standard library.

``tools/png/loader.py`` reads a PNG file and ``tools/png/read.py`` decodes it;
this is their minimal inverse, used to generate
the wallpaper images. The output is deterministic: every row uses filter type
0 and one IDAT chunk is compressed at zlib level 9, so the same pixels always
produce the same bytes.
"""

from __future__ import annotations

import struct
import zlib

try:
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from ints import is_plain_int

_MAGIC = b"\x89PNG\r\n\x1a\n"

# The PNG spec stores each IHDR dimension in a 4-byte field but limits it to
# 2**31 - 1. A larger positive integer passed the old positive-int check and,
# with a matching buffer, was written into the header as a dimension no
# decoder accepts; above 2**32 - 1 the IHDR pack raises a bare struct.error
# that names neither the dimension nor this function.
_MAX_DIMENSION = (1 << 31) - 1


def _chunk(ctype: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", crc)


def _validate_dimension(name: str, value: object) -> None:
    """Reject a PNG dimension that is not an integer from 1 to 2**31 - 1.

    ``is_plain_int`` rejects ``bool`` (an ``int`` subclass that would pass as
    1/0) and the upper bound keeps the value inside the PNG spec's dimension
    range, naming the field and both limits instead of letting an out-of-range
    value reach the IHDR pack or a decoder.
    """
    if not is_plain_int(value) or value < 1:
        raise ValueError(
            f"PNG {name} must be a positive integer: {name}={value!r}"
        )
    if value > _MAX_DIMENSION:
        raise ValueError(
            f"PNG {name} must be at most {_MAX_DIMENSION} (the PNG header's "
            f"32-bit signed limit): {name}={value}"
        )


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    """Return the PNG bytes of a *width* x *height* image of packed *rgb* pixels.

    Raises ``ValueError`` when a dimension is not an integer in the PNG
    header's 1..2**31-1 range, or *rgb* is not ``bytes``/``bytearray`` of
    exactly ``width * height * 3`` bytes.
    """
    for name, value in (("width", width), ("height", height)):
        _validate_dimension(name, value)
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
