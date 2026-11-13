"""Tests for tools/apply_theme.py, its apply_optional boundary and the
`make apply` target.

`apply_theme.main` runs the re-selection commands against fake
executables on `PATH`, which record their argv and the
`DBUS_SESSION_BUS_ADDRESS` they saw, so the order, the ``--resetLayout``
omission, the session-bus default and the failure paths are pinned without a
running Plasma session. The Makefile tests drive the `apply` target through
`theme_install`, whose child processes run under the suite's timeout.
"""

from __future__ import annotations

import contextlib
import io
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
from tools import (
    apply_theme,
    diagnostics,
    required_command,
    apply_optional,
    theme_defaults,
)


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
        patch = mock.patch.dict(
            os.environ,
            {
                "PATH": str(self.bin),
                "HOME": str(self.home),
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


class TestCommandOrder(StubTools):
    def test_runs_the_steps_in_order(self):
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            [
                "lookandfeeltool -a org.macos8.desktop",
                "kwriteconfig6 --file kdeglobals --group General --key fixed "
                "JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium",
                "plasma-apply-colorscheme MacOS8",
                "plasma-apply-desktoptheme org.macos8.desktop",
                "kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 "
                "--key ButtonsOnLeft X",
                "kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 "
                "--key ButtonsOnRight AL",
                "kvantummanager --set org.macos8.desktop",
                "qdbus6 org.kde.KWin /KWin reconfigure",
            ],
            self.recorded(),
        )

    def test_the_button_layout_is_the_one_the_global_theme_declares(self):
        # The apply writes the pair the shipped contents/defaults already
        # names; a drift between the two would silently restore the stock
        # right-hand button cluster the theme exists to replace.
        self.assertEqual(
            {"ButtonsOnLeft": "X", "ButtonsOnRight": "AL"},
            dict(apply_theme.DECORATION_BUTTONS),
        )
        section = theme_defaults.defaults_groups()[
            (apply_theme.DECORATION_FILE, apply_theme.DECORATION_GROUP)
        ]
        self.assertEqual(
            tuple((key, section[key]) for key, _ in apply_theme.DECORATION_BUTTONS),
            apply_theme.DECORATION_BUTTONS,
        )

    def test_the_fixed_font_selection_is_the_one_the_global_theme_declares(self):
        # The apply writes the fixed-width selection the shipped
        # contents/defaults already names, because the look-and-feel apply
        # publishes no defaults' font key on the installed Plasma; a drift
        # between the two would leave the selection silent or wrong.
        self.assertEqual(
            (apply_theme.FIXED_FILE, apply_theme.FIXED_GROUP, apply_theme.FIXED_KEY),
            ("kdeglobals", "General", "fixed"),
        )
        section = theme_defaults.defaults_groups()[
            (apply_theme.FIXED_FILE, apply_theme.FIXED_GROUP)
        ]
        self.assertEqual(section[apply_theme.FIXED_KEY], apply_theme.FIXED_VALUE)

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
            diagnostics.tempfile, "mkdtemp", side_effect=OSError("no space left")
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

    def test_a_failing_button_layout_write_exits_1_and_stops_before_the_optional_steps(
        self,
    ):
        # The layout write is required: a kwinrc the apply cannot reach would
        # otherwise leave the stock button cluster in place with no
        # diagnostic. The stub fails only the kwinrc writes, so the earlier
        # fixed-width selection write succeeds and this failure path is the
        # layout's own.
        self.stub(
            "kwriteconfig6",
            'case "$*" in *kwinrc*) echo cannot write kwinrc >&2\nexit 6;; esac\nexit 0',
        )
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 6", stderr)
        self.assertIn("cannot write kwinrc", stderr)
        recorded = self.recorded()
        self.assertEqual(
            "kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 "
            "--key ButtonsOnLeft X",
            recorded[-1],
        )
        self.assertNotIn("kvantummanager --set org.macos8.desktop", recorded)

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


class TestKvantumDataHomeNote(StubTools):
    """The apply-time note when Kvantum can only resolve our theme from the
    default data home.

    Kvantum joins its literal ``$HOME/.local/share/themes`` search path from
    ``$HOME``, so a selection written under another data home still succeeds
    while the engine silently keeps drawing its built-in default theme. These
    drive ``apply_optional.select_kvantum_theme`` directly through the
    stubbed ``kvantummanager`` machinery above, one env shape per test, and
    assert the selection argv and status never change with the note.
    """

    def note(self, home, resolved):
        """Return the one-note full stderr line for *home* and *resolved*."""
        return (
            "apply_theme: note: the Kvantum engine reads its theme directory "
            f"only under the default data home {home}/.local/share, not the "
            f"resolved {resolved}; widgets draw Kvantum's built-in default "
            "theme until themes/org.macos8.desktop/Kvantum exists there"
        )

    def select(self):
        """Run the selection against the stubbed PATH, returning (status, stderr)."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = apply_optional.select_kvantum_theme(
                self.root, dict(os.environ), apply_theme.COMMAND_TIMEOUT
            )
        return status, stderr.getvalue()

    def test_a_non_default_absolute_data_home_prints_the_note(self):
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual([self.note(self.home, self.data)], stderr.splitlines())
        self.assertEqual(
            ["kvantummanager --set org.macos8.desktop"], self.recorded()
        )

    def theme_directory_at_default(self):
        """Create the theme directory the engine's default home resolves."""
        directory = (
            self.home / ".local" / "share" / "themes" / "org.macos8.desktop" / "Kvantum"
        )
        directory.mkdir(parents=True)
        return directory

    def test_a_theme_already_at_the_default_data_home_stays_silent(self):
        # The note exists for the selection the engine's literal search path
        # cannot reach; when the default home already holds the theme
        # directory (an earlier install under the default data home) the
        # engine can reach the selection and the warning would be false.
        self.theme_directory_at_default()
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)
        self.assertEqual(
            ["kvantummanager --set org.macos8.desktop"], self.recorded()
        )

    def test_a_wrongly_named_directory_at_the_default_home_still_warns(self):
        # Only the exact themes/org.macos8.desktop/Kvantum path silences the
        # note; a sibling-named theme cannot be what the engine resolves, so
        # the check must not stop at the themes directory or the theme name.
        for layout in (
            "themes/org.macos8.desktop/not-Kvantum",
            "themes/other.theme/Kvantum",
            "Kvantum/org.macos8.desktop",
        ):
            with self.subTest(layout=layout):
                (self.home / ".local" / "share" / layout).mkdir(parents=True)
                status, stderr = self.select()
                self.assertEqual(0, status, stderr)
                self.assertEqual(
                    [self.note(self.home, self.data)], stderr.splitlines()
                )

    def test_the_default_data_home_below_home_stays_silent(self):
        with mock.patch.dict(
            os.environ, {"XDG_DATA_HOME": str(self.home / ".local" / "share")}
        ):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_unset_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("XDG_DATA_HOME", None)
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_empty_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": ""}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_relative_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": "relative/data"}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_unset_home_leaves_no_default_to_name_and_stays_silent(self):
        # The resolved home comes from the absolute XDG_DATA_HOME alone, but
        # without a usable HOME there is no default to name, so the check
        # must skip instead of printing a half-substituted note.
        with mock.patch.dict(os.environ):
            os.environ.pop("HOME", None)
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_relative_home_leaves_no_default_to_name_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"HOME": "relative/home"}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_falling_back_home_with_no_data_home_stays_silent(self):
        # An empty/relative XDG_DATA_HOME with an unusable HOME resolves
        # neither side of the comparison.
        for data_home in ("", "relative/data"):
            with self.subTest(data_home=data_home), mock.patch.dict(
                os.environ, {"HOME": "relative/home", "XDG_DATA_HOME": data_home}
            ):
                status, stderr = self.select()
            self.assertEqual(0, status, stderr)
            self.assertEqual("", stderr)

    def test_a_missing_kvantummanager_prints_no_data_home_note(self):
        # The missing-engine remedy already names everything the operator has
        # to do; the data-home warning must not add a second note about a
        # selection that never ran.
        self.unstub("kvantummanager")
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual(1, len(stderr.splitlines()), stderr)
        self.assertIn("kvantummanager is not on PATH", stderr)
        self.assertNotIn("default data home", stderr)

    def test_a_failing_selection_still_prints_the_data_home_note(self):
        self.stub("kvantummanager", "echo set failed >&2\nexit 5")
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertIn(self.note(self.home, self.data), stderr.splitlines())
        self.assertIn("kvantummanager --set exited 5", stderr)
        self.assertIn("fall back", stderr)


