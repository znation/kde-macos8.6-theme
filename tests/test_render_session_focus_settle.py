"""Focused checks for the inactive-window session focus-settle loop."""

from __future__ import annotations

import os
import shlex
import sys
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.executable_stubs import write_executable
from tools import render_session, render_workflow  # noqa: E402


class TestSessionFocusSettle(unittest.TestCase):
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
        write_executable(root / "plasma-apply-colorscheme", "#!/bin/sh\nexit 0\n")
        calls = root / "qdbus-calls"
        capturing = root / "capturing"
        write_executable(
            root / "qdbus6",
            "#!/bin/sh\n"
            f'log="{calls}"\n'
            'case "$*" in\n'
            "  *loadScript*) echo 0; printf 'loadScript\\n' >> \"$log\";;\n"
            "  *Script0*)\n"
            f'    if [ -e "{capturing}" ]; then phase=run-during-the-capture; '
            'else phase=run-before-the-capture; fi\n'
            '    printf "%s\\n" "$phase" >> "$log";;\n'
            "esac\n",
        )
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

    def _run_focus_session(self, root, path, focus_script):
        # A stubbed one-window session: the spectacle stub returns at once,
        # the client only waits to be stopped, and PATH holds just the
        # tools the script needs plus whatever qdbus stub the test adds.
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        client = root / "client.py"
        client.write_text("import signal; signal.pause()\n", encoding="utf-8")
        return render_workflow.run_logged(
            [
                "/bin/sh", "-c",
                "spectacle() { return 0; }; "
                + render_session.session_script(focus_script),
                "sh", "1", str(root / "capture.png"), sys.executable,
                str(client),
            ],
            {**os.environ, "PATH": f"{root}:{path}"},
            root / "session.log", 10, root,
        )

    def test_a_missing_qdbus_names_the_tool_and_starts_no_focus_loop(self):
        # With no qdbus on PATH the focus settle cannot load its script, so
        # the session must name the missing tool, run no settle loop, and
        # still finish the capture and reach its settle ceiling.
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        for name in ("sleep", "date", "rm", "touch"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._run_focus_session(
            root, str(bindir), "/scratch/inactive-dialog-focus-settle.js"
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: no qdbus for the focus settle", log)
        self.assertNotIn("focus settle loop running", log)
        self.assertIn("capture status 0", log)
        self.assertIn("settle ceiling reached before a client ready file", log)

    def test_a_focus_script_that_does_not_load_runs_no_settle_loop(self):
        # qdbus answers loadScript with no script id, so the settle must
        # report that the script did not load and never run it: any
        # invocation other than the load is recorded in runs.log.
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        runs = root / "runs.log"
        qdbus = bindir / "qdbus6"
        qdbus.write_text(
            "#!/bin/sh\n"
            "case \"$*\" in\n"
            "  *loadScript*) ;;\n"
            f"  *) echo \"$*\" >> {runs};;\n"
            "esac\n",
            encoding="utf-8",
        )
        qdbus.chmod(0o755)
        for name in ("sleep", "date", "rm", "touch"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._run_focus_session(
            root, str(bindir), "/scratch/inactive-dialog-focus-settle.js"
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: the focus settle script did not load", log)
        self.assertNotIn("focus settle loop running", log)
        self.assertFalse(runs.exists(), "the settle script was run without loading")

    def test_a_non_numeric_focus_script_id_is_not_run_and_the_settle_ceiling_still_ends_it(self):
        # A loadScript answer that is not a script number ("x") is not an id
        # the settle may address as /Scripting/Script<id>: the session must
        # report the script did not load, start no settle loop, and still
        # reach its ceiling so the capture runs.
        root = tmp_dir.make_tmp_dir(self)
        bindir = root / "bin"
        bindir.mkdir()
        runs = root / "runs.log"
        qdbus = bindir / "qdbus6"
        qdbus.write_text(
            "#!/bin/sh\n"
            "case \"$*\" in\n"
            "  *loadScript*) echo x;;\n"
            f"  *) echo \"$*\" >> {runs};;\n"
            "esac\n",
            encoding="utf-8",
        )
        qdbus.chmod(0o755)
        for name in ("sleep", "date", "rm", "touch"):
            (bindir / name).symlink_to(f"/usr/bin/{name}")
        status = self._run_focus_session(
            root, str(bindir), "/scratch/inactive-dialog-focus-settle.js"
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status, log)
        self.assertIn("render-session: the focus settle script did not load", log)
        self.assertNotIn("focus settle loop running", log)
        self.assertIn("capture status 0", log)
        self.assertIn("settle ceiling reached before a client ready file", log)
        self.assertFalse(runs.exists(), "the settle script was run with a non-numeric id")


if __name__ == "__main__":
    unittest.main()
