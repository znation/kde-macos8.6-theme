"""An independent test-side reader for the Xcursor files ``tools/xcursor.py`` writes.

The reader is written against the Xcursor binary layout, not the writer: it
imports no symbol from ``tools/xcursor.py``, so a writer that mis-frames a
field cannot make the reader agree with it. It validates the file header,
tolerates and skips a TOC entry whose type is not an image chunk, validates
each image chunk header, and returns the stored premultiplied ARGB payload
re-encoded as an RGBA PNG (the stored colour channels are not divided by
alpha, so only an opaque frame reproduces its original PNG bytes). Errors are
``ValueError`` naming the path and the field or offset that failed.
"""

from __future__ import annotations

import functools
import os
import struct
from pathlib import Path
from typing import NamedTuple

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.png.write import encode_rgba_png  # noqa: E402

MAGIC = b"Xcur"
FILE_VERSION = 0x00010000
FILE_HEADER_SIZE = 16
TOC_ENTRY_SIZE = 12
IMAGE_TYPE = 0xFFFD0002
CHUNK_VERSION = 1
IMAGE_HEADER_SIZE = 36
MAX_IMAGE_SIZE = 0x7FFF


class CursorImage(NamedTuple):
    """One image frame read back from an Xcursor file."""

    nominal_size: int
    width: int
    height: int
    hotspot_x: int
    hotspot_y: int
    png: bytes


class CursorFile(NamedTuple):
    """The image frames an Xcursor file holds, in TOC order."""

    images: tuple[CursorImage, ...]


def _fail(path: Path, message: str) -> None:
    raise ValueError(f"{path}: {message}")


def _rgba_from_words(data: bytes, offset: int, count: int) -> bytes:
    """Return *count* little-endian ARGB words at *offset* as packed RGBA."""
    words = struct.unpack_from(f"<{count}I", data, offset)
    rgba = bytearray(count * 4)
    for index, word in enumerate(words):
        start = index * 4
        rgba[start] = (word >> 16) & 0xFF
        rgba[start + 1] = (word >> 8) & 0xFF
        rgba[start + 2] = word & 0xFF
        rgba[start + 3] = (word >> 24) & 0xFF
    return bytes(rgba)


