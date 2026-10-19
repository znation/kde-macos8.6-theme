"""Well-formedness check for the absolute source URLs in the provenance record.

``url_problem`` explains why a URL is not a well-formed absolute URL, and
``is_absolute_url`` is its yes/no form. ``tools/reference_validation.py`` calls
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
# ABNF literals are case insensitive, so the leading ``v`` may be either case.
_IPV_FUTURE = re.compile(r"[vV][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+")

# RFC 3986 reg-name: *( unreserved / pct-encoded / sub-delims ). The host of
# an unbracketed authority is a reg-name, so a character outside those sets
# (``<``, ``>``, ``{``, ``}``, ``\``, ``"``, ``|``, ``^``, a backtick or a
# raw non-ASCII byte) is malformed.
_REG_NAME_UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)
_REG_NAME_SUB_DELIMS = frozenset("!$&'()*+,;=")
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")

# RFC 3986 path/query/fragment characters beyond the unreserved and sub-delims
# ``_is_uri_component`` already allows: ``pchar`` adds ":" and "@", the path
# separates its segments with "/", and a query or fragment may also hold "?".
_PATH_EXTRA = frozenset(":@/")
_QUERY_FRAGMENT_EXTRA = frozenset(":@/?")


def _is_uri_component(text: str, extra: frozenset[str] = frozenset()) -> bool:
    """Return True when *text* is unreserved / sub-delims / pct-encoded / *extra*.

    A percent sign must introduce exactly two hex digits; any character
    outside the allowed sets -- ``<``, ``>``, ``{``, ``}``, ``\\``, ``"``,
    ``|``, ``^``, a backtick or a raw non-ASCII byte -- is not part of one.
    """
    index = 0
    while index < len(text):
        char = text[index]
        if char == "%":
            if (
                index + 2 >= len(text)
                or text[index + 1] not in _HEX_DIGITS
                or text[index + 2] not in _HEX_DIGITS
            ):
                return False
            index += 3
            continue
        if (
            char not in _REG_NAME_UNRESERVED
            and char not in _REG_NAME_SUB_DELIMS
            and char not in extra
        ):
            return False
        index += 1
    return True


def _is_reg_name(host: str) -> bool:
    """Return True when *host* is an RFC 3986 reg-name.

    A reg-name is a run of unreserved characters, sub-delims and pct-encoded
    octets.
    """
    return _is_uri_component(host)


def _is_userinfo(userinfo: str) -> bool:
    """Return True when *userinfo* is an RFC 3986 userinfo.

    userinfo is a run of unreserved characters, sub-delims, pct-encoded octets
    and colons, so ``user:pass`` is well-formed while an unencoded ``@``,
    ``user name`` or ``user\\name`` is not.
    """
    return _is_uri_component(userinfo, frozenset(":"))


def _is_path(path: str) -> bool:
    """Return True when *path* is an RFC 3986 path-abempty.

    path-abempty is a run of ``/``-separated ``pchar`` segments, so a
    non-empty path must start with ``/`` and hold only characters ``pchar``
    allows.
    """
    return (not path or path.startswith("/")) and _is_uri_component(
        path, _PATH_EXTRA
    )


def _is_query_or_fragment(text: str) -> bool:
    """Return True when *text* is an RFC 3986 query or fragment.

    Both are a run of ``pchar``, ``/`` and ``?``.
    """
    return _is_uri_component(text, _QUERY_FRAGMENT_EXTRA)


def _is_ip_literal(text: str) -> bool:
    """Return True when *text* is an RFC 3986 IPv6address or IPvFuture.

    RFC 3986 gives an IP-literal no zone identifier, so a ``%`` (raw or
    percent-encoded, as in ``fe80::1%eth0``) is not part of one even though
    Python's :mod:`ipaddress` accepts a scope id.
    """
    if "%" in text:
        return False
    if _IPV_FUTURE.fullmatch(text):
        return True
    try:
        ipaddress.IPv6Address(text)
    except ValueError:
        return False
    return True


def _is_port(port: str) -> bool:
    """Return True when *port* is an RFC 3986 port.

    A port is ``*DIGIT`` -- zero or more ASCII digits -- so an empty string
    (the ``host:`` form) is well-formed and ``80:90`` and ``abc`` are not.
    """
    return all(ch in "0123456789" for ch in port)


def _authority_host(authority: str) -> tuple[str, str | None]:
    """Return ``(host, problem)`` for an RFC 3986 *authority*.

    The host is what follows any ``userinfo@`` prefix and precedes any
    ``:port`` suffix. Userinfo is an RFC 3986 userinfo, so an unencoded
    ``@``, a space or a backslash before the host is malformed. A bracketed
    IP-literal (``[::1]``) must be closed and hold an IPv6 or IPvFuture
    address; a bracket in an unbracketed host is malformed, as is a port
    holding anything but ASCII digits. An unbracketed host is an RFC 3986
    reg-name, so a character outside that set (``<``, ``{``, a backslash, a
    bare percent) is malformed too. *problem* is a diagnostic for a malformed
    authority, and *host* is empty when the authority names no host at all.
    """
    userinfo, sep, hostport = authority.rpartition("@")
    if sep and not _is_userinfo(userinfo):
        return "", "must use only userinfo characters before '@'"
    if hostport.startswith("["):
        end = hostport.find("]")
        if end == -1:
            return "", "must close the bracketed host with ']'"
        if end + 1 < len(hostport):
            if hostport[end + 1] != ":":
                return "", "must put only a port after the bracketed host"
            if not _is_port(hostport[end + 2 :]):
                return "", "must put only digits in the port after the bracketed host"
        host = hostport[1:end]
        if not _is_ip_literal(host):
            return "", "must bracket an IPv6 or IPvFuture address"
        return host, None
    if "[" in hostport or "]" in hostport:
        return "", "must not put '[' or ']' in a host"
    host, sep, port = hostport.partition(":")
    if sep and not _is_port(port):
        return "", "must put only digits in the port"
    if not _is_reg_name(host):
        return "", "must use only reg-name characters in the host"
    return host, None


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
    A port must be ASCII digits (or empty), so ``host:80:90`` and
    ``host:abc`` are malformed citations. An unbracketed host is an RFC 3986
    reg-name, so ``host name``, ``host<a>`` and a bare ``host%`` are malformed
    too. Userinfo follows the same shape, so ``user name@host`` and
    ``user@host`` (an unencoded ``@``) are malformed as well. The path, query
    and fragment are held to their RFC 3986 character sets, so a bare ``%``
    or a raw ``<``, ``{`` or backslash there is malformed too.
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
    # What follows the authority is the path, then an optional ``?`` query and
    # ``#`` fragment; the ``#`` splits first because it starts the fragment
    # even when a ``?`` appears after it. Each part has its own RFC 3986
    # character set, so a bare percent or a character no ``pchar`` allows
    # (``<``, ``{``, a backslash, a raw non-ASCII byte) is malformed even when
    # the authority is well-formed.
    path_and_query, _, fragment = rest[len(authority):].partition("#")
    path, _, query = path_and_query.partition("?")
    if not _is_path(path):
        return "must use only path characters; percent-encode the rest"
    if not _is_query_or_fragment(query):
        return "must use only query characters; percent-encode the rest"
    if not _is_query_or_fragment(fragment):
        return "must use only fragment characters; percent-encode the rest"
    return None


def is_absolute_url(url: str) -> bool:
    """Return True when *url* is a well-formed absolute URL.

    See :func:`url_problem`, which this wraps, for the rules and the reason a
    URL can fail.
    """
    return url_problem(url) is None
