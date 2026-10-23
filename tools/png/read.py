"""The PNG decode pipeline.

Decodes 8-bit, non-interlaced PNG images (color types 0, 2, 3, 4 and 6) into
tightly packed RGB bytes (:func:`decode_png`) or RGBA bytes
(:func:`decode_rgba`), using only the Python standard library. The RGBA path
also applies a ``tRNS`` chunk's transparency for the color types that store it
out of band. This module
holds the decode pipeline (header validation, bounds, inflate and color
expansion); the file reader that loads a path and applies the file-level
guards is :func:`tools.png.loader.read_png`, and
:func:`tools.png.loader.read_png_size` shares those guards but returns only
the declared dimensions. The pieces the decoder is built from live in sibling
modules: ``tools/png/image.py`` (``PngError``, ``Image``, ``pixel_at``),
``tools/png/chunks.py`` (chunk framing), ``tools/png/scanlines.py``
(unfiltering) and ``tools/png/filters.py`` (the Sub/Up lane arithmetic and
Paeth delta table). ``tools/png/write.py`` is its minimal inverse, and
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

import struct
import zlib

try:
    from tools.image_format import PNG_MAGIC, other_image_format
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from image_format import PNG_MAGIC, other_image_format
    from ints import is_plain_int

from .chunks import chunk_name, iter_chunks
from .image import Image, PngError
from .scanlines import drop_alpha, raw_byte_length, unfilter

# color_type -> channels per pixel at bit depth 8
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}

# Cap on declared pixels. A PNG's IDAT can be arbitrarily smaller than the
# scanlines it expands to, so a few KB can demand gigabytes (a decompression
# bomb). 64 MP is far above any screenshot this tool compares and still bounds
# one decode to a few hundred MB.
_MAX_PIXELS = 64_000_000


def _to_rgb(color_type: int, samples: bytes, palette: bytes | None) -> bytes:
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


def _validate_max_rows(max_rows: int | None) -> None:
    """Raise :class:`PngError` unless *max_rows* is None or a positive int.

    ``bool`` is rejected even though it is an ``int`` subclass: ``True`` would
    pass as 1 and silently select a different row bound. This lives apart from
    :func:`decode_png` so a caller that serves an already-decoded image (the
    test reference cache) can apply the same bound check without decoding.
    """
    if max_rows is None:
        return
    if not is_plain_int(max_rows):
        raise PngError(
            f"max_rows must be an integer or None: max_rows={max_rows!r}"
        )
    if max_rows < 1:
        raise PngError(f"max_rows must be positive: max_rows={max_rows}")


def _parse_ihdr(header: bytes) -> tuple[int, int, int]:
    """Validate a 13-byte IHDR payload, returning ``(width, height, color_type)``.

    Both :func:`decode_png` and :func:`tools.png.loader.read_png_size` use this
    so a size-only read rejects the same malformed or unsupported headers the
    decoder does.
    """
    if len(header) != 13:
        raise PngError(
            f"IHDR chunk has {len(header)} bytes, expected 13"
        )
    width, height, depth, color_type, compression, filt, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if depth != 8:
        raise PngError(f"unsupported PNG bit depth {depth} (need 8)")
    if interlace != 0:
        raise PngError(
            "interlaced PNG is not supported; re-export it without "
            "interlacing"
        )
    if compression != 0:
        raise PngError(
            f"unsupported PNG compression method {compression} (need 0)"
        )
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in _CHANNELS:
        # Name the set the decoder handles, the way the bit-depth,
        # compression and filter messages name their required value, so the
        # operator does not have to look up which PNG color types are valid.
        supported = ", ".join(str(value) for value in sorted(_CHANNELS))
        raise PngError(
            f"unsupported PNG color type {color_type} "
            f"(need one of {supported})"
        )
    if width == 0 or height == 0:
        # Name the declared dimensions so the operator can tell which field is
        # zero (and in which header) instead of having to dump the bytes.
        raise PngError(
            f"PNG header declares zero width or height: {width}x{height}; "
            "both dimensions must be positive"
        )
    return width, height, color_type


def _check_pixel_limit(width: int, height: int) -> None:
    if width * height > _MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {_MAX_PIXELS}-pixel limit"
        )


def _take_ihdr(
    payload: bytes, header: bytes | None, previous_chunk: bytes | None
) -> bytes:
    """Return *payload* as the image header, refusing a misordered IHDR.

    *previous_chunk* is the first chunk already seen, or None when this is
    the first chunk. The PNG spec gives the image exactly one header and puts
    it first; a stream that reaches IDAT before its header, or carries a
    second IHDR, would otherwise decode against a header a conformant reader
    would not use and silently produce different pixels.
    """
    if header is not None:
        raise PngError(
            "PNG has more than one IHDR chunk; the image header "
            "must appear exactly once"
        )
    if previous_chunk is not None:
        raise PngError(
            f"PNG's IHDR chunk must be the first chunk, but "
            f"{chunk_name(previous_chunk)} comes before it"
        )
    return payload


def _take_plte(payload: bytes) -> bytes:
    """Return *payload* as the palette, refusing a malformed PLTE length."""
    if len(payload) % 3 or not 3 <= len(payload) <= 768:
        raise PngError(
            f"PLTE chunk is {len(payload)} bytes; expected a multiple "
            "of 3 between 3 and 768 (1-256 palette entries)"
        )
    return payload


def _collect_chunks(
    data: bytes,
) -> tuple[bytes, bytes | None, bytearray, bytes | None]:
    """Return ``(header, palette, idat, trns)`` from *data*'s chunk stream.

    Walks the chunks after the signature, collecting the image header, palette,
    IDAT payloads and the optional tRNS transparency payload. It refuses a
    misordered or duplicate IHDR, a malformed PLTE length, an unknown critical
    chunk, a missing IEND and a missing IHDR. Filtering and colour expansion
    are the decoders' concern; this helper owns only the framing the rest of
    the decode reads.
    """
    header = None
    palette = None
    trns = None
    idat = bytearray()
    saw_iend = False
    first_chunk = None
    for ctype, payload in iter_chunks(data):
        # Record the first chunk before handling it, but pass the previous
        # value to the IHDR guard: the first chunk is allowed to be IHDR, while
        # a later one is not.
        previous_first = first_chunk
        if first_chunk is None:
            first_chunk = ctype
        if ctype == b"IHDR":
            header = _take_ihdr(payload, header, previous_first)
            continue
        if ctype == b"PLTE":
            palette = _take_plte(payload)
            continue
        if ctype == b"tRNS":
            # tRNS is ancillary, but it changes what the pixels mean for the
            # three non-alpha colour types, so it must be collected rather
            # than skipped with the other unknown ancillary chunks. Colour
            # types 4 and 6 carry their transparency in the pixel itself, so
            # :func:`decode_rgba` ignores it for those.
            trns = payload
            continue
        if ctype == b"IDAT":
            idat += payload
            continue
        if ctype == b"IEND":
            saw_iend = True
            break
        if ctype[:1].isupper():
            # A chunk whose first byte is uppercase is critical: the decoder
            # must understand it to know how the image is interpreted. The
            # four critical chunks (IHDR, PLTE, IDAT, IEND) are all modelled
            # above, so an unknown one carries data that may change the
            # pixels. Ignoring it the way an unknown *ancillary* chunk
            # (lowercase first byte) is ignored could decode the image wrong
            # with no sign that anything was skipped, so refuse it by name.
            raise PngError(
                f"unknown critical PNG chunk {chunk_name(ctype)}"
            )
    if header is None:
        raise PngError("PNG has no IHDR chunk")
    if not saw_iend:
        # The IEND chunk terminates the chunk stream, so a file cut at a
        # chunk boundary can hold a complete IHDR and IDAT and still be
        # truncated. Without this the decoder returns the image from the
        # partial stream as if the file were whole.
        raise PngError(
            "PNG has no IEND chunk (the chunk stream may be truncated)"
        )
    return header, palette, idat, trns


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
    if not isinstance(data, (bytes, bytearray)):
        raise PngError(
            f"decode_png data must be bytes or bytearray, not "
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
    header, palette, idat, _trns = _collect_chunks(data)
    width, height, color_type = _parse_ihdr(header)
    _validate_max_rows(max_rows)
    rows = height if max_rows is None else min(max_rows, height)
    channels = _CHANNELS[color_type]
    # Bound the work by the header before zlib sees any data: reject an image
    # too large to be a screenshot, then decompress at most the exact unfiltered
    # byte count the header declares, so an oversized stream cannot be expanded.
    _check_pixel_limit(width, height)
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
    if not decompressor.eof:
        # A stream cut before its end marker can still yield exactly
        # expected_raw bytes; without this its adler32 trailer would go
        # unverified silently.
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
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
        rgb = _to_rgb(color_type, samples, palette)
        return Image(width, rows, rgb[: rows * width * 3])
    samples = unfilter(raw, width, height, channels, rows)
    return Image(width, rows, _to_rgb(color_type, samples, palette))


def _palette_trns_alphas(trns: bytes | None, entries: int) -> bytes:
    """Return one alpha byte per palette entry, applying a ``tRNS`` chunk.

    A palette ``tRNS`` chunk names alphas only for its first entries; a shorter
    chunk leaves the remaining entries opaque. An empty chunk, or one longer
    than the palette, cannot describe a palette entry, so it is refused by
    length instead of ignored.
    """
    if trns is None:
        return b"\xff" * entries
    if not 1 <= len(trns) <= entries:
        raise PngError(
            f"tRNS chunk has {len(trns)} bytes; a palette PNG with "
            f"{entries} entries needs 1 to {entries}"
        )
    return trns + b"\xff" * (entries - len(trns))


def _sample_trns_key(
    trns: bytes | None, color_type: int
) -> int | tuple[int, ...] | None:
    """Return the sample value a greyscale or truecolor ``tRNS`` names.

    Color type 0 names one 16-bit greyscale sample, color type 2 three 16-bit
    samples (red, green, blue); a pixel equal to that value is transparent.
    ``None`` means the image has no tRNS and every pixel is opaque.
    """
    if trns is None:
        return None
    expected = 2 if color_type == 0 else 6
    if len(trns) != expected:
        name = "greyscale" if color_type == 0 else "truecolor"
        raise PngError(
            f"tRNS chunk has {len(trns)} bytes; a {name} PNG (color type "
            f"{color_type}) needs exactly {expected}"
        )
    if color_type == 0:
        return struct.unpack(">H", trns)[0]
    return struct.unpack(">HHH", trns)


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
    expanded. ``height`` in the result is the number of rows returned.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise PngError(
            f"decode_rgba data must be bytes or bytearray, not "
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
    header, palette, idat, trns = _collect_chunks(data)
    width, height, color_type = _parse_ihdr(header)
    _validate_max_rows(max_rows)
    rows = height if max_rows is None else min(max_rows, height)
    channels = _CHANNELS[color_type]
    _check_pixel_limit(width, height)
    expected_raw = raw_byte_length(width, height, channels)
    if not idat:
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
    if not decompressor.eof:
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
        )
    if color_type == 3:
        if palette is None:
            raise PngError("palette PNG has no PLTE chunk")
        samples = unfilter(raw, width, height, channels)
        rgb = _to_rgb(color_type, samples, palette)
        alphas = _palette_trns_alphas(trns, len(palette) // 3)
        rgb = rgb[: rows * width * 3]
        out = bytearray()
        for i in range(0, len(rgb), 3):
            index = samples[i // 3]
            out += rgb[i:i + 3] + alphas[index:index + 1]
        return width, rows, bytes(out)
    samples = unfilter(raw, width, height, channels, rows)
    if color_type == 6:
        rgba = samples
    elif color_type == 4:
        out = bytearray()
        for i in range(0, len(samples), 2):
            g = samples[i]
            a = samples[i + 1]
            out += bytes((g, g, g, a))
        rgba = bytes(out)
    elif color_type == 2:
        key = _sample_trns_key(trns, color_type)
        out = bytearray()
        for i in range(0, len(samples), 3):
            pixel = samples[i:i + 3]
            alpha = 0 if key is not None and tuple(pixel) == key else 255
            out += pixel + bytes((alpha,))
        rgba = bytes(out)
    elif color_type == 0:
        key = _sample_trns_key(trns, color_type)
        out = bytearray()
        for g in samples:
            out += bytes((g, g, g, 0 if g == key else 255))
        rgba = bytes(out)
    else:
        raise PngError(f"unsupported PNG color type {color_type}")
    return width, rows, rgba
