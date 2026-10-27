"""Write an Xcursor cursor file from RGBA frames using only the standard library.

The cursor artifact stores its frames as Xcursor image chunks. The container
is an X/KDE-required binary layout that no screenshot in
``macos8.6-screenshots/`` shows, so its values are recorded here rather than
sampled: a 16-byte file header (``b"Xcur"``, header size 16, file version
0x00010000, TOC count), one 12-byte TOC entry per chunk (type, subtype, byte
offset), and a 36-byte image chunk header (header size 36, type 0xfffd0002,
subtype = nominal size, chunk version 1, width, height, hotspot x, hotspot y,
delay 0). The image payload is ``width * height`` little-endian premultiplied
ARGB words, not PNG bytes: each colour channel is premultiplied with
``(channel * alpha + 127) // 255``, and alpha is stored unchanged. The write
is deterministic, so the same records always produce byte-identical output.

:func:`write_cursor` takes each frame as PNG bytes and decodes it first, which
is convenient for a caller that holds an encoded image. :func:`write_rgba_cursor`
takes the RGBA pixels directly, so a generator that already holds them (the
cursor generator renders its grids to RGBA) does not encode a PNG only to
decode it again.

The cursor artifact's provenance is recorded in the existing ``## icons``
row of ``docs/invariants.md``; no ``## cursors`` section exists, because
``tests/support/invariants.py`` accepts only ``theme/`` subsystem sections plus
``tooling``.
"""

from __future__ import annotations

import struct

try:
    from tools.ints import is_plain_int
    from tools.png import PngError, decode_rgba
except ImportError:  # imported from a directly run tool
    from ints import is_plain_int
    from png import PngError, decode_rgba

MAGIC = b"Xcur"
FILE_VERSION = 0x00010000
FILE_HEADER_SIZE = 16
TOC_ENTRY_SIZE = 12
IMAGE_TYPE = 0xFFFD0002
CHUNK_VERSION = 1
IMAGE_HEADER_SIZE = 36
MAX_IMAGE_SIZE = 0x7FFF


def _require_dimension(name: str, value: object) -> None:
    """Reject a dimension that is not an integer in 1..``MAX_IMAGE_SIZE``."""
    if not is_plain_int(value):
        raise ValueError(
            f"{name} must be an integer, not {type(value).__name__}: "
            f"{name}={value!r}"
        )
    if not 1 <= value <= MAX_IMAGE_SIZE:
        raise ValueError(
            f"{name} must be between 1 and {MAX_IMAGE_SIZE}: {name}={value}"
        )


def _require_hotspot(name: str, value: object, limit: int) -> None:
    """Reject a hotspot coordinate outside its image's pixel range."""
    if not is_plain_int(value):
        raise ValueError(
            f"{name} must be an integer, not {type(value).__name__}: "
            f"{name}={value!r}"
        )
    if not 0 <= value < limit:
        raise ValueError(
            f"{name} {value} lies outside its {limit}-pixel image"
        )


