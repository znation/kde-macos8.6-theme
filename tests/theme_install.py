"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`, so the install
tests in `test_colorscheme`, `test_lookandfeel` and `test_desktoptheme` pass a
throwaway `DESTDIR` and inspect the result there.
"""

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The data home inside each test's throwaway DESTDIR.
XDG_DATA_HOME = "/share"


def _run(target, destdir):
    return subprocess.run(
        ["make", target, f"DESTDIR={destdir}", f"XDG_DATA_HOME={XDG_DATA_HOME}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def install(destdir):
    """Run `make install` rooted at `destdir`; returns the CompletedProcess."""
    return _run("install", destdir)


def uninstall(destdir):
    """Run `make uninstall` rooted at `destdir`; returns the CompletedProcess."""
    return _run("uninstall", destdir)
