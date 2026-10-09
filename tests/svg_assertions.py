"""SVG inspection helpers shared by the desktop theme test modules.

Test-only: parses the theme's nine-slice SVGs and reads their ids, hints,
transforms and composited pixels, so each widget's test module states only the
artwork it pins instead of re-deriving the KSvg layout rules.
"""

from __future__ import annotations

import math
import re


SLICE_IDS = [
    "center", "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
]
HINT_IDS = [
    "hint-tile-center",
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
    "hint-top-inset", "hint-bottom-inset",
    "hint-left-inset", "hint-right-inset",
]


def local_name(element):
    """Return *element*'s tag without its `{namespace}` prefix.

    Each SVG declares the default SVG namespace, so ElementTree reports a tag
    as `{http://www.w3.org/2000/svg}rect`; these tests match on the local name.
    """
    return element.tag.rsplit("}", 1)[-1]


def attribute_values(tree, name):
    """Return the set of *name* values across every element in *tree*.

    An element that omits *name* contributes nothing, so the set holds exactly
    the values present in the parsed SVG. The contract tests read the artwork's
    ids, fills and strokes through this set rather than searching the raw file,
    whose comments name those values too.
    """
    return {element.get(name) for element in tree.iter() if element.get(name)}


def assert_slice_ids_present(case, tree, prefixes):
    """Assert each state's nine-slice, margin-hint and centre ids are present.

    *prefixes* lists each state prefix in *tree* -- ``("plain", "raised",
    "sunken")`` for frame, ``["base"]`` for lineedit, ``[""]`` for an
    unprefixed SVG. Every state must carry all nine ``SLICE_IDS`` and the four
    margin hints KSvg reads to size the nine-slice; the shared
    ``hint-tile-center`` is checked once. *case* is the calling
    ``unittest.TestCase``.
    """
    ids = attribute_values(tree, "id")
    for prefix in prefixes:
        sep = "-" if prefix else ""
        for name in SLICE_IDS:
            case.assertIn(f"{prefix}{sep}{name}", ids, name)
        for side in ("top", "bottom", "left", "right"):
            case.assertIn(f"{prefix}{sep}hint-{side}-margin", ids, side)
    case.assertIn("hint-tile-center", ids)


def groups_with_id(tree):
    """Yield each id-bearing `<g>` element in *tree*.

    Every nine-slice slice and focus group is a `<g id=...>`; the hints are
    separate elements rather than groups. The group-only filter lives here
    for `render_slices` and `tile_origins`, which composite and place whole
    groups; `elements_by_id` is the general id map for callers that must
    reach a non-`<g>` element.
    """
    for element in tree.iter():
        if local_name(element) == "g" and element.get("id"):
            yield element


def elements_by_id(tree):
    """Return {id: element} for every id-bearing element in *tree*.

    Unlike `groups_with_id`, this keeps non-`<g>` elements, so a caller can
    read a `<circle>` or `<path>` by id -- radiobutton's selection dot and
    hint circle, checkmarks' glyphs. The ids in these SVGs are unique; if two
    elements shared one, the later in document order would win.
    """
    return {
        element.get("id"): element
        for element in tree.iter()
        if element.get("id")
    }


def children_named(element, tag):
    """Return *element*'s direct children whose local tag is *tag*.

    A nine-slice group holds the rects and paths that paint it, and an item's
    glyphs sit directly under its group, so the artwork a test reads is one
    level down: this returns a group's own rects, paths or circles without
    re-filtering ``local_name`` at every call site.
    """
    return [child for child in element if local_name(child) == tag]


def assert_no_script_elements(case, tree):
    """Assert *tree* holds no ``<script>`` element.

    KSvg executes a script element rather than drawing it, so a pixel check
    would not notice one; only this structural assertion catches it. *case* is
    the calling ``unittest.TestCase``; its assertion names the element.
    """
    for element in tree.iter():
        tag = local_name(element)
        case.assertFalse(tag.endswith("script"), tag)


