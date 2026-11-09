"""Direct tests for the kcminputrc reads tests/test_apply_cursor.py leaves open.

``TestCursorThemeSetting`` in the apply-cursor suite already pins the
reader's parsing contract directly: only the ``[Mouse]`` section counts,
comment lines hold no value, surrounding whitespace is trimmed, a BOM is
stripped, and a non-UTF-8 file or a directory reads as no setting. A FIFO
at the path is pinned indirectly there by
``TestRemove.test_a_fifo_kcminputrc_does_not_block_removal``, which shows
the removal still finishes with the FIFO in place. This module holds the
two behaviors that suite never exercises: a missing ``kcminputrc`` reads
as no setting, and a later ``cursorTheme`` line overrides an earlier one.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import cursor_config


class TestCursorThemeSetting(unittest.TestCase):
    def setUp(self):
        self.config_home = tmp_dir.make_tmp_dir(self)

    def test_a_missing_kcminputrc_reads_as_no_setting(self):
        # The docstring reads a missing file as None: the removal's note
        # about the selection must not depend on the file existing.
        self.assertIsNone(cursor_config.cursor_theme_setting(self.config_home))

    def test_a_later_cursor_theme_value_overrides_an_earlier_one(self):
        # The reader keeps the last cursorTheme line's value, like the
        # config files the KDE reader keeps.
        (self.config_home / "kcminputrc").write_text(
            "[Mouse]\ncursorTheme=ours\ncursorTheme=theirs\n",
            encoding="utf-8",
        )
        self.assertEqual(
            "theirs", cursor_config.cursor_theme_setting(self.config_home)
        )


if __name__ == "__main__":
    unittest.main()
