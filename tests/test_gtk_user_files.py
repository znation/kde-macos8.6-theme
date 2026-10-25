"""Direct tests for tools/gtk_user_files.py.

``tests/test_gtk_apply.py`` drives these helpers through the whole tool; these
pin the read and user-CSS decisions on their own: which occupants read as
"nothing there", that line endings survive the read untouched, and what the
write and remove decisions return for each kind of ``gtk.css``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import gtk_user_files


class TestReadConfigText(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_a_missing_file_reads_as_none(self):
        self.assertIsNone(gtk_user_files.read_config_text(self.directory / "no"))

    def test_a_path_below_a_regular_file_reads_as_none(self):
        parent = self.directory / "file"
        parent.write_text("x", encoding="utf-8")
        self.assertIsNone(gtk_user_files.read_config_text(parent / "settings.ini"))

    def test_a_directory_reads_as_none(self):
        self.assertIsNone(gtk_user_files.read_config_text(self.directory))

    def test_every_line_ending_and_the_bom_survive_the_read(self):
        path = self.directory / "settings.ini"
        raw = "﻿a\r\nb\rc\nd"
        path.write_bytes(raw.encode("utf-8"))
        self.assertEqual(raw, gtk_user_files.read_config_text(path))

    def test_an_empty_file_reads_as_empty_text_not_none(self):
        path = self.directory / "empty"
        path.write_bytes(b"")
        self.assertEqual("", gtk_user_files.read_config_text(path))

    def test_invalid_utf8_is_refused_naming_the_file(self):
        path = self.directory / "bad.ini"
        path.write_bytes(b"\xff\xfe")
        with self.assertRaises(gtk_user_files.ConfigError) as caught:
            gtk_user_files.read_config_text(path)
        self.assertIn(str(path), str(caught.exception))


class TestUserCssDecisions(unittest.TestCase):
    def setUp(self):
        self.config = tmp_dir.make_tmp_dir(self)
        self.sheet = self.config / "share" / "gtk.css"
        self.notes: list[str] = []

    def css(self, text: str | None) -> Path:
        path = gtk_user_files.user_css_path(self.config)
        if text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
        return path

    def write(self):
        return gtk_user_files.user_css_write(self.config, self.sheet, self.notes.append)

    def test_paths_sit_below_the_versioned_config_directories(self):
        self.assertEqual(
            self.config / "gtk-3.0" / "settings.ini",
            gtk_user_files.settings_path(self.config, "gtk-3.0"),
        )
        self.assertEqual(
            self.config / "gtk-4.0" / "gtk.css",
            gtk_user_files.user_css_path(self.config),
        )

    def test_a_missing_file_gets_the_marker_and_an_import_of_the_sheet(self):
        path = self.css(None)
        self.assertEqual(
            (
                path,
                f'{gtk_user_files.GTK4_CSS_MARKER}\n'
                f'@import url("{self.sheet.as_uri()}");\n',
            ),
            self.write(),
        )
        self.assertEqual([], self.notes)

    def test_our_marker_led_file_is_rewritten_even_with_other_content(self):
        path = self.css(f"{gtk_user_files.GTK4_CSS_MARKER}\r\nold\n")
        result = self.write()
        self.assertEqual(path, result[0])
        self.assertNotIn("old", result[1])

    def test_a_marker_only_on_a_later_line_is_foreign(self):
        path = self.css(f"a {{}}\n{gtk_user_files.GTK4_CSS_MARKER}\n")
        self.assertIsNone(self.write())
        self.assertEqual([f"{path} exists but is not our user CSS; leaving it untouched"], self.notes)

    def test_remove_returns_the_path_only_for_our_file(self):
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))
        path = self.css("a {}\n")
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))
        self.css(f"{gtk_user_files.GTK4_CSS_MARKER}\n")
        self.assertEqual(path, gtk_user_files.user_css_remove(self.config))

    def test_remove_keeps_an_empty_file(self):
        self.css("")
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))


if __name__ == "__main__":
    unittest.main()
