"""Layout and arc assertions for the SVG test helpers.

Each compares a hint geometry, a nine-slice tile layout, a root canvas, a
bounds rect or a bevel half-disc's arc against the layout the artwork must
keep, naming the failing slice in its message. The pixel-comparison
assertions live in ``svg_assertions/pixels.py``.
"""

from __future__ import annotations

import math

from .elements import rect_geometry
from .nine_slice import (
    _state_margin_hints,
    nine_slice_hint_geometry,
    nine_slice_tile_sizes,
    tile_origins,
)
from .paths import arc_center, path_arcs
from .render import render_slices
from .tree import children_named, local_name


def assert_diagonal_half_disc(case, path, index, radius, center):
    """Assert *path* is the *index*-th half-disc of a raised diagonal bevel.

    The bevel's two half-discs split along the disc centre's bottom-left to
    top-right diagonal: the first runs bottom-left -> top-right and the second
    top-right -> bottom-left, both swept (sweep 1) so the first covers the
    top-left side a raised bevel paints its highlight on. A half-disc rotated
    onto the other diagonal would still centre on the disc at the same radius,
    so pin both endpoints and the sweep that picks the top-left side, not only
    the radius and centre. *case* is the calling ``unittest.TestCase``;
    *index* is the half-disc's document-order index (0 or 1); *radius* is the
    bevel radius and *center* the disc's ``(x, y)`` centre.
    """
    entries = list(path_arcs(path.get("d")))
    case.assertEqual(len(entries), 1)
    start, arc, end = entries[0]
    case.assertEqual((arc[0], arc[1]), (radius, radius))
    case.assertEqual((arc[2], arc[3]), (0, 1))
    diagonal = radius / math.sqrt(2)
    cx, cy = center
    expected_start, expected_end = (
        ((cx - diagonal, cy + diagonal), (cx + diagonal, cy - diagonal)),
        ((cx + diagonal, cy - diagonal), (cx - diagonal, cy + diagonal)),
    )[index]
    for got, want in ((start, expected_start), (end, expected_end)):
        case.assertAlmostEqual(got[0], want[0], delta=1e-3)
        case.assertAlmostEqual(got[1], want[1], delta=1e-3)
    centre = arc_center(start, arc, end)
    case.assertAlmostEqual(centre[0], center[0], places=2)
    case.assertAlmostEqual(centre[1], center[1], places=2)


def assert_arcs_share_center(case, entries, center, msg=None):
    """Assert every arc in *entries* is circular and centred on *center*.

    *entries* is a sequence of ``(start, arc, end)`` triples as `path_arcs`
    yields them. Each arc's two radii must be equal -- an elliptical arc would
    make `arc_center`'s circular reconstruction meaningless -- and its
    reconstructed centre must match *center* to two decimal places, the
    precision a rendered arc's rounded endpoints allow. *case* is the calling
    ``unittest.TestCase``; *msg* is an optional assertion message.
    """
    for start, arc, end in entries:
        case.assertEqual(arc[0], arc[1], msg)
        centre = arc_center(start, arc, end)
        case.assertAlmostEqual(centre[0], center[0], places=2, msg=msg)
        case.assertAlmostEqual(centre[1], center[1], places=2, msg=msg)


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


def assert_root_canvas(case, tree, width, height, origin_states=()):
    """Assert *tree*'s root <svg> declares a *width* x *height* canvas 1:1.

    KSvg draws the artwork in the root coordinate space, so a viewBox that
    disagrees with the canvas -- or a width/height that disagrees with the
    viewBox -- rescales the whole widget. Every other test reads only the
    artwork's own coordinates, so nothing else would notice. A nine-slice
    SVG's right/bottom margin rects must also reach the canvas edge: their far
    edge is where that border ends, so the canvas is the layout they imply.
    *origin_states* lists state prefixes (``""`` for the unprefixed state)
    that sit at the canvas origin of a canvas grown to hold a taller state:
    their margin rects need only lie inside the canvas, not reach its edge.
    """
    exempt = {f"{s}-" if s else "" for s in origin_states}
    root = tree.getroot()
    case.assertEqual(local_name(root), "svg")
    case.assertEqual(root.get("viewBox"), f"0 0 {width} {height}")
    case.assertEqual(root.get("width"), str(width))
    case.assertEqual(root.get("height"), str(height))
    for name, (x, y, w, h) in rect_geometry(tree).items():
        sep_prefix = name.rsplit("hint-", 1)[0]
        if name.endswith("hint-right-margin"):
            far, canvas = int(x) + int(w), width
        elif name.endswith("hint-bottom-margin"):
            far, canvas = int(y) + int(h), height
        else:
            continue
        if sep_prefix in exempt:
            case.assertLessEqual(far, canvas, name)
        else:
            case.assertEqual(far, canvas, name)


def assert_bounds_rect(case, group, expected):
    """Assert *group* holds exactly one rect with the *expected* bounds values.

    KSvg scales a widget element by its invisible full-canvas bounds rect, so
    that rect fixes the element's natural size and the group must hold exactly
    one: a missing rect, a second one, or a changed geometry or fill rescales
    or recolours the widget even while the contract and path tests pass.
    *case* is the calling ``unittest.TestCase``, *group* the parsed ``<g>``,
    and *expected* the five attribute strings in
    ``(x, y, width, height, fill)`` order.
    """
    rects = children_named(group, "rect")
    case.assertEqual(len(rects), 1)
    case.assertEqual(
        [rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
        expected,
    )
