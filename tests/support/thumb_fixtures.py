"""Pixel maps of the Platinum thumb the slider and switch widgets draw.

`slider.svg` and `switch.svg` both paint their handle as a 1px #000000 outline
around a beveled #DDDDDD face: a 1px highlight on the top/left edges and a 1px
shadow on the bottom/right ones. The widget tests pin each handle pixel by
pixel with `svg_assertions.assert_slice_pixels`, so the map is built here once
instead of in each test module. `thumb_pixels` takes the two bevel colours --
the raised and pressed states swap them -- `raised_thumb_pixels` and
`sunken_thumb_pixels` name those two states, and `ring_pixels` is the focus
ring: the same outline with a transparent inside.
"""

from __future__ import annotations

from support.platinum_palette import BLACK, FACE, GREY, WHITE


def thumb_pixels(width, height, top_left, bottom_right):
    """Return the {(x, y): fill} map of a *width* x *height* Platinum thumb.

    The 1px #000000 outline is the outer ring; inside it a 1px bevel runs
    *top_left* on the top/left edges and *bottom_right* on the bottom/right
    ones, and the vertical bevel is painted over the horizontal so the two
    edges turn the corners the way the scroll bar thumb's corner slices do.
    Every remaining pixel is the #DDDDDD face. *top_left* and *bottom_right*
    are #FFFFFF and #999999 for the raised thumb, swapped for the pressed one.
    """
    pixels = {}
    for y in range(height):
        for x in range(width):
            if x in (0, width - 1) or y in (0, height - 1):
                colour = BLACK
            elif x == 1:
                colour = top_left
            elif x == width - 2:
                colour = bottom_right
            elif y == 1:
                colour = top_left
            elif y == height - 2:
                colour = bottom_right
            else:
                colour = FACE
            pixels[(x, y)] = colour
    return pixels


def raised_thumb_pixels(width, height):
    """Return the raised thumb: white highlight top/left, grey shadow bottom/right."""
    return thumb_pixels(width, height, WHITE, GREY)


def sunken_thumb_pixels(width, height):
    """Return the pressed thumb: grey shadow top/left, white highlight bottom/right."""
    return thumb_pixels(width, height, GREY, WHITE)


def ring_pixels(width, height):
    """Return only the 1px #000000 outer ring of a *width* x *height* thumb.

    The focus ring's inside is transparent, so the map carries no interior
    points; `render_slices` records only the painted ring rects.
    """
    return {
        (x, y): BLACK
        for y in range(height)
        for x in range(width)
        if x in (0, width - 1) or y in (0, height - 1)
    }
