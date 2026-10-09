"""The raster-format signatures the tools recognize by their leading bytes.

``tools/png.py`` names a wrong-format file when :func:`decode_png` is handed
one, and ``tools/check_references.py`` decides whether a file on disk is an
image at all. Both recognize the same formats from the same signatures, so the
signatures and the detection live here once instead of in each tool, where
they could drift apart.

The extension is deliberately never consulted: the reference set's
``sherlock_fandom.jpg`` is a WebP payload.
"""

from __future__ import annotations

# Leading bytes of the raster formats the reference set uses.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
GIF_MAGICS = (b"GIF87a", b"GIF89a")
IMAGE_MAGICS = (PNG_MAGIC, JPEG_MAGIC, *GIF_MAGICS)

# First line of an unmaterialized Git LFS pointer file; a real image never
# starts with this text. The reference screenshots are stored with Git LFS, so
# a fresh clone that has not run ``git lfs pull`` hands the tools a small text
# pointer under an image name.
LFS_POINTER_MAGIC = b"version https://git-lfs.github.com/spec/v1"

# WebP is a RIFF container; the ``WEBP`` fourcc at bytes 8-11 is what makes a
# RIFF payload an image rather than, say, a WAVE sound.
_RIFF_MAGIC = b"RIFF"
_WEBP_FOURCC = b"WEBP"


def is_webp(data: bytes) -> bool:
    """Return True when *data* begins with the RIFF/WEBP container signature."""
    return data[:4] == _RIFF_MAGIC and data[8:12] == _WEBP_FOURCC


def is_image(data: bytes) -> bool:
    """Return True when *data* begins with a known raster image signature.

    PNG, JPEG, GIF and WebP are recognized; only the leading bytes decide,
    never a file extension.
    """
    return any(data.startswith(magic) for magic in IMAGE_MAGICS) or is_webp(data)


def other_image_format(data: bytes) -> str | None:
    """Return the non-PNG raster format *data* starts with, or ``None``.

    Names the formats the reference set uses besides PNG (JPEG, GIF and WebP)
    so a decode failure can say which wrong file was passed instead of only
    "not a PNG file".
    """
    if data.startswith(JPEG_MAGIC):
        return "JPEG"
    if any(data.startswith(magic) for magic in GIF_MAGICS):
        return "GIF"
    if is_webp(data):
        return "WebP"
    return None
