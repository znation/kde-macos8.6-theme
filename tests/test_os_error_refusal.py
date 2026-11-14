"""Direct tests for tools/os_error_refusal.py's ``refusing_os_errors`` block wrap."""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.os_error_refusal import refusing_os_errors


class RefusalError(Exception):
    """A stand-in for a caller's own refusal class."""


class TestRefusingOsErrors(unittest.TestCase):
    def test_an_os_error_becomes_the_given_class_naming_action_and_path(self):
        cause = OSError("boom")
        with self.assertRaises(RefusalError) as caught:
            with refusing_os_errors(RefusalError, "write", Path("/a/b")):
                raise cause
        self.assertEqual(str(caught.exception), "cannot write /a/b: boom")
        self.assertIs(caught.exception.__cause__, cause)

    def test_a_non_os_error_passes_through_unchanged(self):
        with self.assertRaises(ValueError) as caught:
            with refusing_os_errors(RefusalError, "remove", Path("/a/b")):
                raise ValueError("not an OS failure")
        self.assertEqual(str(caught.exception), "not an OS failure")

    def test_a_block_without_an_error_does_nothing(self):
        ran = []
        with refusing_os_errors(RefusalError, "create", Path("/a/b")):
            ran.append(True)
        self.assertEqual(ran, [True])


if __name__ == "__main__":
    unittest.main()
