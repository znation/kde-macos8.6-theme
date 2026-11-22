"""The temp-home cursor case shared by the ``apply_cursor`` suites.

``tests/test_apply_cursor.py`` drives the home and install workflow,
``tests/test_apply_cursor_selection.py`` drives the ``plasma-apply-cursortheme``
selector step, ``tests/test_apply_cursor_remove.py`` drives ``apply_cursor
--remove``, and ``tests/test_apply_cursor_locks.py`` mirrors this setUp for
its data-home lock arms. All four share the same temp home, data and config
homes, recording selector stub and installed-theme fixture, so the base lives
here once and no test module imports another. The module name does not match
``test*.py``, so ``unittest discover`` never collects it.
"""

from __future__ import annotations

import unittest

from support.cli_fixtures import run_main_with_env
from support.cursor_theme_fixtures import write_cursor_theme
from support.executable_stubs import write_executable
from support.recorded_lines import recorded_lines
from support.tmp_dir import make_session_home
from tools.cursor import link as cursor_link, selection as cursor_selection
from tools import apply_cursor


class CursorTestCase(unittest.TestCase):
    """Base with a temp home, data/config homes and a recording selector stub."""

    def setUp(self):
        self.root, self.home, self.data, self.config, self.bin, self.env = (
            make_session_home(self)
        )
        self.calls = self.root / "calls"
        self.installed = (
            self.data / "icons" / cursor_link.CURSOR_THEME
        )
        self.link = self.home / ".icons" / cursor_link.CURSOR_THEME

    def install_theme(self):
        """Write the installed theme's ``index.theme`` and ``cursors/left_ptr``."""
        write_cursor_theme(self.installed)

    def stub_selector(self, body="exit 0"):
        """Write a ``plasma-apply-cursortheme`` stub recording its argv."""
        path = self.bin / cursor_selection.SELECT_TOOL
        write_executable(
            path,
            "#!/bin/sh\n"
            f'printf \'%s\\n\' "$*" >> "{self.calls}"\n'
            f"{body}\n",
        )

    def run_tool(self, *args, env=None):
        return run_main_with_env(
            apply_cursor.main, "apply_cursor", args, env or self.env
        )

    def recorded(self):
        return recorded_lines(self.calls)
