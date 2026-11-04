"""Tests for the selection workflow's offline helpers and file shapes.

The installed-sheet lookup that must precede a selection is pinned here,
so are the ``tools.gtk_selection.remove`` clearing shapes that only a
directly driven unit test can build.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401
from tools.gtk_selection import (
    GTK_ID,
    installed_sheet,
    installed_sheets,
    remove,
)
from tools.gtk_user_files import GTK4_CSS_MARKER, settings_path


class TestInstalledSheets(unittest.TestCase):
    def test_missing_first_sheet_reports_gtk4_before_gtk3(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = io.StringIO()

            with contextlib.redirect_stderr(errors):
                result = installed_sheets(Path(directory))

            self.assertIsNone(result)
            self.assertIn("installed gtk-4.0 sheet is missing", errors.getvalue())
            self.assertNotIn("installed gtk-3.0 sheet is missing", errors.getvalue())

    def test_returns_both_installed_sheets(self):
        with tempfile.TemporaryDirectory() as directory:
            data_home = Path(directory)
            expected = {}
            for version in ("gtk-3.0", "gtk-4.0"):
                path = installed_sheet(data_home, version)
                path.parent.mkdir(parents=True)
                path.write_text("/* sheet */", encoding="utf-8")
                expected[version] = path

            self.assertEqual(installed_sheets(data_home), expected)

    def test_missing_second_sheet_refuses_partial_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            data_home = Path(directory)
            gtk4 = installed_sheet(data_home, "gtk-4.0")
            gtk4.parent.mkdir(parents=True)
            gtk4.write_text("/* sheet */", encoding="utf-8")
            errors = io.StringIO()

            with contextlib.redirect_stderr(errors):
                result = installed_sheets(data_home)

            self.assertIsNone(result)
            self.assertIn("installed gtk-3.0 sheet is missing", errors.getvalue())
            self.assertIn("make install-gtk", errors.getvalue())


class TestRemoveSelection(unittest.TestCase):
    """The selection removal's file shapes, driven directly.

    ``tests/test_apply_gtk.py`` drives ``remove`` through the CLI with the
    full file set an install publishes; these exercise the removal itself on
    the shapes the CLI runs do not build -- every file absent, only one
    settings file present -- so an absent file is pinned to skip silently
    while the present twin is still cleared, and nothing is created.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / "config"

    def our_settings(self, foreign_line: str) -> str:
        """Return settings text naming our theme beside a foreign line."""
        return (
            "[Settings]\n"
            f"{foreign_line}\n"
            f"gtk-theme-name={GTK_ID}\n"
        )

    def write_our_css(self) -> Path:
        """Create the marker-led user CSS ``remove`` deletes."""
        path = self.config / "gtk-4.0" / "gtk.css"
        path.parent.mkdir(parents=True)
        path.write_text(f"{GTK4_CSS_MARKER}\n@import url('sheet');\n", encoding="utf-8")
        return path

    def run_remove(self) -> tuple[int, str]:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = remove(self.config)
        return status, stderr.getvalue()

    def test_a_config_home_with_nothing_of_ours_is_a_silent_no_op(self):
        # read_config_text returns None for every missing file, and none of
        # them is ours, so remove must stage no write and no removal: the
        # config home (absent itself) gains nothing and no note is printed.
        status, stderr = self.run_remove()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)
        self.assertFalse(self.config.exists(), "remove created user files")

    def test_one_present_settings_file_is_cleared_while_the_absent_twin_stays_absent(
        self,
    ):
        # Only gtk-3.0's settings file exists (a partial install or a GTK 3
        # client that ran first). The removal must still clear it and the
        # marker-led user CSS, and must not write into the absent gtk-4.0
        # config directory; the directory read as None is the same shape.
        self.write_our_css()
        gtk3 = settings_path(self.config, "gtk-3.0")
        gtk3.parent.mkdir(parents=True)
        gtk3.write_text(
            self.our_settings("gtk-font-name=Lato 10"), encoding="utf-8"
        )
        status, stderr = self.run_remove()
        self.assertEqual(0, status, stderr)
        self.assertNotIn("org.macos8.desktop", gtk3.read_text(encoding="utf-8"))
        self.assertIn("gtk-font-name=Lato 10", gtk3.read_text(encoding="utf-8"))
        self.assertFalse(
            settings_path(self.config, "gtk-4.0").exists(),
            "remove wrote the absent gtk-4.0 settings file",
        )
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())

    def test_a_second_removal_after_ours_is_gone_is_silent_and_byte_identical(
        self,
    ):
        self.write_our_css()
        for name in ("gtk-3.0", "gtk-4.0"):
            path = settings_path(self.config, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                self.our_settings("gtk-font-name=Lato 10"), encoding="utf-8"
            )
        status, stderr = self.run_remove()
        self.assertEqual(0, status, stderr)
        before = {
            path: path.read_text(encoding="utf-8")
            for name in ("gtk-3.0", "gtk-4.0")
            for path in [settings_path(self.config, name)]
        }

        status, stderr = self.run_remove()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)
        for path, text in before.items():
            self.assertEqual(text, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
