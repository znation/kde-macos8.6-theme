"""The Mac OS 8.6 Platinum palette values the theme's test suites share.

The desktop theme's per-widget test modules name the colours their artwork is
painted from --
the black outline, the white bevel highlight, the grey bevel shadow, the
#DDDDDD face, the flat #EEEEEE trough, the flat #FFFFCC tooltip face and the
flat #CCCCFF selection -- and assert their fill sets. Naming the values here
gives those modules one place to import the palette from instead of
redefining it. `test_colorscheme_reference` remains the test that grounds
these values in the reference screenshots; the trough, painted from
`[Colors:View] BackgroundAlternate`, is grounded by
`test_colorscheme_reference.TestReferenceAnchors.test_view_background_alternate`
in `setup_emaculation.png` and tied to the artwork by
`test_desktoptheme_scrollbar.TestScrollbarReference`; the selection fill is
grounded by
`test_colorscheme_reference.TestReferenceAnchors.test_selection_background`
in the Setup Assistant's Introduction banner (`firstboot_betawiki.png`) and
tied to the artwork by the widget tests that draw it; only the tooltip face
is a KDE-required `[Colors:Tooltip]` role no screenshot shows, pinned by the
widget tests that draw it and by `test_colorscheme`.
"""

from __future__ import annotations

from svg_assertions import attribute_values


BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#999999"
FACE = "#DDDDDD"

# The etched separator's dark half from widgets/line.svg (its light half is
# the existing WHITE); userChrome.css's menu separators and the Firefox
# preferences sidebar's separators paint the pair.
ETCH_DARK = "#888888"

# The inactive frame's 1px outline, sampled from the unfocused windows' outer
# frame edge in `desktop_fandom.png` (x=25 and y=57) by
# `tests/test_aurorae_frame.py`; both GTK sheets reuse it for a backdrop
# headerbar's border.
INACTIVE_OUTLINE = "#555555"

# The four fills a raised Platinum face artwork uses: the black outline, the
# white bevel highlight, the grey bevel shadow and the #DDDDDD face.
PLATINUM_FILLS = frozenset({BLACK, WHITE, GREY, FACE})

# The raised push button's bevel shadow, sampled from the Get Info window's two
# popup buttons in `aboutsystem_betawiki.png`: (150,121) and (150,291). It is
# lighter than the #999999 shadow the frame and other raised faces paint, so
# the button test swaps it in for `GREY`.
BUTTON_SHADOW = "#AAAAAA"

# The window box's 1px inner outline and the diagonal face's mid gradient
# band, run rects of the Aurorae close/shade/maximize widgets' active-center
# groups (sampled by tests/test_aurorae_buttons.py from
# aboutsystem_betawiki.png and systemprofiler_betawiki.png) that the Kvantum
# SVG's `mdi` window-button groups copy. The outline is darker and the band
# mid-way between the #999999 and #AAAAAA bevel greys, so both are named
# extras rather than part of PLATINUM_FILLS.
BOX_INNER_OUTLINE = "#222222"
BOX_FACE_MID = "#BBBBBB"

# The size grip's dark checker fill, sampled from the grow box in the retail
# System Profiler window (`systemprofiler_betawiki.png`, x=796..807,
# y=748..758); its white squares are WHITE and its three lower-left edge
# pixels are BUTTON_SHADOW.
SIZEGRIP_DARK = "#777777"

# The flat trough the scroll bar and slider tracks share, painted from
# `[Colors:View] BackgroundAlternate`. It is not part of the raised-face fill
# set above, so a widget test that draws it passes it as `extra`.
TROUGH = "#EEEEEE"

# The tooltip face: `[Colors:Tooltip] BackgroundNormal`, a KDE-required role
# taken from the classic Platinum palette. No reference screenshot shows a
# tooltip, so it is not screenshot-sampled.
TOOLTIP_FACE = "#FFFFCC"

# The flat selection fill the menu and item-view artwork paints from
# `[Colors:Selection] BackgroundNormal`, the same #CCCCFF the desktop theme's
# listitem.svg and viewitem.svg draw and the Setup Assistant's Introduction
# banner shows (firstboot_betawiki.png).
SELECTION = "#CCCCFF"


def hex_colour(rgb):
    """Return the ``#RRGGBB`` form of the sampled pixel *rgb*, as an SVG fill is written."""
    return "#%02X%02X%02X" % tuple(rgb)


def assert_fill_palette(case, tree, extra=frozenset(), shadow=GREY):
    """Assert *tree*'s parsed fill set is exactly the Platinum artwork palette.

    The widget modules read the parsed artwork's `fill` attributes through
    `attribute_values` -- not a text search of the raw file, whose comments
    name the same colours -- and pin the whole set; this states that one
    comparison once. *extra* adds a widget-specific fill such as `TROUGH`;
    *shadow* replaces `GREY` in the expected set for artwork whose bevel
    shadow is the reference's lighter `BUTTON_SHADOW`; *case* is the calling
    ``unittest.TestCase``.
    """
    palette = PLATINUM_FILLS
    if shadow != GREY:
        palette = (palette - {GREY}) | {shadow}
    case.assertEqual(attribute_values(tree, "fill"), palette | extra)
