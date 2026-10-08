"""Validate the org.macos8.desktop Plasma desktop theme package."""

import math
import os
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from install_failure_cases import FailedInstallPreservesPackage
from install_lifecycle_cases import InstallLifecycleCases
from kpackage_install_case import KPackageInstallCase
from kde_config import read as read_kde_config
from package_metadata import PackageMetadata, load_metadata
from theme_install import (
    ROOT,
    assert_files_identical,
    install,
    installed_package,
    run,
    shadow_command_env,
)

DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktop-themes", DTHEME_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
PANEL_SVG = os.path.join(PACKAGE, "widgets", "panel-background.svg")
FRAME_SVG = os.path.join(PACKAGE, "widgets", "frame.svg")
FRAME_PREFIXES = ("plain", "raised", "sunken")
BUTTON_SVG = os.path.join(PACKAGE, "widgets", "button.svg")
BUTTON_PREFIXES = ("normal", "pressed", "focus")
BUTTON_MARGIN_HINTS = (
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
)
RADIOBUTTON_SVG = os.path.join(PACKAGE, "widgets", "radiobutton.svg")
CHECKMARKS_SVG = os.path.join(PACKAGE, "widgets", "checkmarks.svg")
LINEEDIT_SVG = os.path.join(PACKAGE, "widgets", "lineedit.svg")

LNF_DEFAULTS = os.path.join(
    ROOT, "theme", "look-and-feel", DTHEME_ID, "contents", "defaults"
)
# configparser reads the KDE `[plasmarc][Theme]` header greedily, so the
# section key includes the inner bracket pair.
PLASMA_SECTION = "plasmarc][Theme"

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

