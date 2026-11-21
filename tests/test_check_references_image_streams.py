"""Tests for declared image payloads in the reference checker.

These tests pin accepted raster signatures and each format's stream ending
with the checker's filesystem loader as the unit under test. The sources.txt
record rules and undeclared-scan and name-safety checks stay in
``test_check_references_validation.py``.
"""

import contextlib
import io
import unittest
from unittest import mock

from support.check_references_fixtures import (
    CheckerTestCase,
    assert_problem,
    check_references_in,
    reference_set,
)
from tools.image_format import (
    GIF_MAGICS,
    JPEG_MAGIC,
    PNG_MAGIC,
    TERMINAL_GIF,
    TERMINAL_JPEG,
    TERMINAL_PNG,
    is_complete,
)
from tools import reference_validation

COMPLETE_PNG = PNG_MAGIC + TERMINAL_PNG


class TestAcceptedImageFormats(CheckerTestCase):
    """The checker must accept every raster format the reference set uses.

    The built-in self-test does not exercise the GIF signatures, so a
    regression in GIF handling would flag the reference set's 1 GIF file as a
    non-image without any test noticing. The WebP signature is pinned here
    too, including the reference set's WebP payload named
    ``sherlock_fandom.jpg``.
    """

    def _problems_for(self, module, filename, content):
        return check_references_in(
            module,
            f"{filename} | https://example.test/x | label\n",
            {filename: content},
        )

    def test_jpeg_signature_is_accepted(self):
        module = self.checker
        # A JPEG begins ff d8 ff; the bytes after it are not part of the
        # signature check, though the stream must still end with the EOI
        # marker for the ending rules to accept it.
        problems = self._problems_for(
            module,
            "photo.jpg",
            b"\xff\xd8\xff\xe1" + b"\x00" * 6 + TERMINAL_JPEG,
        )
        self.assertEqual(problems, [])

    def test_gif87a_signature_is_accepted(self):
        module = self.checker
        problems = self._problems_for(
            module, "anim.gif", b"GIF87a" + b"\x00" * 5 + TERMINAL_GIF
        )
        self.assertEqual(problems, [])

    def test_gif89a_signature_is_accepted(self):
        module = self.checker
        problems = self._problems_for(
            module, "anim.gif", b"GIF89a" + b"\x00" * 5 + TERMINAL_GIF
        )
        self.assertEqual(problems, [])

    def test_webp_signature_is_accepted(self):
        module = self.checker
        # The reference set's sherlock_fandom.jpg is a WebP payload, so the
        # RIFF/WEBP signature must be accepted even under a .jpg name; only
        # the bytes decide, never the extension.
        problems = self._problems_for(
            module, "sherlock_fandom.jpg", b"RIFF" + (8).to_bytes(4, "little") + b"WEBPVP8 "
        )
        self.assertEqual(problems, [])

    def test_riff_container_that_is_not_webp_is_rejected(self):
        module = self.checker
        # A RIFF/WAVE payload shares the RIFF prefix but is not an image; the
        # WEBP marker at bytes 8-11 is what makes it a WebP.
        problems = self._problems_for(
            module, "sound.png", b"RIFF\x24\x00\x00\x00WAVEfmt "
        )
        assert_problem(
            self, problems, "sound.png", "not a PNG, JPEG, GIF or WebP"
        )

    def test_declared_image_prefix_is_read_with_one_open(self):
        module = self.checker
        original_open = reference_validation.open_regular_binary
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
            {"good.png": COMPLETE_PNG},
        ) as root:
            with mock.patch.object(
                reference_validation, "open_regular_binary", wraps=original_open
            ) as opened:
                self.assertEqual(module.check_references(root), [])
        self.assertEqual(opened.call_count, 1)


