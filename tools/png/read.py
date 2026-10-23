"""The PNG decode pipeline.

Decodes 8-bit, non-interlaced PNG images (color types 0, 2, 3, 4 and 6) into
tightly packed RGB bytes (:func:`decode_png`) or RGBA bytes
(:func:`decode_rgba`), using only the Python standard library. The RGBA path
also applies a ``tRNS`` chunk's transparency for the color types that store it
out of band; both paths refuse a ``tRNS`` chunk the header's color type or
palette cannot carry, even though the RGB path discards alpha, and both refuse
a ``PLTE`` chunk the header's greyscale color type can never use. This module
holds the decode pipeline (inflate and row handling); the chunk-stream and
header validation it reads first lives in ``tools/png/stream.py``, and the
color expansion from unfiltered samples to RGB or RGBA lives in
``tools/png/expand.py``. The file reader that loads a path and applies the
file-level guards is :func:`tools.png.loader.read_png`, and
:func:`tools.png.loader.read_png_size` shares those guards but returns only
the declared dimensions. The pieces the decoder is built from live in sibling
modules: ``tools/png/image.py`` (``PngError``, ``Image``, ``pixel_at``),
``tools/png/stream.py`` (chunk-stream and header validation),
``tools/png/chunks.py`` (chunk framing), ``tools/png/scanlines.py``
(unfiltering), ``tools/png/expand.py`` (color expansion) and
``tools/png/filters.py`` (the Sub/Up lane arithmetic and Paeth delta table).
``tools/png/write.py`` is its minimal inverse, and
``tools/png/__init__.py`` re-exports the public names.

The CLI in ``tools/fidelity.py``, the sampler in ``tools/sample.py``, the
renderer in ``tools/render_surface.py`` and the wallpaper generator in
``tools/make_wallpaper.py`` load PNGs through
:func:`tools.png.loader.read_png`; the decode pipeline here stays independent
of the filesystem, so a caller that already holds the bytes can pass them
straight to :func:`decode_png`.

Raises :class:`PngError` for a malformed or unsupported PNG.
"""

from __future__ import annotations

import zlib

try:
    from tools.image_format import PNG_MAGIC, other_image_format
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from image_format import PNG_MAGIC, other_image_format

from .expand import (
    greyscale_rgba,
    palette_rgba,
    sample_trns_key,
    to_rgb,
    truecolor_rgba,
)
from .image import Image, PngError
from .scanlines import drop_alpha, raw_byte_length, unfilter
from .stream import (
    CHANNELS,
    check_pixel_limit,
    check_plte,
    check_trns,
    collect_chunks,
    parse_ihdr,
    validate_max_rows,
)


