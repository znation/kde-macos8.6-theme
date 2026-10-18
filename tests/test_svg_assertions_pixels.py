"""Direct tests for ``svg_assertions.checks``'s pixel-comparison assertions.

Each widget test reaches these helpers only over its own current artwork, so a
helper that mis-orders a band, mirrors the wrong sides or drops the size check
could still pass every widget test. These tests pin the helpers on maps built
independently of the artwork and prove each can fail. The layout assertions
are tested in ``test_svg_assertions_checks.py``.
"""

from __future__ import annotations

import unittest

from support.error_assertions import NoSubTest, assert_rejects
from svg_assertions import (
    SLICE_IDS,
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_slice_pixels,
    assert_slices_fill_their_tiles,
    assert_slices_have_no_fill,
    assert_slices_uniform,
    face_corners,
    face_edge_bands,
    pixel_map,
)
from support.svg_fixtures import _svg_tree


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
        assert_rejects(assert_slice_pixels, slices, "center", expected)

    def test_slices_uniform_pins_every_pixel_and_rejects_a_break(self):
        colour = "#CCCCFF"
        slices = {
            f"pressed-{name}": pixel_map((colour,) * 4, 2, 2)
            for name in SLICE_IDS
        }
        assert_slices_uniform(self, slices, "pressed", colour)
        # The empty prefix names the slices directly, with no separator.
        assert_slices_uniform(
            self,
            {name: slices[f"pressed-{name}"] for name in SLICE_IDS},
            "",
            colour,
        )
        # One recoloured pixel in one slice must fail, so a helper that
        # skipped a slice (or compared loosely) would not pass.
        recoloured = dict(slices)
        recoloured["pressed-center"] = pixel_map(
            ("#FFFFFF",) + (colour,) * 3, 2, 2
        )
        assert_rejects(assert_slices_uniform, recoloured, "pressed", colour)
        # A missing slice must fail on the lookup rather than be skipped; the
        # key is read inside the subTest frame, so use the stub case to let
        # the KeyError surface.
        missing = dict(slices)
        del missing["pressed-topleft"]
        case = NoSubTest()
        with case.assertRaises(KeyError):
            assert_slices_uniform(case, missing, "pressed", colour)

    def test_slices_have_no_fill_pins_the_placeholder_and_rejects_a_fill(self):
        # The transparent-placeholder convention: every slice of an invisible
        # state renders None and the tree's only fill-opacity is 0.01.
        def transparent(fill=None, opacity="0.01"):
            rect = f' fill="{fill}"' if fill else ""
            body = "".join(
                f'<g id="normal-{name}">'
                f'<rect width="1" height="1"{rect} '
                f'fill-opacity="{opacity}"/>'
                "</g>"
                for name in SLICE_IDS
            )
            return _svg_tree(body)

        assert_slices_have_no_fill(self, transparent(), "normal")
        # A slice that paints a colour must fail: render_slices reads the fill,
        # so the uniform-None check catches it.
        assert_rejects(
            assert_slices_have_no_fill, transparent("#CCCCFF"), "normal"
        )
        # A placeholder that is fully opaque must fail too: the helper pins the
        # artwork's 0.01, not merely "some transparency".
        assert_rejects(
            assert_slices_have_no_fill, transparent(opacity="0"), "normal"
        )

    def test_slices_fill_their_tiles_pins_every_tile_and_rejects_a_gap(self):
        colour = "#CCCCFF"
        fills = {"pressed": colour, "normal": None}
        # A 4px border on a 12x12 canvas makes every tile 4x4, so the maps can
        # be built without re-deriving their sizes from the helper.
        border = tile = 4
        slices = {
            f"{prefix}-{name}": pixel_map((fills[prefix],) * 16, 4, 4)
            for prefix in fills
            for name in SLICE_IDS
        }
        assert_slices_fill_their_tiles(
            self, slices, tuple(fills.items()), border, tile
        )
        # A tile one pixel short must fail: its fill is uniform, so only the
        # full-map compare catches the missing pixel.
        short = dict(slices)
        short["pressed-center"] = pixel_map((colour,) * 16, 4, 4)
        del short["pressed-center"][(3, 3)]
        assert_rejects(
            assert_slices_fill_their_tiles,
            short,
            tuple(fills.items()),
            border,
            tile,
        )

    def test_edge_band_pixels_pins_a_top_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"top": _horizontal_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "top", "top", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        assert_rejects(
            assert_edge_band_pixels, slices, "top", "top", mirrored, size
        )

    def test_edge_band_pixels_pins_a_left_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"left": _vertical_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "left", "left", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        assert_rejects(
            assert_edge_band_pixels, slices, "left", "left", mirrored, size
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
        assert_rejects(
            assert_edge_bevels, broken_bottom, "", outward, mirrored, size
        )

        broken_left = _bevel_slices(outward, mirrored, size)
        broken_left["left"] = _vertical_band(mirrored, size)
        assert_rejects(
            assert_edge_bevels, broken_left, "", outward, mirrored, size
        )

        broken_right = _bevel_slices(outward, mirrored, size)
        broken_right["right"] = _vertical_band(outward, size)
        assert_rejects(
            assert_edge_bevels, broken_right, "", outward, mirrored, size
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
            assert_rejects(
                assert_corner_pixels,
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
        assert_rejects(assert_face_corners, broken, "state", corners)

    def test_center_tile_is_pins_the_full_square_and_its_size(self):
        colour = "#DDDDDD"
        slices = {"center": pixel_map((colour,) * 36, 6, 6)}
        assert_center_tile_is(self, slices, "center", colour, 6)
        # A 7x7 centre has the right colour everywhere but the wrong tile
        # size, which the declared-size pin must reject.
        bigger = {"center": pixel_map((colour,) * 49, 7, 7)}
        assert_rejects(assert_center_tile_is, bigger, "center", colour, 6)

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
                assert_rejects(
                    assert_face_bevel, broken_center, "", face, bevel,
                    size=size,
                )

                _, mirrored = face_edge_bands(face, bevel)
                broken_edge = _face_slices(face, bevel, size)
                broken_edge["top"] = _horizontal_band(mirrored, size)
                assert_rejects(
                    assert_face_bevel, broken_edge, "", face, bevel,
                    size=size,
                )

                broken_corner = _face_slices(face, bevel, size)
                broken_corner["topleft"] = pixel_map(("#FFFFFF",) * 9, 3, 3)
                assert_rejects(
                    assert_face_bevel, broken_corner, "", face, bevel,
                    size=size,
                )


if __name__ == "__main__":
    unittest.main()
