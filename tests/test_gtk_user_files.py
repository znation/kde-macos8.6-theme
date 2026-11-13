"""Direct tests for tools/gtk_user_files.py.

``tests/test_apply_gtk.py`` drives these helpers through the whole tool; these
pin the read and user-CSS decisions on their own: which occupants read as
"nothing there", that line endings survive the read untouched, and what the
write and remove decisions return for each kind of ``gtk.css``.
"""

from __future__ import annotations

import errno
import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.close_tracking import tracking_closes
from support.theme_install import write_file
from tools import gtk_user_files


class TestReadConfigText(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_a_missing_file_reads_as_none(self):
        self.assertIsNone(gtk_user_files.read_config_text(self.directory / "no"))

    def test_a_path_below_a_regular_file_reads_as_none(self):
        parent = self.directory / "file"
        parent.write_text("x", encoding="utf-8")
        self.assertIsNone(gtk_user_files.read_config_text(parent / "settings.ini"))

    def test_a_directory_reads_as_none(self):
        self.assertIsNone(gtk_user_files.read_config_text(self.directory))

    def test_every_line_ending_and_the_bom_survive_the_read(self):
        path = self.directory / "settings.ini"
        raw = "﻿a\r\nb\rc\nd"
        path.write_bytes(raw.encode("utf-8"))
        self.assertEqual(raw, gtk_user_files.read_config_text(path))

    def test_an_empty_file_reads_as_empty_text_not_none(self):
        path = self.directory / "empty"
        path.write_bytes(b"")
        self.assertEqual("", gtk_user_files.read_config_text(path))

    def test_invalid_utf8_is_refused_naming_the_file(self):
        path = self.directory / "bad.ini"
        path.write_bytes(b"\xff\xfe")
        with self.assertRaises(gtk_user_files.ConfigError) as caught:
            gtk_user_files.read_config_text(path)
        self.assertIn(str(path), str(caught.exception))

    def _assert_failed_syscall_refuses_and_closes(
        self, function: str, failure: str
    ) -> None:
        """Pin the read_config_text refusal when ``gtk_user_files.os``
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
                gtk_user_files.os,
                function,
                side_effect=OSError(errno.EIO, failure),
            ):
                with self.assertRaises(gtk_user_files.ConfigError) as caught:
                    gtk_user_files.read_config_text(path)
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

        with mock.patch.object(gtk_user_files.os, "close", side_effect=close_then_fail):
            with self.assertRaises(gtk_user_files.ConfigError) as caught:
                gtk_user_files.read_config_text(path)
        self.assertIn(f"cannot close {path}", str(caught.exception))
        self.assertIn("simulated close failure", str(caught.exception))

    def test_an_open_refused_for_another_reason_is_a_config_error(self):
        path = self.directory / "settings.ini"
        path.write_text("[Settings]\n", encoding="utf-8")
        with mock.patch.object(
            gtk_user_files.os,
            "open",
            side_effect=PermissionError(errno.EACCES, "simulated refusal"),
        ):
            with self.assertRaises(gtk_user_files.ConfigError) as caught:
                gtk_user_files.read_config_text(path)
        self.assertIn(f"cannot read {path}", str(caught.exception))
        self.assertIn("simulated refusal", str(caught.exception))

    def test_a_platform_that_refuses_to_open_a_directory_reads_as_none(self):
        # Linux opens a directory read-only, so the fstat check catches it;
        # the open-time EISDIR arm is the fallback for platforms that refuse.
        path = self.directory / "gtk-4.0"
        path.mkdir()
        with tracking_closes() as closed:
            with mock.patch.object(
                gtk_user_files.os,
                "open",
                side_effect=OSError(errno.EISDIR, "simulated EISDIR"),
            ):
                self.assertIsNone(gtk_user_files.read_config_text(path))
        self.assertEqual([], closed)


class TestUserCssDecisions(unittest.TestCase):
    def setUp(self):
        self.config = tmp_dir.make_tmp_dir(self)
        self.sheet = self.config / "share" / "gtk.css"

    def css(self, text: str | None) -> Path:
        path = gtk_user_files.user_css_path(self.config)
        if text is not None:
            write_file(path, text)
        return path

    def write(self):
        return gtk_user_files.user_css_write(self.config, self.sheet)

    def test_paths_sit_below_the_versioned_config_directories(self):
        self.assertEqual(
            self.config / "gtk-3.0" / "settings.ini",
            gtk_user_files.settings_path(self.config, "gtk-3.0"),
        )
        self.assertEqual(
            self.config / "gtk-4.0" / "gtk.css",
            gtk_user_files.user_css_path(self.config),
        )

    def test_a_missing_file_gets_the_marker_and_an_import_of_the_sheet(self):
        path = self.css(None)
        self.assertEqual(
            (
                path,
                f'{gtk_user_files.GTK4_CSS_MARKER}\n'
                f'@import url("{self.sheet.as_uri()}");\n',
                None,
            ),
            self.write(),
        )

    def test_our_marker_led_file_is_rewritten_even_with_other_content(self):
        path = self.css(f"{gtk_user_files.GTK4_CSS_MARKER}\r\nold\n")
        result = self.write()
        self.assertEqual(path, result[0])
        self.assertNotIn("old", result[1])
        self.assertIsNone(result[2])

    def test_a_first_line_that_only_starts_with_the_marker_is_foreign(self):
        # Lines end at LF, CR and CRLF only (tools/text_lines.py): a Unicode
        # line separator (U+2028) inside the first line is part of it, so a
        # file whose first line merely starts with our marker text is not
        # the marker-led file -- it is backed up, not rewritten in place.
        path = self.css(f"{gtk_user_files.GTK4_CSS_MARKER}\u2028/* edits */\n")
        result = self.write()
        self.assertEqual(path, result[2])

    def test_a_foreign_file_is_rewritten_and_named_as_the_backup_source(self):
        path = self.css(f"a {{}}\n{gtk_user_files.GTK4_CSS_MARKER}\n")
        result = self.write()
        self.assertEqual(
            (
                path,
                f'{gtk_user_files.GTK4_CSS_MARKER}\n'
                f'@import url("{self.sheet.as_uri()}");\n',
                path,
            ),
            result,
        )

    def test_remove_returns_the_path_only_for_our_file(self):
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))
        path = self.css("a {}\n")
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))
        self.css(f"{gtk_user_files.GTK4_CSS_MARKER}\n")
        self.assertEqual(path, gtk_user_files.user_css_remove(self.config))

    def test_remove_keeps_an_empty_file(self):
        self.css("")
        self.assertIsNone(gtk_user_files.user_css_remove(self.config))


class TestUserCssBackup(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)
        self.path = gtk_user_files.user_css_path(self.directory)

    def css(self, text: str) -> Path:
        write_file(self.path, text)
        return self.path

    def test_the_plain_bak_name_copies_every_byte(self):
        text = "\ufeff/* foreign */\r\n@import url(\"x.css\");\n"
        path = self.css(text)
        backup = gtk_user_files.user_css_backup(path)
        self.assertEqual(path.with_name("gtk.css.bak"), backup)
        self.assertEqual(text.encode("utf-8"), backup.read_bytes())
        self.assertEqual(text.encode("utf-8"), path.read_bytes())

    def test_an_existing_backup_is_never_overwritten(self):
        path = self.css("first\n")
        existing = path.with_name("gtk.css.bak")
        existing.write_bytes(b"older backup\n")
        path.write_bytes(b"second\n")
        backup = gtk_user_files.user_css_backup(path)
        self.assertEqual(path.with_name("gtk.css.bak.1"), backup)
        self.assertEqual(b"older backup\n", existing.read_bytes())
        self.assertEqual(b"second\n", backup.read_bytes())

    def test_a_missing_file_is_refused_by_name(self):
        with self.assertRaises(gtk_user_files.ConfigError) as caught:
            gtk_user_files.user_css_backup(self.path)
        self.assertIn(str(self.path), str(caught.exception))

    def test_a_failed_copy_leaves_no_partial_backup(self):
        path = self.css("x\n")
        with mock.patch.object(
            os, "fdopen", side_effect=OSError("injected close failure")
        ):
            with self.assertRaises(gtk_user_files.ConfigError):
                gtk_user_files.user_css_backup(path)
        self.assertFalse(path.with_name("gtk.css.bak").exists())
        self.assertEqual(b"x\n", path.read_bytes())

    def test_a_failed_write_leaves_no_partial_backup(self):
        # The open and the exclusive create succeeded, so a write failure
        # must close the descriptor, discard the partial sibling and refuse
        # naming the stylesheet and the backup; the source stays untouched.
        # The handle emulates a real written wrapper, whose context manager
        # closes the descriptor on exit, so the tracking pins that close.
        path = self.css("original\n")
        backup = path.with_name("gtk.css.bak")

        class FailingHandle:
            def __init__(self, descriptor):
                self.descriptor = descriptor

            def __enter__(self):
                return self

            def __exit__(self, *args):
                os.close(self.descriptor)
                return False

            def write(self, data):
                raise OSError(errno.ENOSPC, "simulated write failure")

        def failing_handle(descriptor, *args, **keywords):
            return FailingHandle(descriptor)

        with tracking_closes() as closed:
            with mock.patch.object(os, "fdopen", side_effect=failing_handle):
                with self.assertRaises(gtk_user_files.ConfigError) as caught:
                    gtk_user_files.user_css_backup(path)
        self.assertIn(f"cannot back up {path} to {backup}", str(caught.exception))
        self.assertIn("simulated write failure", str(caught.exception))
        self.assertEqual(2, len(closed))
        with self.assertRaises(OSError):
            os.fstat(closed[1])
        self.assertFalse(backup.exists())
        self.assertEqual(b"original\n", path.read_bytes())

    def test_an_open_refusal_names_the_backup(self):
        # The exclusive create is the only open that must refuse for a reason
        # other than "name taken"; the stylesheet's own read still succeeds,
        # so the refusal names the backup the copy never created.
        path = self.css("x\n")
        backup = path.with_name("gtk.css.bak")
        real_open = os.open

        def refuse_backup_open(file, *args, **keywords):
            if "bak" in os.fspath(file):
                raise PermissionError(errno.EACCES, "simulated open refusal")
            return real_open(file, *args, **keywords)

        with mock.patch.object(
            gtk_user_files.os, "open", side_effect=refuse_backup_open
        ):
            with self.assertRaises(gtk_user_files.ConfigError) as caught:
                gtk_user_files.user_css_backup(path)
        self.assertIn(f"cannot back up {path} to {backup}", str(caught.exception))
        self.assertIn("simulated open refusal", str(caught.exception))
        self.assertFalse(backup.exists())
        self.assertEqual(b"x\n", path.read_bytes())

    def test_exhausted_backup_names_are_refused_by_name(self):
        # Every sibling ``.bak.N`` name through the last attempted suffix
        # taken must exhaust the search, not wrap onto an earlier name or
        # print a suffix the loop never visited. The count comes from the
        # module constant, so a changed attempt budget stays in step with
        # these names.
        path = self.css("x\n")
        attempts = gtk_user_files._BACKUP_NAME_ATTEMPTS
        for index in range(attempts):
            suffix = "" if index == 0 else f".{index}"
            (path.with_name(f"{path.name}{gtk_user_files.USER_CSS_BACKUP_SUFFIX}{suffix}")
             .write_bytes(b"taken\n"))
        with self.assertRaises(gtk_user_files.ConfigError) as caught:
            gtk_user_files.user_css_backup(path)
        self.assertIn(
            f"cannot find an unused backup name for {path}", str(caught.exception)
        )
        self.assertEqual(b"x\n", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
