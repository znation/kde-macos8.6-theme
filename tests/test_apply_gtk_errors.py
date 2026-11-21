"""Tests for the unreadable and unwritable config-file arms of ``apply_gtk``.

A settings or user-CSS file that cannot be read or written must be one
``apply_gtk: error:`` line naming the path, and every read and write is
staged before any is committed, so a fault leaves the user's files byte for
byte. The workflow, lock and Makefile arms live in
``tests/test_apply_gtk.py`` and ``tests/test_apply_gtk_locks.py``; the
shared temp-root case is ``support.apply_gtk_case``. The non-UTF-8, FIFO and
read-cap refusals live in ``tests/test_apply_gtk_unreadable_config.py``.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.apply_gtk_case import ApplyGtkTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_succeeded,
)
from support.theme_install import write_file
from support.unlink_failure import unlink_failing_for
from tools import gtk_user_files


class TestSettingsErrors(ApplyGtkTestCase):
    """A config file that cannot be read or written is a diagnostic by name."""

    def test_apply_and_remove_refuse_symlinked_config_directories(self):
        self.install_sheet()
        outside = self.root / "dotfiles" / "gtk-4.0"
        settings = outside / "settings.ini"
        css = outside / "gtk.css"
        write_file(settings, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        write_file(
            css,
            f"{gtk_user_files.GTK4_CSS_MARKER}\n@import url(\"file:///old\");\n",
        )
        link = self.config / "gtk-4.0"
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(outside, target_is_directory=True)

        for args, action in (((), "write"), (("--remove",), "remove")):
            with self.subTest(action=action):
                result = self.run_tool(*args)
                assert_exit_2_without_traceback(self, result)
                self.assertIn(f"cannot {action} {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                self.assertEqual(
                    "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
                    settings.read_text(encoding="utf-8"),
                )
                self.assertIn("file:///old", css.read_text(encoding="utf-8"))

    def test_unreadable_settings_file_is_reported_by_name(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=Adwaita\n",
        )
        bad = self.settings("gtk-4.0")
        write_file(bad, b"\xff\xfe[Settings]\n")

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot read {bad}", result.stderr)
        self.assertIn("apply_gtk: error:", result.stderr)
        # Every settings file is read before any is written: the readable
        # gtk-3.0 file keeps its foreign value when the gtk-4.0 read failed.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=Adwaita\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_settings_path_that_is_a_directory_is_reported_by_name(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=Adwaita\n",
        )
        path = self.settings("gtk-4.0")
        path.mkdir(parents=True)

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {path}", result.stderr)
        # Every write is staged before any is committed: the unwritable
        # gtk-4.0 settings path leaves the gtk-3.0 file unchanged.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=Adwaita\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_settings_parent_that_is_a_file_is_reported_by_name(self):
        self.install_sheet()
        path = self.settings("gtk-4.0")
        self.write(path.parent, "not a directory\n")

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {path}", result.stderr)
        self.assertFalse(self.settings("gtk-3.0").exists())

    def test_apply_refuses_a_symlinked_settings_file_before_writing_anything(self):
        self.install_sheet()
        target = self.root / "dotfiles" / "gtk-3.0-settings.ini"
        original = "[Settings]\ngtk-theme-name=Adwaita\n"
        write_file(target, original)
        link = self.settings("gtk-3.0")
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The refused link and the file it names are untouched, and no other
        # settings file or user CSS was staged or written.
        self.assertTrue(link.is_symlink())
        self.assertEqual(original, target.read_text(encoding="utf-8"))
        self.assertFalse(self.settings("gtk-4.0").exists())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_apply_refuses_a_symlinked_user_css_before_writing_anything(self):
        self.install_sheet()
        settings = self.settings("gtk-3.0")
        original = b"[Settings]\r\ngtk-theme-name=Adwaita\r\n"
        self.write_bytes(settings, original)
        target = self.root / "dotfiles" / "gtk.css"
        target.parent.mkdir(parents=True)
        link = self.config / "gtk-4.0" / "gtk.css"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        for css in (
            b"",
            (f'{gtk_user_files.GTK4_CSS_MARKER}\n'
             '@import url("file:///old-sheet.css");\n').encode("utf-8"),
        ):
            with self.subTest(css=css):
                target.write_bytes(css)

                result = self.run_tool()

                assert_exit_2_without_traceback(self, result)
                self.assertIn(f"cannot write {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertEqual(css, target.read_bytes())
                self.assertEqual(original, settings.read_bytes())
                self.assertFalse(self.settings("gtk-4.0").exists())
                self.assertFalse(list(self.config.rglob("*.staging")))

    def test_apply_refuses_dangling_config_links_before_writing_anything(self):
        self.install_sheet()
        paths = (
            self.settings("gtk-3.0"),
            self.settings("gtk-4.0"),
            self.config / "gtk-4.0" / "gtk.css",
        )
        originals = (
            b"[Settings]\r\ngtk-theme-name=Adwaita\r\n",
            b"[Settings]\ngtk-theme-name=Adwaita\n",
            (gtk_user_files.GTK4_CSS_MARKER + "\n").encode("utf-8"),
        )
        target = self.root / "missing-dotfile"
        for link in paths:
            with self.subTest(path=link):
                for path, original in zip(paths, originals):
                    self.write_bytes(path, original)
                link.unlink()
                link.symlink_to(target)

                result = self.run_tool()

                assert_exit_2_without_traceback(self, result)
                self.assertIn(f"cannot write {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertFalse(target.exists())
                self.assertFalse(list(self.config.rglob("*.staging")))
                link.unlink()
                self._assert_others_keep_originals(paths, originals, link)

    def _assert_others_keep_originals(self, paths, originals, link):
        """Assert every path but *link* still holds its original bytes."""
        for path, original in zip(paths, originals):
            if path != link:
                self.assertEqual(original, path.read_bytes())

    def test_a_symlinked_config_home_is_still_supported(self):
        self.install_sheet()
        real_config = self.root / "dotfiles" / "config"
        real_config.mkdir(parents=True)
        self.config.symlink_to(real_config)

        result = self.run_tool()
        assert_succeeded(self, result)
        # The refusal is about a link at the config file itself; a config home
        # that is a symlink is the user's normal layout and still gets written.
        self.assertTrue((real_config / "gtk-3.0" / "settings.ini").is_file())
        self.assertTrue((real_config / "gtk-4.0" / "gtk.css").is_file())

    def test_remove_refuses_a_symlinked_settings_file_before_clearing_anything(self):
        target = self.root / "dotfiles" / "gtk-3.0-settings.ini"
        original = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        write_file(target, original)
        link = self.settings("gtk-3.0")
        link.parent.mkdir(parents=True)
        link.symlink_to(target)
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(
            css,
            f'{gtk_user_files.GTK4_CSS_MARKER}\n@import url("file:///sheet.css");\n',
        )

        result = self.run_tool("--remove")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The settings link was checked before the commit, so the user CSS is
        # still installed and the selection was not cleared through the link.
        self.assertTrue(link.is_symlink())
        self.assertEqual(original, target.read_text(encoding="utf-8"))
        self.assertTrue(css.is_file())

    def test_remove_refuses_a_symlinked_user_css_before_clearing_anything(self):
        settings = self.settings("gtk-3.0")
        original = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        self.write(settings, original)
        target = self.root / "dotfiles" / "gtk.css"
        css_text = (
            f'{gtk_user_files.GTK4_CSS_MARKER}\n'
            '@import url("file:///sheet.css");\n'
        )
        write_file(target, css_text)
        link = self.config / "gtk-4.0" / "gtk.css"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        result = self.run_tool("--remove")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The refused link and the file it names are untouched, and the
        # settings selection was not cleared before the refusal.
        self.assertTrue(link.is_symlink())
        self.assertEqual(css_text, target.read_text(encoding="utf-8"))
        self.assertEqual(original, settings.read_text(encoding="utf-8"))

    def test_remove_reports_an_unreadable_settings_file(self):
        path = self.settings("gtk-3.0")
        write_file(path, b"\xff[Settings]\n")

        result = self.run_tool("--remove")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot read {path}", result.stderr)

    def test_foreign_user_css_that_is_not_utf8_is_reported_by_name(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=Adwaita\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        write_file(css, b"\xff\xfe")

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot read {css}", result.stderr)
        # The user CSS is read before any settings write: neither settings
        # file is created or changed when its read fails.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=Adwaita\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertFalse(self.settings("gtk-4.0").exists())

    def test_unwritable_user_css_write_leaves_settings_unmodified(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=Adwaita\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        css.mkdir(parents=True)

        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {css}", result.stderr)
        # The user CSS is staged after the settings: its failure discards the
        # staged settings, so the gtk-3.0 file is unchanged and the missing
        # gtk-4.0 file is not created.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=Adwaita\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertFalse(self.settings("gtk-4.0").exists())

    def test_remove_reports_an_unreadable_user_css(self):
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        write_file(css, b"\xff\xfe")

        result = self.run_tool("--remove")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot read {css}", result.stderr)
        # The user CSS is read before any settings write: the settings file
        # still carries our selection.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_remove_reports_a_failed_user_css_unlink(self):
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        write_file(
            css,
            f"{gtk_user_files.GTK4_CSS_MARKER}\n@import url(\"file:///sheet.css\");\n",
        )

        # The backup link and the settings replacement succeed, so this
        # reaches the unlink itself, after the settings were changed.
        with unlink_failing_for(css):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot remove {css}", result.stderr)
        self.assertIn("injected unlink failure", result.stderr)
        # The settings were already replaced when the CSS unlink failed, so the
        # rollback restores the gtk-3.0 selection and leaves the CSS in place.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertTrue(css.is_file())


if __name__ == "__main__":
    unittest.main()
