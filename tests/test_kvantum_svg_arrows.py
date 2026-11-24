"""Validate the org.macos8.desktop Kvantum SVG's indicator and tree-expander arrows.

The `arrow-<direction>-<state>` combo and scrollbar indicators and the
`arrow-minus/plus-<state>` tree-expander triangles of
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: each id is shipped,
each draws its pinned triangle, and each carries its per-state fill. The SVG's
other ids, shapes, palette and safety guards stay in `tests/test_kvantum_svg.py`.
"""

from __future__ import annotations

import os
import unittest

from support.kvantum_fixtures import SVG
from support.pin_registries import assert_registries_name_each_key_once
from support.svg_case import parse_svg
from svg_assertions import (
    attribute_values,
    children_named,
    elements_by_id,
)

ARROW_DIRECTIONS = ("up", "down", "left", "right")
ARROW_STATES = ("normal", "focused", "pressed", "disabled")

# Each indicator arrow is one 9x9 triangle whose `d` is the same in every
# state; only the disabled state greys its fill. The four `d` values are the
# up/down/left/right triangles, so pinning them by direction catches a path
# rotated or mirrored onto the wrong direction, which the id-only check above
# passes. The fills are pinned by state because #000000 and #999999 are both
# in the palette, so a disabled arrow painted black still passes the palette
# test.
ARROW_PATH_D = {
    "up": "M4.5,0 L9,9 L0,9 Z",
    "down": "M0,0 L9,0 L4.5,9 Z",
    "left": "M9,0 L9,9 L0,4.5 Z",
    "right": "M0,0 L9,4.5 L0,9 Z",
}
ARROW_FILL = {
    "normal": "#000000",
    "focused": "#000000",
    "pressed": "#000000",
    "disabled": "#999999",
}
# Kvantum's tree expander names its branch art `<element>-minus-<state>` for
# an open branch and `<element>-plus-<state>` for a closed one, not
# `arrow-<direction>-<state>`. The branch triangles reuse the grounded arrow
# paths: minus (open) points down and plus (closed) points right.
BRANCH_ARROW_PATH_D = {
    "minus": ARROW_PATH_D["down"],
    "plus": ARROW_PATH_D["right"],
}


class TestSvgArrows(unittest.TestCase):
    def setUp(self):
        self.tree = parse_svg(SVG)
        self.ids = attribute_values(self.tree, "id")

    def _assert_arrow_ids(self, variants, variant_label):
        """Assert every arrow-<variant>-<state> id is shipped.

        Drives both arrow groups the SVG ships under the `arrow-` prefix:
        the combo/scrollbar indicator's four directions and the tree
        expander's minus/plus shapes, labelled by *variant_label*.
        """
        for variant in variants:
            for state in ARROW_STATES:
                with self.subTest(**{variant_label: variant, "state": state}):
                    self.assertIn(f"arrow-{variant}-{state}", self.ids)

    def _assert_arrow_paths_painted(self, path_d_by_variant, variant_label):
        """Assert each arrow element paints exactly path_d_by_variant.

        Every arrow-<variant>-<state> element must hold one path child
        whose `d` equals path_d_by_variant's *variant* entry and whose
        fill equals ARROW_FILL's *state* entry.
        """
        by_id = elements_by_id(self.tree)
        for variant, path_d in path_d_by_variant.items():
            for state in ARROW_STATES:
                paths = children_named(
                    by_id[f"arrow-{variant}-{state}"], "path"
                )
                with self.subTest(**{variant_label: variant, "state": state}):
                    self.assertEqual(len(paths), 1)
                    self.assertEqual(paths[0].get("d"), path_d)
                    self.assertEqual(paths[0].get("fill"), ARROW_FILL[state])

    def test_indicator_arrows_ship_every_direction_and_state(self):
        self._assert_arrow_ids(ARROW_DIRECTIONS, "direction")

    def test_indicator_arrows_draw_the_pinned_triangle_and_fill(self):
        self._assert_arrow_paths_painted(ARROW_PATH_D, "direction")

    def test_branch_arrows_ship_every_shape_and_state(self):
        self._assert_arrow_ids(tuple(BRANCH_ARROW_PATH_D), "shape")

    def test_branch_arrows_draw_the_pinned_triangle_and_fill(self):
        self._assert_arrow_paths_painted(BRANCH_ARROW_PATH_D, "shape")


class TestRegistryKeys(unittest.TestCase):
    """Guard the pin registries against a merge that repeats a key.

    Each registry's consumer iterates ``.items()`` or indexes by state, so a
    duplicated key literal is legal Python that silently keeps the last pin
    and stops asserting the discarded entry's pins.
    """

    def test_the_pin_registries_name_each_key_exactly_once(self):
        assert_registries_name_each_key_once(
            self,
            os.path.abspath(__file__),
            ("ARROW_PATH_D", "ARROW_FILL", "BRANCH_ARROW_PATH_D"),
        )


if __name__ == "__main__":
    unittest.main()
