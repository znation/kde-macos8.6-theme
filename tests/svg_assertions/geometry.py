"""Pure geometry for the SVG test helpers.

The face-corner tables and bevels, the path/arc and rect/circle readers, and
the nine-slice margin, hint and tile-size arithmetic: the values a widget test
pins, independent of how a slice is composited into pixels.
"""

from __future__ import annotations

import math
import re

from .tree import _numeric_attribute, groups_with_id, local_name

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

def _require_known_bevel(bevel):
    """Raise ValueError unless *bevel* is ``"raised"``, ``"sunken"`` or ``"flat"``.

    `face_edge_bands` and `face_corners` both dispatch on the same three
    bevel names, so the vocabulary -- and the diagnostic naming the accepted
    values -- lives here once instead of in each dispatcher.
    """
    if bevel not in ("raised", "sunken", "flat"):
        raise ValueError(
            f"unknown bevel {bevel!r}; expected 'raised', 'sunken' or 'flat'"
        )

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
    trough) and *bevel* is ``"raised"``, ``"sunken"`` or ``"flat"``; any
    other value is rejected by `_require_known_bevel`.
    """
    _require_known_bevel(bevel)
    if bevel == "raised":
        return ("#000000", "#FFFFFF", face), (face, "#999999", "#000000")
    if bevel == "sunken":
        return ("#000000", "#999999", face), (face, "#FFFFFF", "#000000")
    if bevel == "flat":
        return ("#000000", face, face), (face, face, "#000000")

def face_corners(face, bevel):
    """Return the four 3x3 corner slices of a *bevel* painted on *face*.

    `assert_face_bevel` checks the corners its edges lead into, and its
    self-test rebuilds a slice from the same table, so both read a bevel's
    corner geometry here: the fixed `RAISED_FACE_CORNERS` (#DDDDDD) for a
    raised face, and the *face*-derived `sunken_face_corners` and
    `flat_face_corners` tables otherwise. *face* is the widget's face colour
    and *bevel* is ``"raised"``, ``"sunken"`` or ``"flat"``; any other value
    is rejected by `_require_known_bevel`.
    """
    _require_known_bevel(bevel)
    if bevel == "raised":
        return RAISED_FACE_CORNERS
    if bevel == "sunken":
        return sunken_face_corners(face)
    if bevel == "flat":
        return flat_face_corners(face)

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
    return _numeric_attribute(
        element, name,
        where=f"rect {rect_id!r}",
        cast=int,
        kind="integer",
        missing="an id-bearing rect must declare x, y, width and height",
        invalid=(
            "an id-bearing rect must declare x, y, width and height "
            "as integers"
        ),
    )

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
    """Return *element*'s *name* attribute, naming the circle when invalid.

    ElementTree hands back ``None`` for an attribute the circle omits, and
    `circle_geometry` converts each value with ``float()``; a bare None would
    surface as a TypeError and a present non-number (``r="3px"``) as a bare
    ``float()`` ValueError, neither naming which circle or attribute is
    malformed. Reject both here, naming the circle, the attribute and the
    value. An anonymous circle -- the radiobutton face and checkmarks dot
    carry no id of their own -- is named generically instead.
    """
    circle_id = element.get("id")
    where = f"circle {circle_id!r}" if circle_id else "circle"
    return _numeric_attribute(
        element, name,
        where=where,
        cast=float,
        kind="numeric",
        missing="a circle must declare cx, cy and r",
        invalid="a circle must declare cx, cy and r as numbers",
    )

def circle_geometry(element):
    """Return *element*'s circle geometry as ``(cx, cy, r)`` floats.

    KSvg reads a circle hint's centre and radius to size and place the widget,
    so a circle nudged off-centre or resized lays the widget out wrong even
    while its id and fill pass the contract tests. ElementTree hands the
    attributes back as strings; convert the three numeric ones here. Raise
    ValueError, naming the circle and the attribute, when one of the three is
    absent or not a number; the callers convert these values with ``float()``,
    so an unnamed None would read as a bare TypeError and a non-number as a
    bare ``float()`` ValueError.
    """
    return tuple(
        float(_circle_dimension(element, name))
        for name in ("cx", "cy", "r")
    )

def circle_geometry_and_fill(element):
    """Return *element*'s circle geometry followed by its ``fill`` attribute.

    The radiobutton and checkmarks tests pin a circle's centre, radius and
    fill together, because a face swapped between black and white or a dot
    nudged off-centre lays the widget out wrong even while each value alone
    passes. The fill is returned exactly as ElementTree hands it back -- the
    attribute string, or None when the circle omits it -- so a caller compares
    one tuple.
    """
    return circle_geometry(element) + (element.get("fill"),)

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

def _state_margin_hints(tree, prefixes, hint_aliases=None):
    """Yield each state's margin hints as ``(state, top, bottom, left, right)``.

    A margin hint names an edge tile's canvas region. For every prefix in
    *prefixes*, the four rects name that state's edge tiles and *state* is the
    id prefix its tile ids carry (``""`` for the unprefixed state). *tree*
    supplies the rects via `rect_geometry`; *hint_aliases* maps a state that
    declares no hints of its own to the state whose hints place its tiles.
    """
    hints = rect_geometry(tree)
    aliases = hint_aliases or {}
    for prefix in prefixes:
        state = f"{prefix}-" if prefix else ""
        source = aliases.get(prefix, prefix)
        source_sep = "-" if source else ""
        yield (
            state,
            hints[f"{source}{source_sep}hint-top-margin"],
            hints[f"{source}{source_sep}hint-bottom-margin"],
            hints[f"{source}{source_sep}hint-left-margin"],
            hints[f"{source}{source_sep}hint-right-margin"],
        )
