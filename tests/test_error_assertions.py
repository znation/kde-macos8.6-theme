"""Tests for tests/support/error_assertions.py -- the shared assertion helpers.

The helpers replace repeated assertion idioms at their call sites, so pin
their own contracts. ``error_message``: the message it returns, that it
forwards both positional and keyword arguments, that a different exception
propagates rather than being swallowed, and that a missing raise fails the
calling test. ``assert_error_names``: that it accepts a message naming every
needle, fails on a missing one, forwards the function's arguments without
leaking ``needles``, and returns the message.
``assert_escapes_escape_character``: that it accepts escaped
ESC text and fails on a raw ESC or a missing escape.
``assert_rejection_names``: that it accepts a diagnostic naming every
needle, fails on a missing one, forwards the guard's arguments without
leaking ``needles``, and returns the message.
``assert_rejects_unequal_lengths``: that it accepts a helper rejecting both
length-mismatch directions and fails the calling test when the helper does
not reject, rejects only one direction, or names another function.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.error_assertions import (
    NoSubTest,
    assert_error_names,
    assert_escapes_escape_character,
    assert_rejection_names,
    assert_rejects_unequal_lengths,
    error_message,
)
from tools.png.filters import _byte_add  # noqa: E402


def _raise(exception):
    raise exception


def _reject(case, value, *, label="bad"):
    case.fail(f"{label} value: {value}")


def _accepts_any_lengths(a, b):
    """A packed-lane stand-in that fails to reject a length mismatch."""
    return b""


def _names_another_function(a, b):
    """A packed-lane stand-in whose diagnostic names a different function."""
    raise ValueError("other() requires equal-length byte strings")


def _rejects_only_short_second(a, b):
    """A packed-lane stand-in that rejects a too-short second argument only."""
    if len(a) > len(b):
        raise ValueError(
            f"{_rejects_only_short_second.__name__}() requires equal-length"
        )
    return b""


def _rejects_only_long_second(a, b):
    """A packed-lane stand-in that rejects a too-long second argument only."""
    if len(a) < len(b):
        raise ValueError(
            f"{_rejects_only_long_second.__name__}() requires equal-length"
        )
    return b""


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


class TestAssertErrorNames(unittest.TestCase):
    def test_passes_when_the_message_names_every_needle(self):
        assert_error_names(
            self,
            ValueError,
            _raise,
            ValueError("bad value: alpha beta"),
            needles=("alpha", "beta"),
        )

    def test_returns_the_message(self):
        self.assertEqual(
            assert_error_names(
                self,
                ValueError,
                _raise,
                ValueError("bad value"),
                needles=("value",),
            ),
            "bad value",
        )

    def test_fails_when_a_needle_is_missing(self):
        with self.assertRaises(AssertionError):
            assert_error_names(
                self,
                ValueError,
                _raise,
                ValueError("bad value"),
                needles=("alpha",),
            )

    def test_forwards_positional_and_keyword_arguments(self):
        def join(*parts, sep="-"):
            raise ValueError(sep.join(parts))

        assert_error_names(
            self, ValueError, join, "a", "b", sep="+", needles=("a+b",)
        )

    def test_needles_is_not_forwarded_to_the_function(self):
        def describe(*args, **kwargs):
            raise ValueError(f"args={args} kwargs={sorted(kwargs)}")

        assert_error_names(
            self,
            ValueError,
            describe,
            1,
            needles=("args=(1,)", "kwargs=[]"),
        )

    def test_a_missing_raise_fails_the_calling_case(self):
        with self.assertRaises(AssertionError):
            assert_error_names(self, ValueError, lambda: None, needles=())


class TestAssertRejectionNames(unittest.TestCase):
    def test_passes_when_the_message_names_every_needle(self):
        assert_rejection_names(
            self, _reject, "alpha beta", needles=("alpha", "beta")
        )

    def test_returns_the_message(self):
        self.assertEqual(
            assert_rejection_names(self, _reject, "x", needles=("x",)),
            "bad value: x",
        )

    def test_fails_when_a_needle_is_missing(self):
        with self.assertRaises(AssertionError):
            assert_rejection_names(self, _reject, "x", needles=("missing",))

    def test_forwards_positional_and_keyword_arguments(self):
        assert_rejection_names(
            self,
            _reject,
            "x",
            label="wrong",
            needles=("wrong value: x",),
        )

    def test_needles_is_not_forwarded_to_the_guard(self):
        def describe(case, *args, **kwargs):
            raise AssertionError(f"args={args} kwargs={sorted(kwargs)}")

        assert_rejection_names(
            self, describe, 1, needles=("args=(1,)", "kwargs=[]")
        )

    def test_a_missing_raise_fails_the_calling_case(self):
        with self.assertRaises(AssertionError):
            assert_rejection_names(self, lambda case: None, needles=())


class TestAssertRejectsUnequalLengths(unittest.TestCase):
    def test_accepts_a_helper_that_rejects_both_directions(self):
        # `_byte_add` is one of the two real callers, and its precondition
        # rejects both length-mismatch directions. That the helper checks
        # both directions is pinned by the two one-direction tests below,
        # not by this one (a one-direction helper still accepts `_byte_add`).
        assert_rejects_unequal_lengths(self, _byte_add)

    def test_fails_when_only_the_too_short_direction_is_rejected(self):
        # A helper that only tried the first (too-short) case would accept
        # this stand-in, leaving the too-long case unpinned.
        case = NoSubTest()
        with self.assertRaises(AssertionError):
            assert_rejects_unequal_lengths(case, _rejects_only_short_second)

    def test_fails_when_only_the_too_long_direction_is_rejected(self):
        # A helper that only tried the second (too-long) case would accept
        # this stand-in, leaving the too-short case unpinned.
        case = NoSubTest()
        with self.assertRaises(AssertionError):
            assert_rejects_unequal_lengths(case, _rejects_only_long_second)

    def test_fails_when_the_function_does_not_reject(self):
        # A helper that merely called the function without asserting would
        # leave every caller passing while pinning nothing, so a function
        # that accepts unequal lengths must fail the calling test.
        case = NoSubTest()
        with self.assertRaises(AssertionError):
            assert_rejects_unequal_lengths(case, _accepts_any_lengths)

    def test_fails_when_the_diagnostic_names_another_function(self):
        # The diagnostic must name the function under test; a message naming
        # another function would not pin this caller's own precondition.
        case = NoSubTest()
        with self.assertRaises(AssertionError):
            assert_rejects_unequal_lengths(case, _names_another_function)


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
