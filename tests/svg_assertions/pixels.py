"""Pixel-comparison assertions for the SVG test helpers.

Each compares rendered slice pixels, a bevel band, a corner tile or a centre
tile against the values the artwork must paint, naming the failing slice in
its message. The layout and arc assertions live in
``svg_assertions/layout.py``.
"""

from __future__ import annotations

from .faces import face_corners, face_edge_bands
from .nine_slice import nine_slice_tile_sizes
from .render import pixel_map, render_slices
from .tree import SLICE_IDS, attribute_values


def assert_slice_pixels(case, slices, name, expected):
    """Assert slice *name* renders exactly the *expected* {(x, y): colour} map.

    *case* is the calling ``unittest.TestCase``. Comparing the full map pins
    every pixel of the slice, so a recoloured, resized or shifted body fails
    rather than just a changed set of fills. *expected* is a `pixel_map` or a
    hand-built map of the same shape.
    """
    with case.subTest(slice=name):
        case.assertEqual(slices[name], expected, name)


def assert_slices_uniform(case, slices, prefix, colour):
    """Assert every pixel of every ``<prefix>-<name>`` slice is *colour*.

    *prefix* names the widget state (``"pressed"``, ``"normal"``); pass
    ``""`` for an unprefixed SVG. Each of the nine ``SLICE_IDS`` is read from
    *slices* and every one of its pixels compared to *colour* -- ``None`` for
    a slice whose rects carry no ``fill`` attribute -- so a recoloured slice
    fails, and a missing slice fails on the lookup. *case* is the calling
    ``unittest.TestCase``.
    """
    sep = "-" if prefix else ""
    for name in SLICE_IDS:
        slice_name = f"{prefix}{sep}{name}"
        with case.subTest(slice=slice_name):
            for point, value in slices[slice_name].items():
                case.assertEqual(value, colour, f"{slice_name} {point}")


def assert_slices_have_no_fill(case, tree, *prefixes):
    """Assert each *prefix*'s slices paint nothing, and pin the placeholder opacity.

    A state that must not paint (an idle item, a merely hovered title) is
    drawn as transparent 0.01-opacity rects that carry only its margins;
    `render_slices` reads those rects as ``None``, so every pixel of every
    ``<prefix>-<name>`` slice must be ``None``. The whole tree's
    ``fill-opacity`` values must also be exactly ``{"0.01"}``, so the
    placeholder cannot become fully opaque. *case* is the calling
    ``unittest.TestCase``; *prefixes* are the widget states that must stay
    invisible.
    """
    slices = render_slices(tree)
    for prefix in prefixes:
        assert_slices_uniform(case, slices, prefix, None)
    case.assertEqual(attribute_values(tree, "fill-opacity"), {"0.01"})


def assert_slices_fill_their_tiles(case, slices, prefix_colours, border, tile):
    """Assert each ``<prefix>-<name>`` slice fills its exact tile with *colour*.

    *prefix_colours* pairs each widget state's prefix with the colour every
    one of its nine tiles paints (``None`` for a state whose rects carry no
    ``fill`` attribute). *border* and *tile* are the SVG's border thickness
    and centre-tile size, so the canvas is ``tile + 2 * border`` square and
    the tiles are the nine regions `nine_slice_tile_sizes` derives from it.
    The per-slice colour checks read each slice's pixels, so a rect one pixel
    short (or long) passes while KSvg leaves a transparent stripe in the
    stretched tile; comparing each tile to a solid `pixel_map` pins the exact
    region. *case* is the calling ``unittest.TestCase``.
    """
    sizes = nine_slice_tile_sizes(
        tile + 2 * border,
        tile + 2 * border,
        border,
        border,
        border,
        border,
    )
    for prefix, colour in prefix_colours:
        for name, (width, height) in sizes.items():
            expected = pixel_map((colour,) * (width * height), width, height)
            assert_slice_pixels(case, slices, f"{prefix}-{name}", expected)


def assert_edge_band_pixels(case, slices, name, side, band, size=6):
    """Assert edge slice *name* paints *band* from its outer edge in.

    A horizontal edge (*side* ``top``/``bottom``) is three *size*-wide rows,
    one per band colour; a vertical edge (*side* ``left``/``right``) is
    *size* rows of three, each running outer to inner. *band* is the three
    colours in the slice's own top-to-bottom (horizontal edge) or
    left-to-right (vertical edge) order, so a bottom or right edge passes the
    mirrored band; `assert_edge_bevels` supplies that mirroring for a
    widget's four edges. *size* is the slice's length along the edge: 6 for
    the button/frame/lineedit tiles, 10 for the scroll bar.
    """
    if side in ("top", "bottom"):
        expected = (band[0],) * size + (band[1],) * size + (band[2],) * size
        points = ((x, y) for y in range(3) for x in range(size))
    else:
        expected = band * size
        points = ((x, y) for y in range(size) for x in range(3))
    pixels = slices[name]
    actual = tuple(pixels.get(point) for point in points)
    with case.subTest(slice=name):
        case.assertEqual(actual, expected, name)


