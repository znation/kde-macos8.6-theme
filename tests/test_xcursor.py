"""Tests for ``tools/xcursor.py`` and the independent test-side Xcursor reader."""

from __future__ import annotations

import struct
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader
from support.error_assertions import assert_error_names  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import xcursor  # noqa: E402
from tools.png.write import encode_rgba_png  # noqa: E402

SIZES = (1, 2, 3, 4)
FILE_HEADER_SIZE = 16
TOC_ENTRY_SIZE = 12
IMAGE_TYPE = 0xFFFD0002
IMAGE_HEADER_SIZE = 36


def opaque_frame(width, height):
    """Return a *width* x *height* RGBA frame whose opaque pixels vary by position."""
    return bytes(
        value
        for y in range(height)
        for x in range(width)
        for value in (
            (x * 37 + y * 11) % 256,
            (x * 17 + y * 53) % 256,
            (x * 7 + y * 91) % 256,
            255,
        )
    )


def frame_record(size):
    """Return one opaque frame record whose hotspot is the bottom-right tip."""
    png = encode_rgba_png(size, size, opaque_frame(size, size))
    return (size, size, size, size - 1, size - 1, png)


class TestWriteReadRoundTrip(unittest.TestCase):
    def setUp(self):
        self.tmp = make_tmp_dir(self)

    def write(self, records, name="cursor.xcursor"):
        path = self.tmp / name
        path.write_bytes(xcursor.write_cursor(records))
        return path

    def test_opaque_frames_round_trip_every_field_and_exact_png_bytes(self):
        for size in SIZES:
            with self.subTest(size=size):
                record = frame_record(size)
                parsed = xcursor_reader.read_cursor(
                    self.write([record], f"{size}.xcursor")
                )
                expected = xcursor_reader.CursorImage(
                    size, size, size, size - 1, size - 1, record[5]
                )
                self.assertEqual(parsed, xcursor_reader.CursorFile((expected,)))
                self.assertEqual(parsed.images[0].png, record[5])

    def test_same_records_produce_byte_identical_files(self):
        records = [frame_record(size) for size in SIZES]
        self.assertEqual(xcursor.write_cursor(records), xcursor.write_cursor(records))

    def test_multiple_frames_keep_order_and_declared_offsets(self):
        records = [frame_record(size) for size in SIZES]
        data = xcursor.write_cursor(records)
        offset = FILE_HEADER_SIZE + TOC_ENTRY_SIZE * len(records)
        for index, size in enumerate(SIZES):
            with self.subTest(index=index):
                chunk_type, nominal_size, chunk_offset = struct.unpack_from(
                    "<III", data, FILE_HEADER_SIZE + TOC_ENTRY_SIZE * index
                )
                self.assertEqual(
                    (chunk_type, nominal_size, chunk_offset),
                    (IMAGE_TYPE, size, offset),
                )
                offset += IMAGE_HEADER_SIZE + size * size * 4
        parsed = xcursor_reader.read_cursor(
            self.write(records, "multiple.xcursor")
        )
        self.assertEqual(
            [image.nominal_size for image in parsed.images], list(SIZES)
        )


class TestContainerLayout(unittest.TestCase):
    def setUp(self):
        self.tmp = make_tmp_dir(self)

    def test_file_and_image_headers_pin_the_xcursor_layout(self):
        # The first pixel is translucent: its stored word is the premultiplied
        # one, so this pins the colour math and not a PNG round trip.
        rgba = bytes(
            (
                10, 20, 30, 128,
                1, 2, 3, 255,
                4, 5, 6, 0,
                7, 8, 9, 64,
            )
        )
        png = encode_rgba_png(2, 2, rgba)
        data = xcursor.write_cursor([(24, 2, 2, 1, 1, png)])

        magic, header_size, version, ntoc = struct.unpack_from("<4sIII", data, 0)
        self.assertEqual((magic, header_size, version, ntoc), (b"Xcur", 16, 0x00010000, 1))

        chunk_type, nominal_size, chunk_offset = struct.unpack_from("<III", data, 16)
        self.assertEqual((chunk_type, nominal_size, chunk_offset), (IMAGE_TYPE, 24, 28))

        header = struct.unpack_from("<IIIIIIIII", data, chunk_offset)
        self.assertEqual(header, (36, IMAGE_TYPE, 24, 1, 2, 2, 1, 1, 0))

        word = struct.unpack_from("<I", data, chunk_offset + IMAGE_HEADER_SIZE)[0]
        self.assertEqual(word, (128 << 24) | (5 << 16) | (10 << 8) | 15)


