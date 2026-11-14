"""Report an ``OSError`` in a block as the caller's own refusal type, by path."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def refusing_os_errors(error: type[Exception], action: str, path: Path) -> Iterator[None]:
    """Raise *error* for an ``OSError`` in the block, naming *action* and *path*.

    The message reads ``cannot {action} {path}: {exc}`` and the original
    ``OSError`` is kept as the cause. Other exceptions pass through unchanged.
    Callers pass their own refusal class so each tool still reports the
    exception type its documentation names. :mod:`tools.gtk_staging`,
    :mod:`tools.firefox_user_files`, :mod:`tools.firefox_profile_actions`,
    :mod:`tools.firefox_transaction`, :mod:`tools.file_lock` (the
    parent-directory create) and :mod:`tools.apply_konsole_font` (the
    directory create and the font reads and writes) use this helper.
    """
    try:
        yield
    except OSError as exc:
        raise error(f"cannot {action} {path}: {exc}") from exc
