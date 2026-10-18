"""Tests for support/reference_image.py's decoded-reference cache."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from support import reference_image  # noqa: E402
from tools.png.write import encode_png  # noqa: E402


def _write_reference(directory):
    """Write a tiny valid PNG into *directory* and return its path."""
    path = os.path.join(directory, "reference.png")
    with open(path, "wb") as handle:
        handle.write(encode_png(2, 2, bytes(12)))
    return path


def _spy_on_read_png():
    """Patch ``read_png`` to count decodes while still calling through."""
    return mock.patch.object(
        reference_image.png,
        "read_png",
        wraps=reference_image.png.read_png,
    )


class TestReadReferenceCache(unittest.TestCase):
    def test_a_second_read_reuses_the_first_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                first, first_error = reference_image.read_reference(path)
                second, second_error = reference_image.read_reference(path)
        self.assertEqual(1, spy.call_count)
        self.assertIs(first, second)
        self.assertIsNone(first_error)
        self.assertIsNone(second_error)

    def test_a_different_max_rows_is_decoded_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                one, one_error = reference_image.read_reference(
                    path, max_rows=1
                )
                two, two_error = reference_image.read_reference(
                    path, max_rows=2
                )
        self.assertEqual(2, spy.call_count)
        self.assertEqual((one.height, two.height), (1, 2))
        self.assertIsNot(one, two)
        self.assertIsNone(one_error)
        self.assertIsNone(two_error)

    def test_a_failed_read_is_cached_like_a_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "absent.png")
            with _spy_on_read_png() as spy:
                first, first_error = reference_image.read_reference(path)
                second, second_error = reference_image.read_reference(path)
        self.assertEqual(1, spy.call_count)
        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertIs(first_error, second_error)
        self.assertIsInstance(first_error, reference_image.png.PngError)


if __name__ == "__main__":
    unittest.main()