def _decode_image(
    data: bytes, max_rows: int | None, name: str
) -> tuple[int, int, int, int, int, bytes, bytes | None, bytes | None]:
    """Validate and inflate *data*, returning the pieces both decoders share.

    The result is ``(width, height, color_type, channels, rows, raw, palette,
    trns)``: the declared image geometry, the number of rows the caller asked
    for, the unfiltered-declared byte count's inflated stream, and the palette
    and tRNS payloads (or None). *name* is the public decoder's name, used in
    the entry-guard error it raises, so each decoder still names itself.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise PngError(
            f"{name} data must be bytes or bytearray, not "
            f"{type(data).__name__}"
        )
    data = bytes(data)
    if not data.startswith(PNG_MAGIC):
        detected = other_image_format(data)
        if detected is not None:
            raise PngError(
                f"not a PNG file: the input is a {detected} image, not a PNG; "
                "convert it to PNG first"
            )
        raise PngError("not a PNG file")
    header, palette, idat, trns, trns_before_plte = collect_chunks(data)
    width, height, color_type = parse_ihdr(header)
    check_plte(palette, color_type)
    check_trns(trns, color_type, palette, trns_before_plte)
    validate_max_rows(max_rows)
    rows = height if max_rows is None else min(max_rows, height)
    channels = CHANNELS[color_type]
    # Bound the work by the header before zlib sees any data: reject an image
    # too large to be a screenshot, then decompress at most the exact unfiltered
    # byte count the header declares, so an oversized stream cannot be expanded.
    check_pixel_limit(width, height)
    expected_raw = raw_byte_length(width, height, channels)
    if not idat:
        # A PNG truncated before its IDAT chunk, or one whose IDAT is empty,
        # reaches zlib with no compressed data; zlib then reports an opaque
        # "incomplete or truncated stream" that names neither the chunk nor
        # the missing data.
        raise PngError("PNG has no IDAT image data")
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(bytes(idat), expected_raw)
    except zlib.error as exc:
        raise PngError(f"corrupt PNG image data: {exc}") from exc
    if decompressor.unconsumed_tail:
        raise PngError(
            f"PNG image data decompresses to more than the {expected_raw} bytes "
            f"its {width}x{height} header declares"
        )
    if decompressor.unused_data:
        # IDAT holds exactly one zlib stream. Once its end marker is reached,
        # any remaining bytes are not image data; zlib keeps them in
        # unused_data instead of failing, so refusing them here keeps a
        # malformed PNG from carrying a payload the decoder silently drops.
        count = len(decompressor.unused_data)
        raise PngError(
            f"PNG image data has {count} trailing "
            f"byte{'s' if count != 1 else ''} after the zlib stream"
        )
    if not decompressor.eof:
        # A stream cut before its end marker can still yield exactly
        # expected_raw bytes; without this its adler32 trailer would go
        # unverified silently.
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
        )
    return width, height, color_type, channels, rows, raw, palette, trns


def decode_png(data: bytes, max_rows: int | None = None) -> Image:
    """Decode an 8-bit, non-interlaced PNG into an :class:`Image`.

    When *max_rows* is given, the returned image is at most that many rows
    tall and holds only the top rows of the PNG. The whole compressed stream
    is still inflated and validated (its length, end marker and adler32), and
    every scanline's filter type is still checked; the bound skips only the
    per-byte unfilter work for the rows past it. A palette image is the
    exception: every row is expanded, because that lookup also validates each
    index and an out-of-range index below the bound is still a malformed PNG.
    """
    width, height, color_type, channels, rows, raw, palette, _trns = (
        _decode_image(data, max_rows, "decode_png")
    )
    if color_type == 6:
        # Alpha is discarded and the result is already RGB, so unfilter the
        # three colour channels directly instead of all four.
        samples = unfilter(
            drop_alpha(raw, width, height), width, height, 3, rows
        )
        return Image(width, rows, samples)
    if color_type == 3:
        # The palette lookup validates each index, so expanding only the rows
        # the caller asked for would let an out-of-range index below the bound
        # pass as a valid image. Expand every row, then return the top ones.
        samples = unfilter(raw, width, height, channels)
        rgb = to_rgb(color_type, samples, palette)
        return Image(width, rows, rgb[: rows * width * 3])
    samples = unfilter(raw, width, height, channels, rows)
    return Image(width, rows, to_rgb(color_type, samples, palette))


def decode_rgba(data: bytes, max_rows: int | None = None) -> tuple[int, int, bytes]:
    """Decode an 8-bit, non-interlaced PNG into packed RGBA bytes.

    The result is ``(width, height, rgba)`` where *rgba* holds
    ``width * height * 4`` bytes in row order. A tRNS chunk's transparency is
    applied for the palette, greyscale and truecolor color types, so a PNG
    whose transparency lives in that chunk decodes with the same alpha as one
    that stores it per pixel; the alpha color types (4 and 6) already carry
    it.

    *max_rows* bounds the returned rows as :func:`decode_png` does: the whole
    compressed stream is still inflated and validated, every scanline's filter
    type is still checked, and a palette image's every index is still
    validated. ``height`` in the result is the number of rows returned.
    """
    width, height, color_type, channels, rows, raw, palette, trns = (
        _decode_image(data, max_rows, "decode_rgba")
    )
    if color_type == 3:
        if palette is None:
            raise PngError("palette PNG has no PLTE chunk")
        samples = unfilter(raw, width, height, channels)
        return width, rows, palette_rgba(samples, palette, trns, width, rows)
    samples = unfilter(raw, width, height, channels, rows)
    if color_type == 6:
        rgba = samples
    elif color_type == 4:
        grey = samples[0::2]
        out = bytearray(len(grey) * 4)
        out[0::4] = grey
        out[1::4] = grey
        out[2::4] = grey
        out[3::4] = samples[1::2]
        rgba = bytes(out)
    elif color_type == 2:
        rgba = truecolor_rgba(samples, sample_trns_key(trns, color_type))
    elif color_type == 0:
        rgba = greyscale_rgba(samples, sample_trns_key(trns, color_type))
    else:
        raise PngError(f"unsupported PNG color type {color_type}")
    return width, rows, rgba