class TestImageStreamCompleteness(unittest.TestCase):
    """:func:`tools.image_format.is_complete` judges each format's ending.

    Running direction by direction: every complete form passes, every cut
    form fails, and a payload that is not an image fails before any ending
    is consulted, so an HTML error page can never be reported as truncated.
    """

    def test_complete_png_passes(self):
        head = PNG_MAGIC + b"\x00" * 4
        tail = b"\x00" * 4 + TERMINAL_PNG
        self.assertTrue(is_complete(head, tail, len(head) + len(tail)))

    def test_png_cut_inside_the_body_fails(self):
        self.assertFalse(is_complete(PNG_MAGIC, b"\x00" * 12, 20))

    def test_png_ending_with_a_broken_iend_crc_fails(self):
        broken = TERMINAL_PNG[:-1] + b"\x00"
        self.assertFalse(is_complete(PNG_MAGIC, broken, 12))

    def test_short_png_tail_cannot_fake_a_complete_version(self):
        # A file shorter than the IEND chunk has no room for it, and the
        # caller may pass a tail without padding; the comparison must not
        # accept a prefix of the terminator.
        self.assertFalse(is_complete(PNG_MAGIC, TERMINAL_PNG[:-1], 12))

    def test_size_must_include_signature_and_complete_terminator(self):
        # A valid ending cannot fit in a file shorter than its format's
        # signature plus that ending, even when the supplied tail looks valid.
        for name, head, ending, size in (
            ("PNG", PNG_MAGIC, TERMINAL_PNG, 19),
            ("JPEG", JPEG_MAGIC, TERMINAL_JPEG, 4),
            ("GIF", b"GIF89a", TERMINAL_GIF, 6),
        ):
            with self.subTest(format=name):
                self.assertFalse(is_complete(head, ending, size))

    def test_complete_jpeg_passes(self):
        self.assertTrue(is_complete(JPEG_MAGIC, TERMINAL_JPEG, 5))

    def test_jpeg_with_a_longer_complete_tail_passes(self):
        tail = b"\x00" * 10 + TERMINAL_JPEG
        self.assertTrue(is_complete(JPEG_MAGIC, tail, 15))

    def test_jpeg_cut_before_the_eoi_marker_fails(self):
        self.assertFalse(is_complete(JPEG_MAGIC, b"\xff\xd8", 10))

    def test_gif87a_complete_passes_and_cut_fails(self):
        self.assertTrue(is_complete(b"GIF87a", TERMINAL_GIF, 7))
        self.assertFalse(is_complete(b"GIF87a", b",", 7))

    def test_gif89a_complete_passes_and_cut_fails(self):
        self.assertTrue(is_complete(b"GIF89a", TERMINAL_GIF, 7))
        self.assertFalse(is_complete(b"GIF89a", b"", 6))

    def test_webp_holding_its_declared_riff_size_passes(self):
        head = b"RIFF" + (4).to_bytes(4, "little") + b"WEBP"
        self.assertTrue(is_complete(head, b"", 12))

    def test_webp_short_of_its_declared_riff_size_fails(self):
        head = b"RIFF" + (64).to_bytes(4, "little") + b"WEBP"
        self.assertFalse(is_complete(head, b"", 12))

    def test_riff_wave_fails_before_any_terminator_check(self):
        # A RIFF/WAVE payload shares the container prefix but is not an image;
        # it must fail the format test itself, never be called an incomplete
        # image stream.
        self.assertFalse(
            is_complete(b"RIFF\x24\x00\x00\x00WAVEfmt ", b"", 16)
        )


class TestTruncatedDeclaredImage(CheckerTestCase):
    """A declared file missing its format's terminator is a checker problem.

    A reference download cut short can end in valid image bytes: the leading
    signature survives, so only the ending rules catch it, and the diagnostic
    names the file, its format's missing terminator and the download caveat
    without ever reaching an image decoder. The recognized-payload diagnostic
    always outranks it: HTML under an image name is not a truncation.
    """

    def _problems_for(self, filename, head):
        module = self.checker
        problems = check_references_in(
            module,
            f"{filename} | https://example.test/x | label\n",
            {filename: head},
        )
        assert_problem(self, problems, filename, "it may be a truncated download")
        return problems

    def test_truncated_png_names_the_iend_trailer(self):
        problems = self._problems_for("cut.png", PNG_MAGIC)
        joined = "\n".join(problems)
        self.assertIn("ends without the PNG IEND trailer", joined)
        self.assertNotIn("not a PNG, JPEG, GIF or WebP image", joined)

    def test_truncated_jpeg_names_the_eoi_marker(self):
        problems = self._problems_for("cut.jpg", JPEG_MAGIC)
        joined = "\n".join(problems)
        self.assertIn("ends without the JPEG EOI marker", joined)

    def test_truncated_gif_names_the_trailer_byte(self):
        problems = self._problems_for(
            "cut.gif", GIF_MAGICS[1]  # GIF89a
        )
        joined = "\n".join(problems)
        self.assertIn("ends without the GIF trailer byte", joined)

    def test_truncated_webp_names_its_declared_and_held_sizes(self):
        problems = self._problems_for(
            "cut.webp", b"RIFF" + (64).to_bytes(4, "little") + b"WEBP"
        )
        joined = "\n".join(problems)
        self.assertIn("declares 64 RIFF bytes but holds 12", joined)

    def test_webp_named_jpg_reports_declared_sizes_not_the_extension(self):
        # The format comes from the head, never the .jpg extension.
        problems = self._problems_for(
            "cut.jpg", b"RIFF" + (64).to_bytes(4, "little") + b"WEBP"
        )
        joined = "\n".join(problems)
        self.assertIn("declares 64 RIFF bytes but holds 12", joined)

    def test_html_error_page_is_not_reported_as_truncated(self):
        module = self.checker
        problems = check_references_in(
            module,
            "fake.png | https://example.test/x | label\n",
            {"fake.png": b"<!DOCTYPE html>\n<html>404 Not Found</html>\n"},
        )
        assert_problem(self, problems, "not a PNG, JPEG, GIF or WebP image")
        # No line names a missing terminator: the non-image diagnostic's own
        # "truncated download" caveat is not the truncation diagnostic.
        self.assertFalse(
            any("ends without the" in line or "declares " in line
                for line in problems),
            problems,
        )

    def test_truncated_set_exits_one_through_the_cli(self):
        module = self.checker
        with reference_set(
            module,
            "cut.png | https://example.test/x | label\n",
            {"cut.png": PNG_MAGIC},
        ) as root:
            out, err = io.StringIO(), io.StringIO()
            with unittest.mock.patch.object(
                module, "REFERENCE_DIR", str(root)
            ), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = module.main([])
        self.assertEqual(code, 1)
        self.assertIn("ends without the PNG IEND trailer", err.getvalue())


if __name__ == "__main__":
    unittest.main()
