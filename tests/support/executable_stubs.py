"""Write executable fake tools for tests that put stubs on PATH."""

from __future__ import annotations

import os
from pathlib import Path


def write_executable(path, text):
    """Write *text* verbatim to *path*, mark it 0755, and return the path.

    *text* keeps its own ``#!`` line, so a stub can be a shell script or
    any other interpreter the test needs.
    """
    path = Path(path)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def write_colorscheme_apply_ok(root, env=None):
    """Write the instant-success ``plasma-apply-colorscheme`` stub into *root*
    and return *env* (default: a copy of the process environment) with *root*
    prepended to its PATH.

    The render session applies the colorscheme through this tool, so the
    session suites stub it to succeed; tests that steer PATH narrowly use
    only the stub and build their own environment.
    """
    write_executable(root / "plasma-apply-colorscheme", "#!/bin/sh\nexit 0\n")
    environment = dict(env if env is not None else os.environ)
    environment["PATH"] = f"{root}:{environment['PATH']}"
    return environment
