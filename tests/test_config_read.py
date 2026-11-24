"""The bounded reader's refusal contract for small user settings files.

``tools/config_read.py`` reads a small UTF-8 settings file once, through an
inspected non-blocking descriptor, and raises ``ConfigError`` naming the
path when a syscall fails: these tests pin the ``None`` answers, the line
ending and BOM survival, the oversize refusal, and the descriptor-closing
refusals.
"""

from __future__ import annotations

import errno
import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.close_tracking import tracking_closes
from tools import config_read


class TestReadConfigText(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_a_missing_file_reads_as_none(self):
        self.assertIsNone(config_read.read_config_text(self.directory / "no"))

    def test_a_path_below_a_regular_file_reads_as_none(self):
        parent = self.directory / "file"
        parent.write_text("x", encoding="utf-8")
        self.assertIsNone(config_read.read_config_text(parent / "settings.ini"))

    def test_a_directory_reads_as_none(self):
        self.assertIsNone(config_read.read_config_text(self.directory))

    def test_every_line_ending_and_the_bom_survive_the_read(self):
        path = self.directory / "settings.ini"
        raw = "﻿a\r\nb\rc\nd"
        path.write_bytes(raw.encode("utf-8"))
        self.assertEqual(raw, config_read.read_config_text(path))

    def test_an_empty_file_reads_as_empty_text_not_none(self):
        path = self.directory / "empty"
        path.write_bytes(b"")
        self.assertEqual("", config_read.read_config_text(path))

    def test_invalid_utf8_is_refused_naming_the_file(self):
        path = self.directory / "bad.ini"
        path.write_bytes(b"\xff\xfe")
        with self.assertRaises(config_read.ConfigError) as caught:
            config_read.read_config_text(path)
        self.assertIn(str(path), str(caught.exception))

    def _assert_failed_syscall_refuses_and_closes(
        self, function: str, failure: str
    ) -> None:
        """Pin the read_config_text refusal when ``config_read.os``
        *function* raises ``failure``.

        The descriptor is opened before the mode is inspected, so a failure
        after the open must still reach the finally: a regression there
        leaks one descriptor per unreadable file. Two call sites, one per
        patched syscall (fstat, read); the close tracking asserts exactly
        the one descriptor the open handed out was closed.
        """
        path = self.directory / "settings.ini"
        path.write_text("[Settings]\n", encoding="utf-8")
        with tracking_closes() as closed:
            with mock.patch.object(
                config_read.os,
                function,
                side_effect=OSError(errno.EIO, failure),
            ):
                with self.assertRaises(config_read.ConfigError) as caught:
                    config_read.read_config_text(path)
        self.assertIn(f"cannot read {path}", str(caught.exception))
        self.assertIn(failure, str(caught.exception))
        self.assertEqual(1, len(closed))
        with self.assertRaises(OSError):
            os.fstat(closed[0])

    def test_a_failed_fstat_is_refused_naming_the_file_and_closes_the_descriptor(
        self,
    ):
        self._assert_failed_syscall_refuses_and_closes(
            "fstat", "simulated fstat failure"
        )

    def test_a_failed_read_is_refused_naming_the_file_and_closes_the_descriptor(
        self,
    ):
        self._assert_failed_syscall_refuses_and_closes(
            "read", "simulated read failure"
        )

    def test_a_failed_close_is_reported_as_a_config_error(self):
        path = self.directory / "settings.ini"
        path.write_text("[Settings]\n", encoding="utf-8")
        real_close = os.close

        def close_then_fail(descriptor):
            real_close(descriptor)
            raise OSError(errno.EIO, "simulated close failure")

        with mock.patch.object(config_read.os, "close", side_effect=close_then_fail):
            with self.assertRaises(config_read.ConfigError) as caught:
                config_read.read_config_text(path)
        self.assertIn(f"cannot close {path}", str(caught.exception))
        self.assertIn("simulated close failure", str(caught.exception))

    def test_an_open_refused_for_another_reason_is_a_config_error(self):
        path = self.directory / "settings.ini"
        path.write_text("[Settings]\n", encoding="utf-8")
        with mock.patch.object(
            config_read.os,
            "open",
            side_effect=PermissionError(errno.EACCES, "simulated refusal"),
        ):
            with self.assertRaises(config_read.ConfigError) as caught:
                config_read.read_config_text(path)
        self.assertIn(f"cannot read {path}", str(caught.exception))
        self.assertIn("simulated refusal", str(caught.exception))

    def test_a_platform_that_refuses_to_open_a_directory_reads_as_none(self):
        # Linux opens a directory read-only, so the fstat check catches it;
        # the open-time EISDIR arm is the fallback for platforms that refuse.
        path = self.directory / "gtk-4.0"
        path.mkdir()
        with tracking_closes() as closed:
            with mock.patch.object(
                config_read.os,
                "open",
                side_effect=OSError(errno.EISDIR, "simulated EISDIR"),
            ):
                self.assertIsNone(config_read.read_config_text(path))
        self.assertEqual([], closed)


if __name__ == "__main__":
    unittest.main()
