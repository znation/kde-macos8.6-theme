"""GTK 4 OSD overlay declaration checks, split from the sheet suite."""

import unittest
from itertools import chain

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import (
    CHECK,
    ENTRY_FIELD,
    ETCH_DARK,
    INFOBAR,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RADIO,
    SCALE_EMPTY_FILL,
    SCALE_TROUGH,
    SCALE_THUMB,
)
from support.platinum_palette import BLACK, FACE, GREY, WHITE


class TestGtk4Osd(Gtk4SheetRuleCases, unittest.TestCase):
    def test_osd_entry_fields(self):
        # The existing entry recipe governs the stock OSD overlay field family
        # too: the sheet restates the toolkit resource's three grouped
        # translucent dark field arms with byte-equal twins carrying the
        # existing ENTRY_FIELD recipe plus the stock-cleared shadings, so a
        # resting, focused or disabled entry or spin-button field inside the
        # existing overlay band paints the raised field instead of dropping
        # back to stock's translucent bubble or the toolkit accent focus
        # border. No collected reference screenshot shows a field inside a
        # GTK OSD overlay, so this is the standing GTK-scope adaptation,
        # mirroring the existing GTK 3 OSD record and the existing GTK 4 OSD
        # check/radio restate; the arms come from
        # /org/gtk/libgtk/theme/Default/Default-light.css and Default-dark.css
        # in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 (libgtk-4 4.18.6).
        field = {
            **ENTRY_FIELD,
            "background-image": "none",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        states = (
            (
                ".osd spinbutton.vertical > text",
                ".osd spinbutton:not(.vertical)",
                ".osd entry",
            ),
            (
                ".osd spinbutton.vertical > text:focus-within",
                ".osd spinbutton:focus-within:not(.vertical)",
                ".osd entry:focus-within",
            ),
            (
                ".osd spinbutton.vertical > text:disabled",
                ".osd spinbutton:disabled:not(.vertical)",
                ".osd entry:disabled",
            ),
        )
        selectors = tuple(chain.from_iterable(states))
        for selector in selectors:
            self.assert_exact_rule_once(selector, field)
        # No other `.osd`-prefixed entry or spinbutton spelling exists
        # beyond the restated field arms and the existing RTL spin-field
        # mirrors the OSD record carries (three `:dir(rtl)` twins, one
        # beside each state group): the scan excludes the stock
        # stepper families (`> button`) and the stock inner-text arms
        # (`.osd spinbutton:not(.vertical) > text` and its backdrop-disabled
        # twin, which carry `:not(.vertical) > text`), so it kills renamed
        # and stray variants alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith(".osd")
                and ("entry" in s or "spinbutton" in s)
                and "> button" not in s
                and ":not(.vertical) > text" not in s
            },
            set(selectors)
            | {
                ".osd spinbutton:dir(rtl):not(.vertical)",
                ".osd spinbutton:dir(rtl):focus-within:not(.vertical)",
                ".osd spinbutton:dir(rtl):disabled:not(.vertical)",
            },
        )

    def test_osd_container_bands(self):
        selectors = (
            ".osd .scale-popup",
            ".app-notification",
            ".rich-list > header",
            ".osd popover.background > arrow",
            ".osd popover.background > contents",
            "popover.background.touch-selection > arrow",
            "popover.background.touch-selection > contents",
            "popover.background.magnifier > arrow",
            "popover.background.magnifier > contents",
            ".osd",
            ".osd popover.background",
            ".toolbar.osd",
            ".osd popover",
            "popover.touch-selection",
            "popover.magnifier",
            ".osd popover > arrow",
            ".osd popover > contents",
            "popover.touch-selection > arrow",
            "popover.touch-selection > contents",
            "popover.magnifier > arrow",
            "popover.magnifier > contents",
        )
        expected = {
            **INFOBAR,
            "background-image": "none",
            "border": "0",
            "border-radius": "0",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector],
                    {**expected, "padding": "13px"}
                    if selector == ".toolbar.osd" else expected,
                )
                infobar = self.rules["infobar > revealer > box"]
                for prop in INFOBAR:
                    self.assertEqual(self.rules[selector][prop], infobar[prop])

        arms = {
            f".osd {node}{state}"
            for node in ("check", "radio")
            for state in ("", ":hover", ":active", ":disabled")
        }
        existing = {
            # The 2026-11-04 residual-corner row squares the color chooser's
            # class-qualified OSD popover cap; its rule carries only the
            # radius, and the sweep's tokens name no `button` in that
            # spelling, so the whole-sheet sweep below must know it too.
            "colorchooser .popover.osd",
            "video image.osd",
            "progressbar.osd > trough",
            "progressbar.osd.horizontal > trough",
            "progressbar.osd.vertical > trough",
            ".osd switch:checked",
            ".osd progressbar > trough",
            ".osd scale > trough",
            ".osd scale > trough > fill",
            ".osd scale > trough > highlight",
            ".osd progressbar > trough > progress",
            ".osd progressbar > trough:disabled",
            ".osd scale > trough:disabled",
            ".osd scale > trough > fill:disabled",
            ".osd scale > trough > highlight:disabled",
            ".osd progressbar > trough > progress:disabled",
            ".osd scale > trough > slider",
            ".osd scale > trough > slider:hover",
            ".osd scale > trough > slider:active",
            ".osd scale > trough > slider:disabled",
            # The OSD entry-field restate: the stock
            # `.osd` field-arm spellings lack the substring `button`, so the
            # whole-sheet sweep below must hold them too; the six spin-button
            # spellings are already excluded by it, as `spinbutton` contains
            # `button`.
            ".osd entry",
            ".osd entry:focus-within",
            ".osd entry:disabled",
        } | arms
        tokens = (
            "osd",
            "touch-selection",
            "magnifier",
            "scale-popup",
            "app-notification",
            "rich-list",
        )
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if "button" not in selector
                and any(token in selector for token in tokens)
            },
            set(selectors) | existing,
        )

    def test_osd_check_radio(self):
        """Pin the four restated stock OSD indicator arms.

        No collected reference screenshot shows a check or radio inside a
        GTK OSD overlay, so the sheet restates the toolkit resource's four
        `.osd check`/`.osd radio` arms with the existing plain check and radio
        recipes (CHECK and RADIO in ``support.gtk_theme_spec.py``) plus one
        clearance the stock arms claim: a black focus-outline colour in
        place of the toolkit's accent-tinted ring. The arm selectors and
        states come from /org/gtk/libgtk/theme/Default/Default-dark.css and
        Default-light.css in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1
        (libgtk-4 4.18.6); each arm is byte-for-byte the recipe in every
        state, because the armed spellings set no geometry, glyph source or
        checked spelling stock could override.
        """
        check = {**CHECK, "outline-color": BLACK}
        radio = {**RADIO, "outline-color": BLACK}
        states = ("", ":hover", ":active", ":disabled")
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
            [check] * 4,
        )
        self.assertEqual(
            [dict(parsed[f".osd radio{state}"]) for state in states],
            [radio] * 4,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd check" in selector or ".osd radio" in selector},
            set(expected),
        )

    def test_osd_spinbutton_steppers(self):
        """Pin the restated stock OSD spinbutton stepper arms.

        No collected reference screenshot shows a spinbutton stepper
        inside a GTK OSD overlay, so the sheet restates the toolkit
        resource's ten ``.osd spinbutton ... button`` stepper arms with
        the existing raised push-button face (the dictionary the existing
        GTK 3 sibling record
        ``tests/test_gtk_theme_osd.py``
        ::test_osd_spinbutton_buttons pins from the same specs), like the
        existing .osd check/radio and scale-thumb restatements: the raised
        #DDDDDD face with a 1px black border, zero radius, the
        BUTTON_BEVEL etch and black labels; the disabled arms take the
        existing grey Etch colour (ETCH_DARK) and keep no outline colour,
        as the existing disabled arms also claim none; the vertical pressed
        arm swaps to the INVERTED_BUTTON_BEVEL; and the vertical arms
        carry the background-clip: border-box clearance stock's
        padding-box claim needs behind the opaque black border. Stock
        declares no horizontal :active arm and no :backdrop arm in either
        family. The arm selectors and states come from
        /org/gtk/libgtk/theme/Default/Default-dark.css and
        Default-light.css in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1
        (libgtk-4 4.18.6); each horizontal comma-group splits into two
        selector keys, so the ten groups hold the sixteen spellings the
        family scan pins.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {GREY}",
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {
            **base,
            "box-shadow": f"inset 1px 1px {GREY}, inset -1px -1px {WHITE}",
        }
        disabled = {
            name: value for name, value in base.items()
            if name != "outline-color"
        }
        disabled["color"] = ETCH_DARK
        horizontal = lambda declarations: declarations
        vertical = lambda declarations: {
            **declarations, "background-clip": "border-box"
        }
        up = ".osd spinbutton:not(.vertical) > button.image-button.up:not(.flat)"
        down = (
            ".osd spinbutton:not(.vertical)"
            " > button.image-button.down:not(.flat)"
        )
        expected = {}
        horizontal_arms = (
            ("", base),
            (":dir(rtl)", base),
            (":hover", base),
            (":disabled", disabled),
            (":dir(ltr):last-child", base),
            (":dir(rtl):first-child", base),
        )
        for suffix, recipe in horizontal_arms:
            for prefix in (up, down):
                expected[prefix + suffix] = horizontal(recipe)
        vertical_arms = (
            ("", base),
            (":hover", base),
            (":active", active),
            (":disabled", disabled),
        )
        for suffix, recipe in vertical_arms:
            expected[f".osd spinbutton.vertical > button:first-child{suffix}"] = (
                vertical(recipe)
            )
        self.assertEqual(len(expected), 16)
        self.assert_rule_group(expected)
        # No other `spinbutton … button` spelling exists inside the overlay
        # scope: the scan kills renamed and stray variants alike (the existing
        # entry-field spellings carry no ` button` token).
        self.assertEqual(
            {
                s
                for s in self.rules
                if "spinbutton" in s
                and " button" in s
                and ".osd" in s
            },
            set(expected),
        )
        # The ten groups sit between the existing OSD scale-thumb tail and the
        # existing scale-popup block.
        first = self.selectors.index(up)
        last = self.selectors.index(
            ".osd spinbutton.vertical > button:first-child:disabled"
        )
        self.assertLess(
            self.selectors.index(".osd scale > trough > slider:disabled"), first
        )
        self.assertLess(last, self.selectors.index(".osd .scale-popup button.flat"))

    def test_osd_progress_scale(self):
        progress_trough = PROGRESSBAR_TROUGH
        scale_trough = SCALE_TROUGH
        fill = SCALE_EMPTY_FILL
        progress = PROGRESSBAR_PROGRESS
        disabled_progress = {**PROGRESSBAR_PROGRESS, "background-color": GREY}
        expected = {
            ".osd progressbar > trough": progress_trough,
            ".osd scale > trough": scale_trough,
            ".osd scale > trough > fill": fill,
            ".osd scale > trough > highlight": fill,
            ".osd progressbar > trough > progress": progress,
            ".osd progressbar > trough:disabled": progress_trough,
            ".osd scale > trough:disabled": scale_trough,
            ".osd scale > trough > fill:disabled": fill,
            ".osd scale > trough > highlight:disabled": fill,
            ".osd progressbar > trough > progress:disabled": disabled_progress,
        }
        self.assert_rule_group(expected)
        self.assertEqual(
            self.rules[".osd scale > trough > fill"],
            self.rules[".osd scale > trough > highlight"],
        )
        self.assertEqual(
            self.rules[".osd progressbar > trough > progress:disabled"]["background-color"],
            self.rules["progressbar > trough > progress:disabled"]["background-color"],
        )
        node_names = ("trough", "fill", "highlight", "progress")
        self.assertEqual(
            {
                selector for selector in self.selectors
                if ".osd" in selector
                and "slider" not in selector
                and any(node in selector for node in node_names)
            } - {
                "progressbar.osd > trough",
                "progressbar.osd.horizontal > trough",
                "progressbar.osd.vertical > trough",
            },
            set(expected),
        )

    def test_osd_scale_thumbs(self):
        """Pin the four OSD scale-thumb arms to the ordinary thumb recipes."""
        enabled = {
            **SCALE_THUMB,
            "color": BLACK,
            "outline-color": BLACK,
            "background-clip": "border-box",
        }
        disabled = {
            **enabled,
            "border": f"1px solid {GREY}",
            "box-shadow": "none",
        }
        expected = {
            ".osd scale > trough > slider": enabled,
            ".osd scale > trough > slider:hover": enabled,
            ".osd scale > trough > slider:active": enabled,
            ".osd scale > trough > slider:disabled": disabled,
        }
        self.assert_rule_group(expected)
        plain_disabled = self.rules["scale > trough > slider:disabled"]
        self.assertEqual(disabled["border"], plain_disabled["border"])
        self.assertEqual(disabled["box-shadow"], plain_disabled["box-shadow"])
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd" in selector and "slider" in selector},
            set(expected),
        )


if __name__ == "__main__":
    unittest.main()
