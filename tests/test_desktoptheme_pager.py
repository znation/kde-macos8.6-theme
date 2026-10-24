"""Tests for the desktop theme's pager.svg virtual-desktop pager cell."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import PAGER_SVG
from support.nine_slice_case import NineSliceCase
from svg_assertions import (
    SLICE_IDS,
    assert_slice_pixels,
    attribute_values,
    children_named,
    elements_by_id,
    nine_slice_rect_hint_geometry,
    nine_slice_tile_sizes,
    rect_geometry,
    render_slices,
    solid_tile,
)

LEFT = RIGHT = TOP = BOTTOM = 1
SIZES = nine_slice_tile_sizes(12, 9, LEFT, RIGHT, TOP, BOTTOM)

PREFIXES = ("normal", "hover", "active")
BORDER_TILES = tuple(name for name in SIZES if name != "center")


def expected_id_set():
    """Return the exact id set the Pager's KSvg lookups require."""
    ids = {"hint-tile-center"}
    for prefix in PREFIXES:
        ids.update(
            f"{prefix}-hint-{side}-margin"
            for side in ("top", "bottom", "left", "right")
        )
        ids.update(f"{prefix}-{name}" for name in SLICE_IDS)
    return ids


class TestPager(NineSliceCase, unittest.TestCase):
    SVG_PATH = PAGER_SVG
    PREFIXES = PREFIXES

    def test_pager_declares_exactly_the_kde_required_ids(self):
        # The Pager's main.qml resolves these ids directly, so a missing one
        # leaves a desktop cell or its margins undrawn and an extra one is art
        # nothing reads.
        self.assertEqual(attribute_values(self.tree, "id"), expected_id_set())

    def test_pager_hint_geometry(self):
        # Every state shares the same cell: a 1px border around a 10x7 centre
        # tile on the 12x9 canvas.
        self.assertEqual(
            rect_geometry(self.tree),
            nine_slice_rect_hint_geometry(PREFIXES, 1, 1, 10, 7),
        )

    def test_pager_normal_outlines_an_idle_desktop(self):
        # An idle desktop is a thin #999999 outline on the panel face, so the
        # eight border tiles paint and the centre stays a transparent
        # placeholder that only carries the margins.
        slices = render_slices(self.tree)
        for name in BORDER_TILES:
            assert_slice_pixels(
                self, slices, f"normal-{name}", solid_tile(SIZES, name, "#999999")
            )
        assert_slice_pixels(
            self, slices, "normal-center", solid_tile(SIZES, "center", None)
        )

    def test_pager_state_centres_stay_translucent(self):
        # The Pager draws each desktop's window previews in `clipRect` at
        # z:1 and the frames above it (z:2-4), so an opaque centre would
        # hide the preview on the hovered and current desktops. The hover and
        # active centres carry the installed default theme's centre opacities;
        # normal stays the transparent 0.01 placeholder.
        by_id = elements_by_id(self.tree)
        expected = {
            "normal-center": (None, "0.01"),
            "hover-center": ("#EEEEEE", "0.2"),
            "active-center": ("#CCCCFF", "0.6"),
        }
        for group_id, (fill, opacity) in expected.items():
            with self.subTest(slice=group_id):
                centre = children_named(by_id[group_id], "rect")[0]
                self.assertEqual(centre.get("fill"), fill)
                self.assertEqual(centre.get("fill-opacity"), opacity)
        # Only the centres are translucent; every border tile stays opaque.
        self.assertEqual(
            attribute_values(self.tree, "fill-opacity"),
            {"0.01", "0.2", "0.6"},
        )

    def test_pager_hover_fills_the_view_trough(self):
        # Hover keeps the #999999 outline but paints the centre with the pale
        # grey view trough. The pixel map reads only the fill attribute; the
        # centre's 0.2 opacity is pinned by the translucency test.
        slices = render_slices(self.tree)
        for name in BORDER_TILES:
            assert_slice_pixels(
                self, slices, f"hover-{name}", solid_tile(SIZES, name, "#999999")
            )
        assert_slice_pixels(
            self, slices, "hover-center", solid_tile(SIZES, "center", "#EEEEEE")
        )

    def test_pager_active_fills_the_selection(self):
        # The current desktop is a black-outlined #CCCCFF selection cell. The
        # pixel map reads only the fill attribute; the centre's 0.6 opacity is
        # pinned by the translucency test.
        slices = render_slices(self.tree)
        for name in BORDER_TILES:
            assert_slice_pixels(
                self, slices, f"active-{name}", solid_tile(SIZES, name, "#000000")
            )
        assert_slice_pixels(
            self, slices, "active-center", solid_tile(SIZES, "center", "#CCCCFF")
        )

    def test_pager_colours(self):
        # The painted slices use only the grounded outline, trough, black and
        # selection tokens; the normal placeholder carries #FFFFFF in `style`
        # so it stays out of the parsed fill set.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {"#000000", "#999999", "#CCCCFF", "#EEEEEE"},
        )


if __name__ == "__main__":
    unittest.main()
