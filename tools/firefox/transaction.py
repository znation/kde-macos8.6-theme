"""Publish Firefox profile files as one recoverable install transaction."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import NoReturn

if __package__ == "tools.firefox":
    from tools.firefox.user_files import (
        ConfigError,
        read_profile_text,
        write_profile_bytes,
        write_profile_text,
    )
    from tools.os_error_refusal import refusing_os_errors
else:  # imported from a directly run tool
    from firefox.user_files import (
        ConfigError,
        read_profile_text,
        write_profile_bytes,
        write_profile_text,
    )
    from os_error_refusal import refusing_os_errors


def raise_with_rollback_errors(
    failure: BaseException, rollback_errors: list[str]
) -> NoReturn:
    """Re-raise *failure* from an ``except`` block, naming any rollback errors.

    With no rollback errors this re-raises *failure* unchanged. Otherwise it
    raises a ``ConfigError`` whose message is *failure* followed by each
    rollback error, chained to *failure* as its cause. Its two callers are
    ``publish_install`` here and the removal path in ``tools/firefox/profile_actions.py``.
    """
    if rollback_errors:
        raise ConfigError(
            f"{failure}; {'; '.join(rollback_errors)}"
        ) from failure
    raise failure


def collect_rollback_errors(actions: Iterable[Callable[[], None]]) -> list[str]:
    """Run each rollback action and collect its ConfigError message."""
    errors = []
    for action in actions:
        try:
            action()
        except ConfigError as rollback:
            errors.append(str(rollback))
    return errors


def _restore_file(path: Path, previous: str | None) -> None:
    """Restore prior text, or remove a file created by the transaction."""
    if previous is None:
        with refusing_os_errors(ConfigError, "restore", path):
            path.unlink(missing_ok=True)
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
        raise_with_rollback_errors(
            exc,
            _restore_published(
                sheets, user_js_path, previous_user_js, published_user_js
            ),
        )


def _restore_published(
    sheets: Sequence[tuple[Path, bytes, str | None]],
    user_js_path: Path,
    previous_user_js: str | None,
    published_user_js: str,
) -> list[str]:
    """Restore every published path; return one message per failed restore."""
    actions = (
        lambda path=path, previous=previous: _restore_file(path, previous)
        for path, _data, previous in sheets
    )
    actions = (*actions, lambda: _restore_user_js(
        user_js_path, previous_user_js, published_user_js
    ))
    return collect_rollback_errors(actions)
