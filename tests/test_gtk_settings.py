"""Tests for tools/gtk_settings.py's pure ``settings.ini`` text transforms.

``tools/apply_gtk.py`` drives ``set_theme_name`` and ``remove_theme_name``
through the CLI, so ``tests/test_gtk_apply.py`` covers the choose/replace,
insert, append and removal shapes end to end, including a CRLF file read and
written back as bytes. These tests pin the transforms directly and add the
file shapes that suite does not write: spaces around ``=``, a commented-out
key, a leading BOM on removal, a missing final newline, a key before the
first section, and CRLF, lone-CR and mixed line endings. They need no
filesystem or environment.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.gtk_settings import GTK_ID, remove_theme_name, set_theme_name


class TestSetThemeName(unittest.TestCase):
    def test_a_key_with_spaces_around_the_equals_is_replaced(self):
        # GTK's key-file reader accepts ``key = value``; treating that line as
        # foreign would insert a second key and leave the old value in place.
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n",
            set_theme_name("[Settings]\ngtk-theme-name = Adwaita\n", GTK_ID),
        )

    def test_a_commented_out_key_is_kept_and_a_real_key_is_inserted(self):
        self.assertEqual(
            "[Settings]\n"
            "gtk-theme-name=org.macos8.desktop\n"
            "# gtk-theme-name=Adwaita\n"
            "; gtk-theme-name=Adwaita\n",
            set_theme_name(
                "[Settings]\n"
                "# gtk-theme-name=Adwaita\n"
                "; gtk-theme-name=Adwaita\n",
                GTK_ID,
            ),
        )

    def test_a_missing_final_newline_is_preserved(self):
        self.assertEqual(
            "[Settings]\ngtk-theme-name=org.macos8.desktop",
            set_theme_name("[Settings]\ngtk-theme-name=Adwaita", GTK_ID),
        )

    def test_setting_the_same_value_twice_equals_setting_it_once(self):
        once = set_theme_name(
            "[Settings]\ngtk-font-name=Lato 10\ngtk-theme-name=Adwaita\n",
            GTK_ID,
        )
        self.assertEqual(once, set_theme_name(once, GTK_ID))


class TestRemoveThemeName(unittest.TestCase):
    def test_removal_preserves_a_leading_bom(self):
        text, removed = remove_theme_name(
            "\ufeff[Settings]\n"
            "gtk-theme-name=org.macos8.desktop\n"
            "gtk-font-name=Lato 10\n"
        )
        self.assertTrue(removed)
        self.assertEqual("\ufeff[Settings]\ngtk-font-name=Lato 10\n", text)

    def test_a_commented_out_copy_of_our_value_is_kept(self):
        text, removed = remove_theme_name(
            "[Settings]\n"
            "; gtk-theme-name=org.macos8.desktop\n"
            "gtk-theme-name=org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual(
            "[Settings]\n; gtk-theme-name=org.macos8.desktop\n", text
        )

    def test_every_matching_line_is_removed(self):
        text, removed = remove_theme_name(
            "[Settings]\n"
            "gtk-theme-name=org.macos8.desktop\n"
            "gtk-theme-name=org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual("[Settings]\n", text)

    def test_a_key_with_spaces_around_the_equals_is_removed(self):
        text, removed = remove_theme_name(
            "[Settings]\ngtk-theme-name = org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual("[Settings]\n", text)

    def test_a_missing_final_newline_is_preserved(self):
        text, removed = remove_theme_name(
            "[Settings]\ngtk-theme-name=org.macos8.desktop"
        )
        self.assertTrue(removed)
        self.assertEqual("[Settings]", text)

    def test_a_matching_key_before_the_first_section_is_kept(self):
        # A GTK key file with no group has its keys in no section at all;
        # removing a value that only resembles ours outside [Settings] would
        # rewrite a file the tool never selected a theme in.
        text, removed = remove_theme_name(
            "gtk-theme-name=org.macos8.desktop\n"
            "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        )
        self.assertTrue(removed)
        self.assertEqual(
            "gtk-theme-name=org.macos8.desktop\n[Settings]\n", text
        )

    def test_a_foreign_value_reports_no_change(self):
        original = "[Settings]\ngtk-theme-name=Adwaita\n"
        self.assertEqual((original, False), remove_theme_name(original))

    def test_removing_then_setting_restores_the_original_foreign_lines(self):
        original = "[Settings]\ngtk-font-name=Lato 10\n"
        selected = set_theme_name(original, GTK_ID)
        self.assertNotEqual(original, selected)
        self.assertEqual((original, True), remove_theme_name(selected))


class TestLineEndings(unittest.TestCase):
    """A foreign file's CRLF, lone-CR or mixed endings survive an edit."""

    def test_replaces_the_key_and_keeps_crlf_endings(self):
        text = (
            "[Settings]\r\n"
            "gtk-font-name=Lato 10\r\n"
            "# keep this comment\r\n"
            "gtk-theme-name=Adwaita\r\n"
        )
        self.assertEqual(
            "[Settings]\r\n"
            "gtk-font-name=Lato 10\r\n"
            "# keep this comment\r\n"
            f"gtk-theme-name={GTK_ID}\r\n",
            set_theme_name(text, GTK_ID),
        )

    def test_inserts_with_the_section_headers_ending(self):
        text = "[Settings]\r\ngtk-font-name=Lato 10\r\n"
        self.assertEqual(
            f"[Settings]\r\ngtk-theme-name={GTK_ID}\r\n"
            "gtk-font-name=Lato 10\r\n",
            set_theme_name(text, GTK_ID),
        )

    def test_appends_with_the_first_line_ending(self):
        # An appended section copies the file's first ending, so a file that
        # mixes CRLF and LF gets neither normalized nor guessed from its last
        # line.
        text = "gtk-font-name=Lato 10\r\ngtk-icon-theme=Adwaita\n"
        self.assertEqual(
            "gtk-font-name=Lato 10\r\ngtk-icon-theme=Adwaita\n"
            f"[Settings]\r\ngtk-theme-name={GTK_ID}\r\n",
            set_theme_name(text, GTK_ID),
        )

    def test_replaces_the_key_and_keeps_lone_cr_endings(self):
        text = "[Settings]\rgtk-font-name=Lato 10\rgtk-theme-name=Adwaita\r"
        self.assertEqual(
            "[Settings]\rgtk-font-name=Lato 10\r"
            f"gtk-theme-name={GTK_ID}\r",
            set_theme_name(text, GTK_ID),
        )

    def test_removal_keeps_the_foreign_lines_and_endings(self):
        text = (
            "[Settings]\r\n"
            f"gtk-theme-name={GTK_ID}\r\n"
            "gtk-font-name=Lato 10\r\n"
        )
        updated, removed = remove_theme_name(text)
        self.assertTrue(removed)
        self.assertEqual("[Settings]\r\ngtk-font-name=Lato 10\r\n", updated)

    def test_keeps_the_endings_of_a_mixed_ending_file(self):
        text = (
            "[Settings]\r\n"
            "gtk-font-name=Lato 10\n"
            "gtk-theme-name=Adwaita\r\n"
        )
        self.assertEqual(
            "[Settings]\r\n"
            "gtk-font-name=Lato 10\n"
            f"gtk-theme-name={GTK_ID}\r\n",
            set_theme_name(text, GTK_ID),
        )

    def test_removal_keeps_lone_cr_endings(self):
        text = (
            f"[Settings]\rgtk-theme-name={GTK_ID}\r"
            "gtk-font-name=Lato 10\r"
        )
        updated, removed = remove_theme_name(text)
        self.assertTrue(removed)
        self.assertEqual("[Settings]\rgtk-font-name=Lato 10\r", updated)

    def test_removing_an_unterminated_last_line_leaves_no_final_ending(self):
        text = f"[Settings]\r\ngtk-theme-name={GTK_ID}"
        updated, removed = remove_theme_name(text)
        self.assertTrue(removed)
        # The file ended without a line ending; the new last line must too.
        self.assertEqual("[Settings]", updated)

    def test_inserting_after_an_unterminated_header_terminates_it(self):
        # The header is the last line and has no ending; the inserted key
        # needs a separator, so the header gets one and stays followed by an
        # unterminated last line.
        text = "[Other]\r\n[Settings]"
        self.assertEqual(
            f"[Other]\r\n[Settings]\r\ngtk-theme-name={GTK_ID}",
            set_theme_name(text, GTK_ID),
        )

    def test_appending_terminates_an_unterminated_last_line(self):
        # The file has no [Settings] section and its last foreign line has no
        # ending; appending a section must not concatenate it with that line.
        text = "gtk-font-name=Lato 10\r\ngtk-icon-theme=Adwaita"
        self.assertEqual(
            "gtk-font-name=Lato 10\r\ngtk-icon-theme=Adwaita\r\n"
            f"[Settings]\r\ngtk-theme-name={GTK_ID}",
            set_theme_name(text, GTK_ID),
        )

    def test_a_replaced_last_line_without_an_ending_gains_none(self):
        text = "[Settings]\r\ngtk-theme-name=Adwaita"
        self.assertEqual(
            f"[Settings]\r\ngtk-theme-name={GTK_ID}",
            set_theme_name(text, GTK_ID),
        )


if __name__ == "__main__":
    unittest.main()
