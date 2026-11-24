"""Unit tests for tools/firefox/user_files.py profile text reads.

``read_profile_text`` reads a profile file (userChrome.css, user.js) through a
byte cap of ``MAX_PROFILE_FILE_BYTES``: a file exactly at the cap is read whole,
and a file one byte longer is refused by name before its tail is loaded.
"""

import os
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.firefox import user_files as firefox_user_files
from tools.firefox.user_files import ConfigError, read_profile_text

CAP = firefox_user_files.MAX_PROFILE_FILE_BYTES


class TestProfileTextCap(unittest.TestCase):
    """A profile text file is accepted up to the cap and refused one byte past it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "userChrome.css"

    def _write_ascii(self, length: int) -> str:
        text = "a" * length
        self.path.write_bytes(text.encode("ascii"))
        return text

    def test_a_file_exactly_at_the_cap_is_read_whole(self):
        expected = self._write_ascii(CAP)
        self.assertEqual(CAP, os.stat(self.path).st_size)
        self.assertEqual(expected, read_profile_text(self.path))

    def test_a_file_one_byte_past_the_cap_is_refused_by_name(self):
        self._write_ascii(CAP + 1)
        with self.assertRaises(ConfigError) as caught:
            read_profile_text(self.path)
        message = str(caught.exception)
        self.assertIn(str(self.path), message)
        self.assertIn("larger than", message)


class TestProfileTextRefusals(unittest.TestCase):
    """A non-UTF-8 or non-regular profile file is refused by name.

    ``read_profile_text``'s docstring promises that a directory, a
    non-regular file and invalid UTF-8 are each reported as a
    :class:`ConfigError` naming the path, rather than escaping as a
    traceback; these pins hold it to that contract at the unit level.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "userChrome.css"

    def test_an_invalid_utf8_profile_file_is_refused_by_name(self):
        # The decode refusal is the read_failure wrap: without it the raw
        # UnicodeDecodeError escapes the installer, which reports only
        # ConfigError, so the raised type is the contract under test.
        self.path.write_bytes(b"\xff\xfe not utf-8")
        with self.assertRaises(ConfigError) as caught:
            read_profile_text(self.path)
        message = str(caught.exception)
        self.assertIn(str(self.path), message)
        self.assertIn("cannot read", message)

    def test_a_directory_at_the_path_is_refused_by_name(self):
        # A directory passes open() and is rejected on the opened
        # descriptor's fstat; the refusal must be the ConfigError naming
        # the path, not an escaping IsADirectoryError.
        self.path.mkdir()
        with self.assertRaises(ConfigError) as caught:
            read_profile_text(self.path)
        self.assertIn(str(self.path), str(caught.exception))


if __name__ == "__main__":
    unittest.main()
