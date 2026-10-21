"""Direct tests for ``svg_assertions.render``'s slice-rendering helpers.

``render_slices`` composites a nine-slice SVG's rects into per-slice pixel
maps, and ``pixel_map``, ``edge_map``, ``corner_map``, ``bevel_edge_maps`` and
``bevel_corner_maps`` build the same shape from colours; all feed the pixel
assertions, so each is pinned directly.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support.error_assertions import assert_error_names, error_message
from support.svg_fixtures import _svg_tree
from svg_assertions import (
    _MAX_RENDERED_PIXELS,
    bevel_corner_maps,
    bevel_edge_maps,
    corner_map,
    edge_map,
    pixel_map,
    render_slices,
)
from svg_assertions import render as render_module


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
                assert_error_names(
                    self,
                    ValueError,
                    render_slices,
                    tree,
                    needles=("'face'", f"'{attr}'", f"'{value}'"),
                )

    def test_non_integer_offset_names_the_rect(self):
        # An SVG rect's x/y default to 0, but a present non-integer one is
        # malformed; name the rect rather than surfacing a bare int() error.
        tree = _svg_tree(
            '<g id="g">'
            '<rect id="face" x="nope" y="0" width="1" height="1" '
            'fill="#111111"/>'
            "</g>"
        )
        assert_error_names(
            self,
            ValueError,
            render_slices,
            tree,
            needles=("'face'", "'x'", "'nope'"),
        )

    def test_rect_transform_is_rejected(self):
        # render_slices composites a tile's rects at their own x/y and never
        # applies a rect-level transform, so a transformed rect would be read
        # from its untransformed pixels and every pixel assertion built on it
        # would pin the wrong position. Reject it, naming the rect and value.
        tree = _svg_tree(
            '<g id="g">'
            '<rect id="face" x="0" y="0" width="1" height="1" '
            'transform="translate(2,0)" fill="#111111"/>'
            "</g>"
        )
        assert_error_names(
            self,
            ValueError,
            render_slices,
            tree,
            needles=("'face'", "translate(2,0)"),
        )

    def test_oversized_tile_is_refused_before_it_is_painted(self):
        # render_slices stores one entry per rect pixel, so a tiny
        # width/height pair is an amplification: a contributor-supplied SVG
        # with a huge rect would allocate until `make check` is OOM-killed.
        # A tile far larger than any real source rect must be refused by
        # name before any pixel is painted.
        tree = _svg_tree(
            '<g id="g"><rect id="face" x="0" y="0" width="300" '
            'height="300" fill="#111111"/></g>'
        )
        message = error_message(self, ValueError, render_slices, tree)
        self.assertIn("'face'", message)
        self.assertIn("300x300", message)

    def test_render_limit_is_cumulative_across_rects_and_inclusive(self):
        # The limit bounds the whole SVG, not each rect: many modest rects
        # must not add up past it. A total exactly at the limit still renders.
        self.assertEqual(_MAX_RENDERED_PIXELS, 256 * 256)
        half = _MAX_RENDERED_PIXELS // 2
        at_limit = (
            f'<rect x="0" y="0" width="{half}" height="1" fill="#111111"/>'
            f'<rect x="0" y="1" width="{half}" height="1" fill="#222222"/>'
        )
        pixels = render_slices(_svg_tree(f'<g id="g">{at_limit}</g>'))["g"]
        self.assertEqual(len(pixels), 2 * half)
        over = f'<g id="g">{at_limit}<rect id="extra" width="1" height="1"/></g>'
        message = error_message(self, ValueError, render_slices, _svg_tree(over))
        self.assertIn("'extra'", message)
        self.assertIn("1x1", message)


class TestRenderSlicesCache(unittest.TestCase):
    """One parsed tree renders once, and callers cannot corrupt the cache."""

    def test_reuses_the_rendered_slices_of_an_unchanged_tree(self):
        # A widget suite renders the same tree from its structure, pixel and
        # reference tests, so a second render must not repaint its rects.
        tree = _svg_tree(
            '<g id="g"><rect width="1" height="1" fill="#111111"/></g>'
        )
        with mock.patch.object(
            render_module, "_paint_rect", wraps=render_module._paint_rect
        ) as paint:
            first = render_slices(tree)
            second = render_slices(tree)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertEqual(paint.call_count, 1)

    def test_a_mutated_result_does_not_change_the_cached_slices(self):
        # The cache hands out fresh maps, so a caller that edits a result (as
        # the helper tests do) cannot make a later read see its edit.
        tree = _svg_tree(
            '<g id="g"><rect width="1" height="1" fill="#111111"/></g>'
        )
        first = render_slices(tree)
        first["g"][(0, 0)] = "#222222"
        first["g"].clear()
        second = render_slices(tree)
        self.assertEqual(second["g"], {(0, 0): "#111111"})


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
                assert_error_names(
                    self,
                    ValueError,
                    pixel_map,
                    colours,
                    2,
                    2,
                    needles=(str(len(colours)), "2x2", "4"),
                )

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



def _pixel_rows(*rows):
    """Return *rows* as a {(x, y): colour} map, row-major."""
    return {
        (x, y): colour
        for y, row in enumerate(rows)
        for x, colour in enumerate(row)
    }


class TestEdgeMap(unittest.TestCase):
    def test_places_outer_and_inner_on_each_side(self):
        outer, inner = "#111111", "#222222"
        expected = {
            "top": _pixel_rows((outer, outer, outer), (inner, inner, inner)),
            "bottom": _pixel_rows((inner, inner, inner), (outer, outer, outer)),
            "left": _pixel_rows((outer, inner), (outer, inner), (outer, inner)),
            "right": _pixel_rows((inner, outer), (inner, outer), (inner, outer)),
        }
        for side, pixels in expected.items():
            with self.subTest(side=side):
                self.assertEqual(edge_map(3, side, outer, inner), pixels)

    def test_rejects_an_unknown_side_naming_it(self):
        self.assertIn(
            "sideways",
            error_message(
                self, ValueError, edge_map, 2, "sideways", "#111111", "#222222"
            ),
        )


class TestCornerMap(unittest.TestCase):
    def test_builds_a_row_major_2x2_and_drops_unpainted_pixels(self):
        self.assertEqual(
            corner_map(("#111111", "#222222", "#333333", "#444444")),
            _pixel_rows(("#111111", "#222222"), ("#333333", "#444444")),
        )
        self.assertEqual(
            corner_map(("#111111", None, "#333333", None)),
            {(0, 0): "#111111", (0, 1): "#333333"},
        )


class TestBevelEdgeMaps(unittest.TestCase):
    def test_swaps_highlight_and_shadow_between_raised_and_sunken(self):
        outline, highlight, shadow = "#000000", "#FFFFFF", "#999999"
        raised = bevel_edge_maps(2, "raised", outline, highlight, shadow)
        self.assertEqual(
            raised,
            {
                "top": _pixel_rows((outline, outline), (highlight, highlight)),
                "bottom": _pixel_rows((shadow, shadow), (outline, outline)),
                "left": _pixel_rows((outline, highlight), (outline, highlight)),
                "right": _pixel_rows((shadow, outline), (shadow, outline)),
            },
        )
        sunken = bevel_edge_maps(2, "sunken", outline, highlight, shadow)
        self.assertEqual(
            sunken,
            {
                "top": _pixel_rows((outline, outline), (shadow, shadow)),
                "bottom": _pixel_rows((highlight, highlight), (outline, outline)),
                "left": _pixel_rows((outline, shadow), (outline, shadow)),
                "right": _pixel_rows((highlight, outline), (highlight, outline)),
            },
        )

    def test_rejects_an_unknown_or_untested_bevel(self):
        for bevel in ("bevelled", "flat", "sunken-outside"):
            with self.subTest(bevel=bevel):
                self.assertIn(
                    bevel,
                    error_message(
                        self, ValueError, bevel_edge_maps, 2, bevel,
                        "#000000", "#FFFFFF", "#999999",
                    ),
                )


class TestBevelCornerMaps(unittest.TestCase):
    def test_paints_the_turning_band_at_each_corner(self):
        outline, highlight, shadow = "#000000", "#FFFFFF", "#999999"
        raised = bevel_corner_maps("raised", outline, highlight, shadow)
        self.assertEqual(
            raised,
            {
                "topleft": _pixel_rows(
                    (outline, outline), (outline, highlight)
                ),
                "topright": _pixel_rows(
                    (outline, outline), (shadow, outline)
                ),
                "bottomleft": _pixel_rows(
                    (outline, highlight), (outline, outline)
                ),
                "bottomright": _pixel_rows(
                    (shadow, outline), (outline, outline)
                ),
            },
        )
        sunken = bevel_corner_maps("sunken", outline, highlight, shadow)
        self.assertEqual(
            sunken,
            {
                "topleft": _pixel_rows(
                    (outline, outline), (outline, shadow)
                ),
                "topright": _pixel_rows(
                    (outline, outline), (highlight, outline)
                ),
                "bottomleft": _pixel_rows(
                    (outline, shadow), (outline, outline)
                ),
                "bottomright": _pixel_rows(
                    (highlight, outline), (outline, outline)
                ),
            },
        )

    def test_rejects_an_unknown_or_untested_bevel(self):
        for bevel in ("bevelled", "flat", "sunken-outside"):
            with self.subTest(bevel=bevel):
                self.assertIn(
                    bevel,
                    error_message(
                        self, ValueError, bevel_corner_maps, bevel,
                        "#000000", "#FFFFFF", "#999999",
                    ),
                )
