"""Tests for the cursor CLI, selection/workflow helpers and cursor targets.

The tool runs in-process with ``HOME``, ``XDG_DATA_HOME`` and
``XDG_CONFIG_HOME`` pointed at a temp root, and the selector is a shell stub on
``PATH`` that records its argv. Cursor link policy in ``tools/cursor_link.py``
and the ``kcminputrc`` reader in ``tools/cursor_config.py`` are pinned alongside
command selection without touching a real ``~/.icons`` or Plasma
configuration. The ``apply_cursor --remove`` arms live in
``tests/test_apply_cursor_remove.py``. The Makefile tests drive the public
targets through ``theme_install``, whose children run under the suite's timeout.
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
from support.executable_stubs import write_executable
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.apply_target_cases import ApplyTargetMakeCases
from support.cursor_case import CursorTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from support.tmp_dir import make_tmp_dir
from tools import apply_cursor, cursor_config, cursor_link, cursor_selection, diagnostics, required_command


class TestHomes(CursorTestCase):
    def test_absolute_home_is_required(self):
        for home, expected in (
            (None, "HOME is unset; export an absolute HOME"),
            ("", "HOME is unset; export an absolute HOME"),
            ("relative/home", "HOME is not an absolute path ('relative/home')"),
        ):
            with self.subTest(home=home):
                env = {"XDG_DATA_HOME": str(self.data)}
                if home is not None:
                    env["HOME"] = home
                result = self.run_tool(env=env)
                assert_exit_2_without_traceback(self, result)
                self.assertIn(expected, result.stderr)

    def test_home_value_reaches_the_diagnostic_escaped(self):
        # HOME can carry a control byte when a caller runs the tool directly
        # instead of through make's guards; the diagnostic must display it
        # escaped, never raw.
        result = self.run_tool(env={"HOME": "home\x1bdir"})
        assert_exit_2_without_traceback(self, result)
        self.assertIn("HOME is not an absolute path ('home\\u001bdir')", result.stderr)

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


class TestInstall(CursorTestCase):
    def test_install_links_the_installed_theme_and_selects_it(self):
        self.install_theme()
        self.stub_selector()
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), os.readlink(self.link))
        self.assertEqual([cursor_selection.CURSOR_THEME], self.recorded())
        self.assertIn("restart", result.stdout)

    def test_repeat_install_keeps_the_link_and_succeeds(self):
        self.install_theme()
        self.stub_selector()
        assert_succeeded(self, self.run_tool())
        assert_succeeded(self, self.run_tool())
        self.assertEqual(str(self.installed), os.readlink(self.link))
        self.assertEqual(
            [cursor_link.CURSOR_THEME, cursor_link.CURSOR_THEME],
            self.recorded(),
        )

    def test_optional_install_links_without_a_selector(self):
        # `make apply` passes --optional so a desktop without the KDE selector
        # still gets the pointer set installed and linked; only the selection
        # is skipped, with a note naming the manual step.
        self.install_theme()
        result = self.run_tool("--optional")
        assert_succeeded(self, result)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), os.readlink(self.link))
        self.assertIn("plasma-apply-cursortheme is not on PATH", result.stdout)
        self.assertIn("select it in your desktop's cursor settings", result.stdout)
        self.assertFalse(self.calls.exists())

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

    def test_unreadable_cursor_symlink_is_reported_without_traceback(self):
        self.install_theme()
        self.stub_selector()
        self.link.parent.mkdir()
        os.symlink(str(self.installed), str(self.link))
        real_readlink = os.readlink

        def failing_readlink(path, *args, **kwargs):
            if Path(path) == self.link:
                raise PermissionError("simulated readlink failure")
            return real_readlink(path, *args, **kwargs)

        with mock.patch.object(apply_cursor.os, "readlink", failing_readlink):
            result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot read symlink", result.stderr)
        self.assertIn(str(self.link), result.stderr)
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

    def test_symlinked_icons_directory_is_refused(self):
        self.install_theme()
        self.stub_selector()
        outside = self.root / "outside-icons"
        outside.mkdir()
        os.symlink(str(outside), str(self.home / ".icons"))

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.home / ".icons"), result.stderr)
        self.assertFalse(os.path.lexists(outside / cursor_link.CURSOR_THEME))
        self.assertEqual([], self.recorded())

    def test_a_failed_link_creation_is_reported_by_path(self):
        # Creating the symlink can still fail (a read-only ~/.icons, for
        # example). The OSError must become the tool's own exit-2 diagnostic
        # naming the link -- not a traceback -- and the selector must not run
        # after the link it was meant to expose is missing.
        self.install_theme()
        self.stub_selector()

        def failing_symlink(source, target, *args, **kwargs):
            raise OSError("simulated link failure")

        with mock.patch.object(apply_cursor.os, "symlink", failing_symlink):
            result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot create", result.stderr)
        self.assertIn(str(self.link), result.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertFalse(self.link.parent.exists())
        self.assertEqual([], self.recorded())

    def test_failed_link_creation_preserves_a_concurrently_populated_icons_dir(self):
        self.install_theme()
        self.stub_selector()

        def populate_then_fail(source, target, *args, **kwargs):
            # Model another process creating content after our mkdir but before
            # the symlink operation fails.
            (self.home / ".icons" / "foreign-entry").write_text("keep\n")
            raise OSError("simulated link failure")

        with mock.patch.object(apply_cursor.os, "symlink", populate_then_fail):
            result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertEqual(
            "keep\n",
            (self.home / ".icons" / "foreign-entry").read_text(encoding="utf-8"),
        )
        self.assertFalse(os.path.lexists(self.link))
        self.assertEqual([], self.recorded())

    def test_a_failed_link_creation_keeps_a_preexisting_icons_directory(self):
        # Cleanup after a failed link removes only a ~/.icons this attempt
        # created; an empty ~/.icons the user already had must survive.
        self.install_theme()
        self.stub_selector()
        self.link.parent.mkdir(parents=True)

        def failing_symlink(source, target, *args, **kwargs):
            raise OSError("simulated link failure")

        with mock.patch.object(apply_cursor.os, "symlink", failing_symlink):
            result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(self.link), result.stderr)
        self.assertTrue(self.link.parent.is_dir())
        self.assertEqual([], self.recorded())


class TestSelection(CursorTestCase):
    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The selector runs with a scratch directory for its log. Creating that
        # directory can fail before the selector starts (a full or unwritable
        # TMPDIR); it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        self.install_theme()
        self.stub_selector()
        with mock.patch.object(
            diagnostics.tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot create a scratch directory", result.stderr)
        self.assertIn("no space left", result.stderr)

    def test_selector_is_invoked_with_the_theme_name(self):
        self.install_theme()
        self.stub_selector()
        assert_succeeded(self, self.run_tool())
        self.assertEqual([cursor_selection.CURSOR_THEME], self.recorded())

    def test_missing_selector_exits_2_naming_it(self):
        self.install_theme()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(cursor_selection.SELECT_TOOL, result.stderr)

    def test_optional_install_still_selects_when_the_selector_is_present(self):
        # --optional skips only the selection when the KDE selector is absent.
        # With the selector on PATH it must still run the selection, and must
        # not print the "not on PATH" note.
        self.install_theme()
        self.stub_selector()
        result = self.run_tool("--optional")
        assert_succeeded(self, result)
        self.assertEqual([cursor_selection.CURSOR_THEME], self.recorded())
        self.assertNotIn("is not on PATH", result.stdout)

    def test_optional_install_still_fails_when_the_selector_fails(self):
        # --optional must not swallow a selector that is present but fails.
        self.install_theme()
        self.stub_selector("echo selector exploded >&2\nexit 3")
        result = self.run_tool("--optional")
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"{cursor_selection.SELECT_TOOL} exited 3", result.stderr)

    def test_successful_install_recommends_restarting_applications(self):
        # cursor_workflow.apply prints the restart advice only once the
        # selection has succeeded, as an apply_cursor note on stdout.
        self.install_theme()
        self.stub_selector()
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertIn(
            "apply_cursor: note: restart running applications", result.stdout
        )

    def test_failed_selection_does_not_recommend_restarting_applications(self):
        # A selector that fails means nothing was applied, so the restart
        # advice must not be printed as though the pointer had changed.
        self.install_theme()
        self.stub_selector("exit 3")
        result = self.run_tool()
        assert_failed(self, result)
        self.assertNotIn("restart running applications", result.stdout)

    def test_failed_selector_exits_1_with_the_log_tail(self):
        self.install_theme()
        self.stub_selector("echo selector exploded >&2\nexit 3")
        result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"{cursor_selection.SELECT_TOOL} exited 3", result.stderr)
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
        selector = self.bin / cursor_selection.SELECT_TOOL
        write_executable(selector, "#!/nonexistent/interpreter\n")

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(
            f"cannot run {cursor_selection.SELECT_TOOL}", result.stderr
        )
        self.assertTrue(self.link.is_symlink())


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
            cursor_link.CURSOR_THEME,
            cursor_config.cursor_theme_setting(self.config),
        )

    def test_a_setting_outside_the_mouse_section_is_ignored(self):
        # A cursorTheme before any heading or under another group must not
        # make removal print a reset note for a selection KDE does not use.
        self.path.write_text(
            "cursorTheme=org.macos8.desktop\n"
            "[Other]\ncursorTheme=org.macos8.desktop\n",
            encoding="utf-8",
        )
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config))

    def test_comments_and_spacing_around_the_key_are_handled(self):
        self.path.write_text(
            "[Mouse]\n"
            "# a comment\n"
            "; another comment\n"
            "  cursorTheme = org.macos8.desktop  \n",
            encoding="utf-8",
        )
        self.assertEqual(
            cursor_link.CURSOR_THEME,
            cursor_config.cursor_theme_setting(self.config),
        )

    def test_an_exotic_separator_in_a_comment_does_not_end_the_line(self):
        # A line ends at LF, CR and CRLF only (tools/text_lines.py): a
        # Unicode line separator (U+2028) inside a comment line does not end
        # it, so its remainder must never read as a cursorTheme setting.
        self.path.write_text(
            "[Mouse]\n"
            "cursorTheme=org.macos8.desktop\n"
            "# a note\u2028cursorTheme=other.theme\n",
            encoding="utf-8",
        )
        self.assertEqual(
            cursor_link.CURSOR_THEME,
            cursor_config.cursor_theme_setting(self.config),
        )

    def test_a_value_line_keeps_a_builtin_exotic_separator_whole(self):
        # A vertical tab inside a value is part of that value, not a break:
        # splitting on it would truncate the theme name mid-word.
        self.path.write_text("[Mouse]\ncursorTheme=widget\x0bengine\n")
        self.assertEqual(
            "widget\x0bengine",
            cursor_config.cursor_theme_setting(self.config),
        )

    def test_a_non_utf8_file_reads_as_no_setting(self):
        self.path.write_bytes(b"[Mouse]\ncursorTheme=\xff\n")
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config))

    def test_a_directory_reads_as_no_setting(self):
        self.path.mkdir()
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config))


class TestMakeApplyCursor(ApplyTargetMakeCases, unittest.TestCase):
    TARGET = "apply-cursor"
    REMOVE_TARGET = "remove-cursor"
    INSTALL_PACKAGES = "icon-theme"
    SCRIPT = "tools/apply_cursor.py"


if __name__ == "__main__":
    unittest.main()
