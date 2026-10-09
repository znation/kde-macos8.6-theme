"""Tests for tests/svg_assertions.py -- the shared artwork-assertion helpers.

Every desktop-theme widget test reads the artwork through these helpers, but
each widget test only reaches the helpers where that widget's current artwork
happens to exercise them. A helper that mis-parses a path or silently treats a
misplaced group as sitting at the origin would weaken all of the widget tests
at once, so pin the parsing/geometry helpers directly here and prove the
structural guards can actually fail.
"""

from __future__ import annotations

import contextlib
import unittest
import xml.etree.ElementTree as ET

from error_assertions import error_message
from svg_assertions import (
    RAISED_FACE_CORNERS,
    SLICE_IDS,
    arc_center,
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_hint_geometry,
    assert_no_script_elements,
    assert_root_canvas,
    assert_slice_ids_present,
    assert_slice_pixels,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    assert_unique_ids,
    attribute_values,
    children_named,
    circle_geometry,
    elements_by_id,
    face_corners,
    face_edge_bands,
    groups_with_id,
    flat_face_corners,
    nine_slice_hint_geometry,
    nine_slice_margins,
    local_name,
    nine_slice_tile_sizes,
    path_arcs,
    pixel_map,
    rect_geometry,
    render_slices,
    sunken_face_corners,
    tile_origins,
)


def _svg_tree(body, **attributes):
    """Return an ElementTree for a namespaced SVG root wrapping *body*.

    The fixtures that build an SVG document root share this wrapper: a
    ``<svg xmlns=...>`` element around a body string. *attributes* are the
    extra root attributes the canvas builders need (``width``, ``height``,
    ``viewBox``). Declaring the SVG namespace is what makes ElementTree
    report each tag as ``{http://www.w3.org/2000/svg}rect``, the form
    `local_name` strips back to ``rect``.
    """
    attrs = "".join(
        f' {name}="{value}"' for name, value in attributes.items()
    )
    return ET.ElementTree(
        ET.fromstring(
            f'<svg xmlns="http://www.w3.org/2000/svg"{attrs}>{body}</svg>'
        )
    )


# A minimal valid nine-slice layout: a 12x12 canvas with 4px borders, so every
# tile region is 4x4. The hints place the edge tiles at 4 and the corners at
# the canvas corners.
_HINTS = (
    '<rect id="hint-tile-center" x="4" y="4" width="4" height="4"/>'
    '<rect id="hint-top-margin" x="4" y="0" width="4" height="4"/>'
    '<rect id="hint-bottom-margin" x="4" y="8" width="4" height="4"/>'
    '<rect id="hint-left-margin" x="0" y="4" width="4" height="4"/>'
    '<rect id="hint-right-margin" x="8" y="4" width="4" height="4"/>'
)
_ORIGINS = {
    "top": (4, 0),
    "bottom": (4, 8),
    "left": (0, 4),
    "right": (8, 4),
    "center": (4, 4),
    "topleft": (0, 0),
    "topright": (8, 0),
    "bottomleft": (0, 8),
    "bottomright": (8, 8),
}


def _nine_slice_tree(origins=None, sizes=None):
    """Build a nine-slice tree whose groups sit at *origins* with *sizes* rects.

    *origins* defaults to the layout the hints imply; *sizes* overrides a
    group's ``(width, height)``, so a caller can paint a slice outside its
    tile.
    """
    origins = _ORIGINS if origins is None else origins
    sizes = sizes or {}
    groups = "".join(
        f'<g id="{name}" transform="translate({x},{y})">'
        f'<rect x="0" y="0" width="{sizes.get(name, (4, 4))[0]}" '
        f'height="{sizes.get(name, (4, 4))[1]}" fill="#000000"/>'
        "</g>"
        for name, (x, y) in origins.items()
    )
    return _svg_tree(
        f"{_HINTS}{groups}", width="12", height="12", viewBox="0 0 12 12"
    )


class TestPathArcs(unittest.TestCase):
    def test_tracks_the_current_point_through_commands(self):
        # An arc's start point is the current point the preceding M/L left, not
        # its own first coordinate pair; reading the wrong start moves the
        # reconstructed centre and the button corner test would measure the
        # wrong geometry.
        arcs = list(path_arcs("M1,1 L5,1 A2,2 0 0 1 9,5 L9,9 A2,2 0 0 0 5,9"))
        self.assertEqual(
            arcs,
            [
                ((5.0, 1.0), (2.0, 2.0, 0, 1), (9.0, 5.0)),
                ((9.0, 9.0), (2.0, 2.0, 0, 0), (5.0, 9.0)),
            ],
        )

    def test_z_yields_no_phantom_arc(self):
        # `Z` closes a subpath without drawing; reading it as an arc command
        # would yield a phantom arc, and the corner test would read a radius
        # that is not in the artwork.
        arcs = list(path_arcs("M1,1 A2,2 0 0 1 3,3 Z"))
        self.assertEqual(arcs, [((1.0, 1.0), (2.0, 2.0, 0, 1), (3.0, 3.0))])

    def test_z_returns_to_the_subpath_start(self):
        # `Z` closes the current subpath, so SVG moves the current point back
        # to that subpath's start. Ignoring it leaves the current point at the
        # last L/A endpoint, and an arc after `Z` is reconstructed from the
        # wrong start (a misplaced corner would still pass the pixel test).
        arcs = list(path_arcs("M1,1 L5,1 Z A2,2 0 0 1 9,5"))
        self.assertEqual(arcs, [((1.0, 1.0), (2.0, 2.0, 0, 1), (9.0, 5.0))])

    def test_z_does_not_leak_into_the_next_subpath(self):
        # A later `M` starts a new subpath, so the `Z` before it must not reset
        # the current point the new subpath's arc starts from.
        arcs = list(path_arcs("M1,1 L5,1 Z M7,7 A2,2 0 0 1 9,9"))
        self.assertEqual(arcs, [((7.0, 7.0), (2.0, 2.0, 0, 1), (9.0, 9.0))])

    def test_rejects_unsupported_path_commands(self):
        # H/V/C/Q/S/T and lowercase relative commands are not parsed. Before
        # the guard they folded into the preceding command's number body and
        # were read as extra coordinates (or raised a bare unpack error on a
        # later command), so pin the named rejection instead.
        for d in (
            "M0,0 H5",
            "M0,0 V5",
            "M0,0 C1,1 2,2 3,3",
            "M0,0 Q1,1 2,2",
            "m0,0 l5,5",
        ):
            with self.subTest(d=d):
                self.assertIn(
                    "unsupported SVG path command",
                    error_message(self, ValueError, list, path_arcs(d)),
                )

    def test_rejects_wrong_number_count_naming_the_command(self):
        # A command body with too few or too many numbers used to raise a bare
        # "not enough/too many values to unpack" that named neither the command
        # nor the path, so a malformed fixture was hard to locate. Pin the
        # named rejection instead.
        for d, command, count in (
            ("M1,1 A2,2 0 0 1", "A", 5),
            ("M1,1 A2,2 0 0 1 9,9 9", "A", 8),
            ("M1,1 2,2", "M", 4),
            ("M1,1 Z5", "Z", 1),
        ):
            with self.subTest(d=d):
                message = error_message(self, ValueError, list, path_arcs(d))
                self.assertIn(f"command {command}", message)
                self.assertIn(f"got {count}", message)
                self.assertIn(repr(d), message)


