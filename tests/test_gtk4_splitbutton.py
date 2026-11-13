"""GTK 4 split-button container and band corner declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4SplitButton(Gtk4SheetRuleCases, unittest.TestCase):
    def test_split_button_container_corners(self):
        container = "splitbutton"
        band = [
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "splitbutton.flat > button",
            "splitbutton.flat > menubutton > button",
        ]
        self.assertEqual(
            {
                selector
                for selector, declarations in self.rules.items()
                if "splitbutton" in selector and "border-radius" in declarations
            },
            {container} | set(band),
        )
        splitbutton = self.rules[container]
        # The existing container record keeps its frame-equal radius; the
        # 2026-11-04 band group squares the absolute-band and .flat faces
        # beside it, and test_splitbutton_band_corners pins their spellings.
        self.assertEqual(splitbutton, {"border-radius": "0"})
        for selector in ("frame > border", ".frame", "button"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    splitbutton["border-radius"],
                    self.rules[selector]["border-radius"],
                )
        for selector in band:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})

    def test_splitbutton_band_corners(self):
        """Pin the toolbar-band and flat split-button face corners.

        The band arm carries four :not() classes behind every band prefix,
        so the existing generic button radius restate loses on it; the group
        restates every spelling byte-equal to stock so later user-sheet
        source order wins the equal-specificity cascade tie.
        """
        band = [
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "splitbutton.flat > button",
            "splitbutton.flat > menubutton > button",
        ]
        # The existing band focus twins end with :focus:focus-visible, so
        # they stay out of this suffix scan, and the bare container key
        # never ends with these suffixes either. Exactly ten face spellings
        # square to the policy; nothing else in the sheet touches a
        # split-button face.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "splitbutton" in s
                and (s.endswith("> button") or s.endswith("> menubutton > button"))
            },
            set(band),
        )
        for selector in band:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                # The group sits between the existing searchbar band focus
                # group and the residual focus group: after the existing
                # splitbutton container key, before label:focus:focus-visible.
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("splitbutton"),
                )
                self.assertLess(
                    self.selectors.index(selector),
                    self.selectors.index("label:focus:focus-visible"),
                )


if __name__ == "__main__":
    unittest.main()
