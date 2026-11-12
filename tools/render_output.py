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
    from tools.containment import open_regular_binary
    from tools.diagnostics import require_path
else:  # imported from a directly run tool
    from atomic_write import write_atomically
    from containment import open_regular_binary
    from diagnostics import require_path


def output_problem(output: Path) -> str | None:
    """Return why *output* cannot be written, or None when it looks writable."""
    require_path("output_problem", "output", output)
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
    require_path("publish", "source", source)
    require_path("publish", "output", output)
    def copy_into(destination):
        with open_regular_binary(source) as origin:
            shutil.copyfileobj(origin, destination)

    write_atomically(output, copy_into, prefix=".render-")
