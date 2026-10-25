"""Platinum spec values shared by the GTK 3, GTK 4 and Firefox sheet suites.

The two GTK stylesheets implement the same Platinum control spec: one etched
separator, the same bevels and tab-state selectors, and the same base
``@define-color`` roles. Each sheet suite still reads and asserts against its
own stylesheet; this module only holds the values the sheets must agree on.
The Firefox sheet takes :data:`ETCH_DARK` for its etched separators. The GTK 4
sheet extends :data:`BASE_DEFINED_COLOURS` with its own surface roles.
:class:`SheetRuleAssertions` holds the rule assertion all three suites use.
:class:`GtkSheetRuleCases` holds the control rules the two GTK suites share,
plus the link, calendar, progress-bar, level-bar, scale, switch, paned-handle,
spin-button field, menu-separator, frame, expander-arrow, submenu-arrow and spinner
assertions they name with their own selectors.
"""

from __future__ import annotations

import re

from support import gtk_css
from support.colorscheme_fixtures import load_scheme
from support.desktoptheme_paths import MENUBARITEM_SVG
from support.svg_case import parse_svg
from svg_assertions import rect_geometry
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    hex_colour,
    INACTIVE_OUTLINE,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    WHITE,
)

# The etched separator's dark half, pinned to the reference by
# tests/test_desktoptheme_line.py's DARK value.
ETCH_DARK = "#888888"

# Link text: the colour scheme's Window ForegroundLink and ForegroundVisited
# roles (Kvantum's link.color and link.visited.color too); assert_links
# re-derives both.
LINK = "#0000EE"
VISITED_LINK = "#551A8B"

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
# GTK 3 paints an entry's progress node over the whole field and ignores its
# min-height, so the strip is the node's 2px bottom border (Adwaita's stock
# thickness) in the progress-bar selection fill, over a transparent face.
ENTRY_PROGRESS = {
    "background-color": "transparent",
    "background-image": "none",
    "border-color": "#CCCCFF",
    "border-radius": "0",
    "border-style": "solid",
    "border-width": "0 0 2px",
    "box-shadow": "none",
    "margin": "0",
}
# GTK 4 sizes the strip through its trough, so the fill keeps min-height.
ENTRY_PROGRESS_GTK4 = {**PROGRESSBAR_PROGRESS, "min-height": "2px"}
SCALE_TROUGH = {**PROGRESSBAR_TROUGH, "min-height": "6px", "min-width": "6px"}
SCALE_EMPTY_FILL = {
    "background-color": "transparent",
    "background-image": "none",
    "border": "0",
    "border-radius": "0",
    "box-shadow": "none",
    "margin": "0",
}
# A level bar reuses the progress trough; its blocks, not the trough, set the size.
LEVELBAR_TROUGH = {
    **{k: v for k, v in PROGRESSBAR_TROUGH.items() if k not in ("min-height", "min-width")},
    "padding": "0",
}
SCALE_THUMB = {
    "background-color": FACE,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": RAISED_BEVEL,
}

# The switch reuses the desktop theme's widgets/switch.svg faces (pinned by
# tests/test_desktoptheme_switch.py): a flat #EEEEEE trough, a flat white
# active field and the raised thumb, with the I/O glyphs hidden.
SWITCH_TRACK = {
    "background-color": TROUGH,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": "none",
    "min-width": "30px",
    "min-height": "16px",
}
SWITCH_TRACK_CHECKED = {"background-color": WHITE, "background-image": "none"}
SWITCH_TRACK_DISABLED = {"border-color": GREY}
SWITCH_THUMB = {
    **SCALE_THUMB,
    "margin": "-1px",
    "min-width": "12px",
    "min-height": "16px",
}
SWITCH_THUMB_DISABLED = {
    "background-color": FACE,
    "border": f"1px solid {GREY}",
    "box-shadow": "none",
}
SWITCH_GLYPH = {"color": "transparent"}

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

# The reference's etched rule from widgets/line.svg, in both orientations. The
# horizontal one declares no margin so the menu separator's margin stays in force.
SEPARATOR_HORIZONTAL = {
    "background-color": ETCH_DARK,
    "border": "0",
    "border-bottom": f"1px solid {WHITE}",
    "min-height": "1px",
    "padding": "0",
}
SEPARATOR_VERTICAL = {
    "background-color": ETCH_DARK,
    "border": "0",
    "border-right": f"1px solid {WHITE}",
    "min-width": "1px",
    "padding": "0",
}

