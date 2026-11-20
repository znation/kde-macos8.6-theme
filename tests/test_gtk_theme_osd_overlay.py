"""Validate GTK 3 Platinum OSD overlay-band declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import BLACK, FACE, WHITE
from support.repo_root import ROOT


class TestGtkThemeOsdOverlay(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

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


if __name__ == "__main__":
    unittest.main()
