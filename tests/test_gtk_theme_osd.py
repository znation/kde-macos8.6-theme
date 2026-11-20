"""Validate the GTK 3 Platinum sheet's OSD overlay widget groups.

The sheet draws every overlay the reference set does not show with the flat
black OSD band and white-faced controls; this module owns the OSD scope of
``tests/test_gtk_theme.py``'s split: the colorchooser OSD popover and the scale-popup
arms. OSD suggested-action declarations live in
``tests/test_gtk_theme_osd_suggested.py``. OSD scale-thumb declarations live in
``tests/test_gtk_theme_osd_scale.py``. OSD check and radio indicators live in
``tests/test_gtk_theme_osd_indicators.py``. Entry fields and spin-button
steppers live in ``tests/test_gtk_theme_osd_fields.py``. Meter declarations
live in ``tests/test_gtk_theme_osd_meters.py``. OSD destructive-action
declarations live in ``tests/test_gtk_theme_osd_destructive.py``. OSD
overlay-band declarations live in ``tests/test_gtk_theme_osd_overlay.py``. The
OSD flat-button declarations live in ``tests/test_gtk_theme_osd_flat.py``.
Plain OSD push-button declarations live in ``tests/test_gtk_theme_osd_buttons.py``.
The sheet's comment blocks carry each value's provenance.
"""

import unittest
from pathlib import Path

from support.gtk_osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
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

    def test_scale_popup_buttons(self):
        """Clear the stock rounded scale-popup button overrides."""
        self.assert_scale_popup_buttons()

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
