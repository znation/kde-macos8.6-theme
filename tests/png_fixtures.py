"""PNG encoding helpers shared by the image test modules.

Test-only: builds 8-bit, non-interlaced PNGs (including deliberately malformed
ones) so the image test modules -- ``tests/test_png.py``,
``tests/test_fidelity_metrics.py`` and ``tests/test_fidelity_cli.py`` -- share
one encoder instead of each carrying its own.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Callable

from tools import png


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# color_type -> channels per pixel at bit depth 8, mirroring tools/png.py's set.
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


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
    """Encode an 8-bit non-interlaced PNG from raw scanlines (test-only).

    Every row must be exactly ``width * channels`` bytes and ``filter_types``,
    when given, must have one entry per row. A mismatch is a bug in the caller
    (a short row silently shifts every later scanline), so it is reported here
    instead of surfacing later as a confusing decode error. ``color_type``
    must be one of the supported PNG types (0, 2, 3, 4 or 6); anything else is
    reported the same way. Fewer rows than ``height`` is allowed: a test
    builds a deliberately truncated IDAT that way.
    """
    channels = _CHANNELS.get(color_type)
    if channels is None:
        # An unknown color type is a fixture bug; the dict lookup used to
        # escape as a bare KeyError that named only the number.
        raise ValueError(
            f"make_png: unsupported color_type {color_type}; expected one of "
            f"{sorted(_CHANNELS)}"
        )
    bpp = channels
    expected = width * channels
    if filter_types is not None and len(filter_types) != len(rows):
        raise ValueError(
            f"make_png: filter_types has {len(filter_types)} entries for "
            f"{len(rows)} rows"
        )
    for index, row in enumerate(rows):
        if len(row) != expected:
            raise ValueError(
                f"make_png: row {index} has {len(row)} bytes; a {width}-pixel "
                f"color_type {color_type} row needs {expected}"
            )
    filtered = bytearray()
    prev = bytes(expected)
    for index, row in enumerate(rows):
        ftype = filter_types[index] if filter_types is not None else 0
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


def png_with_idat(
    payload: bytes, width: int = 1, height: int = 1
) -> bytes:
    """Return a minimal 8-bit RGB PNG whose IDAT holds *payload* verbatim.

    Tests that reach a decode failure past a valid IHDR -- a decompression
    bomb, a truncated or corrupt deflate stream, an oversized declared image --
    need control over the raw IDAT bytes, which ``make_png`` does not expose.
    The IHDR declares ``width`` x ``height`` and the stream is closed with
    IEND.
    """
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        _PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", payload)
        + _chunk(b"IEND", b"")
    )


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

