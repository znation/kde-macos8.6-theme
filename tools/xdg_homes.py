"""Resolve the XDG data and config home directories for the tools.

An absolute ``$XDG_DATA_HOME`` or ``$XDG_CONFIG_HOME`` is used as given; an
empty or relative value is invalid under the XDG Base Directory spec and falls
back to its default below an absolute ``$HOME`` (``.local/share`` or
``.config``). Each resolver returns ``None`` when no absolute path can be
resolved, so the caller refuses instead of guessing where to read or write;
:func:`require_home` raises that refusal with the shared diagnostic naming the
received values, which the GTK and Kvantum selection tools raise through
their own :class:`~tools.gtk_user_files.ConfigError`.
"""

from __future__ import annotations

import os
from pathlib import Path


def _absolute(env: dict[str, str], name: str) -> Path | None:
    """Return *name* from *env* when it is an absolute path, else ``None``."""
    value = env.get(name, "")
    return Path(value) if os.path.isabs(value) else None


def _home_child(env: dict[str, str], *parts: str) -> Path | None:
    """Return an absolute ``$HOME`` joined with *parts*, else ``None``."""
    home = env.get("HOME", "")
    if not os.path.isabs(home):
        return None
    return Path(home).joinpath(*parts)


def data_home(env: dict[str, str]) -> Path | None:
    """Resolve the data home: absolute XDG, else ``$HOME/.local/share``.

    An empty or relative ``XDG_DATA_HOME`` is invalid and falls back to the
    XDG default; with an unusable ``HOME`` there is no absolute path to use,
    so the result is ``None``.
    """
    return _absolute(env, "XDG_DATA_HOME") or _home_child(env, ".local", "share")


def default_data_home(env: dict[str, str]) -> Path | None:
    """Return the XDG default data home, ``$HOME/.local/share``.

    Unlike :func:`data_home` no ``$XDG_DATA_HOME`` value is consulted: this
    is the fallback path the spec defines below an absolute ``$HOME``, so a
    usable ``HOME`` is the only way to name it. Callers compare it with
    :func:`data_home`'s result to detect a data home Kvantum's literal
    ``$HOME/.local/share/themes`` search cannot reach.
    """
    return _home_child(env, ".local", "share")


def config_home(env: dict[str, str]) -> Path | None:
    """Resolve the config home: absolute XDG, else ``$HOME/.config``.

    An empty or relative ``XDG_CONFIG_HOME`` is invalid and falls back to the
    XDG default; with an unusable ``HOME`` there is no absolute path to use,
    so the result is ``None``.
    """
    return _absolute(env, "XDG_CONFIG_HOME") or _home_child(env, ".config")


def require_home(
    path: Path | None, env: dict[str, str], variable: str, fallback: str, error
) -> Path:
    """Return *path*, or refuse naming the values that could not resolve.

    *fallback* is the ``$HOME``-relative path the XDG spec falls back to,
    included in the diagnostic so the user can see which directory could not
    be resolved. A resolver above returns ``None`` only when both *variable*
    and ``HOME`` are unusable, so both received values appear, in shell
    quoting that marks the bounds of a value (an empty one counts as unset,
    matching the resolver's own treatment), and ``report_error``'s escaping
    keeps every byte from reaching a terminal raw. *error* is the refusal
    class to raise, so each tool raises the error type its callers catch.
    """
    if path is None:
        raise error(
            f"{variable} is {_home_state(env, variable)} and HOME is "
            f"{_home_state(env, 'HOME')}, so the {fallback} fallback cannot "
            f"be used; set {variable} to an absolute path or export an "
            "absolute HOME"
        )
    return path


def _home_state(env: dict[str, str], variable: str) -> str:
    """Describe the *variable* value *env* carries, for a refusal message."""
    if variable not in env:
        return "unset"
    if not env[variable]:
        return "empty"
    return f"not an absolute path ('{env[variable]}')"
