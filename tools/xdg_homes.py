"""Resolve the XDG data and config home directories for the tools.

An absolute ``$XDG_DATA_HOME`` or ``$XDG_CONFIG_HOME`` is used as given; an
empty or relative value is invalid under the XDG Base Directory spec and falls
back to its default below an absolute ``$HOME`` (``.local/share`` or
``.config``). Each resolver returns ``None`` when no absolute path can be
resolved, so the caller refuses with its own tool-named diagnostic instead of
guessing where to read or write.
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


def config_home(env: dict[str, str]) -> Path | None:
    """Resolve the config home: absolute XDG, else ``$HOME/.config``.

    An empty or relative ``XDG_CONFIG_HOME`` is invalid and falls back to the
    XDG default; with an unusable ``HOME`` there is no absolute path to use,
    so the result is ``None``.
    """
    return _absolute(env, "XDG_CONFIG_HOME") or _home_child(env, ".config")
