"""Tests for tests/error_assertions.py -- the shared error-message assertion.

The helper replaces the ``assertRaises``/``str(...exception)`` pair at every
call site, so pin its own contract: the message it returns, that it forwards
both positional and keyword arguments, that a different exception propagates
rather than being swallowed, and that a missing raise fails the calling test.
"""

from __future__ import annotations

import unittest

from error_assertions import error_message


def _raise(exception):
    raise exception


class TestErrorMessage(unittest.TestCase):
    def test_returns_the_message_of_the_expected_exception(self):
        self.assertEqual(
            error_message(self, ValueError, _raise, ValueError("bad value")),
            "bad value",
        )

    def test_forwards_positional_and_keyword_arguments(self):
        def join(*parts, sep="-"):
            raise ValueError(sep.join(parts))

        self.assertEqual(
            error_message(self, ValueError, join, "a", "b", sep="+"),
            "a+b",
        )

    def test_a_different_exception_propagates(self):
        with self.assertRaises(KeyError):
            error_message(self, ValueError, _raise, KeyError("k"))

    def test_a_missing_raise_fails_the_calling_case(self):
        with self.assertRaises(AssertionError):
            error_message(self, ValueError, lambda: None)


if __name__ == "__main__":
    unittest.main()
