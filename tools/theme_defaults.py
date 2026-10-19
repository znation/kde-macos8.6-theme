"""Read the global theme's ``contents/defaults`` and write the config files it feeds.

The ``defaults`` file names each target config file in the first bracket pair
of a section heading (``[kwinrc][org.kde.kdecoration2]``). :func:`defaults_groups`
parses those sections; :func:`write_configs` writes them out as plain INI files
in a config home. The file is read as ``utf-8-sig``: a leading UTF-8 BOM (an
editor artifact) is stripped rather than folded into the first heading, where
it would make that heading unrecognizable and silently drop its keys.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

if __package__:
    from tools.containment import require_within_repo
else:  # imported from a directly run tool
    from containment import require_within_repo

ROOT = Path(__file__).resolve().parents[1]

DEFAULTS = (
    ROOT
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

    A plain ``[Wallpaper]`` section names no file and is skipped. A heading
    that is neither a plain ``[group]`` nor a complete ``[file][group]`` -- a
    mistyped bracket, a missing closing bracket, trailing text after the
    closing ``]``, or surrounding whitespace inside a bracket pair -- raises
    ``ValueError`` naming it, so its keys cannot silently vanish from the
    written config. A padded name (``[kwinrc ][Theme]``) would otherwise parse
    as the distinct file ``'kwinrc '``, which :func:`write_configs` compares
    against the real name and drops. The file is decoded as
    ``utf-8-sig``, so a leading UTF-8 BOM is stripped instead of being folded
    into the first heading, where it would make that heading match neither
    pattern and silently drop its section. A repository path that resolves
    outside the repository (a checked-in symlink escape) raises ``ValueError``
    before it is read; a path outside the repository is left alone.
    """
    groups: dict[tuple[str, str], dict[str, str]] = {}
    current: dict[str, str] | None = None
    require_within_repo(path, ROOT)
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Any line that opens a bracket must be a well-formed heading: a
        # heading with no closing bracket (``[kwinrc``) matches neither
        # ``_FILE_GROUP`` nor ``_ANY_HEADING.fullmatch``, so testing
        # ``_ANY_HEADING.match`` here would let it fall through as a bare line
        # and attach its keys to the previous section (or, when it carries an
        # ``=``, become a bogus key). A non-heading line never starts with
        # ``[`` -- a key line starts with the key -- so this is the same test
        # the match made, widened to catch the bracket with no close.
        if line.startswith("["):
            match = _FILE_GROUP.match(line)
            if match:
                file, group = match.groups()
                # A name padded with whitespace (``[kwinrc ][Theme]``) matches
                # the pattern but names a file/group distinct from the
                # unpadded one, so the section is silently dropped when
                # ``write_configs`` filters on the exact name. Refuse it by
                # name rather than guess which spelling was meant.
                if file != file.strip() or group != group.strip():
                    raise ValueError(
                        f"{path}: malformed section heading {line!r}: the "
                        "file and group names must not have surrounding "
                        "whitespace"
                    )
                current = groups.setdefault((file, group), {})
            elif _ANY_HEADING.fullmatch(line):
                # A plain ``[Wallpaper]`` names no config file and is skipped.
                current = None
            else:
                raise ValueError(
                    f"{path}: malformed section heading {line!r}: expected "
                    "'[file][group]' or a plain '[group]'"
                )
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