def _fingerprint(path):
    """Return *path*'s stat fingerprint, or None when it cannot be read.

    A failed stat is not cached, so the caller's read still reports the missing
    or unreadable path the way it did before.
    """
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def _read_cursor_file(path: Path) -> CursorFile:
    """Read and validate the Xcursor file at *path*."""
    data = path.read_bytes()
    if len(data) < FILE_HEADER_SIZE:
        _fail(
            path,
            f"file header is truncated: {len(data)} bytes at offset 0, "
            f"need {FILE_HEADER_SIZE}",
        )
    magic, header_size, version, ntoc = struct.unpack_from(
        "<4sIII", data, 0
    )
    if magic != MAGIC:
        _fail(path, f"bad magic {magic!r} at offset 0, expected {MAGIC!r}")
    if header_size != FILE_HEADER_SIZE:
        _fail(
            path,
            f"file header size {header_size} at offset 4, "
            f"expected {FILE_HEADER_SIZE}",
        )
    if version != FILE_VERSION:
        _fail(
            path,
            f"file version {version:#010x} at offset 8, "
            f"expected {FILE_VERSION:#010x}",
        )
    toc_end = FILE_HEADER_SIZE + TOC_ENTRY_SIZE * ntoc
    if toc_end > len(data):
        _fail(
            path,
            f"TOC of {ntoc} entries at offset {FILE_HEADER_SIZE} overruns "
            f"the file's {len(data)} bytes",
        )

    images = []
    for index in range(ntoc):
        entry_offset = FILE_HEADER_SIZE + TOC_ENTRY_SIZE * index
        chunk_type, nominal_size, chunk_offset = struct.unpack_from(
            "<III", data, entry_offset
        )
        if chunk_type != IMAGE_TYPE:
            continue
        if nominal_size < 1:
            _fail(
                path,
                f"TOC nominal size {nominal_size} at offset "
                f"{entry_offset + 4} must be positive",
            )
        if nominal_size > MAX_IMAGE_SIZE:
            _fail(
                path,
                f"TOC nominal size {nominal_size} at offset "
                f"{entry_offset + 4} exceeds {MAX_IMAGE_SIZE}",
            )
        chunk_end = chunk_offset + IMAGE_HEADER_SIZE
        if chunk_end > len(data):
            _fail(
                path,
                f"image chunk {index} header at offset {chunk_offset} runs "
                f"past the file's {len(data)} bytes",
            )
        (
            image_header_size,
            image_type,
            image_nominal_size,
            image_version,
            width,
            height,
            hotspot_x,
            hotspot_y,
            _delay,
        ) = struct.unpack_from("<IIIIIIIII", data, chunk_offset)
        if image_header_size != IMAGE_HEADER_SIZE:
            _fail(
                path,
                f"image header size {image_header_size} at offset "
                f"{chunk_offset}, expected {IMAGE_HEADER_SIZE}",
            )
        if image_type != IMAGE_TYPE:
            _fail(
                path,
                f"image chunk type {image_type:#010x} at offset "
                f"{chunk_offset + 4}, expected {IMAGE_TYPE:#010x}",
            )
        if image_version != CHUNK_VERSION:
            _fail(
                path,
                f"image chunk version {image_version} at offset "
                f"{chunk_offset + 12}, expected {CHUNK_VERSION}",
            )
        if image_nominal_size < 1:
            _fail(
                path,
                f"image nominal size {image_nominal_size} at offset "
                f"{chunk_offset + 8} must be positive",
            )
        if image_nominal_size > MAX_IMAGE_SIZE:
            _fail(
                path,
                f"image nominal size {image_nominal_size} at offset "
                f"{chunk_offset + 8} exceeds {MAX_IMAGE_SIZE}",
            )
        if image_nominal_size != nominal_size:
            _fail(
                path,
                f"image nominal size {image_nominal_size} at offset "
                f"{chunk_offset + 8} does not match the TOC's {nominal_size}",
            )
        if width < 1 or height < 1:
            _fail(
                path,
                f"image dimensions {width}x{height} at offset "
                f"{chunk_offset + 16} must be positive",
            )
        if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
            _fail(
                path,
                f"image dimensions {width}x{height} at offset "
                f"{chunk_offset + 16} exceed {MAX_IMAGE_SIZE}",
            )
        if not 0 <= hotspot_x < width:
            _fail(
                path,
                f"hotspot_x {hotspot_x} at offset {chunk_offset + 24} lies "
                f"outside the {width}-pixel image",
            )
        if not 0 <= hotspot_y < height:
            _fail(
                path,
                f"hotspot_y {hotspot_y} at offset {chunk_offset + 28} lies "
                f"outside the {height}-pixel image",
            )
        payload_offset = chunk_offset + IMAGE_HEADER_SIZE
        payload_bytes = width * height * 4
        if payload_offset + payload_bytes > len(data):
            _fail(
                path,
                f"image payload at offset {payload_offset} needs "
                f"{payload_bytes} bytes but the file ends at {len(data)}",
            )
        rgba = _rgba_from_words(data, payload_offset, width * height)
        images.append(
            CursorImage(
                image_nominal_size,
                width,
                height,
                hotspot_x,
                hotspot_y,
                encode_rgba_png(width, height, rgba),
            )
        )
    return CursorFile(tuple(images))


@functools.lru_cache(maxsize=128)
def _parse_cached(path_text, fingerprint):
    """Parse *path_text*; the stat fingerprint is the cache's change key."""
    return _read_cursor_file(Path(path_text))


def read_cursor(path) -> CursorFile:
    """Read and validate the Xcursor file at *path* into a :class:`CursorFile`.

    A cursor suite reads the same file from many test methods, so a successful
    parse is reused instead of re-reading and re-encoding every PNG frame. The
    key carries the file's stat fingerprint, so a rewritten or replaced file is
    parsed again; a failed read is never cached, and the cache is bounded to
    128 entries. Callers treat the returned immutable frames as read-only.
    """
    path = Path(path)
    fingerprint = _fingerprint(path)
    if fingerprint is None:
        return _read_cursor_file(path)
    return _parse_cached(str(path), fingerprint)
