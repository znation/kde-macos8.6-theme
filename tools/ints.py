"""Shared integer-type predicate for the ``tools/`` validation code.

``bool`` is a subclass of ``int``, so ``isinstance(True, int)`` is true and a
boolean silently passes as 1/0 through any check that only asks for an
integer. The validators in ``tools/png.py`` and ``tools/fidelity_metrics.py``
-- and the test helpers that mirror them -- all need the genuine-integer test,
so it lives here once and names what it excludes.
"""

from __future__ import annotations


def is_plain_int(value: object) -> bool:
    """Return True when *value* is an ``int`` that is not a ``bool``.

    A boolean is rejected because it is an ``int`` subclass and would pass as
    1/0, silently selecting a different dimension, coordinate or tolerance
    instead of the value the caller meant.
    """
    return isinstance(value, int) and not isinstance(value, bool)
