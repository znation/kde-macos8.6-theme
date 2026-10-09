"""Shared structural checks for the nine-slice artwork tests.

Every nine-slice widget test asserts the same structural invariants: each
state's slice and margin-hint ids are present, each tile sits at the origin its
margins imply, no slice spills into a neighbouring tile, and the file carries no
`<script>`. Each subclass sets `SVG_PATH` and inherits those checks once; a
widget whose SVG prefixes its states (``normal-top``) also sets `PREFIXES`.
"""

from __future__ import annotations

from svg_case import SvgCase
from svg_assertions import (
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
)


class NineSliceCase(SvgCase):
    """Mixin: the structural checks shared by the nine-slice widgets.

    Subclasses set `SVG_PATH` to the widget SVG and `PREFIXES` to each state
    prefix in it (``("",)`` for an unprefixed SVG). A state that paints its
    own tiles but declares no margin hints of its own is listed in
    `HINT_ALIASES`, mapping it to the state whose hints size its tiles (the
    inactive Aurorae frame reuses the active one's). It is a plain mixin, not
    a `TestCase`, so importing it does not collect an unconfigured base. The
    widget's own pixel test pins the painted result; the checks here guard the
    structure that pixel test does not read. `SvgCase` parses `SVG_PATH` once
    per test into `self.tree`.
    """

    PREFIXES = ("",)
    HINT_ALIASES = {}
    # Id-bearing <g> groups that are not nine-slice tiles (a slider handle,
    # say), mapped to the origin each must sit at. `assert_tiles_placed_by_
    # margins` compares the full origin map, so without this the widget's own
    # non-tile groups would fail its tile-placement check.
    EXTRA_GROUPS = None

    def test_slice_ids_present(self):
        assert_slice_ids_present(
            self, self.tree, self.PREFIXES, self.HINT_ALIASES
        )

    def test_tiles_placed_by_margins(self):
        # The widget's pixel test composites each slice from its rects but
        # ignores the group's translate, so a group moved off its slice draws
        # from the wrong canvas region and still passes. Pin each tile's origin
        # against the margins that size the nine-slice.
        assert_tiles_placed_by_margins(
            self,
            self.tree,
            self.PREFIXES,
            self.HINT_ALIASES,
            self.EXTRA_GROUPS,
        )

    def test_tiles_stay_within_their_margins(self):
        # The widget's pixel test reads only points inside each tile, so an
        # oversized rect spilling into the neighbouring canvas region -- which
        # KSvg samples into that adjacent tile -- passes. Pin every slice to
        # the tile region its hints define.
        assert_slices_stay_within_their_tiles(
            self, self.tree, self.PREFIXES, self.HINT_ALIASES
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, self.tree)
