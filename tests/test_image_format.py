"""Tests for tools/image_format.py -- the shared raster-format signatures.

``tools/png.py`` and ``tools/check_references.py`` both recognize PNG, JPEG,
GIF and WebP from the same leading bytes, but each tool's own tests exercise
only the formats its current fixtures happen to use. These tests pin the
shared signatures and detection directly, so a change to a magic or to the
WebP container test is caught here instead of in one tool and not the other.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import image_format  # noqa: E402


# A representative leading byte string per format, with trailing bytes so a
# detector that reads past the signature is exercised too.
PNG = image_format.PNG_MAGIC + b"\x00" * 8
JPEG = image_format.JPEG_MAGIC + b"\xe1" + b"\x00" * 8
GIF87A = b"GIF87a" + b"\x00" * 6
GIF89A = b"GIF89a" + b"\x00" * 6
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 "


class TestSignatures(unittest.TestCase):
    def test_every_signature_has_its_documented_bytes(self):
        # The literals are the wire format; pin them so a typo in a magic is
        # caught here rather than silently failing to recognize a real file.
        self.assertEqual(image_format.PNG_MAGIC, b"\x89PNG\r\n\x1a\n")
        self.assertEqual(image_format.JPEG_MAGIC, b"\xff\xd8\xff")
        self.assertEqual(image_format.GIF_MAGICS, (b"GIF87a", b"GIF89a"))
        self.assertEqual(
            image_format.IMAGE_MAGICS,
            (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a"),
        )
        self.assertEqual(
            image_format.LFS_POINTER_MAGIC,
            b"version https://git-lfs.github.com/spec/v1",
        )


class TestIsImage(unittest.TestCase):
    def test_accepts_each_raster_format(self):
        for name, data in (
            ("PNG", PNG),
            ("JPEG", JPEG),
            ("GIF87a", GIF87A),
            ("GIF89a", GIF89A),
            ("WebP", WEBP),
        ):
            with self.subTest(format=name):
                self.assertTrue(image_format.is_image(data))

    def test_rejects_a_riff_container_that_is_not_webp(self):
        # A RIFF/WAVE payload shares the RIFF prefix but is not an image; the
        # WEBP fourcc at bytes 8-11 is what makes a WebP.
        self.assertFalse(image_format.is_image(b"RIFF\x24\x00\x00\x00WAVEfmt "))

    def test_rejects_non_image_bytes_and_short_input(self):
        for name, data in (
            ("html", b"<!DOCTYPE html>\n<html>404 Not Found</html>\n"),
            ("empty", b""),
            ("one byte", b"\x89"),
            ("short riff", b"RIFF"),
        ):
            with self.subTest(input=name):
                self.assertFalse(image_format.is_image(data))


class TestIsWebp(unittest.TestCase):
    def test_requires_both_the_riff_prefix_and_the_webp_fourcc(self):
        self.assertTrue(image_format.is_webp(WEBP))
        self.assertFalse(image_format.is_webp(b"RIFF\x24\x00\x00\x00WAVEfmt "))
        self.assertFalse(image_format.is_webp(b"\x89PNG\r\n\x1a\n"))


class TestOtherImageFormat(unittest.TestCase):
    def test_names_each_non_png_format(self):
        for name, data in (
            ("JPEG", JPEG),
            ("GIF", GIF87A),
            ("GIF", GIF89A),
            ("WebP", WEBP),
        ):
            with self.subTest(format=name):
                self.assertEqual(image_format.other_image_format(data), name)

    def test_returns_none_for_png_and_for_unknown_bytes(self):
        # PNG is the expected input, so it is not an "other" format; the
        # caller must get None rather than a misleading format name.
        self.assertIsNone(image_format.other_image_format(PNG))
        self.assertIsNone(image_format.other_image_format(b"not an image"))
        self.assertIsNone(image_format.other_image_format(b""))


if __name__ == "__main__":
    unittest.main()
