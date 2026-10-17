"""PNG chunk framing: split a PNG byte string into validated chunks.

:func:`iter_chunks` walks the chunk stream after the signature and yields
``(type, payload)`` for each chunk, rejecting an oversized length, an invalid
type code, a truncated payload or CRC, and a bad checksum by name. What the
chunks mean (IHDR, PLTE, IDAT, IEND) is ``tools/png.py``'s concern.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Iterator

if __package__:
    from tools.image_format import PNG_MAGIC
    from tools.png_image import PngError
else:  # run as a top-level module, e.g. imported by tools/png.py
    from image_format import PNG_MAGIC
    from png_image import PngError

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
    pos = len(PNG_MAGIC)
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
        yield ctype, payload
        pos += 12 + length
