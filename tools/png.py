"""PNG reading for the Mac OS 8.6 fidelity tooling.

Decodes 8-bit, non-interlaced PNG images (color types 0, 2, 3, 4 and 6) into
tightly packed RGB bytes, using only the Python standard library. The fidelity
comparison in ``tools/fidelity_metrics.py`` and the CLI in ``tools/fidelity.py``
are the consumers today; keeping the reader separate lets a future capture or
render step read PNGs without pulling in the comparison and CLI layers.

Raises :class:`PngError` for a malformed or unsupported PNG.
"""

from __future__ import annotations

import os
import stat
import struct
import zlib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

if __package__:
    from tools.byteops import require_equal_lengths
    from tools.image_format import (
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        other_image_format,
    )
else:  # run as a top-level module, e.g. imported by tools/fidelity.py
    from byteops import require_equal_lengths
    from image_format import (
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        other_image_format,
    )

# The PNG spec caps a chunk's payload length at 2**31 - 1 bytes: the field is
# 32-bit unsigned, but values with the high bit set are reserved. A file
# declaring more is malformed; without this check the length is compared
# against the bytes present and reported as a truncated chunk, which points at
# a missing tail instead of the invalid length.
_MAX_CHUNK_LENGTH = (1 << 31) - 1

# color_type -> channels per pixel at bit depth 8
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}

# Cap on declared pixels. A PNG's IDAT can be arbitrarily smaller than the
# scanlines it expands to, so a few KB can demand gigabytes (a decompression
# bomb). 64 MP is far above any screenshot this tool compares and still bounds
# one decode to a few hundred MB.
_MAX_PIXELS = 64_000_000

# Cap on the bytes read_png will load from disk. decode_png bounds the decoded
# image by _MAX_PIXELS, but read_png reads the whole file before decode_png
# sees the header, and a path can name a file far larger than any screenshot,
# so without a read cap a few bytes of argv can demand unbounded memory. 512
# MiB is generous for screenshot-sized inputs while keeping one read on the
# same order as the decoder's own worst-case allocation for the largest image
# it accepts.
_MAX_FILE_BYTES = 512 * 1024 * 1024


class PngError(Exception):
    """A PNG file could not be read or decoded."""


@dataclass(frozen=True)
class Image:
    """An 8-bit RGB image with tightly packed ``width * height * 3`` bytes."""

    width: int
    height: int
    rgb: bytes

    def __post_init__(self) -> None:
        # bool is an int subclass, so True/False would pass an isinstance check
        # as 1/0 and silently build a 1x1 image; a non-int dimension reaches
        # the comparison below as an opaque TypeError (or, for a float, a byte
        # count that is not a whole number). Require genuine integers here and
        # name the offending dimension.
        for name, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise PngError(
                    f"Image {name} must be an integer: {name}={value!r}"
                )
        if self.width <= 0 or self.height <= 0:
            raise PngError(
                f"Image dimensions must be positive: {self.width}x{self.height}"
            )
        # The annotation says bytes, but only the length was checked: a str
        # or list of the right length passed here and reached fidelity_metrics'
        # _abs_diff as an opaque TypeError ("can only concatenate str (not
        # bytes) to str") that named neither the field nor its type. bytes and
        # bytearray are both accepted -- the decoder returns bytes and a caller
        # may build a buffer in place, and a bytearray supports every operation
        # the tool performs -- while anything else is rejected by type here.
        if not isinstance(self.rgb, (bytes, bytearray)):
            raise PngError(
                f"Image rgb must be bytes or bytearray, not "
                f"{type(self.rgb).__name__}"
            )
        expected = self.width * self.height * 3
        if len(self.rgb) != expected:
            raise PngError(
                f"Image has {len(self.rgb)} RGB bytes; a {self.width}x"
                f"{self.height} image needs {expected} (width*height*3)"
            )


def pixel_at(image: Image, x: int, y: int) -> tuple[int, int, int]:
    """Return the RGB pixel at ``(x, y)`` in *image*.

    A coordinate outside the image is rejected instead of read: the RGB slice
    would be empty, and an ``x`` past the row end would wrap to the next row
    and return the wrong pixel. Naming the coordinate and the image size turns
    that silent misread into a diagnostic. Sampling a reference screenshot's
    palette or metric value goes through this accessor.
    """
    if not (0 <= x < image.width and 0 <= y < image.height):
        raise ValueError(
            f"pixel ({x}, {y}) is outside the {image.width}x{image.height} image"
        )
    offset = (y * image.width + x) * 3
    return (image.rgb[offset], image.rgb[offset + 1], image.rgb[offset + 2])


