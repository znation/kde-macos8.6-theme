"""The shared GTK stylesheet parser's ``@define-color`` scanner.

These cases pin how ``support.gtk_css`` finds ``@define-color`` definitions:
only CSS whitespace separates the directive's parts, and a definition inside
a quoted value, a function value or a rule block is text. The rule-pairing
cases live in ``tests/test_gtk_css_blocks.py``; grouping and whitespace
cases remain in ``tests/test_gtk_css.py``, and the
declaration-merging cases in ``tests/test_gtk_css_cascade.py``.
"""

from __future__ import annotations

import unittest

from support.gtk_css import _define_color_matches, parse_css


class TestDefineColorScan(unittest.TestCase):
    """Pins how the shared parser finds ``@define-color`` definitions."""

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
        # Each function, quoted and escaped brace is unmatched, so counting
        # any of them would expose a decoy or hide a genuine definition.
        text = (
            'a { content: fn(}); --x: "}"; --y: \\}; '
            "b { --z: @define-color nested #444444; } "
            "--w: @define-color inner #666666; }\n"
            "} @define-color between #555555;\n"
            'x: fn({); --q: "{"; --e: \\{;\n'
            "@define-color shown #777777;"
        )
        self.assertEqual(
            [match.group("name") for match in _define_color_matches(text)],
            ["between", "shown"],
        )


if __name__ == "__main__":
    unittest.main()
