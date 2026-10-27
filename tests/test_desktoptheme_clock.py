"""Tests for the desktop theme's clock.svg analog clock face."""

from __future__ import annotations

import re
import unittest

from support.desktoptheme_paths import CLOCK_SVG
from support.svg_case import SvgCase
from svg_assertions import (
    assert_bounds_rect,
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
)

# The analog clock plasmoid (org.kde.plasma.analogclock) requests these
# nine element ids from imagePath "widgets/clock" (read 2026-10-27 from
# the installed plasmoid's main.qml); the canvas order below is the
# left-to-right column order of the 528x96 canvas.
CLOCK_IDS = (
    "ClockFace",
    "HandCenterScrew",
    "HourHandShadow",
    "HourHand",
    "MinuteHandShadow",
    "MinuteHand",
    "SecondHandShadow",
    "SecondHand",
    "Glass",
)

# Every hand: its pinned square bounds rect, its single shaft's pinned
# endpoints, and its stroke width. The pivot is each rect's centre (the
# plasmoid's Hand.qml fallback when no rotation-center hint is shipped),
# the tail is 12 above the pivot, and the tip -- the lower endpoint --
# ends half a stroke width short of the rect's lower edge so the square
# cap lands exactly on it.
HANDS = {
    "HourHand": (
        ("140", "0", "56", "56"),
        "M 168,54 L 168,16",
        "4",
    ),
    "MinuteHand": (
        ("220", "0", "88", "88"),
        "M 264,86.5 L 264,32",
        "3",
    ),
    "SecondHand": (
        ("332", "0", "88", "88"),
        "M 376,87 L 376,32",
        "2",
    ),
}

# The three shadow groups and Glass hold only their invisible bounds
# rects: the flat theme draws no drop shadows and no glass sheen.
EMPTY_IDS = {
    "HourHandShadow": ("124", "0", "8", "8"),
    "MinuteHandShadow": ("204", "0", "8", "8"),
    "SecondHandShadow": ("316", "0", "8", "8"),
    "Glass": ("432", "0", "96", "96"),
}

# The twelve hour-tick angles, compared as integers; the 0 tick is the
# one path written bare (no rotate(0) wrapper).
TICK_ANGLES = frozenset(range(0, 360, 30))
ROTATE = re.compile(r"^rotate\((\d+) 48 48\)$")
SHAFT = re.compile(r"^M ([\d.]+),([\d.]+) L ([\d.]+),([\d.]+)$")


def tick_angles(clock_face):
    """Return each tick path in *clock_face* as (angle, path element).

    A tick is either a bare path child (the 0 tick) or a path inside a
    wrapper group whose transform is ``rotate(θ 48 48)``; the pivot is
    the face circle's centre at (48, 48).
    """
    entries = []
    for child in clock_face:
        name = local_name(child)
        if name == "path":
            entries.append((0, child))
        elif name == "g":
            match = ROTATE.match(child.get("transform", ""))
            entries.append((int(match.group(1)), children_named(child, "path")[0]))
    return entries


