"""Discover test modules and assign collision-safe worker logs."""

from __future__ import annotations

import fnmatch
import os

# unittest discovery loads only valid Python module filenames.
_VALID_MODULE_NAME = __import__("re").compile(r"[_a-zA-Z]\w*\.py$")


def discover_modules(tests_dir: str, pattern: str) -> list[str]:
    """Return the dotted module names unittest discovery would import."""
    names: list[str] = []

    def visit(directory: str, prefix: str) -> None:
        for entry in sorted(os.listdir(directory)):
            path = os.path.join(directory, entry)
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
