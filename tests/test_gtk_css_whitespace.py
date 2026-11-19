"""Pin GTK CSS whitespace normalization and escape terminators."""

import itertools
import unittest

from support.gtk_css import parse_css


class TestWhitespaceNormalization(unittest.TestCase):
    def test_whitespace_inside_a_quoted_selector_value_is_preserved(self):
        self.assertEqual(
            parse_css('[title="a  b"] { color: #111111; }')[1:],
            ({'[title="a  b"]': {"color": "#111111"}}, ['[title="a  b"]']),
        )
        self.assertEqual(
            parse_css('[title="a  b"] { color: #111111; }'
                      '[title="a b"] { margin: 1px; }')[1],
            {'[title="a  b"]': {"color": "#111111"},
             '[title="a b"]': {"margin": "1px"}},
        )

    def test_whitespace_inside_a_quoted_declaration_value_is_preserved(self):
        self.assertEqual(parse_css('a { content: "a  b"; }')[1],
                         {"a": {"content": '"a  b"'}})
        self.assertEqual(parse_css('a { background-image: url("a  b.png"); }')[1],
                         {"a": {"background-image": 'url("a  b.png")'}})

    def test_only_css_ascii_whitespace_collapses_between_tokens(self):
        for character in ("\u00a0", "\u2003", "\u000b"):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                self.assertEqual(parse_css(f".a{character}b {{ color: red; }}"
                                           ".a b { color: blue; }"),
                    ({}, {f".a{character}b": {"color": "red"},
                         ".a b": {"color": "blue"}}, [f".a{character}b", ".a b"]))
                self.assertEqual(parse_css(f"a {{ content: token{character}name; }}")[1],
                                 {"a": {"content": f"token{character}name"}})
        self.assertEqual(parse_css(".a \t\n\r\f b { color: red; }")[1:],
                         ({".a b": {"color": "red"}}, [".a b"]))

    def test_non_css_whitespace_at_declaration_boundaries_is_preserved(self):
        for character in ("\u00a0", "\u2003", "\u000b"):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                for value, expected in ((f"{character}token", f"{character}token"),
                                        (f"token{character}", f"token{character}"),
                                        (f" \t{character}token{character}\r\n",
                                         f"{character}token{character}"),
                                        (character, character)):
                    self.assertEqual(parse_css(f"a {{ content: {value}; }}")[1],
                                     {"a": {"content": expected}})
                with self.assertRaisesRegex(ValueError,
                        r"^source\.css: malformed declaration in selector 'a':"):
                    parse_css("a { \u00a0; }" if character == "\u00a0" else
                              f"a {{ {character}; }}", source="source.css")
        self.assertEqual(parse_css("a { ; \t\n\r\f; content: token \t; }")[1],
                         {"a": {"content": "token"}})

    def test_escaped_trailing_value_whitespace_is_preserved(self):
        for suffix in ("; color: red;", ""):
            declarations = parse_css(f"a {{ --sample: token   {suffix}}}")[1]["a"]
            expected = {"--sample": "token"}
            if suffix:
                expected["color"] = "red"
            self.assertEqual(declarations, expected)
        for whitespace, slash_count, suffix in itertools.product(
                (" ", "\t"), (1, 2, 3), ("; color: red;", "")):
            value = "token" + "\\" * slash_count + whitespace
            declarations = parse_css(f"a {{ --value: {value}   {suffix}}}")[1]["a"]
            expected = "token" + "\\" * slash_count + (
                whitespace if slash_count % 2 else "")
            self.assertEqual(declarations["--value"], expected)
            if suffix:
                self.assertEqual(declarations["color"], "red")
        self.assertEqual(parse_css("a { --value: token\\\\ ; }")[1],
                         {"a": {"--value": "token\\\\"}})
        self.assertEqual(parse_css('a { --value: "token "; }')[1],
                         {"a": {"--value": '"token "'}})

    def test_hex_escape_terminators_survive_selector_and_value_normalization(self):
        css = (r".\31  a { color: red; } .\31 a { margin: 1px; } "
               "a { --hex: \\41   ; --tab: \\42\t  ; --crlf: \\43\r\n  ; }")
        _, rules, selectors = parse_css(css)
        self.assertEqual(selectors, [r".\31  a", r".\31 a", "a"])
        self.assertEqual(rules[r".\31  a"], {"color": "red"})
        self.assertEqual(rules[r".\31 a"], {"margin": "1px"})
        self.assertEqual(rules["a"], {"--hex": r"\41 ", "--tab": "\\42\t",
                                       "--crlf": "\\43\r\n"})

    def test_hex_escape_selector_terminator_is_distinct_from_separator(self):
        _, rules, selectors = parse_css(r".\31  a { color: red; } .\31 a { margin: 1px; }")
        self.assertEqual(selectors, [r".\31  a", r".\31 a"])
        self.assertEqual(rules, {r".\31  a": {"color": "red"},
                                 r".\31 a": {"margin": "1px"}})

    def test_hex_escape_lengths_and_terminators_in_values(self):
        values = ((r"\a ", r"\a "), (r"\AB ", r"\AB "),
                  (r"\123 ", r"\123 "), (r"\1234 ", r"\1234 "),
                  (r"\12345 ", r"\12345 "), (r"\123456 ", r"\123456 "),
                  (r"\1234567", r"\1234567"))
        for source, expected in values:
            with self.subTest(source=source):
                self.assertEqual(parse_css("a { --value: " + source + "  ; }")[1]
                                 ["a"]["--value"], expected)
        self.assertEqual(parse_css("a { --crlf: \\41\r\n  ; }")[1]["a"]["--crlf"],
                         "\\41\r\n")


if __name__ == "__main__":
    unittest.main()