class TestArcCenter(unittest.TestCase):
    def test_flags_select_the_side_of_the_chord(self):
        # Endpoints (0,3)->(3,0) at radius 3 admit two centres, (3,3) and
        # (0,0). The large-arc and sweep flags choose one; a flipped sign in
        # arc_center would place the centre on the wrong side and a corner arc
        # that curved the wrong way could still pass.
        start, end = (0.0, 3.0), (3.0, 0.0)
        for flags, expected in (
            ((0, 1), (3.0, 3.0)),
            ((0, 0), (0.0, 0.0)),
            ((1, 1), (0.0, 0.0)),
            ((1, 0), (3.0, 3.0)),
        ):
            with self.subTest(flags=flags):
                self.assertEqual(
                    arc_center(start, (3, 3, flags[0], flags[1]), end), expected
                )

    def test_zero_length_chord_names_the_arc(self):
        # start == end has no perpendicular bisector, so the centre is
        # undefined. Before the guard this was a bare ZeroDivisionError that
        # named neither the arc nor its defect.
        message = error_message(
            self, ValueError, arc_center, (2.0, 2.0), (3, 3, 0, 1), (2.0, 2.0)
        )
        self.assertIn("(2.0, 2.0)", message)
        self.assertIn("zero-length chord", message)

    def test_radius_too_small_names_the_arc_and_the_chord(self):
        # Endpoints 6 apart need radius >= 3; a radius of 2 cannot reach both
        # and the square root would fail with "math domain error".
        message = error_message(
            self, ValueError, arc_center, (0.0, 0.0), (2, 2, 0, 1), (6.0, 0.0)
        )
        self.assertIn("(0.0, 0.0)", message)
        self.assertIn("(6.0, 0.0)", message)
        self.assertIn("radius 2", message)
        self.assertIn("half its chord 3", message)


class TestTileOrigins(unittest.TestCase):
    def test_reads_translates_and_surfaces_unparseable_transforms(self):
        tree = _svg_tree(
            '<g id="moved" transform="translate(3, 4)"/>'
            '<g id="at-origin"/>'
            '<g id="unknown" transform="matrix(1,0,0,1,9,9)"/>'
        )
        origins = tile_origins(tree)
        self.assertEqual(origins["moved"], (3, 4))
        self.assertEqual(origins["at-origin"], (0, 0))
        # A transform this helper cannot parse must come back as its raw text,
        # so the caller's equality check fails loudly instead of reading a
        # misplaced group as sitting at the origin.
        self.assertEqual(origins["unknown"], "matrix(1,0,0,1,9,9)")


class TestNineSliceMargins(unittest.TestCase):
    def test_derives_the_four_margins_from_a_centred_tile(self):
        # KSvg reads these four hint rects to size the nine-slice, so a wrong
        # coordinate here would make every widget test pin the wrong layout.
        # Pin a 3px-border/6px-tile layout and a differently sized one, plus
        # the unprefixed form (``""``) whose values match the _HINTS fixture
        # above (a 4px border around a 4px tile on the 12x12 canvas).
        self.assertEqual(
            nine_slice_margins("normal", 3, 6),
            {
                "normal-hint-top-margin": ("3", "0", "6", "3"),
                "normal-hint-bottom-margin": ("3", "9", "6", "3"),
                "normal-hint-left-margin": ("0", "3", "3", "6"),
                "normal-hint-right-margin": ("9", "3", "3", "6"),
            },
        )
        self.assertEqual(
            nine_slice_margins("focus", 2, 8),
            {
                "focus-hint-top-margin": ("2", "0", "8", "2"),
                "focus-hint-bottom-margin": ("2", "10", "8", "2"),
                "focus-hint-left-margin": ("0", "2", "2", "8"),
                "focus-hint-right-margin": ("10", "2", "2", "8"),
            },
        )
        self.assertEqual(
            nine_slice_margins("", 4, 4),
            {
                "hint-top-margin": ("4", "0", "4", "4"),
                "hint-bottom-margin": ("4", "8", "4", "4"),
                "hint-left-margin": ("0", "4", "4", "4"),
                "hint-right-margin": ("8", "4", "4", "4"),
            },
        )


class TestNineSliceHintGeometry(unittest.TestCase):
    def test_pins_the_shared_centre_plus_every_state_s_margins(self):
        # Every widget's hint-geometry test compares this helper's dict against
        # the SVG's parsed hints, so a wrong centre coordinate here would make
        # them all pin the wrong layout. The unprefixed 4px-border/4px-tile
        # layout must match the _HINTS fixture exactly.
        self.assertEqual(
            nine_slice_hint_geometry([""], 4, 4),
            {
                "hint-tile-center": ("4", "4", "4", "4"),
                "hint-top-margin": ("4", "0", "4", "4"),
                "hint-bottom-margin": ("4", "8", "4", "4"),
                "hint-left-margin": ("0", "4", "4", "4"),
                "hint-right-margin": ("8", "4", "4", "4"),
            },
        )
        # Several states share the one centre hint, so the helper must merge
        # each prefix's margins beside it without dropping the earlier ones.
        self.assertEqual(
            nine_slice_hint_geometry(("normal", "pressed"), 3, 6),
            {
                "hint-tile-center": ("3", "3", "6", "6"),
                **nine_slice_margins("normal", 3, 6),
                **nine_slice_margins("pressed", 3, 6),
            },
        )


