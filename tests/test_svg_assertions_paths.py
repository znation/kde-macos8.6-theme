"""Direct tests for ``svg_assertions.paths``'s helpers.

The path/arc readers turn artwork path markup into the arcs every widget
corner test compares against, so a mis-parse here would weaken them all.
"""

from __future__ import annotations

import unittest

from support.error_assertions import assert_error_names, error_message
from svg_assertions import arc_center, path_arcs


class TestPathArcs(unittest.TestCase):
    def test_tracks_the_current_point_through_commands(self):
        # An arc's start point is the current point the preceding M/L left, not
        # its own first coordinate pair; reading the wrong start moves the
        # reconstructed centre and the button corner test would measure the
        # wrong geometry.
        arcs = list(path_arcs("M1,1 L5,1 A2,2 0 0 1 9,5 L9,9 A2,2 0 0 0 5,9"))
        self.assertEqual(
            arcs,
            [
                ((5.0, 1.0), (2.0, 2.0, 0, 1), (9.0, 5.0)),
                ((9.0, 9.0), (2.0, 2.0, 0, 0), (5.0, 9.0)),
            ],
        )

    def test_z_yields_no_phantom_arc(self):
        # `Z` closes a subpath without drawing; reading it as an arc command
        # would yield a phantom arc, and the corner test would read a radius
        # that is not in the artwork.
        arcs = list(path_arcs("M1,1 A2,2 0 0 1 3,3 Z"))
        self.assertEqual(arcs, [((1.0, 1.0), (2.0, 2.0, 0, 1), (3.0, 3.0))])

    def test_z_returns_to_the_subpath_start(self):
        # `Z` closes the current subpath, so SVG moves the current point back
        # to that subpath's start. Ignoring it leaves the current point at the
        # last L/A endpoint, and an arc after `Z` is reconstructed from the
        # wrong start (a misplaced corner would still pass the pixel test).
        arcs = list(path_arcs("M1,1 L5,1 Z A2,2 0 0 1 9,5"))
        self.assertEqual(arcs, [((1.0, 1.0), (2.0, 2.0, 0, 1), (9.0, 5.0))])

    def test_z_does_not_leak_into_the_next_subpath(self):
        # A later `M` starts a new subpath, so the `Z` before it must not reset
        # the current point the new subpath's arc starts from.
        arcs = list(path_arcs("M1,1 L5,1 Z M7,7 A2,2 0 0 1 9,9"))
        self.assertEqual(arcs, [((7.0, 7.0), (2.0, 2.0, 0, 1), (9.0, 9.0))])

    def test_rejects_unsupported_path_commands(self):
        # H/V/C/Q/S/T and lowercase relative commands are not parsed. Before
        # the guard they folded into the preceding command's number body and
        # were read as extra coordinates (or raised a bare unpack error on a
        # later command), so pin the named rejection instead.
        for d in (
            "M0,0 H5",
            "M0,0 V5",
            "M0,0 C1,1 2,2 3,3",
            "M0,0 Q1,1 2,2",
            "m0,0 l5,5",
        ):
            with self.subTest(d=d):
                self.assertIn(
                    "unsupported SVG path command",
                    error_message(self, ValueError, list, path_arcs(d)),
                )

    def test_rejects_wrong_number_count_naming_the_command(self):
        # A command body with too few or too many numbers used to raise a bare
        # "not enough/too many values to unpack" that named neither the command
        # nor the path, so a malformed fixture was hard to locate. Pin the
        # named rejection instead.
        for d, command, count in (
            ("M1,1 A2,2 0 0 1", "A", 5),
            ("M1,1 A2,2 0 0 1 9,9 9", "A", 8),
            ("M1,1 2,2", "M", 4),
            ("M1,1 Z5", "Z", 1),
        ):
            with self.subTest(d=d):
                assert_error_names(
                    self,
                    ValueError,
                    list,
                    path_arcs(d),
                    needles=(f"command {command}", f"got {count}", repr(d)),
                )


class TestArcCenter(unittest.TestCase):
    def test_flags_select_the_side_of_the_chord(self):
        # Endpoints (0,3)->(3,0) at radius 3 admit two centres, (3,3) and
        # (0,0). The large-arc and sweep flags choose one; a flipped sign in
        # arc_center would place the centre on the wrong side and a corner arc
        # that curved the wrong way could still pass.
        start, end = (0.0, 3.0), (3.0, 0.0)
        for flags, expected in (
            ((0, 1), (3.0, 3.0)),
            ((0, 0), (0.0, 0.0)),
            ((1, 1), (0.0, 0.0)),
            ((1, 0), (3.0, 3.0)),
        ):
            with self.subTest(flags=flags):
                self.assertEqual(
                    arc_center(start, (3, 3, flags[0], flags[1]), end), expected
                )

    def test_zero_length_chord_names_the_arc(self):
        # start == end has no perpendicular bisector, so the centre is
        # undefined. Before the guard this was a bare ZeroDivisionError that
        # named neither the arc nor its defect.
        assert_error_names(
            self,
            ValueError,
            arc_center,
            (2.0, 2.0),
            (3, 3, 0, 1),
            (2.0, 2.0),
            needles=("(2.0, 2.0)", "zero-length chord"),
        )

    def test_radius_too_small_names_the_arc_and_the_chord(self):
        # Endpoints 6 apart need radius >= 3; a radius of 2 cannot reach both
        # and the square root would fail with "math domain error".
        assert_error_names(
            self,
            ValueError,
            arc_center,
            (0.0, 0.0),
            (2, 2, 0, 1),
            (6.0, 0.0),
            needles=("(0.0, 0.0)", "(6.0, 0.0)", "radius 2", "half its chord 3"),
        )


if __name__ == "__main__":
    unittest.main()
