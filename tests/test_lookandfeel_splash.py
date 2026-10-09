"""Tests for the org.macos8.desktop look-and-feel startup splash.

The splash artwork is authored on the 240x180 grid of the reference thumbnail
``macos8.6-screenshots/boot2_betawiki.png``. These tests tie the QML's colour
and rectangle literals and the logo SVG's fills back to pixels and colour scans
of that reference, so a literal that drifts from the reference fails here
rather than only looking wrong on screen.
"""

from __future__ import annotations

import os
import re
import unittest
import xml.etree.ElementTree as ET

from reference_image import skip_unless_materialized
from theme_install import ROOT

from tools import png  # noqa: E402
from svg_assertions import (  # noqa: E402
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    assert_unique_ids,
    attribute_values,
    elements_by_id,
    local_name,
)
from svg_case import SvgCase  # noqa: E402

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
SPLASH = os.path.join(PACKAGE, "contents", "splash", "Splash.qml")
LOGO = os.path.join(PACKAGE, "contents", "splash", "images", "macos-logo.svg")
REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "boot2_betawiki.png"
)

# The exact reference pixels the QML colours are pinned to. (74,60) is the
# #DDDDDD bevel and (78,60) the #BFBFBF rule that bounds the white face at
# (100,60); (135,96) is the #DDDDDD track at the unfilled right end of the
# progress well and (120,100) the #ADADAD fill.
FIELD = (99, 99, 156)
PANEL_BEVEL = (221, 221, 221)
PANEL_RULE = (191, 191, 191)
TRACK = (221, 221, 221)
FILL = (173, 173, 173)

# The logo is the only blue region inside the panel's white face; the progress
# well is the only region darker than the panel's #DDDDDD in the lower band.
LOGO_FACE = (range(80, 160), range(39, 89))
TRACK_BAND = (range(80, 160), range(90, 105))


def _read_qml():
    with open(SPLASH, encoding="utf-8") as handle:
        return handle.read()


def qml_int(name):
    """Return the integer literal of ``readonly property int <name>: N``.

    The QML declares every reference-grid coordinate this way, so the geometry
    test reads the same number the artwork uses instead of a second copy.
    """
    match = re.search(
        rf"readonly property int {re.escape(name)}:\s*(\d+)", _read_qml()
    )
    if match is None:
        raise AssertionError(f"{SPLASH}: no integer literal for {name}")
    return int(match.group(1))


def qml_rect(name):
    """Return the QML ``(X, Y, Width, Height)`` integer literals for *name*.

    Each reference rectangle's four coordinates are ``readonly property int``
    literals sharing the ``<name>X/Y/Width/Height`` suffix pattern, so the
    geometry test compares the whole rectangle with one call.
    """
    return tuple(
        qml_int(f"{name}{part}") for part in ("X", "Y", "Width", "Height")
    )


def qml_color(name):
    """Return the uppercase ``#RRGGBB`` of ``readonly property color <name>``."""
    match = re.search(
        rf'readonly property color {re.escape(name)}:\s*'
        r'"(#[0-9A-Fa-f]{6})"',
        _read_qml(),
    )
    if match is None:
        raise AssertionError(f"{SPLASH}: no colour literal for {name}")
    return match.group(1).upper()


def qml_border_width():
    """Return the integer factor of the panel's ``border.width`` binding."""
    match = re.search(r"border\.width:\s*(\d+) \* root\.unit", _read_qml())
    if match is None:
        raise AssertionError(f"{SPLASH}: no integer border width")
    return int(match.group(1))


def qml_unit_expression():
    """Return the whitespace-normalized expression bound to ``root.unit``.

    Every geometry binding multiplies a reference-grid literal by ``root.unit``,
    so the scale itself is as load-bearing as those bindings: the reference
    thumbnail is 240x180, and the ``Math.max(1, ...)`` floor keeps a window
    smaller than that grid from collapsing the splash to zero. The definition
    is one line today but may wrap, so collapse its whitespace before comparing
    it to the canonical expression.
    """
    match = re.search(r"readonly property int unit:[ \t]*(.+)", _read_qml())
    if match is None:
        raise AssertionError(f"{SPLASH}: no unit property definition")
    return " ".join(match.group(1).split())


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


