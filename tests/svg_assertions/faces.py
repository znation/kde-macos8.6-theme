"""Face and bevel corner geometry for the SVG test helpers.

The 3x3 corner tables and edge bands a beveled Platinum face paints: the
fixed raised-face corners, the face-parameterized sunken and flat tables, and
the dispatchers that select a table and its edge bands by bevel name.
"""

from __future__ import annotations

# The four 3x3 corner slices of the raised #DDDDDD face painted by the
# scroll-bar thumb and the toolbar, row-major in slice-local coordinates:
# the 1px #000000 outline on the two outer edges, a #FFFFFF highlight inside
# the top/left edges and a #999999 shadow inside the bottom/right ones,
# meeting over the #DDDDDD face. `face_corners` rebuilds this table with a
# different shadow (the dialog body's reference #AAAAAA). The frame's raised
# state shares the edges and three of these corners but turns its bottom-left
# corner differently (a #999999 pixel where these have #FFFFFF), so it
# overrides only that corner.
RAISED_FACE_CORNERS = {
    "topleft": (
        "#000000", "#000000", "#000000",
        "#000000", "#FFFFFF", "#FFFFFF",
        "#000000", "#FFFFFF", "#DDDDDD",
    ),
    "topright": (
        "#000000", "#000000", "#000000",
        "#FFFFFF", "#999999", "#000000",
        "#DDDDDD", "#999999", "#000000",
    ),
    "bottomleft": (
        "#000000", "#FFFFFF", "#DDDDDD",
        "#000000", "#FFFFFF", "#999999",
        "#000000", "#000000", "#000000",
    ),
    "bottomright": (
        "#DDDDDD", "#999999", "#000000",
        "#999999", "#999999", "#000000",
        "#000000", "#000000", "#000000",
    ),
}


def sunken_face_corners(face, shadow="#999999"):
    """Return the four 3x3 sunken-face corner slices painted for *face*.

    A sunken face is a 1px #000000 outline with a 1px bevel inside it -- a
    *shadow* (the default #999999) on the top/left edges and a #FFFFFF
    highlight on the bottom/right ones -- meeting over *face*. The frame's
    sunken state paints a #DDDDDD face, so the face is the parameter; the
    pressed button paints the reference's #AAAAAA shadow. The raised face
    keeps its own `RAISED_FACE_CORNERS` because the frame's raised bottom-left
    corner turns differently; the line edit's field draws its bevel outside
    the outline instead, from `sunken_outside_face_corners`.
    """
    return {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", shadow, shadow,
            "#000000", shadow, face,
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            shadow, "#FFFFFF", "#000000",
            face, "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", shadow, face,
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            face, "#FFFFFF", "#000000",
            "#FFFFFF", "#FFFFFF", "#000000",
            "#000000", "#000000", "#000000",
        ),
    }


def flat_face_corners(face):
    """Return the four 3x3 flat-face corner slices painted for *face*.

    A flat face carries no bevel, so the only non-face pixels are the 1px
    #000000 outline on the two outer edges. The frame's plain state and the
    scroll-bar trough share this geometry but paint a #DDDDDD and #EEEEEE
    face respectively, so the face is the parameter. The raised and sunken
    faces keep their own tables because their corners carry a bevel.
    """
    return {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", face, face,
            "#000000", face, face,
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            face, face, "#000000",
            face, face, "#000000",
        ),
        "bottomleft": (
            "#000000", face, face,
            "#000000", face, face,
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            face, face, "#000000",
            face, face, "#000000",
            "#000000", "#000000", "#000000",
        ),
    }


def sunken_outside_face_corners(face, shadow="#999999"):
    """Return the four 3x3 sunken-outside corner slices painted for *face*.

    A sunken-outside face is a 1px *shadow* (the default #999999)/#FFFFFF
    bevel on the outer edge, a 1px #000000 outline inside it and *face*
    innermost -- the Mac OS 8.6 text field's order, the reverse of
    `sunken_face_corners`, which puts the outline outside the bevel. The face
    pixels are (2,2) of the top-left, (0,2) of the top-right, (2,0) of the
    bottom-left and (0,0) of the bottom-right slice; the remaining #FFFFFF
    pixels are the bottom/right outer highlight, so only the face pixels
    follow *face*.

    The reference field leaves the top-right outer pixel (2,0 of the
    top-right slice) unpainted -- the bevel's top shadow stops one pixel
    short of the outer highlight -- so that entry is ``None``, which
    `assert_corner_pixels` matches against an unpainted pixel. Its true
    bottom turns the same way: the bottom-left outer pixel (0,2 of the
    bottom-left slice) is unpainted and the highlight starts one pixel in at
    (1,2); the #000000 outline stops one row short of the bottom-right outer
    edge, so its (1,2) pixel is the bottom/right highlight.
    """
    return {
        "topleft": (
            shadow, shadow, shadow,
            shadow, "#000000", "#000000",
            shadow, "#000000", face,
        ),
        "topright": (
            shadow, shadow, None,
            "#000000", "#000000", "#FFFFFF",
            face, "#000000", "#FFFFFF",
        ),
        "bottomleft": (
            shadow, "#000000", face,
            shadow, "#000000", "#000000",
            None, "#FFFFFF", "#FFFFFF",
        ),
        "bottomright": (
            face, "#000000", "#FFFFFF",
            "#000000", "#000000", "#FFFFFF",
            "#FFFFFF", "#FFFFFF", "#FFFFFF",
        ),
    }


