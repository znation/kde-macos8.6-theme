"""Tests for the scratch-root removal in ``tools/render/session.py``.

A removal that fails must not hide the leftover directory, and must not
replace the render's own outcome: the note names the path and the error on
stderr, and the render's exception or result is what the caller sees.
"""

from __future__ import annotations

import contextlib
import errno
import io
import os
import shutil
import tempfile
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools.render import session as render_session  # noqa: E402

NOTE = "render_surface: note: could not remove scratch session directory"


class TestScratchRootRemoval(unittest.TestCase):
    def test_a_failed_removal_on_exit_is_named_and_the_render_error_survives(self):
        session = render_session.Session.create()
        root = session.root
        err = io.StringIO()
        try:
            with mock.patch.object(
                os, "rmdir", side_effect=OSError(errno.EBUSY, "Device busy")
            ):
                with contextlib.redirect_stderr(err):
                    with self.assertRaises(RuntimeError) as raised:
                        with session:
                            raise RuntimeError("render failed")
        finally:
            shutil.rmtree(root)
        self.assertEqual("render failed", str(raised.exception))
        self.assertIn(NOTE, err.getvalue())
        self.assertIn(str(root), err.getvalue())
        self.assertIn("Device busy", err.getvalue())

    def test_a_failed_removal_after_a_failed_setup_keeps_the_setup_error(self):
        real_mkdtemp = tempfile.mkdtemp
        made = []

        def record_mkdtemp(*args, **kwargs):
            path = real_mkdtemp(*args, **kwargs)
            made.append(path)
            return path

        err = io.StringIO()
        try:
            with mock.patch.object(
                render_session.tempfile, "mkdtemp", side_effect=record_mkdtemp
            ), mock.patch.object(
                render_session, "_session_directories",
                side_effect=RuntimeError("setup broke"),
            ), mock.patch.object(
                os, "rmdir", side_effect=OSError(errno.EBUSY, "Device busy")
            ), contextlib.redirect_stderr(err):
                with self.assertRaises(RuntimeError) as raised:
                    render_session.Session.create()
        finally:
            for path in made:
                shutil.rmtree(path, ignore_errors=True)
        self.assertEqual("setup broke", str(raised.exception))
        self.assertIn(NOTE, err.getvalue())
        self.assertIn(made[0], err.getvalue())

    def test_a_root_blocked_by_a_file_keeps_the_setup_error(self):
        # The runtime path is a file, so the real setup raises FileExistsError
        # after mkdtemp has made the root; its removal then fails too.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()
        (prepared / "rt").write_bytes(b"in the way")
        err = io.StringIO()
        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ), mock.patch.object(
            os, "rmdir", side_effect=OSError(errno.EBUSY, "Device busy")
        ), contextlib.redirect_stderr(err):
            with self.assertRaises(FileExistsError):
                render_session.Session.create()
        # One note, whose leftover path is the root itself.
        self.assertEqual(1, len(err.getvalue().splitlines()))
        self.assertTrue(err.getvalue().startswith(f"{NOTE} {prepared}: "))
        self.assertIn("Device busy", err.getvalue())

    def test_one_undeletable_entry_leaves_the_rest_removed(self):
        session = render_session.Session.create()
        entries = [session.root / f"entry-{index}" for index in range(3)]
        for entry in entries:
            entry.write_text("x")
        real_unlink = os.unlink
        kept = []

        def refuse_the_first(path, *args, **kwargs):
            # Refuse whichever entry comes first, so others remain after it.
            if not kept:
                kept.append(os.path.basename(path))
                raise OSError(errno.EBUSY, "Device busy")
            return real_unlink(path, *args, **kwargs)

        err = io.StringIO()
        try:
            with mock.patch.object(os, "unlink", side_effect=refuse_the_first):
                with contextlib.redirect_stderr(err):
                    session.cleanup()
            remaining = [path.name for path in entries if path.exists()]
        finally:
            shutil.rmtree(session.root)
        self.assertEqual(kept, remaining)
        self.assertIn("Device busy", err.getvalue())

    def test_an_already_absent_root_prints_nothing(self):
        session = render_session.Session.create()
        shutil.rmtree(session.root)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            session.cleanup()
        self.assertEqual("", err.getvalue())

    def test_a_successful_removal_prints_nothing(self):
        session = render_session.Session.create()
        root = session.root
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with session:
                pass
        self.assertFalse(root.exists())
        self.assertEqual("", err.getvalue())


if __name__ == "__main__":
    unittest.main()
