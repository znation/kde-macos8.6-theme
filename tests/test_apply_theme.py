"""Tests for tools/apply_theme.py and the `make apply` target.

`apply_theme.main` runs the re-selection commands against fake
executables on `PATH`, which record their argv and the
`DBUS_SESSION_BUS_ADDRESS` they saw, so the order, the ``--resetLayout``
omission, the session-bus default and the failure paths are pinned without a
running Plasma session. The Makefile tests drive the `apply` target through
`theme_install`, whose child processes run under the suite's timeout.
"""

from __future__ import annotations

import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import process_runner, theme_install
from support.cli_fixtures import assert_missing_tool_named, call_main
from support.process_assertions import assert_failed, assert_succeeded
from support.recorded_lines import recorded_lines
from tools import apply_theme, required_command


class StubTools(unittest.TestCase):
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
        self.calls = self.root / "calls"
        self.env_log = self.root / "env"
        for name in apply_theme.REQUIRED_TOOLS:
            self.stub(name)
        self.stub("qdbus6")
        self.stub("kvantummanager")
        patch = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
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


class TestCommandOrder(StubTools):
    def test_runs_the_steps_in_order(self):
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            [
                "lookandfeeltool -a org.macos8.desktop",
                "plasma-apply-colorscheme MacOS8",
                "plasma-apply-desktoptheme org.macos8.desktop",
                "kvantummanager --set org.macos8.desktop",
                "qdbus6 org.kde.KWin /KWin reconfigure",
            ],
            self.recorded(),
        )

    def test_never_passes_reset_layout(self):
        call_main(apply_theme.main)
        self.assertNotIn("--resetLayout", " ".join(self.recorded()))

    def test_falls_back_to_qdbus_when_qdbus6_is_missing(self):
        self.unstub("qdbus6")
        self.stub("qdbus")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            ["qdbus org.kde.KWin /KWin reconfigure"], self.recorded()[-1:]
        )


class TestFailurePaths(StubTools):
    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # Creating the scratch directory can fail before there is anything to
        # clean up (a full or unwritable TMPDIR). It must be this tool's own
        # exit-2 diagnostic, not a traceback that skips the exit contract.
        with mock.patch.object(
            apply_theme.tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(2, status)
        self.assertIn("cannot create a scratch directory", stderr)
        self.assertIn("no space left", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_failing_required_command_exits_1_with_the_output_tail(self):
        self.stub(
            "plasma-apply-colorscheme",
            "echo colorscheme exploded >&2\nexit 4",
        )
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(1, status)
        self.assertIn("plasma-apply-colorscheme exited 4", stderr)
        self.assertIn("colorscheme exploded", stderr)

    def test_missing_qdbus_prints_a_note_and_exits_0(self):
        self.unstub("qdbus6")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)
        self.assertIn("qdbus", stderr)

    def test_missing_kvantummanager_prints_a_note_and_exits_0(self):
        self.unstub("kvantummanager")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)
        self.assertIn("kvantummanager", stderr)
        self.assertNotIn("kvantummanager --set", " ".join(self.recorded()))

    def test_failing_qdbus_prints_a_note_and_exits_0(self):
        self.stub("qdbus6", "echo reconfigure failed >&2\nexit 3")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)

    def test_failing_kvantummanager_prints_a_note_and_exits_0(self):
        self.stub("kvantummanager", "echo set failed >&2\nexit 5")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)
        self.assertIn("kvantummanager --set exited 5", stderr)
        self.assertIn("fall back", stderr)


