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

# The exact hex set the two GTK stylesheets may paint: the pinned Platinum
# palette values plus the two link inks. The suites
# tests/test_gtk_theme.py and tests/test_gtk4_theme.py assert their parsed
# sheet against this one frozenset through test_only_palette_hex_literals,
# so any other hex literal in either sheet fails both; the Firefox sheets'
# palettes differ and still name their own smaller sets there.
SHEET_PALETTE = frozenset(
    {
        BLACK,
        WHITE,
        GREY,
        FACE,
        BUTTON_SHADOW,
        TROUGH,
        SELECTION,
        ETCH_DARK,
        LINK,
        VISITED_LINK,
        TOOLTIP_FACE,
        INACTIVE_OUTLINE,
    }
)

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
# The raised bevel with the highlight and shadow halves swapped: the pressed
# arm of the GTK 4 spinbutton steppers (the sheet's own box-shadow, pinned
# byte-equal in theme/gtk/src/gtk-4.0/010-spinbutton.css).
INVERTED_RAISED_BEVEL = f"inset 1px 1px {GREY}, inset -1px -1px {WHITE}"
BUTTON_BEVEL = f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW}"
INVERTED_BUTTON_BEVEL = f"inset 1px 1px {BUTTON_SHADOW}, inset -1px -1px {WHITE}"

# The OSD push-button recipe the sheets restate across their overlay
# families: the raised push-button face (square, 1px black border,
# ``BUTTON_BEVEL``, black label) the osd-scoped ``button``, ``button.flat``
# and action-class arms all draw. The GTK 3 suites go through
# ``osd_button_arms``; ``test_gtk4_scale`` pins its scale-popup arm with the
# constant alone.
OSD_BUTTON_RECIPE = {
    "background-color": FACE,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": BUTTON_BEVEL,
    "color": BLACK,
    "outline-color": BLACK,
    "text-shadow": "none",
    "-gtk-icon-shadow": "none",
}


# The GTK 4 spinbutton stepper recipe: the same raised push-button face
# ``OSD_BUTTON_RECIPE`` holds, but with the GTK 4 sheet's ``RAISED_BEVEL``
# etch in the place where the GTK 3 sheet's OSD families carry
# ``BUTTON_BEVEL`` (theme/gtk/src/gtk-4.0/010-spinbutton.css paints
# inset 1px 1px #FFFFFF, inset -1px -1px #999999). The suites
# ``tests/test_gtk4_spinbutton`` and ``tests/test_gtk4_osd`` pin its
# restatements through ``spinbutton_stepper_arms``.
SPINBUTTON_STEPPER_RECIPE = {
    **OSD_BUTTON_RECIPE,
    "box-shadow": RAISED_BEVEL,
}


def spinbutton_stepper_arms():
    """Return the GTK 4 spinbutton stepper's (resting, active, disabled) arms.

    The resting arm is :data:`SPINBUTTON_STEPPER_RECIPE`; the active arm
    swaps only the box-shadow to :data:`INVERTED_RAISED_BEVEL`; the disabled
    arm keeps the raised bevel with the Inactive grey (``ETCH_DARK``) and no
    ``outline-color``, like the disabled OSD button arm. Returns fresh
    dicts, so a suite may trim or extend its own copy without touching the
    shared recipe.

    Called by the two GTK 4 sheet suites that pin its restatements:
    ``tests/test_gtk4_spinbutton`` (the seven plain horizontal stepper
    arms) and ``tests/test_gtk4_osd`` (the ten ``.osd`` stepper arms, whose
    vertical members add the stock ``background-clip: border-box``
    clearance in that suite).
    """
    base = dict(SPINBUTTON_STEPPER_RECIPE)
    active = {**base, "box-shadow": INVERTED_RAISED_BEVEL}
    disabled = {**base, "color": ETCH_DARK}
    del disabled["outline-color"]
    return base, active, disabled


def osd_button_arms(clip=False):
    """Return the OSD button's (resting, active, disabled) declarations.

    The resting arm is :data:`OSD_BUTTON_RECIPE`, plus
    ``background-clip: border-box`` when *clip* (the stock
    destructive/suggested-action arms carry it); the active arm swaps only
    the box-shadow to ``INVERTED_BUTTON_BEVEL``; the disabled arm keeps
    ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
    ``outline-color``. Returns fresh dicts, so a suite may trim or extend
    its own copy without touching the shared recipe.

    Called by the six GTK 3 sheet suites that pin its restatements: the
    five OSD rule families ``test_gtk_theme_osd_buttons``,
    ``test_gtk_theme_osd_flat`` and ``test_gtk_theme_osd_fields`` without
    *clip*, ``test_gtk_theme_osd_destructive`` and
    ``test_gtk_theme_osd_suggested`` with ``clip=True``, and
    ``test_gtk_theme_infobar`` without *clip* (its untyped bar-button
    family restates the same face the ``.app-notification`` and ``.osd``
    button groups pin). The non-OSD suites restate their own
    ``border-color``-spelled faces and stay local.
    """
    base = dict(OSD_BUTTON_RECIPE)
    if clip:
        base["background-clip"] = "border-box"
    active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
    disabled = {**base, "color": ETCH_DARK}
    del disabled["outline-color"]
    return base, active, disabled


