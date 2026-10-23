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
    from tools.atomic_write import write_atomically
    from tools.containment import open_regular_binary, require_within_repo
else:  # imported from a directly run tool
    from atomic_write import write_atomically
    from containment import open_regular_binary, require_within_repo

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
# ``contents/defaults`` is contributor-supplied, so a checked-in (or
# LFS-smudged) multi-gigabyte file must not be loaded whole: ``read_text``
# would allocate it and raise ``MemoryError`` (which is neither an ``OSError``
# nor a ``ValueError``, so the render's handler would not report it) instead of
# a diagnostic. The real file is a few hundred bytes; 1 MiB leaves ample room
# for growth while bounding the read the way ``reference_validation`` bounds
# ``sources.txt`` and ``local_hook`` bounds an existing hook.
_MAX_DEFAULTS_BYTES = 1 << 20


def _read_defaults_text(path: Path) -> str:
    """Return *path*'s text (``utf-8-sig``), refusing one over the size limit.

    At most one byte past the cap is read, so an oversize file is detected
    without loading the rest of it; a longer file raises ``ValueError`` naming
    the limit, like a malformed heading, so the caller reports it instead of a
    ``MemoryError`` aborting the run. Decoding as ``utf-8-sig`` strips a
    leading UTF-8 BOM, which an editor may have added. A file that is not
    valid UTF-8 raises ``ValueError`` naming the path instead of a bare
    ``UnicodeDecodeError``. A FIFO or device
    would block or stream forever, so it is refused by name when the opened
    descriptor turns out not to be a regular file.
    """
    with open_regular_binary(path) as handle:
        data = handle.read(_MAX_DEFAULTS_BYTES + 1)
    if len(data) > _MAX_DEFAULTS_BYTES:
        raise ValueError(
            f"{path}: is larger than the {_MAX_DEFAULTS_BYTES}-byte limit "
            "for a defaults file"
        )
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"{path}: is not valid UTF-8: {exc}"
        ) from exc


def _section_heading(path: Path, line: str) -> tuple[str, str] | None:
    """Return the ``(file, group)`` a heading names, or None for a plain group.

    A plain ``[Wallpaper]`` heading names no config file and returns None. A
    heading that is neither that nor a complete ``[file][group]`` -- a
    mistyped bracket, a missing closing bracket, trailing text after the
    closing ``]``, or surrounding whitespace inside a bracket pair -- raises
    ``ValueError`` naming it, so its keys cannot silently vanish from the
    written config. A padded name (``[kwinrc ][Theme]``) would otherwise parse
    as the distinct file ``'kwinrc '``, which :func:`write_configs` compares
    against the real name and drops.
    """
    match = _FILE_GROUP.match(line)
    if match:
        file, group = match.groups()
        if file != file.strip() or group != group.strip():
            raise ValueError(
                f"{path}: malformed section heading {line!r}: the "
                "file and group names must not have surrounding "
                "whitespace"
            )
        return file, group
    if _ANY_HEADING.fullmatch(line):
        return None
    raise ValueError(
        f"{path}: malformed section heading {line!r}: expected "
        "'[file][group]' or a plain '[group]'"
    )


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
    pattern and silently drop its section. A file larger than
    ``_MAX_DEFAULTS_BYTES`` raises ``ValueError`` naming the limit instead of
    being read whole. A repository path that resolves outside the repository
    (a checked-in symlink escape) raises ``ValueError`` before it is read; a
    path outside the repository is left alone.
    """
    groups: dict[tuple[str, str], dict[str, str]] = {}
    current: dict[str, str] | None = None
    require_within_repo(path, ROOT)
    for raw in _read_defaults_text(path).splitlines():
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
            heading = _section_heading(path, line)
            current = (
                None if heading is None else groups.setdefault(heading, {})
            )
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key.strip()] = value.strip()
    return groups


def _write_config_atomically(path: Path, content: str) -> None:
    """Write *content* to *path* so it is either the old file or the whole new one.

    A crash mid-write leaves the previous config (or no file) rather than a
    truncated one that Plasma would read as malformed; see
    :func:`tools.atomic_write.write_atomically`.
    """
    mode = path.stat().st_mode & 0o777 if path.exists() else None
    write_atomically(
        path,
        lambda destination: destination.write(content.encode("utf-8")),
        mode=mode,
    )


def write_configs(config_home: Path, names: Iterable[str]) -> None:
    """Write one config file per name in *names* from the defaults' sections for it."""
    if not isinstance(config_home, Path):
        raise ValueError(
            f"write_configs config_home must be a pathlib.Path, not "
            f"{type(config_home).__name__}"
        )
    groups = defaults_groups()
    for name in names:
        lines: list[str] = []
        for (file, group), values in groups.items():
            if file != name:
                continue
            lines.append(f"[{group}]")
            lines.extend(f"{key}={value}" for key, value in values.items())
            lines.append("")
        _write_config_atomically(config_home / name, "\n".join(lines))
