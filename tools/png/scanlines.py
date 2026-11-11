"""PNG scanline handling: declared-size checks, unfiltering, alpha removal.

Turns the inflated IDAT bytes (one filter-type byte plus the filtered samples
per row) into plain samples. The Sub/Up lane arithmetic and Paeth delta table
live in ``tools/png/filters.py``; the chunk framing in ``tools/png/chunks.py``
and the color-type expansion in ``tools/png/expand.py``.
"""

from __future__ import annotations

import functools

from .filters import byte_add, paeth_delta_rows, prefix_sum
from .image import PngError


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


def _unfilter_line(
    ftype: int, line: bytearray, prev: bytearray, channels: int
) -> bytes | bytearray:
    """Undo filter *ftype* on one scanline *line*, given the previous row.

    The caller has already rejected a filter type above 4, so no branch here
    validates it. Sub and Up dispatch to the lane arithmetic, Average is a
    per-byte predictor, and Paeth mutates *line* in place. Filter type 0
    leaves the line unchanged.
    """
    if ftype == 0:
        return line
    if ftype == 1:
        for c in range(channels):
            line[c::channels] = prefix_sum(line[c::channels])
        return line
    if ftype == 2:
        return byte_add(line, prev)
    if ftype == 3:
        _unfilter_average(line, prev, channels)
        return line
    _unfilter_paeth(line, prev, channels)
    return line


@functools.cache
def _average_rows() -> tuple[bytes, ...]:
    """Return ``rows[left][up]``, the Average predictor ``(left + up) >> 1``.

    Indexing a precomputed row replaces the shift and the add per byte, so
    the Average loop does one row lookup and one index per sample.
    """
    return tuple(
        bytes((left + up) >> 1 for up in range(256)) for left in range(256)
    )


def _unfilter_average(line: bytearray, prev: bytearray, channels: int) -> None:
    """Undo the Average filter in place, one colour lane at a time.

    Each sample's left neighbour is the reconstructed sample *channels*
    bytes back, so a lane is a sequential chain that starts at 0 for the
    row's first pixel. Walking each lane with its own running ``left`` gives
    the same result as the per-byte loop it replaces, without a bounds check
    on every byte.
    """
    rows = _average_rows()
    for c in range(channels):
        above = prev[c::channels]
        out = bytearray(len(above))
        left = 0
        for k, (value, up) in enumerate(zip(line[c::channels], above)):
            left = (value + rows[left][up]) & 0xFF
            out[k] = left
        line[c::channels] = out


def unfilter(
    raw: bytes,
    width: int,
    height: int,
    channels: int,
    max_rows: int | None = None,
    max_cols: int | None = None,
) -> bytes:
    """Unfilter scanlines, returning at most *max_rows* rows of samples.

    Every scanline's filter type is validated, but when a bound is given only
    the first *max_rows* rows are actually unfiltered: the per-byte predictor
    work is what dominates decoding a large screenshot, so a caller that reads
    only its top rows skips that work for the rest without giving up the
    filter-type check.

    *max_cols* bounds each kept row to its first *max_cols* pixels. PNG
    predictors reference only the same row's earlier pixels and the previous
    row at the same or an earlier column, so a row prefix unfilters to exactly
    the bytes a full decode would produce there; the rest of each row is
    skipped unread. The returned bytes are ``rows * cols * channels`` long,
    where *cols* is *max_cols* clamped to *width* (or *width* when no column
    bound is given).
    """
    stride = width * channels
    _require_raw_length(raw, width, height, channels)
    rows = height if max_rows is None else min(max_rows, height)
    cols = width if max_cols is None else min(max_cols, width)
    out_stride = cols * channels
    out = bytearray(rows * out_stride)
    prev = bytearray(out_stride)
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
        line = bytearray(raw[src : src + out_stride])
        src += stride
        line = _unfilter_line(ftype, line, prev, channels)
        out[dst : dst + out_stride] = line
        dst += out_stride
        prev = line
    return bytes(out)


def _unfilter_paeth(line: bytearray, prev: bytearray, channels: int) -> None:
    """Undo the Paeth filter on *line* in place, given the previous row *prev*.

    A predictor only ever references same-channel neighbours, so the
    channels unfilter independently and can be done one at a time.
    Iterating each channel's stream with ``zip`` lets the left neighbour be a
    carried local instead of a ``line[i - channels]`` read, and appending the
    reconstructed bytes to a list avoids a per-byte ``line[i] = ...`` store.
    The delta table's rows are indexed by ``a - c`` first and ``b - c`` second,
    so each byte is one row lookup plus one row index rather than a shift and
    an add into a flat table. When the above and above-left bytes are equal
    (``b == c``), ``pa = |b - c| = 0`` wins the predictor outright and the
    prediction is always the left byte, so those bytes skip both table lookups.
    On the largest reference screenshot (``desktop_fandom.png``) nearly half
    the bytes take that branch, and the fast path decodes it ~18% quicker.
    """
    rows = paeth_delta_rows()
    for c in range(channels):
        filtered = line[c::channels]
        above = prev[c::channels]
        # The first pixel of a row has no left or above-left neighbour, so the
        # predictor is just the above byte.
        left = (filtered[0] + above[0]) & 0xFF
        unfiltered = [left]
        append = unfiltered.append
        for value, up, upleft in zip(filtered[1:], above[1:], above):
            if up == upleft:
                left = (value + left) & 0xFF
            else:
                left = (
                    value + upleft + rows[left - upleft + 255][up - upleft + 255]
                ) & 0xFF
            append(left)
        line[c::channels] = bytes(unfiltered)


def drop_alpha(
    raw: bytes,
    width: int,
    height: int,
    max_cols: int | None = None,
    max_rows: int | None = None,
) -> bytes:
    """Return ``raw`` with the alpha byte of every pixel removed.

    PNG filters reference only same-channel neighbours, so an alpha byte never
    influences a colour channel's predictor.  Removing alpha before
    unfiltering lets a colour-type-6 image unfilter as three channels instead
    of four and leaves the result already RGB, so ``expand.py``'s ``to_rgb``
    has no colour-type-6 case.  The filter-type byte at the start of each
    scanline is kept.

    *max_cols* keeps only each row's first *max_cols* pixels, so a caller that
    reads only a prefix does not copy the rest of every row. The returned rows
    are ``cols * 3`` samples after their filter byte, where *cols* is
    *max_cols* clamped to *width*.

    *max_rows* limits alpha removal to the rows that will be unfiltered. Later
    rows retain their filter byte and have zero-filled sample bytes; the
    unfilterer's row bound skips those samples while still validating every
    filter byte.
    """
    _require_raw_length(raw, width, height, 4)
    cols = width if max_cols is None else min(max_cols, width)
    rows = height if max_rows is None else min(max_rows, height)
    stride = width * 4
    out = bytearray(height * (cols * 3 + 1))
    src = 0
    dst = 0
    for row in range(height):
        out[dst] = raw[src]
        src += 1
        dst += 1
        if row < rows:
            line = bytearray(raw[src : src + cols * 4])
            del line[3::4]
            out[dst : dst + cols * 3] = line
        src += stride
        dst += cols * 3
    return bytes(out)
