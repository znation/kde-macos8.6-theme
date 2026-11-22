"""Tests for the scratch-root removal in ``tools/render/session.py``.

A removal that fails must not hide the leftover directory, and must not
replace the render's own outcome: the note names the path and the error on
stderr, and the render's exception or result is what the caller sees.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.render import session as render_session  # noqa: E402

NOTE = "render_surface: note: could not remove scratch session directory"


class TestScratchRootRemoval(unittest.TestCase):
    def test_a_failed_removal_on_exit_is_named_and_the_render_error_survives(self):
        session = render_session.Session.create()
        root = session.root
        err = io.StringIO()
        try:
            with mock.patch.object(
                render_session.shutil, "rmtree", side_effect=OSError("Device busy")
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
                render_session.shutil, "rmtree", side_effect=OSError("Device busy")
            ), contextlib.redirect_stderr(err):
                with self.assertRaises(RuntimeError) as raised:
                    render_session.Session.create()
        finally:
            for path in made:
                shutil.rmtree(path, ignore_errors=True)
        self.assertEqual("setup broke", str(raised.exception))
        self.assertIn(NOTE, err.getvalue())
        self.assertIn(made[0], err.getvalue())

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
