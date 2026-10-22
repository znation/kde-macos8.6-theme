"""Direct tests for ``svg_assertions.safety``'s document-safety guards.

A shipped widget SVG must stay self-contained and inert: no ``<script>``, no
``<style>`` element, no reference to another file, and no duplicate ``id``.
Every desktop-theme widget test runs these guards over its own artwork, so a
guard that checked only the root's children, or mis-read a namespace-qualified
attribute, would weaken them all at once. These tests prove each guard accepts
a clean tree and rejects the forbidden form at the root and nested below it.
"""

from __future__ import annotations

import time
import unittest

from support.rejection_assertions import assert_rejection_names
from support.svg_fixtures import _svg_tree
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
)
from svg_assertions.safety import _url_targets


class TestNoScriptElements(unittest.TestCase):
    def test_passes_a_tree_without_a_script(self):
        tree = _svg_tree('<rect id="center"/>')
        assert_no_script_elements(self, tree)

    def test_catches_a_script_after_another_element(self):
        tree = _svg_tree(
            '<rect id="center"/><script>alert(1)</script>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)

    def test_catches_a_script_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<g id="top"><g><script>alert(1)</script></g></g>'
        )
        with self.assertRaises(AssertionError):
            assert_no_script_elements(self, tree)


class TestNoStyleElements(unittest.TestCase):
    def test_passes_a_tree_without_a_style_element(self):
        # The shipped SVGs state their real colours in presentation `fill`
        # attributes and use an inline `style` only for hint sentinels and
        # transparent placeholders; only a `<style>` element is rejected.
        tree = _svg_tree('<rect id="center" style="fill:#ff6600"/>')
        assert_no_style_elements(self, tree)

    def test_catches_a_style_element_naming_it(self):
        tree = _svg_tree(
            '<rect id="center"/><style>rect{fill:#ff6600}</style>'
        )
        assert_rejection_names(
            self, assert_no_style_elements, tree, needles=("style",)
        )

    def test_catches_a_style_element_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<g id="top"><style>rect{fill:#ff6600}</style></g>'
        )
        with self.assertRaises(AssertionError):
            assert_no_style_elements(self, tree)


class TestNoExternalReferences(unittest.TestCase):
    def test_passes_a_tree_with_no_references(self):
        tree = _svg_tree('<rect id="center" style="fill:#ff6600"/>')
        assert_no_external_references(self, tree)

    def test_passes_a_same_document_fragment_reference(self):
        # An internal `#id` reference stays inside the file, so it is allowed.
        tree = _svg_tree('<use href="#center"/>')
        assert_no_external_references(self, tree)

    def test_catches_an_image_element(self):
        tree = _svg_tree('<image href="panel.png"/>')
        assert_rejection_names(
            self, assert_no_external_references, tree, needles=("image",)
        )

    def test_catches_a_file_href_naming_the_value(self):
        tree = _svg_tree('<use href="other.svg#center"/>')
        assert_rejection_names(
            self,
            assert_no_external_references,
            tree,
            needles=("other.svg#center",),
        )

    def test_catches_an_xlink_href(self):
        # A declared xlink namespace makes ElementTree report the attribute as
        # `{http://www.w3.org/1999/xlink}href`; the guard must strip it and
        # still reject the file reference.
        tree = _svg_tree(
            '<use xlink:href="other.svg#center"/>',
            **{"xmlns:xlink": "http://www.w3.org/1999/xlink"},
        )
        assert_rejection_names(
            self,
            assert_no_external_references,
            tree,
            needles=("other.svg#center",),
        )

    def test_catches_a_data_uri_href(self):
        # A `data:` URI is self-contained but still not an in-file #id, so the
        # guard rejects it like any other non-fragment reference.
        tree = _svg_tree('<use href="data:image/png;base64,AAAA"/>')
        assert_rejection_names(
            self, assert_no_external_references, tree, needles=("data:",)
        )

    def test_passes_an_in_file_url_reference(self):
        # `fill="url(#id)"` names a same-document paint, so it is allowed.
        tree = _svg_tree('<rect id="center" fill="url(#gradient)"/>')
        assert_no_external_references(self, tree)

    def test_passes_a_quoted_padded_url_reference(self):
        tree = _svg_tree(
            "<rect id=\"center\" fill=\"url( '#gradient' )\"/>"
        )
        assert_no_external_references(self, tree)

    def test_catches_an_external_url_in_fill(self):
        # A `url(...)` target that is not a `#id` names another file, which
        # the copied install does not ship.
        tree = _svg_tree(
            '<rect id="center" fill="url(other.svg#gradient)"/>'
        )
        assert_rejection_names(
            self,
            assert_no_external_references,
            tree,
            needles=("other.svg#gradient",),
        )

    def test_catches_an_external_url_in_an_inline_style(self):
        tree = _svg_tree(
            '<rect id="center" style="filter:url(other.svg#blur)"/>'
        )
        assert_rejection_names(
            self,
            assert_no_external_references,
            tree,
            needles=("other.svg#blur",),
        )

    def test_catches_a_data_uri_url(self):
        tree = _svg_tree(
            '<rect id="center" fill="url(data:image/svg+xml,x)"/>'
        )
        assert_rejection_names(
            self, assert_no_external_references, tree, needles=("data:",)
        )

    def test_url_targets_finishes_promptly_on_a_hostile_value(self):
        # A contributor-supplied attribute value with many ``url(`` starts
        # and no closing ``)`` made the old backtracking regex rescan to the
        # end of the value at every start: quadratic time, so this ~24 KB
        # value took seconds and a real artwork could stall `make check` for
        # minutes. The scanner must find no target and finish well inside a
        # generous bound.
        value = "url(" * 6000
        started = time.monotonic()
        targets = list(_url_targets(value))
        elapsed = time.monotonic() - started
        self.assertEqual(targets, [])
        self.assertLess(
            elapsed, 1.0, f"scanning {len(value)} bytes took {elapsed:.3f}s"
        )


