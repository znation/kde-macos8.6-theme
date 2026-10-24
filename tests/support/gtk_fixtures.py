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
    "assets/arrow-down.svg",
    "assets/arrow-up.svg",
)
