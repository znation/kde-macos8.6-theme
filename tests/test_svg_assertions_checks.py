"""Direct tests for tests/svg_assertions.py's assertion helpers.

Every desktop-theme widget test reaches these helpers only over its own
current artwork, so a helper that mis-orders a band, mirrors the wrong sides
or drops the size would weaken all of them at once. These tests prove each
assertion passes a correct layout and can actually fail a broken one, and pin
the tree-validation guards (missing slice ids, duplicate ids, scripts, canvas
geometry).
"""

from __future__ import annotations

import contextlib
import unittest
import xml.etree.ElementTree as ET

from error_assertions import error_message
from svg_assertions import (
    SLICE_IDS,
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_hint_geometry,
    assert_no_script_elements,
    assert_no_external_references,
    assert_no_style_elements,
    assert_root_canvas,
    assert_slice_ids_present,
    assert_slice_pixels,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    assert_unique_ids,
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


class _NoSubTest(unittest.TestCase):
    """A real TestCase whose ``subTest`` is a no-op frame.

    The structural guards report a bad slice through ``case.subTest``;
    unittest records a subTest failure on the result and keeps going rather
    than raising, so an ``assertRaises`` around the guard would never see it.
    Dropping the subTest frame keeps the real ``assertEqual`` (which raises)
    so the guard's failure is observable here.

    The pixel guards compare whole ``{(x, y): colour}`` maps, and every use of
    this stub is a deliberately broken map whose only observable is that the
    guard raises. ``assertEqual`` on two dicts dispatches to
    ``assertDictEqual``, whose failure path pretty-prints both maps and runs
    them through difflib -- a large, pure-diagnostic cost these callers never
    read. Compare without that diff; a mismatch still raises
    ``AssertionError``, so the guard's failure stays observable.
    """

    def subTest(self, **kwargs):
        return contextlib.nullcontext()

    def assertDictEqual(self, d1, d2, msg=None):
        self.assertIsInstance(d1, dict, "First argument is not a dictionary")
        self.assertIsInstance(d2, dict, "Second argument is not a dictionary")
        if d1 != d2:
            self.fail(self._formatMessage(msg, "the maps differ"))


def _assert_rejects(guard, *args, **kwargs):
    """Assert *guard* rejects a broken input instead of accepting it.

    A guard that reports a bad slice through ``case.subTest`` does not raise:
    unittest records the failure and keeps going, so ``assertRaises`` would
    never observe it. Giving the guard the ``_NoSubTest`` case drops the
    subTest frame so the underlying assertion raises instead; a guard that
    raises directly is unaffected. *args* and *kwargs* are the guard's own
    parameters after ``case``.
    """
    case = _NoSubTest()
    with case.assertRaises(AssertionError):
        guard(case, *args, **kwargs)


def _rejection_message(guard, *args, **kwargs):
    """Return the AssertionError message *guard* raises for a broken input.

    `_assert_rejects` proves a guard rejects an input; a test that also pins
    what the diagnostic names needs the message. Like that helper this gives
    the guard a ``_NoSubTest`` case, so a guard that reports through
    ``case.subTest`` still raises. *args* and *kwargs* are the guard's own
    parameters after ``case``.
    """
    case = _NoSubTest()
    return error_message(
        case, AssertionError, guard, case, *args, **kwargs
    )


class TestStructuralGuards(unittest.TestCase):
    def test_tiles_placed_by_margins_passes_a_correct_layout(self):
        assert_tiles_placed_by_margins(self, _nine_slice_tree(), [""])

    def test_tiles_placed_by_margins_catches_a_misplaced_group(self):
        origins = dict(_ORIGINS)
        origins["top"] = (0, 0)
        _assert_rejects(
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
        _assert_rejects(
            assert_slices_stay_within_their_tiles,
            _nine_slice_tree(sizes={"top": (5, 4)}),
            [""],
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

    def test_catches_a_missing_id_in_a_later_prefix(self):
        # A guard that only checks the first prefix would pass the two-prefix
        # positive control; the missing id is in the second state.
        with self.assertRaises(AssertionError):
            assert_slice_ids_present(
                self,
                _id_tree(("plain", "raised"), omit=("raised-top",)),
                ["plain", "raised"],
            )


class TestNoScriptElements(unittest.TestCase):
    def test_passes_a_tree_without_a_script(self):
        tree = _svg_tree('<rect id="center"/>')
        assert_no_script_elements(self, tree)

    def test_catches_a_script_after_another_element(self):
        tree = _svg_tree(
            '<rect id="center"/><script>alert(1)</script>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)

    def test_catches_a_script_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<g id="top"><g><script>alert(1)</script></g></g>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)


class TestNoStyleElements(unittest.TestCase):
    def test_passes_a_tree_without_a_style_element(self):
        # An inline `style` attribute is how every shipped SVG states its
        # colours; only a `<style>` element is rejected.
        tree = _svg_tree('<rect id="center" style="fill:#ff6600"/>')
        assert_no_style_elements(self, tree)

    def test_catches_a_style_element_naming_it(self):
        tree = _svg_tree(
            '<rect id="center"/><style>rect{fill:#ff6600}</style>'
        )
        self.assertIn(
            "style",
            _rejection_message(assert_no_style_elements, tree),
        )

    def test_catches_a_style_element_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<g id="top"><style>rect{fill:#ff6600}</style></g>'
        )
        with self.assertRaises(AssertionError):
            assert_no_style_elements(self, tree)


class TestNoExternalReferences(unittest.TestCase):
    def test_passes_a_tree_with_no_references(self):
        tree = _svg_tree('<rect id="center" style="fill:#ff6600"/>')
        assert_no_external_references(self, tree)

    def test_passes_a_same_document_fragment_reference(self):
        # An internal `#id` reference stays inside the file, so it is allowed.
        tree = _svg_tree('<use href="#center"/>')
        assert_no_external_references(self, tree)

    def test_catches_an_image_element(self):
        tree = _svg_tree('<image href="panel.png"/>')
        self.assertIn(
            "image",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_file_href_naming_the_value(self):
        tree = _svg_tree('<use href="other.svg#center"/>')
        self.assertIn(
            "other.svg#center",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_catches_an_xlink_href(self):
        # A declared xlink namespace makes ElementTree report the attribute as
        # `{http://www.w3.org/1999/xlink}href`; the guard must strip it and
        # still reject the file reference.
        tree = _svg_tree(
            '<use xlink:href="other.svg#center"/>',
            **{"xmlns:xlink": "http://www.w3.org/1999/xlink"},
        )
        self.assertIn(
            "other.svg#center",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_data_uri_href(self):
        # A `data:` URI is self-contained but still not an in-file #id, so the
        # guard rejects it like any other non-fragment reference.
        tree = _svg_tree('<use href="data:image/png;base64,AAAA"/>')
        self.assertIn(
            "data:",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_passes_an_in_file_url_reference(self):
        # `fill="url(#id)"` names a same-document paint, so it is allowed.
        tree = _svg_tree('<rect id="center" fill="url(#gradient)"/>')
        assert_no_external_references(self, tree)

    def test_passes_a_quoted_padded_url_reference(self):
        tree = _svg_tree(
            "<rect id=\"center\" fill=\"url( '#gradient' )\"/>"
        )
        assert_no_external_references(self, tree)

    def test_catches_an_external_url_in_fill(self):
        # A `url(...)` target that is not a `#id` names another file, which
        # the copied install does not ship.
        tree = _svg_tree(
            '<rect id="center" fill="url(other.svg#gradient)"/>'
        )
        self.assertIn(
            "other.svg#gradient",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_catches_an_external_url_in_an_inline_style(self):
        tree = _svg_tree(
            '<rect id="center" style="filter:url(other.svg#blur)"/>'
        )
        self.assertIn(
            "other.svg#blur",
            _rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_data_uri_url(self):
        tree = _svg_tree(
            '<rect id="center" fill="url(data:image/svg+xml,x)"/>'
        )
        self.assertIn(
            "data:",
            _rejection_message(assert_no_external_references, tree),
        )


class TestUniqueIds(unittest.TestCase):
    def test_passes_a_tree_with_unique_ids(self):
        tree = _svg_tree(
            '<rect id="center"/><g id="top"><rect id="top-body"/></g>'
        )
        assert_unique_ids(self, tree)

    def test_passes_a_tree_whose_elements_have_no_ids(self):
        tree = _svg_tree("<rect/>")
        assert_unique_ids(self, tree)

    def test_catches_a_duplicate_id_naming_it(self):
        tree = _svg_tree('<rect id="center"/><rect id="center"/>')
        self.assertIn(
            "center",
            _rejection_message(assert_unique_ids, tree),
        )

    def test_catches_a_duplicate_id_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<rect id="center"/><g><rect id="center"/></g>'
        )
        self.assertIn(
            "center",
            _rejection_message(assert_unique_ids, tree),
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
        _assert_rejects(assert_slice_pixels, slices, "center", expected)

    def test_edge_band_pixels_pins_a_top_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"top": _horizontal_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "top", "top", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        _assert_rejects(
            assert_edge_band_pixels, slices, "top", "top", mirrored, size
        )

    def test_edge_band_pixels_pins_a_left_band_and_rejects_its_mirror(self):
        size = 6
        slices = {"left": _vertical_band(_EDGE_BAND, size)}
        assert_edge_band_pixels(self, slices, "left", "left", _EDGE_BAND, size)
        mirrored = tuple(reversed(_EDGE_BAND))
        _assert_rejects(
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
        _assert_rejects(
            assert_edge_bevels, broken_bottom, "", outward, mirrored, size
        )

        broken_left = _bevel_slices(outward, mirrored, size)
        broken_left["left"] = _vertical_band(mirrored, size)
        _assert_rejects(
            assert_edge_bevels, broken_left, "", outward, mirrored, size
        )

        broken_right = _bevel_slices(outward, mirrored, size)
        broken_right["right"] = _vertical_band(outward, size)
        _assert_rejects(
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
            _assert_rejects(
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
        _assert_rejects(assert_face_corners, broken, "state", corners)

    def test_center_tile_is_pins_the_full_square_and_its_size(self):
        colour = "#DDDDDD"
        slices = {"center": pixel_map((colour,) * 36, 6, 6)}
        assert_center_tile_is(self, slices, "center", colour, 6)
        # A 7x7 centre has the right colour everywhere but the wrong tile
        # size, which the declared-size pin must reject.
        bigger = {"center": pixel_map((colour,) * 49, 7, 7)}
        _assert_rejects(assert_center_tile_is, bigger, "center", colour, 6)

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
                _assert_rejects(
                    assert_face_bevel, broken_center, "", face, bevel,
                    size=size,
                )

                _, mirrored = face_edge_bands(face, bevel)
                broken_edge = _face_slices(face, bevel, size)
                broken_edge["top"] = _horizontal_band(mirrored, size)
                _assert_rejects(
                    assert_face_bevel, broken_edge, "", face, bevel,
                    size=size,
                )

                broken_corner = _face_slices(face, bevel, size)
                broken_corner["topleft"] = pixel_map(("#FFFFFF",) * 9, 3, 3)
                _assert_rejects(
                    assert_face_bevel, broken_corner, "", face, bevel,
                    size=size,
                )


if __name__ == "__main__":
    unittest.main()
