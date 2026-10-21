"""Direct tests for ``svg_assertions.faces``'s helpers.

The face corner tables and edge bands are the pixel expectations every widget
bevel test compares against, so a wrong table here would weaken them all.
"""

from __future__ import annotations

import unittest

from support.error_assertions import error_message
from svg_assertions import (
    RAISED_FACE_CORNERS,
    face_corners,
    face_edge_bands,
    flat_face_corners,
    sunken_face_corners,
    sunken_outside_face_corners,
)


def _face_substituted(table, face):
    """Return *table* with each #DDDDDD face pixel replaced by *face*.

    The sunken and flat corner tables are parameterized by the face colour,
    so a test that pins the #DDDDDD table can derive the expected table for
    another face by swapping only the face pixels.
    """
    return {
        name: tuple(
            face if colour == "#DDDDDD" else colour for colour in pixels
        )
        for name, pixels in table.items()
    }


def _shadow_substituted(table, shadow):
    """Return *table* with each #999999 shadow pixel replaced by *shadow*.

    The raised and sunken corner tables take the bevel shadow as a parameter,
    so a test that pins the #999999 table derives the reference's #AAAAAA
    table by swapping only the shadow pixels.
    """
    return {
        name: tuple(
            shadow if colour == "#999999" else colour for colour in pixels
        )
        for name, pixels in table.items()
    }


class TestSunkenFaceCorners(unittest.TestCase):
    def test_paints_the_outline_shadow_and_highlight_around_the_face(self):
        # The frame's sunken state reads its corner pixels from this
        # generator, so a swapped band would weaken that test. Pin the full
        # #DDDDDD table, then check the #FFFFFF face substitutes only the
        # face pixels.
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
        self.assertEqual(
            sunken_face_corners("#DDDDDD", shadow="#AAAAAA"),
            _shadow_substituted(sunken, "#AAAAAA"),
        )


class TestSunkenOutsideFaceCorners(unittest.TestCase):
    def test_paints_the_bevel_outside_the_outline(self):
        # The line edit's field reads its corner pixels from this generator,
        # so a swapped ring would weaken its test. Pin the full #DDDDDD
        # table, then check the #FFFFFF face substitutes only the face
        # pixels -- the fixed #FFFFFF bottom/right highlight must not move,
        # and the unpainted top-right and bottom-left outer pixels stay
        # unpainted.
        sunken = sunken_outside_face_corners("#DDDDDD")
        self.assertEqual(
            sunken,
            {
                "topleft": (
                    "#999999", "#999999", "#999999",
                    "#999999", "#000000", "#000000",
                    "#999999", "#000000", "#DDDDDD",
                ),
                "topright": (
                    "#999999", "#999999", None,
                    "#000000", "#000000", "#FFFFFF",
                    "#DDDDDD", "#000000", "#FFFFFF",
                ),
                "bottomleft": (
                    "#999999", "#000000", "#DDDDDD",
                    "#999999", "#000000", "#000000",
                    None, "#FFFFFF", "#FFFFFF",
                ),
                "bottomright": (
                    "#DDDDDD", "#000000", "#FFFFFF",
                    "#000000", "#000000", "#FFFFFF",
                    "#FFFFFF", "#FFFFFF", "#FFFFFF",
                ),
            },
        )
        self.assertEqual(
            sunken_outside_face_corners("#FFFFFF"),
            _face_substituted(sunken, "#FFFFFF"),
        )
        self.assertEqual(
            sunken_outside_face_corners("#DDDDDD", shadow="#AAAAAA"),
            _shadow_substituted(sunken, "#AAAAAA"),
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
            face_edge_bands("#DDDDDD", "raised", shadow="#AAAAAA"),
            (("#000000", "#FFFFFF", "#DDDDDD"),
             ("#DDDDDD", "#AAAAAA", "#000000")),
        )
        self.assertEqual(
            face_edge_bands("#DDDDDD", "sunken", shadow="#AAAAAA"),
            (("#000000", "#AAAAAA", "#DDDDDD"),
             ("#DDDDDD", "#FFFFFF", "#000000")),
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
        self.assertEqual(
            face_edge_bands("#FFFFFF", "sunken-outside"),
            (("#999999", "#000000", "#FFFFFF"),
             ("#FFFFFF", "#000000", "#FFFFFF")),
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
            face_corners("#FFFFFF", "sunken-outside"),
            sunken_outside_face_corners("#FFFFFF"),
        )
        self.assertEqual(
            face_corners("#EEEEEE", "flat"), flat_face_corners("#EEEEEE")
        )
        self.assertEqual(
            face_corners("#DDDDDD", "raised", shadow="#AAAAAA"),
            _shadow_substituted(RAISED_FACE_CORNERS, "#AAAAAA"),
        )
        self.assertEqual(
            face_corners("#DDDDDD", "sunken", shadow="#AAAAAA"),
            sunken_face_corners("#DDDDDD", shadow="#AAAAAA"),
        )
        self.assertEqual(
            face_corners("#DDDDDD", "sunken-outside", shadow="#AAAAAA"),
            sunken_outside_face_corners("#DDDDDD", shadow="#AAAAAA"),
        )
        self.assertEqual(
            face_corners("#EEEEEE", "flat", shadow="#AAAAAA"),
            flat_face_corners("#EEEEEE"),
        )

    def test_rejects_an_unknown_bevel_naming_it(self):
        self.assertIn(
            "bevelled",
            error_message(
                self, ValueError, face_corners, "#DDDDDD", "bevelled"
            ),
        )
