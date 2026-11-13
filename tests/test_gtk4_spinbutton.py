"""GTK 4 spinbutton declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import BLACK, FACE, GREY, WHITE


class TestGtk4Spinbutton(Gtk4SheetRuleCases, unittest.TestCase):
    def test_spinbutton_focus_outline_color(self):
        for selector in (
            "spinbutton.vertical > text:focus-within",
            "spinbutton:focus-within:not(.vertical)",
            "spinbutton:focus-within",
        ):
            with self.subTest(selector=selector):
                self.assert_scale_focus_outline(selector)
                self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("spinbutton")
                and "focus-within" in s
                and ".error" not in s
                and ".warning" not in s
                and "selection" not in s
            },
            {
                "spinbutton.vertical > text:focus-within",
                "spinbutton:focus-within:not(.vertical)",
                "spinbutton:focus-within",
            },
        )

    def test_spinbutton_focus_transition(self):
        self.assert_scale_slider_transition("spinbutton")

    def test_spinbutton_steppers(self):
        """Pin the restated stock plain spinbutton stepper arms.

        No collected reference screenshot shows a GTK spinbutton stepper
        in any state, so the sheet restates the toolkit resource's seven
        plain (non-``.osd``) horizontal ``spinbutton ... button`` stepper
        arms with the existing raised push-button face — the same dictionary
        the existing OSD stepper record pins — so a horizontal stepper
        outside the OSD overlay paints the raised #DDDDDD face with a 1px
        black border, zero radius, the BUTTON_BEVEL etch, black labels and
        no icon shadow. This plain family is the only family stock gives
        an ``:active`` arm, and the pressed arm swaps to the inverted
        bevel; the disabled arms take the existing grey Etch colour
        (ETCH_DARK) and keep no outline colour. Stock's min-height and
        padding geometry are not restated, and stock's plain vertical
        ``spinbutton.vertical > button`` geometry arms stay stock: the
        existing generic button restate paints them and their shared-edge
        mechanics are the existing linked-group policy. The arm selectors
        and states come from
        /org/gtk/libgtk/theme/Default/Default-dark.css and
        Default-light.css in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1
        (libgtk-4 4.18.6); each horizontal comma-group splits into two
        selector keys, so the seven groups hold the fourteen spellings
        the family scan pins.
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
        up = "spinbutton:not(.vertical) > button.image-button.up:not(.flat)"
        down = (
            "spinbutton:not(.vertical)"
            " > button.image-button.down:not(.flat)"
        )
        expected = {}
        arms = (
            ("", base),
            (":dir(rtl)", base),
            (":hover", base),
            (":disabled", disabled),
            (":active", active),
            (":dir(ltr):last-child", base),
            (":dir(rtl):first-child", base),
        )
        for suffix, recipe in arms:
            for prefix in (up, down):
                expected[prefix + suffix] = recipe
        self.assertEqual(len(expected), 14)
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, declarations)
        # No other non-.osd ``spinbutton … button`` spelling exists in the
        # sheet: the existing .linked group members pair the two names but
        # carry no `` button`` token, and the existing OSD steppers are
        # excluded here, so the scan kills renamed and stray variants.
        # The 2026-11-04 residual radii record adds the six byte-equal
        # row-spin steppers (the vertical preference-row variant stock
        # gives its own 9px and 9999px arms) to this scan; the existing
        # plain-steppers record named those variants its own future
        # candidates, and their selectors carry the `` button`` token the
        # scan keys on.
        row_spin = (
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(rtl):first-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
        )
        # The 2026-11-04 axis-chain record adds the eight byte-equal
        # libadwaita spin-button end-corner chains (five extra :not() atoms
        # beat these existing short restatements' specificity, so the chains
        # needed their own zero-radius restatement) to this scan; their
        # selectors carry the `` button`` token the scan keys on, and each
        # rule is the bare zero radius the new record restates.
        chain = (
            "spinbutton:not(.vertical) > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "spinbutton:not(.vertical) > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "spinbutton:not(.vertical) > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
            "spinbutton:not(.vertical) > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
            "spinbutton.vertical > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "spinbutton.vertical > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "spinbutton.vertical > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):first-child",
            "spinbutton.vertical > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):first-child",
        )
        for selector in chain:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})
        self.assertEqual(
            {
                s
                for s in self.rules
                if "spinbutton" in s
                and " button" in s
                and ".osd" not in s
            },
            set(expected) | set(row_spin) | set(chain),
        )
        # The seven groups sit between the existing entry.warning focus arm
        # and the existing OSD entry-field block.
        first = self.selectors.index(up)
        last = self.selectors.index(
            "spinbutton:not(.vertical)"
            " > button.image-button.down:not(.flat):dir(rtl):first-child"
        )
        self.assertLess(
            self.selectors.index("entry.warning:focus-within"), first
        )
        self.assertLess(
            last, self.selectors.index(".osd spinbutton.vertical > text")
        )

    def test_spinbutton_axis_corner_chains(self):
        """Pin the restated stock plain-axis spinbutton end-corner chains.

        No collected reference screenshot shows a GTK spin button in any
        state, so the sheet restates the integration resource's four
        radius-bearing plain-axis ``button.image-button`` arms with a bare
        zero radius — each byte-equal to its stock twin and winning the
        equal-specificity tie by later user-sheet source order. The existing
        plain-stepper record squared these same nodes through the toolkit
        resource's short :not(.flat) chains, but the integration chains
        carry five extra :not() class atoms whose higher specificity beat
        those short restatements, so the corner radii stayed stock's 9px
        cuts until these four groups were added; the arms were probed
        2026-11-04 from /org/gnome/Adwaita/styles/base.css (lines 2157,
        2159, 2165 and 2167, quoted verbatim in the sheet comment whose
        probe path is recorded in docs/invariants.md), and the toolkit's
        Default resources carry only the short spelling the existing short
        restatements are byte-equal to. The vertical end halves'
        border-top-width and
        border-bottom-width shared-edge mechanics stay inherited
        per-property, and the base arm's sizing paddings stay stock too.
        """
        chains = (
            "spinbutton:not(.vertical) > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "spinbutton:not(.vertical) > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "spinbutton:not(.vertical) > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
            "spinbutton:not(.vertical) > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
            "spinbutton.vertical > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "spinbutton.vertical > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "spinbutton.vertical > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):first-child",
            "spinbutton.vertical > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):first-child",
        )
        for selector in chains:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_matches_frame(selector, "border-radius")
        # The sweep keys on the :not() atom count stock's chains alone
        # carry: every existing spinbutton-rooted key carries at most two
        # :not() atoms and the row-spin keys start with the row compound,
        # so the scan kills a dropped, renamed or de-qualified chain.
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("spinbutton")
                and s.count(":not(") >= 5
            },
            set(chains),
        )
        # Every chain sits after the existing short corner twin in source
        # order, so the additions are tail-resident whatever merges first.
        for selector in chains:
            with self.subTest(selector=selector):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index(
                        "spinbutton:not(.vertical)"
                        " > button.image-button.down:not(.flat)"
                        ":dir(rtl):first-child"
                    ),
                )


if __name__ == "__main__":
    unittest.main()

