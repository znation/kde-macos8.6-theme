"""The drag, hand and forbidden cursor grids for the Platinum pointer set.

The 16x16 ASCII grids and hotspots for the circle-slash, drag-and-drop copy
plus, and the open and closed hands. ``#`` is the black face, ``.`` the white
outline and a space is transparent. The grids in this module are bound to their
canonical X names by ``tools/cursor_art.py``; ``tools/make_cursors.py`` scales
and writes them.
"""

# The circle-slash draws a black ring with a black NW-SE slash through its
# centre; the hotspot is the middle of the slash.
NOT_ALLOWED_HOTSPOT = (7, 7)
NOT_ALLOWED_GRID = (
    "    ........    ",
    "   ..######..   ",
    "  ..########..  ",
    " ..##      ##.. ",
    "..###.      ##..",
    ".## .#.      ##.",
    ".##  .#.     ##.",
    ".##   .#.    ##.",
    ".##    .#.   ##.",
    ".##     .#.  ##.",
    ".##      .#. ##.",
    "..##      .###..",
    " ..##      ##.. ",
    "  ..########..  ",
    "   ..######..   ",
    "    ........    ",
)

# The copy plus draws a black vertical bar and two horizontal arms; the
# vertical bar's white outline splits the arms, and the hotspot is the centre.
DND_COPY_HOTSPOT = (7, 7)
DND_COPY_GRID = (
    "                ",
    "       .        ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "  .....#.....   ",
    " .####.#.####.  ",
    "  .....#.....   ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "       .        ",
    "                ",
    "                ",
)

# The open hand raises four 1px fingers over a black palm; the hotspot is the
# middle of the palm.
GRAB_HOTSPOT = (7, 12)
GRAB_GRID = (
    "                ",
    "   .  .  .  .   ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    "  .#..#..#..#.  ",
    " .############. ",
    " .############. ",
    " .############. ",
    " .############. ",
    " .............. ",
    "                ",
)

# The closed fist drops the raised fingers and folds a thumb across the black
# block; the hotspot is the middle of the palm.
GRABBING_HOTSPOT = (7, 12)
GRABBING_GRID = (
    "                ",
    "                ",
    "                ",
    "                ",
    " .............. ",
    " .############. ",
    " ........#####. ",
    " .#######.####. ",
    " .#######.####. ",
    " .#######.####. ",
    " ........#####. ",
    " .############. ",
    " .############. ",
    " .############. ",
    " .............. ",
    "                ",
)

