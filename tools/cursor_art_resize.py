"""The move, resize and precision cursor grids for the Platinum pointer set.

The 16x16 ASCII grids and hotspots for the move cross, the four resize arrows
and the crosshair. ``#`` is the black face, ``.`` the white outline and a space
is transparent. The grids in this module are bound to their canonical X names
by ``tools/cursor_art.py``; ``tools/make_cursors.py`` scales and writes them.
"""

# The move cross points up, down, left and right; its hotspot is the centre.
FLEUR_HOTSPOT = (7, 7)
FLEUR_GRID = (
    "      ....      ",
    "      .##.      ",
    "     .####.     ",
    "      .##.      ",
    "      .##.      ",
    "  .   .##.   .  ",
    "..#....##....#..",
    ".##############.",
    ".##############.",
    "..#....##....#..",
    "  .   .##.   .  ",
    "      .##.      ",
    "      .##.      ",
    "     .####.     ",
    "      .##.      ",
    "      ....      ",
)

# The horizontal resize arrow joins left and right arrowheads through a stem
# on rows 7-8; its hotspot is the centre of the stem.
SIZE_HOR_HOTSPOT = (7, 7)
SIZE_HOR_GRID = (
    "                ",
    "                ",
    "                ",
    "                ",
    "  ...      ...  ",
    " ..#.      .#.. ",
    "..##........##..",
    ".##############.",
    ".##############.",
    "..##........##..",
    " ..#.      .#.. ",
    "  ...      ...  ",
    "                ",
    "                ",
    "                ",
    "                ",
)

# The vertical resize arrow is the horizontal glyph rotated a quarter turn;
# its hotspot is the centre of its stem.
SIZE_VER_HOTSPOT = (7, 7)
SIZE_VER_GRID = (
    "      ....      ",
    "     ..##..     ",
    "    ..####..    ",
    "    .######.    ",
    "    ...##...    ",
    "      .##.      ",
    "      .##.      ",
    "      .##.      ",
    "      .##.      ",
    "      .##.      ",
    "      .##.      ",
    "    ...##...    ",
    "    .######.    ",
    "    ..####..    ",
    "     ..##..     ",
    "      ....      ",
)

# The NW-SE resize arrow draws a black arrowhead in each corner joined by a
# two-pixel shaft along the main diagonal; its hotspot is on the shaft.
SIZE_FDIAG_HOTSPOT = (7, 7)
SIZE_FDIAG_GRID = (
    "                ",
    " .......        ",
    " .#####.        ",
    " .####..        ",
    " .####..        ",
    " .##.##..       ",
    " .#...##..      ",
    " ... ..##..     ",
    "      ..##..... ",
    "       ..##..#. ",
    "        ..####. ",
    "         ..###. ",
    "        ..####. ",
    "        .#####. ",
    "        ....... ",
    "                ",
)

# The NE-SW resize arrow is the forward diagonal glyph mirrored left to right;
# its hotspot is on the shaft.
SIZE_BDIAG_HOTSPOT = (7, 7)
SIZE_BDIAG_GRID = (
    "                ",
    "        ....... ",
    "        .#####. ",
    "        ..####. ",
    "        ..####. ",
    "       ..##.##. ",
    "      ..##...#. ",
    "     ..##.. ... ",
    " .....##..      ",
    " .#..##..       ",
    " .####..        ",
    " .###..         ",
    " .####..        ",
    " .#####.        ",
    " .......        ",
    "                ",
)

# The precision cross puts a one-pixel black arm on row 7 and another on
# column 7, crossing at the hotspot; every other cell is outline or blank.
CROSSHAIR_HOTSPOT = (7, 7)
CROSSHAIR_GRID = (
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    ".......#........",
    "################",
    ".......#........",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
)