class TestNineSliceTileSizes(unittest.TestCase):
    def test_derives_each_tile_from_the_borders_and_canvas(self):
        # assert_slices_stay_within_their_tiles and the list-item test both
        # build their tile map here, so a wrong edge or centre size would make
        # both pin the wrong regions. The 12x12 canvas with 4px borders matches
        # the _HINTS fixture: every tile is 4x4.
        self.assertEqual(
            nine_slice_tile_sizes(12, 12, 4, 4, 4, 4),
            {
                "top": (4, 4),
                "bottom": (4, 4),
                "left": (4, 4),
                "right": (4, 4),
                "center": (4, 4),
                "topleft": (4, 4),
                "topright": (4, 4),
                "bottomleft": (4, 4),
                "bottomright": (4, 4),
            },
        )
        # Distinct borders (left 2, right 4, top 3, bottom 5 on a 16x10 canvas)
        # must stretch each edge tile by canvas minus its two opposite borders,
        # not to a shared size.
        self.assertEqual(
            nine_slice_tile_sizes(16, 10, 2, 4, 3, 5),
            {
                "top": (10, 3),
                "bottom": (10, 5),
                "left": (2, 2),
                "right": (4, 2),
                "center": (10, 2),
                "topleft": (2, 3),
                "topright": (4, 3),
                "bottomleft": (2, 5),
                "bottomright": (4, 5),
            },
        )


