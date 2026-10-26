"""Tests for tools/apply_cursor.py and the cursor Makefile targets.

The tool runs in-process with ``HOME``, ``XDG_DATA_HOME`` and
``XDG_CONFIG_HOME`` pointed at a temp root, and the selector is a shell stub on
``PATH`` that records its argv. The link, the selection, the foreign-path
refusals and the removal are pinned without touching a real ``~/.icons`` or
Plasma configuration. The Makefile tests drive the public targets through
``theme_install``, whose children run under the suite's timeout.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import process_runner
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import snippet_child
from support.apply_target_cases import ApplyTargetMakeCases
from support.cli_fixtures import run_main
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from support.recorded_lines import recorded_lines
from support.tmp_dir import make_tmp_dir
from support.unlink_failure import unlink_failing_for
from tools import apply_cursor, required_command


class CursorCase(unittest.TestCase):
    """Base with a temp home, data/config homes and a recording selector stub."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data = self.root / "data"
        self.config = self.root / "config"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.calls = self.root / "calls"
        self.installed = (
            self.data / "icons" / apply_cursor.CURSOR_THEME
        )
        self.link = self.home / ".icons" / apply_cursor.CURSOR_THEME
        self.env = {
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "PATH": str(self.bin),
        }

    def install_theme(self):
        """Write the installed theme's ``index.theme`` and ``cursors/left_ptr``."""
        (self.installed / "cursors").mkdir(parents=True, exist_ok=True)
        (self.installed / "index.theme").write_text(
            "[Icon Theme]\nName=Mac OS 8.6\n", encoding="utf-8"
        )
        (self.installed / "cursors" / "left_ptr").write_bytes(b"cursor\n")

    def stub_selector(self, body="exit 0"):
        """Write a ``plasma-apply-cursortheme`` stub recording its argv."""
        path = self.bin / apply_cursor.SELECT_TOOL
        path.write_text(
            "#!/bin/sh\n"
            f'printf \'%s\\n\' "$*" >> "{self.calls}"\n'
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def run_tool(self, *args, env=None):
        with mock.patch.dict(os.environ, env or self.env, clear=True):
            return run_main(apply_cursor.main, "apply_cursor", args)

    def recorded(self):
        return recorded_lines(self.calls)


class TestHomes(CursorCase):
    def test_absolute_home_is_required(self):
        for home in (None, "relative/home"):
            with self.subTest(home=home):
                env = {"XDG_DATA_HOME": str(self.data)}
                if home is not None:
                    env["HOME"] = home
                result = self.run_tool(env=env)
                assert_exit_2_without_traceback(self, result)
                self.assertIn("HOME", result.stderr)

    def test_data_home_falls_back_to_home(self):
        home, data, config = apply_cursor.resolve_homes(
            {"HOME": "/home/u"}
        )
        self.assertEqual(Path("/home/u"), home)
        self.assertEqual(Path("/home/u/.local/share"), data)
        self.assertEqual(Path("/home/u/.config"), config)

    def test_absolute_xdg_homes_win_and_relative_ones_fall_back(self):
        _, data, config = apply_cursor.resolve_homes(
            {
                "HOME": "/home/u",
                "XDG_DATA_HOME": "/data",
                "XDG_CONFIG_HOME": "/config",
            }
        )
        self.assertEqual(Path("/data"), data)
        self.assertEqual(Path("/config"), config)
        _, data, config = apply_cursor.resolve_homes(
            {
                "HOME": "/home/u",
                "XDG_DATA_HOME": "relative",
                "XDG_CONFIG_HOME": "",
            }
        )
        self.assertEqual(Path("/home/u/.local/share"), data)
        self.assertEqual(Path("/home/u/.config"), config)


class TestInstall(CursorCase):
    def test_install_links_the_installed_theme_and_selects_it(self):
        self.install_theme()
        self.stub_selector()
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), os.readlink(self.link))
        self.assertEqual([apply_cursor.CURSOR_THEME], self.recorded())
        self.assertIn("restart", result.stdout)

    def test_repeat_install_keeps_the_link_and_succeeds(self):
        self.install_theme()
        self.stub_selector()
        assert_succeeded(self, self.run_tool())
        assert_succeeded(self, self.run_tool())
        self.assertEqual(str(self.installed), os.readlink(self.link))
        self.assertEqual(
            [apply_cursor.CURSOR_THEME, apply_cursor.CURSOR_THEME],
            self.recorded(),
        )

    def test_missing_installed_theme_names_the_path(self):
        self.stub_selector()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.installed / "index.theme"), result.stderr)
        self.assertIn("make install", result.stderr)
        self.assertFalse(self.link.exists())

    def test_missing_cursor_file_names_the_path(self):
        self.install_theme()
        (self.installed / "cursors" / "left_ptr").unlink()
        self.stub_selector()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.installed / "cursors" / "left_ptr"), result.stderr)

    def test_foreign_symlink_is_refused_and_unchanged(self):
        self.install_theme()
        self.stub_selector()
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.link.parent.mkdir(parents=True)
        os.symlink(str(elsewhere), str(self.link))
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.link), result.stderr)
        self.assertEqual(str(elsewhere), os.readlink(self.link))
        self.assertEqual([], self.recorded())

    def test_real_directory_is_refused_and_unchanged(self):
        self.install_theme()
        self.stub_selector()
        self.link.mkdir(parents=True)
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.link), result.stderr)
        self.assertTrue(self.link.is_dir())

    def test_file_is_refused_and_unchanged(self):
        self.install_theme()
        self.stub_selector()
        self.link.parent.mkdir(parents=True)
        self.link.write_text("foreign\n", encoding="utf-8")
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.link), result.stderr)
        self.assertEqual("foreign\n", self.link.read_text(encoding="utf-8"))

    def test_icons_path_that_is_not_a_directory_is_refused(self):
        self.install_theme()
        self.stub_selector()
        (self.home / ".icons").write_text("not a directory\n", encoding="utf-8")
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.home / ".icons"), result.stderr)

    def test_a_failed_link_creation_is_reported_by_path(self):
        # Creating the symlink can still fail (a read-only ~/.icons, for
        # example). The OSError must become the tool's own exit-2 diagnostic
        # naming the link -- not a traceback -- and the selector must not run
        # after the link it was meant to expose is missing.
        self.install_theme()
        self.stub_selector()
        self.link.parent.mkdir(parents=True)

        def failing_symlink(source, target, *args, **kwargs):
            raise OSError("simulated link failure")

        with mock.patch.object(apply_cursor.os, "symlink", failing_symlink):
            result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot create", result.stderr)
        self.assertIn(str(self.link), result.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertEqual([], self.recorded())


class TestSelection(CursorCase):
    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The selector runs with a scratch directory for its log. Creating that
        # directory can fail before the selector starts (a full or unwritable
        # TMPDIR); it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        self.install_theme()
        self.stub_selector()
        with mock.patch.object(
            apply_cursor.tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot create a scratch directory", result.stderr)
        self.assertIn("no space left", result.stderr)

    def test_selector_is_invoked_with_the_theme_name(self):
        self.install_theme()
        self.stub_selector()
        assert_succeeded(self, self.run_tool())
        self.assertEqual([apply_cursor.CURSOR_THEME], self.recorded())

    def test_missing_selector_exits_2_naming_it(self):
        self.install_theme()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(apply_cursor.SELECT_TOOL, result.stderr)

    def test_failed_selector_exits_1_with_the_log_tail(self):
        self.install_theme()
        self.stub_selector("echo selector exploded >&2\nexit 3")
        result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"{apply_cursor.SELECT_TOOL} exited 3", result.stderr)
        self.assertIn("selector exploded", result.stderr)

    def test_selector_timeout_exits_1_with_the_log_tail(self):
        self.install_theme()
        self.stub_selector()
        with mock.patch.object(
            required_command, "run_logged", return_value=None
        ):
            result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn("timed out", result.stderr)

    def test_sigterm_kills_the_selector_group_and_removes_scratch(self):
        # run_logged starts the selector in its own session, so without a
        # SIGTERM handler the tool dies before its finally blocks: the
        # selector keeps running and the scratch directory is left behind.
        self.install_theme()
        scratch_parent = self.root / "tmp"
        scratch_parent.mkdir()
        pidfile = self.root / "selector.pid"
        self.stub_selector(f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(
            self.env,
            PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            TMPDIR=str(scratch_parent),
        )
        selector_pid = None

        def kill_selector():
            if selector_pid is not None:
                try:
                    os.kill(selector_pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_selector)
        with process_runner.running(
            [sys.executable, apply_cursor.__file__],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) as process:
            selector_pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="apply_cursor", child="selector"
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assertEqual([], os.listdir(scratch_parent))
        with self.assertRaises(ProcessLookupError):
            os.kill(selector_pid, 0)

    def test_unrunnable_selector_exits_2_without_a_traceback(self):
        # `shutil.which` finds an executable script whose interpreter is
        # missing, so the missing-tool check passes, but Popen raises OSError.
        # The selector is as unusable as a missing one and must be reported as
        # this tool's own diagnostic, not a traceback that skips the exit
        # contract. PATH holds only the stub bin, so execvp cannot fall
        # through to a real selector later on PATH.
        self.install_theme()
        selector = self.bin / apply_cursor.SELECT_TOOL
        selector.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        selector.chmod(0o755)

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(
            f"cannot run {apply_cursor.SELECT_TOOL}", result.stderr
        )
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue(self.link.is_symlink())


class TestRemove(CursorCase):
    def make_our_link(self):
        self.link.parent.mkdir(parents=True)
        os.symlink(str(self.installed), str(self.link))

    def test_removal_unlinks_only_our_symlink_and_keeps_the_icons_dir(self):
        self.make_our_link()
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertFalse(os.path.lexists(self.link))
        self.assertTrue((self.home / ".icons").is_dir())

    def test_removal_accepts_a_dangling_link_to_our_theme(self):
        self.make_our_link()
        self.assertFalse(self.installed.exists())
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertFalse(os.path.lexists(self.link))

    def test_removal_is_repeatable(self):
        self.make_our_link()
        assert_succeeded(self, self.run_tool("--remove"))
        assert_succeeded(self, self.run_tool("--remove"))

    def test_removal_leaves_a_foreign_symlink_dir_and_file(self):
        for kind in ("symlink", "directory", "file"):
            with self.subTest(kind=kind):
                if self.link.is_symlink() or os.path.lexists(self.link):
                    if self.link.is_dir() and not self.link.is_symlink():
                        self.link.rmdir()
                    else:
                        self.link.unlink()
                self.link.parent.mkdir(parents=True, exist_ok=True)
                if kind == "symlink":
                    elsewhere = self.root / "foreign"
                    os.symlink(str(elsewhere), str(self.link))
                elif kind == "directory":
                    self.link.mkdir()
                else:
                    self.link.write_text("foreign\n", encoding="utf-8")
                result = self.run_tool("--remove")
                assert_succeeded(self, result)
                self.assertIn(str(self.link), result.stdout)
                self.assertTrue(os.path.lexists(self.link))

    def test_a_failed_link_removal_is_reported_by_path(self):
        # The link this tool created can still fail to unlink (a read-only
        # ~/.icons, for example). The OSError must become the tool's own exit-2
        # diagnostic naming the link -- not a traceback -- and the link must
        # stay in place so the operator can retry.
        self.make_our_link()

        with unlink_failing_for(self.link, "simulated unlink failure"):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot remove", result.stderr)
        self.assertIn(str(self.link), result.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), os.readlink(self.link))

    def test_kcminputrc_note_names_the_reset_only_when_our_theme_is_selected(self):
        self.make_our_link()
        kcminputrc = self.config / "kcminputrc"
        kcminputrc.parent.mkdir(parents=True)
        kcminputrc.write_text(
            "[Mouse]\ncursorTheme=org.macos8.desktop\n", encoding="utf-8"
        )
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertIn("plasma-apply-cursortheme breeze_cursors", result.stdout)
        self.assertEqual(
            "[Mouse]\ncursorTheme=org.macos8.desktop\n",
            kcminputrc.read_text(encoding="utf-8"),
        )

    def test_kcminputrc_note_is_absent_for_a_foreign_selection(self):
        self.make_our_link()
        kcminputrc = self.config / "kcminputrc"
        kcminputrc.parent.mkdir(parents=True)
        kcminputrc.write_text("[Mouse]\ncursorTheme=Adwaita\n", encoding="utf-8")
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertNotIn("breeze_cursors", result.stdout)

    def test_a_fifo_kcminputrc_does_not_block_removal(self):
        # A plain read_text/open on a FIFO waits forever for a writer. Run the
        # removal in a child so a regression is a bounded timeout rather than
        # a stalled check, and the removal still succeeds with no note.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        self.make_our_link()
        self.config.mkdir(parents=True)
        os.mkfifo(self.config / "kcminputrc")
        snippet = (
            "import sys; from tools.apply_cursor import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        with mock.patch.dict(os.environ, self.env, clear=True):
            child = snippet_child.run(
                [snippet, "--remove"], cwd=repo_root.ROOT, timeout=10
            )
        self.assertEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertNotIn("breeze_cursors", child.stdout)


class TestCursorThemeSetting(unittest.TestCase):
    """Pin the ``[Mouse] cursorTheme`` reader the removal note depends on."""

    def setUp(self):
        self.config = make_tmp_dir(self)
        self.path = self.config / "kcminputrc"

    def test_a_leading_bom_does_not_hide_the_mouse_section(self):
        # kcminputrc is decoded as utf-8-sig; plain utf-8 would fold the BOM
        # into the section heading, so the reset note would silently vanish.
        self.path.write_bytes(
            b"\xef\xbb\xbf[Mouse]\ncursorTheme=org.macos8.desktop\n"
        )
        self.assertEqual(
            apply_cursor.CURSOR_THEME,
            apply_cursor._cursor_theme_setting(self.config),
        )

    def test_a_setting_outside_the_mouse_section_is_ignored(self):
        # A cursorTheme before any heading or under another group must not
        # make removal print a reset note for a selection KDE does not use.
        self.path.write_text(
            "cursorTheme=org.macos8.desktop\n"
            "[Other]\ncursorTheme=org.macos8.desktop\n",
            encoding="utf-8",
        )
        self.assertIsNone(apply_cursor._cursor_theme_setting(self.config))

    def test_comments_and_spacing_around_the_key_are_handled(self):
        self.path.write_text(
            "[Mouse]\n"
            "# a comment\n"
            "; another comment\n"
            "  cursorTheme = org.macos8.desktop  \n",
            encoding="utf-8",
        )
        self.assertEqual(
            apply_cursor.CURSOR_THEME,
            apply_cursor._cursor_theme_setting(self.config),
        )

    def test_a_non_utf8_file_reads_as_no_setting(self):
        self.path.write_bytes(b"[Mouse]\ncursorTheme=\xff\n")
        self.assertIsNone(apply_cursor._cursor_theme_setting(self.config))

    def test_a_directory_reads_as_no_setting(self):
        self.path.mkdir()
        self.assertIsNone(apply_cursor._cursor_theme_setting(self.config))


class TestMakeApplyCursor(ApplyTargetMakeCases, unittest.TestCase):
    TARGET = "apply-cursor"
    REMOVE_TARGET = "remove-cursor"
    INSTALL_PACKAGES = "icon-theme"
    SCRIPT = "tools/apply_cursor.py"


if __name__ == "__main__":
    unittest.main()
