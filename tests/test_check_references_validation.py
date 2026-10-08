"""Record-validation tests for tools/check_references.py.

``sources.txt`` entries and the files they name are validated before the
checker reads any image: a filename must be bare, a source URL must be a
well-formed absolute URL, a declared file's bytes must be a known raster
format, and an untrusted name must be escaped before it reaches a terminal.
"""

import tempfile
import unittest
from pathlib import Path

from check_references_fixtures import (
    assert_problem,
    check_references_in,
    load_checker,
    reference_set,
)


class TestFilenameMustBeBare(unittest.TestCase):
    """A sources.txt entry must name a bare file in the directory.

    A nested path or ``..`` traversal can reach a file outside the reference
    directory even when that file exists, so the entry is rejected on its
    shape rather than on whether it resolves.
    """

    def test_nested_filename_is_rejected_even_when_the_file_exists(self):
        module = load_checker()
        with reference_set(
            module,
            "sub/good.png | https://example.test/g.png | label\n",
            {"sub/good.png": module.PNG_MAGIC},
        ) as root:
            problems = module.check_references(root)
        assert_problem(self, problems, "sub/good.png", "bare filename")

    def test_parent_traversal_is_rejected_even_when_the_file_exists(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "refs"
            root.mkdir()
            (root / module.SOURCES_NAME).write_text(
                "../escape.png | https://example.test/e.png | label\n",
                encoding="utf-8",
            )
            (root.parent / "escape.png").write_bytes(module.PNG_MAGIC)
            problems = module.check_references(root)
        assert_problem(self, problems, "../escape.png", "bare filename")


class TestAbsoluteUrlSchemeShape(unittest.TestCase):
    """A source entry must be a scheme followed by a non-empty remainder.

    A scheme with nothing after it names no resource, and a bare host or
    relative path has no scheme at all; both must be rejected so a broken
    citation cannot pass as provenance.
    """

    def test_scheme_and_remainder_are_both_required(self):
        module = load_checker()
        self.assertTrue(module._is_absolute_url("https://example.test/x"))
        # A scheme with nothing after it names no resource.
        self.assertFalse(module._is_absolute_url("https://"))
        # A bare host or relative path has no scheme at all.
        self.assertFalse(module._is_absolute_url("example.test/x"))

    def test_scheme_must_start_with_an_ascii_letter(self):
        module = load_checker()
        # RFC 3986: ALPHA *( ALPHA / DIGIT / "+" / "-" / "." ).
        self.assertTrue(module._is_absolute_url("h2://example.test/x"))
        self.assertTrue(module._is_absolute_url("svn+ssh://example.test/x"))
        self.assertFalse(module._is_absolute_url("1http://example.test/x"))
        self.assertFalse(module._is_absolute_url("h\u00e9llo://example.test/x"))
        self.assertFalse(module._is_absolute_url("://example.test/x"))

    def test_empty_remainder_is_reported_by_the_checker(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text(
                "good.png | https:// | label\n", encoding="utf-8"
            )
            (root / "good.png").write_bytes(module.PNG_MAGIC)
            problems = module.check_references(root)
        assert_problem(self, problems, "absolute URL")


class TestAbsoluteUrlWellFormedness(unittest.TestCase):
    """The source URL must be a well-formed absolute URL, not merely start
    with something alpha-like before ``://``."""

    def setUp(self):
        self.is_absolute = load_checker()._is_absolute_url

    def test_well_formed_urls_are_accepted(self):
        for url in (
            "https://example.test/x.png",
            "http://example.test",
            "git+ssh://example.test/repo",
            "a.b-c+d://example.test",
            # file:// is the one scheme whose authority may be empty.
            "file:///tmp/x.png",
            "file://host/tmp/x.png",
        ):
            self.assertTrue(self.is_absolute(url), url)

    def test_relative_and_schemeless_urls_are_rejected(self):
        for url in (
            "example.test/x.png",
            "https://",
            "://example.test",
            "1http://example.test",
        ):
            self.assertFalse(self.is_absolute(url), url)

    def test_urls_with_an_empty_authority_are_rejected(self):
        # The scheme is valid, but ``://`` with no host names nowhere for the
        # citation to point; only file:// may omit the authority.
        for url in (
            "https:///x.png",
            "http:///x.png",
            "https://?q",
            "https://#frag",
            "git+ssh:///repo",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))
        self.assertTrue(self.is_absolute("file:///x.png"))

    def test_malformed_scheme_is_rejected(self):
        for url in (
            "ht tp://example.test/x.png",
            "ht!tp://example.test/x.png",
            "ht\ttp://example.test/x.png",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))

    def test_raw_whitespace_or_control_characters_are_rejected(self):
        for url in (
            "https://example.test/a b.png",
            "https://example.test/a\tb.png",
            "https://example.test/a\x01b.png",
        ):
            self.assertFalse(self.is_absolute(url), repr(url))

    def test_raw_whitespace_problem_names_the_whitespace_not_the_scheme(self):
        # The URL's scheme is valid, so a diagnostic that blames the scheme
        # sends the reader after the wrong fix; it must point at the space.
        module = load_checker()
        problems = check_references_in(
            module,
            "bad.png | https://example.test/a b.png | label\n",
            {"bad.png": module.PNG_MAGIC},
        )
        assert_problem(self, problems, "whitespace or control")
        self.assertFalse(
            any("absolute URL" in line for line in problems), problems
        )

    def test_empty_authority_problem_names_the_host_not_the_scheme(self):
        # The scheme is valid, so a diagnostic that blames it sends the reader
        # after the wrong fix; it must point at the missing host instead.
        module = load_checker()
        problems = check_references_in(
            module,
            "bad.png | https:///a.png | label\n",
            {"bad.png": module.PNG_MAGIC},
        )
        assert_problem(self, problems, "must name a host")
        self.assertFalse(
            any("absolute URL" in line for line in problems), problems
        )


