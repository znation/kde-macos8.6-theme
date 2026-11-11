"""Tests for ``tools/text_lines.py``'s line splitting and first-line readers."""

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.text_lines import first_line, has_first_line_marker, split_lines


class SplitLinesTests(unittest.TestCase):
    """Tests for ``split_lines``' line-break handling."""

    def test_splits_lf_crlf_and_bare_cr(self):
        self.assertEqual(split_lines("first\nsecond\r\nthird\rfourth"), [
            "first", "second", "third", "fourth",
        ])

    def test_preserves_other_unicode_separators(self):
        self.assertEqual(split_lines("left\vmiddle\u2028right\u2029end"), [
            "left\vmiddle\u2028right\u2029end",
        ])

    def test_preserves_empty_lines_and_empty_input(self):
        self.assertEqual(split_lines(""), [""])
        self.assertEqual(split_lines("\n\r\r\n"), ["", "", "", ""])


class FirstLineTests(unittest.TestCase):
    """Tests for ``first_line``'s line-break handling."""

    def test_uses_the_same_line_breaks_as_split_lines(self):
        self.assertEqual("first", first_line("first\nsecond"))
        self.assertEqual("first", first_line("first\r\nsecond"))
        self.assertEqual("first", first_line("first\rsecond"))

    def test_empty_and_unicode_separator_content_stay_on_the_first_line(self):
        self.assertEqual("", first_line(""))
        self.assertEqual("left\v\u2028right", first_line("left\v\u2028right\nend"))


class FirstLineMarkerTests(unittest.TestCase):
    """Tests for ``has_first_line_marker``'s exact-match handling."""

    def test_matches_exact_first_line_with_optional_bom_and_supported_endings(self):
        for text in ("marker\nrest", "\ufeffmarker\r\nrest", "marker\rrest"):
            with self.subTest(text=text):
                self.assertTrue(has_first_line_marker(text, "marker"))

    def test_rejects_prefixes_extra_boms_and_later_lines(self):
        for text in ("marker extra", "\ufeff\ufeffmarker", "other\nmarker"):
            with self.subTest(text=text):
                self.assertFalse(has_first_line_marker(text, "marker"))


if __name__ == "__main__":
    unittest.main()
