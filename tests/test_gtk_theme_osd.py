"""Validate the GTK 3 Platinum sheet's OSD overlay widget groups.

The sheet draws every overlay the reference set does not show with the flat
black OSD band and white-faced controls; this module owns the OSD scope of
``tests/test_gtk_theme.py``'s split: the colorchooser OSD popover, the OSD
flat button, and the scale-popup
arms. OSD suggested-action declarations live in
``tests/test_gtk_theme_osd_suggested.py``. OSD scale-thumb declarations live in
``tests/test_gtk_theme_osd_scale.py``. OSD check and radio indicators live in
``tests/test_gtk_theme_osd_indicators.py``. Entry fields and spin-button
steppers live in ``tests/test_gtk_theme_osd_fields.py``. Meter declarations
live in ``tests/test_gtk_theme_osd_meters.py``. OSD destructive-action
declarations live in ``tests/test_gtk_theme_osd_destructive.py``. OSD
overlay-band declarations live in ``tests/test_gtk_theme_osd_overlay.py``. The
sheet's comment blocks carry each value's provenance.
"""

import unittest
from pathlib import Path

from support.gtk_osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import (
    BLACK,
    FACE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeOsd(OsdSelectorAssertions, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_colorchooser_osd_popover_corners(self):
        self.assertEqual(
            self.rules["colorchooser .popover.osd"], {"border-radius": "0"}
        )
        self.assertEqual(
            self.rules["colorchooser .popover.osd"]["border-radius"],
            self.rules[".popover"]["border-radius"],
        )

    def test_osd_flat_button(self):
        """Pin the 24 restated stock OSD flat-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        flat button inside one, so the sheet restates the toolkit
        resource's grouped ``.app-notification button.flat, …, .osd
        button.flat`` arms with the existing plain push-button recipe (the
        base ``button`` dictionary ``test_osd_button`` pins):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the existing disabled arms also claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock
            ``button.osd`` minimums and the stock ``.osd .scale-popup
            button.flat`` pointer arm is restated by its dedicated test;
            the restated blocks
        put disabled after backdrop so inactive insensitive labels stay
        grey; active/checked keeps stock's sheet-order win over hover.
        """
        recipe = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**recipe, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": ETCH_DARK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        expected = [
            (recipe, (
                ".app-notification button.flat",
                "popover.background.touch-selection button.flat",
                "popover.background.magnifier button.flat",
                ".osd button.flat",
                ".app-notification button.flat:hover",
                "popover.background.touch-selection button.flat:hover",
                "popover.background.magnifier button.flat:hover",
                ".osd button.flat:hover",
                ".app-notification button.flat:backdrop",
                "popover.background.touch-selection button.flat:backdrop",
                "popover.background.magnifier button.flat:backdrop",
                ".osd button.flat:backdrop",
            )),
            (disabled, (
                ".app-notification button.flat:disabled",
                "popover.background.touch-selection button.flat:disabled",
                "popover.background.magnifier button.flat:disabled",
                ".osd button.flat:disabled",
            )),
            (active, (
                ".app-notification button.flat:active",
                "popover.background.touch-selection button.flat:active",
                "popover.background.magnifier button.flat:active",
                ".app-notification button.flat:checked",
                "popover.background.touch-selection button.flat:checked",
                "popover.background.magnifier button.flat:checked",
                ".osd button.flat:active",
                ".osd button.flat:checked",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 24)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        # Equal-specificity disabled and backdrop arms must keep grey text.
        for family in (
            ".app-notification button.flat",
            "popover.background.touch-selection button.flat",
            "popover.background.magnifier button.flat",
            ".osd button.flat",
        ):
            candidates = {family + ":disabled", family + ":backdrop"}
            colour = None
            for selector in self.selectors:
                if selector in candidates:
                    colour = self.rules[selector]["color"]
            with self.subTest(disabled_backdrop=family):
                self.assertEqual(colour, ETCH_DARK)
        self.assertEqual(
            # "button" and "flat" as bare tokens: the shipped sheet's only
            # button.flat spellings are these 24 restated arms plus the
            # dedicated scale-popup flat-button arm. 2026-10-31: the plain
            # flat colour-class series restates `button.flat` arms at the
            # sheet tail, so the sweep keeps to the overlay bands by
            # keeping only prefixed spellings: every overlay arm names
            # its scope before `button`, and this series' plain flat keys
            # (generic and future `…-action.flat` twins) start with
            # `button.flat` or `button.suggested-action.flat`. 2026-10-31:
            # the selected-row button series restates two `row:selected
            # button.flat…` arms at the sheet tail (pinned by
            # test_selected_row_button_arms), prefixed like the overlay
            # arms, so the sweep keeps to the overlay bands still by
            # keeping only the named prefix sets. 2026-10-31: the notebook
            # tab-close restatements (pinned by
            # test_notebook_tab_close_button_arms) get their own exclusion.
            # 2026-11-04: the existing round-button face corners carry the bare
            # ``modelbutton.flat`` and ``.menuitem.button.flat`` stock twins
            # (menu rows, not overlay bands, pinned by
            # test_gtk_theme_corners.TestGtkThemeCorners::test_round_button_face_corners),
            # excluded like the notebook arms. 2026-11-04: the linked-field
            # end-corner record restates the three
            # ``toolbar.inline-toolbar toolbutton…`` end-member arms (linked
            # rows, not overlay bands, pinned by
            # test_gtk_theme_linked.TestGtkThemeLinked::
            # test_linked_end_field_corners), excluded like the notebook
            # arms.
            {selector
             for selector in self.rules
             if "button" in selector and "flat" in selector
             and not selector.startswith("button")
             and not selector.startswith("row:selected button")
             and not selector.startswith("notebook > header tab")
             and selector not in
             ("modelbutton.flat", ".menuitem.button.flat",
              "toolbar.inline-toolbar toolbutton:first-child > button.flat",
              "toolbar.inline-toolbar toolbutton:last-child > button.flat",
              "toolbar.inline-toolbar toolbutton:only-child > button.flat")},
            enumerated | {".osd .scale-popup button.flat"},
        )

    def test_scale_popup_buttons(self):
        """Clear the stock rounded scale-popup button overrides."""
        self.assert_scale_popup_buttons()

    def test_osd_button(self):
        """Pin the 37 restated stock OSD push-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        push button inside one, so the sheet restates the toolkit
        resource's stock ``button.osd`` and grouped ``.app-notification
        button, …, .osd button`` arms with the existing plain push-button
        recipe (the base ``button`` dictionary pinned by
        ``support.gtk_rule_cases.py::GtkSheetRuleCases::test_button``):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the active and checked
        arms swap only ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the
        disabled arms keep ``BUTTON_BEVEL`` with the Inactive grey
        (``ETCH_DARK``); ``outline-color: #000000`` replaces the stock
        rgba(238,238,236,0.3) only in the arms whose stock counterparts
        claim an outline colour. The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no restated arm sets on-disk geometry, so the
        stock ``button.osd`` minimums and the ``button.osd.image-button``
        minimum-width arm keep governing.
        """
        recipe = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**recipe, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": ETCH_DARK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        expected = [
            (recipe, (
                "button.osd",
                "button.osd:hover",
                "button.osd:backdrop",
                ".app-notification button",
                ".app-notification.frame button",
                ".csd popover.background.touch-selection button",
                ".csd popover.background.magnifier button",
                "popover.background.touch-selection button",
                "popover.background.magnifier button",
                ".osd button",
                ".app-notification button:hover",
                "popover.background.touch-selection button:hover",
                "popover.background.magnifier button:hover",
                ".osd button:hover",
                ".app-notification button:backdrop",
                "popover.background.touch-selection button:backdrop",
                "popover.background.magnifier button:backdrop",
                ".osd button:backdrop",
            )),
            (active, (
                "button.osd:active",
                "button.osd:checked",
                ".app-notification button:active",
                "popover.background.touch-selection button:active",
                "popover.background.magnifier button:active",
                ".app-notification button:checked",
                "popover.background.touch-selection button:checked",
                "popover.background.magnifier button:checked",
                ".osd button:active:backdrop",
                ".osd button:active",
                ".osd button:checked:backdrop",
                ".osd button:checked",
            )),
            (disabled, (
                "button.osd:disabled:backdrop",
                "button.osd:disabled",
                ".app-notification button:disabled",
                "popover.background.touch-selection button:disabled",
                "popover.background.magnifier button:disabled",
                ".osd button:disabled:backdrop",
                ".osd button:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 37)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        osd_like = (".osd", "app-notification", "touch-selection",
                    "magnifier")
        self.assertEqual(
            {selector
             for selector in self.rules
             # "button" as a bare token: a spinbutton is a field, not a
             # button, so its node spelling never counts toward the scan;
             # a flat button node carries the flat-style arms, not the
             # plain ones, and is pinned by test_osd_flat_button; a
             # suggested-action or destructive-action button node
             # carries its own restated arms, also not the plain ones,
             # and is pinned by test_osd_suggested_action and
             # test_osd_destructive_action in the focused OSD modules.
             if "button" in selector
             and "spinbutton" not in selector
             and "flat" not in selector
             and "suggested-action" not in selector
             and "destructive-action" not in selector
             and any(token in selector for token in osd_like)},
            enumerated,
        )

    def test_queued_claims_track_the_sheet(self):
        """Provenance prose names existing rules, never queued future plans.

        The sheet comments and the register rows may say an arm is
        restated (naming the existing groups that restate it) or absent
        (naming the residual) — never that one awaits a queued plan.
        """
        banned = (
            "queued surface plan",
            "queued surface plans",
            "queued plan",
            "queued plans",
        )
        sheet = CSS.read_text(encoding="utf-8")
        register = (Path(ROOT) / "docs" / "invariants.md").read_text(
            encoding="utf-8"
        )
        for text, source in ((sheet, CSS), (register, "docs/invariants.md")):
            for phrase in banned:
                self.assertNotIn(phrase, text, f"{source}: {phrase!r}")
        # The residual arm stays recorded, not silently in place: no rule
        # in the parsed sheet carries an .osd-qualified colorswatch
        # selector.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "colorswatch" in selector and ".osd" in selector
            },
            set(),
        )
        # The existing groups the rewritten prose cross-references really
        # exist in the parsed sheet.
        for selector in (
            ".osd spinbutton:not(.vertical) button",
            "colorchooser .popover.osd",
            ".osd .scale-popup button.flat",
            "progressbar.osd trough",
            "progressbar.osd progress",
        ):
            self.assertIn(selector, self.rules)


if __name__ == "__main__":
    unittest.main()
