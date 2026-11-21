"""Discover test modules and assign collision-safe worker logs."""

from __future__ import annotations

import fnmatch
import os
import re
import stat

# unittest discovery loads only valid Python module filenames.
_VALID_MODULE_NAME = re.compile(r"[_a-zA-Z]\w*\.py$")


class DiscoveryError(Exception):
    """A directory of the test tree could not be listed.

    Raising instead of skipping the directory keeps the run honest: a silently
    skipped directory would hide its modules from the run and let a worker
    count that no longer matches the tree pass, while one shared unreadable
    directory must not abort coordinator startup as a bare traceback that
    names neither the directory nor the error.
    """


def _entry_is_directory(item: os.DirEntry) -> bool | None:
    """Return whether *item* is a directory, or ``None`` when discovery skips it.

    Symlinks return ``None``: unittest discovery does not follow
    package-directory symlinks, and following one here could import
    contributor-controlled code from outside the selected test tree.
    """
    try:
        if item.is_symlink():
            return None
        return item.is_dir()
    except OSError as entry_error:
        # Unlike DirEntry predicates, the original path checks
        # suppress metadata errors (e.g. on filesystems that need
        # a stat call to determine an entry's type). Use explicit
        # stat calls so a second metadata failure cannot silently
        # omit a test module from the run.
        try:
            metadata = os.lstat(item.path)
            if stat.S_ISLNK(metadata.st_mode):
                return None
            return stat.S_ISDIR(os.stat(item.path).st_mode)
        except OSError as exc:
            raise DiscoveryError(
                f"cannot inspect {item.path}: {exc}"
            ) from entry_error


def discover_modules(tests_dir: str, pattern: str | None = None) -> list[str]:
    """Return the dotted module names unittest discovery would import.

    *pattern* narrows the result to modules whose file name matches it, as
    the unittest discovery flags do; without a pattern every valid module
    in the tree is returned, the whole-tree list the durations-cache merge
    prunes the cache's entries by.

    Any directory of the tree whose listing fails -- a permission error, or
    a directory removed after :func:`discover_modules` was entered -- raises
    :class:`DiscoveryError` naming the directory and the error, instead of a
    bare ``OSError`` traceback. Skipping the failed directory would silently
    drop its modules from the run.
    """
    names: list[str] = []

    def visit(directory: str, prefix: str) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as exc:
            raise DiscoveryError(f"cannot list {directory}: {exc}") from exc
        for item in entries:
            entry = item.name
            is_directory = _entry_is_directory(item)
            if is_directory is None:
                continue
            if is_directory:
                if os.path.isfile(os.path.join(item.path, "__init__.py")):
                    visit(item.path, f"{prefix}{entry}.")
                continue
            if (_VALID_MODULE_NAME.match(entry)
                    and (pattern is None or fnmatch.fnmatch(entry, pattern))):
                names.append(f"{prefix}{entry[:-len('.py')]}")

    visit(tests_dir, "")
    return names


def assign_log_paths(modules: list[str], scratch: str) -> dict[str, str]:
    """Map modules to unique paths, preserving natural names where possible."""
    reserved = {f"{module.replace('.', '_')}.log" for module in modules}
    names: dict[str, str] = {}
    for module in modules:
        natural = f"{module.replace('.', '_')}.log"
        if natural not in names.values():
            names[module] = natural
            continue
        suffix = 2
        while True:
            candidate = f"{natural[:-len('.log')]}_{suffix}.log"
            suffix += 1
            if candidate not in reserved:
                reserved.add(candidate)
                names[module] = candidate
                break
    return {module: os.path.join(scratch, name) for module, name in names.items()}
