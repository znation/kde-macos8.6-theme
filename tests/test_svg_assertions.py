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

from svg_assertions import (
    arc_center,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    circle_geometry,
    nine_slice_hint_geometry,
    nine_slice_margins,
    path_arcs,
    rect_geometry,
    render_slices,
    tile_origins,
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
    return ET.ElementTree(
        ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" '
            f'viewBox="0 0 12 12">{_HINTS}{groups}</svg>'
        )
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
                with self.assertRaises(ValueError) as caught:
                    list(path_arcs(d))
                self.assertIn(
                    "unsupported SVG path command", str(caught.exception)
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
                with self.assertRaises(ValueError) as caught:
                    list(path_arcs(d))
                message = str(caught.exception)
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
        with self.assertRaises(ValueError) as caught:
            arc_center((2.0, 2.0), (3, 3, 0, 1), (2.0, 2.0))
        message = str(caught.exception)
        self.assertIn("(2.0, 2.0)", message)
        self.assertIn("zero-length chord", message)

    def test_radius_too_small_names_the_arc_and_the_chord(self):
        # Endpoints 6 apart need radius >= 3; a radius of 2 cannot reach both
        # and the square root would fail with "math domain error".
        with self.assertRaises(ValueError) as caught:
            arc_center((0.0, 0.0), (2, 2, 0, 1), (6.0, 0.0))
        message = str(caught.exception)
        self.assertIn("(0.0, 0.0)", message)
        self.assertIn("(6.0, 0.0)", message)
        self.assertIn("radius 2", message)
        self.assertIn("half its chord 3", message)


class TestTileOrigins(unittest.TestCase):
    def test_reads_translates_and_surfaces_unparseable_transforms(self):
        tree = ET.ElementTree(
            ET.fromstring(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<g id="moved" transform="translate(3, 4)"/>'
                '<g id="at-origin"/>'
                '<g id="unknown" transform="matrix(1,0,0,1,9,9)"/>'
                "</svg>"
            )
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
        with self.assertRaises(ValueError) as caught:
            circle_geometry(element)
        message = str(caught.exception)
        self.assertIn("symbol", message)
        self.assertIn("'cx'", message)

    def test_anonymous_missing_dimension_still_names_the_attribute(self):
        # The radiobutton face and checkmarks dot carry no id of their own, so
        # the diagnostic must still name the attribute when it cannot name the
        # element.
        element = ET.fromstring('<circle cy="8" r="3"/>')
        with self.assertRaises(ValueError) as caught:
            circle_geometry(element)
        self.assertIn("'cx'", str(caught.exception))


class TestRectGeometry(unittest.TestCase):
    def test_reads_the_four_dimensions_of_each_id_bearing_rect(self):
        # The layout guards and the per-widget hint tests read geometry
        # through this map, so a missing or reordered value would mispin the
        # nine-slice layout. Pin the order and that a rect without an id is
        # left out.
        tree = ET.ElementTree(
            ET.fromstring(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect id="a" x="1" y="2" width="3" height="4"/>'
                '<rect x="9" y="9" width="9" height="9"/>'
                "</svg>"
            )
        )
        self.assertEqual(rect_geometry(tree), {"a": ("1", "2", "3", "4")})

    def test_missing_dimension_names_the_rect_and_the_attribute(self):
        # ElementTree hands an absent attribute back as None, and the layout
        # guards convert each value with int(); the error must name the rect
        # and the attribute rather than surfacing as a bare TypeError.
        tree = ET.ElementTree(
            ET.fromstring(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect id="hint-top-margin" y="0" width="4" height="4"/>'
                "</svg>"
            )
        )
        with self.assertRaises(ValueError) as caught:
            rect_geometry(tree)
        message = str(caught.exception)
        self.assertIn("hint-top-margin", message)
        self.assertIn("'x'", message)


class TestRenderSlices(unittest.TestCase):
    def test_later_rects_paint_over_earlier_ones(self):
        # KSvg composites a tile's rects in document order, so an overlay's
        # colour must win; otherwise a bevel drawn under the face would read as
        # the face and a pixel test would pin the wrong layer.
        tree = ET.ElementTree(
            ET.fromstring(
                '<svg xmlns="http://www.w3.org/2000/svg"><g id="g">'
                '<rect x="0" y="0" width="2" height="1" fill="#111111"/>'
                '<rect x="1" y="0" width="1" height="1" fill="#222222"/>'
                "</g></svg>"
            )
        )
        self.assertEqual(
            render_slices(tree)["g"],
            {(0, 0): "#111111", (1, 0): "#222222"},
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


if __name__ == "__main__":
    unittest.main()
