import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.text_lines import split_lines


class SplitLinesTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
