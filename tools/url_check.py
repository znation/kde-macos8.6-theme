"""Well-formedness check for the absolute source URLs in the provenance record.

``url_problem`` explains why a URL is not a well-formed absolute URL, and
``is_absolute_url`` is its yes/no form. ``tools/check_references.py`` calls
``url_problem`` to validate each ``sources.txt`` entry.
"""

from __future__ import annotations

# RFC 3986 scheme: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ). Any other
# character (a space from a copy-paste, a stray "!") means the token is not a
# scheme, however absolute the rest of the URL looks.
_SCHEME_PUNCTUATION = frozenset("+-.")

# Schemes whose host may legitimately be empty: ``file:///path`` names no
# host, while a network scheme with an empty host (``https:///path``) is a
# citation with nowhere to point.
_SCHEMES_ALLOWING_EMPTY_HOST = frozenset({"file"})


def url_problem(url: str) -> str | None:
    """Return why *url* is not a well-formed absolute URL, or None when it is.

    A provenance source is an absolute URL, so a bare host or a relative path
    (``example.test/x.png``) is a broken citation even though it is non-empty.
    The scheme must follow RFC 3986 (``ALPHA *( ALPHA / DIGIT / "+" / "-" /
    "." )``), the URL must contain no raw whitespace or control character
    (which belong percent-encoded), and the authority between ``://`` and the
    path must name a host unless the scheme is ``file``. The rules catch broken
    citations that a first-character-only scheme test accepts: ``ht!tp://x``,
    ``https://example.test/a b.png``, ``https:///image.png`` and
    ``https://user@/image.png``.

    The failures are returned separately because the fix differs: a URL with no
    (or a malformed) scheme needs a source, one whose scheme is fine but which
    carries a space or control character only needs that character
    percent-encoded, and one with an empty authority needs a host. Blaming the
    scheme for the latter two sends the reader after the wrong thing.
    """
    scheme, sep, rest = url.partition("://")
    if (
        not (sep and rest)
        or not scheme.isascii()
        or not scheme[:1].isalpha()
        or not all(ch.isalnum() or ch in _SCHEME_PUNCTUATION for ch in scheme)
    ):
        return (
            "must be an absolute URL with a valid scheme, "
            "e.g. https://example.test/image.png"
        )
    if not all(ch.isprintable() and not ch.isspace() for ch in url):
        return "must not contain whitespace or control characters; percent-encode them"
    # The authority runs to the first ``/``, ``?`` or ``#``. Its host is what
    # remains after any ``userinfo@`` prefix and ``:port`` suffix, so an
    # authority that is empty, or holds only userinfo or only a port, names no
    # host at all (``scheme:///path``, ``scheme://@/path``, ``scheme://:80/p``).
    authority = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    host = authority.rsplit("@", 1)[-1].split(":", 1)[0]
    if not host and scheme.lower() not in _SCHEMES_ALLOWING_EMPTY_HOST:
        return (
            "must name a host between the scheme and the path "
            "(only file:// URLs may omit it), "
            "e.g. https://example.test/image.png"
        )
    return None


def is_absolute_url(url: str) -> bool:
    """Return True when *url* is a well-formed absolute URL.

    See :func:`url_problem`, which this wraps, for the rules and the reason a
    URL can fail.
    """
    return url_problem(url) is None
