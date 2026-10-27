"""List the files a package directory ships, for registry-coverage checks.

Several package suites pin the exact set of files a theme package ships and
compare it against a registry of the paths their tests visit, so a file added
to the package but never registered fails. The set is derived here once
instead of each suite repeating the same ``os.walk``.
"""

from __future__ import annotations

import os

from support.repo_root import ROOT


def shipped_files(root, suffix=None, anchor=None):
    """Return the files under *root*, as paths relative to *root*.

    *suffix*, when given, keeps only filenames ending with it (``.svg``). The
    returned paths are relative so a suite can compare them against a registry
    written in package-relative form regardless of where the package lives.

    *root* and every entry under it must be a regular file or directory, not a
    symlink, and no component of *root*'s path down to *anchor* may be a
    symlink either: ``make install`` refuses a symlink in the theme package
    tree, and following a checked-in link here would list a private
    directory's names (or walk outside the package) before that refusal. The
    ancestor scan reads the path exactly as given instead of collapsing
    ``..`` lexically, so a link that a ``..`` component would hide is still
    refused. Above *anchor* -- the repository root by default, since the
    filesystem above the checkout (a symlinked TMPDIR, say) is not
    contributor-controlled -- symlinked ancestors are followed without
    complaint; pass *anchor* to bound the scan when *root* lives outside the
    repository. A symlink raises ``ValueError`` naming its path.
    """
    path = os.path.join(os.getcwd(), os.fspath(root))
    path = path.rstrip(os.sep) or os.sep
    boundary = os.path.realpath(str(ROOT) if anchor is None else str(anchor))
    while True:
        if os.path.islink(path):
            raise ValueError(
                f"{path} is a symlink; a package ships regular files, not links"
            )
        if path == boundary or not path.startswith(boundary + os.sep):
            break
        path = os.path.dirname(path)
    found = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in (*dirnames, *filenames):
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                raise ValueError(
                    f"{path} is a symlink; a package ships regular files, "
                    "not links"
                )
        for filename in filenames:
            if suffix is not None and not filename.endswith(suffix):
                continue
            found.add(os.path.relpath(os.path.join(dirpath, filename), root))
    return found
