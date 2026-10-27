"""Tests for the desktop theme's timer.svg Timer plasmoid LCD digits."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import TIMER_SVG
from support.svg_case import SvgCase
from svg_assertions import (
    assert_bounds_rect,
    assert_no_script_elements,
    circle_geometry_and_fill,
    children_named,
    elements_by_id,
    local_name,
)

# The seven-segment lit-set table, recorded verbatim from the plan: each
# digit names its lit segments in the order the path draws them.
SEGMENTS = {
    "a": (3, 5, 13, 5),
    "b": (13, 5, 13, 15),
    "c": (13, 17, 13, 27),
    "d": (3, 27, 13, 27),
    "e": (3, 17, 3, 27),
    "f": (3, 5, 3, 15),
    "g": (3, 16, 13, 16),
}
DIGIT_SEGMENTS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abfgcd",
}


def expected_d(digit, ox, oy):
    """Re-derive a digit's stroke-only ``d`` from the pinned segment endpoints.

    Each lit segment contributes one ``M x1,y1 L x2,y2`` move, offset into the
    digit's own cell by ``(ox, oy)``: KSvg extracts an element's artwork from
    its region of the canvas, so a path left in the (0, 0) cell would never
    draw inside a cell further along the row.
    """
    return " ".join(
        "M %d,%d L %d,%d" % (
            SEGMENTS[s][0] + ox, SEGMENTS[s][1] + oy,
            SEGMENTS[s][2] + ox, SEGMENTS[s][3] + oy,
        )
        for s in DIGIT_SEGMENTS[digit]
    )


class TestTimer(SvgCase, unittest.TestCase):
    SVG_PATH = TIMER_SVG

    def test_timer_declares_exactly_the_kde_required_ids(self):
        # TimerEdit.qml requests num + digitSuffix and "separator" +
        # digitSuffix, where digitSuffix is "" normally and "_1" in alert
        # mode, so the file needs exactly these twenty-two ids and no
        # others (the default theme's separatorB/separatorC ids are
        # legacy this plasmoid never requests). The order is canvas order:
        # the normal row, then the alert row, then the two separators.
        expected = (
            [str(i) for i in range(10)]
            + ["%d_1" % i for i in range(10)]
            + ["separator", "separator_1"]
        )
        ids = [
            element.get("id")
            for element in self.tree.iter()
            if local_name(element) == "g" and element.get("id")
        ]
        self.assertEqual(ids, expected)
        self.assertEqual(set(elements_by_id(self.tree)), set(expected))
        assert_no_script_elements(self, self.tree)

    def test_digits_are_seven_segment_paths(self):
        # The SvgItem renders each digit at a 1:2 wide:tall aspect, so every
        # digit cell is 16x32: the normal row at y=0, the alert row at
        # y=32. The invisible full-cell bounds rect pins the element's
        # natural size (the checkmarks.svg convention), and the glyph is a
        # stroke-only seven-segment path re-derived from the pinned
        # segment endpoints, so a segment moved or dropped fails here.
        by_id = elements_by_id(self.tree)
        for row_y, suffix in ((0, ""), (32, "_1")):
            for i in range(10):
                group = by_id["%d%s" % (i, suffix)]
                self.assertEqual(local_name(group), "g")
                assert_bounds_rect(
                    self, group,
                    [str(16 * i), str(row_y), "16", "32", "none"],
                )
                paths = children_named(group, "path")
                self.assertEqual(len(paths), 1)
                self.assertEqual(
                    paths[0].get("d"),
                    expected_d(str(i), 16 * i, row_y),
                )
                self.assertEqual(paths[0].get("fill"), "none")
                # The 2px square caps are what make the segments meet
                # without gaps at the corners; a round or butt cap would
                # leave notches between the lit segments.
                self.assertEqual(paths[0].get("stroke-width"), "2")
                self.assertEqual(paths[0].get("stroke-linecap"), "square")

    def test_normal_digits_are_black_and_alert_digits_are_the_negative_red(self):
        # Colour provenance: the normal row strokes #000000, the scheme's
        # [Colors:Tooltip] ForegroundNormal=0,0,0, and the alert row (the
        # "_1" digits, plus separator_1 pinned by the separator test)
        # strokes #CC0000, ForegroundNegative=204,0,0, both from
        # theme/color-schemes/MacOS8.colors. Pinning the split here makes a
        # future edit re-ground it deliberately.
        by_id = elements_by_id(self.tree)
        for i in range(10):
            normal = children_named(by_id[str(i)], "path")
            self.assertEqual(len(normal), 1)
            self.assertEqual(normal[0].get("stroke"), "#000000")
            alert = children_named(by_id["%d_1" % i], "path")
            self.assertEqual(len(alert), 1)
            self.assertEqual(alert[0].get("stroke"), "#CC0000")

    def test_separators_are_black_colon_dots(self):
        # Each separator is an 8x32 cell holding exactly two filled colon
        # dots at (cx=164, cy=row+10 and row+22, r=1.5): an element can
        # silently gain or lose a dot only by failing this test.
        by_id = elements_by_id(self.tree)
        for group_id, row_y, fill in (
            ("separator", 0, "#000000"),
            ("separator_1", 32, "#CC0000"),
        ):
            group = by_id[group_id]
            self.assertEqual(local_name(group), "g")
            assert_bounds_rect(
                self, group, ["160", str(row_y), "8", "32", "none"],
            )
            circles = children_named(group, "circle")
            self.assertEqual(len(circles), 2)
            self.assertEqual(
                circle_geometry_and_fill(circles[0]),
                (164.0, row_y + 10.0, 1.5, fill),
            )
            self.assertEqual(
                circle_geometry_and_fill(circles[1]),
                (164.0, row_y + 22.0, 1.5, fill),
            )


if __name__ == "__main__":
    unittest.main()
