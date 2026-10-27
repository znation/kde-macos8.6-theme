"""Report every import a module never uses and no other module imports from it.

The repository holds no lint dependency, so the suite carries this small
stdlib-only scanner instead: :func:`unused_imports` parses every module under
``tools/`` and ``tests/`` (skipping package ``__init__.py`` facades, whose
imports exist to re-export) with :mod:`ast` and names each imported alias that

- no ``ast.Name`` in its own module reads, and
- no ``__all__`` entry of its module re-exports, and
- no other module imports from this one, so a shared-constant re-export hub
  (``aurorae_fixtures`` hands ``INACTIVE_OUTLINE`` to the aurorae suites)
  is not flagged -- a package facade's ``__init__.py`` counts as that other
  module too: it is skipped as a scan subject, but its ``from .x import y``
  statements are resolved to ``pkg.x`` and recorded, so a submodule import
  that exists only to feed the facade is kept, and
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


def _resolved_module(package: tuple[str, ...], node: ast.ImportFrom) -> str:
    """Return the dotted module string *node* imports from, dots resolved.

    An absolute statement (``level == 0``) imports from ``node.module`` as
    written. A relative one climbs ``level - 1`` packages above the file's
    own package -- ``from .x import y`` in ``pkg/mod.py`` sources ``pkg.x``,
    ``from ..x import y`` sources ``x`` -- and a package ``__init__.py``
    sits in its package, so the directory holding the file is the package
    either way and one formula serves both.
    """
    if node.level == 0:
        return node.module or ""
    base = package[: len(package) - (node.level - 1)]
    parts = list(base)
    if node.module:
        parts += node.module.split(".")
    return ".".join(parts)


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


def _scan_module(
    tree: ast.Module,
) -> tuple[list[tuple[ast.stmt, list[str]]], set[str], set[str]]:
    """Collect in one walk what the scan needs from a module.

    Returns the import statements each with the names it binds, every
    ``ast.Name`` the module reads, and every string named in an ``__all__``
    assignment or in a call that grows ``__all__`` (``append``, ``extend``,
    ``insert``). One walk gathers all three; re-walking the tree once per
    need costs several times the parse itself on the real tree.
    """
    imports: list[tuple[ast.stmt, list[str]]] = []
    read_names: set[str] = set()
    entries: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append((node, _alias_names(node)))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            # Only a Load context reads the name. A re-assignment (`os =
            # None`, a loop or walrus target) is a write, not a read, so
            # counting it would hide a genuinely dead import; a `del` then
            # flags aloud rather than being taken as a use.
            read_names.add(node.id)
        else:
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AugAssign):
                targets = [node.target]
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = [node.target]
            # The call form `__all__.extend(["os"])` (and its append and
            # insert siblings) adds entries exactly like an assignment, so
            # a re-export hub that grows `__all__` by method call keeps the
            # names it adds. A call that only shrinks or reorders (`remove`,
            # `sort`) adds nothing and is no allowance.
            grows_all = (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("append", "extend", "insert")
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "__all__"
            )
            if not grows_all and not any(
                isinstance(t, ast.Name) and t.id == "__all__"
                for t in targets
            ):
                continue
            for value in ast.walk(node):
                if isinstance(value, ast.Constant) and isinstance(
                    value.value, str
                ):
                    entries.add(value.value)
    return imports, read_names, entries


def unused_imports(
    root: Path, directories: tuple[str, ...] = _SCANNED_DIRS
) -> list[str]:
    """Return one finding per import no statement in its module reads.

    *root* is the repository (or synthetic-tree) root; the scan covers the
    package directories in *directories*, skipping ``__pycache__`` and
    treating package ``__init__.py`` facades as re-export sources only --
    their imports are never flagged but do register what they re-export.
    Findings are sorted by path, then line, because
    the file walk is sorted.
    """
    files = sorted(
        path
        for directory in directories
        for path in (root / directory).rglob("*.py")
        if "__pycache__" not in path.parts
    )

    # One walk per module: the collected record carries the import
    # statements with their bound names, the read names and the ``__all__``
    # entries, and folding every (module string, name) pair any file imports
    # into ``imported_from`` here keeps a name another module imports from
    # this one a re-export, not a dead one. The package facades --
    # ``__init__.py`` files -- are skipped as scan subjects but still
    # register their ``from .x import y`` statements (resolved to the
    # submodule's dotted name), because a facade re-export is exactly the
    # import-from-elsewhere that keeps a submodule's own import alive.
    imported_from: set[tuple[str, str]] = set()
    scanned: list[
        tuple[Path, list[tuple[ast.stmt, list[str]]], list[str], set[str], set[str]]
    ] = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        imports, read_names, dunder_all = _scan_module(tree)
        package = path.relative_to(root).with_suffix("").parts[:-1]
        for node, names in imports:
            if not isinstance(node, ast.ImportFrom):
                continue
            resolved = _resolved_module(package, node)
            for alias in node.names:
                # Record the name as this file imported it (never the
                # ``as`` alias a consuming module rebinds it to), so an
                # aliased re-export keeps the source module's own import
                # without masking a dead one under another name.
                if alias.name == "*":
                    continue
                imported_from.add((resolved, alias.name))
        if path.name != "__init__.py":
            scanned.append(
                (path, imports, source.splitlines(), read_names, dunder_all)
            )

    findings: list[tuple[str, int, str]] = []
    for path, imports, lines, read_names, dunder_all in scanned:
        relative = str(path.relative_to(root))
        candidates = _dotted_candidates(path, root)
        for node, names in imports:
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module == "__future__"
            ):
                continue
            if _noqa_marked(lines, node):
                continue
            for name in names:
                if name in read_names or name in dunder_all:
                    continue
                if any(
                    module in candidates and imported == name
                    for module, imported in imported_from
                ):
                    continue
                findings.append((relative, node.lineno, name))
    # ast.walk collects a module's imports breadth-first, so a nested or
    # block-nested import would trail its later top-level imports; sort by
    # path, then line, then name to keep the promise the docstring states.
    return [
        f"{found_path}:{line}: unused import {name}"
        for found_path, line, name in sorted(findings)
    ]
