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
import unittest
import unittest.mock

import theme_install


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
