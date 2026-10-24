"""Publish the rendered surface to the caller's output path safely.

The renderer writes a screenshot to a path the caller names. That write must
leave *output* as either the old file or the whole new one -- never a partial
one -- and must not follow a symlink another local user planted at a guessable
temporary name. :func:`output_problem` is the pre-flight check the CLI runs
before it starts a render session; :func:`publish` is the atomic copy the
session's capture is committed through.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

if __package__:
    from tools.atomic_write import write_atomically
else:  # imported from a directly run tool
    from atomic_write import write_atomically


def output_problem(output: Path) -> str | None:
    """Return why *output* cannot be written, or None when it looks writable."""
    if not isinstance(output, Path):
        raise ValueError(
            f"output_problem() requires a pathlib.Path: output must be Path, "
            f"not {type(output).__name__}"
        )
    if output.is_dir():
        return "is a directory"
    if not output.parent.is_dir():
        return "its directory does not exist"
    if not os.access(output.parent, os.W_OK | os.X_OK):
        return "its directory is not writable"
    return None


def publish(source: Path, output: Path) -> None:
    """Copy *source* to *output* so *output* is either the old file or the whole new one.

    The bytes go to a fresh temporary file whose name the OS picks in
    *output*'s directory, then that file is renamed over *output*. A fixed,
    guessable name would let another local user who can write the directory
    park a symlink there first and make the copy overwrite whatever file it
    names.
    """
    if not isinstance(source, Path):
        raise ValueError(
            f"publish() requires pathlib.Path: source must be Path, "
            f"not {type(source).__name__}"
        )
    if not isinstance(output, Path):
        raise ValueError(
            f"publish() requires pathlib.Path: output must be Path, "
            f"not {type(output).__name__}"
        )
    def copy_into(destination):
        with source.open("rb") as origin:
            shutil.copyfileobj(origin, destination)

    write_atomically(output, copy_into, prefix=".render-")
