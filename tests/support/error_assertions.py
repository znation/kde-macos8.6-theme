"""Shared assertions for raised-exception messages and printed diagnostics.

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
helpers in ``tools/png/filters.py`` and ``tools/byte_lanes.py`` both reject a
length mismatch, and each must name itself in the diagnostic.

Guards that report a bad slice through ``case.subTest`` need the opposite
observation (the failure never raises); their assertions live in the sibling
``tests/support/rejection_assertions.py``.
"""

from __future__ import annotations

import re


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

    *function* is a packed-lane byte helper (``tools.png.filters._byte_add`` or
    ``tools.byte_lanes.abs_diff``) whose length precondition is
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
