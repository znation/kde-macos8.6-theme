"""Write a file through an exclusive temporary sibling and an atomic rename.

Several tools publish a file that must never be left half-written: a config
file Plasma reads, a wallpaper ``make install`` ships, a rendered screenshot, or
a git hook. Each writes the new bytes to a fresh temporary file in the target's
directory, gives it the intended mode, and renames it over the target, so a
crash leaves either the previous file or the whole new one.

The temporary name is picked by :func:`tempfile.mkstemp`, which creates the file
exclusively: a fixed, guessable name would let another local user who can write
the directory park a symlink there first and make the write clobber whatever
file it names. The bytes go through the descriptor ``mkstemp`` returned rather
than the path being reopened by name, so a path swapped after the exclusive
create cannot redirect them.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO


def write_bytes_atomically(path: Path, data: bytes) -> None:
    """Write *data* to *path* through :func:`write_atomically`.

    Use this when the whole new contents are already in memory as bytes;
    it fills the temporary sibling with one ``write`` call.
    """
    write_atomically(path, lambda destination: destination.write(data))


def write_atomically(
    path: Path,
    fill: Callable[[BinaryIO], None],
    *,
    prefix: str | None = None,
    mode: int | None = None,
) -> None:
    """Write *path* by filling a temporary sibling and renaming it into place.

    *fill* receives the binary file object for the temporary file and writes
    the new contents. When *mode* is given the file gets exactly that mode;
    otherwise it gets the mode a plain ``open(..., "wb")`` would create under
    the process umask. *prefix* sets the temporary file's name prefix
    (``.<path.name>-`` by default). The temporary file is removed when the
    write fails.
    """
    if mode is None:
        previous_umask = os.umask(0)
        os.umask(previous_umask)
        mode = 0o666 & ~previous_umask
    descriptor, partial_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=prefix if prefix is not None else f".{path.name}-",
        suffix=".tmp",
    )
    partial = Path(partial_name)
    descriptor_closed = False
    try:
        # ``mkstemp`` opens the file 0600; set the intended mode on the
        # descriptor before wrapping it, so a path swapped after the exclusive
        # create cannot redirect the chmod either.
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as destination:
            descriptor_closed = True
            fill(destination)
        os.replace(partial, path)
    except BaseException:
        if not descriptor_closed:
            os.close(descriptor)
        partial.unlink(missing_ok=True)
        raise
