"""Stubbed session checks for the render readiness D-Bus signal."""

from __future__ import annotations

import os
import sys
import time
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import render_session, render_workflow  # noqa: E402


class TestRenderReadiness(unittest.TestCase):
    def _session(self, root, path, settle):
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
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
        monitor = bindir / "dbus-monitor"
        monitor.write_text(
            "#!/bin/sh\n"
            f"echo $$ > {monitor_pid}\n"
            "echo 'member=ClientReady'\n"
            "exec sleep 30\n",
            encoding="utf-8",
        )
        monitor.chmod(0o755)
        qdbus = bindir / "qdbus6"
        qdbus.write_text("#!/bin/sh\necho 7\n", encoding="utf-8")
        qdbus.chmod(0o755)
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

    def test_paint_grace_does_not_extend_the_settle_ceiling(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        monitor = bindir / "dbus-monitor"
        monitor.write_text(
            "#!/bin/sh\necho 'member=ClientReady'\nexec sleep 30\n",
            encoding="utf-8",
        )
        monitor.chmod(0o755)
        qdbus = bindir / "qdbus6"
        qdbus.write_text("#!/bin/sh\necho 7\n", encoding="utf-8")
        qdbus.chmod(0o755)
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

    def test_the_listener_waits_its_ceiling_without_a_signal(self):
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        monitor = bindir / "dbus-monitor"
        monitor.write_text("#!/bin/sh\nexec sleep 30\n", encoding="utf-8")
        monitor.chmod(0o755)
        qdbus = bindir / "qdbus6"
        qdbus.write_text("#!/bin/sh\necho 7\n", encoding="utf-8")
        qdbus.chmod(0o755)
        (bindir / "sleep").symlink_to("/usr/bin/sleep")
        status = self._session(root, f"{bindir}:/usr/bin:/bin", 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertIn("settle ceiling reached before a client ready file", log)

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
        monitor = bindir / "dbus-monitor"
        monitor.write_text(
            f"#!/bin/sh\ntouch {started_marker}\nexec sleep 30\n",
            encoding="utf-8",
        )
        monitor.chmod(0o755)
        # mkfifo is present so only the qdbus guard keeps the listener off.
        for name in ("sleep", "date", "rm", "touch", "mkfifo"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._session(root, str(bindir), 1)
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: no qdbus for client readiness", log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertFalse(started_marker.exists(), log)


if __name__ == "__main__":
    unittest.main()
