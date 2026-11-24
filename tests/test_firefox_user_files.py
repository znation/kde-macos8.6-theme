"""Unit tests for tools/firefox/user_files.py profile text reads.

``read_profile_text`` reads a profile file (userChrome.css, user.js) through a
byte cap of ``MAX_PROFILE_FILE_BYTES``: a file exactly at the cap is read whole,
and a file one byte longer is refused by name before its tail is loaded.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


class TestProfileTextAbsence(unittest.TestCase):
    """A profile file that does not exist reads as ``None``, not an error.

    ``read_profile_text``'s docstring promises ``None`` for an absent path,
    and the install and removal workflows lean on that: profile_actions
    owns a sheet only when ``read_profile_text(sheet_path)`` returns text,
    so a fresh profile must read as ``None`` for every owned file instead
    of raising the wrapped :class:`FileNotFoundError`.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "userChrome.css"

    def test_a_missing_profile_file_reads_as_none(self):
        self.assertFalse(self.path.exists())
        self.assertIsNone(read_profile_text(self.path))


class TestProfilePublish(unittest.TestCase):
    """The publish helpers write bytes verbatim and refuse write failures.

    ``write_profile_text`` publishes its text encoded as UTF-8 and
    ``write_profile_bytes`` publishes *data* at *path* exactly as given;
    a hidden decode or re-encode in either would corrupt a byte round-trip.
    The module's docstring makes :class:`ConfigError` the wrap for a write
    failure so ``main`` can report one ``install_firefox: error:`` line
    instead of letting a bare ``OSError`` traceback escape; the refusal
    must name the action and the path and keep the ``OSError`` as cause.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "userChrome.css"

    def test_published_text_is_encoded_as_utf8_bytes(self):
        text = "café — Platinum\n"
        firefox_user_files.write_profile_text(self.path, text)
        self.assertEqual(text.encode("utf-8"), self.path.read_bytes())

    def test_published_bytes_are_written_verbatim(self):
        # Bytes that are not valid UTF-8 must still land byte-for-byte: the
        # publisher takes *data*, not text, so it must not interpret them.
        data = b"\x00\xff not utf-8\n"
        firefox_user_files.write_profile_bytes(self.path, data)
        self.assertEqual(data, self.path.read_bytes())

    def test_a_failing_write_is_refused_by_path_as_a_config_error(self):
        # The wrap lives here, so this is where its shape is pinned: the
        # raised type is ConfigError (the type main catches to print the
        # one ``install_firefox: error:`` line), the message names the
        # action and the path, and the OSError stays as the cause.
        failure = OSError("simulated write failure")
        with mock.patch.object(
            firefox_user_files, "write_atomically", side_effect=failure
        ):
            with self.assertRaises(ConfigError) as caught:
                firefox_user_files.write_profile_bytes(self.path, b"data")
        message = str(caught.exception)
        self.assertIn("cannot write", message)
        self.assertIn(str(self.path), message)
        self.assertIs(failure, caught.exception.__cause__)
        self.assertFalse(self.path.exists())


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
