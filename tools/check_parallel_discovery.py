"""Discover test modules and assign collision-safe worker logs."""

from __future__ import annotations

import fnmatch
import os

# unittest discovery loads only valid Python module filenames.
_VALID_MODULE_NAME = __import__("re").compile(r"[_a-zA-Z]\w*\.py$")


class DiscoveryError(Exception):
    """A directory of the test tree could not be listed.

    Raising instead of skipping the directory keeps the run honest: a silently
    skipped directory would hide its modules from the run and let a worker
    count that no longer matches the tree pass, while one shared unreadable
    directory must not abort coordinator startup as a bare traceback that
    names neither the directory nor the error.
    """


def discover_modules(tests_dir: str, pattern: str) -> list[str]:
    """Return the dotted module names unittest discovery would import.

    Any directory of the tree whose listing fails -- a permission error, or
    a directory removed after :func:`discover_modules` was entered -- raises
    :class:`DiscoveryError` naming the directory and the error, instead of a
    bare ``OSError`` traceback. Skipping the failed directory would silently
    drop its modules from the run.
    """
    names: list[str] = []

    def visit(directory: str, prefix: str) -> None:
        try:
            entries = sorted(os.listdir(directory))
        except OSError as exc:
            raise DiscoveryError(f"cannot list {directory}: {exc}") from exc
        for entry in entries:
            path = os.path.join(directory, entry)
            # unittest discovery does not follow package-directory symlinks;
            # following one here could import contributor-controlled code
            # from outside the selected test tree.
            if os.path.islink(path):
                continue
            if os.path.isdir(path):
                if os.path.isfile(os.path.join(path, "__init__.py")):
                    visit(path, f"{prefix}{entry}.")
            elif _VALID_MODULE_NAME.match(entry) and fnmatch.fnmatch(entry, pattern):
                names.append(f"{prefix}{entry[:-len('.py')]}")

    visit(tests_dir, "")
    return names


def _log_paths(modules: list[str], scratch: str) -> dict[str, str]:
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
