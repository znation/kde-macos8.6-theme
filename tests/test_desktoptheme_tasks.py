"""Tests for the desktop theme's tasks.svg Task Manager task background."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import TASKS_SVG
from support.nine_slice_case import NineSliceCase
from svg_assertions import (
    SLICE_IDS,
    assert_slice_pixels,
    assert_slices_have_no_fill,
    assert_slices_uniform,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
    nine_slice_rect_hint_geometry,
    nine_slice_tile_sizes,
    pixel_map,
    rect_geometry,
    render_slices,
    solid_tile,
)

LEFT = RIGHT = 7
TOP = BOTTOM = 3
TILE = 6
SIZES = nine_slice_tile_sizes(20, 12, LEFT, RIGHT, TOP, BOTTOM)

PREFIXES = ("normal", "hover", "focus", "attention", "minimized", "progress")
EXPANDER_IDS = {
    "group-expander-top": "M1 6 L4 3 L7 6 Z",
    "group-expander-bottom": "M1 2 L4 5 L7 2 Z",
    "group-expander-left": "M6 1 L3 4 L6 7 Z",
    "group-expander-right": "M2 1 L5 4 L2 7 Z",
}
EXPANDER_ORIGINS = {name: (0, 0) for name in EXPANDER_IDS}
TRANSPARENT_TILES = (
    "top",
    "left",
    "right",
    "center",
    "topleft",
    "topright",
)
RULE_TILES = ("bottom", "bottomleft", "bottomright")


def expected_id_set():
    """Return the exact id set the Task Manager's KSvg lookups require."""
    ids = {"hint-tile-center"} | set(EXPANDER_IDS)
    for prefix in PREFIXES:
        ids.update(
            f"{prefix}-hint-{side}-margin"
            for side in ("top", "bottom", "left", "right")
        )
        ids.update(f"{prefix}-{name}" for name in SLICE_IDS)
    return ids


def bottom_rule_tile(name, colour):
    """Return tile *name* with its bottom two rows *colour* and the top row empty."""
    width, height = SIZES[name]
    return pixel_map(
        (None,) * width + (colour,) * (width * (height - 1)),
        width,
        height,
    )


class TestTasks(NineSliceCase, unittest.TestCase):
    SVG_PATH = TASKS_SVG
    PREFIXES = PREFIXES
    EXTRA_GROUPS = EXPANDER_ORIGINS

    def test_tasks_declares_exactly_the_kde_required_ids(self):
        # Task.qml, TaskProgressOverlay.qml and GroupExpanderOverlay.qml
        # resolve these ids directly, so a missing one leaves a task face or
        # arrow undrawn and an extra one is art nothing reads.
        self.assertEqual(attribute_values(self.tree, "id"), expected_id_set())

    def test_tasks_hint_geometry(self):
        # Every state shares the menubaritem nine-slice: a 7px left/right and
        # 3px top/bottom border around a 6x6 centre on the 20x12 canvas.
        self.assertEqual(
            rect_geometry(self.tree),
            nine_slice_rect_hint_geometry(PREFIXES, 7, 3, 6, 6),
        )

    def test_tasks_normal_is_transparent(self):
        # An idle task shows the menu-bar face, so normal carries only the
        # 0.01-opacity placeholders that supply the margins.
        assert_slices_have_no_fill(self, self.tree, "normal")
        slices = render_slices(self.tree)
        for name in SIZES:
            assert_slice_pixels(
                self, slices, f"normal-{name}", solid_tile(SIZES, name, None)
            )

    def test_tasks_hover_focus_and_attention_are_flat(self):
        # Hover and focus paint the selection fill; attention paints the
        # tooltip fill. Compare every tile's exact region, not just the
        # pixels the artwork happens to cover, so a short rect fails too.
        slices = render_slices(self.tree)
        for prefix, colour in (
            ("hover", "#CCCCFF"),
            ("focus", "#CCCCFF"),
            ("attention", "#FFFFCC"),
        ):
            assert_slices_uniform(self, slices, prefix, colour)
            for name in SIZES:
                assert_slice_pixels(
                    self,
                    slices,
                    f"{prefix}-{name}",
                    solid_tile(SIZES, name, colour),
                )

    def test_tasks_minimized_and_progress_paint_a_bottom_rule(self):
        # The minimized task keeps the transparent face and gains a 2px
        # #999999 rule in the bottom band; progress gains the same rule in
        # #CCCCFF. The rule is local y=1..2 within the 3px band, leaving a
        # transparent row above it.
        slices = render_slices(self.tree)
        for prefix, colour in (
            ("minimized", "#999999"),
            ("progress", "#CCCCFF"),
        ):
            for name in TRANSPARENT_TILES:
                assert_slice_pixels(
                    self,
                    slices,
                    f"{prefix}-{name}",
                    solid_tile(SIZES, name, None),
                )
            for name in RULE_TILES:
                assert_slice_pixels(
                    self,
                    slices,
                    f"{prefix}-{name}",
                    bottom_rule_tile(name, colour),
                )

    def test_tasks_group_expanders_are_black_triangles(self):
        # GroupExpanderOverlay.qml names each edge's triangle directly, so
        # pin the path and the white-free black fill of all four.
        by_id = elements_by_id(self.tree)
        for name, path in EXPANDER_IDS.items():
            with self.subTest(element=name):
                group = by_id[name]
                self.assertEqual(local_name(group), "g")
                paths = children_named(group, "path")
                self.assertEqual(len(paths), 1)
                self.assertEqual(paths[0].get("d"), path)
                self.assertEqual(paths[0].get("fill"), "#000000")

    def test_tasks_colours(self):
        # The painted slices use only the grounded selection, tooltip and
        # bevel tokens plus black for the expander arrows; the placeholders
        # carry #FFFFFF in `style` so they stay out of the fill set.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {"#CCCCFF", "#FFFFCC", "#999999", "#000000"},
        )


if __name__ == "__main__":
    unittest.main()
