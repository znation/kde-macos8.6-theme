"""Tests for the Kvantum selection removal tool and its transform.

``tools/kvantum_selection.py`` removes only the ``[General] theme=
org.macos8.desktop`` line ``kvantummanager --set`` writes, leaving every
other line of ``kvantum.kvconfig`` byte-identical; the driver runs in-process
with ``XDG_CONFIG_HOME`` and ``HOME`` pointed at a temp root, so no user
configuration is touched. The Makefile target and the uninstall diagnostic
are pinned in ``tests/test_kvantum_selection_make.py``. The line surgery
reuses ``tools/gtk_settings``' scanners, whose own behaviour its existing
tests pin; the tests here pin what the Kvantum tool builds on them.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main_with_env
from support.flock_fixtures import hold_directory_flock
from support.theme_install import write_file
from support.tmp_dir import make_tmp_dir
from tools import kvantum_selection


class TestRemoveThemeTransform(unittest.TestCase):
    """The pure transform: only our ``[General] theme`` line disappears."""

    def test_removes_our_line_and_keeps_every_other_byte(self):
        text = (
            "[General]\r\n"
            "Author=KvantumAlt\r\n"
            "theme=org.macos8.desktop\r\n"
            "\n"
            ";a CRLF-less comment\n"
            "[SomeOtherPanel]\n"
            "theme=surface\n"
        )
        updated, removed = kvantum_selection.remove_theme(text)
        self.assertTrue(removed)
        self.assertEqual(
            "[General]\r\n"
            "Author=KvantumAlt\r\n"
            "\n"
            ";a CRLF-less comment\n"
            "[SomeOtherPanel]\n"
            "theme=surface\n",
            updated,
        )

    def test_removes_every_duplicate_of_ours_the_last_one_included(self):
        # Removal is a line filter, not a duplicate-override read: every
        # matching line disappears, foreign lines around them survive.
        updated, removed = kvantum_selection.remove_theme(
            "[General]\ntheme=KvArc\ntheme=org.macos8.desktop\ntheme=KvArc\ntheme=org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual("[General]\ntheme=KvArc\ntheme=KvArc\n", updated)

    def test_a_foreign_theme_value_is_left_untouched(self):
        for text in (
            "[General]\ntheme=KvBreezeDark\n",
            "[General]\ntheme=\n",
            "[General]\n",
            "[Other]\ntheme=org.macos8.desktop\n",
        ):
            with self.subTest(text=text):
                self.assertEqual((text, False), kvantum_selection.remove_theme(text))

    def test_comments_and_indented_keys_are_treated_like_the_scanner(self):
        before = "[General]\n  # comment\n  theme = org.macos8.desktop  \n;theme=org.macos8.desktop\n"
        updated, removed = kvantum_selection.remove_theme(before)
        self.assertTrue(removed)
        self.assertEqual("[General]\n  # comment\n;theme=org.macos8.desktop\n", updated)

    def test_a_bom_is_preserved(self):
        # A leading UTF-8 BOM hides nothing: the same selection under it is
        # found and removed, and the BOM is kept on the way back.
        updated, removed = kvantum_selection.remove_theme(
            "\ufeff[General]\ntheme=org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual("\ufeff[General]\n", updated)

    def test_an_unterminated_last_line_stays_unterminated(self):
        updated, removed = kvantum_selection.remove_theme(
            "[General]\ntheme=org.macos8.desktop"
        )
        self.assertTrue(removed)
        self.assertEqual("[General]", updated)


class RemoveKvantumCase(unittest.TestCase):
    """Base with a temp config home so the driver never sees the real one."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.config = self.root / "config"
        self.kvconfig = self.config / "Kvantum" / "kvantum.kvconfig"
        self.env = {
            "XDG_CONFIG_HOME": str(self.config),
            "HOME": str(self.root / "home"),
        }

    def run_tool(self):
        return run_main_with_env(
            kvantum_selection.main, "remove_kvantum", [], self.env
        )

    def write(self, text, path=None):
        path = path if path is not None else self.kvconfig
        write_file(path, text)

    def read_bytes(self):
        return self.kvconfig.read_bytes()


