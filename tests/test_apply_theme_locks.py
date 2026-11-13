"""Tests for the data-home lock of ``apply_theme``.

An apply holds the data-home flock ``make install``/``make uninstall`` hold
(the Makefile's ``run_locked``) across its re-selection steps, so a concurrent
uninstall cannot remove the installed packages between the
``lookandfeeltool``/``plasma-apply-*`` selections and leave a selection that
silently falls back with no diagnostic. The workflow, fault and stub cases live
in ``tests/test_apply_theme.py``; the case base mirrors its ``StubTools``
setUp.
"""

from __future__ import annotations

import shlex
import stat
import sys
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main_with_env
from support.flock_fixtures import assert_directory_flock_free, hold_directory_flock
from support.process_assertions import (
    assert_failed,
    assert_lock_time_out,
    assert_succeeded,
)
from support.tmp_dir import make_tmp_dir
from tools import apply_theme


class ThemeLockCase(unittest.TestCase):
    """Base with a temp home, data home and stubbed selection tools."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data = self.root / "data"
        # The lock is taken on the data home, so it must exist when the apply
        # runs; ``make install`` creates it before this script runs.
        self.data.mkdir(parents=True)
        self.config = self.root / "config"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.calls = self.root / "calls"
        for name in apply_theme.REQUIRED_TOOLS:
            self.stub(name)
        self.stub("qdbus6")
        self.stub("kvantummanager")
        self.env = {
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "PATH": str(self.bin),
        }

    def stub(self, name, body="exit 0"):
        """Write an executable *name* that records its argv, then runs *body*."""
        path = self.bin / name
        path.write_text(
            "#!/bin/sh\n"
            "name=${0##*/}\n"
            f'printf \'%s %s\\n\' "$name" "$*" >> "{self.calls}"\n'
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_tool(self):
        return run_main_with_env(apply_theme.main, "apply_theme", [], self.env)

    def hold_data_lock(self):
        """Take the data-home lock a concurrent install or uninstall holds."""
        hold_directory_flock(self, self.data)



class TestDataHomeLock(ThemeLockCase):
    """An apply serializes on the data-home lock make install/uninstall hold."""

    def test_apply_refuses_while_an_install_or_uninstall_holds_the_data_home_lock(self):
        self.hold_data_lock()

        with mock.patch.object(apply_theme, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool()

        assert_lock_time_out(
            self,
            result,
            "waiting for another install or uninstall",
            self.data,
        )
        # No selection step ran: the refusal precedes lookandfeeltool.
        self.assertFalse(self.calls.exists())

    def test_apply_releases_the_data_home_lock_for_the_next_run(self):
        result = self.run_tool()

        assert_succeeded(self, result)
        # After the apply printed its last selection, the data-home lock is
        # free for the next install, uninstall or apply: a non-blocking
        # attempt takes it at once.
        assert_directory_flock_free(self.data)

    def test_the_selections_run_while_the_data_home_lock_is_held(self):
        """Each command independently observes the held data-home lock."""
        observations = self.root / "lock-observations"
        names = (
            "lookandfeeltool",
            "plasma-apply-colorscheme",
            "plasma-apply-desktoptheme",
            "kvantummanager",
            "qdbus6",
        )
        for name in names:
            # A separate process opens its own descriptor, just as a concurrent
            # uninstall would. Record the outcome even for best-effort commands,
            # whose failures alone would not make the apply fail.
            code = (
                "import errno, fcntl, os\n"
                f"fd = os.open({str(self.data)!r}, os.O_RDONLY)\n"
                "try:\n"
                "    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
                "    state = 'unlocked'\n"
                "except OSError as exc:\n"
                "    if exc.errno not in (errno.EACCES, errno.EAGAIN):\n"
                "        raise\n"
                "    state = 'locked'\n"
                "finally:\n"
                "    os.close(fd)\n"
                f"with open({str(observations)!r}, 'a') as sink:\n"
                f"    sink.write({name!r} + ' ' + state + '\\n')\n"
            )
            self.stub(name, f"exec {shlex.quote(sys.executable)} -c {shlex.quote(code)}")

        result = self.run_tool()

        assert_succeeded(self, result)
        self.assertEqual(
            [f"{name} locked" for name in names],
            observations.read_text().splitlines(),
        )

    def test_an_unresolvable_data_home_refuses_the_apply(self):
        """An apply with no resolvable data home cannot serialize at all.

        ``make apply`` runs ``make install`` first, which resolves the same
        data home, so an env where no absolute path can be resolved cannot have
        come from a serialized install; the apply refuses by name instead of
        selecting on top of an unserialized removal.
        """
        # An empty XDG_DATA_HOME falls back below HOME, and an empty HOME
        # resolves no absolute fallback: no data home to serialize on.
        self.env["HOME"] = ""
        self.env["XDG_DATA_HOME"] = ""

        result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("export an absolute HOME", result.stderr)
        # The selections never ran: nothing serialized them with install.
        self.assertFalse(self.calls.exists())

    def test_the_unresolvable_refusal_names_both_received_values(self):
        """The refusal says which variable was empty and what HOME held.

        A relative HOME with an empty XDG_DATA_HOME leaves no absolute data
        home; the message must name both received values, not only HOME.
        """
        self.env["HOME"] = "relative/home"
        self.env["XDG_DATA_HOME"] = ""

        result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("XDG_DATA_HOME is empty", result.stderr)
        self.assertIn("HOME is not an absolute path ('relative/home')", result.stderr)
        self.assertIn("export an absolute HOME", result.stderr)
        self.assertFalse(self.calls.exists())


if __name__ == "__main__":
    unittest.main()
