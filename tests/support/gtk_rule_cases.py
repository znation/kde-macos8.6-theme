"""Reusable GTK and Firefox sheet rule assertions and shared control cases.

The two GTK sheet suites and the Firefox sheet suite each parse their own
stylesheet; these classes hold the rule assertion all three use and the
control rules the two GTK suites both satisfy. The Platinum spec values they
assert live in the sibling ``tests/support/gtk_theme_spec.py``.

:class:`SheetRuleAssertions` holds the rule assertion all three suites use.
:class:`GtkSheetRuleCases` holds the control rules the two GTK suites share.
GTK 3 and GTK 4 spell the same nodes differently, so the link, calendar,
infobar, progress-bar, level-bar, scale, switch, spin-button field,
menu-separator, menu-bar-title, frame, tree-header, expander-arrow,
submenu-arrow, text-selection, view-background, disabled-text, rubberband
and title-button assertions take
the suite's own selectors; the spinner assertion takes the rotation
transform instead, and the standalone separators and paned handles are
spelled alike in both, so their assertions take none.
"""

from __future__ import annotations

import re

from support import gtk_css
from support.colorscheme_fixtures import load_scheme
from support.desktoptheme_paths import MENUBARITEM_SVG
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CALENDAR_SELECTED_DAY,
    CHECK,
    CHECK_GLYPH,
    COMBO_ARROW,
    DISABLED_TEXT,
    ENTRY_FIELD,
    EXPANDER_COLLAPSED,
    EXPANDER_EXPANDED,
    FRAME,
    INFOBAR,
    INVERTED_BUTTON_BEVEL,
    LEVELBAR_TROUGH,
    LINK,
    LINK_BUTTON,
    LINK_TEXT,
    MENU_SEPARATOR,
    MIXED_GLYPH,
    PANED_HANDLE_HORIZONTAL,
    PANED_HANDLE_VERTICAL,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RADIO,
    RADIO_GLYPH,
    RAISED_BEVEL,
    ROW_HOVER,
    ROW_SELECTED,
    RUBBERBAND,
    SCALE_EMPTY_FILL,
    SCALE_THUMB,
    SCALE_TROUGH,
    SEPARATOR_HORIZONTAL,
    SEPARATOR_VERTICAL,
    SPINNER_RULES,
    SUBMENU_ARROW,
    SWITCH_GLYPH,
    SWITCH_THUMB,
    SWITCH_THUMB_DISABLED,
    SWITCH_TRACK,
    SWITCH_TRACK_CHECKED,
    SWITCH_TRACK_DISABLED,
    TAB_STATES,
    TEXT_SELECTION,
    TITLE_BUTTON,
    TOOLTIP,
    TOOLTIP_BACKGROUND,
    TREE_HEADER,
    TREE_HEADER_ACTIVE,
    TREE_HEADER_HOVER,
    TREE_HEADER_LAST,
    VIEW_BACKGROUND,
    VISITED_LINK,
    VISITED_TEXT,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
    hex_colour,
)
from support.svg_case import parse_svg
from svg_assertions import rect_geometry


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
    that owns them. GTK 3 and GTK 4 spell the same nodes differently, so the
    link, calendar, infobar, progress-bar, level-bar, scale, switch,
    spin-button field, menu-separator, menu-bar-title, frame, tree-header,
    expander-arrow, submenu-arrow, text-selection, view-background,
    disabled-text, rubberband and title-button assertions take the suite's
    own selectors; :meth:`assert_spinner` takes the rotation transform
    instead, and the standalone separators and paned handles are spelled
    alike in both, so ``assert_separators`` and ``assert_paned_handles``
    take none.
    """

    def assert_color_swatch_corners(self, overlay_suffix, extra_declarations=None):
        """Check square swatch rules using the suite's overlay relationship."""
        roots = (
            "colorswatch",
            "colorswatch.top",
            "colorswatch.bottom",
            "colorswatch.left",
            "colorswatch.right",
            "colorswatch:first-child:not(.top)",
            "colorswatch:last-child:not(.bottom)",
            "colorswatch#add-color-button",
            "colorswatch#add-color-button:only-child",
            "colorswatch#editor-color-sample",
        )
        expected = set(roots) | {root + overlay_suffix for root in roots}
        corner_selectors = expected.copy()
        extra_declarations = extra_declarations or {}
        expected.update(extra_declarations)
        self.assertEqual(
            {selector for selector in self.rules if "colorswatch" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                declarations = (
                    {"border-radius": "0"} if selector in corner_selectors else {}
                )
                declarations.update(extra_declarations.get(selector, {}))
                self.assertEqual(self.rules[selector], declarations)

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
                    "min-height": "22px",
                    "padding": "0 4px",
                },
            )
        self.assert_rule("headerbar", {"border-width": "0 0 1px 0"})
        for selector in ("headerbar:backdrop", ".titlebar:backdrop"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": INACTIVE_OUTLINE,
                    "box-shadow": "none",
                    "color": GREY,
                },
            )

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
        self.assert_rule("entry", ENTRY_FIELD)

    def test_check_and_radio(self):
        self.assert_rule("check", CHECK)
        self.assert_rule("radio", RADIO)
        self.assert_rule("check:checked", CHECK_GLYPH)
        self.assert_rule("radio:checked", RADIO_GLYPH)
        self.assert_rule("check:indeterminate", MIXED_GLYPH)
        self.assert_rule("radio:indeterminate", MIXED_GLYPH)

    def test_combobox_arrow(self):
        self.assert_rule("combobox arrow", COMBO_ARROW)

    def test_tooltip(self):
        self.assert_rule("tooltip", TOOLTIP)
        self.assert_rule("tooltip.background", TOOLTIP_BACKGROUND)

    def test_row_hover(self):
        for selector in ("treeview.view:hover", "list row.activatable:hover"):
            self.assert_rule(selector, ROW_HOVER)

    def test_row_selection(self):
        for selector in (
            "treeview.view:selected",
            "treeview.view:selected:hover",
            "list row.activatable:selected",
            "list row.activatable:selected:hover",
        ):
            self.assert_rule(selector, ROW_SELECTED)

    def test_row_selection_backdrop(self, selectors):
        for selector in selectors:
            self.assert_rule(selector, ROW_SELECTED)

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

    def assert_levelbar(self, trough, filled, empty, disabled, horizontal, vertical):
        """Assert the level bar paints as the progress bar, sized by its blocks."""
        self.assert_rule(trough, LEVELBAR_TROUGH)
        for prop in ("min-height", "min-width"):
            self.assertNotIn(prop, self.rules[trough])
        self.assert_rule(filled, PROGRESSBAR_PROGRESS)
        self.assert_rule(empty, SCALE_EMPTY_FILL)
        self.assert_rule(disabled, {"background-color": GREY})
        self.assert_rule(horizontal, {"min-height": "10px"})
        self.assert_rule(vertical, {"min-width": "10px"})

    def assert_spinner(self, transform):
        """Assert a running spinner rotates the icon theme's icon, a stopped one hides."""
        for selector, spec in SPINNER_RULES.items():
            self.assert_rule(selector, spec)
        # parse_css files a nested keyframe block under a bare ``to`` selector,
        # so the keyframe is checked against the raw text.
        self.assertRegex(
            gtk_css.strip_comments(self.css),
            r"@keyframes\s+spin\s*\{\s*to\s*\{\s*"
            + re.escape(transform)
            + r"\s*:\s*rotate\(1turn\)\s*;?\s*\}\s*\}",
        )

    def assert_separators(self):
        """Assert the etched standalone separators in both orientations."""
        for selector, spec in (
            ("separator.horizontal", SEPARATOR_HORIZONTAL),
            ("separator.vertical", SEPARATOR_VERTICAL),
        ):
            self.assert_rule(selector, spec)
            self.assertNotIn("margin", self.rules[selector])

    def assert_paned_handles(self):
        """Assert the etched paned split handles in both orientations."""
        self.assert_rule("paned.horizontal > separator", PANED_HANDLE_HORIZONTAL)
        self.assert_rule("paned.vertical > separator", PANED_HANDLE_VERTICAL)

    def assert_menu_separator(self, selectors):
        """Assert the Platinum etched menu separator against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, MENU_SEPARATOR)

    def assert_frame(self, selectors):
        """Assert the sunken frame bevel against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, FRAME)

    def assert_text_selection(self, selectors):
        """Assert the selected-text fill against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, TEXT_SELECTION)

    def assert_view_background(self, selectors):
        """Assert the white view fill against the view *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, VIEW_BACKGROUND)

    def assert_disabled_text(self, selectors):
        """Assert the inactive grey against *selectors*, and re-derive it."""
        for selector in selectors:
            self.assert_rule(selector, DISABLED_TEXT)
        self._assert_inactive_grey_from_scheme()

    def _assert_inactive_grey_from_scheme(self):
        rgb = load_scheme().get("Colors:Button", "ForegroundInactive")
        self.assertEqual(
            hex_colour([int(part) for part in rgb.split(",")]),
            DISABLED_TEXT["color"],
        )

    def assert_calendar(self, selected, other_month):
        """Assert the calendar's selected-day fill and other-month grey."""
        for selector in selected:
            self.assert_rule(selector, CALENDAR_SELECTED_DAY)
        for selector in other_month:
            self.assert_rule(selector, DISABLED_TEXT)
        self._assert_inactive_grey_from_scheme()

    def assert_links(self, button, link, visited, underline):
        """Assert faceless link buttons and the coloured link text.

        *button*, *link* and *visited* are selector tuples; *underline* is the
        toolkit's underline declaration. Both colours are re-derived from the
        colour scheme.
        """
        for selector in button:
            self.assert_rule(selector, LINK_BUTTON)
        for selector in link:
            self.assert_rule(selector, {**LINK_TEXT, **underline})
        for selector in visited:
            self.assert_rule(selector, VISITED_TEXT)
        scheme = load_scheme()
        for key, expected in (
            ("ForegroundLink", LINK),
            ("ForegroundVisited", VISITED_LINK),
        ):
            rgb = scheme.get("Colors:Window", key)
            self.assertEqual(
                hex_colour([int(part) for part in rgb.split(",")]), expected
            )

    def assert_rubberband(self, selectors):
        """Assert the dotted, unfilled marquee against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, RUBBERBAND)

    def assert_infobar(self, selectors):
        """Assert the menu-bar band's infobar paint against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, INFOBAR)

    def assert_spin_button_field(self, selectors):
        """Assert the entry field against the spin-button *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, ENTRY_FIELD)

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

    def assert_switch(self, slider, disabled_slider, glyph):
        """Assert the shared switch spec against this sheet's selectors."""
        self.assert_rule("switch", SWITCH_TRACK)
        self.assert_rule("switch:checked", SWITCH_TRACK_CHECKED)
        self.assert_rule("switch:disabled", SWITCH_TRACK_DISABLED)
        self.assert_rule(slider, SWITCH_THUMB)
        self.assert_rule(disabled_slider, SWITCH_THUMB_DISABLED)
        self.assert_rule(glyph, SWITCH_GLYPH)

    def assert_title_button(self, selector, asset):
        """Assert the Aurorae box in a 16px hit area with *asset* behind it."""
        self.assert_rule(selector, TITLE_BUTTON)
        self.assert_rule(
            selector, {"background-image": f'url("../assets/{asset}")'}
        )

    def assert_tree_header(self, selectors):
        """Assert the raised header face, its states and the last-column grid."""
        for selector in selectors:
            self.assert_rule(selector, TREE_HEADER)
            self.assert_rule(f"{selector}:hover", TREE_HEADER_HOVER)
            self.assert_rule(f"{selector}:active", TREE_HEADER_ACTIVE)
            self.assert_rule(f"{selector}:last-child", TREE_HEADER_LAST)

    def assert_expander_arrows(self, collapsed, expanded):
        """Assert the right (collapsed) and down (checked) disclosure arrows."""
        for selector in collapsed:
            self.assert_rule(selector, EXPANDER_COLLAPSED)
        for selector in expanded:
            self.assert_rule(selector, EXPANDER_EXPANDED)

    def assert_submenu_arrow(self, selectors, sized):
        """Assert the submenu arrow icon, and the 16px box when *sized*."""
        for selector in selectors:
            self.assert_rule(selector, SUBMENU_ARROW)
            if sized:
                self.assert_rule(
                    selector, {"min-width": "16px", "min-height": "16px"}
                )

    def assert_menubar_titles(self, selector):
        """Assert *selector* pads a title with the menubaritem SVG's margins."""
        geometry = rect_geometry(parse_svg(MENUBARITEM_SVG))
        top = geometry["normal-hint-top-margin"][3]
        left = geometry["normal-hint-left-margin"][2]
        self.assert_rule(selector, {"padding": f"{top}px {left}px"})
