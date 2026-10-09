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


def _slice_where(rect):
    """Name *rect* for an error, by id when it has one."""
    rect_id = rect.get("id")
    return f"rect {rect_id!r}" if rect_id else "rect"


def _slice_offset(rect, name):
    """Return *rect*'s integer *name* offset, defaulting to 0 when absent.

    An SVG rect's x and y default to 0, so an omitted offset is valid. A
    present but non-integer one is malformed and would otherwise surface as a
    bare ``int()`` ValueError naming no rect.
    """
    value = rect.get(name)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{_slice_where(rect)} has a non-integer {name!r} of {value!r}: "
            "a nine-slice tile rect's x and y must be integers"
        ) from None


def _slice_extent(rect, name):
    """Return *rect*'s positive integer *name* extent, naming it when invalid.

    ``render_slices`` iterates ``range(extent)``, so a zero or negative width
    or height silently paints no pixels and weakens every pixel assertion built
    on it, and an absent one would surface as a bare ``int(None)`` TypeError.
    """
    value = rect.get(name)
    if value is None:
        raise ValueError(
            f"{_slice_where(rect)} has no {name!r} attribute: a nine-slice "
            "tile rect must declare a positive width and height"
        )
    try:
        extent = int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{_slice_where(rect)} has a non-integer {name!r} of {value!r}: "
            "a nine-slice tile rect must declare a positive width and height"
        ) from None
    if extent <= 0:
        raise ValueError(
            f"{_slice_where(rect)} has a non-positive {name!r} of {value!r}: "
            "a nine-slice tile rect must declare a positive width and height"
        )
    return extent


def render_slices(tree):
    """Composite each id-bearing <g> of a nine-slice SVG into a {(x, y): fill} map.

    The frame's corner slices and the button's edge slices are both read this
    way. Coordinates are slice-local: the groups are pure translations, so a
    slice's appearance is its rects painted in document order, with a later
    rect overriding an earlier one as KSvg composites one nine-slice tile.
    Raise ValueError, naming the rect, when one of its width/height attributes
    is absent, non-integer or non-positive, or its x/y is non-integer; a
    silently empty or mis-sampled tile would otherwise pass the pixel checks.
    """
    slices = {}
    for group in groups_with_id(tree):
        pixels = {}
        for rect in children_named(group, "rect"):
            x = _slice_offset(rect, "x")
            y = _slice_offset(rect, "y")
            for dx in range(_slice_extent(rect, "width")):
                for dy in range(_slice_extent(rect, "height")):
                    pixels[(x + dx, y + dy)] = rect.get("fill")
        slices[group.get("id")] = pixels
    return slices


