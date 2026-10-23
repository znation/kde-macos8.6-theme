"""Platinum spec values shared by the GTK 3 and GTK 4 sheet suites.

The two stylesheets implement the same Platinum control spec: one etched
separator, the same bevels and tab-state selectors, and the same base
``@define-color`` roles. Each suite still reads and asserts against its own
stylesheet; this module only holds the values both sheets must agree on.
The GTK 4 sheet extends :data:`BASE_DEFINED_COLOURS` with its own surface roles.
"""

from __future__ import annotations

from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    SELECTION,
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


class GtkRuleAssertions:
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
