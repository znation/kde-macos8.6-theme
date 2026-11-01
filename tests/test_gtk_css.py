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

from support.gtk_css import _define_color_matches, parse_css, strip_comments


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

    def test_escaped_colons_in_declaration_names(self):
        css = (
            r"a, b { --tone\:active: red; --many\:parts\:here: "
            r"url(https://example.test/a:b); } "
            r"a { --tone\:active: blue !important; } "
            r"a { --tone\:active: green; }"
        )
        self.assertEqual(
            parse_css(css),
            (
                {},
                {
                    "a": {
                        r"--tone\:active": "blue !important",
                        r"--many\:parts\:here": "url(https://example.test/a:b)",
                    },
                    "b": {
                        r"--tone\:active": "red",
                        r"--many\:parts\:here": "url(https://example.test/a:b)",
                    },
                },
                ["a", "b", "a", "a"],
            ),
        )
        self.assertEqual(
            parse_css("a { --odd\\:name: value; --even\\\\: value; }")[1]["a"],
            {"--odd\\:name": "value", "--even\\\\": "value"},
        )

    def test_escaped_colon_without_separator_is_malformed(self):
        for declaration in (r"--tone\:active", ": value", "name:"):
            with self.subTest(declaration=declaration):
                with self.assertRaisesRegex(
                    ValueError,
                    r"^source\.css: malformed declaration in selector 'a':",
                ):
                    parse_css(f"a {{ {declaration}; }}", source="source.css")

    def test_escaped_colon_names_preserve_values_and_priority_ties(self):
        cases = (
            (r"a { --tone\:active: red; color: blue; }",
             {r"--tone\:active": "red", "color": "blue"}, ["a"]),
            (r"a { --tone\:active\:hover: red; }",
             {r"--tone\:active\:hover": "red"}, ["a"]),
            (r"a { --slashes\\:name: red; }",
             {r"--slashes\\": "name: red"}, ["a"]),
            (r"a { --slashes\:name: red; }",
             {r"--slashes\:name": "red"}, ["a"]),
            (r"a { --tone\:active: url(https://example.test/a:b); }",
             {r"--tone\:active": "url(https://example.test/a:b)"}, ["a"]),
            (r"a, b { --tone\:active: red; }",
             {r"--tone\:active": "red"}, ["a", "b"]),
        )
        for text, expected_rules, selectors in cases:
            with self.subTest(text=text):
                self.assertEqual(parse_css(text), ({}, {s: expected_rules.copy() for s in selectors}, selectors))

        self.assertEqual(
            parse_css(r"a { --tone\:active: red; --tone\:active: blue !important; "
                      r"--tone\:active: green; }")[1]["a"][r"--tone\:active"],
            "blue !important",
        )
        self.assertEqual(
            parse_css(r"a { --tone\:active: red !important; "
                      r"--tone\:active: blue !important; }")[1]["a"][r"--tone\:active"],
            "blue !important",
        )
        for text in (r"a { --tone\:active; }", "a { : red; }", "a { color: ; }"):
            with self.subTest(text=text), self.assertRaisesRegex(
                ValueError,
                r"^source\.css: malformed declaration in selector 'a':",
            ):
                parse_css(text, source="source.css")

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

    def test_escaped_trailing_value_whitespace_is_preserved(self):
        cases = (
            (r"token\ ; color: red;", r"token\ ", {"color": "red"}),
            ("token\\\t; color: red;", "token\\\t", {"color": "red"}),
            (r"token\ }", r"token\ ", {}),
            ("token\\\t}", "token\\\t", {}),
            (r"token\   ; color: red;", r"token\ ", {"color": "red"}),
            (r"token\\   ; color: red;", r"token\\", {"color": "red"}),
            ("token   ; color: red;", "token", {"color": "red"}),
        )
        for body, expected_value, following in cases:
            with self.subTest(body=body):
                _, rules, selectors = parse_css("a { --sample: " + body + " }")
                self.assertEqual(selectors, ["a"])
                self.assertEqual(rules["a"], {"--sample": expected_value, **following})

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

    def test_ordinary_declaration_names_fold_ascii_case(self):
        self.assertEqual(
            parse_css(
                "a { COLOR: red !important; color: blue; -WebKit-Thing: One; } "
                "a { CoLoR: green; -webkit-thing: Two; }"
            ),
            (
                {},
                {"a": {"color": "red !important", "-webkit-thing": "Two"}},
                ["a", "a"],
            ),
        )

    def test_escaped_ordinary_declaration_names_are_canonicalized(self):
        cases = (
            (r"\61 ", "a"),
            (r"\061 ", "a"),
            (r"\0061 ", "a"),
            (r"\00061 ", "a"),
            (r"\000061", "a"),
            ("\\000061\r\n", "a"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(parse_css("a { " + source + ": red; }")[1]["a"], {expected: "red"})

        self.assertEqual(
            parse_css(r"a { \63 olor: red; color: blue; \000063olor: green; co\lor: gold; }")[1]["a"],
            {"color": "gold"},
        )
        self.assertEqual(
            parse_css(r"a { -\77 ebkit-thing: one; -webkit-thing: two; }")[1]["a"],
            {"-webkit-thing": "two"},
        )
        self.assertEqual(
            parse_css("a { \\0000617: red; \\0000c4lor: blue; \\000000: zero; \\00d800: surrogate; \\110000: large; }")[1]["a"],
            {"a7": "red", "\u00c4lor": "blue", "\ufffd": "large"},
        )

    def test_escaped_property_names_share_cascade_priority(self):
        cases = (
            (r"a { color: red; \63 olor: blue; }", "blue"),
            (r"a { \63 olor: red; color: blue; }", "blue"),
            (r"a { color: red !important; \63 olor: blue; }", "red !important"),
            (r"a { \63 olor: blue; color: red !important; }", "red !important"),
            (r"a { color: red; } a { \63 olor: blue; }", "blue"),
            (r"a { color: red !important; } a { \63 olor: blue; }", "red !important"),
        )
        for css, expected in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css)[1]["a"]["color"], expected)

    def test_custom_and_invalid_escaped_property_names_keep_source_spelling(self):
        self.assertEqual(
            parse_css("a { --\\63 olor: red; \\2d-escaped: blue; bad\\\\: red; bad\\\nname: green; }")[1]["a"],
            {r"--\63 olor": "red", r"\2d-escaped": "blue", "bad\\": "red", "bad\\\nname": "green"},
        )

    def test_ordinary_declaration_names_decode_css_escapes_before_merging(self):
        cases = (
            (r"a { \63 olor: red !important; color: blue; }", {"color": "red !important"}, ["a"]),
            (r"a { color: red; co\lor: blue; } a { \43 olor: green; }",
             {"color": "green"}, ["a", "a"]),
            (r"a, b { -\57 ebkit-Thing: one; -webkit-thing: two; }",
             {"-webkit-thing": "two"}, ["a", "b"]),
            (r"a { \000063olor: one; \63 olor: two; }", {"color": "two"}, ["a"]),
            (r"a { \1234567: value; }", {"�7": "value"}, ["a"]),
            (r"a { \e9: one; \c9: two; }", {"é": "one", "É": "two"}, ["a"]),
        )
        for css, expected, selectors in cases:
            with self.subTest(css=css):
                _, rules, actual_selectors = parse_css(css)
                self.assertEqual(rules["a"], expected)
                self.assertEqual(actual_selectors, selectors)

        _, rules, _ = parse_css("a { \\0: zero; \\d800: surrogate; \\110000: large; }")
        self.assertEqual(rules["a"], {"�": "large"})
        _, rules, _ = parse_css("a { \\63\tolor: first; color: second; \\63\r\nolor: third; }")
        self.assertEqual(rules["a"], {"color": "third"})
        _, rules, _ = parse_css(r"a { \;name: literal; }")
        self.assertEqual(rules["a"], {";name": "literal"})
        _, rules, _ = parse_css(r"a { co\:lor: escaped colon; }")
        self.assertEqual(rules["a"], {"co:lor": "escaped colon"})
        _, rules, _ = parse_css("a { broken\\\n name: literal; }")
        self.assertEqual(list(rules["a"].values()), ["literal"])
        self.assertTrue(next(iter(rules["a"])).startswith("broken"))
        _, rules, _ = parse_css(
            r"a { \63 olor: two; \063 olor: three; \0063olor: four; "
            r"\00063olor: five; \000063olor: six; }"
        )
        self.assertEqual(rules["a"], {"color": "six"})
        _, rules, _ = parse_css(r"a { \a: one; }")
        self.assertEqual(rules["a"], {"\n": "one"})
        self.assertEqual(
            parse_css(r"a { --Tone: one; --tone: two; --tone\:active: three; }")[1]["a"],
            {"--Tone": "one", "--tone": "two", r"--tone\:active": "three"},
        )

    def test_custom_property_names_and_non_ascii_name_characters_are_preserved(self):
        self.assertEqual(
            parse_css("a { --Tone: One; --tone: Two; Cİlor: red; COLOR: blue; }"),
            (
                {},
                {"a": {"--Tone": "One", "--tone": "Two", "cİlor": "red", "color": "blue"}},
                ["a"],
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
        for whitespace in (" ", "\t"):
            for slash_count in (1, 3):
                with self.subTest(whitespace=repr(whitespace), slashes=slash_count):
                    value = "token" + "\\" * slash_count + whitespace
                    for suffix in ("; color: red;", ""):
                        source = f"a {{ --value: {value}   {suffix}}}"
                        expected = "token" + "\\" * slash_count + whitespace
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

    def test_a_nested_block_replaces_the_pending_selector(self):
        # The expression's selector body could not cross a brace, so the inner
        # block's text became its match: only `a` is a rule here, not `x`.
        self.assertEqual(
            parse_css("x{a{color:#111111}}"),
            ({}, {"a": {"color": "#111111"}}, ["a"]),
        )

    def test_a_brace_inside_a_quoted_string_does_not_pair_a_block(self):
        # A quoted value or selector may hold a brace. Treating it as a block
        # delimiter cut the declaration in two and reported the quoted text as
        # a selector, so the rule lost its declarations.
        self.assertEqual(
            parse_css(
                'a { content: "}"; color: #111111; } b { color: #222222; }'
            ),
            (
                {},
                {
                    "a": {"content": '"}"', "color": "#111111"},
                    "b": {"color": "#222222"},
                },
                ["a", "b"],
            ),
        )
        self.assertEqual(
            parse_css('a { content: "{"; color: #111111; }')[1],
            {"a": {"content": '"{"', "color": "#111111"}},
        )
        self.assertEqual(
            parse_css('[title="{"] { color: #111111; }')[1],
            {'[title="{"]': {"color": "#111111"}},
        )

    def test_a_brace_inside_an_unquoted_url_value_is_text(self):
        # An unquoted url() token may hold braces (CSS url code points), and
        # quotes inside it do not open a string. A brace there paired the
        # pending selector with half the declaration and reported the rest as
        # a malformed declaration of a bogus selector. The declaration scanner
        # already treats parentheses this way; the block scanner does the
        # same, and a quote inside parentheses stays literal either way.
        self.assertEqual(
            parse_css(
                "a { background-image: url(data:image/svg+xml,<g {x}>);"
                " color: #111111; } b { color: #222222; }"
            ),
            (
                {},
                {
                    "a": {
                        "background-image":
                            "url(data:image/svg+xml,<g {x}>)",
                        "color": "#111111",
                    },
                    "b": {"color": "#222222"},
                },
                ["a", "b"],
            ),
        )
        self.assertEqual(
            parse_css(
                "a { background-image: url(data:image/svg+xml,<g {x}>) }"
            )[1],
            {"a": {"background-image": "url(data:image/svg+xml,<g {x}>)"}},
        )
        self.assertEqual(
            parse_css(
                "a[href=\"}\"] { content: url(data:x{y}); margin: 1px; }"
            )[1],
            {
                'a[href="}"]': {
                    "content": "url(data:x{y})",
                    "margin": "1px",
                },
            },
        )

    def test_braces_inside_square_bracket_values_are_preserved(self):
        cases = (
            ("a { --tokens: [x{y}z]; color: red; } b { color: blue; }",
             ["a", "b"],
             {"a": {"--tokens": "[x{y}z]", "color": "red"},
              "b": {"color": "blue"}}),
            ("a, b { --tokens: [[x{y};z]]; color: red; }",
             ["a", "b"],
             {"a": {"--tokens": "[[x{y};z]]", "color": "red"},
              "b": {"--tokens": "[[x{y};z]]", "color": "red"}}),
            ("a { --tokens: fn([x{y}]); }",
             ["a"], {"a": {"--tokens": "fn([x{y}])"}}),
            ("a { --tokens: [fn(x{y})]; }",
             ["a"], {"a": {"--tokens": "[fn(x{y})]"}}),
            ('a { --tokens: ["[x{y}]"]; color: red; }',
             ["a"],
             {"a": {"--tokens": '["[x{y}]"]', "color": "red"}}),
            (r"a { --tokens: [x\] {y}]; color: red; }",
             ["a"],
             {"a": {"--tokens": r"[x\] {y}]", "color": "red"}}),
            (r"a { --tokens: [x\[ {y}]; color: red; }",
             ["a"],
             {"a": {"--tokens": r"[x\[ {y}]", "color": "red"}}),
            ("a { --tokens: [x{y}z]}", ["a"],
             {"a": {"--tokens": "[x{y}z]"}}),
        )
        for css, selectors, rules in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css), ({}, rules, selectors))
        self.assertEqual(
            parse_css("] a { color: red; } b { color: blue; }")[2],
            ["] a", "b"],
        )

    def test_a_stray_closing_parenthesis_does_not_hide_a_brace_either(self):
        # Mirrors the declaration scanner: an unmatched ')' must not drive the
        # depth negative and make the following block delimiters disappear.
        self.assertEqual(
            parse_css("a { color: red) } b { color: #222222; }"),
            (
                {},
                {"a": {"color": "red)"}, "b": {"color": "#222222"}},
                ["a", "b"],
            ),
        )

    def test_important_declarations_win_with_later_ties(self):
        cases = (
            ("a { color: red !important; color: blue; }", "red !important"),
            ("a { color: blue; color: red !important; }", "red !important"),
            ("a { color: red !important; } a { color: blue; }", "red !important"),
            ("a { color: blue; } a { color: red !important; }", "red !important"),
            ("a { color: red !important; } a { color: green ! IMPORTANT; }", "green ! IMPORTANT"),
            ("a { color: red !important; } a { color: blue !important; }", "blue !important"),
        )
        for css, expected in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css)[1]["a"]["color"], expected)

    def test_important_priority_requires_css_whitespace(self):
        non_css_whitespace = ("\u00a0", "\u2003", "\v")
        for separator in non_css_whitespace:
            with self.subTest(separator=repr(separator)):
                invalid = f"red !{separator}important"
                self.assertEqual(
                    parse_css(f"a {{ color: {invalid}; color: blue; }}")[1]["a"]["color"],
                    "blue",
                )
                self.assertEqual(
                    parse_css(f"a {{ color: {invalid}; }} a {{ color: blue; }}")[1]["a"]["color"],
                    "blue",
                )
                self.assertEqual(parse_css(f"a {{ color: {invalid}; }}")[1]["a"]["color"], invalid)

        for separator in (" ", "\t", "\n", "\r", "\f", " \t\n\r\f"):
            with self.subTest(separator=repr(separator)):
                for trailing in ("", separator):
                    with self.subTest(trailing=repr(trailing)):
                        css = f"a {{ color: red !{separator}IMPORTANT{trailing}; color: blue; }}"
                        self.assertEqual(parse_css(css)[1]["a"]["color"], "red ! IMPORTANT")

    def test_important_keyword_uses_ascii_case_folding(self):
        for lookalike in ("\u0131", "\u0130"):
            with self.subTest(lookalike=repr(lookalike)):
                invalid = f"red !{lookalike}mportant"
                self.assertEqual(parse_css(f"a {{ color: {invalid}; }}")[1]["a"]["color"], invalid)
                self.assertEqual(
                    parse_css(f"a {{ color: {invalid}; color: blue; }}")[1]["a"]["color"],
                    "blue",
                )
                self.assertEqual(
                    parse_css(f"a {{ color: {invalid}; }} a {{ color: blue; }}")[1]["a"]["color"],
                    "blue",
                )

        for keyword in ("important", "IMPORTANT", "ImPoRtAnT"):
            for separator in ("", " "):
                for blocks in (False, True):
                    with self.subTest(keyword=keyword, separator=separator, blocks=blocks):
                        first = f"red !{separator}{keyword}{separator}"
                        css = (
                            f"a {{ color: {first}; }} a {{ color: blue; }}"
                            if blocks
                            else f"a {{ color: {first}; color: blue; }}"
                        )
                        self.assertEqual(parse_css(css)[1]["a"]["color"], first.strip())

    def test_important_keyword_decodes_css_escapes(self):
        valid = (
            r"!\69mportant", r"!\000069mportant", r"!\69 mportant",
            r"!impor\74 ant", r"!\49\4DPORTANT", r"!impor\tant",
        )
        for suffix in valid:
            for repeated_block in (False, True):
                with self.subTest(suffix=suffix, repeated_block=repeated_block):
                    value = "red " + suffix
                    css = (
                        f"a {{ color: {value}; }} a {{ color: blue; }}"
                        if repeated_block
                        else f"a {{ color: {value}; color: blue; }}"
                    )
                    self.assertEqual(parse_css(css)[1]["a"]["color"], value)

        for suffix in (
            r"!importantx", "!impor tant", r"!\0mportant", r"!\110000mportant",
            r"!\D800mportant", "!\\\nimportant", r"red\!important",
            '"!important"',
        ):
            with self.subTest(invalid_suffix=suffix):
                css = f"a {{ color: red {suffix}; color: blue; }}"
                self.assertEqual(parse_css(css)[1]["a"]["color"], "blue")

        self.assertEqual(
            parse_css(r"a { color: red !\69 mportant; }")[1]["a"]["color"],
            r"red !\69 mportant",
        )

    def test_important_scanner_ignores_strings_urls_and_escaped_bangs(self):
        css = (
            'a { x: red !important; y: blue; } '
            'a { x: green; y: "!important"; z: url(icon!important); '
            'w: red\\!important; } '
            'a, b { x: black; }'
        )
        definitions, rules, selectors = parse_css(css)
        self.assertEqual(definitions, {})
        self.assertEqual(rules["a"], {
            "x": "red !important", "y": '"!important"',
            "z": "url(icon!important)", "w": r"red\!important",
        })
        self.assertEqual(rules["b"], {"x": "black"})
        self.assertEqual(selectors, ["a", "a", "a", "b"])

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

    def test_define_color_separators_require_css_whitespace(self):
        # The definition regular expression scanned with Python's Unicode
        # whitespace, so a directive whose separators were U+00A0, U+2003 or
        # U+000B still entered the map; CSS whitespace is exactly space, tab,
        # LF, CR and form feed, and the three separator positions are the run
        # after the directive, the run before the value and the run before the
        # semicolon.
        non_css = ("\u00a0", "\u2003", "\u000b")
        positions = (
            "@define-color{c}x #123456;",
            "@define-color x{c}#123456;",
            "@define-color x #123456{c};",
        )
        for character in non_css:
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                for template in positions:
                    directive = template.format(c=character)
                    self.assertEqual(list(_define_color_matches(directive)), [])
                    self.assertEqual(parse_css(directive)[0], {})
        for character in (" ", "\t", "\n", "\r", "\f"):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                for template in positions:
                    directive = template.format(c=character)
                    self.assertEqual(
                        [match.group("name")
                         for match in _define_color_matches(directive)],
                        ["x"],
                    )
                    self.assertEqual(
                        parse_css(directive)[0], {"x": "#123456"}
                    )
        self.assertEqual(
            parse_css("@define-color \t\n x \r\f #123456 \t\n\r\f;")[0],
            {"x": "#123456"},
        )

    def test_a_define_color_inside_a_quoted_value_is_text(self):
        # The definition scan ran over the whole sheet, so the value both
        # invented a colour definition and lost the text around it.
        cases = (
            '"@define-color decoy #123456;"',
            '"escaped \\" @define-color decoy #123456;"',
        )
        for content in cases:
            with self.subTest(content=content):
                self.assertEqual(
                    parse_css(
                        f"a {{ content: {content}; color: #ABCDEF; }}"
                    ),
                    (
                        {},
                        {
                            "a": {
                                "content": content,
                                "color": "#ABCDEF",
                            }
                        },
                        ["a"],
                    ),
                )

    def test_a_define_color_inside_function_values_is_text(self):
        text = "a { --sample: fn(inner(@define-color phantom #123456;)); color: red; }"
        self.assertEqual(
            parse_css(text),
            (
                {},
                {"a": {"--sample": "fn(inner(@define-color phantom #123456;))", "color": "red"}},
                ["a"],
            ),
        )

    def test_define_color_scan_tracks_function_parentheses(self):
        text = (
            'a { content: fn("(", \\) @define-color hidden #111111; '
            '@define-color also_hidden #333333;); }\n'
            "@define-color shown #222222;"
        )
        self.assertEqual(
            [match.group("name") for match in _define_color_matches(text)],
            ["shown"],
        )
        self.assertEqual(
            [
                match.group("name")
                for match in _define_color_matches(") @define-color shown #222222;")
            ],
            ["shown"],
        )

    def test_a_define_color_inside_a_declaration_block_is_text(self):
        self.assertEqual(
            parse_css(
                "@define-color before #111111;\n"
                "a { --tokens: @define-color embedded #123456; color: red; }\n"
                "@define-color after #222222;"
            ),
            (
                {"before": "#111111", "after": "#222222"},
                {
                    "a": {
                        "--tokens": "@define-color embedded #123456",
                        "color": "red",
                    }
                },
                ["a"],
            ),
        )

    def test_define_color_scan_tracks_braces_outside_functions(self):
        text = (
            'a { content: fn({ @define-color hidden #111111; }); '
            'b { --x: "{ @define-color quoted #222222; }"; '
            r'--y: \{ @define-color escaped #333333; \}; '
            "--z: @define-color nested #444444; } }\n"
            "} @define-color shown #555555;"
        )
        self.assertEqual(
            [match.group("name") for match in _define_color_matches(text)],
            ["shown"],
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
