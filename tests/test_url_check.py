"""Unit tests for tools/url_check.py.

A provenance source must be a well-formed absolute URL: a scheme per RFC 3986
followed by an authority that names a host (only ``file://`` may omit it),
with no raw whitespace or control characters.
"""

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.url_check import is_absolute_url


class TestAbsoluteUrlSchemeShape(unittest.TestCase):
    """A source entry must be a scheme followed by a non-empty remainder.

    A scheme with nothing after it names no resource, and a bare host or
    relative path has no scheme at all; both must be rejected so a broken
    citation cannot pass as provenance.
    """

    def test_scheme_and_remainder_are_both_required(self):
        self.assertTrue(is_absolute_url("https://example.test/x"))
        # A scheme with nothing after it names no resource.
        self.assertFalse(is_absolute_url("https://"))
        # A bare host or relative path has no scheme at all.
        self.assertFalse(is_absolute_url("example.test/x"))

    def test_scheme_must_start_with_an_ascii_letter(self):
        # RFC 3986: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ).
        self.assertTrue(is_absolute_url("h2://example.test/x"))
        self.assertTrue(is_absolute_url("svn+ssh://example.test/x"))
        self.assertFalse(is_absolute_url("1http://example.test/x"))
        self.assertFalse(is_absolute_url("h\u00e9llo://example.test/x"))
        self.assertFalse(is_absolute_url("://example.test/x"))


class TestAbsoluteUrlWellFormedness(unittest.TestCase):
    """The source URL must be a well-formed absolute URL, not merely start
    with something alpha-like before ``://``."""

    def setUp(self):
        self.is_absolute = is_absolute_url

    def test_well_formed_urls_are_accepted(self):
        for url in (
            "https://example.test/x.png",
            "http://example.test",
            "git+ssh://example.test/repo",
            "a.b-c+d://example.test",
            # A host is what follows any userinfo and precedes any port.
            "https://@example.test/x.png",
            "https://user@example.test/x.png",
            "https://user:pass@example.test:8080/x.png",
            # file:// is the one scheme whose host may be empty.
            "file:///tmp/x.png",
            "file://host/tmp/x.png",
        ):
            self.assertTrue(self.is_absolute(url), url)

    def test_relative_and_schemeless_urls_are_rejected(self):
        for url in (
            "example.test/x.png",
            "https://",
            "://example.test",
            "1http://example.test",
        ):
            self.assertFalse(self.is_absolute(url), url)

    def test_urls_with_an_empty_authority_are_rejected(self):
        # The scheme is valid, but ``://`` with no host names nowhere for the
        # citation to point; only file:// may omit the authority.
        for url in (
            "https:///x.png",
            "http:///x.png",
            "https://?q",
            "https://#frag",
            "git+ssh:///repo",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))
        self.assertTrue(self.is_absolute("file:///x.png"))

    def test_urls_with_an_authority_but_no_host_are_rejected(self):
        # A non-empty authority can still name no host: ``user@`` is userinfo
        # and ``:8080`` is a port, each leaving the host empty, so the
        # citation points nowhere even though the scheme is valid.
        for url in (
            "https://@/x.png",
            "https://user@/x.png",
            "https://:8080/x.png",
            "https://user@:80/x.png",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))

    def test_malformed_scheme_is_rejected(self):
        for url in (
            "ht tp://example.test/x.png",
            "ht!tp://example.test/x.png",
            "ht\ttp://example.test/x.png",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))

    def test_raw_whitespace_or_control_characters_are_rejected(self):
        for url in (
            "https://example.test/a b.png",
            "https://example.test/a\tb.png",
            "https://example.test/a\x01b.png",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))


class TestBracketedHosts(unittest.TestCase):
    """A bracketed host must be a closed RFC 3986 IP-literal.

    A bracketed authority must name a host, so ``[]`` and an unclosed
    ``[::1`` are rejected, as is a bracket in an unbracketed host; the
    previously accepted forms let a malformed citation pass as provenance.
    """

    def test_valid_ip_literals_are_accepted(self):
        for url in (
            "https://[::1]/x",
            "https://[::1]:8080/x",
            "https://user@[2001:db8::1]/x",
            "https://[v1.fe80::a]/x",
            # ABNF literals are case insensitive, so the IPvFuture ``v``
            # may be uppercase too.
            "https://[V1.a]/x",
            "file://[::1]/x",
        ):
            self.assertTrue(is_absolute_url(url), url)

    def test_malformed_bracketed_hosts_are_rejected(self):
        for url in (
            "https://[]/x",
            # ``file`` is the one scheme allowed an empty host, for
            # ``file:///path``; an empty *bracketed* host is still malformed.
            "file://[]/x",
            "file://[]",
            "file://[]:80/x",
            "https://[::1/x",
            "https://[not-an-ip]/x",
            "https://[::1]extra/x",
            # RFC 3986 IPv6address has no zone identifier; Python's
            # ``ipaddress`` accepts one, so a raw or percent-encoded scope
            # used to pass as a well-formed host.
            "https://[fe80::1%eth0]/x",
            "https://[fe80::1%25eth0]/x",
            "https://[::1%eth0]/x",
        ):
            self.assertFalse(is_absolute_url(url), url)

    def test_brackets_outside_a_bracketed_host_are_rejected(self):
        for url in (
            "https://exa[mple].test/x",
            "https://example.test]/x",
        ):
            self.assertFalse(is_absolute_url(url), url)


