"""Generate the Mac OS 8.6 Platinum Xcursor pointer set from pixel grids.

The grids and hotspots live in ``tools/cursor_art_pointers.py``,
``tools/cursor_art_resize.py`` and ``tools/cursor_art_drag.py``; the X-name
manifest and palette live in ``tools/cursor_art.py``. This module validates a
grid, scales it nearest-neighbour to the nominal sizes 16, 24 and 32, encodes
each frame as an Xcursor image chunk, and writes every canonical cursor and
alias into the icon theme package's ``cursors/``.

Run ``python3 tools/make_cursors.py`` from anywhere; the output is
deterministic, so re-running rewrites identical bytes. A cursors directory that
resolves outside the repository (a checked-in symlink) is refused by name
before anything is written, so the artifact stays in the icon theme package.

Exit status: 0 when every cursor file was written (and for ``--help``/``-h``),
2 for a usage error, a cursors directory that resolves outside the repository,
or a directory or file that cannot be created or written.
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_bytes_atomically
    from tools.cursor_art import ARROW_GRID, CURSORS, GRID_SIZE, HOTSPOT, PIXELS
    from tools.generated_files import write_generated_files
    from tools.ints import is_plain_int
    from tools.repo_root import ROOT
    from tools.xcursor import MAX_IMAGE_SIZE, write_rgba_cursor
else:  # run directly: python3 tools/make_cursors.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_bytes_atomically
    from cursor_art import ARROW_GRID, CURSORS, GRID_SIZE, HOTSPOT, PIXELS
    from generated_files import write_generated_files
    from ints import is_plain_int
    from repo_root import ROOT
    from xcursor import MAX_IMAGE_SIZE, write_rgba_cursor

TOOL = "make_cursors"
PACKAGE_DIR = Path("theme", "icons", "org.macos8.desktop")
CURSORS_DIR = "cursors"
NOMINAL_SIZES = (16, 24, 32)


def _checked_rows(rows, name="arrow"):
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


def _checked_size(size, noun="size"):
    """Return *size* after checking it fits an Xcursor image frame.

    The renderer allocates ``size * size * 4`` bytes, so a value above the
    writer's frame-dimension limit is refused here, naming the limit, instead
    of attempting an enormous allocation and only then failing in
    :func:`tools.xcursor.write_rgba_cursor`.
    """
    if not is_plain_int(size) or size < 1:
        raise ValueError(f"{noun} must be a positive integer: size={size!r}")
    if size > MAX_IMAGE_SIZE:
        raise ValueError(
            f"{noun} must be at most {MAX_IMAGE_SIZE} (the Xcursor frame "
            f"limit): size={size}"
        )
    return size


def render_rgba(rows, size, name="arrow"):
    """Return *size* x *size* packed RGBA pixels scaled from the 16x16 *rows*.

    Raises ``ValueError`` when *size* is not an integer in
    1..``MAX_IMAGE_SIZE``, the writer's frame-dimension limit.
    """
    checked = _checked_rows(rows, name)
    size = _checked_size(size)
    rgba = bytearray(size * size * 4)
    for y in range(size):
        source_y = y * GRID_SIZE // size
        source_row = checked[source_y]
        for x in range(size):
            source_x = x * GRID_SIZE // size
            start = (y * size + x) * 4
            rgba[start : start + 4] = PIXELS[source_row[source_x]]
    return bytes(rgba)


def _checked_hotspot(hotspot):
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


def _checked_sizes(sizes):
    """Return *sizes* after checking each is an Xcursor frame dimension."""
    checked = [_checked_size(size, "nominal size") for size in sizes]
    if not checked:
        raise ValueError("at least one nominal size is required")
    return tuple(checked)


def _scaled_hotspot(size, hotspot):
    """Return the grid *hotspot* at the first destination pixel it covers."""
    x, y = _checked_hotspot(hotspot)
    # The nearest-neighbour mapping sends destination pixel ``d`` to source
    # pixel ``d * 16 // size``, so a source pixel's first destination pixel is
    # the ceiling of its scaled start. A size below the grid maps several
    # source pixels to one destination pixel and can skip the hotspot's source
    # pixel entirely; clamp to the last rendered pixel so the frame's hotspot
    # stays inside its image.
    return (
        min((x * size + GRID_SIZE - 1) // GRID_SIZE, size - 1),
        min((y * size + GRID_SIZE - 1) // GRID_SIZE, size - 1),
    )


def _build_cursor_bytes(rows, sizes, hotspot, name):
    """Build the Xcursor bytes for already-checked *rows* and *sizes*."""
    frames = []
    for size in _checked_sizes(sizes):
        hotspot_x, hotspot_y = _scaled_hotspot(size, hotspot)
        rgba = render_rgba(rows, size, name)
        frames.append((size, size, size, hotspot_x, hotspot_y, rgba))
    # The frames are already RGBA, so write them directly: encoding each one
    # to PNG for ``write_cursor`` to decode again would redo the pixel work
    # twice for no change in the written bytes.
    return write_rgba_cursor(frames)


# Built cursors, keyed by their validated inputs. A build is pure: the same
# grid, sizes, hotspot and name always produce the same bytes. The committed
# manifest's checks regenerate the whole set from ``cursor_art.CURSORS``
# several times in one ``make check`` (fresh-output, variants and determinism
# cases), which measured 84 distinct builds of 125 requests; the cache turns
# the repeated ones into a lookup. The entry-count bound keeps a caller
# generating many variants from growing it without limit; with the shipped
# nominal sizes one entry is under 7 KiB. Rows, sizes and the hotspot are
# checked before this cache is consulted, so a malformed request is refused on
# every call rather than being hidden by a cached result.
_MAX_CACHED_CURSORS = 128


@functools.lru_cache(maxsize=_MAX_CACHED_CURSORS)
def _cached_cursor_bytes(rows, sizes, hotspot, name):
    """Return :func:`_build_cursor_bytes`'s result, reusing an unchanged one."""
    return _build_cursor_bytes(rows, sizes, hotspot, name)


