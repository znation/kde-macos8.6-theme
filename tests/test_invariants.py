"""Keep ``docs/invariants.md`` in step with the tests it names.

The register states, per ``theme/`` subsystem and for the fidelity gate, the
guarantee a surface must keep and the test that pins it, so a future bug is
confirmable without reconstructing the intent from the test's body. Nothing
otherwise ties the register to the repository: this module parses its sections
and table rows and fails when a ``theme/`` subsystem directory has no section,
when a row names a test file, class or method that does not exist, when a row
names a method that is not a test, when a row names no test, or when a guarantee
cell is blank.
"""

from __future__ import annotations

import ast
import os
import re
import unittest
from collections import namedtuple

from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir

REGISTER = os.path.join(ROOT, "docs", "invariants.md")
THEME_DIR = "theme"
# Sections that are not ``theme/`` subsystem directories but still belong in
# the register: the render/fidelity tooling lives under ``tooling``.
EXTRA_SECTIONS = ("tooling",)

SECTION = re.compile(r"^##\s+(?P<name>.+?)\s*$")
REFERENCE = re.compile(r"`([^`]+)`")
# A separator cell is a run of dashes, optionally bounded by a colon on
# either side (``---``, ``:--``, ``--:``, ``:-:``).
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
HEADER_CELLS = ("guarantee", "test", "provenance exception")

Row = namedtuple("Row", "guarantee tests provenance")


def _cells(line):
    """Return a table row's three cells, or None for a non-row line.

    A cell may hold a literal pipe, written ``\\|`` in Markdown; the escape is
    consumed and the pipe kept, so such a row still reads as three cells
    instead of being dropped with its guarantee unpinned.
    """
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    cells = []
    current = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            following = text[index + 1]
            if following == "|":
                current.append("|")
                index += 2
                continue
            if following == "\\":
                current.append("\\")
                index += 2
                continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    if len(cells) != 3:
        return None
    return cells


def _is_table_scaffold(cells):
    """Return True for a table's header or separator row, not a data row."""
    if all(SEPARATOR_CELL.match(cell) for cell in cells):
        return True
    return tuple(cell.lower() for cell in cells) == HEADER_CELLS


def parse_rows(text):
    """Return ``{section name: [Row, ...]}`` for the register *text*.

    The header and separator rows of a table are scaffold, not data, and are
    skipped; every other three-cell row becomes a :class:`Row`, even when its
    Test cell names no test, so :func:`cross_check` can reject that row instead
    of losing its guarantee. A line that starts with a pipe but does not split
    into three cells raises :class:`AssertionError`, naming the line, so a
    malformed row cannot be dropped silently.
    """
    sections = {}
    current = None
    for line in text.splitlines():
        match = SECTION.match(line)
        if match:
            current = match.group("name")
            sections.setdefault(current, [])
            continue
        if current is None or not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if cells is None:
            raise AssertionError(
                f"malformed table row in section {current} "
                f"(expected 3 cells): {line.strip()}"
            )
        if _is_table_scaffold(cells):
            continue
        guarantee, test, provenance = cells
        sections[current].append(Row(guarantee, REFERENCE.findall(test), provenance))
    return sections


def _defined_names(path):
    """Return ``{class name: {method name, ...}}`` defined at *path*'s top level."""
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    return classes


def check_reference(root, reference, section):
    """Assert *reference* names an existing test in *root*.

    A reference is ``path``, ``path::Class`` or ``path::Class::method``; raises
    :class:`AssertionError` naming *section* and the first missing piece. A
    reference ending in ``::`` names no class and a reference with a fourth
    ``::`` segment is rejected too, so neither can silently pin a guarantee to
    no test. A named method must be a test (a ``test``-prefixed name, the only
    kind unittest runs), so a helper cannot stand in for the test that pins the
    guarantee.
    """
    path, sep, qualifier = reference.partition("::")
    file_path = os.path.join(root, path)
    if not os.path.isfile(file_path):
        raise AssertionError(f"{section}: {reference} names a missing file")
    if not qualifier:
        if sep:
            raise AssertionError(
                f"{section}: {reference} names no class or method after '::'"
            )
        return
    names = qualifier.split("::")
    if len(names) > 2:
        raise AssertionError(
            f"{section}: {reference} names more than a class and method"
        )
    classes = _defined_names(file_path)
    class_name = names[0]
    if class_name not in classes:
        raise AssertionError(f"{section}: {reference} names a missing class {class_name}")
    if len(names) > 1:
        method_name = names[1]
        if method_name not in classes[class_name]:
            raise AssertionError(
                f"{section}: {reference} names a missing method {method_name}"
            )
        if not method_name.startswith("test"):
            raise AssertionError(
                f"{section}: {reference} names a method that is not a test "
                f"{method_name}"
            )


