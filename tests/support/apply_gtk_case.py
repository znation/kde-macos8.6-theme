"""The temp-root GTK apply case shared by the ``apply_gtk`` suites.

``tests/test_apply_gtk.py`` drives the apply and removal workflow,
``tests/test_apply_gtk_errors.py`` plants unreadable and unwritable config
faults and ``tests/test_apply_gtk_locks.py`` holds the serialization locks;
all three need the same scratch root, temp ``XDG_DATA_HOME``/
``XDG_CONFIG_HOME``/``HOME`` and installed-sheet fixtures. They live here
once so each suite states only the behaviour it pins. The module name does
not match ``test*.py``, so ``unittest discover`` never collects it.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root
from support import snippet_child
from support.cli_fixtures import run_main
from support.tmp_dir import make_tmp_dir
from tools import apply_gtk


class ApplyGtkTestCase(unittest.TestCase):
    """Base with a temp data/config/home root and an installed GTK 4 sheet."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.data = self.root / "data"
        self.config = self.root / "config"
        self.home = self.root / "home"
        self.sheet = (
            self.data / "themes" / apply_gtk.GTK_ID / "gtk-4.0" / "gtk.css"
        )
        self.env = {
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "HOME": str(self.home),
        }

    def run_tool(self, *args):
        with mock.patch.dict(os.environ, self.env, clear=True):
            return run_main(apply_gtk.main, "apply_gtk", args)

    def run_tool_in_child(self, *args):
        """Run the tool in a child so a FIFO open that slips through times out.

        ``run_tool`` cannot bound a blocking ``open``: if the guard regresses,
        the call hangs the whole check instead of failing this test. The child
        inherits ``self.env`` and is killed at the timeout, like the suite's
        other FIFO guards.
        """
        snippet = (
            "import sys; from tools.apply_gtk import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        with mock.patch.dict(os.environ, self.env, clear=True):
            return snippet_child.run(
                [snippet, *args], cwd=repo_root.ROOT, timeout=10
            )

    def install_sheet(self, *versions):
        """Write the installed sheet for each *versions* (both by default)."""
        for version in versions or ("gtk-3.0", "gtk-4.0"):
            sheet = self.data / "themes" / apply_gtk.GTK_ID / version / "gtk.css"
            sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.write_text("/* installed sheet */\n", encoding="utf-8")

    def settings(self, version):
        return self.config / version / "settings.ini"

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_bytes(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
