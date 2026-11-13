"""Pixel diagnostics for fidelity surfaces.

Every diagnostic reads the same per-channel absolute-delta byte
strings that :func:`tools.fidelity_metrics.compare` builds -- a strided
RGB channel slice per channel through ``tools.byte_lanes.abs_diff``, plus
an alpha string whenever the planes differ in presence or content -- and
then folds them with ``tools.byte_lanes.byte_max`` into one maximum-delta
byte string per pixel.  Each scan reads those strings back through
C-speed ``bytes`` operations instead of re-deriving each pixel's raw RGBA
deltas in Python, which dominated a screenshot-sized diagnostic.
"""

from __future__ import annotations

from collections import Counter

if __package__:
    from tools.byte_lanes import abs_diff, byte_max, max_byte_index
    from tools.fidelity_metrics import over_table
    from tools.png import Image
else:  # imported by a directly run CLI
    from byte_lanes import abs_diff, byte_max, max_byte_index
    from fidelity_metrics import over_table
    from png import Image


def channel_deltas(candidate: Image, reference: Image) -> list[bytes]:
    """Return per-channel absolute-delta byte strings in RGBA order.

    The scan interface takes this list through the optional keyword-only
    *deltas* parameter of each diagnostic below: a run that requests several
    pixel reports computes the pass once, up front, and hands the result to
    each call. Passing ``None`` (the default) derives the list here, so
    every one-function caller keeps the behaviour it had.

    RGB deltas are read straight from the packed planes, including beneath
    transparent pixels, so a pixel's RGB entries index the strings exactly
    like the image-local pixel index.  A plane without an image alpha
    channel is fully opaque; when both alpha sides are opaque -- present or
    absent -- every pixel's alpha delta is zero and the string is omitted,
    the opaque-plane skip :func:`tools.fidelity_metrics.compare` makes, and
    diagnostics that would have counted a zero alpha contribution simply
    read that zero from the absent string.
    """
    deltas = [
        abs_diff(candidate.rgb[channel::3], reference.rgb[channel::3])
        for channel in range(3)
    ]
    alpha_a, alpha_b = candidate.alpha, reference.alpha
    if alpha_a is not None or alpha_b is not None:
        pixels = len(deltas[0])
        opaque_a = alpha_a is None or alpha_a.count(255) == pixels
        opaque_b = alpha_b is None or alpha_b.count(255) == pixels
        if not (opaque_a and opaque_b):
            opaque = b"\xff" * pixels
            deltas.append(abs_diff(
                opaque if alpha_a is None else alpha_a,
                opaque if alpha_b is None else alpha_b,
            ))
    return deltas


def _maximum_deltas(
    candidate: Image, reference: Image, deltas: list[bytes] | None,
) -> bytes:
    """Return one byte string holding each pixel's maximum channel delta."""
    deltas = _resolved_deltas(candidate, reference, deltas)
    maximum = deltas[0]
    for delta in deltas[1:]:
        maximum = byte_max(maximum, delta)
    return maximum


def _resolved_deltas(
    candidate: Image, reference: Image, deltas: list[bytes] | None,
) -> list[bytes]:
    """Return the shared *deltas* list, deriving it when ``None``."""
    return channel_deltas(candidate, reference) if deltas is None else deltas


def worst_pixels(
    candidate: Image,
    reference: Image,
    tolerance: int,
    limit: int,
    *,
    offset: int | None = None,
    deltas: list[bytes] | None = None,
) -> list[dict[str, object]]:
    """Return up to *limit* pixels exceeding *tolerance*, ranked by delta.

    Inputs are equally sized validated images, a tolerance in 0..255, and a
    limit in 1..1000. Ties follow row-major order; coordinates are image-local.
    The optional offset skips earlier ranked records; ``None`` (the offset
    option was not given) acts as 0 and skips nothing; selection storage is
    bounded by the image area and grows with the requested page position.

    The ranking walks delta values from 255 down to one past the tolerance and,
    inside each value, the maximum-delta string's ``find`` scan in image
    order -- the same descending-delta, row-major-ties order a full sort of
    ``(-delta, index)`` would produce -- stopping as soon as the requested
    selection size is gathered. *deltas* shares one :func:`channel_deltas`
    pass across a run of pixel reports; ``None`` derives the list here.
    """
    offset = 0 if offset is None else offset
    width, height = candidate.width, candidate.height
    area = width * height
    selection_size = min(offset + limit, area)
    if not selection_size:
        return []

    maximum = _maximum_deltas(candidate, reference, deltas)
    selected: list[tuple[int, int]] = []
    for value in range(255, tolerance, -1):
        position = maximum.find(value)
        while position >= 0:
            selected.append((value, position))
            if len(selected) == selection_size:
                break
            position = maximum.find(value, position + 1)
        if len(selected) == selection_size:
            break

    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    records = []
    for delta, index in selected[offset:]:
        channel_offset = index * 3
        records.append({
            "x": index % width,
            "y": index // width,
            "candidate_rgba": [
                *candidate_rgb[channel_offset:channel_offset + 3],
                255 if candidate_alpha is None else candidate_alpha[index],
            ],
            "reference_rgba": [
                *reference_rgb[channel_offset:channel_offset + 3],
                255 if reference_alpha is None else reference_alpha[index],
            ],
            "max_delta": delta,
        })
    return records


