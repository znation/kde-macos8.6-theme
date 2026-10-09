"""Shared path and parser loader for the color-scheme test modules.

``test_colorscheme``, ``test_colorscheme_reference`` and
``test_colorscheme_install`` all locate and parse
``theme/color-schemes/MacOS8.colors``; the path and the KDE-INI loader live
here once instead of in each module.
"""

import os

from kde_config import read as read_kde_config
from repo_root import ROOT

SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")


def load_scheme():
    return read_kde_config(SCHEME)
