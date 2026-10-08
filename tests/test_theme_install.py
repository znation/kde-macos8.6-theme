"""The shared install harness and the Makefile paths it drives.

`theme_install.run` is the suite's timeout runner: the tests route their `make`
/ `plasma-apply-*` / `kpackagetool6` calls through it, so a fake `make` that
never exits raises `subprocess.TimeoutExpired` instead of stalling `make check`
forever. (One lock test starts `make install` directly, bounding it with its
own deadline and `communicate(timeout=...)`.) The Makefile also has to survive
a `DESTDIR` or `XDG_DATA_HOME` that contains whitespace, so its recipe words
are quoted.
"""

import os
import subprocess
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


class TestSubprocessTimeout(unittest.TestCase):
    def test_install_times_out_when_make_hangs(self):
        with tempfile.TemporaryDirectory() as tmp:
            bindir = os.path.join(tmp, "fakebin")
            os.makedirs(bindir)
            fake_make = os.path.join(bindir, "make")
            with open(fake_make, "w", encoding="utf-8") as handle:
                handle.write("#!/bin/sh\nexec sleep 5\n")
            os.chmod(fake_make, 0o755)

            env = {"PATH": bindir + os.pathsep + os.environ.get("PATH", "")}
            with unittest.mock.patch.dict(os.environ, env):
                original = theme_install.SUBPROCESS_TIMEOUT
                theme_install.SUBPROCESS_TIMEOUT = 0.5
                try:
                    with self.assertRaises(subprocess.TimeoutExpired):
                        theme_install.install(tmp)
                finally:
                    theme_install.SUBPROCESS_TIMEOUT = original

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
            bindir = os.path.join(tmp, "fakebin")
            os.makedirs(bindir)
            fake_make = os.path.join(bindir, "make")
            with open(fake_make, "w", encoding="utf-8") as handle:
                handle.write(
                    "#!/bin/sh\n"
                    "sleep 5 &\n"
                    'echo "$!" > "$GRANDCHILD_PIDFILE"\n'
                    "exec sleep 5\n"
                )
            os.chmod(fake_make, 0o755)

            env = dict(
                os.environ,
                PATH=bindir + os.pathsep + os.environ.get("PATH", ""),
                GRANDCHILD_PIDFILE=pidfile,
            )
            original = theme_install.SUBPROCESS_TIMEOUT
            theme_install.SUBPROCESS_TIMEOUT = 0.5
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    theme_install.install(tmp, env=env)
            finally:
                theme_install.SUBPROCESS_TIMEOUT = original

            with open(pidfile, encoding="utf-8") as handle:
                grandchild = int(handle.read())
            # A killed process can linger as a zombie until it is reaped, so
            # poll briefly instead of probing once. The grandchild sleeps for
            # five seconds, so it is still alive at this deadline exactly when
            # the timeout failed to kill it.
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline and _process_alive(grandchild):
                time.sleep(0.05)
            self.assertFalse(
                _process_alive(grandchild),
                "grandchild survived the timeout",
            )


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
