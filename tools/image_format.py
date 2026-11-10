"""The raster-format signatures the tools recognize by their leading bytes.

``tools/png/read.py`` names a wrong-format file when
:func:`tools.png.read.decode_png` is handed one, and ``tools/reference_validation.py``
decides whether a file on disk is an
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

# Stream-terminator bytes each format must end with. PNG writes a final
# zero-length IEND chunk whose CRC is constant; JPEG ends with the EOI
# marker; GIF ends with its single trailer byte. WebP instead ends by
# keeping its declared RIFF size, which :func:`is_complete` bounds.
TERMINAL_PNG = b"\x00\x00\x00\x00IEND\xaeB`\x82"
TERMINAL_JPEG = b"\xff\xd9"
TERMINAL_GIF = b";"

# First line of an unmaterialized Git LFS pointer file; a real image never
# starts with this text. The reference screenshots are stored with Git LFS, so
# a fresh clone that has not run ``git lfs pull`` hands the tools a small text
# pointer under an image name.
LFS_POINTER_MAGIC = b"version https://git-lfs.github.com/spec/v1"

# WebP is a RIFF container; the ``WEBP`` fourcc at bytes 8-11 is what makes a
# RIFF payload an image rather than, say, a WAVE sound.
_RIFF_MAGIC = b"RIFF"
_WEBP_FOURCC = b"WEBP"


def _require_bytes(data: bytes | bytearray, name: str) -> None:
    """Reject non-byte inputs with the public detector's diagnostic format."""
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError(
            f"{name} data must be bytes or bytearray, not "
            f"{type(data).__name__}"
        )


def is_webp(data: bytes | bytearray) -> bool:
    """Return True when *data* begins with the RIFF/WEBP container signature."""
    _require_bytes(data, "is_webp")
    return data[:4] == _RIFF_MAGIC and data[8:12] == _WEBP_FOURCC


def image_stream_format(head: bytes | bytearray) -> str | None:
    """Name the raster format *head*'s leading bytes identify, or ``None``.

    Complements :func:`other_image_format` with PNG so a diagnostic can name
    the stream whose ending is being judged. Only the leading bytes decide,
    never a file extension: ``sherlock_fandom.jpg`` is a WebP stream here too.
    """
    _require_bytes(head, "image_stream_format")
    if head.startswith(PNG_MAGIC):
        return "PNG"
    if head.startswith(JPEG_MAGIC):
        return "JPEG"
    if any(head.startswith(magic) for magic in GIF_MAGICS):
        return "GIF"
    if is_webp(head):
        return "WebP"
    return None


def is_complete(
    head: bytes | bytearray, tail: bytes | bytearray, size: int
) -> bool:
    """Return True when the stream *head* identifies ends at *size*.

    *head* holds the file's leading bytes and *tail* its last bytes (at
    least as many as the longest terminator; a small file may pass fewer);
    *size* is the file's byte length. This is a bounded structural check,
    not a decode, so a download cut inside a valid-looking body still fails
    wherever its signature survives: PNG must end with its zero-length IEND
    chunk (trailer and constant CRC), JPEG with the EOI marker, GIF with the
    trailer byte, and WebP with its declared RIFF size actually held.
    """
    _require_bytes(head, "is_complete")
    _require_bytes(tail, "is_complete")
    stream = image_stream_format(head)
    if stream == "PNG":
        return tail[-len(TERMINAL_PNG):] == TERMINAL_PNG
    if stream == "JPEG":
        return tail[-len(TERMINAL_JPEG):] == TERMINAL_JPEG
    if stream == "GIF":
        return tail[-len(TERMINAL_GIF):] == TERMINAL_GIF
    # WebP: RIFF stores the chunk-group size at bytes 4-7; the stream is
    # complete when that plus the 8-byte RIFF header matches the file size.
    if stream == "WebP":
        return int.from_bytes(head[4:8], "little") + 8 == size
    return False


def is_image(data: bytes | bytearray) -> bool:
    """Return True when *data* begins with a known raster image signature.

    PNG, JPEG, GIF and WebP are recognized; only the leading bytes decide,
    never a file extension.
    """
    _require_bytes(data, "is_image")
    return any(data.startswith(magic) for magic in IMAGE_MAGICS) or is_webp(data)


def other_image_format(data: bytes | bytearray) -> str | None:
    """Return the non-PNG raster format *data* starts with, or ``None``.

    Names the formats the reference set uses besides PNG (JPEG, GIF and WebP)
    so a decode failure can say which wrong file was passed instead of only
    "not a PNG file".
    """
    _require_bytes(data, "other_image_format")
    if data.startswith(JPEG_MAGIC):
        return "JPEG"
    if any(data.startswith(magic) for magic in GIF_MAGICS):
        return "GIF"
    if is_webp(data):
        return "WebP"
    return None
