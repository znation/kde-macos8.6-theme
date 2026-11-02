"""Per-channel counts and ranked pixels for fidelity surfaces with over-tolerance deltas."""

from __future__ import annotations

import heapq

if __package__:
    from tools.png import Image
else:  # imported by a directly run CLI
    from png import Image


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
            rgb_offset = index * 3
            red_delta = abs(candidate_rgb[rgb_offset] - reference_rgb[rgb_offset])
            green_delta = abs(candidate_rgb[rgb_offset + 1] - reference_rgb[rgb_offset + 1])
            blue_delta = abs(candidate_rgb[rgb_offset + 2] - reference_rgb[rgb_offset + 2])
            alpha_delta = abs(
                (255 if candidate_alpha is None else candidate_alpha[index])
                - (255 if reference_alpha is None else reference_alpha[index])
            )
            delta = max(
                red_delta, green_delta, blue_delta, alpha_delta
            )
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
        rgb_offset = index * 3
        red_delta = abs(candidate_rgb[rgb_offset] - reference_rgb[rgb_offset])
        green_delta = abs(candidate_rgb[rgb_offset + 1] - reference_rgb[rgb_offset + 1])
        blue_delta = abs(candidate_rgb[rgb_offset + 2] - reference_rgb[rgb_offset + 2])
        alpha_delta = abs(
            (255 if candidate_alpha is None else candidate_alpha[index])
            - (255 if reference_alpha is None else reference_alpha[index])
        )
        if red_delta > tolerance:
            counts["r"] += 1
        if green_delta > tolerance:
            counts["g"] += 1
        if blue_delta > tolerance:
            counts["b"] += 1
        if alpha_delta > tolerance:
            counts["a"] += 1
    return counts


def delta_histogram(candidate: Image, reference: Image) -> list[dict[str, int]]:
    """Count compared pixels by their maximum absolute RGBA channel delta.

    Inputs are equally sized validated images, as checked by the CLI's
    comparison. Missing alpha planes represent opaque pixels.
    """
    counters = [0] * 256
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    for index in range(candidate.width * candidate.height):
        offset = index * 3
        delta = max(
            abs(candidate_rgb[offset] - reference_rgb[offset]),
            abs(candidate_rgb[offset + 1] - reference_rgb[offset + 1]),
            abs(candidate_rgb[offset + 2] - reference_rgb[offset + 2]),
            abs((255 if candidate_alpha is None else candidate_alpha[index])
                - (255 if reference_alpha is None else reference_alpha[index])),
        )
        counters[delta] += 1
    return [{"delta": delta, "count": count}
            for delta, count in enumerate(counters) if count]