# A horizontal paned (side-by-side panes) has a vertical handle, so it takes the
# vertical rule; a vertical paned takes the horizontal one. Both reuse the
# reference etch, and drop stock's builtin handle image.
PANED_HANDLE_HORIZONTAL = {**SEPARATOR_VERTICAL, "-gtk-icon-source": "none", "margin": "0"}
PANED_HANDLE_VERTICAL = {**SEPARATOR_HORIZONTAL, "-gtk-icon-source": "none", "margin": "0"}

FRAME = {
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": f"inset 1px 1px {GREY}",
    "margin": "0",
    "padding": "0",
}

# The GTK 3 scroll-bar steppers paint the reference's arrow box: the
# installer CD window's horizontal bar shows a 14px trough face inside the
# bar's 1px black border, with a 1px #555555 divider on the edge facing the
# trough, so the visible box is 16x16. The shipped up/down triangles rotate a
# quarter turn on a horizontal bar.
SCROLLBAR_STEPPER = {
    "background-color": TROUGH,
    "background-image": "none",
    "border": "0",
    "border-radius": "0",
    "box-shadow": "none",
    "min-height": "14px",
    "min-width": "14px",
    "padding": "0",
}
SCROLLBAR_STEPPER_ACTIVE = {
    "background-color": TROUGH,
    "box-shadow": (
        f"inset 1px 1px {BUTTON_SHADOW}, inset -1px -1px {WHITE}"
    ),
}
SCROLLBAR_STEPPER_ARROWS = {
    "scrollbar.vertical button.up": {
        "-gtk-icon-source": 'url("../assets/arrow-up.svg")',
        "border-bottom": f"1px solid {INACTIVE_OUTLINE}",
    },
    "scrollbar.vertical button.down": {
        "-gtk-icon-source": 'url("../assets/arrow-down.svg")',
        "border-top": f"1px solid {INACTIVE_OUTLINE}",
    },
    "scrollbar.horizontal button.up": {
        "-gtk-icon-source": 'url("../assets/arrow-up.svg")',
        "-gtk-icon-transform": "rotate(-0.25turn)",
        "border-right": f"1px solid {INACTIVE_OUTLINE}",
    },
    "scrollbar.horizontal button.down": {
        "-gtk-icon-source": 'url("../assets/arrow-down.svg")',
        "-gtk-icon-transform": "rotate(-0.25turn)",
        "border-left": f"1px solid {INACTIVE_OUTLINE}",
    },
}

# Both sheets paint the title-bar controls as the reference-grounded Aurorae
# box in a 16px hit area, with the toolkit glyph hidden. assert_title_button
# adds the control's own asset URL.
TITLE_BUTTON = {
    "background-color": "transparent",
    "background-position": "center",
    "background-repeat": "no-repeat",
    "background-size": "13px 13px",
    "border": "0",
    "border-radius": "0",
    "box-shadow": "none",
    "margin": "0",
    "min-height": "16px",
    "min-width": "16px",
    "padding": "0",
    "-gtk-icon-source": "none",
}
TITLE_BUTTON_IMAGE = {
    "background-color": "transparent",
    "color": "transparent",
    "min-height": "16px",
    "min-width": "16px",
}
# GTK 4's default sheet gives the image a circular background on these states,
# so each needs its own transparent rule to outrank that default.
TITLE_BUTTON_IMAGE_STATE = {"background-color": "transparent"}

# The tree-view and column-view header faces both sheets paint as the raised
# Platinum push button, with one black line between columns and under the row.
TREE_HEADER = {
    "background-color": FACE,
    "background-image": "none",
    "color": BLACK,
    "text-shadow": "none",
    "border-width": "0 1px 1px 0",
    "border-style": "solid",
    "border-color": BLACK,
    "border-radius": "0",
    "box-shadow": BUTTON_BEVEL,
}
TREE_HEADER_HOVER = {
    "background-color": FACE,
    "color": BLACK,
    "text-shadow": "none",
    "box-shadow": BUTTON_BEVEL,
}
TREE_HEADER_ACTIVE = {
    "color": BLACK,
    "text-shadow": "none",
    "box-shadow": INVERTED_BUTTON_BEVEL,
}
# The last column shares the header's bottom line but ends the row's grid.
TREE_HEADER_LAST = {"border-right-width": "0"}
EXPANDER_COLLAPSED = {
    "min-width": "16px",
    "min-height": "16px",
    "-gtk-icon-source": 'url("../assets/arrow-right.svg")',
}
EXPANDER_EXPANDED = {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}
SUBMENU_ARROW = {"-gtk-icon-source": 'url("../assets/submenu-arrow.svg")'}