def _chunk_name(ctype: bytes) -> str:
    """The chunk type as a printable ``repr`` for error messages."""
    return repr(ctype.decode("ascii", "replace"))


def _iter_chunks(data: bytes) -> Iterator[tuple[bytes, bytes]]:
    pos = len(PNG_MAGIC)
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        if length > _MAX_CHUNK_LENGTH:
            raise PngError(
                f"PNG chunk {_chunk_name(ctype)} at offset {pos} declares "
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
                f"invalid PNG chunk type {_chunk_name(ctype)} at offset "
                f"{pos}: chunk types are four ASCII letters"
            )
        payload = data[pos + 8 : pos + 8 + length]
        if len(payload) != length:
            raise PngError(
                f"truncated PNG chunk {_chunk_name(ctype)} at "
                f"offset {pos}: declared {length} payload bytes, only "
                f"{len(payload)} present"
            )
        checksum = data[pos + 8 + length : pos + 12 + length]
        if len(checksum) != 4:
            raise PngError(
                f"truncated PNG chunk {_chunk_name(ctype)} CRC "
                f"at offset {pos + 8 + length}: expected 4 bytes, got "
                f"{len(checksum)}"
            )
        (expected,) = struct.unpack(">I", checksum)
        actual = zlib.crc32(ctype + payload) & 0xFFFFFFFF
        if actual != expected:
            raise PngError(
                f"PNG chunk {_chunk_name(ctype)} at offset {pos} "
                f"has a bad CRC: stored 0x{expected:08x}, computed "
                f"0x{actual:08x}"
            )
        yield ctype, payload
        pos += 12 + length


_PAETH_DELTA: bytes | None = None


def _paeth_delta_table() -> bytes:
    """Paeth predictor deltas, indexed by ``(a - c, b - c)``.

    With ``a``, ``b`` and ``c`` the left, above and above-left bytes, the
    Paeth predictor adds ``c + delta`` where ``delta`` depends only on the two
    differences ``da = a - c`` and ``db = b - c``.  The 511x511 table (row
    stride 512) turns each byte of a Paeth-filtered row into one lookup.

    A predictor call per cell costs ~50 ms, a large share of decoding a small
    Paeth image.  Instead each row is filled from the closed form of the
    predictor with ``c = 0``: ``delta`` is ``da``, ``db`` or ``0``, and as
    ``db`` runs from -255 to 255 those three values occupy at most four
    contiguous blocks, so a row is the ``db`` pattern with two blocks
    overwritten.  Built on first use, so a decode with no Paeth rows never
    pays for it.
    """
    global _PAETH_DELTA
    table = _PAETH_DELTA
    if table is not None:
        return table
    table = bytearray(511 * 512)
    # db mod 256 for db in -255..255, the value of a row wherever the
    # predictor selects ``db``.
    db_row = bytes((db + 256) & 0xFF for db in range(-255, 256))
    zeros = bytes(511)
    for da in range(-255, 256):
        base = (da + 255) << 9
        row = bytearray(db_row)
        magnitude = da if da >= 0 else -da
        if da >= 0:
            # Blocks in order: db, 0, da, db.
            zero_lo, zero_hi = max(0, 256 - 2 * magnitude), 254 - magnitude // 2
            da_lo, da_hi = 255 - magnitude // 2, 255 + magnitude
        else:
            # Blocks in order: db, da, 0, db.
            da_lo, da_hi = 255 - magnitude, 255 + magnitude // 2
            zero_lo = 256 + magnitude // 2
            zero_hi = min(254 + 2 * magnitude, 510)
        row[da_lo : da_hi + 1] = bytes([da & 0xFF]) * (da_hi + 1 - da_lo)
        if zero_lo <= zero_hi:
            row[zero_lo : zero_hi + 1] = zeros[: zero_hi + 1 - zero_lo]
        table[base : base + 511] = row
    table = bytes(table)
    _PAETH_DELTA = table
    return table


