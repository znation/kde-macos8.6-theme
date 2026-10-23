"""Packed-integer byte-lane arithmetic for the fidelity tooling.

``tools/fidelity_metrics.py`` compares two images by turning each channel's
byte string into that channel's absolute per-byte deltas, then summing and
locating maxima over those byte strings.  Doing that with a Python loop per
byte dominated runtime on screenshot-sized inputs, so the operations here pack
a byte string into one big integer, work on many bytes per arithmetic step,
and unpack the result.

The functions are independent of images and of the fidelity metric contract:
each takes and returns byte strings (or, for :func:`max_byte_index`, an index)
and is checked against a naive per-byte oracle in ``tests/test_byte_lanes.py``.
The shared equal-length precondition lives in the sibling ``tools/byteops.py``.
Only the Python standard library is used.
"""

from __future__ import annotations

if __package__:
    from tools.byteops import require_equal_lengths
else:  # imported from inside tools/: python3 -c 'import byte_lanes'
    from byteops import require_equal_lengths


# value -> the low and high bytes of value squared.  A byte string's sum of
# squares is then ``sum(low bytes) + (sum(high bytes) << 8)``: two C-level
# ``bytes.translate`` passes instead of a Python call per byte.
_SQUARES_LOW = bytes((value * value) & 0xFF for value in range(256))
_SQUARES_HIGH = bytes((value * value) >> 8 for value in range(256))


def sum_squares(channel: bytes) -> int:
    """Return the sum of the squares of one channel's byte values.

    ``sum(value * value for value in channel)`` is the obvious spelling, but
    it runs a Python-level generator step per byte.  Splitting each square
    into its low and high byte tables keeps the work inside
    ``bytes.translate`` and ``sum``, which run in C; the result is identical
    because ``value**2 == (value**2 & 0xFF) + ((value**2 >> 8) << 8)``.
    """
    return sum(channel.translate(_SQUARES_LOW)) + (
        sum(channel.translate(_SQUARES_HIGH)) << 8
    )


_MAX_BYTE_ONES_CACHE: dict[int, int] = {}


def max_byte_index(data: bytes) -> int:
    """Return the index of the first occurrence of the maximum byte in *data*.

    ``max(data)`` walks the channel as Python ints and a following
    ``data.find`` rescans it to locate the winner; this returns both from one
    bit-sliced pass.  It treats *data* as one big integer and narrows the set
    of candidate byte positions one bit at a time: ``ones`` marks bit 0 of
    every byte lane, so ``(value >> bit) & ones`` keeps exactly the lanes whose
    byte has that bit set.  Intersecting the eight bit levels leaves the lanes
    holding the maximum, and the lowest set bit of that mask is its first
    index.  *data* must be non-empty.
    """
    length = len(data)
    if length == 0:
        raise ValueError("max_byte_index() arg is an empty byte string")
    value = int.from_bytes(data, "little")
    ones = _MAX_BYTE_ONES_CACHE.get(length)
    if ones is None:
        ones = int.from_bytes(b"\x01" * length, "little")
        _MAX_BYTE_ONES_CACHE[length] = ones
    candidates = ones
    for bit in range(7, -1, -1):
        has_bit = (value >> bit) & ones
        narrowed = has_bit & candidates
        if narrowed:
            candidates = narrowed
    lowest = candidates & -candidates
    return (lowest.bit_length() - 1) >> 3


_ABS_DIFF_MASKS_CACHE: dict[int, tuple[int, int]] = {}


def abs_diff(a: bytes, b: bytes) -> bytes:
    """Return the per-byte absolute difference of two equal-length byte strings.

    ``bytes(map(abs, map(sub, a, b)))`` is the obvious spelling, but it walks
    both strings one Python int at a time.  This computes the same bytes with
    a handful of big-integer operations: the input is packed two bytes per
    16-bit lane, each lane gets a guard bit so a subtraction cannot borrow
    into its neighbour, and the absolute value is selected from the two
    per-lane differences.

    Both byte strings must be the same length; :func:`require_equal_lengths`
    rejects a mismatch and returns the shared length.
    """
    length = require_equal_lengths(a, b, "abs_diff")
    if length == 0:
        return b""
    if length & 1:
        # Pad to a whole number of 16-bit lanes; the extra byte is dropped by
        # ``to_bytes(length)`` at the end.
        a = a + b"\x00"
        b = b + b"\x00"
    lanes = len(a) // 2
    cached = _ABS_DIFF_MASKS_CACHE.get(lanes)
    if cached is None:
        # 0xFF in the low byte of every lane, and the guard bit (bit 8) of every
        # lane -- the lane-parallel equivalents of a scalar mask.
        low = int.from_bytes(b"\xff\x00" * lanes, "little")
        guard_bit = int.from_bytes(b"\x00\x01" * lanes, "little")
        cached = (low, guard_bit)
        _ABS_DIFF_MASKS_CACHE[lanes] = cached
    else:
        low, guard_bit = cached
    x = int.from_bytes(a, "little")
    y = int.from_bytes(b, "little")
    # Split each string into its even- and odd-indexed bytes, each already
    # sitting in the low byte of its own 16-bit lane.
    even_x, odd_x = x & low, (x >> 8) & low
    even_y, odd_y = y & low, (y >> 8) & low

    def lane_abs(u: int, v: int) -> int:
        # With the guard bit set, ``u - v`` is 256 + u - v in [1, 511], so the
        # subtraction never borrows across a lane and bit 8 is set exactly when
        # u >= v.  That lane's low byte is then |u - v| already, so the result
        # picks the low byte of whichever of the two differences is >= 256.
        ge = (u | guard_bit) - v
        lt = (v | guard_bit) - u
        higher = ge & guard_bit
        ge_mask = higher - (higher >> 8)  # 0xFF in lanes where u >= v
        return ((ge & low) & ge_mask) | ((lt & low) & (low ^ ge_mask))

    # Lane j of the even/odd halves carries byte 2j / 2j+1, so interleaving the
    # two lane-packed results reconstructs the original byte order.
    return (lane_abs(even_x, even_y) | (lane_abs(odd_x, odd_y) << 8)).to_bytes(
        length, "little"
    )
