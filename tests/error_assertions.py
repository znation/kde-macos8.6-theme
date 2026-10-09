"""Shared assertions for raised-exception messages and terminal-escaped text.

Many tests assert that a call rejects a bad input and then read the raised
exception's message to pin what it names. This names that expectation once::

    message = error_message(self, ValueError, circle_geometry, element)

A test that pins several substrings of that message at once uses
``assert_error_names``, which extracts the message and asserts each name in
it.

``case.assertRaises`` reports a failure against the calling test when
*function* does not raise *exception*; a different exception propagates.

``assert_escapes_escape_character`` names the terminal-safety outcome the
tools' output is expected to have: no raw ESC byte, its visible escape shown.

``assert_rejects_unequal_lengths`` names the caller side of the shared
``tools.byteops.require_equal_lengths`` precondition: the packed-lane byte
helpers in ``tools/png.py`` and ``tools/fidelity_metrics.py`` both reject a
length mismatch, and each must name itself in the diagnostic.

``NoSubTest``, ``assert_rejects`` and ``rejection_message`` observe the other
kind of failure: a ``tests/svg_assertions/`` guard that reports a bad slice
through ``case.subTest`` records a failure on the result and keeps going
instead of raising, so ``assertRaises`` would never see it. They drop the
subTest frame so the underlying assertion raises and its message is readable.
"""

from __future__ import annotations

import contextlib
import re
import unittest


def error_message(case, exception, function, *args, **kwargs):
    """Call *function* and return the message of the *exception* it raises.

    *case* is the calling ``unittest.TestCase``, so a missing raise fails
    against the right test. Positional and keyword arguments are forwarded to
    *function*.
    """
    with case.assertRaises(exception) as caught:
        function(*args, **kwargs)
    return str(caught.exception)


def assert_error_names(case, exception, function, *args, needles=(), **kwargs):
    """Assert *function* raises *exception* whose message names each *needle*.

    A test that rejects a bad input and pins several substrings the
    diagnostic must carry would extract the message with ``error_message``
    and then repeat ``assertIn`` per substring; this names that expectation
    once. *args* and *kwargs* are forwarded to *function*; ``needles`` is
    consumed here and never forwarded. Returns the message, so a test that
    must read it further still can.
    """
    message = error_message(case, exception, function, *args, **kwargs)
    for needle in needles:
        case.assertIn(needle, message)
    return message


def assert_escapes_escape_character(case, text):
    """Assert *text* carries no raw ESC (U+001B), only its ``\\u001b`` escape.

    The command-line tools route contributor-supplied paths through
    ``tools.terminal.escape_controls``; this pins what a caller sees of that
    output: the byte that would drive a terminal is gone, and the visible
    escape that identifies it is present.
    """
    case.assertNotIn("\x1b", text)
    case.assertIn("\\u001b", text)


def assert_rejects_unequal_lengths(case, function):
    """Assert *function* rejects byte strings whose lengths differ.

    *function* is a packed-lane byte helper (``tools/png_filters._byte_add`` or
    ``tools/fidelity_metrics._abs_diff``) whose length precondition is
    ``tools.byteops.require_equal_lengths``. A second argument that is too
    short would silently drop bytes and one that is too long would overflow
    ``to_bytes``, so both directions must raise a ``ValueError`` naming
    *function* and the equal-length requirement.
    """
    for a, b in (
        (b"\x01\x02\x03", b"\x01\x02"),
        (b"\x01", b"\x01\x02\x03"),
    ):
        with case.subTest(a=a, b=b):
            with case.assertRaisesRegex(
                ValueError,
                rf"{re.escape(function.__name__)}\(\) requires equal-length",
            ):
                function(a, b)


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
        return contextlib.nullcontext()

    def assertDictEqual(self, d1, d2, msg=None):
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
