"""Containment guard for reads of contributor-supplied repository files.

The theme, reference and package files under the repository are
contributor-supplied, and a checked-in symlink can point anywhere on the
machine. A reader that opens such a path can read a private file and, when its
error message echoes the file's lines (``configparser`` does), hand that
content to a failing test's diagnostic. :func:`require_within_repo` resolves
the path and refuses one that is lexically inside the repository but lands
outside it; a path that is not inside the repository at all (a test's
temporary file) is left alone.
"""

from __future__ import annotations

import os


def _resolves_within(directory, path):
    """Return True when *path* resolves to a location inside *directory*.

    A resolution that fails is not assumed to be contained: an ``OSError`` (a
    filesystem failure, a symlink loop) and a ``RuntimeError`` (the loop
    ``Path.resolve`` raised before Python 3.13) both make this return False, so
    the caller refuses the path instead of the exception aborting the read.
    """
    try:
        resolved = os.path.realpath(path)
        base = os.path.realpath(directory)
    except (OSError, RuntimeError):
        return False
    return resolved == base or resolved.startswith(base + os.sep)


def _is_within(directory, path):
    """Return True when *path* is lexically inside *directory* (symlinks unresolved)."""
    base = os.path.abspath(directory)
    absolute = os.path.abspath(path)
    return absolute == base or absolute.startswith(base + os.sep)


def require_within_repo(path, root):
    """Raise ``ValueError`` when a repository *path* resolves outside *root*.

    Only a *path* lexically inside *root* is checked, so a reader that is also
    handed a test's temporary file is unaffected. A checked-in symlink at a
    repository path resolves elsewhere and is refused with the path named.
    """
    if not _is_within(root, path):
        return
    if not _resolves_within(root, path):
        raise ValueError(
            f"{path} resolves outside {root} (a symlink escape); "
            "refusing to read it"
        )


def read_bytes(path, root):
    """Return the bytes of repository *path*, refusing a symlink escape.

    A contributor-supplied file that a test compares with a second copy is
    read through here: the comparison echoes both byte strings when they
    differ, so a checked-in symlink at *path* that resolves outside *root*
    must be refused before it is opened rather than leaking a private file's
    bytes into the diagnostic. A *path* outside *root* (a test's temporary
    file) is read as before.
    """
    require_within_repo(path, root)
    with open(path, "rb") as handle:
        return handle.read()