def assert_edge_bevels(case, slices, prefix, outward, mirrored, size=6):
    """Assert each of *prefix*'s four edge tiles paints its bevel band.

    A widget's bevel runs the same way along all four edges, so the bottom
    and right bands mirror the top and left ones: *outward* is the (outer
    outline, bevel, inner face) band read from a top/left slice's outer edge
    inward, and *mirrored* is the bottom/right band, whose outline stays on
    the outer edge while the bevel colour swaps sides. Each band is checked
    by `assert_edge_band_pixels`, so *size* is the tile's length along the
    edge (6 for the button/frame/lineedit tiles, 10 for the scroll bar).
    *prefix* names the state (``"normal"``, ``"slider"``); pass ``""`` for
    an unprefixed SVG. *case* is the calling ``unittest.TestCase``.
    """
    sep = "-" if prefix else ""
    for side in ("top", "bottom", "left", "right"):
        band = outward if side in ("top", "left") else mirrored
        assert_edge_band_pixels(
            case, slices, f"{prefix}{sep}{side}", side, band, size
        )


def assert_corner_pixels(case, slices, name, expected):
    """Assert corner slice *name* paints the 3x3 *expected* pixels.

    *expected* is the nine colours in row-major order, top-left first -- the
    shape the corner tests each otherwise rebuild by hand.
    """
    pixels = slices[name]
    actual = tuple(
        pixels.get((x, y))
        for y in range(3)
        for x in range(3)
    )
    with case.subTest(corner=name):
        case.assertEqual(actual, expected, name)


def assert_face_corners(case, slices, prefix, corners):
    """Assert every 3x3 corner slice in *corners* paints its expected pixels.

    *corners* maps a corner name (``"topleft"`` ...) to the nine colours in
    row-major order; each is looked up in *slices* as ``"<prefix>-<name>"``,
    or ``"<name>"`` when *prefix* is ``""``. `assert_face_bevel` passes its
    bevel's table here, and the frame's plain/raised/sunken and the line
    edit's ``"base"`` corner tests pass theirs. *case* is the calling
    ``unittest.TestCase``.
    """
    sep = "-" if prefix else ""
    for name, expected in corners.items():
        assert_corner_pixels(case, slices, f"{prefix}{sep}{name}", expected)


def assert_center_tile_is(case, slices, name, colour, size):
    """Assert centre slice *name* is a solid *size* x *size* rectangle of *colour*.

    The nine-slice centre tile is a single body rect, so every pixel is the
    widget's face colour. *size* pins the tile's width and height -- 6 for the
    button/frame/lineedit, 8 for the panel -- so a resized centre body rect
    fails here; comparing the full map also catches a centre tile shifted off
    its origin, which a count-and-uniformity check would not.
    """
    expected = pixel_map((colour,) * (size * size), size, size)
    assert_slice_pixels(case, slices, name, expected)


def assert_face_bevel(case, slices, prefix, face, bevel, size=6):
    """Assert *prefix*'s nine-slice paints the *bevel* on *face*.

    A face bevel is a *face*-coloured centre tile, a 1px #000000 outline on
    each edge tile's outer edge with the bevel's highlight/shadow bands
    inside it, and the four 3x3 corner slices where those bands turn the
    corner. *face* is the widget's face colour (the #DDDDDD button/frame/
    scroll-bar-thumb face, the #FFFFFF line-edit/menu face, the #EEEEEE
    scroll-bar trough), *bevel* is ``"raised"``, ``"sunken"`` or ``"flat"``,
    *prefix* names the state (``""`` for an unprefixed SVG), and *size* is the
    centre and edge tile length. The corner table comes from `face_corners`,
    so a raised face reads the fixed `RAISED_FACE_CORNERS` (#DDDDDD) and the
    sunken and flat faces their *face*-derived tables. *case* is the calling
    ``unittest.TestCase``.
    """
    sep = "-" if prefix else ""
    assert_center_tile_is(case, slices, f"{prefix}{sep}center", face, size)
    outward, mirrored = face_edge_bands(face, bevel)
    assert_edge_bevels(case, slices, prefix, outward, mirrored, size)
    assert_face_corners(case, slices, prefix, face_corners(face, bevel))

