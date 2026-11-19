"""Tests for the render CLI and throwaway render workflow units.

The render's end-to-end capture gates live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py``, their failure orchestration in
``tests/test_render_failure_paths.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: KWin session command construction in
``tools/render_session.py``, the capture paint check in
``tools/render_workflow.py``. The session command and dialog argv checks
live in ``tests/test_render_session_command.py``, the scratch-session
setup checks live in ``tests/test_render_session_setup.py``, and the
session theme-source checks live in ``tests/test_render_session_theme_sources.py``,
and the CLI calculator applet preflight checks live in
``tests/test_render_applet_preflight.py``.
Dialog-mode argument checks live in ``tests/test_render_dialog_arguments.py``.
The ``--desktop`` and ``--splash`` argument checks live in
``tests/test_render_fixed_client_modes.py``. General CLI argument checks live
in ``tests/test_render_cli_arguments.py``.
"""

from __future__ import annotations

import os
import shlex
import shutil
import signal
import subprocess
import threading
import sys
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import (
    render_session,
    render_workflow,
)  # noqa: E402


class TestCapturePaintCheck(unittest.TestCase):

    def test_empty_rgb_plane_is_unpainted(self):
        self.assertTrue(render_workflow._capture_is_unpainted(b""))

    def test_any_nonblack_rgb_byte_marks_capture_as_painted(self):
        self.assertFalse(render_workflow._capture_is_unpainted(b"\x00\x00\x01"))

    def test_a_non_regular_log_keeps_the_generic_diagnosis(self):
        # The bounded tail read goes through the open guard, which raises
        # ValueError -- not OSError -- for a non-regular log, so a session
        # log swapped for a FIFO must leave the black-capture diagnosis
        # with its generic verdict instead of tracebacking out of the run.
        root = tmp_dir.make_tmp_dir(self)
        fifo = root / "session.log"
        os.mkfifo(fifo)
        self.assertFalse(render_workflow._client_exited_during_capture(fifo))