def render_slices(tree):
    """Composite each id-bearing <g> of a nine-slice SVG into a {(x, y): fill} map.

    The frame's corner slices and the button's edge slices are both read this
    way. Coordinates are slice-local: the groups are pure translations, so a
    slice's appearance is its rects painted in document order, with a later
    rect overriding an earlier one as KSvg composites one nine-slice tile.
    """
    slices = {}
    for group in groups_with_id(tree):
        pixels = {}
        for rect in children_named(group, "rect"):
            x = int(rect.get("x", 0))
            y = int(rect.get("y", 0))
            for dx in range(int(rect.get("width"))):
                for dy in range(int(rect.get("height"))):
                    pixels[(x + dx, y + dy)] = rect.get("fill")
        slices[group.get("id")] = pixels
    return slices


def pixel_map(colours, width, height):
    """Return the {(x, y): colour} map for a row-major *colours* sequence.

    *colours* is read left to right, top to bottom, filling *height* rows of
    *width* entries; a solid rectangle passes the same colour ``width *
    height`` times. The map has the same shape as one entry of
    `render_slices`, so a caller can compare the two directly.
    """
    return {
        (index % width, index // width): colour
        for index, colour in enumerate(colours)
    }


def assert_slice_pixels(case, slices, name, expected):
    """Assert slice *name* renders exactly the *expected* {(x, y): colour} map.

    *case* is the calling ``unittest.TestCase``. Comparing the full map pins
    every pixel of the slice, so a recoloured, resized or shifted body fails
    rather than just a changed set of fills. *expected* is a `pixel_map` or a
    hand-built map of the same shape.
    """
    with case.subTest(slice=name):
        case.assertEqual(slices[name], expected, name)


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


_PATH_COMMAND = re.compile(r"([MALZ])([^MALZ]*)")
_PATH_LETTER = re.compile(r"[A-Za-z]")
_SUPPORTED_PATH_COMMANDS = frozenset("MALZ")


def _path_commands(d):
    """Yield (command, numbers) for each command letter in an SVG path *d*.

    Only the M/A/L/Z commands the widget artwork uses are interpreted. Any
    other letter -- H/V/C/Q/S/T, a lowercase relative command, or an exponent
    marker -- would otherwise fold into the preceding command's number body
    and be silently misread (or raise on a later tuple unpack), so name it and
    fail instead.
    """
    unsupported = sorted(set(_PATH_LETTER.findall(d)) - _SUPPORTED_PATH_COMMANDS)
    if unsupported:
        raise ValueError(
            f"unsupported SVG path command {', '.join(unsupported)} in {d!r}; "
            "this helper reads only M, A, L and Z"
        )
    for letter, body in _PATH_COMMAND.findall(d):
        yield letter, [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", body)]


def path_arcs(d):
    """Yield (start, (rx, ry, large_arc, sweep), end) for each arc in path *d*.

    Only the M/A/L/Z commands the button corner paths use are interpreted; an
    `A` command advances the current point to its endpoint, and `Z` closes the
    subpath and returns the current point to the subpath start, as SVG
    requires, so an arc after `Z` starts where the closed subpath began.
    """
    x = y = 0.0
    subpath_start = (0.0, 0.0)
    for command, numbers in _path_commands(d):
        if command == "M":
            x, y = numbers
            subpath_start = (x, y)
        elif command == "L":
            x, y = numbers
        elif command == "Z":
            x, y = subpath_start
        elif command == "A":
            rx, ry, _rotation, large_arc, sweep, nx, ny = numbers
            yield (x, y), (rx, ry, int(large_arc), int(sweep)), (nx, ny)
            x, y = nx, ny


def arc_center(start, arc, end):
    """Return the centre of a circular SVG arc given its endpoint form.

    *arc* is (rx, ry, large_arc, sweep) with no x-axis rotation, so the centre
    lies on the perpendicular bisector of start->end and the flags pick which
    side. A flipped sweep flag puts the centre on the opposite side, which is
    exactly the arc defect the button corner test computes against.

    Raise ValueError, naming the arc, when it has no centre to reconstruct: a
    zero-length chord (start == end) has no perpendicular bisector, and a
    radius shorter than half the chord cannot reach both endpoints. Both are
    fixture defects the arithmetic would otherwise report as a bare
    ZeroDivisionError or "math domain error".
    """
    (x1, y1), (rx, _ry, large_arc, sweep), (x2, y2) = start, arc, end
    x1p = (x1 - x2) / 2
    y1p = (y1 - y2) / 2
    denom = x1p * x1p + y1p * y1p
    if denom == 0:
        raise ValueError(
            f"arc from {start} to {end} is a zero-length chord: a circular "
            "arc cannot start and end at the same point"
        )
    if rx * rx < denom:
        raise ValueError(
            f"arc from {start} to {end} has radius {rx:g} smaller than half "
            f"its chord {math.sqrt(denom):g}"
        )
    factor = math.sqrt((rx * rx - denom) / denom)
    if large_arc == sweep:
        factor = -factor
    return (factor * y1p + (x1 + x2) / 2, -factor * x1p + (y1 + y2) / 2)


def rect_geometry(tree):
    """Return {id: (x, y, width, height)} for every id-bearing <rect>.

    KSvg reads a nine-slice hint rect's geometry to size the widget, so the
    ids the contract tests pin are not enough: a margin rect naming the wrong
    tile size or border lays the widget out wrong. The artwork rects in these
    nine-slice SVGs live inside id-bearing <g> elements, so the only
    id-bearing rects are the hints and this is each SVG's full hint geometry.
    """
    geometry = {}
    for element in tree.iter():
        if local_name(element) == "rect" and element.get("id"):
            geometry[element.get("id")] = (
                element.get("x"), element.get("y"),
                element.get("width"), element.get("height"),
            )
    return geometry


def nine_slice_margins(prefix, border, size):
    """Return the four margin-hint rects of a centred nine-slice tile.

    A nine-slice SVG whose *size*-square centre tile is inset by a *border*
    on every side declares four margin hints, each naming an edge tile's
    canvas region as ``(x, y, width, height)``. The tile is centred, so the
    canvas is ``size + 2 * border`` square and the bottom/right hints start
    at ``size + border``. *prefix* is the state prefix (``""`` for an
    unprefixed SVG). The shared ``hint-tile-center`` is not included; use
    `nine_slice_hint_geometry` when every state shares one centred tile.
    """
    sep = "-" if prefix else ""
    return {
        f"{prefix}{sep}hint-top-margin": (
            str(border), "0", str(size), str(border)
        ),
        f"{prefix}{sep}hint-bottom-margin": (
            str(border), str(size + border), str(size), str(border)
        ),
        f"{prefix}{sep}hint-left-margin": (
            "0", str(border), str(border), str(size)
        ),
        f"{prefix}{sep}hint-right-margin": (
            str(size + border), str(border), str(border), str(size)
        ),
    }


def nine_slice_hint_geometry(prefixes, border, size):
    """Return the full hint geometry of a centred nine-slice SVG.

    Every state in these SVGs shares one ``hint-tile-center`` -- the
    *size*-square centre tile at ``(border, border)`` -- so it is pinned once
    alongside each state's four margin hints from `nine_slice_margins`.
    *prefixes* lists every state prefix (pass ``[""]`` for an unprefixed
    SVG). Callers whose SVG declares extra hints (an inset band, a track
    size) merge those in themselves.
    """
    geometry = {
        "hint-tile-center": (str(border), str(border), str(size), str(size))
    }
    for prefix in prefixes:
        geometry.update(nine_slice_margins(prefix, border, size))
    return geometry


_TRANSLATE = re.compile(r"translate\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def tile_origins(tree):
    """Return {id: (x, y)} for every id-bearing <g> in *tree*.

    KSvg composites a nine-slice tile from the canvas region its group's
    `transform` names, so a group translated off its slice draws the tile from
    the wrong pixels. `render_slices` reads each group's rects slice-local and
    ignores the transform, so the pixel tests cannot see this; read the
    transform directly. A group with no transform sits at the origin.
    """
    origins = {}
    for group in groups_with_id(tree):
        transform = group.get("transform")
        if transform is None:
            origins[group.get("id")] = (0, 0)
            continue
        match = _TRANSLATE.fullmatch(transform.strip())
        if match:
            origins[group.get("id")] = (int(match.group(1)), int(match.group(2)))
        else:
            # Keep the raw text so a transform this test cannot parse fails
            # loudly instead of silently reading as the origin.
            origins[group.get("id")] = transform
    return origins


def _margin_hints(hints, prefix):
    """Return one state's margin hints as ``(sep, top, bottom, left, right)``.

    A margin hint names an edge tile's canvas region; *prefix* selects one
    state (``""`` for an unprefixed SVG), whose hint ids carry no separator.
    *hints* is the rect map from `rect_geometry`. The returned *sep* is the
    prefix separator both callers reuse when naming the tiles those hints
    place.
    """
    sep = "-" if prefix else ""
    return (
        sep,
        hints[f"{prefix}{sep}hint-top-margin"],
        hints[f"{prefix}{sep}hint-bottom-margin"],
        hints[f"{prefix}{sep}hint-left-margin"],
        hints[f"{prefix}{sep}hint-right-margin"],
    )


def assert_tiles_placed_by_margins(case, tree, prefixes):
    """Assert every nine-slice tile group sits where its margin hints place it.

    A margin hint names a border: its width/height is the border's thickness
    and its outer coordinate is where the edge tile starts. Deriving each
    tile's origin from those hints pins the artwork against the layout KSvg
    reads, so a group translated to the wrong canvas region fails even though
    `render_slices` ignores transforms. *prefixes* lists each state prefix in
    *tree* (pass ``[""]`` for an unprefixed SVG).
    """
    origins = tile_origins(tree)
    hints = rect_geometry(tree)
    expected = {}
    for prefix in prefixes:
        sep, top, bottom, left, right = _margin_hints(hints, prefix)
        border_x = int(left[0]) + int(left[2])
        border_y = int(top[1]) + int(top[3])
        expected.update({
            f"{prefix}{sep}top": (int(top[0]), int(top[1])),
            f"{prefix}{sep}bottom": (int(bottom[0]), int(bottom[1])),
            f"{prefix}{sep}left": (int(left[0]), int(left[1])),
            f"{prefix}{sep}right": (int(right[0]), int(right[1])),
            f"{prefix}{sep}center": (border_x, border_y),
            f"{prefix}{sep}topleft": (int(left[0]), int(top[1])),
            f"{prefix}{sep}topright": (int(right[0]), int(top[1])),
            f"{prefix}{sep}bottomleft": (int(left[0]), int(bottom[1])),
            f"{prefix}{sep}bottomright": (int(right[0]), int(bottom[1])),
        })
    case.assertEqual(origins, expected)


def assert_slices_stay_within_their_tiles(case, tree, prefixes):
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
    *tree* (pass ``[""]`` for an unprefixed SVG).
    """
    slices = render_slices(tree)
    hints = rect_geometry(tree)
    for prefix in prefixes:
        sep, top, bottom, left, right = _margin_hints(hints, prefix)
        left_w, right_w = int(left[2]), int(right[2])
        top_h, bottom_h = int(top[3]), int(bottom[3])
        # The right/bottom margin rects reach the canvas edge, so their far
        # edge is the canvas size (the same tie `assert_root_canvas` makes).
        canvas_w = int(right[0]) + right_w
        canvas_h = int(bottom[1]) + bottom_h
        edge_w = canvas_w - left_w - right_w
        edge_h = canvas_h - top_h - bottom_h
        # (width, height) of each tile region.
        regions = {
            "top": (edge_w, top_h),
            "bottom": (edge_w, bottom_h),
            "left": (left_w, edge_h),
            "right": (right_w, edge_h),
            "center": (edge_w, edge_h),
            "topleft": (left_w, top_h),
            "topright": (right_w, top_h),
            "bottomleft": (left_w, bottom_h),
            "bottomright": (right_w, bottom_h),
        }
        for name, (width, height) in regions.items():
            region = {
                (px, py) for py in range(height) for px in range(width)
            }
            slice_id = f"{prefix}{sep}{name}"
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
