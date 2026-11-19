"""The shared GTK stylesheet parser merges declarations as the cascade requires.

These cases pin ``support.gtk_css.parse_css``'s declaration merging: name
decoding and ASCII case folding, the first unescaped colon that separates a
name from its value, later-wins replacement of an earlier declaration, and
``!important`` priority. The rule-pairing, grouping, whitespace and
``@define-color`` cases remain in ``tests/test_gtk_css_define_color.py``.
"""

from __future__ import annotations

import itertools
import unittest

from support.gtk_css import parse_css


class TestDeclarationCascade(unittest.TestCase):
    """Pins how ``parse_css`` merges declarations that share a name."""

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
                        "--tone:active": "blue !important",
                        "--many:parts:here": "url(https://example.test/a:b)",
                    },
                    "b": {
                        "--tone:active": "red",
                        "--many:parts:here": "url(https://example.test/a:b)",
                    },
                },
                ["a", "b", "a", "a"],
            ),
        )
        self.assertEqual(
            parse_css("a { --odd\\:name: value; --even\\\\: value; }")[1]["a"],
            {"--odd:name": "value", "--even\\": "value"},
        )

    def test_escaped_colon_without_separator_is_malformed(self):
        for declaration in (r"--tone\:active", ": value", "name:"):
            with self.subTest(declaration=declaration):
                with self.assertRaisesRegex(
                    ValueError,
                    r"^source\.css: malformed declaration in selector 'a':",
                ):
                    parse_css(f"a {{ {declaration}; }}", source="source.css")

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
        self.assertEqual(
            parse_css("a { COLOR: red !important; } a { color: Blue !important; }"),
            ({}, {"a": {"color": "Blue !important"}}, ["a", "a"]),
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
            (r"a { \63 olor: red !important; color: blue; }", "red !important"),
            (r"a { \63 olor: red !important; } a { color: blue; }", "red !important"),
            (r"a, b { \63 olor: red; } a { color: blue; }", "blue"),
        )
        for css, expected in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css)[1]["a"]["color"], expected)
        self.assertEqual(
            parse_css(r"a { \63 olor: red !important; color: blue; }"),
            ({}, {"a": {"color": "red !important"}}, ["a"]),
        )

    def test_escaped_colon_in_ordinary_name_decodes_without_moving_separator(self):
        self.assertEqual(
            parse_css(r"a { Foo\:Bar: red; foo\3a bar: blue !important; }")[1]["a"],
            {"foo:bar": "blue !important"},
        )

    def test_custom_names_decode_and_invalid_escaped_names_keep_source_spelling(self):
        self.assertEqual(
            parse_css("a { --\\63 olor: red; \\2d-escaped: blue; bad\\\\: red; bad\\\nname: green; }")[1]["a"],
            {"--color": "red", "--escaped": "blue", "bad\\": "red", "bad\\\nname": "green"},
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
            {"--Tone": "one", "--tone": "two", "--tone:active": "three"},
        )

    def test_custom_property_names_decode_without_case_folding_before_merging(self):
        cases = (
            (r"a { --tone: red !important; --t\6f ne: blue; }", {"--tone": "red !important"}),
            (r"a { --tone: red; --t\6f ne: blue; }", {"--tone": "blue"}),
            (r"a { --tone: red; --t\6f ne: blue; } a { --t\6f ne: green; }", {"--tone": "green"}),
            (r"a,b { --t\6f ne: red; } a { --tone: blue; }", {"--tone": "blue"}),
            (r"a { --Tone: upper; --t\6f ne: lower; --T\4f ne: other; }", {"--Tone": "upper", "--tone": "lower", "--TOne": "other"}),
            (r"a { \2d-tone: simple; --tone: literal; }", {"--tone": "literal"}),
            ("a { --t\\6f\r\nne: crlf; --tone: literal; }", {"--tone": "literal"}),
            (r"a { --\110000: replacement; --�: literal; }", {"--�": "literal"}),
            (r"a { --\e9: lower; --\c9: upper; }", {"--é": "lower", "--É": "upper"}),
            ("a { --to\\\nne: newline; --tone: literal; }", {"--to\\\nne": "newline", "--tone": "literal"}),
        )
        for css, expected in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css)[1]["a"], expected)

    def test_custom_property_names_and_non_ascii_name_characters_are_preserved(self):
        self.assertEqual(
            parse_css("a { --Tone: One; --tone: Two; Cİlor: red; COLOR: blue; }"),
            (
                {},
                {"a": {"--Tone": "One", "--tone": "Two", "cİlor": "red", "color": "blue"}},
                ["a"],
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
            for trailing in ("", separator):
                with self.subTest(separator=repr(separator), trailing=repr(trailing)):
                    self._important_keyword_with_trailing(separator, trailing)

    def _important_keyword_with_trailing(self, separator, trailing):
        """The upper-case keyword stays recognized whatever follows it."""
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

        cases = itertools.product(
            ("important", "IMPORTANT", "ImPoRtAnT"), ("", " "), (False, True)
        )
        for keyword, separator, blocks in cases:
            with self.subTest(keyword=keyword, separator=separator, blocks=blocks):
                self._important_keyword_form(keyword, separator, blocks)

    def _important_keyword_form(self, keyword, separator, blocks):
        """One keyword spelling, separator and placement: `first` wins."""
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


if __name__ == "__main__":
    unittest.main()
