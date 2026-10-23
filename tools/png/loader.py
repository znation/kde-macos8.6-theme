"""The PNG file reader: load a path and read its image.

:func:`read_png` applies the file-level guards before the byte-level decoder in
``tools/png/read.py`` sees the data: it opens without blocking so a FIFO cannot
hang ``open()``, rejects any non-regular file, bounds the read with
``_MAX_FILE_BYTES``, and names an unmaterialized Git LFS pointer instead of
letting :func:`decode_png` report it as "not a PNG file". :func:`read_rgba`
uses the same guards and decodes the image into packed RGBA bytes.
:func:`read_png_size`
uses the same guards but inspects only the IHDR chunk, returning the declared
``(width, height)`` without decoding rows. Decoding itself -- header
validation, inflate and color expansion -- lives in ``read.py``.
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
from .read import _check_pixel_limit, _parse_ihdr, decode_png, decode_rgba

# Cap on the bytes read_png will load from disk. decode_png bounds the decoded
# image by its pixel limit, but read_png reads the whole file before decode_png
# sees the header, and a path can name a file far larger than any screenshot,
# so without a read cap a few bytes of argv can demand unbounded memory. 512
# MiB is generous for screenshot-sized inputs while keeping one read on the
# same order as the decoder's own worst-case allocation for the largest image
# it accepts.
_MAX_FILE_BYTES = 512 * 1024 * 1024


def _read_png_data(path: str | Path) -> bytes:
    """Read the whole PNG at *path* under the file guards of :func:`read_png`."""
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
    return data


def read_png(path: str | Path, max_rows: int | None = None) -> Image:
    """Read and decode the PNG at *path*, naming it in any :class:`PngError`.

    *max_rows* is forwarded to :func:`decode_png`: the returned image holds at
    most that many top scanlines.
    """
    data = _read_png_data(path)
    try:
        return decode_png(data, max_rows)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc


def read_rgba(path: str | Path, max_rows: int | None = None) -> tuple[int, int, bytes]:
    """Read and decode the PNG at *path* into packed RGBA bytes."""
    data = _read_png_data(path)
    try:
        return decode_rgba(data, max_rows)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc


def read_png_size(path: str | Path) -> tuple[int, int]:
    """Return the ``(width, height)`` a PNG declares without decoding its rows.

    Only the first chunk (IHDR) is inspected, so a caller that samples a few
    top rows can learn the full image size and then bound its decode with
    ``read_png(path, max_rows=...)``. A file that cannot be read, or whose
    IHDR chunk is malformed or unsupported, raises :class:`PngError` naming
    *path*.
    """
    data = _read_png_data(path)
    if data.startswith(PNG_MAGIC):
        # Walking the first chunk validates its framing and CRC; _parse_ihdr
        # then applies the same field checks decode_png does.
        try:
            first = next(iter_chunks(data), None)
        except PngError as exc:
            raise PngError(f"cannot decode {path}: {exc}") from exc
        if first is not None and first[0] == b"IHDR":
            try:
                width, height, _ = _parse_ihdr(first[1])
                _check_pixel_limit(width, height)
            except PngError as exc:
                raise PngError(f"cannot decode {path}: {exc}") from exc
            return width, height
    # Fall back to the decoder so a file whose first chunk is not IHDR gets
    # the same diagnostic read_png would produce; it rejects before
    # unfiltering.
    try:
        decode_png(data)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc
    raise PngError(
        f"cannot decode {path}: PNG has no readable IHDR chunk"
    )
