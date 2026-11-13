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


def make_session_home(
    case: unittest.TestCase,
) -> tuple[Path, Path, Path, Path, Path, dict[str, str]]:
    """Return (root, home, data, config, bin, env): a scratch session home.

    *root* is a fresh temp dir *case* removes when its test ends. ``home``
    and ``bin`` are created under it (the stub bin needs to exist before a
    tool run reaches PATH); *env* maps HOME, XDG_DATA_HOME, XDG_CONFIG_HOME
    and PATH onto the four paths, so a tool run with *env* reads and writes
    only inside the root. ``data`` and ``config`` are only paths: suites
    stage exactly what a case needs, and a suite may need the data home
    absent (a removal that must run without it) or populated (a lock that
    must be takeable there). The apply-cursor and apply-theme workflow and
    lock suites stage their homes through this helper.
    """
    root = make_tmp_dir(case)
    home = root / "home"
    home.mkdir()
    data = root / "data"
    config = root / "config"
    bin_dir = root / "bin"
    bin_dir.mkdir()
    env = {
        "HOME": str(home),
        "XDG_DATA_HOME": str(data),
        "XDG_CONFIG_HOME": str(config),
        "PATH": str(bin_dir),
    }
    return root, home, data, config, bin_dir, env


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
