"""Unit tests for the Xcursor binary container layout."""

from __future__ import annotations

import struct
import unittest

from support import repo_root  # noqa: F401
from tools.xcursor_container import (
    CHUNK_VERSION,
    FILE_HEADER_SIZE,
    FILE_VERSION,
    IMAGE_HEADER_SIZE,
    IMAGE_TYPE,
    MAGIC,
    MAX_IMAGE_SIZE,
    TOC_ENTRY_SIZE,
    assemble,
)


class TestAssemble(unittest.TestCase):
    def test_table_offsets_and_chunks_follow_frame_payload_lengths(self):
        frames = [
            (16, 1, 1, 0, 0, b"abc"),
            (32, 2, 1, 1, 0, b"123456"),
        ]
        data = assemble(frames)

        self.assertEqual(
            struct.unpack_from("<4sIII", data),
            (MAGIC, FILE_HEADER_SIZE, FILE_VERSION, 2),
        )
        first_offset = FILE_HEADER_SIZE + 2 * TOC_ENTRY_SIZE
        second_offset = first_offset + IMAGE_HEADER_SIZE + len(frames[0][-1])
        self.assertEqual(struct.unpack_from("<III", data, FILE_HEADER_SIZE),
                         (IMAGE_TYPE, 16, first_offset))
        self.assertEqual(struct.unpack_from("<III", data, FILE_HEADER_SIZE + TOC_ENTRY_SIZE),
                         (IMAGE_TYPE, 32, second_offset))
        self.assertEqual(
            struct.unpack_from("<9I", data, first_offset),
            (IMAGE_HEADER_SIZE, IMAGE_TYPE, 16, CHUNK_VERSION, 1, 1, 0, 0, 0),
        )
        self.assertEqual(data[first_offset + IMAGE_HEADER_SIZE:second_offset], b"abc")
        self.assertEqual(
            struct.unpack_from("<9I", data, second_offset),
            (IMAGE_HEADER_SIZE, IMAGE_TYPE, 32, CHUNK_VERSION, 2, 1, 1, 0, 0),
        )
        self.assertEqual(data[second_offset + IMAGE_HEADER_SIZE:], b"123456")
        self.assertEqual(
            len(data), second_offset + IMAGE_HEADER_SIZE + len(frames[1][-1])
        )

    def test_format_constants_match_the_xcursor_file_format(self):
        # The values come from the Xcursor file format as libXcursor reads
        # it (Xcursor.h / xcursorint.h), not from this module: the other
        # tests build their expected bytes from these constants, so a wrong
        # constant would otherwise agree with itself and pass.
        self.assertEqual(MAGIC, b"Xcur")
        self.assertEqual(FILE_HEADER_SIZE, 4 * 4)
        self.assertEqual(FILE_VERSION, 0x10000)
        self.assertEqual(TOC_ENTRY_SIZE, 3 * 4)
        self.assertEqual(IMAGE_TYPE, 0xFFFD0002)
        self.assertEqual(IMAGE_HEADER_SIZE, 9 * 4)
        self.assertEqual(CHUNK_VERSION, 1)
        self.assertEqual(MAX_IMAGE_SIZE, 0x7FFF)

    def test_empty_frames_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one frame"):
            assemble([])


if __name__ == "__main__":
    unittest.main()
