"""Validate GTK 3 notebook declarations in the Platinum sheet."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, DISABLED_TEXT, INVERTED_BUTTON_BEVEL
from support.platinum_palette import BLACK, FACE
from support.repo_root import ROOT


class TestGtkThemeNotebook(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {"background-color": FACE, "border": f"1px solid {BLACK}"},
        )

    def test_notebook_tab_close_button_arms(self):
        for selector in (
            "notebook > header tab button.flat",
            "notebook > header tab button.flat:backdrop",
        ):
            self.assert_rule(selector, {"color": BLACK})
        for selector in (
            "notebook > header tab button.flat:disabled",
            "notebook > header tab button.flat:backdrop:disabled",
        ):
            self.assert_rule(selector, {"color": DISABLED_TEXT["color"]})

    def test_notebook_tab_scroll_arrow_faces(self):
        """Pin the 2026-11-11 notebook overflow-arrow restatement."""
        # 2026-11-11: stock paints the notebook header's overflow arrows
        # with the flat-button family — transparent at rest, a toolkit
        # gradient plus a highlighted glyph on hover, 5px-rounded corners —
        # and no collected reference screenshot shows the arrows, so each
        # state arm below restates the existing plain `button.flat` family's
        # dictionary at the arrow's own exact stock spelling, later source
        # order winning the tie per-property.
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        hover = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "-gtk-icon-effect": "none",
            "transition": "none",
        }
        # The radius addition is the base twin's alone: in the hovered and
        # pressed states stock's own later re-square arm (line 912) already
        # squares the arrow, so the other twins carry the existing
        # `button.flat` dictionaries byte-equal.
        flat = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        arrow = "notebook > header > tabs > arrow"
        self.assert_rule_group({
            arrow: face,
            f"{arrow}.flat": face,
            f"{arrow}:hover": hover,
            f"{arrow}.flat:hover": hover,
            f"{arrow}:hover:active": {"transition": "none"},
            f"{arrow}.flat:hover:active": {"transition": "none"},
            f"{arrow}:active": sunken,
            f"{arrow}:checked": sunken,
            f"{arrow}:backdrop": flat,
            f"{arrow}:backdrop:active": sunken,
            f"{arrow}:backdrop:checked": sunken,
            f"{arrow}:backdrop:disabled": disabled,
            f"{arrow}:backdrop:disabled:active": disabled,
            f"{arrow}:backdrop:disabled:checked": disabled,
            f"{arrow}:disabled": disabled,
            f"{arrow}:disabled:active": disabled,
            f"{arrow}:disabled:checked": disabled,
            f"{arrow}:hover:not(:active):not(:backdrop)": hover,
        })
        # Source order: the base arrow group files after the existing
        # plain `button.flat` family's tail group, so every arrow twin
        # decides the equal-specificity race against the stock arms.
        self.assert_rule_after(
            f"{arrow},\n{arrow}.flat {{",
            "button.flat:disabled:active, button.flat:disabled:checked {",
        )
        # The token sweep keys on a substring no other existing selector
        # carries: a dropped twin, a renamed spelling, a lost comma member
        # or a stray extra rule fails.
        self.assertEqual(
            {selector for selector in self.selectors if arrow in selector},
            {
                arrow,
                f"{arrow}.flat",
                f"{arrow}:hover",
                f"{arrow}.flat:hover",
                f"{arrow}:hover:active",
                f"{arrow}.flat:hover:active",
                f"{arrow}:active",
                f"{arrow}:checked",
                f"{arrow}:backdrop",
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:hover:not(:active):not(:backdrop)",
            },
        )

    def test_notebook_tab_focus_outline(self):
        self.assert_dotted_focus_outline("notebook > header > tabs > tab:focus")

if __name__ == "__main__":
    unittest.main()

