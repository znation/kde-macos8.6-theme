"""Pin ``cross_check``'s register validation on a synthetic repository.

The register-shape tests here cover what a valid register is and how
``cross_check`` rejects a malformed or unreadable one, from the data row
through the blank provenance cell. The shipped-register drive stays in
``tests/test_invariants.py``; the shared fixture is ``InvariantsRegisterTestCase``
in ``tests/support/invariants_register_case.py``.
"""

import unittest
from unittest import mock

from support import invariants
from support.invariants import cross_check
from support.invariants_register_case import InvariantsRegisterTestCase
from support.theme_install import write_file
from support.tmp_dir import make_tmp_dir


class TestCrossCheck(InvariantsRegisterTestCase):
    """Pin ``cross_check`` on malformed, unreadable and blank register rows."""

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

    def test_parsed_module_reuses_an_unchanged_files_parse(self):
        # The invariant checker and the entry-point guard test both read the
        # test modules in one run, so the second reader must reuse the first's
        # tree rather than parsing the same unchanged file again.
        path = self.root / self.MODULE
        with mock.patch.object(
            invariants.ast, "parse", wraps=invariants.ast.parse
        ) as parse:
            first = invariants.parsed_module(path, self.root)
            second = invariants.parsed_module(path, self.root)
        self.assertIs(first, second)
        self.assertEqual(parse.call_count, 1)

    def test_parsed_module_rechecks_containment_on_a_cache_hit(self):
        # A tree first read while the path was outside the named root is
        # cached; a later call naming a root the path escapes must still run
        # the containment check instead of serving the cached tree.
        private_root = make_tmp_dir(self)
        private = private_root / "private.py"
        private.write_text("secret = 1\n", encoding="utf-8")
        path = self.root / self.MODULE
        path.unlink()
        path.symlink_to(private)
        invariants.parsed_module(path, private_root)
        with self.assertRaisesRegex(ValueError, "resolves outside"):
            invariants.parsed_module(path, self.root)

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
        register = write_file(root / "docs" / "invariants.md", "## aurorae\n")
        with self.assertRaisesRegex(AssertionError, "cannot be listed"):
            cross_check(str(root), str(register))

    def test_cross_check_reports_an_unreadable_theme_directory(self):
        register = self._valid_register()
        theme_dir = str(self.root / "theme")
        with mock.patch.object(
            invariants.os, "listdir", side_effect=PermissionError("permission denied")
        ) as listdir:
            with self.assertRaisesRegex(
                AssertionError, r"theme.*cannot be listed: permission denied"
            ):
                cross_check(self.root, register)
        listdir.assert_called_once_with(theme_dir)

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


if __name__ == "__main__":
    unittest.main()
