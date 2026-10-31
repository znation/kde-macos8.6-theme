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
    from tools.containment import read_capped_bytes, require_within_repo
    from tools.repo_root import ROOT
else:  # imported from a directly run tool
    from atomic_write import write_atomically
    from containment import read_capped_bytes, require_within_repo
    from repo_root import ROOT

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
# Only CR, LF and CRLF end a line in this INI-shaped file. ``str.splitlines``
# also breaks on U+2028/U+2029, NEL and the C0 separators, so a value containing
# one would split into a phantom line and the rest of the value would be
# silently dropped from the written config.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")
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
    data = read_capped_bytes(
        path,
        _MAX_DEFAULTS_BYTES,
        "for a defaults file",
    )
    assert data is not None
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

    A plain ``[Wallpaper]`` section names no file and is skipped. A
    repeated ``[file][group]`` heading continues the same group: keys from
    both occurrences are kept, and a key repeated within it keeps the later
    value. A heading
    that is neither a plain ``[group]`` nor a complete ``[file][group]`` -- a
    mistyped bracket, a missing closing bracket, trailing text after the
    closing ``]``, or surrounding whitespace inside a bracket pair -- raises
    ``ValueError`` naming it, so its keys cannot silently vanish from the
    written config. A padded name (``[kwinrc ][Theme]``) would otherwise parse
    as the distinct file ``'kwinrc '``, which :func:`write_configs` compares
    against the real name and drops. Only CR, LF and CRLF end a line, so
    U+2028, U+2029, NEL or a C0 separator inside a value does not split it
    into a phantom line. The file is decoded as
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
    for raw in _LINE_BREAK.split(_read_defaults_text(path)):
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

    The mode is read with one guarded ``stat``, not an ``exists()`` probe
    followed by a ``stat()``: a partner writing the same config home (a KWin
    session's scratch config, saved at exit) can remove the file between the
    two calls, and an unguarded second lookup would then raise a bare
    ``FileNotFoundError`` out of the middle of :func:`write_configs`, after
    some configs were written and before the rest. A file removed before the
    lookup reads exactly like one that never existed: the write carries the
    umask's default mode.
    """
    mode: int | None = None
    try:
        mode = path.stat().st_mode & 0o777
    except FileNotFoundError:
        pass
    write_atomically(
        path,
        lambda destination: destination.write(content.encode("utf-8")),
        mode=mode,
    )


def _config_name(name: object) -> str:
    """Return *name* as a plain config filename, refusing a path.

    :func:`write_configs` joins each name onto the caller's config home, so a
    name carrying a separator (``../kwinrc``) or an absolute path would write
    outside it. The defaults file only ever names flat files such as
    ``kwinrc``, so anything that is not its own basename is refused before a
    single file is written. A NUL byte is refused too: ``open()`` would raise
    ``ValueError`` for it after the earlier files had already been written.
    """
    if not isinstance(name, str):
        raise ValueError(
            f"write_configs names must be str config filenames, not "
            f"{type(name).__name__}"
        )
    if (
        not name
        or name in (".", "..")
        or name != Path(name).name
        or "\0" in name
    ):
        raise ValueError(
            f"write_configs names must be plain config filenames inside "
            f"the config home: {name!r}"
        )
    return name


def write_configs(config_home: Path, names: Iterable[str]) -> None:
    """Write one config file per name in *names* from the defaults' sections for it.

    Each name must be a bare filename, so the writes stay inside *config_home*;
    a list of names is validated before any of them is written, and a single
    string is refused rather than iterated character by character into one
    file per letter. Every name must have at least one ``[name][group]``
    section in the defaults file: a truncated or empty defaults file would
    otherwise write an empty config, silently dropping the theme's settings
    for that file. All names are checked before the first one is written, so
    a missing section leaves every config unchanged.
    """
    if not isinstance(config_home, Path):
        raise ValueError(
            f"write_configs config_home must be a pathlib.Path, not "
            f"{type(config_home).__name__}"
        )
    if isinstance(names, (str, bytes)):
        raise ValueError(
            "write_configs names must be a sequence of config filenames, "
            f"not a single {type(names).__name__}: {names!r}"
        )
    wanted = [_config_name(name) for name in names]
    groups = defaults_groups(DEFAULTS)
    missing = [
        name
        for name in wanted
        if not any(section_file == name for section_file, _ in groups)
    ]
    if missing:
        raise ValueError(
            f"{DEFAULTS}: no [<file>][<group>] section defines "
            f"{', '.join(missing)}; refusing to write an empty config"
        )
    for name in wanted:
        lines: list[str] = []
        for (section_file, group), values in groups.items():
            if section_file != name:
                continue
            lines.append(f"[{group}]")
            lines.extend(f"{key}={value}" for key, value in values.items())
            lines.append("")
        _write_config_atomically(config_home / name, "\n".join(lines))
