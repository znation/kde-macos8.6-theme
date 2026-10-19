"""Direct tests for ``svg_assertions.layout``'s layout and arc assertions.

Every desktop-theme widget test reaches these helpers only over its own
current artwork, so a helper that mis-orders a tile, drops a slice id or
misreads the canvas would weaken all of them at once. These tests prove each
assertion passes a correct layout and can actually fail a broken one. The
pixel-comparison assertions are tested in ``test_svg_assertions_pixels.py``,
and the document-safety guards (scripts, style elements, external references,
duplicate ids) in ``test_svg_assertions_safety.py``.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from support.error_assertions import assert_error_names, assert_rejects
from support.svg_fixtures import _svg_tree
from svg_assertions import (
    SLICE_IDS,
    assert_arcs_share_center,
    assert_bounds_rect,
    assert_diagonal_half_disc,
    assert_hint_geometry,
    assert_root_canvas,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    elements_by_id,
    path_arcs,
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
# The correct layout with the top tile moved off its margin hint.
_ORIGINS_TOP_MISPLACED = {**_ORIGINS, "top": (0, 0)}


# A hostile variant of _HINTS: the right and bottom margin rects sit at
# x=y=1000, so the canvas the hints imply is ~1004x1004 and the centre tile's
# region is ~996x996 -- far past the render cap, but small enough that the
# pre-cap code built the set without dying outright.
_HUGE_CANVAS_HINTS = (
    '<rect id="hint-tile-center" x="4" y="4" width="4" height="4"/>'
    '<rect id="hint-top-margin" x="4" y="0" width="4" height="4"/>'
    '<rect id="hint-bottom-margin" x="4" y="1000" width="4" height="4"/>'
    '<rect id="hint-left-margin" x="0" y="4" width="4" height="4"/>'
    '<rect id="hint-right-margin" x="1000" y="4" width="4" height="4"/>'
)


def _nine_slice_tree(origins=None, sizes=None, hints=_HINTS):
    """Build a nine-slice tree whose groups sit at *origins* with *sizes* rects.

    *origins* defaults to the layout the hints imply; *sizes* overrides a
    group's ``(width, height)``, so a caller can paint a slice outside its
    tile. *hints* is the margin-hint markup, so a caller can declare a
    hostile canvas.
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
        f"{hints}{groups}", width="12", height="12", viewBox="0 0 12 12"
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


def _bevel_half_disc(index, radius=16.0, center=(18.0, 18.0), rotated=False):
    """Return a ``<path>`` holding a raised-bevel half-disc arc.

    *index* selects the document-order half-disc (0 or 1); *rotated* puts its
    endpoints on the other diagonal, the defect `assert_diagonal_half_disc`
    must catch.
    """
    diagonal = radius / 2 ** 0.5
    cx, cy = center
    if rotated:
        start, end = (cx, cy - radius), (cx, cy + radius)
    else:
        start, end = (
            (cx - diagonal, cy + diagonal), (cx + diagonal, cy - diagonal)
        )
    if index:
        start, end = end, start
    return ET.fromstring(
        f'<path d="M {start[0]},{start[1]} A {radius},{radius} 0 0 1 '
        f'{end[0]},{end[1]}"/>'
    )


