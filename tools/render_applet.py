"""Locate the KPackage applet package a ``plasmawindowed`` client opens.

``plasmawindowed <applet>`` opens a Plasma applet package from the XDG data
directories: KPackage searches ``<data root>/plasma/plasmoids/<id>/`` and reads
its ``metadata.json``. A package is not a command, so a missing-tool check
never sees its absence -- on a host without the default applet, the capture
would waste a full scratch KWin session and time out before anything paints.
:func:`applet_problem` is the pre-flight check that closes that wart: it
returns a diagnostic string when the package cannot be found, or ``None`` when
one of the searched roots holds it.

Location rule probed on 2026-11-11: ``plasmawindowed --help`` takes ``applet``
as its first positional argument, and the installed default applet's package
stands at ``/usr/share/plasma/plasmoids/org.kde.plasma.calculator/metadata.json``
on that host -- the XDG data-root layout this module mirrors.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

# The XDG defaults: an unset or empty ``XDG_DATA_HOME`` falls back to
# ``~/.local/share``, and an unset or empty ``XDG_DATA_DIRS`` to these two.
_DEFAULT_DATA_DIRS = ("/usr/local/share", "/usr/share")


def _default_data_home() -> Path:
    """Return the ``~/.local/share`` fallback KPackage shares."""
    return Path.home() / ".local" / "share"


def data_roots_from_environment(
    environ: Mapping[str, str] | None = None,
) -> list[Path]:
    """Return the XDG data roots a KPackage search would cover.

    ``environ`` defaults to ``os.environ``; a root derived from an unset or
    empty variable is the XDG default for it. The ``XDG_DATA_DIRS`` entries
    keep their listed order and drop empty components.
    """
    if environ is None:
        environ = os.environ
    home = environ.get("XDG_DATA_HOME")
    roots = [Path(home) if home else _default_data_home()]
    dirs = environ.get("XDG_DATA_DIRS")
    if not dirs:
        roots.extend(Path(entry) for entry in _DEFAULT_DATA_DIRS)
    else:
        roots.extend(Path(entry) for entry in dirs.split(":") if entry)
    return roots


def applet_problem(applet_id: str, data_roots=None) -> str | None:
    """Return why *applet_id* cannot be opened, or None when a package exists.

    A plasmoid id is a dotted KPlugin id: an empty id, ``.``, ``..``, or one
    carrying ``/``, ``\\`` or NUL is refused as its own problem, before any
    directory is searched. (``..`` is refused because the filesystem resolves
    ``plasma/plasmoids/../metadata.json`` out of the plasmoids directory, so a
    stray ``plasma/metadata.json`` under a root would otherwise count as a
    package.) With ``data_roots`` unset the roots come from
    :func:`data_roots_from_environment`; a root whose
    ``plasma/plasmoids/<id>/metadata.json`` is a plain file ends the search
    with ``None``, and the returned problem names the id and every root that
    was searched.
    """
    if not isinstance(applet_id, str):
        raise ValueError(
            f"applet_problem() requires a str id: id must be str, "
            f"not {type(applet_id).__name__}"
        )
    if (
        not applet_id
        or applet_id in (".", "..")
        or "/" in applet_id
        or "\\" in applet_id
        or "\0" in applet_id
    ):
        return (
            f"not a plasmoid id: {applet_id!r} is empty, is '.' or '..', or "
            "carries a path separator"
        )
    roots = data_roots if data_roots is not None else data_roots_from_environment()
    relative = Path("plasma") / "plasmoids" / applet_id / "metadata.json"
    for root in roots:
        if (Path(root) / relative).is_file():
            return None
    searched = ", ".join(str(root) for root in roots)
    return (
        f"required applet package not found: {applet_id} "
        f"(no plasma/plasmoids/{applet_id}/metadata.json under {searched})"
    )