def _require_known_bevel(bevel):
    """Raise ValueError unless *bevel* is a known bevel name.

    `face_edge_bands` and `face_corners` both dispatch on the same bevel
    names -- ``"raised"``, ``"sunken"``, ``"sunken-outside"`` and
    ``"flat"`` -- so the vocabulary, and the diagnostic naming the accepted
    values, lives here once instead of in each dispatcher.
    """
    if bevel not in ("raised", "sunken", "sunken-outside", "flat"):
        raise ValueError(
            f"unknown bevel {bevel!r}; expected 'raised', 'sunken', "
            "'sunken-outside' or 'flat'"
        )


def face_edge_bands(face, bevel, shadow="#999999"):
    """Return the (outward, mirrored) edge bands for a *bevel* on *face*.

    `assert_edge_bevels` checks a widget's four edge tiles with two
    three-colour bands: *outward* reads a top/left slice from its outer edge
    inward, and *mirrored* is the bottom/right band, whose #000000 outline
    stays on the outer edge while the bevel colour swaps sides. A raised face
    paints a #FFFFFF highlight inside the top/left outline and a *shadow*
    inside the bottom/right ones; a sunken face swaps those two bevel
    colours; a sunken-outside face puts the bevel outside the outline instead,
    a *shadow* and a #FFFFFF highlight on the outer edges and the #000000
    outline inside them; a flat face has no bevel, so both inner bands are
    *face*.
    *face* is the widget's face colour (#DDDDDD for the button, frame and
    scroll-bar thumb, #FFFFFF for the line edit, #EEEEEE for the scroll-bar
    trough), *bevel* is ``"raised"``, ``"sunken"``, ``"sunken-outside"``
    or ``"flat"``, and *shadow* is the bevel's shadow colour: the default
    #999999, or the reference's lighter #AAAAAA for the push button. Any
    other *bevel* is rejected by `_require_known_bevel`.
    """
    _require_known_bevel(bevel)
    if bevel == "raised":
        return ("#000000", "#FFFFFF", face), (face, shadow, "#000000")
    if bevel == "sunken":
        return ("#000000", shadow, face), (face, "#FFFFFF", "#000000")
    if bevel == "sunken-outside":
        return (shadow, "#000000", face), (face, "#000000", "#FFFFFF")
    if bevel == "flat":
        return ("#000000", face, face), (face, face, "#000000")


def face_corners(face, bevel, shadow="#999999"):
    """Return the four 3x3 corner slices of a *bevel* painted on *face*.

    `assert_face_bevel` checks the corners its edges lead into, and its
    self-test rebuilds a slice from the same table, so both read a bevel's
    corner geometry here: the fixed `RAISED_FACE_CORNERS` (#DDDDDD) for a
    raised face, and the *face*-derived `sunken_face_corners`,
    `sunken_outside_face_corners` and `flat_face_corners` tables otherwise.
    *face* is the widget's face colour, *bevel* is ``"raised"``,
    ``"sunken"``, ``"sunken-outside"`` or ``"flat"``, and *shadow* is the
    bevel's shadow colour (the default #999999, or the reference's #AAAAAA
    for the dialog body and pressed button). A non-default *shadow* rebuilds
    the raised table and substitutes into the sunken tables; the flat table
    has no shadow. Any other *bevel* is rejected by `_require_known_bevel`.
    """
    _require_known_bevel(bevel)
    if bevel == "raised":
        if shadow == "#999999":
            return RAISED_FACE_CORNERS
        return {
            name: tuple(
                shadow if colour == "#999999" else colour
                for colour in pixels
            )
            for name, pixels in RAISED_FACE_CORNERS.items()
        }
    if bevel == "sunken":
        return sunken_face_corners(face, shadow)
    if bevel == "sunken-outside":
        return sunken_outside_face_corners(face, shadow)
    if bevel == "flat":
        return flat_face_corners(face)
