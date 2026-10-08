"""The suite's shared subprocess runner must bound a hung child.

Every `make` / `plasma-apply-*` / `kpackagetool6` call the tests make goes
through `theme_install.run`, which applies `SUBPROCESS_TIMEOUT`. This test
injects a fake `make` that never exits and asserts the install path raises
`subprocess.TimeoutExpired` instead of stalling `make check` forever.
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


if __name__ == "__main__":
    unittest.main()