class TestUrlReferenceScanning(unittest.TestCase):
    """``url(...)`` is a CSS token, so its keyword and body have fixed shapes.

    The scanner reads every ``url(...)`` in an attribute value and hands the
    target to the guard. CSS matches the keyword case-insensitively, so
    ``URL(other.svg)`` names the same external reference as ``url(other.svg)``;
    losing that flag would let it pass unnoticed. The body may be unquoted and
    padded, or quoted with the ``)`` right after the closing quote; a quoted
    body that is not shaped that way falls back to the unquoted read.
    """

    def test_uppercase_url_keyword_is_found(self):
        self.assertEqual(
            list(_url_targets("URL(other.svg#x)")), ["other.svg#x"]
        )

    def test_uppercase_url_reference_is_rejected_end_to_end(self):
        # The guard must reject `URL(...)` exactly as it rejects `url(...)`;
        # the old scanner matched with re.IGNORECASE for this reason.
        tree = _svg_tree(
            '<rect id="center" fill="URL(other.svg#gradient)"/>'
        )
        assert_rejection_names(
            self,
            assert_no_external_references,
            tree,
            needles=("other.svg#gradient",),
        )

    def test_padded_unquoted_target_is_stripped(self):
        self.assertEqual(
            list(_url_targets("url(  #gradient  )")), ["#gradient"]
        )

    def test_a_quoted_target_not_followed_by_a_paren_falls_back(self):
        # ``url("a" b)`` is malformed: the quoted form needs its ``)`` right
        # after the closing quote, so the scanner falls back to the unquoted
        # read and yields the raw remainder. This pins that fall-through.
        self.assertEqual(list(_url_targets('url("a" b)')), ['"a" b'])

    def test_an_unclosed_quote_with_no_closing_paren_yields_nothing(self):
        self.assertEqual(list(_url_targets('url("a')), [])

    def test_several_references_in_one_value_are_all_yielded(self):
        self.assertEqual(
            list(_url_targets("url(#a) url( '#b' ) URL(#c)")),
            ["#a", "#b", "#c"],
        )


class TestUniqueIds(unittest.TestCase):
    def test_passes_a_tree_with_unique_ids(self):
        tree = _svg_tree(
            '<rect id="center"/><g id="top"><rect id="top-body"/></g>'
        )
        assert_unique_ids(self, tree)

    def test_passes_a_tree_whose_elements_have_no_ids(self):
        tree = _svg_tree("<rect/>")
        assert_unique_ids(self, tree)

    def test_catches_a_duplicate_id_naming_it(self):
        tree = _svg_tree('<rect id="center"/><rect id="center"/>')
        assert_rejection_names(
            self, assert_unique_ids, tree, needles=("center",)
        )

    def test_catches_a_duplicate_id_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<rect id="center"/><g><rect id="center"/></g>'
        )
        assert_rejection_names(
            self, assert_unique_ids, tree, needles=("center",)
        )


if __name__ == "__main__":
    unittest.main()