class TestSunkenFaceCorners(unittest.TestCase):
    def test_paints_the_outline_shadow_and_highlight_around_the_face(self):
        # The frame's sunken state and the line edit's field both read their
        # corner pixels from this generator, so a swapped band would weaken
        # both tests at once. Pin the full #DDDDDD table, then check the
        # #FFFFFF face substitutes only the face pixels.
        sunken = sunken_face_corners("#DDDDDD")
        self.assertEqual(
            sunken,
            {
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
        )
        self.assertEqual(
            sunken_face_corners("#FFFFFF"),
            {
                name: tuple(
                    "#FFFFFF" if colour == "#DDDDDD" else colour
                    for colour in pixels
                )
                for name, pixels in sunken.items()
            },
        )


class TestFlatFaceCorners(unittest.TestCase):
    def test_paints_only_the_outline_and_the_face(self):
        # The frame's plain state and the scroll-bar trough both read their
        # corner pixels from this generator, so a stray bevel colour would
        # weaken both tests at once. Pin the full #DDDDDD table, then check
        # the #EEEEEE face substitutes only the face pixels.
        flat = flat_face_corners("#DDDDDD")
        self.assertEqual(
            flat,
            {
                "topleft": (
                    "#000000", "#000000", "#000000",
                    "#000000", "#DDDDDD", "#DDDDDD",
                    "#000000", "#DDDDDD", "#DDDDDD",
                ),
                "topright": (
                    "#000000", "#000000", "#000000",
                    "#DDDDDD", "#DDDDDD", "#000000",
                    "#DDDDDD", "#DDDDDD", "#000000",
                ),
                "bottomleft": (
                    "#000000", "#DDDDDD", "#DDDDDD",
                    "#000000", "#DDDDDD", "#DDDDDD",
                    "#000000", "#000000", "#000000",
                ),
                "bottomright": (
                    "#DDDDDD", "#DDDDDD", "#000000",
                    "#DDDDDD", "#DDDDDD", "#000000",
                    "#000000", "#000000", "#000000",
                ),
            },
        )
        self.assertEqual(
            flat_face_corners("#EEEEEE"),
            {
                name: tuple(
                    "#EEEEEE" if colour == "#DDDDDD" else colour
                    for colour in pixels
                )
                for name, pixels in flat.items()
            },
        )


class TestFaceEdgeBands(unittest.TestCase):
    def test_paints_the_outline_bevel_and_face_for_each_direction(self):
        # The button, frame, line edit and scroll-bar trough all read their
        # edge bands from this generator, so a swapped highlight/shadow would
        # weaken every one of them at once. Pin all three directions on the
        # #DDDDDD face, then check a different face substitutes only the face
        # pixels.
        self.assertEqual(
            face_edge_bands("#DDDDDD", "raised"),
            (("#000000", "#FFFFFF", "#DDDDDD"),
             ("#DDDDDD", "#999999", "#000000")),
        )
        self.assertEqual(
            face_edge_bands("#DDDDDD", "sunken"),
            (("#000000", "#999999", "#DDDDDD"),
             ("#DDDDDD", "#FFFFFF", "#000000")),
        )
        self.assertEqual(
            face_edge_bands("#DDDDDD", "flat"),
            (("#000000", "#DDDDDD", "#DDDDDD"),
             ("#DDDDDD", "#DDDDDD", "#000000")),
        )
        self.assertEqual(
            face_edge_bands("#FFFFFF", "sunken"),
            (("#000000", "#999999", "#FFFFFF"),
             ("#FFFFFF", "#FFFFFF", "#000000")),
        )

    def test_rejects_an_unknown_direction_naming_it(self):
        self.assertIn(
            "bevelled",
            error_message(
                self, ValueError, face_edge_bands, "#DDDDDD", "bevelled"
            ),
        )


class TestFaceCorners(unittest.TestCase):
    def test_selects_the_table_for_each_bevel(self):
        # `assert_face_bevel` and its `_face_slices` fixture both read the
        # corner table through this dispatch, so a swapped branch would
        # weaken both at once. Pin each bevel to its table, including a
        # non-#DDDDDD face for the sunken and flat generators.
        self.assertIs(face_corners("#DDDDDD", "raised"), RAISED_FACE_CORNERS)
        self.assertEqual(
            face_corners("#DDDDDD", "sunken"), sunken_face_corners("#DDDDDD")
        )
        self.assertEqual(
            face_corners("#FFFFFF", "sunken"), sunken_face_corners("#FFFFFF")
        )
        self.assertEqual(
            face_corners("#EEEEEE", "flat"), flat_face_corners("#EEEEEE")
        )

    def test_rejects_an_unknown_bevel_naming_it(self):
        self.assertIn(
            "bevelled",
            error_message(
                self, ValueError, face_corners, "#DDDDDD", "bevelled"
            ),
        )


class TestCircleGeometry(unittest.TestCase):
    def test_reads_centre_and_radius_as_floats(self):
        # The radiobutton and checkmarks tests compare this against float
        # tuples, so a string passthrough would fail there; pin the conversion
        # (a decimal cx) and the argument order directly.
        element = ET.fromstring(
            '<circle cx="7.5" cy="24" r="3" fill="#000000"/>'
        )
        self.assertEqual(circle_geometry(element), (7.5, 24.0, 3.0))

    def test_missing_dimension_names_the_circle_and_the_attribute(self):
        # ElementTree hands an absent attribute back as None, and
        # circle_geometry converts each value with float(); the error must
        # name the circle and the attribute rather than surfacing as a bare
        # TypeError.
        element = ET.fromstring('<circle id="symbol" cy="8" r="3"/>')
        message = error_message(self, ValueError, circle_geometry, element)
        self.assertIn("symbol", message)
        self.assertIn("'cx'", message)

    def test_anonymous_missing_dimension_still_names_the_attribute(self):
        # The radiobutton face and checkmarks dot carry no id of their own, so
        # the diagnostic must still name the attribute when it cannot name the
        # element.
        element = ET.fromstring('<circle cy="8" r="3"/>')
        self.assertIn(
            "'cx'", error_message(self, ValueError, circle_geometry, element)
        )

    def test_non_numeric_dimension_names_the_circle_attribute_and_value(self):
        # A present but non-numeric value (r="3px") would reach float() and
        # surface as a bare ValueError naming no circle or attribute; name
        # the circle, the attribute and the value instead.
        element = ET.fromstring(
            '<circle id="symbol" cx="8" cy="8" r="3px"/>'
        )
        message = error_message(self, ValueError, circle_geometry, element)
        self.assertIn("symbol", message)
        self.assertIn("'r'", message)
        self.assertIn("'3px'", message)

    def test_anonymous_non_numeric_dimension_still_names_the_attribute(self):
        element = ET.fromstring('<circle cx="8" cy="8" r="3px"/>')
        message = error_message(self, ValueError, circle_geometry, element)
        self.assertIn("'r'", message)
        self.assertIn("'3px'", message)


class TestRectGeometry(unittest.TestCase):
    def test_reads_the_four_dimensions_of_each_id_bearing_rect(self):
        # The layout guards and the per-widget hint tests read geometry
        # through this map, so a missing or reordered value would mispin the
        # nine-slice layout. Pin the order and that a rect without an id is
        # left out.
        tree = _svg_tree(
            '<rect id="a" x="1" y="2" width="3" height="4"/>'
            '<rect x="9" y="9" width="9" height="9"/>'
        )
        self.assertEqual(rect_geometry(tree), {"a": ("1", "2", "3", "4")})

    def test_missing_dimension_names_the_rect_and_the_attribute(self):
        # ElementTree hands an absent attribute back as None, and the layout
        # guards convert each value with int(); the error must name the rect
        # and the attribute rather than surfacing as a bare TypeError.
        tree = _svg_tree(
            '<rect id="hint-top-margin" y="0" width="4" height="4"/>'
        )
        message = error_message(self, ValueError, rect_geometry, tree)
        self.assertIn("hint-top-margin", message)
        self.assertIn("'x'", message)

    def test_non_integer_dimension_names_the_rect_attribute_and_value(self):
        # A hint rect is never rendered by render_slices (it lives outside
        # the id-bearing <g> groups), so rect_geometry is the only reader of
        # its x/y/width/height. A present but non-integer value (x="4px")
        # would reach the layout guards' int() and surface as a bare
        # ValueError naming no rect; name the rect, attribute and value.
        tree = _svg_tree(
            '<rect id="hint-top-margin" x="4px" y="0" width="4" '
            'height="4"/>'
        )
        message = error_message(self, ValueError, rect_geometry, tree)
        self.assertIn("hint-top-margin", message)
        self.assertIn("'x'", message)
        self.assertIn("'4px'", message)


class TestRenderSlices(unittest.TestCase):
    def test_later_rects_paint_over_earlier_ones(self):
        # KSvg composites a tile's rects in document order, so an overlay's
        # colour must win; otherwise a bevel drawn under the face would read as
        # the face and a pixel test would pin the wrong layer.
        tree = _svg_tree(
            '<g id="g">'
            '<rect x="0" y="0" width="2" height="1" fill="#111111"/>'
            '<rect x="1" y="0" width="1" height="1" fill="#222222"/>'
            "</g>"
        )
        self.assertEqual(
            render_slices(tree)["g"],
            {(0, 0): "#111111", (1, 0): "#222222"},
        )

    def test_missing_extent_names_the_rect_and_the_attribute(self):
        # render_slices iterates range(width/height), so an absent extent
        # previously surfaced as a bare int(None) TypeError; the error must
        # name the rect (or say "rect" for anonymous artwork) and the
        # attribute.
        for rect, rect_id in (
            ('<rect id="face" x="0" y="0" height="1" fill="#111111"/>', "face"),
            ('<rect x="0" y="0" height="1" fill="#111111"/>', None),
        ):
            with self.subTest(rect=rect):
                tree = _svg_tree(f'<g id="g">{rect}</g>')
                message = error_message(self, ValueError, render_slices, tree)
                self.assertIn("'width'", message)
                if rect_id is None:
                    self.assertIn("rect has no 'width'", message)
                else:
                    self.assertIn("'face'", message)

    def test_non_positive_extent_is_rejected(self):
        # range(0) and range(-1) paint nothing, so a zero or negative width or
        # height silently drops pixels and weakens every pixel assertion built
        # on render_slices; reject it, naming the rect, attribute and value.
        for attr, value in (("width", "0"), ("height", "-1")):
            with self.subTest(attr=attr, value=value):
                other = "height" if attr == "width" else "width"
                tree = _svg_tree(
                    f'<g id="g"><rect id="face" x="0" y="0" {other}="1" '
                    f'{attr}="{value}" fill="#111111"/></g>'
                )
                message = error_message(self, ValueError, render_slices, tree)
                self.assertIn("'face'", message)
                self.assertIn(f"'{attr}'", message)
                self.assertIn(f"'{value}'", message)

    def test_non_integer_offset_names_the_rect(self):
        # An SVG rect's x/y default to 0, but a present non-integer one is
        # malformed; name the rect rather than surfacing a bare int() error.
        tree = _svg_tree(
            '<g id="g">'
            '<rect id="face" x="nope" y="0" width="1" height="1" '
            'fill="#111111"/>'
            "</g>"
        )
        message = error_message(self, ValueError, render_slices, tree)
        self.assertIn("'face'", message)
        self.assertIn("'x'", message)
        self.assertIn("'nope'", message)


class TestPixelMap(unittest.TestCase):
    def test_builds_a_row_major_map(self):
        # Positive control: width decides the row length and height is honoured
        # as the number of rows, so the map has the shape the caller declared.
        self.assertEqual(
            pixel_map(("#111111", "#222222", "#333333", "#444444"), 2, 2),
            {
                (0, 0): "#111111",
                (1, 0): "#222222",
                (0, 1): "#333333",
                (1, 1): "#444444",
            },
        )

    def test_wrong_colour_count_names_the_shape(self):
        # The comprehension lays out rows from width alone, so height is inert
        # without this check: three colours declared as a 2x2 map would yield a
        # 2x2 map missing its last pixel instead of an error. Name the count
        # and the shape that was declared.
        for colours in (("#111111",) * 3, ("#111111",) * 5):
            with self.subTest(colours=len(colours)):
                message = error_message(
                    self, ValueError, pixel_map, colours, 2, 2
                )
                self.assertIn(str(len(colours)), message)
                self.assertIn("2x2", message)
                self.assertIn("4", message)

    def test_non_positive_dimension_is_rejected(self):
        # width=0 would divide by zero in the comprehension and a negative one
        # would fold every index into a nonsense coordinate; reject both by
        # name instead of surfacing a bare ZeroDivisionError.
        for name, width, height in (
            ("width", 0, 2),
            ("width", -1, 2),
            ("height", 2, 0),
            ("height", 2, -1),
        ):
            with self.subTest(name=name):
                message = error_message(
                    self, ValueError, pixel_map, (), width, height
                )
                self.assertIn(name, message)

    def test_non_integer_dimension_is_rejected(self):
        # bool is an int subclass, so True would pass an isinstance check as 1;
        # require a genuine integer and name the offending dimension.
        for name, width, height in (
            ("width", "2", 2),
            ("width", True, 2),
            ("height", 2, "2"),
            ("height", 2, True),
        ):
            with self.subTest(name=name):
                self.assertIn(
                    name,
                    error_message(self, ValueError, pixel_map, (), width, height),
                )


class _NoSubTest(unittest.TestCase):
    """A real TestCase whose ``subTest`` is a no-op frame.

    The structural guards report a bad slice through ``case.subTest``;
    unittest records a subTest failure on the result and keeps going rather
    than raising, so an ``assertRaises`` around the guard would never see it.
    Dropping the subTest frame keeps the real ``assertEqual`` (which raises)
    so the guard's failure is observable here.
    """

    def subTest(self, **kwargs):
        return contextlib.nullcontext()


class TestStructuralGuards(unittest.TestCase):
    def test_tiles_placed_by_margins_passes_a_correct_layout(self):
        assert_tiles_placed_by_margins(self, _nine_slice_tree(), [""])

    def test_tiles_placed_by_margins_catches_a_misplaced_group(self):
        origins = dict(_ORIGINS)
        origins["top"] = (0, 0)
        with self.assertRaises(AssertionError):
            assert_tiles_placed_by_margins(
                _NoSubTest(), _nine_slice_tree(origins=origins), [""]
            )

    def test_slices_within_their_tiles_passes_a_correct_layout(self):
        assert_slices_stay_within_their_tiles(self, _nine_slice_tree(), [""])

    def test_slices_within_their_tiles_catches_an_oversized_rect(self):
        # A rect one pixel wider than its tile spills into the neighbouring
        # canvas region, which KSvg samples into that tile; the guard must
        # report the overflow instead of silently accepting it.
        with self.assertRaises(AssertionError):
            assert_slices_stay_within_their_tiles(
                _NoSubTest(), _nine_slice_tree(sizes={"top": (5, 4)}), [""]
            )

    def test_hint_geometry_passes_a_correct_layout(self):
        assert_hint_geometry(self, _svg_tree(_HINTS), [""], 4, 4)

    def test_hint_geometry_merges_extra_hints(self):
        # An SVG may declare hints beyond the nine-slice layout (an inset
        # band, a track size); those must be checked too, not ignored.
        extra = {"hint-extra": ("0", "0", "12", "12")}
        assert_hint_geometry(
            self,
            _svg_tree(
                _HINTS
                + '<rect id="hint-extra" x="0" y="0" width="12" height="12"/>'
            ),
            [""],
            4,
            4,
            extra,
        )

    def test_hint_geometry_catches_a_moved_hint(self):
        moved = _HINTS.replace(
            'x="4" y="0" width="4" height="4"',
            'x="5" y="0" width="4" height="4"',
        )
        with self.assertRaises(AssertionError):
            assert_hint_geometry(self, _svg_tree(moved), [""], 4, 4)


def _id_tree(prefixes=("",), omit=()):
    """Build a minimal SVG carrying every id `assert_slice_ids_present` reads.

    Each prefix contributes the nine slice ids and four margin hints, joined by
    the same separator the helper uses; the shared ``hint-tile-center`` is
    added once. *omit* names ids to leave out, so a caller can assert the guard
    reports a missing one. The elements are bare rects because the helper reads
    only the ``id`` attribute.
    """
    ids = []
    for prefix in prefixes:
        sep = "-" if prefix else ""
        ids.extend(f"{prefix}{sep}{name}" for name in SLICE_IDS)
        ids.extend(
            f"{prefix}{sep}hint-{side}-margin"
            for side in ("top", "bottom", "left", "right")
        )
    ids.append("hint-tile-center")
    body = "".join(
        f'<rect id="{name}"/>' for name in ids if name not in omit
    )
    return _svg_tree(body)


class TestSliceIdsPresent(unittest.TestCase):
    def test_passes_a_tree_with_every_slice_and_margin_id(self):
        assert_slice_ids_present(self, _id_tree(), [""])

    def test_passes_prefixed_ids_joined_by_the_separator(self):
        assert_slice_ids_present(
            self, _id_tree(("plain", "raised")), ["plain", "raised"]
        )

    def test_catches_each_missing_slice_id(self):
        for name in SLICE_IDS:
            with self.subTest(name=name):
                with self.assertRaises(AssertionError):
                    assert_slice_ids_present(self, _id_tree(omit=(name,)), [""])

    def test_catches_each_missing_margin_hint(self):
        for side in ("top", "bottom", "left", "right"):
            with self.subTest(side=side):
                with self.assertRaises(AssertionError):
                    assert_slice_ids_present(
                        self, _id_tree(omit=(f"hint-{side}-margin",)), [""]
                    )

    def test_catches_a_missing_tile_centre(self):
        with self.assertRaises(AssertionError):
            assert_slice_ids_present(
                self, _id_tree(omit=("hint-tile-center",)), [""]
            )

    def test_catches_a_missing_id_in_a_later_prefix(self):
        # A guard that only checks the first prefix would pass the two-prefix
        # positive control; the missing id is in the second state.
        with self.assertRaises(AssertionError):
            assert_slice_ids_present(
                self,
                _id_tree(("plain", "raised"), omit=("raised-top",)),
                ["plain", "raised"],
            )


class TestGroupsWithId(unittest.TestCase):
    def _tree(self, body):
        return _svg_tree(body)

    def test_yields_only_id_bearing_groups(self):
        # The documented filter: an id-bearing <rect>, <path> or <circle> must
        # not be yielded -- render_slices and tile_origins composite whole
        # groups and would misread a bare shape as one. An id-less <g> is not
        # a slice either.
        tree = self._tree(
            '<g id="top"><rect/></g>'
            '<g><rect id="unused"/></g>'
            '<rect id="center"/>'
            '<path id="edge"/>'
            '<circle id="dot"/>'
        )
        self.assertEqual([g.get("id") for g in groups_with_id(tree)], ["top"])

    def test_yields_every_group_in_document_order(self):
        tree = self._tree(
            '<g id="a"/>'
            '<g id="b"><g id="b-inner"/></g>'
            '<g id="c"/>'
        )
        self.assertEqual(
            [g.get("id") for g in groups_with_id(tree)],
            ["a", "b", "b-inner", "c"],
        )

    def test_yields_the_group_element_itself(self):
        # Callers read the group's id and its child rects, so the yielded
        # object must be the <g>, not a copy or a wrapper.
        tree = self._tree('<g id="top"><rect fill="#000000"/></g>')
        group = next(iter(groups_with_id(tree)))
        self.assertEqual(group.get("id"), "top")
        self.assertEqual(group[0].get("fill"), "#000000")

    def test_yields_nothing_when_no_group_has_an_id(self):
        tree = self._tree('<rect id="center"/><g><rect id="x"/></g>')
        self.assertEqual(list(groups_with_id(tree)), [])


class TestAttributeValues(unittest.TestCase):
    def _tree(self, body):
        return _svg_tree(body)

    def test_collects_values_from_every_descendant(self):
        # The ids sit at different depths -- a root child, a nested group and
        # a rect under a nested group -- so a helper that scanned only the
        # root's children would miss the deeper ones.
        tree = self._tree(
            '<rect id="top"/>'
            '<g id="group"><rect id="nested"/>'
            '<g><path id="deep"/></g></g>'
        )
        self.assertEqual(
            attribute_values(tree, "id"),
            {"top", "group", "nested", "deep"},
        )

    def test_omits_elements_that_lack_the_attribute(self):
        # An element without `fill` contributes nothing: the set must not hold
        # None, which would make every widget's fill assertion fail.
        tree = self._tree(
            '<rect fill="#000000"/><rect/><g><path fill="#FFFFFF"/></g>'
        )
        self.assertEqual(
            attribute_values(tree, "fill"), {"#000000", "#FFFFFF"}
        )

    def test_deduplicates_repeated_values(self):
        tree = self._tree(
            '<rect fill="#000000"/><rect fill="#000000"/>'
        )
        self.assertEqual(attribute_values(tree, "fill"), {"#000000"})

    def test_returns_an_empty_set_when_no_element_has_the_attribute(self):
        tree = self._tree('<rect id="center"/><g id="top"/>')
        self.assertEqual(attribute_values(tree, "stroke"), set())


class TestChildrenNamed(unittest.TestCase):
    def _first_child(self, body):
        return _svg_tree(body).getroot()[0]

    def test_returns_only_the_direct_children_with_the_tag(self):
        # A rect nested inside a child <g> is a grandchild, not a child: the
        # helper reads a group's own shapes and must not descend into nested
        # groups, or a widget would read another slice's rect.
        group = self._first_child(
            '<g id="top">'
            '<rect id="direct-1"/>'
            '<path id="direct-2"/>'
            '<g id="inner"><rect id="grandchild"/></g>'
            "</g>"
        )
        self.assertEqual(
            [r.get("id") for r in children_named(group, "rect")],
            ["direct-1"],
        )

    def test_matches_the_local_name_of_a_namespaced_element(self):
        # ElementTree reports the tag as `{namespace}rect`; the helper must
        # match on the local name or every widget test would see no shapes.
        group = self._first_child('<g id="top"><rect id="r"/></g>')
        self.assertEqual(
            [c.get("id") for c in children_named(group, "rect")], ["r"]
        )

    def test_returns_empty_when_only_descendants_match(self):
        group = self._first_child(
            '<g id="top"><g id="inner"><rect id="grandchild"/></g></g>'
        )
        self.assertEqual(children_named(group, "rect"), [])


class TestElementsById(unittest.TestCase):
    def _tree(self, body):
        return _svg_tree(body)

    def test_keeps_elements_that_are_not_groups(self):
        # Unlike groups_with_id, this map must keep a <circle> or <path>:
        # radiobutton reads its selection dot and checkmarks their glyphs by
        # id, and both are non-<g> elements.
        tree = self._tree(
            '<g id="top"><rect id="r"/></g>'
            '<circle id="dot"/><path id="glyph"/>'
        )
        self.assertEqual(
            sorted(elements_by_id(tree)), ["dot", "glyph", "r", "top"]
        )

    def test_maps_each_id_to_its_element(self):
        # Callers read the element's own attributes, so the value must be the
        # parsed element, not a copy or its id string.
        tree = self._tree('<circle id="dot" r="3"/>')
        self.assertEqual(elements_by_id(tree)["dot"].get("r"), "3")

    def test_later_element_wins_when_an_id_repeats(self):
        # The docstring promises later-in-document order wins; pin it so a
        # future rewrite cannot silently flip which duplicate a widget reads.
        tree = self._tree(
            '<rect id="dup" fill="#000000"/>'
            '<rect id="dup" fill="#FFFFFF"/>'
        )
        self.assertEqual(elements_by_id(tree)["dup"].get("fill"), "#FFFFFF")

    def test_omits_elements_without_an_id(self):
        # An id-less element must contribute no key -- not even None -- or
        # callers looking up a real id could collide with it.
        tree = self._tree('<rect/><g><path id="glyph"/></g>')
        self.assertEqual(sorted(elements_by_id(tree)), ["glyph"])

    def test_returns_an_empty_map_when_no_element_has_an_id(self):
        tree = self._tree('<rect/><g><path/></g>')
        self.assertEqual(elements_by_id(tree), {})


class TestLocalName(unittest.TestCase):
    def test_strips_the_svg_namespace_prefix(self):
        # Every shipped SVG declares the default SVG namespace, so ElementTree
        # reports each tag as `{namespace}local`; the helper must return the
        # local part, which is what every widget test matches on.
        root = ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg"><g id="g"/></svg>'
        )
        self.assertEqual(local_name(root), "svg")
        self.assertEqual(local_name(root[0]), "g")

    def test_returns_an_unprefixed_tag_unchanged(self):
        # A tree parsed without an xmlns has no `{namespace}` prefix at all.
        # The widget tests never build one, so a helper that sliced a fixed
        # prefix (or assumed a `}` is always present) would pass them while
        # corrupting every unprefixed tag; pin the bare tag here.
        root = ET.fromstring("<svg><rect id=\"r\"/></svg>")
        self.assertEqual(local_name(root), "svg")
        self.assertEqual(local_name(root[0]), "rect")

    def test_strips_a_namespace_that_is_not_svg(self):
        # The prefix is the element's own namespace, not a hardcoded SVG one;
        # a foreign-namespaced element must still reduce to its local name.
        element = ET.Element("{http://example.test/ns}widget")
        self.assertEqual(local_name(element), "widget")