def _byte_add(a: bytes, b: bytes) -> bytes:
    """Return ``a`` and ``b`` added byte-wise modulo 256.

    Adding the two strings as big integers would let a carry cross from one
    byte into the next.  Keeping only the low seven bits of each input bounds
    every per-byte sum below 256, so no byte can carry, and XORing back the
    bit-7 difference restores the top bit.  The result equals
    ``bytes((x + y) & 0xFF for x, y in zip(a, b))`` at C speed.

    Both byte strings must be the same length; :func:`require_equal_lengths`
    rejects a mismatch and returns the shared length.
    """
    length = require_equal_lengths(a, b, "_byte_add")
    if length == 0:
        return b""
    low7 = int.from_bytes(b"\x7f" * length, "little")
    high = int.from_bytes(b"\x80" * length, "little")
    x = int.from_bytes(a, "little")
    y = int.from_bytes(b, "little")
    return (((x & low7) + (y & low7)) ^ ((x ^ y) & high)).to_bytes(
        length, "little"
    )


def _prefix_sum(channel: bytes) -> bytes:
    """Return the inclusive prefix sum of ``channel`` modulo 256.

    Equivalent to ``out[0] = channel[0]`` and
    ``out[i] = (out[i] + out[i - 1]) & 0xFF``.  A Hillis-Steele scan adds a
    doubling span at each of ``log2(len(channel))`` steps, using the same
    carry-free lane addition as :func:`_byte_add`, so a whole channel's Sub
    filter runs at C speed instead of a Python loop per byte.
    """
    length = len(channel)
    if length <= 1:
        return bytes(channel)
    low7 = int.from_bytes(b"\x7f" * length, "little")
    high = int.from_bytes(b"\x80" * length, "little")
    mask = (1 << (length * 8)) - 1
    value = int.from_bytes(channel, "little")
    step = 1
    while step < length:
        shifted = (value << (step * 8)) & mask
        value = ((value & low7) + (shifted & low7)) ^ ((value ^ shifted) & high)
        step <<= 1
    return value.to_bytes(length, "little")


def _require_raw_length(raw: bytes, width: int, height: int, channels: int) -> None:
    """Reject scanline data shorter than the header's declared size."""
    expected = height * (width * channels + 1)
    if len(raw) < expected:
        raise PngError(
            f"PNG image data is shorter than its header declares: got "
            f"{len(raw)} bytes, expected {expected} for a {width}x{height} image"
        )


def _unfilter(raw: bytes, width: int, height: int, channels: int) -> bytes:
    stride = width * channels
    _require_raw_length(raw, width, height, channels)
    out = bytearray(height * stride)
    prev = bytearray(stride)
    src = 0
    dst = 0
    for row in range(height):
        ftype = raw[src]
        src += 1
        line = bytearray(raw[src : src + stride])
        src += stride
        if ftype == 1:
            for c in range(channels):
                line[c::channels] = _prefix_sum(line[c::channels])
        elif ftype == 2:
            line = _byte_add(line, prev)
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            table = _paeth_delta_table()
            # A predictor only ever references same-channel neighbours, so the
            # channels unfilter independently and can be done one at a time.
            # Iterating each channel's stream with ``zip`` lets the left
            # neighbour be a carried local instead of a ``line[i - channels]``
            # read, and appending the reconstructed bytes to a list avoids a
            # per-byte ``line[i] = ...`` store; the result is byte-identical
            # and roughly a third faster than the interleaved loop.
            for c in range(channels):
                filtered = line[c::channels]
                above = prev[c::channels]
                # The first pixel of a row has no left or above-left neighbour,
                # so the predictor is just the above byte.
                left = (filtered[0] + above[0]) & 0xFF
                unfiltered = [left]
                for value, up, upleft in zip(filtered[1:], above[1:], above):
                    da = left - upleft + 255
                    db = up - upleft + 255
                    left = (value + upleft + table[(da << 9) + db]) & 0xFF
                    unfiltered.append(left)
                line[c::channels] = bytes(unfiltered)
        elif ftype != 0:
            raise PngError(
                f"unsupported PNG filter type {ftype} in row {row}"
            )
        out[dst : dst + stride] = line
        dst += stride
        prev = line
    return bytes(out)


