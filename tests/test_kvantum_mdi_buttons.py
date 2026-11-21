"""Validate the org.macos8.desktop Kvantum SVG's title-band window buttons.

The `mdi-*` ids of `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
which the `[TitleBar]` section resolves its close, minimize, maximize and
restore buttons onto, pinned against the Aurorae decoration's box art. The
SVG's other ids, palette and safety guards stay in `test_kvantum_svg`.
"""

from __future__ import annotations

import os
import unittest

from support.aurorae_fixtures import AURORAE_DIR, inactive_fill
from support.kvantum_fixtures import SVG
from support.platinum_palette import BOX_INNER_OUTLINE
from support.svg_case import parse_svg
from svg_assertions import (
    attribute_values,
    elements_by_id,
    groups_with_id,
    local_name,
    drawing_elements as _drawing_elements,
    rect_element as _rect,
)

# The QMdiSubWindow title band's window buttons are one indicator element
# the [TitleBar] section resolves onto: one 12x12 `mdi` box per role and
# state, the Aurorae decoration's own reference-grounded box art.
MDI_STATES = ("normal", "disabled")
MDI_ROLES = ("close", "minimize", "maximize", "restore")
# The Aurorae widget each role's art is defined as: the zoom box is the
# same in both zoom roles (Mac OS does not change the zoom box when a
# window is zoomed), and each zoom source draws its box five pixels right
# of the group-local origin.
MDI_SOURCES = {
    "close": "close.svg",
    "minimize": "shade.svg",
    "maximize": "maximize.svg",
    "restore": "maximize.svg",
}
SOURCES_ZOOM = ("maximize", "restore")

# The zoom glyph: the inner square's left side (the #222222 rects at x=7,
# y=2..6) and bottom edge (the #222222 run spanning x=1..7 at y=7). The
# collapse glyph: the two bars' #222222 runs spanning the full box width at
# y=5 and y=7 (the run merges the bars with the box outline at its
# endpoints, which is why the span reaches x=1..11 rather than the bars'
# own x=2..10). The disabled flattening repaints the gradient face only,
# so these rects must survive it in every state.
MDI_ZOOM_GLYPH = (
    _rect("7", "2", "1", "1", BOX_INNER_OUTLINE),
    _rect("7", "3", "1", "1", BOX_INNER_OUTLINE),
    _rect("7", "4", "1", "1", BOX_INNER_OUTLINE),
    _rect("7", "5", "1", "1", BOX_INNER_OUTLINE),
    _rect("7", "6", "1", "1", BOX_INNER_OUTLINE),
    _rect("1", "7", "7", "1", BOX_INNER_OUTLINE),
)
MDI_MINIMIZE_GLYPH = (
    _rect("1", "5", "11", "1", BOX_INNER_OUTLINE),
    _rect("1", "7", "11", "1", BOX_INNER_OUTLINE),
)


class TestMdiButtons(unittest.TestCase):
    """Pin the QMdiSubWindow title band's four window buttons.

    The [TitleBar] section resolves the buttons onto the `mdi` indicator
    element; the art is defined as the Aurorae decoration's own
    reference-grounded box art (tests/test_aurorae_buttons.py pins the
    boxes against the reference screenshots), so each state's child rects
    must equal the source widget's active-center group -- not merely exist
    with palette-member fills. The flattening cannot lose a glyph: the
    #888888/#222222 rects are the same tuples in both states.
    """

    def setUp(self):
        self.tree = parse_svg(SVG)

    def _expectation(self, role, disabled=False):
        """Return the source Aurorae box's rect-dict tuple for one role.

        The highlight column and row drop (the shift lands the zoom box's
        own on x=12 along with its spacing runs), and the disabled state
        flattens every non-outline fill to #CCCCCC, the way the reference
        less Aurorae inactive groups are drawn.
        """
        source = parse_svg(os.path.join(AURORAE_DIR, MDI_SOURCES[role]))
        expected = []
        for element in elements_by_id(source)["active-center"]:
            if local_name(element) != "rect":
                continue
            attributes = dict(element.attrib)
            x, y = int(attributes["x"]), int(attributes["y"])
            if role in SOURCES_ZOOM:
                # The zoom box sits five pixels into its source canvas:
                # the five gap columns and the spacing run stay behind.
                if x < 5:
                    continue
                x -= 5
            if x >= 12 or y >= 12:
                # The source's 13th-pixel highlight column/row.
                continue
            fill = attributes["fill"]
            if disabled:
                # The disabled state flattens every non-outline fill the
                # way the reference-less Aurorae inactive groups are drawn
                # (the shared `inactive_fill` rule).
                fill = inactive_fill(fill)
            expected.append(
                _rect(str(x), str(y), attributes["width"], attributes["height"], fill)
            )
        return tuple(expected)

    def test_mdi_buttons_ship_normal_and_disabled(self):
        # Exactly the eight roles-and-states ids: a later state sneaking in
        # (say `-focused`, which the engine resolves down to `-normal`) or
        # a fallback-relevant state going missing fails here.
        ids = {i for i in attribute_values(self.tree, "id") if i.startswith("mdi-")}
        self.assertEqual(
            ids,
            {
                f"mdi-{role}-{state}"
                for role in MDI_ROLES
                for state in MDI_STATES
            },
        )
        # The eight groups follow `titlebar-focused`, role-major, and the
        # four `combofield` families appended after them take the tail: the
        # id-set comparison above cannot see placement, position or
        # duplication.
        order = [group.get("id") for group in groups_with_id(self.tree)]
        self.assertEqual(
            order[order.index("titlebar-focused") + 1 : -36],
            [
                f"mdi-{role}-{state}"
                for role in MDI_ROLES
                for state in MDI_STATES
            ],
        )

    def test_mdi_buttons_are_the_aurorae_box_art(self):
        by_id = elements_by_id(self.tree)
        for role in MDI_ROLES:
            for state in MDI_STATES:
                with self.subTest(role=role, state=state):
                    self.assertEqual(
                        _drawing_elements(by_id[f"mdi-{role}-{state}"]),
                        self._expectation(role, disabled=(state == "disabled")),
                    )

    def test_mdi_glyphs_survive_the_flattening(self):
        by_id = elements_by_id(self.tree)
        for role in MDI_ROLES:
            if role in SOURCES_ZOOM:
                glyph = MDI_ZOOM_GLYPH
            elif role == "minimize":
                glyph = MDI_MINIMIZE_GLYPH
            else:
                # The close box has no glyph; only the exact-art test above
                # pins its art.
                continue
            self._assert_role_glyph(by_id, role, glyph)

    def _assert_role_glyph(self, by_id, role, glyph):
        """Pin *glyph*'s pixels inside every MDI state of *role*."""
        for state in MDI_STATES:
            shipped = _drawing_elements(by_id[f"mdi-{role}-{state}"])
            with self.subTest(role=role, state=state):
                for pixel in glyph:
                    self.assertIn(pixel, shipped)


if __name__ == "__main__":
    unittest.main()
