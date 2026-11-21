"""Record, URL and name validation tests for tools/check_references.py.

``sources.txt`` entries and the files they name are validated before the
checker reads any image: a filename must be bare and a source URL must be a
well-formed absolute URL. The undeclared scan and filename safety checks also
ensure untrusted names are escaped before they reach a terminal. Declared
image payload checks live in ``test_check_references_image_streams.py``.
"""

import os
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
from tools.image_format import (
    PNG_MAGIC,
    TERMINAL_PNG,
)
from tools import reference_sources

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


class TestOccupiedDeclaredName(CheckerTestCase):
    """A declared name that is not absent is named as occupied, not missing.

    A directory, or a dangling symlink, sitting at the declared name is
    present on disk, so reporting it as ``does not exist`` would send the
    author looking for a file that is already there.
    """

    def test_directory_at_the_declared_name_is_not_called_missing(self):
        module = self.checker
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
        ) as root:
            (root / "good.png").mkdir()
            problems = module.check_references(root)
        assert_problem(self, problems, "good.png", "is not a regular file")
        self.assertFalse(
            any("does not exist" in line for line in problems), problems
        )

    def test_dangling_symlink_at_the_declared_name_is_not_called_missing(self):
        module = self.checker
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
        ) as root:
            os.symlink(root / "nowhere.png", root / "good.png")
            problems = module.check_references(root)
        assert_problem(self, problems, "good.png", "is not a regular file")
        self.assertFalse(
            any("does not exist" in line for line in problems), problems
        )

    def test_absent_declared_name_is_still_called_missing(self):
        module = self.checker
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
        ) as root:
            problems = module.check_references(root)
        assert_problem(self, problems, "good.png", "does not exist")


if __name__ == "__main__":
    unittest.main()
