"""Tests for tools/png/loader.py's read_png input guards and error paths.

The bounded declared-size read is pinned in ``tests/test_png_read_size.py``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from typing import get_type_hints
from unittest import mock

from support.allocation_fixtures import peak_allocation
from support.close_tracking import failing_fdopen, tracking_closes
from support.error_assertions import error_message
from support.fifo_fixtures import make_fifo
from support.process_assertions import assert_failed
from support.tmp_dir import make_tmp_dir

from support import repo_root
from support import snippet_child
from support.png_fixtures import (  # noqa: E402
    input_file,
    rgb_image,
)
from tools import png  # noqa: E402
from tools.png import loader  # noqa: E402
from tools.png import read as png_read  # noqa: E402


class TestDecoderInputAnnotations(unittest.TestCase):
    def test_public_decoders_annotate_their_accepted_bytearray_input(self):
        for decoder in (png_read.decode_png, png_read.decode_rgba):
            with self.subTest(decoder=decoder.__name__):
                self.assertEqual(
                    bytes | bytearray, get_type_hints(decoder)["data"]
                )


class TestReadPng(unittest.TestCase):

    def _file(self, name: str, data: bytes) -> Path:
        return input_file(self, name, data)

    def _assert_png_error_names_path(self, path: Path, *needles: str) -> None:
        """Assert ``read_png(path)`` raises ``PngError`` naming *path*.

        A PngError message must name the file so a two-input invocation can
        tell which of candidate/reference was bad; each extra *needle* pins
        one part of the diagnosis.
        """
        message = error_message(self, png.PngError, png.read_png, path)
        self.assertIn(str(path), message)
        for needle in needles:
            self.assertIn(needle, message)

    def test_read_png_rejects_oversize_file_without_reading_it_all(self):
        # read_png reads the whole file before decode_png sees its header, so
        # an oversize file would be loaded into memory first. The read must
        # stop at the cap. Patch the cap down so the fixture stays small.
        limit = 4096
        path = self._file("oversize.png", b"\x00" * (limit + 1))
        with mock.patch.object(loader, "_MAX_FILE_BYTES", limit):
            message, peak = peak_allocation(
                lambda: error_message(self, png.PngError, png.read_png, path)
            )
        self.assertIn(str(limit), message)
        self.assertIn(f"{limit + 1} bytes", message)
        self.assertLess(peak, limit + 1024 * 1024)

    def test_read_png_accepts_a_file_exactly_at_the_cap(self):
        # The cap is inclusive: a file of exactly _MAX_FILE_BYTES bytes is a
        # valid input, and only one byte more is refused. A strict >= check
        # would refuse this file.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("at_cap.png", data)
        with mock.patch.object(loader, "_MAX_FILE_BYTES", len(data)):
            image = png.read_png(path)
        self.assertEqual((image.width, image.height), (3, 4))

    def test_read_png_names_undecodable_file(self):
        # A decode failure must name the file it came from, so a two-input
        # invocation can tell which of the candidate/reference was bad.
        self._assert_png_error_names_path(
            self._file("broken.png", b"not a png")
        )

    def test_read_png_names_an_unmaterialized_lfs_pointer(self):
        # The reference screenshots are stored with Git LFS. On a fresh clone
        # without `git lfs pull`, a reference path is a small text pointer;
        # decoding it would report only "not a PNG file", which reads as a
        # corrupt image rather than a missing fetch. Name the pointer and the
        # command that fetches it. The pointer text is written out literally,
        # not read from the module constant, so the test fails if the constant
        # stops matching a real Git LFS pointer.
        path = self._file(
            "pointer.png",
            b"version https://git-lfs.github.com/spec/v1\n"
            b"oid sha256:" + b"0" * 64 + b"\n"
            b"size 12345\n",
        )
        self._assert_png_error_names_path(
            path, "Git LFS pointer", "git lfs pull"
        )

    def test_read_png_forwards_max_rows(self):
        # The early-stop bound is why read_png takes a second argument; pin
        # that it reaches decode_png instead of being dropped.
        image, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        top = png.read_png(self._file("image.png", data), max_rows=2)
        self.assertEqual(top, png.Image(3, 2, image.rgb[: 3 * 2 * 3]))

    def test_read_png_forwards_max_cols(self):
        # The column bound must reach the decoder as the row bound does, or a
        # reference reader would decode the full width it asked to skip.
        image, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        prefix = png.read_png(self._file("image.png", data), max_cols=2)
        expected = b"".join(
            image.rgb[row * 9 : row * 9 + 6] for row in range(4)
        )
        self.assertEqual(prefix, png.Image(2, 4, expected))

    def test_read_png_names_a_read_failure(self):
        # A read() that fails after a successful open (a disk error) must be
        # reported as a PngError naming the file, not leak the raw OSError:
        # the fidelity CLI catches only PngError and FidelityError, so a leak
        # would crash it with a traceback instead of its exit-2 read-error
        # path. Patch fdopen to hand back the real handle with a failing read.
        path = self._file("unreadable.png", b"x")
        real_fdopen = loader.os.fdopen

        def failing_fdopen(fd, *args, **kwargs):
            handle = real_fdopen(fd, *args, **kwargs)
            handle.read = mock.Mock(
                side_effect=OSError(5, "Input/output error")
            )
            return handle

        with mock.patch.object(loader.os, "fdopen", failing_fdopen):
            self._assert_png_error_names_path(
                path, "cannot read", "Input/output error"
            )

    def test_read_png_closes_the_fd_when_fstat_fails(self):
        # os.fstat runs on the open fd before os.fdopen takes ownership; if it
        # raises, the fd is still open and the finally block must close it, or
        # every failed read leaks a descriptor. The except converts the raw
        # OSError into a PngError naming the file, so the fidelity CLI stays
        # on its exit-2 path instead of tracing back.
        path = self._file("unstattable.png", b"x")

        with mock.patch.object(
            loader.os, "fstat", side_effect=OSError(5, "Input/output error")
        ):
            with tracking_closes() as closed_fds:
                self._assert_png_error_names_path(
                    path, "cannot read", "Input/output error"
                )

        # The finally block closed exactly the fd os.open handed out, so it is
        # no longer a valid descriptor.
        self.assertEqual(len(closed_fds), 1)
        with self.assertRaises(OSError):
            os.fstat(closed_fds[0])

    def test_read_png_closes_the_fd_when_fdopen_fails(self):
        # os.fdopen takes ownership of the descriptor only when it returns;
        # if it raises, the raw fd from os.open is still open. The finally
        # block must close it, or every read that cannot be wrapped leaks a
        # descriptor. Patching fdopen to raise is the only way to reach that
        # arm -- a valid fd and mode otherwise always succeed.
        path = self._file("unwrappable.png", b"x")

        with failing_fdopen() as closed_fds:
            self._assert_png_error_names_path(
                path, "cannot read", "simulated fdopen failure"
            )

        # Exactly the fd os.open handed out was closed, so no descriptor
        # leaked and no unrelated descriptor was disturbed.
        self.assertEqual(len(closed_fds), 1)
        with self.assertRaises(OSError):
            os.fstat(closed_fds[0])

    def test_read_png_rejects_a_fifo_instead_of_blocking(self):
        # open() on a FIFO blocks until a writer appears, and read() on a pipe
        # whose writer never sends or closes blocks forever; the byte cap
        # bounds neither wait. read_png must reject a non-regular file. Run it
        # in a child, since a direct call would hang this test, and require it
        # to exit before the timeout.
        fifo = make_tmp_dir(self) / "pipe.png"
        make_fifo(self, fifo)
        child = snippet_child.run(
            [
                "import sys; sys.path.insert(0, sys.argv[1]); import png; "
                "png.read_png(sys.argv[2])",
                str(repo_root.ROOT / "tools"),
                str(fifo),
            ],
            timeout=10,
        )
        assert_failed(self, child)
        self.assertIn("not a regular file", child.stderr)


if __name__ == "__main__":
    unittest.main()
