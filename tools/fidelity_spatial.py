"""Spatially indexed pixel diagnostics for fidelity surfaces."""

from __future__ import annotations

if __package__:
    from tools.fidelity_pixels import _absolute_deltas
    from tools.png import Image
else:  # imported by a directly run CLI
    from fidelity_pixels import _absolute_deltas
    from png import Image


def difference_columns(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each column of equally sized images."""
    width, height = candidate.width, candidate.height
    counts = [0] * width
    for index in range(width * height):
        if max(_absolute_deltas(candidate.rgb, reference.rgb, candidate.alpha,
                                reference.alpha, index)) > tolerance:
            counts[index % width] += 1
    return counts


def difference_rows(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each crop-relative row."""
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
    """Return each differing row's smallest crop-relative horizontal interval."""
    width, height = candidate.width, candidate.height
    bounds = []
    for y in range(height):
        first = last = None
        for x in range(width):
            index = y * width + x
            differing = max(_absolute_deltas(candidate.rgb, reference.rgb,
                                              candidate.alpha, reference.alpha, index)) > tolerance
            if differing and first is None:
                first = x
            if differing:
                last = x
        bounds.append(None if first is None else {"x": first, "width": last - first + 1})
    return bounds


def difference_column_bounds(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int] | None]:
    """Return each differing column's smallest crop-relative vertical interval."""
    width, height = candidate.width, candidate.height
    bounds = []
    for x in range(width):
        first = last = None
        for y in range(height):
            index = y * width + x
            differing = max(_absolute_deltas(candidate.rgb, reference.rgb,
                                              candidate.alpha, reference.alpha, index)) > tolerance
            if differing and first is None:
                first = y
            if differing:
                last = y
        bounds.append(None if first is None else {"y": first, "height": last - first + 1})
    return bounds


def _difference_axis_runs(
    candidate: Image, reference: Image, tolerance: int, *, vertical: bool
) -> list[dict[str, int]]:
    """Collect maximal over-tolerance intervals along each scanline."""
    width, height = candidate.width, candidate.height
    scanline_count, scanline_length = (width, height) if vertical else (height, width)
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    records = []
    for scanline in range(scanline_count):
        start = None
        for offset in range(scanline_length):
            x, y = (scanline, offset) if vertical else (offset, scanline)
            index = y * width + x
            differing = max(_absolute_deltas(
                candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
            )) > tolerance
            if differing and start is None:
                start = offset
            elif not differing and start is not None:
                run_x, run_y = (scanline, start) if vertical else (start, scanline)
                records.append({"x": run_x, "y": run_y, "length": offset - start})
                start = None
        if start is not None:
            run_x, run_y = (scanline, start) if vertical else (start, scanline)
            records.append({"x": run_x, "y": run_y, "length": scanline_length - start})
    return records


def difference_runs(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int]]:
    """Return maximal horizontal runs of over-tolerance pixels, row-major."""
    return _difference_axis_runs(candidate, reference, tolerance, vertical=False)


def difference_column_runs(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int]]:
    """Return maximal vertical runs of over-tolerance pixels, column-major."""
    return _difference_axis_runs(candidate, reference, tolerance, vertical=True)


def difference_centroid(candidate: Image, reference: Image, tolerance: int) -> dict[str, float] | None:
    """Return the equal-pixel centroid of over-tolerance pixels, crop-relative."""
    width, height = candidate.width, candidate.height
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    count = sum_x = sum_y = 0
    for index in range(width * height):
        if max(_absolute_deltas(candidate_rgb, reference_rgb, candidate_alpha,
                                reference_alpha, index)) > tolerance:
            count += 1
            sum_x += index % width
            sum_y += index // width
    if not count:
        return None
    return {"x": sum_x / count, "y": sum_y / count}
