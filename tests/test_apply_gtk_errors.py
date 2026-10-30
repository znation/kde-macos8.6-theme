"""Tests for the unreadable and unwritable config-file arms of ``apply_gtk``.

A settings or user-CSS file that cannot be read or written must be one
``apply_gtk: error:`` line naming the path, and every read and write is
staged before any is committed, so a fault leaves the user's files byte for
byte. The workflow, lock and Makefile arms live in
``tests/test_apply_gtk.py`` and ``tests/test_apply_gtk_locks.py``; the
shared temp-root case is ``support.apply_gtk_case``.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.apply_gtk_case import ApplyGtkTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_succeeded,
)
from support.unlink_failure import unlink_failing_for
from tools import gtk_user_files


class TestSettingsErrors(ApplyGtkTestCase):
    """A config file that cannot be read or written is a diagnostic by name."""

    def test_apply_and_remove_refuse_symlinked_config_directories(self):
        self.install_sheet()
        outside = self.root / "dotfiles" / "gtk-4.0"
        outside.mkdir(parents=True)
        settings = outside / "settings.ini"
        css = outside / "gtk.css"
        settings.write_text(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n", encoding="utf-8"
        )
        css.write_text(
            f"{gtk_user_files.GTK4_CSS_MARKER}\n@import url(\"file:///old\");\n",
            encoding="utf-8",
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
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_bytes(b"\xff\xfe[Settings]\n")

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
        target.parent.mkdir(parents=True)
        original = "[Settings]\ngtk-theme-name=Adwaita\n"
        target.write_text(original, encoding="utf-8")
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
                for path, original in zip(paths, originals):
                    if path != link:
                        self.assertEqual(original, path.read_bytes())
                self.assertFalse(list(self.config.rglob("*.staging")))
                link.unlink()

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
        target.parent.mkdir(parents=True)
        original = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        target.write_text(original, encoding="utf-8")
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
        target.parent.mkdir(parents=True)
        css_text = (
            f'{gtk_user_files.GTK4_CSS_MARKER}\n'
            '@import url("file:///sheet.css");\n'
        )
        target.write_text(css_text, encoding="utf-8")
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff[Settings]\n")

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
        css.parent.mkdir(parents=True, exist_ok=True)
        css.write_bytes(b"\xff\xfe")

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
        css.parent.mkdir(parents=True, exist_ok=True)
        css.write_bytes(b"\xff\xfe")

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
        css.parent.mkdir(parents=True, exist_ok=True)
        css.write_text(
            f"{gtk_user_files.GTK4_CSS_MARKER}\n@import url(\"file:///sheet.css\");\n",
            encoding="utf-8",
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


class TestUnreadableConfig(ApplyGtkTestCase):
    """A config file that cannot be read stops the run before anything is written.

    The fault is planted in the *second* file the tool would touch, so a fix
    that only reports the error after the first write still fails: the first
    file's bytes must stay exactly as they were.
    """

    def test_apply_refuses_a_non_utf8_settings_file_before_writing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        gtk4.parent.mkdir(parents=True, exist_ok=True)
        gtk4.write_bytes(b"[Settings]\ngtk-theme-name=\xff\n")

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("settings.ini", result.stderr)
        self.assertIn("utf-8", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(before, gtk3.read_bytes())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_remove_refuses_a_non_utf8_settings_file_before_clearing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        assert_succeeded(self, self.run_tool())
        css = self.config / "gtk-4.0" / "gtk.css"
        self.assertTrue(css.is_file())
        gtk3_before = gtk3.read_bytes()
        self.settings("gtk-4.0").write_bytes(
            b"[Settings]\ngtk-theme-name=\xff\n"
        )

        result = self.run_tool("--remove")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("utf-8", result.stderr)
        self.assertEqual(gtk3_before, gtk3.read_bytes())
        self.assertTrue(css.is_file())

    def test_apply_refuses_a_fifo_settings_file_before_writing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        make_fifo(self, gtk4)

        result = self.run_tool_in_child()

        assert_fifo_refused(self, result, gtk4)
        self.assertEqual(before, gtk3.read_bytes())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_a_fifo_swapped_in_for_a_regular_settings_file_is_refused(self):
        # A regular file can become a FIFO between a path check and the open.
        # Patching os.open to open the FIFO while the path still names a
        # regular file proves the guard inspects the opened descriptor, so the
        # swap is refused by name instead of blocking on or reading the pipe.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        gtk4 = self.settings("gtk-4.0")
        self.write(gtk4, "[Settings]\ngtk-theme-name=Adwaita\n")
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        real_open = os.open

        def open_the_fifo(target, flags, *args, **kwargs):
            # O_RDWR makes the test itself independent of the flags under
            # test, so a missing O_NONBLOCK fails the assertion, not the run.
            return real_open(fifo, os.O_RDWR | os.O_NONBLOCK)

        with mock.patch.object(gtk_user_files.os, "open", side_effect=open_the_fifo):
            with self.assertRaises(gtk_user_files.ConfigError) as caught:
                gtk_user_files.read_config_text(gtk4)
        self.assertIn(f"cannot read {gtk4}", str(caught.exception))
        self.assertIn("not a regular file", str(caught.exception))

    def test_apply_refuses_a_fifo_user_css_before_writing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        before = gtk3.read_bytes()
        css = self.config / "gtk-4.0" / "gtk.css"
        make_fifo(self, css)

        result = self.run_tool_in_child()

        assert_fifo_refused(self, result, css)
        self.assertEqual(before, gtk3.read_bytes())
        self.assertFalse(self.settings("gtk-4.0").exists())

    def test_remove_refuses_a_fifo_settings_file_before_clearing_anything(self):
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        make_fifo(self, gtk4)
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, f"{gtk_user_files.GTK4_CSS_MARKER}\n")

        result = self.run_tool_in_child("--remove")

        assert_fifo_refused(self, result, gtk4)
        self.assertEqual(before, gtk3.read_bytes())
        self.assertTrue(css.is_file())

    def test_remove_refuses_a_fifo_user_css_before_clearing_anything(self):
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        before = gtk3.read_bytes()
        css = self.config / "gtk-4.0" / "gtk.css"
        make_fifo(self, css)

        result = self.run_tool_in_child("--remove")

        assert_fifo_refused(self, result, css)
        self.assertEqual(before, gtk3.read_bytes())

    def test_apply_refuses_an_oversize_settings_file_before_writing_anything(
        self,
    ):
        # Reading a multi-gigabyte settings file whole would exhaust memory,
        # and MemoryError is not an OSError, so it would escape as a traceback
        # instead of the documented exit 2. A sparse file keeps the test cheap.
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        gtk4.parent.mkdir(parents=True, exist_ok=True)
        with gtk4.open("wb") as handle:
            handle.truncate(gtk_user_files.MAX_CONFIG_FILE_BYTES + 1)

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(gtk4), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(before, gtk3.read_bytes())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_remove_refuses_an_oversize_user_css_before_clearing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        assert_succeeded(self, self.run_tool())
        gtk3_before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        gtk4_before = gtk4.read_bytes()
        css = self.config / "gtk-4.0" / "gtk.css"
        with css.open("wb") as handle:
            handle.truncate(gtk_user_files.MAX_CONFIG_FILE_BYTES + 1)

        result = self.run_tool("--remove")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(css), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(gtk3_before, gtk3.read_bytes())
        self.assertEqual(gtk4_before, gtk4.read_bytes())
        self.assertEqual(
            gtk_user_files.MAX_CONFIG_FILE_BYTES + 1, css.stat().st_size
        )

    def test_a_settings_file_at_the_1_mib_cap_is_accepted(self):
        # One byte past the cap is refused; exactly 1 MiB is the accepted
        # boundary, so the documented cap is pinned by an actual file rather
        # than only by one past the private constant.
        self.install_sheet()
        cap = 1 << 20
        head = b"[Settings]\ngtk-theme-name=Adwaita-Longer-Name\n"
        pad = cap - len(head)
        data = head + b"#" + b"x" * (pad - 2) + b"\n"
        self.assertEqual(cap, len(data))
        gtk4 = self.settings("gtk-4.0")
        gtk4.parent.mkdir(parents=True, exist_ok=True)
        gtk4.write_bytes(data)

        result = self.run_tool()

        assert_succeeded(self, result)
        self.assertIn(
            "gtk-theme-name=org.macos8.desktop", gtk4.read_text("utf-8")
        )
        self.assertLess(gtk4.stat().st_size, cap)
        self.assertTrue((self.config / "gtk-4.0" / "gtk.css").is_file())

    def test_an_apply_that_would_grow_a_settings_file_past_the_cap_is_refused(
        self,
    ):
        # The reader accepts exactly 1 MiB, but replacing a shorter foreign
        # gtk-theme-name with ours would grow that file past the cap; a
        # successful apply must never create a settings file the reader itself
        # refuses, or every later apply and removal would exit 2.
        self.install_sheet()
        cap = 1 << 20
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        gtk3_before = gtk3.read_bytes()
        head = b"[Settings]\ngtk-theme-name=Adwaita\n"
        pad = cap - len(head)
        data = head + b"#" + b"x" * (pad - 2) + b"\n"
        self.assertEqual(cap, len(data))
        gtk4 = self.settings("gtk-4.0")
        gtk4.parent.mkdir(parents=True, exist_ok=True)
        gtk4.write_bytes(data)

        result = self.run_tool()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(gtk4), result.stderr)
        self.assertIn("1048576-byte limit", result.stderr)
        self.assertEqual(gtk3_before, gtk3.read_bytes())
        self.assertEqual(data, gtk4.read_bytes())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())



if __name__ == "__main__":
    unittest.main()
