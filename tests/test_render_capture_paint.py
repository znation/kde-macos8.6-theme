"""Capture-paint diagnosis checks for the render capture diagnosis module."""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools.render import capture_diagnosis  # noqa: E402


class TestCapturePaintCheck(unittest.TestCase):

    def test_empty_rgb_plane_is_unpainted(self):
        self.assertTrue(capture_diagnosis.capture_is_unpainted(b""))

    def test_any_nonblack_rgb_byte_marks_capture_as_painted(self):
        self.assertFalse(capture_diagnosis.capture_is_unpainted(b"\x00\x00\x01"))

    def test_a_non_regular_log_keeps_the_generic_diagnosis(self):
        # The bounded tail read goes through the open guard, which raises
        # ValueError -- not OSError -- for a non-regular log, so a session
        # log swapped for a FIFO must leave the black-capture diagnosis
        # with its generic verdict instead of tracebacking out of the run.
        root = tmp_dir.make_tmp_dir(self)
        fifo = root / "session.log"
        os.mkfifo(fifo)
        self.assertFalse(capture_diagnosis.client_exited_during_capture(fifo))


if __name__ == "__main__":
    unittest.main()
