"""The Platinum block edit in `tools/ghostty_config.py`, on bytes and without I/O.

The block is the three lines the Ghostty apply writes; the expected bytes below
are written out from the marker text in the backlog entry, never computed by
the code under test.
"""

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import ghostty_config
from tools.ghostty_config import GhosttyConfigError, apply_block, remove_block

THEME = b"/home/u/.local/share/ghostty/themes/org.macos8.desktop/Platinum"
BLOCK = (
    b"# >>> Platinum theme (managed by make apply-ghostty) >>>\n"
    b"theme = " + THEME + b"\n"
    b"# <<< Platinum theme <<<\n"
)


class TestApplyBlock(unittest.TestCase):
    def test_appends_block_after_a_file_ending_in_newline(self):
        self.assertEqual(
            apply_block(b"font-size = 12\n", THEME),
            b"font-size = 12\n" + BLOCK,
        )

    def test_empty_file_gets_only_the_block(self):
        self.assertEqual(apply_block(b"", THEME), BLOCK)

    def test_file_without_trailing_newline_gets_one_before_the_block(self):
        self.assertEqual(apply_block(b"font-size = 12", THEME), b"font-size = 12\n" + BLOCK)

    def test_existing_block_is_replaced_in_place_keeping_both_sides(self):
        data = b"before = 1\n" + BLOCK + b"after = 2\n"
        self.assertEqual(apply_block(data, THEME), data)

    def test_stale_block_content_is_replaced(self):
        stale = (
            b"# >>> Platinum theme (managed by make apply-ghostty) >>>\n"
            b"theme = /old/path\n"
            b"# <<< Platinum theme <<<\n"
        )
        data = b"x = 1\n" + stale + b"y = 2\n"
        self.assertEqual(apply_block(data, THEME), b"x = 1\n" + BLOCK + b"y = 2\n")

    def test_theme_path_with_line_break_is_refused(self):
        with self.assertRaises(GhosttyConfigError):
            apply_block(b"", THEME + b"\nfont-size = 99")

    def test_theme_path_with_carriage_return_is_refused(self):
        with self.assertRaises(GhosttyConfigError):
            apply_block(b"", THEME + b"\rfont-size = 99")

    def test_end_marker_before_begin_marker_is_refused_not_spliced(self):
        data = b"# <<< Platinum theme <<<\nx = 1\n" + BLOCK.split(b"theme = ")[0]
        with self.assertRaises(GhosttyConfigError):
            apply_block(data, THEME)

    def test_applying_to_a_file_without_final_newline_is_idempotent(self):
        once = apply_block(b"font-size = 12", THEME)
        self.assertEqual(apply_block(once, THEME), once)

    def test_crlf_block_is_found_and_replaced_keeping_crlf_outside_it(self):
        # The marker lines end in CRLF in a CRLF file; they are still the
        # block's markers, so the block is replaced where it stands and the
        # CRLF bytes on both sides are kept exactly.
        crlf_block = BLOCK.replace(b"\n", b"\r\n")
        data = b"x = 1\r\n" + crlf_block + b"y = 2\r\n"
        self.assertEqual(apply_block(data, THEME), b"x = 1\r\n" + BLOCK + b"y = 2\r\n")

    def test_block_whose_end_marker_is_the_last_line_without_newline_is_replaced(self):
        # BLOCK[:-1] drops only the final newline after the end marker, so the
        # marker is still the block's last line and the file ends inside it.
        data = b"x = 1\n" + BLOCK[:-1]
        self.assertEqual(apply_block(data, THEME), b"x = 1\n" + BLOCK)


class TestRemoveBlock(unittest.TestCase):
    def test_block_whose_end_marker_is_the_last_line_without_newline_is_removed(self):
        self.assertEqual(remove_block(b"font-size = 12\n" + BLOCK[:-1]), b"font-size = 12\n")

    def test_block_only_without_final_newline_becomes_empty(self):
        self.assertEqual(remove_block(BLOCK[:-1]), b"")

    def test_restores_bytes_before_the_block(self):
        self.assertEqual(remove_block(b"background = #000000\n" + BLOCK), b"background = #000000\n")

    def test_block_only_becomes_empty(self):
        self.assertEqual(remove_block(BLOCK), b"")

    def test_file_without_block_is_unchanged(self):
        data = b"theme = other\r\nfont-size = 12"
        self.assertEqual(remove_block(data), data)

    def test_removing_restores_the_newline_the_apply_added(self):
        applied = apply_block(b"font-size = 12", THEME)
        self.assertEqual(remove_block(applied), b"font-size = 12\n")

    def test_crlf_block_is_removed_and_the_crlf_before_it_is_kept(self):
        crlf_block = BLOCK.replace(b"\n", b"\r\n")
        self.assertEqual(remove_block(b"background = #000000\r\n" + crlf_block),
                         b"background = #000000\r\n")

    def test_end_marker_before_begin_marker_is_refused_not_spliced(self):
        data = b"# <<< Platinum theme <<<\nx = 1\n" + BLOCK.split(b"theme = ")[0]
        with self.assertRaises(GhosttyConfigError):
            remove_block(data)

    def test_begin_marker_without_end_is_refused(self):
        with self.assertRaises(GhosttyConfigError):
            remove_block(BLOCK.split(b"# <<<")[0])

    def test_end_marker_without_begin_is_refused(self):
        with self.assertRaises(GhosttyConfigError):
            remove_block(b"# <<< Platinum theme <<<\n")

    def test_repeated_block_is_refused(self):
        with self.assertRaises(GhosttyConfigError):
            remove_block(BLOCK + BLOCK)

    def test_marker_text_inside_a_longer_line_is_not_a_marker(self):
        data = b"# note: " + ghostty_config.END_MARKER + b"\n"
        self.assertEqual(remove_block(data), data)


if __name__ == "__main__":
    unittest.main()
