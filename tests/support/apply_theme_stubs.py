"""The shell-stub base case shared by the ``apply_theme`` suites.

``tests/test_apply_theme.py`` runs ``apply_theme.main`` against fake tools on
``PATH``, and ``tests/test_apply_optional_helpers.py`` drives the Kvantum
data-home note through the same stubs. Both need the same narrowed ``PATH``,
temp ``HOME``/``XDG_CONFIG_HOME``/``XDG_DATA_HOME`` and stub writers, so the
base lives here once. The module name does not match ``test*.py``, so
``unittest discover`` never collects it.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.recorded_lines import recorded_lines
from tools import apply_theme


class ApplyStubTestCase(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools.

    `PATH` is narrowed to the stub directory, so a `qdbus6` installed on the
    host cannot be picked up and the fallback can be exercised. Each stub is a
    POSIX shell script that appends its own argv and the session bus address it
    inherited to two files in the test's temp dir.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="apply-theme-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        # The apply holds the flock on the data home its selection reads, so
        # the data home is a temp directory, never the caller's real one.
        self.data = self.root / "data"
        self.data.mkdir(parents=True)
        self.calls = self.root / "calls"
        self.env_log = self.root / "env"
        for name in apply_theme.REQUIRED_TOOLS:
            self.stub(name)
        self.stub("qdbus6")
        self.stub("kvantummanager")
        # The config home is pinned too: an inherited XDG_CONFIG_HOME (a CI
        # runner exports one) would otherwise send the konsolerc commands to
        # the host's real config directory instead of ``$HOME/.config``.
        patch = mock.patch.dict(
            os.environ,
            {
                "PATH": str(self.bin),
                "HOME": str(self.home),
                "XDG_CONFIG_HOME": str(self.home / ".config"),
                "XDG_DATA_HOME": str(self.data),
            },
        )
        patch.start()
        self.addCleanup(patch.stop)

    def stub(self, name, body="exit 0"):
        """Write an executable *name* that records its argv, then runs *body*."""
        path = self.bin / name
        path.write_text(
            "#!/bin/sh\n"
            "name=${0##*/}\n"
            f'printf \'%s %s\\n\' "$name" "$*" >> "{self.calls}"\n'
            f'printf \'%s DBUS=%s\\n\' "$name" "${{DBUS_SESSION_BUS_ADDRESS-}}"'
            f' >> "{self.env_log}"\n'
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def unstub(self, name):
        """Remove the stub script named *name* from the stub bin."""
        (self.bin / name).unlink()

    def broken_stub(self, name):
        """Make *name* executable but unable to start.

        ``shutil.which`` finds it, so the missing-tool check passes, but the
        kernel cannot exec a script whose interpreter does not exist; Popen
        raises ``OSError``. This is the fault a corrupt binary or a broken
        shell script presents.
        """
        path = self.bin / name
        path.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def recorded(self):
        """Return the ``"<name> <argv>"`` lines the stubs appended, in order."""
        return recorded_lines(self.calls)

    def env_recorded(self):
        """Return the ``"<name> DBUS=<address>"`` lines the stubs appended."""
        return recorded_lines(self.env_log)
