"""Tests for tools/png.py's read_png -- the file-size cap and the
regular-file guard.

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
            with self.assertRaises(png.PngError) as ctx:
                png.read_png(path)
            self.assertIn(str(path), str(ctx.exception))

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
            with self.assertRaises(png.PngError) as ctx:
                png.read_png(path)
            message = str(ctx.exception)
            self.assertIn(str(path), message)
            self.assertIn("Git LFS pointer", message)
            self.assertIn("git lfs pull", message)

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
                with self.assertRaises(png.PngError) as ctx:
                    png.read_png(path)
        message = str(ctx.exception)
        self.assertIn(str(path), message)
        self.assertIn("cannot read", message)
        self.assertIn("Input/output error", message)

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
