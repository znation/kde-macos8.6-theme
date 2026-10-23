"""Containment guard for reads of contributor-supplied repository files.

The theme, reference and package files under the repository are
contributor-supplied, and a checked-in symlink can point anywhere on the
machine. A reader that opens such a path can read a private file and, when its
error message echoes the file's lines (``configparser`` does), hand that
content to a failing test's diagnostic.

This is the one implementation of the guard. The ``tools/`` scripts and the
test suite both import it -- tests reach it as ``tools.containment`` with the
repository root on ``sys.path`` -- so a refinement here reaches every reader
instead of the private copies the guard used to be reimplemented in.

:func:`require_within_repo` resolves the path and refuses one that is lexically
inside the repository but lands outside it; a path that is not inside the
repository at all -- a test's temporary file, or the user's own configuration
such as the ``kcminputrc`` the cursor selection inspects -- skips that check.
Every read still passes the regular-file and size guards below.
"""

from __future__ import annotations

import io
import os
import stat
from pathlib import Path
from typing import BinaryIO


def resolves_within(directory: str | Path, path: str | Path) -> bool:
    """Return True when *path* resolves to a location inside *directory*.

    A resolution that fails is not assumed to be contained: an ``OSError`` (a
    filesystem failure), a ``RuntimeError`` (the symlink loop ``Path.resolve()``
    raised before Python 3.13) and a ``ValueError`` (an embedded NUL byte, which
    POSIX ``Path.resolve()`` rejects) all make this return False, so the caller
    refuses the path instead of the exception aborting the read.
    """
    try:
        resolved = Path(path).resolve()
        base = Path(directory).resolve()
    except (OSError, RuntimeError, ValueError):
        return False
    return resolved.is_relative_to(base)


def _absolute_lexical(path: str | Path) -> str:
    """Return *path*'s absolute form with one POSIX double-slash spelling normalized.

    POSIX permits a path to start with exactly two slashes, and
    ``os.path.abspath`` preserves that spelling (``//tmp/repo``). On POSIX
    systems those two slashes name the same root as one, so comparing both
    spellings literally would make an equivalent root look different and skip
    the symlink check. Windows treats ``//server/share`` as a UNC path, so only
    a POSIX path is collapsed here.
    """
    absolute = os.path.abspath(path)
    if (
        os.name == "posix"
        and absolute.startswith("//")
        and not absolute.startswith("///")
    ):
        return "/" + absolute.lstrip("/")
    return absolute


def is_within(directory: str | Path, path: str | Path) -> bool:
    """Return True when *path* is lexically inside *directory* (symlinks unresolved)."""
    base = _absolute_lexical(directory)
    absolute = _absolute_lexical(path)
    # A root already ends with the separator; appending another would make
    # ``//`` and reject every real child (and skip the symlink check).
    boundary = base.rstrip(os.sep) + os.sep
    return absolute == base or absolute.startswith(boundary)


def require_within_repo(
    path: str | Path, root: str | Path, action: str = "read"
) -> None:
    """Raise ``ValueError`` when a repository *path* resolves outside *root*.

    Only a *path* lexically inside *root* is checked, so a reader that is also
    handed a path outside the repository -- a test's temporary file, or the
    user's ``kcminputrc`` -- is unaffected. A checked-in symlink at a
    repository path resolves elsewhere and is refused with the path named.
    *action* names the operation the caller was about to perform -- ``"read"``
    or ``"write"`` -- so the diagnostic says which one the escape would have
    reached.
    """
    if not is_within(root, path):
        return
    if not resolves_within(root, path):
        raise ValueError(
            f"{path} resolves outside {root} (a symlink escape); "
            f"refusing to {action} it"
        )


def open_regular_binary(path: str | Path) -> BinaryIO:
    """Open *path* for binary reading, refusing a non-regular file.

    ``open()`` on a FIFO blocks until a writer appears and a device can stream
    without end, so a reader with no timeout would hang the run. Opening with
    ``O_NONBLOCK`` lets a FIFO be examined without waiting, and ``fstat`` on
    that same descriptor rejects it by name; ``fstat`` on the descriptor rather
    than a separate ``stat`` of the path also means a regular file swapped for
    a FIFO between the check and the open cannot slip through. ``O_NONBLOCK``
    has no effect on a regular file. The caller closes the returned handle.
    """
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError(
                f"{path} cannot be read: not a regular file; refusing to open it"
            )
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise


# The files a checker reads through here are source files, SVGs and registers,
# tens of kilobytes at most. The path is contributor-supplied and can name
# something arbitrarily large -- a stray multi-gigabyte file, or a Git LFS
# object whose pointer was never replaced -- and a plain ``handle.read()``
# would try to allocate the whole file. A ``MemoryError`` is not an ``OSError``
# and would abort the checker with a traceback naming neither the file nor the
# guard, so bound the read and refuse an oversize file by name instead.
_MAX_READ_BYTES = 1 << 20


def _read_bounded(handle: BinaryIO, path: str | Path) -> bytes:
    """Return at most ``_MAX_READ_BYTES`` from *handle*, refusing a longer file.

    One byte past the cap is read, so a file exactly at the limit is accepted
    while a longer one is refused without loading the rest of it.
    """
    data = handle.read(_MAX_READ_BYTES + 1)
    if len(data) > _MAX_READ_BYTES:
        raise ValueError(
            f"{path} is larger than the {_MAX_READ_BYTES}-byte limit this "
            "guard reads; refusing to load it whole"
        )
    return data


def read_bytes(path: str | Path, root: str | Path) -> bytes:
    """Return the bytes of *path*, refusing a symlink escape inside *root*.

    A contributor-supplied file that a test compares with a second copy is
    read through here: the comparison echoes both byte strings when they
    differ, so a checked-in symlink at *path* that resolves outside *root*
    must be refused before it is opened rather than leaking a private file's
    bytes into the diagnostic. A file larger than ``_MAX_READ_BYTES`` is
    refused with a ``ValueError`` naming *path* instead of being loaded whole,
    which could raise an uncaught ``MemoryError``. A FIFO or device is refused
    by name rather than opened, since it would block or stream forever. A
    *path* outside *root* is not a repository file, so the containment check
    does not apply and it is read as given.
    """
    require_within_repo(path, root)
    with open_regular_binary(path) as handle:
        return _read_bounded(handle, path)


def read_text(
    path: str | Path, root: str | Path, encoding: str = "utf-8"
) -> str:
    """Return the text of *path*, refusing a symlink escape inside *root*.

    A contributor-supplied file whose lines a test feeds to an assertion that
    echoes them (``assertIn``, ``assertRegex``) is read through here: a
    checked-in symlink at *path* that resolves outside *root* must be refused
    before it is opened rather than leaking a private file's text into the
    diagnostic. A file larger than ``_MAX_READ_BYTES`` is refused with a
    ``ValueError`` naming *path* instead of being loaded whole, which could
    raise an uncaught ``MemoryError``. A FIFO or device is refused by name
    rather than opened, since it would block or stream forever. A *path*
    outside *root* is not a repository file, so the containment check does
    not apply and it is read as given.
    """
    require_within_repo(path, root)
    with open_regular_binary(path) as handle:
        data = _read_bounded(handle, path)
    # Decode through the text layer so the result matches ``open(path,
    # encoding=encoding)``: universal-newline translation and the UTF-8 BOM
    # ``utf-8-sig`` strips, neither of which a bare ``bytes.decode`` does.
    with io.TextIOWrapper(io.BytesIO(data), encoding=encoding) as stream:
        return stream.read()