def _premultiplied_word(r: int, g: int, b: int, a: int) -> int:
    """Return one little-endian Xcursor ARGB word with premultiplied colours."""
    return (
        (a << 24)
        | (((r * a + 127) // 255) << 16)
        | (((g * a + 127) // 255) << 8)
        | ((b * a + 127) // 255)
    )


def _premultiplied_payload(width: int, height: int, rgba: bytes) -> bytes:
    """Return *width* x *height* premultiplied ARGB words from *rgba* pixels."""
    payload = bytearray(width * height * 4)
    for pixel, start in enumerate(range(0, len(rgba), 4)):
        r, g, b, a = rgba[start : start + 4]
        struct.pack_into(
            "<I", payload, pixel * 4, _premultiplied_word(r, g, b, a)
        )
    return bytes(payload)


def _frame_fields(
    index: int, record: object, payload_name: str
) -> tuple[int, int, int, int, int, object]:
    """Unpack a frame record and validate its five numeric fields.

    *payload_name* names the sixth item (``"png"`` or ``"rgba"``) in the
    wrong-length diagnostic. The payload is returned unvalidated, because the
    two writers accept a different pixel representation.
    """
    try:
        nominal_size, width, height, hotspot_x, hotspot_y, payload = record
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"images[{index}] must be a 6-item (nominal_size, width, height, "
            f"hotspot_x, hotspot_y, {payload_name}) record: {record!r}"
        ) from exc

    _require_dimension(f"images[{index}] nominal_size", nominal_size)
    _require_dimension(f"images[{index}] width", width)
    _require_dimension(f"images[{index}] height", height)
    _require_hotspot(f"images[{index}] hotspot_x", hotspot_x, width)
    _require_hotspot(f"images[{index}] hotspot_y", hotspot_y, height)
    return nominal_size, width, height, hotspot_x, hotspot_y, payload


def _require_bytes(index: int, name: str, value: object) -> None:
    """Reject a frame payload that is not ``bytes`` or ``bytearray``."""
    if not isinstance(value, (bytes, bytearray)):
        raise ValueError(
            f"images[{index}] {name} must be bytes or bytearray, not "
            f"{type(value).__name__}"
        )


def _build_payload(index: int, record: object) -> tuple[int, int, int, int, int, bytes]:
    """Validate one PNG frame record and return its fields plus the ARGB payload."""
    nominal_size, width, height, hotspot_x, hotspot_y, png = _frame_fields(
        index, record, "png"
    )
    _require_bytes(index, "png", png)
    try:
        png_width, png_height, rgba = decode_rgba(png)
    except PngError as exc:
        raise ValueError(
            f"images[{index}] png could not be decoded: {exc}"
        ) from exc
    if (png_width, png_height) != (width, height):
        raise ValueError(
            f"images[{index}] png is {png_width}x{png_height} but the record "
            f"declares {width}x{height}"
        )

    return (
        nominal_size,
        width,
        height,
        hotspot_x,
        hotspot_y,
        _premultiplied_payload(width, height, rgba),
    )


def _rgba_frame(index: int, record: object) -> tuple[int, int, int, int, int, bytes]:
    """Validate one raw-RGBA frame record and return its fields plus the ARGB payload."""
    nominal_size, width, height, hotspot_x, hotspot_y, rgba = _frame_fields(
        index, record, "rgba"
    )
    _require_bytes(index, "rgba", rgba)
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(
            f"images[{index}] rgba is {len(rgba)} bytes; a {width}x{height} "
            f"RGBA frame needs {expected}"
        )

    return (
        nominal_size,
        width,
        height,
        hotspot_x,
        hotspot_y,
        _premultiplied_payload(width, height, rgba),
    )


def _assemble(frames) -> bytes:
    """Return the Xcursor bytes for already-validated, non-empty *frames*."""
    if not frames:
        raise ValueError(
            "images must contain at least one frame; a cursor file with no "
            "image cannot be drawn"
        )
    ntoc = len(frames)
    next_offset = FILE_HEADER_SIZE + TOC_ENTRY_SIZE * ntoc
    toc = bytearray()
    chunks = bytearray()
    for nominal_size, width, height, hotspot_x, hotspot_y, payload in frames:
        toc += struct.pack("<III", IMAGE_TYPE, nominal_size, next_offset)
        chunk = (
            struct.pack(
                "<IIIIIIIII",
                IMAGE_HEADER_SIZE,
                IMAGE_TYPE,
                nominal_size,
                CHUNK_VERSION,
                width,
                height,
                hotspot_x,
                hotspot_y,
                0,
            )
            + payload
        )
        chunks += chunk
        next_offset += len(chunk)
    return (
        struct.pack(
            "<4sIII", MAGIC, FILE_HEADER_SIZE, FILE_VERSION, ntoc
        )
        + bytes(toc)
        + bytes(chunks)
    )


def write_cursor(images) -> bytes:
    """Return the Xcursor bytes for *images*.

    *images* is an iterable of ``(nominal_size, width, height, hotspot_x,
    hotspot_y, png_bytes)`` records, one per image frame. Each ``png_bytes``
    must decode to exactly ``width`` x ``height`` RGBA pixels. Raises
    ``ValueError`` when *images* contains no frames, and otherwise naming the
    offending record field for a dimension outside 1..``MAX_IMAGE_SIZE``, a
    hotspot outside its image, a non-integer numeric field (including a
    ``bool``), a PNG field that is not ``bytes``/``bytearray``, and a PNG
    whose size disagrees with the record.
    """
    frames = [_build_payload(index, record) for index, record in enumerate(images)]
    return _assemble(frames)


def write_rgba_cursor(images) -> bytes:
    """Return the Xcursor bytes for raw-RGBA *images*.

    *images* is an iterable of ``(nominal_size, width, height, hotspot_x,
    hotspot_y, rgba_bytes)`` records, one per image frame. Each ``rgba_bytes``
    must hold exactly ``width * height * 4`` bytes in row order. The result is
    byte-identical to :func:`write_cursor` given the same pixels encoded as
    PNG, without the encode/decode round trip. Raises ``ValueError`` naming
    the offending record field, as :func:`write_cursor` does, when a dimension
    or hotspot is invalid or the pixel buffer is the wrong type or length, and
    when *images* contains no frames.
    """
    frames = [_rgba_frame(index, record) for index, record in enumerate(images)]
    return _assemble(frames)
