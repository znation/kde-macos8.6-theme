"""Tests for tools/byte_lanes.py -- the packed-integer byte operations.

Each routine packs a byte string into one big integer to work on many bytes per
arithmetic step.  These tests compare every routine against the obvious
per-byte spelling, so a borrow, carry or bit-slice bug is caught here rather
than through a wrong fidelity metric.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import itertools
import random
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.error_assertions import assert_rejects_unequal_lengths  # noqa: E402
from tools import byte_lanes


def assert_matches_oracle(case, actual, reference, *, arity, min_length=0):
    """Check a packed-integer routine against a naive per-byte oracle.

    ``actual`` and ``reference`` each take ``arity`` byte strings and return
    equal results.  Every length from ``min_length`` to 39, then the
    63/64/65, 255/256/257 and 1000 boundaries, is exercised on eight random
    blocks so a borrow, carry, or bit-slice bug shows up across byte positions.
    """
    rng = random.Random(0)
    lengths = list(range(min_length, 40)) + [63, 64, 65, 255, 256, 257, 1000]
    for length in lengths:
        for _ in range(8):
            args = [rng.randbytes(length) for _ in range(arity)]
            with case.subTest(length=length):
                case.assertEqual(actual(*args), reference(*args))


class TestAbsDiff(unittest.TestCase):
    """The packed-integer byte differ must agree with the per-byte form."""

    @staticmethod
    def _reference(a: bytes, b: bytes) -> bytes:
        return bytes(abs(x - y) for x, y in zip(a, b))

    def test_matches_per_byte_reference(self):
        assert_matches_oracle(
            self, byte_lanes.abs_diff, self._reference, arity=2
        )

    def test_unequal_lengths_raise(self):
        assert_rejects_unequal_lengths(self, byte_lanes.abs_diff)

    def test_extreme_values(self):
        # 0/255 is where a borrow or carry would show up first, for both an
        # even and an odd byte count.
        for length, x, y in itertools.product((1, 2, 7), (0, 255), (0, 255)):
            a = bytes([x]) * length
            b = bytes([y]) * length
            with self.subTest(length=length, x=x, y=y):
                self.assertEqual(
                    byte_lanes.abs_diff(a, b), self._reference(a, b)
                )


class TestSumSquares(unittest.TestCase):
    """The split-table sum of squares must agree with the per-byte form."""

    @staticmethod
    def _reference(channel: bytes) -> int:
        return sum(value * value for value in channel)

    def test_matches_per_byte_reference(self):
        assert_matches_oracle(
            self, byte_lanes.sum_squares, self._reference, arity=1
        )

    def test_every_byte_value(self):
        # A single square can spill into the high byte (255*255 == 65025), so
        # exercise every value, both alone and repeated enough to carry.
        channel = bytes(range(256))
        self.assertEqual(
            byte_lanes.sum_squares(channel), self._reference(channel)
        )
        self.assertEqual(
            byte_lanes.sum_squares(b"\xff" * 1000),
            self._reference(b"\xff" * 1000),
        )


class TestMaxByteIndex(unittest.TestCase):
    """The bit-sliced maximum must agree with ``max`` plus ``find``."""

    @staticmethod
    def _reference(data: bytes) -> int:
        return data.find(max(data))

    def test_matches_max_and_find(self):
        assert_matches_oracle(
            self,
            byte_lanes.max_byte_index,
            self._reference,
            arity=1,
            min_length=1,
        )

    def test_edges_and_ties(self):
        cases = (
            b"\x00",  # single zero
            b"\xff",  # single maximum
            b"\x00\xff",  # maximum last
            b"\xff\x00",  # maximum first
            b"\x05\x05\x05",  # all equal: first wins
            bytes(range(256)),  # every value once: 255 at the end
            bytes(range(255, -1, -1)),  # every value once: 255 at the start
        )
        for data in cases:
            with self.subTest(data=data[:8]):
                self.assertEqual(
                    byte_lanes.max_byte_index(data), self._reference(data)
                )

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            byte_lanes.max_byte_index(b"")


if __name__ == "__main__":
    unittest.main()
