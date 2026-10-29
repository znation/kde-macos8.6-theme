"""PNG header and decode-limit validation shared by both readers."""

from __future__ import annotations

import struct

try:
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from ints import is_plain_int

from .image import PngError
from .trns import check_palette_trns_length, check_sample_trns_length

# color_type -> channels per pixel at bit depth 8
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}

# Bound declared pixels before allocating decoded scanlines.
MAX_PIXELS = 64_000_000


def validate_max_rows(max_rows: int | None) -> None:
    """Raise :class:`PngError` unless *max_rows* is None or a positive int."""
    if max_rows is None:
        return
    if not is_plain_int(max_rows):
        raise PngError(f"max_rows must be an integer or None: max_rows={max_rows!r}")
    if max_rows < 1:
        raise PngError(f"max_rows must be positive: max_rows={max_rows}")


def validate_max_cols(max_cols: int | None) -> None:
    """Raise :class:`PngError` unless *max_cols* is None or a positive int."""
    if max_cols is None:
        return
    if not is_plain_int(max_cols):
        raise PngError(f"max_cols must be an integer or None: max_cols={max_cols!r}")
    if max_cols < 1:
        raise PngError(f"max_cols must be positive: max_cols={max_cols}")


def parse_ihdr(header: bytes) -> tuple[int, int, int]:
    """Validate IHDR, returning ``(width, height, color_type)``."""
    if len(header) != 13:
        raise PngError(f"IHDR chunk has {len(header)} bytes, expected 13")
    width, height, depth, color_type, compression, filt, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if depth != 8:
        raise PngError(f"unsupported PNG bit depth {depth} (need 8)")
    if interlace != 0:
        raise PngError("interlaced PNG is not supported; re-export it without interlacing")
    if compression != 0:
        raise PngError(f"unsupported PNG compression method {compression} (need 0)")
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in CHANNELS:
        supported = ", ".join(str(value) for value in sorted(CHANNELS))
        raise PngError(
            f"unsupported PNG color type {color_type} (need one of {supported})"
        )
    if width == 0 or height == 0:
        raise PngError(
            f"PNG header declares zero width or height: {width}x{height}; "
            "both dimensions must be positive"
        )
    return width, height, color_type


def check_trns(
    trns: bytes | None,
    color_type: int,
    palette: bytes | None,
    trns_before_plte: bool = False,
) -> None:
    """Refuse a tRNS payload the header's color type and palette cannot carry."""
    if trns is None:
        return
    if color_type in (4, 6):
        raise PngError(
            f"PNG has a tRNS chunk, but color type {color_type} carries "
            "transparency in each pixel; tRNS is only valid for color types 0, 2 and 3"
        )
    if color_type == 3 and palette is None:
        return
    if trns_before_plte and palette is not None:
        raise PngError("PNG has a tRNS chunk before its PLTE chunk; tRNS must follow the PLTE chunk, if any")
    if color_type == 3:
        check_palette_trns_length(trns, len(palette) // 3)
        return
    check_sample_trns_length(trns, color_type)


def check_plte(palette: bytes | None, color_type: int) -> None:
    """Refuse a palette the header's color type does not permit."""
    if palette is None or color_type in (2, 3, 6):
        return
    raise PngError(
        f"PNG has a PLTE chunk, but color type {color_type} is greyscale; "
        "PLTE is prohibited for the greyscale color types 0 and 4"
    )


def check_pixel_limit(width: int, height: int) -> None:
    """Raise :class:`PngError` when the declared image exceeds ``MAX_PIXELS``."""
    if width * height > MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {MAX_PIXELS}-pixel limit"
        )