class TestAcceptedImageFormats(unittest.TestCase):
    """The checker must accept every raster format the reference set uses.

    The built-in self-test does not exercise the GIF signatures, so a
    regression in GIF handling would flag the reference set's 1 GIF file as a
    non-image without any test noticing.
    """

    def _problems_for(self, module, filename, content):
        return check_references_in(
            module,
            f"{filename} | https://example.test/x | label\n",
            {filename: content},
        )

    def test_jpeg_signature_is_accepted(self):
        module = load_checker()
        # A JPEG begins ff d8 ff; the bytes after it are not part of the check.
        problems = self._problems_for(
            module, "photo.jpg", b"\xff\xd8\xff\xe1" + b"\x00" * 8
        )
        self.assertEqual(problems, [])

    def test_gif87a_signature_is_accepted(self):
        module = load_checker()
        problems = self._problems_for(module, "anim.gif", b"GIF87a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_gif89a_signature_is_accepted(self):
        module = load_checker()
        problems = self._problems_for(module, "anim.gif", b"GIF89a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_riff_container_that_is_not_webp_is_rejected(self):
        module = load_checker()
        # A RIFF/WAVE payload shares the RIFF prefix but is not an image; the
        # WEBP marker at bytes 8-11 is what makes it a WebP.
        problems = self._problems_for(
            module, "sound.png", b"RIFF\x24\x00\x00\x00WAVEfmt "
        )
        assert_problem(
            self, problems, "sound.png", "not a PNG, JPEG, GIF or WebP"
        )


class TestUndeclaredImageExtension(unittest.TestCase):
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
        module = load_checker()
        self._assert_undeclared(module, "half-downloaded.png")

    def test_uppercase_extension_is_matched_case_insensitively(self):
        module = load_checker()
        self._assert_undeclared(module, "SHOT.PNG")

    def test_jpeg_extension_is_matched(self):
        module = load_checker()
        self._assert_undeclared(module, "photo.jpeg")


class TestControlCharactersInFilenames(unittest.TestCase):
    """An untrusted filename must not reach the terminal as live bytes.

    The reference directory can hold a contributor-supplied name, so an ESC or
    newline in it would otherwise drive the operator's terminal or forge a
    diagnostic line when the checker reports the undeclared image.
    """

    def _undeclared(self, module, filename):
        return check_references_in(module, "", {filename: module.PNG_MAGIC})

    def test_escape_sequence_in_name_is_escaped(self):
        module = load_checker()
        problems = self._undeclared(module, "evil\x1b[31m.png")
        self.assertTrue(problems, "expected an undeclared-image problem")
        joined = "\n".join(problems)
        self.assertNotIn("\x1b", joined)
        self.assertIn("\\u001b", joined)

    def test_newline_in_name_cannot_forge_a_line(self):
        module = load_checker()
        problems = self._undeclared(module, "fake\nproblem line.png")
        joined = "\n".join(problems)
        self.assertNotIn("fake\nproblem", joined)
        self.assertIn("\\u000a", joined)


class TestNullByteFilename(unittest.TestCase):
    """A NUL byte in a source entry must be a diagnostic, not a crash.

    A NUL cannot appear in a POSIX path and makes ``Path.resolve()`` raise
    ValueError, so the symlink containment check must not let a malformed
    sources.txt line abort the whole run with an unhandled exception.
    """

    def test_null_byte_in_filename_is_reported_not_raised(self):
        module = load_checker()
        problems = check_references_in(
            module,
            b"bad\x00name.png | https://example.test/b.png | label\n",
        )
        assert_problem(self, problems, "bad\\x00name.png", "NUL")


if __name__ == "__main__":
    unittest.main()
