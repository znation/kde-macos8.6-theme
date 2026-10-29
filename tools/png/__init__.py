"""The PNG codec's public interface.

Reads 8-bit, non-interlaced PNG images into tightly packed RGB or RGBA bytes
and writes 8-bit RGB or RGBA images back to PNG, using only the Python
standard library.
The pieces are split by concern and re-exported here, so a consumer imports a
public name from ``tools.png`` regardless of which submodule defines it:
``tools/png/image.py`` holds :class:`Image`, :class:`PngError` and
:func:`pixel_at`, ``tools/png/loader.py`` the file reader :func:`read_png`,
:func:`read_png_size` and :func:`read_rgba`, ``tools/png/read.py`` the decode
pipeline :func:`decode_png` and :func:`decode_rgba`, and
``tools/png/write.py`` the inverses :func:`encode_png` and
:func:`encode_rgba_png`.
``tools/png/chunks.py``, ``tools/png/stream.py``, ``tools/png/header.py``,
``tools/png/trns.py``, ``tools/png/scanlines.py``, ``tools/png/expand.py`` and
``tools/png/filters.py`` hold the chunk framing, chunk ordering and collection,
header validation, tRNS length rules, unfiltering,
color expansion and filter arithmetic those are built from.
"""

from __future__ import annotations

from .image import Image, PngError, pixel_at
from .loader import read_png, read_png_size, read_rgba
from .read import decode_png, decode_rgba
from .write import encode_png, encode_rgba_png

__all__ = [
    "Image",
    "PngError",
    "decode_png",
    "decode_rgba",
    "encode_png",
    "encode_rgba_png",
    "pixel_at",
    "read_png",
    "read_rgba",
    "read_png_size",
]
