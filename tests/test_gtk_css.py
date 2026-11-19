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

import itertools
import time
import unittest

from support.gtk_css import (
    inline_link_state_selectors,
    parse_css,
    strip_comments,
)


class TestInlineLinkStateSelectors(unittest.TestCase):
    def test_expands_each_root_over_base_hover_and_active_in_root_order(self):
        self.assertEqual(
            inline_link_state_selectors(("a:link", "a:visited")),
            (
                "a:link",
                "a:link:hover",
                "a:link:active",
                "a:visited",
                "a:visited:hover",
                "a:visited:active",
            ),
        )

    def test_state_and_prefix_wrap_every_root(self):
        # An empty state must still append the suffixes: the GTK 4 suite
        # relies on its roots already carrying the state, so a helper that
        # dropped the suffixes when *state* is empty would silently
        # un-pind the base-state rules there.
        self.assertEqual(
            inline_link_state_selectors(
                ("a:link",), state=":backdrop", prefix=":selected "
            ),
            (
                ":selected a:link:backdrop",
                ":selected a:link:backdrop:hover",
                ":selected a:link:backdrop:active",
            ),
        )


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

    def test_a_comment_marker_inside_a_quoted_string_is_text(self):
        # A CSS string is a token: ``/*`` and ``*/`` inside one are literal
        # text, not comment delimiters. Removing them rewrote the value.
        cases = (
            'a { content: "/* keep */"; }',
            'a { content: "a\\"/* keep */"; }',
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(strip_comments(text), text)

    def test_comment_markers_inside_unquoted_urls_are_text(self):
        cases = (
            "url(https://example.invalid/a/*literal*/b.png)",
            "URL(https://example.invalid/a/*literal*/b.png)",
            "uRl(  https://example.invalid/a/*literal*/b.png)",
            r"url(https://example.invalid/a\)/*literal*/b.png)",
            "url(https://example.invalid/a/*unterminated",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(strip_comments(text), text)
        self.assertEqual(strip_comments("url(\"a/*quoted*/b\")"), "url(\"a/*quoted*/b\")")
        self.assertEqual(strip_comments("myurl(a/*gone*/b)"), "myurl(ab)")
        # Every non-ASCII code point is an identifier character in CSS.
        self.assertEqual(strip_comments("\u2603url(a/*gone*/b)"), "\u2603url(ab)")
        self.assertEqual(strip_comments("\u00b7url(a/*gone*/b)"), "\u00b7url(ab)")
        self.assertEqual(strip_comments("/*before*/url(a/*keep*/b)/*after*/"), "url(a/*keep*/b)")
        self.assertEqual(strip_comments("fn(a/*gone*/b)"), "fn(ab)")


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

    def test_empty_custom_property_values_preserve_grouping_and_priority(self):
        css = (
            "a, b { --empty:; --spaces: \t\n ; --comment: /* only comment */; "
            "color: red; }"
            "a { --empty: ; } a { --empty: blue; }"
            "a { --important: red !important; --later: ; --across: red; }"
            "a { --important: ; --later: blue !important; --across: ; }"
            "a { --case: ; --Case: blue; --tie: red; --tie: ; }"
        )
        self.assertEqual(
            parse_css(css),
            (
                {},
                {
                    "a": {
                        "--empty": "blue",
                        "--spaces": "",
                        "--comment": "",
                        "color": "red",
                        "--important": "red !important",
                        "--later": "blue !important",
                        "--across": "",
                        "--case": "",
                        "--Case": "blue",
                        "--tie": "",
                    },
                    "b": {
                        "--empty": "",
                        "--spaces": "",
                        "--comment": "",
                        "color": "red",
                    },
                },
                ["a", "b", "a", "a", "a", "a", "a"],
            ),
        )

    def test_empty_custom_property_at_semicolon_and_block_end(self):
        self.assertEqual(
            parse_css("a { --semicolon: ; --end: } b { --end:}")[1],
            {"a": {"--semicolon": "", "--end": ""}, "b": {"--end": ""}},
        )

    def test_malformed_empty_declarations_keep_source_prefix(self):
        for text in ("a { color: ; }", "a { --: ; }", "a { : ; }", "a { color; }"):
            with self.subTest(text=text), self.assertRaisesRegex(
                ValueError,
                r"^source\.css: malformed declaration in selector 'a':",
            ):
                parse_css(text, source="source.css")

    def test_empty_custom_property_values_are_retained_and_cascade(self):
        cases = (
            ("--empty:;", ""),
            ("--empty:   ;", ""),
            ("--empty: /* comment */ ;", ""),
        )
        for declaration, expected in cases:
            with self.subTest(declaration=declaration):
                self.assertEqual(
                    parse_css(f"a, b {{ {declaration} color: red; }}"),
                    ({}, {"a": {"--empty": expected, "color": "red"},
                         "b": {"--empty": expected, "color": "red"}}, ["a", "b"]),
                )
        self.assertEqual(
            parse_css("a { --x: old; --x:; } a { --x:; } b { --x: old !important; --x:; } "
                       "c { --x:; --x: new !important; }")[1],
            {"a": {"--x": ""}, "b": {"--x": "old !important"},
             "c": {"--x": "new !important"}},
        )
        self.assertEqual(
            parse_css("a { --Tone: one; --tone: two; }")[1],
            {"a": {"--Tone": "one", "--tone": "two"}},
        )

    def test_empty_bare_custom_and_ordinary_values_remain_malformed(self):
        for declaration in ("--:;", "color:;", " : value", "color"):
            with self.subTest(declaration=declaration):
                with self.assertRaisesRegex(
                    ValueError, r"^source\.css: malformed declaration in selector 'a':",
                ):
                    parse_css(f"a {{ {declaration}; }}", source="source.css")

    def test_unquoted_url_comment_markers_preserve_following_declarations(self):
        css = (
            "a, b { background-image: url(https://example.invalid/a/*literal*/b.png); "
            "color: red; }"
        )
        self.assertEqual(
            parse_css(css),
            (
                {},
                {
                    "a": {
                        "background-image": "url(https://example.invalid/a/*literal*/b.png)",
                        "color": "red",
                    },
                    "b": {
                        "background-image": "url(https://example.invalid/a/*literal*/b.png)",
                        "color": "red",
                    },
                },
                ["a", "b"],
            ),
        )

    def test_hex_escape_terminators_survive_selector_and_value_normalization(self):
        css = (
            r".\31  a { color: red; } .\31 a { margin: 1px; } "
            "a { --hex: \\41   ; --tab: \\42\t  ; --crlf: \\43\r\n  ; }"
        )
        _, rules, selectors = parse_css(css)
        self.assertEqual(selectors, [r".\31  a", r".\31 a", "a"])
        self.assertEqual(rules[r".\31  a"], {"color": "red"})
        self.assertEqual(rules[r".\31 a"], {"margin": "1px"})
        self.assertEqual(rules["a"], {
            "--hex": r"\41 ",
            "--tab": "\\42\t",
            "--crlf": "\\43\r\n",
        })

    def test_hex_escape_selector_terminator_is_distinct_from_separator(self):
        _, rules, selectors = parse_css(r".\31  a { color: red; } .\31 a { margin: 1px; }")
        self.assertEqual(selectors, [r".\31  a", r".\31 a"])
        self.assertEqual(rules, {
            r".\31  a": {"color": "red"},
            r".\31 a": {"margin": "1px"},
        })

    def test_hex_escape_lengths_and_terminators_in_values(self):
        values = (
            (r"\a ", r"\a "),
            (r"\AB ", r"\AB "),
            (r"\123 ", r"\123 "),
            (r"\1234 ", r"\1234 "),
            (r"\12345 ", r"\12345 "),
            (r"\123456 ", r"\123456 "),
            (r"\1234567", r"\1234567"),
        )
        for source, expected in values:
            with self.subTest(source=source):
                _, rules, _ = parse_css("a { --value: " + source + "  ; }")
                self.assertEqual(rules["a"]["--value"], expected)
        _, rules, _ = parse_css("a { --crlf: \\41\r\n  ; }")
        self.assertEqual(rules["a"]["--crlf"], "\\41\r\n")

    def test_semicolons_inside_square_bracket_values_are_preserved(self):
        cases = (
            ("a { --tokens: [a;b]; color: red; }", ["a"],
             {"a": {"--tokens": "[a;b]", "color": "red"}}),
            ("a { --tokens: [[a;b];c]; color: red; }", ["a"],
             {"a": {"--tokens": "[[a;b];c]", "color": "red"}}),
            ("a { --tokens: [a;(b;c)]; color: red; }", ["a"],
             {"a": {"--tokens": "[a;(b;c)]", "color": "red"}}),
            ("a { --tokens: fn([a;b]); color: red; }", ["a"],
             {"a": {"--tokens": "fn([a;b])", "color": "red"}}),
            ('a { --tokens: ["a;b";c]; color: red; }', ["a"],
             {"a": {"--tokens": '["a;b";c]', "color": "red"}}),
            ('a { --tokens: ["[;]";c]; color: red; }', ["a"],
             {"a": {"--tokens": '["[;]";c]', "color": "red"}}),
            (r"a { --tokens: [a\]b;c]; color: red; }", ["a"],
             {"a": {"--tokens": r"[a\]b;c]", "color": "red"}}),
            (r"a { --tokens: [a\[;b]; color: red; }", ["a"],
             {"a": {"--tokens": r"[a\[;b]", "color": "red"}}),
            ("a { --tokens: a]; color: red; }", ["a"],
             {"a": {"--tokens": "a]", "color": "red"}}),
            ("a, b { --tokens: [a;b] }", ["a", "b"],
             {"a": {"--tokens": "[a;b]"}, "b": {"--tokens": "[a;b]"}}),
            (r"a { --tokens: [a\;b]; color: red; }", ["a"],
             {"a": {"--tokens": r"[a\;b]", "color": "red"}}),
        )
        for text, selectors, rules in cases:
            with self.subTest(text=text):
                self.assertEqual(parse_css(text), ({}, rules, selectors))

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

    def test_a_comma_inside_an_attribute_selector_does_not_split_the_group(self):
        # A comma inside an attribute selector's quoted value, or inside its
        # brackets, is part of that value, not a selector-list separator. The
        # splitter used to track only parentheses, so it cut these selectors
        # into fragments that match no rule.
        for selector in ('[title="a,b"]', "[title='a,b']", "[title=a,b]"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    parse_css(f"{selector}, b {{ color: #111111; }}"),
                    (
                        {},
                        {
                            selector: {"color": "#111111"},
                            "b": {"color": "#111111"},
                        },
                        [selector, "b"],
                    ),
                )

    def test_whitespace_inside_a_quoted_selector_value_is_preserved(self):
        # Normalizing a selector collapses a run of whitespace between its
        # tokens, but whitespace inside a quoted attribute value is part of
        # that value: collapsing it renamed the selector and merged two
        # distinct rules into one.
        self.assertEqual(
            parse_css('[title="a  b"] { color: #111111; }')[1:],
            (
                {'[title="a  b"]': {"color": "#111111"}},
                ['[title="a  b"]'],
            ),
        )
        self.assertEqual(
            parse_css(
                '[title="a  b"] { color: #111111; }'
                '[title="a b"] { margin: 1px; }'
            )[1],
            {
                '[title="a  b"]': {"color": "#111111"},
                '[title="a b"]': {"margin": "1px"},
            },
        )

    def test_whitespace_inside_a_quoted_declaration_value_is_preserved(self):
        # The same normalization applies to a declaration's value, where a
        # quoted string may hold significant spaces (``content`` or a URL).
        self.assertEqual(
            parse_css('a { content: "a  b"; }')[1],
            {"a": {"content": '"a  b"'}},
        )
        self.assertEqual(
            parse_css('a { background-image: url("a  b.png"); }')[1],
            {"a": {"background-image": 'url("a  b.png")'}},
        )

    def test_only_css_ascii_whitespace_collapses_between_tokens(self):
        for character in ("\u00a0", "\u2003", "\u000b"):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                self.assertEqual(
                    parse_css(
                        f".a{character}b {{ color: red; }}"
                        ".a b { color: blue; }"
                    ),
                    (
                        {},
                        {
                            f".a{character}b": {"color": "red"},
                            ".a b": {"color": "blue"},
                        },
                        [f".a{character}b", ".a b"],
                    ),
                )
                self.assertEqual(
                    parse_css(f"a {{ content: token{character}name; }}")[1],
                    {"a": {"content": f"token{character}name"}},
                )

        self.assertEqual(
            parse_css(".a \t\n\r\f b { color: red; }")[1:],
            ({".a b": {"color": "red"}}, [".a b"]),
        )

    def test_non_css_whitespace_at_declaration_boundaries_is_preserved(self):
        for character in ("\u00a0", "\u2003", "\u000b"):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                self._boundaries_preserve_or_refuse(character)

    def _boundaries_preserve_or_refuse(self, character):
        """`character` survives verbatim in a value, or a bare one is refused."""
        for value, expected in (
            (f"{character}token", f"{character}token"),
            (f"token{character}", f"token{character}"),
            (f" \t{character}token{character}\r\n",
             f"{character}token{character}"),
            (character, character),
        ):
            with self.subTest(value=repr(value)):
                self.assertEqual(
                    parse_css(f"a {{ content: {value}; }}")[1],
                    {"a": {"content": expected}},
                )

        with self.assertRaisesRegex(
            ValueError,
            r"^source\.css: malformed declaration in selector 'a':",
        ):
            parse_css("a { \u00a0; }" if character == "\u00a0" else
                      f"a {{ {character}; }}", source="source.css")

        self.assertEqual(
            parse_css("a { ; \t\n\r\f; content: token \t; }")[1],
            {"a": {"content": "token"}},
        )

    def test_escaped_trailing_value_whitespace_is_preserved(self):
        # Unescaped trailing whitespace is trimmed: only an escaped run keeps
        # its trailing CSS whitespace, whatever the following declaration is.
        for suffix in ("; color: red;", ""):
            with self.subTest(suffix=suffix):
                declarations = parse_css(f"a {{ --sample: token   {suffix}}}")[1]["a"]
                expected = {"--sample": "token"}
                if suffix:
                    expected["color"] = "red"
                self.assertEqual(declarations, expected)

        for whitespace, slash_count, suffix in itertools.product(
                (" ", "\t"), (1, 2, 3), ("; color: red;", "")):
            with self.subTest(whitespace=repr(whitespace), slashes=slash_count,
                              suffix=suffix):
                value = "token" + "\\" * slash_count + whitespace
                source = f"a {{ --value: {value}   {suffix}}}"
                # A pair of backslashes escapes a literal backslash, so
                # the trailing whitespace escapes only after an odd
                # run; an even run leaves it unescaped and trimmed.
                escaped = slash_count % 2
                expected = "token" + "\\" * slash_count + (whitespace if escaped else "")
                declarations = parse_css(source)[1]["a"]
                self.assertEqual(declarations["--value"], expected)
                if suffix:
                    self.assertEqual(declarations["color"], "red")

        self.assertEqual(
            parse_css("a { --value: token\\\\ ; }")[1],
            {"a": {"--value": "token\\\\"}},
        )
        self.assertEqual(
            parse_css('a { --value: "token "; }')[1],
            {"a": {"--value": '"token "'}},
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
