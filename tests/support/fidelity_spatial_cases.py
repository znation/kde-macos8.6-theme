"""The nonsquare 5x4 pair the spatial-runs unit suites pin both axes against.

``difference_runs`` and ``difference_column_runs`` split the same differing
pixels along opposite scan directions, so both unit suites pin the identical
literal intervals on one shared pair.  The pair and the shared assertion
live here once; each suite keeps a one-line test naming what it pins.

This module defines no test cases, so ``unittest discover`` never collects
it; the mixin only holds the assertion both suites call.
"""

from __future__ import annotations

from tools.fidelity_lib.metrics import compare
from tools.fidelity_lib.spatial import difference_column_runs, difference_runs
from tools.png import Image

_WIDTH, _HEIGHT = 5, 4

_NON_SQUARE_RGB = bytearray(_WIDTH * _HEIGHT * 3)
for _x, _y, _value in ((0, 0, 11), (1, 0, 12), (4, 0, 30),
                       (0, 2, 20), (4, 2, 11), (4, 3, 11)):
    _NON_SQUARE_RGB[(_y * _WIDTH + _x) * 3] = _value

NON_SQUARE_PAIR = (Image(_WIDTH, _HEIGHT, bytes(_NON_SQUARE_RGB)),
                   Image(_WIDTH, _HEIGHT, bytes(_WIDTH * _HEIGHT * 3)))

NON_SQUARE_HORIZONTAL_RUNS = [
    {"x": 0, "y": 0, "length": 2}, {"x": 4, "y": 0, "length": 1},
    {"x": 0, "y": 2, "length": 1}, {"x": 4, "y": 2, "length": 1},
    {"x": 4, "y": 3, "length": 1},
]
NON_SQUARE_VERTICAL_RUNS = [
    {"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 1},
    {"x": 1, "y": 0, "length": 1},
    {"x": 4, "y": 0, "length": 1}, {"x": 4, "y": 2, "length": 2},
]


class SpatialRunsCase:
    """Mixin carrying the shared both-axes assertion for the run suites."""

    def assert_both_axes_match_the_nonsquare_intervals(self) -> None:
        """Both run functions split the pair's six over-tolerance pixels, and each run list covers exactly ``compare().differing``."""
        candidate, reference = NON_SQUARE_PAIR
        horizontal = difference_runs(candidate, reference, 10)
        vertical = difference_column_runs(candidate, reference, 10)
        self.assertEqual(horizontal, NON_SQUARE_HORIZONTAL_RUNS)
        self.assertEqual(vertical, NON_SQUARE_VERTICAL_RUNS)
        differing = compare(candidate, reference, tolerance=10).differing
        self.assertEqual(sum(run["length"] for run in horizontal), differing)
        self.assertEqual(sum(run["length"] for run in vertical), differing)
