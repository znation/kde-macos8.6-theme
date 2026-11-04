"""Make boundary tests for the standalone Plasma selection target."""

import shutil
import tempfile
import unittest
from pathlib import Path

from support import theme_install
from support.process_assertions import assert_failed, assert_succeeded


class TestMakeApplyPlasma(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="make-apply-plasma-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data = self.root / "data"
        self.data.mkdir()
        self.calls = self.root / "calls"
        self.python = self.root / "python"

    def interpreter(self, body):
        self.python.write_text("#!/bin/sh\n" + body)
        self.python.chmod(0o755)
        env = theme_install.make_env("PYTHON", "DESTDIR", "XDG_DATA_HOME")
        env.update(
            {
                "HOME": str(self.home),
                "XDG_DATA_HOME": str(self.data),
                "PYTHON": str(self.python),
            }
        )
        return env

    def test_dry_run_invokes_only_the_plasma_helper(self):
        result = theme_install.run_make(
            ["-n", "apply-plasma"], env=self.interpreter("")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_theme.py", result.stdout)
        for unwanted in ("install", "apply_keymap.py", "apply_gtk.py", "apply_cursor.py", "install_firefox.py"):
            self.assertNotIn("tools/" + unwanted, result.stdout)

    def test_success_probes_python_then_runs_only_the_plasma_helper(self):
        env = self.interpreter(
            'if [ "$1" = "-c" ]; then exit 0; fi\n'
            f'printf "%s\\n" "$*" >> "{self.calls}"\n'
        )
        result = theme_install.run_make(["apply-plasma"], env=env)
        assert_succeeded(self, result)
        self.assertEqual(["tools/apply_theme.py"], self.calls.read_text().splitlines())
        self.assertEqual([], list(self.data.iterdir()))

    def test_nonempty_destdir_is_refused_before_helper(self):
        env = self.interpreter(
            'if [ "$1" = "-c" ]; then exit 0; fi\n'
            f'printf called >> "{self.calls}"\n'
        )
        stage = self.root / "stage"
        result = theme_install.run_make(
            ["apply-plasma", f"DESTDIR={stage}"], env=env
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_missing_or_old_python_is_refused_before_helper(self):
        env = self.interpreter("")
        missing = theme_install.run_make(
            ["apply-plasma", f"PYTHON={self.root / 'missing'}"], env=env
        )
        assert_failed(self, missing)
        self.assertIn("Python 3.10 or newer", missing.stderr)
        old = theme_install.run_make(
            ["apply-plasma", f"PYTHON={self.python}"],
            env=self.interpreter('if [ "$1" = "-c" ]; then exit 3; fi\n'),
        )
        assert_failed(self, old)
        self.assertIn("Python 3.10 or newer", old.stderr)

    def test_helper_failure_fails_make(self):
        env = self.interpreter(
            'if [ "$1" = "-c" ]; then exit 0; fi\nexit 9\n'
        )
        result = theme_install.run_make(["apply-plasma"], env=env)
        assert_failed(self, result)


if __name__ == "__main__":
    unittest.main()
