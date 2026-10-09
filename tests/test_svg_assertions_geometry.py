"""Direct tests for tests/svg_assertions.py's geometry helpers.

The helpers that turn artwork markup into geometry -- ``path_arcs`` /
``arc_center``, ``rect_geometry`` / ``circle_geometry``, the nine-slice margin,
hint and tile sizes, the group origins, face edge bands and face corner
tables -- feed every widget test's pixel assertions, so a mis-parse here
would weaken them all at once.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from error_assertions import error_message
from svg_assertions import (
    RAISED_FACE_CORNERS,
    arc_center,
    circle_geometry,
    face_corners,
    face_edge_bands,
    flat_face_corners,
    nine_slice_hint_geometry,
    nine_slice_margins,
    nine_slice_tile_sizes,
    path_arcs,
    rect_geometry,
    sunken_face_corners,
    tile_origins,
)
from svg_fixtures import _svg_tree


def _face_substituted(table, face):
    """Return *table* with each #DDDDDD face pixel replaced by *face*.

    The sunken and flat corner tables are parameterised by the face colour,
    so a test that pins the #DDDDDD table can derive the expected table for
    another face by swapping only the face pixels.
    """
    return {
        name: tuple(
            face if colour == "#DDDDDD" else colour for colour in pixels
        )
        for name, pixels in table.items()
    }


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
            _face_substituted(sunken, "#FFFFFF"),
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
            _face_substituted(flat, "#EEEEEE"),
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