class TestNoScriptElements(unittest.TestCase):
    def test_passes_a_tree_without_a_script(self):
        tree = _svg_tree('<rect id="center"/>')
        assert_no_script_elements(self, tree)

    def test_catches_a_script_after_another_element(self):
        tree = _svg_tree(
            '<rect id="center"/><script>alert(1)</script>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)

    def test_catches_a_script_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<g id="top"><g><script>alert(1)</script></g></g>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)


class TestUniqueIds(unittest.TestCase):
    def test_passes_a_tree_with_unique_ids(self):
        tree = _svg_tree(
            '<rect id="center"/><g id="top"><rect id="top-body"/></g>'
        )
        assert_unique_ids(self, tree)

    def test_passes_a_tree_whose_elements_have_no_ids(self):
        tree = _svg_tree("<rect/>")
        assert_unique_ids(self, tree)

    def test_catches_a_duplicate_id_naming_it(self):
        tree = _svg_tree('<rect id="center"/><rect id="center"/>')
        self.assertIn(
            "center",
            error_message(
                self, AssertionError, assert_unique_ids, self, tree
            ),
        )

    def test_catches_a_duplicate_id_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<rect id="center"/><g><rect id="center"/></g>'
        )
        self.assertIn(
            "center",
            error_message(
                self, AssertionError, assert_unique_ids, self, tree
            ),
        )


