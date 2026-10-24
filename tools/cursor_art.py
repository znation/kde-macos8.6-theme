"""The Mac OS 8.6 Platinum cursor set: X names, aliases and the shared palette.

The theme ships twenty cursors inside the ``org.macos8.desktop`` icon theme
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
``zoom-out`` (magnifiers with a plus or minus), and ``context-menu`` (the arrow
beside a small white menu panel), each with the X-name aliases listed in
``CURSORS``. The role-equivalent X names reuse the landed resize, copy and
hand glyphs (``col-resize``/``split_h`` on ``size_hor``,
``row-resize``/``split_v`` on ``size_ver``, ``cell``/``plus`` on ``dnd-copy``,
``openhand`` on ``grab`` and ``closedhand`` on ``grabbing``). The help,
progress, zoom and context-menu names are X/KDE-required and follow the
installed Breeze cursor set; ``pencil``, ``zoom-in``, ``zoom-out`` and
``context-menu`` have no aliases there.
Each file holds the same art at nominal sizes 16, 24 and 32. No reference
screenshot in ``macos8.6-screenshots/`` shows the mouse pointer, so the art is
our own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline,
not traced from Apple's artwork; the nominal sizes, the Xcursor container and
the X names are KDE/X-required values. The pixel grids and hotspots live
in ``tools/cursor_art_pointers.py``, ``tools/cursor_art_resize.py`` and
``tools/cursor_art_drag.py``; this module
binds each canonical name to its grid and hotspot and lists the aliases that
must carry byte-identical copies. ``tools/make_cursors.py`` scales the grids
and writes the files.
"""

from __future__ import annotations

if __package__:
    from tools.cursor_art_drag import (
        DND_COPY_GRID,
        DND_COPY_HOTSPOT,
        GRAB_GRID,
        GRAB_HOTSPOT,
        GRABBING_GRID,
        GRABBING_HOTSPOT,
        NOT_ALLOWED_GRID,
        NOT_ALLOWED_HOTSPOT,
    )
    from tools.cursor_art_pointers import (
        ARROW_GRID,
        CONTEXT_MENU_GRID,
        CONTEXT_MENU_HOTSPOT,
        HAND2_GRID,
        HAND2_HOTSPOT,
        HELP_GRID,
        HELP_HOTSPOT,
        HOTSPOT,
        PENCIL_GRID,
        PENCIL_HOTSPOT,
        PROGRESS_GRID,
        PROGRESS_HOTSPOT,
        WATCH_GRID,
        WATCH_HOTSPOT,
        XTERM_GRID,
        XTERM_HOTSPOT,
        ZOOM_IN_GRID,
        ZOOM_IN_HOTSPOT,
        ZOOM_OUT_GRID,
        ZOOM_OUT_HOTSPOT,
    )
    from tools.cursor_art_resize import (
        CROSSHAIR_GRID,
        CROSSHAIR_HOTSPOT,
        FLEUR_GRID,
        FLEUR_HOTSPOT,
        SIZE_BDIAG_GRID,
        SIZE_BDIAG_HOTSPOT,
        SIZE_FDIAG_GRID,
        SIZE_FDIAG_HOTSPOT,
        SIZE_HOR_GRID,
        SIZE_HOR_HOTSPOT,
        SIZE_VER_GRID,
        SIZE_VER_HOTSPOT,
    )
else:  # imported from a directly run tool
    from cursor_art_drag import (
        DND_COPY_GRID,
        DND_COPY_HOTSPOT,
        GRAB_GRID,
        GRAB_HOTSPOT,
        GRABBING_GRID,
        GRABBING_HOTSPOT,
        NOT_ALLOWED_GRID,
        NOT_ALLOWED_HOTSPOT,
    )
    from cursor_art_pointers import (
        ARROW_GRID,
        CONTEXT_MENU_GRID,
        CONTEXT_MENU_HOTSPOT,
        HAND2_GRID,
        HAND2_HOTSPOT,
        HELP_GRID,
        HELP_HOTSPOT,
        HOTSPOT,
        PENCIL_GRID,
        PENCIL_HOTSPOT,
        PROGRESS_GRID,
        PROGRESS_HOTSPOT,
        WATCH_GRID,
        WATCH_HOTSPOT,
        XTERM_GRID,
        XTERM_HOTSPOT,
        ZOOM_IN_GRID,
        ZOOM_IN_HOTSPOT,
        ZOOM_OUT_GRID,
        ZOOM_OUT_HOTSPOT,
    )
    from cursor_art_resize import (
        CROSSHAIR_GRID,
        CROSSHAIR_HOTSPOT,
        FLEUR_GRID,
        FLEUR_HOTSPOT,
        SIZE_BDIAG_GRID,
        SIZE_BDIAG_HOTSPOT,
        SIZE_FDIAG_GRID,
        SIZE_FDIAG_HOTSPOT,
        SIZE_HOR_GRID,
        SIZE_HOR_HOTSPOT,
        SIZE_VER_GRID,
        SIZE_VER_HOTSPOT,
    )

GRID_SIZE = 16

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
            "col-resize",
            "split_h",
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
            "row-resize",
            "split_v",
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
    ("dnd-copy", DND_COPY_GRID, DND_COPY_HOTSPOT, ("cell", "plus")),
    ("grab", GRAB_GRID, GRAB_HOTSPOT, ("openhand",)),
    ("grabbing", GRABBING_GRID, GRABBING_HOTSPOT, ("closedhand",)),
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
    ("context-menu", CONTEXT_MENU_GRID, CONTEXT_MENU_HOTSPOT, ()),
)

PIXELS = {
    "#": b"\x00\x00\x00\xff",
    ".": b"\xff\xff\xff\xff",
    " ": b"\x00\x00\x00\x00",
}