class TestTimeoutPaths(StubTools):
    """The ``run_logged`` timeout result (``None``) at the three call sites.

    ``run_logged`` returns ``None`` when a command exceeds the 60s
    ``COMMAND_TIMEOUT``. A real timeout would need a hung child and the full
    timeout, so these patch it to report the timeout directly and pin the
    diagnostic each call site prints: the shared required-command runner for
    the steps, and ``apply_optional.run_logged`` for the best-effort
    selections.
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

        with mock.patch.object(
            apply_optional, "run_logged", side_effect=run_logged
        ):
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

        with mock.patch.object(
            apply_optional, "run_logged", side_effect=run_logged
        ):
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
        # The first steps ran, then the unrunnable one stopped the run: no
        # later selection may be attempted after the failure.
        self.assertEqual(
            [
                "lookandfeeltool -a org.macos8.desktop",
                "kwriteconfig6 --file kdeglobals --group General --key fixed "
                "JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium",
            ],
            self.recorded(),
        )

    def test_an_unrunnable_fixed_font_write_exits_2_without_a_traceback(self):
        # The fixed-width selection write is required too: an unrunnable
        # kwriteconfig6 stops the run after the global-theme step with the
        # tool's own exit-2 diagnostic, and no later selection runs.
        self.broken_stub("kwriteconfig6")

        status, stderr = call_main(apply_theme.main)

        self.assertEqual(2, status)
        self.assertIn("cannot run kwriteconfig6", stderr)
        self.assertIn("apply_theme: error:", stderr)
        self.assertNotIn("Traceback", stderr)
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
        search path, so the name the best-effort selection picks
        (``apply_optional``) must be that package's directory name;
        otherwise the selection silently misses."""
        package_root = Path(apply_theme.ROOT) / "theme" / "kvantum"
        shipped = {
            entry.name for entry in package_root.iterdir() if entry.is_dir()
        }
        self.assertEqual({apply_optional.KVANTUM_THEME}, shipped)


