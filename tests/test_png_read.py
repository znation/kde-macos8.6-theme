"""Tests for tools/png/loader.py's read_png and read_png_size -- their input
guards (the file-size cap and the regular-file check) and their error paths.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
import zlib
from pathlib import Path
from unittest import mock

from support.allocation_fixtures import peak_allocation
from support.error_assertions import error_message
from support.process_assertions import assert_failed
from support.tmp_dir import make_tmp_dir

from support import repo_root
from support.png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    ihdr_chunk,
    rgb_image,
    with_ihdr_byte,
)
from tools import png  # noqa: E402
from tools.png import loader, read  # noqa: E402


class TestReadPng(unittest.TestCase):

    def _file(self, name: str, data: bytes) -> Path:
        """Write *data* to *name* in a fresh temp dir and return its path."""
        path = make_tmp_dir(self) / name
        path.write_bytes(data)
        return path

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

    def test_read_png_size_reports_declared_dimensions_without_decoding(self):
        # The sampler needs the full image size to report and validate a
        # coordinate, but must not pay to unfilter rows it will not read.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("image.png", data)
        with mock.patch.object(loader, "decode_png") as decode:
            self.assertEqual(png.read_png_size(path), (3, 4))
        decode.assert_not_called()

    def test_read_png_size_names_undecodable_file(self):
        path = self._file("broken.png", b"not a png")
        message = error_message(self, png.PngError, png.read_png_size, path)
        self.assertIn(str(path), message)

    def _assert_size_matches_decode(self, data: bytes, needle: str) -> None:
        """Assert read_png_size rejects *data* exactly as read_png does."""
        path = self._file("malformed.png", data)
        decode_message = error_message(self, png.PngError, png.read_png, path)
        self.assertEqual(
            error_message(self, png.PngError, png.read_png_size, path),
            decode_message,
        )
        self.assertIn(needle, decode_message)

    def test_read_png_size_rejects_a_corrupt_ihdr_crc(self):
        # A header byte changed without fixing the CRC makes the declared
        # dimensions untrustworthy; the size read must use the framing check.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        broken = bytearray(data)
        broken[23] ^= 0xFF  # last height byte, inside the IHDR payload
        self._assert_size_matches_decode(bytes(broken), "bad CRC")

    def test_read_png_size_rejects_unsupported_ihdr_fields(self):
        # A valid-CRC header can still declare a format the decoder refuses;
        # the size read must not report dimensions for it.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        self._assert_size_matches_decode(
            with_ihdr_byte(data, 8, 16), "bit depth 16"
        )

    def test_read_png_size_rejects_an_image_over_the_pixel_limit(self):
        # read_png_size must apply decode_png's decompression-bomb guard: a
        # header declaring more than the cap must not hand dimensions to a
        # caller that would then try to decode them.
        width, height = 8001, 8000  # 64,008,000 pixels, above the cap
        path = self._file(
            "huge.png", _PNG_SIGNATURE + ihdr_chunk(width, height, 2)
        )
        with mock.patch.object(loader, "decode_png") as decode:
            message = error_message(
                self, png.PngError, png.read_png_size, path
            )
        decode.assert_not_called()
        self.assertIn(str(path), message)
        self.assertIn(str(read._MAX_PIXELS), message)

    def test_read_png_size_rejects_a_png_whose_ihdr_is_not_first(self):
        # The size read trusts the first chunk only when it is IHDR. With an
        # IDAT first it must fall back to the decoder's framing check rather
        # than scanning ahead and accepting a header the decoder refuses.
        misordered = (
            _PNG_SIGNATURE
            + _chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03"))
            + ihdr_chunk(1, 1, 2)
            + _chunk(b"IEND", b"")
        )
        self._assert_size_matches_decode(misordered, "first chunk")

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
        real_close = loader.os.close
        closed_fds = []

        def recording_close(fd):
            closed_fds.append(fd)
            return real_close(fd)

        with mock.patch.object(
            loader.os, "fstat", side_effect=OSError(5, "Input/output error")
        ):
            with mock.patch.object(loader.os, "close", recording_close):
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
        fifo = make_tmp_dir(self) / "pipe.png"
        os.mkfifo(fifo)
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, sys.argv[1]); import png; "
                "png.read_png(sys.argv[2])",
                str(repo_root.ROOT / "tools"),
                str(fifo),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert_failed(self, child)
        self.assertIn("not a regular file", child.stderr)


if __name__ == "__main__":
    unittest.main()
