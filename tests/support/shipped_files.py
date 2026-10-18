"""List the files a package directory ships, for registry-coverage checks.

Several package suites pin the exact set of files a theme package ships and
compare it against a registry of the paths their tests visit, so a file added
to the package but never registered fails. The set is derived here once
instead of each suite repeating the same ``os.walk``.
"""

from __future__ import annotations

import os


def shipped_files(root, suffix=None):
    """Return the files under *root*, as paths relative to *root*.

    *suffix*, when given, keeps only filenames ending with it (``.svg``). The
    returned paths are relative so a suite can compare them against a registry
    written in package-relative form regardless of where the package lives.
    """
    found = set()
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if suffix is not None and not filename.endswith(suffix):
                continue
            found.add(os.path.relpath(os.path.join(dirpath, filename), root))
    return found
