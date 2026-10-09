"""The Mac OS 8.6 Platinum palette values the desktop-theme tests share.

The per-widget test modules name the colours their artwork is painted from --
the black outline, the white bevel highlight, the grey bevel shadow and the
#DDDDDD face -- and the raised-face modules assert that fill set. Naming the
values here gives those modules one place to import the palette from instead
of redefining it. `test_colorscheme_reference` remains the test that grounds
these values in the reference screenshots.
"""

from __future__ import annotations


BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#999999"
FACE = "#DDDDDD"

# The four fills a raised Platinum face artwork uses: the black outline, the
# white bevel highlight, the grey bevel shadow and the #DDDDDD face.
PLATINUM_FILLS = frozenset({BLACK, WHITE, GREY, FACE})
