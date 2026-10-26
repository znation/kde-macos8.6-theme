"""The PNG file reader: load a path and read its image.

:func:`read_png` applies the file-level guards before the byte-level decoder in
``tools/png/read.py`` sees the data: it opens without blocking so a FIFO cannot
hang ``open()``, rejects any non-regular file, bounds the read with
``_MAX_FILE_BYTES``, and names an unmaterialized Git LFS pointer instead of
letting :func:`decode_png` report it as "not a PNG file". :func:`read_rgba`
uses the same guards and decodes the image into packed RGBA bytes; passing
``alpha=True`` to :func:`read_png` does the same and splits them into an
:class:`Image`'s colour and alpha planes.
:func:`read_png_size`
uses the same guards but reads only a header-sized prefix, returning the
declared ``(width, height)`` without decoding rows or loading a large file.
Decoding itself lives in
``read.py`` (inflate), ``stream.py`` (chunk-stream and header validation) and
``expand.py`` (color expansion).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

try:
    from tools.image_format import LFS_POINTER_MAGIC, PNG_MAGIC
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from image_format import LFS_POINTER_MAGIC, PNG_MAGIC

from .chunks import iter_chunks
from .image import Image, PngError
from .read import decode_png, decode_rgba
from .stream import check_pixel_limit, parse_ihdr

# Cap on the bytes read_png will load from disk. decode_png bounds the decoded
# image by its pixel limit, but read_png reads the whole file before decode_png
# sees the header, and a path can name a file far larger than any screenshot,
# so without a read cap a few bytes of argv can demand unbounded memory. 512
# MiB is generous for screenshot-sized inputs while keeping one read on the
# same order as the decoder's own worst-case allocation for the largest image
# it accepts.
_MAX_FILE_BYTES = 512 * 1024 * 1024

# A PNG signature plus one complete chunk header, a 13-byte IHDR payload and
# its CRC: enough for iter_chunks and parse_ihdr to validate the size without
# reading a single image row.
_HEADER_PREFIX_BYTES = len(PNG_MAGIC) + 4 + 4 + 13 + 4


def _read_png_data(
    path: str | Path, *, prefix_bytes: int | None = None
) -> bytes:
    """Read the PNG at *path* under the file guards of :func:`read_png`.

    With *prefix_bytes*, only that many leading bytes are read, after the
    file's stat size is checked against the same cap a whole read applies.
    :func:`read_png_size` uses this so reporting a large screenshot's declared
    size does not load the whole file.
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
        # A whole read stops at one byte past the cap: enough to detect an
        # oversize file without loading the rest of it. A prefix read is
        # bounded by its caller and relies on the fstat size checked below.
        with os.fdopen(fd, "rb") as handle:
            fd = -1
            if prefix_bytes is None:
                data = handle.read(_MAX_FILE_BYTES + 1)
            else:
                data = handle.read(prefix_bytes)
    except OSError as exc:
        raise PngError(f"cannot read {path}: {exc}") from exc
    finally:
        if fd >= 0:
            os.close(fd)
    if len(data) > _MAX_FILE_BYTES or (
        prefix_bytes is not None and file_stat.st_size > _MAX_FILE_BYTES
    ):
        # fstat on the already-open fd names the file's size without a second
        # path lookup, so an operator can see how far over the cap it is
        # instead of only the cap itself. A prefix read checks the stat size
        # before reading, so it keeps refusing an oversize file even though it
        # never loads enough bytes to see the overrun itself.
        raise PngError(
            f"cannot read {path}: file is {file_stat.st_size} bytes, larger "
            f"than the {_MAX_FILE_BYTES}-byte limit"
        )
    if data.startswith(LFS_POINTER_MAGIC):
        raise PngError(
            f"cannot decode {path}: the file is an unmaterialized Git LFS "
            "pointer, not image data; run `git lfs pull` to fetch it"
        )
    return data


def _image_with_alpha(width: int, height: int, rgba: bytes) -> Image:
    """Split packed RGBA bytes into an :class:`Image`'s colour and alpha planes."""
    rgb = bytearray(width * height * 3)
    rgb[0::3] = rgba[0::4]
    rgb[1::3] = rgba[1::4]
    rgb[2::3] = rgba[2::4]
    return Image(width, height, bytes(rgb), rgba[3::4])


def read_png(
    path: str | Path,
    max_rows: int | None = None,
    max_cols: int | None = None,
    *,
    alpha: bool = False,
) -> Image:
    """Read and decode the PNG at *path*, naming it in any :class:`PngError`.

    *max_rows* and *max_cols* are forwarded to :func:`decode_png`: the
    returned image holds at most that many top scanlines and left columns.
    With *alpha* true the image is decoded
    through :func:`decode_rgba` instead, so the returned image's alpha plane
    holds each pixel's transparency (including a ``tRNS`` chunk's) and its
    RGB plane holds the same colour bytes; the default returns the RGB-only
    image as before.
    """
    data = _read_png_data(path)
    try:
        if alpha:
            width, height, rgba = decode_rgba(data, max_rows, max_cols)
            return _image_with_alpha(width, height, rgba)
        return decode_png(data, max_rows, max_cols)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc


def read_rgba(
    path: str | Path,
    max_rows: int | None = None,
    max_cols: int | None = None,
) -> tuple[int, int, bytes]:
    """Read and decode the PNG at *path* into packed RGBA bytes."""
    data = _read_png_data(path)
    try:
        return decode_rgba(data, max_rows, max_cols)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc


def read_png_size(path: str | Path) -> tuple[int, int]:
    """Return the ``(width, height)`` a PNG declares without decoding its rows.

    Only the header prefix is read, so a caller that samples a few top rows
    can learn the full image size without loading a large file, then bound
    its decode with ``read_png(path, max_rows=...)``. A file that cannot be
    read, or whose IHDR chunk is malformed or unsupported, raises
    :class:`PngError` naming *path*.
    """
    data = _read_png_data(path, prefix_bytes=_HEADER_PREFIX_BYTES)
    if data.startswith(PNG_MAGIC):
        # Walking the first chunk validates its framing and CRC; parse_ihdr
        # then applies the same field checks decode_png does. The prefix can
        # end inside a first chunk that declares more than an IHDR payload
        # (a misordered chunk), so a framing error there falls through to the
        # full read, which yields the canonical decoder diagnosis.
        try:
            first = next(iter_chunks(data), None)
        except PngError:
            first = None
        if first is not None and first[0] == b"IHDR":
            try:
                width, height, _ = parse_ihdr(first[1])
                check_pixel_limit(width, height)
            except PngError as exc:
                raise PngError(f"cannot decode {path}: {exc}") from exc
            return width, height
    # Fall back to the full read and the decoder so a file whose first chunk
    # is not IHDR gets the same diagnostic read_png would produce; it rejects
    # before unfiltering.
    data = _read_png_data(path)
    try:
        decode_png(data)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc
    raise PngError(
        f"cannot decode {path}: PNG has no readable IHDR chunk"
    )
