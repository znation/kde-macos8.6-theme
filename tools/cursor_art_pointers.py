"""The pointer and magnifier cursor grids for the Platinum pointer set.

The 16x16 ASCII grids and hotspots for the arrow, text I-beam, pointing hand,
busy wristwatch, help and progress arrows, pencil, zoom magnifiers and
context-menu arrow. ``#`` is the black face, ``.`` the white outline and a
space is transparent. The grids in this module are bound to their canonical X
names and aliases by ``tools/cursor_art.py``; ``tools/make_cursors.py`` scales
and writes them. The arrow is also given as a ``VectorCursor`` (``ARROW_ART``),
which the generator rasterizes at each nominal size instead of scaling a grid.
"""

if __package__:
    from tools.cursor_vector import VectorCursor
else:  # run directly or from tools/ on sys.path
    from cursor_vector import VectorCursor

HOTSPOT = (1, 1)

# The arrow is the classic silhouette: a vertical left edge rising to the tip
# at grid (1, 1), a longer shallow trailing edge that reaches its widest point
# low in the frame, and the two-cell black tail hanging below the notch.
# ``#`` is the black face, ``.`` the white outline and a space is transparent.
# The art is drawn at 16x16 and scaled nearest-neighbour to the larger nominal
# sizes.
ARROW_GRID = (
    "..              ",
    ".#.             ",
    ".##.            ",
    ".###.           ",
    ".####.          ",
    ".#####.         ",
    ".######.        ",
    ".#######.       ",
    ".########.      ",
    ".#########.     ",
    ".##########.    ",
    ".######....     ",
    " ....##.        ",
    "    .##.        ",
    "    .##.        ",
    "    ....        ",
)

# The antialiased arrow: this theme's own original outline, drawn on a 32-unit
# design grid and rasterized natively at each nominal size by
# ``tools/cursor_vector.py``. The face runs from the tip at (3, 3) down the
# vertical left edge to (3, 24), notches in to (8, 19.5), drops to the tail
# tip at (12, 28), and returns through the inner notch to the wing at
# (18, 18.5). ``ARROW_GRID`` above stays the grid reference for the tests that
# still compare against it.
ARROW_ART = VectorCursor(
    face=(
        (3, 3),
        (3, 24),
        (8, 19.5),
        (12, 28),
        (15, 26.6),
        (11.2, 18.5),
        (18, 18.5),
    ),
    outline_width=2,
    design_size=32,
)
ARROW_HOTSPOT = (3, 3)

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

# The busy watch is a small round-faced wristwatch: a crown above a round
# ring that surrounds a white face carrying two black hands; its hotspot is
# the hands' crossing point at the face centre.
WATCH_HOTSPOT = (7, 7)
WATCH_GRID = (
    "                ",
    "      ...       ",
    "      .#.       ",
    "    .......     ",
    "    .#####.     ",
    "   .##.#.##.    ",
    "   .#..#..#.    ",
    "   .#..##.#.    ",
    "   .#.....#.    ",
    "   .##...##.    ",
    "    .#####.     ",
    "     .....      ",
    "                ",
    "                ",
    "                ",
    "                ",
)


# The help pointer is the arrow with a question mark stamped in the free
# right-hand area; its hotspot is the arrow tip.
HELP_HOTSPOT = (1, 1)
HELP_GRID = (
    "..              ",
    ".#.             ",
    ".##.     ...... ",
    ".###.    .###.  ",
    ".####.   ....#. ",
    ".#####.  ...##. ",
    ".######........ ",
    ".#######....#.. ",
    ".########...... ",
    ".#########.     ",
    ".##########.    ",
    ".######....     ",
    " ....##.        ",
    "    .##.        ",
    "    .##.        ",
    "    ....        ",
)

# The progress pointer is the arrow with a miniature of the busy watch's
# round face in the free right-hand area; its hotspot is the arrow tip.
PROGRESS_HOTSPOT = (1, 1)
PROGRESS_GRID = (
    "..              ",
    ".#.             ",
    ".##.       ...  ",
    ".###.     .###. ",
    ".####.   .#.#.#.",
    ".#####.  .#.###.",
    ".######. .#...#.",
    ".#######...###. ",
    ".########. ...  ",
    ".#########.     ",
    ".##########.    ",
    ".######....     ",
    " ....##.        ",
    "    .##.        ",
    "    .##.        ",
    "    ....        ",
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

# The zoom pointers share a white-outlined black lens ring, a transparent
# glass holding the centred black arms, and a black handle to the bottom
# right; their hotspots are the lens centre. ``zoom-in`` fills the plus and
# ``zoom-out`` keeps only its horizontal bar: each pair differs only at the
# vertical plus arm's four cells.
ZOOM_IN_HOTSPOT = (7, 7)
ZOOM_IN_GRID = (
    "                ",
    "                ",
    "     .....      ",
    "    .#####.     ",
    "   .#######.    ",
    "  .##..#..##.   ",
    "  .##..#..##.   ",
    "  .##########.  ",
    "  .##..#..##.   ",
    "  .##..#..##.   ",
    "   .#######.    ",
    "    .#####.#.   ",
    "     .......#.  ",
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
    "   .#######.    ",
    "  .##.....##.   ",
    "  .##.....##.   ",
    "  .##########.  ",
    "  .##.....##.   ",
    "  .##.....##.   ",
    "   .#######.    ",
    "    .#####.#.   ",
    "     .......#.  ",
    "            .#. ",
    "             .  ",
    "                ",
)

# The context-menu pointer is the existing arrow at exactly ``ARROW_GRID``'s
# cells plus a black-bordered menu panel beside the tail, with two black text
# bars and the shared one-cell white outline round its walls; its hotspot is
# the arrow tip.
CONTEXT_MENU_HOTSPOT = (1, 1)
CONTEXT_MENU_GRID = (
    "..              ",
    ".#.             ",
    ".##.            ",
    ".###.           ",
    ".####.          ",
    ".#####.         ",
    ".######.        ",
    ".#######.       ",
    ".########.      ",
    ".#########.     ",
    ".##########.....",
    ".######.#######.",
    " ....##.#.###.#.",
    "    .##.#.##..#.",
    "    .##.#######.",
    "    ........... ",
)

