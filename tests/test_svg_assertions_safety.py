"""Direct tests for tests/svg_assertions.py's document-safety guards.

A shipped widget SVG must stay self-contained and inert: no ``<script>``, no
``<style>`` element, no reference to another file, and no duplicate ``id``.
Every desktop-theme widget test runs these guards over its own artwork, so a
guard that checked only the root's children, or mis-read a namespace-qualified
attribute, would weaken them all at once. These tests prove each guard accepts
a clean tree and rejects the forbidden form at the root and nested below it.
"""

from __future__ import annotations

import unittest

from error_assertions import rejection_message
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
)
from svg_fixtures import _svg_tree


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
        self.assertIn(
            "style",
            rejection_message(assert_no_style_elements, tree),
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
        self.assertIn(
            "image",
            rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_file_href_naming_the_value(self):
        tree = _svg_tree('<use href="other.svg#center"/>')
        self.assertIn(
            "other.svg#center",
            rejection_message(assert_no_external_references, tree),
        )

    def test_catches_an_xlink_href(self):
        # A declared xlink namespace makes ElementTree report the attribute as
        # `{http://www.w3.org/1999/xlink}href`; the guard must strip it and
        # still reject the file reference.
        tree = _svg_tree(
            '<use xlink:href="other.svg#center"/>',
            **{"xmlns:xlink": "http://www.w3.org/1999/xlink"},
        )
        self.assertIn(
            "other.svg#center",
            rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_data_uri_href(self):
        # A `data:` URI is self-contained but still not an in-file #id, so the
        # guard rejects it like any other non-fragment reference.
        tree = _svg_tree('<use href="data:image/png;base64,AAAA"/>')
        self.assertIn(
            "data:",
            rejection_message(assert_no_external_references, tree),
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
        self.assertIn(
            "other.svg#gradient",
            rejection_message(assert_no_external_references, tree),
        )

    def test_catches_an_external_url_in_an_inline_style(self):
        tree = _svg_tree(
            '<rect id="center" style="filter:url(other.svg#blur)"/>'
        )
        self.assertIn(
            "other.svg#blur",
            rejection_message(assert_no_external_references, tree),
        )

    def test_catches_a_data_uri_url(self):
        tree = _svg_tree(
            '<rect id="center" fill="url(data:image/svg+xml,x)"/>'
        )
        self.assertIn(
            "data:",
            rejection_message(assert_no_external_references, tree),
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
        self.assertIn(
            "center",
            rejection_message(assert_unique_ids, tree),
        )

    def test_catches_a_duplicate_id_nested_below_the_root(self):
        # The guard walks every descendant, not just the root's children.
        tree = _svg_tree(
            '<rect id="center"/><g><rect id="center"/></g>'
        )
        self.assertIn(
            "center",
            rejection_message(assert_unique_ids, tree),
        )


if __name__ == "__main__":
    unittest.main()
