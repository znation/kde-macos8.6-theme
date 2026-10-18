"""Paths into the org.macos8.desktop theme packages.

Shared by the per-widget test modules and the package test module so each
names the artifact it checks without re-deriving the package layout. The
widget paths point into the desktop theme package; LNF_DEFAULTS is the global
theme's contents/defaults file, which selects that desktop theme.
"""

from __future__ import annotations

import os

from support.theme_install import ROOT


DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktop-themes", DTHEME_ID)
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
