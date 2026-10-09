"""PNG encoding helpers shared by the image test modules.

Test-only: builds 8-bit, non-interlaced PNGs (including deliberately malformed
ones) so the PNG test modules -- ``tests/test_png_decode.py``,
``tests/test_png_filters.py``, ``tests/test_png_fixtures.py``,
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


def ihdr_end(data: bytes) -> int:
    """Return the offset just past the IHDR chunk in *data*.

    IHDR's payload is fixed at 13 bytes, but reading the chunk's own length
    field keeps this correct for any framing: the 8-byte signature, then the
    4-byte length, 4-byte type, payload and 4-byte CRC. The decode tests
    splice deliberately malformed chunks in after IHDR and so need this
    boundary rather than re-deriving it at each site.
    """
    start = len(_PNG_SIGNATURE)
    length = struct.unpack(">I", data[start : start + 4])[0]
    return start + 8 + length + 4


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


def _require_positive_dimensions(name: str, width: int, height: int) -> None:
    """Reject a non-positive width or height before it reaches ``struct.pack``.

    A zero or negative dimension is a fixture bug. A negative one used to
    escape from ``struct.pack(">I", ...)`` as a bare ``struct.error`` that
    named neither the argument nor the requirement, and a zero width silently
    built a degenerate PNG whose decode error pointed at the decoder rather
    than the fixture. Every PNG dimension is positive, so report it here by
    name.
    """
    if width <= 0 or height <= 0:
        raise ValueError(
            f"{name}: width and height must be positive: {width}x{height}"
        )


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
    builds a deliberately truncated IDAT that way. ``width`` and ``height``
    must be positive.
    """
    _require_positive_dimensions("make_png", width, height)
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
    method, 11 the filter method, and 12 the interlace method. ``offset`` must
    lie in the payload and ``value`` must be a byte; a negative ``offset``
    would otherwise index from the end and silently rewrite a different field,
    and the other out-of-range cases used to escape as a bare ``IndexError``
    or ``ValueError`` naming neither the argument nor the valid range.
    """
    start = len(_PNG_SIGNATURE) + 8  # skip signature, length, and "IHDR"
    length = struct.unpack(
        ">I", data[len(_PNG_SIGNATURE) : len(_PNG_SIGNATURE) + 4]
    )[0]
    if not 0 <= offset < length:
        raise ValueError(
            f"with_ihdr_byte: offset {offset} is outside the IHDR payload "
            f"(expected 0 <= offset < {length})"
        )
    if not 0 <= value <= 255:
        raise ValueError(
            f"with_ihdr_byte: value {value} is not a byte "
            "(expected 0 <= value <= 255)"
        )
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
    The IHDR declares ``width`` x ``height`` (both positive) and the stream is
    closed with IEND.
    """
    _require_positive_dimensions("png_with_idat", width, height)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        _PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", payload)
        + _chunk(b"IEND", b"")
    )


def _pixel_channels(x: int, y: int, value: object) -> bytes:
    """Validate one ``pixel(x, y)`` result and return its three channel bytes.

    The callback contract is an ``(r, g, b)`` triple of 0-255 ints. ``bytes``
    accepts a plain int as a length, so a callback that returned ``3`` would
    silently build three zero bytes and a wrong image instead of failing;
    converting to a tuple first turns that into an error naming the
    coordinate. Each channel is checked too, so a non-integer or out-of-range
    value names the coordinate and channel instead of escaping as a bare
    ``bytes`` error.
    """
    try:
        channels = tuple(value)
    except TypeError:
        raise ValueError(
            f"rgb_image: pixel({x}, {y}) returned {value!r}; "
            "expected an (r, g, b) triple"
        ) from None
    if len(channels) != 3:
        raise ValueError(
            f"rgb_image: pixel({x}, {y}) returned {len(channels)} channels "
            f"({value!r}); expected 3 (r, g, b)"
        )
    for name, channel in zip(("r", "g", "b"), channels):
        if isinstance(channel, bool) or not isinstance(channel, int):
            raise ValueError(
                f"rgb_image: pixel({x}, {y}) channel {name} is not an "
                f"integer: {channel!r}"
            )
        if not 0 <= channel <= 255:
            raise ValueError(
                f"rgb_image: pixel({x}, {y}) channel {name} is outside "
                f"0-255: {channel}"
            )
    return bytes(channels)


def rgb_image(
    width: int, height: int, pixel: Callable[[int, int], tuple[int, int, int]]
) -> tuple[png.Image, bytes]:
    """Return an RGB image and its PNG bytes.

    The ``pixel`` callback is called with ``(x, y)`` and returns an
    ``(r, g, b)`` triple for that coordinate. A result that is not three
    0-255 integers is reported with the coordinate, so a malformed callback
    fails here instead of building a wrong image or raising a bare error.
    """
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row += _pixel_channels(x, y, pixel(x, y))
        rows.append(bytes(row))
    image = png.Image(width, height, b"".join(rows))
    return image, make_png(width, height, rows)


def solid_rgb(
    width: int, height: int, color: tuple[int, int, int] = (0, 0, 0)
) -> tuple[png.Image, bytes]:
    """Return a single-colour RGB image and its PNG bytes.

    A flat fill is the common case in the decode, metrics and CLI tests, which
    otherwise each spell it as an argument-ignoring ``lambda``; naming the
    case here keeps the colour visible at the call site.
    """
    return rgb_image(width, height, lambda x, y: color)

