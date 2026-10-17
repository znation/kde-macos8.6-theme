"""Read the global theme's ``contents/defaults`` and write the config files it feeds.

The ``defaults`` file names each target config file in the first bracket pair
of a section heading (``[kwinrc][org.kde.kdecoration2]``). :func:`defaults_groups`
parses those sections; :func:`write_configs` writes them out as plain INI files
in a config home.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

DEFAULTS = (
    Path(__file__).resolve().parents[1]
    / "theme"
    / "look-and-feel"
    / "org.macos8.desktop"
    / "contents"
    / "defaults"
)

_FILE_GROUP = re.compile(r"\[([^\[\]]+)\]\[([^\[\]]+)\]$")
_ANY_HEADING = re.compile(r"\[[^\]]*\]")


def defaults_groups(path: Path = DEFAULTS) -> dict[tuple[str, str], dict[str, str]]:
    """Return ``{(file, group): {key: value}}`` for the ``[file][group]`` sections.

    A plain ``[Wallpaper]`` section names no file and is skipped.
    """
    groups: dict[tuple[str, str], dict[str, str]] = {}
    current: dict[str, str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if _ANY_HEADING.match(line):
            match = _FILE_GROUP.match(line)
            current = groups.setdefault(match.groups(), {}) if match else None
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key.strip()] = value.strip()
    return groups


def write_configs(config_home: Path, names: Iterable[str]) -> None:
    """Write one config file per name in *names* from the defaults' sections for it."""
    groups = defaults_groups()
    for name in names:
        lines: list[str] = []
        for (file, group), values in groups.items():
            if file != name:
                continue
            lines.append(f"[{group}]")
            lines.extend(f"{key}={value}" for key, value in values.items())
            lines.append("")
        (config_home / name).write_text("\n".join(lines), encoding="utf-8")
