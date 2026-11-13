"""GTK 4 popover and toast declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT, ETCH_DARK
from support.platinum_palette import BLACK, FACE, SELECTION


class TestGtk4Popover(Gtk4SheetRuleCases, unittest.TestCase):
    def test_popover(self):
        for selector in ("popover > contents", "popover > arrow"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                },
            )
        for selector in (
            "popover.menu modelbutton:hover",
            "popover.menu modelbutton:selected",
        ):
            self.assert_rule(selector, {"background-color": SELECTION})
        # Stock's popover-menu modelbutton arms declare a 5px corner
        # (Default-light.css in libgtk-4 4.18.6, probed 2026-11-03); the
        # restated byte-twin arms square the row like the square popover
        # contents shell above.
        for selector in ("popover.menu modelbutton", "modelbutton.flat"):
            self.assertEqual(self.rules[selector], {"border-radius": "0"})
            self.assertEqual(
                self.rules[selector]["border-radius"],
                self.rules["popover > contents"]["border-radius"],
            )
        # Stock's grey colour arms still govern the hover, disabled and
        # pressed-selected states of a standalone flat modelbutton and the
        # pressed-selected state inside a popover menu; the byte-twin
        # restatements paint the existing selection fill and disabled text
        # there (Default-light.css in libgtk-4 4.18.6, probed 2026-11-03).
        for selector in (
            "popover.menu modelbutton:selected:active",
            "modelbutton.flat:hover",
        ):
            self.assertEqual(self.rules[selector], {"background-color": SELECTION})
            self.assertEqual(
                self.rules[selector]["background-color"],
                self.rules["popover.menu modelbutton:hover"]["background-color"],
            )
        self.assertEqual(self.rules["modelbutton.flat:disabled"], {"color": ETCH_DARK})
        # The existing sheet carries no other modelbutton arm: any stray,
        # renamed or removed kind fails the family bound.
        self.assertEqual(
            {selector for selector in self.rules if "modelbutton" in selector},
            {
                "popover.menu modelbutton:hover",
                "popover.menu modelbutton:selected",
                "popover.menu modelbutton:selected:active",
                "popover modelbutton check",
                "popover modelbutton radio",
                "popover.background modelbutton check",
                "popover.background modelbutton radio",
                "popover.menu modelbutton > arrow.right",
                "popover.menu modelbutton",
                "modelbutton.flat",
                "modelbutton.flat:hover",
                "modelbutton.flat:disabled",
            },
        )
        # Both squaring arms sit after the existing hover/select block, the
        # source position that beats any same-theme arm on the corner.
        for selector in ("popover.menu modelbutton", "modelbutton.flat"):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("popover.menu modelbutton:hover"),
            )
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("popover.menu modelbutton:selected"),
            )
        # Each colour arm sits after the existing hover/select blocks and the
        # squaring radius arms, the source position that beats stock's
        # equal-specificity grey arms and keeps the family together.
        for selector in (
            "popover.menu modelbutton:selected:active",
            "modelbutton.flat:hover",
            "modelbutton.flat:disabled",
        ):
            for earlier in (
                "popover.menu modelbutton:hover",
                "popover.menu modelbutton:selected",
                "popover.menu modelbutton",
                "modelbutton.flat",
            ):
                self.assertGreater(
                    self.selectors.index(selector), self.selectors.index(earlier)
                )

    def test_popover_menu_accelerator_foreground(self):
        selector = "popover.menu accelerator"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT})
        # Stock dims the accelerator inside the color declaration alone, so
        # the restatement carries the opacity-free, shadow-free dict whole.
        self.assert_exact_rule_once(selector, {**DISABLED_TEXT})
        # The stock-twin spelling lands after the existing popover-menu
        # modelbutton faces, the source position that beats either toolkit
        # arm on the tie.
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("popover.menu modelbutton"),
        )

    def test_toast_surface(self):
        selectors = {"toast", "toast:backdrop"}
        self.assertEqual(
            {selector for selector in self.selectors if "toast" in selector},
            selectors,
        )
        expected = {
            "background-color": FACE,
            "background-image": "none",
            "color": BLACK,
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": "none",
            "text-shadow": "none",
        }
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                self._assert_toast_matches_popover(selector)


if __name__ == "__main__":
    unittest.main()
