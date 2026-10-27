"""Report every import a module never uses and no other module imports from it.

The repository holds no lint dependency, so the suite carries this small
stdlib-only scanner instead: :func:`unused_imports` parses every module under
``tools/`` and ``tests/`` (skipping package ``__init__.py`` facades, whose
imports exist to re-export) with :mod:`ast` and names each imported alias that

- no ``ast.Name`` in its own module reads, and
- no ``__all__`` entry of its module re-exports, and
- no other module imports from this one, so a shared-constant re-export hub
  (``aurorae_fixtures`` hands ``INACTIVE_OUTLINE`` to the aurorae suites)
  is not flagged, and
- its import statement does not carry a ``# noqa`` comment, which marks the
  side-effect imports the suite deliberately keeps (the ``from support import
  repo_root`` sys.path bootstrap), and
- is not ``from __future__ import annotations``, which no name can read.

Each finding is one ``path:line: unused import name`` string, so the tree-clean
assertion's failure message lists every offender with its location.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SCANNED_DIRS = ("tools", "tests")


def _dotted_candidates(path: Path, root: Path) -> set[str]:
    """Return the module strings another file may import *path* as.

    A module can be reached by its repository dotted name
    (``tests.support.tmp_dir``), by the dotted name of its import root
    (``support.tmp_dir``, or ``tools.png.image``), or by its bare stem when a
    directly run tool imports a sibling.
    """
    parts = path.relative_to(root).with_suffix("").parts
    return {".".join(parts), ".".join(parts[1:]), parts[-1]}


def _alias_names(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return the module-level names *node* binds, skipping ``import *``."""
    names = []
    for alias in node.names:
        if alias.name == "*":
            continue
        if isinstance(node, ast.ImportFrom):
            names.append(alias.asname or alias.name)
        else:  # `import a.b` binds `a`; an asname replaces the whole path
            names.append(alias.asname or alias.name.split(".")[0])
    return names


def _noqa_marked(lines: list[str], node: ast.stmt) -> bool:
    """Return whether the statement's lines carry a ``# noqa`` comment."""
    span = lines[node.lineno - 1 : (node.end_lineno or node.lineno)]
    return any("noqa" in line for line in span)


def _all_entries(tree: ast.Module) -> set[str]:
    """Return every string named in a module-level ``__all__`` assignment."""
    entries: set[str] = set()
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
        if not any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in targets
        ):
            continue
        for value in ast.walk(node):
            if isinstance(value, ast.Constant) and isinstance(
                value.value, str
            ):
                entries.add(value.value)
    return entries


def unused_imports(
    root: Path, directories: tuple[str, ...] = _SCANNED_DIRS
) -> list[str]:
    """Return one finding per import no statement in its module reads.

    *root* is the repository (or synthetic-tree) root; the scan covers the
    package directories in *directories* and skips ``__pycache__`` and package
    ``__init__.py`` facades. Findings are sorted by path, then line, because
    the file walk is sorted.
    """
    files = sorted(
        path
        for directory in directories
        for path in (root / directory).rglob("*.py")
        if "__pycache__" not in path.parts and path.name != "__init__.py"
    )

    # One pass first: every (module string, name) pair any file imports, so a
    # name another module imports from this one is a re-export, not a dead one.
    imported_from: set[tuple[str, str]] = set()
    parsed: list[tuple[Path, ast.Module, list[str]]] = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        parsed.append((path, tree, source.splitlines()))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for name in _alias_names(node):
                    imported_from.add((node.module, name))

    findings: list[str] = []
    for path, tree, lines in parsed:
        candidates = _dotted_candidates(path, root)
        dunder_all = _all_entries(tree)
        read_names = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        }
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module == "__future__"
            ):
                continue
            if _noqa_marked(lines, node):
                continue
            for name in _alias_names(node):
                if name in read_names or name in dunder_all:
                    continue
                if any(
                    module in candidates and imported == name
                    for module, imported in imported_from
                ):
                    continue
                findings.append(
                    f"{path.relative_to(root)}:{node.lineno}: "
                    f"unused import {name}"
                )
    return findings
