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
    path_arcs,
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
