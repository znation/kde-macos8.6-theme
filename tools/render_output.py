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
import tempfile
from pathlib import Path


def output_problem(output: Path) -> str | None:
    """Return why *output* cannot be written, or None when it looks writable."""
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
    descriptor, partial_name = tempfile.mkstemp(
        dir=output.parent, prefix=".render-", suffix=".tmp"
    )
    partial = Path(partial_name)
    descriptor_closed = False
    try:
        with os.fdopen(descriptor, "wb") as destination:
            descriptor_closed = True
            # mkstemp opens the file 0600; the plain copy this replaces
            # created it with the process umask applied, so restore that mode
            # and leave the output's permissions unchanged.
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(destination.fileno(), 0o666 & ~umask)
            with source.open("rb") as origin:
                shutil.copyfileobj(origin, destination)
        os.replace(partial, output)
    except BaseException:
        if not descriptor_closed:
            os.close(descriptor)
        partial.unlink(missing_ok=True)
        raise
