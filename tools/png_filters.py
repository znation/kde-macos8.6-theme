"""The byte-lane arithmetic and Paeth delta table the PNG scanline unfilter uses.

``tools/png.py``'s Sub and Up filters reconstruct a whole scanline at once by
packing each byte into a big-integer lane, and its Paeth filter indexes a
precomputed predictor-delta table. Those helpers are pure byte-in/value-out
math with no dependency on the codec's framing, image type or error class, so
they live here and are pinned directly by ``tests/test_png_filters.py``.
"""

from __future__ import annotations

if __package__:
    from tools.byteops import require_equal_lengths
else:  # run as a top-level module, e.g. imported by tools/png.py
    from byteops import require_equal_lengths


_PAETH_DELTA: bytes | None = None


def _paeth_delta_table() -> bytes:
    """Paeth predictor deltas, indexed by ``(a - c, b - c)``.

    With ``a``, ``b`` and ``c`` the left, above and above-left bytes, the
    Paeth predictor adds ``c + delta`` where ``delta`` depends only on the two
    differences ``da = a - c`` and ``db = b - c``.  The 511x511 table (row
    stride 512) turns each byte of a Paeth-filtered row into one lookup.

    A predictor call per cell costs ~50 ms, a large share of decoding a small
    Paeth image.  Instead each row is filled from the closed form of the
    predictor with ``c = 0``: ``delta`` is ``da``, ``db`` or ``0``, and as
    ``db`` runs from -255 to 255 those three values occupy at most four
    contiguous blocks, so a row is the ``db`` pattern with two blocks
    overwritten.  Built on first use, so a decode with no Paeth rows never
    pays for it.
    """
    global _PAETH_DELTA
    table = _PAETH_DELTA
    if table is not None:
        return table
    table = bytearray(511 * 512)
    # db mod 256 for db in -255..255, the value of a row wherever the
    # predictor selects ``db``.
    db_row = bytes((db + 256) & 0xFF for db in range(-255, 256))
    zeros = bytes(511)
    for da in range(-255, 256):
        base = (da + 255) << 9
        row = bytearray(db_row)
        magnitude = da if da >= 0 else -da
        if da >= 0:
            # Blocks in order: db, 0, da, db.
            zero_lo, zero_hi = max(0, 256 - 2 * magnitude), 254 - magnitude // 2
            da_lo, da_hi = 255 - magnitude // 2, 255 + magnitude
        else:
            # Blocks in order: db, da, 0, db.
            da_lo, da_hi = 255 - magnitude, 255 + magnitude // 2
            zero_lo = 256 + magnitude // 2
            zero_hi = min(254 + 2 * magnitude, 510)
        row[da_lo : da_hi + 1] = bytes([da & 0xFF]) * (da_hi + 1 - da_lo)
        if zero_lo <= zero_hi:
            row[zero_lo : zero_hi + 1] = zeros[: zero_hi + 1 - zero_lo]
        table[base : base + 511] = row
    table = bytes(table)
    _PAETH_DELTA = table
    return table


def _lane_masks(length: int) -> tuple[int, int]:
    """Return the low-seven-bit and high-bit masks for *length* packed bytes.

    The two masks :func:`_lane_add` needs to add one byte per big-integer
    lane without a carry crossing between lanes.
    """
    return (
        int.from_bytes(b"\x7f" * length, "little"),
        int.from_bytes(b"\x80" * length, "little"),
    )


def _lane_add(x: int, y: int, low7: int, high: int) -> int:
    """Return *x* and *y* added byte-wise modulo 256, with no inter-byte carry.

    *x* and *y* are big integers packing one byte per lane; *low7* and *high*
    are the masks :func:`_lane_masks` returns for their shared length. Adding
    the two integers directly would let a carry cross from one byte into the
    next.  Keeping only the low seven bits of each input bounds every per-byte
    sum below 256, so no byte can carry, and XORing back the bit-7 difference
    restores the top bit.  The result equals
    ``bytes((a + b) & 0xFF for a, b in zip(...))`` at C speed.
    """
    return ((x & low7) + (y & low7)) ^ ((x ^ y) & high)


def _byte_add(a: bytes, b: bytes) -> bytes:
    """Return ``a`` and ``b`` added byte-wise modulo 256.

    Packs both byte strings into one lane per byte and applies
    :func:`_lane_add`.  They must be the same length;
    :func:`require_equal_lengths` rejects a mismatch and returns the shared
    length.
    """
    length = require_equal_lengths(a, b, "_byte_add")
    if length == 0:
        return b""
    low7, high = _lane_masks(length)
    return _lane_add(
        int.from_bytes(a, "little"),
        int.from_bytes(b, "little"),
        low7,
        high,
    ).to_bytes(length, "little")


def _prefix_sum(channel: bytes) -> bytes:
    """Return the inclusive prefix sum of ``channel`` modulo 256.

    Equivalent to ``out[0] = channel[0]`` and
    ``out[i] = (out[i] + out[i - 1]) & 0xFF``.  A Hillis-Steele scan adds a
    doubling span at each of ``log2(len(channel))`` steps, each one the
    carry-free lane addition of :func:`_lane_add`, so a whole channel's Sub
    filter runs at C speed instead of a Python loop per byte.
    """
    length = len(channel)
    if length <= 1:
        return bytes(channel)
    low7, high = _lane_masks(length)
    mask = (1 << (length * 8)) - 1
    value = int.from_bytes(channel, "little")
    step = 1
    while step < length:
        shifted = (value << (step * 8)) & mask
        value = _lane_add(value, shifted, low7, high)
        step <<= 1
    return value.to_bytes(length, "little")
