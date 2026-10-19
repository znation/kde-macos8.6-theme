"""The PNG codec's public interface.

Reads 8-bit, non-interlaced PNG images into tightly packed RGB bytes and
writes 8-bit RGB images back to PNG, using only the Python standard library.
The pieces are split by concern and re-exported here, so a consumer imports a
public name from ``tools.png`` regardless of which submodule defines it:
``tools/png/image.py`` holds :class:`Image`, :class:`PngError` and
:func:`pixel_at`, ``tools/png/read.py`` the decode pipeline and
:func:`read_png`, and ``tools/png/write.py`` the inverse :func:`encode_png`.
``tools/png/chunks.py``, ``tools/png/scanlines.py`` and ``tools/png/filters.py``
hold the chunk framing, unfiltering and filter arithmetic those are built from.
"""

from __future__ import annotations

from .image import Image, PngError, pixel_at
from .read import decode_png, read_png
from .write import encode_png

__all__ = [
    "Image",
    "PngError",
    "decode_png",
    "encode_png",
    "pixel_at",
    "read_png",
]