def _object_source(qml, object_id):
    """Return the brace-balanced QML object whose ``id`` is ``object_id``.

    ``id`` is written just inside the object's opening brace, so the nearest
    preceding ``{`` opens that object and the matching ``}`` closes it. This
    lets the painting test assert a colour binding on the same object whose
    geometry binding the geometry test pins.
    """
    match = re.search(rf"\bid:\s*{re.escape(object_id)}\b", qml)
    if match is None:
        raise AssertionError(f"{SPLASH}: no object with id {object_id}")
    start = qml.rfind("{", 0, match.start())
    if start < 0:
        raise AssertionError(f"{SPLASH}: id {object_id} is not in an object")
    depth = 0
    for index in range(start, len(qml)):
        if qml[index] == "{":
            depth += 1
        elif qml[index] == "}":
            depth -= 1
            if depth == 0:
                return qml[start : index + 1]
    raise AssertionError(f"{SPLASH}: object {object_id} is not brace-balanced")


class SplashReferenceCase(unittest.TestCase):
    """Load the Git LFS reference once; skip the class when it is absent.

    ``make check`` must not require the LFS reference set (that is what
    ``make check-references`` is for), so a clone without the thumbnail skips
    the reference-derived tests instead of failing.
    """

    @classmethod
    def setUpClass(cls):
        cls.image = None
        cls.image_error = None
        try:
            cls.image = png.read_png(REFERENCE)
        except png.PngError as exc:
            cls.image_error = exc

    def setUp(self):
        skip_unless_materialized(self, REFERENCE, self.image_error)

    def pixel(self, x, y):
        return png.pixel_at(self.image, x, y)


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
        # (135,96) is the #DDDDDD track at the unfilled right end of the
        # progress well; (120,100) is the flat #ADADAD fill.
        self.assertEqual(self.pixel(135, 96), TRACK)
        self.assertEqual(self.pixel(120, 100), FILL)
        self.assertEqual(qml_color("trackColor"), "#DDDDDD")
        self.assertEqual(qml_color("fillColor"), "#ADADAD")

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
            {"#%02X%02X%02X" % highlight, "#%02X%02X%02X" % face},
        )


class TestSplashGeometry(SplashReferenceCase):
    def test_grid_geometry(self):
        # The panel is the #BFBFBF rule that bounds the reference's white face,
        # the bevel the bounding box of every non-field pixel, the logo the
        # bounding box of the blue pixels inside the white face, and the
        # progress well the bounding box of the pixels darker than the panel's
        # #DDDDDD in the lower band. Re-derive each and require the QML
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
            (track, (135, 96)),
            (track, (120, 100)),
        ):
            self.assertTrue(
                _contains(rect, *sample), f"{sample} outside {rect}"
            )


