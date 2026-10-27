"""Platinum spec values shared by the GTK 3, GTK 4 and Firefox sheet suites.

The two GTK stylesheets implement the same Platinum control spec: one etched
separator, the same bevels and tab-state selectors, and the same base
``@define-color`` roles. Each sheet suite still reads and asserts against its
own stylesheet; this module only holds the values the sheets must agree on.
The Firefox sheet takes :data:`ETCH_DARK` for its etched separators. The GTK 4
sheet extends :data:`BASE_DEFINED_COLOURS` with its own surface roles. The
assertion classes that read these values live in the sibling
``tests/support/gtk_rule_cases.py``.
"""

from __future__ import annotations

from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
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

# An infobar draws the menu-bar band's face and etched bottom rule. No
# reference screenshot shows a GTK infobar; the GTK-required type class names
# take no per-type colour, so all four message types use this one band.
INFOBAR = {
    "background-color": FACE,
    "color": BLACK,
    "border-bottom": f"1px solid {ETCH_DARK}",
    "box-shadow": f"inset 0 -1px {WHITE}",
}
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
MIXED_GLYPH = {"-gtk-icon-source": 'url("../assets/check-mixed.svg")'}

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
