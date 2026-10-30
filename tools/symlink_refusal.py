"""Refuse to replace or delete a user-owned file reached through a symlink."""

from __future__ import annotations

from pathlib import Path


def refuse_symlink(path: Path, action: str, error: type[Exception]) -> None:
    """Raise *error* when *path* is a symbolic link; otherwise do nothing.

    A dotfile manager commonly makes a configuration file a symlink to a file
    it manages. Replacing or deleting that link would silently detach the
    config path from the file the user meant to edit, so *path* is refused by
    name before anything is staged; the link and its target are left
    untouched. Callers may also check parent directories when their
    operation must remain inside a selected configuration root.

    *action* names the operation for the diagnostic ("write" or "remove").
    *error* is the caller's own refusal type, so each tool still reports its
    documented exception class; :mod:`tools.apply_gtk` and
    :mod:`tools.install_firefox` both pass theirs.
    """
    if path.is_symlink():
        raise error(
            f"cannot {action} {path}: it is a symbolic link; refusing to "
            "replace or delete the link instead of the file it names"
        )