# The list and tree rows both sheets paint, adapted from the reference-grounded
# widgets/listitem.svg row: a hovered row stays the view background and a
# selected row is the flat selection fill with square corners and black text.
ROW_HOVER = {"background-color": "transparent"}
# Views paint the white content field with black text; the white is the colour
# scheme's View background that
# test_colorscheme_reference.TestReferenceAnchors.test_window_view_background
# re-derives from the reference.
VIEW_BACKGROUND = {"background-color": WHITE, "color": BLACK}

# An insensitive widget's label and entry text: the colour scheme's
# ForegroundInactive grey, which assert_disabled_text re-derives.
DISABLED_TEXT = {"color": ETCH_DARK}

# A link button draws no face; link and visited link text take the scheme's
# link colours. The underline property differs per toolkit, so it is passed
# to assert_links.
LINK_BUTTON = {
    "background-color": "transparent",
    "background-image": "none",
    "border-color": "transparent",
    "box-shadow": "none",
}
LINK_TEXT = {"color": LINK}
VISITED_TEXT = {"color": VISITED_LINK}

# The drag-selection marquee: a dotted outline with no fill, after the Mac OS
# Finder marquee.
RUBBERBAND = {"background-color": "transparent", "border": f"1px dotted {BLACK}"}
ROW_SELECTED = {
    "background-color": SELECTION,
    "color": BLACK,
    "border-radius": "0",
}

# Selected text in entries, labels and text views reuses the row selection
# fill. The colour stays black: GTK draws the selected glyphs again in this
# node's colour, so a transparent colour would hide them.
TEXT_SELECTION = {"background-color": SELECTION, "color": BLACK}

# A calendar's selected day reuses the row selection fill.
CALENDAR_SELECTED_DAY = {"background-color": SELECTION, "color": BLACK}

# The text field both sheets paint on ``entry`` and on a spin button's field.
ENTRY_FIELD = {
    "background-color": WHITE,
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": f"inset 1px 1px {GREY}",
    "color": BLACK,
}

# The check box and radio faces both sheets paint. The box reuses the
# reference-grounded Kvantum check face; the radio's flat white face matches
# widgets/radiobutton.svg.
CHECK_RADIO = {
    "min-height": "14px",
    "min-width": "14px",
    "margin": "0 4px",
    "background-color": FACE,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {ETCH_DARK}",
}
CHECK = {**CHECK_RADIO, "border-radius": "0"}
RADIO = {
    **CHECK_RADIO,
    "background-color": WHITE,
    "border-radius": "50%",
    "box-shadow": "none",
}
CHECK_GLYPH = {"-gtk-icon-source": 'url("../assets/checkmark.svg")'}
RADIO_GLYPH = {"-gtk-icon-source": 'url("../assets/bullet.svg")'}

# The combo box dropdown arrow both sheets paint from the desktop theme's
# pinned down-arrow triangle, sized to the installed default sheet's 16px.
COMBO_ARROW = {
    "-gtk-icon-source": 'url("../assets/arrow-down.svg")',
    "min-height": "16px",
    "min-width": "16px",
}

# A menu button's down and up arrows reuse the shipped combo box triangles.
MENUBUTTON_ARROWS = {
    "menubutton arrow.down": {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'},
    "menubutton arrow.up": {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'},
}

# A menu item's check box shows the bare glyph, not the raised content face.
MENU_CHECK = {
    "margin": "0",
    "background-color": "transparent",
    "border-color": "transparent",
    "box-shadow": "none",
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

SPINNER_RULES = {
    "spinner": {
        "background": "none",
        "opacity": "0",
        "-gtk-icon-source": '-gtk-icontheme("process-working-symbolic")',
    },
    "spinner:checked": {
        "opacity": "1",
        "animation": "spin 1s linear infinite",
    },
    "spinner:checked:disabled": {"opacity": "0.5"},
}


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
    that owns them. The progress-bar, scale, switch, menu-separator, frame,
    text-selection, view-background, disabled-text and calendar assertions take the suite's own selectors, since GTK 3 and GTK 4 spell the
    same nodes differently. The standalone separators are spelled alike in both,
    so ``assert_separators`` takes no selectors.
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