class TestSessionScript(unittest.TestCase):
    """The in-session shell script applies the scheme and captures the applet.

    It is the only place the colour scheme is applied inside the throwaway
    session and the only place ``spectacle`` is told what to capture. A
    dropped flag or a wrong positional parameter there renders an unthemed or
    empty surface, which the fidelity gate then reports as a pixel difference
    rather than as the renderer's own bug.
    """

    def test_applies_the_scheme_before_opening_the_client(self):
        script = render_session.session_script()
        # The installed scheme id, applied inside the session; `|| exit 1`
        # aborts the session on a failed apply instead of capturing an
        # unthemed window. The client opens before the settle sleep, so the
        # sleep is the wait for it to paint.
        self.assertIn(
            f"plasma-apply-colorscheme {render_session.COLOR_SCHEME} || exit 1",
            script,
        )
        self.assertLess(script.index('"$@"'), script.index("sleep"))

    def test_pins_the_clients_to_the_nested_wayland_platform(self):
        # A headless caller has no XDG_SESSION_TYPE, so Qt otherwise falls
        # through to xcb and aborts without a display. The export lives in
        # this session shell, after KWin has started, so it reaches only the
        # clients and the scheme apply.
        script = render_session.session_script()
        self.assertTrue(
            script.startswith("export QT_QPA_PLATFORM=wayland; "),
            "the session must export the nested Wayland platform first",
        )

    def test_captures_to_the_capture_positional_with_spectacle(self):
        # `-b` runs without a GUI, `-n` suppresses the notification, `-f`
        # captures the full screen, and `-o` writes the surface path that the
        # session command passes as the second positional parameter.
        self.assertIn(
            'spectacle -b -n -f -o "$capture"', render_session.session_script()
        )

    def test_stops_the_client_and_exits_with_the_capture_status(self):
        script = render_session.session_script()
        self.assertIn('kill "$client"', script)
        self.assertIn('wait "$client"', script)
        self.assertIn("exit $status", script)
        # A client that ignores SIGTERM must not hold the session past its
        # capture; the bounded wait escalates to SIGKILL before reaping.
        self.assertIn("waited=0; ", script)
        self.assertIn('kill -9 "$client"', script)
        # The client that passed the settle's liveness check is frozen
        # before the capture and resumed before the termination:
        # Spectacle's unbounded startup latency must not outlive a client
        # with a finite lifetime (BUGS.md, the splash black-frame report,
        # director decision 2026-11-12). A stopped client only acts on the
        # termination signal once the resume reaches it, so the resume
        # must precede the kill.
        self.assertIn('kill -STOP "$client" 2>/dev/null; ', script)
        self.assertIn('kill -CONT "$client" 2>/dev/null; ', script)
        self.assertLess(
            script.index('"$1 exited before the capture"'),
            script.index('kill -STOP "$client"'),
        )
        self.assertLess(
            script.index('kill -STOP "$client"'),
            script.index("spectacle -b"),
        )
        self.assertLess(
            script.index('kill -CONT "$client"'),
            script.index('resumed=0; while [ "$resumed" -lt 50 ]'),
        )
        self.assertLess(
            script.index('resumed=0; while [ "$resumed" -lt 50 ]'),
            script.index('kill "$client"'),
        )
        self.assertLess(
            script.index('kill "$client"'), script.index('kill -9 "$client"')
        )
        self.assertLess(
            script.index('kill -9 "$client"'), script.index('wait "$client"')
        )
        # Reap the killed child before exiting; the wait's status must not
        # replace the capture status saved above.
        self.assertLess(
            script.index('kill "$client"'), script.index('wait "$client"')
        )

    def test_resume_wait_reads_state_after_a_process_name_with_spaces(self):
        # Linux comm may contain spaces and closing parentheses; state follows
        # the final ') ', rather than the third whitespace-delimited field.
        child = subprocess.Popen([
            sys.executable, "-c",
            "import ctypes, os, signal; "
            "ctypes.CDLL(None).prctl(15, b'held ) client', 0, 0, 0); "
            "os.kill(os.getpid(), signal.SIGSTOP); signal.pause()",
        ])
        timer = None
        try:
            os.waitpid(child.pid, os.WUNTRACED)
            script = render_session.session_script()
            wait = script.split('kill -CONT "$client" 2>/dev/null; ', 1)[1]
            wait = wait.split('kill "$client" 2>/dev/null; ', 1)[0]
            # Delay the resume so a broken parser deterministically returns
            # while the real client is still stopped.
            timer = threading.Timer(1, os.kill, args=(child.pid, signal.SIGCONT))
            timer.start()
            result = subprocess.run(
                ["sh", "-c", 'client="$1"; ' + wait +
                 'sed \'s/.*) //; s/ .*//\' "/proc/$client/stat"',
                 "sh", str(child.pid)],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotEqual("T", result.stdout.strip())
        finally:
            if timer is not None:
                timer.cancel()
                timer.join()
            child.terminate()
            os.kill(child.pid, signal.SIGCONT)
            child.wait(timeout=5)

    def test_exports_the_client_pid_before_the_freeze(self):
        # A capture-side helper cannot learn the client pid from a pidfile
        # the client writes: under load the freeze can land before the
        # client's first instruction, and a pidfile read then sees nothing
        # (BUGS.md, the client-exit stub regression, 2026-11-12). The
        # session shell owns ``$!``, so it must publish the pid itself,
        # and it must do so before the stop that can predate any client
        # code.
        script = render_session.session_script()
        self.assertIn('export RENDER_SESSION_CLIENT_PID="$client"; ', script)
        self.assertLess(
            script.index('export RENDER_SESSION_CLIENT_PID="$client"'),
            script.index('kill -STOP "$client"'),
        )

    def test_waits_for_client_termination_and_preserves_capture_status(self):
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        stopped = root / "stopped"
        client = root / "client.py"
        client.write_text(
            "import os, signal, sys, time\n"
            # A slow start, longer than the one-second settle ceiling: under
            # load Python's startup can outlast a short ceiling.
            "time.sleep(2)\n"
            "from pathlib import Path\n"
            "def stop(*args):\n"
            "    time.sleep(0.2)\n"
            "    Path(sys.argv[2]).write_text('terminated')\n"
            "    sys.exit(23)\n"
            "signal.signal(signal.SIGTERM, stop)\n"
            "signal.alarm(30)\n"
            # The session waits on this ready file (settle is the ceiling),
            # so the freeze lands only after the client's handler is installed.
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "Path(sys.argv[1]).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        # Replace only the desktop commands. The real shell launches, signals
        # and waits for a real child whose termination deliberately takes time.
        # run_logged tears down descendants when the shell exits, so omitting
        # wait prevents the child from recording its completed termination.
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        # The capture stub may take longer than the old five-second budget,
        # as a capture does under load. The session must still finish and
        # return its status, so the outer budget must cover the whole run.
        for capture_status, capture_seconds in ((0, 0), (7, 0), (0, 5.5)):
            # Each subtest's client touches the ready file, so the settle ends
            # on it. The 20 s settle is only the ceiling: a short one let a
            # slow client start outlast it, so the session froze the client
            # before its SIGTERM handler existed and the client died unhandled.
            with self.subTest(capture_status=capture_status, capture_seconds=capture_seconds):
                ready.unlink(missing_ok=True)
                stopped.unlink(missing_ok=True)
                prefix = (
                    f'sleep() {{ if [ "$1" = 0 ]; then {shlex.join([sys.executable, "-c", poll, str(ready)])}; else command sleep "$@"; fi; }}; '
                    f"spectacle() {{ command sleep {capture_seconds}; return {capture_status}; }}; "
                )
                status = render_workflow.run_logged(
                    ["sh", "-c", prefix + render_session.session_script(),
                     "sh", "20", str(root / "capture.png"), sys.executable,
                     str(client), str(ready), str(stopped)],
                    environment, root / "session.log", 30, root,
                )
                self.assertEqual(capture_status, status)
                log = (root / "session.log").read_text(encoding="utf-8", errors="replace")
                self.assertTrue(
                    stopped.exists(),
                    f"session exited before client termination; session log:\n{log}",
                )

    def test_the_settle_ends_early_once_the_client_writes_its_ready_file(self):
        # The settle budget is a ceiling, not a fixed sleep: a client that
        # writes RENDER_SESSION_READY_FILE as soon as its window is up lets
        # the capture start at once. The 15 s settle here would take far
        # longer than the 10 s bound if the script still slept it out.
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        client = root / "client.py"
        client.write_text(
            "import os, signal\n"
            "from pathlib import Path\n"
            "signal.alarm(30)\n"
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        prefix = "spectacle() { return 0; }; "
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "15", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 60, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertLess(elapsed, 10, "the settle slept out its full ceiling")
        self.assertIn("render-session: client ready at", log)

    def test_the_settle_waits_its_ceiling_when_the_client_never_signals(self):
        # A client that never writes the ready file keeps the old behaviour:
        # the session waits the whole settle ceiling before the capture.
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        client = root / "client.py"
        client.write_text(
            "import signal\n"
            "signal.alarm(30)\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        prefix = "spectacle() { return 0; }; "
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "2", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 60, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertGreaterEqual(elapsed, 2)
        self.assertIn("settle ceiling reached before a client ready file", log)

    def test_dbus_readiness_ends_the_settle_and_reaps_its_listener(self):
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        qdbus = root / "qdbus6"
        qdbus.write_text("#!/bin/sh\necho 17\n", encoding="utf-8")
        qdbus.chmod(0o755)
        monitor = root / "dbus-monitor"
        monitor.write_text(
            "#!/bin/sh\necho $$ > \"$RENDER_MONITOR_PID\"\n"
            "echo '    member=ClientReady'\nexec sleep 30\n",
            encoding="utf-8",
        )
        monitor.chmod(0o755)
        pidfile = root / "monitor.pid"
        environment = dict(
            os.environ, PATH=f"{root}:{os.environ['PATH']}",
            RENDER_MONITOR_PID=str(pidfile),
        )
        client = root / "client.py"
        client.write_text(
            "import signal\nsignal.alarm(30)\nsignal.pause()\n",
            encoding="utf-8",
        )
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["sh", "-c", "spectacle() { return 0; }; " +
             render_session.session_script(None, str(root / "readiness.js")),
             "sh", "15", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 30, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertLess(elapsed, 10, log)
        self.assertIn("render-session: client ready at", log)
        self.assertTrue(pidfile.exists(), log)
        with self.assertRaises(ProcessLookupError):
            os.kill(int(pidfile.read_text()), 0)

    def test_missing_dbus_monitor_keeps_the_settle_ceiling(self):
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        # Keep the session PATH deliberately small: the readiness probe must
        # take its documented missing-monitor path even on hosts with D-Bus
        # tools installed. These commands are used by the ordinary shell path.
        for name in ("date", "rm", "sleep", "touch"):
            (root / name).symlink_to(shutil.which(name))
        client = root / "client.py"
        client.write_text(
            "import signal\nsignal.alarm(30)\nsignal.pause()\n",
            encoding="utf-8",
        )
        environment = dict(os.environ, PATH=str(root))
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["/bin/sh", "-c", "spectacle() { return 0; }; " +
             render_session.session_script(None, str(root / "readiness.js")),
             "sh", "1", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 10, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertGreaterEqual(elapsed, 1, log)
        self.assertIn("render-session: no dbus-monitor for client readiness", log)
        self.assertIn("settle ceiling reached before a client ready file", log)

    def test_logs_the_capture_timeline_and_a_client_exit_during_the_capture(self):
        # The black-frame diagnosis needs to tell a vanished client from an
        # unpainted window, so the script stamps every stage on one wall
        # clock and, after the capture returns, records whether the client
        # that passed the settle's liveness check is still running. The stub
        # client passes the check (it is alive through the settle) and the
        # session then freezes it for the capture, so it cannot exit on its
        # own mid-capture; the spectacle stub therefore ends it with
        # SIGKILL -- the only thing that can stop a frozen client -- before
        # returning, so the session's post-capture check deterministically
        # sees a dead client; the timing stamps and the exit marker the
        # render's black-capture diagnosis greps for must all be in the
        # log, and the capture status must survive.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        pidfile = root / "client.pid"
        client = root / "client.py"
        client.write_text(
            "import os, sys, time\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(str(os.getpid()))\n"
            "Path(sys.argv[2]).touch()\n"
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "time.sleep(0.5)\n",
            encoding="utf-8",
        )
        # The client writes the session's ready file, so the settle (1 s,
        # only the ceiling) ends once the client has started; the spectacle
        # stub then SIGKILLs the held client (a frozen client
        # cannot exit on its own) and spins until the recorded pid is gone,
        # so the client -- alive at the liveness check -- dies mid-capture.
        prefix = (
            # The stub reads the pid the session exports before the capture.
            'spectacle() { pid="$RENDER_SESSION_CLIENT_PID"; '
            'kill -9 "$pid" 2>/dev/null; n=0; '
            'while kill -0 "$pid" 2>/dev/null && [ $n -lt 200 ]; do '
            'command sleep 0.01; n=$((n + 1)); done; return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "1", str(root / "capture.png"), sys.executable,
             str(client), str(pidfile), str(ready)],
            environment, root / "session.log", 10, root,
        )
        self.assertEqual(0, status)
        log = (root / "session.log").read_text(encoding="utf-8")
        for marker in (
            "render-session: client started at ",
            "render-session: settle done at ",
            "render-session: capturing at ",
            "render-session: capture status 0 at ",
            render_session.CLIENT_EXITED_DURING_CAPTURE,
        ):
            self.assertIn(marker, log)
        self.assertNotIn("client alive after the capture", log)

    def test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination(
        self,
    ):
        # The client that passes the settle's liveness check is frozen with
        # SIGSTOP before the capture and resumed with SIGCONT immediately
        # before the post-capture termination, so Spectacle's unbounded
        # startup latency cannot outlive a client with a finite lifetime
        # (BUGS.md, the splash black-frame report, director decision
        # 2026-11-12). The spectacle stub records the client's scheduler
        # state once it has seen "T" (stopped) or spent its poll cap, which
        # must be "T" while the capture runs; a trapped SIGTERM that writes
        # its own file pins the resume, because a still-stopped client
        # cannot run its termination handler inside the session's bounded
        # wait.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        pidfile = root / "client.pid"
        captured_state = root / "captured-state"
        terminated = root / "terminated"
        client = root / "client.py"
        client.write_text(
            "import os, signal, sys\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(str(os.getpid()))\n"
            "Path(sys.argv[2]).touch()\n"
            "def terminate(*args):\n"
            "    Path(sys.argv[3]).write_text('terminated')\n"
            "    sys.exit(0)\n"
            "signal.signal(signal.SIGTERM, terminate)\n"
            # The ready file ends the settle only once the handler is in, so
            # the hold cannot freeze the client before it can be resumed.
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        # The spectacle stub polls the client's scheduler state until it is
        # "T" (stopped): `kill -STOP` returns before the woken client stops,
        # so a single read at capture start can still see "R". A capture
        # that starts without the hold never reaches "T" and fails the test.
        state_of = 'state=$(awk \'{print $3}\' "/proc/$pid/stat" 2>/dev/null); '
        prefix = (
            # The stub reads the pid the session exports before the capture.
            # It records the final state and the number of polls it made, so
            # a capture that started before the stop landed names that case.
            'spectacle() { pid="$RENDER_SESSION_CLIENT_PID"; n=0; '
            f'{state_of} '
            'while [ "$state" != T ] && [ $n -lt 200 ]; do '
            f'command sleep 0.01; n=$((n + 1)); {state_of} done; '
            f'printf "%s %s" "$state" "$n" > "{captured_state}"; '
            'return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "20", str(root / "capture.png"), sys.executable,
             str(client), str(pidfile), str(ready), str(terminated)],
            environment, root / "session.log", 30, root,
        )
        state, polls = captured_state.read_text(encoding="utf-8").split()
        self.assertEqual(
            "T", state,
            f"the client was still in state {state!r} after {polls} polls "
            "(cap 200) during the capture: the SIGSTOP had not taken effect "
            "within the stub's poll cap",
        )
        self.assertEqual(0, status)
        self.assertTrue(
            terminated.exists(),
            "the held client was never resumed for its termination",
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertIn("render-session: client held at ", log)
        # The post-capture aliveness check runs while the client is still
        # frozen, before the resume, so a held client reads as alive.
        self.assertIn("client alive after the capture", log)
        self.assertNotIn(render_session.CLIENT_EXITED_DURING_CAPTURE, log)

    def test_keeps_the_one_window_session_free_of_the_focus_settle(self):
        # No mode but the inactive pair has a focus race: the default
        # session script must carry an empty focus path, so its settle
        # guard never fires and a one-window render runs the stages the
        # inactive mode's session runs minus the settle loop.
        script = render_session.session_script()
        self.assertIn('focus=""; ', script)

    def test_loads_the_focus_settle_before_the_settle_sleep_and_stops_it_after_the_capture(
        self,
    ):
        # The settle loop must start between the client's start and the
        # settle sleep (the re-activation must already run while the
        # windows map) and stop only after the capture status is recorded
        # (Spectacle's startup latency is unbounded under concurrent
        # renders, so the last re-run has to sit between the focused
        # window's map and the frame being read; BUGS.md, the inactive-dialog
        # focus race, 2026-11-13). The stop must precede the client's
        # resume so no re-run can land after the frame was read, and a
        # session without a settle script carries neither the loop nor its
        # stop.
        script = render_session.session_script("/scratch/inactive-dialog-focus-settle.js")
        self.assertIn("focus=/scratch/inactive-dialog-focus-settle.js; ", script)
        self.assertIn("org.kde.kwin.Scripting.loadScript", script)
        self.assertLess(
            script.index("Scripting.loadScript"),
            script.index('sleep "$settle"'),
        )
        self.assertGreater(
            script.index("capture status $status"),
            script.index("Scripting.loadScript"),
        )
        self.assertLess(
            script.index('kill "$settle_loop"'),
            script.index('kill -CONT "$client"'),
        )
        self.assertIn('focus=""; ', render_session.session_script())

    def test_runs_the_focus_settle_loop_until_the_capture_has_returned(self):
        # The inactive-dialog capture must settle the pair's focus state
        # before the frame is read: the session loads the settle script
        # into KWin once and re-runs it in a bounded loop, so a re-run
        # lands inside the capture window itself, where the newest-window
        # activation race used to catch the left window active (BUGS.md,
        # 2026-11-13). The qdbus6 stub records every invocation, tagged
        # with whether the capture was already in flight; the settle
        # script and the repeated runs must both be recorded, a run must
        # land inside the capture, the sentinel must exist after the
        # session (the loop's stop), and the capture status must survive.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        calls = root / "qdbus-calls"
        capturing = root / "capturing"
        qdbus = root / "qdbus6"
        qdbus.write_text(
            "#!/bin/sh\n"
            f'log="{calls}"\n'
            'case "$*" in\n'
            "  *loadScript*) echo 0; printf 'loadScript\\n' >> \"$log\";;\n"
            "  *Script0*)\n"
            f'    if [ -e "{capturing}" ]; then phase=run-during-the-capture; '
            'else phase=run-before-the-capture; fi\n'
            '    printf "%s\\n" "$phase" >> "$log";;\n'
            "esac\n",
            encoding="utf-8",
        )
        qdbus.chmod(0o755)
        ready = root / "ready"
        client = root / "client.py"
        client.write_text(
            "import sys, time\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).touch()\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        settle_script = root / "inactive-dialog-focus-settle.js"
        settle_script.write_text("// stub\n", encoding="utf-8")
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        # The settle's `sleep 0` polls until the client has started; the
        # spectacle stub marks the capture window and holds it for 0.6s,
        # long enough for the 0.25s settle loop to re-run inside it.
        prefix = (
            f'sleep() {{ if [ "$1" = 0 ]; then '
            f"{shlex.join([sys.executable, '-c', poll, str(ready)])}; "
            'else command sleep "$@"; fi; }; '
            f'spectacle() {{ touch "{capturing}"; command sleep 0.6; return 0; }}; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(str(settle_script)),
             "sh", "0", str(root / "capture.png"), sys.executable,
             str(client), str(ready)],
            dict(os.environ, PATH=f"{root}:{os.environ['PATH']}"),
            root / "session.log", 10, root,
        )
        self.assertEqual(0, status)
        recorded = calls.read_text(encoding="utf-8").splitlines()
        self.assertIn("loadScript", recorded)
        self.assertIn("run-during-the-capture", recorded)
        self.assertTrue(
            Path(f"{settle_script}.done").exists(),
            "the focus settle loop was never stopped after the capture",
        )


if __name__ == "__main__":
    unittest.main()
