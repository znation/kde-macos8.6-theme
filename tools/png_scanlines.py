"""PNG scanline handling: declared-size checks, unfiltering, alpha removal.

Turns the inflated IDAT bytes (one filter-type byte plus the filtered samples
per row) into plain samples. The Sub/Up lane arithmetic and Paeth delta table
live in ``tools/png_filters.py``; the chunk framing in ``tools/png_chunks.py``
and the color-type expansion in ``tools/png.py``.
"""

from __future__ import annotations

if __package__:
    from tools.png_filters import _byte_add, _paeth_delta_table, _prefix_sum
    from tools.png_image import PngError
else:  # run as a top-level module, e.g. imported by tools/png.py
    from png_filters import _byte_add, _paeth_delta_table, _prefix_sum
    from png_image import PngError


def raw_byte_length(width: int, height: int, channels: int) -> int:
    """Return the unfiltered byte count the header declares.

    Every one of *height* scanlines holds *width* pixels of *channels*
    samples plus one leading filter-type byte, so a stream shorter than this
    is truncated. Both the decode-time decompression bound and the later
    length check derive the declared size from this one formula, so they
    cannot disagree about it.
    """
    return height * (width * channels + 1)


def _require_raw_length(raw: bytes, width: int, height: int, channels: int) -> None:
    """Reject scanline data shorter than the header's declared size."""
    expected = raw_byte_length(width, height, channels)
    if len(raw) < expected:
        raise PngError(
            f"PNG image data is shorter than its header declares: got "
            f"{len(raw)} bytes, expected {expected} for a {width}x{height} image"
        )


def unfilter(
    raw: bytes,
    width: int,
    height: int,
    channels: int,
    max_rows: int | None = None,
) -> bytes:
    """Unfilter scanlines, returning at most *max_rows* rows of samples.

    Every scanline's filter type is validated, but when a bound is given only
    the first *max_rows* rows are actually unfiltered: the per-byte predictor
    work is what dominates decoding a large screenshot, so a caller that reads
    only its top rows skips that work for the rest without giving up the
    filter-type check. The returned bytes are ``max_rows * width * channels``
    long (or the whole image when no bound is given).
    """
    stride = width * channels
    _require_raw_length(raw, width, height, channels)
    rows = height if max_rows is None else min(max_rows, height)
    out = bytearray(rows * stride)
    prev = bytearray(stride)
    src = 0
    dst = 0
    for row in range(height):
        ftype = raw[src]
        src += 1
        if ftype > 4:
            raise PngError(
                f"unsupported PNG filter type {ftype} in row {row}"
            )
        if row >= rows:
            # Past the requested bound: the filter type above is still
            # checked, but the predictor work is skipped.
            src += stride
            continue
        line = bytearray(raw[src : src + stride])
        src += stride
        if ftype == 1:
            for c in range(channels):
                line[c::channels] = _prefix_sum(line[c::channels])
        elif ftype == 2:
            line = _byte_add(line, prev)
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            _unfilter_paeth(line, prev, channels)
        out[dst : dst + stride] = line
        dst += stride
        prev = line
    return bytes(out)


def _unfilter_paeth(line: bytearray, prev: bytearray, channels: int) -> None:
    """Undo the Paeth filter on *line* in place, given the previous row *prev*.

    A predictor only ever references same-channel neighbours, so the
    channels unfilter independently and can be done one at a time.
    Iterating each channel's stream with ``zip`` lets the left neighbour be a
    carried local instead of a ``line[i - channels]`` read, and appending the
    reconstructed bytes to a list avoids a per-byte ``line[i] = ...`` store.
    """
    table = _paeth_delta_table()
    for c in range(channels):
        filtered = line[c::channels]
        above = prev[c::channels]
        # The first pixel of a row has no left or above-left neighbour, so the
        # predictor is just the above byte.
        left = (filtered[0] + above[0]) & 0xFF
        unfiltered = [left]
        for value, up, upleft in zip(filtered[1:], above[1:], above):
            da = left - upleft + 255
            db = up - upleft + 255
            left = (value + upleft + table[(da << 9) + db]) & 0xFF
            unfiltered.append(left)
        line[c::channels] = bytes(unfiltered)


def drop_alpha(raw: bytes, width: int, height: int) -> bytes:
    """Return ``raw`` with the alpha byte of every pixel removed.

    PNG filters reference only same-channel neighbours, so an alpha byte never
    influences a colour channel's predictor.  Removing alpha before
    unfiltering lets a colour-type-6 image unfilter as three channels instead
    of four and leaves the result already RGB, so ``png._to_rgb`` has no
    colour-type-6 case.  The filter-type byte at the start of each scanline is
    kept.
    """
    _require_raw_length(raw, width, height, 4)
    stride = width * 4
    out = bytearray(height * (width * 3 + 1))
    src = 0
    dst = 0
    for _ in range(height):
        out[dst] = raw[src]
        src += 1
        dst += 1
        line = bytearray(raw[src : src + stride])
        del line[3::4]
        out[dst : dst + width * 3] = line
        src += stride
        dst += width * 3
    return bytes(out)
