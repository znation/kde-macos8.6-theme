"""Record-validation tests for tools/check_references.py.

``sources.txt`` entries and the files they name are validated before the
checker reads any image: a filename must be bare, a source URL must be a
well-formed absolute URL, a declared file's bytes must be a known raster
format, and an untrusted name must be escaped before it reaches a terminal.
"""

import tempfile
import unittest
from pathlib import Path

from support.check_references_fixtures import (
    CheckerTestCase,
    assert_problem,
    check_references_in,
    reference_set,
)
from support.error_assertions import assert_escapes_escape_character
from tools.image_format import PNG_MAGIC


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
            {"good.png": PNG_MAGIC},
        )
        self.assertEqual(problems, [])

    def test_carriage_return_still_ends_a_line(self):
        module = self.checker
        problems = check_references_in(
            module,
            "good.png | https://example.test/g.png | label\r"
            "bad.png | https://example.test/b.png | label\r",
            {"good.png": PNG_MAGIC, "bad.png": b"not an image"},
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
            {"sub/good.png": PNG_MAGIC},
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
        # A JPEG begins ff d8 ff; the bytes after it are not part of the check.
        problems = self._problems_for(
            module, "photo.jpg", b"\xff\xd8\xff\xe1" + b"\x00" * 8
        )
        self.assertEqual(problems, [])

    def test_gif87a_signature_is_accepted(self):
        module = self.checker
        problems = self._problems_for(module, "anim.gif", b"GIF87a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_gif89a_signature_is_accepted(self):
        module = self.checker
        problems = self._problems_for(module, "anim.gif", b"GIF89a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_webp_signature_is_accepted(self):
        module = self.checker
        # The reference set's sherlock_fandom.jpg is a WebP payload, so the
        # RIFF/WEBP signature must be accepted even under a .jpg name; only
        # the bytes decide, never the extension.
        problems = self._problems_for(
            module, "sherlock_fandom.jpg", b"RIFF\x24\x00\x00\x00WEBPVP8 "
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

    A NUL cannot appear in a POSIX path and makes ``Path.resolve()`` raise
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
