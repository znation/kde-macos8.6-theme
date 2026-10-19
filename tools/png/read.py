"""The PNG decode pipeline and file reader.

Decodes 8-bit, non-interlaced PNG images (color types 0, 2, 3, 4 and 6) into
tightly packed RGB bytes, using only the Python standard library. This module
holds the decode pipeline (header validation, bounds, inflate, color
expansion) and :func:`read_png`; the pieces it is built from live in sibling
modules: ``tools/png/image.py`` (``PngError``, ``Image``, ``pixel_at``),
``tools/png/chunks.py`` (chunk framing), ``tools/png/scanlines.py``
(unfiltering) and ``tools/png/filters.py`` (the Sub/Up lane arithmetic and
Paeth delta table). ``tools/png/write.py`` is its minimal inverse, and
``tools/png/__init__.py`` re-exports this module's public names.

The CLI in ``tools/fidelity.py``, the sampler in ``tools/sample.py``, the
renderer in ``tools/render_surface.py`` and the wallpaper generator in
``tools/make_wallpaper.py`` read PNGs through it today; keeping the reader
separate lets each do so without pulling in the comparison and CLI layers.

Raises :class:`PngError` for a malformed or unsupported PNG.
"""

from __future__ import annotations

import os
import stat
import struct
import zlib
from pathlib import Path

try:
    from tools.image_format import (
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        other_image_format,
    )
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from image_format import (
        LFS_POINTER_MAGIC,
        PNG_MAGIC,
        other_image_format,
    )
    from ints import is_plain_int

from .chunks import chunk_name, iter_chunks
from .image import Image, PngError
from .scanlines import drop_alpha, raw_byte_length, unfilter

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
            index = next(i for i in samples if i >= entries)
            raise _palette_index_error(index, entries, len(palette)) from None
    raise PngError(f"unsupported PNG color type {color_type}")


def _palette_index_error(index: int, entries: int, palette_bytes: int) -> PngError:
    """Build the error for the first out-of-range palette *index*.

    The sibling PLTE-length error counts entries, so this one names the entry
    count as well as the byte count.
    """
    entry_word = "entry" if entries == 1 else "entries"
    return PngError(
        f"palette PNG index {index} is outside PLTE "
        f"(palette has {entries} {entry_word} in {palette_bytes} bytes)"
    )


def _validate_max_rows(max_rows: int | None) -> None:
    """Raise :class:`PngError` unless *max_rows* is None or a positive int.

    ``bool`` is rejected even though it is an ``int`` subclass: ``True`` would
    pass as 1 and silently select a different row bound. This lives apart from
    :func:`decode_png` so a caller that serves an already-decoded image (the
    test reference cache) can apply the same bound check without decoding.
    """
    if max_rows is None:
        return
    if not is_plain_int(max_rows):
        raise PngError(
            f"max_rows must be an integer or None: max_rows={max_rows!r}"
        )
    if max_rows < 1:
        raise PngError(f"max_rows must be positive: max_rows={max_rows}")


def decode_png(data: bytes, max_rows: int | None = None) -> Image:
    """Decode an 8-bit, non-interlaced PNG into an :class:`Image`.

    When *max_rows* is given, the returned image is at most that many rows
    tall and holds only the top rows of the PNG. The whole compressed stream
    is still inflated and validated (its length, end marker and adler32), and
    every scanline's filter type is still checked; the bound skips only the
    per-byte unfilter work for the rows past it.
    """
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
    for ctype, payload in iter_chunks(data):
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
                f"unknown critical PNG chunk {chunk_name(ctype)}"
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
        raise PngError(
            "interlaced PNG is not supported; re-export it without "
            "interlacing"
        )
    if compression != 0:
        raise PngError(
            f"unsupported PNG compression method {compression} (need 0)"
        )
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in _CHANNELS:
        # Name the set the decoder handles, the way the bit-depth,
        # compression and filter messages name their required value, so the
        # operator does not have to look up which PNG color types are valid.
        supported = ", ".join(str(value) for value in sorted(_CHANNELS))
        raise PngError(
            f"unsupported PNG color type {color_type} "
            f"(need one of {supported})"
        )
    if width == 0 or height == 0:
        # Name the declared dimensions so the operator can tell which field is
        # zero (and in which header) instead of having to dump the bytes.
        raise PngError(
            f"PNG header declares zero width or height: {width}x{height}; "
            "both dimensions must be positive"
        )
    _validate_max_rows(max_rows)
    rows = height if max_rows is None else min(max_rows, height)
    channels = _CHANNELS[color_type]
    # Bound the work by the header before zlib sees any data: reject an image
    # too large to be a screenshot, then decompress at most the exact unfiltered
    # byte count the header declares, so an oversized stream cannot be expanded.
    if width * height > _MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {_MAX_PIXELS}-pixel limit"
        )
    expected_raw = raw_byte_length(width, height, channels)
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
        # expected_raw bytes; without this its adler32 trailer would go
        # unverified silently.
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
        )
    if color_type == 6:
        # Alpha is discarded and the result is already RGB, so unfilter the
        # three colour channels directly instead of all four.
        samples = unfilter(
            drop_alpha(raw, width, height), width, height, 3, rows
        )
        return Image(width, rows, samples)
    samples = unfilter(raw, width, height, channels, rows)
    return Image(width, rows, _to_rgb(color_type, samples, palette))


def read_png(path: str | Path, max_rows: int | None = None) -> Image:
    """Read and decode the PNG at *path*, naming it in any :class:`PngError`.

    *max_rows* is forwarded to :func:`decode_png`: the returned image holds at
    most that many top scanlines.
    """
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
        return decode_png(data, max_rows)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc
