"""Paths into the org.macos8.desktop theme packages, and its reference anchors.

Shared by the per-widget test modules and the package test module so each
names the artifact it checks without re-deriving the package layout. The
widget paths point into the desktop theme package; LNF_DEFAULTS is the global
theme's contents/defaults file, which selects that desktop theme. The
reference anchors name the screenshots and decode bounds several of those
modules share.
"""

from __future__ import annotations

import os

from support.theme_install import ROOT


DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktoptheme", DTHEME_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
PANEL_SVG = os.path.join(PACKAGE, "widgets", "panel-background.svg")
FRAME_SVG = os.path.join(PACKAGE, "widgets", "frame.svg")
BUTTON_SVG = os.path.join(PACKAGE, "widgets", "button.svg")
RADIOBUTTON_SVG = os.path.join(PACKAGE, "widgets", "radiobutton.svg")
CHECKMARKS_SVG = os.path.join(PACKAGE, "widgets", "checkmarks.svg")
LINEEDIT_SVG = os.path.join(PACKAGE, "widgets", "lineedit.svg")
LISTITEM_SVG = os.path.join(PACKAGE, "widgets", "listitem.svg")
VIEWITEM_SVG = os.path.join(PACKAGE, "widgets", "viewitem.svg")
MENUBARITEM_SVG = os.path.join(PACKAGE, "widgets", "menubaritem.svg")
TABBAR_SVG = os.path.join(PACKAGE, "widgets", "tabbar.svg")
SCROLLBAR_SVG = os.path.join(PACKAGE, "widgets", "scrollbar.svg")
SLIDER_SVG = os.path.join(PACKAGE, "widgets", "slider.svg")
SWITCH_SVG = os.path.join(PACKAGE, "widgets", "switch.svg")
BUSYWIDGET_SVG = os.path.join(PACKAGE, "widgets", "busywidget.svg")
ACTIONBUTTON_SVG = os.path.join(PACKAGE, "widgets", "actionbutton.svg")
ACTION_OVERLAYS_SVG = os.path.join(PACKAGE, "widgets", "action-overlays.svg")
BAR_METER_HORIZONTAL_SVG = os.path.join(
    PACKAGE, "widgets", "bar_meter_horizontal.svg"
)
BACKGROUND_SVG = os.path.join(PACKAGE, "widgets", "background.svg")
TRANSLUCENT_BACKGROUND_SVG = os.path.join(
    PACKAGE, "widgets", "translucentbackground.svg"
)
DIALOG_BACKGROUND_SVG = os.path.join(PACKAGE, "dialogs", "background.svg")
TOOLBAR_SVG = os.path.join(PACKAGE, "widgets", "toolbar.svg")
ARROWS_SVG = os.path.join(PACKAGE, "widgets", "arrows.svg")
LINE_SVG = os.path.join(PACKAGE, "widgets", "line.svg")
PLASMOIDHEADING_SVG = os.path.join(PACKAGE, "widgets", "plasmoidheading.svg")
TOOLTIP_SVG = os.path.join(PACKAGE, "widgets", "tooltip.svg")
SOLID_TOOLTIP_SVG = os.path.join(PACKAGE, "solid", "widgets", "tooltip.svg")
SOLID_PANEL_SVG = os.path.join(PACKAGE, "solid", "widgets", "panel-background.svg")

LNF_DEFAULTS = os.path.join(
    ROOT, "theme", "look-and-feel", DTHEME_ID, "contents", "defaults"
)

FANDOM_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "desktop_fandom.png"
)
# The four test classes that read desktop_fandom.png -- the Aurorae frame and
# the dialog, fill-gradient and tab-bar anchors -- share this bound so the
# reference cache decodes the screenshot once, not once per bound: the
# memory-meter gradient ends at row 1248, so 1250 rows covers every pixel any
# of them samples, and sharing the bound makes the single decode independent
# of discovery order.
FANDOM_MAX_ROWS = 1250

# The open Apple menu's Platinum body and the "Automated Tasks" submenu
# arrow. Every reader of this screenshot samples at or above row 300 (the
# color scheme's window-view anchor), so 301 rows covers them all and the
# reference cache decodes the screenshot once regardless of discovery order.
ARCHIVEORG_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png"
)
ARCHIVEORG_MAX_ROWS = 301

# The installer CD window's horizontal scroll bar. The deepest pixel any
# reader samples is the bar's bottom black rule at y=477, so 478 rows covers
# them all with a single cached decode.
SETUP_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "setup_emaculation.png"
)
SETUP_MAX_ROWS = 478

# The Setup Assistant's "Introduction" banner and its line-edit field. The
# deepest pixel any reader samples is the field's bottom border at y=351, so
# 352 rows covers them all with a single cached decode.
FIRSTBOOT_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "firstboot_betawiki.png"
)
FIRSTBOOT_MAX_ROWS = 352
