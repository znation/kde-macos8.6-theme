"""Tests for the installed GTK sheet lookup used before selection."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401
from tools.gtk_selection import installed_sheet, installed_sheets


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


if __name__ == "__main__":
    unittest.main()
