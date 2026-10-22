"""Tests for tests/support/rejection_assertions.py -- the guard-rejection helpers.

A guard that reports a bad slice through ``case.subTest`` does not raise, so
these helpers give it a ``NoSubTest`` case that drops the frame.
``assert_rejection_names``: that it accepts a diagnostic naming every needle,
fails on a missing one, forwards the guard's arguments without leaking
``needles``, and returns the message. ``assert_rejects`` and
``rejection_message`` are exercised through it and by the guard modules it
serves.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.rejection_assertions import assert_rejection_names


def _reject(case, value, *, label="bad"):
    case.fail(f"{label} value: {value}")


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


if __name__ == "__main__":
    unittest.main()
