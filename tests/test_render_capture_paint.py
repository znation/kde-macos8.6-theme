"""Capture-paint diagnosis checks for the render capture diagnosis module."""

from __future__ import annotations

import contextlib
import io
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


class TestClientExitMarker(unittest.TestCase):

    def test_a_log_ending_in_the_exit_marker_reports_the_client_exited(self):
        root = tmp_dir.make_tmp_dir(self)
        log = root / "session.log"
        log.write_text(
            "render-session: capturing at 1\n"
            f"{capture_diagnosis.CLIENT_EXITED_DURING_CAPTURE} at 2\n",
            encoding="utf-8",
        )
        self.assertTrue(capture_diagnosis.client_exited_during_capture(log))

    def test_a_log_without_the_exit_marker_keeps_the_generic_diagnosis(self):
        root = tmp_dir.make_tmp_dir(self)
        log = root / "session.log"
        log.write_text("render-session: capture status 0 at 2\n", encoding="utf-8")
        self.assertFalse(capture_diagnosis.client_exited_during_capture(log))

    def test_the_marker_at_the_end_of_a_log_longer_than_the_tail_is_found(self):
        # The read is a bounded tail: a chatty client's output ahead of the
        # marker must not push the marker out of the window, and the window
        # must start at the end of the file rather than at its beginning.
        root = tmp_dir.make_tmp_dir(self)
        log = root / "session.log"
        log.write_text(
            "client output line\n" * (1 << 13)
            + f"{capture_diagnosis.CLIENT_EXITED_DURING_CAPTURE} at 9\n",
            encoding="utf-8",
        )
        self.assertGreater(log.stat().st_size, 1 << 17)
        self.assertTrue(capture_diagnosis.client_exited_during_capture(log))

    def test_a_missing_log_keeps_the_generic_diagnosis(self):
        root = tmp_dir.make_tmp_dir(self)
        self.assertFalse(
            capture_diagnosis.client_exited_during_capture(root / "absent.log")
        )


class TestRenderLogReport(unittest.TestCase):

    def test_log_size_reports_the_byte_count_of_an_existing_log(self):
        root = tmp_dir.make_tmp_dir(self)
        log = root / "session.log"
        log.write_bytes(b"twelve bytes")
        self.assertEqual("12 bytes", capture_diagnosis.log_size(log))

    def test_log_size_reports_missing_for_an_absent_log(self):
        root = tmp_dir.make_tmp_dir(self)
        self.assertEqual(
            "missing", capture_diagnosis.log_size(root / "absent.log")
        )

    def test_report_prints_the_log_size_and_each_tail_line(self):
        root = tmp_dir.make_tmp_dir(self)
        log = root / "session.log"
        log.write_text("first\nsecond\n", encoding="utf-8")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            capture_diagnosis.report_render_log(log, "render_surface")
        self.assertEqual(
            [
                "render_surface: note: render log (13 bytes), last lines:",
                "render_surface: note:   first",
                "render_surface: note:   second",
            ],
            out.getvalue().splitlines(),
        )

    def test_report_names_an_unreadable_log_instead_of_failing(self):
        root = tmp_dir.make_tmp_dir(self)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            capture_diagnosis.report_render_log(
                root / "absent.log", "render_surface"
            )
        lines = out.getvalue().splitlines()
        self.assertEqual(1, len(lines))
        self.assertTrue(
            lines[0].startswith("render_surface: note: render log unreadable: "),
            lines[0],
        )


if __name__ == "__main__":
    unittest.main()
