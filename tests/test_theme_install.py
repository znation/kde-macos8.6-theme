"""The shared install harness and the Makefile paths it drives.

`theme_install.run` is the suite's timeout runner: the tests route their `make`
/ `plasma-apply-*` / `kpackagetool6` calls through it, so a fake `make` that
never exits raises `subprocess.TimeoutExpired` instead of stalling `make check`
forever. (One lock test starts `make install` itself to poll it, then finishes
it through `theme_install.running`, which kills the child if the poll raises.)
The Makefile also has to survive
a `DESTDIR` or `XDG_DATA_HOME` that contains whitespace, so its recipe words
are quoted.
"""

import contextlib
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock

import theme_install


def _process_alive(pid):
    """Return True while a process with *pid* still exists."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@contextlib.contextmanager
def _short_subprocess_timeout(seconds=0.5):
    """Temporarily shorten `theme_install.SUBPROCESS_TIMEOUT` for one block.

    Each timeout test cuts the suite's 60-second budget to a fraction of a
    second; the global must be restored even when the body raises, or every
    later subprocess call in the suite would time out.
    """
    original = theme_install.SUBPROCESS_TIMEOUT
    theme_install.SUBPROCESS_TIMEOUT = seconds
    try:
        yield
    finally:
        theme_install.SUBPROCESS_TIMEOUT = original


class TestSubprocessTimeout(unittest.TestCase):
    def _assert_process_dies(self, pid, message):
        """Assert process *pid* is gone within a short deadline.

        A killed process can linger as a zombie until it is reaped, so poll
        briefly instead of probing once.
        """
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and _process_alive(pid):
            time.sleep(0.05)
        self.assertFalse(_process_alive(pid), message)

    def test_install_times_out_when_make_hangs(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = theme_install.shadow_command_env(
                tmp, "make", "#!/bin/sh\nexec sleep 5\n"
            )
            with unittest.mock.patch.dict(os.environ, env):
                with _short_subprocess_timeout():
                    with self.assertRaises(subprocess.TimeoutExpired):
                        theme_install.install(tmp)

    def test_timeout_kills_grandchildren(self):
        """A timeout must kill the whole make/flock/make chain, not just make.

        `make install` runs `flock ... make _install`, so the process the suite
        starts has descendants that survive when only the direct child is
        killed -- still running against the throwaway DESTDIR and still
        holding the data-home lock. The fake make backgrounds a long sleep and
        records its pid, so the test can tell whether that descendant outlived
        the timeout.
        """
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = os.path.join(tmp, "grandchild.pid")
            env = theme_install.shadow_command_env(
                tmp,
                "make",
                "#!/bin/sh\n"
                "sleep 5 &\n"
                'echo "$!" > "$GRANDCHILD_PIDFILE"\n'
                "exec sleep 5\n",
            )
            env["GRANDCHILD_PIDFILE"] = pidfile
            with _short_subprocess_timeout():
                with self.assertRaises(subprocess.TimeoutExpired):
                    theme_install.install(tmp, env=env)

            with open(pidfile, encoding="utf-8") as handle:
                grandchild = int(handle.read())
            # The grandchild sleeps for five seconds, so it is still alive at
            # the deadline exactly when the timeout failed to kill it.
            self._assert_process_dies(
                grandchild, "grandchild survived the timeout"
            )

    def test_finish_kills_a_hung_child(self):
        """A caller-started child that times out must be killed, not leaked.

        `test_lookandfeel` starts `make install` itself to poll it, then waits
        with `theme_install.finish`. A child that outlives the timeout must be
        SIGKILLed with its process group, so a hung `make install` -- and its
        `flock` descendants -- cannot keep running after the test has failed.
        """
        process = theme_install.start(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with _short_subprocess_timeout():
            with self.assertRaises(subprocess.TimeoutExpired):
                theme_install.finish(process)
        self._assert_process_dies(
            process.pid, "child survived finish()'s timeout"
        )

    def _kill_escaped(self, pidfile):
        """SIGKILL the escaped grandchild whose pid *pidfile* holds, if any."""
        try:
            with open(pidfile, encoding="utf-8") as handle:
                pid = int(handle.read())
        except (OSError, ValueError):
            return
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    @unittest.skipUnless(hasattr(os, "setsid"), "needs os.setsid")
    def test_finish_reports_a_descendant_that_escaped_the_process_group(self):
        """A descendant outside the group must not make finish() block again.

        Killing the direct child's process group reaps its descendants, but a
        descendant that called setsid() has left that group and still holds
        the child's stdout/stderr pipes. communicate() then cannot reach EOF
        and times out a second time; finish must report the timeout with no
        captured output instead of blocking on the escaped descendant.
        """
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = os.path.join(tmp, "escaped.pid")
            readyfile = os.path.join(tmp, "escaped.ready")
            grandchild = (
                "import os, sys, time\n"
                "os.setsid()\n"
                "open(sys.argv[1], 'w').write('ok')\n"
                "time.sleep(30)\n"
            )
            child = (
                "import subprocess, sys, time\n"
                "p = subprocess.Popen(\n"
                "    [sys.executable, '-c', sys.argv[3], sys.argv[2]])\n"
                "open(sys.argv[1], 'w').write(str(p.pid))\n"
                "time.sleep(30)\n"
            )
            process = theme_install.start(
                [sys.executable, "-c", child, pidfile, readyfile, grandchild],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                # The grandchild writes `readyfile` only after setsid(), so
                # the group kill below cannot race its escape.
                deadline = time.monotonic() + 5.0
                while (
                    not os.path.exists(readyfile)
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.01)
                self.assertTrue(
                    os.path.exists(readyfile),
                    "the child did not spawn an escaped grandchild",
                )
                with _short_subprocess_timeout():
                    with self.assertRaises(subprocess.TimeoutExpired) as caught:
                        theme_install.finish(process)
                # The escaped-descendant path re-raises with no captured
                # output; the normal path drains the killed child's pipes and
                # includes their (empty) bytes.
                self.assertIsNone(caught.exception.output)
                self.assertIsNone(caught.exception.stderr)
            finally:
                self._kill_escaped(pidfile)
                if process.poll() is None:
                    process.kill()
                process.wait()
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()

    def test_running_kills_the_child_when_the_block_raises(self):
        """An abandoned started child must be killed, not left running.

        `test_lookandfeel` starts `make install`, polls it, and only then
        finishes it. If the poll raises -- the operator interrupts `make
        check`, or the poll itself fails -- the child and its `flock`
        descendants would keep running and holding the data-home lock after
        the test has failed. `running` kills the child's process group on the
        way out whatever happens.
        """
        with self.assertRaises(RuntimeError):
            with theme_install.running(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process:
                raise RuntimeError("poll failed")
        self.assertIsNotNone(process.poll())
        self._assert_process_dies(process.pid, "running left the child alive")

    def test_running_leaves_a_finished_child_alone(self):
        """A child the caller already finished must not be touched again.

        The lock test calls `finish` inside the `running` block, so `running`
        must see the exited child and do nothing; re-signalling or waiting on
        it would fail the normal path.
        """
        with theme_install.running(
            [sys.executable, "-c", "pass"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            theme_install.finish(process)
        self.assertEqual(process.returncode, 0)

    def test_running_closes_the_pipes_of_an_exited_child(self):
        """A child that exits before the block does must not leak its pipes.

        `running` only has to kill a still-running child, but the caller may
        leave the block without `finish` after the child has already exited --
        an interrupt during the lock test's poll, once `make install` has
        finished, is exactly that. The child is reaped, but its stdout/stderr
        read ends stay open until the `Popen` is collected unless `running`
        closes them, so close every pipe on the way out whether or not a kill
        was needed.
        """
        with theme_install.running(
            [sys.executable, "-c", "pass"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            deadline = time.monotonic() + 5.0
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertIsNotNone(process.poll())
        self.assertTrue(process.stdout.closed, "stdout pipe leaked")
        self.assertTrue(process.stderr.closed, "stderr pipe leaked")


class TestWhitespaceInInstallPaths(unittest.TestCase):
    """`make install`/`uninstall` must quote paths that contain whitespace.

    A `DESTDIR` or `XDG_DATA_HOME` with a space is legal; an unquoted recipe
    word-splits it, so the copy lands in the wrong place or fails outright.
    All three artifacts must install and uninstall under a spaced root.
    """

    def test_install_and_uninstall_under_a_path_with_a_space(self):
        with tempfile.TemporaryDirectory() as tmp:
            destdir = os.path.join(tmp, "spaced root")
            result = theme_install.install(destdir)
            self.assertEqual(result.returncode, 0, result.stderr)

            scheme = theme_install.installed_color_scheme(destdir)
            self.assertTrue(os.path.isfile(scheme), scheme)
            lnf = os.path.join(
                theme_install.installed_plasma_dir(destdir, "look-and-feel"),
                "org.macos8.desktop",
            )
            self.assertTrue(os.path.isdir(lnf), lnf)
            dtheme = os.path.join(
                theme_install.installed_plasma_dir(destdir, "desktoptheme"),
                "org.macos8.desktop",
            )
            self.assertTrue(os.path.isdir(dtheme), dtheme)

            removed = theme_install.uninstall(destdir)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(scheme), scheme)
            self.assertFalse(os.path.exists(lnf), lnf)
            self.assertFalse(os.path.exists(dtheme), dtheme)


class TestXdgDataHomeDefault(unittest.TestCase):
    """An empty or relative $XDG_DATA_HOME must fall back to the XDG default.

    The XDG Base Directory spec resolves $XDG_DATA_HOME to $HOME/.local/share
    when it is unset or empty, and treats a relative value as invalid and
    ignores it; README's Installing section documents the same default. `?=`
    alone kept an empty environment value, so `make install` targeted
    $(DESTDIR) itself (or, with no DESTDIR, ran `install -d ""`). Drive
    `make -n` with a controlled environment and read the data-home path the
    recipe would use.
    """

    HOME = "/tmp/tumwater-test-home"

    def _install_dry_run(self, xdg):
        """Return the `make -n install` output for *xdg* in the environment."""
        env = dict(os.environ, HOME=self.HOME, XDG_DATA_HOME=xdg)
        result = theme_install.run(
            ["make", "-n", "install"],
            cwd=theme_install.ROOT,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_empty_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)

    def test_relative_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("relative/share")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)
        self.assertNotIn("relative/share", out)

    def test_absolute_is_kept(self):
        out = self._install_dry_run("/custom/share")
        self.assertIn('install -d "/custom/share"', out)


if __name__ == "__main__":
    unittest.main()