class TestOptionalSelectionHelpers(unittest.TestCase):
    """Direct coverage of the extracted apply_optional boundary.

    The stub-tool classes above exercise the boundary through
    ``apply_theme.main``; these call the module's own functions against a
    narrowed PATH, so the notes and the always-0 status are pinned beside the
    extraction rather than only through the orchestrator.
    """

    def test_run_optional_selections_notes_both_missing_tools_and_returns_0(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        empty_bin = root / "bin"
        empty_bin.mkdir()
        env = {"PATH": str(empty_bin)}
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with contextlib.redirect_stderr(stderr):
                status = apply_optional.run_optional_selections(
                    root, dict(os.environ), 60.0
                )
        self.assertEqual(0, status)
        text = stderr.getvalue()
        self.assertIn("apply_theme: note:", text)
        self.assertIn("kvantummanager is not on PATH", text)
        self.assertIn("neither qdbus6 nor qdbus is on PATH", text)

    def test_run_best_effort_success_prints_nothing(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        stub_bin = root / "bin"
        stub_bin.mkdir()
        stub = stub_bin / "tool"
        stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": str(stub_bin)}, clear=False):
            with contextlib.redirect_stderr(stderr):
                apply_optional.run_best_effort(
                    root,
                    dict(os.environ),
                    ["tool"],
                    "tool.log",
                    60.0,
                    label="tool call",
                    consequence="nothing happens",
                )
        self.assertEqual("", stderr.getvalue())
        self.assertTrue((root / "tool.log").exists())


class TestReconfigureKwin(unittest.TestCase):
    """Direct coverage of ``apply_optional.reconfigure_kwin``.

    The orchestrator path above only reaches the function's missing-tool
    arrow (both qdbus binaries absent), so the branch that runs a found
    qdbus never executes in the suite: its pinned ``org.kde.KWin`` reconfigure
    argv, its qdbus6-over-qdbus preference, its ``KWin reconfigure`` label and
    its note-on-failure policy are believed, not checked, until a stub qdbus
    runs. These tests narrow PATH to stub scripts; each stub prints a marker
    (or the reconfigure argv it received) to stdout, which ``run_logged``
    captures in the scratch ``qdbus.log``.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="reconfigure-kwin-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def _stub(self, name, body):
        stub = self.bin / name
        stub.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        return stub

    def _run(self):
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}, clear=False):
            with contextlib.redirect_stderr(stderr):
                status = apply_optional.reconfigure_kwin(
                    self.root, {"PATH": str(self.bin)}, 60.0
                )
        return status, stderr.getvalue()

    def test_a_found_qdbus6_receives_the_kwin_reconfigure_argv(self):
        self._stub("qdbus6", 'echo "$@"')
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertEqual("org.kde.KWin /KWin reconfigure\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))
        self.assertEqual("", text)

    def test_qdbus6_is_preferred_over_qdbus(self):
        self._stub("qdbus6", "echo picked:qdbus6")
        self._stub("qdbus", "echo picked:qdbus")
        status, _ = self._run()
        self.assertEqual(0, status)
        self.assertEqual("picked:qdbus6\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))

    def test_only_the_qdbus_fallback_still_reaches_kwin(self):
        self._stub("qdbus", 'echo "$@"')
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertEqual("org.kde.KWin /KWin reconfigure\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))
        self.assertEqual("", text)

    def test_a_failing_reconfigure_is_a_note_though_the_status_stays_0(self):
        self._stub("qdbus6", "exit 3")
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertIn(
            "apply_theme: note: KWin reconfigure exited 3; KWin reloads the "
            "decoration on its next start",
            text,
        )


class TestMakeApply(unittest.TestCase):
    def test_a_hostile_DESTDIR_value_is_refused_without_running_its_shell(self):
        """Refuse a DESTDIR carrying shell quoting without executing it.

        A DESTDIR pasted into a double-quoted recipe word would close the
        recipe's own quotes, so the Makefile refuses any value carrying a
        recipe-shell metacharacter at make level, before any recipe runs;
        this test's canary file must not be created.
        """
        tmp = tempfile.mkdtemp(prefix="apply-hostile-destdir-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        canary = Path(tmp) / "injected"
        hostile = f'"; touch "{canary}"; echo "'
        result = theme_install.run_make(
            ["apply", f"DESTDIR={hostile}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR contains a shell metacharacter", result.stderr)
        self.assertIn(hostile, result.stderr)
        self.assertFalse(canary.exists(), hostile)

    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix="apply-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = theme_install.run_make(
            ["apply", f"DESTDIR={destdir}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertNotIn("apply_theme.py", result.stdout + result.stderr)

    def test_dry_run_applies_every_surface_after_installing(self):
        result = theme_install.run_make(
            ["-n", "apply"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        steps = [
            "--no-print-directory install",
            "tools/apply_theme.py",
            "tools/apply_gtk.py",
            "tools/apply_cursor.py --optional",
            "tools/install_firefox.py --optional",
        ]
        positions = []
        for step in steps:
            with self.subTest(step=step):
                self.assertIn(step, result.stdout)
                positions.append(result.stdout.index(step))
        self.assertEqual(sorted(positions), positions, result.stdout)
        self.assertNotIn("apply_keymap.py", result.stdout)

    def test_keymap_targets_are_removed(self):
        help_result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, help_result)
        self.assertNotIn("apply-keymap", help_result.stdout)
        self.assertNotIn("remove-keymap", help_result.stdout)
        for target in ("apply-keymap", "remove-keymap"):
            with self.subTest(target=target):
                result = theme_install.run_make([target], env=theme_install.make_env())
                self.assertNotEqual(0, result.returncode)
                self.assertIn("No rule to make target", result.stderr)

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
