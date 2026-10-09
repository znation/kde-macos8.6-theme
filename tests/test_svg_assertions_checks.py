"""Direct tests for tests/svg_assertions.py's layout and pixel assertions.

Every desktop-theme widget test reaches these helpers only over its own
current artwork, so a helper that mis-orders a band, mirrors the wrong sides
or drops the size would weaken all of them at once. These tests prove each
assertion passes a correct layout and can actually fail a broken one. The
document-safety guards (scripts, style elements, external references,
duplicate ids) have their own module, ``test_svg_assertions_safety.py``.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from error_assertions import NoSubTest, assert_rejects
from svg_assertions import (
    SLICE_IDS,
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_hint_geometry,
    assert_root_canvas,
    assert_slice_ids_present,
    assert_slice_pixels,
    assert_slices_fill_their_tiles,
    assert_slices_stay_within_their_tiles,
    assert_slices_uniform,
    assert_tiles_placed_by_margins,
    face_corners,
    face_edge_bands,
    pixel_map,
)
from svg_fixtures import _svg_tree


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


def _tree_with_extra_group(origin=(0, 0)):
    """A valid nine-slice tree plus an id-bearing non-tile group at *origin*.

    The slider's handle groups are id-bearing but are not nine-slice tiles,
    so `assert_tiles_placed_by_margins` needs their origin supplied through
    its *extra_groups* map instead of deriving it from the margin hints.
    """
    x, y = origin
    groups = "".join(
        f'<g id="{name}" transform="translate({gx},{gy})">'
        '<rect width="4" height="4" fill="#000000"/>'
        "</g>"
        for name, (gx, gy) in _ORIGINS.items()
    )
    extra = (
        f'<g id="handle" transform="translate({x},{y})">'
        '<rect width="2" height="2" fill="#000000"/>'
        "</g>"
    )
    return _svg_tree(
        f"{_HINTS}{groups}{extra}",
        width="12",
        height="12",
        viewBox="0 0 12 12",
    )


# A base state with hints plus a hintless alias state that reuses them, the
# shape the inactive Aurorae frame has. The alias tiles sit at the base
# origins; the SVG carries no `alias-hint-*-margin` ids.
_ALIAS_HINTS = (
    '<rect id="hint-tile-center" x="4" y="4" width="4" height="4"/>'
    '<rect id="base-hint-top-margin" x="4" y="0" width="4" height="4"/>'
    '<rect id="base-hint-bottom-margin" x="4" y="8" width="4" height="4"/>'
    '<rect id="base-hint-left-margin" x="0" y="4" width="4" height="4"/>'
    '<rect id="base-hint-right-margin" x="8" y="4" width="4" height="4"/>'
)

# The alias state declares that it reuses the base state's hints, so the alias
# tiles are placed by `base-hint-*-margin` rather than their own.
_ALIAS_PREFIXES = ["base", "alias"]
_ALIAS_HINT_MAP = {"alias": "base"}


def _aliased_nine_slice_tree(alias_origins=None):
    """Build a nine-slice tree whose alias state reuses the base's hints.

    *alias_origins* defaults to the base layout; overriding one lets a caller
    place an alias tile where the base hints do not, so the alias-aware guard
    can be proven to reject it.
    """
    alias_origins = _ORIGINS if alias_origins is None else alias_origins

    def groups(prefix, origins):
        sep = "-" if prefix else ""
        return "".join(
            f'<g id="{prefix}{sep}{name}" transform="translate({x},{y})">'
            '<rect x="0" y="0" width="4" height="4" fill="#000000"/>'
            "</g>"
            for name, (x, y) in origins.items()
        )

    body = (
        _ALIAS_HINTS
        + groups("base", _ORIGINS)
        + groups("alias", alias_origins)
    )
    return _svg_tree(body, width="12", height="12", viewBox="0 0 12 12")


class TestStructuralGuards(unittest.TestCase):
    def test_tiles_placed_by_margins_passes_a_correct_layout(self):
        assert_tiles_placed_by_margins(self, _nine_slice_tree(), [""])

    def test_tiles_placed_by_margins_catches_a_misplaced_group(self):
        origins = dict(_ORIGINS)
        origins["top"] = (0, 0)
        assert_rejects(
            assert_tiles_placed_by_margins,
            _nine_slice_tree(origins=origins),
            [""],
        )

    def test_slices_within_their_tiles_passes_a_correct_layout(self):
        assert_slices_stay_within_their_tiles(self, _nine_slice_tree(), [""])

    def test_slices_within_their_tiles_catches_an_oversized_rect(self):
        # A rect one pixel wider than its tile spills into the neighbouring
        # canvas region, which KSvg samples into that tile; the guard must
        # report the overflow instead of silently accepting it.
        assert_rejects(
            assert_slices_stay_within_their_tiles,
            _nine_slice_tree(sizes={"top": (5, 4)}),
            [""],
        )

    def test_tiles_placed_by_margins_uses_the_alias_hints(self):
        assert_tiles_placed_by_margins(
            self,
            _aliased_nine_slice_tree(),
            _ALIAS_PREFIXES,
            _ALIAS_HINT_MAP,
        )

    def test_tiles_placed_by_margins_catches_a_misplaced_alias_tile(self):
        origins = dict(_ORIGINS)
        origins["top"] = (0, 0)
        assert_rejects(
            assert_tiles_placed_by_margins,
            _aliased_nine_slice_tree(alias_origins=origins),
            _ALIAS_PREFIXES,
            _ALIAS_HINT_MAP,
        )

    def test_tiles_placed_by_margins_accounts_for_extra_groups(self):
        # The slider's handle groups are id-bearing but are not nine-slice
        # tiles; their origin is supplied separately so the exact map
        # comparison does not fail on them.
        assert_tiles_placed_by_margins(
            self,
            _tree_with_extra_group(),
            [""],
            extra_groups={"handle": (0, 0)},
        )

    def test_tiles_placed_by_margins_catches_a_misplaced_extra_group(self):
        assert_rejects(
            assert_tiles_placed_by_margins,
            _tree_with_extra_group(origin=(1, 1)),
            [""],
            extra_groups={"handle": (0, 0)},
        )

    def test_slices_within_their_tiles_uses_the_alias_hints(self):
        assert_slices_stay_within_their_tiles(
            self,
            _aliased_nine_slice_tree(),
            _ALIAS_PREFIXES,
            _ALIAS_HINT_MAP,
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

    def test_accepts_a_hintless_alias(self):
        # The alias state carries the nine slice ids but no hint ids; its
        # tiles are placed by the base hints, so the guard must not demand
        # `alias-hint-*-margin` once the alias is declared.
        assert_slice_ids_present(
            self,
            _aliased_nine_slice_tree(),
            _ALIAS_PREFIXES,
            _ALIAS_HINT_MAP,
        )

    def test_requires_the_alias_hints_when_no_alias_is_declared(self):
        with self.assertRaises(AssertionError):
            assert_slice_ids_present(
                self, _aliased_nine_slice_tree(), _ALIAS_PREFIXES
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
