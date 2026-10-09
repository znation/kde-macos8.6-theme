"""Tests for tools/png.py's read_png -- its input guards (the file-size cap
and the regular-file check) and its error paths.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402


class TestReadPng(unittest.TestCase):

    def _assert_png_error_names_path(self, path: Path, *needles: str) -> None:
        """Assert ``read_png(path)`` raises ``PngError`` naming *path*.

        A PngError message must name the file so a two-input invocation can
        tell which of candidate/reference was bad; each extra *needle* pins
        one part of the diagnosis.
        """
        with self.assertRaises(png.PngError) as ctx:
            png.read_png(path)
        message = str(ctx.exception)
        self.assertIn(str(path), message)
        for needle in needles:
            self.assertIn(needle, message)

    def test_read_png_rejects_oversize_file_without_reading_it_all(self):
        # read_png reads the whole file before decode_png sees its header, so
        # an oversize file would be loaded into memory first. The read must
        # stop at the cap. Patch the cap down so the fixture stays small.
        limit = 4096
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oversize.png"
            path.write_bytes(b"\x00" * (limit + 1))
            with mock.patch.object(png, "_MAX_FILE_BYTES", limit):
                tracemalloc.start()
                try:
                    with self.assertRaises(png.PngError) as ctx:
                        png.read_png(path)
                    peak = tracemalloc.get_traced_memory()[1]
                finally:
                    tracemalloc.stop()
        self.assertIn(str(limit), str(ctx.exception))
        self.assertIn(f"{limit + 1} bytes", str(ctx.exception))
        self.assertLess(peak, limit + 1024 * 1024)

    def test_read_png_names_undecodable_file(self):
        # A decode failure must name the file it came from, so a two-input
        # invocation can tell which of the candidate/reference was bad.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_bytes(b"not a png")
            self._assert_png_error_names_path(path)

    def test_read_png_names_an_unmaterialized_lfs_pointer(self):
        # The reference screenshots are stored with Git LFS. On a fresh clone
        # without `git lfs pull`, a reference path is a small text pointer;
        # decoding it would report only "not a PNG file", which reads as a
        # corrupt image rather than a missing fetch. Name the pointer and the
        # command that fetches it. The pointer text is written out literally,
        # not read from the module constant, so the test fails if the constant
        # stops matching a real Git LFS pointer.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pointer.png"
            path.write_bytes(
                b"version https://git-lfs.github.com/spec/v1\n"
                b"oid sha256:" + b"0" * 64 + b"\n"
                b"size 12345\n"
            )
            self._assert_png_error_names_path(
                path, "Git LFS pointer", "git lfs pull"
            )

    def test_read_png_names_a_read_failure(self):
        # A read() that fails after a successful open (a disk error) must be
        # reported as a PngError naming the file, not leak the raw OSError:
        # the fidelity CLI catches only PngError and FidelityError, so a leak
        # would crash it with a traceback instead of its exit-2 read-error
        # path. Patch fdopen to hand back the real handle with a failing read.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unreadable.png"
            path.write_bytes(b"x")
            real_fdopen = png.os.fdopen

            def failing_fdopen(fd, *args, **kwargs):
                handle = real_fdopen(fd, *args, **kwargs)
                handle.read = mock.Mock(
                    side_effect=OSError(5, "Input/output error")
                )
                return handle

            with mock.patch.object(png.os, "fdopen", failing_fdopen):
                self._assert_png_error_names_path(
                    path, "cannot read", "Input/output error"
                )

    def test_read_png_closes_the_fd_when_fstat_fails(self):
        # os.fstat runs on the open fd before os.fdopen takes ownership; if it
        # raises, the fd is still open and the finally block must close it, or
        # every failed read leaks a descriptor. The except converts the raw
        # OSError into a PngError naming the file, so the fidelity CLI stays
        # on its exit-2 path instead of tracing back.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "unstattable.png"
            path.write_bytes(b"x")
            real_close = png.os.close
            closed_fds = []

            def recording_close(fd):
                closed_fds.append(fd)
                return real_close(fd)

            with mock.patch.object(
                png.os, "fstat", side_effect=OSError(5, "Input/output error")
            ):
                with mock.patch.object(png.os, "close", recording_close):
                    self._assert_png_error_names_path(
                        path, "cannot read", "Input/output error"
                    )

        # The finally block closed exactly the fd os.open handed out, so it is
        # no longer a valid descriptor.
        self.assertEqual(len(closed_fds), 1)
        with self.assertRaises(OSError):
            os.fstat(closed_fds[0])

    def test_read_png_rejects_a_fifo_instead_of_blocking(self):
        # open() on a FIFO blocks until a writer appears, and read() on a pipe
        # whose writer never sends or closes blocks forever; the byte cap
        # bounds neither wait. read_png must reject a non-regular file. Run it
        # in a child, since a direct call would hang this test, and require it
        # to exit before the timeout.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "pipe.png"
            os.mkfifo(fifo)
            child = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, sys.argv[1]); import png; "
                    "png.read_png(sys.argv[2])",
                    str(REPO_ROOT / "tools"),
                    str(fifo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertNotEqual(child.returncode, 0)
        self.assertIn("not a regular file", child.stderr)
