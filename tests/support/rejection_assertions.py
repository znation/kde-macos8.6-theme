"""Shared assertions for guards that report a bad input through ``case.subTest``.

A ``tests/svg_assertions/`` guard reports a bad slice through ``case.subTest``:
unittest records a failure on the result and keeps going instead of raising,
so ``assertRaises`` would never see it. ``NoSubTest`` drops the subTest frame
so the underlying assertion raises, and the helpers here name the expectations
built on it::

    assert_rejects(guard, *args)
    rejection_message(guard, *args)
    assert_rejection_names(case, guard, *args, needles=...)

A guard that raises directly is observed with the raised-exception helpers in
the sibling ``tests/support/error_assertions.py``.
"""

from __future__ import annotations

import contextlib
import unittest

from support.error_assertions import error_message


class NoSubTest(unittest.TestCase):
    """A real TestCase whose ``subTest`` is a no-op frame.

    The structural guards report a bad slice through ``case.subTest``;
    unittest records a subTest failure on the result and keeps going rather
    than raising, so an ``assertRaises`` around the guard would never see it.
    Dropping the subTest frame keeps the real ``assertEqual`` (which raises)
    so the guard's failure is observable here.

    The pixel guards compare whole ``{(x, y): colour}`` maps, and every use of
    this stub is a deliberately broken map whose only observable is that the
    guard raises. ``assertEqual`` on two dicts dispatches to
    ``assertDictEqual``, whose failure path pretty-prints both maps and runs
    them through difflib -- a large, pure-diagnostic cost these callers never
    read. Compare without that diff; a mismatch still raises
    ``AssertionError``, so the guard's failure stays observable.
    """

    def subTest(self, **kwargs):
        """Drop the subTest frame so a failed assertion raises; see the class docstring."""
        return contextlib.nullcontext()

    def assertDictEqual(self, d1, d2, msg=None):
        """Compare maps without difflib; see the class docstring."""
        self.assertIsInstance(d1, dict, "First argument is not a dictionary")
        self.assertIsInstance(d2, dict, "Second argument is not a dictionary")
        if d1 != d2:
            self.fail(self._formatMessage(msg, "the maps differ"))


def assert_rejects(guard, *args, **kwargs):
    """Assert *guard* rejects a broken input instead of accepting it.

    A guard that reports a bad slice through ``case.subTest`` does not raise:
    unittest records the failure and keeps going, so ``assertRaises`` would
    never observe it. Giving the guard the ``NoSubTest`` case drops the
    subTest frame so the underlying assertion raises instead; a guard that
    raises directly is unaffected. *args* and *kwargs* are the guard's own
    parameters after ``case``.
    """
    case = NoSubTest()
    with case.assertRaises(AssertionError):
        guard(case, *args, **kwargs)


def rejection_message(guard, *args, **kwargs):
    """Return the AssertionError message *guard* raises for a broken input.

    `assert_rejects` proves a guard rejects an input; a test that also pins
    what the diagnostic names needs the message. Like that helper this gives
    the guard a ``NoSubTest`` case, so a guard that reports through
    ``case.subTest`` still raises. *args* and *kwargs* are the guard's own
    parameters after ``case``.
    """
    case = NoSubTest()
    return error_message(
        case, AssertionError, guard, case, *args, **kwargs
    )


def assert_rejection_names(case, guard, *args, needles=(), **kwargs):
    """Assert *guard* rejects an input and its message names each *needle*.

    ``assert_rejects`` proves the rejection and ``rejection_message`` returns
    the diagnostic; a test that pins what that diagnostic names would call
    one and then assert each substring against the other. This names that
    expectation once, mirroring ``assert_error_names`` for the
    subTest-reporting guards. *args* and *kwargs* are the guard's own
    parameters after ``case``; ``needles`` is consumed here and never
    forwarded. Returns the message, so a test that must read it further still
    can.
    """
    message = rejection_message(guard, *args, **kwargs)
    for needle in needles:
        case.assertIn(needle, message)
    return message
