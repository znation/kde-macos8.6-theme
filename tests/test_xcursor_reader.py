"""Tests for the test-side Xcursor reader in ``tests/support/xcursor.py``.

The reader is independent of ``tools/xcursor.py``. These tests feed it bytes the
production writer builds, plus hand-edited fields, and pin its rejections,
unknown-chunk skipping, parse cache and containment.
"""

from __future__ import annotations

import struct
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader
from support.error_assertions import assert_error_names  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from support.xcursor_lib.frames import (  # noqa: E402
    FILE_HEADER_SIZE,
    TOC_ENTRY_SIZE,
    frame_record,
)
from tools import xcursor  # noqa: E402


class TestParserRejections(unittest.TestCase):
    def setUp(self):
        self.tmp = make_tmp_dir(self)
        self.valid = xcursor.write_cursor([frame_record(2)])

    def path_for(self, data, name="cursor.xcursor"):
        path = self.tmp / name
        path.write_bytes(data)
        return path

    def assert_reader_names(self, data, needles):
        path = self.path_for(data)
        assert_error_names(
            self,
            ValueError,
            xcursor_reader.read_cursor,
            path,
            needles=(str(path),) + needles,
        )

    def chunk_offset(self):
        """Return the first image chunk's offset in the valid cursor bytes.

        Each TOC entry is 12 bytes: chunk type, nominal size, then the chunk
        offset at +8. The parser tests mutate fields inside that chunk, so
        they share this lookup instead of re-deriving the TOC layout.
        """
        return struct.unpack_from("<I", self.valid, FILE_HEADER_SIZE + 8)[0]

    def mutated(self, offset, value):
        """Return the valid cursor with the little-endian word at *offset* replaced."""
        data = bytearray(self.valid)
        struct.pack_into("<I", data, offset, value)
        return bytes(data)

    def test_rejects_a_truncated_file_header(self):
        self.assert_reader_names(b"Xcur", ("header", "0"))

    def test_rejects_a_bad_magic(self):
        self.assert_reader_names(b"Bad!" + self.valid[4:], ("magic", "0"))

    def test_rejects_a_wrong_file_header_size(self):
        self.assert_reader_names(self.mutated(4, 20), ("header size", "4"))

    def test_rejects_a_wrong_file_version(self):
        self.assert_reader_names(
            self.mutated(8, 0x00020000), ("version", "8")
        )

    def test_rejects_a_toc_that_overruns_the_file(self):
        self.assert_reader_names(self.mutated(12, 1000), ("TOC", "16"))

    def test_rejects_a_chunk_offset_outside_the_file(self):
        self.assert_reader_names(
            self.mutated(FILE_HEADER_SIZE + 8, len(self.valid) + 4),
            ("offset",),
        )

    def test_rejects_a_truncated_image_payload(self):
        self.assert_reader_names(self.valid[:-1], ("payload", "offset"))

    def test_rejects_a_hotspot_outside_its_image(self):
        self.assert_reader_names(
            self.mutated(self.chunk_offset() + 24, 2), ("hotspot_x",)
        )

    def test_rejects_a_hotspot_y_outside_its_image(self):
        self.assert_reader_names(
            self.mutated(self.chunk_offset() + 28, 2), ("hotspot_y",)
        )

    def test_rejects_a_zero_toc_nominal_size(self):
        self.assert_reader_names(
            self.mutated(FILE_HEADER_SIZE + 4, 0),
            ("TOC nominal size", "positive"),
        )

    def test_rejects_a_zero_image_nominal_size(self):
        self.assert_reader_names(
            self.mutated(self.chunk_offset() + 8, 0),
            ("image nominal size", "positive"),
        )

    def test_rejects_a_toc_nominal_size_above_the_maximum(self):
        self.assert_reader_names(
            self.mutated(
                FILE_HEADER_SIZE + 4, xcursor_reader.MAX_IMAGE_SIZE + 1
            ),
            ("TOC nominal size", "exceeds"),
        )

    def test_rejects_an_image_nominal_size_above_the_maximum(self):
        self.assert_reader_names(
            self.mutated(
                self.chunk_offset() + 8, xcursor_reader.MAX_IMAGE_SIZE + 1
            ),
            ("image nominal size", "exceeds"),
        )

    def test_rejects_an_image_size_above_the_maximum(self):
        chunk_offset = self.chunk_offset()
        for field, offset, dimensions in (
            ("width", 16, f"{xcursor_reader.MAX_IMAGE_SIZE + 1}x2"),
            ("height", 20, f"2x{xcursor_reader.MAX_IMAGE_SIZE + 1}"),
        ):
            with self.subTest(field=field):
                data = self.mutated(
                    chunk_offset + offset, xcursor_reader.MAX_IMAGE_SIZE + 1
                )
                self.assert_reader_names(data, (dimensions, "exceed"))

    def test_rejects_a_nominal_size_that_disagrees_with_the_toc(self):
        self.assert_reader_names(
            self.mutated(self.chunk_offset() + 8, 3),
            ("image nominal size", "does not match"),
        )

    def test_rejects_bad_image_header_fields(self):
        chunk_offset = self.chunk_offset()
        for field, offset, value, needle in (
            ("header size", 0, 40, "image header size"),
            ("type", 4, 0, "image chunk type"),
            ("version", 12, 2, "image chunk version"),
        ):
            with self.subTest(field=field):
                data = self.mutated(chunk_offset + offset, value)
                self.assert_reader_names(data, (needle,))

    def test_rejects_a_zero_image_dimension(self):
        chunk_offset = self.chunk_offset()
        for field, offset, dimensions in (
            ("width", 16, "0x2"),
            ("height", 20, "2x0"),
        ):
            with self.subTest(field=field):
                data = self.mutated(chunk_offset + offset, 0)
                self.assert_reader_names(data, (dimensions, "positive"))


