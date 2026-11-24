"""Control test cases each GTK suite that inherits them runs once.

These are the shared ``test_*`` control cases the GTK 3 ``TestGtkTheme`` and
the GTK 4 ``Gtk4SheetRuleCases`` inherit once each. The parametrised
assertions they call live in ``tests/support/gtk_rule_cases.py``.
"""

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CHECK,
    CHECK_GLYPH,
    COMBO_ARROW,
    ENTRY_FIELD,
    INVERTED_BUTTON_BEVEL,
    MENU_CHECK,
    MIXED_GLYPH,
    RADIO,
    RADIO_GLYPH,
    ROW_HOVER,
    ROW_SELECTED,
    TOOLTIP,
    TOOLTIP_BACKGROUND,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
)


class GtkSharedControlCases(GtkSheetRuleCases):
    """Shared control test cases run against each inheriting GTK sheet.

    Each suite-level class inherits these cases once, so a suite like the
    GTK 3 theme's ``TestGtkTheme`` runs them exactly once however many
    module-level split-out classes share its assertions; the other split
    classes subclass :class:`GtkSheetRuleCases` directly.
    """

    def assert_infobar_message_type_ban(self, selectors=None):
        """Assert no swept ``infobar`` selector names a message type.

        *selectors* defaults to this sheet's full selector inventory so
        both GTK sheets' ``test_infobar`` cases sweep everything; call
        sites may pass a narrower family instead to restate the ban over
        its own members. The ban covers infobar selectors alone because
        the restated entry colour-class twins carry ``.warning``/
        ``.error`` spellings, and only ``infobar``-containing selectors
        name no message type.
        """
        if selectors is None:
            selectors = self.selectors
        for message_type in (".info", ".question", ".warning", ".error"):
            for selector in selectors:
                if "infobar" in selector:
                    self.assertNotIn(message_type, selector, message_type)

    def test_headerbar(self):
        for selector in ("headerbar", ".titlebar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                    "min-height": "22px",
                    "padding": "0 4px",
                },
            )
        self.assert_rule("headerbar", {"border-width": "0 0 1px 0"})
        for selector in ("headerbar:backdrop", ".titlebar:backdrop"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": INACTIVE_OUTLINE,
                    "box-shadow": "none",
                    "color": GREY,
                },
            )

    def test_button(self):
        self.assert_rule(
            "button",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": BUTTON_BEVEL,
            },
        )
        self.assert_rule("button:hover", {"background-color": FACE})
        for selector in ("button:active", "button:checked"):
            self.assert_rule(selector, {"box-shadow": INVERTED_BUTTON_BEVEL})

    def test_entry(self):
        self.assert_rule("entry", ENTRY_FIELD)

    def test_check_and_radio(self):
        self.assert_rule("check", CHECK)
        self.assert_rule("radio", RADIO)
        self.assert_rule("check:checked", CHECK_GLYPH)
        self.assert_rule("radio:checked", RADIO_GLYPH)
        self.assert_rule("check:indeterminate", MIXED_GLYPH)
        self.assert_rule("radio:indeterminate", MIXED_GLYPH)

        # The plain state-twin arms keep the existing face under
        # every state: each suite's sheet restates the toolkit's plain
        # element-level state arms (quoted verbatim in the sheet-tail
        # comment and in docs/invariants.md) with the existing check and
        # radio faces' fill, border colour and shadow pair -- no geometry,
        # ink, glyph, radius or clip restatement (one transition reach:
        # the no-fade rule erases the stock 200ms backdrop fade
        # on the two bare :backdrop groups). The scanned
        # parser merges each checked and indeterminate spelling's face
        # blocks into the existing glyph spelling's dictionary, so the four
        # merged keys pin the glyph union and the other spellings land in
        # one block each. The suites carry the same plain dictionaries;
        # the GTK 3 sheet adds the three plain :backdrop face arms its
        # toolkit resource declares and the GTK 4 resource lacks.
        check_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": CHECK["box-shadow"],
        }
        check_checked_face = {**check_face, "background-color": FACE}
        radio_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": "none",
        }
        expected = {
            "check:hover": check_face,
            "radio:hover": radio_face,
            "check:active": check_face,
            "radio:active": radio_face,
            "check:disabled": check_face,
            "radio:disabled": radio_face,
            "check:checked": {**CHECK_GLYPH, **check_checked_face},
            "radio:checked": {**RADIO_GLYPH, **radio_face},
            "check:checked:hover": check_checked_face,
            "radio:checked:hover": radio_face,
            "check:checked:active": check_checked_face,
            "radio:checked:active": radio_face,
            "check:checked:disabled": check_checked_face,
            "radio:checked:disabled": radio_face,
            "check:indeterminate": {**MIXED_GLYPH, **check_checked_face},
            "radio:indeterminate": {**MIXED_GLYPH, **radio_face},
            "check:indeterminate:hover": check_checked_face,
            "radio:indeterminate:hover": radio_face,
            "check:indeterminate:active": check_checked_face,
            "radio:indeterminate:active": radio_face,
            "check:indeterminate:disabled": check_checked_face,
            "radio:indeterminate:disabled": radio_face,
        }
        merged = (
            "check:checked",
            "radio:checked",
            "check:indeterminate",
            "radio:indeterminate",
        )
        if "gtk-3.0" in str(self.CSS_PATH):
            # The no-fade rule erases the stock 200ms
            # backdrop fade on the two bare :backdrop groups only, so the
            # checked and indeterminate :backdrop twins read unchanged.
            expected.update(
                {
                    "check:backdrop": {**check_face, "transition": "none"},
                    "radio:backdrop": {**radio_face, "transition": "none"},
                    "check:checked:backdrop": check_checked_face,
                    "radio:checked:backdrop": radio_face,
                    "check:indeterminate:backdrop": check_checked_face,
                    "radio:indeterminate:backdrop": radio_face,
                }
            )
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.selectors.count(selector),
                    2 if selector in merged else 1,
                )
                self.assertEqual(self.rules[selector], declarations)

        # The existing out-of-reach provenance stays: the suite's menu-check
        # keys keep their existing bare-glyph dictionaries and the existing OSD
        # pressed indicators keep the recipe properties their own record
        # pins (the full dictionaries differ between the two sheets'
        # stock-cleared shadow twins, so this pins the recipe surface per
        # property).
        if "gtk-3.0" in str(self.CSS_PATH):
            menu_keys = (
                "menu menuitem check",
                "menu menuitem radio",
                "popover modelbutton check",
                "popover modelbutton radio",
            )
        else:
            menu_keys = (
                "popover modelbutton check",
                "popover.background modelbutton check",
                "popover modelbutton radio",
                "popover.background modelbutton radio",
            )
        for selector in menu_keys:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], MENU_CHECK)
        osd_pins = (
            (".osd check:active", CHECK),
            (".osd radio:active", RADIO),
        )
        for selector, recipe in osd_pins:
            with self.subTest(selector=selector):
                for name in ("background-color", "box-shadow", "border-radius"):
                    self.assertEqual(self.rules[selector][name], recipe[name])
                self.assertEqual(self.rules[selector]["outline-color"], BLACK)

    def test_combobox_arrow(self):
        self.assert_rule("combobox arrow", COMBO_ARROW)

    def test_tooltip(self):
        self.assert_rule("tooltip", TOOLTIP)
        self.assert_rule("tooltip.background", TOOLTIP_BACKGROUND)

    def test_row_hover(self):
        for selector in ("treeview.view:hover", "list row.activatable:hover"):
            self.assert_rule(selector, ROW_HOVER)

    def test_row_selection(self):
        for selector in (
            "treeview.view:selected",
            "treeview.view:selected:hover",
            "list row.activatable:selected",
            "list row.activatable:selected:hover",
        ):
            self.assert_rule(selector, ROW_SELECTED)

        self.assert_tab_faces()

    def test_tab_states(self):
        """Assert the plain tabs' TAB_STATES faces under their named pointer.

        The suite's invariant rows cite the named share case
        ``tests/support/gtk_shared_control_cases.py::GtkSharedControlCases::test_tab_states``;
        the assertion body itself lives in :meth:`assert_tab_faces`, so the
        named case and the stack-switcher/path-bar forms share one recipe and
        stay byte-identical in assertion.
        """
        self.assert_tab_faces()

