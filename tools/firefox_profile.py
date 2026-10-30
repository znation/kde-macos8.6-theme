"""Resolve the Firefox profile directory that the installer should use.

An explicit ``--profile``/``FIREFOX_PROFILE`` names the directory directly;
otherwise the active profile is discovered under ``$HOME/.mozilla/firefox``
following Firefox's own ``installs.ini`` then ``profiles.ini`` order.

:class:`ConfigError` is the Firefox install's refusal type, defined in
``tools/firefox_user_files.py`` so this module and the installer raise the
same one.
"""

from __future__ import annotations

import configparser
import io
import os
from pathlib import Path

if __package__:
    from tools.containment import read_capped_bytes, resolves_within
    from tools.firefox_user_files import ConfigError
else:  # imported from a directly run tool
    from containment import read_capped_bytes, resolves_within
    from firefox_user_files import ConfigError


# Firefox's INI files are a few kilobytes at most. The path is the user's and
# can name something arbitrarily large (a wrong file dropped in the Firefox
# root); configparser would read the whole thing, and a MemoryError is not an
# OSError, so it would escape as a traceback instead of this module's ConfigError.
_MAX_INI_FILE_BYTES = 1 << 20


def _read_ini(path: Path) -> configparser.ConfigParser | None:
    """Return *path* parsed without interpolation, or ``None`` when absent.

    The file is opened through the shared regular-file reader, so a FIFO or
    device at an INI path is refused by name instead of blocking profile
    discovery on an open that waits for a writer. The opened descriptor is
    checked, so a regular file swapped for a pipe before the open is still
    refused. At most one byte past ``_MAX_INI_FILE_BYTES`` is read, so an
    oversize INI is refused by name instead of being loaded whole.
    """
    try:
        data = read_capped_bytes(
            path,
            _MAX_INI_FILE_BYTES,
            "this discovery reads; refusing to load it whole",
            missing_ok=True,
            error=ConfigError,
        )
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    if data is None:
        return None
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with io.TextIOWrapper(io.BytesIO(data), encoding="utf-8") as handle:
            parser.read_file(handle)
    except (UnicodeDecodeError, ValueError, configparser.Error) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    return parser


def _candidate(
    root: Path, section: configparser.SectionProxy, key: str
) -> Path | None:
    """Return the directory *section* names under *key*, or ``None``.

    The path is relative to *root* unless the section sets ``IsRelative=0``.
    ``installs.ini`` names its default under ``Default`` while a
    ``profiles.ini`` profile names its directory under ``Path``.
    """
    value = section.get(key, fallback="").strip()
    if not value:
        return None
    path = Path(value)
    is_relative = section.get("IsRelative", fallback="1").strip()
    if is_relative not in {"0", "1"}:
        raise ConfigError(
            f"invalid IsRelative value {is_relative!r} for Firefox profile path {value!r}; expected 0 or 1"
        )
    if is_relative != "0":
        candidate = root / path
        if not resolves_within(root, candidate):
            raise ConfigError(
                f"relative Firefox profile path escapes its root: {value!r}"
            )
        return candidate
    return path


def _candidates(root: Path) -> list[Path]:
    """Return profile candidates in Firefox's own preference order.

    Every installs.ini section's default comes first, in file order (the
    running binary's install hash is unknown, so a stale first section must
    not hide a later live one), then a ``profiles.ini`` section marked
    ``Default=1``, then every ``profiles.ini`` section that names a ``Path`` in
    file order. Every section is listed, not just the first, so a stale marked
    default (or a stale first section) falls through to a later live profile
    instead of reporting that no profile was found. Each directory appears
    once: the marked default is normally also a section in file order.
    """
    candidates: list[Path] = []

    def remember(candidate: Path | None) -> None:
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)

    installs = _read_ini(root / "installs.ini")
    if installs is not None:
        for name in installs.sections():
            # Firefox names these sections by install hash (and older releases
            # by ``Install`` plus a suffix), so any section can hold Default.
            candidate = _candidate(root, installs[name], "Default")
            remember(candidate)
    profiles = _read_ini(root / "profiles.ini")
    if profiles is not None:
        sections = [
            profiles[name]
            for name in profiles.sections()
            if name.startswith("Profile")
        ]
        default = next(
            (
                section
                for section in sections
                if section.get("Default", fallback="").strip() == "1"
            ),
            None,
        )
        if default is not None:
            remember(_candidate(root, default, "Path"))
        for section in sections:
            remember(_candidate(root, section, "Path"))
    return candidates


def resolve_profile(explicit: str | None, env: dict[str, str]) -> Path:
    """Return the profile directory named by *explicit*, the environment or INI.

    *explicit* is the ``--profile`` value; when it is ``None`` an
    ``FIREFOX_PROFILE`` environment variable is used. Either named path must
    be an absolute existing directory. An empty ``FIREFOX_PROFILE`` is
    treated as unset, matching the Makefile's ``$(if $(FIREFOX_PROFILE),...)``
    which omits ``--profile``; without a named path, ``HOME`` must be absolute
    and the profile is resolved from ``$HOME/.mozilla/firefox``.
    """
    named = explicit
    if named is None:
        named = env.get("FIREFOX_PROFILE") or None
    if named is not None:
        path = Path(named)
        if not path.is_absolute():
            raise ConfigError(f"Firefox profile must be an absolute path: {path}")
        if not path.is_dir():
            raise ConfigError(f"Firefox profile is not a directory: {path}")
        return path

    home = env.get("HOME", "")
    if not os.path.isabs(home):
        raise ConfigError(
            "HOME is unset or not absolute and no Firefox profile was named"
        )
    root = Path(home) / ".mozilla" / "firefox"
    candidates = _candidates(root)
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    tried = ", ".join(str(path) for path in candidates) or "none"
    raise ConfigError(
        f"no Firefox profile found under {root}; candidates tried: {tried}"
    )
