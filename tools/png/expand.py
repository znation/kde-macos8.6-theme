"""Color expansion: turn unfiltered PNG samples into RGB or RGBA bytes.

:func:`tools.png.read.decode_png` and :func:`tools.png.read.decode_rgba` share
the chunk-stream and inflate half of the decode; this module is their second
half. It expands the unfiltered samples the decoders produce into the shape
each one returns: packed RGB for the opaque decoder, and packed RGBA for the
decoder that keeps or derives an alpha channel. A ``tRNS`` chunk's
transparency is applied here for the palette, greyscale and truecolor types,
the three families that can store alpha out of band.

The module works on bytes already in memory and knows nothing about chunk
framing or the file system, so a caller that holds samples can use it
directly. :func:`to_rgb` expands the RGB path, :func:`greyscale_rgba`,
:func:`truecolor_rgba` and :func:`palette_rgba` expand the RGBA path, and
:func:`sample_trns_key` reads the greyscale and truecolor ``tRNS`` forms those
helpers match against.
"""

from __future__ import annotations

import struct

from .image import PngError
from .trns import check_palette_trns_length, check_sample_trns_length


def to_rgb(color_type: int, samples: bytes, palette: bytes | None) -> bytes:
    """Expand unfiltered *samples* of *color_type* into packed RGB bytes.

    Color types 2 (truecolor), 0 (greyscale), 3 (palette, using *palette*)
    and 4 (greyscale with alpha, which is dropped) are supported; any other
    type raises :class:`PngError`.
    """
    if color_type == 2:  # truecolor RGB
        return samples
    if color_type == 0:  # greyscale
        return bytes(b for g in samples for b in (g, g, g))
    if color_type == 4:  # greyscale + alpha, alpha ignored
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


def _palette_trns_alphas(trns: bytes | None, entries: int) -> bytes:
    """Return one alpha byte per palette entry, applying a ``tRNS`` chunk.

    A palette ``tRNS`` chunk names alphas only for its first entries; a shorter
    chunk leaves the remaining entries opaque. An empty chunk, or one longer
    than the palette, cannot describe a palette entry, so it is refused by
    length instead of ignored.
    """
    if trns is None:
        return b"\xff" * entries
    check_palette_trns_length(trns, entries)
    return trns + b"\xff" * (entries - len(trns))


def sample_trns_key(
    trns: bytes | None, color_type: int
) -> int | tuple[int, ...] | None:
    """Return the sample value a greyscale or truecolor ``tRNS`` names.

    Color type 0 names one 16-bit greyscale sample, color type 2 three 16-bit
    samples (red, green, blue); a pixel equal to that value is transparent.
    ``None`` means the image has no tRNS and every pixel is opaque.
    """
    if trns is None:
        return None
    check_sample_trns_length(trns, color_type)
    if color_type == 0:
        return struct.unpack(">H", trns)[0]
    return struct.unpack(">HHH", trns)


def _interleave_alpha(rgb: bytes, alpha: bytes) -> bytes:
    """Interleave 3-byte RGB pixels with one *alpha* byte per pixel.

    Each channel and the alpha plane are gathered with a strided slice and
    written back with another, so the whole expansion runs in C. A per-pixel
    Python loop built the same bytes one ``+=`` at a time and dominated a
    truecolor decode.
    """
    pixels = len(rgb) // 3
    out = bytearray(pixels * 4)
    out[0::4] = rgb[0::3]
    out[1::4] = rgb[1::3]
    out[2::4] = rgb[2::3]
    out[3::4] = alpha
    return bytes(out)


def greyscale_rgba(grey: bytes, key: int | None) -> bytes:
    """Expand greyscale *grey* to RGBA, transparent where it equals *key*."""
    pixels = len(grey)
    if key is None:
        alpha = b"\xff" * pixels
    else:
        # A tRNS grey sample names a 16-bit value; for an 8-bit image only
        # 0-255 can match a pixel, and the table leaves the rest opaque.
        alpha = grey.translate(
            bytes(0 if value == key else 255 for value in range(256))
        )
    out = bytearray(pixels * 4)
    out[0::4] = grey
    out[1::4] = grey
    out[2::4] = grey
    out[3::4] = alpha
    return bytes(out)


# Alpha for a whole-pixel tRNS key match: index 0 is an opaque pixel, index 1
# a matching (transparent) one.
_MATCH_ALPHA = bytes(0 if value == 1 else 255 for value in range(256))
# Marking dense key matches by scanning each channel is cheaper than one
# Python ``find`` per occurrence once a match falls in every 32 pixels; below
# that the per-occurrence loop wins.
_DENSE_MATCHES_PER_PIXEL = 32


def _match_table(value: int) -> bytes:
    """Return a translation table with 1 at *value* and 0 at every other byte."""
    table = bytearray(256)
    table[value] = 1
    return bytes(table)


def truecolor_rgba(rgb: bytes, key: tuple[int, ...] | None) -> bytes:
    """Expand truecolor *rgb* to RGBA, transparent where a pixel equals *key*."""
    pixels = len(rgb) // 3
    if key is None or any(value > 255 for value in key):
        # A 16-bit sample above 255 cannot equal an 8-bit pixel value.
        return _interleave_alpha(rgb, b"\xff" * pixels)
    key_bytes = bytes(key)
    occurrences = rgb.count(key_bytes)
    if occurrences == 0:
        return _interleave_alpha(rgb, b"\xff" * pixels)
    if occurrences * _DENSE_MATCHES_PER_PIXEL >= pixels:
        # Three C-level ``translate`` passes mark each channel's key bytes, a
        # big-integer AND keeps the lanes where all three match, and one more
        # ``translate`` turns those lanes into alpha. The per-occurrence
        # ``find`` loop below is one Python iteration per match, which
        # dominated an image whose tRNS key fills most of the frame.
        match = int.from_bytes(
            rgb[0::3].translate(_match_table(key[0])), "little"
        )
        match &= int.from_bytes(
            rgb[1::3].translate(_match_table(key[1])), "little"
        )
        match &= int.from_bytes(
            rgb[2::3].translate(_match_table(key[2])), "little"
        )
        alpha = match.to_bytes(pixels, "little").translate(_MATCH_ALPHA)
        return _interleave_alpha(rgb, alpha)
    alpha = bytearray(b"\xff" * pixels)
    start = 0
    while True:
        # Find each key occurrence in C; only a match starting on a pixel
        # boundary (a multiple of 3) names a transparent pixel.
        index = rgb.find(key_bytes, start)
        if index < 0:
            break
        if index % 3 == 0:
            alpha[index // 3] = 0
        start = index + 1
    return _interleave_alpha(rgb, bytes(alpha))


def palette_rgba(
    samples: bytes,
    palette: bytes,
    trns: bytes | None,
    width: int,
    rows: int,
) -> bytes:
    """Expand palette *samples* to RGBA, applying *trns* alphas.

    Every index is validated even past the returned *rows* bound, matching
    the RGB decoder: a malformed index below the bound must not pass as a
    valid image.
    """
    entries = len(palette) // 3
    if samples and max(samples) >= entries:
        index = next(i for i in samples if i >= entries)
        raise _palette_index_error(index, entries, len(palette))
    alphas = _palette_trns_alphas(trns, entries)
    table = [
        palette[i * 3 : i * 3 + 3] + alphas[i : i + 1] for i in range(entries)
    ]
    return b"".join(map(table.__getitem__, samples[: rows * width]))