# Every pixel of each raised/sunken 3x3 corner slice, row-major in slice-local
# coordinates. The bevel must turn the corner: the edge bevel colours continue
# into the corner and meet there. A corner that stops the bevel one pixel short
# leaves a face-coloured (#DDDDDD) notch where the side tile shows highlight or
# shadow, so pinning the pixels makes that defect fail the suite.
CORNER_PIXELS = {
    "raised": {
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
            "#000000", "#999999", "#999999",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#999999", "#000000",
            "#999999", "#999999", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
    "sunken": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#999999", "#999999",
            "#000000", "#999999", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#999999", "#FFFFFF", "#000000",
            "#DDDDDD", "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", "#999999", "#DDDDDD",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#FFFFFF", "#000000",
            "#FFFFFF", "#FFFFFF", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
}

# Every pixel of each panel-background edge/corner slice, row-major in
# slice-local coordinates (the centre tile is checked separately). The menu-bar
# bevel must run the right way: #FFFFFF on the outer top/left edge, #999999 on
# the inner bottom edge and the outer right edge, and the #000000 rule on the
# outer bottom edge. `test_platinum_colours_present` sees the same four fills
# whichever way the bevel runs, so only pinning the pixels catches a swapped
# highlight/shadow or the black rule moved to the wrong edge.
PANEL_EDGE_PIXELS = {
    "top": (8, 2, ("#FFFFFF",) * 8 + ("#DDDDDD",) * 8),
    "bottom": (8, 2, ("#999999",) * 8 + ("#000000",) * 8),
    "left": (2, 8, ("#FFFFFF", "#DDDDDD") * 8),
    "right": (2, 8, ("#DDDDDD", "#999999") * 8),
    "topleft": (2, 2, ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#DDDDDD")),
    "topright": (2, 2, ("#FFFFFF", "#999999", "#DDDDDD", "#999999")),
    "bottomleft": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
    "bottomright": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
}


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


# Each widget SVG's root canvas. The four nine-slice widgets share a tight
# 12x12 canvas; checkmarks is two stacked 16x16 cells and radiobutton two
# side-by-side, so their canvases are 16x32 and 48x16.
SVG_CANVASES = (
    ("panel-background.svg", PANEL_SVG, 12, 12),
    ("frame.svg", FRAME_SVG, 12, 12),
    ("button.svg", BUTTON_SVG, 12, 12),
    ("lineedit.svg", LINEEDIT_SVG, 12, 12),
    ("checkmarks.svg", CHECKMARKS_SVG, 16, 32),
    ("radiobutton.svg", RADIOBUTTON_SVG, 48, 16),
)


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/Theme"
    PACKAGE_ID = DTHEME_ID
    PLASMA_API_KEY = "X-Plasma-API"
    PLASMA_API_VERSION = "5.0"


class TestSvgRootCanvas(unittest.TestCase):
    def test_root_canvas_matches_the_artwork_layout(self):
        # A root viewBox/width/height change rescales the whole widget while
        # every per-element test keeps passing, so pin the canvas for every
        # widget and tie it to the margin hints where there are any.
        for name, path, width, height in SVG_CANVASES:
            with self.subTest(svg=name):
                assert_root_canvas(self, ET.parse(path), width, height)


class TestPanelBackground(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(PANEL_SVG)
        self.ids = attribute_values(self.tree, "id")

    def test_nine_slice_ids_present(self):
        for name in SLICE_IDS:
            self.assertIn(name, self.ids, name)

    def test_hint_ids_present(self):
        for name in HINT_IDS:
            self.assertIn(name, self.ids, name)

    def test_panel_background_hint_geometry(self):
        # `test_hint_ids_present` pins only the hint ids, so a margin or inset
        # rect with the wrong position or size passes it. KSvg reads this
        # geometry to size the menu bar's nine-slice, so pin each hint.
        self.assertEqual(
            rect_geometry(self.tree),
            {
                "hint-tile-center": ("2", "2", "8", "8"),
                "hint-top-margin": ("2", "0", "2", "2"),
                "hint-bottom-margin": ("2", "10", "2", "2"),
                "hint-left-margin": ("0", "2", "2", "2"),
                "hint-right-margin": ("10", "2", "2", "2"),
                "hint-top-inset": ("2", "0", "8", "0"),
                "hint-bottom-inset": ("2", "12", "8", "0"),
                "hint-left-inset": ("0", "2", "0", "8"),
                "hint-right-inset": ("12", "2", "0", "8"),
            },
        )

    def test_panel_background_tiles_placed_by_margins(self):
        # `test_panel_background_pixels` composites each slice from its rects
        # but ignores the group's translate, so a group moved off its slice
        # draws from the wrong canvas region and still passes. Pin each tile's
        # origin against the margins that size the menu bar's nine-slice.
        assert_tiles_placed_by_margins(self, self.tree, [""])

    def test_platinum_colours_present(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment names all four colours, so a text search would pass
        # even if the artwork used none of them.
        fills = attribute_values(self.tree, "fill")
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_panel_background_pixels(self):
        # `test_platinum_colours_present` pins only the set of fills, so a
        # highlight/shadow swap or a rule on the wrong edge passes it. Read
        # each edge/corner slice's pixels in paint order instead.
        slices = render_slices(self.tree)
        for name, (width, height, expected) in PANEL_EDGE_PIXELS.items():
            pixels = slices[name]
            actual = tuple(
                pixels.get((x, y))
                for y in range(height)
                for x in range(width)
            )
            with self.subTest(slice=name):
                self.assertEqual(actual, expected, name)
        # The centre tile is one body rect, so every pixel is the same face.
        center = slices["center"]
        self.assertEqual(set(center.values()), {"#DDDDDD"})
        self.assertEqual(len(center), 8 * 8)

    def test_no_script_elements(self):
        assert_no_script_elements(self, self.tree)


class TestButton(unittest.TestCase):
    def test_button_slice_ids(self):
        tree = ET.parse(BUTTON_SVG)
        ids = attribute_values(tree, "id")
        for prefix in BUTTON_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for hint in BUTTON_MARGIN_HINTS:
                self.assertIn(f"{prefix}-{hint}", ids, hint)
        self.assertIn("hint-tile-center", ids)

    def test_button_hint_geometry(self):
        # `test_button_slice_ids` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, and normal/pressed use a 3px
        # border while focus uses 2px, so pin every state's margins and the
        # shared centre tile.
        expected = {"hint-tile-center": ("3", "3", "6", "6")}
        for prefix in ("normal", "pressed"):
            expected.update({
                f"{prefix}-hint-top-margin": ("3", "0", "6", "3"),
                f"{prefix}-hint-bottom-margin": ("3", "9", "6", "3"),
                f"{prefix}-hint-left-margin": ("0", "3", "3", "6"),
                f"{prefix}-hint-right-margin": ("9", "3", "3", "6"),
            })
        expected.update({
            "focus-hint-top-margin": ("2", "0", "8", "2"),
            "focus-hint-bottom-margin": ("2", "10", "8", "2"),
            "focus-hint-left-margin": ("0", "2", "2", "8"),
            "focus-hint-right-margin": ("10", "2", "2", "8"),
        })
        self.assertEqual(rect_geometry(ET.parse(BUTTON_SVG)), expected)

    def test_button_tiles_placed_by_margins(self):
        # `test_button_hint_geometry` pins the margins but not the artwork's
        # `transform`s, and `render_slices` ignores them; a tile translated off
        # its slice would draw from the wrong canvas region. Focus uses a 2px
        # border, so its centre sits at (2,2), not the shared hint's (3,3).
        assert_tiles_placed_by_margins(self, ET.parse(BUTTON_SVG), BUTTON_PREFIXES)

    def test_button_colours(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment and the hint rects (which set colour through `style`)
        # would otherwise make a text search pass without any Platinum grey.
        tree = ET.parse(BUTTON_SVG)
        fills = attribute_values(tree, "fill")
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(BUTTON_SVG))

    def test_button_bevel_direction(self):
        # `test_button_colours` sees the same four fills whichever way the
        # normal/pressed bevels run, so only the per-slice paint order pins
        # the direction: normal is #FFFFFF inside top/left and #999999 inside
        # bottom/right, and pressed is the exact inverse. Composite the edge
        # slices (their rects) and read the corner paths' document order.
        slices = render_slices(ET.parse(BUTTON_SVG))
        # (outer outline, bevel, inner face), from the slice's outer edge in.
        outward = {
            "normal-top": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-bottom": ("#000000", "#999999", "#DDDDDD"),
            "normal-left": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-right": ("#000000", "#999999", "#DDDDDD"),
            "pressed-top": ("#000000", "#999999", "#DDDDDD"),
            "pressed-bottom": ("#000000", "#FFFFFF", "#DDDDDD"),
            "pressed-left": ("#000000", "#999999", "#DDDDDD"),
            "pressed-right": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in outward.items():
            pixels = slices[name]
            horizontal = name.endswith(("top", "bottom"))
            reversed_axis = name.endswith(("bottom", "right"))
            for depth, colour in enumerate(colours):
                local = 2 - depth if reversed_axis else depth
                point = (0, local) if horizontal else (local, 0)
                with self.subTest(slice=name, depth=depth):
                    self.assertEqual(pixels.get(point), colour, name)

        # The corner paths carry no rects, so `render_slices` cannot composite
        # them; pin the order they are painted in instead: the black outline,
        # the corner's bevel colour, then the face.
        tree = ET.parse(BUTTON_SVG)
        groups = {el.get("id"): el for el in groups_with_id(tree)}
        corners = {
            "normal-topleft": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-topright": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomleft": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomright": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topleft": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topright": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomleft": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomright": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in corners.items():
            fills = tuple(
                child.get("fill")
                for child in groups[name]
                if local_name(child) == "path"
            )
            with self.subTest(corner=name):
                self.assertEqual(fills, colours, name)

    def test_button_corner_arcs_curve_around_the_inner_corner(self):
        # `test_button_bevel_direction` reads the corner paths' fills only, so
        # a corner path whose `d` arcs the wrong way, at the wrong radius, or
        # around the wrong point passes every other test: the rounded corner
        # is the button's one piece of geometry no pixel test reaches. Read
        # each arc's centre and radius from `d` and pin both against the
        # slice's inner corner and the corner's layer radii. A flipped sweep
        # flag moves the centre to the opposite corner; a changed radius moves
        # it too, so this catches an arc the fill-order test cannot.
        expected = {
            # group: (inner corner, radii in document order)
            "normal-topleft": ((3, 3), (3, 2, 1)),
            "normal-topright": ((0, 3), (3, 2, 2, 1, 1)),
            "normal-bottomleft": ((3, 0), (3, 2, 2, 1, 1)),
            "normal-bottomright": ((0, 0), (3, 2, 1)),
            "pressed-topleft": ((3, 3), (3, 2, 1)),
            "pressed-topright": ((0, 3), (3, 2, 2, 1, 1)),
            "pressed-bottomleft": ((3, 0), (3, 2, 2, 1, 1)),
            "pressed-bottomright": ((0, 0), (3, 2, 1)),
            "focus-topleft": ((2, 2), (2, 1)),
            "focus-topright": ((0, 2), (2, 1)),
            "focus-bottomleft": ((2, 0), (2, 1)),
            "focus-bottomright": ((0, 0), (2, 1)),
        }
        tree = ET.parse(BUTTON_SVG)
        groups = {el.get("id"): el for el in groups_with_id(tree)}
        for name, (center, radii) in expected.items():
            entries = [
                entry
                for path in groups[name]
                if local_name(path) == "path"
                for entry in path_arcs(path.get("d"))
            ]
            with self.subTest(corner=name):
                self.assertEqual(
                    [arc[0] for _, arc, _ in entries], list(radii), name
                )
                for start, arc, end in entries:
                    rx, ry = arc[0], arc[1]
                    self.assertEqual(rx, ry, name)
                    actual = arc_center(start, arc, end)
                    # The mixed-corner arcs meet the diagonal at coordinates
                    # rounded to three decimals, so their reconstructed centre
                    # is within a thousandth of the exact inner corner.
                    self.assertAlmostEqual(actual[0], center[0], places=2, msg=name)
                    self.assertAlmostEqual(actual[1], center[1], places=2, msg=name)

    def test_button_edge_pixels(self):
        # `test_button_bevel_direction` reads only the first column of each
        # horizontal band and the first row of each vertical one, so it pins
        # the band order only while the band stays uniform along its axis: a
        # rect narrowed to one pixel -- an outline or bevel missing along most
        # of the edge -- still passes. The frame and lineedit edge tests pin
        # every pixel; do the same for the button's normal/pressed bands.
        slices = render_slices(ET.parse(BUTTON_SVG))
        # (outer outline, bevel, inner face) for top/left, read from the
        # slice's outer edge in; bottom/right mirror it, with the outline
        # still on the outer edge and the bevel colour swapped.
        outward = {
            "normal": ("#000000", "#FFFFFF", "#DDDDDD"),
            "pressed": ("#000000", "#999999", "#DDDDDD"),
        }
        mirrored = {
            "normal": ("#DDDDDD", "#999999", "#000000"),
            "pressed": ("#DDDDDD", "#FFFFFF", "#000000"),
        }
        for prefix in ("normal", "pressed"):
            for side in ("top", "bottom", "left", "right"):
                band = (outward if side in ("top", "left") else mirrored)[prefix]
                if side in ("top", "bottom"):
                    # Three 6px rows, one per band colour.
                    expected = (band[0],) * 6 + (band[1],) * 6 + (band[2],) * 6
                    points = ((x, y) for y in range(3) for x in range(6))
                else:
                    # Six 3px rows, each running outer to inner.
                    expected = band * 6
                    points = ((x, y) for y in range(6) for x in range(3))
                pixels = slices[f"{prefix}-{side}"]
                actual = tuple(pixels.get(point) for point in points)
                with self.subTest(slice=f"{prefix}-{side}"):
                    self.assertEqual(actual, expected, f"{prefix}-{side}")

    def test_button_center_tiles_are_face(self):
        # `test_button_colours` pins only the set of fills, so a centre tile
        # recoloured to another Platinum grey (#FFFFFF or #999999) passes it,
        # and neither bevel test reads the centre. The centre is the button
        # face for both states, so pin every pixel.
        slices = render_slices(ET.parse(BUTTON_SVG))
        expected = {(x, y): "#DDDDDD" for y in range(6) for x in range(6)}
        for name in ("normal-center", "pressed-center"):
            with self.subTest(slice=name):
                self.assertEqual(slices[name], expected, name)

    def test_button_focus_ring_pixels(self):
        # The focus state is a 1px #000000 ring on the outer pixel of its 2px
        # border, transparent inside and in the centre, so ButtonFocus draws
        # it 1-2px outside the button outline. `test_button_colours` sees the
        # same four fills whichever pixel of the border is painted, so only
        # pinning the pixels keeps the ring from sliding to the inner pixel,
        # being recoloured to another Platinum grey, or the centre from being
        # filled in.
        slices = render_slices(ET.parse(BUTTON_SVG))
        expected = {
            "focus-top": {(x, 0): "#000000" for x in range(8)},
            "focus-bottom": {(x, 1): "#000000" for x in range(8)},
            "focus-left": {(0, y): "#000000" for y in range(8)},
            "focus-right": {(1, y): "#000000" for y in range(8)},
            "focus-center": {},
        }
        for name, pixels in expected.items():
            with self.subTest(slice=name):
                self.assertEqual(slices[name], pixels, name)

        # The rounded corners are paths, so `render_slices` cannot composite
        # them; pin that each carries exactly the one black ring path.
        tree = ET.parse(BUTTON_SVG)
        groups = {el.get("id"): el for el in groups_with_id(tree)}
        for name in (
            "focus-topleft", "focus-topright",
            "focus-bottomleft", "focus-bottomright",
        ):
            with self.subTest(corner=name):
                self.assertEqual(
                    [
                        child.get("fill") for child in groups[name]
                        if local_name(child) == "path"
                    ],
                    ["#000000"],
                    name,
                )


class TestRadioButton(unittest.TestCase):
    def test_radiobutton_contract(self):
        tree = ET.parse(RADIOBUTTON_SVG)
        ids = attribute_values(tree, "id")
        for name in ("normal", "symbol", "hint-size"):
            self.assertIn(name, ids, name)
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#000000"})
        assert_no_script_elements(self, tree)

    def test_radiobutton_geometry(self):
        # The black ring is a filled circle under the white face, so the two
        # normal circles must stay concentric at (8, 8) with r=8 over r=7 (a
        # 1px outline), and the selected dot must stay at (40, 8) with r=3 (a
        # 6x6 symbol). Pin each circle's centre with its fill and radius: the
        # contract test only checks the fill set, so a swap of the two faces
        # (black face, white ring) or a circle nudged off-centre would
        # otherwise pass.
        tree = ET.parse(RADIOBUTTON_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}
        circles = [
            el for el in by_id["normal"]
            if local_name(el) == "circle"
        ]
        self.assertEqual(
            [
                (float(el.get("cx")), float(el.get("cy")),
                 float(el.get("r")), el.get("fill"))
                for el in circles
            ],
            [(8, 8, 8, "#000000"), (8, 8, 7, "#FFFFFF")],
        )
        symbol = by_id["symbol"]
        self.assertEqual(
            (float(symbol.get("cx")), float(symbol.get("cy")),
             float(symbol.get("r")), symbol.get("fill")),
            (40, 8, 3, "#000000"),
        )
        # KSvg reads the hint circle's size (not its colour) to size the
        # widget, so its centre and radius are part of the contract too.
        hint = by_id["hint-size"]
        self.assertEqual(
            (float(hint.get("cx")), float(hint.get("cy")), float(hint.get("r"))),
            (24, 8, 8),
        )


class TestCheckmarks(unittest.TestCase):
    def test_checkmarks_contract(self):
        tree = ET.parse(CHECKMARKS_SVG)
        ids = attribute_values(tree, "id")
        for name in ("checkbox", "radiobutton"):
            self.assertIn(name, ids, name)
        strokes = attribute_values(tree, "stroke")
        self.assertEqual(strokes, {"#000000"})
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"none", "#000000"})
        assert_no_script_elements(self, tree)

    def test_checkmarks_geometry(self):
        # The consumers anchor the SvgItem with `anchors.fill`, so KSvg scales
        # each element by its bounds. Without the invisible full-cell bounding
        # rect the checkbox path's natural ~12x9 bounds (and the 6x6 dot)
        # would stretch to the 16x16 cell; pin the group, the rect, and the
        # glyph so that scaling cannot creep back in.
        tree = ET.parse(CHECKMARKS_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}

        checkbox = by_id["checkbox"]
        self.assertEqual(local_name(checkbox), "g")
        check_rects = [el for el in checkbox if local_name(el) == "rect"]
        check_paths = [el for el in checkbox if local_name(el) == "path"]
        self.assertEqual(len(check_rects), 1)
        self.assertEqual(len(check_paths), 1)
        self.assertEqual(
            [check_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "0", "16", "16", "none"],
        )
        self.assertEqual(
            check_paths[0].get("d"),
            "M 3.5,8.5 L 6.5,11.5 L 12.5,5.5",
        )
        self.assertEqual(check_paths[0].get("stroke-width"), "2")
        self.assertEqual(check_paths[0].get("fill"), "none")

        radiobutton = by_id["radiobutton"]
        self.assertEqual(local_name(radiobutton), "g")
        radio_rects = [el for el in radiobutton if local_name(el) == "rect"]
        radio_circles = [el for el in radiobutton if local_name(el) == "circle"]
        self.assertEqual(len(radio_rects), 1)
        self.assertEqual(len(radio_circles), 1)
        self.assertEqual(
            [radio_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "16", "16", "16", "none"],
        )
        # The dot must stay centred in the bottom 16x16 cell at (8, 24) so
        # the fallback indicator draws concentric with the radio face; the
        # contract test only checks the fill set, so a dot nudged off-centre
        # would otherwise pass. Pin its centre with its radius and fill.
        self.assertEqual(
            (float(radio_circles[0].get("cx")),
             float(radio_circles[0].get("cy")),
             float(radio_circles[0].get("r")),
             radio_circles[0].get("fill")),
            (8, 24, 3, "#000000"),
        )


class TestLineEdit(unittest.TestCase):
    def test_lineedit_slice_ids(self):
        tree = ET.parse(LINEEDIT_SVG)
        ids = attribute_values(tree, "id")
        for name in SLICE_IDS:
            self.assertIn(f"base-{name}", ids, name)
        for side in ("top", "bottom", "left", "right"):
            self.assertIn(f"base-hint-{side}-margin", ids, side)
        self.assertIn("hint-tile-center", ids)

    def test_lineedit_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: white face/highlight, grey shadow, black outline.
        tree = ET.parse(LINEEDIT_SVG)
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#999999", "#000000"})

    def test_lineedit_face_is_white(self):
        # The field must not silently become the grey frame face: pin the
        # centre tile to #FFFFFF so a copy of frame.svg's sunken geometry
        # fails here.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        self.assertEqual(
            slices["base-center"],
            {(x, y): "#FFFFFF" for y in range(6) for x in range(6)},
        )

    def test_lineedit_edge_bevels_are_sunken(self):
        # `test_lineedit_colours` sees the same three fills whichever way the
        # bevel runs, so only the per-slice paint order pins the sunken
        # direction: the #999999 shadow sits inside the top/left outline and
        # the #FFFFFF highlight inside the bottom/right, with the white face
        # innermost. A swap (a raised field) passes every existing test.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        # (outer outline, bevel, inner face) read from the slice's outer edge in.
        outward = ("#000000", "#999999", "#FFFFFF")
        # The bottom/right edges mirror the top/left: the outline stays on the
        # outer edge while the bevel colour swaps sides.
        mirrored = ("#FFFFFF", "#FFFFFF", "#000000")
        for side in ("top", "bottom", "left", "right"):
            band = outward if side in ("top", "left") else mirrored
            if side in ("top", "bottom"):
                # Three 6px rows, one per band colour.
                expected = (band[0],) * 6 + (band[1],) * 6 + (band[2],) * 6
                points = ((x, y) for y in range(3) for x in range(6))
            else:
                # Six 3px rows, each running outer to inner.
                expected = band * 6
                points = ((x, y) for y in range(6) for x in range(3))
            pixels = slices[f"base-{side}"]
            actual = tuple(pixels.get(point) for point in points)
            with self.subTest(slice=f"base-{side}"):
                self.assertEqual(actual, expected, f"base-{side}")

    def test_lineedit_corner_bevels_turn_the_corner(self):
        # The edge bevel must continue into the corner and meet there; a
        # corner that stops one pixel short leaves a white face-coloured
        # notch where the edge tile shows shadow or highlight. Pin every
        # pixel of each corner slice.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        expected = {
            "base-topleft": (
                "#000000", "#000000", "#000000",
                "#000000", "#999999", "#999999",
                "#000000", "#999999", "#FFFFFF",
            ),
            "base-topright": (
                "#000000", "#000000", "#000000",
                "#999999", "#FFFFFF", "#000000",
                "#FFFFFF", "#FFFFFF", "#000000",
            ),
            "base-bottomleft": (
                "#000000", "#999999", "#FFFFFF",
                "#000000", "#FFFFFF", "#FFFFFF",
                "#000000", "#000000", "#000000",
            ),
            "base-bottomright": (
                "#FFFFFF", "#FFFFFF", "#000000",
                "#FFFFFF", "#FFFFFF", "#000000",
                "#000000", "#000000", "#000000",
            ),
        }
        for name, colours in expected.items():
            pixels = slices[name]
            actual = tuple(
                pixels.get((x, y))
                for y in range(3)
                for x in range(3)
            )
            with self.subTest(corner=name):
                self.assertEqual(actual, colours, name)

    def test_lineedit_tiles_placed_by_margins(self):
        # `test_lineedit_face_is_white` composites `base-center` slice-local,
        # so a `base-*` group translated off its slice would still pass. Pin
        # every tile's origin against the base margin hints.
        assert_tiles_placed_by_margins(self, ET.parse(LINEEDIT_SVG), ["base"])

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(LINEEDIT_SVG))


class TestFrame(unittest.TestCase):
    def test_frame_svg_contract(self):
        tree = ET.parse(FRAME_SVG)
        ids = attribute_values(tree, "id")
        for prefix in FRAME_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for side in ("top", "bottom", "left", "right"):
                self.assertIn(f"{prefix}-hint-{side}-margin", ids, side)
        self.assertIn("hint-tile-center", ids)
        # Read the raw file for the palette: the frame's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(FRAME_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)
        assert_no_script_elements(self, tree)

    def test_frame_hint_geometry(self):
        # `test_frame_svg_contract` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, so pin each state's margins and
        # the shared centre tile.
        expected = {"hint-tile-center": ("3", "3", "6", "6")}
        for prefix in FRAME_PREFIXES:
            expected.update({
                f"{prefix}-hint-top-margin": ("3", "0", "6", "3"),
                f"{prefix}-hint-bottom-margin": ("3", "9", "6", "3"),
                f"{prefix}-hint-left-margin": ("0", "3", "3", "6"),
                f"{prefix}-hint-right-margin": ("9", "3", "3", "6"),
            })
        self.assertEqual(rect_geometry(ET.parse(FRAME_SVG)), expected)

    def test_frame_tiles_placed_by_margins(self):
        # The pixel tests composite each slice from its rects but ignore the
        # group's translate, so a tile translated off its slice draws from the
        # wrong canvas region and still passes. Pin every state's tile origins
        # against its margin hints.
        assert_tiles_placed_by_margins(self, ET.parse(FRAME_SVG), FRAME_PREFIXES)

    def test_frame_corner_bevels_turn_the_corner(self):
        slices = render_slices(ET.parse(FRAME_SVG))
        for prefix, corners in CORNER_PIXELS.items():
            for name, expected in corners.items():
                pixels = slices[f"{prefix}-{name}"]
                actual = tuple(
                    pixels.get((x, y))
                    for y in range(3)
                    for x in range(3)
                )
                self.assertEqual(actual, expected, f"{prefix}-{name}")

    def test_frame_plain_corners_are_flat(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners, and `test_frame_edge_bevels` does not reach the
        # corners, so a plain corner that copy-pasted a bevel from a
        # neighbouring state leaves a #FFFFFF or #999999 pixel where the face
        # should be and passes every existing test. Pin every plain-corner
        # pixel: the face plus the 1px black outline on the two outer edges,
        # with no bevel.
        slices = render_slices(ET.parse(FRAME_SVG))
        expected = {
            "plain-topleft": (
                "#000000", "#000000", "#000000",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
            ),
            "plain-topright": (
                "#000000", "#000000", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
            ),
            "plain-bottomleft": (
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#000000", "#000000",
            ),
            "plain-bottomright": (
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#000000", "#000000", "#000000",
            ),
        }
        for name, colours in expected.items():
            pixels = slices[name]
            actual = tuple(
                pixels.get((x, y))
                for y in range(3)
                for x in range(3)
            )
            with self.subTest(corner=name):
                self.assertEqual(actual, colours, name)

    def test_frame_edge_bevels(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners; the edge slices carry the same bevel along the frame
        # and are otherwise checked by id alone, so a raised top painted with
        # the shadow colour (or a plain edge that grew a bevel) passes every
        # existing test. Pin each edge's pixels from its outer edge in, and
        # each state's centre tile to the face.
        slices = render_slices(ET.parse(FRAME_SVG))
        # (outer outline, bevel, inner face) read from the slice's outer edge
        # inward; plain has no bevel, so its middle band is the face.
        outward = {
            "plain": ("#000000", "#DDDDDD", "#DDDDDD"),
            "raised": ("#000000", "#FFFFFF", "#DDDDDD"),
            "sunken": ("#000000", "#999999", "#DDDDDD"),
        }
        # The bottom/right edges mirror the top/left: the outline stays on the
        # outer edge while the bevel colour swaps sides.
        mirrored = {
            "plain": ("#DDDDDD", "#DDDDDD", "#000000"),
            "raised": ("#DDDDDD", "#999999", "#000000"),
            "sunken": ("#DDDDDD", "#FFFFFF", "#000000"),
        }
        for prefix in FRAME_PREFIXES:
            for side in ("top", "bottom", "left", "right"):
                band = (
                    outward if side in ("top", "left") else mirrored
                )[prefix]
                horizontal = side in ("top", "bottom")
                if horizontal:
                    # Three 6px rows, one per band colour.
                    expected = (band[0],) * 6 + (band[1],) * 6 + (band[2],) * 6
                    points = ((x, y) for y in range(3) for x in range(6))
                else:
                    # Six 3px rows, each running outer to inner.
                    expected = band * 6
                    points = ((x, y) for y in range(6) for x in range(3))
                pixels = slices[f"{prefix}-{side}"]
                actual = tuple(pixels.get(point) for point in points)
                with self.subTest(slice=f"{prefix}-{side}"):
                    self.assertEqual(actual, expected, f"{prefix}-{side}")
            # The centre tile is one body rect, so every pixel is the face.
            with self.subTest(slice=f"{prefix}-center"):
                self.assertEqual(
                    slices[f"{prefix}-center"],
                    {(x, y): "#DDDDDD" for y in range(6) for x in range(6)},
                )

    def test_frame_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = os.path.join(
                installed_package(tmp, "desktoptheme", DTHEME_ID),
                "widgets", "frame.svg",
            )
            assert_files_identical(self, FRAME_SVG, target)
            again = install(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


class TestDefaultsWiring(unittest.TestCase):
    def test_defaults_select_the_desktop_theme(self):
        parser = read_kde_config(LNF_DEFAULTS)
        self.assertEqual(
            parser.get(PLASMA_SECTION, "name"),
            load_metadata(METADATA)["KPlugin"]["Id"],
        )


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "desktoptheme"
    PACKAGE_ID = DTHEME_ID
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = (
        "metadata.json",
        os.path.join("widgets", "panel-background.svg"),
        os.path.join("widgets", "button.svg"),
        os.path.join("widgets", "radiobutton.svg"),
        os.path.join("widgets", "checkmarks.svg"),
        os.path.join("widgets", "lineedit.svg"),
    )

    def reinstall_failure_env(self, tmp):
        # Shadow `cp` with a fake that fails only when copying the desktop
        # theme (the look-and-feel copy must still succeed), writing part of
        # the tree then dying like a killed or out-of-space `cp` would.
        real_cp = shutil.which("cp")
        return shadow_command_env(
            tmp,
            "cp",
            "#!/bin/sh\n"
            'case "$2" in\n'
            "  */desktop-themes/*)\n"
            '    dest="$3/$(basename "$2")"\n'
            '    mkdir -p "$dest"\n'
            '    printf partial > "$dest/metadata.json"\n'
            "    exit 1;;\n"
            "esac\n"
            f'exec "{real_cp}" "$@"\n',
        )


@unittest.skipUnless(
    shutil.which("plasma-apply-desktoptheme"),
    "needs plasma-apply-desktoptheme",
)
class TestApplyDesktopTheme(unittest.TestCase):
    def test_apply_lists_and_selects_the_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            env = dict(
                os.environ,
                XDG_DATA_HOME=os.path.join(tmp, "share"),
                XDG_CONFIG_HOME=os.path.join(tmp, "config"),
            )
            listed = run(
                ["plasma-apply-desktoptheme", "--list-themes"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn(DTHEME_ID, listed.stdout)
            applied = run(
                ["plasma-apply-desktoptheme", DTHEME_ID],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            parser = read_kde_config(os.path.join(tmp, "config", "plasmarc"))
            self.assertEqual(parser.get("Theme", "name"), DTHEME_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Plasma/Theme"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = DTHEME_ID


if __name__ == "__main__":
    unittest.main()
