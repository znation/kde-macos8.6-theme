"""Assemble validated cursor frames into the Xcursor binary container."""

from __future__ import annotations

import struct
from collections.abc import Sequence

MAGIC = b"Xcur"
FILE_VERSION = 0x00010000
FILE_HEADER_SIZE = 16
TOC_ENTRY_SIZE = 12
IMAGE_TYPE = 0xFFFD0002
CHUNK_VERSION = 1
IMAGE_HEADER_SIZE = 36
MAX_IMAGE_SIZE = 0x7FFF
Frame = tuple[int, int, int, int, int, bytes]


def assemble(frames: Sequence[Frame]) -> bytes:
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
        chunk = struct.pack(
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
        ) + payload
        chunks += chunk
        next_offset += len(chunk)
    return (
        struct.pack("<4sIII", MAGIC, FILE_HEADER_SIZE, FILE_VERSION, ntoc)
        + bytes(toc)
        + bytes(chunks)
    )
