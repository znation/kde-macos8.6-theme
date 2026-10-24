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
entry point in ``tools/fidelity.py``; this module holds the comparison math
and the crop geometry the CLI and :func:`crop` both validate against
(:func:`crop_rect_problem`).  The packed byte-lane arithmetic it measures with
lives in the sibling :mod:`tools.byte_lanes` module.  It uses only the Python
standard library, keeping the check self-contained and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

if __package__:
    from tools.byte_lanes import abs_diff, max_byte_index, sum_squares
    from tools.ints import is_plain_int
    from tools.png import Image
else:  # imported from a directly run tool
    from byte_lanes import abs_diff, max_byte_index, sum_squares
    from ints import is_plain_int
    from png import Image


class FidelityError(Exception):
    """A candidate and reference image could not be compared."""


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


def crop_rect_problem(x: int, y: int, width: int, height: int) -> str | None:
    """Return why ``(x, y, width, height)`` is not a valid crop rectangle.

    Public because it is the shared crop-rectangle contract: the CLI's
    ``--crop`` parser calls it before reading an image, and :func:`crop`
    calls it before slicing one, so both reject the same rectangles with the
    same wording.

    Every value must be an integer: :func:`crop` slices the image's RGB byte
    string, so a float coordinate would reach the slice as a raw
    ``TypeError`` naming neither the argument nor its value.  The origin must
    be non-negative (``x=0``/``y=0`` is the top-left pixel, not a fault) and
    the size positive.
    """
    for name, value in (
        ("x", x),
        ("y", y),
        ("width", width),
        ("height", height),
    ):
        if not is_plain_int(value):
            return f"crop rectangle values must be integers: {name}={value!r}"
    if x < 0 or y < 0:
        return (
            f"crop rectangle origin must not be negative: "
            f"x={x} y={y} w={width} h={height}"
        )
    if width <= 0 or height <= 0:
        return (
            f"crop rectangle must have positive size: "
            f"x={x} y={y} w={width} h={height}"
        )
    return None


def crop(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """Return the ``width x height`` region of ``image`` at ``(x, y)``."""
    if not isinstance(image, Image):
        raise FidelityError(
            f"crop image must be an Image, not {type(image).__name__}"
        )
    problem = crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise FidelityError(problem)
    if x + width > image.width or y + height > image.height:
        raise FidelityError(
            f"crop rectangle x={x} y={y} w={width} h={height} falls outside "
            f"the {image.width}x{image.height} image"
        )
    rows = []
    alpha_rows = [] if image.alpha is not None else None
    for row in range(y, y + height):
        start = (row * image.width + x) * 3
        rows.append(image.rgb[start : start + width * 3])
        if alpha_rows is not None:
            alpha_start = row * image.width + x
            alpha_rows.append(image.alpha[alpha_start : alpha_start + width])
    alpha = None if alpha_rows is None else b"".join(alpha_rows)
    return Image(width, height, b"".join(rows), alpha)


_OVER_TABLE_CACHE: dict[int, bytes] = {}


def compare(candidate: Image, reference: Image, tolerance: int = 0) -> Metrics:
    """Compare a candidate image against a reference image.

    Both must be the same size; ``tolerance`` is a per-channel delta in the
    range 0-255.  A delta is a byte, so a tolerance outside that range cannot
    be meaningful: above 255 no pixel ever exceeds it (the ``differing``
    metric silently reads zero) and below 0 every pixel does.  The command
    line rejects both as usage errors; this is the same bound for a caller
    that uses the comparison directly.
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
    if compare_alpha:
        deltas.append(abs_diff(alpha_a, alpha_b))
    channel_count = len(deltas)
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
    over = _OVER_TABLE_CACHE.get(tolerance)
    if over is None:
        over = bytes(1 if value > tolerance else 0 for value in range(256))
        _OVER_TABLE_CACHE[tolerance] = over
    flags = 0
    for delta in deltas:
        flags |= int.from_bytes(delta.translate(over), "little")
    differing = flags.bit_count()

    channels = pixels * channel_count
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
        mae_a=None if not compare_alpha else totals[3] / pixels,
    )
