"""The pointer and magnifier cursor grids for the Platinum pointer set.

The 16x16 ASCII grids and hotspots for the arrow, text I-beam, pointing hand,
busy hourglass, help and progress arrows, pencil, zoom magnifiers and
context-menu arrow. ``#`` is the black face, ``.`` the white outline and a
space is transparent. The grids in this module are bound to their canonical X
names and aliases by ``tools/cursor_art.py``; ``tools/make_cursors.py`` scales
and writes them.
"""

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

# The text I-beam has serifs at the top and bottom of a centred stem; its
# hotspot is the middle of the stem.
XTERM_HOTSPOT = (7, 7)
XTERM_GRID = (
    "   ..........   ",
    "   .########.   ",
    "   ....#.....   ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "   ....#.....   ",
    "   .########.   ",
    "   ..........   ",
)

# The pointing hand raises its index finger and holds the thumb to the right;
# its hotspot is the fingertip.
HAND2_HOTSPOT = (7, 2)
HAND2_GRID = (
    "                ",
    "      ...       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#.       ",
    "      .#....    ",
    "      .####.    ",
    "      .####.    ",
    "     .#####.    ",
    "     .#####.    ",
    "     .#####.    ",
    "     .......    ",
    "                ",
    "                ",
    "                ",
)

# The busy hourglass joins a wide top and bottom through a narrow waist; its
# hotspot is the waist.
WATCH_HOTSPOT = (7, 5)
WATCH_GRID = (
    "    ........    ",
    "    .######.    ",
    "    .######.    ",
    "     .####.     ",
    "      .##.      ",
    "      .##.      ",
    "      .##.      ",
    "     .####.     ",
    "    .######.    ",
    "    .######.    ",
    "    ........    ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
)


# The help pointer is the arrow with a question mark stamped in the free
# right-hand area; its hotspot is the arrow tip.
HELP_HOTSPOT = (1, 1)
HELP_GRID = (
    "...             ",
    ".#..            ",
    ".##..    ...... ",
    ".###..   .####. ",
    ".####..  ....#. ",
    ".#####.. ...##. ",
    ".######........ ",
    ".#######....#.. ",
    ".########...... ",
    "....##....      ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   .##.         ",
    "   ....         ",
)

# The progress pointer is the arrow with a small hourglass in the free
# right-hand area; its hotspot is the arrow tip.
PROGRESS_HOTSPOT = (1, 1)
PROGRESS_GRID = (
    "...             ",
    ".#..            ",
    ".##..           ",
    ".###..          ",
    ".####..         ",
    ".#####..        ",
    ".######..       ",
    ".#######..      ",
    ".########...... ",
    "....##....####. ",
    "   .##.  ..##.. ",
    "   .##.  ..##.. ",
    "   .##.  ..##.. ",
    "   .##.  .####. ",
    "   .##.  ...... ",
    "   ....         ",
)

# The pencil draws a two-pixel black shaft on the anti-diagonal band x+y =
# 15/16 from the writing tip (2, 14) to the eraser (13, 2), bounded by one
# white cell on every side; its hotspot is the writing tip.
PENCIL_HOTSPOT = (2, 14)
PENCIL_GRID = (
    "                ",
    "             .  ",
    "            .#. ",
    "           .##. ",
    "          .##.  ",
    "         .##.   ",
    "        .##.    ",
    "       .##.     ",
    "      .##.      ",
    "     .##.       ",
    "    .##.        ",
    "   .##.         ",
    "  .##.          ",
    " .##.           ",
    " .#.            ",
    "  .             ",
)

# The zoom pointers share a white-outlined black lens ring and a black
# handle; their hotspots are the lens centre. ``zoom-in`` fills the plus and
# ``zoom-out`` keeps only its horizontal bar.
ZOOM_IN_HOTSPOT = (7, 7)
ZOOM_IN_GRID = (
    "                ",
    "                ",
    "     .....      ",
    "    .#####.     ",
    "   .##...##.    ",
    "  .##. # .##.   ",
    "  .#.  #  .#.   ",
    "  .#.#####.#.   ",
    "  .#.  #  .#.   ",
    "  .##. # .##.   ",
    "   .##...##.    ",
    "    .#####.#.   ",
    "     ..... .#.  ",
    "            .#. ",
    "             .  ",
    "                ",
)

ZOOM_OUT_HOTSPOT = (7, 7)
ZOOM_OUT_GRID = (
    "                ",
    "                ",
    "     .....      ",
    "    .#####.     ",
    "   .##...##.    ",
    "  .##.   .##.   ",
    "  .#.     .#.   ",
    "  .#.#####.#.   ",
    "  .#.     .#.   ",
    "  .##.   .##.   ",
    "   .##...##.    ",
    "    .#####.#.   ",
    "     ..... .#.  ",
    "            .#. ",
    "             .  ",
    "                ",
)

# The context-menu pointer adds a white-faced, black-bordered menu panel to
# the arrow's right, with two black text bars; its hotspot is the arrow tip.
CONTEXT_MENU_HOTSPOT = (1, 1)
CONTEXT_MENU_GRID = (
    "...             ",
    ".#..            ",
    ".##..           ",
    ".###..          ",
    ".####..         ",
    ".#####..        ",
    ".######..       ",
    ".#######..      ",
    ".########.      ",
    "....##..#######.",
    "   .##..#.....#.",
    "   .##..#.###.#.",
    "   .##..#.....#.",
    "   .##..#.##..#.",
    "   .##..#######.",
    "   ....         ",
)

