"""Tests for tools/ints.py -- the shared genuine-integer predicate.

``tools/png.py``, ``tools/fidelity_metrics.py`` and the test helpers
``tests/png_fixtures.py`` and ``tests/svg_assertions.py`` all call
``is_plain_int`` before using a caller-supplied number as a dimension,
coordinate, channel or tolerance. Their own tests exercise the rejection
through each caller's diagnostic, so none of them pins the predicate's
boundary directly; these tests do, so a change to the check is caught here
rather than in every caller at once.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import ints


class TestIsPlainInt(unittest.TestCase):
    def test_accepts_genuine_integers(self):
        for value in (0, 1, -1, 255, 2**31, -2**31):
            with self.subTest(value=value):
                self.assertTrue(ints.is_plain_int(value))

    def test_rejects_both_booleans(self):
        # bool is an int subclass, so this is the case a bare
        # ``isinstance(value, int)`` would wrongly accept as 1/0.
        for value in (True, False):
            with self.subTest(value=value):
                self.assertFalse(ints.is_plain_int(value))

    def test_rejects_non_integers(self):
        for value in (1.0, "1", None, [1], (1,)):
            with self.subTest(value=value):
                self.assertFalse(ints.is_plain_int(value))

    def test_subclasses_of_int_that_are_not_bool_pass(self):
        # Only ``bool`` is singled out: an int subclass that carries a real
        # numeric value is still an integer for these validators.
        class IntSubclass(int):
            pass

        self.assertTrue(ints.is_plain_int(IntSubclass(3)))


if __name__ == "__main__":
    unittest.main()
