"""Well-formedness check for the absolute source URLs in the provenance record.

``url_problem`` explains why a URL is not a well-formed absolute URL, and
``is_absolute_url`` is its yes/no form. ``tools/check_references.py`` calls
``url_problem`` to validate each ``sources.txt`` entry.
"""

from __future__ import annotations

import ipaddress
import re

# RFC 3986 scheme: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ). Any other
# character (a space from a copy-paste, a stray "!") means the token is not a
# scheme, however absolute the rest of the URL looks.
_SCHEME_PUNCTUATION = frozenset("+-.")

# Schemes whose host may legitimately be empty: ``file:///path`` names no
# host, while a network scheme with an empty host (``https:///path``) is a
# citation with nowhere to point.
_SCHEMES_ALLOWING_EMPTY_HOST = frozenset({"file"})

# RFC 3986 IPvFuture: "v" 1*HEXDIG "." 1*( unreserved / sub-delims / ":" ).
_IPV_FUTURE = re.compile(r"v[0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+")


def _is_ip_literal(text: str) -> bool:
    """Return True when *text* is an RFC 3986 IPv6address or IPvFuture."""
    if _IPV_FUTURE.fullmatch(text):
        return True
    try:
        ipaddress.IPv6Address(text)
    except ValueError:
        return False
    return True


def _authority_host(authority: str) -> tuple[str, str | None]:
    """Return ``(host, problem)`` for an RFC 3986 *authority*.

    The host is what follows any ``userinfo@`` prefix and precedes any
    ``:port`` suffix. A bracketed IP-literal (``[::1]``) must be closed and
    hold an IPv6 or IPvFuture address; a bracket in an unbracketed host is
    malformed. *problem* is a diagnostic for a malformed authority, and
    *host* is empty when the authority names no host at all.
    """
    hostport = authority.rsplit("@", 1)[-1]
    if hostport.startswith("["):
        end = hostport.find("]")
        if end == -1:
            return "", "must close the bracketed host with ']'"
        if end + 1 < len(hostport) and hostport[end + 1] != ":":
            return "", "must put only a port after the bracketed host"
        host = hostport[1:end]
        if host and not _is_ip_literal(host):
            return "", "must bracket an IPv6 or IPvFuture address"
        return host, None
    if "[" in hostport or "]" in hostport:
        return "", "must not put '[' or ']' in a host"
    return hostport.split(":", 1)[0], None


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
    scheme for the latter two sends the reader after the wrong thing. A
    bracketed host is held to its RFC 3986 form: ``[::1]`` is a host, while
    ``[]``, an unclosed ``[::1`` and a bracket in an unbracketed host are not.
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
    host, problem = _authority_host(authority)
    if problem is not None:
        return problem
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
