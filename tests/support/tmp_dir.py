"""Temp directories a test case removes when its test ends."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


def make_tmp_dir(case: unittest.TestCase) -> Path:
    """Return a fresh temp dir that *case* removes when its test ends."""
    tmp = tempfile.TemporaryDirectory()
    case.addCleanup(tmp.cleanup)
    return Path(tmp.name)


def make_config_home(case: unittest.TestCase) -> tuple[str, str]:
    """Return (tmp, config): a fresh scratch home and its config home.

    *tmp* is the scratch root the suites run the recipes from and *config* is
    the `<tmp>/config` path their `XDG_CONFIG_HOME` is pointed at; neither is
    created eagerly — the suites stage exactly the files and directories a
    case needs. All of the `_uninstall` diagnostic suites and their sibling
    uninstall cases stage their config homes through this helper.
    """
    tmp = make_tmp_dir(case)
    return str(tmp), os.path.join(str(tmp), "config")
