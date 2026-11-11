"""Record-validation tests for tools/check_references.py.

``sources.txt`` entries and the files they name are validated before the
checker reads any image: a filename must be bare, a source URL must be a
well-formed absolute URL, a declared file's bytes must be a known raster
format, and an untrusted name must be escaped before it reaches a terminal.
"""

import contextlib
import io
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from support.check_references_fixtures import (
    CheckerTestCase,
    assert_problem,
    check_references_in,
    reference_set,
)
from support.error_assertions import assert_escapes_escape_character
from tools.image_format import (
    GIF_MAGICS,
    JPEG_MAGIC,
    PNG_MAGIC,
    TERMINAL_GIF,
    TERMINAL_JPEG,
    TERMINAL_PNG,
    is_complete,
)
from tools import reference_sources, reference_validation

# A complete minimal PNG stream: the file every_fixture expects a clean pass
# for must satisfy the ending rules as well as the signature check.
COMPLETE_PNG = PNG_MAGIC + TERMINAL_PNG


class TestSourceParser(unittest.TestCase):
    """The record parser reports syntax and declarations without filesystem access."""

    def test_line_splitting_and_declaration_line_numbers(self):
        problems, entries = reference_sources.parse_sources(
            Path("refs"), Path("refs/sources.txt"),
            "# header\r\ngood.png | https://example.test/a | label\r"
            "bad.png | https://example.test/b | label\n",
        )
        self.assertEqual(problems, [])
        self.assertEqual(entries, {"good.png": 2, "bad.png": 3})

    def test_invalid_url_name_and_duplicate_do_not_become_declarations(self):
        problems, entries = reference_sources.parse_sources(
            Path("refs"), Path("refs/sources.txt"),
            "../unsafe.png | https://example.test/a | label\n"
            "bad.png | https:///b | label\n"
            "good.png | https://example.test/g | label\n"
            "good.png | https://example.test/again | label\n",
        )
        self.assertEqual(entries, {"good.png": 3})
        self.assertEqual([line for line, _ in problems], [1, 2, 4])


def assert_url_problem_not_the_scheme(case, url, *needles):
    """Assert a malformed *url* is reported for *needles*, not for its scheme.

    Every URL passed here has a valid scheme and fails for some other reason
    (a missing host, a raw space), so a diagnostic that blames the scheme
    sends the reader after the wrong fix: the reported problems must name
    *needles* and none may mention an absolute URL.
    """
    module = case.checker
    problems = check_references_in(
        module,
        f"bad.png | {url} | label\n",
        {"bad.png": PNG_MAGIC},
    )
    assert_problem(case, problems, *needles)
    case.assertFalse(
        any("absolute URL" in line for line in problems), problems
    )


class TestLineSplitting(CheckerTestCase):
    """sources.txt is newline-delimited; other Unicode separators are data.

    ``str.splitlines`` also breaks on U+2028/U+2029, NEL and the C0
    separators, so a version label pasted from a web page or PDF could split
    into a phantom line and be reported as a malformed entry. Only CR, LF and
    CRLF end a record.
    """

    def test_unicode_line_separator_stays_inside_the_label(self):
        module = self.checker
        problems = check_references_in(
            module,
            "good.png | https://example.test/g.png | Mac OS 8.6\u2028retail\n",
            {"good.png": COMPLETE_PNG},
        )
        self.assertEqual(problems, [])

    def test_carriage_return_still_ends_a_line(self):
        module = self.checker
        problems = check_references_in(
            module,
            "good.png | https://example.test/g.png | label\r"
            "bad.png | https://example.test/b.png | label\r",
            {"good.png": COMPLETE_PNG, "bad.png": b"not an image"},
        )
        assert_problem(self, problems, "bad.png", "not a PNG")


class TestFilenameMustBeBare(CheckerTestCase):
    """A sources.txt entry must name a bare file in the directory.

    A nested path or ``..`` traversal can reach a file outside the reference
    directory even when that file exists, so the entry is rejected on its
    shape rather than on whether it resolves.
    """

    def test_nested_filename_is_rejected_even_when_the_file_exists(self):
        module = self.checker
        with reference_set(
            module,
            "sub/good.png | https://example.test/g.png | label\n",
            {"sub/good.png": COMPLETE_PNG},
        ) as root:
            problems = module.check_references(root)
        assert_problem(self, problems, "sub/good.png", "bare filename")

    def test_parent_traversal_is_rejected_even_when_the_file_exists(self):
        module = self.checker
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "refs"
            root.mkdir()
            (root / module.SOURCES_NAME).write_text(
                "../escape.png | https://example.test/e.png | label\n",
                encoding="utf-8",
            )
            (root.parent / "escape.png").write_bytes(PNG_MAGIC)
            problems = module.check_references(root)
        assert_problem(self, problems, "../escape.png", "bare filename")

    def test_bare_parent_directory_is_rejected_as_a_bare_name(self):
        # A lone `..` names a directory, not a file, but ``Path("..").name``
        # is "..", so the path-shape clause alone accepts it: only the
        # explicit (".", "..") guard rejects it as non-bare. Without that
        # guard the entry reaches the symlink-escape check, which reports it
        # as pointing outside the directory and blames the wrong thing.
        module = self.checker
        problems = check_references_in(
            module,
            ".. | https://example.test/e.png | label\n",
        )
        assert_problem(self, problems, "'..'", "must be a bare filename")
        self.assertFalse(
            any("symlink escape" in line for line in problems), problems
        )