def _drop_alpha(raw: bytes, width: int, height: int) -> bytes:
    """Return ``raw`` with the alpha byte of every pixel removed.

    PNG filters reference only same-channel neighbours, so an alpha byte never
    influences a colour channel's predictor.  Removing alpha before
    unfiltering lets a colour-type-6 image unfilter as three channels instead
    of four and leaves the result already RGB -- the dropped bytes are the
    ones ``_to_rgb`` used to strip after the fact.  The filter-type byte at the
    start of each scanline is kept.
    """
    _require_raw_length(raw, width, height, 4)
    stride = width * 4
    out = bytearray(height * (width * 3 + 1))
    src = 0
    dst = 0
    for _ in range(height):
        out[dst] = raw[src]
        src += 1
        dst += 1
        line = bytearray(raw[src : src + stride])
        del line[3::4]
        out[dst : dst + width * 3] = line
        src += stride
        dst += width * 3
    return bytes(out)


def _to_rgb(color_type: int, samples: bytes, palette: bytes | None) -> bytes:
    if color_type == 2:  # truecolor RGB
        return samples
    if color_type == 0:  # grayscale
        return bytes(b for g in samples for b in (g, g, g))
    if color_type == 4:  # grayscale + alpha, alpha ignored
        return bytes(b for i in range(0, len(samples), 2) for b in (samples[i],) * 3)
    if color_type == 3:  # palette
        if palette is None:
            raise PngError("palette PNG has no PLTE chunk")
        entries = len(palette) // 3
        # Expand indices at C speed: index a table of 3-byte entries and join,
        # instead of a Python loop concatenating a slice per pixel. An
        # out-of-range index raises IndexError from that lookup, so the
        # all-in-range case -- the common one -- needs no separate pass to
        # validate every index before expanding it.
        table = [palette[i * 3 : i * 3 + 3] for i in range(entries)]
        try:
            return b"".join(map(table.__getitem__, samples))
        except IndexError:
            # An out-of-range index must still name the first offending index
            # and the palette size; only this failure path scans for it. The
            # sibling PLTE-length error counts entries, so name the entry
            # count here as well as the byte count.
            entry_word = "entry" if entries == 1 else "entries"
            for index in samples:
                if index >= entries:
                    raise PngError(
                        f"palette PNG index {index} is outside PLTE "
                        f"(palette has {entries} {entry_word} in "
                        f"{len(palette)} bytes)"
                    ) from None
            raise
    raise PngError(f"unsupported PNG color type {color_type}")


