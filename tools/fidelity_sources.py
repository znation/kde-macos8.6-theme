"""Guarded PNG input loading for the fidelity comparison CLI.

A reference or candidate named as a JPEG is decoded once through the
sampler's shared convert bridge (``tools/jpeg_convert.py``) into a private
temporary PNG and then read exactly like any PNG input, so the reference
set's JPEG screenshots are comparable directly. Every other format keeps
the PNG loader's own diagnostics.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

if __package__:
    from tools.containment import open_regular_binary, require_within_repo
    from tools.fidelity_geometry import FidelityError
    from tools.jpeg_convert import convert_jpeg, is_jpeg
    from tools.png import PngError, read_png
    from tools.repo_root import ROOT
else:  # imported by direct execution of tools/fidelity.py
    from containment import open_regular_binary, require_within_repo
    from fidelity_geometry import FidelityError
    from jpeg_convert import convert_jpeg, is_jpeg
    from png import PngError, read_png
    from repo_root import ROOT

# The sniff reads exactly the bytes ``is_jpeg`` needs; three bytes are
# also enough that an unmaterialized Git LFS pointer or an empty file
# never looks like a JPEG.
_SNIFF_BYTES = 3


def read_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Read a PNG with alpha, bounding decoded rows when a crop allows it.

    Sideways overflow is retried without a row bound so the crop diagnostic
    retains the image's real dimensions. Vertical overflow is left bounded;
    the PNG decoder clamps the bound to the image height.

    A JPEG input is sniffed by its first bytes and decoded once through
    ImageMagick into a private temporary PNG; every diagnostic on the JPEG
    branch names the path the operator gave, never the temporary file.
    """
    require_within_repo(path, ROOT)
    head = _sniff_head(path)
    if head is not None and is_jpeg(head):
        return _read_jpeg_source(path, crop_rect)
    return _read_png_source(path, crop_rect)


def _sniff_head(path: str) -> bytes | None:
    """Return the file's leading bytes, or None when they cannot be read.

    An absent, unreadable, or non-regular path falls through to the PNG
    branch so ``read_png`` keeps producing its own diagnostic for it; the
    non-blocking open matches ``read_png``'s own guard, so a FIFO path
    cannot block the sniff waiting for a writer.
    """
    return _read_bytes(path, _SNIFF_BYTES)


def _read_jpeg_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Decode a JPEG input through the convert bridge and read the PNG.

    The decoded PNG lives in a private temporary directory of this call's
    own, dropped when the call returns; nothing is written next to the
    input. ``convert_jpeg`` already scrubs its own temporary paths from
    converter logs, and any decode failure's message has the temporary
    PNG's path rewritten to the given path before it escapes.
    """
    jpeg = _read_bytes(path, -1)
    if jpeg is None:
        # The file vanished, became unreadable, or became non-regular
        # between the sniff and this read: fall through to the PNG
        # branch, whose open produces the standing diagnostic for it.
        return _read_png_source(path, crop_rect)
    directory = tempfile.mkdtemp(prefix="fidelity-jpeg-")
    try:
        temp_png = Path(directory) / "decoded.png"
        problem = convert_jpeg(jpeg, temp_png)
        if problem is not None:
            raise FidelityError(f"cannot decode {path}: {problem}")
        try:
            return _decode(str(temp_png), crop_rect)
        except PngError as exc:
            raise PngError(str(exc).replace(str(temp_png), path)) from exc
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def _read_bytes(path: str, count: int) -> bytes | None:
    """Return at most *count* leading bytes, or None when they cannot be read.

    A negative *count* reads the file whole. The path is opened through
    :func:`containment.open_regular_binary`, the same non-blocking open and
    regular-file check ``read_png`` uses, so a pipe, device or vanished path
    falls through to the PNG branch instead of blocking or raising here.
    """
    try:
        with open_regular_binary(path) as handle:
            if count < 0:
                return handle.read()
            return handle.read(count)
    except (OSError, ValueError):
        return None


def _read_png_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Read the PNG at *path* with the standing bounded-decode policy."""
    return _decode(path, crop_rect)


def _decode(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Decode *path* once with the crop-aware row bound and retry policy."""
    if crop_rect is None:
        return read_png(path, alpha=True)
    x, y, width, height = crop_rect
    image = read_png(path, max_rows=y + height, alpha=True)
    if x + width > image.width:
        return read_png(path, alpha=True)
    return image
