"""Pixel diagnostics for fidelity surfaces."""

from __future__ import annotations

import heapq

if __package__:
    from tools.png import Image
else:  # imported by a directly run CLI
    from png import Image


def _absolute_deltas(
    candidate_rgb: bytes,
    reference_rgb: bytes,
    candidate_alpha: bytes | None,
    reference_alpha: bytes | None,
    index: int,
) -> tuple[int, int, int, int]:
    """Return one raw RGBA absolute delta tuple; absent alpha means opaque."""
    offset = index * 3
    return (
        abs(candidate_rgb[offset] - reference_rgb[offset]),
        abs(candidate_rgb[offset + 1] - reference_rgb[offset + 1]),
        abs(candidate_rgb[offset + 2] - reference_rgb[offset + 2]),
        abs((255 if candidate_alpha is None else candidate_alpha[index])
            - (255 if reference_alpha is None else reference_alpha[index])),
    )


def worst_pixels(
    candidate: Image,
    reference: Image,
    tolerance: int,
    limit: int,
) -> list[dict[str, object]]:
    """Return up to *limit* pixels exceeding *tolerance*, ranked by delta.

    Inputs are equally sized validated images, a tolerance in 0..255, and a
    limit in 1..1000. Ties follow row-major order; coordinates are image-local.
    """
    width, height = candidate.width, candidate.height
    candidate_rgb = candidate.rgb
    reference_rgb = reference.rgb
    candidate_alpha = candidate.alpha
    reference_alpha = reference.alpha

    def ranked():
        for index in range(width * height):
            delta = max(_absolute_deltas(
                candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
            ))
            if delta > tolerance:
                yield (-delta, index)

    selected = heapq.nsmallest(limit, ranked())
    records = []
    for negative_delta, index in selected:
        offset = index * 3
        records.append({
            "x": index % width,
            "y": index // width,
            "candidate_rgba": [*candidate_rgb[offset:offset + 3], 255 if candidate_alpha is None else candidate_alpha[index]],
            "reference_rgba": [*reference_rgb[offset:offset + 3], 255 if reference_alpha is None else reference_alpha[index]],
            "max_delta": -negative_delta,
        })
    return records


def channel_counts(
    candidate: Image,
    reference: Image,
    tolerance: int,
) -> dict[str, int]:
    """Count the pixels each channel differs beyond *tolerance* on.

    Inputs are equally sized validated images and a tolerance in 0..255 -- the
    same preconditions :func:`worst_pixels` relies on, which the CLI's own
    ``compare`` call has already checked by the time this runs. A pixel
    contributes once to each channel whose absolute delta is strictly greater
    than the tolerance, so ``delta == tolerance`` is not differing, mirroring
    the gate. The four counts overlap (one pixel can appear in several), so
    they must not be summed to obtain the union differing-pixel count.
    A missing alpha plane counts every pixel as opaque 255.
    """
    width, height = candidate.width, candidate.height
    candidate_rgb = candidate.rgb
    reference_rgb = reference.rgb
    candidate_alpha = candidate.alpha
    reference_alpha = reference.alpha
    counts = {"r": 0, "g": 0, "b": 0, "a": 0}
    for index in range(width * height):
        deltas = _absolute_deltas(
            candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
        )
        red_delta, green_delta, blue_delta, alpha_delta = deltas
        if red_delta > tolerance:
            counts["r"] += 1
        if green_delta > tolerance:
            counts["g"] += 1
        if blue_delta > tolerance:
            counts["b"] += 1
        if alpha_delta > tolerance:
            counts["a"] += 1
    return counts


