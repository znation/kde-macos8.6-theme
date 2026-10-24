"""Platinum spec values shared by the GTK 3, GTK 4 and Firefox sheet suites.

The two GTK stylesheets implement the same Platinum control spec: one etched
separator, the same bevels and tab-state selectors, and the same base
``@define-color`` roles. Each sheet suite still reads and asserts against its
own stylesheet; this module only holds the values the sheets must agree on.
The Firefox sheet takes :data:`ETCH_DARK` for its etched separators. The GTK 4
sheet extends :data:`BASE_DEFINED_COLOURS` with its own surface roles.
:class:`SheetRuleAssertions` holds the rule assertion all three suites use.
:class:`GtkSheetRuleCases` holds the control rules the two GTK suites share,
plus the progress-bar, scale, menu-separator and frame assertions they name
with their own selectors.
"""

from __future__ import annotations

from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    WHITE,
)

# The etched separator's dark half, pinned to the reference by
# tests/test_desktoptheme_line.py's DARK value.
ETCH_DARK = "#888888"

BASE_DEFINED_COLOURS = {
    "theme_bg_color": FACE,
    "theme_fg_color": BLACK,
    "theme_base_color": WHITE,
    "theme_text_color": BLACK,
    "theme_selected_bg_color": SELECTION,
    "theme_selected_fg_color": BLACK,
    "borders": BLACK,
    "unfocused_borders": GREY,
}

RAISED_BEVEL = f"inset 1px 1px {WHITE}, inset -1px -1px {GREY}"
BUTTON_BEVEL = f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW}"
INVERTED_BUTTON_BEVEL = f"inset 1px 1px {BUTTON_SHADOW}, inset -1px -1px {WHITE}"

# The progress-bar and scale spec both sheets implement. Their selectors differ
# (GTK 3 names the nodes as descendants, GTK 4 as children), but the trough,
# selection fill and beveled thumb declarations must match.
PROGRESSBAR_TROUGH = {
    "background-color": TROUGH,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": f"inset 1px 1px {GREY}",
    "min-height": "10px",
    "min-width": "10px",
}
PROGRESSBAR_PROGRESS = {
    "background-color": SELECTION,
    "background-image": "none",
    "border": "0",
    "border-radius": "0",
    "box-shadow": "none",
    "margin": "0",
}
SCALE_TROUGH = {**PROGRESSBAR_TROUGH, "min-height": "6px", "min-width": "6px"}
SCALE_EMPTY_FILL = {
    "background-color": "transparent",
    "background-image": "none",
    "border": "0",
    "border-radius": "0",
    "box-shadow": "none",
    "margin": "0",
}
SCALE_THUMB = {
    "background-color": FACE,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": RAISED_BEVEL,
}

# Both sheets spell the tooltip selectors the same way.
TOOLTIP = {
    "background-color": TOOLTIP_FACE,
    "color": BLACK,
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": "none",
    "padding": "2px 4px",
}
TOOLTIP_BACKGROUND = {
    "background-color": TOOLTIP_FACE,
    "background-clip": "padding-box",
}

MENU_SEPARATOR = {
    "background-color": ETCH_DARK,
    "border": "0",
    "border-bottom": f"1px solid {WHITE}",
    "margin": "2px 0",
    "min-height": "1px",
    "padding": "0",
}

FRAME = {
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": f"inset 1px 1px {GREY}",
    "margin": "0",
    "padding": "0",
}

