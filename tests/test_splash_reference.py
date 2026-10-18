"""Tests for the splash artwork's colours and grid geometry against the reference.

These tie the QML's colour and rectangle literals and the logo SVG's fills back
to pixels and colour scans of ``macos8.6-screenshots/boot2_betawiki.png``, so a
literal that drifts from the reference fails here rather than only looking
wrong on screen.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from platinum_palette import hex_colour
from splash_fixtures import (
    LOGO,
    SplashReferenceCase,
    qml_border_width,
    qml_color,
    qml_rect,
)

from svg_assertions import attribute_values  # noqa: E402

# The exact reference pixels the QML colours are pinned to. (74,60) is the
# #DDDDDD bevel and (78,60) the #BFBFBF rule that bounds the white face at
# (100,60); (120,100) is the #ADADAD unfilled track of the progress well and
# (102,100) the #9B9BEA lavender fill at its left end.
FIELD = (99, 99, 156)
PANEL_BEVEL = (221, 221, 221)
PANEL_RULE = (191, 191, 191)
TRACK = (173, 173, 173)
FILL = (155, 155, 234)

# The logo is the only blue region inside the panel's white face; the progress
# well is the only region darker than #C8C8C8 in the rows below the "Starting
# Up" text (y=94..97) and above the panel's lower bevel.
LOGO_FACE = (range(80, 160), range(39, 89))
TRACK_BAND = (range(80, 160), range(98, 105))


def _field_like(rgb):
    """True for the reference's dithered #63639C field.

    The thumbnail is a downscaled frame, so the field is not one exact colour:
    it dithers with ``b - r`` in 44..61 around r=99, and the four rounded-corner
    pixels are (49,49,77). This predicate accepts those and no panel, logo or
    progress-bar pixel.
    """
    r, g, b = rgb
    return abs(r - g) <= 6 and 20 <= b - r <= 80 and r <= 130 and g <= 130


def _rect(points):
    """Return ``(x, y, width, height)`` for an iterable of ``(x, y)`` points."""
    points = list(points)
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    return (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


def _contains(rect, x, y):
    """True when ``(x, y)`` is inside the half-open grid rect ``(x, y, w, h)``."""
    rx, ry, width, height = rect
    return rx <= x < rx + width and ry <= y < ry + height


class TestSplashReference(SplashReferenceCase):
    def test_field_colour_matches_reference(self):
        # The field is one flat #63639C, unlike the dithered panel edge: pin
        # both a corner and the opposite quadrant to the QML's literal.
        self.assertEqual(self.pixel(5, 5), FIELD)
        self.assertEqual(self.pixel(200, 150), FIELD)
        self.assertEqual(FIELD, (0x63, 0x63, 0x9C))
        self.assertEqual(qml_color("fieldColor"), "#63639C")

    def test_panel_colours_match_reference(self):
        # The panel's white face, #BFBFBF rule and #DDDDDD bevel are the greys
        # the QML names; the sample points are on the panel's left edge, clear
        # of the logo and wordmark.
        self.assertEqual(self.pixel(74, 60), PANEL_BEVEL)
        self.assertEqual(self.pixel(78, 60), PANEL_RULE)
        self.assertEqual(self.pixel(100, 60), (255, 255, 255))
        self.assertEqual(qml_color("panelBevelColor"), "#DDDDDD")
        self.assertEqual(qml_color("panelRuleColor"), "#BFBFBF")
        self.assertEqual(qml_color("panelColor"), "#FFFFFF")

    def test_wordmark_colour_matches_reference(self):
        # The "Mac OS" wordmark is the only pure black inside the panel face;
        # (97,73) is one of its glyph pixels.
        self.assertEqual(self.pixel(97, 73), (0, 0, 0))
        self.assertEqual(qml_color("wordmarkColor"), "#000000")

    def test_progress_colours_match_reference(self):
        # (120,100) is the #ADADAD unfilled track of the progress well;
        # (102,100) is the #9B9BEA lavender fill at the well's left end.
        self.assertEqual(self.pixel(120, 100), TRACK)
        self.assertEqual(self.pixel(102, 100), FILL)
        self.assertEqual(qml_color("trackColor"), "#ADADAD")
        self.assertEqual(qml_color("fillColor"), "#9B9BEA")

    def test_logo_colours_match_reference(self):
        # The logo SVG's two fills are the blues of the reference's logo
        # rectangle. (107, 48) is an exact #7286D6 highlight pixel and
        # (111, 48) an exact #4C65CB face pixel; pin each fill to the pixel it
        # was sampled from, so a fill that drifts from the reference fails
        # here instead of only looking wrong on screen.
        highlight = self.pixel(107, 48)
        face = self.pixel(111, 48)
        self.assertEqual(highlight, (114, 134, 214))
        self.assertEqual(face, (76, 101, 203))
        self.assertEqual(
            attribute_values(ET.parse(LOGO), "fill"),
            {hex_colour(highlight), hex_colour(face)},
        )


class TestSplashGeometry(SplashReferenceCase):
    def test_grid_geometry(self):
        # The panel is the #BFBFBF rule that bounds the reference's white face,
        # the bevel the bounding box of every non-field pixel, the logo the
        # bounding box of the blue pixels inside the white face, and the
        # progress well the bounding box of the pixels darker than #C8C8C8
        # in the rows below the "Starting Up" text. Re-derive each and require the QML
        # literals to match, so a moved rectangle fails here.
        face = _rect(
            (x, y)
            for y in range(self.image.height)
            for x in range(self.image.width)
            if self.pixel(x, y) == (255, 255, 255)
        )
        self.assertEqual(face, (80, 39, 80, 50))

        # The rule is the exact #BFBFBF pixel left of the face; the gap from
        # the face to it is the border width the QML must draw, and the rule
        # bounding box is the panel rectangle.
        rule_left = min(
            x
            for y in range(face[1], face[1] + face[3])
            for x in range(60, face[0])
            if self.pixel(x, y) == PANEL_RULE
        )
        border = face[0] - rule_left
        self.assertEqual(border, 2)
        panel = (
            face[0] - border,
            face[1] - border,
            face[2] + 2 * border,
            face[3] + 2 * border,
        )
        self.assertEqual(qml_rect("panel"), panel)
        self.assertEqual(qml_border_width(), border)

        bevel = _rect(
            (x, y)
            for y in range(self.image.height)
            for x in range(self.image.width)
            if not _field_like(self.pixel(x, y))
        )
        self.assertEqual(qml_rect("bevel"), bevel)

        logo = _rect(
            (x, y)
            for y in LOGO_FACE[1]
            for x in LOGO_FACE[0]
            if self.pixel(x, y)[2] - self.pixel(x, y)[0] > 40
        )
        self.assertEqual(qml_rect("logo"), logo)

        track = _rect(
            (x, y)
            for y in TRACK_BAND[1]
            for x in TRACK_BAND[0]
            if max(self.pixel(x, y)) < 200
        )
        self.assertEqual(qml_rect("track"), track)

        # Every reference pixel the colour test samples must lie inside the
        # rectangle the QML paints the matching colour on, so the geometry
        # literals and the colour literals pin the same position.
        for rect, sample in (
            (bevel, (74, 60)),
            (panel, (78, 60)),
            (panel, (100, 60)),
            (track, (120, 100)),
            (track, (102, 100)),
        ):
            self.assertTrue(
                _contains(rect, *sample), f"{sample} outside {rect}"
            )


if __name__ == "__main__":
    unittest.main()