class TestSplashQml(unittest.TestCase):
    """QML structure checks that need no reference image.

    They run in a clone without the LFS thumbnail, where ``SplashReferenceCase``
    skips; the logo source and the ``stage`` binding must still be checked.
    """

    def test_uses_the_logo_image(self):
        self.assertIn('source: "images/macos-logo.svg"', _read_qml())

    def test_logo_rasterizes_at_its_displayed_size(self):
        # `test_uses_the_logo_image` pins the source path and
        # `test_grid_geometry` pins the 26x21 grid rect it is drawn into, but
        # nothing pins the size the SVG is rasterized at. The SVG's intrinsic
        # size is that same 26x21, so on any `unit` above 1 (the splash scales
        # its whole grid by whole pixels) an Image without `sourceSize` would
        # load a 26x21 bitmap and scale it up, softening the logo while every
        # geometry and colour test still passed. Bind the raster size to the
        # item's displayed size.
        logo = _object_source(_read_qml(), "logo")
        self.assertIn("sourceSize.width: width", logo)
        self.assertIn("sourceSize.height: height", logo)

    def test_progress_fill_follows_stage(self):
        # The fill width binds to the KDE splash `stage` (0..6), so the
        # reference's mostly-full bar is stage 5 of 6. Pin the binding, or a
        # fill that ignores `stage` would look plausible but never advance.
        self.assertIn(
            "width: parent.width * Math.min(1, root.stage / 6)", _read_qml()
        )

    def test_progress_fill_stretches_to_the_track_height(self):
        # The fill's width binding is pinned above, but its vertical extent is
        # not. The fill declares no `height` of its own, so it is drawn only
        # because `anchors.top` and `anchors.bottom` stretch it to the track's
        # inside; dropping either collapses it to a 0px line, an empty-looking
        # progress well, while the width test and every colour test still pass.
        # `anchors.left` places its origin on the track's left edge. Pin all
        # three so the fill keeps spanning the well as the stage advances.
        fill = _object_source(_read_qml(), "fill")
        self.assertIn("anchors.left: parent.left", fill)
        self.assertIn("anchors.top: parent.top", fill)
        self.assertIn("anchors.bottom: parent.bottom", fill)

    def test_unit_scales_the_reference_grid_without_collapsing(self):
        # Every geometry binding is a reference-grid literal times `root.unit`,
        # but no test pinned `unit` itself. A definition that dropped the
        # `Math.max(1, ...)` floor would let `unit` reach 0 on a window smaller
        # than the 240x180 grid and collapse the whole splash, while every
        # geometry binding still read correctly. Pin the exact scale: one whole
        # pixel per reference-grid pixel, floored at 1.
        self.assertEqual(
            qml_unit_expression(),
            "Math.max(1, Math.floor(Math.min(width / 240, height / 180)))",
        )

    def test_stage_two_starts_the_intro_animation(self):
        # The QML follows Breeze's stage protocol: the splash stays hidden
        # until the session reaches stage 2, then fades in. `stage` drives
        # both the progress fill and this reveal, but only the fill was
        # pinned. Dropping the handler, changing the stage it tests, or
        # assigning a different animator would leave the splash permanently
        # invisible while every other test still passed. Tie the stage number
        # to the assignment in one match so they cannot drift apart.
        match = re.search(
            r"onStageChanged:\s*\{\s*if \(stage == (\d+)\)\s*\{\s*"
            r"introAnimation\.running = true\s*\}",
            _read_qml(),
        )
        self.assertIsNotNone(
            match, "onStageChanged must start introAnimation"
        )
        self.assertEqual(match.group(1), "2")

    def test_intro_animation_fades_content_in(self):
        # The reveal is only correct as a whole chain: `content` must start
        # transparent, and the animator must target that same item and fade it
        # from 0 to 1. A retargeted animator, or a `content` that starts
        # opaque (a visible flash before the fade), would otherwise pass every
        # other test while looking wrong on screen.
        qml = _read_qml()
        self.assertIn("opacity: 0", _object_source(qml, "content"))
        animator = _object_source(qml, "introAnimation")
        self.assertIn("target: content", animator)
        self.assertIn("from: 0", animator)
        self.assertIn("to: 1", animator)

    def test_content_is_the_centred_reference_grid(self):
        # Every child rect is positioned in the 240x180 reference grid, but the
        # `content` item those coordinates are relative to is unpinned: if its
        # size dropped a grid literal, or its `anchors.centerIn` moved the
        # item's origin off centre, the whole composition would shrink or
        # shift while every child-binding and colour test still passed.
        # `anchors.centerIn` centres the item's own rect, so its size and its
        # anchor are one position and must be pinned together.
        content = _object_source(_read_qml(), "content")
        self.assertIn("width: 240 * root.unit", content)
        self.assertIn("height: 180 * root.unit", content)
        self.assertIn("anchors.centerIn: parent", content)

    def test_wordmark_sits_on_the_panel_at_its_reference_position(self):
        # The "Mac OS" wordmark is the only element placed relative to the
        # panel rather than the grid: `test_wordmark_colour_matches_reference`
        # pins its colour and `test_reference_colours_are_painted` its colour
        # binding, but nothing pins where it is drawn. A changed `y` literal or
        # a dropped `anchors.horizontalCenter` would slide the wordmark off the
        # panel while every colour and rectangle test still passed.
        wordmark = _object_source(_read_qml(), "wordmark")
        self.assertIn("y: 71 * root.unit", wordmark)
        self.assertIn(
            "anchors.horizontalCenter: panel.horizontalCenter", wordmark
        )

    def test_wordmark_shows_the_reference_label_at_its_grid_size(self):
        # Where the wordmark sits and what colour it is are pinned, but not the
        # label it draws or the size it draws it at. `test_wordmark_colour_
        # matches_reference` samples one of its glyph pixels and the position
        # test pins that pixel's location, yet a changed `text` or a dropped
        # `font.pixelSize` (Text would then fall back to the application's
        # default font, at a different size) would leave every other test
        # green. Pin the label and the reference-grid size together.
        wordmark = _object_source(_read_qml(), "wordmark")
        self.assertIn('text: "Mac OS"', wordmark)
        self.assertIn("font.pixelSize: 12 * root.unit", wordmark)

    def test_reference_colours_are_painted(self):
        """Each anchor colour must be bound to the object at its reference rect.

        A declared colour property proves nothing about the screen: the pixel
        and geometry tests would still pass if no object bound the colour, or
        bound it to the wrong rectangle. This ties every anchor colour property
        to the object whose geometry literals ``test_grid_geometry`` pins to
        the reference rectangle, so the pair can only hold when that object
        paints that colour over that rectangle.
        """
        qml = _read_qml()
        self.assertIn("color: root.fieldColor", qml)
        expected = {
            "bevel": (
                "color: root.panelBevelColor",
                "x: root.bevelX * root.unit",
                "y: root.bevelY * root.unit",
                "width: root.bevelWidth * root.unit",
                "height: root.bevelHeight * root.unit",
            ),
            "panel": (
                "color: root.panelColor",
                "border.color: root.panelRuleColor",
                "x: root.panelX * root.unit",
                "y: root.panelY * root.unit",
                "width: root.panelWidth * root.unit",
                "height: root.panelHeight * root.unit",
            ),
            "track": (
                "color: root.trackColor",
                "x: root.trackX * root.unit",
                "y: root.trackY * root.unit",
                "width: root.trackWidth * root.unit",
                "height: root.trackHeight * root.unit",
            ),
            "fill": ("color: root.fillColor",),
            "wordmark": ("color: root.wordmarkColor",),
        }
        for object_id, bindings in expected.items():
            block = _object_source(qml, object_id)
            for binding in bindings:
                self.assertIn(binding, block, f"{object_id}: {binding}")


