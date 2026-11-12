"""Tests for the shared private-PNG decode helper in tools/jpeg_convert.py.

Both the sampler and the fidelity CLI decode JPEG inputs through
``decoded_png``; these tests pin its contract directly, with ``convert_jpeg``
stubbed so no ImageMagick run is needed.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from support.repo_root import ROOT  # noqa: F401  (puts root on sys.path)
from tools import jpeg_convert


def _converter_writing(payload: bytes, problem=None):
    """A stand-in for convert_jpeg that writes *payload* to the PNG path."""

    def convert(input_bytes, temp_png):
        Path(temp_png).write_bytes(payload)
        return problem

    return convert


class TestDecodedPng(unittest.TestCase):
    """The yielded PNG lives in a private directory removed on every exit."""

    def test_yields_a_png_inside_a_prefixed_directory_that_is_then_removed(self):
        seen = {}
        converter = _converter_writing(b"png bytes")
        with mock.patch.object(jpeg_convert, "convert_jpeg", side_effect=converter):
            with jpeg_convert.decoded_png(b"jpeg", "unit-test-") as temp_png:
                seen["path"] = temp_png
                seen["exists_inside"] = temp_png.read_bytes()
                seen["name"] = temp_png.name
                seen["parent_name"] = temp_png.parent.name
        self.assertEqual(seen["exists_inside"], b"png bytes")
        self.assertEqual(seen["name"], "decoded.png")
        self.assertTrue(seen["parent_name"].startswith("unit-test-"))
        self.assertFalse(seen["path"].parent.exists())

    def test_converter_receives_the_jpeg_bytes_unchanged(self):
        converter = _converter_writing(b"png")
        with mock.patch.object(
            jpeg_convert, "convert_jpeg", side_effect=converter
        ) as convert_mock:
            with jpeg_convert.decoded_png(b"the jpeg", "unit-test-"):
                pass
        convert_mock.assert_called_once()
        self.assertEqual(convert_mock.call_args.args[0], b"the jpeg")

    def test_decode_failure_raises_with_the_diagnostic_and_removes_directory(self):
        directories = []

        def failing(input_bytes, temp_png):
            directories.append(Path(temp_png).parent)
            return "convert exited 7: bad marker"

        body_ran = False
        with mock.patch.object(jpeg_convert, "convert_jpeg", side_effect=failing):
            with self.assertRaises(jpeg_convert.JpegDecodeError) as caught:
                with jpeg_convert.decoded_png(b"jpeg", "unit-test-"):
                    body_ran = True
        self.assertEqual(str(caught.exception), "convert exited 7: bad marker")
        self.assertFalse(body_ran)
        self.assertEqual(len(directories), 1)
        self.assertFalse(directories[0].exists())

    def test_body_exception_propagates_and_still_removes_directory(self):
        directories = []

        def record(input_bytes, temp_png):
            directories.append(Path(temp_png).parent)
            Path(temp_png).write_bytes(b"png")
            return None

        with mock.patch.object(jpeg_convert, "convert_jpeg", side_effect=record):
            with self.assertRaises(RuntimeError):
                with jpeg_convert.decoded_png(b"jpeg", "unit-test-"):
                    raise RuntimeError("reader failed")
        self.assertEqual(len(directories), 1)
        self.assertFalse(directories[0].exists())


if __name__ == "__main__":
    unittest.main()
