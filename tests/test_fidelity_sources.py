"""Input policy for the fidelity PNG reader."""

from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from support import repo_root  # noqa: F401  (puts ROOT on sys.path)
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.png_fixtures import rgb_image
from support.repo_root import ROOT
from support import snippet_child
from tools import fidelity_sources, png


class TestFidelitySources(unittest.TestCase):
    """Test bounded source-image decoding for fidelity comparisons."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "image.png"
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 7))
        self.path.write_bytes(data)

    def test_uncropped_read_decodes_alpha_once(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), None)
        self.assertEqual((image.width, image.height), (3, 4))
        read.assert_called_once_with(str(self.path), alpha=True)

    def test_crop_bounds_decoded_rows(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), (0, 1, 2, 2))
        self.assertEqual(image.height, 3)
        read.assert_called_once_with(str(self.path), max_rows=3, alpha=True)

    def test_sideways_overflow_retries_unbounded(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), (2, 1, 2, 2))
        self.assertEqual(image.height, 4)
        self.assertEqual([call.kwargs for call in read.call_args_list], [
            {"max_rows": 3, "alpha": True}, {"alpha": True}
        ])

    def test_vertical_and_combined_overflow_stay_bounded(self):
        with mock.patch.object(
            fidelity_sources, "read_png", wraps=png.read_png
        ) as read:
            image = fidelity_sources.read_source(str(self.path), (0, 2, 2, 3))
        self.assertEqual(image.height, 4)
        read.assert_called_once_with(str(self.path), max_rows=5, alpha=True)

        # When both dimensions overflow, sideways overflow still triggers the
        # full read so the crop diagnostic retains the real image dimensions.
        with mock.patch.object(
            fidelity_sources, "read_png", wraps=png.read_png
        ) as read:
            image = fidelity_sources.read_source(str(self.path), (2, 2, 2, 3))
        self.assertEqual(image.height, 4)
        self.assertEqual([call.kwargs for call in read.call_args_list], [
            {"max_rows": 5, "alpha": True}, {"alpha": True}
        ])

    def test_repository_escape_is_rejected_before_decode(self):
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        link = repo / "link.png"
        link.symlink_to(self.path)
        with mock.patch.object(fidelity_sources, "ROOT", repo), mock.patch.object(
            fidelity_sources, "read_png"
        ) as read:
            with self.assertRaisesRegex(ValueError, "resolves outside"):
                fidelity_sources.read_source(str(link), None)
        read.assert_not_called()

    def test_inside_repository_symlink_and_external_path_are_readable(self):
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        target = repo / "target.png"
        target.write_bytes(self.path.read_bytes())
        link = repo / "link.png"
        link.symlink_to(target)
        with mock.patch.object(fidelity_sources, "ROOT", repo):
            self.assertEqual(fidelity_sources.read_source(str(link), None).width, 3)
            self.assertEqual(fidelity_sources.read_source(str(self.path), None).width, 3)

    def test_an_unreadable_file_falls_through_to_the_png_branch(self):
        # The sniff promises None, not an exception, when an openable file
        # cannot be read: an I/O error from fstat or from read after the
        # non-blocking open must fall through to the PNG branch — which
        # decodes (or diagnoses) the path the operator gave — instead of
        # escaping read_source as an OSError traceback. The open failure
        # and vanished-file arms are pinned elsewhere; this pins the
        # post-open arm of the same guard.
        def fail_with_eio(*args, **kwargs):
            raise OSError(errno.EIO, "Input/output error")

        expected = SimpleNamespace(width=3, height=4)
        for operation in ("fstat", "read"):
            with self.subTest(operation=operation), \
                    mock.patch(f"os.{operation}", fail_with_eio), \
                    mock.patch.object(
                        fidelity_sources, "read_png", return_value=expected
                    ) as decoder:
                image = fidelity_sources.read_source(str(self.path), None)
            self.assertIs(image, expected)
            decoder.assert_called_once_with(str(self.path), alpha=True)


class TestReadSource(unittest.TestCase):
    """Test safe source reads, crop bounds, and repository path checks."""
    def test_uncropped_and_in_bounds_reads_preserve_alpha_and_bound_rows(self):
        image = SimpleNamespace(width=8, height=9)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            self.assertIs(fidelity_sources.read_source("external.png", None), image)
            decoder.assert_called_once_with("external.png", alpha=True)
            decoder.reset_mock()
            self.assertIs(
                fidelity_sources.read_source("external.png", (1, 2, 3, 4)), image
            )
            decoder.assert_called_once_with(
                "external.png", max_rows=6, alpha=True
            )

    def test_sideways_overflow_retries_full_image(self):
        image = SimpleNamespace(width=3, height=8)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", (2, 0, 2, 2))
        self.assertEqual(
            decoder.call_args_list,
            [mock.call("image.png", max_rows=2, alpha=True),
             mock.call("image.png", alpha=True)],
        )

    def test_vertical_overflow_stays_bounded_and_combined_retries(self):
        image = SimpleNamespace(width=3, height=3)
        rect = (0, 1, 2, 4)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", rect)
            decoder.assert_called_once_with(
                "image.png", max_rows=rect[1] + rect[3], alpha=True
            )

        # Sideways overflow takes precedence when both dimensions overflow.
        rect = (2, 1, 2, 4)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", rect)
        self.assertEqual(
            decoder.call_args_list,
            [mock.call("image.png", max_rows=5, alpha=True),
             mock.call("image.png", alpha=True)],
        )

    def test_repository_symlink_escape_is_rejected_before_decode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            outside = Path(directory) / "outside.png"
            outside.write_bytes(b"png")
            link = root / "linked.png"
            link.symlink_to(outside)
            with mock.patch.object(fidelity_sources, "ROOT", root), mock.patch.object(
                fidelity_sources, "read_png"
            ) as decoder:
                with self.assertRaises(ValueError):
                    fidelity_sources.read_source(str(link), None)
            decoder.assert_not_called()

    def test_a_fifo_candidate_is_refused_instead_of_blocking(self):
        # A FIFO at a candidate path must not stall the run: the sniff's
        # non-blocking open and regular-file check match read_png's own
        # guards, so the pipe falls through to the PNG branch and the
        # standing cannot-read refusal names it. The CLI runs in a child
        # process, so a blocking regression is a bounded timeout, not a
        # stalled suite (the same shape tests/test_containment.py uses).
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as directory:
            fifo = Path(directory) / "candidate.png"
            make_fifo(self, fifo)
            _, reference = rgb_image(1, 1, lambda x, y: (0, 0, 0))
            reference_path = Path(directory) / "reference.png"
            reference_path.write_bytes(reference)
            child = snippet_child.run(
                [
                    "import sys; from tools import fidelity; "
                    "sys.exit(fidelity.main([sys.argv[1], sys.argv[2]]))",
                    str(fifo),
                    str(reference_path),
                ],
                cwd=ROOT,
                timeout=10,
            )
            assert_fifo_refused(self, child, fifo)


class TestVanishedJpegFallThrough(unittest.TestCase):
    """A JPEG side that vanishes between the sniff and the whole read."""

    def test_vanished_jpeg_falls_through_to_the_png_branch(self):
        # The docstring promises the whole read's None falls through to the
        # PNG branch, whose own open produces the standing diagnostic. The
        # vanishing is staged offline: the second os.open of the run — the
        # JPEG branch's whole read, after the sniff's — fails with the
        # ENOENT a deleted file produces, and every later open (read_png's)
        # succeeds. A regression that converts the None bytes anyway fails
        # through the converter guard, and one that swallows the fall-through
        # fails for want of the standing refusal.
        _, png_data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        jpeg = b"\xff\xd8\xff" + png_data
        real_open = os.open
        opened = []

        def flaky_open(path, flags):
            opened.append(path)
            if len(opened) == 2:
                raise OSError(errno.ENOENT, "No such file or directory", str(path))
            return real_open(path, flags)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vanished.jpg"
            path.write_bytes(jpeg)
            with mock.patch("os.open", flaky_open), \
                    mock.patch.object(
                        fidelity_sources, "convert_jpeg",
                        side_effect=AssertionError("converted vanished bytes"),
                    ):
                with self.assertRaisesRegex(png.PngError, "not a PNG file") as caught:
                    fidelity_sources.read_source(str(path), None)
        # The PNG loader's decode guard prefixes the operator's path to the
        # standing refusal (tools/png/loader.py: "cannot decode {path}").
        self.assertEqual(
            str(caught.exception),
            f"cannot decode {path}: not a PNG file: the input is a JPEG "
            "image, not a PNG; convert it to PNG first",
        )
        self.assertEqual(len(opened), 3)


class TestWholeFileRead(unittest.TestCase):
    """The JPEG branch's whole-file read across the sniff's chunk bound."""

    def test_negative_count_reads_a_file_bigger_than_one_chunk_whole(self):
        # _read_bytes promises that a negative count reads the file whole;
        # a file over 64 KiB is larger than any single raw read or buffer
        # fill, so a whole-read truncated to one read cannot survive here.
        payload = bytes(range(256)) * 257  # 65792 bytes: 65536 + 256
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.bin"
            path.write_bytes(payload)
            self.assertEqual(fidelity_sources._read_bytes(str(path), -1), payload)

    def test_negative_count_reads_a_single_chunk_file_whole(self):
        # A file of exactly 64 KiB must still be read whole and terminate
        # at end-of-file without a trailing empty or duplicated read.
        payload = bytes(range(256)) * 256  # exactly 65536 bytes
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bounded.bin"
            path.write_bytes(payload)
            self.assertEqual(fidelity_sources._read_bytes(str(path), -1), payload)

    def test_jpeg_branch_hands_the_whole_file_to_the_converter(self):
        # read_source routes a JPEG-magic file through the convert bridge
        # with the file's full bytes: the sniff reads three, the JPEG branch
        # re-reads whole. A regression that hands the converter only the
        # sniffed head or a truncated first chunk fails here, offline —
        # no ImageMagick run is needed to observe the bytes handed over.
        payload = b"\xff\xd8\xff" + bytes(range(256)) * 257
        _, png_data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        seen = {}

        def fake_convert(jpeg_bytes, temp_png):
            seen["bytes"] = jpeg_bytes
            temp_png.write_bytes(png_data)
            return None

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.jpg"
            path.write_bytes(payload)
            with mock.patch.object(fidelity_sources, "convert_jpeg", fake_convert):
                image = fidelity_sources.read_source(str(path), None)
        self.assertEqual(seen["bytes"], payload)
        self.assertEqual((image.width, image.height), (1, 1))


if __name__ == "__main__":
    unittest.main()
