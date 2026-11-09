"""Spatially indexed pixel diagnostics for fidelity surfaces.

Every scan derives one 0/1 flag byte per pixel with the byte-level
arithmetic :func:`tools.fidelity_metrics.compare` uses for its
differing metric -- strided channel slices through
``tools.byte_lanes.abs_diff``, each translated to a flag byte by a
tolerance table, and the per-pixel channel flags ORed as one big
integer -- instead of re-deriving per-pixel RGBA deltas in Python,
which dominated a screenshot-sized spatial report.  Each scanline
result then reads the returned row-major flag string through C-speed
``bytes`` operations: ``count`` for axis counts, ``find``/``rfind``
for bounds, and a compiled ``\\x01+`` run regex for interval runs; a
column scanline is one strided ``flags[x::width]`` slice.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator

if __package__:
    from tools.byte_lanes import abs_diff
    from tools.fidelity_metrics import over_table
    from tools.png import Image
else:  # imported as the top-level package by a directly run CLI
    from byte_lanes import abs_diff
    from fidelity_metrics import over_table
    from png import Image

_RUN = re.compile(b"\x01+")


def differing_flags(candidate: Image, reference: Image, tolerance: int) -> bytes:
    """Return one 0/1 flag byte per pixel, row-major.

    A pixel's flag is 1 when its maximum raw RGBA delta strictly exceeds
    *tolerance*: RGB deltas are read straight from the packed planes,
    including beneath transparency, and a missing alpha plane counts every
    pixel as opaque 255 -- the same union the CLI's ``compare`` call
    computes. This is the module's only pass over the image planes; every
    scanline report reads the flag string it returns.

    The scan interface takes this string through the optional keyword-only
    *flags* parameter: a run that requests several spatial reports computes
    the pass once, up front, and hands the result to each call. Passing
    ``None`` (the default) derives the string here, so every one-function
    caller keeps the behaviour it had.
    """
    width, height = candidate.width, candidate.height
    pixels = width * height
    pa, pb = candidate.rgb, reference.rgb
    deltas = [abs_diff(pa[channel::3], pb[channel::3]) for channel in range(3)]
    alpha_a, alpha_b = candidate.alpha, reference.alpha
    if alpha_a is not None or alpha_b is not None:
        if alpha_a is None or alpha_b is None:
            # An Image without an alpha plane is fully opaque; representing it
            # as 255 lets an RGB image be compared against an RGBA one.
            opaque = bytes([255]) * pixels
            alpha_a = opaque if alpha_a is None else alpha_a
            alpha_b = opaque if alpha_b is None else alpha_b
        deltas.append(abs_diff(alpha_a, alpha_b))
    table = over_table(tolerance)
    flags = 0
    for delta in deltas:
        flags |= int.from_bytes(delta.translate(table), "little")
    return flags.to_bytes(pixels, "little")


def difference_rows(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[int]:
    """Count over-tolerance pixels in each row of equally sized images.

    *flags* shares one :func:`differing_flags` pass across a run of spatial
    reports; ``None`` derives the string here.
    """
    return _difference_axis_counts(
        candidate, reference, tolerance, vertical=False, flags=flags
    )


def difference_columns(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[int]:
    """Count over-tolerance pixels in each column of equally sized images.

    *flags* shares one :func:`differing_flags` pass across a run of spatial
    reports; ``None`` derives the string here.
    """
    return _difference_axis_counts(
        candidate, reference, tolerance, vertical=True, flags=flags
    )


def _difference_axis_counts(
    candidate: Image, reference: Image, tolerance: int,
    *, vertical: bool, flags: bytes | None = None,
) -> list[int]:
    """Count each over-tolerance pixel once in its row or column."""
    flags = differing_flags(candidate, reference, tolerance) if flags is None else flags
    width, height = candidate.width, candidate.height
    if vertical:
        return [flags[x::width].count(1) for x in range(width)]
    return [flags[y * width:(y + 1) * width].count(1) for y in range(height)]


def difference_row_bounds(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[dict[str, int] | None]:
    """Return each differing row's smallest crop-relative horizontal interval.

    *flags* shares one :func:`differing_flags` pass across a run of spatial
    reports; ``None`` derives the string here.
    """
    return _difference_axis_bounds(
        candidate, reference, tolerance, vertical=False, flags=flags
    )


def difference_column_bounds(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[dict[str, int] | None]:
    """Return each differing column's smallest crop-relative vertical interval.

    *flags* shares one :func:`differing_flags` pass across a run of spatial
    reports; ``None`` derives the string here.
    """
    return _difference_axis_bounds(
        candidate, reference, tolerance, vertical=True, flags=flags
    )


def _difference_axis_bounds(
    candidate: Image, reference: Image, tolerance: int,
    *, vertical: bool, flags: bytes | None = None,
) -> list[dict[str, int] | None]:
    """Collect each scanline's smallest interval containing a differing pixel."""
    flags = differing_flags(candidate, reference, tolerance) if flags is None else flags
    width, height = candidate.width, candidate.height
    start_key, length_key = ("y", "height") if vertical else ("x", "width")
    bounds = []
    for scanline in range(width if vertical else height):
        scanline_flags = (
            flags[scanline::width] if vertical
            else flags[scanline * width:(scanline + 1) * width]
        )
        first = scanline_flags.find(1)
        if first < 0:
            bounds.append(None)
        else:
            bounds.append({start_key: first,
                           length_key: scanline_flags.rfind(1) - first + 1})
    return bounds


