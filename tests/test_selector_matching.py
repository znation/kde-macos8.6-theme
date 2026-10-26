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

from support.selector_matching import matches


def element(tag, classes=(), parent=None, element_id="", attrs=None, hover=False):
    """Build one fixture element with the keys the matcher reads."""
    return {
        "tag": tag,
        "id": element_id,
        "classes": classes,
        "attrs": {} if attrs is None else attrs,
        "hover": hover,
        "parent": parent,
    }


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


if __name__ == "__main__":
    unittest.main()
