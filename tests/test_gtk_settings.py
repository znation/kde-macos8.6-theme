"""Tests for tools/gtk_settings.py's pure ``settings.ini`` text transforms.

``tools/apply_gtk.py`` drives ``set_theme_name`` and ``remove_theme_name``
through the CLI, so ``tests/test_gtk_apply.py`` covers the choose/replace,
insert and append shapes end to end. These tests pin the transforms directly
and add the file shapes that suite does not write: spaces around ``=``, a
commented-out key, a leading BOM on removal, a missing final newline, and a
key before the first section. They need no filesystem or environment.

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


if __name__ == "__main__":
    unittest.main()