def _iter_difference_axis_runs(
    candidate: Image, reference: Image, tolerance: int,
    *, vertical: bool, flags: bytes | None = None,
) -> Iterator[dict[str, int]]:
    """Yield maximal over-tolerance intervals along each scanline.

    Horizontal runs scan rows row-major; vertical runs scan columns
    column-major, so a run never spans a scanline boundary -- the same
    segmentation the axis counts and bounds read from the flag string.
    *flags* shares one :func:`differing_flags` pass across a run of spatial
    reports; ``None`` derives the string here.
    """
    flags = differing_flags(candidate, reference, tolerance) if flags is None else flags
    width, height = candidate.width, candidate.height
    for scanline in range(width if vertical else height):
        scanline_flags = (
            flags[scanline::width] if vertical
            else flags[scanline * width:(scanline + 1) * width]
        )
        for match in _RUN.finditer(scanline_flags):
            start, end = match.span()
            if vertical:
                yield {"x": scanline, "y": start, "length": end - start}
            else:
                yield {"x": start, "y": scanline, "length": end - start}


def select_longest_run(runs: Iterable[dict[str, int]]) -> dict[str, int] | None:
    """Return the first longest run without materializing the iterable."""
    return max(runs, key=lambda run: run["length"], default=None)


def longest_difference_run(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> dict[str, int] | None:
    """Return the longest horizontal mismatch run; ties use earliest (y, x)."""
    return select_longest_run(
        _iter_difference_axis_runs(
            candidate, reference, tolerance, vertical=False, flags=flags
        )
    )


def longest_difference_column_run(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> dict[str, int] | None:
    """Return the longest vertical mismatch run; ties use earliest (x, y)."""
    return select_longest_run(
        _iter_difference_axis_runs(
            candidate, reference, tolerance, vertical=True, flags=flags
        )
    )


def difference_runs(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[dict[str, int]]:
    """Return maximal horizontal runs of over-tolerance pixels, row-major."""
    return list(_iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=False, flags=flags
    ))


def difference_run_count(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> int:
    """Count horizontal mismatch runs without retaining their intervals."""
    return sum(1 for _ in _iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=False, flags=flags
    ))


def difference_column_run_count(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> int:
    """Count vertical mismatch runs without retaining their intervals."""
    return sum(1 for _ in _iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=True, flags=flags
    ))


def difference_column_runs(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> list[dict[str, int]]:
    """Return maximal vertical runs of over-tolerance pixels, column-major."""
    return list(_iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=True, flags=flags
    ))


def difference_centroid(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> dict[str, float] | None:
    """Return the equal-pixel centroid of over-tolerance pixels, crop-relative.

    The centroid reads along the flag string's maximal runs rather than
    per pixel: within one run of ``end - start`` pixels at 0-based columns
    ``start`` .. ``end - 1`` the x sum is ``length * (start + end - 1) / 2``
    and the y sum adds ``length * y`` per row, so the denominators the old
    per-pixel walk accumulated are reproduced exactly while the row loop
    visits only run boundaries.
    """
    width, height = candidate.width, candidate.height
    flags = differing_flags(candidate, reference, tolerance) if flags is None else flags
    count = flags.count(1)
    if not count:
        return None
    sum_x = sum_y = 0
    for y in range(height):
        for match in _RUN.finditer(flags[y * width:(y + 1) * width]):
            start, end = match.span()
            run_length = end - start
            sum_x += run_length * (start + end - 1) // 2
            sum_y += run_length * y
    return {"x": sum_x / count, "y": sum_y / count}
