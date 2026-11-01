"""Rank the most severe differing pixels in a pair of fidelity surfaces."""

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

    def ranked():
        for index in range(width * height):
            rgb_offset = index * 3
            candidate_rgb = candidate.rgb[rgb_offset:rgb_offset + 3]
            reference_rgb = reference.rgb[rgb_offset:rgb_offset + 3]
            candidate_alpha = 255 if candidate.alpha is None else candidate.alpha[index]
            reference_alpha = 255 if reference.alpha is None else reference.alpha[index]
            delta = max(
                *(abs(a - b) for a, b in zip(candidate_rgb, reference_rgb)),
                abs(candidate_alpha - reference_alpha),
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
            "candidate_rgba": [*candidate.rgb[offset:offset + 3], 255 if candidate.alpha is None else candidate.alpha[index]],
            "reference_rgba": [*reference.rgb[offset:offset + 3], 255 if reference.alpha is None else reference.alpha[index]],
            "max_delta": -negative_delta,
        })
    return records
