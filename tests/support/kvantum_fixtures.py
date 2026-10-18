"""Shared paths and constants for the org.macos8.desktop Kvantum tests.

The package directory, the `.kvconfig` and `.svg` paths, the color scheme the
palette is grounded in, and the two files the package ships. The
`test_kvantum_*` modules each cover one concern of the Kvantum widget style and
import what they share from here.
"""

from __future__ import annotations

import os

from support.theme_install import ROOT

KVANTUM_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "kvantum", KVANTUM_ID)
KVCONFIG = os.path.join(PACKAGE, KVANTUM_ID + ".kvconfig")
SVG = os.path.join(PACKAGE, KVANTUM_ID + ".svg")
COLOR_SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

SHIPPED_FILES = (KVANTUM_ID + ".kvconfig", KVANTUM_ID + ".svg")
