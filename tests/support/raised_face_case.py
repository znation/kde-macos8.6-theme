"""Shared pixel checks for the raised Platinum face artwork.

`widgets/toolbar.svg` and `dialogs/background.svg` paint the same raised
Platinum face: a 3px margin hint around a 10px centre tile on the 16x16
canvas, a 1px #000000 outline with a 1px bevel inside it (#FFFFFF top/left,
a shadow on bottom/right), and the raised-face fill palette. This mixin states
those three checks once; each subclass sets `SVG_PATH` to its SVG, may set
`SHADOW` to the bevel's shadow colour (#999999 by default) and `CORNERS` to a
reference-specific corner table (the dialog body's mixed corners), and
inherits them. `NineSliceCase` already pins the slices' structure, and
`test_frame_bevel` here pins the painted result.
"""

from __future__ import annotations

from support.nine_slice_case import NineSliceCase
from support.platinum_palette import FACE, GREY, assert_fill_palette
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    render_slices,
)


class RaisedFaceCase(NineSliceCase):
    """Mixin: the hint, bevel and palette checks shared by raised faces.

    A subclass sets `SVG_PATH` to its widget SVG, may set `SHADOW` to the
    bevel's shadow colour (#999999 by default; the dialog body uses the
    reference's #AAAAAA) and `CORNERS` to a reference-specific corner table
    (the dialog body's mixed corners leave a face pixel). It is a plain
    mixin, not a `TestCase`, so importing it does not collect an unconfigured
    base.
    """

    SHADOW = GREY
    CORNERS = None

    def test_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin hint
        # with the wrong position or size passes it while KSvg lays the body
        # out wrong. Pin every hint: a 3px border around a 10px centre tile on
        # the 16x16 canvas.
        assert_hint_geometry(self, self.tree, [""], 3, 10)

    def test_frame_bevel(self):
        # The body is a raised #DDDDDD face: a 1px #000000 outline with a 1px
        # bevel inside it (#FFFFFF top/left, SHADOW bottom/right), the same
        # bevel direction as button.svg's normal state and scrollbar.svg's
        # thumb; `assert_face_bevel` pins the centre tile, the four edge bands
        # and the four corners.
        slices = render_slices(self.tree)
        assert_face_bevel(
            self, slices, "", FACE, "raised", size=10, shadow=self.SHADOW,
            corners=self.CORNERS,
        )

    def test_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: face, outline, bevel highlight and bevel shadow.
        assert_fill_palette(self, self.tree, shadow=self.SHADOW)
