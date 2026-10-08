"""PNG encoding helpers shared by the image test modules.

Test-only: builds 8-bit, non-interlaced PNGs (including deliberately malformed
ones) so ``tests/test_png.py`` and ``tests/test_fidelity.py`` share one encoder
instead of each carrying its own.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Callable

from tools import png


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + ctype
        + payload
        + struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF)
    )


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _filter_line(ftype: int, line: bytes, prev: bytes, bpp: int) -> bytes:
    if ftype == 0:
        return line
    out = bytearray(len(line))
    for i in range(len(line)):
        a = line[i - bpp] if i >= bpp else 0
        b = prev[i]
        c = prev[i - bpp] if i >= bpp else 0
        if ftype == 1:
            pred = a
        elif ftype == 2:
            pred = b
        elif ftype == 3:
            pred = (a + b) >> 1
        else:
            pred = _paeth(a, b, c)
        out[i] = (line[i] - pred) & 0xFF
    return bytes(out)


def make_png(
    width: int,
    height: int,
    rows: list[bytes],
    color_type: int = 2,
    palette: bytes | None = None,
    filter_types: list[int] | None = None,
) -> bytes:
    """Encode an 8-bit non-interlaced PNG from raw scanlines (test-only)."""
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    bpp = channels
    filtered = bytearray()
    prev = bytes(width * channels)
    for index, row in enumerate(rows):
        ftype = filter_types[index] if filter_types else 0
        filtered += bytes([ftype]) + _filter_line(ftype, row, prev, bpp)
        prev = row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    out = _PNG_SIGNATURE + _chunk(b"IHDR", ihdr)
    if palette is not None:
        out += _chunk(b"PLTE", palette)
    out += _chunk(b"IDAT", zlib.compress(bytes(filtered))) + _chunk(b"IEND", b"")
    return out


def with_ihdr_byte(data: bytes, offset: int, value: int) -> bytes:
    """Return *data* with one IHDR payload byte replaced and the CRC fixed.

    ``offset`` is relative to the IHDR payload, so 10 selects the compression
    method, 11 the filter method, and 12 the interlace method.
    """
    start = len(_PNG_SIGNATURE) + 8  # skip signature, length, and "IHDR"
    length = struct.unpack(
        ">I", data[len(_PNG_SIGNATURE) : len(_PNG_SIGNATURE) + 4]
    )[0]
    payload = bytearray(data[start : start + length])
    payload[offset] = value
    crc = struct.pack(">I", zlib.crc32(b"IHDR" + bytes(payload)) & 0xFFFFFFFF)
    return data[:start] + bytes(payload) + crc + data[start + length + 4 :]


def rgb_image(
    width: int, height: int, pixel: Callable[[int, int], tuple[int, int, int]]
) -> tuple[png.Image, bytes]:
    """Return an RGB image and its PNG bytes.

    The ``pixel`` callback is called with ``(x, y)`` and returns an
    ``(r, g, b)`` triple for that coordinate.
    """
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row += bytes(pixel(x, y))
        rows.append(bytes(row))
    image = png.Image(width, height, b"".join(rows))
    return image, make_png(width, height, rows)

