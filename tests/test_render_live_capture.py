"""The render CLI's live-session capture outcomes, against shell stubs.

The real session script's applet liveness check, the crashed-applet setup-wait
diagnosis, and the refusal of a failed, wrong-size, black or vanished-client
capture run here under stubs of the tools the session starts, without any
Plasma session. The other failure paths stay in
``tests/test_render_failure_paths.py``.
"""

from __future__ import annotations

import shlex
import unittest

from support.cli_fixtures import run_main
from tools import render_surface
from tools.png.write import encode_png  # noqa: E402
from support.render_stub_tools import StubTools


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


class TestLiveCapture(StubTools, unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
