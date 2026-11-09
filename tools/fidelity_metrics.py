"""Comparison metrics for the Mac OS 8.6 fidelity tooling.

The project's acceptance bar is "pixel-perfect", but a rendered surface cannot
be confirmed against its Mac OS 8.6 reference without a repeatable measurement.
This module supplies that measurement: it compares two decoded images pixel by
pixel and reports objective difference metrics -- mean absolute error (MAE),
per-channel mean absolute error (R, G, B, and A when either image carries
alpha), root-mean-square error (RMSE), the
worst per-channel delta and the coordinate where it occurs, and the fraction of
pixels whose worst channel differs by more than a tolerance.

PNG decoding lives in the sibling ``tools/png`` package and the command-line
entry point in ``tools/fidelity.py``; this module holds the comparison math.
The crop geometry lives in :mod:`tools.fidelity_geometry`; its public names
are re-exported here for existing callers. The packed byte-lane arithmetic it
measures with lives in the sibling :mod:`tools.byte_lanes` module. It uses
only the Python standard library, keeping the check self-contained and
deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

if __package__:
    from tools.byte_lanes import abs_diff, max_byte_index, sum_squares
    from tools.ints import is_plain_int
    from tools.png import Image
    from tools.fidelity_geometry import (
        FidelityError,
        crop_rect_problem,
        crop,
    )
else:  # imported from a directly run tool
    from byte_lanes import abs_diff, max_byte_index, sum_squares
    from ints import is_plain_int
    from png import Image
    from fidelity_geometry import FidelityError, crop_rect_problem, crop

__all__ = [
    "FidelityError",
    "crop_rect_problem",
    "crop",
    "Metrics",
    "compare",
    "over_table",
]


@dataclass(frozen=True)
class Metrics:
    """Per-pixel difference between two equally sized images.

    ``mae`` is averaged over all channels; ``mae_r``/``mae_g``/``mae_b`` average
    one channel each, so a systematic colour cast shows up as one channel's MAE
    standing out from the other two. ``mae_a`` is the alpha channel's mean
    absolute error when alpha was compared, or ``None`` for an RGB-only
    comparison. ``max_x``/``max_y`` locate the first pixel whose worst channel
    delta equals ``max_delta``; both are 0 when the images are identical.
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
    mae_a: float | None = None
    difference_bounds: tuple[int, int, int, int] | None = None


_OVER_TABLE_CACHE: dict[int, bytes] = {}


def over_table(tolerance: int) -> bytes:
    """Return the flag table translating each byte delta to 0/1 over tolerance.

    A byte delta is 0-255, so one 256-entry table suffices for any tolerance;
    it is cached per tolerance because a tolerance is fixed for one CLI run
    while the table feeds every channel translation.
    """
    table = _OVER_TABLE_CACHE.get(tolerance)
    if table is None:
        table = bytes(1 if value > tolerance else 0 for value in range(256))
        _OVER_TABLE_CACHE[tolerance] = table
    return table


