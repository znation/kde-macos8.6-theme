"""Shared preconditions for the byte-string lane arithmetic in ``tools/``.

``tools/png.py``'s ``_byte_add`` and ``tools/fidelity_metrics.py``'s
``_abs_diff`` both pack byte strings into big-integer lanes, where a length
mismatch would silently truncate or overflow the result. Both reject it the
same way, so the check and its diagnostic live here once.
"""

from __future__ import annotations


def require_equal_lengths(a: bytes, b: bytes, name: str) -> int:
    """Return ``len(a)`` after checking *a* and *b* are equal-length.

    *name* is the caller's function name, without parentheses, and is used to
    name it in the diagnostic. Raises ``ValueError`` naming *name* and both
    lengths, so a caller bug surfaces instead of a silently truncated or
    overflowing result.
    """
    if len(a) != len(b):
        raise ValueError(
            f"{name}() requires equal-length byte strings: "
            f"len(a)={len(a)} len(b)={len(b)}"
        )
    return len(a)