class TestTimeoutPaths(StubTools):
    """The ``run_logged`` timeout result (``None``) at the three call sites.

    ``run_logged`` returns ``None`` when a command exceeds the 60s
    ``COMMAND_TIMEOUT``. A real timeout would need a hung child and the full
    timeout, so these patch it to report the timeout directly and pin the
    diagnostic each call site prints: the shared required-command runner for
    the steps, and ``apply_theme.run_logged`` for the best-effort selections.
    ``test_render_surface`` covers the process-group kill that produces the
    ``None`` in the first place.
    """

    def test_a_required_step_timeout_exits_1_naming_the_tool(self):
        with mock.patch.object(
            required_command, "run_logged", return_value=None
        ):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(1, status)
        self.assertIn(
            f"lookandfeeltool timed out after {apply_theme.COMMAND_TIMEOUT:g}s",
            stderr,
        )
        self.assertNotIn("Traceback", stderr)

    def test_a_kwin_reconfigure_timeout_prints_a_note_and_exits_0(self):
        def run_logged(argv, env, log, timeout, cwd):
            # The three required steps succeed; the KWin reconfigure times out.
            return None if argv[0].endswith("qdbus6") else 0

        with mock.patch.object(apply_theme, "run_logged", side_effect=run_logged):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn(
            f"KWin reconfigure timed out after {apply_theme.COMMAND_TIMEOUT:g}s",
            stderr,
        )

    def test_a_kvantum_selection_timeout_prints_a_note_and_exits_0(self):
        def run_logged(argv, env, log, timeout, cwd):
            # The three required steps succeed; the Kvantum selection times out.
            return None if argv[0].endswith("kvantummanager") else 0

        with mock.patch.object(apply_theme, "run_logged", side_effect=run_logged):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn(
            "kvantummanager --set timed out after "
            f"{apply_theme.COMMAND_TIMEOUT:g}s",
            stderr,
        )
        self.assertIn("fall back", stderr)


class TestUnrunnableTools(StubTools):
    """A tool on PATH that cannot be started is a diagnostic, not a traceback.

    ``report_missing_tool`` only proves each command exists; a corrupt binary
    or a script whose interpreter is missing still fails in ``Popen``. The
    required steps must report that as the tool's own exit-2 diagnostic, and
    the best-effort selections must treat it like any other failure so an
    otherwise successful apply still exits 0.
    """

    def test_an_unrunnable_required_step_exits_2_without_a_traceback(self):
        self.broken_stub("plasma-apply-colorscheme")

        status, stderr = call_main(apply_theme.main)

        self.assertEqual(2, status)
        self.assertIn("cannot run plasma-apply-colorscheme", stderr)
        self.assertIn("apply_theme: error:", stderr)
        self.assertNotIn("Traceback", stderr)
        # The first step ran, then the unrunnable one stopped the run: no
        # later selection may be attempted after the failure.
        self.assertEqual(
            ["lookandfeeltool -a org.macos8.desktop"], self.recorded()
        )

    def test_an_unrunnable_kwin_reconfigure_is_a_note_and_exits_0(self):
        self.broken_stub("qdbus6")

        status, stderr = call_main(apply_theme.main)

        self.assertEqual(0, status, stderr)
        self.assertIn("KWin reconfigure could not be started", stderr)
        self.assertIn("KWin reloads the decoration on its next start", stderr)
        self.assertNotIn("Traceback", stderr)


class TestTermination(StubTools):
    """A SIGTERM while a command runs unwinds through the cleanup.

    ``run_logged`` starts each command in its own session. Without
    ``exit_on_termination``, SIGTERM would kill ``apply_theme`` before its
    ``finally`` blocks ran: the command would keep running and its scratch
    directory would be left behind. This runs the CLI as a child and signals
    it mid-command, so the handler, the group kill and the scratch removal are
    all exercised together rather than mocked.
    """

    def assert_sigterm_cleanup(self, tool, body):
        """Signal apply_theme once its stub *tool* has started; assert cleanup."""
        scratch_parent = self.root / "tmp"
        scratch_parent.mkdir()
        pidfile = self.root / "step.pid"
        self.stub(tool, f'echo $$ > "{pidfile}"; {body}')
        env = dict(os.environ, TMPDIR=str(scratch_parent))
        step_pid = None

        def kill_step():
            if step_pid is not None:
                try:
                    os.kill(step_pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_step)
        with process_runner.running(
            [sys.executable, apply_theme.__file__],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) as process:
            step_pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="apply_theme", child="step"
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)

        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assertEqual([], os.listdir(scratch_parent))
        with self.assertRaises(ProcessLookupError):
            os.kill(step_pid, 0)

    def test_sigterm_kills_the_step_group_and_removes_scratch(self):
        self.assert_sigterm_cleanup("lookandfeeltool", "exec /bin/sleep 60")

    def test_sigterm_during_a_best_effort_selection_also_cleans_up(self):
        # Kvantum's selection and KWin's reconfigure are best-effort, but an
        # interrupt must still leave no command running and no scratch behind;
        # their shared helper must not swallow the SystemExit on the way out.
        self.assert_sigterm_cleanup("kvantummanager", "exec /bin/sleep 60")


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_required_tool_and_exits_2(self):
        assert_missing_tool_named(self, apply_theme.main, apply_theme.REQUIRED_TOOLS)


