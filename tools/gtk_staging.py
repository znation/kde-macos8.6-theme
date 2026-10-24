"""Stage GTK config writes and commit them together.

A GTK selection touches two settings files and a user stylesheet. Staging
every write first means an unwritable later file leaves every earlier file
unmodified; :func:`commit` then replaces the staged files and removes the
user stylesheet as one transaction, restoring every target if a later step
fails.
"""

from __future__ import annotations

import os
import secrets
from collections.abc import Iterable
from pathlib import Path

if __package__:
    from tools.atomic_write import write_atomically
    from tools.gtk_user_files import ConfigError
else:  # imported from a directly run tool
    from atomic_write import write_atomically
    from gtk_user_files import ConfigError


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


def _backup(path: Path) -> Path | None:
    """Hard-link *path* to an unused ``.backup`` sibling, or return None.

    The sibling name carries a random token, so a file the user already keeps
    at ``.gtk.css.backup`` (or any other name) is never removed or
    overwritten. A hard link keeps the previous inode reachable without a
    moment when the target is missing, so a process killed during the commit
    still leaves the old settings file in place. A target that became a
    directory is refused rather than linked, so the commit reports it instead
    of replacing it.
    """
    if path.is_dir():
        raise IsADirectoryError(f"is a directory: {path}")
    for _ in range(10):
        backup = path.with_name(
            f".{path.name}.{secrets.token_hex(8)}.backup"
        )
        try:
            os.link(path, backup, follow_symlinks=False)
        except FileExistsError:
            continue
        except FileNotFoundError:
            return None
        return backup
    raise OSError(f"cannot name a backup for {path}")


def _same_file(left: Path, right: Path) -> bool:
    """Return whether *left* and *right* name the same inode."""
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def _restore(path: Path, backup: Path | None) -> None:
    """Put *backup* back at *path*, or remove a file the commit created."""
    if backup is None:
        path.unlink(missing_ok=True)
    elif _same_file(path, backup):
        # The target was not changed before the failure, so *backup* is a
        # second hard link to it. os.replace() between two links to the same
        # inode does nothing, leaving the backup sibling behind; dropping the
        # extra link restores the target and cleans the directory.
        backup.unlink()
    else:
        os.replace(backup, path)


def _rollback(applied: list[tuple[Path, Path | None]]) -> None:
    """Restore every changed target, newest first, reporting failures."""
    failures = []
    for path, backup in reversed(applied):
        try:
            _restore(path, backup)
        except OSError as exc:
            failures.append(f"cannot restore {path}: {exc}")
    if failures:
        raise ConfigError("; ".join(failures))


def commit(
    staged: list[tuple[Path, Path]], removals: Iterable[Path] = ()
) -> None:
    """Replace every staged file and delete every removal as a transaction.

    Each target is linked to a uniquely named ``.backup`` sibling before its
    staged file takes its place or its removal deletes it. If any step fails,
    every target changed so far is restored from its backup and a path that did not
    exist before is removed again, so a failure on the second settings file
    cannot leave the first one rewritten or the user CSS already deleted.
    Backups and leftover staging files are removed when the commit succeeds.
    """
    applied: list[tuple[Path, Path | None]] = []
    try:
        for path, staging in staged:
            try:
                backup = _backup(path)
            except OSError as exc:
                raise ConfigError(f"cannot write {path}: {exc}") from exc
            applied.append((path, backup))
            try:
                os.replace(staging, path)
            except OSError as exc:
                raise ConfigError(f"cannot write {path}: {exc}") from exc
        for path in removals:
            try:
                backup = _backup(path)
            except OSError as exc:
                raise ConfigError(f"cannot remove {path}: {exc}") from exc
            if backup is None:
                continue
            applied.append((path, backup))
            try:
                path.unlink()
            except OSError as exc:
                raise ConfigError(f"cannot remove {path}: {exc}") from exc
    except BaseException as exc:
        try:
            _rollback(applied)
        except ConfigError as rollback_error:
            raise ConfigError(f"{exc}; {rollback_error}") from exc
        raise
    else:
        for _, backup in applied:
            if backup is not None:
                discard(backup)
    finally:
        for _, staging in staged:
            discard(staging)