class TestEmptyUrlRemainder(CheckerTestCase):
    """A scheme with nothing after it is a broken citation the checker reports."""

    def test_empty_remainder_is_reported_by_the_checker(self):
        module = self.checker
        problems = check_references_in(
            module,
            "good.png | https:// | label\n",
            {"good.png": PNG_MAGIC},
        )
        assert_problem(self, problems, "absolute URL")


class TestUrlProblemDiagnostics(CheckerTestCase):
    """A malformed URL is reported for its actual defect, not blamed on the scheme."""

    def test_no_host_problem_names_the_host_not_the_scheme(self):
        assert_url_problem_not_the_scheme(
            self, "https://user@/a.png", "must name a host"
        )

    def test_raw_whitespace_problem_names_the_whitespace_not_the_scheme(self):
        assert_url_problem_not_the_scheme(
            self, "https://example.test/a b.png", "whitespace or control"
        )

    def test_empty_authority_problem_names_the_host_not_the_scheme(self):
        assert_url_problem_not_the_scheme(
            self, "https:///a.png", "must name a host"
        )


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


class TestUndeclaredImageExtension(CheckerTestCase):
    """A stray file named like an image is undeclared even without image bytes.

    The scan flags an unlisted file whose extension marks it as an image, not
    only one whose leading bytes are a raster signature: a half-downloaded or
    renamed error page saved as ``.png`` must surface as an undeclared image
    instead of hiding behind its name. The comparison is case-insensitive and
    covers every suffix the reference set accepts.
    """

    def _problems_for(self, module, filename):
        return check_references_in(
            module, "", {filename: b"<!DOCTYPE html>\n404 Not Found\n"}
        )

    def _assert_undeclared(self, module, filename):
        problems = self._problems_for(module, filename)
        assert_problem(self, problems, filename, "image has no entry")

    def test_stray_png_extension_without_image_bytes_is_undeclared(self):
        module = self.checker
        self._assert_undeclared(module, "half-downloaded.png")

    def test_uppercase_extension_is_matched_case_insensitively(self):
        module = self.checker
        self._assert_undeclared(module, "SHOT.PNG")

    def test_jpeg_extension_is_matched(self):
        module = self.checker
        self._assert_undeclared(module, "photo.jpeg")


class TestControlCharactersInFilenames(CheckerTestCase):
    """An untrusted filename must not reach the terminal as live bytes.

    The reference directory can hold a contributor-supplied name, so an ESC or
    newline in it would otherwise drive the operator's terminal or forge a
    diagnostic line when the checker reports the undeclared image.
    """

    def _undeclared(self, module, filename):
        return check_references_in(module, "", {filename: PNG_MAGIC})

    def test_escape_sequence_in_name_is_escaped(self):
        module = self.checker
        problems = self._undeclared(module, "evil\x1b[31m.png")
        self.assertTrue(problems, "expected an undeclared-image problem")
        joined = "\n".join(problems)
        assert_escapes_escape_character(self, joined)

    def test_newline_in_name_cannot_forge_a_line(self):
        module = self.checker
        problems = self._undeclared(module, "fake\nproblem line.png")
        joined = "\n".join(problems)
        self.assertNotIn("fake\nproblem", joined)
        self.assertIn("\\u000a", joined)


class TestNullByteFilename(CheckerTestCase):
    """A NUL byte in a source entry must be a diagnostic, not a crash.

    A NUL cannot appear in a POSIX path and makes ``os.path.realpath()`` raise
    ValueError, so the symlink containment check must not let a malformed
    sources.txt line abort the whole run with an unhandled exception.
    """

    def test_null_byte_in_filename_is_reported_not_raised(self):
        module = self.checker
        problems = check_references_in(
            module,
            b"bad\x00name.png | https://example.test/b.png | label\n",
        )
        assert_problem(self, problems, "bad\\x00name.png", "NUL")


if __name__ == "__main__":
    unittest.main()