# Two margin rects whose far edges reach a 12x12 canvas. `assert_root_canvas`
# only inspects the right/bottom margin rects, so this minimal tree exercises
# the canvas tie without the full nine-slice layout.
_ROOT_CANVAS_HINTS = (
    '<rect id="hint-right-margin" x="8" y="4" width="4" height="4"/>'
    '<rect id="hint-bottom-margin" x="4" y="8" width="4" height="4"/>'
)


def _root_canvas_tree(viewbox="0 0 12 12", width="12", height="12",
                      hints=_ROOT_CANVAS_HINTS):
    """Build a minimal root <svg> for `assert_root_canvas` to inspect.

    The two margin rects reach the 12x12 canvas edge; *viewbox*, *width*,
    *height* and *hints* each let a caller break one declared value at a time.
    """
    return _svg_tree(
        hints, width=width, height=height, viewBox=viewbox
    )


class TestRootCanvas(unittest.TestCase):
    def test_passes_a_1_to_1_canvas_with_margins_at_the_edge(self):
        # Positive control: viewBox/width/height agree and each margin rect's
        # far edge is the canvas edge, so the guard must accept the tree.
        assert_root_canvas(self, _root_canvas_tree(), 12, 12)

    def test_rejects_a_root_that_is_not_svg(self):
        # KSvg draws from the root element, so a tree whose root is not <svg>
        # declares no canvas to lay the artwork out in; the guard must reject
        # it rather than read a viewBox off an unrelated element.
        tree = ET.ElementTree(
            ET.fromstring(
                '<g xmlns="http://www.w3.org/2000/svg" width="12" '
                'height="12" viewBox="0 0 12 12"/>'
            )
        )
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, tree, 12, 12)

    def test_rejects_a_viewbox_that_disagrees_with_the_canvas(self):
        # A viewBox narrower than the declared width rescales the whole widget
        # horizontally while every per-element coordinate test still passes.
        with self.assertRaises(AssertionError):
            assert_root_canvas(
                self, _root_canvas_tree(viewbox="0 0 11 12"), 12, 12
            )

    def test_rejects_a_width_that_disagrees_with_the_viewbox(self):
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, _root_canvas_tree(width="11"), 12, 12)

    def test_rejects_a_height_that_disagrees_with_the_viewbox(self):
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, _root_canvas_tree(height="11"), 12, 12)

    def test_rejects_a_right_margin_that_stops_short_of_the_canvas(self):
        # A right-margin rect one pixel short leaves the right border short of
        # the canvas edge, so KSvg samples the wrong region into that tile.
        hints = (
            '<rect id="hint-right-margin" x="7" y="4" width="4" height="4"/>'
            '<rect id="hint-bottom-margin" x="4" y="8" width="4" height="4"/>'
        )
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, _root_canvas_tree(hints=hints), 12, 12)

    def test_rejects_a_bottom_margin_that_stops_short_of_the_canvas(self):
        hints = (
            '<rect id="hint-right-margin" x="8" y="4" width="4" height="4"/>'
            '<rect id="hint-bottom-margin" x="4" y="7" width="4" height="4"/>'
        )
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, _root_canvas_tree(hints=hints), 12, 12)


