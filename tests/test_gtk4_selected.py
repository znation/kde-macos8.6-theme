"""GTK 4 selected declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_css import strip_comments
from support.gtk_theme_spec import TEXT_SELECTION
from support.platinum_palette import BLACK, GREY


class TestGtk4Selected(Gtk4SheetRuleCases, unittest.TestCase):
    def test_selected_text_arms(self):
        focus = (
            "label > selection:focus-within",
            "textview > text > selection:focus-within",
            "entry > text > selection:focus-within",
            "spinbutton:not(.vertical) > text > selection:focus-within",
            "spinbutton.vertical > text > text > selection:focus-within",
            "spinbutton.vertical > text > selection:focus-within",
            "editablelabel > stack > text > selection:focus-within",
        )
        disabled = (
            "label:disabled > selection",
            "label:disabled:selected",
            "textview > text:disabled:selected",
            "textview > text:disabled:selected:focus",
        )
        for selector in focus:
            self.assert_rule(selector, TEXT_SELECTION)
        self.assert_disabled_text(disabled)
        self.assertEqual(
            {s for s in self.rules if s in focus or s in disabled},
            set(focus) | set(disabled),
        )

    def test_selected_inline_link_foregrounds(self):
        roots = ("link:selected:not(:disabled)", "link:visited:selected:not(:disabled)")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], {"color": TEXT_SELECTION["color"]}, selector)
            for ordinary in ("link:visited", "link:hover", "link:active"):
                self.assertGreater(css.index(selector), css.index(ordinary), selector)

    def test_selected_ancestor_inline_link_foregrounds(self):
        roots = (":selected link:not(:disabled)", ":selected link:visited:not(:disabled)")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        selected_links = css.index("link:selected:not(:disabled)")
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assert_rule(selector, {"color": TEXT_SELECTION["color"]})
            self.assertEqual(self.rules[selector], {"color": TEXT_SELECTION["color"]})
            for earlier in ("link:visited", "link:hover", "link:active"):
                self.assertGreater(css.index(selector), css.index(earlier), selector)
            self.assertGreater(css.index(selector), selected_links, selector)

    def test_selected_row_button_arms(self):
        # The selected-row button arms restate the existing black: see
        # assert_selected_row_button_arms in support.gtk_rule_cases.
        self.assert_selected_row_button_arms("button:backdrop.flat")

    def test_selected_row_meter_rims(self):
        """A meter in a selected row keeps the existing rims over the selection.

        Stock's selected-row meter arms (libgtk-4 light resource lines
        1085, 1095 and 1133, dark twins at 1073, 1083 and 1121) repaint
        the trough rim with the stock accent-deep ink under the stock
        translucent white selection outline and both thumb states with
        the accent-deep ink, and the `row:selected` prefix out-specifies
        the existing plain meter groups, so inside the existing lavender
        selection a meter's rims repaint stock's ink today. The restated
        groups repeat the existing trough rim #000000 and the existing thumb
        rims — #000000 enabled, flat #999999 disabled — as byte-equal
        stock spellings that sit later, so under lower-sheet riding they
        win the per-property tie at stock's own specificity; under the
        replacement reading these rules are the only holders of the
        spellings. Stock's one thumb comma group is split by existing state
        into two single-spelling rules, since a comma group shares its
        declarations across every member and one group cannot carry the
        disabled thumb's flat grey rim and the enabled thumb's black rim;
        the disabled spelling out-specifies the bare thumb spelling, so
        each state keeps its existing rim. The sweep and order pins kill a
        merged comma group, a renamed spelling and a stray selected-row
        meter rule.
        """
        self.assert_rule_group(
            {
                "row:selected progressbar > trough": {"border-color": BLACK},
                "row:selected scale > trough": {"border-color": BLACK},
                "row:selected scale > trough > slider:disabled": {
                    "border-color": GREY
                },
                "row:selected scale > trough > slider": {
                    "border-color": BLACK
                },
            }
        )
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if selector.startswith("row:selected")
                and ("trough" in selector or "slider" in selector)
            },
            {
                "row:selected progressbar > trough",
                "row:selected scale > trough",
                "row:selected scale > trough > slider:disabled",
                "row:selected scale > trough > slider",
            },
        )
        # The restated rims sit inside the existing disabled-meter
        # neighbourhood on the raw sheet: after the existing disabled
        # trough group and before the existing opaque disabled policy.
        self.assert_rule_after(
            "row:selected progressbar > trough,",
            "scale > trough:disabled",
        )
        self.assert_rule_after(
            "progressbar:disabled",
            "row:selected scale > trough > slider:disabled",
        )



if __name__ == "__main__":
    unittest.main()
