"""Shared paths and constants for the org.macos8.desktop Kvantum tests.

The package directory, the `.kvconfig` and `.svg` paths, the color scheme the
palette is grounded in, and the two files the package ships. The
`test_kvantum_*` modules each cover one concern of the Kvantum widget style,
and `support.kvantum_config_spec` builds its pin tables from the same paths;
all import what they share from here.
"""

from __future__ import annotations

import os

from support.repo_root import ROOT

KVANTUM_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "kvantum", KVANTUM_ID)
KVCONFIG = os.path.join(PACKAGE, KVANTUM_ID + ".kvconfig")
SVG = os.path.join(PACKAGE, KVANTUM_ID + ".svg")
COLOR_SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

# The About This Computer screenshot (an 8.6a3c2 beta build) whose System Info
# "Show:" popup draws the combo box's double up/down arrow. Its deepest
# sampled row is y117, the cell's bottom face row.
SYSTEMINFO_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "systeminfo_betawiki.png"
)
SYSTEMINFO_MAX_ROWS = 118

SHIPPED_FILES = (KVANTUM_ID + ".kvconfig", KVANTUM_ID + ".svg")