class TestStructuralGuards(unittest.TestCase):
    def test_tiles_placed_by_margins_passes_a_correct_layout(self):
        assert_tiles_placed_by_margins(self, _nine_slice_tree(), [""])

    def test_tiles_placed_by_margins_catches_a_misplaced_group(self):
        assert_rejects(
            assert_tiles_placed_by_margins,
            _nine_slice_tree(origins=_ORIGINS_TOP_MISPLACED),
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

    def test_slices_within_their_tiles_refuses_a_hostile_canvas(self):
        # A contributor-supplied SVG's margin hints set the canvas the guard
        # derives each tile region from; a hostile hint would make the region
        # set hold ~10^6 entries here (billions in a real attack) and exhaust
        # `make check`. The guard must refuse the geometry with a diagnostic
        # rather than allocate it.
        assert_error_names(
            self,
            ValueError,
            assert_slices_stay_within_their_tiles,
            self,
            _nine_slice_tree(hints=_HUGE_CANVAS_HINTS),
            [""],
            needles=("pixel limit",),
        )

    def test_tiles_placed_by_margins_uses_the_alias_hints(self):
        assert_tiles_placed_by_margins(
            self,
            _aliased_nine_slice_tree(),
            _ALIAS_PREFIXES,
            _ALIAS_HINT_MAP,
        )

    def test_tiles_placed_by_margins_catches_a_misplaced_alias_tile(self):
        assert_rejects(
            assert_tiles_placed_by_margins,
            _aliased_nine_slice_tree(alias_origins=_ORIGINS_TOP_MISPLACED),
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

    def test_diagonal_half_disc_passes_a_correct_arc(self):
        for index in (0, 1):
            with self.subTest(index=index):
                assert_diagonal_half_disc(
                    self, _bevel_half_disc(index), index, 16.0, (18.0, 18.0)
                )

    def test_diagonal_half_disc_catches_a_rotated_arc(self):
        assert_rejects(
            assert_diagonal_half_disc,
            _bevel_half_disc(0, rotated=True),
            0,
            16.0,
            (18.0, 18.0),
        )


class TestArcsShareCenter(unittest.TestCase):
    def test_passes_arcs_centred_on_the_expected_point(self):
        entries = list(path_arcs(_bevel_half_disc(0).get("d")))
        assert_arcs_share_center(self, entries, (18.0, 18.0))

    def test_rejects_an_elliptical_arc(self):
        # `arc_center` reconstructs a *circular* arc from rx alone, so an
        # ellipse's centre would be meaningless; the guard must reject it
        # rather than compare a value it cannot derive.
        entries = list(path_arcs("M 2,18 A 16,10 0 0 1 34,18"))
        assert_rejects(assert_arcs_share_center, entries, (18.0, 18.0))

    def test_rejects_an_arc_centred_elsewhere(self):
        entries = list(path_arcs("M 0,0 A 5,5 0 0 1 10,0"))
        assert_rejects(assert_arcs_share_center, entries, (18.0, 18.0))


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

    def test_origin_state_may_stop_short_of_a_taller_canvas(self):
        # A state at the origin of a canvas grown for a taller state ends
        # above the canvas bottom; listing it as an origin state accepts that,
        # while the taller prefixed state must still reach the edge.
        hints = (
            '<rect id="hint-right-margin" x="8" y="4" width="4" height="4"/>'
            '<rect id="hint-bottom-margin" x="4" y="8" width="4" height="4"/>'
            '<rect id="north-hint-right-margin" x="8" y="4" width="4" height="4"/>'
            '<rect id="north-hint-bottom-margin" x="4" y="18" width="4" height="4"/>'
        )
        tree = _root_canvas_tree(
            viewbox="0 0 12 22", height="22", hints=hints
        )
        assert_root_canvas(self, tree, 12, 22, origin_states=("",))
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, tree, 12, 22)
        with self.assertRaises(AssertionError):
            assert_root_canvas(self, tree, 12, 22, origin_states=("north",))


# One group carrying the invisible full-canvas bounds rect `assert_bounds_rect`
# reads; the rect itself is anonymous.
_BOUNDS_RECT_BODY = (
    '<g id="normal">'
    '<rect x="0" y="0" width="16" height="16" fill="none"/>'
    "</g>"
)


class TestBoundsRect(unittest.TestCase):
    def test_passes_a_group_with_one_matching_rect(self):
        # Positive control: the group holds exactly the expected rect, so the
        # guard must accept it.
        group = elements_by_id(_svg_tree(_BOUNDS_RECT_BODY))["normal"]
        assert_bounds_rect(self, group, ["0", "0", "16", "16", "none"])

    def test_rejects_a_group_with_no_rect(self):
        # Without the bounds rect KSvg scales the element by its artwork's
        # natural size instead of the cell, so the guard must fail.
        group = elements_by_id(_svg_tree('<g id="normal"/>'))["normal"]
        with self.assertRaises(AssertionError):
            assert_bounds_rect(self, group, ["0", "0", "16", "16", "none"])

    def test_rejects_a_group_with_a_second_rect(self):
        # A second rect adds to the composited bounds, so the guard must reject
        # the group even though the first rect matches.
        body = _BOUNDS_RECT_BODY.replace(
            "</g>", '<rect x="0" y="0" width="1" height="1"/></g>'
        )
        group = elements_by_id(_svg_tree(body))["normal"]
        with self.assertRaises(AssertionError):
            assert_bounds_rect(self, group, ["0", "0", "16", "16", "none"])

    def test_rejects_a_rect_with_a_wrong_fill(self):
        # The fill is part of the pinned tuple, so a recoloured bounds rect
        # fails even with the geometry unchanged.
        body = _BOUNDS_RECT_BODY.replace('fill="none"', 'fill="#000000"')
        group = elements_by_id(_svg_tree(body))["normal"]
        with self.assertRaises(AssertionError):
            assert_bounds_rect(self, group, ["0", "0", "16", "16", "none"])
