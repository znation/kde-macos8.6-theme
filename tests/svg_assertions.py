"""SVG inspection helpers shared by the desktop theme test modules.

Test-only: parses the theme's nine-slice SVGs and reads their ids, hints,
transforms and composited pixels, so each widget's test module states only the
artwork it pins instead of re-deriving the KSvg layout rules.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET


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


def groups_with_id(tree):
    """Yield each id-bearing `<g>` element in *tree*.

    Every nine-slice slice, hint and focus group is a `<g id=...>`; the
    contract tests read those groups by id, so the tag-and-id filter lives
    here rather than in each caller.
    """
    for element in tree.iter():
        if local_name(element) == "g" and element.get("id"):
            yield element


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
        for rect in group:
            if local_name(rect) != "rect":
                continue
            x = int(rect.get("x", 0))
            y = int(rect.get("y", 0))
            for dx in range(int(rect.get("width"))):
                for dy in range(int(rect.get("height"))):
                    pixels[(x + dx, y + dy)] = rect.get("fill")
        slices[group.get("id")] = pixels
    return slices


def assert_edge_band_pixels(case, slices, name, side, band):
    """Assert edge slice *name* paints *band* from its outer edge in.

    A horizontal edge (*side* ``top``/``bottom``) is three 6px rows, one per
    band colour; a vertical edge (*side* ``left``/``right``) is six 3px rows,
    each running outer to inner. *band* is the three colours read from the
    slice's outer edge in, so the expected sequence depends on the edge's
    orientation -- the part the button, lineedit and frame edge tests each
    otherwise recompute.
    """
    if side in ("top", "bottom"):
        expected = (band[0],) * 6 + (band[1],) * 6 + (band[2],) * 6
        points = ((x, y) for y in range(3) for x in range(6))
    else:
        expected = band * 6
        points = ((x, y) for y in range(6) for x in range(3))
    pixels = slices[name]
    actual = tuple(pixels.get(point) for point in points)
    with case.subTest(slice=name):
        case.assertEqual(actual, expected, name)


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


_PATH_COMMAND = re.compile(r"([MALZ])([^MALZ]*)")


def _path_commands(d):
    """Yield (command, numbers) for each command letter in an SVG path *d*."""
    for letter, body in _PATH_COMMAND.findall(d):
        yield letter, [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", body)]


def path_arcs(d):
    """Yield (start, (rx, ry, large_arc, sweep), end) for each arc in path *d*.

    Only the M/A/L/Z commands the button corner paths use are interpreted; an
    `A` command advances the current point to its endpoint, and `Z` closes the
    subpath without moving it.
    """
    x = y = 0.0
    for command, numbers in _path_commands(d):
        if command in ("M", "L"):
            x, y = numbers
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
    """
    (x1, y1), (rx, _ry, large_arc, sweep), (x2, y2) = start, arc, end
    x1p = (x1 - x2) / 2
    y1p = (y1 - y2) / 2
    denom = x1p * x1p + y1p * y1p
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
        match = None if transform is None else _TRANSLATE.fullmatch(transform.strip())
        if transform is None:
            origins[group.get("id")] = (0, 0)
        elif match:
            origins[group.get("id")] = (int(match.group(1)), int(match.group(2)))
        else:
            # Keep the raw text so a transform this test cannot parse fails
            # loudly instead of silently reading as the origin.
            origins[group.get("id")] = transform
    return origins


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
        sep = "-" if prefix else ""
        top = hints[f"{prefix}{sep}hint-top-margin"]
        bottom = hints[f"{prefix}{sep}hint-bottom-margin"]
        left = hints[f"{prefix}{sep}hint-left-margin"]
        right = hints[f"{prefix}{sep}hint-right-margin"]
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
