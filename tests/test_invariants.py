"""Drive ``tests/invariants.py``'s register parser and cross-check.

The register states, per ``theme/`` subsystem and for the fidelity gate, the
guarantee a surface must keep and the test that pins it. ``tests/invariants.py``
parses the register and cross-checks it against the repository; this module
drives those checks, first against a synthetic repository (``TestHelpers``) and
then against the shipped register (``TestRepositoryRegister``).
"""

from __future__ import annotations

import traceback
import unittest
from unittest import mock

import invariants
from invariants import REGISTER, Row, cross_check, parse_rows
from support.error_assertions import assert_escapes_escape_character
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir


class TestHelpers(unittest.TestCase):
    """Pin the register reader on a synthetic repository."""

    # The synthetic module lives only in the temp root, never in the
    # repository, so its name carries no module suffix or repository
    # directory prefix that a repository path check could try to resolve.
    MODULE = "fake_module"
    # A module with no test case at all, for the bare-file reference check.
    NO_TESTS_MODULE = "no_tests_module"

    def setUp(self):
        self.root = make_tmp_dir(self)
        (self.root / "theme" / "aurorae").mkdir(parents=True)
        self._write(
            self.MODULE,
            "import unittest\n\n\n"
            "class TestFake(unittest.TestCase):\n"
            "    def setUp(self):\n"
            "        pass\n"
            "\n"
            "    def test_ok(self):\n"
            "        pass\n"
            "\n\n"
            "class Helper:\n"
            "    def helper(self):\n"
            "        pass\n"
            "\n\n"
            "class NotATestCase:\n"
            "    def test_looks_like_a_test(self):\n"
            "        pass\n"
            "\n\n"
            "class MixinCase(unittest.TestCase):\n"
            "    pass\n"
            "\n\n"
            "class TestViaMixin(MixinCase):\n"
            "    def test_ok(self):\n"
            "        pass\n"
            "\n\n"
            "class FakeTestCase:\n"
            "    pass\n"
            "\n\n"
            "class TestNotCollected(FakeTestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
        )
        self._write(
            self.NO_TESTS_MODULE,
            "class Helper:\n"
            "    def helper(self):\n"
            "        pass\n",
        )

    def _write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def _register(self, text):
        path = self.root / "docs" / "invariants.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return str(path)

    def _table(self, rows):
        lines = ["| Guarantee | Test | Provenance exception |", "| --- | --- | --- |"]
        for guarantee, reference in rows:
            lines.append(f"| {guarantee} | `{reference}` | none |")
        return "\n".join(lines) + "\n"

    def _valid_register(self, aurorae_rows=None):
        return self._register(
            "# Invariants\n\n"
            "## aurorae\n\n"
            + self._table(
                aurorae_rows
                if aurorae_rows is not None
                else [("The aurorae thing holds.", f"{self.MODULE}::TestFake")]
            )
            + "\n## tooling\n\n"
            + self._table(
                [("The gate holds.", f"{self.MODULE}::TestFake::test_ok")]
            )
        )

    def assert_cross_check_rejects(self, reference, message):
        """Assert `cross_check` rejects a register whose row names *reference*.

        The register is otherwise valid, so the failure isolates the
        malformed *reference*, and *message* is a regex the diagnostic must
        match.
        """
        register = self._valid_register([("The thing holds.", reference)])
        with self.assertRaisesRegex(AssertionError, message):
            cross_check(self.root, register)

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

    def test_cross_check_rejects_a_data_row_without_a_test_reference(self):
        # A data row whose Test cell lost its backticks is malformed, not a
        # header; dropping it silently would leave its guarantee unpinned.
        # The section keeps a valid first row so the bug is not masked by the
        # empty-section check.
        register = self._register(
            "# Invariants\n\n## aurorae\n\n"
            "| Guarantee | Test | Provenance exception |\n"
            "| --- | --- | --- |\n"
            f"| The first thing holds. | `{self.MODULE}::TestFake` | none |\n"
            f"| The second thing holds. | {self.MODULE}::TestFake | none |\n"
            "\n## tooling\n\n"
            + self._table([("The gate holds.", f"{self.MODULE}::TestFake::test_ok")])
        )
        with self.assertRaisesRegex(AssertionError, "no test reference"):
            cross_check(self.root, register)

    def test_cross_check_accepts_a_matching_register(self):
        sections = cross_check(self.root, self._valid_register())
        self.assertEqual(set(sections), {"aurorae", "tooling"})

    def test_cross_check_reuses_an_unchanged_modules_parse(self):
        # The same module is named by two rows, and the check runs over the
        # same tree repeatedly (the mutation cases do), so an unchanged file
        # must be parsed once rather than once per row and again per run.
        register = self._valid_register()
        with mock.patch.object(
            invariants.ast, "parse", wraps=invariants.ast.parse
        ) as parse:
            cross_check(self.root, register)
            cross_check(self.root, register)
        self.assertEqual(parse.call_count, 1)

    def test_cross_check_reparses_a_module_that_changed(self):
        # A cached parse must not mask a rewritten module: the second check
        # names the old class, which the new contents no longer define.
        cross_check(self.root, self._valid_register())
        self._write(
            self.MODULE,
            "import unittest\n\n\n"
            "class TestChanged(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
        )
        self.assert_cross_check_rejects(
            f"{self.MODULE}::TestFake", "missing class TestFake"
        )

    def test_cross_check_rejects_an_unreadable_register(self):
        # The register is read with open(); a missing or unreadable
        # docs/invariants.md must be reported as the checker's own
        # AssertionError naming the path, not a bare OSError naming neither
        # the checker nor the register's role.
        with self.assertRaisesRegex(AssertionError, "cannot be read"):
            cross_check(self.root, str(self.root / "docs" / "invariants.md"))

    def test_cross_check_rejects_a_non_utf8_register(self):
        # A register whose bytes are not UTF-8 would otherwise abort the check
        # with a bare UnicodeDecodeError; report it as the checker's own
        # AssertionError naming the path instead.
        path = self.root / "docs" / "invariants.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfe not utf-8")
        with self.assertRaisesRegex(AssertionError, "not valid UTF-8"):
            cross_check(self.root, str(path))

    def test_cross_check_refuses_a_symlinked_register_that_escapes(self):
        # `parse_rows` echoes a malformed row's line in its AssertionError, so
        # a checked-in symlink at docs/invariants.md that resolves outside the
        # repository must be refused before it is opened rather than read and
        # echoed. The private file sits under a second temp root, outside
        # `self.root`, so the symlink escapes it.
        private_root = make_tmp_dir(self)
        private = private_root / "private.txt"
        private.write_text(
            "## aurorae\n| secret-token | short\n", encoding="utf-8"
        )
        register = self.root / "docs" / "invariants.md"
        register.parent.mkdir(parents=True, exist_ok=True)
        register.symlink_to(private)
        with self.assertRaises(ValueError) as caught:
            cross_check(str(self.root), str(register))
        self.assertIn("resolves outside", str(caught.exception))
        self.assertNotIn("secret-token", str(caught.exception))

    def test_cross_check_rejects_a_bare_file_with_no_test_case(self):
        # The bare `path` form names the whole file, so it pins the guarantee
        # to that file's tests. A file that defines no test case pins nothing;
        # accepting it would leave the guarantee unchecked while the register
        # reads as if it were covered.
        self.assert_cross_check_rejects(
            self.NO_TESTS_MODULE, "defines no test case"
        )

    def test_cross_check_accepts_a_test_case_inherited_from_a_module_base(self):
        # `path::TestViaMixin` reaches `unittest.TestCase` through a base
        # defined in the same module. unittest collects it, so the register
        # must accept it even though it does not list TestCase directly.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestViaMixin")]
        )
        cross_check(self.root, register)

    def test_cross_check_accepts_a_test_case_with_a_local_non_test_base(self):
        # `TestWithMixin(LocalMixin, unittest.TestCase)` reaches TestCase only
        # through its second base: the first is a class defined in the same
        # module that is not a test case. `is_test_case` must keep scanning the
        # remaining bases instead of stopping at the first local one, so
        # unittest's collection of this class and the register's acceptance
        # agree.
        self._write(
            "mixed_base_module",
            "import unittest\n\n\n"
            "class LocalMixin:\n"
            "    def helper(self):\n"
            "        pass\n"
            "\n\n"
            "class TestWithMixin(LocalMixin, unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
        )
        register = self._valid_register(
            [("The thing holds.", "mixed_base_module::TestWithMixin")]
        )
        cross_check(self.root, register)

    def test_cross_check_rejects_a_module_with_a_base_cycle(self):
        # A class whose base chain loops back on itself (`First(Second)`,
        # `Second(First)`) never reaches TestCase and unittest never collects
        # it, but a base-following check must terminate on the cycle instead of
        # recursing forever. The bare-file reference must reject the module by
        # name, not escape as a `RecursionError`.
        self._write(
            "cycle_module",
            "class First(Second):\n"
            "    pass\n"
            "\n\n"
            "class Second(First):\n"
            "    pass\n",
        )
        register = self._valid_register([("The thing holds.", "cycle_module")])
        with self.assertRaisesRegex(AssertionError, "defines no test case"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_subsystem_section(self):
        register = self._register(
            "# Invariants\n\n## tooling\n\n"
            + self._table([("The gate holds.", f"{self.MODULE}::TestFake")])
        )
        with self.assertRaisesRegex(AssertionError, "theme/aurorae has no section"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_section_with_no_rows(self):
        register = self._register(
            "# Invariants\n\n## aurorae\n\nNo table yet.\n\n## tooling\n\n"
            + self._table([("The gate holds.", f"{self.MODULE}::TestFake")])
        )
        with self.assertRaisesRegex(AssertionError, "section aurorae .* has no rows"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_tooling_section(self):
        register = self._register(
            "# Invariants\n\n## aurorae\n\n"
            + self._table([("The thing holds.", f"{self.MODULE}::TestFake")])
        )
        with self.assertRaisesRegex(AssertionError, "tooling has no section"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_theme_directory(self):
        # The register is cross-checked against `theme/`; a root whose
        # `theme/` directory is missing (a fresh checkout mid-setup, a
        # rename) makes `os.listdir` raise `FileNotFoundError`, naming neither
        # the checker nor the directory.
        root = make_tmp_dir(self)
        register = root / "docs" / "invariants.md"
        register.parent.mkdir(parents=True)
        register.write_text("## aurorae\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "cannot be listed"):
            cross_check(str(root), str(register))

    def test_cross_check_rejects_a_section_for_a_missing_subsystem(self):
        # A section for a subsystem that is not there -- a stale heading left
        # after a rename, or a typo -- reads as a pinned guarantee while no
        # surface enforces it. Reject it by name instead of letting the
        # register overstate what it covers.
        register = self._register(
            "# Invariants\n\n## aurorae\n\n"
            + self._table([("The thing holds.", f"{self.MODULE}::TestFake")])
            + "\n## ghost\n\n"
            + self._table([("The ghost holds.", f"{self.MODULE}::TestFake")])
            + "\n## tooling\n\n"
            + self._table([("The gate holds.", f"{self.MODULE}::TestFake")])
        )
        with self.assertRaisesRegex(AssertionError, "section ghost .* names no"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_blank_guarantee(self):
        register = self._valid_register([("", f"{self.MODULE}::TestFake")])
        with self.assertRaisesRegex(AssertionError, "blank guarantee"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_blank_provenance(self):
        # The third column records the provenance exception or the literal
        # "none"; a blank cell reads as an exception that was never written
        # down. Reject it by name so the row cannot claim a guarantee while
        # saying nothing about where its value came from.
        register = self._register(
            "# Invariants\n\n"
            "## aurorae\n\n"
            "| Guarantee | Test | Provenance exception |\n"
            "| --- | --- | --- |\n"
            f"| The thing holds. | `{self.MODULE}::TestFake` | |\n"
            "\n## tooling\n\n"
            + self._table(
                [("The gate holds.", f"{self.MODULE}::TestFake::test_ok")]
            )
        )
        with self.assertRaisesRegex(AssertionError, "blank provenance"):
            cross_check(self.root, register)

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
        # cannot be opened (a permission error, for example), so
        # `_defined_names`'s `open` raises `OSError`. That exception names
        # neither the register section nor the reference, so a maintainer
        # cannot tell which row points at the unreadable file. `OSError` is
        # one of the three exception types the read guard catches; the other
        # two (`UnicodeDecodeError`, `SyntaxError`) are pinned above, so this
        # case keeps the `OSError` arm of that catch observable.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestFake")]
        )
        with mock.patch.object(
            invariants, "_defined_names", side_effect=OSError("permission denied")
        ):
            with self.assertRaisesRegex(AssertionError, "cannot be read as Python"):
                cross_check(self.root, register)

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
        outside.mkdir()
        (outside / self.MODULE).write_text(
            "import unittest\n\n\n"
            "class TestFake(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        repo = base / "repo"
        (repo / "theme" / "aurorae").mkdir(parents=True)
        register = repo / "docs" / "invariants.md"
        register.parent.mkdir(parents=True)
        for path in (str(outside / self.MODULE), f"../outside/{self.MODULE}"):
            with self.subTest(path=path):
                register.write_text(
                    "# Invariants\n\n## aurorae\n\n"
                    + self._table([("The thing holds.", f"{path}::TestFake")])
                    + "\n## tooling\n\n"
                    + self._table([("The gate holds.", f"{path}::TestFake::test_ok")]),
                    encoding="utf-8",
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