class TestWriterRejections(unittest.TestCase):
    def setUp(self):
        self.png = encode_rgba_png(2, 2, opaque_frame(2, 2))

    def record(self, **changes):
        fields = {
            "nominal_size": 2,
            "width": 2,
            "height": 2,
            "hotspot_x": 1,
            "hotspot_y": 1,
            "png": self.png,
        }
        fields.update(changes)
        return (
            fields["nominal_size"],
            fields["width"],
            fields["height"],
            fields["hotspot_x"],
            fields["hotspot_y"],
            fields["png"],
        )

    def test_rejects_a_hotspot_outside_its_image(self):
        for hotspot_x, hotspot_y, needle in (
            (2, 1, "hotspot_x"),
            (1, 2, "hotspot_y"),
            (-1, 1, "hotspot_x"),
        ):
            with self.subTest(hotspot=(hotspot_x, hotspot_y)):
                assert_error_names(
                    self,
                    ValueError,
                    xcursor.write_cursor,
                    [self.record(hotspot_x=hotspot_x, hotspot_y=hotspot_y)],
                    needles=(needle,),
                )

    def test_rejects_a_zero_dimension(self):
        for name in ("nominal_size", "width", "height"):
            with self.subTest(field=name):
                assert_error_names(
                    self,
                    ValueError,
                    xcursor.write_cursor,
                    [self.record(**{name: 0})],
                    needles=(name,),
                )

    def test_rejects_a_bool_dimension(self):
        assert_error_names(
            self,
            ValueError,
            xcursor.write_cursor,
            [self.record(width=True)],
            needles=("width", "bool"),
        )

    def test_rejects_a_dimension_above_the_maximum(self):
        for name in ("nominal_size", "width", "height"):
            for value in (xcursor.MAX_IMAGE_SIZE + 1, -1):
                with self.subTest(field=name, value=value):
                    assert_error_names(
                        self,
                        ValueError,
                        xcursor.write_cursor,
                        [self.record(**{name: value})],
                        needles=(name, str(value)),
                    )

    def test_rejects_a_non_integer_hotspot(self):
        for name in ("hotspot_x", "hotspot_y"):
            for value in (1.0, True):
                with self.subTest(field=name, value=value):
                    assert_error_names(
                        self,
                        ValueError,
                        xcursor.write_cursor,
                        [self.record(**{name: value})],
                        needles=(name, type(value).__name__),
                    )

    def test_rejects_a_png_sized_differently_from_its_record(self):
        assert_error_names(
            self,
            ValueError,
            xcursor.write_cursor,
            [self.record(width=1, height=1, hotspot_x=0, hotspot_y=0)],
            needles=("png", "2x2", "1x1"),
        )

    def test_rejects_a_non_bytes_png(self):
        assert_error_names(
            self,
            ValueError,
            xcursor.write_cursor,
            [self.record(png="not bytes")],
            needles=("png", "str"),
        )

    def test_rejects_a_record_with_the_wrong_number_of_fields(self):
        # The part-3 frame table is written by hand, so a miscounted tuple is a
        # likely mistake. The writer's contract is a ValueError naming the
        # record, not a bare unpacking error that hides which frame is wrong.
        for record in ((2, 2, 2, 1, self.png), self.record() + (None,), 42):
            with self.subTest(record=record):
                assert_error_names(
                    self,
                    ValueError,
                    xcursor.write_cursor,
                    [record],
                    needles=("images[0]", "6-item"),
                )

    def test_rejects_a_png_that_does_not_decode(self):
        # A frame PNG is read from the frame table; a corrupt or non-PNG frame
        # must be reported against its index and cause instead of escaping as a
        # PngError the writer never promises or a bare traceback.
        assert_error_names(
            self,
            ValueError,
            xcursor.write_cursor,
            [self.record(png=b"not a png")],
            needles=("images[0]", "could not be decoded", "not a PNG file"),
        )

    def test_accepts_a_bytearray_png(self):
        # The documented input accepts bytes or bytearray, so a mutable frame
        # buffer must produce the same cursor bytes as its immutable copy.
        record = self.record()
        mutable = record[:5] + (bytearray(record[5]),)
        self.assertEqual(
            xcursor.write_cursor([record]), xcursor.write_cursor([mutable])
        )


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


if __name__ == "__main__":
    unittest.main()
