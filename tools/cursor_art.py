"""The Mac OS 8.6 Platinum cursor pixel art: grids, hotspots and aliases.

The theme ships nineteen cursors inside the ``org.macos8.desktop`` icon theme
package, under ``cursors/``: ``left_ptr`` (the arrow), ``xterm`` (the text
I-beam), ``hand2`` (the pointing hand), ``watch`` (the busy hourglass),
``fleur`` (the move cross), ``size_hor`` and ``size_ver`` (the horizontal and
vertical resize arrows), ``size_fdiag`` and ``size_bdiag`` (the NW-SE and NE-SW
resize arrows), ``crosshair`` (the precision cross), ``not-allowed`` (the
circle-slash), ``dnd-copy`` (the drag-and-drop copy plus), ``grab`` (the open
hand), ``grabbing`` (the closed fist), ``help`` (the arrow plus a question
mark, aliases ``left_ptr_help``, ``question_arrow``, ``whats_this`` and the
Breeze hash names ``5c6cd98b3f3ebcb1f9c7f1c204630408`` and
``d9ce0ab605698f320427677b458ad60b``), ``progress`` (the arrow plus a small
hourglass, aliases ``half-busy``, ``left_ptr_watch`` and the Breeze hash names
``00000000000000020006000e7e9ffc3f``, ``08e8e1c95fe2fc01f976f1e063a24ccd`` and
``3ecb610c1bf2410f44200f48c40d3599``), ``pencil`` (a diagonal pencil), ``zoom-in`` and
``zoom-out`` (magnifiers with a plus or minus), each with the X-name aliases
listed in ``CURSORS``. The help, progress and zoom names are X/KDE-required
and follow the installed Breeze cursor set; ``pencil``, ``zoom-in`` and
``zoom-out`` have no aliases there.
Each file holds the same art at nominal sizes 16, 24 and 32. No reference
screenshot in ``macos8.6-screenshots/`` shows the mouse pointer, so the art is
our own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline,
not traced from Apple's artwork; the nominal sizes, the Xcursor container and
the X names are KDE/X-required values. ``tools/make_cursors.py`` scales the
grids and writes the files.
"""

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

# The canonical cursor name, its grid, its hotspot and the X-name aliases that
# must carry byte-identical copies. ``main`` writes them in this order.
CURSORS = (
    (
        "left_ptr",
        ARROW_GRID,
        HOTSPOT,
        ("arrow", "default", "top_left_arrow", "dnd-none"),
    ),
    ("xterm", XTERM_GRID, XTERM_HOTSPOT, ("text", "ibeam")),
    ("hand2", HAND2_GRID, HAND2_HOTSPOT, ("hand1", "pointer", "pointing_hand")),
    ("watch", WATCH_GRID, WATCH_HOTSPOT, ("wait",)),
    (
        "fleur",
        FLEUR_GRID,
        FLEUR_HOTSPOT,
        ("move", "all-scroll", "size_all", "dnd-move"),
    ),
    (
        "size_hor",
        SIZE_HOR_GRID,
        SIZE_HOR_HOTSPOT,
        (
            "e-resize",
            "ew-resize",
            "w-resize",
            "h_double_arrow",
            "sb_h_double_arrow",
        ),
    ),
    (
        "size_ver",
        SIZE_VER_GRID,
        SIZE_VER_HOTSPOT,
        (
            "n-resize",
            "ns-resize",
            "s-resize",
            "sb_v_double_arrow",
            "v_double_arrow",
            "00008160000006810000408080010102",
        ),
    ),
    (
        "size_fdiag",
        SIZE_FDIAG_GRID,
        SIZE_FDIAG_HOTSPOT,
        ("nw-resize", "se-resize", "nwse-resize"),
    ),
    (
        "size_bdiag",
        SIZE_BDIAG_GRID,
        SIZE_BDIAG_HOTSPOT,
        ("ne-resize", "sw-resize", "nesw-resize"),
    ),
    ("crosshair", CROSSHAIR_GRID, CROSSHAIR_HOTSPOT, ("cross", "tcross")),
    (
        "not-allowed",
        NOT_ALLOWED_GRID,
        NOT_ALLOWED_HOTSPOT,
        (
            "circle",
            "crossed_circle",
            "03b6e0fcb3499374a867c041f52298f0",
            "forbidden",
            "no-drop",
            "dnd-no-drop",
        ),
    ),
    ("dnd-copy", DND_COPY_GRID, DND_COPY_HOTSPOT, ()),
    ("grab", GRAB_GRID, GRAB_HOTSPOT, ()),
    ("grabbing", GRABBING_GRID, GRABBING_HOTSPOT, ()),
    (
        "help",
        HELP_GRID,
        HELP_HOTSPOT,
        (
            "left_ptr_help",
            "question_arrow",
            "whats_this",
            "5c6cd98b3f3ebcb1f9c7f1c204630408",
            "d9ce0ab605698f320427677b458ad60b",
        ),
    ),
    (
        "progress",
        PROGRESS_GRID,
        PROGRESS_HOTSPOT,
        (
            "half-busy",
            "left_ptr_watch",
            "00000000000000020006000e7e9ffc3f",
            "08e8e1c95fe2fc01f976f1e063a24ccd",
            "3ecb610c1bf2410f44200f48c40d3599",
        ),
    ),
    ("pencil", PENCIL_GRID, PENCIL_HOTSPOT, ()),
    ("zoom-in", ZOOM_IN_GRID, ZOOM_IN_HOTSPOT, ()),
    ("zoom-out", ZOOM_OUT_GRID, ZOOM_OUT_HOTSPOT, ()),
)

PIXELS = {
    "#": b"\x00\x00\x00\xff",
    ".": b"\xff\xff\xff\xff",
    " ": b"\x00\x00\x00\x00",
}
