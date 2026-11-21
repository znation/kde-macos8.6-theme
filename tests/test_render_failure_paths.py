"""The render CLI's failure-path suite, against shell stubs of the external tools.

``tools/render_surface.py``'s argument handling and its workflow's failure
behavior -- a missing or unrunnable tool, an unusable scratch directory, an
unpainted or failed capture, publication that must keep the previous output
whole -- run here against stub executables, without any Plasma session; the
pixel gates that drive the same CLI against a real headless session live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py`` beside the ``Test...DialogRender``
gates. Environment-isolation cases live in ``tests/test_render_environment.py``. The output-publication cases (refusal
before installing, copy-over, the previous output kept, ``make render`` passing
a dash-leading output) live in ``tests/test_render_output_cli.py``. The per-mode
session wiring (the client each mode launches and the configs it writes) lives in
``tests/test_render_session_modes.py``.
"""

from __future__ import annotations

import errno
import os
import shlex
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from support import process_runner
from support.cli_fixtures import assert_missing_tool_named, call_main, run_main
from tools import (
    render_setup,
    render_surface,
    render_workflow,
)  # noqa: E402
from tools.png.write import encode_png  # noqa: E402
from support.render_stub_tools import StubTools


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


class TestFailurePaths(StubTools, unittest.TestCase):
    def assert_unrunnable_command_is_reported(self, command, diagnostic):
        """Check the CLI handles a found executable that cannot be started."""
        executable = self.bin / command
        executable.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)

        # Keep execvp from falling through to a real command after ENOENT.
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}):
            status, stderr, output = self.run_main()

        self.assert_failed_run(status, stderr, output, 2, diagnostic)

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
        # The session exits 0 but never writes the PNG. The diagnostic must
        # say so and report the render log's size, so a zero-status run with
        # no capture is not indistinguishable from a session that logged.
        # The stub logs exactly six bytes ("hello\n") before exiting 0.
        self.stub("dbus-run-session", "printf 'hello\\n'; exit 0")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "not a readable PNG",
            "the session exited 0 and wrote no capture",
            "(render log 6 bytes)",
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
        self.stub("dbus-monitor", "exit 0")
        self.stub("dbus-run-session", 'for script; do :; done; eval "$script"')

    def test_a_running_applet_is_still_captured(self):
        self.stub_live_session("exec sleep 60")
        status, stderr, output = self.run_main("--settle", "0")
        self.assertEqual((0, ""), (status, stderr))
        self.assertTrue(output.exists())
        self.assert_scratch_removed()

    def test_a_painted_capture_reports_the_session_log_on_stdout(self):
        # A passing render keeps its session log's tail in the run's output,
        # so a later pixel mismatch can show which settle path ran. The
        # dbus-run-session stub prints a marker into the log before it starts
        # the session; the marker must reach stdout.
        self.stub_live_session("exec sleep 60")
        self.stub(
            "dbus-run-session",
            "printf 'settle marker\\n'; for script; do :; done; eval \"$script\"",
        )
        output = self.root / "out.png"
        result = run_main(
            render_surface.main, "render_surface", [str(output), "--settle", "0"]
        )
        self.assertEqual((0, ""), (result.returncode, result.stderr))
        self.assertTrue(output.exists())
        self.assertIn("render_surface: note: render log", result.stdout)
        self.assertIn("render_surface: note:   settle marker", result.stdout)

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
        # client. The stub spectacle takes the pid from the session
        # shell's RENDER_SESSION_CLIENT_PID export, not from a pidfile the
        # client writes: under load the freeze can land before the
        # client's first instruction, and a pidfile read then sees nothing
        # (the 2026-11-12 parallel-gate red runs, BUGS.md).
        sentinel = self.root / "capture-started"
        fixture = self.root / "black.png"
        fixture.write_bytes(encode_png(320, 240, bytes(320 * 240 * 3)))
        self.stub(
            "plasmawindowed",
            f"n=0; while [ ! -f {shlex.quote(str(sentinel))} ] "
            "&& [ $n -lt 100000 ]; do n=$((n + 1)); done; exit 0",
        )
        self.stub(
            "spectacle",
            f"pause={shlex.quote(self.real_sleep)}; "
            'out=; while [ "$#" -gt 0 ]; do '
            'if [ "$1" = -o ]; then shift; out=$1; fi; shift; done; '
            f"touch {shlex.quote(str(sentinel))}; "
            'pid=${RENDER_SESSION_CLIENT_PID:?}; '
            'kill -9 "$pid" 2>/dev/null; n=0; '
            'while kill -0 "$pid" 2>/dev/null && [ $n -lt 200 ]; do '
            '"$pause" 0.01; n=$((n + 1)); done; '
            f'cp "{fixture}" "$out"',
        )
        self.stub("dbus-monitor", "exit 0")
        self.stub("dbus-run-session", 'for script; do :; done; eval "$script"')
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is entirely black",
            "client exited during the capture",
        )
        self.assertNotIn("did not paint", stderr)

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
        log = self.root / "render.log"
        with log.open("w", encoding="utf-8") as err, process_runner.running(
            argv, env=env, stdout=subprocess.DEVNULL, stderr=err
        ) as process:
            pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="render", child="session", log=log
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assert_scratch_removed()
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)



if __name__ == "__main__":
    unittest.main()
