"""The Setup Assistant body text field the line-edit reference tests sample.

Both the desktop theme's `lineedit.svg` reference test and the Kvantum line
edit's reference test re-derive the same field in
`macos8.6-screenshots/firstboot_betawiki.png` (retail Mac OS 8.6): a
#999999/#FFFFFF bevel outside a 1px #000000 outline over the #FFFFFF face.
One copy of the field's border runs and four 2x2 corners lives here so the
two readers pin the same pixels instead of carrying parallel tables.
"""

from __future__ import annotations

# The field's border runs, read from the outside in: the bevel's outer pixel,
# the #000000 outline and the #FFFFFF face. One run per side, away from the
# corners.
FIELD_BORDER_RUNS = (
    # left border, left to right at y=95
    ((28, 95), "#999999"),
    ((29, 95), "#000000"),
    ((30, 95), "#FFFFFF"),
    # top border, top to bottom at x=100
    ((100, 58), "#999999"),
    ((100, 59), "#000000"),
    ((100, 60), "#FFFFFF"),
    # right border at y=150: face, outline, outer highlight
    ((429, 150), "#FFFFFF"),
    ((430, 150), "#000000"),
    ((431, 150), "#FFFFFF"),
    # bottom border at x=100: outline, outer highlight
    ((100, 376), "#000000"),
    ((100, 377), "#FFFFFF"),
)

# The field's four 2x2 corners, row-major from the field's top-left pixel.
# The top-right outer pixel (431,58) is the window face #CCCCCC: the top
# shadow stops one pixel short of the outer highlight, so that corner leaves
# it unpainted, and the shipped corner tile does too. The field's true bottom
# is y=377: the bottom-left outer pixel (28,377) is the window face #CCCCCC
# (the highlight starts one pixel in at (29,377)), and the bottom-right
# outline stops one row short at (430,376), leaving (430,377) to the
# highlight.
FIELD_CORNER_PIXELS = (
    ((28, 58), "#999999"),
    ((29, 58), "#999999"),
    ((28, 59), "#999999"),
    ((29, 59), "#000000"),
    ((430, 58), "#999999"),
    ((431, 58), "#CCCCCC"),
    ((430, 59), "#000000"),
    ((431, 59), "#FFFFFF"),
    ((28, 376), "#999999"),
    ((29, 376), "#000000"),
    ((28, 377), "#CCCCCC"),
    ((29, 377), "#FFFFFF"),
    ((430, 376), "#000000"),
    ((431, 376), "#FFFFFF"),
    ((430, 377), "#FFFFFF"),
    ((431, 377), "#FFFFFF"),
)
