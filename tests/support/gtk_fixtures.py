"""Shared paths and constants for the org.macos8.desktop GTK tests."""

from __future__ import annotations

import os

from support.repo_root import ROOT

GTK_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "gtk", GTK_ID)

SHIPPED_FILES = (
    "index.theme",
    "gtk-3.0/gtk.css",
    "gtk-4.0/gtk.css",
    "assets/checkmark.svg",
    "assets/bullet.svg",
    "assets/check-mixed.svg",
    "assets/arrow-down.svg",
    "assets/arrow-up.svg",
    "assets/arrow-right.svg",
    "assets/submenu-arrow.svg",
    "assets/window-close.svg",
    "assets/window-maximize.svg",
    "assets/window-minimize.svg",
)

# The url("...") forms the two shipped sheets reference the assets with:
# each sheet sits one directory below the package root, so every asset
# reference is a "../"-prefixed quoted path.
SHIPPED_ASSET_URLS = frozenset(
    f'"../{path}"' for path in SHIPPED_FILES if path.startswith("assets/")
)
