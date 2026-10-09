"""Direct tests for tests/svg_assertions.py's slice-rendering helpers.

``render_slices`` composites a nine-slice SVG's rects into per-slice pixel
maps and ``pixel_map`` builds the same shape from a colour sequence; both feed
the pixel assertions, so each is pinned directly.
"""

from __future__ import annotations

import unittest

from error_assertions import error_message
from svg_assertions import pixel_map, render_slices
from svg_fixtures import _svg_tree


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