# Every tab state covers both the plain and the notebook-scoped selectors, in
# the plain and `.reorderable-page` forms. A checked state also names the third
# member: whether its bevel and bottom border must be dropped.
TAB_STATES = (
    (
        "base",
        (
            "tab",
            "tab.reorderable-page",
            "notebook > header > tabs > tab",
            "notebook > header > tabs > tab.reorderable-page",
        ),
        False,
    ),
    (
        "hover",
        (
            "tab:hover",
            "tab.reorderable-page:hover",
            "notebook > header > tabs > tab:hover",
            "notebook > header > tabs > tab.reorderable-page:hover",
        ),
        False,
    ),
    (
        "checked",
        (
            "tab:checked",
            "tab.reorderable-page:checked",
            "notebook > header > tabs > tab:checked",
            "notebook > header > tabs > tab.reorderable-page:checked",
        ),
        True,
    ),
    (
        "checked+hover",
        (
            "tab:checked:hover",
            "tab.reorderable-page:checked:hover",
            "notebook > header > tabs > tab:checked:hover",
            "notebook > header > tabs > tab.reorderable-page:checked:hover",
        ),
        True,
    ),
    (
        "backdrop",
        (
            "tab:backdrop",
            "tab.reorderable-page:backdrop",
            "notebook > header > tabs > tab:backdrop",
            "notebook > header > tabs > tab.reorderable-page:backdrop",
        ),
        False,
    ),
    (
        "backdrop+checked",
        (
            "tab:backdrop:checked",
            "tab.reorderable-page:backdrop:checked",
            "notebook > header > tabs > tab:backdrop:checked",
            "notebook > header > tabs > tab.reorderable-page:backdrop:checked",
        ),
        True,
    ),
)


class SheetRuleAssertions:
    """Rule assertion for suites that store the parsed sheet in ``self.rules``."""

    def assert_rule(self, selector, expected):
        """Assert *selector* exists and carries each declaration in *expected*."""
        self.assertIn(selector, self.rules, f"missing rule for {selector}")
        for name, value in expected.items():
            self.assertEqual(
                self.rules[selector].get(name),
                value,
                f"{selector}: expected {name}: {value}",
            )


class GtkSheetRuleCases(SheetRuleAssertions):
    """The control rules the GTK 3 and GTK 4 sheets must both satisfy.

    Both suites inherit these cases and run them against their own parsed
    ``self.rules``. Selectors and values that differ between the sheets
    (window, notebook header, scrollbar, popover, toolbar) stay in the suite
    that owns them. The progress-bar, scale, menu-separator and frame
    assertions take the suite's own selectors, since GTK 3 and GTK 4 spell the
    same nodes differently.
    """

    def test_headerbar(self):
        for selector in ("headerbar", ".titlebar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                },
            )
        self.assert_rule("headerbar", {"border-width": "0 0 1px 0"})

    def test_button(self):
        self.assert_rule(
            "button",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": BUTTON_BEVEL,
            },
        )
        self.assert_rule("button:hover", {"background-color": FACE})
        for selector in ("button:active", "button:checked"):
            self.assert_rule(selector, {"box-shadow": INVERTED_BUTTON_BEVEL})

    def test_entry(self):
        self.assert_rule(
            "entry",
            {
                "background-color": WHITE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
                "color": BLACK,
            },
        )

    def test_tooltip(self):
        self.assert_rule("tooltip", TOOLTIP)
        self.assert_rule("tooltip.background", TOOLTIP_BACKGROUND)

    def test_tab_states(self):
        for state, selectors, checked in TAB_STATES:
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in selectors:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def assert_progressbar(self, trough, progress, disabled):
        """Assert the shared progress-bar spec against this sheet's selectors."""
        self.assert_rule(trough, PROGRESSBAR_TROUGH)
        self.assert_rule(progress, PROGRESSBAR_PROGRESS)
        self.assert_rule(disabled, {"background-color": GREY})

    def assert_menu_separator(self, selectors):
        """Assert the Platinum etched menu separator against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, MENU_SEPARATOR)

    def assert_frame(self, selectors):
        """Assert the sunken frame bevel against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, FRAME)

    def assert_scale(
        self, trough, fill, slider, horizontal, vertical, disabled
    ):
        """Assert the shared scale spec against this sheet's selectors.

        *fill* is a tuple of the empty-fill selectors; the slider's hover and
        active states are derived from *slider*.
        """
        self.assert_rule(trough, SCALE_TROUGH)
        for selector in fill:
            self.assert_rule(selector, SCALE_EMPTY_FILL)
        self.assert_rule(slider, {**SCALE_THUMB, "margin": "-5px"})
        self.assert_rule(horizontal, {"min-width": "12px", "min-height": "16px"})
        self.assert_rule(vertical, {"min-width": "16px", "min-height": "12px"})
        for selector in (f"{slider}:hover", f"{slider}:active"):
            self.assert_rule(selector, SCALE_THUMB)
        self.assert_rule(
            disabled,
            {
                "background-color": FACE,
                "border": f"1px solid {GREY}",
                "box-shadow": "none",
            },
        )