# A distinct three-colour band for the pixel-assertion tests, so a reversed
# band cannot be confused with the artwork's real bevel colours.
_EDGE_BAND = ("#AA0000", "#00BB00", "#0000CC")


def _horizontal_band(band, size):
    """A *size* x 3 map: three rows, one band colour across each whole row."""
    return pixel_map(
        (band[0],) * size + (band[1],) * size + (band[2],) * size,
        size,
        3,
    )


def _vertical_band(band, size):
    """A 3 x *size* map: three columns, one band colour down each column."""
    return pixel_map(band * size, 3, size)


def _bevel_slices(outward, mirrored, size, prefix=""):
    """Build the four edge slices `assert_edge_bevels` reads for *prefix*.

    The top/left edges paint *outward* and the bottom/right paint *mirrored*,
    matching the helper's own mirroring rule.
    """
    sep = "-" if prefix else ""
    return {
        f"{prefix}{sep}top": _horizontal_band(outward, size),
        f"{prefix}{sep}bottom": _horizontal_band(mirrored, size),
        f"{prefix}{sep}left": _vertical_band(outward, size),
        f"{prefix}{sep}right": _vertical_band(mirrored, size),
    }


def _face_slices(face, bevel, size, prefix=""):
    """Build a nine-slice that `assert_face_bevel` accepts for *prefix*.

    The edges come from `face_edge_bands` and the corners from
    `face_corners`, so a failure here means the helper's wiring changed, not
    the pinned corner table (which the widget tests pin against artwork).
    """
    sep = "-" if prefix else ""
    outward, mirrored = face_edge_bands(face, bevel)
    slices = _bevel_slices(outward, mirrored, size, prefix)
    slices[f"{prefix}{sep}center"] = pixel_map(
        (face,) * (size * size), size, size
    )
    for name, colours in face_corners(face, bevel).items():
        slices[f"{prefix}{sep}{name}"] = pixel_map(colours, 3, 3)
    return slices


