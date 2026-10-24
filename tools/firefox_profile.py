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
    from tools.containment import open_regular_binary
    from tools.firefox_user_files import ConfigError
else:  # imported from a directly run tool
    from containment import open_regular_binary
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
        with open_regular_binary(path) as binary:
            data = binary.read(_MAX_INI_FILE_BYTES + 1)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    if len(data) > _MAX_INI_FILE_BYTES:
        raise ConfigError(
            f"{path} is larger than the {_MAX_INI_FILE_BYTES}-byte limit "
            "this discovery reads; refusing to load it whole"
        )
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
    if section.get("IsRelative", fallback="1").strip() != "0":
        return root / path
    return path


def _candidates(root: Path) -> list[Path]:
    """Return profile candidates in Firefox's own preference order."""
    candidates = []
    installs = _read_ini(root / "installs.ini")
    if installs is not None:
        for name in installs.sections():
            # Firefox names these sections by install hash (and older releases
            # by ``Install`` plus a suffix), so any section can hold Default.
            candidate = _candidate(root, installs[name], "Default")
            if candidate is None:
                continue
            candidates.append(candidate)
            break
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
            candidate = _candidate(root, default, "Path")
            if candidate is not None:
                candidates.append(candidate)
        for section in sections:
            candidate = _candidate(root, section, "Path")
            if candidate is None:
                continue
            candidates.append(candidate)
            break
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
