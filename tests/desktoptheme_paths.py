"""Paths into the org.macos8.desktop theme packages.

Shared by the per-widget test modules and the package test module so each
names the artifact it checks without re-deriving the package layout. The
widget paths point into the desktop theme package; LNF_DEFAULTS is the global
theme's contents/defaults file, which selects that desktop theme.
"""

from __future__ import annotations

import os

from theme_install import ROOT


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
SCROLLBAR_SVG = os.path.join(PACKAGE, "widgets", "scrollbar.svg")
BACKGROUND_SVG = os.path.join(PACKAGE, "widgets", "background.svg")
DIALOG_BACKGROUND_SVG = os.path.join(PACKAGE, "dialogs", "background.svg")


LNF_DEFAULTS = os.path.join(
    ROOT, "theme", "look-and-feel", DTHEME_ID, "contents", "defaults"
)