class TestPixelAssertions(unittest.TestCase):
    """Direct pass/fail tests for the pixel-comparison assertion helpers.

    Each widget test reaches these only over its own current artwork, so a
    helper that mis-orders a band, mirrors the wrong sides or drops the size
    check could still pass every widget test. These pin the helpers on maps
    built independently of the artwork, and prove each can fail.
    """

    def test_slice_pixels_pins_the_full_map(self):
        expected = pixel_map(("#FFFFFF",) * 4, 2, 2)
        slices = {"center": pixel_map(("#FFFFFF",) * 4, 2, 2)}
        assert_slice_pixels(self, slices, "center", expected)
        # An extra pixel outside the 2x2 body must fail: a full-map compare
        # catches a resized or shifted slice that a colour check would miss.
        slices["center"][(2, 2)] = "#FFFFFF"
        with self.assertRaises(AssertionError):
            assert_slice_pixels(_NoSubTest(), slices, "center", expected)

    def test_edge_band_pixels_pins_a_top_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"top": _horizontal_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "top", "top", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        with self.assertRaises(AssertionError):
            assert_edge_band_pixels(
                _NoSubTest(), slices, "top", "top", mirrored, size
            )

    def test_edge_band_pixels_pins_a_left_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"left": _vertical_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "left", "left", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        with self.assertRaises(AssertionError):
            assert_edge_band_pixels(
                _NoSubTest(), slices, "left", "left", mirrored, size
            )

    def test_edge_bevels_supplies_the_bottom_and_right_mirror(self):
        size = 6
        outward = ("#000000", "#FFFFFF", "#DDDDDD")
        mirrored = ("#DDDDDD", "#999999", "#000000")
        assert_edge_bevels(
            self, _bevel_slices(outward, mirrored, size), "", outward,
            mirrored, size,
        )
        # `assert_edge_bevels`, not the caller, supplies the mirroring, and
        # each edge is read on its own. Break only the bottom, then only the
        # right, then only the left, so a helper that skips an edge (say its
        # loop ends `("top", "bottom", "bottom", "right")` or
        # `("top", "bottom", "left", "left")`) still fails.
        broken_bottom = _bevel_slices(outward, mirrored, size)
        broken_bottom["bottom"] = _horizontal_band(outward, size)
        with self.assertRaises(AssertionError):
            assert_edge_bevels(
                _NoSubTest(), broken_bottom, "", outward, mirrored, size
            )

        broken_left = _bevel_slices(outward, mirrored, size)
        broken_left["left"] = _vertical_band(mirrored, size)
        with self.assertRaises(AssertionError):
            assert_edge_bevels(
                _NoSubTest(), broken_left, "", outward, mirrored, size
            )

        broken_right = _bevel_slices(outward, mirrored, size)
        broken_right["right"] = _vertical_band(outward, size)
        with self.assertRaises(AssertionError):
            assert_edge_bevels(
                _NoSubTest(), broken_right, "", outward, mirrored, size
            )

    def test_edge_bevels_names_each_slice_by_prefix(self):
        size = 6
        outward = ("#000000", "#FFFFFF", "#DDDDDD")
        mirrored = ("#DDDDDD", "#999999", "#000000")
        slices = _bevel_slices(outward, mirrored, size, prefix="normal")
        assert_edge_bevels(self, slices, "normal", outward, mirrored, size)

    def test_corner_pixels_pins_all_nine_pixels(self):
        # Nine distinct colours: no pixel can stand in for another, so a
        # helper that reads only some of the nine (or only the diagonal) is
        # not saved by a repeated colour.
        colours = (
            "#000001", "#000002", "#000003",
            "#000004", "#000005", "#000006",
            "#000007", "#000008", "#000009",
        )
        slices = {"topleft": pixel_map(colours, 3, 3)}
        assert_corner_pixels(self, slices, "topleft", colours)
        # Break one pixel at a time; each must be noticed on its own.
        for index in range(9):
            broken = list(colours)
            broken[index] = "#FFFFFF"
            with self.assertRaises(AssertionError):
                assert_corner_pixels(
                    _NoSubTest(),
                    {"topleft": pixel_map(tuple(broken), 3, 3)},
                    "topleft",
                    colours,
                )

    def test_face_corners_names_each_slice_by_prefix(self):
        colours = ("#000001",) * 9
        corners = {"topleft": colours}
        slices = {"state-topleft": pixel_map(colours, 3, 3)}
        assert_face_corners(self, slices, "state", corners)
        # The prefix names the slice: the table's only entry is stored under
        # the prefixed key, so a helper that dropped or doubled the prefix
        # would not find it. A wrong pixel must also fail.
        broken = {"state-topleft": pixel_map(("#FFFFFF",) * 9, 3, 3)}
        with self.assertRaises(AssertionError):
            assert_face_corners(_NoSubTest(), broken, "state", corners)

    def test_center_tile_is_pins_the_full_square_and_its_size(self):
        colour = "#DDDDDD"
        slices = {"center": pixel_map((colour,) * 36, 6, 6)}
        assert_center_tile_is(self, slices, "center", colour, 6)
        # A 7x7 centre has the right colour everywhere but the wrong tile
        # size, which the declared-size pin must reject.
        bigger = {"center": pixel_map((colour,) * 49, 7, 7)}
        with self.assertRaises(AssertionError):
            assert_center_tile_is(_NoSubTest(), bigger, "center", colour, 6)

    def test_face_bevel_pins_centre_edges_and_corners(self):
        size = 10
        # Raised #DDDDDD (the scroll-bar thumb and dialog body) and flat
        # #EEEEEE (the scroll-bar trough) exercise both corner-table paths.
        for face, bevel in (("#DDDDDD", "raised"), ("#EEEEEE", "flat")):
            with self.subTest(face=face, bevel=bevel):
                assert_face_bevel(
                    self, _face_slices(face, bevel, size), "", face, bevel,
                    size=size,
                )
                assert_face_bevel(
                    self, _face_slices(face, bevel, size, prefix="state"),
                    "state", face, bevel, size=size,
                )
                # Each component assertion can fail on its own: the centre
                # tile, an edge band, and a corner slice. Break one at a time
                # so a helper that checked only the centre would not pass.
                broken_center = _face_slices(face, bevel, size)
                broken_center["center"] = pixel_map(
                    ("#CCCCCC",) * (size * size), size, size
                )
                with self.assertRaises(AssertionError):
                    assert_face_bevel(
                        _NoSubTest(), broken_center, "", face, bevel,
                        size=size,
                    )

                _, mirrored = face_edge_bands(face, bevel)
                broken_edge = _face_slices(face, bevel, size)
                broken_edge["top"] = _horizontal_band(mirrored, size)
                with self.assertRaises(AssertionError):
                    assert_face_bevel(
                        _NoSubTest(), broken_edge, "", face, bevel,
                        size=size,
                    )

                broken_corner = _face_slices(face, bevel, size)
                broken_corner["topleft"] = pixel_map(("#FFFFFF",) * 9, 3, 3)
                with self.assertRaises(AssertionError):
                    assert_face_bevel(
                        _NoSubTest(), broken_corner, "", face, bevel,
                        size=size,
                    )


if __name__ == "__main__":
    unittest.main()
