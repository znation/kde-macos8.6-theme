"""Generate the Mac OS 8.6 Platinum Xcursor pointer set from pixel grids.

The grids, hotspots and X-name aliases live in ``tools/cursor_art.py``; this
module validates a grid, scales it nearest-neighbour to the nominal sizes 16,
24 and 32, encodes each frame as an Xcursor image chunk, and writes every
canonical cursor and alias into the icon theme package's ``cursors/``.

Run ``python3 tools/make_cursors.py`` from anywhere; the output is
deterministic, so re-running rewrites identical bytes. A cursors directory that
resolves outside the repository (a checked-in symlink) is refused by name
before anything is written, so the artifact stays in the icon theme package.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_bytes_atomically
    from tools.containment import require_within_repo
    from tools.cursor_art import ARROW_GRID, CURSORS, GRID_SIZE, HOTSPOT, PIXELS
    from tools.diagnostics import report_error
    from tools.ints import is_plain_int
    from tools.repo_root import ROOT
    from tools.xcursor import write_rgba_cursor
else:  # run directly: python3 tools/make_cursors.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_bytes_atomically
    from containment import require_within_repo
    from cursor_art import ARROW_GRID, CURSORS, GRID_SIZE, HOTSPOT, PIXELS
    from diagnostics import report_error
    from ints import is_plain_int
    from repo_root import ROOT
    from xcursor import write_rgba_cursor

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


def render_rgba(rows, size, name="arrow"):
    """Return *size* x *size* packed RGBA pixels scaled from the 16x16 *rows*."""
    checked = _checked_rows(rows, name)
    if not is_plain_int(size) or size < 1:
        raise ValueError(f"size must be a positive integer: size={size!r}")
    rgba = bytearray(size * size * 4)
    for y in range(size):
        source_y = y * GRID_SIZE // size
        source_row = checked[source_y]
        for x in range(size):
            source_x = x * GRID_SIZE // size
            start = (y * size + x) * 4
            rgba[start : start + 4] = PIXELS[source_row[source_x]]
    return bytes(rgba)


def _scaled_hotspot(size, hotspot):
    """Return the grid *hotspot* at the first destination pixel it covers."""
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
    # The nearest-neighbour mapping sends destination pixel ``d`` to source
    # pixel ``d * 16 // size``, so a source pixel's first destination pixel is
    # the ceiling of its scaled start.
    return (
        (x * size + GRID_SIZE - 1) // GRID_SIZE,
        (y * size + GRID_SIZE - 1) // GRID_SIZE,
    )


def cursor_bytes(
    rows=ARROW_GRID, sizes=NOMINAL_SIZES, hotspot=HOTSPOT, name="arrow"
):
    """Return the Xcursor bytes for *rows* at every nominal *size*."""
    checked = _checked_rows(rows, name)
    frames = []
    for size in sizes:
        if not is_plain_int(size) or size < 1:
            raise ValueError(
                f"nominal size must be a positive integer: size={size!r}"
            )
        hotspot_x, hotspot_y = _scaled_hotspot(size, hotspot)
        rgba = render_rgba(checked, size, name)
        frames.append((size, size, size, hotspot_x, hotspot_y, rgba))
    if not frames:
        raise ValueError("at least one nominal size is required")
    # The frames are already RGBA, so write them directly: encoding each one
    # to PNG for ``write_cursor`` to decode again would redo the pixel work
    # twice for no change in the written bytes.
    return write_rgba_cursor(frames)


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
    try:
        require_within_repo(directory, ROOT, action="write")
    except ValueError as exc:
        return report_error(TOOL, str(exc))
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return report_error(TOOL, f"cannot create {directory}: {exc}")
    for canonical, rows, hotspot, aliases in CURSORS:
        data = cursor_bytes(rows, NOMINAL_SIZES, hotspot, name=canonical)
        for name in (canonical, *aliases):
            target = directory / name
            try:
                write_bytes_atomically(target, data)
            except OSError as exc:
                return report_error(TOOL, f"cannot write {target}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
