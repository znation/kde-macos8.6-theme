"""Direct tests for tests/svg_assertions.py's tree-query helpers.

The helpers that read a parsed SVG's element tree -- ``local_name``,
``attribute_values``, ``groups_with_id``, ``elements_by_id`` and
``children_named`` -- are the base every geometry and assertion helper builds
on, so each is pinned directly here.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from svg_assertions import (
    attribute_values,
    children_named,
    elements_by_id,
    groups_with_id,
    local_name,
)
from svg_fixtures import SvgBodyCase, _svg_tree


class TestGroupsWithId(SvgBodyCase, unittest.TestCase):
    def test_yields_only_id_bearing_groups(self):
        # The documented filter: an id-bearing <rect>, <path> or <circle> must
        # not be yielded -- render_slices and tile_origins composite whole
        # groups and would misread a bare shape as one. An id-less <g> is not
        # a slice either.
        tree = self._tree(
            '<g id="top"><rect/></g>'
            '<g><rect id="unused"/></g>'
            '<rect id="center"/>'
            '<path id="edge"/>'
            '<circle id="dot"/>'
        )
        self.assertEqual([g.get("id") for g in groups_with_id(tree)], ["top"])

    def test_yields_every_group_in_document_order(self):
        tree = self._tree(
            '<g id="a"/>'
            '<g id="b"><g id="b-inner"/></g>'
            '<g id="c"/>'
        )
        self.assertEqual(
            [g.get("id") for g in groups_with_id(tree)],
            ["a", "b", "b-inner", "c"],
        )

    def test_yields_the_group_element_itself(self):
        # Callers read the group's id and its child rects, so the yielded
        # object must be the <g>, not a copy or a wrapper.
        tree = self._tree('<g id="top"><rect fill="#000000"/></g>')
        group = next(iter(groups_with_id(tree)))
        self.assertEqual(group.get("id"), "top")
        self.assertEqual(group[0].get("fill"), "#000000")

    def test_yields_nothing_when_no_group_has_an_id(self):
        tree = self._tree('<rect id="center"/><g><rect id="x"/></g>')
        self.assertEqual(list(groups_with_id(tree)), [])


class TestAttributeValues(SvgBodyCase, unittest.TestCase):
    def test_collects_values_from_every_descendant(self):
        # The ids sit at different depths -- a root child, a nested group and
        # a rect under a nested group -- so a helper that scanned only the
        # root's children would miss the deeper ones.
        tree = self._tree(
            '<rect id="top"/>'
            '<g id="group"><rect id="nested"/>'
            '<g><path id="deep"/></g></g>'
        )
        self.assertEqual(
            attribute_values(tree, "id"),
            {"top", "group", "nested", "deep"},
        )

    def test_omits_elements_that_lack_the_attribute(self):
        # An element without `fill` contributes nothing: the set must not hold
        # None, which would make every widget's fill assertion fail.
        tree = self._tree(
            '<rect fill="#000000"/><rect/><g><path fill="#FFFFFF"/></g>'
        )
        self.assertEqual(
            attribute_values(tree, "fill"), {"#000000", "#FFFFFF"}
        )

    def test_deduplicates_repeated_values(self):
        tree = self._tree(
            '<rect fill="#000000"/><rect fill="#000000"/>'
        )
        self.assertEqual(attribute_values(tree, "fill"), {"#000000"})

    def test_returns_an_empty_set_when_no_element_has_the_attribute(self):
        tree = self._tree('<rect id="center"/><g id="top"/>')
        self.assertEqual(attribute_values(tree, "stroke"), set())


class TestChildrenNamed(unittest.TestCase):
    def _first_child(self, body):
        return _svg_tree(body).getroot()[0]

    def test_returns_only_the_direct_children_with_the_tag(self):
        # A rect nested inside a child <g> is a grandchild, not a child: the
        # helper reads a group's own shapes and must not descend into nested
        # groups, or a widget would read another slice's rect.
        group = self._first_child(
            '<g id="top">'
            '<rect id="direct-1"/>'
            '<path id="direct-2"/>'
            '<g id="inner"><rect id="grandchild"/></g>'
            "</g>"
        )
        self.assertEqual(
            [r.get("id") for r in children_named(group, "rect")],
            ["direct-1"],
        )

    def test_matches_the_local_name_of_a_namespaced_element(self):
        # ElementTree reports the tag as `{namespace}rect`; the helper must
        # match on the local name or every widget test would see no shapes.
        group = self._first_child('<g id="top"><rect id="r"/></g>')
        self.assertEqual(
            [c.get("id") for c in children_named(group, "rect")], ["r"]
        )

    def test_returns_empty_when_only_descendants_match(self):
        group = self._first_child(
            '<g id="top"><g id="inner"><rect id="grandchild"/></g></g>'
        )
        self.assertEqual(children_named(group, "rect"), [])


class TestElementsById(SvgBodyCase, unittest.TestCase):
    def test_keeps_elements_that_are_not_groups(self):
        # Unlike groups_with_id, this map must keep a <circle> or <path>:
        # radiobutton reads its selection dot and checkmarks their glyphs by
        # id, and both are non-<g> elements.
        tree = self._tree(
            '<g id="top"><rect id="r"/></g>'
            '<circle id="dot"/><path id="glyph"/>'
        )
        self.assertEqual(
            sorted(elements_by_id(tree)), ["dot", "glyph", "r", "top"]
        )

    def test_maps_each_id_to_its_element(self):
        # Callers read the element's own attributes, so the value must be the
        # parsed element, not a copy or its id string.
        tree = self._tree('<circle id="dot" r="3"/>')
        self.assertEqual(elements_by_id(tree)["dot"].get("r"), "3")

    def test_later_element_wins_when_an_id_repeats(self):
        # The docstring promises later-in-document order wins; pin it so a
        # future rewrite cannot silently flip which duplicate a widget reads.
        tree = self._tree(
            '<rect id="dup" fill="#000000"/>'
            '<rect id="dup" fill="#FFFFFF"/>'
        )
        self.assertEqual(elements_by_id(tree)["dup"].get("fill"), "#FFFFFF")

    def test_omits_elements_without_an_id(self):
        # An id-less element must contribute no key -- not even None -- or
        # callers looking up a real id could collide with it.
        tree = self._tree('<rect/><g><path id="glyph"/></g>')
        self.assertEqual(sorted(elements_by_id(tree)), ["glyph"])

    def test_returns_an_empty_map_when_no_element_has_an_id(self):
        tree = self._tree('<rect/><g><path/></g>')
        self.assertEqual(elements_by_id(tree), {})


class TestLocalName(unittest.TestCase):
    def test_strips_the_svg_namespace_prefix(self):
        # Every shipped SVG declares the default SVG namespace, so ElementTree
        # reports each tag as `{namespace}local`; the helper must return the
        # local part, which is what every widget test matches on.
        root = ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg"><g id="g"/></svg>'
        )
        self.assertEqual(local_name(root), "svg")
        self.assertEqual(local_name(root[0]), "g")

    def test_returns_an_unprefixed_tag_unchanged(self):
        # A tree parsed without an xmlns has no `{namespace}` prefix at all.
        # The widget tests never build one, so a helper that sliced a fixed
        # prefix (or assumed a `}` is always present) would pass them while
        # corrupting every unprefixed tag; pin the bare tag here.
        root = ET.fromstring("<svg><rect id=\"r\"/></svg>")
        self.assertEqual(local_name(root), "svg")
        self.assertEqual(local_name(root[0]), "rect")

    def test_strips_a_namespace_that_is_not_svg(self):
        # The prefix is the element's own namespace, not a hardcoded SVG one;
        # a foreign-namespaced element must still reduce to its local name.
        element = ET.Element("{http://example.test/ns}widget")
        self.assertEqual(local_name(element), "widget")


if __name__ == "__main__":
    unittest.main()
