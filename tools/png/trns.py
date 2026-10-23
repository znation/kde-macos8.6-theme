"""tRNS payload length rules shared by chunk validation and color expansion.

The PNG spec gives a ``tRNS`` chunk one form per color type: one 16-bit sample
for greyscale, three for truecolor, and one alpha byte per palette entry for
palette images. :func:`check_sample_trns_length` refuses the two sample forms
at any other length, and :func:`check_palette_trns_length` refuses a palette
form that names no entry or more entries than the palette has. Both the
chunk-stream validator and the color expander call them, so the same malformed
payload gets the same diagnosis on the RGB and RGBA decode paths.
"""

from __future__ import annotations

from .image import PngError

# tRNS payload length for the two color types that name a transparent sample
# value; a palette image uses one alpha byte per palette entry instead.
_TRNS_SAMPLE_LENGTHS = {0: 2, 2: 6}


def check_palette_trns_length(trns: bytes, entries: int) -> None:
    """Refuse a palette ``tRNS`` that names no entry or too many entries."""
    if not 1 <= len(trns) <= entries:
        raise PngError(
            f"tRNS chunk has {len(trns)} bytes; a palette PNG with "
            f"{entries} entries needs 1 to {entries}"
        )


def check_sample_trns_length(trns: bytes, color_type: int) -> None:
    """Refuse a greyscale or truecolor ``tRNS`` of the wrong length."""
    expected = _TRNS_SAMPLE_LENGTHS[color_type]
    if len(trns) != expected:
        name = "greyscale" if color_type == 0 else "truecolor"
        raise PngError(
            f"tRNS chunk has {len(trns)} bytes; a {name} PNG (color type "
            f"{color_type}) needs exactly {expected}"
        )
