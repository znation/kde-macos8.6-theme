"""Tests for the test-side selector matcher in ``tests/support``.

The Firefox sheet's scope tests build small element trees and ask
:func:`support.selector_matching.matches` whether a rule's selector would paint
each element. The sheet's selectors use direct-child combinators (``>``) as
well as descendant combinators, so the matcher must distinguish them: a child
combinator matches only the immediate parent, while a descendant combinator
may climb any number of levels. Treating ``>`` as its own compound made every
selector that used one fail to match a valid chain, which would hide a
too-broad rule from a scope test (or a correct one from a match assertion).
"""

from __future__ import annotations

import unittest

from support.selector_matching import (
    _selector_is_supported,
    element as build_element,
    matches,
)


def element(tag, classes=(), parent=None, element_id="", attrs=None, hover=False):
    """Build one fixture element, adapting this module's positional order."""
    return build_element(
        tag, identifier=element_id, classes=classes, attrs=attrs,
        hover=hover, parent=parent,
    )


class TestSelectorMatching(unittest.TestCase):
    def test_child_combinator_matches_a_direct_child_chain(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        target = element("button", parent=inner)
        self.assertTrue(matches(".outer > .inner > button", target))

    def test_child_combinator_does_not_match_a_grandchild(self):
        outer = element("box", ("outer",))
        target = element("button", parent=outer)
        self.assertFalse(matches(".outer > .inner > button", target))

    def test_child_combinator_does_not_skip_an_intermediate_element(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        target = element("button", parent=inner)
        self.assertFalse(matches(".outer > button", target))

    def test_attribute_only_compound_keeps_its_combinator(self):
        outer = element("box", ("a",))
        disabled = element("box", attrs={"disabled": ""}, parent=outer)
        target = element("button", parent=disabled)
        self.assertTrue(matches(".a [disabled] button", target))
        self.assertTrue(matches(".a > [disabled] > button", target))
        grandchild = element("button", parent=element("span", parent=disabled))
        self.assertFalse(matches(".a > [disabled] > button", grandchild))

    def test_descendant_combinator_climbs_past_intermediate_elements(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        target = element("button", parent=inner)
        self.assertTrue(matches(".outer button", target))

    def test_mixed_combinators_keep_their_own_relation(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        body = element("box", ("body",), parent=inner)
        target = element("button", parent=body)
        self.assertTrue(matches(".outer > .inner .body > button", target))
        self.assertFalse(matches(".outer > .body > button", target))

    def test_whitespace_around_the_child_combinator_is_ignored(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        for selector in (".outer>.inner", ".outer >.inner", ".outer> .inner"):
            with self.subTest(selector=selector):
                self.assertTrue(matches(selector, inner))

    def test_descendant_step_backtracks_to_match_the_preceding_child(self):
        outer = element("box", ("a",))
        first = element("box", ("b",), parent=outer)
        second = element("box", ("b",), parent=first)
        target = element("button", ("c",), parent=second)
        self.assertFalse(matches(".a > .b > .c", target))
        self.assertTrue(matches(".a > .b .c", target))

    def test_sibling_combinators_are_not_treated_as_descendant_steps(self):
        # The fixture model has no sibling order, so a sibling combinator is
        # outside the supported subset. It must not be read as a descendant
        # step: ``.a + .b`` used to match a ``.b`` grandchild of ``.a``.
        outer = element("box", ("a",))
        middle = element("box", ("middle",), parent=outer)
        target = element("box", ("b",), parent=middle)
        for selector in (".a + .b", ".a ~ .b", ".a+.b", ".a~.b"):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, target))

    def test_negation_still_applies_in_a_child_chain(self):
        outer = element("box", ("outer",))
        inner = element("box", ("inner",), parent=outer)
        target = element("button", parent=inner)
        disabled_inner = {**inner, "attrs": {"disabled": ""}}
        self.assertTrue(matches(".outer > .inner:not([disabled]) > button", target))
        self.assertFalse(
            matches(
                ".outer > .inner:not([disabled]) > button",
                {**target, "parent": disabled_inner},
            )
        )
    def test_supported_hover_negation_still_matches_and_excludes(self):
        searchbar = element("searchbar", element_id="searchbar")
        self.assertTrue(matches("#searchbar:not(:hover)", searchbar))
        self.assertFalse(
            matches("#searchbar:not(:hover)", {**searchbar, "hover": True})
        )

    def test_attribute_value_containing_a_colon_is_matched_literally(self):
        # A colon and the attribute selector's brackets are part of the value,
        # not a pseudo-class the matcher has to reject as unsupported.
        target = element("box", attrs={"title": "a:b"})
        self.assertTrue(matches('[title="a:b"]', target))
        self.assertFalse(matches('[title="a:c"]', target))

    def test_attribute_value_containing_hover_does_not_require_the_hover_flag(self):
        # ``:hover`` inside an attribute value is text, not the pseudo-class;
        # only a real trailing ``:hover`` makes the selector need the flag.
        target = element("box", attrs={"title": ":hover"})
        self.assertTrue(matches('[title=":hover"]', target))
        self.assertTrue(
            matches('[title=":hover"]:hover', {**target, "hover": True})
        )
        self.assertFalse(matches('[title=":hover"]:hover', target))

    def test_unsupported_attribute_syntax_matches_nothing(self):
        # An attribute selector the matcher cannot parse must not become
        # supported just because a masked value hid its unsupported syntax.
        target = element("box", attrs={"title": "a:b"})
        for selector in ('[title^="a:b"]', '[title:has(.x)]'):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, target))
        self.assertFalse(matches(':not([title^="a:b"])', target))

    def test_malformed_attribute_selectors_match_nothing(self):
        # An unmatched bracket or quote is not an attribute test the matcher
        # can read; leaving it out must not turn the compound into a universal
        # match.
        target = element("box", attrs={"title": "ab"})
        for selector in (
            "[title",
            "[title]]",
            '[title="ab]',
            '[title="ab"',
            '[title="ab"]"',
            "[title][",
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, target))

    def test_attribute_value_containing_a_class_is_matched_literally(self):
        # The dot is part of the quoted value, not a class the element needs.
        target = element("box", attrs={"title": "a.b"})
        self.assertTrue(matches('[title="a.b"]', target))
        other = {**target, "attrs": {"title": "a.c"}}
        self.assertFalse(matches('[title="a.b"]', other))

    def test_attribute_value_containing_a_negation_is_matched_literally(self):
        # ``:not(...)`` inside the quoted value must not be evaluated as a
        # negation of the element the selector is tested against.
        target = element("box", classes=("a",), attrs={"title": ":not(.a)"})
        self.assertTrue(matches('[title=":not(.a)"]', target))
        self.assertFalse(matches('[title=":not(.b)"]', target))

    def test_negated_attribute_value_with_a_parenthesis_is_literal(self):
        # The quoted ``)`` must not end the ``:not(...)`` argument early; the
        # negation applies to the whole attribute test, not a truncated one.
        self.assertTrue(
            matches(
                ':not([title=":not(.a)"])',
                element("box", attrs={"title": ":not(.b)"}),
            )
        )
        self.assertFalse(
            matches(
                ':not([title=":not(.a)"])',
                element("box", attrs={"title": ":not(.a)"}),
            )
        )

    def test_pseudo_class_name_starting_with_hover_is_unsupported(self):
        # ``:hover`` is supported only as the complete pseudo-class name; a
        # longer name must not be shortened to ``:hover`` and accepted.
        searchbar = element(
            "searchbar",
            element_id="searchbar",
            attrs={"title": "x"},
            hover=True,
        )
        for selector in (
            "[title]:hover-x",
            "[title]:hoverx",
            "#searchbar:not(:hover-x)",
            "#searchbar:not(:hoverx)",
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, searchbar))

    def test_unsupported_negation_argument_makes_the_whole_selector_match_nothing(self):
        # Recursing into ``:not(...)`` rejects an argument the matcher cannot
        # evaluate, such as one with a sibling combinator or an empty one.
        target = element("box", ("a", "b"))
        for selector in (".a:not(.b + .c)", ".a:not()"):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, target))

    def test_a_comma_inside_negation_is_a_selector_list_not_a_descendant_chain(self):
        # ``:not(.a, .b)`` negates either class; reading the comma as a
        # descendant step (``.a .b``) made the negation true for a class-``a``
        # element and for one under a class-``a`` parent. A selector list is
        # outside the supported subset, so it must match nothing rather than
        # be read as a descendant chain.
        target = element("toolbarbutton", ("a",))
        parent = element("box", ("a",))
        under_parent = element("toolbarbutton", ("a",), parent=parent)
        for selector in (":not(.a, .b)", ":not(.a,.b)", ".a:not(.b, .c)"):
            with self.subTest(selector=selector):
                self.assertFalse(_selector_is_supported(selector))
                self.assertFalse(matches(selector, target))
                self.assertFalse(matches(selector, under_parent))

    def test_a_top_level_comma_is_a_selector_list_not_a_descendant_chain(self):
        # The matcher does not evaluate selector lists; ``.a, .b`` used to be
        # read as ``.a .b``.
        target = element("toolbarbutton", ("b",))
        parent = element("box", ("a",))
        under_parent = element("toolbarbutton", ("b",), parent=parent)
        self.assertFalse(matches(".a, .b", under_parent))
        self.assertFalse(matches(".a, .b", target))

    def test_a_comma_inside_an_attribute_value_is_literal(self):
        # A quoted value's comma is text, not a selector-list separator, so
        # the rejection above must not drop a supported attribute test.
        target = element("box", attrs={"title": "a,b"})
        other = element("box", attrs={"title": "a"})
        self.assertTrue(matches('[title="a,b"]', target))
        self.assertFalse(matches('[title="a,b"]', other))
        self.assertTrue(matches(':not([title="a,b"])', other))
        self.assertFalse(matches(':not([title="a,b"])', target))

    def test_unsupported_pseudo_class_inside_negation_matches_nothing(self):
        # A pseudo-class outside the supported subset cannot be evaluated, so
        # it must make its whole selector match nothing. Negating it must not
        # invert that gap into a selector that matches every element: the
        # Firefox sheet's ``#searchbar:not(:focus-within)`` used to match a
        # focused searchbar because ``:focus-within`` was read as false.
        searchbar = element("searchbar", classes=("a",), element_id="searchbar")
        for selector in (
            "#searchbar:not(:focus-within)",
            ".a:not(:is(.b))",
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, searchbar))
        # Nested ``:not(...)`` is outside the flat-negation subset too, so a
        # matching inner selector must not silently make the negation true.
        self.assertFalse(
            matches(".a:not(:not(.b))", {**searchbar, "classes": ("a", "b")})
        )


if __name__ == "__main__":
    unittest.main()
