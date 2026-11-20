"""Stubbed session checks for the render readiness D-Bus signal."""

from __future__ import annotations

import os
import sys
import time
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.executable_stubs import write_executable
from tools import render_session, render_workflow  # noqa: E402


class TestRenderReadiness(unittest.TestCase):
    def _session(self, root, path, settle):
        write_executable(root / "plasma-apply-colorscheme", "#!/bin/sh\nexit 0\n")
        client = root / "client.py"
        client.write_text("import signal; signal.pause()\n", encoding="utf-8")
        return render_workflow.run_logged(
            [
                "/bin/sh", "-c",
                "spectacle() { return 0; }; " + render_session.session_script(
                    readiness_script="/scratch/readiness.js"
                ),
                "sh", str(settle), str(root / "capture.png"), sys.executable,
                str(client),
            ],
            {**os.environ, "PATH": f"{root}:{path}"},
            root / "session.log", 10, root,
        )

    def test_a_dbus_readiness_signal_ends_the_settle_and_reaps_its_listener(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        monitor_pid = root / "monitor.pid"
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\n"
            f"echo $$ > {monitor_pid}\n"
            "echo 'member=ClientReady'\n"
            "exec sleep 30\n",
        )
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        for tool in ("sleep", "mkfifo"):
            (bindir / tool).symlink_to(f"/usr/bin/{tool}")
        started = time.monotonic()
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 15)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        elapsed = time.monotonic() - started
        self.assertGreaterEqual(elapsed, 1)
        self.assertLess(elapsed, 10)
        self.assertIn("render-session: client ready at", log)
        self.assertTrue(monitor_pid.exists())
        with self.assertRaises(ProcessLookupError):
            os.kill(int(monitor_pid.read_text()), 0)

    def test_qdbus_is_used_when_qdbus6_is_unavailable(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        calls = root / "qdbus.calls"
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\necho 'member=ClientReady'\nexec sleep 30\n",
        )
        write_executable(
            bindir / "qdbus",
            "#!/bin/sh\n"
            f"echo \"$*\" >> {calls}\n"
            "case \"$*\" in *loadScript*) echo 7;; esac\n",
        )
        for tool in ("sleep", "mkfifo", "date", "rm", "touch", "sed"):
            (bindir / tool).symlink_to(f"/usr/bin/{tool}")

        status = self._session(root, str(bindir), 15)
        log = (root / "session.log").read_text(encoding="utf-8")

        self.assertEqual(0, status, log)
        self.assertIn("render-session: client ready at", log)
        recorded_calls = calls.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, len(recorded_calls))
        self.assertTrue(recorded_calls[0].endswith("loadScript /scratch/readiness.js"))
        self.assertTrue(recorded_calls[1].endswith("/Scripting/Script7 run"))

    def test_the_listener_ignores_unrelated_dbus_members_until_client_ready(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        premature_ready = root / "premature-ready"
        ready_emitted = root / "ready-emitted"
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\n"
            "echo 'member=PropertiesChanged'\n"
            "sleep 0.3\n"
            f'if [ -e "$RENDER_SESSION_READY_FILE" ]; then touch "{premature_ready}"; fi\n'
            f'touch "{ready_emitted}"\n'
            "echo 'member=ClientReady'\n"
            "exec sleep 30\n",
        )
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        for tool in ("sleep", "mkfifo"):
            (bindir / tool).symlink_to(f"/usr/bin/{tool}")

        started = time.monotonic()
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 15)
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")

        self.assertEqual(0, status, log)
        self.assertTrue(ready_emitted.exists(), log)
        self.assertFalse(premature_ready.exists(), log)
        self.assertLess(elapsed, 10, log)
        self.assertIn("render-session: client ready at", log)

    def test_paint_grace_does_not_extend_the_settle_ceiling(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\necho 'member=ClientReady'\nexec sleep 30\n",
        )
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        # The ceiling's `sleep 0.2` is stubbed to touch the ceiling file at
        # once, while the grace loop's `sleep 0.1` iterations keep their
        # real duration. A real ceiling sleep depends on fork/exec
        # scheduling: under a parallel `make check` the hosted runner
        # starved a correct session's ceiling timer ~800 ms past its
        # deadline (2026-11-20), so the ceiling-cut grace still ran its
        # full second and no start-anchored bound separates a correct
        # settle from a broken one. With the ceiling deterministic, a
        # correct settle ends within scheduling slack of the client's
        # start (the ready file exists before the settle loop's first
        # check, and the grace's ceiling guard stops it at once), while a
        # grace that ignores the ceiling still runs its 10 x 0.1 s and
        # fails the bound. The stub only stands in for the timer's sleep;
        # the ceiling-fallback path without a ready signal keeps its real
        # sleep in `test_the_listener_waits_its_ceiling_without_a_signal`.
        write_executable(
            bindir / "sleep",
            "#!/bin/sh\n"
            'if [ "$1" = 0.2 ]; then\n'
            f'  touch "{root / "capture.png.ceiling"}"\n'
            "  exit 0\n"
            "fi\n"
            'exec /usr/bin/sleep "$@"\n',
        )
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 0.2)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: client ready at", log)
        stamps = {}
        for line in log.splitlines():
            for stage in ("client started", "settle done"):
                if line.startswith(f"render-session: {stage} at "):
                    stamps[stage] = int(line.rsplit(" ", 1)[1])
        # Allow scheduling slack, but reject an unconditional one-second grace.
        self.assertLess(stamps["settle done"] - stamps["client started"], 900, log)

    def test_dbus_readiness_gets_paint_grace_when_the_ceiling_allows_it(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\necho 'member=ClientReady'\nexec sleep 30\n",
        )
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")

        status = self._session(root, f"{bindir}:/usr/bin:/bin", 3)
        log = (root / "session.log").read_text(encoding="utf-8")

        self.assertEqual(0, status, log)
        self.assertIn("render-session: client ready at", log)
        stamps = {}
        for line in log.splitlines():
            for stage in ("client started", "settle done"):
                if line.startswith(f"render-session: {stage} at "):
                    stamps[stage] = int(line.rsplit(" ", 1)[1])
        elapsed_ms = stamps["settle done"] - stamps["client started"]
        # Require the full one-second grace, excluding setup and cleanup time.
        self.assertGreaterEqual(elapsed_ms, 1000, log)
        self.assertLess(elapsed_ms, 2500, log)

    def test_a_client_touched_ready_file_without_the_dbus_signal_gets_no_paint_grace(self):
        # Only a D-Bus readiness signal earns the one-second paint grace. A
        # client that touches RENDER_SESSION_READY_FILE itself leaves the
        # ready file empty, so the settle must end at once, well inside the
        # three-second ceiling that would otherwise allow the grace.
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        write_executable(
            bindir / "dbus-monitor",
            "#!/bin/sh\nexec sleep 30\n",
        )
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        # The pin is behavioral, not temporal: every wall-clock span in this
        # session includes fork/exec latency that a loaded host makes
        # unbounded (the hosted runner measured 873 ms of Python client
        # startup here, 2026-11-20, putting a correct session at 902 ms
        # against the old 900 ms bound, and the `client ready at` stamp is
        # emitted after the grace loop, so it cannot anchor a bound). The
        # sleep stub records every 0.1 s tick taken while the ready file
        # exists and the capture does not: the grace loop's ticks only
        # happen when a ready file earned the grace, and a settle loop that
        # ignores the ready file until the ceiling keeps polling with the
        # file present. The spectacle stub touches the capture, so the
        # termination wait's tick (after the capture) is never recorded.
        # A correct session records at most one tick, the race where the
        # client's touch lands between the settle loop's existence check
        # and the stub's own check of that same tick; the touch is a
        # single instant, so two ticks cannot both span it. The regressions
        # record ten-plus ticks (measured: grace 11, ignored-ready 30) and
        # fail.
        sleep_record = root / "sleep-ticks"
        write_executable(
            bindir / "sleep",
            "#!/bin/sh\n"
            'if [ "$1" = 0.1 ] && [ -e "$RENDER_SESSION_READY_FILE" ] '
            f'&& [ ! -e "{root / "capture.png"}" ]; then\n'
            f'  echo tick >> "{sleep_record}"\n'
            "fi\n"
            'exec /usr/bin/sleep "$@"\n',
        )
        write_executable(root / "plasma-apply-colorscheme", "#!/bin/sh\nexit 0\n")
        client = root / "client.py"
        client.write_text(
            "import os, pathlib, signal\n"
            "pathlib.Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        status = render_workflow.run_logged(
            [
                "/bin/sh", "-c",
                'spectacle() { touch "$capture"; return 0; }; '
                + render_session.session_script(
                    readiness_script="/scratch/readiness.js"
                ),
                "sh", "3", str(root / "capture.png"), sys.executable,
                str(client),
            ],
            {**os.environ, "PATH": f"{bindir}:{root}:/usr/bin:/bin"},
            root / "session.log", 10, root,
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: client ready at", log)
        ticks = (
            len(sleep_record.read_text(encoding="utf-8").splitlines())
            if sleep_record.exists() else 0
        )
        self.assertLessEqual(
            ticks, 1,
            f"{ticks} post-ready settle ticks recorded"
            + (f": {sleep_record.read_text(encoding='utf-8')}" if ticks else ""),
        )

    def test_the_listener_waits_its_ceiling_without_a_signal(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        write_executable(bindir / "dbus-monitor", "#!/bin/sh\nexec sleep 30\n")
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        (bindir / "sleep").symlink_to("/usr/bin/sleep")
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertIn("settle ceiling reached before a client ready file", log)

    def test_an_early_closed_monitor_fifo_falls_back_to_the_settle_ceiling(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        write_executable(bindir / "dbus-monitor", "#!/bin/sh\nexit 0\n")
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        for name in ("sleep", "date", "rm", "touch", "mkfifo"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")

        status = self._session(root, f"{bindir}:/usr/bin:/bin", 1)
        log = (root / "session.log").read_text(encoding="utf-8")

        self.assertEqual(0, status, log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertNotIn("client ready at", log)

    def test_a_missing_dbus_monitor_names_the_tool_and_keeps_the_ceiling(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        for name in ("sleep", "date", "rm", "touch"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._session(root, str(bindir), 3)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: no dbus-monitor for client readiness", log)
        self.assertIn("settle ceiling reached before a client ready file", log)

    def test_a_missing_qdbus_names_the_tool_and_starts_no_listener(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        started_marker = root / "monitor.started"
        write_executable(
            bindir / "dbus-monitor",
            f"#!/bin/sh\ntouch {started_marker}\nexec sleep 30\n",
        )
        # mkfifo is present so only the qdbus guard keeps the listener off.
        for name in ("sleep", "date", "rm", "touch", "mkfifo"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._session(root, str(bindir), 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: no qdbus for client readiness", log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertFalse(started_marker.exists(), log)

    def test_a_failed_fifo_creation_starts_no_readiness_listener(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        started_marker = root / "monitor.started"
        write_executable(
            bindir / "dbus-monitor",
            f"#!/bin/sh\ntouch {started_marker}\nexec sleep 30\n",
        )
        write_executable(bindir / "mkfifo", "#!/bin/sh\nexit 1\n")
        write_executable(bindir / "qdbus6", "#!/bin/sh\necho 7\n")
        for name in ("sleep", "date", "rm", "touch"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")

        status = self._session(root, str(bindir), 1)
        log = (root / "session.log").read_text(encoding="utf-8")

        self.assertEqual(0, status, log)
        self.assertIn("render-session: cannot create readiness listener pipe", log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertFalse(started_marker.exists(), log)

    def test_a_non_numeric_readiness_id_is_not_run_and_the_ceiling_still_ends_the_session(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        monitor_pid = root / "monitor.pid"
        monitor = bindir / "dbus-monitor"
        write_executable(
            monitor,
            f"#!/bin/sh\necho $$ > {monitor_pid}\nexec sleep 30\n",
        )
        run_marker = root / "run.called"
        # loadScript answers with a non-numeric id ("x"); any run call is recorded.
        qdbus = bindir / "qdbus6"
        write_executable(
            qdbus,
            "#!/bin/sh\n"
            f"case \"$*\" in *run*) touch {run_marker};; *) echo x;; esac\n",
        )
        for name in ("sleep", "date", "rm", "touch", "mkfifo"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: the readiness settle script did not load", log)
        self.assertNotIn("did not run", log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertFalse(run_marker.exists(), log)
        # The listener was started before the load, so the monitor must be reaped.
        self.assertTrue(monitor_pid.exists(), log)
        with self.assertRaises(ProcessLookupError):
            os.kill(int(monitor_pid.read_text()), 0)

    def test_a_readiness_script_whose_run_fails_is_reported_and_the_ceiling_still_ends_the_session(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        monitor = bindir / "dbus-monitor"
        write_executable(monitor, "#!/bin/sh\nexec sleep 30\n")
        # loadScript yields a numeric id, but the script's run call exits 1.
        qdbus = bindir / "qdbus6"
        write_executable(
            qdbus,
            "#!/bin/sh\n"
            "case \"$*\" in *run*) exit 1;; *) echo 7;; esac\n",
        )
        for name in ("sleep", "date", "rm", "touch", "mkfifo"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._session(root, str(bindir), 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: the readiness settle script did not run", log)
        self.assertNotIn("did not load", log)
        self.assertIn("settle ceiling reached before a client ready file", log)


if __name__ == "__main__":
    unittest.main()
