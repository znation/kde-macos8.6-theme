"""Direct tests for ``svg_assertions.nine_slice``'s helpers.

The margin, hint and tile-size arithmetic and the group-origin reader derive
the layout every widget test pins, so a wrong value here would weaken them all.
"""

from __future__ import annotations

import unittest

from support.svg_fixtures import _svg_tree
from svg_assertions import (
    nine_slice_hint_geometry,
    nine_slice_id_set,
    nine_slice_inset_hints,
    nine_slice_margins,
    nine_slice_rect_hint_geometry,
    nine_slice_tile_sizes,
    solid_tile,
    tile_origins,
)


class TestTileOrigins(unittest.TestCase):
    def test_reads_translates_and_surfaces_unparseable_transforms(self):
        tree = _svg_tree(
            '<g id="moved" transform="translate(3, 4)"/>'
            '<g id="at-origin"/>'
            '<g id="unknown" transform="matrix(1,0,0,1,9,9)"/>'
        )
        origins = tile_origins(tree)
        self.assertEqual(origins["moved"], (3, 4))
        self.assertEqual(origins["at-origin"], (0, 0))
        # A transform this helper cannot parse must come back as its raw text,
        # so the caller's equality check fails loudly instead of reading a
        # misplaced group as sitting at the origin.
        self.assertEqual(origins["unknown"], "matrix(1,0,0,1,9,9)")


class TestNineSliceMargins(unittest.TestCase):
    def test_derives_the_four_margins_from_a_centred_tile(self):
        # KSvg reads these four hint rects to size the nine-slice, so a wrong
        # coordinate here would make every widget test pin the wrong layout.
        # Pin a 3px-border/6px-tile layout and a differently sized one, plus
        # the unprefixed form (``""``) whose values match the _HINTS fixture
        # above (a 4px border around a 4px tile on the 12x12 canvas).
        self.assertEqual(
            nine_slice_margins("normal", 3, 6),
            {
                "normal-hint-top-margin": ("3", "0", "6", "3"),
                "normal-hint-bottom-margin": ("3", "9", "6", "3"),
                "normal-hint-left-margin": ("0", "3", "3", "6"),
                "normal-hint-right-margin": ("9", "3", "3", "6"),
            },
        )
        self.assertEqual(
            nine_slice_margins("focus", 2, 8),
            {
                "focus-hint-top-margin": ("2", "0", "8", "2"),
                "focus-hint-bottom-margin": ("2", "10", "8", "2"),
                "focus-hint-left-margin": ("0", "2", "2", "8"),
                "focus-hint-right-margin": ("10", "2", "2", "8"),
            },
        )
        self.assertEqual(
            nine_slice_margins("", 4, 4),
            {
                "hint-top-margin": ("4", "0", "4", "4"),
                "hint-bottom-margin": ("4", "8", "4", "4"),
                "hint-left-margin": ("0", "4", "4", "4"),
                "hint-right-margin": ("8", "4", "4", "4"),
            },
        )


class TestNineSliceHintGeometry(unittest.TestCase):
    def test_pins_the_shared_centre_plus_every_state_s_margins(self):
        # Every widget's hint-geometry test compares this helper's dict against
        # the SVG's parsed hints, so a wrong centre coordinate here would make
        # them all pin the wrong layout. The unprefixed 4px-border/4px-tile
        # layout must match the _HINTS fixture exactly.
        self.assertEqual(
            nine_slice_hint_geometry([""], 4, 4),
            {
                "hint-tile-center": ("4", "4", "4", "4"),
                "hint-top-margin": ("4", "0", "4", "4"),
                "hint-bottom-margin": ("4", "8", "4", "4"),
                "hint-left-margin": ("0", "4", "4", "4"),
                "hint-right-margin": ("8", "4", "4", "4"),
            },
        )
        # Several states share the one centre hint, so the helper must merge
        # each prefix's margins beside it without dropping the earlier ones.
        self.assertEqual(
            nine_slice_hint_geometry(("normal", "pressed"), 3, 6),
            {
                "hint-tile-center": ("3", "3", "6", "6"),
                **nine_slice_margins("normal", 3, 6),
                **nine_slice_margins("pressed", 3, 6),
            },
        )


class TestNineSliceRectHintGeometry(unittest.TestCase):
    def test_wraps_a_rectangular_centre_with_unequal_borders(self):
        # The pager's 1px border around a 10x7 centre tests the width and
        # height are not swapped; unequal borders test the x and y insets.
        self.assertEqual(
            nine_slice_rect_hint_geometry(("normal",), 2, 3, 10, 7),
            {
                "hint-tile-center": ("2", "3", "10", "7"),
                "normal-hint-top-margin": ("2", "0", "10", "3"),
                "normal-hint-bottom-margin": ("2", "10", "10", "3"),
                "normal-hint-left-margin": ("0", "3", "2", "7"),
                "normal-hint-right-margin": ("12", "3", "2", "7"),
            },
        )

    def test_agrees_with_the_square_helper_on_a_square_centre(self):
        self.assertEqual(
            nine_slice_rect_hint_geometry(("a", "b"), 3, 3, 6, 6),
            nine_slice_hint_geometry(("a", "b"), 3, 6),
        )