class TestUnknownChunk(unittest.TestCase):
    def setUp(self):
        self.tmp = make_tmp_dir(self)

    def test_parser_skips_an_unknown_toc_entry_and_returns_the_image(self):
        record = frame_record(2)
        data = xcursor.write_cursor([record])
        ntoc = struct.unpack_from("<I", data, 12)[0]
        old_type, old_subtype, old_offset = struct.unpack_from(
            "<III", data, FILE_HEADER_SIZE
        )
        unknown = struct.pack("<III", 0xFFFE0003, 0, len(data) + 100)
        old = struct.pack("<III", old_type, old_subtype, old_offset + TOC_ENTRY_SIZE)
        hand_appended = (
            data[:12]
            + struct.pack("<I", ntoc + 1)
            + unknown
            + old
            + data[FILE_HEADER_SIZE + TOC_ENTRY_SIZE * ntoc :]
        )
        path = self.tmp / "unknown.xcursor"
        path.write_bytes(hand_appended)

        parsed = xcursor_reader.read_cursor(path)
        self.assertEqual(
            parsed,
            xcursor_reader.CursorFile(
                (
                    xcursor_reader.CursorImage(
                        2, 2, 2, 1, 1, record[5]
                    ),
                )
            ),
        )
        self.assertEqual(parsed.images[0].png, record[5])


class TestReadCache(unittest.TestCase):
    """Pin the reader's parse cache and its invalidation."""

    def setUp(self):
        self.tmp = make_tmp_dir(self)

    def write(self, records, name="cursor.xcursor"):
        path = self.tmp / name
        path.write_bytes(xcursor.write_cursor(records))
        return path

    def test_an_unchanged_file_reuses_one_parsed_result(self):
        path = self.write([frame_record(2)])
        first = xcursor_reader.read_cursor(path)
        self.assertIs(xcursor_reader.read_cursor(path), first)

    def test_a_rewritten_file_is_parsed_again(self):
        path = self.write([frame_record(2)])
        first = xcursor_reader.read_cursor(path)
        path.write_bytes(xcursor.write_cursor([frame_record(3), frame_record(4)]))
        second = xcursor_reader.read_cursor(path)
        self.assertIsNot(second, first)
        self.assertEqual([image.nominal_size for image in second.images], [3, 4])

    def test_a_failed_read_is_not_cached(self):
        path = self.tmp / "missing.xcursor"
        with self.assertRaises(FileNotFoundError):
            xcursor_reader.read_cursor(path)
        path.write_bytes(xcursor.write_cursor([frame_record(2)]))
        parsed = xcursor_reader.read_cursor(path)
        self.assertEqual([image.nominal_size for image in parsed.images], [2])


class TestContainment(unittest.TestCase):
    """A scratch root is a containment boundary, as the repository root is."""

    def test_a_symlink_that_escapes_the_root_is_refused(self):
        tmp = make_tmp_dir(self)
        root = tmp / "root"
        root.mkdir()
        outside = tmp / "outside"
        outside.mkdir()
        private = outside / "private.xcursor"
        private.write_bytes(xcursor.write_cursor([frame_record(2)]))
        link = root / "cursor.xcursor"
        link.symlink_to(private)

        with self.assertRaises(ValueError) as caught:
            xcursor_reader.read_cursor(link, root=root)

        self.assertIn("symlink escape", str(caught.exception))
        self.assertIn(str(link), str(caught.exception))


if __name__ == "__main__":
    unittest.main()
