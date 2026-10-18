"""The Mac OS 8.6 Platinum palette values the desktop-theme tests share.

The per-widget test modules name the colours their artwork is painted from --
the black outline, the white bevel highlight, the grey bevel shadow, the
#DDDDDD face, the flat #EEEEEE trough, the flat #FFFFCC tooltip face and the
flat #CCCCFF selection -- and assert their fill sets. Naming the values here
gives those modules one place to import the palette from instead of
redefining it. `test_colorscheme_reference` remains the test that grounds
these values in the reference screenshots; the trough, painted from
`[Colors:View] BackgroundAlternate`, is pinned only by the widget tests that
draw it, and the tooltip face and the selection fill are KDE-required
`[Colors:Tooltip]` and `[Colors:Selection]` roles no screenshot shows,
pinned by the widget tests that draw them and by `test_colorscheme`.
"""

from __future__ import annotations

from svg_assertions import attribute_values


BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#999999"
FACE = "#DDDDDD"

# The four fills a raised Platinum face artwork uses: the black outline, the
# white bevel highlight, the grey bevel shadow and the #DDDDDD face.
PLATINUM_FILLS = frozenset({BLACK, WHITE, GREY, FACE})

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
# listitem.svg and viewitem.svg draw.
SELECTION = "#CCCCFF"


def hex_colour(rgb):
    """Return the ``#RRGGBB`` form of the sampled pixel *rgb*, as an SVG fill is written."""
    return "#%02X%02X%02X" % tuple(rgb)


def assert_fill_palette(case, tree, extra=frozenset()):
    """Assert *tree*'s parsed fill set is exactly the Platinum artwork palette.

    The widget modules read the parsed artwork's `fill` attributes through
    `attribute_values` -- not a text search of the raw file, whose comments
    name the same colours -- and pin the whole set; this states that one
    comparison once. *extra* adds a widget-specific fill such as `TROUGH`;
    *case* is the calling ``unittest.TestCase``.
    """
    case.assertEqual(attribute_values(tree, "fill"), PLATINUM_FILLS | extra)