def pixel_map(colours, width, height):
    """Return the {(x, y): colour} map for a row-major *colours* sequence.

    *colours* is read left to right, top to bottom, filling *height* rows of
    *width* entries; a solid rectangle passes the same colour ``width *
    height`` times. The map has the same shape as one entry of
    `render_slices`, so a caller can compare the two directly.

    Raise ValueError when *width* or *height* is not a positive integer, or
    when *colours* does not hold exactly ``width * height`` entries. Without
    the count check *height* is inert -- the comprehension lays out rows from
    *width* alone -- so a caller passing the wrong height would get a
    differently shaped map instead of an error naming the mismatch, and a
    zero width would surface as a bare ``ZeroDivisionError``.
    """
    for name, value in (("width", width), ("height", height)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(
                f"pixel_map {name} must be an integer: {name}={value!r}"
            )
        if value <= 0:
            raise ValueError(
                f"pixel_map {name} must be positive: {name}={value!r}"
            )
    expected = width * height
    if len(colours) != expected:
        raise ValueError(
            f"pixel_map got {len(colours)} colours; a {width}x{height} map "
            f"needs {expected} (width*height)"
        )
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


# The four 3x3 corner slices of the raised #DDDDDD face painted by the
# scroll-bar thumb and the dialog body, row-major in slice-local coordinates:
# the 1px #000000 outline on the two outer edges, a #FFFFFF highlight inside
# the top/left edges and a #999999 shadow inside the bottom/right ones,
# meeting over the #DDDDDD face. The frame's raised state shares the edges and
# three of these corners but turns its bottom-left corner differently (a
# #999999 pixel where these have #FFFFFF), so it overrides only that corner.
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


def sunken_face_corners(face):
    """Return the four 3x3 sunken-face corner slices painted for *face*.

    A sunken face is a 1px #000000 outline with a 1px bevel inside it -- a
    #999999 shadow on the top/left edges and a #FFFFFF highlight on the
    bottom/right ones -- meeting over *face*. The frame's sunken state and the
    line edit's field share this geometry but paint a #DDDDDD and #FFFFFF face
    respectively, so the face is the parameter. The raised face keeps its own
    `RAISED_FACE_CORNERS` because the frame's raised bottom-left corner turns
    differently.
    """
    return {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#999999", "#999999",
            "#000000", "#999999", face,
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#999999", "#FFFFFF", "#000000",
            face, "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", "#999999", face,
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


def face_edge_bands(face, bevel):
    """Return the (outward, mirrored) edge bands for a *bevel* on *face*.

    `assert_edge_bevels` checks a widget's four edge tiles with two
    three-colour bands: *outward* reads a top/left slice from its outer edge
    inward, and *mirrored* is the bottom/right band, whose #000000 outline
    stays on the outer edge while the bevel colour swaps sides. A raised face
    paints a #FFFFFF highlight inside the top/left outline and a #999999
    shadow inside the bottom/right ones; a sunken face swaps those two bevel
    colours; a flat face has no bevel, so both inner bands are *face*.
    *face* is the widget's face colour (#DDDDDD for the button, frame and
    scroll-bar thumb, #FFFFFF for the line edit, #EEEEEE for the scroll-bar
    trough) and *bevel* is ``"raised"``, ``"sunken"`` or ``"flat"``.
    """
    if bevel == "raised":
        return ("#000000", "#FFFFFF", face), (face, "#999999", "#000000")
    if bevel == "sunken":
        return ("#000000", "#999999", face), (face, "#FFFFFF", "#000000")
    if bevel == "flat":
        return ("#000000", face, face), (face, face, "#000000")
    raise ValueError(
        f"unknown bevel {bevel!r}; expected 'raised', 'sunken' or 'flat'"
    )


def assert_raised_face_bevel(case, slices, prefix, size=6):
    """Assert *prefix*'s nine-slice paints the raised #DDDDDD face bevel.

    This is the bevel shared by the scroll-bar thumb and the dialog body: a
    #DDDDDD centre tile, a 1px #000000 outline with a #FFFFFF highlight inside
    the top/left edges and a #999999 shadow inside the bottom/right ones, and
    the four `RAISED_FACE_CORNERS` slices where those bands turn the corner.
    *prefix* names the state, ``""`` for an unprefixed SVG, and *size* is the
    centre and edge tile length (10 for both the scroll bar and the dialog).
    *case* is the calling ``unittest.TestCase``.
    """
    sep = "-" if prefix else ""
    assert_center_tile_is(
        case, slices, f"{prefix}{sep}center", "#DDDDDD", size
    )
    outward, mirrored = face_edge_bands("#DDDDDD", "raised")
    assert_edge_bevels(case, slices, prefix, outward, mirrored, size)
    for name, expected in RAISED_FACE_CORNERS.items():
        assert_corner_pixels(case, slices, f"{prefix}{sep}{name}", expected)


_PATH_COMMAND = re.compile(r"([MALZ])([^MALZ]*)")
_PATH_LETTER = re.compile(r"[A-Za-z]")
_SUPPORTED_PATH_COMMANDS = frozenset("MALZ")
_PATH_COMMAND_ARITY = {"M": 2, "L": 2, "A": 7, "Z": 0}


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

    Raise ValueError, naming the command and the path, when a command's body
    does not carry the number of coordinates that command takes: a fixture
    defect would otherwise surface as a bare tuple-unpack error naming neither.
    """
    x = y = 0.0
    subpath_start = (0.0, 0.0)
    for command, numbers in _path_commands(d):
        expected = _PATH_COMMAND_ARITY[command]
        if len(numbers) != expected:
            raise ValueError(
                f"SVG path command {command} takes {expected} numbers but got "
                f"{len(numbers)} in {d!r}"
            )
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


def _rect_dimension(element, rect_id, name):
    """Return *element*'s integer *name* attribute, naming the rect when invalid.

    ElementTree hands back ``None`` for an attribute the rect omits, and the
    geometry helpers convert each value with ``int()``; a bare None would
    surface as a TypeError and a present non-integer (``x="4px"``) as a bare
    ``int()`` ValueError, neither naming which rect or attribute is malformed.
    Reject both here, naming the rect, the attribute and the value.
    """
    value = element.get(name)
    if value is None:
        raise ValueError(
            f"rect {rect_id!r} has no {name!r} attribute: an id-bearing rect "
            "must declare x, y, width and height"
        )
    try:
        int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"rect {rect_id!r} has a non-integer {name!r} of {value!r}: an "
            "id-bearing rect must declare x, y, width and height as integers"
        ) from None
    return value


def rect_geometry(tree):
    """Return {id: (x, y, width, height)} for every id-bearing <rect>.

    KSvg reads a nine-slice hint rect's geometry to size the widget, so the
    ids the contract tests pin are not enough: a margin rect naming the wrong
    tile size or border lays the widget out wrong. The artwork rects in these
    nine-slice SVGs live inside id-bearing <g> elements, so the only
    id-bearing rects are the hints and this is each SVG's full hint geometry.

    Raise ValueError, naming the rect and the attribute, when an id-bearing
    rect omits one of the four or declares a non-integer value; the layout
    guards convert these values with ``int()``, so an unnamed None would read
    as a bare TypeError and a non-integer one as a bare ``int()`` ValueError.
    """
    geometry = {}
    for element in tree.iter():
        if local_name(element) == "rect" and element.get("id"):
            rect_id = element.get("id")
            geometry[rect_id] = tuple(
                _rect_dimension(element, rect_id, name)
                for name in ("x", "y", "width", "height")
            )
    return geometry


def _circle_dimension(element, name):
    """Return *element*'s *name* attribute, naming the circle when absent.

    ElementTree hands back ``None`` for an attribute the circle omits, and
    `circle_geometry` converts each value with ``float()``; a bare None would
    surface as a TypeError that never says which circle or attribute is
    malformed. An anonymous circle -- the radiobutton face and checkmarks dot
    carry no id of their own -- is named generically instead.
    """
    value = element.get(name)
    if value is None:
        circle_id = element.get("id")
        where = f"circle {circle_id!r}" if circle_id else "circle"
        raise ValueError(
            f"{where} has no {name!r} attribute: a circle must declare "
            "cx, cy and r"
        )
    return value


def circle_geometry(element):
    """Return *element*'s circle geometry as ``(cx, cy, r)`` floats.

    KSvg reads a circle hint's centre and radius to size and place the widget,
    so a circle nudged off-centre or resized lays the widget out wrong even
    while its id and fill pass the contract tests. ElementTree hands the
    attributes back as strings; convert the three numeric ones here. Raise
    ValueError, naming the circle and the missing attribute, when one of the
    three is absent; the callers convert these values with ``float()``, so an
    unnamed None would read as a bare TypeError.
    """
    return tuple(
        float(_circle_dimension(element, name))
        for name in ("cx", "cy", "r")
    )


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


def nine_slice_tile_sizes(canvas_w, canvas_h, left, right, top, bottom):
    """Return the ``(width, height)`` of each of a nine-slice's nine tiles.

    *left*, *right*, *top* and *bottom* are the four border thicknesses and
    the canvas is *canvas_w* x *canvas_h*. Each corner tile is border x
    border; each edge tile spans the canvas between its two opposite borders
    and is one border thick; the centre is the canvas inside all four
    borders. Keys are the tile names (``top``, ``topleft``, ...) that the
    margin-hint ids and the slice group ids share.
    """
    edge_w = canvas_w - left - right
    edge_h = canvas_h - top - bottom
    return {
        "top": (edge_w, top),
        "bottom": (edge_w, bottom),
        "left": (left, edge_h),
        "right": (right, edge_h),
        "center": (edge_w, edge_h),
        "topleft": (left, top),
        "topright": (right, top),
        "bottomleft": (left, bottom),
        "bottomright": (right, bottom),
    }


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
        regions = nine_slice_tile_sizes(
            canvas_w, canvas_h, left_w, right_w, top_h, bottom_h
        )
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
