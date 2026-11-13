"""GTK 4 notebook declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, DISABLED_TEXT, INVERTED_BUTTON_BEVEL
from support.platinum_palette import BLACK, FACE


class TestGtk4Notebook(Gtk4SheetRuleCases, unittest.TestCase):
    def test_notebook_focus_transition(self):
        self.assert_scale_slider_transition(
            "notebook > header > tabs > tab:checked"
        )


    def test_notebook_tab_close_button_arms(self):
        for selector in (
            "notebook > header > tabs > tab button.flat",
            "notebook > header > tabs > tab button.flat:backdrop",
        ):
            self.assert_rule(selector, {"color": BLACK})
        for selector in (
            "notebook > header > tabs > tab button.flat:disabled",
            "notebook > header > tabs > tab button.flat:backdrop:disabled",
        ):
            self.assert_rule(selector, {"color": DISABLED_TEXT["color"]})


    def test_notebook_tab_scroll_arrow_faces(self):
        """Pin the 2026-11-11 notebook overflow-arrow restatement."""
        # 2026-11-11: stock paints the notebook header's overflow arrows
        # with the plain button family — rounded grey-gradient bevels and a
        # brightness-boosted hover glyph — and no collected reference
        # screenshot shows the arrows, so each state arm below restates the
        # existing same-sheet button arm at the arrow's own exact stock
        # spelling, later source order winning the tie per-property.
        raised = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "transition": "none",
        }
        arrow = "notebook > header > tabs > arrow"
        self.assert_rule_group({
            arrow: raised,
            f"{arrow}:hover": {**raised, "-gtk-icon-filter": "none"},
            f"{arrow}:hover:not(:active):not(:backdrop)": {
                **raised, "-gtk-icon-filter": "none"},
            **dict.fromkeys((
                f"{arrow}.keyboard-activating",
                f"{arrow}:active",
                f"{arrow}:checked",
            ), sunken),
            **dict.fromkeys((
                f"{arrow}:checked:hover",
                f"{arrow}:checked:active",
            ), sunken),
            f"{arrow}:focus:focus-visible": {"outline-color": BLACK},
            **dict.fromkeys((
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
            ), {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": DISABLED_TEXT["color"],
            }),
            f"{arrow}:backdrop": {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            },
            **dict.fromkeys((
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
            ), {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": INVERTED_BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            }),
        })
        # Source order: the base arrow group files after the existing
        # `button.flat` family's tail block, so every arrow twin decides
        # the equal-specificity race against the stock arms.
        self.assertGreater(
            self.selectors.index(arrow),
            self.selectors.index("button.flat:backdrop"),
        )
        # The token sweep keys on a substring no other existing selector
        # carries: a dropped twin, a renamed spelling, a lost comma member
        # or a stray extra rule fails.
        self.assertEqual(
            {selector for selector in self.selectors if arrow in selector},
            {
                arrow,
                f"{arrow}:hover",
                f"{arrow}:hover:not(:active):not(:backdrop)",
                f"{arrow}.keyboard-activating",
                f"{arrow}:active",
                f"{arrow}:checked",
                f"{arrow}:checked:hover",
                f"{arrow}:checked:active",
                f"{arrow}:focus:focus-visible",
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
                f"{arrow}:backdrop",
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
            },
        )


    def test_notebook_focus_outline_color(self):
        self.assert_scale_focus_outline(
            "notebook:focus:focus-visible > header > tabs > tab:checked"
        )


    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {
                "background-color": FACE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )


if __name__ == "__main__":
    unittest.main()
