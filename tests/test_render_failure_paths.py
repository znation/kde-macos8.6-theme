"""The render CLI's failure-path suite, against shell stubs of the external tools.

``tools/render_surface.py``'s argument handling and its workflow's failure
behavior -- a missing or unrunnable tool, an unusable scratch directory, an
unpainted or failed capture, publication that must keep the previous output
whole -- run here against stub executables, without any Plasma session; the
pixel gates that drive the same CLI against a real headless session live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py`` beside the ``Test...DialogRender``
gates.
"""

from __future__ import annotations

import errno
import os
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import process_runner, repo_root
from support.cli_fixtures import assert_missing_tool_named, call_main
from tools import (
    render_session,
    render_setup,
    render_surface,
    render_window_rules,
    render_workflow,
)  # noqa: E402
from tools.png.write import encode_png  # noqa: E402


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-surface-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        # Capture the real make and sleep before the stub directory goes on
        # PATH.
        self.real_make = shutil.which("make")
        self.real_sleep = shutil.which("sleep")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.scratch_parent = self.root / "tmp"
        self.scratch_parent.mkdir()
        self.stub("make", "exit 0")
        for name in render_surface.REQUIRED_TOOLS:
            if name != "make":
                self.stub(name, "exit 0")
        path = f"{self.bin}{os.pathsep}{os.environ['PATH']}"
        patches = (
            mock.patch.dict(os.environ, {"PATH": path}),
            mock.patch.object(tempfile, "tempdir", str(self.scratch_parent)),
            # These tests pin render and capture failure paths, not package
            # discovery; the applet preflight's XDG-root search is pinned off
            # so the runs stay host-independent.
            mock.patch.object(render_surface, "applet_problem", return_value=None),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def stub(self, name, body):
        """Write an executable stub named *name* that runs *body*."""
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def assert_scratch_removed(self):
        """Assert the scratch parent holds no leftover entries."""
        self.assertEqual([], os.listdir(self.scratch_parent))

    def assert_failed_run(self, status, stderr, output, expected_status, *diagnostics):
        """Assert a failed render's whole exit contract: the named exit
        status with only its own diagnostics on stderr (no traceback), no
        rendered output published and no leftover scratch session.

        Shared by the 18 failure-path tails in :class:`TestFailurePaths`.
        """
        self.assertEqual(expected_status, status)
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_tool_and_exits_2(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(render_surface.main, "out.png")
        self.assertEqual(2, status)
        self.assertIn(render_surface.REQUIRED_TOOLS[0], stderr)
        self.assertIn("render_surface: error:", stderr)

    def test_applet_id_with_nul_is_rejected_as_usage_error(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(
                    render_surface.main, "out.png", "--applet", "org.example\0widget"
                )
        self.assertEqual(2, status)
        self.assertIn("--applet must be a plasmoid id without NUL", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_a_single_missing_tool_is_the_one_named(self):
        assert_missing_tool_named(
            self, render_surface.main, render_surface.REQUIRED_TOOLS, ("out.png",)
        )


def crashed_applet_setup_diagnosis(setup_timeout):
    """Return the fail message the crashed-applet fixture builds on expiry.

    Shared by the crashed-applet test and the offline reproduction of its
    expired-wait diagnosis, so both name the recorded wait instead of a bare
    status mismatch.
    """
    return (
        "the crashed applet's setup did not "
        f"{setup_timeout.read_text().strip()} within the polling "
        "budget; the settle stub must start and reap it before the "
        "session's liveness check"
    )


class TestFailurePaths(StubTools):
    def run_main(self, *extra):
        """Run ``main`` on ``out.png`` with *extra* and return status, stderr, output."""
        output = self.root / "out.png"
        status, stderr = call_main(render_surface.main, str(output), *extra)
        return status, stderr, output

    def assert_unrunnable_command_is_reported(self, command, diagnostic):
        """Check the CLI handles a found executable that cannot be started."""
        executable = self.bin / command
        executable.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)

        # Keep execvp from falling through to a real command after ENOENT.
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}):
            status, stderr, output = self.run_main()

        self.assert_failed_run(status, stderr, output, 2, diagnostic)

    def test_menu_dialog_launches_its_kdialog_menu_client(self):
        # The menu mode must reach the session as a KDialog menu client (and
        # therefore apply the dialog's Kvantum configuration path), not fall
        # through to the default Plasma calculator applet.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection:
            status, stderr, output = self.run_main("--menu-dialog")

        # The menu mode takes the dialog path: the dialog's config files (the
        # global theme's kdeglobals) and the Kvantum selection, not the
        # applet render's session-only set. The rendered siblings pin this
        # path too, but only for the checkbox and combobox modes.
        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("kdialog", argv[-1])
        self.assertIn("--menu", argv[-1])
        self.assertIn("Alpha", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_inactive_dialog_launches_its_two_window_wrapper(self):
        # The inactive mode must reach the session as the two-window sh -c
        # wrapper (one kdialog per fixed title, opened inactive-window
        # first), not fall through to the default Plasma calculator applet.
        # Its session also writes the forced-geometry rules the two titles
        # are matched by, beside the dialog's Kvantum selection.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection, \
                mock.patch.object(render_workflow, "write_window_rules") as rules:
            status, stderr, output = self.run_main("--inactive-dialog")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        rules.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("kdialog", argv[-1])
        self.assertIn(render_window_rules.INACTIVE_TITLE, argv[-1])
        self.assertIn(render_window_rules.FOCUSED_TITLE, argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_desktop_render_launches_the_plasmashell_client(self):
        # The desktop mode must reach the session as plasmashell (the shell
        # draws the menu bar itself), with the look-and-feel selection
        # written beside the session configs, not fall through to the
        # default Plasma calculator applet or a dialog client.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as selection:
            status, stderr, output = self.run_main("--desktop")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("plasmashell", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_splash_render_launches_the_ksplashqml_client(self):
        # The splash mode must reach the session as ksplashqml pointing at
        # the session-local installed look-and-feel package (the splash
        # paints its own Splash.qml from the scratch data home, never the
        # caller's), writing only the applet's session configs: the splash
        # reads no selection, so no look-and-feel, Kvantum, GTK or window
        # rules write may ride the session.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as look, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as kvantum, \
                mock.patch.object(render_workflow, "write_window_rules") as rules, \
                mock.patch.object(render_workflow, "install_gtk_selection") as gtk:
            status, stderr, output = self.run_main("--splash")

        self.assertEqual(render_setup.CONFIG_FILES, configs.call_args.kwargs["files"])
        look.assert_not_called()
        kvantum.assert_not_called()
        rules.assert_not_called()
        gtk.assert_not_called()
        argv = run.call_args.args[0]
        self.assertIn("ksplashqml", argv[-1])
        self.assertIn("--nofork", argv[-1])
        self.assertIn(
            "plasma/look-and-feel/org.macos8.desktop", argv[-1]
        )
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_only_the_inactive_dialog_writes_the_window_rules(self):
        # The two-window forced-geometry rules are the inactive mode's own
        # session config: no applet render and no one-window dialog render
        # may write a kwinrulesrc the other sessions never asked for.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_window_rules"
        ) as rules, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            for extra in ((), ("--checkbox-dialog",)):
                with self.subTest(extra=extra):
                    status, _, _ = self.run_main(*extra)
                    self.assertEqual(1, status)
                    rules.assert_not_called()
            status, _, _ = self.run_main("--inactive-dialog")
            self.assertEqual(1, status)

        rules.assert_called_once()
        self.assert_scratch_removed()

    def test_only_dialog_renders_add_kdeglobals_to_the_session_configs(self):
        # Dialog clients are Qt applications, so the scratch session must
        # apply the global theme defaults that select Kvantum. The applet
        # render deliberately writes only the window-decoration configs.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_session_configs"
        ) as write_configs, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, _, _ = self.run_main()
            self.assertEqual(1, status)
            applet_files = write_configs.call_args.kwargs["files"]

            status, _, _ = self.run_main("--checkbox-dialog")
            self.assertEqual(1, status)
            dialog_files = write_configs.call_args.kwargs["files"]

        self.assertEqual(("kwinrc", "plasmarc"), applet_files)
        self.assertEqual(
            ("kwinrc", "plasmarc", "kdeglobals"), dialog_files
        )
        self.assert_scratch_removed()

    def test_gtk_dialog_installs_the_gtk_selection_beside_the_kvatum_one(self):
        # The GTK mode's zenity client wears the theme through the selection
        # the workflow publishes into the scratch config home, so the GTK
        # selection install must run beside the Kvantum one, not be
        # forgotten the way a fourth copy of the fan-out could omit it.
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow, "install_gtk_selection"
        ) as install, mock.patch.object(
            render_workflow, "write_kvantum_selection"
        ) as kvantum, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(status, stderr, output, 1)
        install.assert_called_once()
        kvantum.assert_called_once()

    def test_a_failed_gtk_selection_install_exits_1_and_removes_scratch(self):
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow,
            "install_gtk_selection",
            side_effect=render_setup._ConfigError("sheet is missing"),
        ) as install, mock.patch.object(
            render_workflow, "run_logged", return_value=0
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(
            status,
            stderr,
            output,
            1,
            "cannot install the GTK selection",
            "sheet is missing",
        )
        install.assert_called_once()

    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The scratch session is created before the install starts. Creating it
        # can fail (a full or unwritable TMPDIR) before there is anything to
        # clean up; it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        with mock.patch.object(
            tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "cannot create a scratch session directory", "no space left",
        )

    def test_failed_install_exits_1_and_removes_scratch(self):
        self.stub("make", "echo install exploded; exit 4")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "make install exited 4", "install exploded",
        )

    def test_an_unrunnable_make_exits_2_and_removes_scratch(self):
        # `which` still finds an executable script whose interpreter is gone,
        # so the missing-tool check passes and Popen raises OSError. The tool
        # must report that itself instead of letting the OSError traceback.
        self.assert_unrunnable_command_is_reported(
            "make", "render_surface: error: cannot run make:"
        )

    def test_an_unrunnable_session_launcher_exits_2_and_removes_scratch(self):
        # Same fault as the make test, at the second command the tool starts
        # itself: `shutil.which` finds dbus-run-session, but Popen raises
        # OSError. It must be the tool's own exit-2 diagnostic, not a
        # traceback that skips the scratch cleanup.
        self.assert_unrunnable_command_is_reported(
            "dbus-run-session", "render_surface: error: cannot run dbus-run-session:"
        )

    def test_a_failed_session_config_write_exits_1_with_a_diagnostic(self):
        # The session config is derived from the shipped defaults and written
        # into the scratch config home. A write that fails there (a full disk),
        # a defaults file that cannot be decoded, or a malformed section
        # heading the reader rejects must become the tool's own diagnostic and
        # exit 1, not a traceback that bypasses the documented exit status.
        def die(config_home, names):
            raise failure

        for label, failure in (
            ("a full disk", OSError(errno.ENOSPC, "No space left on device")),
            (
                "a non-UTF-8 defaults file",
                UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            ),
            (
                "a malformed defaults heading",
                ValueError("malformed section heading '[a][b] # note'"),
            ),
        ):
            with self.subTest(label):
                with mock.patch.object(render_setup, "write_configs", die):
                    status, stderr, output = self.run_main()
                self.assert_failed_run(
                    status, stderr, output, 1,
                    "render_surface: error:", "session config",
                )

    def test_a_failed_themes_link_exits_2_and_removes_scratch(self):
        # The scratch home's themes link is made after `make install`, at the
        # one place the engine's literal `$HOME/.local/share/themes/` search
        # path is satisfied. When the link cannot be made (an entry raced in
        # at the link name), the tool must report its own exit-2 diagnostic
        # naming the path, not a traceback that skips the scratch cleanup.
        themes = self.root / "themes"
        problem = OSError(errno.EEXIST, "File exists")

        def die(session):
            return problem, themes

        with mock.patch.object(render_workflow, "link_kvantum_themes", die):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "render_surface: error: cannot link",
            str(themes), "File exists",
        )

    def test_a_failed_kvantum_selection_write_exits_1_and_removes_scratch(self):
        # A dialog render selects the Kvantum theme in the scratch config
        # home before the session starts; without the name the engine falls
        # back to its compiled-in default and the gate would silently compare
        # the wrong theme's pixels. A selection write that fails there (a
        # full disk) must become the tool's own exit-1 diagnostic, not a
        # traceback that skips the scratch cleanup or a render that goes out
        # carrying an unthemed widget.
        def die(session):
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(render_workflow, "write_kvantum_selection", die):
            status, stderr, output = self.run_main("--menu-dialog")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render_surface: error:",
            "cannot write the Kvantum selection",
            "No space left on device",
        )

    def test_install_timeout_exits_1_with_a_timeout_diagnostic(self):
        # A hung `make install` is killed by run_logged, which reports the
        # timeout as None. The diagnostic must name the timeout rather than
        # the raw status ("exited None"), and the failure must still exit 1
        # and remove the scratch root. The real install timeout is minutes
        # long, so run_logged is stubbed instead of waited out; the render
        # session's own timeout is covered by
        # test_timeout_kills_the_session_group_and_exits_1.
        with mock.patch.object(render_setup, "run_logged", return_value=None):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1, "make install timed out",
        )

    def test_failed_session_exits_1_and_removes_scratch(self):
        self.stub("dbus-run-session", "echo no display; exit 3")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 3", "no display",
        )

    def test_session_without_a_capture_exits_1(self):
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1, "not a readable PNG",
        )

    def stub_live_session(self, plasmawindowed_body):
        """Run the real session script under stubs of the tools it starts.

        The fake launcher evaluates the script ``render_surface`` hands the
        session, so the applet liveness check is the tool's own script and not
        a test double. ``spectacle`` writes a valid capture whenever the script
        reaches it, which is what makes a silently crashed applet observable.
        """
        fixture = self.root / "session-capture.png"
        fixture.write_bytes(
            encode_png(320, 240, bytes([0xDD]) * (320 * 240 * 3))
        )
        self.stub("plasmawindowed", plasmawindowed_body)
        self.stub(
            "spectacle",
            'out=; while [ "$#" -gt 0 ]; do '
            'if [ "$1" = -o ]; then shift; out=$1; fi; shift; done; '
            f'cp "{fixture}" "$out"',
        )
        self.stub("dbus-run-session", 'for script; do :; done; eval "$script"')

    def test_a_running_applet_is_still_captured(self):
        self.stub_live_session("exec sleep 60")
        status, stderr, output = self.run_main("--settle", "0")
        self.assertEqual((0, ""), (status, stderr))
        self.assertTrue(output.exists())
        self.assert_scratch_removed()

    def test_a_crashed_applet_is_not_captured_as_a_successful_render(self):
        # plasmawindowed is backgrounded, so its failure is otherwise invisible;
        # spectacle would capture the empty session and the tool would publish
        # that PNG as a successful render. The settle stub returns only once
        # the crashed applet has been started and reaped, so the liveness check
        # cannot race the background process's exit. A slow host can delay that
        # setup past the polling budget; the stub then records which wait
        # expired, so the test names the setup race instead of failing as a
        # bare status mismatch against a render of a still-starting applet.
        pidfile = self.root / "applet.pid"
        setup_timeout = self.root / "setup-timeout"
        self.stub_live_session(f"echo $$ > {shlex.quote(str(pidfile))}; exit 1")
        self.stub(
            "sleep",
            f"pidfile={shlex.quote(str(pidfile))}; "
            f"timeout={shlex.quote(str(setup_timeout))}; "
            f"pause={shlex.quote(self.real_sleep)}; "
            'n=0; while [ ! -s "$pidfile" ]; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && { echo start > "$timeout"; exit 1; }; '
            '"$pause" 0.02; done; '
            'pid=$(cat "$pidfile"); n=0; '
            'while kill -0 "$pid" 2>/dev/null; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && { echo reap > "$timeout"; exit 1; }; '
            '"$pause" 0.02; done',
        )
        status, stderr, output = self.run_main("--settle", "0")
        if setup_timeout.exists():
            self.fail(crashed_applet_setup_diagnosis(setup_timeout))
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 1", "plasmawindowed exited before the capture",
        )

    def test_an_expired_setup_wait_is_reported_by_name_not_as_a_status_mismatch(self):
        # The offline reproduction of the crashed-applet fixture's expired
        # setup wait (the archived slow-check record): a stubbed session whose
        # applet start passes inside the widened 1500-iteration bound, and
        # whose recorded `setup-timeout` file then names the expired wait, so
        # the shipped diagnosis branch fires and reports the wait by name
        # before any status assertion. The stub forces the file's content
        # instead of spending the real 1500-iteration 0.02 s poll -- the
        # ledger requires the failure diagnosis to be reproduced offline,
        # not the wall clock -- and it reaps the applet first, so the
        # session's own liveness check still fails the render deterministically.
        pidfile = self.root / "applet.pid"
        setup_timeout = self.root / "setup-timeout"
        self.stub_live_session(f"echo $$ > {shlex.quote(str(pidfile))}; exit 1")
        self.stub(
            "sleep",
            f"pidfile={shlex.quote(str(pidfile))}; "
            f"timeout={shlex.quote(str(setup_timeout))}; "
            f"pause={shlex.quote(self.real_sleep)}; "
            'n=0; while [ ! -s "$pidfile" ]; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && exit 1; "$pause" 0.02; done; '
            'pid=$(cat "$pidfile"); n=0; '
            'while kill -0 "$pid" 2>/dev/null; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && exit 1; "$pause" 0.02; done; '
            # Forced: name the expired start wait, then fail the settle
            # exactly as the shipped stub's expired branch does.
            'echo start > "$timeout"; exit 1',
        )
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 1", "plasmawindowed exited before the capture",
        )
        # The forced record names the expired wait, and the diagnosis the
        # shipped crashed-applet fixture builds from it names that wait and
        # its polling budget -- never a bare status mismatch.
        self.assertEqual("start", setup_timeout.read_text().strip())
        diagnosis = crashed_applet_setup_diagnosis(setup_timeout)
        self.assertIn("start", diagnosis)
        self.assertIn("within the polling budget", diagnosis)

    def test_a_failing_capture_session_exits_1_writes_no_output_and_removes_scratch(self):
        # A live applet can sit inside a session whose capture command fails
        # -- spectacle without a usable compositor, an unwritable surface
        # path -- so the liveness check passes and the script reaches `exit
        # $status` with the capture command's own non-zero status. Keeping
        # the client alive pins that arm: the session must exit with the
        # capture's status and not call it a success, and the tool must
        # treat it exactly like any other failed session -- the failure and
        # the capture stub's word on stderr replayed, nothing published,
        # scratch removed.
        self.stub_live_session("exec sleep 60")
        self.stub("spectacle", "echo capture shot down >&2; exit 7")
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 7", "capture shot down",
        )

    def test_a_capture_of_the_wrong_size_exits_1_and_writes_nothing(self):
        # spectacle can hand back a surface captured at the wrong geometry. The
        # render must refuse it: publishing that PNG would report success for a
        # size the fidelity comparison never asked to check.
        self.stub_capture()
        status, stderr, output = self.run_main("--width", "64", "--height", "48")
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is 320x240, expected 64x48",
        )

    def test_an_unpainted_capture_exits_1_and_writes_nothing(self):
        # A virtual session that has not painted presents an all-black screen.
        # The render used to publish that correctly sized PNG as a success,
        # which surfaced later as unexplained pixel mismatches. It must fail
        # here, naming the paint budget, instead of publishing a render of
        # nothing.
        self.stub_capture(fill=0x00)
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is entirely black", "did not paint", "8s settle",
        )

    def test_a_client_that_exits_during_the_capture_is_not_blamed_on_the_paint_budget(
        self,
    ):
        # A client that passes the settle's liveness check and then dies
        # while the capture runs takes its window with it: the black frame
        # is a vanished client, not a window that never painted. The
        # session log's exit marker must switch the diagnosis to the
        # vanished client -- "retry with a longer --settle" cannot fix a
        # client that already ended, and the splash's ``--test`` lifetime
        # ends about 10 s in, right inside this race (BUGS.md, the splash
        # black-frame report, director direction 2026-11-12). The stub
        # client spins on a sentinel the spectacle stub creates at capture
        # start, so the liveness check -- before any sentinel exists --
        # passes, and the session then freezes it for the capture, so it
        # cannot exit on its own mid-capture; the spectacle stub therefore
        # ends it with SIGKILL -- the only thing that can stop a frozen
        # client -- and waits for it to be gone before returning, so the
        # session's own post-capture check deterministically sees a dead
        # client.
        pidfile = self.root / "client.pid"
        sentinel = self.root / "capture-started"
        fixture = self.root / "black.png"
        fixture.write_bytes(encode_png(320, 240, bytes(320 * 240 * 3)))
        self.stub(
            "plasmawindowed",
            f"echo $$ > {shlex.quote(str(pidfile))}; "
            f"n=0; while [ ! -f {shlex.quote(str(sentinel))} ] "
            "&& [ $n -lt 100000 ]; do n=$((n + 1)); done; exit 0",
        )
        self.stub(
            "spectacle",
            f"pause={shlex.quote(self.real_sleep)}; "
            'out=; while [ "$#" -gt 0 ]; do '
            'if [ "$1" = -o ]; then shift; out=$1; fi; shift; done; '
            f"touch {shlex.quote(str(sentinel))}; "
            f'pid=$(cat {shlex.quote(str(pidfile))}); '
            'kill -9 "$pid" 2>/dev/null; n=0; '
            'while kill -0 "$pid" 2>/dev/null && [ $n -lt 200 ]; do '
            '"$pause" 0.01; n=$((n + 1)); done; '
            f'cp "{fixture}" "$out"',
        )
        self.stub("dbus-run-session", 'for script; do :; done; eval "$script"')
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is entirely black",
            "client exited during the capture",
        )
        self.assertNotIn("did not paint", stderr)

    def test_unwritable_output_is_refused_before_installing(self):
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        for label, output in (
            ("a directory", self.root),
            ("an empty path", Path("")),
            ("a missing directory", self.root / "missing" / "out.png"),
        ):
            with self.subTest(label):
                status, stderr = call_main(render_surface.main, str(output))
                self.assertEqual(2, status)
                self.assertIn("render_surface: error: cannot write", stderr)
                self.assertFalse(marker.exists())
                self.assert_scratch_removed()

    def test_a_read_only_output_directory_is_refused_before_installing(self):
        # The last branch of `tools/render_output.py`'s `output_problem`: the
        # directory exists but this
        # user may not write it. `os.access` is the only check that sees that,
        # and a refusal here keeps the failure a named diagnostic instead of
        # letting the copy fail later with an errno the operator has to read
        # out of a traceback.
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        if os.access(locked, os.W_OK):
            self.skipTest("directory permissions are not enforced for this user")
        status, stderr = call_main(render_surface.main, str(locked / "out.png"))
        self.assertEqual(2, status)
        self.assertIn("render_surface: error: cannot write", stderr)
        self.assertIn("its directory is not writable", stderr)
        self.assertFalse(marker.exists())
        self.assert_scratch_removed()

    def hidden_files(self):
        """Return the dot-prefixed entries left in the scratch root."""
        return [name for name in os.listdir(self.root) if name.startswith(".")]

    def stub_capture(self, fill=0xDD):
        """Make the stubbed session write a valid 320x240 PNG where spectacle would.

        *fill* is the byte every colour channel holds; the default is the
        theme's painted window face, while 0 gives the all-black surface of a
        session that has not painted yet.
        """
        fixture = self.root / "capture.png"
        fixture.write_bytes(
            encode_png(320, 240, bytes([fill]) * (320 * 240 * 3))
        )
        # The session's argv ends with the shlex-joined `sh -c` line whose
        # positional parameters are the settle seconds, the surface path and
        # then the client: the capture stub extracts the surface path between
        # them, so the fixture lands where spectacle would have written it.
        self.stub(
            "dbus-run-session",
            'for a; do :; done; '
            "dest=$(printf '%s\\n' \"$a\" | sed -n "
            "'s/.* sh [^ ]* \\([^ ]*\\) plasmawindowed.*/\\1/p'); "
            f'cp "{fixture}" "$dest"',
        )
        return fixture

    def test_a_capture_is_copied_to_the_output(self):
        fixture = self.stub_capture()
        status, stderr, output = self.run_main()
        self.assertEqual((0, ""), (status, stderr))
        self.assertEqual(fixture.read_bytes(), output.read_bytes())
        self.assertEqual([], self.hidden_files())

    def test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file(self):
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        def die_midway(src, dst):
            dst.write(b"half a PNG")
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(shutil, "copyfileobj", die_midway):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_a_fifo_refusal_is_reported_as_a_failed_render(self):
        # The open guard refuses a non-regular capture source with ValueError,
        # not OSError; the CLI must still report it as a failed render with
        # its own diagnostic instead of tracebacking out of the exit contract.
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        with mock.patch.object(
            render_workflow,
            "publish",
            side_effect=ValueError(
                f"{self.root / 'surface.png'} cannot be read: "
                "not a regular file; refusing to open it"
            ),
        ):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertIn("not a regular file", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_make_render_passes_a_dash_leading_output_as_a_path(self):
        real_path = os.pathsep.join(
            entry
            for entry in os.environ["PATH"].split(os.pathsep)
            if entry != str(self.bin)
        )
        result = subprocess.run(
            ["make", "-n", "render", "RENDER_OUTPUT=-x.png"],
            cwd=repo_root.ROOT,
            env={**os.environ, "PATH": real_path},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertIn('render_surface.py "$@" -- "-x.png"', result.stdout)

    def test_session_receives_the_geometry_and_the_themed_configs(self):
        record = self.root / "args"
        self.stub(
            "dbus-run-session",
            f'echo "$@" > "{record}"; cat "$XDG_CONFIG_HOME/kwinrc" >> "{record}";'
            f' echo "$XDG_DATA_HOME $WAYLAND_DISPLAY $DISPLAY" >> "{record}"',
        )
        with mock.patch.dict(os.environ, {"WAYLAND_DISPLAY": "wl", "DISPLAY": ":9"}):
            self.run_main("--width", "64", "--height", "48", "--applet", "a b")
        text = record.read_text(encoding="utf-8")
        self.assertIn("--width 64 --height 48", text)
        self.assertIn("--socket render-surface", text)
        self.assertIn("theme=org.macos8.desktop", text)
        self.assertIn("--exit-with-session", text)
        last = text.splitlines()[-1].split()
        self.assertTrue(Path(last[0]).parent.name.startswith("render-surface-"))
        self.assertEqual(
            ["render-surface"],
            last[1:],
            "the session did not get its own socket, or DISPLAY leaked",
        )

    def test_session_ignores_a_config_search_path_from_the_environment(self):
        # `plasma-apply-colorscheme` and the session resolve config through
        # XDG_CONFIG_DIRS as well as XDG_CONFIG_HOME, so a caller-set search
        # path would let the host session's kdeglobals/kwinrc leak into a
        # render that is supposed to run against the throwaway config home
        # only. The render must drop it like it drops the caller's
        # WAYLAND_DISPLAY/DISPLAY.
        record = self.root / "config-dirs"
        self.stub(
            "dbus-run-session",
            f'printf "%s" "$XDG_CONFIG_DIRS" > "{record}"',
        )
        with mock.patch.dict(
            os.environ, {"XDG_CONFIG_DIRS": str(self.root / "ambient")}
        ):
            self.run_main()
        self.assertEqual(
            "",
            record.read_text(encoding="utf-8"),
            "the caller's XDG_CONFIG_DIRS leaked into the render session",
        )

    def test_session_pins_the_nested_bus_to_a_display_free_qt_platform(self):
        # The private bus hands the session environment to every service it
        # D-Bus-activates. A GUI service activated while WAYLAND_DISPLAY
        # points at the nested KWin socket (not yet listening, or gone
        # because the nested KWin exited) aborts in QGuiApplication and the
        # bus re-activates it in a coredump loop. The session therefore pins
        # the whole bus subtree to a display-free Qt platform, overriding a
        # caller's ambient value, and only the session script (the clients
        # that must draw on the nested compositor) sets wayland back.
        record = self.root / "qt-platform"
        self.stub(
            "dbus-run-session",
            f'printf "%s" "$QT_QPA_PLATFORM" > "{record}"',
        )
        with mock.patch.dict(
            os.environ, {"QT_QPA_PLATFORM": "wayland"}
        ):
            self.run_main()
        self.assertEqual(
            "offscreen",
            record.read_text(encoding="utf-8"),
            "the caller's QT_QPA_PLATFORM leaked into the render session, or the "
            "activated services were left free to open the nested Wayland socket",
        )

    def test_session_script_keeps_the_clients_on_the_nested_compositor_platform(self):
        # The nested bus's display-free QT_QPA_PLATFORM applies to the
        # session script too, so the script itself must re-pin the clients to
        # the nested compositor's wayland socket: without the override a
        # client would never align its platform with the wayland socket the
        # script's own comment says it needs.
        script = render_session.session_script()
        self.assertIn(
            "export QT_QPA_PLATFORM=wayland; ",
            script,
            "the session script no longer re-pins the client to the nested "
            "compositor's wayland platform, while the session subtree is pinned "
            "to a display-free one",
        )

    def test_install_ignores_a_destdir_from_the_environment(self):
        record = self.root / "make-env"
        self.stub("make", f'echo "[$DESTDIR] $*" > "{record}"')
        with mock.patch.dict(os.environ, {"DESTDIR": str(self.root / "stage")}):
            self.run_main()
        argv = record.read_text(encoding="utf-8")
        self.assertTrue(argv.startswith("[] install XDG_DATA_HOME="), argv)

    def test_install_ignores_makefiles_from_the_environment(self):
        marker = self.root / "makefiles-executed"
        injected_makefile = self.root / "injected.mk"
        injected_makefile.write_text(
            f"$(shell touch '{marker}')\n", encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" "$@"')
        with mock.patch.dict(os.environ, {"MAKEFILES": str(injected_makefile)}):
            self.run_main()
        self.assertFalse(
            marker.exists(), "caller-controlled MAKEFILES ran during the render install"
        )

    def test_install_ignores_a_destdir_from_the_outer_make_command_line(self):
        # `make DESTDIR=/stage render` exports the command-line variable through
        # MAKEFLAGS as well as the environment, so dropping DESTDIR alone leaves
        # the inner `make install` staging the theme outside the scratch home.
        # Run the real make so it imports MAKEFLAGS the way the outer one would.
        record = self.root / "make-destdir"
        makefile = self.root / "install.mk"
        makefile.write_text(
            f'install:\n\t@echo "[$(DESTDIR)]" > "{record}"\n', encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" -f "{makefile}" "$@"')
        with mock.patch.dict(
            os.environ, {"MAKEFLAGS": f"-- DESTDIR={self.root / 'stage'}"}
        ):
            self.run_main()
        self.assertEqual("[]", record.read_text(encoding="utf-8").strip())

    def test_timeout_kills_the_session_group_and_exits_1(self):
        # The session must write its pid before the one-second timeout fires,
        # or the timeout kills it first and the read below has nothing to
        # check. A loaded host can lose that race, so retry with a fresh
        # pidfile per attempt; each timed-out attempt has already had its
        # whole group killed by run_logged, so retrying leaks nothing. The
        # deadline bounds the retries, so a host that never starts the session
        # fails instead of spinning.
        started = time.monotonic()
        deadline = started + 30
        while True:
            self.assertLess(
                time.monotonic(),
                deadline,
                "the session never wrote its pid before the timeout",
            )
            pidfile = self.root / f"pid-{time.monotonic_ns()}"
            self.stub(
                "dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60'
            )
            status, stderr, output = self.run_main(
                "--settle", "0", "--timeout", "1"
            )
            self.assert_failed_run(
                status, stderr, output, 1, "render timed out after 1s",
            )
            try:
                pid = int(pidfile.read_text(encoding="utf-8"))
            except (FileNotFoundError, ValueError):
                # The timeout fired before the session finished its setup, so
                # this attempt proved nothing about the group kill.
                continue
            break
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_sigterm_kills_the_session_group_and_removes_scratch(self):
        pidfile = self.root / "pid"
        self.stub("dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(os.environ, TMPDIR=str(self.scratch_parent))
        argv = [sys.executable, render_surface.__file__, str(self.root / "o.png")]
        with process_runner.running(
            argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ) as process:
            pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="render", child="session"
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assert_scratch_removed()
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)



if __name__ == "__main__":
    unittest.main()
