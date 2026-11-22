"""Tests for the ``apply_gtk`` refusals of a config file that cannot be read as text.

A GTK settings or user-CSS file that is not UTF-8, is a FIFO, or is past the
1 MiB read cap must stop the run before anything is written or removed. The
other read and write fault arms live in ``tests/test_apply_gtk_errors.py``;
the shared temp-root case is ``support.apply_gtk_case``.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fifo_fixtures import assert_fifo_refused, fifo_swap_opener, make_fifo
from support.apply_gtk_case import ApplyGtkTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_succeeded,
)
from support.theme_install import write_file
from tools.gtk import user_files as gtk_user_files


class TestUnreadableConfig(ApplyGtkTestCase):
    """A config file that cannot be read stops the run before anything is written.

    The fault is planted in the *second* file the tool would touch, so a fix
    that only reports the error after the first write still fails: the first
    file's bytes must stay exactly as they were.
    """

    def assert_gtk3_unchanged(self, expected):
        """Assert rejection left GTK 3 settings byte-for-byte intact."""
        self.assertEqual(expected, self.settings("gtk-3.0").read_bytes())

    def assert_settings_unchanged(self, gtk3_expected, gtk4_expected):
        """Assert rejection preserved both GTK settings files."""
        self.assert_gtk3_unchanged(gtk3_expected)
        self.assertEqual(gtk4_expected, self.settings("gtk-4.0").read_bytes())

    def test_apply_refuses_a_non_utf8_settings_file_before_writing_anything(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=Adwaita\n")
        before = gtk3.read_bytes()
        gtk4 = self.settings("gtk-4.0")
        write_file(gtk4, b"[Settings]\ngtk-theme-name=\xff\n")

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn("settings.ini", result.stderr)
        self.assertIn("utf-8", result.stderr)
        self.assert_gtk3_unchanged(before)
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

        assert_exit_2_without_traceback(self, result)
        self.assertIn("utf-8", result.stderr)
        self.assert_gtk3_unchanged(gtk3_before)
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
        self.assert_gtk3_unchanged(before)
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_a_fifo_swapped_in_for_a_regular_settings_file_is_refused(self):
        # A regular file can become a FIFO between a path check and the open.
        # Patching os.open to open the FIFO while the path still names a
        # regular file proves the guard inspects the opened descriptor, so the
        # swap is refused by name instead of blocking on or reading the pipe.
        gtk4 = self.settings("gtk-4.0")
        self.write(gtk4, "[Settings]\ngtk-theme-name=Adwaita\n")
        fifo = self.root / "pipe"
        make_fifo(self, fifo)
        open_the_fifo = fifo_swap_opener(fifo)

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
        self.assert_gtk3_unchanged(before)
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
        self.assert_gtk3_unchanged(before)
        self.assertTrue(css.is_file())

    def test_remove_refuses_a_fifo_user_css_before_clearing_anything(self):
        gtk3 = self.settings("gtk-3.0")
        self.write(gtk3, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        before = gtk3.read_bytes()
        css = self.config / "gtk-4.0" / "gtk.css"
        make_fifo(self, css)

        result = self.run_tool_in_child("--remove")

        assert_fifo_refused(self, result, css)
        self.assert_gtk3_unchanged(before)

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

        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(gtk4), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assert_gtk3_unchanged(before)
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

        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(css), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assert_settings_unchanged(gtk3_before, gtk4_before)
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
        write_file(gtk4, data)

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
        write_file(gtk4, data)

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(gtk4), result.stderr)
        self.assertIn("1048576-byte limit", result.stderr)
        self.assert_settings_unchanged(gtk3_before, data)
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())


if __name__ == "__main__":
    unittest.main()
