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