def cursor_bytes(
    rows=ARROW_GRID, sizes=NOMINAL_SIZES, hotspot=HOTSPOT, name="arrow"
):
    """Return the Xcursor bytes for *rows* at every nominal *size*.

    Each size must be an integer in 1..``MAX_IMAGE_SIZE``, the writer's
    frame-dimension limit. The result is cached by the validated rows, sizes, hotspot and name, so a
    caller that regenerates an unchanged cursor (the manifest checks do) does
    not redo its pixel and container work. Sizes and the hotspot are checked
    before the lookup, so a malformed request is refused on every call rather
    than being answered by an earlier build whose arguments compare equal
    (``16``, ``16.0`` and ``True`` all compare equal in a cache key).
    """
    checked_rows = _checked_rows(rows, name)
    sizes_key = _checked_sizes(sizes)
    hotspot_key = _checked_hotspot(hotspot)
    return _cached_cursor_bytes(checked_rows, sizes_key, hotspot_key, name)


def main(argv: list[str] | None = None) -> int:
    """Run the generator CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Regenerate the icon theme package's Xcursor pointer set."
        ),
        epilog=(
            "exit status: 0 when every cursor file was written, "
            "2 on a usage or read/write error"
        ),
    )
    parser.parse_args(argv)
    directory = ROOT / PACKAGE_DIR / CURSORS_DIR
    files = []
    for canonical, rows, hotspot, aliases in CURSORS:
        data = cursor_bytes(rows, NOMINAL_SIZES, hotspot, name=canonical)
        for name in (canonical, *aliases):
            files.append((directory / name, data))
    # The publisher's write comes from this module's name so a test patching
    # make_cursors.write_bytes_atomically still intercepts the writes.
    return write_generated_files(
        TOOL, ROOT, directory, files, write=write_bytes_atomically
    )


if __name__ == "__main__":
    sys.exit(main())
