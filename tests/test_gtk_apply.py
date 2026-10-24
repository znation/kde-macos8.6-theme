"""Tests for tools/apply_gtk.py and the `make apply-gtk`/`remove-gtk` targets.

The tool runs in-process with ``XDG_DATA_HOME``, ``XDG_CONFIG_HOME`` and
``HOME`` pointed at a temp root, so the settings edit, the libadwaita user CSS
and the removal are pinned without touching the user's configuration. The
Makefile pins drive the public targets through ``theme_install``, which applies
the suite's timeout to each child process.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import snippet_child
from support import theme_install
from support.cli_fixtures import run_main
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools import apply_gtk


class GtkApplyCase(unittest.TestCase):
    """Base with a temp data/config/home root and an installed GTK 4 sheet."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.data = self.root / "data"
        self.config = self.root / "config"
        self.home = self.root / "home"
        self.sheet = (
            self.data / "themes" / apply_gtk.GTK_ID / "gtk-4.0" / "gtk.css"
        )
        self.env = {
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "HOME": str(self.home),
        }

    def run_tool(self, *args):
        with mock.patch.dict(os.environ, self.env, clear=True):
            return run_main(apply_gtk.main, "apply_gtk", args)

    def run_tool_in_child(self, *args):
        """Run the tool in a child so a FIFO open that slips through times out.

        ``run_tool`` cannot bound a blocking ``open``: if the guard regresses,
        the call hangs the whole check instead of failing this test. The child
        inherits ``self.env`` and is killed at the timeout, like the suite's
        other FIFO guards.
        """
        snippet = (
            "import sys; from tools.apply_gtk import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        with mock.patch.dict(os.environ, self.env, clear=True):
            return snippet_child.run(
                [snippet, *args], cwd=repo_root.ROOT, timeout=10
            )

    def install_sheet(self, *versions):
        """Write the installed sheet for each *versions* (both by default)."""
        for version in versions or ("gtk-3.0", "gtk-4.0"):
            sheet = self.data / "themes" / apply_gtk.GTK_ID / version / "gtk.css"
            sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.write_text("/* installed sheet */\n", encoding="utf-8")

    def settings(self, version):
        return self.config / version / "settings.ini"

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_bytes(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class TestApply(GtkApplyCase):
    def test_apply_writes_both_settings_and_user_css(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\n"
            "gtk-font-name=Lato 10\n"
            "# keep this comment\n"
            "gtk-theme-name=Adwaita\n",
        )
        result = self.run_tool()
        assert_succeeded(self, result)

        gtk3 = self.settings("gtk-3.0").read_text(encoding="utf-8")
        self.assertIn("gtk-font-name=Lato 10", gtk3)
        self.assertIn("# keep this comment", gtk3)
        self.assertIn("gtk-theme-name=org.macos8.desktop", gtk3)
        self.assertNotIn("Adwaita", gtk3)

        gtk4 = self.settings("gtk-4.0").read_text(encoding="utf-8")
        self.assertIn("[Settings]", gtk4)
        self.assertIn("gtk-theme-name=org.macos8.desktop", gtk4)

        css = (self.config / "gtk-4.0" / "gtk.css").read_text(encoding="utf-8")
        lines = css.splitlines()
        self.assertEqual(apply_gtk.GTK4_CSS_MARKER, lines[0])
        self.assertEqual(f'@import url("{self.sheet.as_uri()}");', lines[1])
        self.assertIn("restart", result.stdout)

    def test_apply_appends_settings_when_absent(self):
        self.install_sheet()
        self.write(self.settings("gtk-4.0"), "gtk-font-name=Lato 10\n")
        result = self.run_tool()
        assert_succeeded(self, result)
        gtk4 = self.settings("gtk-4.0").read_text(encoding="utf-8")
        self.assertIn("[Settings]", gtk4)
        self.assertIn("gtk-theme-name=org.macos8.desktop", gtk4)
        self.assertIn("gtk-font-name=Lato 10", gtk4)

    def test_apply_leaves_a_foreign_section_key_alone(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Other]\ngtk-theme-name=Adwaita\n",
        )
        result = self.run_tool()
        assert_succeeded(self, result)
        # The tool edits only [Settings]: a same-named key in a foreign
        # section keeps its value and gains nothing from our selection.
        self.assertEqual(
            "[Other]\ngtk-theme-name=Adwaita\n"
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_apply_keeps_a_leading_bom_for_matching_and_writing(self):
        self.install_sheet()
        self.write(self.settings("gtk-3.0"), "\ufeff[Settings]\ngtk-theme-name=Adwaita\n")
        result = self.run_tool()
        assert_succeeded(self, result)
        gtk3 = self.settings("gtk-3.0").read_text(encoding="utf-8")
        self.assertTrue(gtk3.startswith("\ufeff"))
        self.assertIn("gtk-theme-name=org.macos8.desktop", gtk3)
        self.assertNotIn("Adwaita", gtk3)

    def test_missing_sheet_names_make_install_gtk(self):
        result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn("make install-gtk", result.stderr)
        self.assertIn("gtk-4.0/gtk.css", result.stderr)

    def test_missing_gtk3_sheet_names_make_install_gtk(self):
        # Selecting the theme in gtk-3.0/settings.ini would point GTK 3 at a
        # theme whose only sheet is absent; refuse before writing either
        # settings file, naming the GTK 3 sheet rather than letting the GTK 4
        # sheet hide it.
        self.install_sheet("gtk-4.0")
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=Adwaita\n",
        )
        result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn("make install-gtk", result.stderr)
        self.assertIn("gtk-3.0/gtk.css", result.stderr)
        self.assertEqual(
            "[Settings]\ngtk-theme-name=Adwaita\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertFalse(self.settings("gtk-4.0").exists())

    def test_empty_user_css_is_adopted(self):
        self.install_sheet()
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write_bytes(css, b"")
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertEqual(
            f'{apply_gtk.GTK4_CSS_MARKER}\n@import url("{self.sheet.as_uri()}");\n',
            css.read_text(encoding="utf-8"),
        )
        self.assertNotIn("not our user CSS", result.stdout)

    def test_foreign_user_css_is_left_byte_identical_with_a_note(self):
        self.install_sheet()
        css = self.config / "gtk-4.0" / "gtk.css"
        foreign = "/* my own user css */\n@import url(\"file:///tmp/other.css\");\n"
        self.write(css, foreign)
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertEqual(foreign, css.read_text(encoding="utf-8"))
        self.assertIn("gtk.css", result.stdout)


class TestSettingsErrors(GtkApplyCase):
    """A config file that cannot be read or written is a diagnostic by name."""

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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {path}", result.stderr)
        self.assertFalse(self.settings("gtk-3.0").exists())

    def test_remove_reports_an_unreadable_settings_file(self):
        path = self.settings("gtk-3.0")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff[Settings]\n")

        result = self.run_tool("--remove")
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
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
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot read {css}", result.stderr)
        # The user CSS is read before any settings write: the settings file
        # still carries our selection.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_remove_reports_a_failed_user_css_unlink(self):
        if os.geteuid() == 0:
            self.skipTest("root ignores a read-only directory")
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        css.parent.mkdir(parents=True, exist_ok=True)
        css.write_text(
            f"{apply_gtk.GTK4_CSS_MARKER}\n@import url(\"file:///sheet.css\");\n",
            encoding="utf-8",
        )
        css.parent.chmod(0o500)
        self.addCleanup(css.parent.chmod, 0o700)

        result = self.run_tool("--remove")
        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {css}", result.stderr)
        # The settings write is only staged when the unlink fails, so the
        # gtk-3.0 selection is left untouched.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertTrue(css.is_file())


class TestRemove(GtkApplyCase):
    def test_remove_deletes_our_key_and_marker_but_keeps_other_lines(self):
        self.install_sheet()
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\n"
            "gtk-theme-name=org.macos8.desktop\n"
            "gtk-font-name=Lato 10\n",
        )
        self.write(
            self.settings("gtk-4.0"),
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        applied = self.run_tool()
        assert_succeeded(self, applied)
        css = self.config / "gtk-4.0" / "gtk.css"
        self.assertTrue(css.is_file())

        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        gtk3 = self.settings("gtk-3.0").read_text(encoding="utf-8")
        self.assertNotIn("gtk-theme-name", gtk3)
        self.assertIn("gtk-font-name=Lato 10", gtk3)
        gtk4 = self.settings("gtk-4.0").read_text(encoding="utf-8")
        self.assertNotIn("gtk-theme-name", gtk4)
        self.assertFalse(css.exists())
        self.assertIn("restart", result.stdout)

    def test_remove_keeps_a_matching_key_outside_settings(self):
        self.write(
            self.settings("gtk-3.0"),
            "[Other]\ngtk-theme-name=org.macos8.desktop\n"
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        # A value that happens to equal ours is not ours to delete outside
        # [Settings]; only the [Settings] line goes.
        self.assertEqual(
            "[Other]\ngtk-theme-name=org.macos8.desktop\n[Settings]\n",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )

    def test_remove_leaves_a_foreign_key_and_file_byte_identical(self):
        foreign_settings = "[Settings]\ngtk-theme-name=Adwaita\n# mine\n"
        self.write(self.settings("gtk-3.0"), foreign_settings)
        self.write(self.settings("gtk-4.0"), foreign_settings)
        foreign_css = "/* foreign user css */\n"
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, foreign_css)

        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertEqual(
            foreign_settings,
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            foreign_settings,
            self.settings("gtk-4.0").read_text(encoding="utf-8"),
        )
        self.assertEqual(foreign_css, css.read_text(encoding="utf-8"))

    def test_remove_clears_the_selection_without_a_resolvable_data_home(self):
        # Removal reads and writes only the config home. A user who sets an
        # absolute XDG_CONFIG_HOME but has no usable HOME or XDG_DATA_HOME can
        # still clear the selection; requiring the data home would refuse a
        # removal that never touches it.
        self.write(
            self.settings("gtk-3.0"),
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
        )
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, apply_gtk.GTK4_CSS_MARKER + "\n")

        with mock.patch.dict(
            os.environ, {"XDG_CONFIG_HOME": str(self.config)}, clear=True
        ):
            result = run_main(apply_gtk.main, "apply_gtk", ("--remove",))

        assert_succeeded(self, result)
        self.assertNotIn(
            "gtk-theme-name",
            self.settings("gtk-3.0").read_text(encoding="utf-8"),
        )
        self.assertFalse(css.exists())


class TestLineEndings(GtkApplyCase):
    """A CRLF or mixed-ending settings file keeps its endings end to end."""

    def test_apply_keeps_crlf_endings_in_both_settings_files(self):
        self.install_sheet()
        self.write_bytes(
            self.settings("gtk-3.0"),
            b"[Settings]\r\ngtk-font-name=Lato 10\r\ngtk-theme-name=Adwaita\r\n",
        )
        self.write_bytes(
            self.settings("gtk-4.0"),
            b"[Settings]\r\ngtk-font-name=Lato 10\r\n",
        )
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertEqual(
            b"[Settings]\r\ngtk-font-name=Lato 10\r\n"
            b"gtk-theme-name=org.macos8.desktop\r\n",
            self.settings("gtk-3.0").read_bytes(),
        )
        self.assertEqual(
            b"[Settings]\r\ngtk-theme-name=org.macos8.desktop\r\n"
            b"gtk-font-name=Lato 10\r\n",
            self.settings("gtk-4.0").read_bytes(),
        )

    def test_remove_keeps_the_foreign_lines_and_mixed_endings(self):
        self.write_bytes(
            self.settings("gtk-3.0"),
            b"[Settings]\r\ngtk-theme-name=org.macos8.desktop\r\n"
            b"gtk-font-name=Lato 10\r\n",
        )
        self.write_bytes(
            self.settings("gtk-4.0"),
            b"[Settings]\r\ngtk-theme-name=org.macos8.desktop\n"
            b"gtk-font-name=Lato 10\r\n",
        )
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertEqual(
            b"[Settings]\r\ngtk-font-name=Lato 10\r\n",
            self.settings("gtk-3.0").read_bytes(),
        )
        self.assertEqual(
            b"[Settings]\r\ngtk-font-name=Lato 10\r\n",
            self.settings("gtk-4.0").read_bytes(),
        )


class TestUnreadableConfig(GtkApplyCase):
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

        with mock.patch.object(apply_gtk.os, "open", side_effect=open_the_fifo):
            with self.assertRaises(apply_gtk.ConfigError) as caught:
                apply_gtk._read_config_text(gtk4)
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
        self.write(css, f"{apply_gtk.GTK4_CSS_MARKER}\n")

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
            handle.truncate(apply_gtk._MAX_CONFIG_FILE_BYTES + 1)

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
            handle.truncate(apply_gtk._MAX_CONFIG_FILE_BYTES + 1)

        result = self.run_tool("--remove")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(str(css), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(gtk3_before, gtk3.read_bytes())
        self.assertEqual(gtk4_before, gtk4.read_bytes())
        self.assertEqual(
            apply_gtk._MAX_CONFIG_FILE_BYTES + 1, css.stat().st_size
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


class TestHomeResolution(unittest.TestCase):
    def test_absolute_data_home_is_used_even_without_home(self):
        self.assertEqual(
            Path("/data"),
            apply_gtk._data_home(
                {"XDG_DATA_HOME": "/data", "XDG_CONFIG_HOME": "/config"}
            ),
        )

    def test_empty_data_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.local/share"),
            apply_gtk._data_home({"XDG_DATA_HOME": "", "HOME": "/home/u"}),
        )

    def test_relative_data_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.local/share"),
            apply_gtk._data_home(
                {"XDG_DATA_HOME": "relative", "HOME": "/home/u"}
            ),
        )

    def test_absolute_config_home_is_used_even_without_home(self):
        self.assertEqual(
            Path("/config"), apply_gtk._config_home({"XDG_CONFIG_HOME": "/config"})
        )

    def test_empty_config_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.config"),
            apply_gtk._config_home({"XDG_CONFIG_HOME": "", "HOME": "/home/u"}),
        )

    def test_relative_config_home_falls_back_to_home(self):
        self.assertEqual(
            Path("/home/u/.config"),
            apply_gtk._config_home(
                {"XDG_CONFIG_HOME": "relative", "HOME": "/home/u"}
            ),
        )

    def _run_with(self, env):
        with mock.patch.dict(os.environ, env, clear=True):
            return run_main(apply_gtk.main, "apply_gtk", ())

    def test_missing_data_home_names_xdg_data_home(self):
        result = self._run_with(
            {"XDG_DATA_HOME": "relative", "XDG_CONFIG_HOME": "/config"}
        )
        assert_failed(self, result)
        self.assertIn("XDG_DATA_HOME", result.stderr)

    def test_missing_config_home_names_xdg_config_home(self):
        result = self._run_with(
            {"XDG_DATA_HOME": "/data", "XDG_CONFIG_HOME": "relative"}
        )
        assert_failed(self, result)
        self.assertIn("XDG_CONFIG_HOME", result.stderr)


