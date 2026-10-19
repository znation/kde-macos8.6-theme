"""Parse and cross-check ``docs/invariants.md`` against the repository.

The register states, per ``theme/`` subsystem and for the fidelity gate, the
guarantee a surface must keep and the test that pins it, so a future bug is
confirmable without reconstructing the intent from the test's body. Nothing
otherwise ties the register to the repository: this module parses its sections
and table rows and fails when a ``theme/`` subsystem directory has no section,
when a section names no ``theme/`` subsystem or registered extra section, when
a section heading repeats an earlier one, when a row names a test file, class or
method that does not exist, when a row names a method that is not a test, when a
row names a file that defines no test case, when a row names no test, or when a
guarantee or provenance-exception cell is blank.

``tests/test_invariants.py`` drives these checks.
"""

from __future__ import annotations

import ast
import os
import re
from collections import namedtuple

from support.repo_root import ROOT

REGISTER = os.path.join(ROOT, "docs", "invariants.md")
THEME_DIR = "theme"
# Sections that are not ``theme/`` subsystem directories but still belong in
# the register: the render/fidelity tooling lives under ``tooling``.
EXTRA_SECTIONS = ("tooling",)

# The reference and row boundaries :func:`cross_check` must reject. Each name
# is also a rejection mutation in ``tests/support/checker_mutations.py``, so a
# boundary the shipped register never crosses is still driven by data; the
# guard in ``tests/test_checker_mutations.py`` fails when a name here has no
# mutation (or a mutation names a boundary that is not here).
REJECTION_SHAPES = (
    "malformed-row",
    "test-cell-without-reference",
    "reference-outside-repository",
    "reference-to-non-test-case-class",
    "method-on-non-test-case-class",
    "non-test-method",
    "trailing-segment",
    "empty-qualifier",
    "local-base-that-only-looks-like-a-test-case",
    "reference-with-nul-byte",
    "unreadable-test-file",
)

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
    malformed row cannot be dropped silently. A section heading that repeats a
    name already seen raises too: two ``## aurorae`` headings would otherwise
    merge into one section, attributing both tables' guarantees to the same
    surface with no error.
    """
    sections = {}
    current = None
    for line in text.splitlines():
        match = SECTION.match(line)
        if match:
            current = match.group("name")
            if current in sections:
                raise AssertionError(
                    f"duplicate section {current} in the register"
                )
            sections[current] = []
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
    """Return ``{class name: (method names, is a test case)}`` at *path*'s top level.

    A class is a test case when it names ``unittest.TestCase``, when it
    reaches one through a base class defined in the same module, or when it
    names a ``*TestCase`` base the module does not define (an imported base
    whose own bases cannot be inspected here). A class unittest never collects
    is not a test case however many ``test``-prefixed methods it defines, so
    the check follows bases rather than trusting a test-shaped method name.
    """
    with open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    nodes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }

    def base_names(node):
        names = []
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                names.append(base.attr)
            elif isinstance(base, ast.Name):
                names.append(base.id)
        return names

    def is_test_case(name, seen):
        if name in seen:
            return False
        seen.add(name)
        for base in base_names(nodes[name]):
            if base in nodes:
                if is_test_case(base, seen):
                    return True
            elif base == "TestCase" or base.endswith("TestCase"):
                return True
        return False

    classes = {}
    for name, node in nodes.items():
        methods = {
            child.name
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        classes[name] = (methods, is_test_case(name, set()))
    return classes


def _parse_test_module(section, reference, file_path):
    """Return ``_defined_names(file_path)``, or raise a register ``AssertionError``.

    A referenced file that cannot be decoded or parsed (a stray byte, a
    syntax error) would otherwise escape as a `UnicodeDecodeError` or
    `SyntaxError` naming neither the section nor the reference. Report it as
    the register's own `AssertionError` so the failing row is identifiable.
    """
    try:
        return _defined_names(file_path)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise AssertionError(
            f"{section}: {reference} names a file that cannot be read as "
            f"Python: {exc}"
        ) from exc


def check_reference(root, reference, section):
    """Assert *reference* names an existing test in *root*.

    A reference is ``path``, ``path::Class`` or ``path::Class::method``; raises
    :class:`AssertionError` naming *section* and the first missing piece. A
    reference ending in ``::`` names no class and a reference with a fourth
    ``::`` segment is rejected too, so neither can silently pin a guarantee to
    no test. A named method must be a test (a ``test``-prefixed name, the only
    kind unittest runs), so a helper cannot stand in for the test that pins the
    guarantee. A named class must be a ``TestCase`` (directly or through a
    base defined in the same module), so a helper class unittest never
    collects cannot stand in for the tests that pin the guarantee. A bare
    ``path`` must define at least one test case, so a file that holds only
    helpers cannot stand in for the tests that pin the guarantee. The path
    must stay inside *root*: an absolute path replaces the root and a ``..``
    segment climbs out of it, so either would let a row pin a guarantee to a
    test outside the tree the register covers. A referenced file that cannot
    be decoded or parsed is rejected by name too, so a broken reference never
    escapes as an unrelated exception. A path carrying a NUL byte is rejected
    by name as well, before it reaches :func:`os.path.realpath`, which would
    raise a bare ``ValueError`` naming neither the section nor the reference.
    """
    path, sep, qualifier = reference.partition("::")
    if "\x00" in path:
        raise AssertionError(
            f"{section}: {reference} names a path containing a NUL byte"
        )
    file_path = os.path.join(root, path)
    root_path = os.path.realpath(root)
    resolved = os.path.realpath(file_path)
    if resolved != root_path and not resolved.startswith(root_path + os.sep):
        raise AssertionError(
            f"{section}: {reference} names a path outside the repository"
        )
    if not os.path.isfile(file_path):
        raise AssertionError(f"{section}: {reference} names a missing file")
    if not qualifier:
        if sep:
            raise AssertionError(
                f"{section}: {reference} names no class or method after '::'"
            )
        classes = _parse_test_module(section, reference, file_path)
        if not any(test_case for _, test_case in classes.values()):
            # The bare ``path`` form names the whole file, so it pins the
            # guarantee to that file's tests. A file with no test case at all
            # pins nothing, and accepting it would leave the guarantee
            # unchecked while the register reads as if it were covered.
            raise AssertionError(
                f"{section}: {reference} names a file that defines no test case"
            )
        return
    names = qualifier.split("::")
    if len(names) > 2:
        raise AssertionError(
            f"{section}: {reference} names more than a class and method"
        )
    classes = _parse_test_module(section, reference, file_path)
    class_name = names[0]
    if class_name not in classes:
        raise AssertionError(f"{section}: {reference} names a missing class {class_name}")
    methods, test_case = classes[class_name]
    if not test_case:
        raise AssertionError(
            f"{section}: {reference} names a class that is not a test case "
            f"{class_name}"
        )
    if len(names) > 1:
        method_name = names[1]
        if method_name not in methods:
            raise AssertionError(
                f"{section}: {reference} names a missing method {method_name}"
            )
        if not method_name.startswith("test"):
            raise AssertionError(
                f"{section}: {reference} names a method that is not a test "
                f"{method_name}"
            )


def _theme_subsystems(theme_dir):
    """Return the sorted subsystem names under *theme_dir*.

    The register is cross-checked against the repository's ``theme/``
    directory, so a missing or unreadable one -- a fresh checkout mid-setup, a
    rename, a permission error -- would otherwise escape as a bare ``OSError``
    naming neither the checker nor the directory. ``os.path.isdir`` swallows
    its own ``OSError`` (an entry that cannot be stat'd is not a directory),
    so only the listing needs the guard.
    """
    try:
        names = os.listdir(theme_dir)
    except OSError as exc:
        raise AssertionError(f"{theme_dir} cannot be listed: {exc}") from exc
    return sorted(
        name
        for name in names
        if os.path.isdir(os.path.join(theme_dir, name))
    )


def cross_check(root, register):
    """Assert *register* covers every subsystem and resolves to real tests.

    Returns ``{section name: [Row, ...]}``; raises :class:`AssertionError` for a
    register that cannot be read or is not valid UTF-8 text, a ``theme/``
    directory that cannot be listed, a ``theme/`` subsystem with no section, a
    missing ``EXTRA_SECTIONS`` section, a section that names neither a
    ``theme/`` subsystem nor an ``EXTRA_SECTIONS`` entry, a repeated section
    heading, an empty section, a blank guarantee or provenance-exception cell, a
    malformed table row, a data row that names no test, a bare file reference to
    a file that defines no test case, or an unresolvable test reference.
    """
    try:
        with open(register, encoding="utf-8") as handle:
            text = handle.read()
    except UnicodeDecodeError as exc:
        raise AssertionError(
            f"{register} is not valid UTF-8 text: {exc}"
        ) from exc
    except OSError as exc:
        raise AssertionError(f"{register} cannot be read: {exc}") from exc
    sections = parse_rows(text)
    theme_dir = os.path.join(root, THEME_DIR)
    subsystems = _theme_subsystems(theme_dir)
    for name in subsystems:
        if name not in sections:
            raise AssertionError(f"{THEME_DIR}/{name} has no section in {register}")
    for name in EXTRA_SECTIONS:
        if name not in sections:
            raise AssertionError(f"{name} has no section in {register}")
    known = set(subsystems) | set(EXTRA_SECTIONS)
    for name in sections:
        if name not in known:
            # A section for a surface that is not there -- a stale heading left
            # after a directory rename, or a typo -- reads as a pinned guarantee
            # while nothing enforces it. Reject it by name instead of letting the
            # register overstate what it covers.
            raise AssertionError(
                f"section {name} in {register} names no {THEME_DIR}/ subsystem "
                "or registered extra section"
            )
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
            if not row.provenance:
                # The third column records the provenance exception or the
                # literal "none"; a blank cell reads as an exception that was
                # never written down, so reject it by name instead of letting
                # the row claim a guarantee while saying nothing about where
                # its value came from.
                raise AssertionError(
                    f"section {name} in {register} has a blank provenance exception"
                )
            for reference in row.tests:
                check_reference(root, reference, name)
    return sections