class TestLogo(SvgCase, unittest.TestCase):
    SVG_PATH = LOGO

    def test_logo_svg(self):
        # The logo is the look-and-feel package's only shipped SVG, so it gets
        # the same structural guard the desktop-theme SVGs get centrally: a
        # pinned canvas (a width/height that drifts from the viewBox would
        # rescale the logo), no <style> element, and no reference to a file
        # the package does not ship. `attribute_values` reads fills only from
        # attributes, so a CSS-styled or externally-referenced logo could
        # otherwise pass this test while rendering wrong or blank.
        assert_root_canvas(self, self.tree, 26, 21)
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        assert_unique_ids(self, self.tree)
        self.assertEqual(
            attribute_values(self.tree, "fill"), {"#4C65CB", "#7286D6"}
        )

    def test_logo_geometry(self):
        # `test_logo_svg` pins the root canvas and the set of fills, and
        # `test_logo_colours_match_reference` pins each fill to a reference
        # pixel, but neither fixes the drawn shape: the face rect could shrink
        # inside the 26x21 canvas or lose its 5px corner radius, or the
        # highlight path could move, and every existing test would still pass.
        # Pin each element's geometry and its own fill, so a drift in either
        # fails here instead of only looking wrong on screen.
        by_id = elements_by_id(self.tree)

        face = by_id["face"]
        self.assertEqual(local_name(face), "rect")
        self.assertEqual(
            [face.get(k) for k in ("x", "y", "width", "height", "rx", "fill")],
            ["0", "0", "26", "21", "5", "#4C65CB"],
        )

        highlight = by_id["highlight"]
        self.assertEqual(local_name(highlight), "path")
        self.assertEqual(highlight.get("fill"), "#7286D6")
        self.assertEqual(
            highlight.get("d"),
            "M 4 3 L 22 3 Q 24 3 24 5 L 24 9 Q 19 6 4 6 Z",
        )

        # The highlight is the lighter blue drawn over the face, and document
        # order is paint order: it must come after `face` or it is hidden.
        order = [
            element.get("id")
            for element in self.tree.iter()
            if element.get("id")
        ]
        self.assertLess(order.index("face"), order.index("highlight"))


if __name__ == "__main__":
    unittest.main()