def compare(candidate: Image, reference: Image, tolerance: int = 0,
            deltas: list[bytes] | None = None) -> Metrics:
    """Compare a candidate image against a reference image.

    Both must be the same size; ``tolerance`` is a per-channel delta in the
    range 0-255.  A delta is a byte, so a tolerance outside that range cannot
    be meaningful: above 255 no pixel ever exceeds it (the ``differing``
    metric silently reads zero) and below 0 every pixel does.  The command
    line rejects both as usage errors; this is the same bound for a caller
    that uses the comparison directly.

    The keyword-only *deltas* parameter shares the per-channel
    absolute-delta byte strings that :func:`tools.fidelity_pixels.channel_deltas`
    derives, so a run that also wants the pixels or spatial reports pays one
    derivation instead of this function's own identical pass. ``None`` (the
    default) keeps deriving them here, the behavior a caller driving only
    the comparison keeps. The shared list carries the computed alpha string
    exactly when this derivation would (both opaque sides omit it), so every
    metric reads the same strings either way.
    """
    if not is_plain_int(tolerance) or not 0 <= tolerance <= 255:
        raise FidelityError(
            f"tolerance must be a per-channel delta between 0 and 255: "
            f"{tolerance!r}"
        )
    if not isinstance(candidate, Image):
        raise FidelityError(
            f"candidate must be an Image, not {type(candidate).__name__}"
        )
    if not isinstance(reference, Image):
        raise FidelityError(
            f"reference must be an Image, not {type(reference).__name__}"
        )
    if candidate.width != reference.width or candidate.height != reference.height:
        raise FidelityError(
            f"size mismatch: candidate {candidate.width}x{candidate.height} "
            f"vs reference {reference.width}x{reference.height}"
        )
    pa, pb = candidate.rgb, reference.rgb
    pixels = candidate.width * candidate.height
    alpha_a, alpha_b = candidate.alpha, reference.alpha
    compare_alpha = alpha_a is not None or alpha_b is not None
    if deltas is None:
        if compare_alpha:
            # An Image without an alpha plane is fully opaque; representing it as
            # 255 lets an RGB reference be compared against an RGBA candidate.
            opaque = bytes([255]) * pixels
            alpha_a = opaque if alpha_a is None else alpha_a
            alpha_b = opaque if alpha_b is None else alpha_b
        # Compare one channel at a time: a strided slice picks a channel,
        # ``abs_diff`` turns it into that channel's absolute deltas as a byte
        # string, and integer sums feed the metrics.  The equivalent per-byte
        # Python loop dominated runtime on screenshot-sized inputs (tens of
        # millions of bytes).  The list is ordered R, G, B, then A when compared.
        deltas = [
            abs_diff(pa[channel::3], pb[channel::3]) for channel in range(3)
        ]
        # A rendered surface and a reference screenshot are usually both fully
        # opaque (an RGB PNG decodes to an all-255 alpha plane), so their alpha
        # deltas are zero everywhere: ``alpha_a.count(255) == pixels`` proves a
        # plane opaque in one C-speed scan, and skipping the appended
        # ``abs_diff`` pass leaves every alpha-fed metric reading the zero
        # contribution the plane would have produced. ``alpha_checked`` records
        # whether the deltas carry a computed alpha channel.
        alpha_checked = False
        if compare_alpha:
            if alpha_a.count(255) == pixels and alpha_b.count(255) == pixels:
                alpha_checked = False
            else:
                deltas.append(abs_diff(alpha_a, alpha_b))
                alpha_checked = True
    else:
        # The shared list was derived with the same substitution and
        # opaque-plane skip, so the presence of the fourth string records
        # whether a computed alpha channel joined the deltas.
        alpha_checked = len(deltas) == 4
    # The compared alpha channel keeps its aggregate slot either way, so the
    # mean and RMSE still divide by four channels when alpha is compared.
    if alpha_checked:
        channel_count = len(deltas)
    elif compare_alpha:
        channel_count = 4
    else:
        channel_count = 3
    totals = [sum(delta) for delta in deltas]
    total_abs_r, total_abs_g, total_abs_b = totals[:3]
    total_sq = sum(sum_squares(delta) for delta in deltas)

    # One bit-sliced pass per channel gives both that channel's maximum and
    # the first byte reaching it, replacing a ``max`` walk plus a ``find``
    # rescan.  The global maximum is the largest of the channels; the pixel is
    # the first offset among the channels that actually reach it.  A channel's
    # byte offset equals its pixel offset, because every slice is the same
    # length.
    indices = [max_byte_index(delta) for delta in deltas]
    maxima = [delta[index] for delta, index in zip(deltas, indices)]
    max_delta = max(maxima)
    max_x = 0
    max_y = 0
    if max_delta:
        first = min(
            index
            for index, channel_max in zip(indices, maxima)
            if channel_max == max_delta
        )
        max_x = first % candidate.width
        max_y = first // candidate.width

    # A pixel differs when any channel exceeds tolerance.  Translate each
    # channel to a 0/1 flag byte, OR the flag strings as one big integer, and
    # popcount it, so a pixel with several differing channels counts once.
    over = over_table(tolerance)
    flags = 0
    for delta in deltas:
        flags |= int.from_bytes(delta.translate(over), "little")
    differing = flags.bit_count()

    difference_bounds = None
    if differing:
        occupied = flags.to_bytes(pixels, "little")
        left = candidate.width
        top = candidate.height
        right = bottom = -1
        for y in range(candidate.height):
            row = occupied[y * candidate.width : (y + 1) * candidate.width]
            first = row.find(1)
            if first < 0:
                continue
            last = row.rfind(1)
            left = min(left, first)
            right = max(right, last)
            top = min(top, y)
            bottom = y
        difference_bounds = (left, top, right - left + 1, bottom - top + 1)

    channels = pixels * channel_count
    if not compare_alpha:
        mae_a = None
    elif alpha_checked:
        mae_a = totals[3] / pixels
    else:
        mae_a = 0.0

    return Metrics(
        width=candidate.width,
        height=candidate.height,
        pixels=pixels,
        mae=sum(totals) / channels,
        mae_r=total_abs_r / pixels,
        mae_g=total_abs_g / pixels,
        mae_b=total_abs_b / pixels,
        rmse=(total_sq / channels) ** 0.5,
        max_delta=max_delta,
        max_x=max_x,
        max_y=max_y,
        differing=differing,
        frac_differing=differing / pixels,
        mae_a=mae_a,
        difference_bounds=difference_bounds,
    )
