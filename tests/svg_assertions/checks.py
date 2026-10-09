"""Pixel and layout assertions for the SVG test helpers.

The assertions a widget test calls: each compares rendered slice pixels, a
bevel band, a corner tile, a centre tile or a hint geometry against the values
the artwork must paint, naming the failing slice in its message.
"""

from __future__ import annotations

from .geometry import (
    _state_margin_hints,
    face_corners,
    face_edge_bands,
    nine_slice_hint_geometry,
    nine_slice_tile_sizes,
    rect_geometry,
    tile_origins,
)
from .render import pixel_map, render_slices
from .tree import SLICE_IDS, local_name

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

def assert_hint_geometry(case, tree, prefixes, border, size, extra=None):
    """Assert *tree*'s hint rects are a centred nine-slice's.

    `nine_slice_hint_geometry` gives the shared ``hint-tile-center`` and
    every state's four margin hints; *extra* merges in any hints beyond
    that layout (an inset band, a track size), keyed by id. The whole map
    is compared against `rect_geometry`, so a hint with a wrong position or
    size fails naming the difference. *prefixes* lists each state prefix
    (pass ``[""]`` for an unprefixed SVG).
    """
    expected = nine_slice_hint_geometry(prefixes, border, size)
    if extra:
        expected.update(extra)
    case.assertEqual(rect_geometry(tree), expected)

def assert_tiles_placed_by_margins(
    case, tree, prefixes, hint_aliases=None, extra_groups=None
):
    """Assert every nine-slice tile group sits where its margin hints place it.

    A margin hint names a border: its width/height is the border's thickness
    and its outer coordinate is where the edge tile starts. Deriving each
    tile's origin from those hints pins the artwork against the layout KSvg
    reads, so a group translated to the wrong canvas region fails even though
    `render_slices` ignores transforms. *prefixes* lists each state prefix in
    *tree* (pass ``[""]`` for an unprefixed SVG). *hint_aliases* maps a
    prefix that declares no hints of its own to the prefix whose hints place
    its tiles; pass ``None`` (the default) when every state declares its own.
    *extra_groups* maps the id of an id-bearing ``<g>`` that is not a
    nine-slice tile -- a slider handle, say -- to the origin it must sit at,
    so the exact map comparison does not fail on the widget's non-tile
    groups; pass ``None`` (the default) when every group is a tile.
    """
    origins = tile_origins(tree)
    expected = {}
    for state, top, bottom, left, right in _state_margin_hints(
        tree, prefixes, hint_aliases
    ):
        border_x = int(left[0]) + int(left[2])
        border_y = int(top[1]) + int(top[3])
        expected.update({
            f"{state}top": (int(top[0]), int(top[1])),
            f"{state}bottom": (int(bottom[0]), int(bottom[1])),
            f"{state}left": (int(left[0]), int(left[1])),
            f"{state}right": (int(right[0]), int(right[1])),
            f"{state}center": (border_x, border_y),
            f"{state}topleft": (int(left[0]), int(top[1])),
            f"{state}topright": (int(right[0]), int(top[1])),
            f"{state}bottomleft": (int(left[0]), int(bottom[1])),
            f"{state}bottomright": (int(right[0]), int(bottom[1])),
        })
    if extra_groups:
        expected.update(extra_groups)
    case.assertEqual(origins, expected)

def assert_slices_stay_within_their_tiles(case, tree, prefixes, hint_aliases=None):
    """Assert no nine-slice tile paints outside the region its hints define.

    A margin hint names a border: for a horizontal edge its height is the
    border's thickness, and for a vertical edge its width is. The edge tile
    spans the canvas between the two opposite borders, so the top tile is
    ``canvas_width - left_border - right_border`` wide and ``top_border``
    tall (and so on); the centre is the canvas inside all four borders.
    `render_slices` reports each slice in its group's local coordinates, so
    the tile region starts at the local origin and this only needs the sizes.
    `render_slices` composites every rect a slice's group holds, so a rect
    wider or taller than its tile spills into the adjacent canvas region;
    KSvg samples that region into the neighbouring tile, yet the per-slice
    pixel tests read only points inside the tile and pass. Fail on any
    painted point outside the region. *prefixes* lists each state prefix in
    *tree* (pass ``[""]`` for an unprefixed SVG). *hint_aliases* maps a
    prefix that declares no hints of its own to the prefix whose hints size
    its tiles; pass ``None`` (the default) when every state declares its own.
    """
    slices = render_slices(tree)
    for state, top, bottom, left, right in _state_margin_hints(
        tree, prefixes, hint_aliases
    ):
        left_w, right_w = int(left[2]), int(right[2])
        top_h, bottom_h = int(top[3]), int(bottom[3])
        # The right/bottom margin rects reach the canvas edge, so their far
        # edge is the canvas size (the same tie `assert_root_canvas` makes).
        canvas_w = int(right[0]) + right_w
        canvas_h = int(bottom[1]) + bottom_h
        regions = nine_slice_tile_sizes(
            canvas_w, canvas_h, left_w, right_w, top_h, bottom_h
        )
        for name, (width, height) in regions.items():
            region = {
                (px, py) for py in range(height) for px in range(width)
            }
            slice_id = f"{state}{name}"
            with case.subTest(slice=slice_id):
                case.assertEqual(
                    set(slices[slice_id]) - region, set(), slice_id
                )

def assert_root_canvas(case, tree, width, height):
    """Assert *tree*'s root <svg> declares a *width* x *height* canvas 1:1.

    KSvg draws the artwork in the root coordinate space, so a viewBox that
    disagrees with the canvas -- or a width/height that disagrees with the
    viewBox -- rescales the whole widget. Every other test reads only the
    artwork's own coordinates, so nothing else would notice. A nine-slice
    SVG's right/bottom margin rects must also reach the canvas edge: their far
    edge is where that border ends, so the canvas is the layout they imply.
    """
    root = tree.getroot()
    case.assertEqual(local_name(root), "svg")
    case.assertEqual(root.get("viewBox"), f"0 0 {width} {height}")
    case.assertEqual(root.get("width"), str(width))
    case.assertEqual(root.get("height"), str(height))
    for name, (x, y, w, h) in rect_geometry(tree).items():
        if name.endswith("hint-right-margin"):
            case.assertEqual(int(x) + int(w), width, name)
        elif name.endswith("hint-bottom-margin"):
            case.assertEqual(int(y) + int(h), height, name)
