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


if __name__ == "__main__":
    unittest.main()