class TestNineSliceInsetHints(unittest.TestCase):
    def test_derives_the_four_insets_from_the_centre_tile(self):
        # The background and tooltip tests build their inset band here, so a
        # wrong coordinate would make both pin the wrong fillable area. A 3px
        # border around a 10px tile puts the band's far edge at 16.
        self.assertEqual(
            nine_slice_inset_hints("", 3, 10, 10),
            {
                "hint-top-inset": ("3", "0", "10", "0"),
                "hint-bottom-inset": ("3", "16", "10", "0"),
                "hint-left-inset": ("0", "3", "0", "10"),
                "hint-right-inset": ("16", "3", "0", "10"),
            },
        )

    def test_prefixes_the_ids_and_stretches_a_non_square_tile(self):
        # The menu bar's `north` state has a taller centre tile, so the
        # left/right insets span its height while the top/bottom span its
        # width; the prefix keeps the two states' ids apart.
        self.assertEqual(
            nine_slice_inset_hints("north", 2, 8, 18),
            {
                "north-hint-top-inset": ("2", "0", "8", "0"),
                "north-hint-bottom-inset": ("2", "22", "8", "0"),
                "north-hint-left-inset": ("0", "2", "0", "18"),
                "north-hint-right-inset": ("12", "2", "0", "18"),
            },
        )


class TestNineSliceTileSizes(unittest.TestCase):
    def test_derives_each_tile_from_the_borders_and_canvas(self):
        # assert_slices_stay_within_their_tiles and the list-item test both
        # build their tile map here, so a wrong edge or centre size would make
        # both pin the wrong regions. The 12x12 canvas with 4px borders matches
        # the _HINTS fixture: every tile is 4x4.
        self.assertEqual(
            nine_slice_tile_sizes(12, 12, 4, 4, 4, 4),
            {
                "top": (4, 4),
                "bottom": (4, 4),
                "left": (4, 4),
                "right": (4, 4),
                "center": (4, 4),
                "topleft": (4, 4),
                "topright": (4, 4),
                "bottomleft": (4, 4),
                "bottomright": (4, 4),
            },
        )
        # Distinct borders (left 2, right 4, top 3, bottom 5 on a 16x10 canvas)
        # must stretch each edge tile by canvas minus its two opposite borders,
        # not to a shared size.
        self.assertEqual(
            nine_slice_tile_sizes(16, 10, 2, 4, 3, 5),
            {
                "top": (10, 3),
                "bottom": (10, 5),
                "left": (2, 2),
                "right": (4, 2),
                "center": (10, 2),
                "topleft": (2, 3),
                "topright": (4, 3),
                "bottomleft": (2, 5),
                "bottomright": (4, 5),
            },
        )


class TestSolidTile(unittest.TestCase):
    def test_paints_the_named_tile_with_its_own_size(self):
        sizes = nine_slice_tile_sizes(16, 10, 2, 4, 3, 5)
        # The top edge is 10x3 here, not the corner or centre size.
        self.assertEqual(
            solid_tile(sizes, "top", "#123456"),
            {(x, y): "#123456" for x in range(10) for y in range(3)},
        )

    def test_unknown_tile_name_raises(self):
        sizes = nine_slice_tile_sizes(12, 12, 4, 4, 4, 4)
        with self.assertRaises(KeyError):
            solid_tile(sizes, "middle", "#000000")


class TestNineSliceIdSet(unittest.TestCase):
    def test_lists_the_shared_centre_hint_and_each_prefix_s_margins_and_slices(self):
        slices = {
            "center", "top", "bottom", "left", "right",
            "topleft", "topright", "bottomleft", "bottomright",
        }
        expected = {"hint-tile-center"}
        for prefix in ("normal", "hover"):
            expected |= {f"{prefix}-hint-{side}-margin" for side in ("top", "bottom", "left", "right")}
            expected |= {f"{prefix}-{name}" for name in slices}
        self.assertEqual(nine_slice_id_set(("normal", "hover")), expected)

    def test_adds_extra_ids_and_no_prefixes_leaves_only_the_centre_hint(self):
        self.assertEqual(nine_slice_id_set((), ["arrow"]), {"hint-tile-center", "arrow"})


if __name__ == "__main__":
    unittest.main()