class TestUnbracketedHostCharacters(unittest.TestCase):
    r"""An unbracketed host is an RFC 3986 reg-name.

    The authority parser checked only that the host was non-empty, so a
    character no reg-name allows (``<``, ``>``, ``{``, ``}``, ``\``, ``"``,
    ``|``, ``^``, a backtick, a raw non-ASCII byte or a bare percent) passed
    as a well-formed citation.
    """

    def test_reg_name_characters_are_accepted(self):
        for url in (
            "https://example.test/x",
            "https://sub-domain.example.test/x",
            "https://under_score.example/x",
            "https://tilde~name.example/x",
            "https://a!$&'()*+,;=.example/x",
            "https://pct%41.example/x",
            "https://pct%41",
            "https://192.168.1.1/x",
        ):
            self.assertTrue(is_absolute_url(url), url)

    def test_non_reg_name_characters_are_rejected(self):
        for url in (
            "https://a<b>c.example/x",
            "https://a{b}c.example/x",
            "https://host\\name.example/x",
            'https://host"name.example/x',
            "https://host|name.example/x",
            "https://host^name.example/x",
            "https://host`name.example/x",
            "https://exa%2.example/x",
            "https://exa%zz.example/x",
            "https://exa%mple.example/x",
            "https://host%",
            "https://host%4",
            "https://a%b",
            "https://\u00e9xample.test/x",
        ):
            self.assertFalse(is_absolute_url(url), repr(url))


class TestUserinfoCharacters(unittest.TestCase):
    r"""Userinfo is an RFC 3986 userinfo.

    The authority parser split the authority at ``@`` and validated only the
    host, so a userinfo holding a character no userinfo allows (``<``, ``>``,
    ``{``, ``}``, ``\``, ``"``, ``|``, ``^``, a backtick, a raw non-ASCII
    byte, a bare percent or an unencoded ``@``) passed as a well-formed
    citation.
    """

    def test_userinfo_characters_are_accepted(self):
        for url in (
            "https://@example.test/x",
            "https://user@example.test/x",
            "https://user:pass@example.test/x",
            "https://a:b:c@example.test/x",
            "https://a!$&'()*+,;=:b@example.test/x",
            "https://pct%41@example.test/x",
            "https://user@[2001:db8::1]/x",
        ):
            self.assertTrue(is_absolute_url(url), url)

    def test_non_userinfo_characters_are_rejected(self):
        for url in (
            "https://a<b>@example.test/x",
            "https://a{b}c@example.test/x",
            "https://host\\name@example.test/x",
            'https://host"name@example.test/x',
            "https://host|name@example.test/x",
            "https://host^name@example.test/x",
            "https://host`name@example.test/x",
            "https://user@@example.test/x",
            "https://exa%2@example.test/x",
            "https://exa%zz@example.test/x",
            "https://\u00e9xample@example.test/x",
        ):
            self.assertFalse(is_absolute_url(url), repr(url))


class TestPathQueryFragmentCharacters(unittest.TestCase):
    r"""The path, query and fragment are held to their RFC 3986 sets.

    The parser checked the scheme, whitespace and authority but never the
    path, query or fragment, so a bare percent or a raw character no
    ``pchar`` allows (``<``, ``{``, a backslash, a non-ASCII byte) passed as
    a well-formed citation.
    """

    def test_path_query_fragment_characters_are_accepted(self):
        for url in (
            "https://example.test/a/b.png",
            "https://example.test/a%20b.png",
            "https://example.test/a:b@c/d",
            "https://example.test/a!$&'()*+,;=b",
            "https://example.test",
            "https://example.test/",
            "https://example.test/?",
            "https://example.test/#",
            "https://example.test/a?q=1&b=2",
            "https://example.test/a?q=1#frag",
            # A query and a fragment may each hold a ``?`` of their own.
            "https://example.test/a?q=1?2",
            "https://example.test#frag?q",
        ):
            self.assertTrue(is_absolute_url(url), url)

    def test_malformed_path_query_fragment_characters_are_rejected(self):
        for url in (
            "https://example.test/%",
            "https://example.test/a%2",
            "https://example.test/a%zz",
            "https://example.test/a%?q",
            "https://example.test/a<b>",
            "https://example.test/a{b}",
            "https://example.test/a\\b",
            'https://example.test/a"b',
            "https://example.test/a|b",
            "https://example.test/a^b",
            "https://example.test/a`b",
            "https://example.test/a\u00e9b",
            "https://example.test/a?q=<b>",
            "https://example.test/a?q=%",
            "https://example.test/a#f<b>",
        ):
            self.assertFalse(is_absolute_url(url), repr(url))


class TestAuthorityPorts(unittest.TestCase):
    """A port is ``*DIGIT``; anything else is a malformed citation.

    The authority parser used to take everything before the first ``:`` as the
    host and ignore the rest, so ``https://host:80:90/x`` and
    ``https://host:abc/x`` passed as well-formed provenance.
    """

    def test_digit_and_empty_ports_are_accepted(self):
        for url in (
            "https://host:80/x",
            "https://host:/x",
            "https://user:pass@host:8080/x",
            "https://[::1]:80/x",
            "https://[::1]:/x",
            "file://host:80/x",
        ):
            self.assertTrue(is_absolute_url(url), url)

    def test_non_digit_ports_are_rejected(self):
        for url in (
            "https://host:abc/x",
            "https://host:80:90/x",
            "https://host:8 0/x",
            "https://user@host:1:2/x",
            "https://[::1]:abc/x",
            "https://[::1]:80:90/x",
        ):
            self.assertFalse(is_absolute_url(url), url)


if __name__ == "__main__":
    unittest.main()
