"""Validate the GTK 3 Platinum sheet's switch and status indicators.

This module owns the switch slice split out of
the former GTK 3 controls suite: the switch track and thumb faces, the
switch focus outline, the switch's state and backdrop faces, and the spinner
and level-bar status indicators. The declaration tests read the stripped CSS
through ``GtkSheetRuleCases``.
"""

import unittest
from pathlib import Path

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeSwitch(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_spinner(self):
        self.assert_spinner("-gtk-icon-transform")

    def test_levelbar(self):
        self.assert_levelbar(
            trough="levelbar trough",
            filled="levelbar block.filled",
            empty="levelbar block.empty",
            disabled="levelbar block.filled:disabled",
            horizontal="levelbar.horizontal block",
            vertical="levelbar.vertical block",
        )

    def test_switch(self):
        self.assert_switch(
            slider="switch slider",
            disabled_slider="switch:disabled slider",
            glyph="switch image",
        )

    def test_switch_focus_outline(self):
        self.assert_dotted_focus_outline("switch:focus")

    def test_switch_state_and_backdrop_faces(self):
        """The existing switch faces hold through every toolkit repaint.

        The toolkit's state, backdrop and selected-row switch arms
        out-specify the existing groups (see the
        sheet), so each stock spelling is restated byte-equal and wins by
        later user-sheet source order. Each spelling counts exactly once,
        the three existing groups carry exactly one added member each, and
        the family sweeps admit no stray or renamed spelling.
        """
        # The restated knob arms: the raised bevel face, no fade.
        for selector in ("switch:hover slider", "switch:backdrop slider"):
            self.assert_rule(
                selector,
                {
                    "border-color": BLACK,
                    "background-image": "none",
                    "box-shadow": "inset 1px 1px #FFFFFF,"
                    " inset -1px -1px #999999",
                    "transition": "none",
                },
            )
        self.assert_rule("switch:checked > slider", {"border-color": BLACK})
        self.assert_rule(
            "switch:backdrop",
            {
                "background-color": TROUGH,
                "border-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            "switch:backdrop:checked",
            {"background-color": WHITE, "border-color": BLACK},
        )
        self.assert_rule(
            "switch:backdrop:disabled",
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assert_rule(
            "switch:backdrop:disabled slider",
            {
                "border-color": GREY,
                "background-image": "none",
                "box-shadow": "none",
                "transition": "none",
            },
        )
        # The selected-row twins of the existing `row:selected button` record.
        for selector in (
            "row:selected switch",
            "row:selected switch:backdrop",
            "row:selected switch > slider:checked",
            "row:selected switch > slider",
        ):
            self.assert_rule(selector, {"border-color": BLACK})

        # The three amended existing groups: one added member each, no more.
        self.assert_rule("switch:checked", {"border-color": BLACK})
        self.assert_rule("switch:disabled", {"background-color": TROUGH})
        self.assert_rule("switch slider", {"transition": "none"})
        self.assertEqual(
            self.rules["switch:checked"],
            {
                "background-color": WHITE,
                "background-image": "none",
                "border-color": BLACK,
            },
        )
        self.assertEqual(
            self.rules["switch:disabled"],
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assertEqual(
            self.rules["switch slider"],
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": "inset 1px 1px #FFFFFF,"
                " inset -1px -1px #999999",
                "margin": "-1px",
                "min-width": "12px",
                "min-height": "16px",
                "transition": "none",
            },
        )
        for selector in ("switch:checked", "switch:disabled", "switch slider"):
            self.assertEqual(self.selectors.count(selector), 1, selector)

        # Family sweeps: no stray or renamed spelling survives.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch") and ":backdrop" in s
            },
            {
                "switch:backdrop",
                "switch:backdrop:checked",
                "switch:backdrop:disabled",
                "switch:backdrop slider",
                "switch:backdrop:checked > slider",
                "switch:backdrop:disabled slider",
            },
        )
        self.assertEqual(
            {s for s in self.selectors if "row:selected switch" in s},
            {
                "row:selected switch",
                "row:selected switch:backdrop",
                "row:selected switch > slider:checked",
                "row:selected switch > slider",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch")
                and ":backdrop" not in s
                and (
                    ":hover" in s
                    or ":active" in s
                    or ":checked" in s
                    or ":disabled" in s
                )
            },
            {
                "switch:checked",
                "switch:disabled",
                "switch:disabled slider",
                "switch:hover slider",
                "switch:checked > slider",
            },
        )

        # Order: the restated block sits between the existing `switch image`
        # group and the existing toolbar band group.
        self.assertGreater(
            self.css.index("switch:hover slider"),
            self.css.index("switch image {"),
        )
        self.assertLess(
            self.css.index("switch:hover slider"),
            self.css.index("toolbar, menubar {"),
        )


if __name__ == "__main__":
    unittest.main()
