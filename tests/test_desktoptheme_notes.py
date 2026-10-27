"""Tests for the desktop theme's notes.svg sticky-note papers."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import NOTES_SVG
from support.svg_case import SvgCase
from svg_assertions import (
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
)

# The Notes plasmoid's config offers these ten colours and requests element
# id `<color>-notes` for each (contents/ui/configAppearance.qml's
# view.model, read 2026-10-27 from the installed plasmoid); the id list and
# canvas order below match it exactly.
NOTE_COLOURS = (
    "white",
    "black",
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "pink",
    "translucent",
    "translucent-light",
)

# The pinned (fill, fill-opacity) per paper: the solid papers carry no
# fill-opacity (None), the two translucent ones the theme's own chosen
# opacities. Every paper's outline is the same 1px black the other flat
# glyphs pin, asserted separately.
NOTES_PAPERS = {
    "white": ("#FFFFFF", None),
    "black": ("#000000", None),
    "red": ("#FF6666", None),
    "orange": ("#FFCC99", None),
    "yellow": ("#FFFFCC", None),
    "green": ("#99FF99", None),
    "blue": ("#99CCFF", None),
    "pink": ("#FF99CC", None),
    "translucent": ("#FFFFFF", "0.5"),
    "translucent-light": ("#FFFFFF", "0.35"),
}


class TestNotes(SvgCase, unittest.TestCase):
    SVG_PATH = NOTES_SVG

    def test_notes_declares_exactly_the_kde_required_ids(self):
        # The plasmoid requests `<color>-notes` for each colour its config
        # offers; an id it does not request is dead art, and a missing one
        # falls back to Breeze. Pin the id set and the canvas order exactly.
        expected = tuple(f"{colour}-notes" for colour in NOTE_COLOURS)
        assert_ids_present(self, self.tree, expected)
        ids = [element.get("id") for element in elements_by_id(self.tree).values()]
        self.assertEqual(tuple(ids), expected)
        assert_no_script_elements(self, self.tree)

    def test_each_paper_is_a_flat_fill_with_a_black_outline(self):
        # The papers are platform-required adaptations (no reference
        # screenshot shows a sticky note): the theme's flat, black-outlined
        # recipe. NOTES_PAPERS pins every (fill, fill-opacity) so a fill
        # cannot drift, and the shared outline recipe -- a 31x31 rect at
        # (0.5, 0.5) inside a 1px black stroke -- is asserted per paper.
        tree = self.tree
        by_id = elements_by_id(tree)

        for index, colour in enumerate(NOTE_COLOURS):
            with self.subTest(colour=colour):
                element = by_id[f"{colour}-notes"]
                self.assertEqual(local_name(element), "g")

                fill, fill_opacity = NOTES_PAPERS[colour]
                papers = children_named(element, "rect")
                self.assertEqual(len(papers), 2)
                paper = papers[1]
                self.assertEqual(paper.get("fill"), fill)
                self.assertEqual(paper.get("fill-opacity"), fill_opacity)
                self.assertEqual(paper.get("stroke"), "#000000")
                self.assertEqual(paper.get("stroke-width"), "1")
                # The paper rect is 31x31 at (cell + 0.5, 0.5) in its cell,
                # so the 1px stroke lands on whole pixels inside the 32x32
                # bounds.
                self.assertEqual(paper.get("x"), str(index * 32 + 0.5))
                self.assertEqual(paper.get("y"), "0.5")
                self.assertEqual(paper.get("width"), "31")
                self.assertEqual(paper.get("height"), "31")

    def test_translucent_papers_are_the_only_opacity_carriers(self):
        # No element outside the two translucent papers may carry a
        # fill-opacity, so an opaque paper cannot silently turn translucent
        # (and the contract test's fill set alone would not catch it).
        carrier_ids = {
            element.get("id")
            for element in elements_by_id(self.tree).values()
            for paper in children_named(element, "rect")
            if paper.get("fill-opacity") is not None
        }
        self.assertEqual(
            carrier_ids, {"translucent-notes", "translucent-light-notes"}
        )

    def test_yellow_paper_reuses_the_tooltip_role(self):
        # yellow-notes' fill is the colour scheme's [Colors:Tooltip]
        # #FFFFCC -- the classic Platinum pale-yellow the scheme already
        # ships as a KDE-required semantic role (recorded as not sampled:
        # no retail balloon reference exists), so a future edit re-grounds
        # it deliberately rather than drifting to a new yellow.
        by_id = elements_by_id(self.tree)
        paper = children_named(by_id["yellow-notes"], "rect")[1]
        self.assertEqual(paper.get("fill"), "#FFFFCC")

    def test_each_element_pins_its_full_cell_bounds(self):
        # The plasmoid's SvgItem scales the element by its bounds and reads
        # no nine-slice margins, so each group's invisible full-cell bounds
        # rect pins the 32x32 cell KSvg scales to, at the cell's canvas
        # offset. (assert_bounds_rect expects a one-rect group; these groups
        # hold the bounds rect plus the paper rect, so pin it directly.)
        by_id = elements_by_id(self.tree)
        for index, colour in enumerate(NOTE_COLOURS):
            with self.subTest(colour=colour):
                element = by_id[f"{colour}-notes"]
                bounds = children_named(element, "rect")[0]
                self.assertEqual(
                    [bounds.get(k) for k in ("x", "y", "width", "height")],
                    [str(index * 32), "0", "32", "32"],
                )
                self.assertEqual(bounds.get("fill"), "none")

    def test_papers_are_the_only_filled_shapes(self):
        # The canvases stay flat paper recipes: every fill in the file is
        # one of the pinned paper fills or the invisible bounds rects'
        # `none`, so no gradient or extra shape can creep in.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {"none"} | {fill for fill, _ in NOTES_PAPERS.values()},
        )


if __name__ == "__main__":
    unittest.main()