# The plain push-button face the GTK 3 sheet's colour-class and flat button
# families restate: the raised face in the ``border-color`` spelling (no full
# border, no radius — the stock rules those families extend own those),
# ``BUTTON_BEVEL`` and the black label with its cleared emboss.
BUTTON_FACE_RECIPE = {
    "background-color": FACE,
    "background-image": "none",
    "border-color": BLACK,
    "box-shadow": BUTTON_BEVEL,
    "color": BLACK,
    "outline-color": BLACK,
    "text-shadow": "none",
    "-gtk-icon-shadow": "none",
}


def button_arms(background_everywhere=False, transition=False):
    """Return the push button's (raised, sunken, disabled) restatements.

    The raised arm is :data:`BUTTON_FACE_RECIPE`, plus ``transition: none``
    when *transition* (the stock flat family's motion clearance); the sunken
    arm swaps only the box-shadow to :data:`INVERTED_BUTTON_BEVEL`; the
    disabled arm keeps :data:`BUTTON_BEVEL` with the Inactive grey
    (``DISABLED_TEXT``). The stock transparent faces the ``.flat`` families
    overlay force the ``background-color`` claim on every arm; pass
    *background_everywhere* to add it to the sunken and disabled arms (the
    raised arm always carries it). Returns fresh dicts, so a suite may trim
    or extend its own copy without touching the shared recipe.

    Called by the three families of ``tests/test_gtk_theme_buttons`` that
    pin the colour-class and flat restatements: the plain action arms with
    neither flag, the ``button.flat`` arms with both flags, and the
    colour-class ``.flat`` arms with *background_everywhere* only. The
    arrow and menu-arrow faces extend this recipe with per-widget keys
    (``tests/test_gtk_theme_notebook``, ``tests/test_gtk_theme_menu``) and
    keep their own copies.
    """
    base = dict(BUTTON_FACE_RECIPE)
    if transition:
        base["transition"] = "none"
    # The sunken arm derives from the recipe, not from *base*: the flat
    # families clear the stock motion claims on the raised arms alone, and
    # their sunken arms carry no `transition`.
    sunken = {**BUTTON_FACE_RECIPE, "box-shadow": INVERTED_BUTTON_BEVEL}
    del sunken["background-color"]
    disabled = {
        "background-image": "none",
        "border-color": BLACK,
        "box-shadow": BUTTON_BEVEL,
        "color": DISABLED_TEXT["color"],
    }
    if background_everywhere:
        sunken["background-color"] = FACE
        disabled["background-color"] = FACE
    return base, sunken, disabled


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
TITLE_BUTTON_ASSETS = (
    ("close", "window-close.svg"),
    ("maximize", "window-maximize.svg"),
    ("minimize", "window-minimize.svg"),
)
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

# The eight selection-check states the content-view check families rest,
# shared by the GTK 3 and GTK 4 suites: the empty suffix plus the seven
# state arms the sheets append. Exactly four tests read it --
# test_tile_check_faces in tests/test_gtk4_tile_checks.py and
# test_iconview_selected_arms in tests/test_gtk4_selection_focus.py,
# test_iconview_selected_arms in tests/test_gtk_theme_selected_views.py and
# test_vertical_stepper_and_content_view_check_corners in
# tests/test_gtk_theme_stepper_check_corners.py.
SELECTION_CHECK_STATES = (
    "",
    ":hover",
    ":active",
    ":backdrop",
    ":checked",
    ":checked:hover",
    ":checked:active",
    ":backdrop:checked",
)

# The content-view tile-check face both suites pin: the existing check
# face's raised etched field at the tile record's zero radius. Exactly two
# tests read it -- test_tile_check_faces in tests/test_gtk4_tile_checks.py and
# test_vertical_stepper_and_content_view_check_corners in
# tests/test_gtk_theme_stepper_check_corners.py.
TILE_CHECK_FACE = {
    "background-color": FACE,
    "background-image": "none",
    "border": f"1px solid {BLACK}",
    "border-radius": "0",
    "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {ETCH_DARK}",
}

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
