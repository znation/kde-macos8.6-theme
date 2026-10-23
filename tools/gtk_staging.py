"""Stage GTK config writes and commit them together.

A GTK selection touches two settings files and a user stylesheet. Staging
every write first means an unwritable later file leaves every earlier file
unmodified; :func:`commit` then renames the staged files into place.
"""

from __future__ import annotations

import os
from pathlib import Path

if __package__:
    from tools.atomic_write import write_atomically
else:  # run directly from tools/
    from atomic_write import write_atomically


class ConfigError(Exception):
    """A GTK settings or user-CSS file could not be read or written.

    The message names the offending path and the underlying error, so
    ``main`` can report it as the one-line diagnostic instead of letting a
    bare ``OSError`` or ``UnicodeDecodeError`` traceback escape. A decoder's
    own error names the byte that failed but not the file it came from.
    """


def discard(staging: Path) -> None:
    """Remove a staging file, ignoring a path that never became one."""
    try:
        staging.unlink()
    except OSError:
        pass


def _stage(path: Path, text: str) -> Path:
    """Write *text* to a ``.staging`` sibling and return its path."""
    staging = path.with_name(f".{path.name}.staging")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            raise ConfigError(f"cannot write {path}: is a directory")
        write_atomically(
            staging, lambda destination: destination.write(text.encode("utf-8"))
        )
    except OSError as exc:
        discard(staging)
        raise ConfigError(f"cannot write {path}: {exc}") from exc
    return staging


def stage_all(writes: list[tuple[Path, str]]) -> list[tuple[Path, Path]]:
    """Stage every ``(path, text)`` write, discarding all on a failure."""
    staged = []
    try:
        for path, text in writes:
            staged.append((path, _stage(path, text)))
    except ConfigError:
        for _, staging in staged:
            discard(staging)
        raise
    return staged


def commit(staged: list[tuple[Path, Path]]) -> None:
    """Rename each staged file over its target, discarding leftovers."""
    try:
        for path, staging in staged:
            try:
                os.replace(staging, path)
            except OSError as exc:
                raise ConfigError(f"cannot write {path}: {exc}") from exc
    finally:
        for _, staging in staged:
            discard(staging)