class TestSessionBus(StubTools):
    def _apply_with_runtime(self, runtime):
        """Run `apply_theme.main` with *runtime* as `XDG_RUNTIME_DIR` and no
        `DBUS_SESSION_BUS_ADDRESS`, asserting a clean exit."""
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": str(runtime)}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)

    def test_defaults_the_address_from_an_absolute_runtime_dir(self):
        runtime = self.root / "rt"
        runtime.mkdir()
        (runtime / "bus").write_text("", encoding="utf-8")
        self._apply_with_runtime(runtime)
        self.assertIn(
            f"qdbus6 DBUS=unix:path={runtime}/bus", self.env_recorded()
        )

    def test_keeps_an_existing_address(self):
        with mock.patch.dict(
            os.environ,
            {"DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"},
            clear=False,
        ):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=unix:path=/existing", self.env_recorded())

    def test_does_not_default_from_a_relative_runtime_dir(self):
        self._apply_with_runtime("relative")
        self.assertIn("qdbus6 DBUS=", self.env_recorded())
        self.assertNotIn("unix:path=relative", self.env_recorded())

    def test_does_not_default_from_an_empty_runtime_dir(self):
        # An empty XDG_RUNTIME_DIR is not an absolute directory, so it cannot
        # name a bus socket; the address stays unset instead of becoming a
        # path relative to the current directory.
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": ""}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=", self.env_recorded())

    def test_does_not_default_without_a_runtime_dir(self):
        # A non-login shell may carry neither variable. The lookup must treat
        # the absent XDG_RUNTIME_DIR as "no runtime directory" instead of
        # raising a KeyError out of the apply.
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("XDG_RUNTIME_DIR", None)
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=", self.env_recorded())

    def test_an_empty_address_is_defaulted_like_an_unset_one(self):
        # An exported but empty DBUS_SESSION_BUS_ADDRESS names no bus either,
        # so the runtime directory's socket must still be used.
        runtime = self.root / "rt"
        runtime.mkdir()
        (runtime / "bus").write_text("", encoding="utf-8")
        with mock.patch.dict(
            os.environ,
            {
                "XDG_RUNTIME_DIR": str(runtime),
                "DBUS_SESSION_BUS_ADDRESS": "",
            },
            clear=False,
        ):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn(
            f"qdbus6 DBUS=unix:path={runtime}/bus", self.env_recorded()
        )

    def test_does_not_default_when_the_bus_socket_is_absent(self):
        runtime = self.root / "empty-runtime"
        runtime.mkdir()
        self._apply_with_runtime(runtime)
        self.assertIn("qdbus6 DBUS=", self.env_recorded())


class TestKvantumSelection(unittest.TestCase):
    def test_the_selected_theme_is_the_shipped_package(self):
        """`make install` copies the `theme/kvantum/` package into Kvantum's
        search path, so the name `apply_theme` selects must be that package's
        directory name; otherwise the selection silently misses."""
        package_root = Path(apply_theme.ROOT) / "theme" / "kvantum"
        shipped = {
            entry.name for entry in package_root.iterdir() if entry.is_dir()
        }
        self.assertEqual({apply_theme.KVANTUM_THEME}, shipped)


class TestMakeApply(unittest.TestCase):
    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix="apply-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = theme_install.run_make(
            ["apply", f"DESTDIR={destdir}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertNotIn("apply_theme.py", result.stdout + result.stderr)

    def test_dry_run_shows_install_before_the_script(self):
        result = theme_install.run_make(
            ["-n", "apply"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_theme.py", result.stdout)
        self.assertLess(
            result.stdout.index("--no-print-directory install"),
            result.stdout.index("tools/apply_theme.py"),
        )

    def test_help_lists_apply(self):
        result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, result)
        self.assertTrue(
            any(
                line.startswith("  apply ")
                for line in result.stdout.splitlines()
            ),
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
