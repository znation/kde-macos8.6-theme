"""Aggregate Make target checks for `make apply`."""

import shutil
import tempfile
import unittest
from pathlib import Path

from support import theme_install
from support.process_assertions import assert_failed, assert_succeeded


class TestMakeApply(unittest.TestCase):
    def test_a_hostile_DESTDIR_value_is_refused_without_running_its_shell(self):
        """Refuse a DESTDIR carrying shell quoting without executing it.

        A DESTDIR pasted into a double-quoted recipe word would close the
        recipe's own quotes, so the Makefile refuses any value carrying a
        recipe-shell metacharacter at make level, before any recipe runs;
        this test's canary file must not be created.
        """
        tmp = tempfile.mkdtemp(prefix="apply-hostile-destdir-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        canary = Path(tmp) / "injected"
        hostile = f'"; touch "{canary}"; echo "'
        result = theme_install.run_make(
            ["apply", f"DESTDIR={hostile}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR contains a shell metacharacter", result.stderr)
        self.assertIn(hostile, result.stderr)
        self.assertFalse(canary.exists(), hostile)

    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix="apply-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = theme_install.run_make(
            ["apply", f"DESTDIR={destdir}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertNotIn("apply_theme.py", result.stdout + result.stderr)

    def test_dry_run_applies_every_surface_after_installing(self):
        result = theme_install.run_make(
            ["-n", "apply"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        steps = [
            "--no-print-directory install",
            "tools/apply_theme.py",
            "tools/apply_gtk.py",
            "tools/apply_cursor.py --optional",
            "tools/install_firefox.py --optional",
        ]
        positions = []
        for step in steps:
            with self.subTest(step=step):
                self.assertIn(step, result.stdout)
                positions.append(result.stdout.index(step))
        self.assertEqual(sorted(positions), positions, result.stdout)
        self.assertNotIn("apply_keymap.py", result.stdout)

    def test_keymap_targets_are_removed(self):
        help_result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, help_result)
        self.assertNotIn("apply-keymap", help_result.stdout)
        self.assertNotIn("remove-keymap", help_result.stdout)
        for target in ("apply-keymap", "remove-keymap"):
            with self.subTest(target=target):
                result = theme_install.run_make([target], env=theme_install.make_env())
                self.assertNotEqual(0, result.returncode)
                self.assertIn("No rule to make target", result.stderr)

    def test_help_lists_apply(self):
        result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, result)
        self.assertTrue(
            any(line.startswith("  apply ") for line in result.stdout.splitlines()),
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
