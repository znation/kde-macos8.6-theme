"""Publish a generator's package directory: refuse, create, write each file.

``make_cursors`` and ``make_wallpaper`` both write a whole package directory
whose path a contributor could have redirected with a checked-in symlink, so
they run the same three steps: refuse a directory that resolves outside the
repository by name, create the directory, and write each (target, data) pair
atomically, reporting a failure through the shared error reporter and
returning exit status 2. Those steps and their diagnostics were word for word
the same in both generators, so they live here as the two call sites
``make_cursors.main`` and ``make_wallpaper.main``.

Like the generators, a failure partway through the writes keeps the files
already written -- each file is still published whole, so a rerun rewrites
identical bytes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

if __package__:
    from tools.atomic_write import write_bytes_atomically
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
else:  # imported while running the generator directly: python3 tools/*.py
    from atomic_write import write_bytes_atomically
    from containment import require_within_repo
    from diagnostics import report_error


def write_generated_files(
    tool: str,
    root: Path,
    directory: Path,
    files: Iterable[tuple[Path, bytes]],
    *,
    write: Callable[[Path, bytes], None] | None = None,
) -> int:
    """Refuse, create, and fill *directory* with *files*, returning the status.

    The guard is the shared containment check: a checked-in symlink in the
    tree cannot move the directory outside *root* and overwrite a like-named
    file somewhere a contributor named. *files* is the (target, data) pairs
    in write order; *write* is the function publishing one pair, by default
    the shared :func:`write_bytes_atomically`. A generator that keeps its own
    module name for these patchable -- ``make_cursors``, whose tests
    intercept a write through ``make_cursors.write_bytes_atomically`` --
    passes its own reference so the suite still sees it. Root comes from the
    caller for the same reason: a suite points the tool module's ``ROOT`` at
    a temp tree. Exit status 0 means every pair was written; 2 means the
    refusal, the creation, or a write failed and the diagnostic was printed,
    with any files before the failed one left written.
    """
    if write is None:
        write = write_bytes_atomically
    try:
        require_within_repo(directory, root, action="write")
    except ValueError as exc:
        return report_error(tool, str(exc))
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return report_error(tool, f"cannot create {directory}: {exc}")
    for target, data in files:
        try:
            write(target, data)
        except OSError as exc:
            return report_error(tool, f"cannot write {target}: {exc}")
    return 0
