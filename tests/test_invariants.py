"""Drive ``tests/support/invariants.py``'s register parser and cross-check.

The register states, per ``theme/`` subsystem and for the fidelity gate, the
guarantee a surface must keep and the test that pins it. ``tests/support/invariants.py``
parses the register and cross-checks it against the repository. This module
drives ``parse_rows`` and the reference-resolution checks of ``cross_check``
against a synthetic repository (``TestHelpers``), then the shipped register
(``TestRepositoryRegister``). The register-shape ``cross_check`` tests live in
``tests/test_invariants_cross_check.py``.
"""

from __future__ import annotations

import traceback
import unittest
from unittest import mock

from support import invariants
from support.invariants import REGISTER, Row, cross_check, parse_rows
from support.error_assertions import assert_escapes_escape_character
from support.invariants_register_case import InvariantsRegisterTestCase
from support.repo_root import ROOT
from support.theme_install import write_file
from support.tmp_dir import make_tmp_dir
from tools import containment as containment_impl


class TestHelpers(InvariantsRegisterTestCase):
    """Pin the register parser and the reference checks on a synthetic repository."""

    def test_parse_rows_reads_sections_and_rows(self):
        sections = parse_rows(
            "## aurorae\n\n"
            "| Guarantee | Test | Provenance exception |\n"
            "| --- | --- | --- |\n"
            f"| The thing holds. | `{self.MODULE}::TestFake` | none |\n"
        )
        self.assertEqual(
            sections,
            {
                "aurorae": [
                    Row("The thing holds.", [f"{self.MODULE}::TestFake"], "none")
                ]
            },
        )

    def test_parse_rows_keeps_a_cell_with_an_escaped_pipe(self):
        # A Markdown table writes a literal pipe as ``\|``. Splitting on
        # every pipe would give four cells and drop the whole row, leaving
        # its guarantee unpinned with no error.
        sections = parse_rows(
            "## aurorae\n\n"
            "| Guarantee | Test | Provenance exception |\n"
            "| --- | --- | --- |\n"
            f"| The a \\| b guarantee holds. | `{self.MODULE}::TestFake` | none |\n"
        )
        self.assertEqual(
            sections,
            {
                "aurorae": [
                    Row(
                        "The a | b guarantee holds.",
                        [f"{self.MODULE}::TestFake"],
                        "none",
                    )
                ]
            },
        )

    def test_parse_rows_unescapes_a_literal_backslash(self):
        # Markdown writes a literal backslash as ``\\``. Consuming the pair
        # keeps a path one backslash, and keeps a cell that ends in a
        # backslash (``\\|``) from reading its closing pipe as an escaped
        # pipe and dropping the whole row as malformed.
        cases = (
            (
                f"| The path C:\\\\tmp holds. | `{self.MODULE}::TestFake` | none |\n",
                "The path C:\\tmp holds.",
            ),
            (
                f"| The path ends with a backslash \\\\| `{self.MODULE}::TestFake` | none |\n",
                "The path ends with a backslash \\",
            ),
        )
        for line, guarantee in cases:
            with self.subTest(line=line):
                sections = parse_rows(
                    "## aurorae\n\n"
                    "| Guarantee | Test | Provenance exception |\n"
                    "| --- | --- | --- |\n"
                    + line
                )
                self.assertEqual(
                    sections,
                    {
                        "aurorae": [
                            Row(guarantee, [f"{self.MODULE}::TestFake"], "none")
                        ]
                    },
                )

    def test_parse_rows_preserves_a_backslash_before_an_unrecognized_escape(self):
        # The parser only consumes Markdown escapes for a pipe or another
        # backslash. A Windows-style path containing ``\q`` must retain both
        # characters instead of silently losing the path separator.
        sections = parse_rows(
            "## aurorae\n\n"
            "| Guarantee | Test | Provenance exception |\n"
            "| --- | --- | --- |\n"
            f"| The path C:\\q holds. | `{self.MODULE}::TestFake` | none |\n"
        )
        self.assertEqual(
            sections["aurorae"],
            [Row("The path C:\\q holds.", [f"{self.MODULE}::TestFake"], "none")],
        )

    def test_parse_rows_rejects_a_row_that_is_not_three_cells(self):
        # A line that starts with a pipe is a table row. One that splits into
        # two or four cells is malformed; dropping it would leave its
        # guarantee unpinned with no error, exactly as an escaped pipe did.
        for malformed in (
            f"| The thing holds. | `{self.MODULE}::TestFake`\n",
            f"| The thing holds. | `{self.MODULE}::TestFake` | none | extra |\n",
        ):
            with self.subTest(row=malformed):
                with self.assertRaisesRegex(AssertionError, "malformed table row"):
                    parse_rows(
                        "## aurorae\n\n"
                        "| Guarantee | Test | Provenance exception |\n"
                        "| --- | --- | --- |\n"
                        + malformed
                    )

    def test_parse_rows_rejects_a_duplicate_section(self):
        # Two ``## aurorae`` headings would otherwise merge into one section
        # (``setdefault``), silently attributing both tables' guarantees to the
        # same subsystem and hiding a section that was mis-split by a rename or
        # a copy-paste.
        with self.assertRaisesRegex(AssertionError, "duplicate section aurorae"):
            parse_rows(
                "## aurorae\n\n"
                "| Guarantee | Test | Provenance exception |\n"
                "| --- | --- | --- |\n"
                f"| The thing holds. | `{self.MODULE}::TestFake` | none |\n"
                "\n## aurorae\n\n"
                "| Guarantee | Test | Provenance exception |\n"
                "| --- | --- | --- |\n"
                f"| The other thing holds. | `{self.MODULE}::TestFake` | none |\n"
            )

    def test_cross_check_rejects_a_missing_test_file(self):
        self.assert_cross_check_rejects(
            "absent_module::TestFake", "missing file"
        )

    def test_cross_check_rejects_a_reference_to_an_unparseable_file(self):
        # `check_reference` reads the named module with `ast.parse` to find its
        # classes. A file that is not UTF-8, or not valid Python, makes that
        # read raise `UnicodeDecodeError`/`SyntaxError` -- an exception that
        # names neither the register section nor the reference, so the failure
        # a maintainer sees does not say which row points at the broken file.
        # Both must surface as the register's own `AssertionError`.
        for name, content in (
            ("not_utf8", b"import unittest\n\n# \xff\xfe stray byte\n"),
            ("not_python", b"def (:\n"),
        ):
            with self.subTest(module=name):
                (self.root / name).write_bytes(content)
                register = self._valid_register(
                    [("The thing holds.", f"{name}::TestFake")]
                )
                with self.assertRaisesRegex(
                    AssertionError, "cannot be read as Python"
                ):
                    cross_check(self.root, register)

    def test_cross_check_rejects_a_reference_to_a_file_it_cannot_read(self):
        # `check_reference`'s isfile guard passes a file that exists but
        # cannot be opened (a permission error, for example), so the
        # `_defined_names` read raises `OSError`. That exception names
        # neither the register section nor the reference, so a maintainer
        # cannot tell which row points at the unreadable file. `OSError` is
        # one of the four exception types the read guard catches; the other
        # three (`UnicodeDecodeError`, `SyntaxError`, `ValueError`) are pinned
        # above or below, so this case keeps the `OSError` arm observable.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestFake")]
        )
        with mock.patch.object(
            invariants, "_defined_names", side_effect=OSError("permission denied")
        ):
            with self.assertRaisesRegex(AssertionError, "cannot be read as Python"):
                cross_check(self.root, register)

    def test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole(self):
        # A register row names a test module by path, and that module is
        # contributor-supplied. A multi-gigabyte file must be refused by the
        # shared reader's cap by name instead of being loaded whole, which
        # could raise a MemoryError naming neither the row nor the file.
        module = self.root / "huge_module.py"
        module.write_bytes(b"x" * (containment_impl._MAX_READ_BYTES + 1))
        register = self._valid_register(
            [("The thing holds.", "huge_module.py::TestFake")]
        )
        with self.assertRaises(AssertionError) as caught:
            cross_check(self.root, register)
        self.assertIn(str(module), str(caught.exception))
        self.assertIn("larger than", str(caught.exception))

    def test_cross_check_rejects_a_reference_with_a_nul_byte(self):
        # A NUL byte in the reference reaches `os.path.realpath`, which raises
        # `ValueError: embedded null character in path` before the
        # isfile/parse guards. That exception names neither the section nor
        # the reference, so the row that broke the register is unidentifiable.
        self.assert_cross_check_rejects(
            f"{self.MODULE}\x00::TestFake", "NUL"
        )

    def test_cross_check_rejects_a_missing_class(self):
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestNope", "missing class TestNope"
        )

    def test_cross_check_rejects_an_empty_qualifier(self):
        # `path::` names no class, so it pins the guarantee to no test. The
        # bare `path` form is the documented way to name the whole file, so
        # the trailing `::` is a malformed reference, not a file reference.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::", "names no class or method"
        )

    def test_cross_check_rejects_a_reference_with_a_trailing_segment(self):
        # `path::Class::method::junk` names the class and method but then a
        # fourth segment that the reference grammar has no room for; accepting
        # it would let a malformed reference pin a guarantee to a test it may
        # not actually name.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestFake::test_ok::junk",
            "more than a class and method",
        )

    def test_cross_check_rejects_a_missing_method(self):
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestFake::test_nope", "missing method test_nope"
        )

    def test_cross_check_rejects_a_reference_to_a_non_test_method(self):
        # `path::Class::setUp` names a method that exists but is not a test,
        # so the row pins its guarantee to a helper instead of the test that
        # enforces it. Only `test`-prefixed methods are tests unittest runs.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestFake::setUp", "not a test"
        )

    def test_cross_check_rejects_a_class_with_no_tests(self):
        # `path::Helper` names a class that exists but is not a test case, so
        # the row pins its guarantee to a helper class instead of the tests
        # that enforce it. A class reference must resolve to a collected test.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::Helper", "not a test case"
        )

    def test_cross_check_rejects_a_method_on_a_class_with_no_test_case(self):
        # `path::NotATestCase::test_looks_like_a_test` names a test-prefixed
        # method on a class with no TestCase base, so unittest never collects
        # it; accepting the reference would pin the guarantee to a method that
        # never runs. The class check must apply to method references too.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::NotATestCase::test_looks_like_a_test",
            "not a test case",
        )

    def test_cross_check_rejects_a_local_base_that_only_looks_like_a_test_case(self):
        # `path::TestNotCollected` inherits from `FakeTestCase`, a class
        # defined in the same module that does not reach `unittest.TestCase`.
        # The `*TestCase` name suffix is a heuristic for bases imported from
        # elsewhere; applying it to a locally defined base would accept a
        # class unittest never collects, pinning the guarantee to no test.
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestNotCollected::test_ok", "not a test case"
        )

    def test_cross_check_rejects_a_reference_outside_the_repository(self):
        # `check_reference` joins the register's path onto the repository
        # root. An absolute path replaces the root, and a `..` segment climbs
        # out of it, so either form can name a module that is not part of the
        # repository; accepting it would pin a guarantee to a test outside the
        # tree the register is meant to cover.
        base = make_tmp_dir(self)
        outside = base / "outside"
        write_file(
            outside / self.MODULE,
            "import unittest\n\n\n"
            "class TestFake(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
        )
        repo = base / "repo"
        (repo / "theme" / "aurorae").mkdir(parents=True)
        register = repo / "docs" / "invariants.md"
        register.parent.mkdir(parents=True)
        for path in (str(outside / self.MODULE), f"../outside/{self.MODULE}"):
            with self.subTest(path=path):
                write_file(
                    register,
                    "# Invariants\n\n## aurorae\n\n"
                    + self._table([("The thing holds.", f"{path}::TestFake")])
                    + "\n## tooling\n\n"
                    + self._table([("The gate holds.", f"{path}::TestFake::test_ok")]),
                )
                with self.assertRaisesRegex(AssertionError, "outside the repository"):
                    cross_check(repo, str(register))

    def test_parse_rows_escapes_control_characters_in_a_malformed_row(self):
        # docs/invariants.md is contributor-supplied, and parse_rows echoes a
        # malformed row's line in its AssertionError. An ESC there must be shown
        # as its visible escape, not written to the operator's terminal.
        with self.assertRaises(AssertionError) as caught:
            parse_rows(
                "## aurorae\n\n"
                "| Guarantee | Test | Provenance exception |\n"
                "| --- | --- | --- |\n"
                "| The thing holds. | \x1b]0;pwned\x07 | none | extra |\n"
            )
        assert_escapes_escape_character(self, str(caught.exception))

    def test_cross_check_escapes_control_characters_in_a_section_heading(self):
        # A register heading names the section echoed by cross_check. An ESC in
        # that heading must not drive the terminal of the maintainer reading a
        # failed check.
        register = self._register(
            "# Invariants\n\n"
            "## aurorae\n\n"
            + self._table([("The thing holds.", f"{self.MODULE}::TestFake")])
            + "\n## evil\x1b]0;pwned\x07\n\n"
            + self._table([("The evil thing holds.", f"{self.MODULE}::TestFake")])
            + "\n## tooling\n\n"
            + self._table([("The gate holds.", f"{self.MODULE}::TestFake::test_ok")])
        )
        with self.assertRaises(AssertionError) as caught:
            cross_check(self.root, register)
        assert_escapes_escape_character(self, str(caught.exception))

    def test_cross_check_escapes_control_characters_in_a_reference(self):
        # A register row's Test cell is contributor-supplied, and the missing
        # file diagnostic echoes the reference. An ESC in the reference must be
        # escaped rather than reaching the terminal live.
        register = self._valid_register(
            [("The thing holds.", "evil\x1b]0;pwned\x07.py::TestFake")]
        )
        with self.assertRaises(AssertionError) as caught:
            cross_check(self.root, register)
        assert_escapes_escape_character(self, str(caught.exception))

    def test_cross_check_escapes_control_characters_in_a_syntax_error(self):
        # _parse_test_module chains the SyntaxError from a broken module to the
        # register's diagnostic, and a formatted traceback reprints that
        # exception's offending source line. An ESC on that line must not reach
        # the terminal live; the escaped reference keeps the visible marker too.
        bad = "bad\x1b]0;pwned\x07.py"
        (self.root / bad).write_text(
            "def (\x1b]0;pwned\x07:\n", encoding="utf-8"
        )
        register = self._valid_register(
            [("The thing holds.", f"{bad}::TestFake")]
        )
        with self.assertRaises(AssertionError) as caught:
            cross_check(self.root, register)
        rendered = "".join(
            traceback.format_exception(
                type(caught.exception),
                caught.exception,
                caught.exception.__traceback__,
            )
        )
        assert_escapes_escape_character(self, rendered)

    def test_cross_check_escapes_control_characters_in_a_theme_subsystem(self):
        # A theme directory's name is contributor-supplied too; cross_check
        # echoes it when the register has no section for it. An ESC in the name
        # must not reach the terminal as a live byte.
        (self.root / "theme" / "evil\x1b]0;pwned\x07").mkdir()
        with self.assertRaises(AssertionError) as caught:
            cross_check(self.root, self._valid_register())
        assert_escapes_escape_character(self, str(caught.exception))


class TestRepositoryRegister(unittest.TestCase):
    """Cross-check the shipped register against the repository."""

    def test_register_covers_every_subsystem_and_resolves(self):
        sections = cross_check(ROOT, REGISTER)
        self.assertTrue(sections)

    def test_tooltip_provenance_exception_is_recorded(self):
        sections = cross_check(ROOT, REGISTER)
        tooltip = [
            row
            for row in sections["color-schemes"]
            if "Tooltip" in row.guarantee or "Tooltip" in row.provenance
        ]
        self.assertTrue(tooltip, "no color-schemes row records the tooltip exception")
        self.assertTrue(
            any(row.provenance and row.provenance != "none" for row in tooltip),
            "the tooltip row records no provenance exception",
        )


if __name__ == "__main__":
    unittest.main()
