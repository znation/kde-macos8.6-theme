"""Rule-block pairing cases for the shared GTK stylesheet parser.

Declaration-splitting, grouping and whitespace cases remain in
``tests/test_gtk_css.py``, declaration-merging cases in
``tests/test_gtk_css_cascade.py`` and ``@define-color`` cases in
``tests/test_gtk_css_define_color.py``.
"""

from __future__ import annotations

import unittest

from support.gtk_css import parse_css


class TestRuleBlockPairing(unittest.TestCase):
    """Pin how ``parse_css`` pairs braces into rule blocks."""

    def test_a_nested_block_replaces_the_pending_selector(self):
        # The expression's selector body could not cross a brace, so the inner
        # block's text became its match: only `a` is a rule here, not `x`.
        self.assertEqual(
            parse_css("x{a{color:#111111}}"),
            ({}, {"a": {"color": "#111111"}}, ["a"]),
        )

    def test_a_brace_inside_a_quoted_string_does_not_pair_a_block(self):
        self.assertEqual(
            parse_css('a { content: "}"; color: #111111; } b { color: #222222; }'),
            ({}, {"a": {"content": '"}"', "color": "#111111"},
                 "b": {"color": "#222222"}}, ["a", "b"]),
        )
        self.assertEqual(parse_css('a { content: "{"; color: #111111; }')[1],
                         {"a": {"content": '"{"', "color": "#111111"}})
        self.assertEqual(parse_css('[title="{"] { color: #111111; }')[1],
                         {'[title="{"]': {"color": "#111111"}})

    def test_a_brace_inside_an_unquoted_url_value_is_text(self):
        self.assertEqual(
            parse_css("a { background-image: url(data:image/svg+xml,<g {x}>);"
                      " color: #111111; } b { color: #222222; }"),
            ({}, {"a": {"background-image": "url(data:image/svg+xml,<g {x}>)",
                         "color": "#111111"}, "b": {"color": "#222222"}},
             ["a", "b"]),
        )
        self.assertEqual(parse_css("a { background-image: url(data:image/svg+xml,<g {x}>) }")[1],
                         {"a": {"background-image": "url(data:image/svg+xml,<g {x}>)"}})
        self.assertEqual(parse_css('a[href="}"] { content: url(data:x{y}); margin: 1px; }')[1],
                         {'a[href="}"]': {"content": "url(data:x{y})", "margin": "1px"}})

    def test_braces_inside_square_bracket_values_are_preserved(self):
        cases = (
            ("a { --tokens: [x{y}z]; color: red; } b { color: blue; }", ["a", "b"],
             {"a": {"--tokens": "[x{y}z]", "color": "red"}, "b": {"color": "blue"}}),
            ("a, b { --tokens: [[x{y};z]]; color: red; }", ["a", "b"],
             {"a": {"--tokens": "[[x{y};z]]", "color": "red"}, "b": {"--tokens": "[[x{y};z]]", "color": "red"}}),
            ("a { --tokens: fn([x{y}]); }", ["a"], {"a": {"--tokens": "fn([x{y}])"}}),
            ("a { --tokens: [fn(x{y})]; }", ["a"], {"a": {"--tokens": "[fn(x{y})]"}}),
            ('a { --tokens: ["[x{y}]"]; color: red; }', ["a"],
             {"a": {"--tokens": '["[x{y}]"]', "color": "red"}}),
            (r"a { --tokens: [x\] {y}]; color: red; }", ["a"], {"a": {"--tokens": r"[x\] {y}]", "color": "red"}}),
            (r"a { --tokens: [x\[ {y}]; color: red; }", ["a"], {"a": {"--tokens": r"[x\[ {y}]", "color": "red"}}),
            ("a { --tokens: [x{y}z]}", ["a"], {"a": {"--tokens": "[x{y}z]"}}),
        )
        for css, selectors, rules in cases:
            with self.subTest(css=css):
                self.assertEqual(parse_css(css), ({}, rules, selectors))
        self.assertEqual(parse_css("] a { color: red; } b { color: blue; }")[2], ["] a", "b"])

    def test_a_quoted_url_parenthesis_does_not_end_value_grouping(self):
        self.assertEqual(parse_css('a { background: url(")} ") url(x{y}); } b { color: red; }')[1],
                         {"a": {"background": 'url(")} ") url(x{y})'}, "b": {"color": "red"}})

    def test_a_stray_closing_parenthesis_does_not_hide_a_brace_either(self):
        self.assertEqual(parse_css("a { color: red) } b { color: #222222; }"),
                         ({}, {"a": {"color": "red)"}, "b": {"color": "#222222"}}, ["a", "b"]))

    def test_a_stray_closing_brace_is_skipped(self):
        self.assertEqual(parse_css("a{color:#111111;} } b{color:#222222;}"),
                         ({}, {"a": {"color": "#111111"}, "b": {"color": "#222222"}}, ["a", "b"]))


if __name__ == "__main__":
    unittest.main()
