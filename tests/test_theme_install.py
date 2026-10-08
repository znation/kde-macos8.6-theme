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


def _fake_make_env(tmp, script, **extra):
    """Install an executable fake `make` in *tmp* and return an environment.

    The fake `make` runs *script*; the returned environment prepends the fake
    bin directory to PATH so `theme_install`'s `make` subprocesses pick it up.
    *extra* adds further variables (the descendant test passes its pid file).
    """
    bindir = os.path.join(tmp, "fakebin")
    os.makedirs(bindir)
    fake_make = os.path.join(bindir, "make")
    with open(fake_make, "w", encoding="utf-8") as handle:
        handle.write(script)
    os.chmod(fake_make, 0o755)
    return dict(
        os.environ,
        PATH=bindir + os.pathsep + os.environ.get("PATH", ""),
        **extra,
    )


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
            env = _fake_make_env(tmp, "#!/bin/sh\nexec sleep 5\n")
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
            env = _fake_make_env(
                tmp,
                "#!/bin/sh\n"
                "sleep 5 &\n"
                'echo "$!" > "$GRANDCHILD_PIDFILE"\n'
                "exec sleep 5\n",
                GRANDCHILD_PIDFILE=pidfile,
            )
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


if __name__ == "__main__":
    unittest.main()
