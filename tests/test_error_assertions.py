"""Tests for tests/error_assertions.py -- the shared assertion helpers.

The helpers replace repeated assertion idioms at their call sites, so pin
their own contracts. ``error_message``: the message it returns, that it
forwards both positional and keyword arguments, that a different exception
propagates rather than being swallowed, and that a missing raise fails the
calling test. ``assert_escapes_escape_character``: that it accepts escaped
ESC text and fails on a raw ESC or a missing escape.
"""

from __future__ import annotations

import unittest

from error_assertions import (
    assert_escapes_escape_character,
    error_message,
)


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


class TestAssertEscapesEscapeCharacter(unittest.TestCase):
    def test_accepts_escaped_esc_text(self):
        assert_escapes_escape_character(self, "evil\\u001b[31m.png")

    def test_rejects_a_raw_esc_byte(self):
        with self.assertRaises(AssertionError):
            assert_escapes_escape_character(self, "evil\x1b[31m.png")

    def test_rejects_text_without_the_escape(self):
        with self.assertRaises(AssertionError):
            assert_escapes_escape_character(self, "evil[31m.png")


if __name__ == "__main__":
    unittest.main()
