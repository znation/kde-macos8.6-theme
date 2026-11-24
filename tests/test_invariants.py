"""Drive ``tests/support/invariants.py``'s register parser and cross-check.

The register states, per ``theme/`` subsystem and for the fidelity gate, the
guarantee a surface must keep and the test that pins it. ``tests/support/invariants.py``
parses the register and cross-checks it against the repository. This module
drives ``parse_rows`` (``TestHelpers``), then the shipped register
(``TestRepositoryRegister``). The ``cross_check`` tests, for both the
reference resolution and the register shape, live in
``tests/test_invariants_cross_check.py``.
"""

from __future__ import annotations

import unittest

from support.invariants import REGISTER, Row, cross_check, parse_rows
from support.error_assertions import assert_escapes_escape_character
from support.invariants_register_case import InvariantsRegisterTestCase
from support.repo_root import ROOT


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
