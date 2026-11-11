"""Spatially indexed pixel diagnostics for fidelity surfaces.

Every scan derives one 0/1 flag byte per pixel with the byte-level
arithmetic :func:`tools.fidelity_metrics.compare` uses for its
differing metric -- the shared per-channel absolute-delta byte strings
:func:`tools.fidelity_pixels.channel_deltas` returns, each translated
to a flag byte by a tolerance table, and the per-pixel channel flags
ORed as one big integer -- instead of re-deriving per-pixel RGBA
deltas in Python, which dominated a screenshot-sized spatial report.
Each scanline result then reads the returned row-major flag string
through C-speed
``bytes`` operations: ``count`` for axis counts, ``find``/``rfind``
for bounds, and a compiled ``\\x01+`` run regex for interval runs; a
column scanline is one strided ``flags[x::width]`` slice.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator

if __package__:
    from tools.fidelity_metrics import over_table
    from tools.fidelity_pixels import channel_deltas
    from tools.png import Image
else:  # imported as the top-level package by a directly run CLI
    from fidelity_metrics import over_table
    from fidelity_pixels import channel_deltas
    from png import Image

_RUN = re.compile(b"\x01+")


def differing_flags(
    candidate: Image, reference: Image, tolerance: int,
    *, deltas: list[bytes] | None = None,
) -> bytes:
    """Return one 0/1 flag byte per pixel, row-major.

    A pixel's flag is 1 when its maximum raw RGBA delta strictly exceeds
    *tolerance*: RGB deltas are read straight from the packed planes,
    including beneath transparency, and a missing alpha plane counts every
    pixel as opaque 255 -- the same union the CLI's ``compare`` call
    computes. The derivation reads the shared per-channel absolute-delta
    byte strings :func:`tools.fidelity_pixels.channel_deltas` returns --
    the same list the pixel reports read -- translates each channel to a
    flag byte through *tolerance*'s table, and ORs the channel flags per
    pixel as one big integer.

    The scan interface takes the channel-delta list through the optional
    keyword-only *deltas* parameter: a run that requests spatial and pixel
    reports together computes that pass once, up front, and hands the same
    list to this derivation and each pixel report. Passing ``None`` (the
    default) derives the list here, so every one-function caller keeps the
    behaviour it had.
    """
    width, height = candidate.width, candidate.height
    deltas = channel_deltas(candidate, reference) if deltas is None else deltas
    table = over_table(tolerance)
    flags = 0
    for delta in deltas:
        flags |= int.from_bytes(delta.translate(table), "little")
    return flags.to_bytes(width * height, "little")


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


def _axis_scanlines(flags: bytes, width: int, height: int, vertical: bool):
    """Yield each row or column flag slice in report order."""
    if vertical:
        for x in range(width):
            yield x, flags[x::width]
    else:
        for y in range(height):
            start = y * width
            yield y, flags[start:start + width]


def _difference_axis_counts(
    candidate: Image, reference: Image, tolerance: int,
    *, vertical: bool, flags: bytes | None = None,
) -> list[int]:
    """Count each over-tolerance pixel once in its row or column."""
    flags = differing_flags(candidate, reference, tolerance) if flags is None else flags
    width, height = candidate.width, candidate.height
    return [scanline.count(1)
            for _, scanline in _axis_scanlines(flags, width, height, vertical)]


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
    for _, scanline_flags in _axis_scanlines(flags, width, height, vertical):
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
    for scanline, scanline_flags in _axis_scanlines(flags, width, height, vertical):
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


def iter_difference_runs(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> Iterator[dict[str, int]]:
    """Yield horizontal mismatch runs in row-major order."""
    return _iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=False, flags=flags
    )


def iter_difference_column_runs(
    candidate: Image, reference: Image, tolerance: int, *, flags=None
) -> Iterator[dict[str, int]]:
    """Yield vertical mismatch runs in column-major order."""
    return _iter_difference_axis_runs(
        candidate, reference, tolerance, vertical=True, flags=flags
    )


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
    for y, row_flags in _axis_scanlines(flags, width, height, vertical=False):
        for match in _RUN.finditer(row_flags):
            start, end = match.span()
            run_length = end - start
            sum_x += run_length * (start + end - 1) // 2
            sum_y += run_length * y
    return {"x": sum_x / count, "y": sum_y / count}
