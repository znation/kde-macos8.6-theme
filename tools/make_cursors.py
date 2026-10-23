"""Generate the Mac OS 8.6 Platinum Xcursor arrow from a pixel grid.

The theme ships its cursor inside the ``org.macos8.desktop`` icon theme package,
under ``cursors/``: ``left_ptr`` plus the X-name aliases ``arrow``, ``default``
and ``top_left_arrow``. Each file holds the same art at nominal sizes 16, 24 and
32. No reference screenshot in ``macos8.6-screenshots/`` shows the mouse
pointer, so the arrow is our own Platinum-style drawing on the pinned #000000
face and #FFFFFF outline, not traced from Apple's artwork; the nominal sizes,
the Xcursor container and the X names are KDE/X-required values.

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
    from tools.atomic_write import write_atomically
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
    from tools.ints import is_plain_int
    from tools.png import encode_rgba_png
    from tools.xcursor import write_cursor
else:  # run directly: python3 tools/make_cursors.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from containment import require_within_repo
    from diagnostics import report_error
    from ints import is_plain_int
    from png import encode_rgba_png
    from xcursor import write_cursor

TOOL = "make_cursors"
ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = Path("theme", "icons", "org.macos8.desktop")
CURSORS_DIR = "cursors"
CURSOR_NAMES = ("left_ptr", "arrow", "default", "top_left_arrow")
NOMINAL_SIZES = (16, 24, 32)
GRID_SIZE = 16
HOTSPOT = (1, 1)

# The arrow's tip is at grid (1, 1). ``#`` is the black face, ``.`` the white
# outline and a space is transparent. The art is drawn at 16x16 and scaled
# nearest-neighbour to the larger nominal sizes.
ARROW_GRID = (
    "...             ",
    ".#..            ",
    ".##..           ",
    ".###..          ",
    ".####..         ",
    ".#####..        ",
    ".######..       ",
    ".#######..      ",
    ".########.      ",
    "....##....      ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   ....         ",
)

PIXELS = {
    "#": b"\x00\x00\x00\xff",
    ".": b"\xff\xff\xff\xff",
    " ": b"\x00\x00\x00\x00",
}


def _checked_rows(rows):
    """Return *rows* after checking it is a ``GRID_SIZE`` square of known cells."""
    if not isinstance(rows, (tuple, list)) or len(rows) != GRID_SIZE:
        raise ValueError(
            f"the arrow grid must have {GRID_SIZE} rows, not "
            f"{len(rows) if isinstance(rows, (tuple, list)) else type(rows).__name__}"
        )
    checked = []
    for y, row in enumerate(rows):
        if not isinstance(row, str) or len(row) != GRID_SIZE:
            width = len(row) if isinstance(row, str) else type(row).__name__
            raise ValueError(
                f"arrow grid row {y} must be a {GRID_SIZE}-character string, "
                f"not {width}"
            )
        for x, cell in enumerate(row):
            if cell not in PIXELS:
                raise ValueError(
                    f"arrow grid cell ({x}, {y}) is {cell!r}; expected one of "
                    f"{sorted(PIXELS)}"
                )
        checked.append(row)
    return tuple(checked)


def render_rgba(rows, size):
    """Return *size* x *size* packed RGBA pixels scaled from the 16x16 *rows*."""
    checked = _checked_rows(rows)
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


def cursor_bytes(rows=ARROW_GRID, sizes=NOMINAL_SIZES, hotspot=HOTSPOT):
    """Return the Xcursor bytes for *rows* at every nominal *size*."""
    checked = _checked_rows(rows)
    frames = []
    for size in sizes:
        if not is_plain_int(size) or size < 1:
            raise ValueError(
                f"nominal size must be a positive integer: size={size!r}"
            )
        hotspot_x, hotspot_y = _scaled_hotspot(size, hotspot)
        png = encode_rgba_png(size, size, render_rgba(checked, size))
        frames.append((size, size, size, hotspot_x, hotspot_y, png))
    if not frames:
        raise ValueError("at least one nominal size is required")
    return write_cursor(frames)


def _write_atomic(path: Path, data: bytes) -> None:
    """Write *data* to *path* so *path* is the old file or the whole new one."""
    write_atomically(path, lambda destination: destination.write(data))


def main(argv: list[str] | None = None) -> int:
    """Run the generator CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Regenerate the icon theme package's Xcursor arrow artifact."
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
    data = cursor_bytes()
    for name in CURSOR_NAMES:
        target = directory / name
        try:
            _write_atomic(target, data)
        except OSError as exc:
            return report_error(TOOL, f"cannot write {target}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