def channel_counts(
    candidate: Image,
    reference: Image,
    tolerance: int,
    *,
    deltas: list[bytes] | None = None,
) -> dict[str, int]:
    """Count the pixels each channel differs beyond *tolerance* on.

    Inputs are equally sized validated images and a tolerance in 0..255 -- the
    same preconditions :func:`worst_pixels` relies on, which the CLI's own
    ``compare`` call has already checked by the time this runs. *deltas*
    shares one :func:`channel_deltas` pass across a run of pixel reports;
    ``None`` derives the list here. A pixel
    contributes once to each channel whose absolute delta is strictly greater
    than the tolerance, so ``delta == tolerance`` is not differing, mirroring
    the gate. The four counts overlap (one pixel can appear in several), so
    they must not be summed to obtain the union differing-pixel count.
    A missing alpha plane counts every pixel as opaque 255.
    """
    counts = {"r": 0, "g": 0, "b": 0, "a": 0}
    over = over_table(tolerance)
    for name, delta in zip(("r", "g", "b", "a"),
                           _resolved_deltas(candidate, reference, deltas)):
        counts[name] = delta.translate(over).count(1)
    return counts


def channel_bias(candidate: Image, reference: Image) -> dict[str, float]:
    """Return mean candidate-minus-reference byte deltas for RGBA.

    Inputs are equally sized validated images. RGB bytes are compared raw,
    including under transparent pixels, and a missing alpha plane is opaque.
    Each mean is the difference of two whole-channel byte sums -- the same
    sum as the per-pixel accumulation, just gathered with C-speed ``sum``
    over strided channel slices.
    """
    pixels = candidate.width * candidate.height
    sums = [
        sum(candidate.rgb[channel::3]) - sum(reference.rgb[channel::3])
        for channel in range(3)
    ]
    alpha_a, alpha_b = candidate.alpha, reference.alpha
    sums.append(
        (255 * pixels if alpha_a is None else sum(alpha_a))
        - (255 * pixels if alpha_b is None else sum(alpha_b))
    )
    return {name: total / pixels for name, total in zip(("r", "g", "b", "a"), sums)}


def channel_maxima(
    candidate: Image,
    reference: Image,
    *,
    deltas: list[bytes] | None = None,
) -> dict[str, int]:
    """Return maximum absolute byte delta for each compared RGBA channel.

    Inputs are equally sized validated images. RGB bytes are compared raw,
    including beneath transparent pixels, and a missing alpha plane is opaque.
    Each maximum comes from the bit-sliced :func:`max_byte_index` pass, which
    yields both the maximum and its first occurrence from one walk. *deltas*
    shares one :func:`channel_deltas` pass across a run of pixel reports;
    ``None`` derives the list here.
    """
    maxima = {"r": 0, "g": 0, "b": 0, "a": 0}
    for name, delta in zip(("r", "g", "b", "a"),
                           _resolved_deltas(candidate, reference, deltas)):
        if delta:
            maxima[name] = delta[max_byte_index(delta)]
    return maxima


def delta_histogram(
    candidate: Image,
    reference: Image,
    *,
    deltas: list[bytes] | None = None,
) -> list[dict[str, int]]:
    """Count compared pixels by their maximum absolute RGBA channel delta.

    Inputs are equally sized validated images, as checked by the CLI's
    comparison. Missing alpha planes represent opaque pixels. Counts gather
    from the maximum-delta byte string in one streamed pass -- the
    standard library's ``Counter`` walks the bytes at C speed -- instead
    of one Python loop step per pixel. *deltas* shares one
    :func:`channel_deltas` pass across a run of pixel reports; ``None``
    derives the list here.
    """
    counted = Counter(_maximum_deltas(candidate, reference, deltas))
    return [{"delta": delta, "count": counted[delta]}
            for delta in range(256) if counted[delta]]
