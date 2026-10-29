"""PNG chunk framing: split a PNG byte string into validated chunks.

:func:`iter_chunks` walks the chunk stream after the signature and yields
``(type, payload)`` for each chunk, rejecting an oversized length, an invalid
type code, a truncated payload or CRC, a bad checksum, a non-empty IEND
payload, and a trailing fragment
after IEND by name. Chunk ordering and payload collection is
``tools/png/stream.py``'s concern; IHDR field validation lives in
``tools/png/header.py``.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Iterator

try:
    from tools.image_format import PNG_MAGIC
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from image_format import PNG_MAGIC

from .image import PngError

# The PNG spec caps a chunk's payload length at 2**31 - 1 bytes: the field is
# 32-bit unsigned, but values with the high bit set are reserved. A file
# declaring more is malformed; without this check the length is compared
# against the bytes present and reported as a truncated chunk, which points at
# a missing tail instead of the invalid length.
_MAX_CHUNK_LENGTH = (1 << 31) - 1


def chunk_name(ctype: bytes) -> str:
    """The chunk type as a printable ``repr`` for error messages."""
    return repr(ctype.decode("ascii", "replace"))


def iter_chunks(data: bytes) -> Iterator[tuple[bytes, bytes]]:
    """Yield ``(type, payload)`` for each chunk in *data* after the signature.

    A declared length above the PNG spec's maximum, an invalid type code, a
    truncated payload or CRC, a bad checksum, and a non-empty IEND payload
    raise :class:`PngError`. So
    does a trailing fragment shorter than a chunk header when it follows IEND:
    IEND ends the datastream, so those bytes are malformed trailing data, not
    the truncated start of a chunk a later read could complete.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise PngError(
            f"iter_chunks data must be bytes or bytearray, not "
            f"{type(data).__name__}"
        )
    data = bytes(data)
    pos = len(PNG_MAGIC)
    saw_iend = False
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        if length > _MAX_CHUNK_LENGTH:
            raise PngError(
                f"PNG chunk {chunk_name(ctype)} at offset {pos} declares "
                f"{length} payload bytes, above the {_MAX_CHUNK_LENGTH}-byte "
                "maximum the PNG spec allows"
            )
        # The PNG spec restricts a chunk type to four ASCII letters, and the
        # first byte alone decides whether the chunk is critical. A type with
        # a digit, space or non-ASCII byte is not a valid code: without this
        # check such a chunk is not recognized as critical (its first byte is
        # not an uppercase letter) and falls through decode_png's ancillary
        # branch, silently skipping malformed framing. Reject it by name.
        if not ctype.isalpha():
            raise PngError(
                f"invalid PNG chunk type {chunk_name(ctype)} at offset "
                f"{pos}: chunk types are four ASCII letters"
            )
        payload = data[pos + 8 : pos + 8 + length]
        if len(payload) != length:
            raise PngError(
                f"truncated PNG chunk {chunk_name(ctype)} at "
                f"offset {pos}: declared {length} payload bytes, only "
                f"{len(payload)} present"
            )
        checksum = data[pos + 8 + length : pos + 12 + length]
        if len(checksum) != 4:
            raise PngError(
                f"truncated PNG chunk {chunk_name(ctype)} CRC "
                f"at offset {pos + 8 + length}: expected 4 bytes, got "
                f"{len(checksum)}"
            )
        (expected,) = struct.unpack(">I", checksum)
        actual = zlib.crc32(ctype + payload) & 0xFFFFFFFF
        if actual != expected:
            raise PngError(
                f"PNG chunk {chunk_name(ctype)} at offset {pos} "
                f"has a bad CRC: stored 0x{expected:08x}, computed "
                f"0x{actual:08x}"
            )
        if ctype == b"IEND" and payload:
            # The spec gives IEND an empty data field: its only job is to end
            # the datastream. A payload is malformed framing, and dropping it
            # silently would decode a file a conformant reader refuses.
            raise PngError(
                f"PNG IEND chunk at offset {pos} has {len(payload)} payload "
                f"byte{'' if len(payload) == 1 else 's'}; IEND's data field "
                "must be empty"
            )
        yield ctype, payload
        if ctype == b"IEND":
            saw_iend = True
        pos += 12 + length
    if saw_iend and pos < len(data):
        # IEND ends the PNG datastream, so bytes left over after it cannot be
        # a chunk a later read completes; they are trailing data a conformant
        # reader refuses. Before IEND the same fragment instead surfaces as
        # collect_chunks' missing-IEND error, so only the post-IEND case needs
        # its own diagnosis here.
        leftover = len(data) - pos
        raise PngError(
            f"PNG has {leftover} trailing byte"
            f"{'' if leftover == 1 else 's'} after IEND that do not form a "
            "chunk; IEND must be the last chunk"
        )
