"""Shared assertions for raised-exception messages and terminal-escaped text.

Many tests assert that a call rejects a bad input and then read the raised
exception's message to pin what it names. This names that expectation once::

    message = error_message(self, ValueError, circle_geometry, element)

``case.assertRaises`` reports a failure against the calling test when
*function* does not raise *exception*; a different exception propagates.

``assert_escapes_escape_character`` names the terminal-safety outcome the
tools' output is expected to have: no raw ESC byte, its visible escape shown.

``assert_rejects_unequal_lengths`` names the caller side of the shared
``tools.byteops.require_equal_lengths`` precondition: the packed-lane byte
helpers in ``tools/png.py`` and ``tools/fidelity_metrics.py`` both reject a
length mismatch, and each must name itself in the diagnostic.
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

    *function* is a packed-lane byte helper (``tools/png._byte_add`` or
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
