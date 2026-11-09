"""Direct tests for tools/cursor_config.py.

The apply-cursor CLI suite exercises three arm outcomes through
`cursor_workflow` (our selection warns, a foreign selection stays silent, a
FIFO stays silent); these pin the reader's own parsing contract, which those
end-to-end arms never reach: only the ``[Mouse]`` section counts, comments
hold no value, a later value overrides an earlier one, surrounding value
whitespace is trimmed, and a BOM-prefixed, non-UTF-8 or missing file reads
as no setting instead of escaping an error.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import cursor_config


class TestCursorThemeSetting(unittest.TestCase):
    def setUp(self):
        self.config_home = tmp_dir.make_tmp_dir(self)

    def write(self, body: bytes | str) -> None:
        path = self.config_home / "kcminputrc"
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body, encoding="utf-8")

    def test_a_missing_kcminputrc_reads_as_no_setting(self):
        # The docstring reads a missing file as None: the removal's note
        # about the selection must not depend on the file existing.
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config_home))

    def test_a_cursor_theme_line_under_a_foreign_section_is_ignored(self):
        # Only ``[Mouse] cursorTheme`` reads as the selection; a same-named
        # key under another group must not count toward the reset note.
        self.write("[Mice]\ncursorTheme=org.macos8.desktop\n")
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config_home))

    def test_a_comment_line_never_carries_the_selection(self):
        # Lines the parser skips (# and ;) must not check whether the
        # remaining text parses as a value.
        self.write(
            "# cursorTheme=org.macos8.desktop\n"
            ";cursorTheme=org.macos8.desktop\n"
        )
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config_home))

    def test_a_later_cursor_theme_value_overrides_an_earlier_one(self):
        # The reader keeps the last cursorTheme line's value, like the
        # config files the KDE reader keeps.
        self.write("[Mouse]\ncursorTheme=ours\ncursorTheme=theirs\n")
        self.assertEqual(
            "theirs", cursor_config.cursor_theme_setting(self.config_home)
        )

    def test_surrounding_value_whitespace_is_trimmed(self):
        self.write("[Mouse]\ncursorTheme=  ours  \n")
        self.assertEqual("ours", cursor_config.cursor_theme_setting(self.config_home))

    def test_a_bom_prefixed_kcminputrc_still_names_its_section(self):
        # The file is decoded as ``utf-8-sig``: an editor-added BOM must
        # not turn the first ``[Mouse]`` heading into a foreign line.
        self.write(b"\xef\xbb\xbf[Mouse]\ncursorTheme=ours\n")
        self.assertEqual("ours", cursor_config.cursor_theme_setting(self.config_home))

    def test_a_non_utf8_kcminputrc_reads_as_no_setting(self):
        # A decoding failure reads as None per the docstring, so the
        # caller keeps its removal path instead of escaping an error.
        self.write(b"\xff\xfe\x00\x00")
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config_home))


if __name__ == "__main__":
    unittest.main()
