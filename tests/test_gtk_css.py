"""The shared GTK stylesheet parser must stay linear on hostile sheets.

``gtk.css`` is contributor-supplied, so a malformed or deliberately hostile
sheet must not be able to stall ``make check``. The comment and rule scanners
in ``support.gtk_css`` replace two backtracking regular expressions that were
quadratic on input a contributor controls: many comment starts with no end,
and a long run of text with no brace. The timing cases below use a size where
the old expressions took seconds while the scanners finish in milliseconds;
the bound is generous so a slow machine does not flake.
"""

from __future__ import annotations

import time
import unittest

from support.gtk_css import parse_css, strip_comments


class TestStripComments(unittest.TestCase):
    def test_removes_each_comment_and_keeps_the_text_between(self):
        self.assertEqual(strip_comments("a/*x*/b/*y*/c"), "abc")
        self.assertEqual(strip_comments("/* only a comment */"), "")

    def test_keeps_an_unterminated_comment_in_place(self):
        # The regular expression required both delimiters, so it removed
        # nothing when the closing ``*/`` was absent. The scanner must not
        # start treating the rest of the sheet as a comment.
        self.assertEqual(strip_comments("a/*x"), "a/*x")
        self.assertEqual(strip_comments("/*a/*b*/c"), "c")


class TestParseCss(unittest.TestCase):
    def test_a_colour_named_in_a_comment_is_not_a_definition(self):
        definitions, rules, selectors = parse_css(
            "/* @define-color commented #000000; */\n"
            "a { color: #111111; }\n"
        )
        self.assertEqual(definitions, {})
        self.assertEqual(rules, {"a": {"color": "#111111"}})
        self.assertEqual(selectors, ["a"])

    def test_a_declaration_without_a_colon_is_rejected(self):
        # A missing ':' used to drop the declaration silently, leaving a sheet
        # test that pinned it to fail on a missing key instead of the typo.
        with self.assertRaisesRegex(
            ValueError,
            r"^theme/gtk/org\.macos8\.desktop/gtk-3\.0/gtk\.css: "
            r"malformed declaration in selector 'a': "
            r"'background #111111' \(expected 'property: value'\)$",
        ):
            parse_css(
                "a { background #111111; }",
                source="theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css",
            )

    def test_an_empty_property_name_or_value_is_rejected(self):
        for text in ("a { : #111111; }", "a { color: ; }"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(
                    ValueError,
                    r"^<stylesheet>: malformed declaration in selector 'a': ",
                ):
                    parse_css(text)

    def test_empty_declarations_between_semicolons_are_ignored(self):
        # The sheet's trailing ';' (and a doubled one) is not a declaration.
        self.assertEqual(
            parse_css("a { ; ; color: #111111; ; }")[1],
            {"a": {"color": "#111111"}},
        )

    def test_a_semicolon_inside_a_string_or_url_is_not_a_separator(self):
        # A quoted string and a url() value carry ';' in the value, not between
        # declarations; splitting there reported the value's tail as malformed.
        cases = {
            'content: "x;y"': {"content": '"x;y"'},
            'background-image: url("data:image/svg+xml;base64,AAAA")': {
                "background-image": 'url("data:image/svg+xml;base64,AAAA")'
            },
            "background-image: url(data:image/svg+xml;base64,AAAA)": {
                "background-image": "url(data:image/svg+xml;base64,AAAA)"
            },
        }
        for declaration, expected in cases.items():
            with self.subTest(declaration=declaration):
                self.assertEqual(
                    parse_css(f"a {{ {declaration}; margin: 1px; }}")[1],
                    {"a": dict(expected, margin="1px")},
                )

    def test_an_escaped_or_foreign_quote_does_not_end_a_string(self):
        # A backslash-escaped quote and the other quote character stay inside
        # the string, so the ';' after them is still part of the value.
        cases = (
            'content: "a\\"b;c"',
            "content: 'a\"b;c'",
        )
        for declaration in cases:
            with self.subTest(declaration=declaration):
                value = declaration.split(": ", 1)[1]
                self.assertEqual(
                    parse_css(f"a {{ {declaration}; margin: 1px; }}")[1],
                    {"a": {"content": value, "margin": "1px"}},
                )

    def test_a_stray_closing_parenthesis_does_not_hide_a_separator(self):
        # An unmatched ')' must not drive the depth negative and swallow the
        # ';' that follows.
        self.assertEqual(
            parse_css("a { color: red); margin: 1px; }")[1],
            {"a": {"color": "red)", "margin": "1px"}},
        )

    def test_a_block_without_a_selector_is_not_a_rule(self):
        self.assertEqual(
            parse_css("{color:#111111} b{color:#222222}"),
            ({}, {"b": {"color": "#222222"}}, ["b"]),
        )


class TestRuleBlockSemantics(unittest.TestCase):
    """The scanner must keep the parsing rules of the regular expression it replaced.

    ``_rule_blocks`` replaced ``(?P<selectors>[^{}]+)\\{(?P<body>[^{}]*)\\}``
    so the parser would stay linear on a hostile sheet. The shipped sheets do
    not happen to contain these shapes, so without direct cases a later
    simplification of the scanner could change how a rule is paired and only
    the GTK sheet tests would be at risk of reading the wrong declarations.
    """

    def test_a_later_block_replaces_an_earlier_declaration(self):
        # parse_css documents the cascade: a repeated selector keeps every
        # declaration, with the later block's declaration replacing an earlier
        # one. A declaration the later block does not repeat survives, and the
        # selector list records both occurrences.
        self.assertEqual(
            parse_css(
                "a { color: #111111; margin: 1px; } a { color: #222222; }"
            ),
            (
                {},
                {"a": {"color": "#222222", "margin": "1px"}},
                ["a", "a"],
            ),
        )

    def test_a_comma_separated_group_shares_its_declarations(self):
        # Whitespace is collapsed before the group is split, so a newline
        # between selectors names the same two selectors as a space does, and
        # both get a copy of the block's declarations.
        self.assertEqual(
            parse_css("a,\n  b { color :  #111111 ; }"),
            (
                {},
                {"a": {"color": "#111111"}, "b": {"color": "#111111"}},
                ["a", "b"],
            ),
        )

    def test_a_comma_inside_parentheses_does_not_split_the_group(self):
        self.assertEqual(
            parse_css("a:not(.x, .y), b { color: #111111; }"),
            (
                {},
                {
                    "a:not(.x, .y)": {"color": "#111111"},
                    "b": {"color": "#111111"},
                },
                ["a:not(.x, .y)", "b"],
            ),
        )

    def test_a_nested_block_replaces_the_pending_selector(self):
        # The expression's selector body could not cross a brace, so the inner
        # block's text became its match: only `a` is a rule here, not `x`.
        self.assertEqual(
            parse_css("x{a{color:#111111}}"),
            ({}, {"a": {"color": "#111111"}}, ["a"]),
        )

    def test_a_stray_closing_brace_is_skipped(self):
        # A `}` that closes no pending block must neither start a rule nor
        # swallow the selector after it.
        self.assertEqual(
            parse_css("a{color:#111111;} } b{color:#222222;}"),
            (
                {},
                {"a": {"color": "#111111"}, "b": {"color": "#222222"}},
                ["a", "b"],
            ),
        )

    def test_a_define_color_is_returned_and_not_taken_for_a_selector(self):
        # Removing definitions before scanning keeps their text, including the
        # trailing semicolon, out of the pending-selector run for the first
        # real block; the value itself is still returned to the caller.
        self.assertEqual(
            parse_css("@define-color x #123456;\na { color: @x; }"),
            ({"x": "#123456"}, {"a": {"color": "@x"}}, ["a"]),
        )


class TestHostileStylesheet(unittest.TestCase):
    def test_comment_scanning_finishes_promptly(self):
        # 8000 ``/*a`` starts and no ``*/``: the lazy comment body rescanned
        # to the end from every start, taking about two seconds at 24 KB and
        # growing quadratically with the sheet.
        text = "/*a" * 8000
        started = time.monotonic()
        definitions, rules, selectors = parse_css(text)
        elapsed = time.monotonic() - started
        self.assertEqual((definitions, rules, selectors), ({}, {}, []))
        self.assertLess(
            elapsed, 1.0, f"parsing {len(text)} bytes took {elapsed:.3f}s"
        )

    def test_rule_scanning_finishes_promptly(self):
        # 20 KB with no brace: the selector expression rescanned to the end
        # from every starting position, taking over five seconds here and
        # growing quadratically with the sheet.
        text = "a" * 20000
        started = time.monotonic()
        definitions, rules, selectors = parse_css(text)
        elapsed = time.monotonic() - started
        self.assertEqual((definitions, rules, selectors), ({}, {}, []))
        self.assertLess(
            elapsed, 1.0, f"parsing {len(text)} bytes took {elapsed:.3f}s"
        )


if __name__ == "__main__":
    unittest.main()
