"""Tests for tools/terminal.py -- escaping contributor text for terminal output.

Both command-line tools route repository- and shell-supplied text through
`escape_controls` before printing it, but their tests pass only three control
bytes (ESC, newline and BEL) through the tools themselves. These tests pin the
shared function's contract directly, so a change to its predicate or escape
format is caught here instead of silently weakening both tools' terminal safety.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import terminal  # noqa: E402


class TestEscapeControls(unittest.TestCase):
    def test_empty_string_is_unchanged(self):
        self.assertEqual(terminal.escape_controls(""), "")

    def test_printable_text_is_returned_unchanged(self):
        # A path is mostly ordinary text: spaces, punctuation and letters must
        # survive so the diagnostic still names the real file.
        text = "reference set/desktop_betawiki.png (8.6) [ok]?"
        self.assertEqual(terminal.escape_controls(text), text)

    def test_non_ascii_printable_text_is_preserved(self):
        # Contributor filenames may be non-ASCII; only non-printable
        # characters are escaped, not the whole string.
        text = "caf\u00e9-\u4e2d\u6587-\U0001f600.png"
        self.assertEqual(terminal.escape_controls(text), text)

    def test_every_c0_c1_and_del_control_is_escaped(self):
        # ESC drives the terminal, newline forges a diagnostic line, and the
        # remaining C0/C1 controls and DEL are equally unprintable; each must
        # appear as a visible \uXXXX escape instead of reaching the terminal.
        codepoints = (
            list(range(0x00, 0x20)) + [0x7F] + list(range(0x80, 0xA0))
        )
        for codepoint in codepoints:
            with self.subTest(codepoint=codepoint):
                self.assertEqual(
                    terminal.escape_controls(chr(codepoint)),
                    "\\u%04x" % codepoint,
                )

    def test_format_and_bidi_controls_are_escaped(self):
        # Zero-width and bidi-override characters are non-printable: left raw
        # they can reorder or hide the diagnostic text on a terminal, so they
        # must be escaped too, not only the C0 controls.
        for codepoint in (0x200B, 0x202E):
            with self.subTest(codepoint=codepoint):
                self.assertEqual(
                    terminal.escape_controls(chr(codepoint)),
                    "\\u%04x" % codepoint,
                )

    def test_mixed_text_escapes_only_the_control_characters(self):
        self.assertEqual(
            terminal.escape_controls("a\nb\x1bc"),
            "a\\u000ab\\u001bc",
        )


if __name__ == "__main__":
    unittest.main()