def cross_check(root, register):
    """Assert *register* covers every subsystem and resolves to real tests.

    Returns ``{section name: [Row, ...]}``; raises :class:`AssertionError` for a
    ``theme/`` subsystem with no section, a missing ``EXTRA_SECTIONS`` section,
    an empty section, a blank guarantee cell, a malformed table row, a data row
    that names no test, or an unresolvable test reference.
    """
    with open(register, encoding="utf-8") as handle:
        sections = parse_rows(handle.read())
    theme_dir = os.path.join(root, THEME_DIR)
    subsystems = sorted(
        name
        for name in os.listdir(theme_dir)
        if os.path.isdir(os.path.join(theme_dir, name))
    )
    for name in subsystems:
        if name not in sections:
            raise AssertionError(f"{THEME_DIR}/{name} has no section in {register}")
    for name in EXTRA_SECTIONS:
        if name not in sections:
            raise AssertionError(f"{name} has no section in {register}")
    for name, rows in sections.items():
        if not rows:
            raise AssertionError(f"section {name} in {register} has no rows")
        for row in rows:
            if not row.guarantee:
                raise AssertionError(f"section {name} in {register} has a blank guarantee")
            if not row.tests:
                raise AssertionError(
                    f"section {name} in {register} has a row with no test reference"
                )
            for reference in row.tests:
                check_reference(root, reference, name)
    return sections


class TestHelpers(unittest.TestCase):
    """Pin the register reader on a synthetic repository."""

    # The synthetic module lives only in the temp root, never in the
    # repository, so its name carries no module suffix or repository
    # directory prefix that a repository path check could try to resolve.
    MODULE = "fake_module"

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

    def test_cross_check_rejects_a_blank_guarantee(self):
        register = self._valid_register([("", f"{self.MODULE}::TestFake")])
        with self.assertRaisesRegex(AssertionError, "blank guarantee"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_test_file(self):
        register = self._valid_register(
            [("The thing holds.", "absent_module::TestFake")]
        )
        with self.assertRaisesRegex(AssertionError, "missing file"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_class(self):
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestNope")]
        )
        with self.assertRaisesRegex(AssertionError, "missing class TestNope"):
            cross_check(self.root, register)

    def test_cross_check_rejects_an_empty_qualifier(self):
        # `path::` names no class, so it pins the guarantee to no test. The
        # bare `path` form is the documented way to name the whole file, so
        # the trailing `::` is a malformed reference, not a file reference.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::")]
        )
        with self.assertRaisesRegex(AssertionError, "names no class or method"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_reference_with_a_trailing_segment(self):
        # `path::Class::method::junk` names the class and method but then a
        # fourth segment that the reference grammar has no room for; accepting
        # it would let a malformed reference pin a guarantee to a test it may
        # not actually name.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestFake::test_ok::junk")]
        )
        with self.assertRaisesRegex(AssertionError, "more than a class and method"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_missing_method(self):
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestFake::test_nope")]
        )
        with self.assertRaisesRegex(AssertionError, "missing method test_nope"):
            cross_check(self.root, register)

    def test_cross_check_rejects_a_reference_to_a_non_test_method(self):
        # `path::Class::setUp` names a method that exists but is not a test,
        # so the row pins its guarantee to a helper instead of the test that
        # enforces it. Only `test`-prefixed methods are tests unittest runs.
        register = self._valid_register(
            [("The thing holds.", f"{self.MODULE}::TestFake::setUp")]
        )
        with self.assertRaisesRegex(AssertionError, "not a test"):
            cross_check(self.root, register)


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
