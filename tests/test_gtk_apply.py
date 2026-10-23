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
from support import theme_install
from support.cli_fixtures import run_main
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

    def install_sheet(self):
        self.sheet.parent.mkdir(parents=True, exist_ok=True)
        self.sheet.write_text("/* installed sheet */\n", encoding="utf-8")

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
