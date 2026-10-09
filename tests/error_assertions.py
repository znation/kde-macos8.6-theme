"""Shared assertion for the ``assertRaises`` + message idiom.

Many tests assert that a call rejects a bad input and then read the raised
exception's message to pin what it names. This names that expectation once::

    message = error_message(self, ValueError, circle_geometry, element)

``case.assertRaises`` reports a failure against the calling test when
*function* does not raise *exception*; a different exception propagates.
"""

from __future__ import annotations


def error_message(case, exception, function, *args, **kwargs):
    """Call *function* and return the message of the *exception* it raises.

    *case* is the calling ``unittest.TestCase``, so a missing raise fails
    against the right test. Positional and keyword arguments are forwarded to
    *function*.
    """
    with case.assertRaises(exception) as caught:
        function(*args, **kwargs)
    return str(caught.exception)