def decode_png(data: bytes) -> Image:
    """Decode an 8-bit, non-interlaced PNG into an :class:`Image`."""
    if not data.startswith(PNG_MAGIC):
        detected = other_image_format(data)
        if detected is not None:
            raise PngError(
                f"not a PNG file: the input is a {detected} image, not a PNG; "
                "convert it to PNG first"
            )
        raise PngError("not a PNG file")
    header = None
    palette = None
    idat = bytearray()
    saw_iend = False
    for ctype, payload in _iter_chunks(data):
        if ctype == b"IHDR":
            header = payload
        elif ctype == b"PLTE":
            if len(payload) % 3 or not 3 <= len(payload) <= 768:
                raise PngError(
                    f"PLTE chunk is {len(payload)} bytes; expected a multiple "
                    "of 3 between 3 and 768 (1-256 palette entries)"
                )
            palette = payload
        elif ctype == b"IDAT":
            idat += payload
        elif ctype == b"IEND":
            saw_iend = True
            break
        elif ctype[:1].isupper():
            # A chunk whose first byte is uppercase is critical: the decoder
            # must understand it to know how the image is interpreted. The
            # four critical chunks (IHDR, PLTE, IDAT, IEND) are all modelled
            # above, so an unknown one carries data that may change the
            # pixels. Ignoring it the way an unknown *ancillary* chunk
            # (lowercase first byte) is ignored could decode the image wrong
            # with no sign that anything was skipped, so refuse it by name.
            raise PngError(
                f"unknown critical PNG chunk {_chunk_name(ctype)}"
            )
    if header is None:
        raise PngError("PNG has no IHDR chunk")
    if len(header) != 13:
        raise PngError(
            f"IHDR chunk has {len(header)} bytes, expected 13"
        )
    if not saw_iend:
        # The IEND chunk terminates the chunk stream, so a file cut at a
        # chunk boundary can hold a complete IHDR and IDAT and still be
        # truncated. Without this the decoder returns the image from the
        # partial stream as if the file were whole.
        raise PngError(
            "PNG has no IEND chunk (the chunk stream may be truncated)"
        )
    width, height, depth, color_type, compression, filt, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if depth != 8:
        raise PngError(f"unsupported PNG bit depth {depth} (need 8)")
    if interlace != 0:
        raise PngError("interlaced PNG is not supported")
    if compression != 0:
        raise PngError(
            f"unsupported PNG compression method {compression} (need 0)"
        )
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in _CHANNELS:
        raise PngError(f"unsupported PNG color type {color_type}")
    if width == 0 or height == 0:
        # Name the declared dimensions so the operator can tell which field is
        # zero (and in which header) instead of having to dump the bytes.
        raise PngError(
            f"PNG header declares zero width or height: {width}x{height}; "
            "both dimensions must be positive"
        )
    channels = _CHANNELS[color_type]
    # Bound the work by the header before zlib sees any data: reject an image
    # too large to be a screenshot, then decompress at most the exact unfiltered
    # byte count the header declares, so an oversized stream cannot be expanded.
    if width * height > _MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {_MAX_PIXELS}-pixel limit"
        )
    expected_raw = height * (width * channels + 1)
    if not idat:
        # A PNG truncated before its IDAT chunk, or one whose IDAT is empty,
        # reaches zlib with no compressed data; zlib then reports an opaque
        # "incomplete or truncated stream" that names neither the chunk nor
        # the missing data.
        raise PngError("PNG has no IDAT image data")
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(bytes(idat), expected_raw)
    except zlib.error as exc:
        raise PngError(f"corrupt PNG image data: {exc}") from exc
    if decompressor.unconsumed_tail:
        raise PngError(
            f"PNG image data decompresses to more than the {expected_raw} bytes "
            f"its {width}x{height} header declares"
        )
    if not decompressor.eof:
        # A stream cut before its end marker can still yield exactly
        # expected_raw bytes; without this the adler32 trailer that
        # zlib.decompress used to verify would be dropped silently.
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
        )
    if color_type == 6:
        # Alpha is discarded and the result is already RGB, so unfilter the
        # three colour channels directly instead of all four.
        samples = _unfilter(_drop_alpha(raw, width, height), width, height, 3)
        return Image(width, height, samples)
    samples = _unfilter(raw, width, height, channels)
    return Image(width, height, _to_rgb(color_type, samples, palette))


def read_png(path: str | Path) -> Image:
    """Read and decode the PNG at *path*, naming it in any :class:`PngError`."""
    # Open with O_NONBLOCK so a path naming a pipe (FIFO) cannot block in
    # open() waiting for a writer; a regular file is unaffected. The byte cap
    # below bounds memory but not time: read() on a pipe whose writer stays
    # open without sending data blocks forever. Reject any non-regular file
    # (pipe, device) outright. fstat on the open fd also avoids a stat/open
    # race where a regular file is swapped for a FIFO between the two.
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as exc:
        raise PngError(f"cannot read {path}: {exc}") from exc
    try:
        file_stat = os.fstat(fd)
        if not stat.S_ISREG(file_stat.st_mode):
            raise PngError(f"cannot read {path}: not a regular file")
        # Read at most one byte past the cap: enough to detect an oversize
        # file without loading the rest of it.
        with os.fdopen(fd, "rb") as handle:
            fd = -1
            data = handle.read(_MAX_FILE_BYTES + 1)
    except OSError as exc:
        raise PngError(f"cannot read {path}: {exc}") from exc
    finally:
        if fd >= 0:
            os.close(fd)
    if len(data) > _MAX_FILE_BYTES:
        # fstat on the already-open fd names the file's size without a second
        # path lookup, so an operator can see how far over the cap it is
        # instead of only the cap itself.
        raise PngError(
            f"cannot read {path}: file is {file_stat.st_size} bytes, larger "
            f"than the {_MAX_FILE_BYTES}-byte limit"
        )
    if data.startswith(LFS_POINTER_MAGIC):
        raise PngError(
            f"cannot decode {path}: the file is an unmaterialized Git LFS "
            "pointer, not image data; run `git lfs pull` to fetch it"
        )
    try:
        return decode_png(data)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc

