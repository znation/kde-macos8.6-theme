"""GTK 4 infobar and search-bar close-button corner and family checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import BLACK, FACE


class TestGtk4CloseButton(Gtk4SheetRuleCases, unittest.TestCase):
    # The 2026-11-09 face extension gives the corner pair the whole existing
    # `button.flat` face recipe beside the radius, so the exact-dict checks
    # below assert the merged dict instead of the radius alone.
    CLOSE_CORNER_PAIR_RULE = {
        "background-color": FACE,
        "background-image": "none",
        "border": f"1px solid {BLACK}",
        "border-radius": "0",
        "box-shadow": BUTTON_BEVEL,
        "transition": "none",
    }

    def test_close_button_corners(self):
        # Stock circles the infobar and search-bar close buttons; the
        # square-corner policy squares both faces, and the added
        # 2026-11-09 face extension paints the existing `button.flat` recipe
        # on them. The existing window-controls close pair is the sibling
        # this test's radius sweep expects beside them.
        selectors = ("infobar .close", "searchbar > revealer > box .close")
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, self.CLOSE_CORNER_PAIR_RULE)
                self.assert_matches_frame(selector, "border-radius")
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("floating-sheet > sheet"),
                )
        self.assertEqual(
            {
                selector
                for selector, declarations in self.rules.items()
                if "close" in selector and "border-radius" in declarations
            },
            {
                "infobar .close",
                "searchbar > revealer > box .close",
                "headerbar windowcontrols button.close",
                ".titlebar windowcontrols button.close",
            },
        )

    def test_close_button_family(self):
        # The 2026-11-09 family restates every stock flat-band face the
        # close class carries except the typed-band twins (the existing
        # message-type ban needs no type token) and the `:drop(active)`
        # ring (nothing existing governs a button drop arm). The four
        # raised-hover recipe faces share the existing `button.flat:hover`
        # recipe minus its radius declaration (the corner pair keeps the
        # radius ownership alone), with the stock ink claim re-pinned
        # black; the pressed and checked faces share the existing inverted
        # bevel; the disabled face keeps the existing `button:disabled`
        # shape and clears the stock dim filter under the existing
        # preserve-the-palette policy.
        hover = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
            "color": BLACK,
        }
        pressed = {
            "background-color": FACE,
            "background-image": "none",
            "box-shadow": INVERTED_BUTTON_BEVEL,
        }
        disabled = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
            "filter": "none",
        }
        expected = {
            "infobar.action:hover > revealer > box": {"background-color": FACE},
            "infobar .close:hover": hover,
            "searchbar .close:hover": hover,
            "searchbar > revealer > box .close:hover": hover,
            "infobar .keyboard-activating.close": pressed,
            "infobar .close:active": pressed,
            "searchbar > revealer > box .keyboard-activating.close": pressed,
            "searchbar > revealer > box .close:active": pressed,
            "infobar .close:checked": pressed,
            "searchbar > revealer > box .close:checked": pressed,
            "infobar .close:checked:hover": pressed,
            "searchbar > revealer > box .close:checked:hover": pressed,
            "infobar .close:checked.keyboard-activating": pressed,
            "infobar .close:checked:active": pressed,
            "searchbar > revealer > box .close:checked.keyboard-activating": pressed,
            "searchbar > revealer > box .close:checked:active": pressed,
            "infobar .close:disabled:not(:checked)": disabled,
            "searchbar > revealer > box .close:disabled:not(:checked)": disabled,
            "infobar .close:focus:focus-visible": {"outline-color": BLACK},
        }
        self.assert_rule_group(expected)
        # The family sweep: every sheet selector naming a close class against
        # an infobar or a search bar is exactly the existing corner pair, the
        # existing searchbar close focus spelling and this family.
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if ".close" in selector
                and ("infobar" in selector or selector.startswith("searchbar"))
            },
            {
                "infobar .close",
                "searchbar > revealer > box .close",
                "searchbar > revealer > box .close:focus:focus-visible",
                *{s for s in expected if ".close" in s},
            },
        )
        # Each family selector sits after the corner groups' index, so the
        # source-order win over the stock arms stays honest.
        corner_index = max(
            self.selectors.index("infobar .close"),
            self.selectors.index("searchbar > revealer > box .close"),
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertGreater(self.selectors.index(selector), corner_index)
        # The existing message-type ban already reads every infobar carrier
        # through test_infobar; restate it over the family's own members so
        # a future edit cannot add a type token inside this group.
        self.assert_infobar_message_type_ban(expected)


if __name__ == "__main__":
    unittest.main()
