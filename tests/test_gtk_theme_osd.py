"""Validate the GTK 3 Platinum sheet's OSD overlay widget groups.

The sheet draws every overlay the reference set does not show with the flat
black OSD band and white-faced controls; this module owns the OSD scope of
``tests/test_gtk_theme.py``'s split: the overlay bands and the colorchooser
OSD popover, the OSD entry fields and spin-button arms, the OSD flat and
suggested/destructive buttons, the OSD check and radio glyphs, the OSD
progress scale and thin bar, and the scale-popup and scale-slider arms. The
sheet's comment blocks carry each value's provenance.
"""

import unittest
from pathlib import Path

from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CHECK,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RADIO,
    SCALE_EMPTY_FILL,
    SCALE_THUMB,
    SCALE_TROUGH,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeOsd(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def assert_osd_selector_count(self, expected, count):
        """Check the flattened selector inventory for an OSD rule family."""
        enumerated = {
            selector for _, selectors in expected for selector in selectors
        }
        self.assertEqual(len(enumerated), count, enumerated)
        return enumerated

    def test_osd_overlay_bands(self):
        selectors = (
            ".osd .scale-popup",
            ".csd popover.background.osd",
            "popover.background.osd",
            ".csd popover.background.touch-selection",
            ".csd popover.background.magnifier",
            "popover.background.touch-selection",
            "popover.background.magnifier",
            ".osd",
            ".osd .scale-popup:backdrop",
            "popover.background.osd:backdrop",
            "popover.background.touch-selection:backdrop",
            "popover.background.magnifier:backdrop",
            ".osd:backdrop",
            "toolbar.osd",
        )
        expected = {
            "background-color": FACE,
            "background-image": "none",
            "color": BLACK,
            "border": "0",
            "border-bottom": f"1px solid {ETCH_DARK}",
            "border-radius": "0",
            "box-shadow": f"inset 0 -1px {WHITE}",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector != "colorchooser .popover.osd"
                and "button" not in selector
                and ((".osd" in selector
                    and ".osd check" not in selector
                    and ".osd entry" not in selector
                    and "fill" not in selector
                    and "highlight" not in selector
                    and "progress" not in selector
                    and ".osd radio" not in selector
                    and ".osd scale slider" not in selector
                    and ".osd spinbutton" not in selector
                    and "trough" not in selector)
                or "magnifier" in selector
                or "touch-selection" in selector
                or "scale-popup" in selector)
            },
            set(selectors),
        )

    def test_colorchooser_osd_popover_corners(self):
        self.assertEqual(
            self.rules["colorchooser .popover.osd"], {"border-radius": "0"}
        )
        self.assertEqual(
            self.rules["colorchooser .popover.osd"]["border-radius"],
            self.rules[".popover"]["border-radius"],
        )

    def test_osd_entry_fields(self):
        """Pin the four restated stock OSD field arms and the nested
        spin-button field's stock-identical clearing.

        No collected reference screenshot shows a field inside a GTK OSD
        overlay, so the sheet restates the toolkit resource's four grouped
        `.osd spinbutton:not(.vertical), .osd entry` arms with the existing
        entry recipe (``ENTRY_FIELD`` in ``support.gtk_theme_spec.py``) plus
        the stock arms' own shadow claims, cleared. The arm selectors,
        states and shadow claims come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49). Each
        state's spin-button arm also carries its RTL twin, the existing etch
        mirror restated beside the group, because the record's
        equal-or-higher specificity kept the plain RTL mirror from ever
        reaching an OSD spin field.
        """
        field = {
            **ENTRY_FIELD,
            "background-image": "none",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        focus = {
            **field,
            "outline": f"1px dotted {BLACK}",
            "outline-offset": "0",
            "-gtk-outline-radius": "0",
        }
        disabled = {**field, "color": DISABLED_TEXT["color"]}
        expected = {
            ".osd spinbutton:not(.vertical)": field,
            ".osd entry": field,
            ".osd spinbutton:focus:not(.vertical)": focus,
            ".osd entry:focus": focus,
            ".osd spinbutton:backdrop:not(.vertical)": field,
            ".osd entry:backdrop": field,
            ".osd spinbutton:disabled:not(.vertical)": disabled,
            ".osd entry:disabled": disabled,
            # The RTL twins restate the existing etch mirror
            # beside each base state group: the groups' equal-or-higher
            # specificity kept the plain RTL mirror from reaching an OSD
            # spin field.
            ".osd spinbutton:dir(rtl):not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):focus:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):backdrop:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):disabled:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            # The nested-field clearing twin restates the
            # resource's byte-equal `.osd spinbutton:not(.vertical) entry`
            # spelling in the entry state-faces record's group, so the
            # family sweep gains its stock-identical clearing.
            ".osd spinbutton:not(.vertical) entry": {
                "min-width": "28px",
                "margin": "0",
                "background": "none",
                "background-color": "transparent",
                "border": "none",
                "border-radius": "0",
                "box-shadow": "none",
            },
        }
        self.assert_rule_group(expected)
        for property_name in ("outline", "outline-offset", "-gtk-outline-radius"):
            self.assertEqual(
                self.rules[".osd entry:focus"][property_name],
                self.rules["entry:focus"][property_name],
            )
        self.assertEqual(
            self.rules[".osd entry:disabled"]["color"],
            self.rules["entry:disabled"]["color"],
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if (".osd entry" in selector or ".osd spinbutton" in selector)
                and " button" not in selector
            },
            set(expected),
        )

    def test_osd_spin_field_mirrors_the_etch_in_rtl(self):
        # The four OSD field groups restate the etch at equal-or-higher
        # specificity than the existing plain RTL mirror, so each state
        # carries its own twin, spelled one class higher than its base
        # group so the win does not depend on source position. Each twin
        # sits directly after its base state group in the comment-stripped
        # sheet, keeping the record together; a twin moved elsewhere —
        # say, gathered at the record's end — breaks the adjacency pin.
        pairs = [
            (
                ".osd spinbutton:not(.vertical),\n.osd entry {",
                ".osd spinbutton:dir(rtl):not(.vertical)",
            ),
            (
                ".osd spinbutton:focus:not(.vertical),\n.osd entry:focus {",
                ".osd spinbutton:dir(rtl):focus:not(.vertical)",
            ),
            (
                ".osd spinbutton:backdrop:not(.vertical),\n.osd entry:backdrop {",
                ".osd spinbutton:dir(rtl):backdrop:not(.vertical)",
            ),
            (
                ".osd spinbutton:disabled:not(.vertical),\n.osd entry:disabled {",
                ".osd spinbutton:dir(rtl):disabled:not(.vertical)",
            ),
        ]
        stripped = strip_comments(self.css)
        for base, twin in pairs:
            with self.subTest(twin=twin):
                self.assertEqual(self.selectors.count(twin), 1, twin)
                self.assertEqual(
                    self.rules[twin],
                    {"box-shadow": "inset -1px 1px #999999"},
                    twin,
                )
                self.assertEqual(stripped.count(twin), 1, twin)
                between = stripped[stripped.index(base):stripped.index(twin)]
                self.assertEqual(
                    between.count("{"),
                    1,
                    f"{twin} does not sit directly after its base group",
                )

    def test_osd_spinbutton_buttons(self):
        """Pin the twelve OSD spinbutton stepper arms to push-button faces."""
        base = {
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
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        horizontal = lambda declarations: declarations
        vertical = lambda declarations: {
            **declarations, "background-clip": "border-box"
        }
        expected = {
            ".osd spinbutton:not(.vertical) button": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl)": horizontal(base),
            ".osd spinbutton:not(.vertical) button:hover": horizontal(base),
            ".osd spinbutton:not(.vertical) button:backdrop": horizontal(base),
            ".osd spinbutton:not(.vertical) button:disabled": horizontal(disabled),
            ".osd spinbutton:not(.vertical) button:dir(ltr):last-child": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl):first-child": horizontal(base),
            ".osd spinbutton.vertical button:first-child": vertical(base),
            ".osd spinbutton.vertical button:first-child:hover": vertical(base),
            ".osd spinbutton.vertical button:first-child:active": vertical(active),
            ".osd spinbutton.vertical button:first-child:disabled": vertical(disabled),
            ".osd spinbutton.vertical button:first-child:backdrop": vertical(base),
        }
        self.assertEqual(len(expected), 12)
        self.assert_rule_group(expected)
        self.assertEqual(
            {selector for selector in self.rules
             if "spinbutton" in selector and " button" in selector
             and any(token in selector for token in (
                 ".osd", "app-notification", "touch-selection", "magnifier"
             ))},
            set(expected),
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
            # test_gtk_theme.TestGtkTheme::test_round_button_face_corners),
            # excluded like the notebook arms. 2026-11-04: the linked-field
            # end-corner record restates the three
            # ``toolbar.inline-toolbar toolbutton…`` end-member arms (linked
            # rows, not overlay bands, pinned by
            # test_gtk_theme_controls.TestGtkThemeControls::
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
             # test_osd_destructive_action.
             if "button" in selector
             and "spinbutton" not in selector
             and "flat" not in selector
             and "suggested-action" not in selector
             and "destructive-action" not in selector
             and any(token in selector for token in osd_like)},
            enumerated,
        )

    def test_osd_suggested_action(self):
        """Pin the nine restated stock OSD suggested-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        suggested-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.suggested-action`` arms with
        the existing plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the existing plain and flat restatements'. The restated arms are
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal, recipe
        ``outline-color`` included, as the existing plain and flat
        backdrop restatements do; the active and checked arms swap only
        ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the disabled arms
        keep ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and
        no ``outline-color``, as the existing disabled arms claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "background-clip": "border-box",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        expected = [
            (base, (
                ".osd button.suggested-action",
                ".osd button.suggested-action:hover",
                ".osd button.suggested-action:backdrop",
            )),
            (active, (
                ".osd button.suggested-action:active:backdrop",
                ".osd button.suggested-action:active",
                ".osd button.suggested-action:checked:backdrop",
                ".osd button.suggested-action:checked",
            )),
            (disabled, (
                ".osd button.suggested-action:disabled:backdrop",
                ".osd button.suggested-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button", ".osd" and "suggested-action" as bare tokens:
            # the shipped sheet's only .osd-scoped suggested-action
            # spellings are these nine restated arms. As of 2026-10-31
            # the generic opaque suggested-action family is restated at
            # the sheet-wide tail (pinned by
            # test_gtk_theme_controls.TestGtkThemeControls
            # .test_suggested_action_plain_arms), so the whole-sheet
            # suggested-action scan this assertion once made is gone;
            # the .flat colour-class members outside .osd still stay
            # undeclared, so the stock resource keeps governing them.
            {selector
             for selector in self.rules
             if "button" in selector
             and ".osd" in selector
             and "suggested-action" in selector},
            enumerated,
        )

    def test_osd_destructive_action(self):
        """Pin the nine restated stock OSD destructive-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        destructive-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.destructive-action`` arms with
        the existing plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the existing plain, flat and suggested-action restatements'. The
        restated arms are the raised ``#DDDDDD`` face with its 1px black
        border and zero radius, ``BUTTON_BEVEL``, and black labels; the
        ``:hover`` and ``:backdrop`` arms repeat the base recipe
        byte-equal, recipe ``outline-color`` included, as the existing
        plain and suggested-action backdrop restatements do; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the existing disabled arms claim none. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "background-clip": "border-box",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        expected = [
            (base, (
                ".osd button.destructive-action",
                ".osd button.destructive-action:hover",
                ".osd button.destructive-action:backdrop",
            )),
            (active, (
                ".osd button.destructive-action:active:backdrop",
                ".osd button.destructive-action:active",
                ".osd button.destructive-action:checked:backdrop",
                ".osd button.destructive-action:checked",
            )),
            (disabled, (
                ".osd button.destructive-action:disabled:backdrop",
                ".osd button.destructive-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button", ".osd" and "destructive-action" as bare tokens:
            # the shipped sheet's only .osd-scoped destructive-action
            # spellings are these nine restated arms. As of 2026-10-31
            # the generic opaque destructive-action family is restated
            # at the sheet-wide tail (pinned by
            # test_gtk_theme_controls.TestGtkThemeControls
            # .test_destructive_action_plain_arms), so the whole-sheet
            # destructive-action scan this assertion once made is gone;
            # the .flat colour-class members outside .osd still stay
            # undeclared, so the stock resource keeps governing them.
            {selector
             for selector in self.rules
             if "button" in selector
             and ".osd" in selector
             and "destructive-action" in selector},
            enumerated,
        )

    def test_osd_check_radio(self):
        """Pin the ten restated stock OSD indicator arms.

        No collected reference screenshot shows a check or radio inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's five `.osd`
        indicator arms with the existing plain check and radio recipes (CHECK
        and RADIO in ``support.gtk_theme_spec.py``) plus two clearances the
        stock arms claim: the white-on-dark text and icon shadows, cleared,
        and a black focus-outline colour in place of the stock
        rgba(238,238,236,0.3). The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); each arm is byte-for-byte the recipe in every
        state, because the armed spellings set no geometry, glyph source or
        checked spelling stock could override.
        """
        clearance = {
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        check = {**CHECK, **clearance}
        radio = {**RADIO, **clearance}
        states = ("", ":hover", ":active", ":backdrop", ":disabled")
        expected = {}
        for state in states:
            expected[f".osd check{state}"] = check
            expected[f".osd radio{state}"] = radio
        parsed = {}
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected[selector])
            parsed[selector] = self.rules[selector]
        self.assertEqual(
            [dict(parsed[f".osd check{state}"]) for state in states],
            [check] * 5,
        )
        self.assertEqual(
            [dict(parsed[f".osd radio{state}"]) for state in states],
            [radio] * 5,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd check" in selector or ".osd radio" in selector},
            set(expected),
        )

    def test_osd_progress_scale(self):
        """Pin the nine restated stock OSD trough, fill and progress arms.

        No collected reference screenshot shows a meter inside a GTK OSD
        overlay, so the sheet restates the toolkit resource's six `.osd`
        trough/fill/progress groups with the existing plain progress-bar and
        scale recipes (``PROGRESSBAR_TROUGH``, ``PROGRESSBAR_PROGRESS``,
        ``SCALE_TROUGH`` and ``SCALE_EMPTY_FILL`` in
        ``support.gtk_theme_spec.py``): the flat ``#EEEEEE`` trough face with
        its black border, zero radius and ``inset 1px 1px #999999`` etch at
        the existing minimums, the transparent scale fill and highlight face,
        and the existing ``#CCCCFF`` progress fill. The disabled groups repeat
        the existing paints byte-for-byte, and the disabled progress fill is
        the existing grey (``GREY`` from ``support.platinum_palette``). The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        stock arms claim no geometry, glyph source or box-shadow, so the
        existing plain meter rules keep governing size and every state an arm
        does not restate.
        """
        trough = PROGRESSBAR_TROUGH
        scale_trough = SCALE_TROUGH
        fill = SCALE_EMPTY_FILL
        progress = PROGRESSBAR_PROGRESS
        disabled_progress = {**PROGRESSBAR_PROGRESS, "background-color": GREY}
        expected = [
            (trough, (
                ".osd progressbar trough",
                "progressbar .osd trough",
                ".osd progressbar trough:disabled",
                "progressbar .osd trough:disabled",
            )),
            (scale_trough, (
                ".osd scale trough",
                "scale .osd trough",
                ".osd scale trough:disabled",
                "scale .osd trough:disabled",
            )),
            (fill, (
                ".osd scale fill",
                "scale .osd fill",
                ".osd scale highlight",
                "scale .osd highlight",
                ".osd scale fill:disabled:backdrop",
                ".osd scale fill:disabled",
                "scale .osd fill:disabled",
                ".osd scale highlight:disabled",
                "scale .osd highlight:disabled",
            )),
            (progress, (
                ".osd progressbar progress",
                "progressbar .osd progress",
            )),
            (disabled_progress, (
                ".osd progressbar progress:disabled",
                "progressbar .osd progress:disabled",
            )),
        ]
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            self.rules[".osd progressbar progress:disabled"]["background-color"],
            self.rules["progressbar progress:disabled"]["background-color"],
        )
        self.assertEqual(
            self.rules["progressbar progress:disabled"]["background-color"],
            GREY,
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd" in selector
                and (
                    "trough" in selector
                    or "fill" in selector
                    or "highlight" in selector
                    or "progress" in selector
                )
            },
            {selector
             for _, selectors in expected
             for selector in selectors}
            | {"progressbar.osd trough", "progressbar.osd progress",
               "progressbar.osd progress:disabled"},
        )

    def test_osd_thin_bar(self):
        """Pin the two restated stock self-class ``.osd`` thin-bar arms.

        No collected reference screenshot shows a GTK OSD overlay, a meter
        inside one or a self-class ``.osd`` thin bar (a ``progressbar.osd``,
        the thin Epiphany-style headerbar indicator), so the sheet restates
        the toolkit resource's stock ``progressbar.osd trough`` and
        ``progressbar.osd progress`` arms with the existing plain progress-bar
        recipes (``PROGRESSBAR_TROUGH`` and ``PROGRESSBAR_PROGRESS`` in
        ``support.gtk_theme_spec.py``), the same reuse the existing GTK 4
        sheet's ``progressbar.osd > trough`` face makes (pinned by
        ``TestGtk4Theme::test_progressbar_osd_trough_paint``). The equal
        specificity restatements append after the toolkit resource, so they
        pre-empt exactly the stock arms they restate, and the existing
        ``.osd progressbar trough, progressbar .osd trough`` ancestor arms
        stay disjoint. The bare ``progressbar.osd`` node arm stays
        undeclared: its ``3px`` minimum is dominated by the trough's
        ``10px`` minimum and its transparent node background stays beneath
        the trough face. The arm selectors and stock claims come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no stock arm claims geometry, so the existing
        plain rules keep governing every state an arm does not restate.
        """
        with self.subTest(selector="progressbar.osd trough"):
            self.assertEqual(self.rules["progressbar.osd trough"],
                             PROGRESSBAR_TROUGH)
        with self.subTest(selector="progressbar.osd progress"):
            self.assertEqual(self.rules["progressbar.osd progress"],
                             PROGRESSBAR_PROGRESS)
        # The self-class base arm otherwise overrides the plain disabled grey.
        self.assertEqual(self.rules["progressbar.osd progress:disabled"],
                         {"background-color": GREY})

    def test_osd_scale_slider(self):
        """Pin the six restated stock OSD scale thumb arms.

        No collected reference screenshot shows a scale thumb inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's six
        ``.osd scale slider`` arms with the existing plain scale-thumb recipes
        (``SCALE_THUMB`` in ``support.gtk_theme_spec.py``) plus two
        clearances the stock arms claim: the white-on-dark text and icon
        shadows, cleared, and a black focus-outline colour in place of the
        stock rgba(238,238,236,0.3). Stock's background-clip stays omitted
        and the stateless arms carry the plain thumb's ``-5px`` margin. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        plain ``scale slider`` rules keep governing size and every state an
        arm does not restate.
        """
        face = {
            **SCALE_THUMB,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        base = {**face, "margin": "-5px"}
        disabled = {
            "background-color": FACE,
            "border": f"1px solid {GREY}",
            "box-shadow": "none",
        }
        raised_states = ("", ":hover", ":active", ":backdrop")
        for state in raised_states:
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"],
                    base if state in ("", ":backdrop") else face,
                )
        for state in (":disabled", ":backdrop:disabled"):
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"], disabled
                )
        self.assertEqual(
            self.rules[".osd scale slider:disabled"],
            self.rules["scale slider:disabled"],
        )
        # The plain knob's existing no-fade amendment is specific to the bare
        # arm's stock animating members; stock's .osd thumb arms claim no
        # transition, so the shared recipe excludes that one member.
        self.assertEqual(
            self.rules[".osd scale slider"],
            {
                **{
                    name: value
                    for name, value in self.rules["scale slider"].items()
                    if name != "transition"
                },
                "outline-color": BLACK,
                "text-shadow": "none",
                "-gtk-icon-shadow": "none",
            },
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd scale slider" in selector
            },
            {
                f".osd scale slider{state}"
                for state in raised_states + (":disabled", ":backdrop:disabled")
            },
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