def difference_columns(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each column of equally sized images."""
    width, height = candidate.width, candidate.height
    counts = [0] * width
    for index in range(width * height):
        if max(_absolute_deltas(candidate.rgb, reference.rgb, candidate.alpha,
                                reference.alpha, index)) > tolerance:
            counts[index % width] += 1
    return counts


def channel_bias(candidate: Image, reference: Image) -> dict[str, float]:
    """Return mean candidate-minus-reference byte deltas for RGBA.

    Inputs are equally sized validated images. RGB bytes are compared raw,
    including under transparent pixels, and a missing alpha plane is opaque.
    """
    pixels = candidate.width * candidate.height
    sums = [0, 0, 0, 0]
    for index in range(pixels):
        offset = index * 3
        for channel in range(3):
            sums[channel] += candidate.rgb[offset + channel] - reference.rgb[offset + channel]
        sums[3] += (255 if candidate.alpha is None else candidate.alpha[index]) - (
            255 if reference.alpha is None else reference.alpha[index]
        )
    return {name: total / pixels for name, total in zip(("r", "g", "b", "a"), sums)}


def channel_maxima(candidate: Image, reference: Image) -> dict[str, int]:
    """Return maximum absolute byte delta for each compared RGBA channel.

    Inputs are equally sized validated images. RGB bytes are compared raw,
    including beneath transparent pixels, and a missing alpha plane is opaque.
    """
    maxima = [0, 0, 0, 0]
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    for index in range(candidate.width * candidate.height):
        for channel, delta in enumerate(_absolute_deltas(
            candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
        )):
            maxima[channel] = max(maxima[channel], delta)
    return dict(zip(("r", "g", "b", "a"), maxima))


def difference_rows(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each crop-relative row.

    Inputs are equally sized validated images. A pixel counts once when any
    raw RGBA channel delta exceeds tolerance; missing alpha is opaque.
    """
    width, height = candidate.width, candidate.height
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    rows = []
    for y in range(height):
        count = 0
        for x in range(width):
            index = y * width + x
            differing = any(delta > tolerance for delta in _absolute_deltas(
                candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
            ))
            count += differing
        rows.append(count)
    return rows


def difference_row_bounds(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int] | None]:
    """Return each differing row's smallest crop-relative horizontal interval.

    Pixels count when any raw RGBA channel delta exceeds tolerance. Missing
    alpha is opaque; RGB beneath transparency remains part of the comparison.
    """
    width, height = candidate.width, candidate.height
    bounds = []
    for y in range(height):
        first = last = None
        for x in range(width):
            index = y * width + x
            if max(_absolute_deltas(candidate.rgb, reference.rgb,
                                    candidate.alpha, reference.alpha, index)) > tolerance:
                if first is None:
                    first = x
                last = x
        bounds.append(None if first is None else {"x": first, "width": last - first + 1})
    return bounds


def difference_column_bounds(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int] | None]:
    """Return each differing column's smallest crop-relative vertical interval.

    Pixels count when any raw RGBA channel delta exceeds tolerance. Missing
    alpha is opaque; RGB beneath transparency remains part of the comparison.
    """
    width, height = candidate.width, candidate.height
    bounds = []
    for x in range(width):
        first = last = None
        for y in range(height):
            index = y * width + x
            if max(_absolute_deltas(candidate.rgb, reference.rgb,
                                    candidate.alpha, reference.alpha, index)) > tolerance:
                if first is None:
                    first = y
                last = y
        bounds.append(None if first is None else {"y": first, "height": last - first + 1})
    return bounds


def difference_runs(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int]]:
    """Return maximal horizontal runs of over-tolerance pixels, row-major."""
    width, height = candidate.width, candidate.height
    records = []
    for y in range(height):
        start = None
        for x in range(width):
            index = y * width + x
            differing = max(_absolute_deltas(candidate.rgb, reference.rgb,
                                              candidate.alpha, reference.alpha, index)) > tolerance
            if differing and start is None:
                start = x
            elif not differing and start is not None:
                records.append({"x": start, "y": y, "length": x - start})
                start = None
        if start is not None:
            records.append({"x": start, "y": y, "length": width - start})
    return records


def difference_column_runs(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int]]:
    """Return maximal vertical runs of over-tolerance pixels, column-major."""
    width, height = candidate.width, candidate.height
    records = []
    for x in range(width):
        start = None
        for y in range(height):
            index = y * width + x
            differing = max(_absolute_deltas(candidate.rgb, reference.rgb,
                                              candidate.alpha, reference.alpha, index)) > tolerance
            if differing and start is None:
                start = y
            elif not differing and start is not None:
                records.append({"x": x, "y": start, "length": y - start})
                start = None
        if start is not None:
            records.append({"x": x, "y": start, "length": height - start})
    return records


def delta_histogram(candidate: Image, reference: Image) -> list[dict[str, int]]:
    """Count compared pixels by their maximum absolute RGBA channel delta.

    Inputs are equally sized validated images, as checked by the CLI's
    comparison. Missing alpha planes represent opaque pixels.
    """
    counters = [0] * 256
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    for index in range(candidate.width * candidate.height):
        delta = max(_absolute_deltas(
            candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
        ))
        counters[delta] += 1
    return [{"delta": delta, "count": count}
            for delta, count in enumerate(counters) if count]