class TestClock(SvgCase, unittest.TestCase):
    SVG_PATH = CLOCK_SVG

    def test_clock_declares_exactly_the_nine_kde_required_ids(self):
        # The plasmoid's main.qml names exactly these nine ids; an id it
        # does not request is dead art, and a missing one falls back to
        # Breeze. Pin the id set and the canvas order exactly, and pin
        # the hint-id absence: Hand.qml queries
        # hint-<hand>[shadow]-rotation-center-offset (six) and main.qml
        # probes hint-hands-shadow-offset-to-west/north/south and
        # hint-hands-shadows-offset-to-east; shipping
        # none keeps the plasmoid on its harmless fallbacks (0 shadow
        # offsets, rotation centres at the hand rects' centres).
        assert_ids_present(self, self.tree, CLOCK_IDS)
        ids = [element.get("id") for element in elements_by_id(self.tree).values()]
        self.assertEqual(tuple(ids), CLOCK_IDS)
        self.assertFalse([i for i in ids if i.startswith("hint-")])
        assert_no_script_elements(self, self.tree)

    def test_face_is_white_ring_and_twelve_hour_ticks(self):
        # ClockFace holds its invisible bounds rect, the white face
        # circle ringed by the etched separator's #888888 (its light
        # half is left off: 1px light on a curve is noise), and exactly
        # twelve 2px black hour ticks around the pivot (48, 48), one per
        # angle 0 to 330 in steps of 30.
        by_id = elements_by_id(self.tree)
        face = by_id["ClockFace"]
        self.assertEqual(local_name(face), "g")
        assert_bounds_rect(self, face, ["0", "0", "96", "96", "none"])

        circles = children_named(face, "circle")
        self.assertEqual(len(circles), 1)
        circle = circles[0]
        self.assertEqual(circle.get("cx"), "48")
        self.assertEqual(circle.get("cy"), "48")
        self.assertEqual(circle.get("r"), "47")
        self.assertEqual(circle.get("fill"), "#FFFFFF")
        self.assertEqual(circle.get("stroke"), "#888888")
        self.assertEqual(circle.get("stroke-width"), "1")

        entries = tick_angles(face)
        self.assertEqual(sorted(angle for angle, _ in entries), sorted(TICK_ANGLES))
        for angle, path in entries:
            with self.subTest(angle=angle):
                self.assertEqual(path.get("d"), "M 48,5 L 48,12")
                self.assertEqual(path.get("stroke"), "#000000")
                self.assertEqual(path.get("stroke-width"), "2")

    def test_hands_are_single_point_down_shafts(self):
        # Each hand is one stroke-only shaft in its pinned square bounds
        # rect: the lower endpoint (the tip) at half a stroke width
        # short of the rect's lower edge, the upper endpoint (the tail)
        # 12 above the pivot at the rect's centre. The point-down
        # neutral is KDE-required: Hand.qml rotates 180 + <angle>, so a
        # rotation-0 hand pointing down stands up at 12 o'clock.
        by_id = elements_by_id(self.tree)
        for name, (bounds, d, width) in HANDS.items():
            with self.subTest(hand=name):
                element = by_id[name]
                self.assertEqual(local_name(element), "g")
                assert_bounds_rect(
                    self, element, list(bounds) + ["none"]
                )
                paths = children_named(element, "path")
                self.assertEqual(len(paths), 1)
                path = paths[0]
                self.assertEqual(path.get("d"), d)
                self.assertEqual(path.get("stroke-width"), width)
                # Re-derive the geometry contract the d string pins:
                # a square cap overhangs each endpoint by half the
                # stroke width, so the tip (the lower endpoint) sits
                # half a width above the rect's lower edge to land the
                # cap exactly on it, and the tail stays 12 above the
                # pivot at the rect's centre.
                x1, y1, x2, y2 = SHAFT.match(d).groups()
                width_value = float(width)
                self.assertEqual(float(x1), float(x2))
                bottom = float(bounds[1]) + float(bounds[3])
                self.assertEqual(
                    max(float(y1), float(y2)) + width_value / 2, bottom
                )
                pivot = float(bounds[1]) + float(bounds[3]) / 2
                self.assertEqual(min(float(y1), float(y2)), pivot - 12)
                self.assertEqual(path.get("stroke-linecap"), "square")
                self.assertEqual(path.get("fill"), "none")

    def test_second_hand_publishes_the_negative_red(self):
        # The second hand strokes #CC0000, the colour scheme's
        # ForegroundNegative=204,0,0 (theme/color-schemes/MacOS8.colors,
        # the same token the timer.svg alert digits reuse), while the
        # hour and minute hands stroke #000000 from
        # ForegroundNormal=0,0,0 (the checkmarks black), so a future
        # edit re-grounds either deliberately rather than drifting.
        by_id = elements_by_id(self.tree)
        for name, stroke in (
            ("HourHand", "#000000"),
            ("MinuteHand", "#000000"),
            ("SecondHand", "#CC0000"),
        ):
            path = children_named(by_id[name], "path")[0]
            self.assertEqual(path.get("stroke"), stroke)

    def test_shadows_and_glass_draw_nothing(self):
        # The three shadow groups and Glass hold only their invisible
        # fill="none" bounds rects at the pinned rects, so the flat
        # theme cannot silently grow drop shadows or a glass sheen.
        by_id = elements_by_id(self.tree)
        for name, bounds in EMPTY_IDS.items():
            with self.subTest(element=name):
                element = by_id[name]
                self.assertEqual(local_name(element), "g")
                self.assertEqual(
                    [local_name(child) for child in element], ["rect"]
                )
                assert_bounds_rect(self, element, list(bounds) + ["none"])

    def test_only_the_face_and_screw_are_filled(self):
        # Every fill in the file is one of the invisible bounds rects'
        # `none`, the face's white, or the screw's black, so no gradient
        # or extra shape can creep in.
        self.assertEqual(
            attribute_values(self.tree, "fill"), {"none", "#FFFFFF", "#000000"}
        )


if __name__ == "__main__":
    unittest.main()
