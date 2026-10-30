"""Publish Firefox profile files as one recoverable install transaction."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

if __package__:
    from tools.firefox_user_files import (
        ConfigError,
        read_profile_text,
        write_profile_bytes,
        write_profile_text,
    )
else:  # imported from a directly run tool
    from firefox_user_files import (
        ConfigError,
        read_profile_text,
        write_profile_bytes,
        write_profile_text,
    )


def _restore_file(path: Path, previous: str | None) -> None:
    """Restore prior text, or remove a file created by the transaction."""
    if previous is None:
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise ConfigError(f"cannot restore {path}: {exc}") from exc
    else:
        write_profile_text(path, previous)


def _restore_user_js(path: Path, previous: str | None, published: str) -> None:
    """Restore user.js only if the failed atomic write published our text."""
    if previous != published and read_profile_text(path) == published:
        _restore_file(path, previous)


def publish_install(
    sheets: Sequence[tuple[Path, bytes, str | None]],
    user_js_path: Path,
    previous_user_js: str | None,
    published_user_js: str,
    write_operation: Callable[[Path, bytes], None] = write_profile_bytes,
) -> None:
    """Publish sheets then user.js; restore published state on any failure."""
    try:
        for path, data, _previous in sheets:
            write_operation(path, data)
        write_profile_text(user_js_path, published_user_js)
    except BaseException as exc:
        rollback_errors = []
        for path, _data, previous in sheets:
            try:
                _restore_file(path, previous)
            except ConfigError as rollback:
                rollback_errors.append(str(rollback))
        try:
            _restore_user_js(user_js_path, previous_user_js, published_user_js)
        except ConfigError as rollback:
            rollback_errors.append(str(rollback))
        if rollback_errors:
            raise ConfigError(f"{exc}; {'; '.join(rollback_errors)}") from exc
        raise
