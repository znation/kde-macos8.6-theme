"""GTK 4 disabled-declaration checks, split from the sheet suite."""

import unittest

from support import gtk_css
from support.gtk_css import strip_comments
from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT
from support.platinum_palette import BLACK, TROUGH, WHITE


class TestGtk4Disabled(Gtk4SheetRuleCases, unittest.TestCase):
    def test_disabled_text(self):
        self.assert_disabled_text(
            ("label:disabled", "text:disabled", "spinbutton.vertical > text:disabled")
        )
    def test_disabled_view_face(self):
        """Pin the restated disabled view field stock-twin."""
        # 2026-11-04: disabled views keep the landed white content field —
        # stock's (0,2,0) disabled view arm beats the landed (0,1,0)
        # `.view, list` group and no landed rule names its compound twins,
        # so stock would wash each member grey without the group.
        # 2026-11-11: the group also co-declares the family's insensitive
        # ink per-property, so each member's whole dict is the DISABLED_TEXT
        # grey ink plus the white field and stock's own disabled-view ink
        # literals never render on these members.
        selectors = (
            ".view:disabled",
            "textview > text:disabled",
            "window.print:not(.ssd-frame) .dialog-action-box:disabled",
            "dialog-host > dialog.view sheet:disabled",
            "window.print:not(.ssd-frame) dialog-host > "
            "dialog.dialog-action-box sheet:disabled",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {**DISABLED_TEXT, "background-color": WHITE})
                self.assert_exact_rule_once(selector, {**DISABLED_TEXT, "background-color": WHITE})
        # The token sweeps key on substrings no landed selector carries:
        # the print action-box spelling alone carries the leading-space
        # " .dialog-action-box:disabled" form (the 2026-11-11 per-family
        # block's print twins name element nodes instead), and both sheet
        # spellings alone carry "sheet:disabled".
        self.assertEqual(
            {s for s in self.rules if " .dialog-action-box:disabled" in s},
            {"window.print:not(.ssd-frame) .dialog-action-box:disabled"},
        )
        self.assertEqual(
            {s for s in self.rules if "sheet:disabled" in s},
            {
                "dialog-host > dialog.view sheet:disabled",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:disabled",
            },
        )
        # The landed frame pair declares no background-color, so the fill
        # anchors to the pinned WHITE constant the landed `.view, list`
        # view-field test uses.
        self.assertEqual(self.rules[".view:disabled"]["background-color"], WHITE)
        # The sheet parser splits the landed comma group into per-selector
        # keys, so the landed field anchor reads under its .view key.
        self.assertEqual(self.rules[".view"]["background-color"], WHITE)
        # Source order: the restated group files after the landed
        # ``.view:disabled:selected`` ink key, then after the landed
        # selection-surface group that ended the sheet tail before it.
        for selector in selectors:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index(".view:disabled:selected"),
                selector,
            )
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index(
                    "window.print:not(.ssd-frame) dialog-host > "
                    "dialog.dialog-action-box sheet:selected"
                ),
                selector,
            )
    def test_disabled_view_family_ink(self):
        """Pin the 2026-11-11 per-family disabled-view ink restatement."""
        # 2026-11-11: the integration library's six disabled-view arms and
        # the toolkit's two each carry a foreign ink; the per-family block
        # restates them with the landed insensitive grey. The landed field
        # group's count-one pin on `.view:disabled` forces the generic arm
        # to be co-declared there, so the per-family block names only the
        # fourteen byte-equal members below, each declaring exactly the
        # grey ink.
        members = (
            "calendar.view:disabled",
            "window.print:not(.ssd-frame) calendar.dialog-action-box:disabled",
            "columnview.view:disabled",
            "treeview.view:disabled",
            "window.print:not(.ssd-frame) columnview.dialog-action-box:disabled",
            "window.print:not(.ssd-frame) treeview.dialog-action-box:disabled",
            "listview.view:disabled",
            "window.print:not(.ssd-frame) listview.dialog-action-box:disabled",
            "list.view:disabled",
            "window.print:not(.ssd-frame) list.dialog-action-box:disabled",
            "flowbox.view:disabled",
            "window.print:not(.ssd-frame) flowbox.dialog-action-box:disabled",
            "gridview.view:disabled",
            "window.print:not(.ssd-frame) gridview.dialog-action-box:disabled",
        )
        for selector in members:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, dict(DISABLED_TEXT))
        # Source order: each member files after the landed field group's
        # `.view:disabled` key and after the landed
        # `columnview.view:disabled:selected` ink key.
        for selector in members:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index(".view:disabled"),
                selector,
            )
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("columnview.view:disabled:selected"),
                selector,
            )
        # The token sweeps key on substrings no other landed selector
        # carries (the :selected twins of the column- and tree-view
        # spellings contain those bare spellings, so those two members are
        # pinned above by the exact-key assertions instead): a dropped
        # member, a lost comma member, a stray extra rule or a changed
        # value fails.
        for token, expected in (
            ("calendar.view:disabled", "calendar.view:disabled"),
            ("flowbox.view:disabled", "flowbox.view:disabled"),
            ("gridview.view:disabled", "gridview.view:disabled"),
            ("listview.view:disabled", "listview.view:disabled"),
            ("list.view:disabled", "list.view:disabled"),
            ("calendar.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) calendar.dialog-action-box:disabled"),
            ("columnview.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) columnview.dialog-action-box:disabled"),
            ("treeview.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) treeview.dialog-action-box:disabled"),
            ("listview.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) listview.dialog-action-box:disabled"),
            ("list.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) list.dialog-action-box:disabled"),
            ("flowbox.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) flowbox.dialog-action-box:disabled"),
            ("gridview.dialog-action-box:disabled",
             "window.print:not(.ssd-frame) gridview.dialog-action-box:disabled"),
        ):
            with self.subTest(token=token):
                self.assertEqual(
                    {s for s in self.rules if token in s},
                    {expected},
                )
    def test_disabled_link_button_labels(self):
        selectors = (
            "button.link:disabled > label",
            "button.link:visited:disabled > label",
        )
        self.assert_disabled_text(selectors)
        css = strip_comments(self.css)
        enabled = css.index("button.link > label")
        visited = css.index("button.link:visited > label")
        for selector in selectors:
            self.assertGreater(css.index(selector), enabled, selector)
            self.assertGreater(css.index(selector), visited, selector)
    def test_disabled_selected_inline_link_foregrounds(self):
        roots = ("link:selected:disabled", "link:visited:selected:disabled")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        ordinary_disabled = css.index("link:disabled")
        selected_links = css.index("link:selected:not(:disabled)")
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertGreater(css.index(selector), ordinary_disabled, selector)
            self.assertGreater(css.index(selector), selected_links, selector)
    def test_disabled_selected_ancestor_inline_link_foregrounds(self):
        roots = (":selected link:disabled", ":selected link:visited:disabled")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        ordinary_disabled = css.index("link:disabled")
        selected_ancestors = css.index(":selected link:not(:disabled)")
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertGreater(css.index(selector), ordinary_disabled, selector)
            self.assertGreater(css.index(selector), selected_ancestors, selector)
    def test_disabled_selected_row_and_child_arms(self):
        """Pin the disabled selected rows and children restated stock-twin."""
        self.assert_disabled_text((
            "row:disabled:selected",
            "list row.activatable:disabled:selected",
            "listview > row.activatable:disabled:selected",
            "list row.activatable:disabled:selected:backdrop",
            "listview > row.activatable:disabled:selected:backdrop",
            "flowbox > flowboxchild:disabled:selected",
            "gridview > child:disabled:selected",
            "columnview.view:disabled:selected",
            "treeview.view:disabled:selected",
            "columnview.view:disabled:selected:backdrop",
            "treeview.view:disabled:selected:backdrop",
            "label:disabled:selected",
            "textview > text:disabled:selected",
            "textview > text:disabled:selected:focus",
        ))
        # The family adds the calendar stock twin alongside the row/view
        # arms; stock has no big :backdrop disabled group here, so backdrop
        # members are the dedicated view arms. The calendar member is pinned
        # against stock by this exact set assertion.
        # 2026-10-31: selected text arms and the generic .view disabled twin
        # are restated by their focused plan entries.
        # More-specific disabled activatable-row overrides also belong
        # to this inventory and preserve grey against enabled row rules.
        self.assertEqual(
            {
                s for s in self.rules if ":disabled:selected" in s
            },
            {
                "row:disabled:selected",
                "list row.activatable:disabled:selected",
                "listview > row.activatable:disabled:selected",
                "list row.activatable:disabled:selected:backdrop",
                "listview > row.activatable:disabled:selected:backdrop",
                "flowbox > flowboxchild:disabled:selected",
                "gridview > child:disabled:selected",
                "columnview.view:disabled:selected",
                "treeview.view:disabled:selected",
                "columnview.view:disabled:selected:backdrop",
                "treeview.view:disabled:selected:backdrop",
                "calendar > grid > label.day-number:disabled:selected",
                ".view:disabled:selected",
                "label:disabled:selected",
                "textview > text:disabled:selected",
                "textview > text:disabled:selected:focus",
            },
        )
    def test_disabled_meter_trough_faces(self):
        """A disabled meter keeps the landed trough face and rim.

        Stock's disabled trough arm (libgtk-4 light resource line 1083, dark
        twin line 1071) carries a pale face and a per-appearance rim ink and
        the `:disabled` pseudo-class raises it above the landed plain groups,
        so the restated group repeats the landed #EEEEEE face and #000000
        rim at stock's specificity and wins the per-property tie by later
        user-sheet source order under lower-sheet riding; the replacement
        reading keeps the landed plain groups already governing these
        spellings. The selected-row meter rims record restates the
        landed disabled thumb rim at higher specificity beside this
        sweep, but its `row:selected scale > trough > slider:disabled`
        spelling carries no `trough:disabled` substring, so the sweep
        and its non-`.osd` count stay unchanged.
        """
        expected = {"background-color": TROUGH, "border-color": BLACK}
        self.assert_rule_group(
            {
                "progressbar > trough:disabled": dict(expected),
                "scale > trough:disabled": dict(expected),
            }
        )
        # The restated colours sit after the landed grey disabled face, and
        # the landed opaque disabled policy still follows them, so the
        # source-order tie and the filter policy both hold on the raw sheet.
        self.assert_rule_after(
            "progressbar > trough:disabled",
            "progressbar > trough > progress:disabled",
        )
        self.assert_rule_after(
            "progressbar:disabled",
            "scale > trough:disabled",
        )
        allowed = {
            "progressbar > trough:disabled",
            "scale > trough:disabled",
            ".osd progressbar > trough:disabled",
            ".osd scale > trough:disabled",
        }
        trough_disabled = [s for s in self.selectors if "trough:disabled" in s]
        for selector in trough_disabled:
            self.assertIn(selector, allowed, selector)
        self.assertEqual(
            len([s for s in trough_disabled if not s.startswith(".osd")]),
            2,
            trough_disabled,
        )
        for member in ("scale > trough > fill:disabled", "scale > trough > highlight:disabled"):
            for selector in self.selectors:
                if not selector.startswith(".osd"):
                    self.assertNotIn(member, selector, selector)


if __name__ == "__main__":
    unittest.main()