class TestMakeApplyGtk(unittest.TestCase):
    def test_dry_run_shows_install_before_the_script(self):
        result = theme_install.run_make(
            ["-n", "apply-gtk"],
            env=theme_install.make_env("XDG_DATA_HOME"),
        )
        assert_succeeded(self, result)
        self.assertIn("INSTALL_PACKAGES=gtk", result.stdout)
        self.assertIn("tools/apply_gtk.py", result.stdout)
        self.assertLess(
            result.stdout.index("INSTALL_PACKAGES=gtk"),
            result.stdout.index("tools/apply_gtk.py"),
        )

    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix="apply-gtk-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = theme_install.run_make(
            ["apply-gtk", f"DESTDIR={destdir}"],
            env=theme_install.make_env(),
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR must be empty", result.stderr)
        self.assertNotIn("apply_gtk.py", result.stdout + result.stderr)

    def test_python_version_is_refused(self):
        tmp = make_tmp_dir(self)
        fake = tmp / "python"
        fake.write_text("#!/bin/sh\nexit 3\n", encoding="utf-8")
        fake.chmod(0o755)
        result = theme_install.run_make(
            ["apply-gtk", f"PYTHON={fake}"],
            env=theme_install.make_env("PYTHON"),
        )
        assert_failed(self, result)
        self.assertIn("Python 3.10 or newer", result.stderr)
        self.assertIn(str(fake), result.stderr)

    def test_dry_run_shows_remove_script(self):
        result = theme_install.run_make(
            ["-n", "remove-gtk"], env=theme_install.make_env()
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_gtk.py --remove", result.stdout)

    def test_help_lists_both_targets(self):
        result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, result)
        lines = result.stdout.splitlines()
        self.assertTrue(
            any(line.startswith("  apply-gtk ") for line in lines), result.stdout
        )
        self.assertTrue(
            any(line.startswith("  remove-gtk ") for line in lines), result.stdout
        )


if __name__ == "__main__":
    unittest.main()
