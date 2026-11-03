"""Spatially indexed pixel diagnostics for fidelity surfaces."""

from __future__ import annotations

from collections.abc import Iterator

if __package__:
    from tools.fidelity_pixels import _absolute_deltas
    from tools.png import Image
else:  # imported by a directly run CLI
    from fidelity_pixels import _absolute_deltas
    from png import Image


def difference_columns(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each column of equally sized images."""
    return _difference_axis_counts(candidate, reference, tolerance, vertical=True)


def difference_rows(candidate: Image, reference: Image, tolerance: int) -> list[int]:
    """Count over-tolerance pixels in each crop-relative row."""
    return _difference_axis_counts(candidate, reference, tolerance, vertical=False)


def _difference_axis_counts(
    candidate: Image, reference: Image, tolerance: int, *, vertical: bool
) -> list[int]:
    """Count each over-tolerance pixel once in its row or column."""
    width, height = candidate.width, candidate.height
    scanline_count, scanline_length = (width, height) if vertical else (height, width)
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    counts = []
    for scanline in range(scanline_count):
        count = 0
        for offset in range(scanline_length):
            index = offset * width + scanline if vertical else scanline * width + offset
            count += max(_absolute_deltas(
                candidate_rgb, reference_rgb, candidate_alpha, reference_alpha, index
            )) > tolerance
        counts.append(count)
    return counts


def _difference_axis_bounds(
    candidate: Image, reference: Image, tolerance: int, *, vertical: bool
) -> list[dict[str, int] | None]:
    """Collect each scanline's smallest interval containing a differing pixel."""
    width, height = candidate.width, candidate.height
    scanline_count, scanline_length = (width, height) if vertical else (height, width)
    start_key, length_key = ("y", "height") if vertical else ("x", "width")
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
    bounds = []
    for scanline in range(scanline_count):
        first = last = None
        for offset in range(scanline_length):
            index = offset * width + scanline if vertical else scanline * width + offset
            differing = max(_absolute_deltas(candidate_rgb, reference_rgb,
                                              candidate_alpha, reference_alpha, index)) > tolerance
            if differing and first is None:
                first = offset
            if differing:
                last = offset
        bounds.append(None if first is None else
                      {start_key: first, length_key: last - first + 1})
    return bounds


def difference_row_bounds(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int] | None]:
    """Return each differing row's smallest crop-relative horizontal interval."""
    return _difference_axis_bounds(candidate, reference, tolerance, vertical=False)


def difference_column_bounds(candidate: Image, reference: Image, tolerance: int) -> list[dict[str, int] | None]:
    """Return each differing column's smallest crop-relative vertical interval."""
    return _difference_axis_bounds(candidate, reference, tolerance, vertical=True)


def _difference_axis_runs(
    candidate: Image, reference: Image, tolerance: int, *, vertical: bool
) -> list[dict[str, int]]:
    """Collect maximal over-tolerance intervals along each scanline."""
    return list(_iter_difference_axis_runs(candidate, reference, tolerance, vertical=vertical))


def _iter_difference_axis_runs(
    candidate: Image, reference: Image, tolerance: int, *, vertical: bool
) -> Iterator[dict[str, int]]:
    """Yield maximal over-tolerance intervals along each scanline."""
    width, height = candidate.width, candidate.height
    scanline_count, scanline_length = (width, height) if vertical else (height, width)
    candidate_rgb, reference_rgb = candidate.rgb, reference.rgb
    candidate_alpha, reference_alpha = candidate.alpha, reference.alpha
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
                yield {"x": run_x, "y": run_y, "length": offset - start}
                start = None
        if start is not None:
            run_x, run_y = (scanline, start) if vertical else (start, scanline)
            yield {"x": run_x, "y": run_y, "length": scanline_length - start}


def longest_difference_run(candidate: Image, reference: Image, tolerance: int) -> dict[str, int] | None:
    """Return the longest horizontal mismatch run; ties use earliest (y, x)."""
    best = None
    for run in _iter_difference_axis_runs(candidate, reference, tolerance, vertical=False):
        if best is None or run["length"] > best["length"]:
            best = run
    return best


def longest_difference_column_run(candidate: Image, reference: Image, tolerance: int) -> dict[str, int] | None:
    """Return the longest vertical mismatch run; ties use earliest (x, y)."""
    best = None
    for run in _iter_difference_axis_runs(candidate, reference, tolerance, vertical=True):
        if best is None or run["length"] > best["length"]:
            best = run
    return best


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