class TestSelectionRemoval(RemoveKvantumCase):
    """The driver: clear ours, leave the rest byte-identical, create nothing."""

    def test_clears_our_selection_and_keeps_every_other_byte(self):
        original = (
            "\ufeff[General]\nForeign=1 ;keep\n"
            "theme=org.macos8.desktop\n"
            "[Panel]\ntheme=surface\n"
        )
        self.write(original)

        result = self.run_tool()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(self.kvconfig), result.stdout)
        self.assertEqual(
            b"\xef\xbb\xbf[General]\nForeign=1 ;keep\n[Panel]\ntheme=surface\n",
            self.read_bytes(),
        )

    def test_a_second_run_is_idempotent_and_prints_the_untouched_note(self):
        self.write("[General]\ntheme=org.macos8.desktop\n")
        first = self.run_tool()
        self.assertEqual(0, first.returncode)
        before = self.read_bytes()

        second = self.run_tool()

        self.assertEqual(0, second.returncode, second.stderr)
        self.assertIn("untouched", second.stdout)
        self.assertIn(str(self.kvconfig), second.stdout)
        self.assertEqual(before, self.read_bytes())

    def test_an_absent_file_and_directory_are_left_absent(self):
        nested = self.root / "deeper" / "config"
        self.env["XDG_CONFIG_HOME"] = str(nested)
        self.env["HOME"] = str(self.root / "home")
        result = run_main_with_env(
            kvantum_selection.main, "remove_kvantum", [], self.env
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(nested / "Kvantum" / "kvantum.kvconfig"), result.stdout)
        # Nothing is created: the absent kvconfig is not made, and neither is
        # the config home itself.
        self.assertFalse(nested.exists())

    def test_a_foreign_theme_leaves_the_file_byte_identical(self):
        text = "[General]\ntheme=KvBreezeDark\nthemeExtra=1\n"
        self.write(text)

        result = self.run_tool()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("untouched", result.stdout)
        self.assertEqual(text.encode("utf-8"), self.read_bytes())

    def test_our_id_in_another_section_is_left_alone(self):
        self.write("[NotGeneral]\ntheme=org.macos8.desktop\n")

        result = self.run_tool()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("untouched", result.stdout)
        self.assertEqual(
            b"[NotGeneral]\ntheme=org.macos8.desktop\n", self.read_bytes()
        )

    def test_a_symlinked_kvconfig_is_refused_without_reading_or_writing_it(self):
        victim = self.root / "victim.kvconfig"
        victim.write_text("[General]\ntheme=org.macos8.desktop\n", encoding="utf-8")
        self.config.mkdir(parents=True, exist_ok=True)
        self.kvconfig.parent.mkdir(parents=True, exist_ok=True)
        self.kvconfig.symlink_to(victim)

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(self.kvconfig), result.stderr)
        self.assertIn("symbolic link", result.stderr)
        self.assertEqual(
            b"[General]\ntheme=org.macos8.desktop\n", victim.read_bytes()
        )

    def test_a_directory_at_the_kvconfig_path_is_refused_not_called_absent(
        self,
    ):
        self.kvconfig.mkdir(parents=True)

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(self.kvconfig), result.stderr)
        self.assertIn("is a directory", result.stderr)
        self.assertNotIn("absent", result.stdout + result.stderr)
        # The directory occupying the path is left exactly as it was.
        self.assertTrue(self.kvconfig.is_dir())

    def test_a_regular_file_at_the_kvantum_directory_path_is_refused(self):
        directory = self.config / "Kvantum"
        write_file(directory, "theme=KvBreezeDark\n")

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(directory), result.stderr)
        self.assertIn("not a directory", result.stderr)
        self.assertNotIn("absent", result.stdout + result.stderr)
        self.assertEqual(
            b"theme=KvBreezeDark\n",
            directory.read_bytes(),
        )

    def test_a_symlinked_kvantum_directory_is_refused(self):
        victim = self.root / "victim-dir"
        victim.mkdir()
        self.config.mkdir(parents=True, exist_ok=True)
        (self.config / "Kvantum").symlink_to(victim)

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(self.config / "Kvantum"), result.stderr)
        self.assertFalse(self.kvconfig.exists())

    def test_an_unresolvable_config_home_is_refused_naming_both_variables(self):
        self.env["XDG_CONFIG_HOME"] = "relative"
        self.env["HOME"] = ""
        result = run_main_with_env(
            kvantum_selection.main, "remove_kvantum", [], self.env
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("XDG_CONFIG_HOME", result.stderr)
        self.assertIn("HOME", result.stderr)
        self.assertFalse(self.config.exists())

    def test_an_expired_lock_takes_exit_2_naming_remove_kvantum(self):
        self.write("[General]\ntheme=org.macos8.desktop\n")
        lock_dir = self.config.parent
        lock_dir.mkdir(parents=True, exist_ok=True)
        hold_directory_flock(self, lock_dir)
        before = self.read_bytes()

        with mock.patch.object(kvantum_selection, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("remove-kvantum", result.stderr)
        self.assertIn(str(self.config), result.stderr)
        self.assertEqual(before, self.read_bytes())

    def test_script_entry_point_and_module_run_are_covered_once(self):
        # `run_tool` calls `main` in-process; each launcher is spawned once so
        # the direct-run and package-run import guards stay covered.
        self.write("[General]\ntheme=org.macos8.desktop\n")
        script = Path(repo_root.ROOT) / "tools" / "kvantum_selection.py"
        for argv in (
            [sys.executable, str(script)],
            [sys.executable, "-m", "tools.kvantum_selection"],
        ):
            with self.subTest(argv=argv[1:]):
                result = subprocess.run(
                    argv,
                    cwd=repo_root.ROOT,
                    capture_output=True,
                    text=True,
                    env=dict(os.environ, **self.env),
                    timeout=60,
                )
                self.assertEqual(0, result.returncode, result.stderr + result.stdout)
                self.assertEqual(b"[General]\n", self.read_bytes())
                self.write("[General]\ntheme=org.macos8.desktop\n")


if __name__ == "__main__":
    unittest.main()
