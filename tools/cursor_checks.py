"""Refusals for the cursor art ``tools/make_cursors.py`` builds.

A grid must be a ``GRID_SIZE`` square of known cells, a hotspot must name a
grid cell, the nominal sizes must be Xcursor frame dimensions, and the art may
be a grid or a ``VectorCursor``. Each check returns its input in a normalized
form or raises ``ValueError`` naming what it refused, so the generator checks
every request before it builds or caches anything.
"""

from __future__ import annotations

if __package__:
    from tools.cursor_art import GRID_SIZE, PIXELS
    from tools.cursor_vector import VectorCursor
    from tools.cursor_vector import checked_size as _checked_size
    from tools.ints import is_plain_int
else:  # run from tools/ on sys.path, as make_cursors.py is run
    from cursor_art import GRID_SIZE, PIXELS
    from cursor_vector import VectorCursor
    from cursor_vector import checked_size as _checked_size
    from ints import is_plain_int


def checked_rows(rows, name="arrow"):
    """Return *rows* after checking it is a ``GRID_SIZE`` square of known cells."""
    if not isinstance(rows, (tuple, list)) or len(rows) != GRID_SIZE:
        raise ValueError(
            f"the {name} grid must have {GRID_SIZE} rows, not "
            f"{len(rows) if isinstance(rows, (tuple, list)) else type(rows).__name__}"
        )
    checked = []
    for y, row in enumerate(rows):
        if not isinstance(row, str) or len(row) != GRID_SIZE:
            width = len(row) if isinstance(row, str) else type(row).__name__
            raise ValueError(
                f"{name} grid row {y} must be a {GRID_SIZE}-character string, "
                f"not {width}"
            )
        for x, cell in enumerate(row):
            if cell not in PIXELS:
                raise ValueError(
                    f"{name} grid cell ({x}, {y}) is {cell!r}; expected one of "
                    f"{sorted(PIXELS)}"
                )
        checked.append(row)
    return tuple(checked)


def checked_hotspot(hotspot):
    """Return *hotspot* as a tuple after checking it names a grid cell."""
    if (
        not isinstance(hotspot, (tuple, list))
        or len(hotspot) != 2
        or not all(is_plain_int(value) for value in hotspot)
    ):
        raise ValueError(
            f"hotspot must be two integers: hotspot={hotspot!r}"
        )
    x, y = hotspot
    if not 0 <= x < GRID_SIZE or not 0 <= y < GRID_SIZE:
        raise ValueError(
            f"hotspot ({x}, {y}) lies outside the {GRID_SIZE}x{GRID_SIZE} grid"
        )
    return x, y


def checked_sizes(sizes):
    """Return *sizes* after checking each is an Xcursor frame dimension."""
    try:
        iterator = iter(sizes)
    except TypeError as exc:
        raise ValueError(
            "nominal sizes must be an iterable, not "
            f"{type(sizes).__name__}"
        ) from exc
    checked = [_checked_size(size, "nominal size") for size in iterator]
    if not checked:
        raise ValueError("at least one nominal size is required")
    return tuple(checked)


def checked_art(rows, name="arrow"):
    """Return *rows* if it is a ``VectorCursor`` or a checked grid, else refuse it."""
    if isinstance(rows, VectorCursor):
        return rows
    return checked_rows(rows, name)
