"""Validate and publish the config files assembled from theme defaults."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

if __package__:
    from tools.atomic_write import write_atomically
else:  # imported from a directly run tool
    from atomic_write import write_atomically


def write_config_atomically(path: Path, content: str) -> None:
    """Write *content* so the target is either the old file or the whole new one.

    The mode is read with one guarded ``stat``. A file removed before the
    lookup reads like one that never existed and receives the umask's mode.
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
    """Return *name* as a plain config filename, refusing a path."""
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


def publish_configs(
    config_home: Path,
    names: Iterable[str],
    *,
    defaults_path: Path,
    read_groups: Callable[[Path], dict[tuple[str, str], dict[str, str]]],
) -> None:
    """Write configs named by *names* using sections from the defaults file.

    The public entry is ``tools.theme_defaults.write_configs``, which binds the
    shipped defaults file and reader; this engine takes both as parameters so
    tests can drive it with a fake defaults file.
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
    try:
        name_iterator = iter(names)
    except TypeError as exc:
        raise ValueError(
            f"write_configs names must be an iterable of config filenames, "
            f"not {type(names).__name__}"
        ) from exc
    wanted = [_config_name(name) for name in name_iterator]
    groups = read_groups(defaults_path)
    missing = [
        name
        for name in wanted
        if not any(section_file == name for section_file, _ in groups)
    ]
    if missing:
        raise ValueError(
            f"{defaults_path}: no [<file>][<group>] section defines "
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
        write_config_atomically(config_home / name, "\n".join(lines))
