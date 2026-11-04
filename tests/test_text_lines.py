import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.text_lines import first_line, split_lines


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


class FirstLineTests(unittest.TestCase):
    def test_uses_the_same_line_breaks_as_split_lines(self):
        self.assertEqual("first", first_line("first\nsecond"))
        self.assertEqual("first", first_line("first\r\nsecond"))
        self.assertEqual("first", first_line("first\rsecond"))

    def test_empty_and_unicode_separator_content_stay_on_the_first_line(self):
        self.assertEqual("", first_line(""))
        self.assertEqual("left\v\u2028right", first_line("left\v\u2028right\nend"))


if __name__ == "__main__":
    unittest.main()
