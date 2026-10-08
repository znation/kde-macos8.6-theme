"""Comparison metrics for the Mac OS 8.6 fidelity tooling.

The project's acceptance bar is "pixel-perfect", but a rendered surface cannot
be confirmed against its Mac OS 8.6 reference without a repeatable measurement.
This module supplies that measurement: it compares two decoded images pixel by
pixel and reports objective difference metrics -- mean absolute error (MAE),
per-channel mean absolute error (R, G, B), root-mean-square error (RMSE), the
worst per-channel delta and the coordinate where it occurs, and the fraction of
pixels whose worst channel differs by more than a tolerance.

PNG decoding lives in the sibling module ``tools/png.py`` and the command-line
entry point in ``tools/fidelity.py``; this module holds only the comparison
math. It uses only the Python standard library, keeping the check
self-contained and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

if __package__:
    from tools.png import Image
else:  # imported from inside tools/: python3 -c 'import fidelity_metrics'
    from png import Image


class FidelityError(Exception):
    """A candidate and reference image could not be compared."""


# value -> the low and high bytes of value squared.  A byte string's sum of
# squares is then ``sum(low bytes) + (sum(high bytes) << 8)``: two C-level
# ``bytes.translate`` passes instead of a Python call per byte.
_SQUARES_LOW = bytes((value * value) & 0xFF for value in range(256))
_SQUARES_HIGH = bytes((value * value) >> 8 for value in range(256))


def _sum_squares(channel: bytes) -> int:
    """Return the sum of the squares of one channel's byte values.

    ``bytes.map`` over a per-byte lookup is the obvious spelling, but it
    makes a Python-level call per byte.  Splitting each square into its low
    and high byte tables keeps the work inside ``bytes.translate`` and
    ``sum``, which run at C speed; the result is identical because
    ``value**2 == (value**2 & 0xFF) + ((value**2 >> 8) << 8)``.
    """
    return sum(channel.translate(_SQUARES_LOW)) + (
        sum(channel.translate(_SQUARES_HIGH)) << 8
    )


def _max_byte_index(data: bytes) -> int:
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
        raise ValueError("_max_byte_index() arg is an empty byte string")
    value = int.from_bytes(data, "little")
    ones = int.from_bytes(b"\x01" * length, "little")
    candidates = ones
    for bit in range(7, -1, -1):
        has_bit = (value >> bit) & ones
        narrowed = has_bit & candidates
        if narrowed:
            candidates = narrowed
    lowest = candidates & -candidates
    return (lowest.bit_length() - 1) >> 3


def _abs_diff(a: bytes, b: bytes) -> bytes:
    """Return the per-byte absolute difference of two equal-length byte strings.

    ``bytes(map(abs, map(sub, a, b)))`` is the obvious spelling, but it makes a
    Python-level call per byte.  This computes the same bytes with a handful of
    big-integer operations: the input is packed two bytes per 16-bit lane, each
    lane gets a guard bit so a subtraction cannot borrow into its neighbour,
    and the absolute value is selected from the two per-lane differences.  On
    screenshot-sized inputs it is ~2.7x faster than the ``map()`` form and
    returns byte-identical output.
    """
    length = len(a)
    if length == 0:
        return b""
    if length & 1:
        # Pad to a whole number of 16-bit lanes; the extra byte is dropped by
        # ``to_bytes(length)`` at the end.
        a = a + b"\x00"
        b = b + b"\x00"
    lanes = len(a) // 2
    # 0xFF in the low byte of every lane, and the guard bit (bit 8) of every
    # lane -- the lane-parallel equivalents of a scalar mask.
    low = int.from_bytes(b"\xff\x00" * lanes, "little")
    guard_bit = int.from_bytes(b"\x00\x01" * lanes, "little")
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


@dataclass(frozen=True)
class Metrics:
    """Per-pixel difference between two equally sized images.

    ``mae`` is averaged over all channels; ``mae_r``/``mae_g``/``mae_b`` average
    one channel each, so a systematic colour cast shows up as one channel's MAE
    standing out from the other two. ``max_x``/``max_y`` locate the first pixel
    whose worst channel delta equals ``max_delta``; both are 0 when the images
    are identical.
    """

    width: int
    height: int
    pixels: int
    mae: float
    mae_r: float
    mae_g: float
    mae_b: float
    rmse: float
    max_delta: int
    max_x: int
    max_y: int
    differing: int
    frac_differing: float


def _crop_rect_problem(x: int, y: int, width: int, height: int) -> str | None:
    """Return why ``(x, y, width, height)`` is not a valid crop rectangle."""
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        return (
            f"crop rectangle must have positive size and origin: "
            f"x={x} y={y} w={width} h={height}"
        )
    return None


def crop(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """Return the ``width x height`` region of ``image`` at ``(x, y)``."""
    problem = _crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise FidelityError(problem)
    if x + width > image.width or y + height > image.height:
        raise FidelityError(
            f"crop rectangle x={x} y={y} w={width} h={height} falls outside "
            f"the {image.width}x{image.height} image"
        )
    rows = []
    for row in range(y, y + height):
        start = (row * image.width + x) * 3
        rows.append(image.rgb[start : start + width * 3])
    return Image(width, height, b"".join(rows))


def compare(candidate: Image, reference: Image, tolerance: int = 0) -> Metrics:
    """Compare a candidate image against a reference image.

    Both must be the same size; ``tolerance`` is a per-channel delta.
    """
    if candidate.width != reference.width or candidate.height != reference.height:
        raise FidelityError(
            f"size mismatch: candidate {candidate.width}x{candidate.height} "
            f"vs reference {reference.width}x{reference.height}"
        )
    pa, pb = candidate.rgb, reference.rgb
    # Compare one channel at a time: a strided slice picks a channel,
    # ``_abs_diff`` turns it into that channel's absolute deltas as a byte
    # string, and integer sums feed the metrics.  The equivalent per-byte
    # Python loop dominated runtime on screenshot-sized inputs (tens of
    # millions of bytes).
    dr = _abs_diff(pa[0::3], pb[0::3])
    dg = _abs_diff(pa[1::3], pb[1::3])
    db = _abs_diff(pa[2::3], pb[2::3])

    total_abs_r = sum(dr)
    total_abs_g = sum(dg)
    total_abs_b = sum(db)
    total_sq = _sum_squares(dr) + _sum_squares(dg) + _sum_squares(db)

    # One bit-sliced pass per channel gives both that channel's maximum and
    # the first byte reaching it, replacing a ``max`` walk plus a ``find``
    # rescan.  The global maximum is the largest of the three; the pixel is the
    # first offset among the channels that actually reach it.  A channel's
    # byte offset equals its pixel offset, because the three slices are the
    # same length.
    r_index = _max_byte_index(dr)
    g_index = _max_byte_index(dg)
    b_index = _max_byte_index(db)
    r_max, g_max, b_max = dr[r_index], dg[g_index], db[b_index]
    max_delta = max(r_max, g_max, b_max)
    max_x = 0
    max_y = 0
    if max_delta:
        first = min(
            index
            for index, channel_max in (
                (r_index, r_max),
                (g_index, g_max),
                (b_index, b_max),
            )
            if channel_max == max_delta
        )
        max_x = first % candidate.width
        max_y = first // candidate.width

    # A pixel differs when any channel exceeds tolerance.  Translate each
    # channel to a 0/1 flag byte, OR the three flag strings as one big integer,
    # and popcount it, so a pixel with several differing channels counts once.
    over = bytes(1 if value > tolerance else 0 for value in range(256))
    differing = (
        int.from_bytes(dr.translate(over), "little")
        | int.from_bytes(dg.translate(over), "little")
        | int.from_bytes(db.translate(over), "little")
    ).bit_count()

    pixels = candidate.width * candidate.height
    channels = pixels * 3
    return Metrics(
        width=candidate.width,
        height=candidate.height,
        pixels=pixels,
        mae=(total_abs_r + total_abs_g + total_abs_b) / channels,
        mae_r=total_abs_r / pixels,
        mae_g=total_abs_g / pixels,
        mae_b=total_abs_b / pixels,
        rmse=(total_sq / channels) ** 0.5,
        max_delta=max_delta,
        max_x=max_x,
        max_y=max_y,
        differing=differing,
        frac_differing=differing / pixels,
    )
