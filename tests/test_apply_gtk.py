"""Tests for the apply_gtk CLI and its GTK selection workflow.

The tool runs in-process with ``XDG_DATA_HOME``, ``XDG_CONFIG_HOME`` and
``HOME`` pointed at a temp root, so the settings edit, the libadwaita user
CSS and the removal are pinned without touching the user's configuration.
The unreadable and unwritable config-file arms live in
``tests/test_apply_gtk_errors.py`` and the serialization locks in
``tests/test_apply_gtk_locks.py``; the shared temp-root case is
``support.apply_gtk_case``. The Makefile pins drive the public targets
through ``theme_install``, which applies the suite's timeout to each child
process.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.apply_target_cases import ApplyTargetMakeCases
from support.cli_fixtures import run_main
from support.apply_gtk_case import ApplyGtkTestCase
from support.process_assertions import assert_failed, assert_succeeded
from tools import apply_gtk, gtk_user_files


class TestApply(ApplyGtkTestCase):
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
        self.assertEqual(gtk_user_files.GTK4_CSS_MARKER, lines[0])
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
            f'{gtk_user_files.GTK4_CSS_MARKER}\n@import url("{self.sheet.as_uri()}");\n',
            css.read_text(encoding="utf-8"),
        )
        self.assertNotIn("not our user CSS", result.stdout)

    def test_a_bom_before_our_marker_keeps_the_user_css_ours(self):
        # A UTF-8 BOM is valid in a CSS file and some editors add one. It must
        # not make our marker-led stylesheet look foreign: the apply rewrites
        # it with the current import and the removal deletes it.
        self.install_sheet()
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, f"\ufeff{gtk_user_files.GTK4_CSS_MARKER}\n")

        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertEqual(
            f'{gtk_user_files.GTK4_CSS_MARKER}\n@import url("{self.sheet.as_uri()}");\n',
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


class TestRemove(ApplyGtkTestCase):
    def test_a_failed_settings_commit_restores_the_selection_and_user_css(self):
        self.install_sheet()
        gtk3 = self.settings("gtk-3.0")
        gtk3_before = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        self.write(gtk3, gtk3_before)
        gtk4 = self.settings("gtk-4.0")
        gtk4_before = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        self.write(gtk4, gtk4_before)
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, f"{gtk_user_files.GTK4_CSS_MARKER}\n")
        real_replace = os.replace

        def fail_the_gtk4_staged_rename(source, destination, *args, **kwargs):
            # The gtk3 replacement has already happened and the user CSS is
            # part of the same commit, so the failure must roll both back.
            if Path(destination) == gtk4 and str(source).endswith(".staging"):
                raise OSError("injected rename failure")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            os, "replace", side_effect=fail_the_gtk4_staged_rename
        ):
            result = self.run_tool("--remove")

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {gtk4}", result.stderr)
        self.assertEqual(gtk3_before, gtk3.read_text(encoding="utf-8"))
        self.assertEqual(gtk4_before, gtk4.read_text(encoding="utf-8"))
        self.assertTrue(css.is_file())

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

    def test_remove_deletes_a_bom_prefixed_our_user_css(self):
        settings = self.settings("gtk-3.0")
        self.write(settings, "[Settings]\ngtk-theme-name=org.macos8.desktop\n")
        css = self.config / "gtk-4.0" / "gtk.css"
        self.write(css, f"\ufeff{gtk_user_files.GTK4_CSS_MARKER}\n")

        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertFalse(css.exists())
        self.assertNotIn(
            "gtk-theme-name", settings.read_text(encoding="utf-8")
        )

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
        self.write(css, gtk_user_files.GTK4_CSS_MARKER + "\n")

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


class TestLineEndings(ApplyGtkTestCase):
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


class TestHomeResolution(unittest.TestCase):
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


class TestMakeApplyGtk(ApplyTargetMakeCases, unittest.TestCase):
    TARGET = "apply-gtk"
    REMOVE_TARGET = "remove-gtk"
    INSTALL_PACKAGES = "gtk"
    SCRIPT = "tools/apply_gtk.py"



if __name__ == "__main__":
    unittest.main()
