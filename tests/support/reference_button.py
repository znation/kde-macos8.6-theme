"""The Get Info window's popup buttons, the shared ground for button bevels.

Both the desktop theme's push button and Kvantum's ``button`` are raised
Platinum bars, and the only lossless raised-button bevel in the reference set
is the pair of popup buttons in `aboutsystem_betawiki.png` (a beta build): a
1px #000000 outline, a 1px #FFFFFF top/left highlight, a #DDDDDD face and a
1px #AAAAAA bottom/right shadow. The two button-reference tests sample the
same pixels, so the button's position, its per-colour anchors and the
re-derived colours live here instead of in each module.
"""

from __future__ import annotations

from support.platinum_palette import BUTTON_SHADOW, hex_colour

# The Get Info window's "表示" popup button: a raised bar at x=80..249,
# y=103..122. The "ラベル" popup button repeats it at y=275..292.
BUTTON_X = 150
BUTTON_Y = 103

# One pixel of the reference button per colour, button-relative: the top
# outline, the top highlight, the face and the bottom shadow.
_BUTTON_ANCHORS = {
    "outline": (0, 0),
    "highlight": (0, 1),
    "face": (0, 5),
    "shadow": (0, 18),
}


def reference_button_colours(pixel):
    """Return the popup button's four colours, sampled at their anchors.

    *pixel* is the calling test's ``self.pixel``; each colour is one
    button-relative anchor offset from ``(BUTTON_X, BUTTON_Y)``.
    """
    return {
        name: hex_colour(pixel(BUTTON_X + dx, BUTTON_Y + dy))
        for name, (dx, dy) in _BUTTON_ANCHORS.items()
    }


def assert_reference_button_is_raised(case, pixel):
    """Assert the reference popup button is a raised Platinum bar.

    Anchors derive the four colours from one pixel each; the values are then
    pinned: the shadow is the #AAAAAA that distinguishes the button from the
    other raised faces' #999999. The second popup button repeats the shadow at
    y=291, the first closes its outline at y=122, and the left bevel repeats
    the outline and the highlight.
    """
    colours = reference_button_colours(pixel)
    case.assertEqual(colours["outline"], "#000000")
    case.assertEqual(colours["highlight"], "#FFFFFF")
    case.assertEqual(colours["face"], "#DDDDDD")
    case.assertEqual(colours["shadow"], BUTTON_SHADOW)
    case.assertEqual(hex_colour(pixel(BUTTON_X, 291)), BUTTON_SHADOW)
    case.assertEqual(hex_colour(pixel(BUTTON_X, 122)), "#000000")
    case.assertEqual(hex_colour(pixel(80, 108)), "#000000")
    case.assertEqual(hex_colour(pixel(81, 108)), "#FFFFFF")
